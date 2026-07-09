"""
Gráficas de KPIs — Simulación v3-REAL (geometría real NV1640 + recorrido real)
==============================================================================
Lee los resultados de la simulación NS-3 v3 (corrida de operación de la batería
vigente, principal_s1_*) y genera un panel profesional de KPIs para el capítulo
de resultados de la tesis:

  Figura A (kpi_v3_panel.png) — 4 paneles:
    1. RSSI vs tiempo con el AP servidor coloreado (roaming real por la zona)
    2. Tabla de KPIs con semáforo (cumple/no cumple) vs umbrales de la tesis
    3. Barras de KPI medido vs umbral (Comandos / Video / Telemetría)
    4. CDF del RSSI a lo largo del recorrido (cobertura)

  Figura B (kpi_v3_ruta_rssi.png) — mapa 2D de la zona con la ruta del LHD
    coloreada por RSSI (heat de señal a lo largo del recorrido real).

Datos = medidos por FlowMonitor / traza de la propia simulación (no inventados).

Ejecutar:  python kpis_v3real.py
"""
import os, csv, importlib.util
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
RES  = os.path.join(HERE, "..", "results")

# geometría (para el mapa de la ruta)
spec = importlib.util.spec_from_file_location("datos", os.path.join(HERE, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

# ---------------- cargar resultados ----------------
def load_flow_stats(path):
    rows = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            rows[r["name"]] = {k: (float(v) if k != "name" else v) for k, v in r.items()}
    return rows

def load_pos_log(path):
    t, x, y, ap, rssi = [], [], [], [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            t.append(float(r["time_s"])); x.append(float(r["x"])); y.append(float(r["y"]))
            # best_ap = AP de mejor señal (cobertura); "serving_ap" era el nombre
            # antiguo (impreciso) de la misma columna — se acepta por compatibilidad.
            ap.append(r.get("best_ap") or r["serving_ap"]); rssi.append(float(r["rssi_dbm"]))
    return (np.array(t), np.array(x), np.array(y), ap, np.array(rssi))

# Escenario de operación canónico: se usa una corrida de la batería vigente
# (principal_s1, generada con el código actual) para que TODAS las figuras
# provengan de la misma versión del simulador. Antes se usaba "mobility_v3",
# una corrida anterior que quedó desincronizada del resto de la batería.
OP = os.path.join(RES, "principal_s1_v3")
flow = load_flow_stats(OP + "_flow_stats.csv")
T, X, Y, AP, RSSI = load_pos_log(OP + "_pos_log.csv")

# ---------------- umbrales de la tesis (RNF) ----------------
# Comandos: OWD<=20ms, PLR<=0.5% (movilidad) | Video: E2E<=150ms, jitP95<=10ms,
# goodput>=38Mbps, PLR<=1% | Telemetría: informativa (OWD<=50ms, PLR<=0.5%)
KPI_DEF = [
    ("Comandos",   "OWD (ms)",        "owd_ms",       20.0,  "<="),
    ("Comandos",   "PLR (%)",         "plr_pct",       0.5,  "<="),
    ("Video",      "E2E (ms)",        "e2e_ms",      150.0,  "<="),
    ("Video",      "Jitter P95 (ms)", "jitter_p95_ms",10.0,  "<="),
    ("Video",      "Goodput (Mbps)",  "goodput_mbps", 38.0,  ">="),
    ("Video",      "PLR (%)",         "plr_pct",       1.0,  "<="),
    ("Telemetria", "OWD (ms)",        "owd_ms",       50.0,  "<="),
    ("Telemetria", "PLR (%)",         "plr_pct",       0.5,  "<="),
]
def cumple(val, thr, op):
    return (val <= thr) if op == "<=" else (val >= thr)

# ---------------- estilo ----------------
plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold"})
BG = "#F7F5EF"; OK = "#1D9E75"; BAD = "#C0392B"; INK = "#2B2B28"

# paleta de APs (Hawk azules, Cardinal morados)
aps_unicos = sorted(set(AP), key=lambda a: (a[0], int(a[1:])))
cmap_h = plt.cm.Blues(np.linspace(0.45, 0.9, sum(1 for a in aps_unicos if a[0] == "H")))
cmap_c = plt.cm.Purples(np.linspace(0.45, 0.9, sum(1 for a in aps_unicos if a[0] == "C")))
col_ap = {}
ih = ic = 0
for a in aps_unicos:
    if a[0] == "H": col_ap[a] = cmap_h[ih]; ih += 1
    else:           col_ap[a] = cmap_c[ic]; ic += 1

# ==================== FIGURA A: panel 2x2 ====================
fig = plt.figure(figsize=(16, 10)); fig.patch.set_facecolor(BG)
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], hspace=0.32, wspace=0.22)

# --- (1) RSSI vs tiempo con AP servidor ---
ax1 = fig.add_subplot(gs[0, 0]); ax1.set_facecolor("#FCFBF7")
for a in aps_unicos:
    m = np.array([s == a for s in AP])
    ax1.scatter(T[m], RSSI[m], s=14, color=col_ap[a], label=a, zorder=3)
ax1.axhline(-68, color="#E67E22", ls="--", lw=1.1)
ax1.annotate("-68 dBm (300 Mbps)", (T.max(), -68), fontsize=8, color="#B9770E", ha="right", va="bottom")
ax1.axhline(-82, color="#C0392B", ls=":", lw=1.1)
ax1.annotate("-82 dBm (54 Mbps)", (T.max(), -82), fontsize=8, color="#C0392B", ha="right", va="bottom")
ax1.set_xlabel("Tiempo (s)"); ax1.set_ylabel("RSSI del mejor AP (dBm)")
ax1.set_title("Nivel de señal disponible a lo largo del recorrido")
ax1.set_ylim(-92, -2); ax1.grid(True, alpha=0.3)
ax1.legend(ncol=3, fontsize=7.5, loc="lower left", framealpha=0.92,
           title=f"Mejor AP ({len(aps_unicos)} APs)", title_fontsize=8)

# --- (2) tabla de KPIs con semáforo ---
ax2 = fig.add_subplot(gs[0, 1]); ax2.axis("off")
ax2.set_title("KPIs medidos vs. umbrales de la tesis (RNF)", pad=14)
cell_text, cell_col = [], []
for grp, lbl, key, thr, op in KPI_DEF:
    val = flow[grp][key]
    ok = cumple(val, thr, op)
    thr_s = f"{op} {thr:g}"
    cell_text.append([grp, lbl, f"{val:.2f}", thr_s, "CUMPLE" if ok else "NO"])
    cell_col.append(["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
                     "#D5F0E4" if ok else "#F7D7D2"])
tab = ax2.table(cellText=cell_text, colLabels=["Flujo", "Métrica", "Medido", "Umbral", "Estado"],
                cellColours=cell_col, cellLoc="center", loc="center",
                colColours=["#E8E4D8"]*5)
tab.auto_set_font_size(False); tab.set_fontsize(9); tab.scale(1, 1.55)
for (r, c), cell in tab.get_celld().items():
    cell.set_edgecolor("#CFCABE")
    if r == 0: cell.set_text_props(weight="bold")
    if c == 4 and r > 0:
        cell.set_text_props(weight="bold",
                            color=OK if cell_text[r-1][4] == "CUMPLE" else BAD)

# --- (3) barras: HOLGURA de cumplimiento (% de margen hasta el umbral) ---
# Para "<=" (menos es mejor): holgura = (1 - medido/umbral)*100  -> 100% = ideal (0)
# Para ">=" (más es mejor):   holgura = (medido/umbral - 1)*100 acotado -> margen sobre el mínimo
ax3 = fig.add_subplot(gs[1, 0]); ax3.set_facecolor("#FCFBF7")
labels = [f"{g}\n{l.split(' (')[0]}" for g, l, *_ in KPI_DEF]
holg, colors = [], []
for grp, lbl, key, thr, op in KPI_DEF:
    val = flow[grp][key]
    if op == "<=":
        h = (1 - val/thr)*100                      # % por debajo del límite
    else:
        h = min((val/thr - 1)*100, 100)            # % por encima del mínimo (tope 100)
    holg.append(max(h, 0)); colors.append(OK if cumple(val, thr, op) else BAD)
xb = np.arange(len(labels))
ax3.bar(xb, holg, color=colors, edgecolor="#333", width=0.62, zorder=3)
ax3.set_xticks(xb); ax3.set_xticklabels(labels, fontsize=7.5)
ax3.set_ylabel("Holgura de cumplimiento (%)")
ax3.set_title("Holgura frente al umbral — más alto = más margen de cumplimiento")
ax3.set_ylim(0, 108); ax3.grid(True, axis="y", alpha=0.3)
for i, h in enumerate(holg):
    ax3.text(i, h+1.5, f"{h:.0f}%", ha="center", fontsize=8, color="#333", weight="bold")

# --- (4) CDF del RSSI ---
ax4 = fig.add_subplot(gs[1, 1]); ax4.set_facecolor("#FCFBF7")
rs = np.sort(RSSI); cdf = np.arange(1, len(rs)+1)/len(rs)*100
ax4.plot(rs, cdf, color="#1B4C7E", lw=2.4, zorder=3)
ax4.fill_between(rs, 0, cdf, color="#2E6FB0", alpha=0.12)
ax4.axvline(-68, color="#E67E22", ls="--", lw=1.1); ax4.axvline(-82, color="#C0392B", ls=":", lw=1.1)
ax4.annotate("-68 dBm", (-68, 5), rotation=90, fontsize=8, color="#B9770E", va="bottom", ha="right")
ax4.annotate("-82 dBm", (-82, 5), rotation=90, fontsize=8, color="#C0392B", va="bottom", ha="right")
ax4.set_xlabel("RSSI (dBm)"); ax4.set_ylabel("% del recorrido ≤ RSSI")
pct_ok = (RSSI >= -68).mean()*100
ax4.set_title(f"CDF del RSSI — {pct_ok:.0f}% del recorrido ≥ -68 dBm (300 Mbps)")
ax4.grid(True, alpha=0.3); ax4.set_xlim(rs.min()-3, rs.max()+3); ax4.set_ylim(0, 100)

glob = all(cumple(flow[g][k], thr, op) for g, l, k, thr, op in KPI_DEF)
fig.suptitle("NV1640 — KPIs de la red 802.11ac para teleoperación LHD (recorrido real, 300 s)\n"
             + ("TODOS LOS KPIs CUMPLEN" if glob else "ALGUNOS KPIs NO CUMPLEN"),
             fontsize=15, fontweight="bold", y=0.98,
             color=OK if glob else BAD)
outA = os.path.join(HERE, "kpi_v3_panel.png")
plt.savefig(outA, dpi=155, bbox_inches="tight", facecolor=BG); plt.close()
print(f"[OK] {outA}")

# ==================== FIGURA B: ruta coloreada por RSSI ====================
figB, axB = plt.subplots(figsize=(11, 11)); figB.patch.set_facecolor(BG); axB.set_facecolor("#FCFBF7")

# caminos de fondo
def bezier(p0, p1, p2, n=16):
    t = np.linspace(0, 1, n)[:, None]
    return (1-t)**2*np.array(p0) + 2*(1-t)*t*np.array(p1) + t**2*np.array(p2)
def densify(pts, cur):
    pts = [np.array(p, float) for p in pts]
    if len(pts) == 2: return np.array(pts)
    o = [pts[0]]
    for i in range(1, len(pts)-1):
        pv, c, nx = pts[i-1], pts[i], pts[i+1]
        if i in cur:
            din = np.linalg.norm(c-pv); do = np.linalg.norm(nx-c); r = min(16, din*.45, do*.45)
            pin = c+(pv-c)/(din+1e-9)*r; po = c+(nx-c)/(do+1e-9)*r
            o.append(pin); o.extend(bezier(pin, c, po)[1:]); o.append(po)
        else: o.append(c)
    o.append(pts[-1]); return np.array(o)
segs = [densify(c, []) for c in D.PRODUCCION]
axB.add_collection(LineCollection(segs, colors="#111", linewidths=7, capstyle="round",
                                  joinstyle="round", zorder=2, alpha=0.18))

# ruta del LHD coloreada por RSSI
pts = np.column_stack([X, Y]).reshape(-1, 1, 2)
segl = np.concatenate([pts[:-1], pts[1:]], axis=1)
lc = LineCollection(segl, cmap="RdYlGn", norm=plt.Normalize(-85, -35), linewidths=4.5, zorder=5)
lc.set_array(RSSI[:-1]); axB.add_collection(lc)
cb = figB.colorbar(lc, ax=axB, fraction=0.045, pad=0.03); cb.set_label("RSSI a lo largo de la ruta (dBm)")

# APs
for (x, y) in D.HAWKS:
    axB.scatter(x, y, s=95, marker="^", c="#1565C0", edgecolors="#fff", linewidths=1.3, zorder=8)
for (x, y) in D.CARDINALS_AP:
    axB.scatter(x, y, s=80, marker="s", c="#7B1FA2", edgecolors="#fff", linewidths=1.3, zorder=8)
for (x, y) in D.DRAWPOINTS:
    axB.scatter(x, y, s=16, c="#0C5B41", zorder=6)
axB.scatter(X[0], Y[0], s=140, marker="o", c="#111", edgecolors="#fff", linewidths=1.5, zorder=9)
axB.annotate("inicio", (X[0], Y[0]), fontsize=9, xytext=(6, -12), textcoords="offset points")

leg = [Line2D([0],[0], marker="^", color="none", markerfacecolor="#1565C0", markeredgecolor="#fff", markersize=12, label="AP Hawk (30 dBm)"),
       Line2D([0],[0], marker="s", color="none", markerfacecolor="#7B1FA2", markeredgecolor="#fff", markersize=11, label="AP Cardinal (23 dBm)"),
       Line2D([0],[0], marker="o", color="none", markerfacecolor="#0C5B41", markersize=8, label="Drawpoint")]
axB.legend(handles=leg, loc="upper left", fontsize=9, framealpha=0.92)
# % del recorrido con señal >= -68 dBm CALCULADO de los datos (nunca hardcodeado)
pct68 = (RSSI >= -68).mean()*100
axB.set_title("Recorrido real del LHD en la zona de producción coloreado por RSSI — NV1640\n"
              f"RSSI entre {RSSI.max():.0f} y {RSSI.min():.0f} dBm · "
              f"{pct68:.0f}% ≥ -68 dBm (soporta vídeo 40 Mbps)",
              fontsize=12.5, fontweight="bold")
axB.set_xlabel("X (m)"); axB.set_ylabel("Y (m)"); axB.set_aspect("equal")
axB.autoscale(); axB.grid(True, alpha=0.25)
outB = os.path.join(HERE, "kpi_v3_ruta_rssi.png")
plt.savefig(outB, dpi=155, bbox_inches="tight", facecolor=BG); plt.close()
print(f"[OK] {outB}")

# ---------------- resumen consola ----------------
print("\n=== KPIs v3-REAL ===")
for grp, lbl, key, thr, op in KPI_DEF:
    val = flow[grp][key]; ok = cumple(val, thr, op)
    print(f"  {grp:11s} {lbl:16s} = {val:8.3f}  ({op}{thr:g})  {'CUMPLE' if ok else 'NO'}")
print(f"\nGLOBAL: {'TODOS CUMPLEN' if glob else 'ALGUNOS NO CUMPLEN'}")
print(f"RSSI recorrido: min {RSSI.min():.1f} / media {RSSI.mean():.1f} / max {RSSI.max():.1f} dBm")
print(f"APs de mejor señal: {len(aps_unicos)} | traspasos de mejor señal: {sum(1 for i in range(1,len(AP)) if AP[i]!=AP[i-1])}")

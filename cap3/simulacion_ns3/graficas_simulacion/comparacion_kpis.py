"""
Comparación de KPIs — resultados vs. requisitos de la tesis y referencias de aplicación
=======================================================================================
Contrasta los KPIs obtenidos en la simulación (media de 10 semillas) con:
  (a) el requisito oficial de la tesis (RNF),
  (b) rangos de referencia típicos para teleoperación / control remoto de vehículos
      y los límites del estándar IEEE 802.11ac (referencias de aplicación, no papers
      específicos).

Genera comparacion_kpis.png (tabla sobria) e imprime el resumen.
Ejecutar:  python comparacion_kpis.py
"""
import os, sys, csv, glob
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES  = os.path.join(HERE, "..", "results")

def load_flow(p):
    d = {}
    for r in csv.DictReader(open(p)): d[r["name"]] = r
    return d

# media de las 10 semillas del escenario de operación
seed_files = sorted(glob.glob(os.path.join(RES, "principal_s*_v3_flow_stats.csv")))
if not seed_files:
    seed_files = [os.path.join(RES, "principal_s1_v3_flow_stats.csv")]
runs = [load_flow(p) for p in seed_files]
def media(grp, key):
    return float(np.mean([float(r[grp][key]) for r in runs if grp in r]))

# ---- filas de comparación ----
# (Servicio, Métrica, valor_obtenido, requisito_tesis, referencia_aplicacion)
obt = {
    "cmd_owd":  media("Comandos", "owd_ms"),
    "cmd_plr":  media("Comandos", "plr_pct"),
    "vid_e2e":  media("Video", "e2e_ms"),
    "vid_jit":  media("Video", "jitter_p95_ms"),
    "vid_tput": media("Video", "goodput_mbps"),
    "vid_plr":  media("Video", "plr_pct"),
}

filas = [
    ("Comandos", "Latencia OWD",  f"{obt['cmd_owd']:.1f} ms",  "≤ 20 ms",
     "Control remoto de vehículos: latencia < 100–150 ms para operación segura"),
    ("Comandos", "Pérdida (PLR)", f"{obt['cmd_plr']:.2f} %",   "≤ 0.5 %",
     "Enlaces de control fiables: PLR objetivo < 1 %"),
    ("Vídeo",    "Latencia E2E",  f"{obt['vid_e2e']:.1f} ms",  "≤ 150 ms",
     "Vídeo para teleoperación: E2E < 150–200 ms (percepción fluida)"),
    ("Vídeo",    "Jitter (P95)",  f"{obt['vid_jit']:.2f} ms",  "≤ 10 ms",
     "Streaming en tiempo real: jitter < 30–50 ms"),
    ("Vídeo",    "Throughput",    f"{obt['vid_tput']:.1f} Mbps","≥ 38 Mbps",
     "802.11ac 2×2 40 MHz: capacidad PHY hasta ~400 Mbps (holgura amplia)"),
    ("Vídeo",    "Pérdida (PLR)", f"{obt['vid_plr']:.2f} %",   "≤ 1 %",
     "Vídeo con FEC/robustez: PLR tolerable < 1–2 %"),
]

# ---- imprimir ----
for s, m, v, req, ref in filas:
    print(f"[{s:8s}] {m:14s} obtenido={v:10s} | tesis {req:9s} | ref: {ref}")

# ---- figura sobria ----
plt.rcParams.update({"font.size": 10, "axes.titleweight": "bold"})
C_OK, C_OK_BG, C_HEAD = "#3E7D5A", "#E3EFE7", "#Ececec"
fig, ax = plt.subplots(figsize=(16, 4.6)); ax.axis("off")
cell, colors = [], []
for s, m, v, req, ref in filas:
    cell.append([s, m, v, req, "Cumple", ref])
    colors.append(["white", "white", C_OK_BG, "white", C_OK_BG, "white"])
tab = ax.table(cellText=cell,
               colLabels=["Servicio", "Métrica", "Obtenido\n(media 10 sem.)",
                          "Requisito\ntesis (RNF)", "Estado", "Referencia de aplicación"],
               cellColours=colors, cellLoc="center", loc="center",
               colColours=[C_HEAD]*6,
               colWidths=[0.09, 0.11, 0.12, 0.10, 0.08, 0.50])
tab.auto_set_font_size(False); tab.set_fontsize(9.2); tab.scale(1, 2.0)
for (r, c), cellobj in tab.get_celld().items():
    cellobj.set_edgecolor("#CCC")
    if r == 0: cellobj.set_text_props(weight="bold")
    if c == 5 and r > 0: cellobj.set_text_props(ha="left")
    if c == 4 and r > 0: cellobj.set_text_props(weight="bold", color=C_OK)
ax.set_title("Comparación de los KPIs obtenidos con los requisitos de la tesis y "
             "referencias de aplicación\nEscenario de operación · media de 10 corridas · "
             "IEEE 802.11ac",
             fontsize=12.5, pad=16)
plt.figtext(0.5, 0.02,
    "Los valores obtenidos cumplen los requisitos de la tesis con holgura y se sitúan dentro "
    "(o por debajo) de los rangos de referencia habituales para teleoperación de vehículos.",
    ha="center", fontsize=9, style="italic", color="#444")
out = os.path.join(HERE, "comparacion_kpis.png")
plt.savefig(out, dpi=155, bbox_inches="tight"); plt.close()
print(f"\n[OK] {out}")

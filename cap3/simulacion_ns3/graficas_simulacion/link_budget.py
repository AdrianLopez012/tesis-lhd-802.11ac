"""
Presupuesto de enlace (link budget) — red 802.11ac NV1640
=========================================================
Calcula el balance de potencia de los enlaces de la red de teleoperación con los
parámetros reales de los datasheets y el modelo de propagación two-slope calibrado.
Para cada enlace representativo (Hawk→LHD, Cardinal→LHD) y a la distancia de diseño
(cobertura por AP), obtiene: PIRE, pérdida de trayecto, potencia recibida y MARGEN
sobre la sensibilidad requerida para vídeo (−68 dBm, 300 Mbps) y para el borde
(−82 dBm, 54 Mbps).

Genera: link_budget.png (tabla sobria) e imprime el desglose.
Ejecutar:  python link_budget.py
"""
import os, sys, importlib.util
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
# parámetros RF reales (fuente única)
spec = importlib.util.spec_from_file_location("rf", os.path.join(HERE, "..", "parametros_rf.py"))
RF = importlib.util.module_from_spec(spec); spec.loader.exec_module(RF)

# ---------------- modelo de propagación two-slope calibrado ----------------
FREQ = 5.0e9; LAMBDA = 3e8 / FREQ
N1, N2, D_BP = 1.9, 3.4, 40.0
PL_D0 = 20 * np.log10(4 * np.pi / LAMBDA)     # pérdida de referencia a 1 m
L_SYS = RF.L_SYSTEM_DB                          # 9.4 dB
GR_LHD = RF.LHD_ANTENA["gain_dbic"]            # 4.8 dBi (HELI-40)

# sensibilidades objetivo (802.11ac 2x2 40 MHz, fuente única: parametros_rf.py)
SENS_VIDEO = RF.SENS_VIDEO_DBM   # 300 Mbps (soporta vídeo 40 Mbps con holgura)
SENS_BORDE = RF.SENS_BORDE_DBM   # 54 Mbps (enlace de borde de celda; = umbral RNF-06)

# distancia de diseño = radio de cobertura por AP (de la geometría)
spec2 = importlib.util.spec_from_file_location("d", os.path.join(HERE, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(D)
D_DISENO = float(getattr(D, "COBERTURA_AP", 60.0))   # 60 m

def path_loss(d):
    d = max(d, 1.0)
    if d < D_BP: return PL_D0 + 10 * N1 * np.log10(d)
    return PL_D0 + 10 * N1 * np.log10(D_BP) + 10 * N2 * np.log10(d / D_BP)

def radio_max(tx_dbm, gt_dbi, sens_dbm):
    """Distancia a la que Prx cae hasta la sensibilidad dada (invierte el two-slope).
    Justifica el radio de diseño COBERTURA_AP: debe ser << que este radio máximo."""
    pl_adm = tx_dbm + gt_dbi + GR_LHD - L_SYS - sens_dbm   # pérdida de trayecto admisible
    pl_bp  = PL_D0 + 10 * N1 * np.log10(D_BP)              # pérdida en el breakpoint
    if pl_adm <= pl_bp:
        return 10 ** ((pl_adm - PL_D0) / (10 * N1))
    return D_BP * 10 ** ((pl_adm - pl_bp) / (10 * N2))

def link(tx_dbm, gt_dbi, d):
    pire = tx_dbm + gt_dbi                       # PIRE (sin pérdidas de sistema tx)
    pl = path_loss(d)
    prx = tx_dbm + gt_dbi + GR_LHD - pl - L_SYS  # potencia recibida en el LHD
    return pire, pl, prx

# enlaces representativos a la distancia de diseño
casos = [
    ("Hawk -> LHD",     RF.HAWK["tx_power_dbm"],     RF.HAWK["tx_gain_dbi"]),
    ("Cardinal -> LHD", RF.CARDINAL["tx_power_dbm"], RF.CARDINAL["tx_gain_dbi"]),
]

print(f"Distancia de diseño (radio cobertura AP): {D_DISENO:.0f} m")
print(f"Pérdida de trayecto a {D_DISENO:.0f} m: {path_loss(D_DISENO):.1f} dB")
# radios máximos de cobertura del modelo para el enlace más exigente (Cardinal):
# demuestran que el radio de diseño (60 m) está holgadamente dentro del alcance.
_txc, _gtc = RF.CARDINAL["tx_power_dbm"], RF.CARDINAL["tx_gain_dbi"]
R_VIDEO = radio_max(_txc, _gtc, SENS_VIDEO)
R_BORDE = radio_max(_txc, _gtc, SENS_BORDE)
print(f"Radio máx. del modelo (Cardinal→LHD): vídeo ({SENS_VIDEO:.0f} dBm) = {R_VIDEO:.0f} m"
      f" | borde ({SENS_BORDE:.0f} dBm) = {R_BORDE:.0f} m")
print(f"=> el radio de diseño ({D_DISENO:.0f} m) es {R_VIDEO/D_DISENO:.1f}x menor que el"
      f" radio máximo de vídeo: cobertura con holgura.\n")

# ---------------- construir tabla de link budget ----------------
# filas del balance (comunes) + por enlace las específicas
rows = []
def fmt(v, u=""): return f"{v:+.1f} {u}".strip() if isinstance(v, float) else str(v)

for nombre, tx, gt in casos:
    pire, pl, prx = link(tx, gt, D_DISENO)
    m_video = prx - SENS_VIDEO
    m_borde = prx - SENS_BORDE
    print(f"[{nombre}]  PIRE={pire:.1f} dBm | PL={pl:.1f} dB | Prx={prx:.1f} dBm "
          f"| margen vídeo={m_video:+.1f} dB | margen borde={m_borde:+.1f} dB")

# tabla detallada del enlace más exigente (Cardinal, menor potencia)
nombre, tx, gt = casos[1]
pire, pl, prx = link(tx, gt, D_DISENO)
detalle = [
    ("Potencia de transmisión (Pt)",          f"{tx:.1f} dBm"),
    ("Ganancia antena transmisora (Gt)",      f"+{gt:.1f} dBi"),
    ("PIRE",                                   f"{pire:.1f} dBm"),
    (f"Pérdida de trayecto a {D_DISENO:.0f} m (two-slope)", f"−{pl:.1f} dB"),
    ("Ganancia antena receptora LHD (Gr)",     f"+{GR_LHD:.1f} dBi"),
    ("Pérdidas de sistema (cables/conectores)", f"−{L_SYS:.1f} dB"),
    ("Potencia recibida (Prx)",                f"{prx:.1f} dBm"),
    ("Sensibilidad vídeo (300 Mbps)",          f"{SENS_VIDEO:.1f} dBm"),
    ("Margen de enlace para vídeo",            f"+{prx - SENS_VIDEO:.1f} dB"),
    ("Sensibilidad borde (54 Mbps)",           f"{SENS_BORDE:.1f} dBm"),
    ("Margen de enlace en borde de celda",     f"+{prx - SENS_BORDE:.1f} dB"),
]

# ---------------- figura sobria ----------------
plt.rcParams.update({"font.size": 11, "axes.titlesize": 12.5, "axes.titleweight": "bold"})
C_OK, C_OK_BG, C_HEAD = "#3E7D5A", "#E3EFE7", "#Ececec"
fig, ax = plt.subplots(figsize=(10.5, 6.2)); ax.axis("off")
cell_text, colors = [], []
resaltar = {"PIRE", "Potencia recibida (Prx)",
            "Margen de enlace para vídeo", "Margen de enlace en borde de celda"}
for concepto, val in detalle:
    cell_text.append([concepto, val])
    hl = concepto in resaltar
    colors.append([C_OK_BG if hl else "white", C_OK_BG if hl else "white"])
tab = ax.table(cellText=cell_text, colLabels=["Concepto", "Valor"],
               cellColours=colors, cellLoc="left", loc="center",
               colColours=[C_HEAD, C_HEAD], colWidths=[0.68, 0.32])
tab.auto_set_font_size(False); tab.set_fontsize(11); tab.scale(1, 1.55)
for (r, c), cell in tab.get_celld().items():
    cell.set_edgecolor("#CCC")
    if r == 0: cell.set_text_props(weight="bold")
    elif detalle[r-1][0] in resaltar: cell.set_text_props(weight="bold", color=C_OK)
    if c == 1 and r > 0: cell.PAD = 0.03
ax.set_title("Presupuesto de enlace — enlace Cardinal → LHD a distancia de diseño "
             f"({D_DISENO:.0f} m)\nRed IEEE 802.11ac · modelo de propagación two-slope calibrado",
             fontsize=12.5, pad=18)
plt.figtext(0.5, 0.03,
    f"El enlace más exigente (Cardinal, 23 dBm) mantiene un margen de "
    f"+{prx - SENS_VIDEO:.1f} dB sobre la sensibilidad de vídeo y "
    f"+{prx - SENS_BORDE:.1f} dB en el borde de celda: cobertura holgada para teleoperación.\n"
    f"El radio de diseño de {D_DISENO:.0f} m (espaciamiento de AP con solape) queda muy por "
    f"debajo del alcance máximo del modelo: {R_VIDEO:.0f} m para vídeo y {R_BORDE:.0f} m en borde.",
    ha="center", fontsize=9.5, style="italic", color="#444", wrap=True)
out = os.path.join(HERE, "link_budget.png")
plt.savefig(out, dpi=155, bbox_inches="tight"); plt.close()
print(f"\n[OK] {out}")

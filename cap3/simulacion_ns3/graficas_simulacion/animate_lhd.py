"""
Animación 2D real del recorrido LHD — Nivel 1640 Nexa Cerro Lindo — v9
Geometría con ramales oblicuos: BP 70°, Desmonte 65°
Lee: mobility_5hawks_real_v9_pos_log.csv (columnas x, y ya son coordenadas 2D reales)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
import math
import os

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "..", "results")
OUT_PATH    = os.path.join(SCRIPT_DIR, "animacion_lhd_v9.gif")

# ── Geometría v9 ────────────────────────────────────────────────────────────
ANGLE_BP_RAD  = math.radians(70.0)
ANGLE_DES_RAD = math.radians(65.0)
LONG_BP  = 55.0
LONG_DES = 48.0
BOCA_BP_X,  BOCA_BP_Y  = 183.7, 0.0
BOCA_DES_X, BOCA_DES_Y = 318.5, 0.0

END_BP_X  = BOCA_BP_X  + LONG_BP  * math.cos(ANGLE_BP_RAD)   # 202.5
END_BP_Y  = BOCA_BP_Y  + LONG_BP  * math.sin(ANGLE_BP_RAD)   # 51.7
END_DES_X = BOCA_DES_X + LONG_DES * math.cos(ANGLE_DES_RAD)  # 338.8
END_DES_Y = BOCA_DES_Y + LONG_DES * math.sin(ANGLE_DES_RAD)  # 43.5

CF_X = BOCA_BP_X  + 30.25 * math.cos(ANGLE_BP_RAD)  # 194.1
CF_Y = BOCA_BP_Y  + 30.25 * math.sin(ANGLE_BP_RAD)  # 28.4
H4_X = BOCA_DES_X + 26.4  * math.cos(ANGLE_DES_RAD) # 329.6
H4_Y = BOCA_DES_Y + 26.4  * math.sin(ANGLE_DES_RAD) # 23.9

HAWK_2D = [
    (0.0,   0.0, "H0"),
    (48.9,  0.0, "H1"),
    (183.7, 0.0, "H2"),
    (318.5, 0.0, "H3"),
    (H4_X,  H4_Y, "H4"),
]
CARDINAL_FIJO_2D = (CF_X, CF_Y)

# ── Cargar datos v9 ─────────────────────────────────────────────────────────
csv_path = os.path.join(RESULTS_DIR, "mobility_5hawks_real_v9_pos_log.csv")
df = pd.read_csv(csv_path)
# x, y ya son coordenadas 2D reales en v9
print(f"Cargado: {csv_path}  ({len(df)} filas)")

# ── Figura ───────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(15, 7), facecolor="#0f0f1a")
ax_map  = fig.add_axes([0.03, 0.13, 0.57, 0.78])
ax_rssi = fig.add_axes([0.64, 0.12, 0.34, 0.78])

for ax in (ax_map, ax_rssi):
    ax.set_facecolor("#16213e")
    ax.tick_params(colors="#90a4ae", labelsize=8)
    ax.xaxis.label.set_color("#90a4ae")
    ax.yaxis.label.set_color("#90a4ae")
    ax.title.set_color("white")
    for sp in ax.spines.values():
        sp.set_edgecolor("#2a2a4a")

# ── Mapa 2D estático ────────────────────────────────────────────────────────
W = 4.5   # ancho visual galería (m)

ax_map.set_xlim(-25, 370)
ax_map.set_ylim(-20, 68)
ax_map.set_aspect("equal")
ax_map.set_xlabel("X (m) — galería principal", fontsize=8)
ax_map.set_ylabel("Y (m) — ramales", fontsize=8)
ax_map.set_title("Recorrido LHD — Nexa Cerro Lindo NV1640 (v9)", fontsize=10)
ax_map.grid(True, color="#1e2a3a", linewidth=0.5, alpha=0.6)

def draw_tunnel_segment(ax, x0, y0, x1, y1, width, color, alpha=0.5):
    """Dibuja un segmento de galería con ancho visual."""
    dx = x1 - x0; dy = y1 - y0
    length = math.sqrt(dx**2 + dy**2)
    if length < 1e-6:
        return
    nx = -dy / length * width / 2
    ny =  dx / length * width / 2
    xs = [x0+nx, x1+nx, x1-nx, x0-nx, x0+nx]
    ys = [y0+ny, y1+ny, y1-ny, y0-ny, y0+ny]
    ax.fill(xs, ys, color=color, alpha=alpha, zorder=1)
    ax.plot([x0, x1], [y0, y1], color=color, lw=1.5, alpha=0.8, zorder=2)

# Galería principal
draw_tunnel_segment(ax_map, 0, 0, 318.5, 0, W, "#4FC3F7", alpha=0.3)

# Ramal BP (70°)
draw_tunnel_segment(ax_map, BOCA_BP_X, BOCA_BP_Y, END_BP_X, END_BP_Y, W, "#81C784", alpha=0.35)

# Ramal Desmonte (65°)
draw_tunnel_segment(ax_map, BOCA_DES_X, BOCA_DES_Y, END_DES_X, END_DES_Y, W, "#FFB74D", alpha=0.35)

# Anotación ángulos
ax_map.annotate("", xy=(BOCA_BP_X + 22*math.cos(ANGLE_BP_RAD),
                         22*math.sin(ANGLE_BP_RAD)),
                xytext=(BOCA_BP_X + 22, 0),
                arrowprops=dict(arrowstyle="-", color="#81C784", lw=1))
ax_map.text(BOCA_BP_X + 24, 6, "70°", color="#81C784", fontsize=8, fontstyle="italic")

ax_map.annotate("", xy=(BOCA_DES_X + 20*math.cos(ANGLE_DES_RAD),
                          20*math.sin(ANGLE_DES_RAD)),
                xytext=(BOCA_DES_X + 20, 0),
                arrowprops=dict(arrowstyle="-", color="#FFB74D", lw=1))
ax_map.text(BOCA_DES_X + 22, 5, "65°", color="#FFB74D", fontsize=8, fontstyle="italic")

# Distancias galería
for (x1v, x2v, lbl) in [(0, 48.9, "48.9 m"), (48.9, 183.7, "134.8 m"), (183.7, 318.5, "134.8 m")]:
    ax_map.annotate("", xy=(x2v, -8), xytext=(x1v, -8),
                    arrowprops=dict(arrowstyle="<->", color="#546e7a", lw=1))
    ax_map.text((x1v+x2v)/2, -11, lbl, ha="center", color="#78909c", fontsize=7)

# Extremos de ramales
ax_map.plot(END_BP_X,  END_BP_Y,  "D", color="#FFF176", markersize=9, zorder=6,
            markeredgecolor="white", markeredgewidth=0.8)
ax_map.text(END_BP_X+3, END_BP_Y+2, "Breakpoint\n(fondo)", color="#FFF176", fontsize=7.5)

ax_map.plot(END_DES_X, END_DES_Y, "D", color="#CE93D8", markersize=9, zorder=6,
            markeredgecolor="white", markeredgewidth=0.8)
ax_map.text(END_DES_X+3, END_DES_Y+2, "Desmonte\n(fondo)", color="#CE93D8", fontsize=7.5)

# Hawks
HAWK_COLORS = ["#1565C0", "#0277BD", "#00838F", "#2E7D32", "#558B2F"]
for (hx, hy, hl), hc in zip(HAWK_2D, HAWK_COLORS):
    ax_map.plot(hx, hy, "^", color=hc, markersize=13, zorder=7,
                markeredgecolor="white", markeredgewidth=1)
    ax_map.text(hx, hy - 5, hl, ha="center", color=hc, fontsize=8,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", fc="#0f0f1a", alpha=0.8, ec="none"))

# Cardinal fijo
ax_map.plot(CF_X, CF_Y, "s", color="#F48FB1", markersize=11, zorder=7,
            markeredgecolor="white", markeredgewidth=1)
ax_map.text(CF_X + 5, CF_Y + 2, "CardFijo", color="#F48FB1", fontsize=7.5,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="#0f0f1a", alpha=0.8, ec="none"))

# Portal
ax_map.plot(0, 0, "*", color="#FFD54F", markersize=14, zorder=8)
ax_map.text(2, -6, "Portal\nacceso", color="#FFD54F", fontsize=7)

# Objetos animados
lhd_dot,   = ax_map.plot([], [], "o", color="#FFEB3B", markersize=16,
                          zorder=10, markeredgecolor="#FF8F00", markeredgewidth=2)
lhd_trail, = ax_map.plot([], [], "-", color="#FFEB3B", linewidth=2.5,
                          alpha=0.4, zorder=9)
ap_line,   = ax_map.plot([], [], "--", color="white", linewidth=1.2,
                          alpha=0.5, zorder=8)

info_box = ax_map.text(2, 60, "", color="white", fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.5", fc="#0d1b2a",
                                  ec="#4FC3F7", alpha=0.92))
nlos_box = ax_map.text(160, 60, "", color="#FFB74D", fontsize=8.5,
                        bbox=dict(boxstyle="round,pad=0.4", fc="#1a0f00",
                                  ec="#FF8F00", alpha=0.9))

# Leyenda
leg_elements = [
    plt.Line2D([0],[0], marker="^", color="w", markerfacecolor="#4CAF50",
               markersize=10, ls="None", label="Hawk AP (H0–H4)"),
    plt.Line2D([0],[0], marker="s", color="w", markerfacecolor="#F48FB1",
               markersize=9,  ls="None", label="Cardinal fijo (ramal BP)"),
    plt.Line2D([0],[0], marker="o", color="w", markerfacecolor="#FFEB3B",
               markersize=10, ls="None", label="LHD Cardinal (móvil)"),
    plt.Line2D([0],[0], marker="D", color="w", markerfacecolor="#FFF176",
               markersize=8,  ls="None", label="Breakpoint / Desmonte"),
    mpatches.Patch(color="#4FC3F7", alpha=0.5, label="Galería principal"),
    mpatches.Patch(color="#81C784", alpha=0.5, label="Ramal BP (70°)"),
    mpatches.Patch(color="#FFB74D", alpha=0.5, label="Ramal Desmonte (65°)"),
]
ax_map.legend(handles=leg_elements, loc="upper left", fontsize=7,
              facecolor="#0f0f1a", edgecolor="#4FC3F7", labelcolor="white",
              ncol=2, framealpha=0.9)

# ── Panel RSSI ───────────────────────────────────────────────────────────────
NLOS_ZONES = [
    (38.9,  58.9,  "Giro\nH0-H1"),
    (173.7, 193.7, "Giro\nBP"),
    (183.7, 239.6, "Trans.\nBP"),
    (364.4, 384.4, "Giro\nDes."),
    (374.4, 426.3, "Trans.\nDes."),
]

ax_rssi.set_xlim(0, 430)
ax_rssi.set_ylim(-92, -20)
ax_rssi.set_xlabel("Distancia acumulada (m)", fontsize=8)
ax_rssi.set_ylabel("RSSI estimado (dBm)", fontsize=8)
ax_rssi.set_title("Señal recibida vs posición", fontsize=9)

for (x0, x1, lbl) in NLOS_ZONES:
    ax_rssi.axvspan(x0, x1, color="#FF6F00", alpha=0.15, zorder=0)
    ax_rssi.text((x0+x1)/2, -23, lbl, ha="center", color="#FFB74D",
                 fontsize=6.5, va="top")

ax_rssi.axhline(-75, color="#EF5350", lw=1.3, ls="--", alpha=0.7, label="Umbral −75 dBm")
ax_rssi.axhline(-91.8, color="#B71C1C", lw=1, ls=":", alpha=0.5, label="Piso ruido −91.8 dBm")

# Estaciones de los Hawks
HAWK_STATIONS = [0.0, 48.9, 183.7, 374.4, 400.3]
HAWK_LABELS   = ["H0", "H1", "H2", "H3", "H4"]
for hs, hl in zip(HAWK_STATIONS, HAWK_LABELS):
    ax_rssi.axvline(hs, color="#4CAF50", lw=1, ls=":", alpha=0.6)
    ax_rssi.text(hs, -21, hl, ha="center", color="#4CAF50", fontsize=7,
                 fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.1", fc="#0f0f1a", alpha=0.8, ec="none"))

rssi_line, = ax_rssi.plot([], [], color="#29B6F6", lw=1.5, alpha=0.9, label="RSSI")
rssi_dot,  = ax_rssi.plot([], [], "o", color="#FFEB3B", markersize=8, zorder=5)
ax_rssi.legend(fontsize=7.5, facecolor="#0f0f1a", edgecolor="#2a2a4a",
               labelcolor="white", loc="lower left")

# Título global
fig.text(0.5, 0.97,
         "Simulación NS-3 · Teleoperación LHD · Nexa Cerro Lindo NV1640 · v9",
         ha="center", color="white", fontsize=11, fontweight="bold")

# ── Animación ────────────────────────────────────────────────────────────────
STEP = 4   # cada N filas del CSV → 1 frame
frames_idx = list(range(0, len(df), STEP))

AP_XY = {
    "H0": (0.0, 0.0), "H1": (48.9, 0.0), "H2": (183.7, 0.0),
    "H3": (318.5, 0.0), "H4": (H4_X, H4_Y), "CardFijo": (CF_X, CF_Y),
}

def update(fi):
    idx     = frames_idx[fi]
    row     = df.iloc[idx]
    x2d     = float(row["x"])
    y2d     = float(row["y"])
    d1d     = float(row["station_m"])
    t       = float(row["time_s"])
    rssi    = float(row["rssi_dbm"])
    nlos_r  = str(row["nlos_region"])
    serving = str(row["serving_hawk"])

    # LHD en mapa
    lhd_dot.set_data([x2d], [y2d])
    trail = df.iloc[max(0, idx - 30):idx + 1]
    lhd_trail.set_data(trail["x"].values, trail["y"].values)

    # Línea al AP actual
    ax_x, ax_y = AP_XY.get(serving, (0.0, 0.0))
    ap_line.set_data([x2d, ax_x], [y2d, ax_y])

    # Texto info
    info_box.set_text(f"t = {t:.0f} s\nAP: {serving}\nRSSI: {rssi:.1f} dBm")

    if nlos_r not in ("LOS", "", "nan", "None"):
        nlos_box.set_text(f"⚠ NLOS: {nlos_r}")
    else:
        nlos_box.set_text("")

    # Panel RSSI
    hist = df.iloc[:idx + 1]
    rssi_line.set_data(hist["station_m"].values, hist["rssi_dbm"].values)
    rssi_dot.set_data([d1d], [rssi])

    return lhd_dot, lhd_trail, ap_line, info_box, nlos_box, rssi_line, rssi_dot

print(f"Generando animación v9 ({len(frames_idx)} frames, STEP={STEP}) ...")
anim = FuncAnimation(fig, update, frames=len(frames_idx), interval=80, blit=True)

writer = PillowWriter(fps=12)
anim.save(OUT_PATH, writer=writer)
print(f"GIF guardado: {OUT_PATH}")

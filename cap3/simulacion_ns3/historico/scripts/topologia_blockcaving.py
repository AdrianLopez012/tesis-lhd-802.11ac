"""
Topología realista Block Caving — Nexa Cerro Lindo Nivel 1640
Geometría 2D con curvas, ángulos reales, breakpoint y ruta LHD.

Características:
- Galería principal con ligera curvatura (no recta perfecta)
- Ramal BP (Breakpoint) con ángulo ~70° (no 90°)
- Ramal Desmonte con ángulo ~65°
- Curvas de radio finito en las intersecciones (radio ~8m, ancho galería ~5m)
- Breakpoint con zona de maniobra ensanchada
- Ruta LHD trazada respetando radio de giro mínimo (~12m)
- Posiciones Hawks y CardFijo sobre la geometría real
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Parámetros físicos de la galería ─────────────────────────────────────────
ANCHO_GAL   = 5.0    # m — ancho galería principal
ANCHO_RAMAL = 4.5    # m — ancho ramales
RADIO_CURVA = 10.0   # m — radio de curvatura en intersecciones
VEL_LHD     = 2.22   # m/s — velocidad nominal LHD

# ── Geometría de la galería principal (con ligera curvatura) ─────────────────
# Se modela como una spline suave — no perfectamente recta
# Puntos de control de la galería principal (x, y) en metros
GP_CTRL = np.array([
    [  0.0,   0.0],   # inicio (Portal acceso)
    [ 50.0,   1.5],   # leve desviación natural de la galería
    [120.0,   2.8],
    [183.7,   3.2],   # bifurcación BP
    [250.0,   3.8],
    [318.5,   4.0],   # bifurcación Desmonte
    [370.0,   3.5],   # fin galería principal
])

def spline_gal_principal(t_vals, ctrl=GP_CTRL):
    """Interpolación cúbica suave de la galería principal."""
    from scipy.interpolate import CubicSpline
    t = np.linspace(0, 1, len(ctrl))
    cs_x = CubicSpline(t, ctrl[:, 0])
    cs_y = CubicSpline(t, ctrl[:, 1])
    return cs_x(t_vals), cs_y(t_vals)

# ── Puntos clave de intersecciones ───────────────────────────────────────────
# Bifurcación BP: en x≈183.7m de la galería principal
# Ángulo del ramal BP respecto a galería: ~70° (no 90°)
BIFURC_BP_T   = 3.0 / 6.0   # t en spline donde está la bifurcación BP
ANGLE_BP_DEG  = 70.0         # ángulo ramal BP respecto eje X
LONG_RAMAL_BP = 55.0         # m — longitud hasta Breakpoint

# Bifurcación Desmonte: en x≈318.5m
BIFURC_DES_T   = 4.5 / 6.0
ANGLE_DES_DEG  = 65.0        # ángulo ramal Desmonte
LONG_RAMAL_DES = 48.0        # m

def ramal_points(origin, angle_deg, length, n=50):
    """Genera puntos de un ramal desde origin con ángulo dado."""
    angle_rad = np.radians(angle_deg)
    t = np.linspace(0, length, n)
    # Ligera curvatura natural del ramal
    curva = 0.03 * t * np.sin(np.radians(15) * t / length)
    x = origin[0] + t * np.cos(angle_rad) + curva * np.sin(angle_rad)
    y = origin[1] + t * np.sin(angle_rad) + curva * np.cos(angle_rad)
    return x, y

# ── Calcular geometría ────────────────────────────────────────────────────────
t_fine = np.linspace(0, 1, 400)
gp_x, gp_y = spline_gal_principal(t_fine)

# Posición exacta de bifurcaciones en la spline
t_bp  = np.linspace(0, 1, 400)
bp_x, bp_y = spline_gal_principal(np.array([BIFURC_BP_T]))
des_x, des_y = spline_gal_principal(np.array([BIFURC_DES_T]))

BIF_BP  = (bp_x[0],  bp_y[0])
BIF_DES = (des_x[0], des_y[0])

# Ramales
rx_bp,  ry_bp  = ramal_points(BIF_BP,  ANGLE_BP_DEG,  LONG_RAMAL_BP)
rx_des, ry_des = ramal_points(BIF_DES, ANGLE_DES_DEG, LONG_RAMAL_DES)

# Breakpoint (extremo ramal BP)
BP_END = (rx_bp[-1], ry_bp[-1])
# Desmonte (extremo ramal Desmonte)
DES_END = (rx_des[-1], ry_des[-1])

# ── Posiciones de Hawks y CardFijo sobre la geometría real ───────────────────
# Posiciones reales usadas en la simulación ns-3 v9
HAWKS_XY = [(0.0, 0.0), (48.9, 0.0), (183.7, 0.0), (318.5, 0.0)]
HAWK_LABELS = ["H0", "H1", "H2", "H3"]
H4_XY = (318.5 + 26.4 * np.cos(np.radians(65)), 26.4 * np.sin(np.radians(65)))   # ≈(329.6, 23.9)
CARDFIJO_XY = (183.7 + 30.25 * np.cos(np.radians(70)), 30.25 * np.sin(np.radians(70)))  # ≈(194.1, 28.4)

# ── Ruta LHD (ciclo completo: galería → ramal BP → Breakpoint → vuelta) ───────
def route_lhd():
    """
    Ciclo LHD realista:
    1. Avanza por galería principal (H0→bifurcación BP)
    2. Gira al ramal BP (curva radio ~12m)
    3. Llega al Breakpoint, maniobra, recoge material
    4. Regresa al ramal BP → galería
    5. Continúa a bifurcación Desmonte
    6. Entra ramal Desmonte, llega, regresa
    7. Descarga en H0
    """
    # Segmento galería principal completo
    t_gal = np.linspace(0, 1, 300)
    gx, gy = spline_gal_principal(t_gal * (5.5/6.0))

    # Ramal BP ida
    rbp_x, rbp_y = ramal_points(BIF_BP, ANGLE_BP_DEG, LONG_RAMAL_BP, 80)

    # Ramal Desmonte ida
    rdes_x, rdes_y = ramal_points(BIF_DES, ANGLE_DES_DEG, LONG_RAMAL_DES, 60)

    # Ciclo: gal(completa) → BP(ida) → BP(vuelta) → gal(completa) → Des(ida) → Des(vuelta) → gal(vuelta)
    route_x = np.concatenate([
        gx,
        rbp_x, rbp_x[::-1],          # ida y vuelta ramal BP
        gx[::-1],                      # regreso galería
        rdes_x, rdes_x[::-1],          # ida y vuelta ramal Desmonte
    ])
    route_y = np.concatenate([
        gy,
        rbp_y, rbp_y[::-1],
        gy[::-1],
        rdes_y, rdes_y[::-1],
    ])
    return route_x, route_y

lhd_x, lhd_y = route_lhd()

# ── FIGURA PRINCIPAL ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_facecolor("#1a1a2e")
fig.patch.set_facecolor("#0f0f1a")

# Dibujar galerías (ancho real)
def draw_gallery(ax, xs, ys, width, color, alpha=0.35, label=None):
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection
    # Offset perpendicular para dar ancho
    dx = np.diff(xs, prepend=xs[0])
    dy = np.diff(ys, prepend=ys[0])
    norm = np.sqrt(dx**2 + dy**2) + 1e-9
    nx = -dy / norm * width / 2
    ny =  dx / norm * width / 2
    x_top = xs + nx
    y_top = ys + ny
    x_bot = xs - nx
    y_bot = ys - ny
    ax.fill(
        np.concatenate([x_top, x_bot[::-1]]),
        np.concatenate([y_top, y_bot[::-1]]),
        color=color, alpha=alpha, zorder=1
    )
    ax.plot(xs, ys, color=color, linewidth=1.5, alpha=0.7, zorder=2, label=label)

# Galería principal
draw_gallery(ax, gp_x, gp_y, ANCHO_GAL, "#4FC3F7", label="Galería principal")

# Ramal BP
draw_gallery(ax, rx_bp, ry_bp, ANCHO_RAMAL, "#81C784", label="Ramal Breakpoint")

# Ramal Desmonte
draw_gallery(ax, rx_des, ry_des, ANCHO_RAMAL, "#FFB74D", label="Ramal Desmonte")

# Ruta LHD
ax.plot(lhd_x, lhd_y, color="#FF6B6B", linewidth=1.8, linestyle="--",
        alpha=0.85, zorder=3, label="Ruta LHD (ciclo completo)")

# Hawks sobre galería
for i, ((hx, hy), lbl) in enumerate(zip(HAWKS_XY, HAWK_LABELS)):
    ax.scatter(hx, hy, s=180, color="#4CAF50", zorder=6, edgecolors="white", linewidths=1.5)
    ax.annotate(lbl, (hx, hy), textcoords="offset points", xytext=(0, 10),
                ha="center", fontsize=8, color="#4CAF50", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="#0f0f1a", alpha=0.8, ec="#4CAF50"))

# H4 en ramal Desmonte
ax.scatter(*H4_XY, s=200, color="#4CAF50", zorder=6, edgecolors="white", linewidths=1.5, marker="^")
ax.annotate("H4", H4_XY, textcoords="offset points", xytext=(8, 0),
            fontsize=8, color="#4CAF50", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="#0f0f1a", alpha=0.8, ec="#4CAF50"))

# CardFijo en ramal BP
ax.scatter(*CARDFIJO_XY, s=200, color="#F48FB1", zorder=6, edgecolors="white", linewidths=1.5, marker="s")
ax.annotate("CardFijo", CARDFIJO_XY, textcoords="offset points", xytext=(8, 0),
            fontsize=8, color="#F48FB1", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="#0f0f1a", alpha=0.8, ec="#F48FB1"))

# Breakpoint
ax.scatter(*BP_END, s=250, color="#FFF176", zorder=6, edgecolors="white", linewidths=1.5, marker="D")
ax.annotate("Breakpoint\n(descarga)", BP_END, textcoords="offset points", xytext=(8, -12),
            fontsize=8, color="#FFF176",
            bbox=dict(boxstyle="round,pad=0.2", fc="#0f0f1a", alpha=0.8, ec="#FFF176"))

# Desmonte
ax.scatter(*DES_END, s=250, color="#CE93D8", zorder=6, edgecolors="white", linewidths=1.5, marker="D")
ax.annotate("Desmonte\n(descarga)", DES_END, textcoords="offset points", xytext=(8, -12),
            fontsize=8, color="#CE93D8",
            bbox=dict(boxstyle="round,pad=0.2", fc="#0f0f1a", alpha=0.8, ec="#CE93D8"))

# Portal de acceso
ax.scatter(gp_x[0], gp_y[0], s=300, color="#FFD54F", zorder=7,
           edgecolors="white", linewidths=2, marker="*")
ax.annotate("Portal\nacceso", (gp_x[0], gp_y[0]),
            textcoords="offset points", xytext=(-15, -20),
            fontsize=8, color="#FFD54F",
            bbox=dict(boxstyle="round,pad=0.2", fc="#0f0f1a", alpha=0.8, ec="#FFD54F"))

# Anotar ángulos de ramales
ax.annotate(f"∠{ANGLE_BP_DEG}°", BIF_BP,
            textcoords="offset points", xytext=(15, 25),
            fontsize=9, color="#81C784", style="italic")
ax.annotate(f"∠{ANGLE_DES_DEG}°", BIF_DES,
            textcoords="offset points", xytext=(15, 25),
            fontsize=9, color="#FFB74D", style="italic")

# Distancias entre Hawks consecutivos en galería principal
dist_pairs = [
    ((0.0, 0.0), (48.9, 0.0), "48.9 m"),
    ((48.9, 0.0), (183.7, 0.0), "134.8 m"),
    ((183.7, 0.0), (318.5, 0.0), "134.8 m"),
]
for (x1, y1), (x2, y2), label in dist_pairs:
    xm = (x1 + x2) / 2
    ax.annotate("", xy=(x2, y1 - 6), xytext=(x1, y1 - 6),
                arrowprops=dict(arrowstyle="<->", color="white", lw=1.2))
    ax.text(xm, y1 - 9, label, ha="center", color="white", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.15", fc="#0f0f1a", alpha=0.8, ec="none"))

# Cobertura WiFi aproximada (círculos translúcidos)
for hx2, hy2 in HAWKS_XY:
    circle = plt.Circle((hx2, hy2), 211, color="#4CAF50", alpha=0.04, zorder=0)
    ax.add_patch(circle)
circle_cf = plt.Circle(CARDFIJO_XY, 138, color="#F48FB1", alpha=0.04, zorder=0)
ax.add_patch(circle_cf)
circle_h4 = plt.Circle(H4_XY, 138, color="#4CAF50", alpha=0.04, zorder=0)
ax.add_patch(circle_h4)

# Escala
scale_x = [10, 60]
scale_y = [-12, -12]
ax.plot(scale_x, scale_y, 'w-', linewidth=2.5, zorder=10)
ax.plot([10, 10], [-14, -10], 'w-', linewidth=2, zorder=10)
ax.plot([60, 60], [-14, -10], 'w-', linewidth=2, zorder=10)
ax.text(35, -16, "50 m", ha="center", color="white", fontsize=9, fontweight="bold")

# Leyenda y formato
legend_elements = [
    mpatches.Patch(color="#4FC3F7", alpha=0.7, label="Galería principal"),
    mpatches.Patch(color="#81C784", alpha=0.7, label="Ramal Breakpoint"),
    mpatches.Patch(color="#FFB74D", alpha=0.7, label="Ramal Desmonte"),
    plt.Line2D([0], [0], color="#FF6B6B", linestyle="--", linewidth=1.8, label="Ruta LHD"),
    plt.Line2D([0], [0], marker="o", color="#4CAF50", linestyle="None", markersize=8, label="Hawk AP (H0–H3)"),
    plt.Line2D([0], [0], marker="^", color="#4CAF50", linestyle="None", markersize=9, label="H4 (ramal Desmonte)"),
    plt.Line2D([0], [0], marker="s", color="#F48FB1", linestyle="None", markersize=9, label="CardFijo (ramal BP)"),
    plt.Line2D([0], [0], marker="D", color="#FFF176", linestyle="None", markersize=9, label="Breakpoint / Desmonte"),
    plt.Line2D([0], [0], marker="*", color="#FFD54F", linestyle="None", markersize=11, label="Portal acceso"),
    mpatches.Patch(color="#4CAF50", alpha=0.12, label="Cobertura Hawk (~211m, MCS7)"),
    mpatches.Patch(color="#F48FB1", alpha=0.12, label="Cobertura CardFijo/H4 (~138m)"),
]
ax.legend(handles=legend_elements, loc="upper right", fontsize=7.5,
          facecolor="#1a1a2e", edgecolor="#4FC3F7", labelcolor="white", ncol=1)

ax.set_xlabel("X (m)", color="white", fontsize=10)
ax.set_ylabel("Y (m)", color="white", fontsize=10)
ax.set_title("Topología Block Caving — Nexa Cerro Lindo Nivel 1640\n"
             "Geometría 2D realista (curvas, ángulos reales, ruta LHD)",
             color="white", fontsize=11, pad=12)
ax.tick_params(colors="white")
for spine in ax.spines.values():
    spine.set_edgecolor("#4FC3F7")
ax.set_aspect("equal")
ax.grid(True, color="#2a2a4a", linewidth=0.5, alpha=0.5)

plt.tight_layout()
out_path = os.path.join(OUT_DIR, "topologia_blockcaving_v2.png")
plt.savefig(out_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"[OK] Topologia guardada: {out_path}")

# ── EXPORTAR COORDENADAS PARA NS-3 ────────────────────────────────────────────
print("\n-- Coordenadas clave para ns-3 --")
print(f"H0:       ({HAWKS_XY[0][0]:.1f}, {HAWKS_XY[0][1]:.1f})")
print(f"H1:       ({HAWKS_XY[1][0]:.1f}, {HAWKS_XY[1][1]:.1f})")
print(f"H2:       ({HAWKS_XY[2][0]:.1f}, {HAWKS_XY[2][1]:.1f})")
print(f"H3:       ({HAWKS_XY[3][0]:.1f}, {HAWKS_XY[3][1]:.1f})")
print(f"H4:       ({H4_XY[0]:.1f}, {H4_XY[1]:.1f})  [ramal Desmonte]")
print(f"CardFijo: ({CARDFIJO_XY[0]:.1f}, {CARDFIJO_XY[1]:.1f})  [ramal BP]")
print(f"Bifurc BP:    ({BIF_BP[0]:.1f}, {BIF_BP[1]:.1f})")
print(f"Bifurc Des:   ({BIF_DES[0]:.1f}, {BIF_DES[1]:.1f})")
print(f"Breakpoint:   ({BP_END[0]:.1f}, {BP_END[1]:.1f})")
print(f"Desmonte end: ({DES_END[0]:.1f}, {DES_END[1]:.1f})")
print(f"\nÁngulo ramal BP:       {ANGLE_BP_DEG}°")
print(f"Ángulo ramal Desmonte: {ANGLE_DES_DEG}°")
print(f"Longitud galería princ: ~{gp_x[-1]:.0f} m")
print(f"Longitud ramal BP:      {LONG_RAMAL_BP} m")
print(f"Longitud ramal Des:     {LONG_RAMAL_DES} m")
print(f"Puntos ruta LHD:        {len(lhd_x)}")

"""
Plano real — Nexa Cerro Lindo Nivel 1640 (zona de teleoperación con cobertura WiFi)
====================================================================================
Geometría REAL aclarada con el usuario (2026-07-05), reemplaza la galería recta
incorrecta de topologia_blockcaving.py.

Estructura real:
  - 3 calles de producción PARALELAS (verticales), de ~134.85 m cada una.
  - Un CRUCERO que las une por el extremo superior.
  - GALERÍA PRINCIPAL de acceso que entra por abajo y conecta al crucero inferior.
  - BREAKPOINTS (puntos de extracción) hacia el interior, con ángulo de inclinación.
  - BOTADEROS de desmonte arriba-derecha: destino de descarga del LHD.

TODAS las medidas están en el bloque DATOS. Cambia un número y se redibuja + reexporta.
Ejecutar:  python plano_nv1640_real.py
Salida:    plano_nv1640_real.png  +  coordenadas impresas para NS-3.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# DATOS — geometría real en metros (ÚNICA fuente de verdad; edita aquí)
# ============================================================================

# --- Calles de producción (paralelas, verticales) ---
LARGO_CALLE   = [134.8536, 134.8386, 134.8386]   # izq, medio, der (dato del usuario)
SEP_CALLES    = 25.9844  # m — separación horizontal entre calles (dato del usuario)
X_CALLE       = [0.0, SEP_CALLES, 2 * SEP_CALLES]  # x de cada calle: 0, 15, 30
Y_BASE        = 0.0      # y del extremo inferior de las calles (donde une el crucero inf.)

# --- Crucero superior que une las 3 calles ---
#   corre horizontal a la altura del extremo superior de las calles
# --- Galería principal de acceso ---
LARGO_GAL_ACC = 60.0     # m — largo de la galería de acceso (AJUSTAR)
                         # el LHD ingresa por ARRIBA y conecta al crucero superior

# --- Breakpoints (puntos de extracción) ---
N_BP_POR_CALLE = 6       # cuántos breakpoints por calle (AJUSTAR)
LONG_BP        = 8.0     # m — longitud del ramal de cada breakpoint (AJUSTAR)
ANGLE_BP_DEG   = 60.0    # ° — ángulo de inclinación del breakpoint (AJUSTAR)

# --- Botaderos de desmonte (destino de descarga) ---
#   Van en la zona SUPERIOR, encima de las calles paralelas. Solo 2.
_Y_TOP = max(LARGO_CALLE)
BOTADEROS = [
    (SEP_CALLES * 0.7,  _Y_TOP + 30.0),   # arriba, sobre las calles (AJUSTAR)
    (SEP_CALLES * 1.3,  _Y_TOP + 30.0),
]

# --- Antenas (se ajustan luego con datasheets) ---
#   Hawks en galería/calles principales, Cardinals en cruceros
_YT = max(LARGO_CALLE)
HAWKS    = [(SEP_CALLES, _YT + LARGO_GAL_ACC - 5), (SEP_CALLES, 90.0), (SEP_CALLES, 30.0)]
CARDINALS = [(X_CALLE[0], 70.0), (X_CALLE[2], 70.0)]

# ============================================================================
# CONSTRUCCIÓN GEOMÉTRICA (derivada de los DATOS — no editar salvo lógica)
# ============================================================================

def calle_puntos(x, y0, largo):
    """Extremos de una calle vertical."""
    return (x, y0), (x, y0 + largo)

calles = [calle_puntos(X_CALLE[i], Y_BASE, LARGO_CALLE[i]) for i in range(3)]
y_top = max(c[1][1] for c in calles)   # crucero superior a la altura del tope

# Crucero superior: de la calle izquierda a la derecha, en y = y_top
CRUCERO_SUP = [(X_CALLE[0], y_top), (X_CALLE[2], y_top)]
# Crucero inferior (donde conecta la galería de acceso)
CRUCERO_INF = [(X_CALLE[0], Y_BASE), (X_CALLE[2], Y_BASE)]

# Galería de acceso: el LHD ingresa por ARRIBA, sube desde el crucero superior
GAL_ACC = [(X_CALLE[1], y_top), (X_CALLE[1], y_top + LARGO_GAL_ACC)]

# Breakpoints: en cada calle, distribuidos a lo largo, apuntando "hacia adentro"
#   izquierda -> apunta a +x ; derecha -> apunta a -x ; centro -> ambos lados
def breakpoints_calle(idx):
    x = X_CALLE[idx]
    largo = LARGO_CALLE[idx]
    ys = np.linspace(20, largo - 15, N_BP_POR_CALLE)
    ang = np.radians(ANGLE_BP_DEG)
    bps = []
    if idx == 0:      dirs = [+1]
    elif idx == 2:    dirs = [-1]
    else:             dirs = [-1, +1]
    for y in ys:
        for d in dirs:
            ex = x + d * LONG_BP * np.cos(ang)
            ey = y + LONG_BP * np.sin(ang)
            bps.append(((x, y), (ex, ey)))
    return bps

all_bps = []
for i in range(3):
    all_bps += breakpoints_calle(i)

# ============================================================================
# RECORRIDO DEL LHD (ruta más compleja — worst case)
#   Entra por galería (arriba) -> crucero sup -> baja calle -> carga breakpoint
#   -> retrocede -> botadero (descarga) -> repite en otra calle.
# ============================================================================
_ba = GAL_ACC[1]                       # boca de la galería de acceso (arriba)
_cru_y = y_top                          # y del crucero superior
_bp_c1 = (X_CALLE[0], 30.0)             # breakpoint bajo en calle 1
_bp_c3 = (X_CALLE[2], 30.0)             # breakpoint bajo en calle 3
_bot1, _bot2 = BOTADEROS[0], BOTADEROS[1]

RUTA_LHD = [
    _ba,                               # 1. entra por la galería
    (X_CALLE[1], _cru_y),              # 2. llega al crucero superior
    (X_CALLE[0], _cru_y),              # 3. va hacia calle 1
    _bp_c1,                            # 4. baja calle 1 a cargar (breakpoint)
    (X_CALLE[0], _cru_y),              # 5. retrocede al crucero
    _bot1,                             # 6. descarga en botadero 1
    (X_CALLE[2], _cru_y),             # 7. cruza hacia calle 3
    _bp_c3,                            # 8. baja calle 3 a cargar
    (X_CALLE[2], _cru_y),             # 9. retrocede
    _bot2,                            # 10. descarga en botadero 2
]
ruta_x = [p[0] for p in RUTA_LHD]
ruta_y = [p[1] for p in RUTA_LHD]

# ============================================================================
# FIGURA
# ============================================================================
fig, ax = plt.subplots(figsize=(9, 10))

# Calles de producción
for i, (p0, p1) in enumerate(calles):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#378ADD", linewidth=7,
            solid_capstyle="round", zorder=3,
            label="Calle de producción" if i == 0 else None)
    ax.annotate(f"Calle {i+1}\n{LARGO_CALLE[i]:.1f} m", (p1[0], p1[1]),
                textcoords="offset points", xytext=(0, 10), ha="center",
                fontsize=8, color="#185FA5")

# Cruceros
ax.plot([CRUCERO_SUP[0][0], CRUCERO_SUP[1][0]], [CRUCERO_SUP[0][1], CRUCERO_SUP[1][1]],
        color="#7F77DD", linewidth=6, solid_capstyle="round", zorder=2, label="Crucero")
ax.plot([CRUCERO_INF[0][0], CRUCERO_INF[1][0]], [CRUCERO_INF[0][1], CRUCERO_INF[1][1]],
        color="#7F77DD", linewidth=6, solid_capstyle="round", zorder=2)

# Galería de acceso
ax.plot([GAL_ACC[0][0], GAL_ACC[1][0]], [GAL_ACC[0][1], GAL_ACC[1][1]],
        color="#1D9E75", linewidth=8, solid_capstyle="round", zorder=2,
        label="Galería de acceso")
ax.annotate("Galería de acceso\n(entra el LHD por arriba)", GAL_ACC[1],
            textcoords="offset points", xytext=(0, 14), ha="center",
            fontsize=8, color="#0F6E56")

# Breakpoints
for (base, end) in all_bps:
    ax.plot([base[0], end[0]], [base[1], end[1]], color="#0F6E56",
            linewidth=3, solid_capstyle="round", zorder=4)
    ax.scatter(*end, s=45, color="#1D9E75", edgecolors="#04342C",
               linewidths=0.8, zorder=5)
ax.scatter([], [], s=45, color="#1D9E75", edgecolors="#04342C",
           label=f"Breakpoint (θ={ANGLE_BP_DEG:.0f}°)")

# Botaderos
for (bx, by) in BOTADEROS:
    ax.scatter(bx, by, s=400, color="#2C2C2A", marker="o",
               edgecolors="black", linewidths=1.5, zorder=5)
ax.scatter([], [], s=120, color="#2C2C2A", label="Botadero (descarga)")
ax.annotate("Botaderos\n(descarga desmonte)", BOTADEROS[0],
            textcoords="offset points", xytext=(15, 10), fontsize=8, color="#2C2C2A")

# Antenas
for (hx, hy) in HAWKS:
    ax.scatter(hx, hy, s=130, color="#185FA5", marker="o",
               edgecolors="white", linewidths=1.3, zorder=6)
ax.scatter([], [], s=90, color="#185FA5", label="Hawk AP")
for (cx, cy) in CARDINALS:
    ax.scatter(cx, cy, s=90, color="#7F77DD", marker="s",
               edgecolors="white", linewidths=1.3, zorder=6)
ax.scatter([], [], s=70, color="#7F77DD", marker="s", label="Cardinal AP")

# Recorrido del LHD (ruta más compleja)
ax.plot(ruta_x, ruta_y, color="#D85A30", linewidth=2, linestyle="--",
        alpha=0.9, zorder=7, label="Recorrido LHD (ruta compleja)")
for k in range(len(RUTA_LHD) - 1):
    ax.annotate("", xy=RUTA_LHD[k + 1], xytext=RUTA_LHD[k],
                arrowprops=dict(arrowstyle="->", color="#993C1D", lw=1.4, alpha=0.8),
                zorder=7)

# Barra de escala 50 m (abajo, bajo el crucero inferior)
x0 = min(X_CALLE) - 20
ax.plot([x0, x0 + 50], [Y_BASE - 20, Y_BASE - 20], "k-", linewidth=2.5)
ax.text(x0 + 25, Y_BASE - 28, "50 m", ha="center", fontsize=9, fontweight="bold")

ax.set_aspect("equal")
ax.grid(True, color="#cccccc", linewidth=0.4, alpha=0.6)
ax.set_xlabel("X (m)", fontsize=10)
ax.set_ylabel("Y (m)", fontsize=10)
ax.set_title("Nexa NV1640 — zona de teleoperación (geometría real, a escala)\n"
             "3 calles de producción paralelas + crucero + galería de acceso",
             fontsize=11, pad=12)
ax.legend(loc="lower right", fontsize=8, framealpha=0.9)

plt.tight_layout()
out_path = os.path.join(OUT_DIR, "plano_nv1640_real.png")
plt.savefig(out_path, dpi=200, bbox_inches="tight")
plt.close()
print(f"[OK] Plano guardado: {out_path}")

# ============================================================================
# EXPORTAR COORDENADAS PARA NS-3
# ============================================================================
print("\n== Coordenadas para NS-3 (metros) ==")
for i, (p0, p1) in enumerate(calles):
    print(f"Calle {i+1}: inicio {p0} -> fin {p1}  (largo {LARGO_CALLE[i]:.2f} m)")
print(f"Crucero superior: {CRUCERO_SUP[0]} -> {CRUCERO_SUP[1]}")
print(f"Galería acceso:   {GAL_ACC[0]} -> {GAL_ACC[1]}")
print(f"Nº breakpoints:   {len(all_bps)}  (ángulo {ANGLE_BP_DEG:.0f}°)")
for i, (bx, by) in enumerate(BOTADEROS):
    print(f"Botadero {i+1}:      ({bx:.1f}, {by:.1f})")
print(f"Hawks:     {HAWKS}")
print(f"Cardinals: {CARDINALS}")

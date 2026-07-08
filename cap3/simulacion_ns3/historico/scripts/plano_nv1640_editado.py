"""
Plano NV1640 — geometría trazada por el usuario en el editor visual (2026-07-06)
=================================================================================
Reproduce a escala real el mapa que el usuario dibujó: rampas de acceso (con
curvatura), calles de producción (contorno + calles verticales + costillas en
espina de pescado), drawpoints (punto + acceso en ángulo) y botaderos.

Coordenadas en METROS (ya convertidas por el editor con escala 30 m/px).
Origen abajo-izquierda. Editar los datos de abajo para ajustar.
Ejecutar:  python plano_nv1640_editado.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# DATOS — export del editor (metros). 'curva' = índice de vértice con curvatura.
# ============================================================================
RAMPAS = [
    # Rampa 1 (con curvatura en 2 vértices)
    {"pts": [(696.0,1648.1),(8976.0,3180.9),(9080.0,19303.2),(11960.0,22335.7),
             (22520.0,22495.4),(28360.0,30001.1)], "curvas": [2,4]},
    # Rampa 2
    {"pts": [(28560.0,7886.8),(9000.0,7966.7)], "curvas": []},
]

PRODUCCION = [
    [(28280.0,30039.8),(47680.0,30079.7),(47680.0,7767.1),(34360.0,7727.2)],  # contorno
    [(40240.0,30081.0),(40240.0,8126.3)],
    [(34040.0,30120.9),(34200.0,7886.8)],
    [(33920.0,25330.8),(40040.0,27884.3)],
    [(33880.0,21498.7),(47320.0,24372.8)],
    [(34080.0,8006.6),(34080.0,7966.7),(28480.0,7966.7)],
    [(34040.0,17906.1),(47360.0,21418.9)],
    [(34040.0,15072.0),(47440.0,18504.9)],
    [(34000.0,12676.9),(47440.0,16030.0)],
    [(34160.0,10321.8),(37240.0,10721.0)],
    [(40160.0,12158.0),(47400.0,13954.3)],
    [(40040.0,10840.7),(43920.0,11319.7)],
    [(33880.0,30199.5),(33720.0,35189.2)],
    [(40040.0,30063.5),(40080.0,35252.8)],
]

# Drawpoints: (punto, base_acceso, ángulo)
DRAWPOINTS = [
    ((36920.0,26726.7),(36971.2,26603.9),113),
    ((36960.0,22337.0),(36996.7,22165.2),102),
    ((43920.0,23933.7),(43978.9,23658.3),102),
    ((37000.0,18944.0),(37063.4,18703.5),105),
    ((43920.0,20660.4),(43956.7,20521.4),105),
    ((37120.0,16189.7),(37199.0,15881.3),104),
    ((37160.0,13714.8),(37218.6,13479.9),104),
    ((43640.0,17786.4),(43701.3,17547.1),104),
    ((43480.0,15351.4),(43552.7,15060.2),104),
    ((37120.0,10960.5),(37152.5,10709.6),97),
    ((43800.0,11399.6),(43811.5,11306.3),97),
    ((43520.0,13275.7),(43586.4,13008.1),104),
]

BOTADEROS = [(33640.0,35133.0),(39880.0,35292.7)]

# ============================================================================
# RECALIBRADO A ESCALA REAL
# El editor usó 30 m/px pero eso infló las distancias. Recalibramos con el dato
# real del usuario: la calle de producción vertical mide 134.85 m.
# Factor = 134.85 / (largo de esa calle en unidades del editor) = 0.006065.
# También se traslada el origen al mínimo (x,y) para que empiece cerca de (0,0).
# ============================================================================
SCALE = 0.006065

def _all_pts():
    for r in RAMPAS:
        for p in r["pts"]:
            yield p
    for cam in PRODUCCION:
        for p in cam:
            yield p
    for pt, base, _ in DRAWPOINTS:
        yield pt; yield base
    for b in BOTADEROS:
        yield b

_xs = [p[0] for p in _all_pts()]
_ys = [p[1] for p in _all_pts()]
_OX, _OY = min(_xs), min(_ys)

def _sc(p):
    return ((p[0]-_OX)*SCALE, (p[1]-_OY)*SCALE)

RAMPAS     = [{"pts":[_sc(p) for p in r["pts"]], "curvas":r["curvas"]} for r in RAMPAS]
PRODUCCION = [[_sc(p) for p in cam] for cam in PRODUCCION]
DRAWPOINTS = [(_sc(pt), _sc(base), ang) for (pt, base, ang) in DRAWPOINTS]
BOTADEROS  = [_sc(b) for b in BOTADEROS]

# ============================================================================
# DIBUJO
# ============================================================================
def quad_bezier(p0, p1, p2, n=24):
    t = np.linspace(0, 1, n)[:, None]
    return (1-t)**2*np.array(p0) + 2*(1-t)*t*np.array(p1) + t**2*np.array(p2)

def draw_camino(ax, pts, curvas, color, lw):
    """Dibuja una polilínea; en los vértices marcados como 'curva' usa una
    curva cuadrática suave usando el propio vértice como control."""
    pts = [np.array(p, float) for p in pts]
    for i in range(len(pts)-1):
        a, b = pts[i], pts[i+1]
        if i in curvas and 0 < i < len(pts):
            # control = vértice actual desplazado (suaviza el codo)
            ctrl = a
            prev = pts[i-1]
            mid_in = (prev + a) / 2
            seg = quad_bezier(mid_in, a, b)
            ax.plot(seg[:,0], seg[:,1], color=color, lw=lw, solid_capstyle="round", zorder=3)
        else:
            ax.plot([a[0],b[0]], [a[1],b[1]], color=color, lw=lw, solid_capstyle="round", zorder=3)

fig, ax = plt.subplots(figsize=(11, 10))

for r in RAMPAS:
    draw_camino(ax, r["pts"], r["curvas"], "#BA7517", 4.5)
for cam in PRODUCCION:
    draw_camino(ax, cam, [], "#378ADD", 5.5)

# Drawpoints: acceso en ángulo ~45° respecto a la calle (provisional, a validar).
# La calle de producción es vertical, así que el acceso sale a 45° del eje Y.
# El drawpoint queda a la izq o der según su posición; el acceso arranca en la
# calle a la misma altura del punto y se abre 45° hacia el drawpoint.
ANG_DRAWPOINT = 45.0  # ° respecto a la calle de producción (PROVISIONAL — validar)
_LARGO_ACCESO = 12.0  # m — largo del ramal de acceso (aprox)

for (pt, base, _ang_old) in DRAWPOINTS:
    px, py = pt
    # dirección horizontal hacia donde está el drawpoint respecto a su base
    lado = 1.0 if (px - base[0]) >= 0 else -1.0
    a = np.radians(ANG_DRAWPOINT)
    # base del acceso: sobre la vertical de la calle, desplazada en Y para que
    # el ramal de largo fijo a 45° llegue al drawpoint
    bx = px - lado * _LARGO_ACCESO * np.sin(a)
    by = py - _LARGO_ACCESO * np.cos(a)
    ax.plot([bx, px], [by, py], color="#0F6E56", lw=3, solid_capstyle="round", zorder=4)
    ax.scatter(px, py, s=90, color="#1D9E75", edgecolors="#04342C", linewidths=1.2, zorder=5)
    ax.annotate(f"{ANG_DRAWPOINT:.0f}°", pt, textcoords="offset points", xytext=(6,4),
                fontsize=7, color="#0F6E56")

# Botaderos
for b in BOTADEROS:
    ax.scatter(*b, s=340, color="#2C2C2A", edgecolors="black", linewidths=1.4, zorder=5)
ax.scatter([], [], s=120, color="#2C2C2A", label="Botadero (descarga)")

# Leyenda
ax.plot([],[], color="#BA7517", lw=4, label="Rampa de acceso")
ax.plot([],[], color="#378ADD", lw=5, label="Calle de producción")
ax.plot([],[], color="#0F6E56", lw=3, label="Acceso a drawpoint (ángulo)")
ax.scatter([],[], s=80, color="#1D9E75", edgecolors="#04342C", label="Drawpoint")

# Escala 50 m (recalibrada)
_ymin = min(b[1] for b in BOTADEROS + [p for cam in PRODUCCION for p in cam])
ax.plot([0, 50], [-15, -15], "k-", lw=2.5)
ax.text(25, -25, "50 m", ha="center", fontsize=9, fontweight="bold")

ax.set_aspect("equal")
ax.grid(True, color="#dddddd", lw=0.4, alpha=0.6)
ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)")
ax.set_title("Nexa NV1640 — geometría real (trazada por el usuario, escala calibrada)", fontsize=12, pad=10)
ax.legend(loc="upper left", fontsize=8, framealpha=0.9)

plt.tight_layout()
out = os.path.join(OUT_DIR, "plano_nv1640_editado.png")
plt.savefig(out, dpi=160, bbox_inches="tight")
plt.close()
print(f"[OK] {out}")
print(f"Rampas: {len(RAMPAS)} | Calles producción: {len(PRODUCCION)} | "
      f"Drawpoints: {len(DRAWPOINTS)} | Botaderos: {len(BOTADEROS)}")

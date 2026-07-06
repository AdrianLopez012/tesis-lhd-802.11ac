"""
Plano NV1640 — versión profesional para tesis (2026-07-06)
==========================================================
Toma la geometría trazada por el usuario en el editor visual y la renderiza
como un PLANO MINERO de calidad: galerías con ancho real (polígonos), estilo
cuidado, drawpoints y botaderos bien representados, tipografía y leyenda limpias.

Reutiliza los datos de plano_nv1640_editado.py (misma geometría y escala).
Ejecutar:  python plano_nv1640_pro.py  ->  plano_nv1640_pro.png
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon as MplPoly
from matplotlib.lines import Line2D
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# DATOS (mismos del editor) — metros tras recalibrar
# ============================================================================
RAMPAS = [
    {"pts": [(696.0,1648.1),(8976.0,3180.9),(9080.0,19303.2),(11960.0,22335.7),
             (22520.0,22495.4),(28360.0,30001.1)], "curvas": [2,4]},
    {"pts": [(28560.0,7886.8),(9000.0,7966.7)], "curvas": []},
]
PRODUCCION = [
    [(28280.0,30039.8),(47680.0,30079.7),(47680.0,7767.1),(34360.0,7727.2)],
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
DRAWPOINTS = [
    ((36920.0,26726.7),(36971.2,26603.9)),((36960.0,22337.0),(36996.7,22165.2)),
    ((43920.0,23933.7),(43978.9,23658.3)),((37000.0,18944.0),(37063.4,18703.5)),
    ((43920.0,20660.4),(43956.7,20521.4)),((37120.0,16189.7),(37199.0,15881.3)),
    ((37160.0,13714.8),(37218.6,13479.9)),((43640.0,17786.4),(43701.3,17547.1)),
    ((43480.0,15351.4),(43552.7,15060.2)),((37120.0,10960.5),(37152.5,10709.6)),
    ((43800.0,11399.6),(43811.5,11306.3)),((43520.0,13275.7),(43586.4,13008.1)),
]
BOTADEROS = [(33640.0,35133.0),(39880.0,35292.7)]

# ============================================================================
# RECALIBRADO A ESCALA REAL (calle vertical = 134.85 m)
# ============================================================================
SCALE = 0.006065
def _all():
    for r in RAMPAS:
        for p in r["pts"]: yield p
    for cam in PRODUCCION:
        for p in cam: yield p
    for pt, base in DRAWPOINTS: yield pt; yield base
    for b in BOTADEROS: yield b
_OX = min(p[0] for p in _all()); _OY = min(p[1] for p in _all())
def sc(p): return ((p[0]-_OX)*SCALE, (p[1]-_OY)*SCALE)
RAMPAS     = [{"pts":[sc(p) for p in r["pts"]],"curvas":r["curvas"]} for r in RAMPAS]
PRODUCCION = [[sc(p) for p in cam] for cam in PRODUCCION]
DRAWPOINTS = [(sc(pt), sc(base)) for pt, base in DRAWPOINTS]
BOTADEROS  = [sc(b) for b in BOTADEROS]

# ============================================================================
# PALETA Y ESTILO
# ============================================================================
BG        = "#F7F5EF"   # fondo tipo papel
ROCK      = "#EDE9DF"   # relleno macizo
C_PROD    = "#2E6FB0"   # producción (azul)
C_PROD_ED = "#1B4C7E"
C_RAMPA   = "#C08422"   # rampa (ocre)
C_RAMPA_ED= "#8A5D12"
C_DRAW    = "#1E9E77"   # drawpoint (verde)
C_DRAW_ED = "#0C5B41"
C_BOT     = "#33322E"   # botadero
C_ACCESO  = "#0F6E56"
INK       = "#2B2B28"

W_PROD  = 5.5   # ancho galería producción (m)
W_RAMPA = 5.0   # ancho rampa (m)
W_ACC   = 3.5   # ancho acceso drawpoint

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": INK, "axes.linewidth": 1.1,
    "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK,
})

# ============================================================================
# UTILIDADES DE DIBUJO CON ANCHO (galerías como polígonos)
# ============================================================================
def resample_curve(pts, curvas):
    """Devuelve una polilínea densa, insertando curvas cuadráticas suaves en
    los vértices marcados."""
    pts = [np.array(p, float) for p in pts]
    out = [pts[0]]
    for i in range(len(pts)-1):
        a, b = pts[i], pts[i+1]
        if i in curvas and 0 < i:
            prev = pts[i-1]
            mid = (prev + a)/2
            t = np.linspace(0,1,20)[:,None]
            seg = (1-t)**2*mid + 2*(1-t)*t*a + t**2*b
            out.extend(seg[1:])
        else:
            out.append(b)
    return np.array(out)

def ribbon(ax, xy, width, face, edge, z=2):
    """Dibuja una polilínea como cinta de ancho fijo (galería con paredes)."""
    xy = np.asarray(xy, float)
    if len(xy) < 2: return
    d = np.diff(xy, axis=0)
    seg_n = np.zeros_like(xy)
    nrm = np.zeros_like(xy)
    # normales por vértice (promedio de segmentos adyacentes)
    dirs = d/ (np.linalg.norm(d,axis=1,keepdims=True)+1e-9)
    vdir = np.zeros_like(xy)
    vdir[0]=dirs[0]; vdir[-1]=dirs[-1]
    vdir[1:-1]=(dirs[:-1]+dirs[1:])
    vdir/= (np.linalg.norm(vdir,axis=1,keepdims=True)+1e-9)
    normal = np.stack([-vdir[:,1], vdir[:,0]],axis=1)
    top = xy + normal*width/2
    bot = xy - normal*width/2
    poly = np.vstack([top, bot[::-1]])
    ax.add_patch(MplPoly(poly, closed=True, facecolor=face, edgecolor=edge,
                         linewidth=1.1, joinstyle="round", zorder=z))

# ============================================================================
# FIGURA
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 10))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# macizo rocoso de fondo (halo suave bajo la zona de producción)
xs=[p[0] for cam in PRODUCCION for p in cam]; ys=[p[1] for cam in PRODUCCION for p in cam]
pad=14
ax.add_patch(FancyBboxPatch((min(xs)-pad, min(ys)-pad),
             (max(xs)-min(xs))+2*pad, (max(ys)-min(ys))+2*pad,
             boxstyle="round,pad=2,rounding_size=8",
             facecolor=ROCK, edgecolor="none", zorder=0))

# Rampas (con ancho + curva)
for r in RAMPAS:
    dense = resample_curve(r["pts"], r["curvas"])
    ribbon(ax, dense, W_RAMPA, C_RAMPA, C_RAMPA_ED, z=2)

# Producción (con ancho)
for cam in PRODUCCION:
    dense = resample_curve(cam, [])
    ribbon(ax, dense, W_PROD, C_PROD, C_PROD_ED, z=3)

# Accesos a drawpoints (a 45° respecto a la calle vertical) + drawpoint
ANG = np.radians(45.0); LACC = 11.0
for (pt, base) in DRAWPOINTS:
    px,py = pt
    lado = 1.0 if (px-base[0])>=0 else -1.0
    bx = px - lado*LACC*np.sin(ANG); by = py - LACC*np.cos(ANG)
    ribbon(ax, [(bx,by),(px,py)], W_ACC, "#BFE3D5", C_ACCESO, z=4)
    ax.add_patch(Circle((px,py), 2.6, facecolor=C_DRAW, edgecolor=C_DRAW_ED,
                        linewidth=1.3, zorder=6))

# Botaderos (símbolo de descarga: círculo con V invertida)
for (bx,by) in BOTADEROS:
    ax.add_patch(Circle((bx,by), 4.6, facecolor=C_BOT, edgecolor="#000", linewidth=1.2, zorder=6))
    ax.plot([bx-2.2,bx,bx+2.2],[by+1.4,by-1.8,by+1.4], color="#F7F5EF", lw=1.6, zorder=7)

# ---- Escala gráfica tipo plano ----
x0 = min(xs); y0 = min(ys)-24
for k in range(5):
    ax.add_patch(plt.Rectangle((x0+k*10, y0), 10, 2.4,
                 facecolor=INK if k%2==0 else BG, edgecolor=INK, lw=0.8, zorder=8))
ax.text(x0, y0-6, "0", ha="center", fontsize=8)
ax.text(x0+50, y0-6, "50 m", ha="center", fontsize=8, fontweight="bold")

# ---- Flecha norte simple ----
nx, ny = max(xs)+2, max(ys)+2
ax.annotate("N", xy=(nx,ny+14), xytext=(nx,ny),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6),
            ha="center", fontsize=11, fontweight="bold")

# ---- Leyenda ----
leg = [
    Line2D([0],[0], color=C_RAMPA, lw=7, label="Rampa de acceso"),
    Line2D([0],[0], color=C_PROD,  lw=7, label="Galería de producción"),
    Line2D([0],[0], color=C_ACCESO,lw=5, label="Acceso a drawpoint (45°)"),
    Line2D([0],[0], marker="o", color="none", markerfacecolor=C_DRAW,
           markeredgecolor=C_DRAW_ED, markersize=11, label="Drawpoint (extracción)"),
    Line2D([0],[0], marker="o", color="none", markerfacecolor=C_BOT,
           markeredgecolor="#000", markersize=13, label="Botadero (descarga)"),
]
lg = ax.legend(handles=leg, loc="upper left", fontsize=10, frameon=True,
               framealpha=0.96, edgecolor=INK, borderpad=0.9, labelspacing=0.8)
lg.get_frame().set_facecolor("#FFFFFF")

ax.set_aspect("equal")
ax.grid(True, color="#D8D3C6", lw=0.5, alpha=0.7, zorder=0)
ax.set_xlabel("Distancia X (m)", fontsize=11)
ax.set_ylabel("Distancia Y (m)", fontsize=11)
ax.set_title("Nivel de producción NV1640 — Nexa Cerro Lindo\n"
             "Zona de teleoperación LHD (geometría real, escala 1:1)",
             fontsize=14, fontweight="bold", pad=14)

# márgenes
ax.set_xlim(min(xs)-30, max(xs)+30)
ax.set_ylim(min(ys)-40, max(ys)+30)

plt.tight_layout()
out = os.path.join(OUT_DIR, "plano_nv1640_pro.png")
plt.savefig(out, dpi=170, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"[OK] {out}")

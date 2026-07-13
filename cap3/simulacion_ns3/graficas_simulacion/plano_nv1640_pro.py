"""
Plano NV1640 profesional — dibujo por capas, sin solapamientos (2026-07-06)
==========================================================================
Lee mapa_nv1640_datos.py y dibuja un plano minero limpio:
  - Galerías dibujadas como capilla UNIFICADA (relleno primero sin bordes, luego
    un solo halo de contorno) para que los cruces se fundan sin líneas internas
    ni solapamientos feos.
  - Costillas en espina de pescado unidas limpiamente a las galerías.
  - Drawbell al centro + drawpoints a los costados (El Teniente).
  - Rampa suave, botaderos, leyenda FUERA del dibujo, lienzo grande.

Ejecutar:  python plano_nv1640_pro.py  ->  plano_nv1640_pro.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon as MplPoly
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
import os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("datos", os.path.join(HERE,"mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

# ---- estilo ----
BG="#F7F5EF"; ROCK="#E9E4D8"; INK="#2B2B28"
C_PROD="#2E6FB0"; C_PROD_ED="#173F66"; C_RAMPA="#C08422"; C_RAMPA_ED="#7A5210"
C_DRAW="#1E9E77"; C_DRAW_ED="#0C5B41"; C_BELL="#C9B98A"; C_BELL_ED="#7A6A3A"; C_BOT="#33322E"
W_PROD=5.0; W_RAMPA=5.0
plt.rcParams.update({"font.family":"DejaVu Sans","axes.edgecolor":INK,"axes.linewidth":1.2,
    "text.color":INK,"axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK})

def bezier(p0,p1,p2,n=20):
    t=np.linspace(0,1,n)[:,None]
    return (1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t**2*np.array(p2)

def densify(pts,curvas,fillet=16.0):
    pts=[np.array(p,float) for p in pts]
    if len(pts)==2: return np.array(pts)
    out=[pts[0]]
    for i in range(1,len(pts)-1):
        prev,cur,nxt=pts[i-1],pts[i],pts[i+1]
        if i in curvas:
            din=np.linalg.norm(cur-prev); dout=np.linalg.norm(nxt-cur)
            r=min(fillet,din*0.45,dout*0.45)
            pin=cur+(prev-cur)/(din+1e-9)*r; pout=cur+(nxt-cur)/(dout+1e-9)*r
            out.append(pin); out.extend(bezier(pin,cur,pout)[1:]); out.append(pout)
        else: out.append(cur)
    out.append(pts[-1]); return np.array(out)

def polyline_segments(paths, width):
    """Devuelve lista de polilíneas densas (para dibujar como LineCollection con
    capas: una gruesa de contorno + una fina de relleno, todas del mismo color,
    de modo que los cruces se funden sin solapamientos visibles)."""
    return [densify(p["pts"] if isinstance(p,dict) else p,
                    p.get("curvas",[]) if isinstance(p,dict) else []) for p in paths]

# ---- figura (lienzo grande) ----
fig,ax=plt.subplots(figsize=(15,12)); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

allpts=[p for cam in D.PRODUCCION for p in cam]+[p for r in D.RAMPAS for p in r["pts"]]+D.DRAWBELLS+D.DRAWPOINTS+D.BOTADEROS
xs=[p[0] for p in allpts]; ys=[p[1] for p in allpts]
px=[p[0] for cam in D.PRODUCCION for p in cam if p[0]>-30]; py=[p[1] for cam in D.PRODUCCION for p in cam]

# macizo de fondo
ax.add_patch(FancyBboxPatch((min(px)-14,min(py)-16),(max(px)-min(px))+28,(max(py)-min(py))+34,
    boxstyle="round,pad=2,rounding_size=10",facecolor=ROCK,edgecolor="none",zorder=0))

# ---- CAPA 1: contorno (líneas gruesas del mismo color-borde) ----
# ---- CAPA 2: relleno (líneas finas del color claro) ----
# Al usar capround y mismo color, todos los cruces se funden sin bordes internos.
def draw_network(paths, width, face, edge, z):
    segs=polyline_segments(paths,width)
    # capa contorno (un poco más ancha, color borde)
    lc_edge=LineCollection(segs,colors=edge,linewidths=width+2.2,capstyle="round",
                           joinstyle="round",zorder=z)
    # capa relleno (color claro encima)
    lc_face=LineCollection(segs,colors=face,linewidths=width,capstyle="round",
                           joinstyle="round",zorder=z+0.1)
    ax.add_collection(lc_edge); ax.add_collection(lc_face)

# escala: matplotlib LineCollection usa puntos; convertimos ancho m->pts según data.
# Para 1:1 aproximado usamos un factor visual (las galerías se ven a ~ancho real).
def m2lw(width_m):
    # ancho de línea en puntos proporcional; ajustado para figsize/escala actual
    return width_m*2.6

draw_network(D.RAMPAS, m2lw(W_RAMPA), C_RAMPA, C_RAMPA_ED, z=2)
draw_network(D.PRODUCCION, m2lw(W_PROD), C_PROD, C_PROD_ED, z=4)

# drawbells / drawpoints / botaderos
for (x,y) in D.DRAWBELLS:
    s=3.2; ax.add_patch(MplPoly([(x,y+s),(x+s,y),(x,y-s),(x-s,y)],closed=True,
        facecolor=C_BELL,edgecolor=C_BELL_ED,linewidth=1.2,zorder=7))
for (x,y) in D.DRAWPOINTS:
    ax.add_patch(Circle((x,y),2.3,facecolor=C_DRAW,edgecolor=C_DRAW_ED,linewidth=1.3,zorder=8))
for (x,y) in D.BOTADEROS:
    ax.add_patch(Circle((x,y),4.8,facecolor=C_BOT,edgecolor="#000",linewidth=1.3,zorder=8))
    ax.plot([x-2.3,x,x+2.3],[y+1.5,y-1.9,y+1.5],color=BG,lw=1.7,zorder=9)

# AP de la red (posiciones reales del plano): Hawk triángulo, Cardinal cuadrado
for (hx,hy) in D.HAWKS:
    ax.scatter(hx,hy,s=150,marker="^",c="#1565C0",edgecolors="#FFF",linewidths=1.4,zorder=11)
for (cx,cy) in D.CARDINALS_AP:
    ax.scatter(cx,cy,s=120,marker="s",c="#7B1FA2",edgecolors="#FFF",linewidths=1.4,zorder=11)

# escala gráfica
x0=min(px); y0=min(py)-26
for k in range(5):
    ax.add_patch(plt.Rectangle((x0+k*10,y0),10,2.6,facecolor=INK if k%2==0 else "#FFF",
                 edgecolor=INK,lw=0.9,zorder=10))
ax.text(x0,y0-7,"0",ha="center",fontsize=9); ax.text(x0+50,y0-7,"50 m",ha="center",fontsize=9,fontweight="bold")

# flecha norte
nx,ny=max(px)+20,max(py)+14
ax.annotate("N",xy=(nx,ny+15),xytext=(nx,ny),
    arrowprops=dict(arrowstyle="-|>",color=INK,lw=1.8),ha="center",fontsize=12,fontweight="bold")

# leyenda FUERA del dibujo (a la derecha)
leg=[Line2D([0],[0],color=C_RAMPA,lw=8,label="Rampa de acceso"),
     Line2D([0],[0],color=C_PROD,lw=8,label="Galería de producción"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_DRAW,markeredgecolor=C_DRAW_ED,markersize=11,label="Drawpoint (extracción)"),
     Line2D([0],[0],marker="D",color="none",markerfacecolor=C_BELL,markeredgecolor=C_BELL_ED,markersize=11,label="Drawbell (mineral compartido)"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_BOT,markeredgecolor="#000",markersize=13,label="Pique de traspaso (descarga)"),
     Line2D([0],[0],marker="^",color="none",markerfacecolor="#1565C0",markeredgecolor="#FFF",markersize=12,label="AP Hawk (30 dBm / 11 dBi)"),
     Line2D([0],[0],marker="s",color="none",markerfacecolor="#7B1FA2",markeredgecolor="#FFF",markersize=11,label="AP Cardinal (23 dBm / 7.5 dBi)")]
lg=ax.legend(handles=leg,loc="upper left",bbox_to_anchor=(1.01,1.0),fontsize=11,
             frameon=True,framealpha=1.0,edgecolor=INK,borderpad=1.0,labelspacing=1.0)
lg.get_frame().set_facecolor("#FFFFFF")

ax.set_aspect("equal"); ax.grid(True,color="#DED9CC",lw=0.5,alpha=0.6,zorder=0)
ax.set_xlabel("Distancia X (m)",fontsize=12); ax.set_ylabel("Distancia Y (m)",fontsize=12)
ax.set_title("Nivel de producción NV1640 — Nexa Cerro Lindo\n"
             "Zona de teleoperación LHD · sección 4×4 m · layout El Teniente · escala 1:1",
             fontsize=14,fontweight="bold",pad=16)
ax.set_xlim(min(xs)-25,max(xs)+30); ax.set_ylim(min(ys)-35,max(ys)+25)

plt.tight_layout()
out=os.path.join(HERE,"plano_nv1640_pro.png")
plt.savefig(out,dpi=160,bbox_inches="tight",facecolor=BG); plt.close()
print(f"[OK] {out}")
print(f"Producción: {len(D.PRODUCCION)} | Rampas: {len(D.RAMPAS)} | "
      f"Drawbells: {len(D.DRAWBELLS)} | Drawpoints: {len(D.DRAWPOINTS)} | Botaderos: {len(D.BOTADEROS)}")

"""
Plano NV1640 profesional — usa la geometría EDITADA POR EL USUARIO
==================================================================
Lee mapa_nv1640_datos.py (geometría real trazada por el usuario en el editor
visual) y la dibuja como plano minero de calidad: galerías con ancho 4 m
(SEC 4x4), curvas donde el usuario las marcó, drawbells compartidos (El Teniente),
drawpoints, rampa y botaderos. Escala real 1:1.

Ejecutar:  python plano_nv1640_pro.py  ->  plano_nv1640_pro.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon as MplPoly
from matplotlib.lines import Line2D
import os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("datos", os.path.join(HERE,"mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

# ---- estilo ----
BG="#F7F5EF"; ROCK="#EDE9DF"; INK="#2B2B28"
C_PROD="#2E6FB0"; C_PROD_ED="#1B4C7E"; C_RAMPA="#C08422"; C_RAMPA_ED="#8A5D12"
C_DRAW="#1E9E77"; C_DRAW_ED="#0C5B41"; C_BELL="#C9B98A"; C_BELL_ED="#7A6A3A"; C_BOT="#33322E"
W_PROD=4.0; W_RAMPA=4.0
plt.rcParams.update({"font.family":"DejaVu Sans","axes.edgecolor":INK,"axes.linewidth":1.1,
    "text.color":INK,"axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK})

def bezier(p0,p1,p2,n=22):
    t=np.linspace(0,1,n)[:,None]
    return (1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t**2*np.array(p2)

def densify(pts, curvas, fillet=16.0):
    """Polilínea densa con REDONDEO local (fillet) en los vértices marcados.
    En un vértice 'curva' se toma un punto a distancia 'fillet' hacia atrás y
    hacia adelante, y se traza una Bézier entre ellos usando el vértice como
    control. Así la esquina se redondea sin dispararse, aunque los segmentos
    sean largos."""
    pts=[np.array(p,float) for p in pts]
    out=[pts[0]]
    for i in range(1,len(pts)-1):
        prev,cur,nxt=pts[i-1],pts[i],pts[i+1]
        if i in curvas:
            din=np.linalg.norm(cur-prev); dout=np.linalg.norm(nxt-cur)
            r=min(fillet, din*0.45, dout*0.45)
            p_in = cur + (prev-cur)/ (din+1e-9)*r
            p_out= cur + (nxt-cur)/ (dout+1e-9)*r
            out.append(p_in)
            out.extend(bezier(p_in,cur,p_out)[1:])
            out.append(p_out)
        else:
            out.append(cur)
    out.append(pts[-1])
    return np.array(out)

def ribbon(ax,xy,width,face,edge,z=2):
    xy=np.asarray(xy,float)
    if len(xy)<2:return
    d=np.diff(xy,axis=0); dirs=d/(np.linalg.norm(d,axis=1,keepdims=True)+1e-9)
    vdir=np.zeros_like(xy); vdir[0]=dirs[0]; vdir[-1]=dirs[-1]
    vdir[1:-1]=dirs[:-1]+dirs[1:]; vdir/=(np.linalg.norm(vdir,axis=1,keepdims=True)+1e-9)
    normal=np.stack([-vdir[:,1],vdir[:,0]],axis=1)
    poly=np.vstack([xy+normal*width/2,(xy-normal*width/2)[::-1]])
    ax.add_patch(MplPoly(poly,closed=True,facecolor=face,edgecolor=edge,
                 linewidth=1.0,joinstyle="round",zorder=z))

# ---- figura ----
fig,ax=plt.subplots(figsize=(13,10)); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

# límites globales
allpts=[p for cam in D.PRODUCCION for p in cam]+[p for r in D.RAMPAS for p in r["pts"]]+D.DRAWBELLS+D.DRAWPOINTS+D.BOTADEROS
xs=[p[0] for p in allpts]; ys=[p[1] for p in allpts]

# macizo de fondo (solo zona de producción, no la rampa larga)
px=[p[0] for cam in D.PRODUCCION for p in cam if p[0]>-30]
py=[p[1] for cam in D.PRODUCCION for p in cam]
ax.add_patch(FancyBboxPatch((min(px)-12,min(py)-12),(max(px)-min(px))+24,(max(py)-min(py))+24,
    boxstyle="round,pad=2,rounding_size=8",facecolor=ROCK,edgecolor="none",zorder=0))

# rampas
for r in D.RAMPAS:
    ribbon(ax,densify(r["pts"],r["curvas"]),W_RAMPA,C_RAMPA,C_RAMPA_ED,z=2)
# galerías de producción
for cam in D.PRODUCCION:
    ribbon(ax,densify(cam,[]),W_PROD,C_PROD,C_PROD_ED,z=3)
# drawbells
for (x,y) in D.DRAWBELLS:
    s=3.2
    ax.add_patch(MplPoly([(x,y+s),(x+s,y),(x,y-s),(x-s,y)],closed=True,
        facecolor=C_BELL,edgecolor=C_BELL_ED,linewidth=1.1,zorder=5))
# drawpoints
for (x,y) in D.DRAWPOINTS:
    ax.add_patch(Circle((x,y),2.4,facecolor=C_DRAW,edgecolor=C_DRAW_ED,linewidth=1.2,zorder=6))
# botaderos
for (x,y) in D.BOTADEROS:
    ax.add_patch(Circle((x,y),4.6,facecolor=C_BOT,edgecolor="#000",linewidth=1.2,zorder=6))
    ax.plot([x-2.2,x,x+2.2],[y+1.4,y-1.8,y+1.4],color=BG,lw=1.6,zorder=7)

# escala gráfica
x0=min(px); y0=min(py)-24
for k in range(5):
    ax.add_patch(plt.Rectangle((x0+k*10,y0),10,2.4,facecolor=INK if k%2==0 else BG,
                 edgecolor=INK,lw=0.8,zorder=8))
ax.text(x0,y0-6,"0",ha="center",fontsize=8); ax.text(x0+50,y0-6,"50 m",ha="center",fontsize=8,fontweight="bold")

# flecha norte
nx,ny=max(px)+16,max(py)+8
ax.annotate("N",xy=(nx,ny+14),xytext=(nx,ny),
    arrowprops=dict(arrowstyle="-|>",color=INK,lw=1.6),ha="center",fontsize=11,fontweight="bold")

# leyenda
leg=[Line2D([0],[0],color=C_RAMPA,lw=7,label="Rampa de acceso"),
     Line2D([0],[0],color=C_PROD,lw=7,label="Galería de producción"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_DRAW,markeredgecolor=C_DRAW_ED,markersize=10,label="Drawpoint (extracción)"),
     Line2D([0],[0],marker="D",color="none",markerfacecolor=C_BELL,markeredgecolor=C_BELL_ED,markersize=10,label="Drawbell (mineral compartido)"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_BOT,markeredgecolor="#000",markersize=12,label="Botadero (descarga)")]
lg=ax.legend(handles=leg,loc="lower left",fontsize=10,frameon=True,framealpha=0.96,
             edgecolor=INK,borderpad=0.9,labelspacing=0.7,bbox_to_anchor=(0.0,0.0))
lg.get_frame().set_facecolor("#FFFFFF")

ax.set_aspect("equal"); ax.grid(True,color="#D8D3C6",lw=0.5,alpha=0.7,zorder=0)
ax.set_xlabel("Distancia X (m)",fontsize=11); ax.set_ylabel("Distancia Y (m)",fontsize=11)
ax.set_title("Nivel de producción NV1640 — Nexa Cerro Lindo\n"
             "Zona de teleoperación LHD · sección 4×4 m · layout El Teniente · escala 1:1",
             fontsize=13,fontweight="bold",pad=14)
ax.set_xlim(min(xs)-15,max(xs)+20); ax.set_ylim(min(ys)-30,max(ys)+20)

plt.tight_layout()
out=os.path.join(HERE,"plano_nv1640_pro.png")
plt.savefig(out,dpi=170,bbox_inches="tight",facecolor=BG); plt.close()
print(f"[OK] {out}")
print(f"Producción: {len(D.PRODUCCION)} | Rampas: {len(D.RAMPAS)} | "
      f"Drawbells: {len(D.DRAWBELLS)} | Drawpoints: {len(D.DRAWPOINTS)} | Botaderos: {len(D.BOTADEROS)}")

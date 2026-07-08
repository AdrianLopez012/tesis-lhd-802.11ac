"""
Plano NV1640 con AP y COBERTURA (2026-07-06)
============================================
Dibuja el mapa + las antenas AP (Hawk y Cardinal) ubicadas por el usuario, con
su radio de cobertura, para verificar que el recorrido del LHD queda cubierto.
Lee mapa_nv1640_datos.py. Reutiliza el estilo del plano profesional.

Ejecutar:  python plano_nv1640_cobertura.py  ->  plano_nv1640_cobertura.png
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon as MplPoly
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
import os, importlib.util

HERE=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("datos",os.path.join(HERE,"mapa_nv1640_datos.py"))
D=importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

BG="#F7F5EF"; ROCK="#E9E4D8"; INK="#2B2B28"
C_PROD="#2E6FB0"; C_PROD_ED="#173F66"; C_RAMPA="#C08422"; C_RAMPA_ED="#7A5210"
C_DRAW="#1E9E77"; C_DRAW_ED="#0C5B41"; C_BELL="#C9B98A"; C_BELL_ED="#7A6A3A"; C_BOT="#33322E"
C_HAWK="#1565C0"; C_CARD="#7B1FA2"
W=4.0
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
def draw_net(ax,paths,width,face,edge,z):
    segs=[densify(p["pts"] if isinstance(p,dict) else p, p.get("curvas",[]) if isinstance(p,dict) else []) for p in paths]
    ax.add_collection(LineCollection(segs,colors=edge,linewidths=width+2.2,capstyle="round",joinstyle="round",zorder=z))
    ax.add_collection(LineCollection(segs,colors=face,linewidths=width,capstyle="round",joinstyle="round",zorder=z+0.1))

fig,ax=plt.subplots(figsize=(15,12)); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
allpts=[p for cam in D.PRODUCCION for p in cam]+[p for r in D.RAMPAS for p in r["pts"]]+D.BOTADEROS+D.HAWKS+D.CARDINALS_AP
xs=[p[0] for p in allpts]; ys=[p[1] for p in allpts]
px=[p[0] for cam in D.PRODUCCION for p in cam if p[0]>-30]; py=[p[1] for cam in D.PRODUCCION for p in cam]
ax.add_patch(FancyBboxPatch((min(px)-14,min(py)-16),(max(px)-min(px))+28,(max(py)-min(py))+34,
    boxstyle="round,pad=2,rounding_size=10",facecolor=ROCK,edgecolor="none",zorder=0))

# COBERTURA de los AP (círculos translúcidos) — primero, debajo de todo
R=D.COBERTURA_AP
for (x,y) in D.HAWKS:
    ax.add_patch(Circle((x,y),R,facecolor=C_HAWK,edgecolor="none",alpha=0.06,zorder=0.5))
for (x,y) in D.CARDINALS_AP:
    ax.add_patch(Circle((x,y),R*0.7,facecolor=C_CARD,edgecolor="none",alpha=0.06,zorder=0.5))

draw_net(ax,D.RAMPAS,W*2.6,C_RAMPA,C_RAMPA_ED,2)
draw_net(ax,D.PRODUCCION,W*2.6,C_PROD,C_PROD_ED,4)
for (x,y) in D.DRAWBELLS:
    s=3.2; ax.add_patch(MplPoly([(x,y+s),(x+s,y),(x,y-s),(x-s,y)],closed=True,facecolor=C_BELL,edgecolor=C_BELL_ED,linewidth=1.2,zorder=7))
for (x,y) in D.DRAWPOINTS: ax.add_patch(Circle((x,y),2.3,facecolor=C_DRAW,edgecolor=C_DRAW_ED,linewidth=1.3,zorder=8))
for (x,y) in D.BOTADEROS:
    ax.add_patch(Circle((x,y),4.8,facecolor=C_BOT,edgecolor="#000",linewidth=1.3,zorder=8))
    ax.plot([x-2.3,x,x+2.3],[y+1.5,y-1.9,y+1.5],color=BG,lw=1.7,zorder=9)

# AP encima
for i,(x,y) in enumerate(D.HAWKS):
    ax.add_patch(Circle((x,y),3.4,facecolor=C_HAWK,edgecolor="#fff",linewidth=1.6,zorder=12))
    ax.annotate(f"H{i+1}",(x,y),textcoords="offset points",xytext=(5,4),fontsize=9,fontweight="bold",color=C_HAWK,zorder=12)
for i,(x,y) in enumerate(D.CARDINALS_AP):
    ax.add_patch(Circle((x,y),3.0,facecolor=C_CARD,edgecolor="#fff",linewidth=1.5,zorder=12))
    ax.annotate(f"C{i+1}",(x,y),textcoords="offset points",xytext=(5,4),fontsize=9,fontweight="bold",color=C_CARD,zorder=12)

# leyenda
leg=[Line2D([0],[0],color=C_RAMPA,lw=8,label="Rampa de acceso"),
     Line2D([0],[0],color=C_PROD,lw=8,label="Galería de producción"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_DRAW,markeredgecolor=C_DRAW_ED,markersize=11,label="Drawpoint"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_BOT,markeredgecolor="#000",markersize=13,label="Pique de traspaso"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_HAWK,markeredgecolor="#fff",markersize=12,label=f"AP Hawk (cobertura {int(R)}m)"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_CARD,markeredgecolor="#fff",markersize=11,label=f"AP Cardinal (cobertura {int(R*0.7)}m)")]
lg=ax.legend(handles=leg,loc="upper left",bbox_to_anchor=(1.01,1.0),fontsize=11,frameon=True,framealpha=1.0,edgecolor=INK,borderpad=1.0,labelspacing=1.0)
lg.get_frame().set_facecolor("#FFFFFF")

ax.set_aspect("equal"); ax.grid(True,color="#DED9CC",lw=0.5,alpha=0.6,zorder=0)
ax.set_xlabel("Distancia X (m)",fontsize=12); ax.set_ylabel("Distancia Y (m)",fontsize=12)
ax.set_title("NV1640 — Cobertura de AP sobre la zona de teleoperación\n"
             f"{len(D.HAWKS)} AP Hawk + {len(D.CARDINALS_AP)} AP Cardinal · mesh InstaMesh + backbone",
             fontsize=14,fontweight="bold",pad=16)
ax.set_xlim(min(xs)-25,max(xs)+30); ax.set_ylim(min(ys)-35,max(ys)+25)

plt.tight_layout()
out=os.path.join(HERE,"plano_nv1640_cobertura.png")
plt.savefig(out,dpi=160,bbox_inches="tight",facecolor=BG); plt.close()
print(f"[OK] {out}")
print(f"AP Hawk: {len(D.HAWKS)} | AP Cardinal: {len(D.CARDINALS_AP)} | cobertura {R}m")

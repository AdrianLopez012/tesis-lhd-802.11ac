"""
Plano NV1640 — versión profesional REGULARIZADA para tesis (2026-07-06)
======================================================================
El dibujo del usuario en el editor fue una GUÍA (trazos aproximados). Aquí la
geometría se REGULARIZA en un plano limpio y coherente:

  - 2 galerías de producción principales, verticales y paralelas.
  - Costillas diagonales parejas (espina de pescado), cada una TERMINA en su
    drawpoint. El ángulo lo lleva la costilla azul; el drawpoint es solo el
    punto verde al final (sin acceso separado).
  - Rampa de acceso suave (arriba) + rama inferior.
  - 2 botaderos arriba (descarga).

Todo parametrizado en metros. Editar el bloque PARÁMETROS para ajustar.
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
# PARÁMETROS (metros) — geometría regularizada a partir de la guía del usuario
# ============================================================================
LARGO_CALLE   = 134.85     # largo de cada galería de producción (dato real)
SEP_CALLES    = 25.98      # separación entre las 2 galerías principales (dato real)
X_C1          = 200.0      # x de la galería 1
X_C2          = X_C1 + SEP_CALLES   # x de la galería 2
Y_BASE        = 35.0       # y del extremo inferior (crucero inferior)
Y_TOP         = Y_BASE + LARGO_CALLE

N_DRAWBELLS   = 6          # nº de drawbells compartidos (pares de drawpoints)
ANG_COSTILLA  = 35.0       # ° de la costilla respecto a la horizontal (espina)
DRAWPT_OFFSET = 6.0        # separación del drawpoint respecto al drawbell (m)

# Rampa de acceso (arriba) y rama inferior — trazo suave
RAMPA_SUP = [(150.0, 138.0),(168.0,168.0),(200.0,Y_TOP)]   # llega al crucero superior izq
RAMPA_INF = [(150.0, Y_BASE),(190.0,Y_BASE)]               # rama inferior

# Botaderos (arriba, sobre las galerías)
BOTADEROS = [(X_C1, Y_TOP+30.0),(X_C2, Y_TOP+30.0)]

# ============================================================================
# CONSTRUCCIÓN — layout EL TENIENTE: pares de drawpoints comparten drawbell
# El drawbell (punto de mineral) está en el centro entre las 2 galerías.
# De cada galería sale una costilla en ángulo que converge al drawbell; el
# drawpoint (punto verde) es la boca al final de cada costilla, junto al drawbell.
# ============================================================================
X_MID = (X_C1 + X_C2) / 2.0

def drawbells():
    ys = np.linspace(Y_BASE+18, Y_TOP-16, N_DRAWBELLS)
    a  = np.radians(ANG_COSTILLA)
    out = []
    for y in ys:
        db = (X_MID, y)                       # drawbell común (centro)
        # costilla desde galería 1 (izq) hacia el drawbell
        dp1 = (X_MID - DRAWPT_OFFSET, y)      # drawpoint lado 1
        b1  = (X_C1, y - DRAWPT_OFFSET*np.tan(np.radians(90-ANG_COSTILLA)))
        # costilla desde galería 2 (der) hacia el drawbell
        dp2 = (X_MID + DRAWPT_OFFSET, y)      # drawpoint lado 2
        b2  = (X_C2, y - DRAWPT_OFFSET*np.tan(np.radians(90-ANG_COSTILLA)))
        out.append({"db": db, "dp1": dp1, "dp2": dp2,
                    "seg1": [b1, dp1], "seg2": [b2, dp2]})
    return out

DBELLS = drawbells()

# Galerías principales (verticales) + cruceros que las unen
GAL_1 = [(X_C1,Y_BASE),(X_C1,Y_TOP)]
GAL_2 = [(X_C2,Y_BASE),(X_C2,Y_TOP)]
CRU_SUP = [(X_C1,Y_TOP),(X_C2,Y_TOP)]
CRU_INF = [(X_C1,Y_BASE),(X_C2,Y_BASE)]
# tramos verticales cortos que suben a los botaderos
SUBE_BOT = [[(X_C1,Y_TOP),(X_C1,Y_TOP+26)],[(X_C2,Y_TOP),(X_C2,Y_TOP+26)]]

# ============================================================================
# ESTILO
# ============================================================================
BG="#F7F5EF"; ROCK="#EDE9DF"; INK="#2B2B28"
C_PROD="#2E6FB0"; C_PROD_ED="#1B4C7E"
C_RAMPA="#C08422"; C_RAMPA_ED="#8A5D12"
C_DRAW="#1E9E77"; C_DRAW_ED="#0C5B41"; C_BOT="#33322E"
# Anchos reales del plano AutoCAD: SEC. 4X4 = galería de 4 m de ancho.
# R4.5 = radio de curva 4.5 m en los codos del camino.
W_PROD=4.0; W_RAMPA=4.0   # sección 4x4 m (dato del plano)
RADIO_CURVA=4.5           # R4.5 m (dato del plano)

plt.rcParams.update({"font.family":"DejaVu Sans","axes.edgecolor":INK,
    "axes.linewidth":1.1,"text.color":INK,"axes.labelcolor":INK,
    "xtick.color":INK,"ytick.color":INK})

def smooth(pts):
    pts=[np.array(p,float) for p in pts]
    if len(pts)<3: return np.array(pts)
    out=[pts[0]]
    for i in range(1,len(pts)-1):
        prev,cur,nxt=pts[i-1],pts[i],pts[i+1]
        t=np.linspace(0,1,16)[:,None]
        seg=(1-t)**2*((prev+cur)/2)+2*(1-t)*t*cur+t**2*((cur+nxt)/2)
        out.extend(seg)
    out.append(pts[-1])
    return np.array(out)

def ribbon(ax,xy,width,face,edge,z=2):
    xy=np.asarray(xy,float)
    if len(xy)<2:return
    d=np.diff(xy,axis=0); dirs=d/(np.linalg.norm(d,axis=1,keepdims=True)+1e-9)
    vdir=np.zeros_like(xy); vdir[0]=dirs[0]; vdir[-1]=dirs[-1]
    vdir[1:-1]=dirs[:-1]+dirs[1:]; vdir/=(np.linalg.norm(vdir,axis=1,keepdims=True)+1e-9)
    normal=np.stack([-vdir[:,1],vdir[:,0]],axis=1)
    poly=np.vstack([xy+normal*width/2, (xy-normal*width/2)[::-1]])
    ax.add_patch(MplPoly(poly,closed=True,facecolor=face,edgecolor=edge,
                 linewidth=1.1,joinstyle="round",zorder=z))

# ============================================================================
# FIGURA
# ============================================================================
fig,ax=plt.subplots(figsize=(11,10)); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

# macizo de fondo
allx=[X_C1,X_C2,X_MID]
ally=[Y_BASE,Y_TOP+30]
ax.add_patch(FancyBboxPatch((min(allx)-30,Y_BASE-16),
    (max(allx)-min(allx))+55,(Y_TOP+34-Y_BASE)+16,
    boxstyle="round,pad=2,rounding_size=10",facecolor=ROCK,edgecolor="none",zorder=0))

# rampas
ribbon(ax,smooth(RAMPA_SUP),W_RAMPA,C_RAMPA,C_RAMPA_ED,z=2)
ribbon(ax,RAMPA_INF,W_RAMPA,C_RAMPA,C_RAMPA_ED,z=2)

# galerías principales + cruceros + subidas a botaderos
for g in [GAL_1,GAL_2,CRU_SUP,CRU_INF]+SUBE_BOT:
    ribbon(ax,g,W_PROD,C_PROD,C_PROD_ED,z=3)

# costillas El Teniente: dos por drawbell, convergen al centro.
for c in DBELLS:
    ribbon(ax,c["seg1"],W_PROD,C_PROD,C_PROD_ED,z=3)
    ribbon(ax,c["seg2"],W_PROD,C_PROD,C_PROD_ED,z=3)
for c in DBELLS:
    # drawbell común (rombo gris) al centro
    db=c["db"]
    ax.add_patch(MplPoly([(db[0],db[1]+3.4),(db[0]+3.4,db[1]),(db[0],db[1]-3.4),
                 (db[0]-3.4,db[1])],closed=True,facecolor="#C9B98A",
                 edgecolor="#7A6A3A",linewidth=1.1,zorder=5))
    # los 2 drawpoints (punto verde) a cada lado del drawbell
    ax.add_patch(Circle(c["dp1"],2.5,facecolor=C_DRAW,edgecolor=C_DRAW_ED,linewidth=1.3,zorder=6))
    ax.add_patch(Circle(c["dp2"],2.5,facecolor=C_DRAW,edgecolor=C_DRAW_ED,linewidth=1.3,zorder=6))

# botaderos
for (bx,by) in BOTADEROS:
    ax.add_patch(Circle((bx,by),4.8,facecolor=C_BOT,edgecolor="#000",linewidth=1.2,zorder=6))
    ax.plot([bx-2.3,bx,bx+2.3],[by+1.5,by-1.9,by+1.5],color=BG,lw=1.7,zorder=7)

# escala gráfica
x0=min(allx)-20; y0=Y_BASE-30
for k in range(5):
    ax.add_patch(plt.Rectangle((x0+k*10,y0),10,2.4,facecolor=INK if k%2==0 else BG,
                 edgecolor=INK,lw=0.8,zorder=8))
ax.text(x0,y0-6,"0",ha="center",fontsize=8)
ax.text(x0+50,y0-6,"50 m",ha="center",fontsize=8,fontweight="bold")

# flecha norte
nx,ny=max(allx)+18,Y_TOP+18
ax.annotate("N",xy=(nx,ny+14),xytext=(nx,ny),
    arrowprops=dict(arrowstyle="-|>",color=INK,lw=1.6),ha="center",fontsize=11,fontweight="bold")

# leyenda
leg=[Line2D([0],[0],color=C_RAMPA,lw=7,label="Rampa de acceso"),
     Line2D([0],[0],color=C_PROD,lw=7,label="Galería de producción"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_DRAW,markeredgecolor=C_DRAW_ED,
            markersize=11,label="Drawpoint (boca de extracción)"),
     Line2D([0],[0],marker="D",color="none",markerfacecolor="#C9B98A",markeredgecolor="#7A6A3A",
            markersize=11,label="Drawbell (mineral compartido)"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor=C_BOT,markeredgecolor="#000",
            markersize=13,label="Botadero (descarga)")]
lg=ax.legend(handles=leg,loc="upper left",fontsize=10,frameon=True,framealpha=0.96,
             edgecolor=INK,borderpad=0.9,labelspacing=0.8)
lg.get_frame().set_facecolor("#FFFFFF")

ax.set_aspect("equal"); ax.grid(True,color="#D8D3C6",lw=0.5,alpha=0.7,zorder=0)
ax.set_xlabel("Distancia X (m)",fontsize=11); ax.set_ylabel("Distancia Y (m)",fontsize=11)
ax.set_title("Nivel de producción NV1640 — Nexa Cerro Lindo\n"
             "Zona de teleoperación LHD · sección galería 4×4 m · R giro 4.5 m · escala 1:1",
             fontsize=13,fontweight="bold",pad=14)
ax.set_xlim(min(allx)-40,max(allx)+40); ax.set_ylim(Y_BASE-40,Y_TOP+45)

plt.tight_layout()
out=os.path.join(OUT_DIR,"plano_nv1640_pro.png")
plt.savefig(out,dpi=170,bbox_inches="tight",facecolor=BG); plt.close()
print(f"[OK] {out}")
print(f"Galerías: 2 | Drawbells: {len(DBELLS)} | Drawpoints: {2*len(DBELLS)} | Botaderos: {len(BOTADEROS)}")

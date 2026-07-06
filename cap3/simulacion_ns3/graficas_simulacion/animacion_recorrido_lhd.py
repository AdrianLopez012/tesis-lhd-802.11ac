"""
Animación del recorrido del LHD sobre la geometría real NV1640 (2026-07-06)
===========================================================================
Usa mapa_nv1640_datos.py (geometría editada por el usuario) y anima el LHD:
  entra por la rampa -> recorre galería -> carga en un drawpoint ->
  lleva al botadero -> descarga -> vuelve por otro drawpoint (ruta compleja).

Genera un GIF: recorrido_lhd.gif
Ejecutar:  python animacion_recorrido_lhd.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon as MplPoly, FancyBboxPatch
from matplotlib.animation import FuncAnimation, PillowWriter
import os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("datos", os.path.join(HERE,"mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

# ---- estilo (igual que el plano pro) ----
BG="#F7F5EF"; ROCK="#EDE9DF"; INK="#2B2B28"
C_PROD="#2E6FB0"; C_PROD_ED="#1B4C7E"; C_RAMPA="#C08422"; C_RAMPA_ED="#8A5D12"
C_DRAW="#1E9E77"; C_DRAW_ED="#0C5B41"; C_BELL="#C9B98A"; C_BELL_ED="#7A6A3A"
C_BOT="#33322E"; C_LHD="#E24B4A"
W_PROD=4.0; W_RAMPA=4.0

def bezier(p0,p1,p2,n=22):
    t=np.linspace(0,1,n)[:,None]
    return (1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t**2*np.array(p2)
def densify(pts,curvas):
    pts=[np.array(p,float) for p in pts]; out=[pts[0]]
    for i in range(len(pts)-1):
        a,b=pts[i],pts[i+1]
        if i in curvas and 0<i: out.extend(bezier((pts[i-1]+a)/2,a,b)[1:])
        else: out.append(b)
    return np.array(out)
def ribbon(ax,xy,width,face,edge,z=2):
    xy=np.asarray(xy,float)
    if len(xy)<2:return
    d=np.diff(xy,axis=0);dirs=d/(np.linalg.norm(d,axis=1,keepdims=True)+1e-9)
    vdir=np.zeros_like(xy);vdir[0]=dirs[0];vdir[-1]=dirs[-1]
    vdir[1:-1]=dirs[:-1]+dirs[1:];vdir/=(np.linalg.norm(vdir,axis=1,keepdims=True)+1e-9)
    nrm=np.stack([-vdir[:,1],vdir[:,0]],axis=1)
    poly=np.vstack([xy+nrm*width/2,(xy-nrm*width/2)[::-1]])
    ax.add_patch(MplPoly(poly,closed=True,facecolor=face,edgecolor=edge,lw=1.0,joinstyle="round",zorder=z))

# ============================================================================
# RECORRIDO DEL LHD (waypoints sobre la geometría real)
# Ruta compleja: rampa -> galería central -> sube a drawpoint (carga) ->
# baja -> botadero (descarga) -> a otro drawpoint -> botadero. En metros.
# ============================================================================
def ruta():
    """Ruta REAL circulando SIEMPRE por las galerías y cruceros (nunca cruza roca).
    Movimiento del LHD sin giro en U: entra de frente al drawpoint, CARGA, sale
    en REVERSA por su costilla, y usa las galerías/cruceros para subir al botadero.
    El LHD puede cargar en drawpoints de cualquier galería y descargar en cualquier
    botadero. Coordenadas de la geometría real (mapa_nv1640_datos.py).
    Waypoint: (punto, acción). Acción: avanza / reversa / CARGA / DESCARGA.
    """
    Xg = D.X; YB, YT = D.YB, D.YT
    gI, gC, gD = Xg[0], Xg[1], Xg[2]        # galerías izq, centro, der
    entrada = (-D.RAMPA_LEN_INF, 0.0)
    b1, b2 = D.BOTADEROS[0], D.BOTADEROS[1]  # botaderos (izq y medio)

    # drawpoints reales agrupados por la galería a la que pertenecen (por su X)
    def galde(dp):
        return min([gI,gC,gD], key=lambda gx:abs(dp[0]-gx))
    dps = sorted(D.DRAWPOINTS, key=lambda p:p[1])
    # elegimos: uno de la galería izq (bajo) y uno de la galería central (más arriba)
    dp1 = next(d for d in dps if galde(d)==gI)                 # izq, bajo
    dp2 = next(d for d in reversed(dps) if galde(d)==gC)       # centro, alto

    def galP(gx,y): return (gx,y)   # punto sobre la galería gx a la altura y

    wp = [
        (entrada,"avanza"), (galP(gI,YB),"avanza"),
        # ---- ciclo 1: carga en drawpoint de la galería IZQUIERDA ----
        (galP(gI,dp1[1]),"avanza"), (dp1,"CARGA"),            # entra de frente
        (galP(gI,dp1[1]),"reversa"),                            # sale en reversa
        (galP(gI,YT),"avanza"), (b1,"DESCARGA"),              # sube por galería izq y descarga en botadero 1
        # ---- ciclo 2: carga en drawpoint de la galería CENTRAL ----
        (galP(gI,YT),"reversa"),                                # baja al crucero superior
        (galP(gC,YT),"avanza"),                                 # cruza por crucero superior a galería central
        (galP(gC,dp2[1]),"avanza"), (dp2,"CARGA"),           # baja y entra de frente
        (galP(gC,dp2[1]),"reversa"),                            # sale en reversa
        (galP(gC,YT),"avanza"), (b2,"DESCARGA"),             # sube y descarga en botadero 2 (medio)
        (galP(gC,YT),"reversa"), (galP(gI,YT),"avanza"),      # vuelve
    ]
    return wp

WP = ruta()

# interpolar el camino a velocidad constante + pausas
def build_path(wp, speed_m_per_frame=2.5, pause_frames=14):
    xs=[]; ys=[]; states=[]
    for i in range(len(wp)-1):
        (p0,_),(p1,act)=wp[i],wp[i+1]
        d=np.hypot(p1[0]-p0[0],p1[1]-p0[1])
        n=max(2,int(d/speed_m_per_frame))
        mov = "reversa" if act=="reversa" else "avanza"
        for k in range(n):
            t=k/n
            xs.append(p0[0]+t*(p1[0]-p0[0])); ys.append(p0[1]+t*(p1[1]-p0[1])); states.append(mov)
        if act in ("CARGA","DESCARGA"):
            for _ in range(pause_frames):
                xs.append(p1[0]); ys.append(p1[1]); states.append(act)
    return np.array(xs),np.array(ys),states

PX,PY,ST = build_path(WP)

# ============================================================================
# FIGURA + fondo estático
# ============================================================================
fig,ax=plt.subplots(figsize=(12,9)); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
allpts=[p for cam in D.PRODUCCION for p in cam]+[p for r in D.RAMPAS for p in r["pts"]]+D.BOTADEROS
xs=[p[0] for p in allpts]; ys=[p[1] for p in allpts]
px=[p[0] for cam in D.PRODUCCION for p in cam if p[0]>-30]; py=[p[1] for cam in D.PRODUCCION for p in cam]
ax.add_patch(FancyBboxPatch((min(px)-12,min(py)-12),(max(px)-min(px))+24,(max(py)-min(py))+24,
    boxstyle="round,pad=2,rounding_size=8",facecolor=ROCK,edgecolor="none",zorder=0))
for r in D.RAMPAS: ribbon(ax,densify(r["pts"],r["curvas"]),W_RAMPA,C_RAMPA,C_RAMPA_ED,2)
for cam in D.PRODUCCION: ribbon(ax,densify(cam,[]),W_PROD,C_PROD,C_PROD_ED,3)
for (x,y) in D.DRAWBELLS:
    s=3.2; ax.add_patch(MplPoly([(x,y+s),(x+s,y),(x,y-s),(x-s,y)],closed=True,facecolor=C_BELL,edgecolor=C_BELL_ED,lw=1.1,zorder=5))
for (x,y) in D.DRAWPOINTS: ax.add_patch(Circle((x,y),2.4,facecolor=C_DRAW,edgecolor=C_DRAW_ED,lw=1.2,zorder=6))
for (x,y) in D.BOTADEROS:
    ax.add_patch(Circle((x,y),4.6,facecolor=C_BOT,edgecolor="#000",lw=1.2,zorder=6))
    ax.plot([x-2.2,x,x+2.2],[y+1.4,y-1.8,y+1.4],color=BG,lw=1.6,zorder=7)

# rastro y LHD (dinámicos)
trail,=ax.plot([],[],color=C_LHD,lw=1.6,alpha=0.5,zorder=8)
lhd=Circle((PX[0],PY[0]),3.6,facecolor=C_LHD,edgecolor="#7a1f1f",lw=1.5,zorder=10)
ax.add_patch(lhd)
label=ax.text(0.02,0.97,"",transform=ax.transAxes,fontsize=12,fontweight="bold",
              va="top",color=INK,bbox=dict(boxstyle="round",fc="#fff",ec=INK,alpha=0.9))

ax.set_aspect("equal"); ax.grid(True,color="#D8D3C6",lw=0.5,alpha=0.6,zorder=0)
ax.set_xlabel("Distancia X (m)"); ax.set_ylabel("Distancia Y (m)")
ax.set_title("Recorrido del LHD teleoperado — NV1640 (geometría real)",fontsize=13,fontweight="bold")
ax.set_xlim(min(xs)-15,max(xs)+20); ax.set_ylim(min(ys)-25,max(ys)+15)

def upd(f):
    lhd.center=(PX[f],PY[f])
    trail.set_data(PX[:f+1],PY[:f+1])
    est={"avanza":"Avanzando","reversa":"En REVERSA (sin girar)",
         "CARGA":"CARGANDO en drawpoint","DESCARGA":"DESCARGANDO en botadero"}[ST[f]]
    label.set_text(f"LHD: {est}")
    col={"avanza":C_LHD,"reversa":"#C08422","CARGA":"#f0b429","DESCARGA":"#8a97a8"}[ST[f]]
    lhd.set_facecolor(col)
    return lhd,trail,label

anim=FuncAnimation(fig,upd,frames=len(PX),interval=60,blit=False)
out=os.path.join(HERE,"recorrido_lhd.gif")
anim.save(out,writer=PillowWriter(fps=16),dpi=90)
plt.close()
print(f"[OK] {out}  ({len(PX)} frames)")

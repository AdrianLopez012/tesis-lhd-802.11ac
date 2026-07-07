"""
Mapa de cobertura PROFESIONAL — NV1640 (heatmap RSSI + SNR/PHY rate)
====================================================================
Calcula la cobertura real con el modelo two-slope calibrado (TamoGraph) y los
parámetros de los datasheets, sobre una grilla de la zona de teleoperación.
Genera dos mapas de calor: (1) RSSI del mejor AP, (2) PHY rate alcanzable.

Es el estándar en tesis RF: no círculos planos, sino nivel de señal calculado
con física de propagación y curvas de nivel en umbrales clave.

Ejecutar:  python mapa_cobertura_pro.py  ->  mapa_cobertura_pro.png
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon as MplPoly
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import os, importlib.util

HERE=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("datos",os.path.join(HERE,"mapa_nv1640_datos.py"))
D=importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

# ---------------- MODELO two-slope calibrado (de modelo_definitivo.py) ----------------
FREQ=5.0e9; LAMBDA=3e8/FREQ; BW=40e6
N1=1.9; N2=3.4; N_NLOS=5.0; D_BP=40.0
L_SYS=9.4                       # dB (Cardinal real)
PL_D0=20*np.log10(4*np.pi/LAMBDA)
NF=6.0; NOISE=10*np.log10(1.38e-23*300*BW*1000)+NF   # ~-91.8 dBm
GR_LHD=4.8                      # antena vehículo HELI-40 (dBic)

# AP: (x, y, Pt, Gt)  — Hawk 30dBm/11dBi, Cardinal 23dBm/7.5dBi
APS=[(x,y,30.0,11.0) for (x,y) in D.HAWKS]+[(x,y,23.0,7.5) for (x,y) in D.CARDINALS_AP]

def path_loss(d, nlos=False):
    d=max(d,1.0)
    if d<D_BP: pl=PL_D0+10*N1*np.log10(d)
    else:      pl=PL_D0+10*N1*np.log10(D_BP)+10*(N_NLOS if nlos else N2)*np.log10(d/D_BP)
    return pl

# --- Distancia por RUTA DE TÚNEL + NLOS (la señal NO cruza roca) ---
# La zona son 3 galerías verticales (en X_GAL) unidas por cruceros arriba/abajo.
# Un enlace AP->punto es LOS si ambos están (aprox) en la MISMA galería; si están
# en galerías distintas, la señal debe rodear por el crucero => más distancia +
# penalización NLOS por cada pared/esquina cruzada.
XG=D.X                       # x de las 3 galerías
YT=D.YT; YB=D.YB
NLOS_PENAL=10.0              # dB extra por cruzar de una galería a otra (esquina)

def cual_galeria(x):
    return min(range(len(XG)), key=lambda i:abs(x-XG[i]))

def ruta_dist_y_nlos(ax,ay,px,py):
    """Distancia siguiendo galerías + nº de transiciones NLOS entre (ax,ay) y (px,py)."""
    ga=cual_galeria(ax); gp=cual_galeria(px)
    if ga==gp:
        # misma galería: distancia casi directa (LOS)
        return abs(ay-py)+abs(ax-XG[ga])+abs(px-XG[gp]), 0
    # galerías distintas: sube/baja al crucero más cercano, cruza, baja/sube
    # elegir crucero (arriba YT o abajo YB) que minimice el recorrido
    d_top = (YT-ay)+abs(XG[ga]-XG[gp])+(YT-py)
    d_bot = (ay-YB)+abs(XG[ga]-XG[gp])+(py-YB)
    d = min(d_top,d_bot) + abs(ax-XG[ga]) + abs(px-XG[gp])
    return d, abs(ga-gp)   # nº de galerías cruzadas = nº transiciones NLOS

def rssi_en(px,py):
    """RSSI del mejor AP en (px,py), con distancia por ruta de túnel + NLOS."""
    best=-999.0
    for (ax,ay,pt,gt) in APS:
        d,ncross=ruta_dist_y_nlos(ax,ay,px,py)
        nlos = ncross>0
        pr=pt+gt+GR_LHD-path_loss(d,nlos)-L_SYS-NLOS_PENAL*ncross
        if pr>best: best=pr
    return best

# ---------------- GRILLA de la zona ----------------
xs=[p[0] for cam in D.PRODUCCION for p in cam if p[0]>-30]
ys=[p[1] for cam in D.PRODUCCION for p in cam]
x0,x1=min(xs)-8,max(xs)+8; y0,y1=min(ys)-8,max(D.PIQUES,key=lambda p:p[1])[1]+8
gx=np.linspace(x0,x1,220); gy=np.linspace(y0,y1,320)
GX,GY=np.meshgrid(gx,gy)
RSSI=np.vectorize(rssi_en)(GX,GY)
SNR=RSSI-NOISE
# PHY rate (Mbps) por SNR (tabla 802.11ac 2x2 40MHz, de la tesis)
def snr_to_rate(s):
    tbl=[(5,13.5),(8,27),(11,40.5),(14,54),(17,81),(20,108),(23,121.5),(26,135),(29,162),(32,180)]
    r=0
    for th,rr in tbl:
        if s>=th: r=rr
    return r
RATE=np.vectorize(snr_to_rate)(SNR)

# ---------------- estilo caminos ----------------
INK="#2B2B28"
def bezier(p0,p1,p2,n=16):
    t=np.linspace(0,1,n)[:,None]; return (1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t**2*np.array(p2)
def densify(pts,cur):
    pts=[np.array(p,float) for p in pts]
    if len(pts)==2: return np.array(pts)
    o=[pts[0]]
    for i in range(1,len(pts)-1):
        pv,c,nx=pts[i-1],pts[i],pts[i+1]
        if i in cur:
            din=np.linalg.norm(c-pv); do=np.linalg.norm(nx-c); r=min(16,din*.45,do*.45)
            pin=c+(pv-c)/(din+1e-9)*r; po=c+(nx-c)/(do+1e-9)*r
            o.append(pin); o.extend(bezier(pin,c,po)[1:]); o.append(po)
        else: o.append(c)
    o.append(pts[-1]); return np.array(o)
def draw_caminos(ax):
    segs=[densify(c,[]) for c in D.PRODUCCION]
    ax.add_collection(LineCollection(segs,colors="#111",linewidths=6.5,capstyle="round",joinstyle="round",zorder=5,alpha=0.35))

# ---------------- FIGURA: 2 paneles ----------------
fig,(a1,a2)=plt.subplots(1,2,figsize=(17,10)); fig.patch.set_facecolor("#F7F5EF")

# panel 1: RSSI
im1=a1.contourf(GX,GY,RSSI,levels=np.arange(-95,-45,3),cmap="RdYlGn",extend="both")
cs=a1.contour(GX,GY,RSSI,levels=[-94,-82,-68],colors="k",linewidths=1.1,linestyles="--")
a1.clabel(cs,fmt="%d dBm",fontsize=8)
draw_caminos(a1)
for (x,y,pt,gt) in APS:
    col="#1565C0" if pt==30 else "#7B1FA2"
    a1.scatter(x,y,s=70,c=col,edgecolors="#fff",linewidths=1.3,zorder=8)
for (x,y) in D.DRAWPOINTS: a1.scatter(x,y,s=18,c="#0C5B41",zorder=7)
cbar1=fig.colorbar(im1,ax=a1,fraction=0.046,pad=0.04); cbar1.set_label("RSSI (dBm)")
a1.set_title("Nivel de señal recibida (RSSI)\nmodelo two-slope calibrado · sensib. -94/-82/-68 dBm",fontsize=12,fontweight="bold")
a1.set_xlabel("X (m)"); a1.set_ylabel("Y (m)"); a1.set_aspect("equal")

# panel 2: PHY rate
im2=a2.contourf(GX,GY,RATE,levels=[0,13.5,27,40.5,54,81,108,135,180],cmap="viridis",extend="max")
draw_caminos(a2)
for (x,y,pt,gt) in APS:
    col="#42A5F5" if pt==30 else "#CE93D8"
    a2.scatter(x,y,s=70,c=col,edgecolors="#000",linewidths=1.3,zorder=8)
for (x,y) in D.DRAWPOINTS: a2.scatter(x,y,s=18,c="#fff",edgecolors="#000",linewidths=0.5,zorder=7)
cbar2=fig.colorbar(im2,ax=a2,fraction=0.046,pad=0.04); cbar2.set_label("PHY rate (Mbps)")
a2.set_title("Tasa PHY alcanzable — 802.11ac 2×2 40MHz\nverde/amarillo = soporta vídeo 40 Mbps",fontsize=12,fontweight="bold")
a2.set_xlabel("X (m)"); a2.set_ylabel("Y (m)"); a2.set_aspect("equal")

leg=[Line2D([0],[0],marker="o",color="none",markerfacecolor="#1565C0",markeredgecolor="#fff",markersize=10,label="AP Hawk (30 dBm)"),
     Line2D([0],[0],marker="o",color="none",markerfacecolor="#7B1FA2",markeredgecolor="#fff",markersize=10,label="AP Cardinal (23 dBm)")]
a1.legend(handles=leg,loc="upper left",fontsize=9,framealpha=0.9)

plt.suptitle("NV1640 — Cobertura RF de la zona de teleoperación LHD (5 Hawk + 7 Cardinal)",
             fontsize=15,fontweight="bold",y=0.99)
plt.tight_layout(rect=[0,0,1,0.97])
out=os.path.join(HERE,"mapa_cobertura_pro.png")
plt.savefig(out,dpi=155,bbox_inches="tight",facecolor="#F7F5EF"); plt.close()
# estadísticas de cobertura
cubierto=(RSSI>=-82).mean()*100
video_ok=(RATE>=54).mean()*100
print(f"[OK] {out}")
print(f"Área con RSSI>=-82dBm (buena): {cubierto:.1f}% | PHY>=54Mbps: {video_ok:.1f}%")

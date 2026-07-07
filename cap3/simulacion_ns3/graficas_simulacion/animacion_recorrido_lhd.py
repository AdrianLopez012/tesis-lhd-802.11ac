"""
Animación del recorrido del LHD — SIGUE LOS CAMINOS REALES (2026-07-06)
======================================================================
Construye un GRAFO con todos los segmentos reales de los caminos (galerías,
cruceros, costillas diagonales, rampa) y calcula la ruta del LHD con Dijkstra,
de modo que el LHD circula EXACTAMENTE por las vías (nunca corta recto por
encima) y entra a los drawpoints por su costilla diagonal.

Movimiento realista: avanza de frente al drawpoint, CARGA, sale en REVERSA por
la misma costilla (sin giro en U), sube por galería/crucero y DESCARGA en botadero.

Genera: recorrido_lhd.gif
Ejecutar:  python animacion_recorrido_lhd.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon as MplPoly, FancyBboxPatch
from matplotlib.collections import LineCollection
from matplotlib.animation import FuncAnimation, PillowWriter
import heapq, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("datos", os.path.join(HERE,"mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

# ---- estilo ----
BG="#F7F5EF"; ROCK="#E9E4D8"; INK="#2B2B28"
C_PROD="#2E6FB0"; C_PROD_ED="#173F66"; C_RAMPA="#C08422"; C_RAMPA_ED="#7A5210"
C_DRAW="#1E9E77"; C_DRAW_ED="#0C5B41"; C_BELL="#C9B98A"; C_BELL_ED="#7A6A3A"
C_BOT="#33322E"; C_LHD="#E24B4A"
W=4.0

def bezier(p0,p1,p2,n=16):
    t=np.linspace(0,1,n)[:,None]
    return (1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t**2*np.array(p2)
def densify(pts,curvas,fillet=16.0):
    pts=[np.array(p,float) for p in pts]
    if len(pts)==2: return [tuple(pts[0]),tuple(pts[1])]
    out=[tuple(pts[0])]
    for i in range(1,len(pts)-1):
        prev,cur,nxt=pts[i-1],pts[i],pts[i+1]
        if i in curvas:
            din=np.linalg.norm(cur-prev); dout=np.linalg.norm(nxt-cur)
            r=min(fillet,din*0.45,dout*0.45)
            pin=cur+(prev-cur)/(din+1e-9)*r; pout=cur+(nxt-cur)/(dout+1e-9)*r
            out.append(tuple(pin))
            for q in bezier(pin,cur,pout)[1:]: out.append(tuple(q))
            out.append(tuple(pout))
        else: out.append(tuple(cur))
    out.append(tuple(pts[-1])); return out

# ============================================================================
# GRAFO de los caminos reales
# ============================================================================
def key(p, prec=1): return (round(p[0],prec), round(p[1],prec))

# Subdividir cada segmento en trocitos de ~2 m para que los cruces y pies de
# costilla caigan sobre nodos reales y el grafo quede bien conectado.
def subdivide(a,b,step=2.0):
    d=np.hypot(b[0]-a[0],b[1]-a[1]); n=max(1,int(d/step))
    return [(a[0]+(b[0]-a[0])*k/n, a[1]+(b[1]-a[1])*k/n) for k in range(n+1)]

# Un tramo de PRODUCCION es "costilla de drawpoint" si su último punto es un
# drawpoint. Esas NO entran al grafo general (para que Dijkstra no las atraviese
# ni entre en sentido de giro cerrado). Solo galerías, cruceros y rampa forman
# el grafo por donde el LHD circula libremente.
draw_set={(round(x,1),round(y,1)) for (x,y) in D.DRAWPOINTS}
def es_costilla(cam):
    p=cam[-1]; return (round(p[0],1),round(p[1],1)) in draw_set

polylines=[]
for cam in D.PRODUCCION:
    if es_costilla(cam):   # costilla a drawpoint: se maneja aparte, no al grafo
        continue
    dense=[]
    for i in range(len(cam)-1): dense+=subdivide(tuple(cam[i]),tuple(cam[i+1]))
    polylines.append(dense)
for r in D.RAMPAS:
    base=densify(r["pts"], r.get("curvas",[])); dense=[]
    for i in range(len(base)-1): dense+=subdivide(base[i],base[i+1])
    polylines.append(dense)

# mapa: drawpoint -> (punto de pie en la galería, coord drawpoint) para maniobras
COSTILLAS={}
for cam in D.PRODUCCION:
    if es_costilla(cam):
        pie=tuple(cam[0]); dp=tuple(cam[-1])
        COSTILLAS[(round(dp[0],1),round(dp[1],1))]=(pie,dp)

adj={}
def add_edge(a,b):
    ka,kb=key(a),key(b); d=np.hypot(a[0]-b[0],a[1]-b[1])
    if d<1e-6: return
    adj.setdefault(ka,[]).append((kb,d)); adj.setdefault(kb,[]).append((ka,d))
for pl in polylines:
    for i in range(len(pl)-1): add_edge(pl[i], pl[i+1])

# Conectar nodos MUY cercanos entre distintos caminos (uniones/cruces).
allkeys=list(adj.keys())
import math
grid={}
for k in allkeys:
    gx,gy=int(k[0]//3),int(k[1]//3); grid.setdefault((gx,gy),[]).append(k)
for k in allkeys:
    gx,gy=int(k[0]//3),int(k[1]//3)
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for k2 in grid.get((gx+dx,gy+dy),[]):
                if k2==k: continue
                d=np.hypot(k[0]-k2[0],k[1]-k2[1])
                if 0<d<3.0: adj[k].append((k2,d))

def nearest_node(p):
    return min(adj.keys(), key=lambda k: np.hypot(k[0]-p[0],k[1]-p[1]))

def dijkstra(src, dst):
    src,dst=key(src),key(dst)
    if src not in adj: src=nearest_node(src)
    if dst not in adj: dst=nearest_node(dst)
    pq=[(0,src,[src])]; seen=set()
    while pq:
        c,u,path=heapq.heappop(pq)
        if u==dst: return path
        if u in seen: continue
        seen.add(u)
        for v,w in adj.get(u,[]):
            if v not in seen: heapq.heappush(pq,(c+w,v,path+[v]))
    return [src,dst]  # fallback

# ============================================================================
# RUTA del LHD (secuencia de destinos) — sigue el grafo entre cada par
# ============================================================================
Xg=D.X; YB,YT=D.YB,D.YT
entrada=(-D.RAMPA_LEN_INF,-28.0)
# SOLO drawpoints ACCESIBLES (giro abierto o recto) — el LHD sube a cargar, así
# que entra a las costillas que se abren hacia adelante en su marcha (regla de
# giro según perspectiva). Los 'cerrado' se excluyen (no los puede encarar).
accesibles=[(x,y) for (x,y,acc) in D.DRAWPOINTS_INFO if acc in ("abierto","recto")]
# elegimos uno bajo y uno alto, ambos accesibles, para una ruta representativa
acc_sorted=sorted(accesibles,key=lambda p:p[1])
dp1=acc_sorted[1] if len(acc_sorted)>1 else acc_sorted[0]   # bajo
dp2=acc_sorted[-1]                                          # más alto
b1,b2=D.BOTADEROS[0],D.BOTADEROS[1]

# pie de costilla de cada drawpoint elegido (para maniobrar)
def pie_de(dp):
    k=(round(dp[0],1),round(dp[1],1))
    return COSTILLAS.get(k,(dp,dp))[0]

route=[]; actions=[]
def append_path(path, st="avanza"):
    for k in path: route.append(k); actions.append(st)

# La ruta: entra -> (por grafo) al PIE del drawpoint -> avanza costilla al
# drawpoint (CARGA) -> reversa costilla al pie -> (por grafo) al pique (DESCARGA).
# Como las costillas NO están en el grafo, Dijkstra jamás entra a un drawpoint
# de paso ni en giro cerrado: la entrada es siempre esta maniobra explícita.
def ir_por_grafo(desde, hasta):
    path=[(x,y) for (x,y) in [ (round(p[0],1),round(p[1],1)) for p in dijkstra(desde,hasta)]]
    append_path(path[1:] if route else path, "avanza")

def cargar_en(dp):
    # Usa COSTILLA_APPROACH: encara el drawpoint por el sentido que da giro
    # ABIERTO de forma natural. Si el drawpoint se encara 'bajando', el LHD
    # RODEA (sube más allá por el grafo) y baja para entrar de frente; si es
    # 'subiendo', se posiciona por debajo y sube. Así TODOS son alcanzables.
    info=D.COSTILLA_APPROACH.get((round(dp[0],1),round(dp[1],1)))
    if info is None:   # fallback
        pie=pie_de(dp); ir_por_grafo(cur_pos(),pie)
        append_path([pie,(dp[0],dp[1])],"avanza"); actions[-1]="CARGA_FIN"
        append_path([(dp[0],dp[1]),pie],"reversa"); return
    pie=info['pie']; gx=info['gal']; sentido=info['sentido']
    # El punto de aproximación se ACOTA a los límites de la galería [YB, YT]
    # para que el LHD nunca se salga del túnel (evita el retroceso raro).
    OFF=10.0
    if sentido=='sube':
        prev=(gx, max(YB, pie[1]-OFF))   # por DEBAJO del pie, dentro de la galería
    else:  # 'baja'
        prev=(gx, min(YT, pie[1]+OFF))   # por ARRIBA del pie, sin pasar el tope
    ir_por_grafo(cur_pos(), prev)             # llega al punto de aproximación (rodeando)
    append_path([prev, pie], "avanza")        # encara de frente (giro abierto)
    append_path([pie, (dp[0],dp[1])], "avanza"); actions[-1]="CARGA_FIN"  # entra al drawpoint
    append_path([(dp[0],dp[1]), pie], "reversa")   # sale en reversa (sin giro en U)

def descargar_en(b):
    ir_por_grafo(cur_pos(), b)
    actions[-1]="DESCARGA_FIN"

def cur_pos():
    return route[-1] if route else entrada

# ejecutar la secuencia — ahora TODOS los drawpoints son alcanzables (rodeando
# para encarar en giro abierto). Elegimos un caso 'abierto' (encara subiendo) y
# un caso 'cerrado' (el LHD RODEA y baja para encararlo) para demostrar la lógica.
todos=sorted(D.DRAWPOINTS,key=lambda p:p[1])
def acc_de(dp):
    for (x,y,a) in D.DRAWPOINTS_INFO:
        if abs(x-dp[0])<0.5 and abs(y-dp[1])<0.5: return a
    return '?'
dp_abierto=next(d for d in todos if acc_de(d)=='abierto')
dp_cerrado=next(d for d in reversed(todos) if acc_de(d)=='cerrado')

append_path([entrada],"avanza")
cargar_en(dp_abierto); descargar_en(b1)      # caso fácil (encara subiendo)
cargar_en(dp_cerrado); descargar_en(b2)      # caso que RODEA para encarar abierto

RXY=[(k[0],k[1]) for k in route]

# ============================================================================
# interpolar a velocidad constante + pausas de carga/descarga
# ============================================================================
PX=[];PY=[];ST=[]
for i in range(len(RXY)-1):
    p0,p1=RXY[i],RXY[i+1]; act=actions[i+1]
    d=np.hypot(p1[0]-p0[0],p1[1]-p0[1]); n=max(2,int(d/2.0))
    mov="reversa" if actions[i]=="reversa" else "avanza"
    for k in range(n):
        t=k/n; PX.append(p0[0]+t*(p1[0]-p0[0])); PY.append(p0[1]+t*(p1[1]-p0[1])); ST.append(mov)
    if act in ("CARGA_FIN","DESCARGA_FIN"):
        for _ in range(14):
            PX.append(p1[0]);PY.append(p1[1]);ST.append("CARGA" if act=="CARGA_FIN" else "DESCARGA")
PX=np.array(PX);PY=np.array(PY)

# ============================================================================
# FIGURA (fondo = plano) + LHD animado
# ============================================================================
# fondo IDÉNTICO al plano bueno (LineCollection en 2 capas: contorno+relleno del
# mismo color, para que los cruces se fundan sin solapamientos)
def draw_network(ax, paths, width, face, edge, z):
    segs=[]
    for p in paths:
        pts=p["pts"] if isinstance(p,dict) else p
        cur=p.get("curvas",[]) if isinstance(p,dict) else []
        segs.append(densify(pts,cur))
    ax.add_collection(LineCollection(segs,colors=edge,linewidths=width+2.2,capstyle="round",joinstyle="round",zorder=z))
    ax.add_collection(LineCollection(segs,colors=face,linewidths=width,capstyle="round",joinstyle="round",zorder=z+0.1))
def m2lw(wm): return wm*2.6

fig,ax=plt.subplots(figsize=(12,9)); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
allpts=[p for cam in D.PRODUCCION for p in cam]+[p for r in D.RAMPAS for p in r["pts"]]+D.BOTADEROS
xs=[p[0] for p in allpts]; ys=[p[1] for p in allpts]
px=[p[0] for cam in D.PRODUCCION for p in cam if p[0]>-30]; py=[p[1] for cam in D.PRODUCCION for p in cam]
ax.add_patch(FancyBboxPatch((min(px)-14,min(py)-16),(max(px)-min(px))+28,(max(py)-min(py))+34,
    boxstyle="round,pad=2,rounding_size=10",facecolor=ROCK,edgecolor="none",zorder=0))
draw_network(ax, D.RAMPAS, m2lw(W), C_RAMPA, C_RAMPA_ED, 2)
draw_network(ax, D.PRODUCCION, m2lw(W), C_PROD, C_PROD_ED, 4)
for (x,y) in D.DRAWBELLS:
    s=3.2; ax.add_patch(MplPoly([(x,y+s),(x+s,y),(x,y-s),(x-s,y)],closed=True,facecolor=C_BELL,edgecolor=C_BELL_ED,lw=1.1,zorder=7))
for (x,y) in D.DRAWPOINTS: ax.add_patch(Circle((x,y),2.3,facecolor=C_DRAW,edgecolor=C_DRAW_ED,lw=1.2,zorder=8))
for (x,y) in D.BOTADEROS:
    ax.add_patch(Circle((x,y),4.6,facecolor=C_BOT,edgecolor="#000",lw=1.2,zorder=8))
    ax.plot([x-2.2,x,x+2.2],[y+1.4,y-1.8,y+1.4],color=BG,lw=1.6,zorder=9)

trail,=ax.plot([],[],color=C_LHD,lw=2.0,alpha=0.6,zorder=15)
lhd=Circle((PX[0],PY[0]),3.4,facecolor=C_LHD,edgecolor="#7a1f1f",lw=1.5,zorder=16); ax.add_patch(lhd)
label=ax.text(0.02,0.97,"",transform=ax.transAxes,fontsize=12,fontweight="bold",va="top",
              bbox=dict(boxstyle="round",fc="#fff",ec=INK,alpha=0.9))
ax.set_aspect("equal"); ax.grid(True,color="#DED9CC",lw=0.5,alpha=0.6,zorder=0)
ax.set_xlabel("Distancia X (m)"); ax.set_ylabel("Distancia Y (m)")
ax.set_title("Recorrido del LHD teleoperado — NV1640 (sigue los caminos)",fontsize=13,fontweight="bold")
ax.set_xlim(min(xs)-15,max(xs)+20); ax.set_ylim(min(ys)-25,max(ys)+15)

def upd(f):
    lhd.center=(PX[f],PY[f]); trail.set_data(PX[:f+1],PY[:f+1])
    est={"avanza":"Avanzando","reversa":"En REVERSA (sin girar)",
         "CARGA":"CARGANDO en drawpoint","DESCARGA":"DESCARGANDO en pique de traspaso"}[ST[f]]
    label.set_text(f"LHD: {est}")
    col={"avanza":C_LHD,"reversa":"#C08422","CARGA":"#f0b429","DESCARGA":"#8a97a8"}[ST[f]]
    lhd.set_facecolor(col); return lhd,trail,label

anim=FuncAnimation(fig,upd,frames=len(PX),interval=60,blit=False)
out=os.path.join(HERE,"recorrido_lhd.gif")
anim.save(out,writer=PillowWriter(fps=16),dpi=90); plt.close()
print(f"[OK] {out}  ({len(PX)} frames, {len(RXY)} nodos de ruta)")

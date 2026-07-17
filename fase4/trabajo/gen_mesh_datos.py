# -*- coding: utf-8 -*-
# Datos para el "MESH EN VIVO": por cada frame del recorrido real,
#   · RSSI a los 12 AP con el modelo two-slope de la tesis sobre DISTANCIA DE RUTA
#     (la señal viaja por las galerías, no atraviesa roca)
#   · la ruta por la malla (AP asociado -> ... -> CORE) re-enrutada dinámicamente
#     (selección por costo de enlace, comportamiento tipo InstaMesh — modelo propio)
# Salidas: mesh_rssi.csv (307x12), mesh_rutas.csv (ruta de AP índices por frame)
import importlib.util, os, sys, heapq
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")

GS  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
SIM = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3"
TRB = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo"

spec = importlib.util.spec_from_file_location("datos", os.path.join(GS, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)
spec2 = importlib.util.spec_from_file_location("rf", os.path.join(SIM, "parametros_rf.py"))
RF = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(RF)

# ---------- grafo de galerías (igual que el enlace) ----------
segs = []
for cam in D.PRODUCCION:
    for i in range(len(cam)-1):
        segs.append((np.array(cam[i],float), np.array(cam[i+1],float)))

nodos = {}; aristas = {}
def nodo(p):
    k = (round(p[0],2), round(p[1],2))
    nodos.setdefault(k, np.array(k)); return k
def arista(k1,k2):
    w = float(np.hypot(k1[0]-k2[0], k1[1]-k2[1]))
    if w < 0.05: return
    aristas.setdefault(k1,[]).append((k2,w))
    aristas.setdefault(k2,[]).append((k1,w))
ptsen = [[] for _ in segs]
for i,(A,B) in enumerate(segs):
    u=B-A; L=np.linalg.norm(u); u=u/L; n=np.array([-u[1],u[0]])
    ptsen[i].extend([0.0,L])
    for j,(C,E) in enumerate(segs):
        if i==j: continue
        for Q in (C,E):
            t=float(np.dot(Q-A,u)); dd=abs(float(np.dot(Q-A,n)))
            if -0.3<=t<=L+0.3 and dd<=2.6: ptsen[i].append(min(max(t,0),L))
for i,(A,B) in enumerate(segs):
    u=B-A; L=np.linalg.norm(u); u=u/L
    ts=sorted(set(round(t,2) for t in ptsen[i]))
    ks=[nodo(A+u*t) for t in ts]
    for a,b in zip(ks,ks[1:]): arista(a,b)

def conectar(P):
    mejor=(1e9,None,None)
    for (A,B) in segs:
        u=B-A; L=np.linalg.norm(u); u=u/L
        t=min(max(float(np.dot(P-A,u)),0),L)
        Q=A+u*t; dd=float(np.hypot(*(P-Q)))
        if dd<mejor[0]: mejor=(dd,Q,(nodo(A),nodo(B)))
    kQ=nodo(mejor[1])
    for kk in mejor[2]: arista(kQ,kk)
    return kQ

def dist_ruta(src, dsts):
    """distancias de ruta desde src a un conjunto de nodos"""
    dist={src:0.0}; pq=[(0.0,src)]
    while pq:
        d,k=heapq.heappop(pq)
        if d>dist.get(k,1e18): continue
        for (k2,w) in aristas.get(k,[]):
            nd=d+w
            if nd<dist.get(k2,1e18): dist[k2]=nd; heapq.heappush(pq,(nd,k2))
    return [dist.get(t,1e9) for t in dsts]

# ---------- APs, core, recorrido ----------
aps = [np.array(p,float) for p in (list(D.HAWKS)+list(D.CARDINALS_AP))]
tipos = [1]*len(D.HAWKS)+[2]*len(D.CARDINALS_AP)
ap_k = [conectar(p) for p in aps]
CORE = np.array([25.98, 134.85])
core_k = conectar(CORE)

REC = np.loadtxt(os.path.join(TRB,"anim_recorrido.csv"), delimiter=",")
P = RF.PROPAGACION
PLD0 = 20*np.log10(4*np.pi/ (3e8/5.0e9))
def rssi(druta, tipo):
    d = max(druta, 1.0)
    pl = PLD0 + 10*P["n1"]*np.log10(min(d,P["d_bp_m"])) + 10*P["n2"]*np.log10(max(d/P["d_bp_m"],1.0))
    pt = RF.HAWK["tx_power_dbm"] if tipo==1 else RF.CARDINAL["tx_power_dbm"]
    gt = RF.HAWK["tx_gain_dbi"]  if tipo==1 else RF.CARDINAL["tx_gain_dbi"]
    return pt + gt + RF.LHD_ANTENA["gain_dbic"] - pl - RF.L_SYSTEM_DB

# RSSI por frame a los 12 AP (distancia de ruta)
NF = len(REC); NA = len(aps)
RS = np.zeros((NF, NA))
for f in range(NF):
    kL = conectar(np.array([REC[f,1], REC[f,2]]))
    dr = dist_ruta(kL, ap_k)
    for a in range(NA):
        RS[f,a] = rssi(dr[a], tipos[a])
np.savetxt(os.path.join(TRB,"mesh_rssi.csv"), RS, fmt="%.1f", delimiter=",")

# ---------- malla AP<->AP (vecinos por distancia de ruta) + ruta al core ----------
dAP = np.zeros((NA,NA))
for a in range(NA):
    dr = dist_ruta(ap_k[a], ap_k)
    dAP[a,:] = dr
adj = {a: [] for a in range(NA)}
for a in range(NA):
    orden = np.argsort(dAP[a,:])
    for b in orden[1:4]:                 # 3 vecinos de malla más cercanos por ruta
        if dAP[a,b] < 1e8:
            adj[a].append((int(b), dAP[a,b]))
d_core = dist_ruta(core_k, ap_k)

def ruta_mesh(a0):
    """AP asociado -> core: Dijkstra sobre la malla, costo = distancia de ruta"""
    dist={a0:0.0}; prev={}; pq=[(0.0,a0)]
    objetivo = int(np.argmin(d_core))    # AP más cercano al core
    while pq:
        d,a=heapq.heappop(pq)
        if a==objetivo: break
        if d>dist.get(a,1e18): continue
        for (b,w) in adj[a]:
            nd=d+w
            if nd<dist.get(b,1e18): dist[b]=nd; prev[b]=a; heapq.heappush(pq,(nd,b))
    if objetivo not in dist: return [a0]
    ruta=[objetivo]
    while ruta[-1]!=a0: ruta.append(prev[ruta[-1]])
    return ruta[::-1]

MAXH = 8
RUTAS = np.full((NF, MAXH), np.nan)
for f in range(NF):
    a0 = int(REC[f,3]) - 1
    if a0 < 0: continue
    r = ruta_mesh(a0)[:MAXH]
    RUTAS[f,:len(r)] = [x+1 for x in r]
np.savetxt(os.path.join(TRB,"mesh_rutas.csv"), RUTAS, fmt="%.0f", delimiter=",")

cand = (RS >= -82).sum(axis=1)
print(f"mesh_rssi: {NF}x{NA} | candidatos por frame min/med/max = {cand.min()}/{cand.mean():.1f}/{cand.max()}")
print(f"mesh_rutas: saltos por ruta max = {int(np.nanmax((~np.isnan(RUTAS)).sum(axis=1)))}")

# -*- coding: utf-8 -*-
# Rutas del VIAJE DE LOS PAQUETES (frame representativo 100):
#   tramo RADIO:   LHD -> AP servidor (por las galerías, de anim_enlace.csv)
#   tramo BACKBONE: AP servidor -> pique (Dijkstra por galerías = malla+fibra)
# Salida: flujo_paths.csv (dos polilíneas, separadas por fila de NaN).
import importlib.util, os, sys, heapq
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")

GS  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
TRB = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo"
spec = importlib.util.spec_from_file_location("datos", os.path.join(GS, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

segs = []
for cam in D.PRODUCCION:
    for i in range(len(cam)-1):
        segs.append((np.array(cam[i],float), np.array(cam[i+1],float)))

def clave(p): return (round(p[0],2), round(p[1],2))
nodos = {}
def nodo(p):
    k = clave(p)
    if k not in nodos: nodos[k] = np.array(k)
    return k
aristas = {}
def arista(k1,k2):
    w = float(np.hypot(k1[0]-k2[0], k1[1]-k2[1]))
    if w < 0.05: return
    aristas.setdefault(k1,[]).append((k2,w))
    aristas.setdefault(k2,[]).append((k1,w))

puntos_en = [[] for _ in segs]
for i,(A,B) in enumerate(segs):
    u = B-A; L = np.linalg.norm(u); u = u/L
    n = np.array([-u[1],u[0]])
    puntos_en[i].extend([0.0, L])
    for j,(C,E) in enumerate(segs):
        if i==j: continue
        for Q in (C,E):
            t = float(np.dot(Q-A,u)); d = abs(float(np.dot(Q-A,n)))
            if -0.3 <= t <= L+0.3 and d <= 2.6:
                puntos_en[i].append(min(max(t,0.0),L))
for i,(A,B) in enumerate(segs):
    u = B-A; L = np.linalg.norm(u); u = u/L
    ts = sorted(set(round(t,2) for t in puntos_en[i]))
    pts = [nodo(A + u*t) for t in ts]
    for a,b in zip(pts, pts[1:]): arista(a,b)

def conectar(P):
    mejor = (1e9, None, None)
    for (A,B) in segs:
        u = B-A; L = np.linalg.norm(u); u = u/L
        t = min(max(float(np.dot(P-A,u)),0.0),L)
        Q = A + u*t; d = float(np.hypot(*(P-Q)))
        if d < mejor[0]: mejor = (d, Q, (nodo(A), nodo(B)))
    kQ = nodo(mejor[1])
    for kk in mejor[2]: arista(kQ, kk)
    return kQ

def dijkstra(src, dst):
    dist = {src: 0.0}; prev = {}; pq = [(0.0, src)]
    while pq:
        d,k = heapq.heappop(pq)
        if k == dst: break
        if d > dist.get(k,1e18): continue
        for (k2,w) in aristas.get(k,[]):
            nd = d+w
            if nd < dist.get(k2,1e18):
                dist[k2]=nd; prev[k2]=k; heapq.heappush(pq,(nd,k2))
    path=[dst]
    while path[-1]!=src: path.append(prev[path[-1]])
    return path[::-1]

REC = np.loadtxt(os.path.join(TRB,"anim_recorrido.csv"), delimiter=",")
ENL = np.loadtxt(os.path.join(TRB,"anim_enlace.csv"), delimiter=",")
ids = [f"H{i+1}" for i in range(len(D.HAWKS))] + [f"C{i+1}" for i in range(len(D.CARDINALS_AP))]
aps = [np.array(p,float) for p in (list(D.HAWKS)+list(D.CARDINALS_AP))]

i0 = 100
x, y, k = REC[i0,1], REC[i0,2], int(REC[i0,3])
print(f"frame {i0}: LHD=({x:.1f},{y:.1f}), AP servidor = {ids[k-1]}")

# tramo RADIO (de anim_enlace)
pts = ENL[i0,2:]; pts = pts[~np.isnan(pts)]
radio = [(x,y)] + [(pts[j],pts[j+1]) for j in range(0,len(pts),2)] + [tuple(aps[k-1])]

# tramo BACKBONE: AP -> pique central
PIQUE = np.array(D.PIQUES[1], float)          # (25.98, 164.85)
kAP = conectar(aps[k-1]); kPQ = conectar(PIQUE)
path = dijkstra(kAP, kPQ)
backbone = [tuple(aps[k-1])] + [tuple(pp) for pp in path] + [tuple(PIQUE)]

MAX = max(len(radio), len(backbone))
out = np.full((2, MAX*2), np.nan)
for j,p in enumerate(radio):    out[0, j*2:j*2+2] = p
for j,p in enumerate(backbone): out[1, j*2:j*2+2] = p
np.savetxt(os.path.join(TRB,"flujo_paths.csv"), out, fmt="%.2f", delimiter=",")
print(f"radio: {len(radio)} pts | backbone: {len(backbone)} pts -> flujo_paths.csv")

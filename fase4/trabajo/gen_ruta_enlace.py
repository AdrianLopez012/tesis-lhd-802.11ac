# -*- coding: utf-8 -*-
# Calcula, para cada frame del recorrido, el CAMINO POR LAS GALERÍAS desde el
# LHD hasta su AP servidor (Dijkstra sobre el grafo del trazado). La señal no
# atraviesa la roca: el enlace visual debe rodear por las labores abiertas.
# Salida: anim_enlace.csv — por frame, hasta 12 puntos (x,y) rellenados con NaN.
import importlib.util, os, sys, heapq
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")

GS  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
TRB = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo"
spec = importlib.util.spec_from_file_location("datos", os.path.join(GS, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

# ---------- grafo del trazado ----------
segs = []
for cam in D.PRODUCCION:
    for i in range(len(cam)-1):
        segs.append((np.array(cam[i],float), np.array(cam[i+1],float)))

# nodos: extremos de segmento + intersecciones entre segmentos
def clave(p): return (round(p[0],2), round(p[1],2))
nodos = {}
def nodo(p):
    k = clave(p)
    if k not in nodos: nodos[k] = np.array(k)
    return k

# puntos de quiebre de cada segmento: extremos + proyecciones de extremos ajenos
puntos_en = [[] for _ in segs]
for i,(A,B) in enumerate(segs):
    u = B-A; L = np.linalg.norm(u); u = u/L
    n = np.array([-u[1],u[0]])
    puntos_en[i].extend([0.0, L])
    for j,(C,E) in enumerate(segs):
        if i==j: continue
        for Q in (C,E):
            t = float(np.dot(Q-A,u)); d = abs(float(np.dot(Q-A,n)))
            if 0-0.3 <= t <= L+0.3 and d <= 2.6:
                puntos_en[i].append(min(max(t,0.0),L))

aristas = {}   # k1 -> [(k2, peso)]
def arista(k1,k2):
    w = float(np.hypot(k1[0]-k2[0], k1[1]-k2[1]))
    if w < 0.05: return
    aristas.setdefault(k1,[]).append((k2,w))
    aristas.setdefault(k2,[]).append((k1,w))

for i,(A,B) in enumerate(segs):
    u = B-A; L = np.linalg.norm(u); u = u/L
    ts = sorted(set(round(t,2) for t in puntos_en[i]))
    pts = [nodo(A + u*t) for t in ts]
    for a,b in zip(pts, pts[1:]): arista(a,b)

print(f"grafo: {len(nodos)} nodos, {sum(len(v) for v in aristas.values())//2} aristas")

def punto_mas_cercano_en_red(P):
    """proyecta P al punto más cercano de cualquier segmento; devuelve (punto, k_ancla1, k_ancla2)"""
    mejor = (1e9, None, None, None)
    for (A,B) in segs:
        u = B-A; L = np.linalg.norm(u); u = u/L
        t = min(max(float(np.dot(P-A,u)),0.0),L)
        Q = A + u*t
        d = float(np.hypot(*(P-Q)))
        if d < mejor[0]:
            mejor = (d, Q, nodo(A+u*max(t-0.01,0)), (A,B,u,L,t))
    return mejor[1], mejor[3]

def dijkstra(src_k, dst_k):
    dist = {src_k: 0.0}; prev = {}; pq = [(0.0, src_k)]
    while pq:
        d,k = heapq.heappop(pq)
        if k == dst_k: break
        if d > dist.get(k,1e18): continue
        for (k2,w) in aristas.get(k,[]):
            nd = d+w
            if nd < dist.get(k2,1e18):
                dist[k2]=nd; prev[k2]=k; heapq.heappush(pq,(nd,k2))
    if dst_k not in dist: return None
    path=[dst_k]
    while path[-1]!=src_k: path.append(prev[path[-1]])
    return path[::-1]

def conectar(P):
    """ancla P a la red: devuelve nodo temporal insertado (con aristas a los quiebres vecinos)"""
    Q, seginfo = punto_mas_cercano_en_red(P)
    A,B,u,L,t = seginfo
    kQ = nodo(Q)
    # conectar Q con los extremos del segmento anfitrión
    for kk in (nodo(A), nodo(B)):
        arista(kQ, kk)
    return kQ

# ---------- APs y recorrido ----------
ids = [f"H{i+1}" for i in range(len(D.HAWKS))] + [f"C{i+1}" for i in range(len(D.CARDINALS_AP))]
aps = [np.array(p,float) for p in (list(D.HAWKS)+list(D.CARDINALS_AP))]
ap_k = [conectar(p) for p in aps]

REC = np.loadtxt(os.path.join(TRB,"anim_recorrido.csv"), delimiter=",")
MAXP = 12
salida = np.full((len(REC), 2+MAXP*2), np.nan)
for f in range(len(REC)):
    x,y,k = REC[f,1], REC[f,2], int(REC[f,3])
    salida[f,0] = REC[f,0]; salida[f,1] = k
    if k < 1: continue
    kL = conectar(np.array([x,y]))
    path = dijkstra(kL, ap_k[k-1])
    if path is None: continue
    pts = [np.array(kk) for kk in path]
    # simplificar colineales
    simp=[pts[0]]
    for i in range(1, len(pts)-1):
        a, b, c = simp[-1], pts[i], pts[i+1]
        v1 = b-a; v2 = c-b
        if np.linalg.norm(v1)>0 and np.linalg.norm(v2)>0:
            cosang = np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))
            if cosang > 0.999: continue
        simp.append(pts[i])
    simp.append(pts[-1])
    simp = simp[:MAXP]
    for i,pnt in enumerate(simp):
        salida[f, 2+i*2] = pnt[0]; salida[f, 3+i*2] = pnt[1]

np.savetxt(os.path.join(TRB,"anim_enlace.csv"), salida, fmt="%.2f", delimiter=",")
npts = np.sum(~np.isnan(salida[:,2::2]), axis=1)
print(f"rutas calculadas: {len(REC)} frames, puntos por ruta min/med/max = {npts.min()}/{npts.mean():.1f}/{npts.max()}")

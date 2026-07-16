# -*- coding: utf-8 -*-
# STL v3 — galerías de sección herradura con UNIONES LIMPIAS: las paredes se
# ABREN donde conecta otra galería/costilla (nada de muros atravesados).
import importlib.util, os, sys, struct
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")

GS = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
OUT = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\galeria_nv1640.stl"
spec = importlib.util.spec_from_file_location("datos", os.path.join(GS, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

W_MAIN = 4.0; W_RIB = 2.8; H_WALL = 2.4; NARC = 6; INSET = W_MAIN/2
tris = []
tris_techo = []

def quad(a,b,c,d): tris.append((a,b,c)); tris.append((a,c,d))
def tri(a,b,c): tris.append((a,b,c))

# ---------- recolectar segmentos ----------
draw_set = {(round(x,1),round(y,1)) for x,y in D.DRAWPOINTS}
segs = []   # (P1, P2, width, es_costilla)
for cam in D.PRODUCCION:
    fin = cam[-1]; es_cost = (round(fin[0],1),round(fin[1],1)) in draw_set
    for i in range(len(cam)-1):
        a, b = np.array(cam[i],float), np.array(cam[i+1],float)
        if es_cost:
            d = b-a; L = np.linalg.norm(d)
            a = a + d/L*INSET if L > INSET else a
        segs.append((a, b, W_RIB if es_cost else W_MAIN, es_cost))

# ---------- huecos en las paredes por conexiones ----------
def gaps_para(idx):
    """para el segmento idx devuelve {(+1|-1): [(t0,t1),...]} huecos por lado"""
    P1, P2, w, _ = segs[idx]
    d = P2-P1; L = np.linalg.norm(d); u = d/L
    n = np.array([-u[1], u[0]])
    out = {1: [], -1: []}
    for j,(Q1,Q2,wq,_) in enumerate(segs):
        if j == idx: continue
        for Q, Qo in ((Q1,Q2),(Q2,Q1)):
            # ¿el extremo Q de otro segmento toca la pared/centro de este?
            t = np.dot(Q-P1, u)
            if t < -wq/2 or t > L+wq/2: continue
            dist = np.dot(Q-P1, n)
            if abs(dist) > w/2 + 0.35: continue     # no toca este tramo
            # lado por el que llega: dirección del otro segmento
            lado = np.sign(np.dot(Qo-Q, n))
            if lado == 0: continue
            # el hueco va en la pared del lado desde el que VIENE el otro tramo
            lado_hueco = -int(np.sign(dist)) if abs(dist) > 0.3 else int(lado)
            t0, t1 = max(0.0, t-wq/2), min(L, t+wq/2)
            if t1 > t0: out[lado_hueco].append((t0, t1))
    # fusionar solapes
    for k in out:
        iv = sorted(out[k]); fus = []
        for a,b in iv:
            if fus and a <= fus[-1][1]: fus[-1] = (fus[-1][0], max(fus[-1][1], b))
            else: fus.append((a,b))
        out[k] = fus
    return out

def perfil_lado(w):
    """puntos (altura) del perfil de UNA pared con arco: (offset fijo, z varía)"""
    r = w/2
    pts = [(0.0), (H_WALL)]
    arco = []
    for k in range(1, NARC):
        th = np.pi*k/NARC
        arco.append((r*(1-np.cos(th)) if False else None))
    return pts

def tramo(idx):
    P1, P2, w, _ = segs[idx]
    d = P2-P1; L = np.linalg.norm(d)
    if L < 0.3: return
    u = d/L; n = np.array([-u[1], u[0]])
    r = w/2
    def PT(t, off, z):
        p = P1 + u*t + n*off
        return (p[0], p[1], z)
    # piso completo
    quad(PT(0,-r,0), PT(0,r,0), PT(L,r,0), PT(L,-r,0))
    # techo en arco -> STL separado (se pinta semitransparente)
    for k in range(NARC):
        th0, th1 = np.pi*k/NARC, np.pi*(k+1)/NARC
        o0, z0 = -r*np.cos(th0), H_WALL + r*np.sin(th0)
        o1, z1 = -r*np.cos(th1), H_WALL + r*np.sin(th1)
        a,b,c,d = PT(0,o0,z0), PT(L,o0,z0), PT(L,o1,z1), PT(0,o1,z1)
        tris_techo.append((a,b,c)); tris_techo.append((a,c,d))
    # paredes verticales por lado, con huecos
    g = gaps_para(idx)
    for lado in (1,-1):
        off = r*lado
        # construir intervalos sólidos = [0,L] menos huecos
        cortes = g[lado]
        t0 = 0.0; solidos = []
        for (a,b) in cortes:
            if a > t0: solidos.append((t0,a))
            t0 = max(t0,b)
        if t0 < L: solidos.append((t0,L))
        for (a,b) in solidos:
            if b-a < 0.05: continue
            quad(PT(a,off,0), PT(b,off,0), PT(b,off,H_WALL), PT(a,off,H_WALL))

for i in range(len(segs)):
    tramo(i)

# drawpoints: marca piramidal
for (x,y) in D.DRAWPOINTS:
    s=1.3
    base=[(x-s,y-s,0),(x+s,y-s,0),(x+s,y+s,0),(x-s,y+s,0)]; top=(x,y,1.5)
    for i in range(4): tri(base[i], base[(i+1)%4], top)

def wstl(path,tris):
    with open(path,"wb") as f:
        f.write(b"\x00"*80); f.write(struct.pack("<I",len(tris)))
        for (a,b,c) in tris:
            a,b,c=np.array(a),np.array(b),np.array(c)
            nrm=np.cross(b-a,c-a); nn=np.linalg.norm(nrm)
            nrm=nrm/nn if nn>0 else np.array([0,0,1.0])
            f.write(struct.pack("<3f",*nrm))
            for v in (a,b,c): f.write(struct.pack("<3f",*v))
            f.write(b"\x00\x00")

wstl(OUT,tris)
wstl(OUT.replace("galeria_nv1640","galeria_techo"),tris_techo)
print(f"STL v3 UNIONES LIMPIAS: {len(segs)} tramos, {len(tris)} triángulos")

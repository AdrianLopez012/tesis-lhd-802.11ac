# -*- coding: utf-8 -*-
# Genera STL 3D de las galerías con SECCIÓN DE HERRADURA REAL (paredes rectas +
# techo en arco), como una labor minera de verdad. Galerías principales anchas +
# costillas de acceso más delgadas + drawpoints. Desde la fuente única.
import importlib.util, os, sys, struct
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")

GS = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
OUT = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\galeria_nv1640.stl"
spec = importlib.util.spec_from_file_location("datos", os.path.join(GS, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

W_MAIN = 4.0    # galería principal
W_RIB  = 2.8    # costilla de acceso
H_WALL = 2.4    # altura de pared recta antes del arco
ARCO   = True   # techo en arco (herradura)
INSET  = W_MAIN/2
NARC   = 6      # segmentos del arco (suavidad del techo)
tris = []

def quad(a,b,c,d): tris.append((a,b,c)); tris.append((a,c,d))
def tri(a,b,c): tris.append((a,b,c))

def perfil_herradura(w):
    """devuelve los puntos (offset_lateral, altura) del contorno de la sección
    tipo herradura: sube por la pared izq, arco por el techo, baja pared der."""
    r = w/2
    pts = [(-r, 0), (-r, H_WALL)]          # pared izquierda
    if ARCO:
        for k in range(1, NARC):            # arco del techo (semicírculo)
            th = np.pi*k/NARC
            pts.append((-r*np.cos(th), H_WALL + r*np.sin(th)))
    pts.append((r, H_WALL))                 # inicio pared derecha (tope)
    pts.append((r, 0))                      # pared derecha
    return pts

def tramo(x1, y1, x2, y2, w):
    L = np.hypot(x2-x1, y2-y1)
    if L < 0.4: return
    ang = np.arctan2(y2-y1, x2-x1)
    nx, ny = -np.sin(ang), np.cos(ang)      # dirección lateral unitaria
    perf = perfil_herradura(w)
    # generar el "tubo" extruyendo el perfil de p1 a p2
    def P(px, py, off, z): return (px+nx*off, py+ny*off, z)
    for i in range(len(perf)-1):
        o1,z1 = perf[i]; o2,z2 = perf[i+1]
        a = P(x1,y1,o1,z1); b = P(x2,y2,o1,z1)
        c = P(x2,y2,o2,z2); d = P(x1,y1,o2,z2)
        quad(a,b,c,d)
    # piso (entre los dos extremos inferiores)
    o=w/2
    quad(P(x1,y1,-o,0), P(x1,y1,o,0), P(x2,y2,o,0), P(x2,y2,-o,0))

def draw_marker(x, y):
    """boca de extracción: pirámide baja marcando el drawpoint"""
    s=1.3
    base=[(x-s,y-s,0),(x+s,y-s,0),(x+s,y+s,0),(x-s,y+s,0)]; top=(x,y,1.5)
    for i in range(4):
        tri(base[i], base[(i+1)%4], top)

draw_set = {(round(x,1),round(y,1)) for x,y in D.DRAWPOINTS}
n_main=n_rib=0
for cam in D.PRODUCCION:
    fin=cam[-1]; es_costilla=(round(fin[0],1),round(fin[1],1)) in draw_set
    for i in range(len(cam)-1):
        a,b = np.array(cam[i],float), np.array(cam[i+1],float)
        if es_costilla:
            d=b-a; L=np.linalg.norm(d)
            a2 = a + d/L*INSET if L>INSET else a
            tramo(a2[0],a2[1],b[0],b[1],W_RIB); n_rib+=1
        else:
            tramo(a[0],a[1],b[0],b[1],W_MAIN); n_main+=1

for (x,y) in D.DRAWPOINTS: draw_marker(x,y)

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
print(f"STL HERRADURA: {n_main} galerías + {n_rib} costillas + {len(D.DRAWPOINTS)} drawpoints, {len(tris)} triángulos")

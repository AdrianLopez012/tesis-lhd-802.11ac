# -*- coding: utf-8 -*-
# Genera un STL 3D de las galerías (paredes, piso, techo) desde la fuente única
# mapa_nv1640_datos.py, para el ray-tracing SBR de MATLAB. Sección 4x4 m.
import importlib.util, os, sys, struct
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")

GS = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
OUT = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\galeria_nv1640.stl"
spec = importlib.util.spec_from_file_location("datos", os.path.join(GS, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

W = 4.0; H = 4.0   # sección de galería 4x4 m
tris = []          # lista de triángulos (cada uno: 3 vértices)

def quad(a, b, c, d):
    # dos triángulos por cara
    tris.append((a, b, c)); tris.append((a, c, d))

def tramo(x1, y1, x2, y2):
    """genera un prisma hueco (túnel) entre (x1,y1) y (x2,y2), sección WxH"""
    L = np.hypot(x2-x1, y2-y1)
    if L < 0.5: return
    ang = np.arctan2(y2-y1, x2-x1)
    ux, uy = -np.sin(ang)*W/2, np.cos(ang)*W/2   # normal horizontal
    # 8 vértices del prisma (4 en inicio, 4 en fin), z=0..H
    def V(px, py, off, z): return (px+off[0], py+off[1], z)
    p1, p2 = (x1, y1), (x2, y2)
    # SIN TECHO (vista de corte de mina: se ve el interior y el vehículo dentro).
    # piso
    quad(V(*p1,(ux,uy),0), V(*p1,(-ux,-uy),0), V(*p2,(-ux,-uy),0), V(*p2,(ux,uy),0))
    # pared izquierda
    quad(V(*p1,(ux,uy),0), V(*p2,(ux,uy),0), V(*p2,(ux,uy),H), V(*p1,(ux,uy),H))
    # pared derecha
    quad(V(*p1,(-ux,-uy),0), V(*p1,(-ux,-uy),H), V(*p2,(-ux,-uy),H), V(*p2,(-ux,-uy),0))

# generar túneles para cada tramo de producción
n = 0
for cam in D.PRODUCCION:
    for i in range(len(cam)-1):
        a, b = cam[i], cam[i+1]
        tramo(a[0], a[1], b[0], b[1]); n += 1

# escribir STL binario
def wstl(path, tris):
    with open(path, "wb") as f:
        f.write(b"\x00"*80)
        f.write(struct.pack("<I", len(tris)))
        for (a, b, c) in tris:
            a, b, c = np.array(a), np.array(b), np.array(c)
            nrm = np.cross(b-a, c-a); nn = np.linalg.norm(nrm)
            nrm = nrm/nn if nn > 0 else np.array([0,0,1.0])
            f.write(struct.pack("<3f", *nrm))
            for v in (a, b, c): f.write(struct.pack("<3f", *v))
            f.write(b"\x00\x00")

wstl(OUT, tris)
print(f"STL generado: {n} tramos, {len(tris)} triángulos -> {OUT}")

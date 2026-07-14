# -*- coding: utf-8 -*-
# Exporta para MATLAB: (a) grilla de RSSI sobre las galerías calculada con el
# MISMO modelo del mapa de cobertura (importa mapa_cobertura_pro), (b) recorrido
# real del LHD, (c) tramos de galería. Fuente única, cero duplicación.
import importlib.util, os, re, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")

GS  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
SIM = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3"
TRB = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo"

# importar el módulo del mapa (ejecuta el script una vez; reutilizamos rssi_en)
spec = importlib.util.spec_from_file_location("mc", os.path.join(GS, "mapa_cobertura_pro.py"))
MC = importlib.util.module_from_spec(spec); spec.loader.exec_module(MC)
D = MC.D   # datos de geometría ya cargados por el módulo

# --- grilla: puntos a lo largo de cada tramo de PRODUCCION, 3 carriles ---
pts = []
for cam in D.PRODUCCION:
    for i in range(len(cam) - 1):
        a, b = np.array(cam[i], float), np.array(cam[i+1], float)
        L = np.linalg.norm(b - a)
        if L < 0.5: continue
        u = (b - a) / L
        n = np.array([-u[1], u[0]])
        for s in np.arange(0, L + 0.01, 1.4):
            p = a + u * min(s, L)
            for off in (-1.3, 0.0, 1.3):
                q = p + n * off
                pts.append((q[0], q[1], MC.rssi_en(q[0], q[1])))
pts = np.array(pts)
np.savetxt(os.path.join(TRB, "grid_rssi.csv"), pts, fmt="%.2f", delimiter=",")
print(f"grid_rssi: {len(pts)} puntos | RSSI {pts[:,2].min():.0f}..{pts[:,2].max():.0f} dBm")

# --- recorrido real (del header autogenerado) ---
txt = open(os.path.join(SIM, "recorrido_nv1640.h"), encoding="utf-8").read()
wp = [(float(x), float(y)) for _, x, y in re.findall(r"\{([\d.]+),([-\d.]+),([-\d.]+)\}", txt)]
np.savetxt(os.path.join(TRB, "ruta.csv"), np.array(wp), fmt="%.2f", delimiter=",")
print(f"ruta: {len(wp)} waypoints")

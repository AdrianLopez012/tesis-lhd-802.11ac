# -*- coding: utf-8 -*-
# Exporta datos del recorrido real (pos_log de NS-3) + geometría + AP para la
# animación 3D del LHD en MATLAB. Todo desde la fuente única.
import importlib.util, os, sys, csv
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")

GS  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
RES = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\results"
TRB = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo"
spec = importlib.util.spec_from_file_location("datos", os.path.join(GS, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

ids = [f"H{i+1}" for i in range(len(D.HAWKS))] + [f"C{i+1}" for i in range(len(D.CARDINALS_AP))]
aps = list(D.HAWKS) + list(D.CARDINALS_AP)

# recorrido: t, x, y, idx_ap_asociado, rssi_asociado
rows = list(csv.DictReader(open(os.path.join(RES, "principal_s1_v3_pos_log.csv"))))
rec = []
for r in rows:
    ap = r["assoc_ap"].strip()
    idx = ids.index(ap)+1 if ap in ids else 0
    rec.append([float(r["time_s"]), float(r["x"]), float(r["y"]), idx, float(r["rssi_assoc_dbm"])])
np.savetxt(os.path.join(TRB, "anim_recorrido.csv"), np.array(rec), fmt="%.2f", delimiter=",")

# AP: x, y, tipo (1=Hawk, 2=Cardinal)
apm = [[x, y, 1 if i < len(D.HAWKS) else 2] for i,(x,y) in enumerate(aps)]
np.savetxt(os.path.join(TRB, "anim_aps.csv"), np.array(apm), fmt="%.2f", delimiter=",")

print(f"recorrido: {len(rec)} pasos | AP: {len(apm)} | listo para MATLAB")

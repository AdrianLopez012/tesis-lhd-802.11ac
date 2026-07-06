"""
Geometría NV1640 — REGULARIZADA a partir de la referencia del usuario (2026-07-06)
==================================================================================
El usuario dio una referencia (trazos aproximados en editor_mapa_nv1640.html).
Aquí se REGULARIZA en geometría limpia y coherente, respetando la estructura:
  - 3 galerías de producción verticales paralelas (X=0, 26, 52), largo 134.85 m.
  - Cruceros superior e inferior que las unen.
  - Layout EL TENIENTE: en cada nivel, un drawbell AL CENTRO entre dos galerías
    y sus dos drawpoints a los COSTADOS (uno por galería), unidos por costillas.
  - Rampa de acceso suave: entra abajo-izquierda, sube y llega a la galería.
  - 2 botaderos arriba (descarga).

Todo parametrizado; cambiar el bloque PARÁMETROS reescala/reordena todo.
Genera geometría en METROS. plano_nv1640_pro.py la dibuja.
"""
import numpy as np

# ---------------- PARÁMETROS (metros) ----------------
LARGO_CALLE = 134.85          # largo galerías de producción (dato real)
SEP         = 25.98           # separación entre galerías (dato real)
X = [0.0, SEP, 2*SEP]         # x de las 3 galerías
YB, YT = 0.0, LARGO_CALLE     # base y tope de las galerías
N_NIV = 6                     # niveles de drawbells a lo largo de la galería
Y0, Y1 = 16.0, LARGO_CALLE-14 # rango vertical de los drawbells
ANG_COSTILLA = 55.0           # grado de inclinación de las costillas (° vs horizontal)
COSTILLA_LEN = 11.0           # largo del ramal de acceso al drawpoint (m)
RAMPA_LEN_INF = 176.0         # largo de la rama inferior de la rampa
BOT_DY = 30.0                 # altura de los botaderos sobre el tope

# ---------------- GALERÍAS + CRUCEROS ----------------
PRODUCCION = []
for x in X:                                   # 3 calles verticales
    PRODUCCION.append([(x,YB),(x,YT)])
PRODUCCION.append([(X[0],YT),(X[2],YT)])      # crucero superior
PRODUCCION.append([(X[0],YB),(X[2],YB)])      # crucero inferior

# ---------------- DRAWBELLS (centro) + DRAWPOINTS (costados) + COSTILLAS ----------------
# Las costillas salen INCLINADAS (ANG_COSTILLA) desde la galería hacia el drawpoint,
# y el drawbell queda al centro entre las dos costillas enfrentadas (El Teniente).
DRAWBELLS=[]; DRAWPOINTS=[]
ys = np.linspace(Y0, Y1, N_NIV)
centros = [SEP*0.5, SEP*1.5]
calles_par = [(X[0],X[1]), (X[1],X[2])]
a = np.radians(ANG_COSTILLA)
dxc = COSTILLA_LEN*np.cos(a)   # avance horizontal de la costilla
dyc = COSTILLA_LEN*np.sin(a)   # avance vertical = inclinación de la costilla
for y in ys:
    for (cx,(xa,xb)) in zip(centros, calles_par):
        # drawbell al centro, a la altura y
        DRAWBELLS.append((cx,y))
        # drawpoints: junto al drawbell (uno a cada lado), misma altura
        dpa=(cx-2.5, y); dpb=(cx+2.5, y)
        DRAWPOINTS.append(dpa); DRAWPOINTS.append(dpb)
        # costillas INCLINADAS: arrancan de la galería más abajo y suben en
        # diagonal hasta el drawpoint (el grado de inclinación queda en el ramal)
        PRODUCCION.append([(xa, y-dyc), dpa])   # desde galería izq sube al drawpoint izq
        PRODUCCION.append([(xb, y-dyc), dpb])   # desde galería der sube al drawpoint der

# ---------------- RAMPAS DE ACCESO ----------------
# Rampa principal: entra abajo-izquierda, sube en curva y llega al TOPE de la
# galería (arriba) — por donde ingresa el LHD.  Rama inferior: acceso por abajo.
RAMPAS = [
    # rampa superior: sube recta por la izquierda, gira y llega al tope (codo suave)
    {"pts":[(-RAMPA_LEN_INF,-28.0),(-RAMPA_LEN_INF,YT-8),(-RAMPA_LEN_INF+30,YT),(X[0],YT)],
     "curvas":[2]},
    # rama inferior: sube recto y entra horizontal a la galería por abajo
    {"pts":[(-RAMPA_LEN_INF,-28.0),(-RAMPA_LEN_INF+18,-8),(X[0],0.0)], "curvas":[1]},
]

# ---------------- BOTADEROS (arriba) + tramos de subida ----------------
# Uno a la izquierda (sobre galería 1) y el otro AL MEDIO (sobre galería central).
BOTADEROS = [(X[0], YT+BOT_DY), (X[1], YT+BOT_DY)]
PRODUCCION.append([(X[0],YT),(X[0],YT+BOT_DY-4)])
PRODUCCION.append([(X[1],YT),(X[1],YT+BOT_DY-4)])

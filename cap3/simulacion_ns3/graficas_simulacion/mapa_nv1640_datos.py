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
N_NIV = 5                     # niveles de drawbells (validado con el usuario)
Y0, Y1 = 30.0, LARGO_CALLE-14 # rango vertical de los drawbells (Y0 más alto = más
                              # separación entre el recto inicial y la 1ª costilla)
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

# ---------------- DRAWBELLS + DRAWPOINTS + COSTILLAS (layout validado) ----------------
# Estructura confirmada con el usuario (esquema de aperturas):
#   - N_NIV niveles de drawbells compartidos.
#   - Drawbell A (entre C1 y C2, centro X=SEP*0.5) por nivel.
#   - Drawbell B (entre C2 y C3, centro X=SEP*1.5) por nivel.
#   - C1: costilla giro ABIERTO (sube ↗) hacia el drawbell A.
#   - C2 lado izq: costilla giro CERRADO (baja ↘) hacia el drawbell A.
#   - C2 lado der: costilla giro ABIERTO (sube ↗) hacia el drawbell B.
#   - C3: costilla giro CERRADO (baja ↙) hacia el drawbell B.
#   - Cada drawbell tiene 2 drawpoints (uno por lado).
# 'abierto' = la costilla sale hacia ARRIBA respecto al sentido de subida (fácil).
# 'cerrado' = sale hacia ABAJO (giro cerrado, el LHD no entra fácil).
DRAWBELLS=[]; DRAWPOINTS=[]
# guardamos metadatos de accesibilidad por drawpoint: (x,y,acceso) acceso: 'abierto'/'cerrado'/'recto'
DRAWPOINTS_INFO=[]
# COSTILLA_APPROACH: por cada drawpoint, cómo encararlo en giro abierto:
#   (dp) -> {'pie':(x,y), 'gal':x_galeria, 'sentido':'sube'/'baja'}
# El LHD debe llegar al 'pie' viniendo en ese 'sentido' (rodeando si hace falta)
# para entrar de frente. Así TODOS los drawpoints son alcanzables.
COSTILLA_APPROACH={}
def _reg(dp, pie, gal, sentido):
    COSTILLA_APPROACH[(round(dp[0],1),round(dp[1],1))]={'pie':pie,'gal':gal,'sentido':sentido}
ys = np.linspace(Y0, Y1, N_NIV)
a = np.radians(ANG_COSTILLA)
dxc = COSTILLA_LEN*np.cos(a)   # avance horizontal de la costilla
dyc = COSTILLA_LEN*np.sin(a)   # inclinación vertical
cAB = SEP*0.5    # centro drawbell entre C1 y C2
cBC = SEP*1.5    # centro drawbell entre C2 y C3

# --- drawpoints RECTOS al inicio (abajo) de C1 y C2, mirando a la derecha ---
def add_recto(xgal, y):
    dp=(xgal+COSTILLA_LEN*0.7, y)
    DRAWPOINTS.append(dp); DRAWPOINTS_INFO.append((dp[0],dp[1],'recto'))
    PRODUCCION.append([(xgal,y), dp])
    _reg(dp,(xgal,y),xgal,'sube')   # recto: se encara subiendo/de frente
add_recto(X[0], YB+8)   # C1 recto
add_recto(X[1], YB+8)   # C2 recto

# Nota: 'abierto'/'cerrado' es respecto a subir; pero TODOS son alcanzables
# rodeando. El campo 'sentido' dice desde qué marcha se encara en giro abierto:
#   costilla que sube ↗  -> se encara SUBIENDO por su galería.
#   costilla que baja ↘↙ -> se encara BAJANDO por su galería.
for y in ys:
    # ----- Drawbell A (C1 sube ↗  +  C2 izq baja ↘) -----
    DRAWBELLS.append((cAB,y))
    dpA1=(cAB-2.5,y); dpA2=(cAB+2.5,y)
    DRAWPOINTS.append(dpA1); DRAWPOINTS.append(dpA2)
    DRAWPOINTS_INFO.append((dpA1[0],dpA1[1],'abierto'))
    DRAWPOINTS_INFO.append((dpA2[0],dpA2[1],'cerrado'))
    PRODUCCION.append([(X[0], y-dyc), dpA1])   # C1: costilla sube ↗
    PRODUCCION.append([(X[1], y+dyc), dpA2])   # C2 izq: costilla baja ↘
    _reg(dpA1,(X[0],y-dyc),X[0],'sube')        # encara subiendo por C1
    _reg(dpA2,(X[1],y+dyc),X[1],'baja')        # encara BAJANDO por C2
    # ----- Drawbell B (C2 der sube ↗  +  C3 baja ↙) -----
    DRAWBELLS.append((cBC,y))
    dpB1=(cBC-2.5,y); dpB2=(cBC+2.5,y)
    DRAWPOINTS.append(dpB1); DRAWPOINTS.append(dpB2)
    DRAWPOINTS_INFO.append((dpB1[0],dpB1[1],'abierto'))
    DRAWPOINTS_INFO.append((dpB2[0],dpB2[1],'cerrado'))
    PRODUCCION.append([(X[1], y-dyc), dpB1])   # C2 der: costilla sube ↗
    PRODUCCION.append([(X[2], y+dyc), dpB2])   # C3: costilla baja ↙
    _reg(dpB1,(X[1],y-dyc),X[1],'sube')        # encara subiendo por C2
    _reg(dpB2,(X[2],y+dyc),X[2],'baja')        # encara BAJANDO por C3

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

# ---------------- PIQUES DE TRASPASO (ore pass) + tramos de subida ----------------
# Punto donde el LHD vacía el material (nombre técnico: pique de traspaso / ore pass).
# Uno a la izquierda (sobre galería 1) y el otro AL MEDIO (sobre galería central).
PIQUES = [(X[0], YT+BOT_DY), (X[1], YT+BOT_DY)]
BOTADEROS = PIQUES   # alias por compatibilidad
PRODUCCION.append([(X[0],YT),(X[0],YT+BOT_DY-4)])
PRODUCCION.append([(X[1],YT),(X[1],YT+BOT_DY-4)])

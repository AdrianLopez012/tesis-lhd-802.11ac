"""
Geometría NV1640 — EDITADA POR EL USUARIO en editor_mapa_nv1640.html (2026-07-06)
=================================================================================
Fuente única de verdad de la geometría real de la zona de teleoperación.
Exportada del editor visual (escala 1 m/px). Coordenadas en METROS.

Estructura:
  - 3 galerías de producción verticales (X=0, 26, 52) de ~135 m + cruceros.
  - Costillas en espina de pescado (layout El Teniente) hacia los drawpoints.
  - 10 drawbells (mineral compartido) + 22 drawpoints en pares.
  - Rampa de acceso con 2 curvas (entra abajo-izq, sube a la zona) + rama inferior.
  - 2 botaderos arriba (descarga).

Este módulo solo define los datos; plano_nv1640_pro.py los dibuja.
Marca {'curva': True} en un punto = ese vértice es curvo (control en 'c').
"""

# Cada camino: dict con tipo y lista de puntos (x, y). Punto curvo lleva 'c'=(cx,cy).
PRODUCCION = [
    [(-74.9,135.8),(0.0,134.8),(0.0,0.0),(-24.1,-0.7)],
    [(26.0,0.0),(26.0,134.8),(25.1,161.7)],
    [(0.0,134.8),(52.0,134.8),(52.0,0.0)],
    [(0.0,0.0),(52.0,0.0)],
    [(0.0,134.8),(0.0,160.8)],
    [(1.0,115.7),(11.4,119.7),(25.1,124.7)],
    [(1.0,96.6),(13.9,100.5),(25.8,103.5)],
    [(0.5,76.2),(13.7,80.4),(25.6,83.6)],
    [(0.5,55.5),(14.2,59.0),(26.6,62.3)],
    [(-0.3,34.2),(14.4,38.1),(25.8,41.4)],
    [(0.5,16.0),(13.2,16.5)],
    [(25.8,103.5),(40.5,106.7),(51.9,109.3)],
    [(25.6,83.6),(40.5,86.8),(53.0,90.3)],
    [(26.6,62.3),(40.1,65.4),(53.0,67.4)],
    [(25.8,41.4),(39.8,44.0),(51.5,46.6)],
    [(25.6,25.2),(40.1,27.4),(51.5,29.8)],
    [(26.0,15.7),(39.8,15.5)],
]

# Rampas: (punto, ..., con curvas donde corresponde)
RAMPAS = [
    {"pts":[(-254.8,-31.8),(-225.2,-24.4),(-176.4,-24.1),(-175.9,59.5),
            (-164.2,73.3),(-125.4,74.6),(-74.9,135.8)], "curvas":[3,5]},
    {"pts":[(-24.1,-0.7),(-176.4,0.6)], "curvas":[]},
]

DRAWBELLS = [
    (11.7,120.2),(13.7,100.8),(13.9,80.7),(13.9,59.5),(14.9,37.6),
    (40.5,106.3),(40.1,87.0),(40.2,65.3),(40.0,43.9),(39.9,27.3),
]

DRAWPOINTS = [
    (12.9,37.1),(16.4,38.1),(12.7,58.5),(16.0,59.1),(12.0,79.9),(15.2,81.0),
    (12.5,100.3),(15.6,100.6),(10.3,118.9),(13.3,120.0),(13.2,16.4),(40.0,15.4),
    (38.8,27.1),(41.2,27.5),(39.1,44.0),(40.8,44.4),(39.0,64.9),(41.4,65.6),
    (39.3,86.7),(41.4,87.2),(38.8,105.8),(41.5,106.7),
]

BOTADEROS = [(0.0,164.8),(24.8,165.7)]

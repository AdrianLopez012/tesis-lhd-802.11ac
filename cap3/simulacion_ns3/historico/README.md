# Histórico — versiones anteriores de la simulación

Esta carpeta conserva, por **trazabilidad**, las versiones previas de la simulación que
fueron reemplazadas por la versión vigente (`../lhd-teleop-v3-real.cc`). **No forman
parte del diseño final** de la tesis; se guardan solo como registro de la evolución.

| Carpeta | Contenido |
|---------|-----------|
| `cc/` | `.cc` de versiones v2/v9 (geometría de galería recta, reemplazada por la geometría real) |
| `scripts/` | scripts de gráficas y análisis de las versiones v8.2/v9 |
| `png/` | figuras y GIF de versiones anteriores |
| `results/` | resultados (CSV/XML) de las simulaciones v8.2 y v9 |

**Diferencia clave con la versión vigente:** las versiones históricas modelaban la zona
como una galería recta con ramales; la versión vigente (v3-real) usa la **geometría real**
del nivel 1640 (3 galerías de producción paralelas, cruceros, drawpoints y piques) y el
**recorrido real** del LHD, con todos los KPIs verificados.

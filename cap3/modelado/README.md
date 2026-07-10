# Modelado de propagación — nota de vigencia

**Qué sigue vigente de esta carpeta:** las curvas de propagación del modelo
two-slope (pérdida vs distancia axial, comparación con Sun & Akyildiz 2009,
ajuste de exponentes n1/n2) son análisis **independientes del layout de la
mina** y siguen siendo el fundamento del modelo usado en la simulación vigente.

**Qué está OBSOLETO:** `modelo_definitivo.py` contiene además la TOPOLOGÍA de
la versión v9 (galería recta de ~318 m con ramales en x=183.7 y x=318.5), que
fue reemplazada por la geometría real de NV1640 (3 galerías El Teniente; ver
`../simulacion_ns3/graficas_simulacion/mapa_nv1640_datos.py`). Las figuras de
**layout/esquema de zona** generadas aquí NO deben usarse en el documento de la
tesis — usar `plano_nv1640_pro.png` y `mapa_cobertura_pro.png` de
`../simulacion_ns3/graficas_simulacion/`.

Los parámetros del modelo (n1=1.9, n2=3.4, d_bp=40 m, penal NLOS 10 dB) tienen
fuente única en `../simulacion_ns3/parametros_rf.py` (dict `PROPAGACION`).

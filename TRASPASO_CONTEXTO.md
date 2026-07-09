# Documento de traspaso — Tesis red 802.11ac para teleoperación LHD (Nexa NV1640)

> **Propósito:** este archivo contiene TODO el contexto del trabajo realizado, desde la
> configuración de GitHub hasta el estado actual, para que otra cuenta/sesión pueda
> continuar sin problemas. Léelo completo antes de continuar.
>
> Fecha del traspaso: 2026-07-09

---

## 1. QUIÉN Y QUÉ

- **Usuario:** Adrián López — estudiante de Ingeniería de Telecomunicaciones, PUCP.
  Email: alvaro.lopez@pucp.edu.pe
- **Tesis:** *"Diseño de una red IEEE 802.11ac para la teleoperación de un vehículo LHD
  en la extracción de mineral en galerías subterráneas"*. Caso: mina Nexa Cerro Lindo,
  nivel **NV1640**. Asesor: Pastor David Chávez Muñoz.
- **Naturaleza:** trabajo de gabinete (modelado + simulación, sin despliegue físico).
  1 solo LHD. Layout de mina tipo **block caving El Teniente**.
- **Objetivo del trabajo con la IA:** construir la simulación NS-3 y las figuras que
  alimentan el **Capítulo 3** (diseño y validación por simulación) de la tesis.

### Idioma y estilo
- Todo en **español**. El usuario prefiere respuestas directas, honestas y sin adornos.
- Máxima fiabilidad: **nunca fabricar resultados**. Si algo no cumple o hay un bug, se
  dice con transparencia. El usuario valora esto explícitamente.
- Títulos de figuras/tablas: **formales y sobrios**, no literales de la instrucción.
  Estado de KPIs: la palabra **"Cumple"** (sin íconos/check), con color verde suave.

---

## 2. GITHUB Y GIT

- **Repo (privado):** https://github.com/AdrianLopez012/tesis-lhd-802.11ac.git
- **Remote:** `origin`
- **Rama de trabajo actual:** `geometria-real-nv1640`
- **Rama principal:** `main`
- Usuario git: Adrian Lopez
- **Convención de commits:** mensajes en español, descriptivos, terminando con
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Se hace commit al terminar cada bloque de trabajo. NO se hace push automático salvo
  que el usuario lo pida.

---

## 3. ENTORNO DE EJECUCIÓN

- **SO:** Windows 11. Shell primario PowerShell; también Bash (Git Bash) disponible.
- **Proyecto:** `C:\Users\Adrian Lopez\Documents\tesis_proyecto`
- **NS-3:** se ejecuta en **WSL** (Ubuntu). Ruta: `~/ns-allinone-3.40/ns-3.40`
  (versión **ns-3.40**). Se invoca con `wsl.exe -e bash -c '...'` desde Windows.
- **Flujo de compilar/correr NS-3:**
  ```bash
  # copiar fuentes a scratch/ y compilar
  cp lhd-teleop-v3-real.cc geometria_nv1640.h recorrido_nv1640.h parametros_rf.h \
     ~/ns-allinone-3.40/ns-3.40/scratch/
  cd ~/ns-allinone-3.40/ns-3.40
  ./ns3 build scratch/lhd-teleop-v3-real
  ./ns3 run "lhd-teleop-v3-real --scenario=mobility --simTime=300"
  ```
- **IMPORTANTE (aprendido):** las simulaciones **NO se pueden paralelizar** en este WSL
  (tanto el binario directo como varios `./ns3 run` a la vez se CUELGAN por contención
  del directorio de build de ns-3). Se corren **EN SERIE**. La batería completa (14
  corridas de 300 s) tarda **~3 HORAS** (medido: 10714 s el 2026-07-09; una versión
  anterior de este documento decía 30-35 min por error). Es lento pero 100% fiable.
- **Lanzar la batería en background desde Windows:** usar `setsid nohup ... < /dev/null &`
  y VERIFICAR con `pgrep` que el proceso vive antes de dar por lanzado. Un `nohup ... &`
  simple dentro de `wsl.exe -e bash -c "..."` MUERE al cerrar la sesión (aprendido:
  un lanzamiento falló silenciosamente y el log viejo dio un falso "completado").
- La batería se lanza con `nohup` y se monitorea leyendo `~/bateria_v3.log`:
  ```bash
  cp run_escenarios_v3.sh ~/ && cd ~ && nohup bash run_escenarios_v3.sh > ~/bateria_v3.log 2>&1 &
  ```

---

## 4. LA GEOMETRÍA REAL (clave del proyecto)

La zona de teleoperación del NV1640 es un **polígono de producción** con layout
El Teniente (block caving), NO una galería recta. Componentes:
- **3 galerías de producción paralelas** verticales en X = 0, 25.98, 51.96 m; largo ~135 m.
- **Cruceros** superior e inferior que unen las galerías.
- **Drawpoints** (bocas físicas de extracción de mineral) en las costillas/zanjas.
- **Drawbells** compartidos entre calles (dos drawpoints comparten un drawbell).
- **Piques de traspaso** (puntos de descarga; y=164.85, por encima del crucero superior).
- **Rampa de acceso** (baja a y≈−176 m) — es SOLO acceso manual/contexto, NO se teleopera.

### Terminología importante (el usuario la enseñó explícitamente)
- **Drawpoint** = boca física de extracción → SÍ va en el mapa.
- **Breakpoint** = parámetro económico de cierre → NO se dibuja (no confundir).
- **Pique de traspaso / ore pass** = punto de descarga (antes llamado "botadero").
- **Zanjas / costillas** = las calles de producción.

### Versiones del modelo
- La geometría de galería recta con ramales (versiones **v2/v8.2/v9**) es **INCORRECTA**
  y fue reemplazada. Está archivada en `cap3/simulacion_ns3/historico/`.
- La versión vigente es **v3-REAL** (geometría real + recorrido real del GIF).

---

## 5. PARÁMETROS TÉCNICOS (de datasheets reales)

- **Estándar:** IEEE 802.11ac (Wi-Fi 5), **5.0 GHz**, canal **40 MHz**, **2×2 MIMO**.
- **AP Hawk** (galerías): 30 dBm, antena 11 dBi. Hay **5**.
- **AP Cardinal** (cruceros/mesh): 23 dBm, antena 7.5 dBi. Hay **7**.
- **LHD:** embarca radio tipo Cardinal (23 dBm) + antena **HELI-40** (4.8 dBi).
- **Pérdidas de sistema:** L_system = 9.4 dB.
- **Mesh:** Rajant **InstaMesh** (L2, sin root node, make-before-break) + backbone de
  fibra óptica en anillo (switches Fortinet, gateway Rajant SLP-1025).
- **Modelo de propagación:** two-slope calibrado contra site survey **TamoGraph**:
  n₁=1.9 (LOS), n₂=3.4 (NLOS), d_bp=40 m. Distancia por **ruta de túnel** (la señal
  sigue las galerías, no cruza roca) + penalización NLOS de 10 dB por galería cruzada.
- Fuente única de estos valores: `cap3/simulacion_ns3/parametros_rf.py`.

### QoS (802.11e/WMM)
- **Vídeo** = AC_VI (TOS 0xb8), 40 Mbps uplink.
- **Comandos** = AC_VO (TOS 0xC0), ≤0.5 Mbps downlink.
- **Telemetría** = AC_BE (TOS 0x00), 0.1 Mbps uplink.

---

## 6. KPIs OFICIALES DE LA TESIS (RNF) — los 6 que la simulación verifica

| KPI | Requisito |
|-----|-----------|
| OWD comandos | ≤ 20 ms |
| RTT (lazo de control) | ≤ 40 ms |
| PLR comandos | ≤ 0.1% estable / ≤ 0.5% movilidad |
| Latencia E2E vídeo | ≤ 150 ms (incluye 35 ms de codec) |
| Jitter P95 (vídeo) | ≤ 10 ms |
| Throughput vídeo | ≥ 38 Mbps (10-50 Mbps, 2-4 cámaras) |
| PLR vídeo | ≤ 1% |
| Handover | ≤ 150 ms (RNF-05) |
| Disponibilidad | ≥ 99.9% (RNF-06) |

### RESULTADO ACTUAL (10 semillas, escenario de operación) — TODOS CUMPLEN
- OWD comandos: **3.04 ± 0.26 ms** · PLR comandos: **0.06%**
- Vídeo E2E: **35.89 ± 0.28 ms** · jitter P95: **0.28 ms** · throughput: **40.29 Mbps** · PLR: **0.01%**
- Telemetría OWD: **3.08 ms** · PLR: **0.14%**
- **RTT: 6.12 ± 0.47 ms** · **Disponibilidad: 100%**
- **Handover: 0.9 ms** (escenario dedicado) ≪ 150 ms
- **10/10 semillas cumplen los 8 indicadores.**

---

## 7. ESTRUCTURA DEL REPOSITORIO

```
tesis_proyecto/
├── TRASPASO_CONTEXTO.md          # este archivo
├── editor_mapa_nv1640.html       # editor visual interactivo de la geometría
├── mapa_cobertura_nv1640.html    # visor de cobertura
├── dashboard.html
├── historico/                    # material antiguo a nivel raíz
└── cap3/
    ├── config/  modelado/  raytracing/
    ├── tamograph/               # reporte TamoGraph real (PDF + imágenes)
    └── simulacion_ns3/          # ← NÚCLEO DEL TRABAJO
        ├── README.md            # documentación de la simulación (LEER)
        ├── lhd-teleop-v3-real.cc        # simulación NS-3 VIGENTE (~640 líneas)
        ├── geometria_nv1640.h           # AUTOGENERADO (namespace geo)
        ├── recorrido_nv1640.h           # AUTOGENERADO (namespace rec)
        ├── parametros_rf.h              # AUTOGENERADO (namespace rf)
        ├── parametros_rf.py             # fuente única de parámetros RF
        ├── run_escenarios_v3.sh         # batería de 14 escenarios (EN SERIE)
        ├── results/                     # resultados v3 (CSV/XML)
        ├── graficas_simulacion/         # scripts y figuras (ver §8)
        └── historico/                   # v2/v8/v9 archivadas (con su README)
```

### Fuente única de verdad de la geometría
`graficas_simulacion/mapa_nv1640_datos.py` define TODA la geometría (galerías,
cruceros, drawpoints, drawbells, piques, posiciones de los 12 AP). De ahí se generan
los headers C++ y todas las figuras. **Si se edita la geometría, hay que regenerar:**
```bash
cd graficas_simulacion
python generar_geometria_h.py    # -> ../geometria_nv1640.h
python generar_recorrido_h.py    # -> ../recorrido_nv1640.h
python generar_parametros_h.py   # -> ../parametros_rf.h
```

---

## 8. SCRIPTS DE FIGURAS Y QUÉ GENERAN (todos en graficas_simulacion/)

| Script | Salida | Descripción |
|--------|--------|-------------|
| `mapa_nv1640_datos.py` | — | fuente única de geometría/AP |
| `generar_geometria_h.py` | geometria_nv1640.h | geometría → C++ |
| `generar_recorrido_h.py` | recorrido_nv1640.h | recorrido LHD → C++ (exporta SPEED_BASE=2.22) |
| `generar_parametros_h.py` | parametros_rf.h | parámetros RF → C++ |
| `plano_nv1640_pro.py` | plano_nv1640_pro.png | plano profesional de la zona |
| `mapa_cobertura_pro.py` | mapa_cobertura_pro.png | heatmap RSSI + tasa PHY (con ±σ) |
| `contraste_tamograph.py` | contraste_tamograph.png | modelo vs TamoGraph (Figura 16) |
| `animacion_recorrido_lhd.py` | recorrido_lhd.gif | animación del recorrido del LHD |
| `resultados_v3.py` | resultados_*.png (4) | KPI multi-semilla, escenarios, handover, cobertura |
| `kpis_v3real.py` | kpi_v3_*.png (2) | panel KPI + ruta coloreada por RSSI |
| `link_budget.py` | link_budget.png | presupuesto de enlace formal |
| `comparacion_kpis.py` | comparacion_kpis.png | KPIs vs requisitos y referencias |
| `arquitectura_red.py` | arquitectura_red.png/.svg | diagrama de arquitectura (3 capas + QoS) |

**Nota de entorno:** los scripts Python corren en Windows (Python 3.13). La consola es
cp1252, así que evitar imprimir caracteres Unicode raros (usar `sys.stdout.reconfigure(
encoding="utf-8")` al inicio si hace falta; ya está en varios scripts).

---

## 9. DECISIONES DE INGENIERÍA IMPORTANTES (y por qué)

1. **Simulación DETERMINISTA (shadowing desactivado en NS-3).** Se intentó añadir
   shadowing log-normal dentro de NS-3 pero DESESTABILIZA el roaming 802.11 (ping-pong,
   escenarios colgados). Decisión (estándar en tesis): NS-3 determinista para los KPIs de
   red; la variabilidad ±σ se muestra en el mapa de cobertura y el contraste TamoGraph.
   El modelo de shadowing existe en la clase (`SetShadowingEnabled`) pero está en `false`.
   **NO reactivar sin control manual de asociación con histéresis fuerte.**

2. **Roaming estable (make-before-break).** `MaxMissedBeacons=10`, `ActiveProbing=false`
   → el STA mantiene su AP hasta perderlo de verdad, emulando el mesh Rajant. Evita el
   ping-pong del roaming ingenuo de NS-3.

3. **Recorrido acotado a la zona de producción.** La rampa (−176 m) es contexto (acceso
   manual), NO se teleopera → se excluye del recorrido simulado (si no, dispara el PLR).

4. **TamoGraph = contraste documental, NO validación experimental.** La tesis lo declara
   así. El reporte real es del NV1970 (mismo tipo de layout). NO sobre-afirmar validación.

5. **Vídeo H.264 VBR** (frames de tamaño variable) en vez de CBR, para tráfico realista.

6. **Jitter bajo (~0.28 ms) es REAL, no un bug** — enlace sin congestión = jitter mínimo,
   que es lo deseable para teleoperación. Se mide con bin fino (0.05 ms).

---

## 10. HISTORIAL DE COMMITS (orden cronológico, del inicio al final)

```
ab58528 Plano NV1640: layout El Teniente (drawbell compartido)
d779e5b Plano NV1640: aplica sección 4x4 m y radio R4.5 del plano AutoCAD
949f5e9 Editor de mapa interactivo + geometría real editada por el usuario
8ebbcfa Mapa NV1640 regularizado: costillas inclinadas + drawbell centrado + rampa superior
7ba2ac5 Mapa NV1640: rampa suavizada con fillet (redondeo local de esquinas)
5d236ff Plano NV1640: dibujo por capas sin solapamientos + leyenda fuera + lienzo grande
e70a666 Mapa NV1640: reubica el segundo botadero al medio (no en la esquina)
7d93127 Animación recorrido LHD (avance+reversa por galerías) + AP en editor
8896768 GIF recorrido LHD: usa el fondo correcto (plano bueno) + ruta por grafo
3732c95 Ajustes finales: separación recto-costilla, pique de traspaso, ruta accesible
8e416a9 Fix ruta LHD: drawpoints como nodos hoja (evita giros cerrados al bajar)
6e41c64 Fix ruta LHD: siempre encara drawpoints subiendo (nunca giro cerrado)
1fdc359 Ruta LHD: rodea para encarar drawpoints en giro abierto (todos alcanzables)
b0f81e5 Fix retroceso raro: acota punto de aproximación a los límites de la galería
bf93a4d Editor: sincroniza geometría inicial con el mapa final + herramienta enlace mesh
b7d2728 Añade AP (5 Hawk + 7 Cardinal) ubicados por el usuario + plano de cobertura
7a41c57 Parámetros RF reales de los datasheets (802.11ac Wave 2)
fd3038b Paso 1 NS-3: backup v9 + header C++ con geometría real autogenerado
2543002 Cobertura RF profesional + contraste de coherencia con TamoGraph
5a7e144 NS-3 v3 REAL: simulación con geometría real compila y CUMPLE todos los KPIs
ff499d8 Integra recorrido REAL del GIF en NS-3 (grafo + maniobras)
00a39b2 Sim v3: recorrido acotado a zona de producción + roaming estable => TODOS CUMPLEN
64e77b8 Gráficas de KPI v3-REAL: panel + ruta coloreada por RSSI
8db10c0 Batería de simulación enriquecida v3: 10 semillas + escenarios + análisis handover
f00b55a Simulación determinista robusta: shadowing documentado pero desactivado
e340136 FASE 2 — contenido técnico: link budget, comparación de KPIs y diagrama de arquitectura
7e9d0cd FASE 3 — ordenar y limpiar el repo de simulación
599b05e Mejoras: RTT + disponibilidad (RNF completos), frecuencia 5GHz, params RF sincronizados
6ad7852 Fix: el escenario de estrés LHD ahora sí aplica la velocidad (bug de BuildRoute)
9ed0051 Auditoría a fondo: vídeo VBR, MCS, jitter fino, escenario handover, sincronización
```

---

## 11. RESUMEN DEL AVANCE POR FASES

- **Fase inicial:** conexión a GitHub (privado), corrección de la geometría (de galería
  recta incorrecta a la geometría real block caving), editor de mapa HTML, animación GIF
  del recorrido del LHD con maniobras físicas reales (avance/reversa/rodeo a drawpoints).
- **Mapa y cobertura:** plano profesional, heatmap de cobertura RSSI+PHY (ruta de túnel
  + NLOS), contraste de coherencia con TamoGraph.
- **Simulación NS-3 v3-REAL:** reconstrucción limpia con geometría real + recorrido real,
  posiciones reales de 12 AP, parámetros de datasheets. Compila y cumple KPIs.
- **Enriquecimiento:** 10 semillas (media ± IC 95%), escenarios (baseline, estrés vídeo
  50 Mbps, estrés LHD 4 m/s, handover), análisis de handover.
- **Contenido técnico (Fase 2):** presupuesto de enlace, comparación de KPIs vs
  requisitos/referencias, diagrama de arquitectura de red.
- **Orden y limpieza (Fase 3):** todo lo v2/v8/v9 archivado en historico/; README creado.
- **Auditorías (2 rondas):** se encontraron y corrigieron bugs reales — el escenario de
  estrés LHD ignoraba la velocidad; faltaban RTT y disponibilidad; frecuencia inconsistente;
  vídeo CBR poco realista; jitter redondeado. Todo corregido. Simulación a nivel de excelencia.

---

## 12. QUÉ FALTA — PRÓXIMO PASO (FASE 4)

**Integrar todo al documento Word de la tesis.** Pendiente:
1. Ubicar el archivo .docx de la tesis (el usuario debe indicar dónde está;
   antes se trabajó con un Word llamado tipo "Avance_Lopez_Adrian_248_paginas").
2. Insertar las figuras nuevas en el Capítulo 3 (con pies de figura).
3. Redactar/actualizar la sección de metodología de simulación y la tabla de KPIs.
4. Actualizar el texto de la geometría real (vs la galería recta anterior).

### Comentarios del profesor pendientes (de una versión anterior de la tesis)
- Corregir "LUCE"→"LUCET" en portada; "802.11 ac"→"802.11ac"; "se a realizado"→"se ha realizado".
- Consolidar informe de similitud; resúmenes ejecutivos en la bitácora de simulación.
- Alineamiento con ODS en Cap. 3 (ya existe sección 3.5.3 — resuelto).
El profesor calificó la tesis como "alto nivel académico, muy bien encaminado".

---

## 13. CÓMO REPRODUCIR TODO DESDE CERO (resumen)

```bash
# 1. (si se editó la geometría) regenerar headers
cd cap3/simulacion_ns3/graficas_simulacion
python generar_geometria_h.py && python generar_recorrido_h.py && python generar_parametros_h.py

# 2. correr la batería completa (en WSL, EN SERIE, ~30-35 min)
cp ../lhd-teleop-v3-real.cc ../*.h ~/ns-allinone-3.40/ns-3.40/scratch/
cp ../run_escenarios_v3.sh ~/
cd ~ && nohup bash run_escenarios_v3.sh > ~/bateria_v3.log 2>&1 &
# monitorear: grep -c LISTO ~/bateria_v3.log   (14 = terminó)

# 3. copiar resultados al repo
cp ~/ns-allinone-3.40/ns-3.40/results/*_v3_* <repo>/cap3/simulacion_ns3/results/

# 4. generar todas las figuras
cd cap3/simulacion_ns3/graficas_simulacion
python resultados_v3.py && python kpis_v3real.py && python link_budget.py \
  && python comparacion_kpis.py && python arquitectura_red.py
```

---

## 14. MEMORIA PERSISTENTE (si se usa Claude Code con memoria)

El proyecto tiene memorias en
`C:\Users\Adrian Lopez\.claude\projects\C--Users-Adrian-Lopez-Documents-tesis-proyecto\memory\`.
Las más relevantes: `simulacion_v3real_resumen.md` (estado definitivo de la sim),
`geometria_real_nv1640.md`, `terminologia_drawpoint_breakpoint.md`, `datasheets_rf.md`,
`tesis_kpis_contexto.md`, `tamograph_hallazgos.md`. Si se traspasa a otra cuenta SIN esa
memoria, este documento (TRASPASO_CONTEXTO.md) contiene todo lo esencial de ellas.

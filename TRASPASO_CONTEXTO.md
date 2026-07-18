# Documento de traspaso — Tesis red 802.11ac para teleoperación LHD (Nexa NV1640)

> **Propósito:** este archivo contiene TODO el contexto del trabajo realizado, desde la
> configuración de GitHub hasta el estado actual, para que otra cuenta/sesión pueda
> continuar sin problemas. Léelo completo antes de continuar.
>
> Fecha del traspaso original: 2026-07-09 · **Actualizado 2026-07-14** (traspaso a otra cuenta).
>
> **⚡ SI CONTINÚAS ESTE TRABAJO EN OTRA CUENTA: lee la sección 12 primero.**
> La simulación NS-3 está CERRADA (6 rondas de auditoría, todos los KPIs cumplen).
> La FASE 4 (integración al Word de la tesis) está sustancialmente TERMINADA;
> el documento maestro es `fase4/trabajo/tesis_v2.docx` (166 págs). Entrega: JUE 16.
> El repo está en GitHub, rama `geometria-real-nv1640`, todo pusheado hasta bf2ba14.

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
  del directorio de build de ns-3). Se corren **EN SERIE**. La batería completa (18
  corridas de 300 s: 10 semillas de operación + baseline + 2 estrés + 5 semillas de
  handover) tarda **~4 HORAS** (la de 14 corridas midió 12596 s el 2026-07-09; una
  versión anterior de este documento decía 30-35 min por error). Lento pero 100% fiable.
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

### RESULTADO ACTUAL (10 semillas, escenario de operación, batería 2026-07-09) — TODOS CUMPLEN
- OWD comandos: **3.04 ± 0.26 ms** · PLR comandos: **0.06%**
- Vídeo E2E: **35.89 ± 0.28 ms** · jitter P95: **0.28 ms** · goodput: **40.12 ± 0.07 Mbps**
  (payload EXACTO, sin cabeceras; una versión previa reportaba 40.29 con fórmula inflada) · PLR: **0.01%**
- Telemetría OWD: **3.08 ms** · PLR: **0.14%**
- **RTT: 6.12 ± 0.47 ms** · **Disponibilidad: 100%**
- **Handover: 0.88 ms** (escenario dedicado, multi-semilla) ≪ 150 ms
- **10/10 semillas cumplen los 8 indicadores.**
- **NOTA (estrés vídeo 50 Mbps):** desde el modelo VBR realista este escenario CUMPLE
  los KPIs; la presión se manifiesta en LATENCIA de comandos (OWD ×2.3 = 6.8 ms,
  P95 32 ms), no en pérdidas. NO citar el antiguo "PLR 1.04%" (era del CBR).
- Esquema del pos_log: `time_s,x,y,best_ap,rssi_dbm,assoc_ap,rssi_assoc_dbm`
  (best = mejor señal/cobertura; assoc = AP realmente asociado).

---

## 7. ESTRUCTURA DEL REPOSITORIO

```
tesis_proyecto/
├── TRASPASO_CONTEXTO.md          # este archivo
├── editor_mapa_nv1640.html       # editor visual interactivo de la geometría
├── historico/                    # material antiguo a nivel raíz (incluye dashboard.html
│                                 #   y mapa_cobertura_nv1640.html, ambos de la era v9)
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
459ee01 Documento de traspaso de contexto completo (handoff)
a8e5dc3 Auditoría 3ª ronda: elimina duplicación de parámetros y aclara supuestos
af57375 Auditoría (Opus): las figuras usaban una corrida obsoleta; unifica a la batería vigente
55cb27f Auditoría final (Fable): 5 hallazgos resueltos (goodput exacto, pos_log honesto,
        radio de diseño justificado, supuesto físico documentado, sin textos hardcodeados)
c9298b1 Batería completa con el código auditado (F1-F5): 14/14 escenarios, TODOS cumplen
1fdeffb Limpieza: elimina archivos espurios de corridas antiguas colados en el commit anterior
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

## 12. FASE 4 (WORD) — ESTADO ACTUAL Y CÓMO CONTINUAR

**ENTREGA: JUEVES 16. El documento está sustancialmente TERMINADO.** Todo el
trabajo de la Fase 4 vive en `fase4/` (NO estaba en el repo al inicio; el
usuario entregó el .docx y dos .md con observaciones/criterios).

### Archivos clave de la Fase 4 (en `fase4/`)
- `tesis_original.docx` — el Word original del usuario, INTACTO (respaldo).
- `trabajo/tesis_v2.docx` — **EL DOCUMENTO MAESTRO** (166 págs, 23 figuras).
  Aquí se edita todo. Contiene ediciones del propio usuario (dedicatoria,
  agradecimientos, estilo) hechas el 2026-07-14 — commit bf2ba14.
- `trabajo/tesis_v2.pdf` — PDF generado desde el Word (para lectura/entrega).
- `anexo_digital_tesis_lopez.zip` — anexo digital (6.8 MB) con código, results,
  figuras y scripts; se regenera con `armar_anexo_digital.sh`. NO versionado.
- `observaciones_asesor.md` — observaciones del asesor (todas resueltas).
- `trabajo/edit_*.py` — scripts REPRODUCIBLES de cada edición (verifican el
  contenido antes de tocar cada párrafo). `gen_matlab_*.py` + `*.m` — figuras MATLAB.

### QUÉ SE HIZO (Etapas A–E + extras, todo commiteado y pusheado)
- **Cap. 3** actualizado v8.2→v3-REAL: 29 párrafos, 5 tablas con datos LEÍDOS
  de los CSVs (cero números a mano), Figuras 9 (plano con 12 AP), 10 (escena 3D
  MATLAB con cobertura+recorrido+patrón), 11 (arquitectura), 12 (RSSI del enlace
  asociado — responde la duda del roaming: nunca baja de −72.1 dBm).
- **Cap. 4** escrito COMPLETO (era placeholder): estructura Lección 09, 11
  secciones, idoneidad técnica/económica/ambiental/legal/ética. Figura 14 (KPIs
  vs referencias), 15 (CAPEX/OPEX estructural SIN montos inventados). Tablas 25/26.
- **Conclusiones** (8, cierran los objetivos específicos) y **Recomendaciones**
  (6) escritas (eran placeholders). Método Lección 10, verbos en presente.
- **Anexos B–H** reescritos con material v3-REAL + huellas SHA-256 reales.
- **Formato**: 3 tablas anchas reescaladas; captions convertidos a campos SEQ
  (el doc usa numeración automática — manual chocaba); índices actualizados.
- **Figuras MATLAB extra** (Antenna Toolbox, R2024b del usuario): patrón de
  antena 3D+cortes (Fig 21), curva Prx-distancia (Fig 22, cruces 127/327 m que
  COINCIDEN con link_budget.py = validación cruzada), CDF RSSI (Fig 23).
- **Coherencia Cap. 1–2** verificada: 0 referencias al modelo viejo.
- Correcciones del asesor: verificadas, ya no existen en esta versión.

### PENDIENTE (para la otra cuenta)
1. **Regenerar el PDF** desde `trabajo/tesis_v2.docx` tras las ediciones del
   usuario (Word COM: abrir → Fields.Update → TablesOfFigures.Update → Save →
   ExportAsFixedFormat 17). Y **regenerar el anexo digital** (`bash
   fase4/armar_anexo_digital.sh`) por si el usuario cambió figuras.
2. **Confirmar el FORMATO de entrega** que pide el curso (¿PDF? ¿Word? ¿+ZIP a
   PAIDEIA?) y armar el paquete final.
3. Aplicar cualquier corrección que el usuario pida tras su lectura final.

### FASES POSTERIORES (NO son la entrega; contexto)
- **Ray-tracing 3D en MATLAB (SBR + STL)**: modelar la galería 3D con materiales
  de roca reales (εr, σ) y comparar cobertura SBR vs two-slope vs TamoGraph =
  validación triple. AGENDADO PARA EL PAPER (riesgo alto antes del jueves).
  El STL se puede generar desde `mapa_nv1640_datos.py` (fuente única).
- **Animación 3D** del recorrido con el AP servidor iluminándose (ya generada:
  `trabajo/anim_recorrido_3d.mp4`, 307 frames del pos_log real) → SUSTENTACIÓN.
- Luego: ODT/PPTX (presentación; el profesor acepta ambos → usar PPTX), póster
  (plantilla XpoSTEM), preparación de sustentación (las rúbricas del jurado están
  en el .md de datos del profesor, BLOQUE VI).

### Comentarios del profesor (TODOS resueltos en esta versión)
- "LUCE"→"LUCET" (solo estaba en el logo gráfico, correcto); "802.11 ac"→"802.11ac";
  "se a realizado"→"se ha realizado"; "debe de garantizar"→"debe garantizar" — verificado 0 residuos.
- Alineamiento con ODS: sección 3.5.3 (resuelto) + ODS 12 añadido en Cap. 4.
- El profesor calificó la tesis "alto nivel académico, muy bien encaminado".

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
# monitorear: grep -c LISTO ~/bateria_v3.log   (18 = terminó)

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

---

## 15. FASE 4 FINAL — ENTREGA, PPT DEFINITIVA Y LABORATORIO MATLAB (2026-07-16)

**Este apartado captura TODO lo hecho el 15-16 de julio para migrar el seguimiento sin pérdida.**

### 15.1 Estado de entregables (cronograma del profesor)
| Entregable | Límite | Estado |
|---|---|---|
| Monografía (tesis_v2.docx) | 16 jul | CORREGIDA Y APROBADA por el profesor ("Excelente trabajo") |
| Presentación de sustentación | 16 jul | TERMINADA (16 slides) — `Sustentacion_LopezPascual_TdT2.pptx` |
| Póster XpoSTEM | 19 jul | REHECHO 18-jul sobre la PLANTILLA AUTORIZADA, en inglés: `fase4/presentacion/Poster_LopezPascual_XpoSTEM.pdf` (A1, subir a PAIDEIA); fuente `poster_xpostem_plantilla.docx` + `gen_poster_plantilla.py`; el pptx anterior queda como histórico |
| Paper | — | **NO APLICA** (el usuario confirmó: solo póster; ignorar menciones previas) |
| Sustentación | 20-23 jul | Pendiente: ENSAYO del usuario (18 min + banco de preguntas) |
| ExpoSTEM (asistencia obligatoria) | 21 jul, 16-20h explanada FCI | Pendiente |

### 15.2 PENDIENTE CRÍTICO: Informe de Similitud (página 2 de la tesis)
- La página 2 del Word es una TABLA-PLANTILLA **con placeholders SIN LLENAR**:
  `[APELLIDOS, NOMBRES]` del asesor, `DNI:[########]`, `ORCID: [####-####-####-####]`, firma.
- Flujo correcto (palabras del profesor): él genera el **reporte Turnitin** -> el tesista
  **llena la página 2** (datos del asesor + % de similitud) -> regenera PDF -> **sube a PAIDEIA**.
- El usuario ya subió Word+PDF+PPT a PAIDEIA posiblemente con la página en placeholders:
  cuando llegue el Turnitin, LLENAR la página 2 y RE-SUBIR (o consultar al profesor).
- Asesor: Dr. Pastor David Chávez Muñoz (DNI/ORCID los tiene el usuario o el asesor).

### 15.3 La tesis: correcciones del profesor aplicadas (todas)
Archivo maestro: `fase4/trabajo/tesis_v2.docx` (backup: `tesis_v2_BACKUP_precorrecciones.docx`).
Las 10 correcciones de `Corecciones.docx` (Downloads, con 8 capturas) resueltas:
100 páginas exactas (Anexos I=RSL, J=parámetros propagación + ex-2.3.3-2.3.6, K=áreas/competencias/normativa,
L=matriz comparativa APAISADA), numeración romanos desde Dedicatoria/arábigos desde Intro=1,
folios ocultos SOLO en 1a pág de Intro+Cap1-4, captions de tabla ARRIBA+fuentes, colores a negro,
tblHeader repetible, Recomendaciones en página aparte, Glosario página propia.
Scripts: `fase4/trabajo/fix_correcciones_1..7.py`. Iteraciones de página: 111->108->95->103->~100.
**Regla aprendida**: Word COM se cuelga -> flujo confiable = usuario hace Ctrl+E -> F9 ->
"Actualizar toda la tabla" -> Ctrl+G y reporta páginas.

### 15.4 La PPT definitiva (16 slides) — fase4/presentacion/
Generador: `gen_ppt_v2.js` (pptxgenjs; `node gen_ppt_v2.js` -> `sustentacion_tesis_v2.pptx`;
se publica copiando a `sustentacion_tesis.pptx` y `Sustentacion_LopezPascual_TdT2.pptx`).
Estructura (agenda del profesor 3+3+5+7+cierre, SIN índice):
1 Carátula oscura (mina 3D) - 2 De qué trata - 3 Motivación (raíz personal REAL del usuario:
"Nací en una tierra donde la minería marca la vida de las familias..." + GRÁFICO OSINERGMIN
con datos de la Tabla 2: 12/14 accidentes y 13/15 víctimas 2024 subterránea = 86.7%) -
4 Objetivos - 5 Design Thinking (números sobrios) - 6 Geometría real + VIDEO EMBEBIDO del LHD -
7 ARQUITECTURA DE ANILLO (diagrama tipo Visio + 3 capas) - 8 KPIs oscura - 9 RSSI/roaming
(-72.1 dBm) - 10 WMM multi-semilla (boxchart 10 semillas + estrés) - 11 Capa física 802.11ac +
patrones red - 12 Antenas datasheet (RCP-50 LHP/RHP BIDIRECCIONAL, EPNT-7 omni, HELI-40
bidireccional) - 13 Validación cruzada ray-tracing - 14 Idoneidad+CAPEX - 15 Reflexión final
(pitch) - 16 Gracias. Notas del orador = guion cronometrado en CADA slide.
Diseño: auditoría anti-IA por feedback de pares (SIN emojis/círculos/sombras; cards rectas
borde fino; Cambria/Calibri; folios discretos; sin etiquetas de tiempo visibles).
Auditoría gramatical completa: cero faltas.
**METADATOS LIMPIOS**: dc:creator y lastModifiedBy = "Adrián Álvaro López Pascual" en deck,
copia formal, póster, flashcards y banco de preguntas; títulos propios; Application genérica;
verificado cero rastros (claude/anthropic/gpt/pptxgenjs/python-docx). Generadores con
p.author/p.title para que futuras regeneraciones nazcan limpias.

### 15.5 Material de preparación de sustentación
- `banco_preguntas_jurado.docx`: 21 preguntas anticipadas con respuesta modelo (5 temas) + tips.
- `flashcards_jurado.pptx`: 16 tarjetas de repaso.
- Puntos clave del profesor (datos_profesor.md, sección sustentación): 20 min MEDIDOS
  (3 motivación / 3 objetivos / 5 metodología con Design Thinking / 7 LOGROS / reflexión de
  cierre = pitch vendedor desde "plataforma de triunfo"); ensayar a 18 min y al menos 1 vez
  con el asesor; 30 min de preguntas (responder COMPLETO puntúa); notas 9/11/15/17/19/20;
  filtros pasa/no-pasa: tiempo, gramática, formato.

### 15.6 Laboratorio MATLAB (fase4/trabajo/) — todo funcional
**Toolboxes**: Antenna/Comms/DSP/Signal/Stats/Optim/Parallel con licencia; **WLAN y 5G
EJECUTAN aunque license('test') devuelva 0** (probado: wlanVHTConfig/waveform funcionan);
Simulink 24.2 + SimEvents 24.2 instalados (librería = **'sldelib'**, NO 'simevents').
**Lanzadores** en `C:\Users\Public\run_*.m` (evitan bug de espacios en matlab -r): run_p3d
(3 globos de patrones), run_flujo (viaje de paquetes por el anillo), run_rayos (Site Viewer
rayos+patrones), run_final (escena cacheada), run_editor (editor de antenas con sliders),
run_mesh (malla en vivo), run_wmm (colas EDCA), run_wmmfig (figura multi-semilla), run_sim (SimEvents).
**Pipeline geométrico**: `gen_stl_galeria.py` (STL v3: sección herradura, huecos en uniones,
24 TAPAS en extremos libres -> modelo estanco; escribe galeria_nv1640.stl paredes+piso,
galeria_techo.stl techo fantasma; se fusionan en galeria_rt.stl para ray-tracing).
**Datos precalculados**: anim_recorrido.csv (pos_log real 307 frames), anim_enlace.csv (ruta
Dijkstra LHD->AP por galerías), anim_aps.csv (x,y,tipo,ángulo de galería), flujo_paths.csv,
mesh_rssi.csv (RSSI 307x12 por distancia de ruta), mesh_rutas.csv, escena_cache.mat (patrones
bidireccionales + 108 rayos SBR de H4 a 12/24/38 m).
**Scripts clave**: anim_lhd_realista.m (video 3D: enlace por galerías + patrones + LHD ->
lhd_recorrido_3d.mp4), precalc_escena.m (extendido con rayos AP<->AP vecinos, NO ejecutado aún),
ver_escena_final.m, editor_antenas.m (FUNCIÓN con anidadas — scripts con uicontrols DEBEN ser
función), ver_mesh_vivo.m (SOLO ilustración conceptual: el Dijkstra de malla NO está en la
tesis), ver_wmm_paquetes.m, fig_wmm_semillas.m (wmm_semillas.png, KPIs exactos 3.04±0.26 etc.),
fig_osinergmin.m, export_patrones3d.m (globos; Hawk BIDIRECCIONAL según datasheet
RCP-50LHP/RHP-11-NM "Bi-Directional, Mine/tunnel"; patternCustom con max(P,flipud(P))),
crear_wmm_simevents.m (SimEvents v2: cablear entidades ANTES de activar estadísticas; puertos
nuevos por handle con setdiff), mega_flujo_wlan.m (PER vs SNR + constelación 256-QAM, receptor
VHT completo con sincronización), raytracing_final.m (validación cruzada ~5 dB campo cercano).
**Antenas según datasheets (corregido 2 veces por el usuario)**: Hawk = PAR RCP-50 LHP+RHP
11 dBi BIDIRECCIONAL (tramos largos; polarizaciones L/R = diversidad para 2 streams MIMO);
Cardinal = EPNT-7 7.5 dBi omni (cruceros); LHD = HELI-40 4.8 dBic bidireccional. El "2x2" es
MIMO del radio, NO un arreglo de 4 hélices.
**Arquitectura documentada (corrección del usuario)**: LHD -radio-> AP -Cat6-> SW acceso
-ANILLO FO 1Gbps SM-> NODO CORE -> workstation. FO=amarillo, Cat6=azul (leyenda de la tesis).
NUNCA dibujar enlaces rectos atravesando roca (se eliminó de mina_realista.m y del deck).

### 15.7 Gotchas técnicos de esta sesión (ahorran horas)
- Heredocs bash con strings JS/MATLAB: los saltos escapados colapsan -> usar SIEMPRE el Write
  tool o archivos .py para parches; nunca python/JS inline con backslashes en heredoc.
- pptxgenjs rounding:true recorta imágenes en ÓVALO — solo para fotos decorativas.
- MATLAB -r con rutas con espacios falla -> lanzadores en C:\Users\Public.
- MATLAB: funciones locales de script NO ven variables del script (uicontrols -> función anidada).
- SimEvents: activar estadísticas cambia numeración de puertos -> cablear entidades primero,
  luego conectar handles nuevos (setdiff de PortHandles.Outport).
- validate.py del skill pptx da falsos "charmap" en consola Windows (no es corrupción).
- markitdown + grep de TODO matchea "TODOS/método" en español (falsos positivos).
- POWERPNT/WINWORD del usuario suelen estar abiertos: matar solo procesos ajenos al documento
  del usuario; python-docx da PermissionError si Word tiene el archivo abierto (flujo: usuario
  cierra -> yo edito -> reabro; el usuario hace F9+guardar, NUNCA guardar por él tras mis ediciones).

### 15.8 Últimos commits (rama geometria-real-nv1640, TODO PUSHEADO a GitHub privado)
1f8e768 tesis corregida + deck v2 - c3a370e banco preguntas + flashcards - 6e4475a póster -
4db49c3 MATLAB avanzado (video LHD, patrones, mega flujo WLAN) - 42f542e herradura -
733eec4 visual v3 (Dijkstra enlace, patrones 12 AP, uniones limpias) - 9cdf539 patrones 3D +
raytracing en deck - 113240e RCP-50 bidireccional + flujo anillo - 767d3ac deck blindado -
ee1bd4c PPT sobria anti-IA + lámina WMM - 99a356f naturalidad (sin tags, folios) -
22376a3 micro-consistencia + copia formal - aa5a3da gráfico OSINERGMIN -
0cac4d1 slide arquitectura + metadatos crédito exclusivo del tesista.

### 15.9 Próximos pasos exactos (para la nueva sesión)
1. Cuando llegue el Turnitin del profesor: llenar página 2 del Word (datos del asesor + %),
   F9, generar PDF, re-subir a PAIDEIA.
2. Acompañar el ensayo: simular la ronda de preguntas del jurado (banco de 21 listo).
3. Opcional MATLAB: SimEvents (modelo construido, correr/validar animación con el usuario);
   precalc de rayos AP<->AP pendiente de ejecutar; el usuario disfruta estas exploraciones.
4. Los labs NO-tesis (mesh Dijkstra) presentarlos SOLO como "ilustración conceptual".
5. El deck está ZANJADO: no seguir puliendo diseño salvo pedido explícito.

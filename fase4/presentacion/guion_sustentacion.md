# GUION DE SUSTENTACIÓN Y DEFENSA — Adrián López · Trabajo de Tesis 2

> Uso: estudiar por bloques, NO memorizar palabra por palabra. Cada respuesta: 30–60 s.
> Estructura de toda respuesta: **reconocer la pregunta → idea clave → número que la respalda → cierre.**

---

## 0. LOS NÚMEROS SAGRADOS (en la punta de la lengua)

| Qué | Valor | Límite |
|---|---|---|
| Latencia comandos (OWD) | **3.04 ± 0.26 ms** | ≤ 20 ms |
| Latencia vídeo E2E | **35.9 ± 0.3 ms** | ≤ 150 ms |
| RTT lazo de control | **6.12 ms** | ≤ 40 ms (P99 ≤ 60) |
| Jitter vídeo P95 | **0.28 ms** | ≤ 10 ms |
| Goodput vídeo | **40 Mbps** | ≥ 38 Mbps |
| PLR vídeo / comandos | **0.01 % / 0.06 %** | ≤ 1 % / ≤ 0.5 % |
| Disponibilidad | **100 %** | ≥ 99.9 % |
| Handover | **0.88 ms** | ≤ 150 ms |
| RSSI mínimo del enlace | **−72.1 dBm** (margen 9.9 dB) | −82 dBm usable |
| Rigor | 18 corridas × 300 s · 10 semillas · IC 95 % | — |
| Estrés | vídeo 50 Mbps y LHD 4 m/s: **todo sigue cumpliendo** (OWD sube 3→6.8 ms) | — |
| Modelo | two-slope n₁=1.9, n₂=3.4, d_bp=40 m · calibrado TamoGraph | — |
| Validación cruzada | ray-tracing SBR y link budget coinciden (cruces 127/327 m) | — |
| Motivación | OSINERGMIN 2024: **12/14 accidentes y 13/15 víctimas** en subterránea | — |

---

## 1. GUION SLIDE POR SLIDE (20 min → ensayar a 18)

| # | Slide | Tiempo | Qué decir (esencia) |
|---|---|---|---|
| 1 | Carátula | 0:20 | Saludo al jurado con calma. Nombre completo, título de la tesis, asesor. |
| 2 | De qué trata | 0:40 | Una frase: "Esta tesis diseña y valida por simulación la red que permite operar un cargador LHD desde superficie, sacando al trabajador de la zona de riesgo". |
| 3 | Motivación | 3:00 | Historia personal (45 s, genuina) → gráfico OSINERGMIN: en 2024, 12 de 14 accidentes fatales y 13 de 15 víctimas fueron en subterránea. "Detrás de cada número hay una familia". |
| 4 | Objetivos | 3:00 | Objetivo general con énfasis en "**evidencia verificable**". Los 6 específicos en 3 bloques: canal+arquitectura / radio+QoS / validación+idoneidad. |
| 5 | Metodología | 5:00 | Decir "**Design Thinking**" explícitamente (rúbrica). 5 pasos a 30–40 s: empatizar (riesgo del operador) → definir (KPIs) → idear (comparativa tecnologías) → prototipar (ns-3 geometría real) → testear (vs site survey). |
| 6 | Geometría + VIDEO | ~1:15 | Plano real 15 s → clic al **video 3D del LHD** y narrar encima: galerías reales, 12 AP, recorrido de acarreo. |
| 7 | Arquitectura anillo | 0:45 | "Solo el último tramo es inalámbrico": LHD →radio→ AP →Cat6→ switch acceso →anillo FO 1 GbE→ core → estación. Redundancia de anillo + VRRP/HSRP en el core L3. |
| 8 | **KPIs (LA slide)** | 1:30 | Leer los 3 primeros con requisito: "3 milisegundos contra 20 permitidos… 36 contra 150… disponibilidad 100 %". Pausa. "Todos, en las 10 semillas". |
| 9 | RSSI/roaming | 0:45 | Anticipa la clásica: "¿y si pierde señal en la curva?" → la línea azul **nunca baja de −72.1 dBm**; roaming estable make-before-break, handover 0.88 ms. |
| 10 | WMM multi-semilla | 1:00 | Panel (a): dispersión de latencia en 10 semillas (cajas pegadas al piso). Panel estrés: a 50 Mbps los comandos suben a 6.8 ms y siguen 3× bajo el límite. |
| 11 | Capa física | 1:00 | Diferenciador: no solo red — constelación 256-QAM, PER vs SNR, receptor VHT completo en MATLAB. |
| 12 | Antenas datasheet | 0:40 | Hawk = **par RCP-50 LHP+RHP** (bidireccional de túnel, polarizaciones L/R = diversidad para 2 streams MIMO); Cardinal = EPNT-7 omni; LHD = **HELI-40** (4.8 dBic). |
| 13 | Ray-tracing | 0:45 | "La slide que blinda el modelo": SBR 3D sobre la galería en STL → coincide con two-slope y con el link budget (cruces 127/327 m). Tres métodos independientes convergen. |
| 14 | Idoneidad + CAPEX | 1:00 | 4 dimensiones. En económica, honesto: "estructura de costos y mecanismos de retorno; la cuantificación exacta requiere cotizaciones vigentes". |
| 15 | Reflexión final | 1:00 | Pitch desde la plataforma de triunfo: "la tecnología para no volver a poner a una persona frente al mineral ya existe; esta tesis demuestra con evidencia que funciona". |
| 16 | Gracias | 0:15 | Agradecer al jurado y al asesor. Respirar. |

**Total ≈ 19:40 → meta de ensayo 18:00.** Si vas tarde en la slide 10, recorta la 11 (30 s) y la 14 (40 s), nunca la 8 ni la 3.

---

## 2. LAS 2 PREGUNTAS PARA EL ASESOR (Dr. Chávez) — terreno físico, donde él asiente

El criterio: son preguntas en SU territorio (física del medio), con respuestas multicapa que
le permiten cerrar el punto ante Paco y Córdova. NO son las que el resto haría solo.

### PREGUNTA A (validación del modelo — física + rigor)
> **"Su modelo de propagación es semi-empírico. ¿Qué evidencia independiente tiene de que
> no está sobreestimando la cobertura real de la galería, y por qué un modelo de dos
> pendientes representa correctamente la física del túnel?"**

**Respuesta modelo (≈75 s):**
"El túnel se comporta como una guía de onda imperfecta: cerca del transmisor coexisten
múltiples modos que refuerzan la señal — por eso el exponente n₁=1.9, cercano al espacio
libre —; pasado el punto de quiebre a 40 m los modos superiores se atenúan por la rugosidad
de la roca y queda el modo dominante, con n₂=3.4. No usé valores de literatura urbana: los
coeficientes se calibraron contra el site survey TamoGraph real de la mina. Y la evidencia
independiente es triple: (1) el contraste con TamoGraph, (2) un ray-tracing SBR en MATLAB
sobre el modelo 3D de la galería con materiales de roca, y (3) el presupuesto de enlace
analítico — los tres convergen: los cruces de cobertura a 127 y 327 metros coinciden entre
métodos que no comparten supuestos. Además el modelo es deliberadamente conservador; el
equipo mesh real solo puede mejorar estos números. Es validación de diseño: la medición de
campo es el paso natural siguiente y así lo declaro."

### PREGUNTA B (polarización circular — electromagnetismo puro, su ADN)
> **"A 5 GHz, en una sección de 5 × 4.5 metros con paredes rugosas, ¿por qué eligió antenas
> de polarización circular y qué pasaría si hubiera usado polarización lineal?"**

**Respuesta modelo (≈70 s):**
"A 5 GHz estamos muy por encima de la frecuencia de corte del modo fundamental de esa
sección, así que la galería propaga múltiples modos con rebotes sucesivos en paredes, piso y
techo. Con polarización lineal, cada rebote rota el plano de polarización y las réplicas
llegan desalineadas: interferencia destructiva y desvanecimientos profundos. Con polarización
circular, el rebote invierte el sentido de giro — la antena discrimina la réplica reflejada y
mantiene el acoplamiento con la componente directa: el fading se suaviza y el SNR queda
estable. Por eso el diseño usa la familia helicoidal de Poynting: el Hawk lleva el par
RCP-50 con polarización izquierda y derecha — que además aporta diversidad de polarización
para los dos flujos espaciales MIMO — y el LHD lleva la HELI-40 bidireccional de 4.8 dBic,
que es la que entra al presupuesto de enlace. El resultado medible: el RSSI del enlace nunca
cayó de −72.1 dBm en todo el recorrido."

---

## 3. EL PUNTO DÉBIL: VIABILIDAD SIN VAN/TIR — DEFENSA EN 3 CAPAS

Te van a preguntar (Paco casi seguro). NO te disculpes; defiende la decisión metodológica.

**Capa 1 — La decisión (por qué NO hay VAN/TIR):**
"Un VAN o TIR exige flujos de caja: precios de mercado vigentes y datos financieros internos
de la mina — tarifas, costos de parada, estructura tributaria — que son confidenciales y a
los que un trabajo de gabinete no accede. Calcular un VAN con supuestos inventados sería
pseudo-precisión: un número con apariencia de rigor y sin sustento. Preferí la honestidad
metodológica: entregar la estructura completa y dejar la cuantificación a la fase de
implementación, que es donde corresponde."

**Capa 2 — Lo que SÍ entrega el Capítulo 4:**
- Estructura CAPEX/OPEX completa por categorías (equipos, instalación, operación, mantenimiento).
- La métrica de decisión **"costo por metro de galería cubierta"** — pensada para el avance
  dinámico del frente: los nodos mesh se reubican y el 100 % del activo se reutiliza.
- Los mecanismos de retorno identificados: horas-hombre fuera de exposición, continuidad
  operativa (la teleoperación permite operar tras voladura sin esperar ventilación completa),
  reducción de primas y de costos por accidente.
- La inversión es **incremental**: aprovecha el backbone de fibra y la infraestructura
  eléctrica que la mina moderna ya tiene.

**Capa 3 — El cierre que voltea el argumento:**
"Y hay un argumento económico que no necesita cotización: el costo de UN solo accidente fatal
— multa de OSINERGMIN, paralización de la operación, procesos legales — supera típicamente el
CAPEX completo de esta red. Con el cronograma de cotizaciones, la plantilla del Capítulo 4
permite calcular el VAN/TIR directamente; es trabajo inmediato de la siguiente fase, no un
vacío conceptual."

---

## 4. MATRIZ DE JURADOS — ataques y contragolpes VERIFICADOS contra la tesis

### ⚠️ TRES CORRECCIONES CRÍTICAS (los contragolpes que te pasaron citan cosas que tu tesis NO dice así)

1. **"Watchdog en la Tabla 7" — NO existe en la tesis.** La palabra watchdog no aparece.
   Lo que SÍ está: "modos degradados" y "protocolos de parada segura" en los aspectos éticos
   y recomendaciones. → Di: *"el diseño contempla modos degradados y parada segura del
   vehículo ante pérdida de enlace, recogidos en los aspectos éticos y operativos de la
   tesis; el mecanismo concreto — un temporizador de vigilancia en el lazo de control — es
   parte de la ingeniería de detalle de la implementación"*. NUNCA cites "Tabla 7 watchdog".

2. **"Expedited Forwarding / Strict Priority" — NO están escritos en la tesis.** Lo que SÍ
   está: el mapeo WMM → colas/DSCP como objetivo y política de QoS. → Di: *"la tesis define
   el mapeo de clases WMM a DSCP en las políticas de QoS; en la configuración de los switches,
   los comandos se llevarían a la clase de máxima prioridad — el equivalente a EF — y eso es
   configuración de implementación, no de diseño"*.

3. **HELI-22 vs HELI-40 — la tesis menciona AMBAS.** El glosario y la descripción de la
   solución citan la HELI-22 (familia helicoidal 2.4/5 GHz); el presupuesto de enlace, la
   simulación y las conclusiones usan la **HELI-40 (4.8 dBic)** como antena embarcada del
   LHD. Si te lo sacan: *"el diseño emplea la familia helicoidal de polarización circular de
   Poynting; el modelo dimensionado para el vehículo es la HELI-40 de 4.8 dBic, que es la que
   entra al presupuesto de enlace y a la simulación"*. No te dejes arrastrar a un debate de
   nomenclatura.

### DR. CHÁVEZ (asesor · física del medio · alergia a la caja negra)
- **Su lente:** el túnel es una guía de onda imperfecta. Exigirá la matemática detrás del simulador.
- **Caja negra ns-3:** explica QUÉ calcula: propagación con TU clase two-slope (no un bloque
  de fábrica — la escribiste tú, ecuación por ecuación), contención CSMA/CA con colas EDCA
  por clase de acceso (802.11e), y FlowMonitor midiendo retardo por paquete. "El modelo de
  pérdidas no es de catálogo: es código propio calibrado con el survey".
- **Worst-case:** estrés 50 Mbps + 4 m/s + escenario dedicado de handover + P95/P99. Y la
  honestidad: falla catastrófica de APs no se modeló — limitación declarada, diseño mitiga
  por densidad (12 AP, celdas solapadas).
- **Semillas:** cada semilla re-inicializa la aleatoriedad de la contención del medio a nivel
  de microsegundos → 10 realizaciones independientes → media e IC 95 %. (OJO: NO digas que
  las semillas varían el shadowing — tu simulación de red es determinista en propagación;
  la variabilidad entre semillas viene de la contención y los tiempos de tráfico.)

### ING. PACO (capas 2/3 · Cisco · costos · alta disponibilidad)
- **L1 Backbone/redundancia:** anillo FO monomodo + switches core L3 con **VRRP/HSRP**
  (SÍ está en la tesis, descripción de la solución). Falla de un tramo → el anillo conmuta;
  falla del gateway → VRRP promueve el respaldo. El presupuesto de 50 ms no se compromete.
- **L2 QoS extremo a extremo:** mapeo WMM→DSCP (con la corrección #2 de arriba).
- **L3 BoM/grado IP:** Rajant Hawk IP67 (polvo/agua), Cardinal embarcado diseñado para
  vibración de maquinaria pesada. "No es equipo de oficina adaptado: es hardware de misión
  crítica minera" (Hawk/Cardinal son equipos de minería documentados con datasheet).
- **L4 Frente que avanza:** ventaja estructural del mesh: reubicar un Hawk no requiere
  recablear ni reconfigurar el core — InstaMesh se auto-organiza. Métrica del Cap. 4:
  **costo por metro de galería cubierta** (SÍ está en la tesis) + 100 % de reutilización de activos.
- **VAN/TIR:** → Sección 3 de este documento, defensa en 3 capas.

### ING. CÓRDOVA (humano · QoE · energía · resiliencia de borde)
- **L1 QoE/MOS sin operador real:** mapeo objetivo por ITU-T **G.1010** (SÍ está en la tesis):
  con jitter P95 < 10 ms y PLR < 1 %, la literatura valida que H.264 1080p30 reconstruye sin
  artefactos → MOS ≥ 4 se garantiza de forma indirecta y científica. Tus números: 0.28 ms y
  0.01 % — órdenes de magnitud mejores que la frontera.
- **L2 Energía a bordo:** modelo de consumo referencial estilo **Heinzelman (Anexo J.3** — SÍ
  está): el consumo del radio embarcado es marginal frente al sistema eléctrico de un LHD
  (decenas de kW); PoE industrial; ante caída de tensión → modo degradado/parada segura
  (con la corrección #1: sin citar "watchdog en Tabla 7").
- **L3 Pérdida total de enlace:** la seguridad manda sobre la disponibilidad: el operador está
  en superficie, así que el peor caso técnico NO pone vidas en riesgo — el vehículo pasa a
  parada segura y se pierde producción, no personas. Esa asimetría ES el argumento central
  de la tesis.
- **L4 Impacto sociolaboral:** no reemplaza al minero: lo **reubica** (jerarquía de controles
  SSO) — de operador expuesto a operador de centro de control, con reconversión de perfil.
  Sección 1.5.2 de la tesis. Cierra con la Tabla 1/OSINERGMIN.

---

## 5. REGLAS DE ORO

1. **Responder COMPLETO puntúa** (criterio explícito del profesor): reconocer → idea → número → cierre.
2. Nunca sobre-afirmar: "validación de diseño", "alcance declarado", "limitación declarada" — el jurado premia esa madurez.
3. Nunca a la defensiva. Las preguntas críticas (P18: "solo simulación") se responden con seguridad: es el alcance, y dentro de ese alcance la evidencia es sólida y reproducible.
4. Si no sabes algo: "No lo desarrollé en esta tesis; lo abordaría así…" — jamás inventar.
5. No dejar mal parado al asesor: si dudas en la matemática base, él no puede salir a defenderte.
6. P20 ("¿qué cambiaría?"): mediciones de campo propias. NUNCA "nada".
7. Traje formal, 18 minutos ensayados, los 3 números sagrados sin mirar: **3 ms · 36 ms · 100 %**.

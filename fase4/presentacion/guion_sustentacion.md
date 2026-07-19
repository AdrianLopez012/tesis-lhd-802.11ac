# GUION DE SUSTENTACIÓN Y DEFENSA — Adrián López · Trabajo de Tesis 2

> Regla del asesor: **expones para el JURADO, no para el público** — registro técnico, sin
> simplificaciones de feria. Estructura de toda respuesta: reconocer → idea clave → número → cierre.

---

## 0. LOS NÚMEROS SAGRADOS

| Qué | Valor | Límite |
|---|---|---|
| Latencia comandos (OWD) | **3.04 ± 0.26 ms** | ≤ 20 ms |
| Latencia vídeo E2E (incluye códec 35 ms) | **35.9 ± 0.3 ms** | ≤ 150 ms |
| RTT lazo de control | **6.12 ms** | ≤ 40 ms |
| Jitter vídeo P95 | **0.28 ms** | ≤ 10 ms |
| Goodput vídeo | **40 Mbps** | ≥ 38 Mbps |
| PLR vídeo / comandos | **0.01 % / 0.06 %** | ≤ 1 % / ≤ 0.5 % |
| Disponibilidad | **100 %** | ≥ 99.9 % |
| Handover (peor caso) | **0.91 ms** | ≤ 150 ms |
| RSSI mínimo del enlace servidor | **−72.1 dBm** (margen 9.9 dB) | −82 dBm usable |
| Rigor | 18 corridas × 300 s · 10 semillas · IC 95 % | — |
| Estrés | 50 Mbps vídeo / 4 m/s: **todo cumple** (comandos 3.0→6.8 ms) | — |
| Modelo | two-slope n₁=1.9 · n₂=3.4 · d_bp=40 m · calibrado TamoGraph | — |
| Ray-tracing | roca εr=6, σ=0.01 S/m · hasta 6 reflexiones · error ~5 dB campo cercano | — |
| OSINERGMIN 2024 | **12/14 accidentes y 13/15 víctimas** en subterránea | — |

---

## 1. GUION HABLADO — SLIDE POR SLIDE (20 min · ensayar a 18)

### SLIDE 1 — Carátula (0:20)
"Buenas tardes, señores miembros del jurado. Mi nombre es Adrián Álvaro López Pascual y
presento el trabajo de tesis *Diseño de una red IEEE 802.11ac para la teleoperación de un
vehículo LHD en la extracción de mineral en galerías subterráneas*, desarrollado bajo la
asesoría del Dr. Pastor David Chávez Muñoz. La imagen de fondo es el modelo tridimensional
del nivel NV1640 de la mina Cerro Lindo, construido en MATLAB a partir del plano real."

### SLIDE 2 — De qué trata (0:40)
"En una frase: esta tesis diseña y valida por simulación la red de comunicaciones que
permite operar un cargador de bajo perfil —un LHD— desde una sala de control en superficie,
retirando al operador del frente de riesgo sin detener la producción. Para eso la red debe
sostener tres flujos simultáneos y de naturaleza distinta: vídeo de conducción en tiempo
real, comandos de control de baja latencia, y telemetría continua del vehículo. El caso de
estudio es el nivel NV1640 de la mina Nexa Cerro Lindo."

### SLIDE 3 — Motivación (3:00)
[45 s — TU historia personal, con tus palabras. La raíz: "Nací en una tierra donde la
minería marca la vida de las familias…" — genuina, sin dramatizar.]
"…Y esa realidad tiene números. En 2024, OSINERGMIN reportó 14 accidentes mineros fatales:
12 ocurrieron en operaciones subterráneas, y de las 15 víctimas, 13 estaban bajo tierra —
el 87 %. El frente de acarreo, donde trabaja el operador del LHD, concentra los mecanismos
más letales: desprendimiento de rocas, gases y tránsito de maquinaria pesada.
La teleoperación existe comercialmente. Lo que faltaba demostrar con evidencia es que una
RED puede sostenerla en una mina peruana real, con su geometría y sus equipos. Eso hace
esta tesis."

### SLIDE 4 — Objetivos (3:00)
"El objetivo general es diseñar la red 802.11ac para la teleoperación del LHD con
**evidencia verificable** del cumplimiento de los indicadores de desempeño — subrayo
verificable: cada afirmación de esta tesis tiene un número y una fuente detrás.
Seis objetivos específicos lo despliegan, y son la columna vertebral de los capítulos:
primero, **caracterizar el canal** de propagación en las galerías; segundo, **diseñar la
arquitectura** física y lógica; tercero, **dimensionar el subsistema de radio y antenas**;
cuarto, **definir las políticas de QoS y movilidad**; quinto, **validar el desempeño extremo
a extremo** por simulación a nivel de paquete; y sexto, **evaluar la idoneidad** técnica,
económica, ambiental y ética de la solución." [~20 s por objetivo, conectados.]

### SLIDE 5 — Metodología: Design Thinking (5:00)
"La metodología es **Design Thinking**, el proceso de diseño centrado en la persona que
usamos en TEL143 y TEL147, en cinco pasos.
**Empatizar** (40 s): el punto de partida no es la tecnología, es el operador: su exposición
a desprendimientos, gases y vibración en el frente de acarreo.
**Definir** (40 s): esa necesidad se traduce a requisitos de ingeniería verificables — los
KPIs: latencia de comandos ≤ 20 ms, vídeo ≤ 150 ms, jitter ≤ 10 ms, disponibilidad ≥ 99.9 %,
traspaso ≤ 150 ms.
**Idear** (40 s): revisión sistemática de literatura con el método Kitchenham y análisis
multicriterio de tecnologías: LPWAN no soporta vídeo; LTE/5G privado añade complejidad y
costo; los enlaces ópticos son sensibles al alineamiento. La elección: 802.11ac industrial
con malla Kinetic Mesh, por capacidad, equipos mineros certificados y priorización estándar.
**Prototipar** (40 s): simulación en ns-3.40 sobre la **geometría real** del nivel —
generada automáticamente desde el plano—, con los 12 puntos de acceso en sus posiciones
reales y el recorrido real del ciclo de acarreo.
**Validar** (40 s): el modelo de propagación se calibró contra el site survey TamoGraph de
la mina, y se ejecutaron 18 simulaciones de 300 segundos: diez semillas independientes del
escenario de operación, línea base, dos escenarios de estrés y uno de traspaso.
Cierro con el principio de rigor: **ningún número de esta tesis sale de una sola corrida**."

### SLIDE 6 — Geometría real + VIDEO (1:15)
"Este es el nivel NV1640 real: tres galerías de producción paralelas, cruceros, puntos de
extracción y piques de traspaso." [15 s en el plano; CLIC → video]
"El vehículo recorre el ciclo real de operación — carga en el drawpoint, acarreo, descarga
en el pique. Arriba ven el punto de acceso que lo está sirviendo y su nivel de señal,
instante a instante. Esto son **datos de la simulación**, no una animación decorativa."
[Si el video no arranca: seguir con la imagen fija SIN perder ritmo.]

### SLIDE 7 — Arquitectura de anillo (0:45)
"La arquitectura sigue el principio de misión crítica: **solo el último tramo es
inalámbrico**. Del LHD al punto de acceso, radio 802.11ac; del punto de acceso al switch de
acceso, cable Cat6; y de ahí, un **anillo de fibra óptica monomodo de 1 gigabit** hasta el
nodo core y la estación de teleoperación. El anillo aporta redundancia física — si un tramo
se corta, el tráfico gira por el lado sano — y en el core, switches de capa 3 con
redundancia de gateway VRRP. El diseño está alineado a la red documentada de la mina."

### SLIDE 8 — KPIs · LA SLIDE MÁS IMPORTANTE (1:30)
"Estos son los resultados centrales del trabajo." [pausa]
"Latencia de comandos: **3 milisegundos**, contra un límite de 20 — más de seis veces de
margen. Latencia de vídeo extremo a extremo, incluyendo el códec: **36 milisegundos** contra
150. Disponibilidad del enlace: **100 %** contra 99.9 exigido. Jitter: 0.28 milisegundos
contra 10. Pérdida de paquetes de vídeo: una centésima de punto porcentual." [pausa]
"E insisto en el punto metodológico: son **medias con intervalo de confianza al 95 % sobre
diez semillas independientes**. No es una corrida afortunada. Todos los indicadores cumplen,
y cumplen con margen."

### SLIDE 9 — RSSI y roaming (0:45)
"La pregunta natural es: ¿y cuando el vehículo dobla la esquina y pierde línea de vista?
Esta es la señal del enlace servidor durante todo el ciclo: la línea azul **nunca cae por
debajo de −72.1 dBm** — 9.9 dB por encima del umbral utilizable. Y el roaming es estable,
*make-before-break*, igual que el equipo de malla real: el vehículo no persigue al AP más
cercano — mantiene el enlace hasta tener uno mejor asegurado. El traspaso de peor caso
midió **0.91 milisegundos**, contra 150 permitidos."

### SLIDE 10 — WMM multi-semilla y estrés (1:00)
"El panel izquierdo muestra la latencia de cada flujo con su dispersión entre las diez
semillas: las cajas son diminutas — el resultado es **estable**. Comandos y telemetría en
torno a 3 milisegundos; vídeo, 36.
El panel derecho compara los cuatro escenarios: en el estrés de vídeo a 50 megabits, los
comandos suben de 3.0 a 6.8 milisegundos — se multiplican por 2.3 — pero **nunca se acercan
al límite de 20**: la clase de acceso de voz AC_VO los protege.
¿Por qué la telemetría no lleva prioridad? Porque es tolerante al retardo — son datos de
estado; lo crítico es el mando. Y aun en la clase de mejor esfuerzo mide 3 milisegundos:
la priorización es un seguro para cuando hay presión."

### SLIDE 11 — Capa física (1:00)
"El análisis no se queda en la capa de red: **baja hasta el símbolo de modulación**. Aquí
ven la jerarquía de esquemas de modulación y codificación del estándar reproducida en
MATLAB, la constelación 256-QAM reconstruida después del canal con el receptor VHT completo
— sincronización, ecualización y demodulación — y la curva de tasa de error de paquete
contra relación señal-ruido. Es la evidencia de que la capa física del diseño se sostiene,
no solo su capa de red."

### SLIDE 12 — Antenas según datasheet (0:40)
"Cada antena está justificada por su hoja de datos Poynting. El Hawk de galería lleva el
**par RCP-50, polarización izquierda y derecha**: es bidireccional — dos lóbulos que cubren
la galería en ambos sentidos, especificado por el fabricante para instalación en túneles y
minas — y las dos polarizaciones circulares dan la **diversidad para los dos flujos
espaciales MIMO**. Por eso va en los tramos largos. El Cardinal de los cruceros usa la
EPNT-7 omnidireccional. Y el LHD lleva la **HELI-40 de 4.8 dBic**, también bidireccional,
porque el vehículo avanza y retrocede. La polarización circular mitiga el multitrayecto de
la roca. Los patrones están calculados por método de momentos."

### SLIDE 13 — Ray-tracing: validación cruzada (0:45)
"Esta lámina blinda el modelo. Primero: construí la galería en 3D con propiedades de roca
reales — permitividad relativa 6, conductividad 0.01 siemens por metro. Segundo: lancé un
trazado de rayos SBR con hasta seis reflexiones. Tercero: en campo cercano, **ambos métodos
coinciden con un error del orden de 5 dB** — el modelo queda validado por un método
independiente que no comparte ningún supuesto con él. Y cuarto, con honestidad metodológica:
a larga distancia el trazado de rayos pierde los rayos porque no modela el guiado de onda
del túnel — limitación documentada en la literatura — y eso **justifica** usar el two-slope
calibrado con el survey real. Doble validación, y cada método usado donde es válido."

### SLIDE 14 — Idoneidad (1:00)
"La idoneidad se evalúa en cuatro dimensiones. **Técnica**: todos los KPIs con margen y
equipo certificado para mina. **Económica** — y aquí soy honesto—: la estructura de costos
CAPEX/OPEX y los mecanismos de retorno están definidos, incluida la métrica de costo por
metro de galería cubierta; la cuantificación exacta requiere cotizaciones vigentes y es el
paso siguiente con planeamiento de la mina. **Ambiental**: banda de 5 GHz de uso libre,
potencias reguladas. **Ética y social**: el proyecto no reemplaza al trabajador — lo reubica
fuera del riesgo, con reconversión hacia el centro de control."

### SLIDE 15 — Reflexión final (1:00)
[El pitch, desde la plataforma de triunfo. Frase central con pausa:]
"La tecnología para no volver a poner a una persona frente al mineral **ya existe**. Lo que
aporta esta tesis es la **evidencia verificable** de que la red que la sostiene funciona en
la geometría real de una mina peruana: cada indicador cumplido con margen y con respaldo
estadístico. Me llevo el aprendizaje de integrar propagación, redes y análisis de idoneidad
en un solo diseño. Y la proyección es directa: mediciones de campo, y de ahí, el despliegue.
Una minería que produce igual — y expone menos vidas." [mirando al jurado]

### SLIDE 16 — Gracias (0:15)
"Muchas gracias, señores del jurado, y gracias a mi asesor. Quedo atento a sus preguntas."
[Respirar. Cada respuesta: reconocer → dato → remitir a la evidencia (capítulo/anexo).]

**Total ≈ 19:40 → meta 18:00.** Si vas tarde: recorta S11 (a 30 s) y S14 (a 40 s). NUNCA S3 ni S8.

---

## 2. LAS 2 PREGUNTAS PARA EL ASESOR — con explicación para INTERIORIZAR

### PREGUNTA A
> **"Su modelo de propagación es semi-empírico. ¿Qué evidencia independiente tiene de que
> no está sobreestimando la cobertura real de la galería, y por qué un modelo de dos
> pendientes representa correctamente la física del túnel?"**

**Respuesta modelo (≈75 s):**
"El túnel se comporta como una guía de onda imperfecta: cerca del transmisor coexisten
múltiples modos que refuerzan la señal — por eso el exponente n₁ = 1.9, cercano al espacio
libre —; pasado el punto de quiebre, a 40 metros, los modos superiores se atenúan por la
rugosidad de la roca y queda el modo dominante, con n₂ = 3.4. No usé valores de literatura
urbana: los coeficientes se calibraron contra el site survey TamoGraph de la mina. Y la
evidencia independiente es triple: el contraste con TamoGraph, un trazado de rayos SBR sobre
el modelo 3D de la galería con propiedades de roca, y el presupuesto de enlace analítico —
métodos que no comparten supuestos y convergen. Además el modelo es deliberadamente
conservador: el equipo real solo puede mejorar estos números. Es validación de diseño; la
medición de campo es el paso natural siguiente, y así lo declaro."

**🧠 PARA INTERIORIZAR — qué significa cada término:**
- **Modelo semi-empírico**: mezcla una fórmula teórica (la ley de pérdidas con la distancia)
  con constantes ajustadas a partir de MEDICIONES (el survey). Ni pura teoría ni pura medición.
- **Two-slope (dos pendientes)**: la señal no decae igual en todo el trayecto. Cerca del
  transmisor decae despacio (pendiente 1); lejos, decae rápido (pendiente 2). El punto donde
  cambia se llama **punto de quiebre (d_bp = 40 m)**.
- **Exponente de pérdidas (n)**: qué tan rápido cae la potencia con la distancia. n=2 es el
  espacio libre (sin obstáculos). **n₁=1.9 < 2** significa que el túnel CONCENTRA la energía
  (mejor que espacio libre) — efecto guía de onda. **n₂=3.4** significa que lejos decae mucho
  más rápido, porque solo sobrevive un modo.
- **Guía de onda**: estructura que confina y conduce ondas (como un tubo conduce agua). El
  túnel actúa como una guía de onda "imperfecta" porque sus paredes de roca no son lisas ni
  perfectamente conductoras.
- **Modos de propagación**: las distintas "formas" en que la onda puede acomodarse dentro de
  la guía (patrones de campo). Cerca del transmisor viajan muchos modos a la vez; con la
  distancia, los modos de orden alto se atenúan (chocan más con las paredes) y sobrevive el
  **modo dominante** (el de menor pérdida).
- **Rugosidad**: las irregularidades de la pared de roca. Cada rebote en una superficie
  rugosa dispersa energía → atenúa más los modos altos.
- **TamoGraph site survey**: estudio de cobertura hecho EN la mina con un software comercial
  (TamoGraph) que mide señal real punto por punto caminando el área. Es el dato empírico con
  el que calibré mis constantes.
- **Ray-tracing (trazado de rayos)**: técnica que simula la propagación lanzando miles de
  "rayos" desde la antena y siguiendo cada uno geométricamente: en qué pared rebota, cuánta
  energía pierde en cada rebote, hasta llegar al receptor. Es un método DETERMINISTA basado
  en óptica geométrica + electromagnetismo.
- **SBR (Shooting and Bouncing Rays)**: el algoritmo concreto de ray-tracing que usa MATLAB:
  "dispara" rayos en todas direcciones y los hace "rebotar" (hasta 6 reflexiones en mi caso)
  contra el modelo 3D. De ahí el nombre: disparar y rebotar.
- **Permitividad relativa (εr = 6)**: propiedad eléctrica del material que dice cuánto se
  polariza ante un campo eléctrico; determina cuánta señal se refleja y cuánta penetra en la
  roca. 6 es el valor típico de roca dura.
- **Conductividad (σ = 0.01 S/m)**: cuánta corriente puede conducir el material; determina
  cuánta energía ABSORBE la roca en cada rebote.
- **Presupuesto de enlace (link budget)**: la suma contable de la cadena: potencia
  transmitida + ganancias de antenas − pérdidas de trayecto − pérdidas de cables = potencia
  recibida. Si queda por encima de la sensibilidad del receptor, el enlace cierra. Es el
  tercer método, puramente analítico.
- **"Convergen"**: los tres métodos, sin compartir supuestos, predicen los mismos puntos de
  cruce de cobertura (~127 m y ~327 m). Cuando caminos independientes llegan al mismo
  resultado, la confianza se multiplica.
- **Conservador**: el modelo asume el caso desfavorable (sin ganancias oportunistas de mesh,
  determinista). Si me equivoco, me equivoco hacia el lado seguro.
- **Validación de diseño vs experimental**: de diseño = demostrar por métodos convergentes y
  calibrados que el diseño cumple EN MODELO. Experimental = medir en el campo desplegado.
  Declaro la primera y remito la segunda a trabajo futuro. NUNCA sobre-afirmar.

### PREGUNTA B
> **"A 5 GHz, en una sección de 5 × 4.5 metros con paredes rugosas, ¿por qué eligió antenas
> de polarización circular y qué pasaría si hubiera usado polarización lineal?"**

**Respuesta modelo (≈70 s):**
"A 5 GHz estamos muy por encima de la frecuencia de corte del modo fundamental de esa
sección, así que la galería propaga múltiples modos con rebotes sucesivos en paredes, piso y
techo. Con polarización lineal, cada rebote rota el plano de polarización y las réplicas
llegan desalineadas: interferencia destructiva y desvanecimientos profundos. Con polarización
circular, el rebote invierte el sentido de giro — la antena discrimina la réplica reflejada
y mantiene el acoplamiento con la componente directa: el desvanecimiento se suaviza y la
relación señal-ruido queda estable. Por eso el diseño usa la familia helicoidal de Poynting:
el Hawk lleva el par RCP-50 con polarización izquierda y derecha — que además aporta
diversidad de polarización para los dos flujos espaciales MIMO — y el LHD lleva la HELI-40
bidireccional de 4.8 dBic, que es la que entra al presupuesto de enlace. El resultado
medible: el RSSI del enlace nunca cayó de −72.1 dBm en todo el recorrido."

**🧠 PARA INTERIORIZAR — qué significa cada término:**
- **Frecuencia de corte**: la frecuencia mínima que puede propagarse dentro de una guía de
  onda de cierto tamaño. Para un túnel de 5 × 4.5 m es de unas decenas de MHz — y nosotros
  operamos a 5 GHz, o sea CIEN veces por encima → la galería propaga sin problema y admite
  MUCHOS modos a la vez (por eso hay multitrayecto).
- **Modo fundamental**: el primer modo, el de menor frecuencia que "cabe" en la guía.
- **Multitrayecto**: la señal llega al receptor por varios caminos (directo + rebotes en
  paredes/piso/techo). Las copias llegan con retardos y fases distintas.
- **Polarización**: la orientación en que oscila el campo eléctrico de la onda.
  **Lineal**: oscila en un plano fijo (vertical u horizontal). **Circular**: el campo va
  ROTANDO como un sacacorchos mientras avanza — puede girar a la izquierda (LHCP) o a la
  derecha (RHCP).
- **Qué hace un rebote**: al reflejarse en la roca, una onda circular INVIERTE su sentido de
  giro (LHCP se vuelve RHCP y viceversa). Una antena de polarización circular "escucha" solo
  su sentido de giro → **rechaza naturalmente la réplica reflejada de primer orden**. Con
  polarización lineal no hay ese filtro: la copia rebotada entra igual, y si llega en
  contrafase, RESTA.
- **Interferencia destructiva / fading (desvanecimiento)**: cuando dos copias de la señal
  llegan en fases opuestas se cancelan → caídas profundas de señal en ciertos puntos del
  túnel. Es el enemigo #1 de un enlace móvil en túnel.
- **SNR (relación señal-ruido)**: cuánta señal útil hay sobre el ruido de fondo. SNR estable
  = modulación alta sostenida = throughput estable.
- **RCP-50 LHP + RHP (el "par")**: dos antenas helicoidales del Hawk, una de giro izquierdo y
  otra derecho. El datasheet Poynting las especifica "Bi-Directional, Mine/tunnel".
- **Bidireccional**: radia en DOS lóbulos opuestos a lo largo del túnel (adelante y atrás),
  no en círculo — ideal para cubrir tramos largos de galería desde un punto.
- **Diversidad de polarización**: usar dos polarizaciones ortogonales (izquierda/derecha)
  como dos "canales" poco correlacionados. Eso le da soporte físico a los **2 streams MIMO**.
- **MIMO 2×2 / streams espaciales**: el estándar envía DOS flujos de datos simultáneos por
  el mismo canal usando dos cadenas de radio. Necesita que los dos caminos sean
  distinguibles — y las dos polarizaciones circulares lo garantizan incluso en túnel.
- **HELI-40 / dBic**: antena helicoidal embarcada del LHD, ganancia 4.8 dBic. El sufijo "ic"
  = dB respecto a un radiador isotrópico de polarización CIRCULAR (así se especifican las
  antenas circulares). El vehículo avanza y retrocede → antena bidireccional.
- **Método de momentos**: técnica numérica de electromagnetismo (resuelve las ecuaciones de
  Maxwell discretizando la antena) con la que MATLAB Antenna Toolbox calcula los patrones
  de radiación que mostré.

*(Si el asesor prefiere preguntas más cortas al formularlas en la mesa, las versiones
breves: A) "¿Qué evidencia independiente respalda su modelo de propagación?" · B) "¿Por qué
polarización circular en el túnel?")*

---

## 3. EL PUNTO DÉBIL: VIABILIDAD SIN VAN/TIR — DEFENSA EN 3 CAPAS

**Capa 1 — La decisión:** "Un VAN o TIR exige flujos de caja: precios vigentes y datos
financieros internos de la mina — confidenciales, fuera del alcance de un trabajo de
gabinete. Calcular un VAN con supuestos inventados sería pseudo-precisión. Preferí entregar
la estructura completa y dejar la cuantificación a la fase de implementación."

**Capa 2 — Lo que SÍ entrega el Cap. 4:** estructura CAPEX/OPEX por categorías · métrica
**"costo por metro de galería cubierta"** (pensada para el frente que avanza: nodos mesh
reubicables, 100 % de reutilización de activos) · mecanismos de retorno: horas-hombre fuera
de exposición, continuidad operativa tras voladura, primas y costos de accidente · inversión
**incremental** sobre el backbone que la mina ya tiene.

**Capa 3 — El remate:** "Hay un argumento económico que no necesita cotización: el costo de
UN accidente fatal — multa, paralización, procesos — supera típicamente el CAPEX completo de
esta red. Con cotizaciones vigentes, la plantilla del Capítulo 4 permite calcular VAN y TIR
directamente: es trabajo inmediato de la siguiente fase, no un vacío conceptual."

---

## 4. MATRIZ DE JURADOS — ataques y contragolpes VERIFICADOS

### ⚠️ TRES CORRECCIONES (tu tesis NO dice esto tal cual — no lo cites así)
1. **"Watchdog en Tabla 7" NO existe.** Sí están: "modos degradados" y "parada segura" en
   aspectos éticos/recomendaciones. → "El diseño contempla modos degradados y parada segura
   ante pérdida de enlace; el temporizador de vigilancia concreto es ingeniería de detalle
   de la implementación."
2. **"Expedited Forwarding / Strict Priority" NO están escritos.** Sí está: mapeo WMM →
   colas/DSCP. → "La tesis define el mapeo de clases WMM a DSCP; llevar comandos a la clase
   máxima —el equivalente EF— es configuración de implementación."
3. **HELI-22 y HELI-40 aparecen AMBAS en la tesis** (glosario/solución vs. presupuesto de
   enlace/conclusiones). → "Familia helicoidal Poynting; la antena dimensionada del LHD es
   la HELI-40 de 4.8 dBic — la que entra al presupuesto de enlace y a la simulación."

### DR. CHÁVEZ (física del medio · anti caja-negra · worst-case)
- **Caja negra ns-3**: "El modelo de pérdidas NO es de catálogo: es una clase propia,
  escrita ecuación por ecuación (two-slope + distancia por ruta de túnel + penalización
  NLOS), calibrada con el survey. La contención del medio la resuelve el MAC 802.11e con
  colas EDCA por clase de acceso, y FlowMonitor mide retardo por paquete."
- **Worst-case**: estrés 50 Mbps + 4 m/s + escenario de handover + P95. Falla catastrófica
  de APs: no modelada — limitación declarada; mitigación por densidad (12 AP solapados).
- **Semillas**: re-inicializan la aleatoriedad de la CONTENCIÓN del medio y los tiempos de
  tráfico (microsegundos) → 10 realizaciones independientes → media ± IC 95 %.
  ⚠️ NO digas que varían el shadowing: tu propagación es determinista (decisión declarada).

### ING. PACO (L2/L3 · Cisco · costos · alta disponibilidad)
- **Backbone/redundancia**: anillo FO + core L3 con **VRRP/HSRP** (SÍ está en la tesis).
- **QoS E2E**: mapeo WMM→DSCP (corrección #2).
- **BoM/ambiente**: Hawk IP67 contra polvo/agua; Cardinal embarcado para vibración severa.
  "No es equipo comercial adaptado: es hardware de misión crítica minera con datasheet."
- **Frente que avanza**: mesh auto-organizable → reubicar un Hawk no toca el core; métrica
  "costo por metro de galería cubierta" (SÍ está) + reutilización 100 % de activos.
- **VAN/TIR** → sección 3.

### ING. CÓRDOVA (humano · QoE · energía · borde)
- **QoE/MOS sin operador**: mapeo objetivo ITU-T **G.1010** (SÍ está): jitter P95 < 10 ms y
  PLR < 1 % ⇒ H.264 1080p30 sin artefactos ⇒ MOS ≥ 4 indirecto. Tus números: 0.28 ms / 0.01 %.
- **Energía a bordo**: modelo referencial **Heinzelman (Anexo J.3**, SÍ está); consumo del
  radio marginal frente al sistema eléctrico de un LHD; PoE industrial; ante caída de
  tensión → modo degradado/parada segura (corrección #1).
- **Pérdida total de enlace**: la asimetría central: el operador está en superficie — el
  peor caso técnico cuesta producción, NO vidas. Parada segura del vehículo.
- **Sociolaboral**: no reemplaza: **reubica** (jerarquía de controles SSO, Sección 1.5.2);
  reconversión a operador de centro de control.

---

## 5. REGLAS DE ORO
1. **Responder COMPLETO puntúa**: reconocer → idea → número → cierre.
2. "Validación de diseño", "alcance declarado", "limitación declarada" — madurez, no debilidad.
3. Nunca a la defensiva; nunca inventar. "No lo desarrollé; lo abordaría así…"
4. No dejar mal parado al asesor: solvencia en la matemática base para que él pueda cerrar puntos.
5. P20 ("¿qué cambiaría?"): mediciones de campo propias. NUNCA "nada".
6. Expones para el JURADO, no para el público.
7. **3 ms · 36 ms · 100 %** — sin mirar.

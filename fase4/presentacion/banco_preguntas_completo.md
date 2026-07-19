# BANCO COMPLETO DE PREGUNTAS DEL JURADO — versión definitiva
### Sustentación · Red IEEE 802.11ac para teleoperación de LHD · Adrián López

> Cada respuesta: 30–60 s. Estructura: **reconocer → idea clave → número → cierre.**
> Los ítems marcados ⚠️ son trampas o requieren cuidado especial con lo que dice tu tesis.
> Complementa (no reemplaza) el `banco_preguntas_jurado.docx` — aquí están TODAS, organizadas
> por quién es más probable que las haga.

---

## BLOQUE 1 — FÍSICA Y PROPAGACIÓN (perfil Dr. Chávez)

**1.1 ¿Por qué un modelo de dos pendientes y qué significa físicamente el punto de quiebre a 40 m?**
El túnel es una guía de onda imperfecta: cerca del transmisor coexisten múltiples modos que
concentran la energía (n₁=1.9, mejor que espacio libre); a partir de ~40 m los modos de orden
alto se han atenuado por la rugosidad y sobrevive el modo dominante (n₂=3.4). El punto de
quiebre marca esa transición modal.

**1.2 ¿Un exponente n₁=1.9 menor que 2 no es antinatural?**
No: es la firma del efecto guía de onda, documentada en la literatura de túneles y minas. El
confinamiento hace que cerca del transmisor la señal decaiga MÁS DESPACIO que en espacio libre.

**1.3 ¿La señal atraviesa la roca entre galerías?**
No. A 5 GHz el pilar de ~26 m atenúa decenas de dB — supuesto declarado. En el modelo la
distancia se calcula POR LA RUTA DE TÚNEL (la señal rodea por los cruceros) más una
penalización NLOS de 10 dB por esquina cruzada.

**1.4 ¿De dónde sale la penalización NLOS de 10 dB?**
De la literatura de pérdida por esquina en minas y túneles, que reporta 6–15 dB por cruce;
tomé un valor central y conservador, coherente con el comportamiento observado en el survey.

**1.5 ⚠️ El site survey TamoGraph, ¿era de este mismo nivel?**
Corresponde a un nivel análogo del mismo yacimiento, con el mismo método de explotación y
tipo de roca. Por eso la tesis lo declara como CONTRASTE DOCUMENTAL de coherencia — no como
validación punto a punto — y los coeficientes se ajustan a ese dato empírico. Honestidad
metodológica declarada.

**1.6 ¿Qué es el ray-tracing SBR y por qué solo vale en campo cercano?**
SBR = Shooting and Bouncing Rays: dispara miles de rayos y los rebota (hasta 6 reflexiones)
contra el modelo 3D con roca de εr=6 y σ=0.01 S/m. En campo cercano coincide con el two-slope
(error ~5 dB) → validación independiente. A larga distancia pierde los rayos porque no modela
el guiado de onda — limitación documentada — lo que justifica usar el two-slope calibrado.

**1.7 ¿Por qué polarización circular y no lineal?**
El rebote en la roca invierte el sentido de giro (LHCP↔RHCP): la antena circular discrimina
la réplica reflejada y evita el desvanecimiento por interferencia destructiva que sufriría la
lineal. Resultado medible: RSSI nunca bajo −72.1 dBm.

**1.8 ¿Y el delay spread del canal? ¿No rompe la señal OFDM?**
El delay spread típico de galería minera (decenas a centenas de ns) queda muy por debajo del
prefijo cíclico de 802.11ac (0.8/0.4 µs): la OFDM absorbe esa dispersión temporal por diseño.
Es una de las razones por las que el estándar es apto para túnel.

**1.9 ¿Por qué 5 GHz y no 2.4 GHz?**
2.4 GHz da algo más de alcance pero solo 3 canales limpios, más interferencia industrial y
menos ancho. En 5 GHz dispongo de canales de 40 MHz limpios, mayor capacidad y los equipos
mineros del proyecto operan la banda con antenas de túnel específicas.

**1.10 ¿Por qué canal de 40 MHz y no 80?**
Equilibrio capacidad-robustez: 40 MHz ya entrega una PHY muy por encima del requisito
(observé hasta 360 Mbps de tasa física contra 40 Mbps requeridos) con más canales disponibles
para planificar y mejor sensibilidad por MHz. 80 MHz sería capacidad ociosa con menos margen.

**1.11 ⚠️ ¿Qué calcula exactamente ns-3? No me diga que "el software lo hizo". (alergia caja negra)**
El modelo de pérdidas NO es de catálogo: es una clase propia escrita ecuación por ecuación —
two-slope + distancia por ruta de túnel + penalización NLOS — calibrada con el survey. La
contención la resuelve el MAC 802.11e con colas EDCA por clase de acceso, y FlowMonitor mide
retardo/jitter/pérdida por paquete. Puedo escribir la ecuación de pérdidas en la pizarra.

**1.12 ¿Cómo funciona EDCA? ¿Por qué AC_VO "gana"?**
Cada clase tiene ventanas de contención y tiempos de espera (AIFS/CWmin) distintos: AC_VO
espera menos y sortea ventanas más cortas, así estadísticamente accede primero al medio. Por
eso bajo estrés los comandos suben solo de 3.0 a 6.8 ms: la prioridad los protege.

---

## BLOQUE 2 — REDES, ARQUITECTURA Y COSTOS (perfil Ing. Paco)

**2.1 ¿Cómo protege el backbone ante un corte de fibra o falla de switch?**
Anillo de fibra monomodo: un corte y el tráfico gira por el lado sano. En el core, switches
L3 con redundancia de gateway VRRP/HSRP (está en la descripción de la solución). El
presupuesto de 50 ms no se compromete.

**2.2 ⚠️ ¿Cómo garantiza el QoS de extremo a extremo (WMM → cableado)?**
La tesis define el mapeo de clases WMM a colas/DSCP en las políticas de QoS: los comandos
(AC_VO) se marcan y conservan prioridad en los switches del backbone. Llevarlos a la clase de
máxima prioridad — el equivalente a EF — es configuración de implementación sobre ese diseño.
(NO digas que "EF/Strict Priority está escrito en la tesis": no lo está.)

**2.3 ¿Los equipos aguantan polvo, humedad y vibración?**
Hawk con carcasa IP67 (polvo fino y agua); Cardinal embarcado diseñado para vibración de
maquinaria pesada. No es equipo de oficina adaptado: es hardware de misión crítica minera con
datasheet, que es la base documental del proyecto.

**2.4 ¿Qué pasa cuando el frente avanza y hay que mover APs?**
Ventaja estructural del mesh: reubicar un Hawk no exige recablear ni tocar el core — InstaMesh
se auto-organiza. La métrica del Cap. 4, costo por metro de galería cubierta, contempla esa
modularidad con 100 % de reutilización de activos.

**2.5 ⚠️ No hay VAN ni TIR. ¿El análisis económico no está incompleto?** (LA pregunta del punto débil)
Decisión metodológica: VAN/TIR exigen flujos de caja con precios vigentes y datos financieros
internos de la mina — confidenciales para un trabajo de gabinete. Un VAN con supuestos
inventados sería pseudo-precisión. Entrego la estructura CAPEX/OPEX completa, la métrica de
costo por metro cubierto y los mecanismos de retorno; y un argumento sin cotización: el costo
de UN accidente fatal supera típicamente el CAPEX de esta red. Con cotizaciones, la plantilla
del Cap. 4 da VAN/TIR directamente.

**2.6 ¿Cuántos LHD soporta esta red antes de saturar?**
El alcance declarado es un vehículo. Dimensionalmente: cada LHD demanda ~41 Mbps y la celda
entrega tasas físicas de cientos de Mbps, así que hay margen para 2-3 vehículos por celda con
la misma calidad; pero múltiples vehículos introducen contención y roaming cruzado que exigen
su propio estudio — lo dejo como extensión natural.

**2.7 ¿Direccionamiento, VLANs, segmentación de tráfico?**
El diseño lógico separa los servicios por clase (vídeo/comandos/telemetría) con marcado
DSCP; en implementación eso se acompaña de segmentación por VLAN de servicio y una zona OT
aislada de la red administrativa. La simulación valida los KPIs sobre el plano de datos.

**2.8 ¿Ciberseguridad? Un atacante podría tomar control del vehículo.**
El diseño se apoya en el cifrado del estándar (WPA2/WPA3-Enterprise con 802.1X en
implementación), la segmentación OT/IT y el principio de red aislada de misión crítica. Un
análisis de ciberseguridad ofensiva excede el alcance declarado, y lo recojo como trabajo
futuro pertinente — la capa de red que diseñé es la base que lo hace posible.

**2.9 ¿Cómo se gestiona la red en operación (monitoreo)?**
La arquitectura incluye el bloque de gestión: monitoreo del estado de nodos y enlaces desde
superficie (el propio ecosistema del fabricante mesh lo provee), alarmas por degradación de
RSSI/PLR y procedimientos de mantenimiento que la tesis recoge en las recomendaciones.

**2.10 ¿Por qué Rajant y no Cisco URWB u otra marca?**
Porque el proyecto se basa en los equipos documentados para la mina (datasheets Hawk/Cardinal,
mesh cinético probado en minería) — el diseño es agnóstico en lo esencial: cualquier mesh
industrial equivalente que cumpla los mismos parámetros RF encaja en la misma arquitectura.

**2.11 ¿La alimentación de los APs en galería?**
PoE industrial desde los switches de acceso del anillo, que se alimentan de la infraestructura
eléctrica ya presente en los niveles productivos; los equipos son de grado minero.

---

## BLOQUE 3 — QoE, ENERGÍA, OPERACIÓN Y PERSONAS (perfil Ing. Córdova)

**3.1 ⚠️ ¿Cómo garantiza MOS ≥ 4 sin un operador humano real?**
Mapeo objetivo por ITU-T G.1010 (está en la tesis): con jitter P95 < 10 ms y PLR < 1 %, la
literatura valida que H.264 1080p30 reconstruye sin artefactos → MOS ≥ 4 de forma indirecta.
Mis números: 0.28 ms y 0.01 % — órdenes de magnitud mejores que esa frontera.

**3.2 ¿Cuál es la latencia total que PERCIBE el operador (glass-to-glass)?**
La cadena completa: captura+códec (35 ms) + red (0.4 ms) + decodificación y refresco de
pantalla (decenas de ms según hardware) → del orden de 60-100 ms percibidos, bajo el umbral
de 150-200 ms que la literatura de teleoperación considera seguro para conducción.

**3.3 ¿El radio embarcado no castiga la energía del vehículo?**
El consumo del nodo embarcado (decenas de watts en pico) es marginal frente al sistema
eléctrico de un LHD de decenas de kW. El modelo referencial de consumo por paquete (enfoque
Heinzelman) está en el Anexo J.3.

**3.4 ⚠️ ¿Qué pasa si el LHD pierde TODO enlace (derrumbe de 2 APs)?**
La seguridad manda sobre la disponibilidad: el diseño contempla modos degradados y parada
segura del vehículo ante pérdida de enlace (aspectos éticos/operativos de la tesis); el
temporizador de vigilancia concreto es ingeniería de detalle de implementación. Y la
asimetría clave: el operador está en superficie — el peor caso técnico cuesta producción,
NUNCA vidas. (NO cites "watchdog en Tabla 7": no está.)

**3.5 ¿Qué pasa con el vídeo cuando el vehículo está lejos del AP y cae el MCS?**
El gestor de tasa adapta la modulación, pero incluso en los bordes del recorrido el goodput
sostuvo los 40 Mbps: el RSSI mínimo (−72.1 dBm) aún soporta MCS altos. La densidad de 12 APs
está dimensionada justamente para que nunca se opere en la zona marginal.

**3.6 ¿Los sindicatos no rechazarán esto por pérdida de empleo?**
No propone reemplazo sino reubicación responsable según la jerarquía de controles SSO
(Sección 1.5.2): el operador expuesto pasa a operador de centro de control con reconversión
de perfil. Se elimina la exposición, no el puesto.

**3.7 ¿Impacto ambiental / exposición RF?**
Banda 5 GHz de uso libre con potencias dentro de la normativa del MTC (30 dBm máx del Hawk);
la red además habilita operar tras voladura sin esperar ventilación completa — menos tiempo
muerto y menos exposición a gases.

**3.8 ¿Por qué la telemetría va en la clase de mejor esfuerzo?**
Porque es tolerante al retardo (datos de estado, no de mando). Lo crítico es el lazo de
control. Y aun en AC_BE midió 3.08 ms — la priorización es un seguro para cuando hay presión,
no una necesidad permanente.

---

## BLOQUE 4 — METODOLOGÍA Y ESTADÍSTICA

**4.1 ¿Por qué 10 semillas? ¿Qué aleatoriedad varía entre ellas?** ⚠️
Cada semilla re-inicializa la aleatoriedad de la CONTENCIÓN del medio y de los tiempos de
tráfico a nivel de microsegundos → 10 realizaciones independientes → media e IC 95 %. Las
cajas del boxchart son diminutas: el resultado es estable, no una corrida afortunada.
(⚠️ NO digas que varían el shadowing: tu propagación es determinista por decisión declarada.)

**4.2 ¿Por qué corridas de 300 segundos?**
Cubren más de un ciclo completo de acarreo (~197 s) con margen para varios traspasos y
llenado de colas — suficiente para que las métricas alcancen régimen estacionario; con 10
repeticiones, el intervalo de confianza confirma que no falta duración.

**4.3 ¿Por qué IC del 95 % y no 99?**
Es la convención de ingeniería para reportar rendimiento; con la dispersión observada
(±0.26 ms en comandos), incluso al 99 % las conclusiones no cambian — el margen contra los
límites es de un orden de magnitud.

**4.4 Su simulación es determinista, ¿no es poco realista sin shadowing?**
Decisión metodológica deliberada y declarada: el shadowing dentro del simulador desestabiliza
el roaming 802.11 y contaminaría los KPIs con un artefacto. La variabilidad de señal se
analiza en el mapa de cobertura y el contraste con el survey; la simulación de red queda
determinista y reproducible — y conservadora.

**4.5 ¿Qué herramientas usó y puede alguien reproducir sus resultados?**
ns-3.40 (código C++ propio), MATLAB R2024b (Antenna/WLAN Toolbox) y Python para el pipeline
de geometría y figuras. Todo parte de una fuente única de datos del plano, y el anexo digital
incluye código, resultados y huellas SHA-256: cualquier miembro del jurado puede regenerar
cada figura.

**4.6 ¿Por qué Design Thinking y no una metodología "de ingeniería" clásica?**
Es la metodología del curso (TEL143/TEL147) y encaja porque el problema nace en una persona
—el operador expuesto—; los 5 pasos aterrizan esa necesidad en KPIs verificables y terminan
en prototipo validado. El rigor técnico vive DENTRO de prototipar y testear.

---

## BLOQUE 5 — DECISIONES DE TECNOLOGÍA Y FUTURO

**5.1 ⚠️ ¿Por qué 802.11ac (Wi-Fi 5) y no Wi-Fi 6/6E, que ya es el estándar vigente?** (alergia a obsolescencia)
Porque el ecosistema de equipos MINEROS certificados del proyecto es 802.11ac Wave 2 — en
entornos industriales la adopción va detrás del mercado de consumo por certificación y
robustez. Las mejoras de ax (OFDMA, más eficiencia multiusuario) brillan con decenas de
clientes; con un LHD el cuello no está ahí. Y la arquitectura es agnóstica: migrar los radios
a ax no cambia el diseño — anillo, mesh, QoS y dimensionamiento se conservan.

**5.2 ¿Y las redes 5G privadas, que están bajando de costo?**
Superiores para movilidad masiva y decenas de vehículos, pero exigen núcleo dedicado,
espectro gestionado e integración más compleja. Para UN vehículo en un corredor acotado,
802.11ac industrial cumple todos los KPIs con margen a una fracción de la complejidad. Si la
mina escala a flotas, la evaluación cambia — y lo digo en trabajo futuro.

**5.3 Si la mina quisiera implementarlo mañana, ¿cuál es el primer paso?**
Piloto en un tramo del nivel: desplegar 2-3 nodos, medir en campo los parámetros del canal,
recalibrar el modelo con datos propios y validar los KPIs medidos contra los simulados. Con
esa correlación, el despliegue por fases del nivel completo.

**5.4 ¿Esto sirve para otras minas o solo para Cerro Lindo?**
La metodología es replicable por diseño: plano → fuente única de geometría → simulación →
KPIs. Cambias el plano y los datasheets y el mismo pipeline dimensiona otra mina. Lo
específico es el caso de estudio; lo transferible es el método.

**5.5 ¿Qué cambiaría si volviera a empezar?**
Gestionaría desde el inicio mediciones de campo propias del nivel para calibrar con datos
primarios, y sumaría una validación independiente adicional. Nunca: "nada".

**5.6 ¿Qué aprendió?**
A integrar tres mundos que la carrera enseña por separado — propagación, redes y análisis de
idoneidad — y que un buen diseño se defiende con evidencia verificable, no con adjetivos.

---

## LOS 12 ATAQUES DIRECTOS DE LOS PERFILES (referencia rápida)

| Jurado | Ataque | Respuesta base |
|---|---|---|
| Chávez | Formalización matemática del modelo | 1.1 + 1.11 (ecuación en pizarra) |
| Chávez | Presupuesto de latencia E2E | Descomposición: códec 35 + red 0.4 + colas EDCA acotadas (RTT 6.12) |
| Chávez | Validez de las 10 semillas | 4.1 ⚠️ (contención, NO shadowing) |
| Chávez | Física de polarización circular | 1.7 (+ pregunta B del asesor) |
| Paco | Cuello de botella backbone | 2.1 (anillo + VRRP/HSRP) |
| Paco | QoS E2E WMM→DSCP | 2.2 ⚠️ |
| Paco | BoM y grado IP | 2.3 |
| Paco | Frente que avanza / ciclo de vida | 2.4 |
| Córdova | QoE/MOS sin humano | 3.1 |
| Córdova | Energía a bordo | 3.3 |
| Córdova | Pérdida total de enlace | 3.4 ⚠️ |
| Córdova | Impacto sociolaboral | 3.6 |

## RECORDATORIOS FINALES
- Los 3 números sagrados: **3 ms · 36 ms · 100 %**.
- Las 3 minas verificadas: watchdog ✗ · EF/Strict-Priority ✗ · HELI-22/40 (ambas, la del LHD es HELI-40).
- Nunca sobre-afirmar; "alcance declarado" y "validación de diseño" son tus escudos.
- Responder COMPLETO puntúa. Reconocer → idea → número → cierre.

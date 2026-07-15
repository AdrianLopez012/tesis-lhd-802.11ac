# -*- coding: utf-8 -*-
# Banco de preguntas del jurado — documento Word para la sustentación.
import docx, sys
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
sys.stdout.reconfigure(encoding="utf-8")

AZUL = RGBColor(0x00,0x33,0xA0); CEL = RGBColor(0x2E,0x6F,0xB0)
VERDE = RGBColor(0x2E,0x8B,0x57); GRIS = RGBColor(0x5B,0x66,0x70)

d = docx.Document()
st = d.styles["Normal"]; st.font.name="Calibri"; st.font.size=Pt(11)
for s in d.sections:
    s.top_margin=s.bottom_margin=Inches(0.7); s.left_margin=s.right_margin=Inches(0.8)

def H1(t):
    p=d.add_paragraph(); r=p.add_run(t); r.bold=True; r.font.size=Pt(20); r.font.color.rgb=AZUL; r.font.name="Cambria"
    p.space_after=Pt(4)
def H2(t):
    p=d.add_paragraph(); r=p.add_run(t); r.bold=True; r.font.size=Pt(14); r.font.color.rgb=CEL; r.font.name="Cambria"
    p.space_before=Pt(10); p.space_after=Pt(2)
def Q(n,t):
    p=d.add_paragraph(); r=p.add_run(f"P{n}.  {t}"); r.bold=True; r.font.size=Pt(11.5); r.font.color.rgb=AZUL
    p.space_before=Pt(8)
def A(t):
    p=d.add_paragraph(); r=p.add_run("R:  "); r.bold=True; r.font.color.rgb=VERDE
    r2=p.add_run(t); r2.font.size=Pt(11)
    p.space_after=Pt(2)
def TIP(t):
    p=d.add_paragraph(); r=p.add_run("💡 "+t); r.italic=True; r.font.size=Pt(10); r.font.color.rgb=GRIS

# ---------- portada ----------
H1("Banco de preguntas del jurado")
p=d.add_paragraph(); r=p.add_run("Sustentación · Diseño de una red IEEE 802.11ac para la teleoperación de un vehículo LHD")
r.italic=True; r.font.color.rgb=GRIS; r.font.size=Pt(11)
p=d.add_paragraph(); r=p.add_run("Adrián Álvaro López Pascual · Trabajo de Tesis 2"); r.font.color.rgb=GRIS; r.font.size=Pt(10)
d.add_paragraph()
p=d.add_paragraph(); r=p.add_run("Cómo usar este documento: ")
r.bold=True
p.add_run("cada respuesta está pensada para durar 30–60 s. No la memorices palabra por palabra; entiende la idea y di el número clave. Si no sabes algo, no inventes: reconócelo y remite a trabajo futuro (el jurado valora la honestidad).")
d.add_paragraph()

# ========== 1. TÉCNICAS DE FONDO ==========
H1("1. Preguntas técnicas de fondo")

Q(1,"¿Por qué eligió 802.11ac y no una red celular privada LTE/5G?")
A("Por tres razones concretas del caso de estudio: (1) los equipos documentados del proyecto ya son 802.11ac industrial (nodos Rajant Hawk y Cardinal), (2) no requiere licenciamiento de espectro —opera en 5 GHz de uso libre—, y (3) la capacidad de 802.11ac (hasta 866 Mbps por radio) sobra para el tráfico agregado de un LHD. LTE/5G privado es una alternativa válida como evolución futura, pero implica mayor complejidad de infraestructura y regulación. Lo declaro así en el Capítulo 3.")
TIP("Si insisten en 5G: reconoce que es superior en movilidad masiva, pero para UN vehículo en un corredor acotado, 802.11ac es suficiente y más simple.")

Q(2,"Su simulación es determinista. ¿No es poco realista no incluir el desvanecimiento (shadowing)?")
A("Es una decisión metodológica deliberada, no una omisión. Intenté incluir shadowing log-normal dentro de NS-3, pero desestabiliza el roaming 802.11 (genera ping-pong artificial). Por eso separé los análisis: los KPIs de red se calculan con el modelo determinista y reproducible, y la variabilidad ±σ se analiza aparte en el mapa de cobertura y el contraste con TamoGraph. Es un enfoque estándar en tesis. Además, el modelo es conservador: el equipo real de malla mejora estos resultados.")

Q(3,"¿Cómo validó su modelo de propagación? ¿Tiene mediciones de campo?")
A("No presento mediciones de campo propias —lo declaro explícitamente—. La validación es de diseño, no experimental. El modelo two-slope está calibrado contra el reporte de site survey TamoGraph del proyecto, que sí es una medición real del entorno. El contraste muestra que mi modelo predice niveles de señal dentro del rango observado en ese survey. La medición punto a punto propia es la primera recomendación de trabajo futuro.")
TIP("Clave: nunca sobre-afirmes. Di 'validación de diseño' y remite el campo a trabajo futuro. El jurado premia esa honestidad.")

Q(4,"¿Por qué el vehículo no se conecta siempre al punto de acceso más cercano?")
A("Es diseño intencional. Perseguir el AP más cercano genera reasociaciones constantes (ping-pong) que producen micro-cortes en el enlace. El diseño usa roaming estable tipo make-before-break, como el mesh Rajant InstaMesh real: el vehículo mantiene su AP mientras el enlace sea bueno. Y lo demuestro con datos: el enlace asociado nunca baja de −72.1 dBm en todo el recorrido, con 9.9 dB de margen sobre el umbral usable. Cuando el traspaso sí ocurre, dura menos de 1 milisegundo.")

Q(5,"¿Cómo modeló la propagación dentro de las galerías? La señal, ¿atraviesa la roca?")
A("No. El supuesto físico es que a 5 GHz la señal NO atraviesa el pilar de roca de ~26 m entre galerías —la atenuación de la roca es de decenas de dB por metro—. La señal viaja por las labores abiertas: a lo largo de la galería en línea de vista, y entre galerías rodeando por los cruceros, con una penalización de 10 dB por cada galería cruzada. Es un supuesto conservador y coherente con la física de propagación en túneles.")

Q(6,"¿Qué es el modelo two-slope y por qué lo usó?")
A("Es un modelo de pérdida de trayecto con dos pendientes: cerca del transmisor (campo cercano) coexisten múltiples modos que refuerzan la señal, con exponente n1=1.9; más allá de un punto de quiebre a 40 m, solo sobreviven los modos dominantes y la atenuación crece, con n2=3.4. Es el modelo estándar para propagación en túneles y minas, documentado por Sun y Akyildiz. Lo calibré con los datos del TamoGraph.")

# ========== 2. METODOLOGÍA ==========
H1("2. Metodología y diseño")

Q(7,"¿Qué metodología de diseño siguió?")
A("Apliqué Design Thinking, un proceso centrado en el usuario: (1) empatizar con el operador y el riesgo que enfrenta; (2) definir los requisitos y KPIs; (3) idear y comparar alternativas tecnológicas; (4) prototipar mediante simulación NS-3 sobre la geometría real; (5) validar contra el site survey. El proceso partió de la persona —la seguridad del operador— y avanzó iterativamente hasta un prototipo validado.")
TIP("MENCIONA 'Design Thinking' sí o sí — es criterio de la rúbrica del profesor.")

Q(8,"¿Por qué simuló en NS-3 y no en otra herramienta?")
A("NS-3 es un simulador de red a nivel de paquetes, de código abierto y estándar académico. Me permite representar los tres flujos reales de teleoperación (vídeo, comandos, telemetría), la priorización QoS 802.11e/WMM, la movilidad del vehículo y el roaming entre APs —cosas que un cálculo de presupuesto de enlace estático no captura—. Complementé con Python para el modelamiento radioeléctrico y las figuras.")

Q(9,"¿Cuántas veces corrió la simulación? ¿Cómo garantiza que los resultados no son casualidad?")
A("Ejecuté 18 simulaciones de 300 segundos cada una. El escenario de operación se corrió con 10 semillas aleatorias independientes, y reporto los resultados como media e intervalo de confianza al 95 %. Eso da respaldo estadístico: los KPIs no son de una corrida afortunada, sino consistentes en las 10. Además incluí escenarios de referencia, de estrés y de traspaso.")

Q(10,"¿Qué es una 'semilla' y por qué usó 10?")
A("La semilla inicializa el generador de números aleatorios del simulador; cada semilla produce una realización estadísticamente independiente del mismo escenario. Usar 10 y promediar con intervalo de confianza es la práctica estándar para separar el resultado real del ruido aleatorio de una sola corrida.")

# ========== 3. RESULTADOS ==========
H1("3. Resultados y KPIs")

Q(11,"¿Cuáles son sus resultados principales?")
A("Todos los indicadores se cumplen con margen: latencia de comandos 3.04 ms (límite 20), latencia de vídeo extremo a extremo 35.9 ms (límite 150), jitter P95 0.28 ms (límite 10), throughput de vídeo 40.1 Mbps (mínimo 38), pérdida de comandos 0.06 % y disponibilidad del 100 %. El traspaso peor caso dura 0.91 ms frente a los 150 ms permitidos. Todo con respaldo de 10 semillas.")
TIP("Ten estos 3 números en la punta de la lengua: 3 ms comandos, 36 ms vídeo, 100% disponibilidad.")

Q(12,"El jitter de 0.28 ms parece demasiado bajo. ¿Es creíble?")
A("Sí, y no es un error de medición. Un enlace sin congestión produce jitter mínimo —es justamente lo deseable para teleoperación—. Lo mido con resolución fina de 0.05 ms para no redondearlo artificialmente. El vídeo se modela con tasa variable (VBR) tipo H.264, que introduce el jitter realista de codificación; aun así es muy bajo porque la red va holgada.")

Q(13,"En el escenario de estrés de vídeo a 50 Mbps, ¿la red falla?")
A("No falla: mantiene todos los criterios de aceptación. Lo que ocurre es que la latencia de comandos sube de 3 a 6.8 ms —sigue muy por debajo del límite de 20—. Eso demuestra dos cosas: que hay margen de dimensionamiento (la red aguanta 25 % más de lo nominal) y que la priorización WMM funciona: ante sobrecarga, degrada primero la latencia del tráfico priorizado, no las pérdidas.")

Q(14,"¿Qué pasa si se cae un punto de acceso?")
A("No lo modelé como escenario de falla —lo declaro como limitación—. El diseño tiene redundancia por densidad: 12 APs con celdas solapadas, de modo que la caída de uno deja cobertura por los vecinos. Cuantificar la resiliencia ante fallas de infraestructura es trabajo futuro explícito. El backbone de fibra en anillo también aporta redundancia física.")

# ========== 4. ECONÓMICAS Y CONTEXTO ==========
H1("4. Económicas, regulatorias y de contexto")

Q(15,"¿Cuánto cuesta implementar su solución?")
A("No presento una cifra monetaria porque requiere cotizaciones vigentes de fabricantes, y prefiero no inventar números. Sí entrego la estructura de costos: es una inversión incremental sobre infraestructura que ya existe en la mina —el backbone de fibra ya está—, concentrada en los 12 equipos de acceso y su integración. El retorno viene de reducir accidentes, ganar continuidad operativa y reutilizar la red existente. La cuantificación es la recomendación económica de trabajo futuro.")
TIP("Si presionan por un número: 'preferí no fabricar cifras sin cotización; la estructura y los mecanismos de retorno están, la cuantificación es el paso siguiente con planeamiento de la mina'.")

Q(16,"¿Su solución cumple la normativa peruana?")
A("Sí. La banda de 5 GHz es de uso libre según la normativa del MTC, así que no requiere licencia de espectro. En seguridad minera, se alinea con el D.S. 024-2016-EM: la teleoperación es precisamente un control de ingeniería que retira al trabajador del peligro, que es lo que exige la jerarquía de controles. Y el tratamiento del vídeo se rige por la Ley 29733 de protección de datos personales.")

Q(17,"¿Por qué esta tesis es importante para el Perú?")
A("Porque la minería subterránea peruana registra accidentes fatales cada año, y muchos ocurren en el frente de operación donde va el operador del LHD. Demostrar que una red basada en estándares abiertos puede sacar a esa persona de la zona de riesgo aporta un camino replicable y de bajo costo hacia una minería más segura. Es tecnología al servicio de la vida del trabajador.")

# ========== 5. CRÍTICAS Y LÍMITES ==========
H1("5. Preguntas críticas y limitaciones")

Q(18,"¿No es una limitación grande que sea solo simulación, sin implementación real?")
A("Es el alcance declarado: una tesis de gabinete basada en prototipado conceptual. No pretendo certificar una red desplegada. Lo que sí logro es un diseño trazable y reproducible, validado contra un site survey real, que reduce el riesgo técnico de una implementación posterior. Declaro con transparencia qué demuestra la simulación y qué debe confirmar el campo. Esa honestidad metodológica es parte del rigor del trabajo.")
TIP("Esta es la pregunta más probable. Respóndela con seguridad, no a la defensiva. 'Alcance declarado' es la frase clave.")

Q(19,"¿Modeló un solo LHD? ¿Y si hay varios vehículos?")
A("Sí, el alcance es un vehículo, como está definido desde el Capítulo 1. La arquitectura es modular y escalable, pero incorporar múltiples vehículos exige recalcular capacidad, interferencia co-canal y reuso de frecuencias —lo dejo como trabajo futuro explícito—. Para el objetivo de esta tesis, un LHD teleoperado es el caso representativo.")

Q(20,"Si tuviera que rehacer la tesis, ¿qué cambiaría?")
A("Priorizaría conseguir mediciones de campo propias del nivel para calibrar el modelo con datos primeros, y agregaría un método de validación independiente como ray-tracing 3D para contrastar. También ampliaría a múltiples vehículos. Son justamente mis recomendaciones de trabajo futuro: sé exactamente dónde puede crecer este trabajo.")
TIP("Nunca digas 'nada, está perfecta'. Mostrar que conoces tus límites es señal de madurez y el jurado lo valora.")

Q(21,"¿Qué aprendió con esta tesis?")
A("A integrar tres mundos que en la carrera se ven separados: propagación radioeléctrica, redes de datos y análisis de idoneidad. Aprendí que un buen diseño no es solo que 'funcione en la simulación', sino que cada número sea trazable y cada supuesto esté declarado. Y aprendí a defender decisiones con datos, no con opiniones. [Personaliza esta con tu experiencia real.]")

d.save(r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\presentacion\banco_preguntas_jurado.docx")
print("Documento Word generado: 21 preguntas")

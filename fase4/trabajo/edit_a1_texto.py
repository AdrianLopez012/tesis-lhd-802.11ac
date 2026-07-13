# -*- coding: utf-8 -*-
# ETAPA A1 — Actualización del texto del Cap. 3: v8.2 -> v3-REAL
# Cada reemplazo verifica que el párrafo empiece con el texto esperado (seguridad:
# si el índice no coincide, NO se toca y se reporta). Preserva el estilo del párrafo.
import docx, sys
sys.stdout.reconfigure(encoding="utf-8")

SRC = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\tesis_original.docx"
DST = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"

# {indice_parrafo: (prefijo_esperado, texto_nuevo)}
R = {
716: ("El diseño utiliza como insumos",
"El diseño utiliza como insumos el plano de comunicaciones del nivel NV1640, la información técnica de los equipos industriales considerados y el reporte TamoGraph disponible para el área BC 428 NV1640. El modelo ns-3 representa la zona de producción del nivel con su geometría real —tres galerías de producción paralelas de tipo El Teniente unidas por cruceros, con sus puntos de extracción (drawpoints) y piques de traspaso—, el recorrido real del ciclo de operación del LHD, zonas NLOS y tres clases de tráfico: video, comandos y telemetría. Esta delimitación permite que los resultados sean interpretados de forma trazable y prudente, reservando el análisis integral de idoneidad para el Capítulo 4."),

727: ("La diferenciación del PLR de comandos",
"La diferenciación del PLR de comandos es necesaria para interpretar correctamente los resultados. El objetivo de confiabilidad en enlace estable (≤ 0.1 %) se mantiene como referencia exigente y el criterio operacional de movilidad (≤ 0.5 %) como umbral de aceptación del diseño. En la versión vigente del prototipo (v3-REAL), el escenario de operación con diez semillas independientes arroja un PLR medio de comandos de 0.06 %, de modo que el diseño cumple incluso la meta estricta en promedio durante la movilidad simulada. Esta evidencia no constituye una validación de seguridad funcional ni sustituye pruebas de campo."),

739: ("La solución también debe ser mantenible",
"La solución también debe ser mantenible y auditable. En una aplicación asociada a seguridad operacional, no resulta suficiente mostrar un valor promedio favorable; es indispensable conservar registros, identificar el escenario evaluado, declarar umbrales y explicar las limitaciones del modelo. Este criterio orienta la selección de salidas CSV/XML y registros de posición y asociación en la versión vigente del prototipo, cuyos parámetros provienen de una fuente única de configuración."),

741: ("El plano documentado del nivel NV1640",
"El plano documentado del nivel NV1640 presenta la infraestructura de comunicaciones completa del área: cinco AP Hawk, siete AP Cardinal, tres nodos de red y la trayectoria del anillo de fibra óptica. A diferencia de las versiones preliminares del prototipo, la simulación vigente modela esta arquitectura de forma íntegra: los doce AP se ubican en sus posiciones reales según el plano y la zona de producción se representa con su geometría real, por lo que los resultados son interpretables directamente sobre la infraestructura documentada [26]."),

742: ("El prototipo v8.2 representa",
"El prototipo v3-REAL representa la zona de producción con su geometría real de tipo El Teniente: tres galerías de producción paralelas de 134.85 m separadas 25.98 m, unidas por cruceros superior e inferior, con veintidós puntos de extracción (drawpoints) y dos piques de traspaso para la descarga. El recorrido simulado corresponde al ciclo real de operación del LHD —carga en un drawpoint y descarga en un pique de traspaso, con maniobras de aproximación y reversa—, que cubre 377.7 m por ciclo en 196.7 s a la velocidad nominal de 2.22 m/s, incluyendo las pausas de carga y descarga. La rampa de acceso al nivel se excluye del recorrido teleoperado por tratarse de una vía de conducción manual fuera de la zona de cobertura dedicada."),

748: ("El prototipo adopta un modelo two-slope",
"El prototipo adopta un modelo two-slope con exponente de pérdida n1 = 1.9 en la región inicial, n2 = 3.4 después de un breakpoint de 40 m, pérdidas de sistema de 9.4 dB y una penalización NLOS de 10 dB por cada galería cruzada. La distancia radioeléctrica se calcula sobre la ruta de túnel: la señal recorre las labores abiertas (galerías y cruceros) y no atraviesa el pilar de roca de aproximadamente 26 m que separa las galerías paralelas, supuesto conservador coherente con la propagación a 5 GHz en roca. Todos los parámetros del modelo tienen una fuente única de configuración, desde la cual se generan automáticamente tanto el código de simulación como las figuras de análisis, garantizando que todos los artefactos del capítulo utilicen exactamente la misma fórmula."),

751: ("El prototipo conceptual se implementa",
"El prototipo conceptual se implementa en ns-3.40 mediante el archivo lhd-teleop-v3-real.cc, cuya geometría y recorrido se generan automáticamente desde la fuente única de datos del plano. Su propósito es evaluar la arquitectura y los flujos definidos, no emular todos los mecanismos propietarios de un producto industrial. En el prototipo, los nodos fijos se conectan a un backbone cableado abstracto mediante Bridge L2, mientras el enlace inalámbrico representa la conectividad entre la infraestructura de la zona de producción y el radio embarcado del LHD (tipo Cardinal con antena HELI-40)."),

752: ("La versión v8.2 incorpora",
"La versión vigente incorpora la geometría real de la zona de producción, el recorrido real del ciclo de operación, distancia radioeléctrica por ruta de túnel, penalización NLOS por galería cruzada, pérdidas de sistema de 9.4 dB, configuración IEEE 802.11ac de 5 GHz/40 MHz/MIMO 2x2, tráfico de video de tasa variable (VBR) tipo H.264, roaming estable de tipo make-before-break coherente con el mesh industrial considerado, y registros de posición y asociación. En consecuencia, supera las simplificaciones geométricas de las versiones previas —que modelaban una galería recta con ramales—, cuya evidencia se conserva únicamente como trazabilidad histórica del proceso de diseño."),

766: ("La evaluación comparativa utiliza",
"La evaluación comparativa utiliza tanto criterios físicos como de servicio. En lo físico, interesa representar la geometría real de las galerías, las pérdidas de sistema y los cambios LOS/NLOS. En lo funcional, interesa sostener el video nominal, proteger comandos y mantener telemetría. La Tabla 16 resume los parámetros del modelo utilizado en la versión v3-REAL."),

768: ("La Figura 9 representa la geometría",
"La Figura 9 representa la geometría utilizada en la simulación: la zona de producción real con sus tres galerías, cruceros, drawpoints y piques de traspaso, y los doce AP del plano —cinco Hawk y siete Cardinal— en sus posiciones reales. A diferencia de las versiones preliminares, la correspondencia entre el modelo y el plano general es directa, por lo que los resultados de cobertura y movilidad se interpretan sin traducción intermedia sobre la infraestructura documentada."),

770: ("Figura 9. Submodelo geométrico",
"Figura 9. Geometría real de la zona de producción y ubicación de los AP en ns-3 v3-REAL."),

771: ("Fuente: Elaboración propia con base en el código y los parámetros del prototipo v8.2.",
"Fuente: Elaboración propia con base en la geometría y los parámetros del prototipo v3-REAL."),

774: ("La selección se fundamenta en cuatro razones",
"La selección se fundamenta en cuatro razones: compatibilidad con los equipos técnicos documentados; capacidad para modelar video, comandos y telemetría; posibilidad de representar la geometría y movilidad reales en ns-3; y trazabilidad de parámetros y resultados. Los siete AP Cardinal se conservan como refuerzo de cobertura en cruceros y zonas de maniobra, y el dimensionamiento del conjunto se sustenta en la batería de escenarios de la versión vigente: operación multi-semilla, referencia estática, estrés de tráfico, estrés de velocidad y traspaso forzado."),

777: ("La arquitectura física se comprende en dos niveles",
"La arquitectura física se comprende en dos niveles. El primero es la arquitectura general documentada del nivel NV1640, que incluye anillo de fibra, nodos de red y el conjunto de AP Hawk y Cardinal mostrado en la Figura 7. El segundo es su representación en el prototipo: un backbone cableado de baja latencia, los cinco nodos Hawk en las galerías, los siete nodos Cardinal en cruceros y zonas de refuerzo, y un radio embarcado de tipo Cardinal en el LHD, todos en las posiciones del plano."),

784: ("El video se modela como un flujo UDP nominal de 40 Mbps",
"El video se modela como un flujo UDP de tasa variable (VBR) tipo H.264 con media de 40 Mbps: la fuente emite cuadros a 30 fps con tamaño variable alrededor de la media (acotado a ±30 %, representando cuadros I frente a P/B), fragmentados en paquetes de hasta 1400 bytes espaciados dentro del intervalo de cada cuadro, y se adiciona un retardo de códec de 35 ms para calcular su latencia extremo a extremo. Los comandos se modelan como UDP de 0.5 Mbps con paquetes de 128 bytes, priorizados por su relevancia operacional. La telemetría se modela como un flujo continuo de 0.1 Mbps con paquetes de 200 bytes. Estas tasas representan perfiles funcionales para la evaluación y no sustituyen la especificación final de cámaras, codificadores o controladores del LHD."),

788: ("La resiliencia física se favorece",
"La resiliencia física se favorece mediante el backbone óptico documentado y la ubicación de nodos de refuerzo en zonas críticas. La simulación aporta evidencia del margen del diseño mediante los escenarios de estrés (video a 50 Mbps y velocidad de 4 m/s) y de la continuidad del enlace mediante el escenario dedicado de traspaso multi-semilla, pero no modela fallas de energía, corte de fibra, ciberataques ni procedimientos de recuperación; estos aspectos deberán incorporarse en la validación integral y en los procedimientos de mantenimiento."),
}

d = docx.Document(SRC)
ok, fail = 0, []
for idx, (pref, nuevo) in R.items():
    p = d.paragraphs[idx]
    actual = p.text.strip()
    if not actual.startswith(pref[:60]):
        fail.append((idx, pref[:40], actual[:40]))
        continue
    # preservar estilo: escribir en el primer run y vaciar el resto
    if p.runs:
        p.runs[0].text = nuevo
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.text = nuevo
    ok += 1

d.save(DST)
print(f"reemplazos OK: {ok}/{len(R)}")
for f in fail:
    print("NO COINCIDE:", f)

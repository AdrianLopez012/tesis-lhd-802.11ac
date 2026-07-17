// Sustentación — deck v2 "excelente". Estructura del profesor (3'+3'+5'+7'+cierre),
// sandwich oscuro/claro, evidencia visual en cada slide, video del LHD embebido.
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
const DIR = "C:/Users/Adrian Lopez/Documents/tesis_proyecto/fase4/presentacion/";

// paleta PUCP: azul dominante, celeste apoyo, blanco; oscuro para portada/cierre
const AZUL = "0033A0", OSCURO = "021740", CELESTE = "5AA0DC", HIELO = "EAF2FB",
      INK = "1A2733", GRIS = "5B6670", BLANCO = "FFFFFF", VERDE = "1E7A46", AMBAR = "B7791F";
const F_H = "Cambria", F_B = "Calibri";

function tag(s, txt) {   // etiqueta de tiempo, esquina superior derecha
  s.addText(txt, { x: 10.6, y: 0.28, w: 2.45, h: 0.4, align: "right",
    fontFace: F_B, fontSize: 12, color: CELESTE, bold: true });
}
function titulo(s, txt, color = AZUL) {
  s.addText(txt, { x: 0.75, y: 0.55, w: 10.2, h: 0.85, fontFace: F_H,
    fontSize: 34, color, bold: true });
}
function card(s, x, y, w, h, fill = HIELO) {
  s.addShape(p.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.03,
    fill: { color: fill }, line: { color: "C7D3E2", width: 0.75 } });
}

// ============ 1 · CARÁTULA (oscura) ============
let s = p.addSlide(); s.background = { color: OSCURO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
s.addImage({ path: DIR + "mina_realista_3d.png", x: 7.1, y: 1.6, w: 5.6, h: 4.3, rounding: true, transparency: 18 });
s.addText("PONTIFICIA UNIVERSIDAD CATÓLICA DEL PERÚ", { x: 0.85, y: 0.7, w: 8, h: 0.4,
  fontFace: F_B, fontSize: 14, color: CELESTE, bold: true, charSpacing: 3 });
s.addText("Facultad de Ciencias e Ingeniería · Ingeniería de las Telecomunicaciones",
  { x: 0.85, y: 1.12, w: 7.5, h: 0.4, fontFace: F_B, fontSize: 13, color: "B9CCE8" });
s.addText("Diseño de una red IEEE 802.11ac para la teleoperación de un vehículo LHD en la extracción de mineral en galerías subterráneas",
  { x: 0.85, y: 2.15, w: 6.1, h: 2.5, fontFace: F_H, fontSize: 29, color: BLANCO, bold: true, lineSpacingMultiple: 1.12 });
s.addText([
  { text: "Adrián Álvaro López Pascual\n", options: { fontSize: 17, color: BLANCO, bold: true } },
  { text: "Asesor: Dr. Pastor David Chávez Muñoz", options: { fontSize: 14, color: "B9CCE8" } },
], { x: 0.85, y: 5.15, w: 6, h: 0.95, fontFace: F_B, lineSpacingMultiple: 1.25 });
s.addText("Sustentación · Trabajo de Tesis 2 · 2026", { x: 0.85, y: 6.45, w: 6, h: 0.4,
  fontFace: F_B, fontSize: 12, color: CELESTE });
s.addNotes("Saludo al jurado. Nombre completo, título de la tesis, asesor. 20 segundos, con calma. La imagen es el modelo 3D real del nivel NV1640 construido en MATLAB.");

// ============ 2 · ¿DE QUÉ TRATA? ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "¿De qué trata este trabajo?");
s.addImage({ path: DIR + "escena_mina_3d.png", x: 6.9, y: 1.5, w: 5.9, h: 4.4 });
s.addText("Zona de producción NV1640 (Nexa Cerro Lindo): cobertura calculada, recorrido real del vehículo y patrón de la antena.",
  { x: 6.9, y: 6.0, w: 5.9, h: 0.65, fontFace: F_B, fontSize: 11, italic: true, color: GRIS, align: "center" });
const QUE = [
  ["Teleoperar un cargador LHD desde superficie", "El operador sale de la zona de riesgo; el vehículo se conduce por vídeo en tiempo real, comandos y telemetría."],
  ["Con una red IEEE 802.11ac diseñada para la mina", "12 puntos de acceso sobre un backbone de fibra, planificados sobre la geometría real de las galerías."],
  ["Validada por simulación con rigor estadístico", "Modelo NS-3 sobre el trazado real: 18 ejecuciones, 10 semillas independientes, todos los KPIs cumplen."],
];
QUE.forEach((q, i) => {
  const y = 1.6 + i * 1.62;
  card(s, 0.75, y, 5.8, 1.42, HIELO);
  s.addText(q[0], { x: 1.05, y: y + 0.16, w: 5.25, h: 0.5, fontFace: F_B, fontSize: 14.5, bold: true, color: AZUL });
  s.addText(q[1], { x: 1.05, y: y + 0.64, w: 5.25, h: 0.72, fontFace: F_B, fontSize: 11.5, color: INK, lineSpacingMultiple: 1.05 });
});
s.addNotes("Descripción breve obligatoria: qué es y qué logra, sin entrar a detalles. 40 segundos. 'Esta tesis diseña y valida la red que permite sacar al operador del frente de riesgo sin detener la producción.'");

// ============ 3 · MOTIVACIÓN (3 min) ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "¿Por qué esta tesis?");
card(s, 0.75, 1.6, 5.9, 2.5, HIELO);
s.addText("Una motivación con raíz personal", { x: 1.05, y: 1.78, w: 5.3, h: 0.42, fontFace: F_B, fontSize: 14, bold: true, color: AZUL });
s.addText("Nací en una tierra donde la minería marca la vida de las familias. Crecí sabiendo lo que significa que alguien entre a una labor subterránea — y esta carrera me dio la forma de devolver algo: usar las telecomunicaciones para cuidar a esas personas.",
  { x: 1.05, y: 2.24, w: 5.35, h: 1.7, fontFace: F_H, fontSize: 13.5, italic: true, color: INK, lineSpacingMultiple: 1.12 });
card(s, 0.75, 4.35, 5.9, 2.3, "FDF3E7");
s.addText("El dato que no se puede ignorar", { x: 1.05, y: 4.55, w: 5.3, h: 0.45, fontFace: F_B, fontSize: 14, bold: true, color: AMBAR });
s.addText("Cada año se registran víctimas mortales en la minería peruana; una parte importante ocurre en el frente de operación, justo donde trabaja el operador del LHD (OSINERGMIN).",
  { x: 1.05, y: 5.02, w: 5.35, h: 1.45, fontFace: F_B, fontSize: 12.5, color: INK, lineSpacingMultiple: 1.12 });
card(s, 7.0, 1.6, 5.55, 5.05, OSCURO);
s.addText("La oportunidad de ingeniería", { x: 7.35, y: 1.85, w: 4.9, h: 0.5, fontFace: F_B, fontSize: 14, bold: true, color: CELESTE });
s.addText([
  { text: "Retirar a la persona del riesgo ", options: { bold: true, color: BLANCO } },
  { text: "sin detener la extracción: teleoperación.\n\n", options: { color: "D7E4F5" } },
  { text: "El eslabón crítico es la red", options: { bold: true, color: BLANCO } },
  { text: ": vídeo en tiempo real, comandos de baja latencia y telemetría continua dentro de galerías con curvas, polvo y roca.\n\n", options: { color: "D7E4F5" } },
  { text: "Mi tesis demuestra que ese eslabón es viable ", options: { bold: true, color: CELESTE } },
  { text: "con un estándar abierto y equipos industriales disponibles.", options: { color: "D7E4F5" } },
], { x: 7.35, y: 2.45, w: 4.85, h: 3.9, fontFace: F_B, fontSize: 14, lineSpacingMultiple: 1.14 });
s.addNotes("3 MINUTOS. Empezar con la historia personal (genuina, 45 s) — el vínculo con la minería y la seguridad del trabajador. Luego el dato duro de OSINERGMIN. Cerrar con la oportunidad técnica: 'la teleoperación existe; lo que falta demostrar es que la RED la sostiene en una mina real. Eso hice.'");

// ============ 4 · OBJETIVOS (3 min) ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "Objetivos");
card(s, 0.75, 1.55, 11.85, 1.25, AZUL);
s.addText([
  { text: "Objetivo general:  ", options: { bold: true, color: CELESTE } },
  { text: "diseñar una red IEEE 802.11ac que soporte la teleoperación de un vehículo LHD en las galerías del nivel NV1640, cumpliendo requisitos de latencia, capacidad y disponibilidad con evidencia verificable.", options: { color: BLANCO } },
], { x: 1.05, y: 1.72, w: 11.25, h: 0.95, fontFace: F_B, fontSize: 14.5, lineSpacingMultiple: 1.1, valign: "middle" });
const OBJ = [
  ["1", "Caracterizar el canal de propagación en galerías (modelo two-slope calibrado)"],
  ["2", "Diseñar la arquitectura física y lógica (backbone óptico + malla de acceso)"],
  ["3", "Dimensionar radio y antenas con equipos industriales reales"],
  ["4", "Definir políticas de QoS y movilidad (WMM, roaming estable)"],
  ["5", "Validar el desempeño extremo a extremo por simulación NS-3"],
  ["6", "Evaluar idoneidad técnica, económica, regulatoria y ética"],
];
OBJ.forEach((o, i) => {
  const col = i % 2, fila = Math.floor(i / 2);
  const x = 0.75 + col * 6.05, y = 3.15 + fila * 1.18;
  card(s, x, y, 5.8, 1.0, HIELO);
  s.addText(o[0] + ".", { x: x + 0.25, y: y + 0.1, w: 0.55, h: 0.82, fontFace: F_H, fontSize: 20, bold: true, color: AZUL, valign: "middle" });
  s.addText(o[1], { x: x + 0.85, y: y + 0.1, w: 4.8, h: 0.82, fontFace: F_B, fontSize: 12.5, color: INK, valign: "middle", lineSpacingMultiple: 1.02 });
});
s.addNotes("3 MINUTOS. Leer el objetivo general con énfasis en 'evidencia verificable'. Los 6 específicos en 20 segundos cada uno máximo, conectándolos: canal → arquitectura → radio → QoS → validación → idoneidad. Son la columna vertebral de los capítulos.");

// ============ 5 · METODOLOGÍA: DESIGN THINKING (5 min) ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "Metodología: Design Thinking aplicado a ingeniería");
const DT = [
  ["Empatizar", "El operador y su exposición al riesgo en el frente"],
  ["Definir", "Requisitos y KPIs medibles por flujo (vídeo, mando, telemetría)"],
  ["Idear", "Comparación multicriterio de tecnologías (RSL método Kitchenham)"],
  ["Prototipar", "Modelo NS-3 sobre la geometría real + MATLAB"],
  ["Validar", "Contraste con site survey TamoGraph + batería multi-semilla"],
];
DT.forEach((d, i) => {
  const x = 0.75 + i * 2.47;
  card(s, x, 1.7, 2.27, 2.6, HIELO);
  s.addText(String(i + 1), { x, y: 1.92, w: 2.27, h: 0.6, align: "center", fontFace: F_H, fontSize: 26, bold: true, color: CELESTE });
  s.addText(d[0], { x, y: 2.62, w: 2.27, h: 0.42, align: "center", fontFace: F_B, fontSize: 14.5, bold: true, color: AZUL });
  s.addText(d[1], { x: x + 0.14, y: 3.06, w: 2.0, h: 1.15, align: "center", fontFace: F_B, fontSize: 10.3, color: INK, lineSpacingMultiple: 1.03 });
  if (i < 4) s.addText("›", { x: x + 2.2, y: 2.5, w: 0.34, h: 0.6, fontFace: F_H, fontSize: 22, color: GRIS, margin: 0, align: "center" });
});
card(s, 0.75, 4.75, 5.85, 1.95, OSCURO);
s.addText("Herramientas", { x: 1.05, y: 4.95, w: 5, h: 0.4, fontFace: F_B, fontSize: 13, bold: true, color: CELESTE });
s.addText([
  { text: "NS-3.40", options: { bold: true, color: BLANCO } }, { text: " simulación de red a nivel de paquetes  ·  ", options: { color: "D7E4F5" } },
  { text: "MATLAB R2024b", options: { bold: true, color: BLANCO } }, { text: " modelamiento del canal, antenas y entorno 3D  ·  ", options: { color: "D7E4F5" } },
  { text: "TamoGraph", options: { bold: true, color: BLANCO } }, { text: " site survey real de contraste  ·  ", options: { color: "D7E4F5" } },
  { text: "Python", options: { bold: true, color: BLANCO } }, { text: " fuente única de parámetros y trazabilidad", options: { color: "D7E4F5" } },
], { x: 1.05, y: 5.38, w: 5.3, h: 1.2, fontFace: F_B, fontSize: 12, lineSpacingMultiple: 1.18 });
card(s, 6.95, 4.75, 5.6, 1.95, HIELO);
s.addText("Rigor de la validación", { x: 7.25, y: 4.95, w: 5, h: 0.4, fontFace: F_B, fontSize: 13, bold: true, color: AZUL });
s.addText([
  { text: "18 ejecuciones de 300 s  ·  10 semillas independientes\n", options: { bold: true, color: INK } },
  { text: "Resultados como media ± intervalo de confianza al 95 %. Escenarios de operación, referencia, estrés y traspaso.", options: { color: INK } },
], { x: 7.25, y: 5.38, w: 5.05, h: 1.2, fontFace: F_B, fontSize: 12, lineSpacingMultiple: 1.15 });
s.addNotes("5 MINUTOS. MENCIONAR 'Design Thinking' explícitamente (rúbrica). Recorrer los 5 pasos con 30-40 s c/u anclando cada uno a lo que se hizo: empatizar (operador), definir (KPIs), idear (RSL Kitchenham + multicriterio), prototipar (NS-3 con geometría real), validar (TamoGraph + 10 semillas). Cerrar con el rigor estadístico: 'ningún número de esta tesis sale de una sola corrida'.");

// ============ 6 · EL ENTORNO REAL + VIDEO ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "El diseño vive en la geometría real de la mina");
s.addImage({ path: DIR + "plano_nv1640_pro.png", x: 0.75, y: 1.6, w: 6.0, h: 4.5 });
s.addText("Plano del nivel NV1640 (block caving tipo El Teniente): galerías, cruceros, drawpoints y los 12 AP.",
  { x: 0.75, y: 6.15, w: 6.0, h: 0.6, fontFace: F_B, fontSize: 11, italic: true, color: GRIS, align: "center" });
try {
  s.addMedia({ type: "video", path: DIR + "lhd_recorrido_3d.mp4", x: 7.15, y: 1.6, w: 5.4, h: 3.05 });
} catch (e) {
  s.addImage({ path: DIR + "mina_realista_3d.png", x: 7.15, y: 1.6, w: 5.4, h: 3.05 });
}
s.addText("Video: recorrido del LHD teleoperado — animación 3D con datos reales de la simulación (AP servidor y RSSI en vivo)",
  { x: 7.15, y: 4.75, w: 5.4, h: 0.6, fontFace: F_B, fontSize: 11, italic: true, color: GRIS, align: "center" });
card(s, 7.15, 5.5, 5.4, 1.15, HIELO);
s.addText([
  { text: "La señal no atraviesa la roca. ", options: { bold: true, color: AZUL } },
  { text: "El modelo respeta la física del túnel: la cobertura viaja por las labores abiertas, con penalización por cada galería cruzada.", options: { color: INK } },
], { x: 7.4, y: 5.62, w: 4.95, h: 0.95, fontFace: F_B, fontSize: 11.5, lineSpacingMultiple: 1.08, valign: "middle" });
s.addNotes("Inicio de los 7 minutos de resultados. Mostrar el plano real 15 s. REPRODUCIR EL VIDEO (clic) mientras se explica: 'el vehículo recorre el ciclo real de operación; arriba se ve el AP que lo sirve y su nivel de señal — datos de la simulación, no una caricatura'. Si el video no reproduce, seguir con la imagen sin perder ritmo.");

// ============ 7 · KPIs (oscura, números grandes) ============
s = p.addSlide(); s.background = { color: OSCURO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
s.addText("Resultados: todos los KPIs se cumplen", { x: 0.75, y: 0.6, w: 10, h: 0.8, fontFace: F_H, fontSize: 34, bold: true, color: BLANCO });
s.addText("18 ejecuciones · 10 semillas independientes · media ± intervalo de confianza al 95 %",
  { x: 0.78, y: 1.38, w: 10, h: 0.45, fontFace: F_B, fontSize: 13, italic: true, color: CELESTE });
const KPI = [
  ["3.04 ms", "OWD comandos", "requisito ≤ 20 ms"],
  ["35.9 ms", "Latencia vídeo E2E", "requisito ≤ 150 ms"],
  ["0.28 ms", "Jitter P95", "requisito ≤ 10 ms"],
  ["40.1 Mbps", "Throughput vídeo", "requisito ≥ 38 Mbps"],
  ["0.06 %", "PLR comandos", "requisito ≤ 0.5 %"],
  ["100 %", "Disponibilidad", "requisito ≥ 99.9 %"],
];
KPI.forEach((k, i) => {
  const col = i % 3, fila = Math.floor(i / 3);
  const x = 0.75 + col * 4.03, y = 2.1 + fila * 2.35;
  s.addShape(p.ShapeType.roundRect, { x, y, w: 3.78, h: 2.1, rectRadius: 0.1, fill: { color: "0A2B66" }, line: { color: "1D4B99", width: 1 } });
  s.addText(k[0], { x, y: y + 0.25, w: 3.78, h: 0.9, align: "center", fontFace: F_H, fontSize: 40, bold: true, color: CELESTE });
  s.addText(k[1], { x, y: y + 1.2, w: 3.78, h: 0.4, align: "center", fontFace: F_B, fontSize: 14, bold: true, color: BLANCO });
  s.addText(k[2], { x, y: y + 1.6, w: 3.78, h: 0.35, align: "center", fontFace: F_B, fontSize: 11, color: "8FB3E8" });
});
s.addNotes("La slide más importante: 60-90 segundos. Leer los tres primeros con sus requisitos ('3 milisegundos contra un límite de 20'). Insistir: son medias con intervalo de confianza sobre 10 semillas — no una corrida afortunada. Todos cumplen con MARGEN.");

// ============ 8 · COBERTURA / ROAMING ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "La red cubre todo el recorrido del vehículo");
s.addImage({ path: DIR + "grafico_rssi_asociado.png", x: 0.75, y: 1.65, w: 7.6, h: 4.55 });
card(s, 8.6, 1.65, 3.95, 2.0, HIELO);
s.addText("−72.1 dBm", { x: 8.6, y: 1.85, w: 3.95, h: 0.85, align: "center", fontFace: F_H, fontSize: 38, bold: true, color: VERDE });
s.addText("peor nivel de señal del enlace en todo el ciclo (9.9 dB sobre el umbral usable)",
  { x: 8.75, y: 2.72, w: 3.65, h: 0.8, align: "center", fontFace: F_B, fontSize: 11.5, color: INK, lineSpacingMultiple: 1.05 });
card(s, 8.6, 3.85, 3.95, 2.35, HIELO);
s.addText([
  { text: "Roaming estable por diseño. ", options: { bold: true, color: AZUL } },
  { text: "El vehículo no persigue al AP más cercano (evita micro-cortes): mantiene un enlace tipo make-before-break, como la malla industrial real. Cuando el traspaso ocurre, dura ", options: { color: INK } },
  { text: "menos de 1 ms.", options: { bold: true, color: VERDE } },
], { x: 8.85, y: 4.05, w: 3.5, h: 2.0, fontFace: F_B, fontSize: 12, lineSpacingMultiple: 1.12 });
s.addText("RSSI del enlace asociado durante el recorrido — 10 semillas.",
  { x: 0.75, y: 6.3, w: 7.6, h: 0.5, fontFace: F_B, fontSize: 11, italic: true, color: GRIS, align: "center" });
s.addNotes("Anticipa la pregunta clásica del jurado ('¿y si pierde señal en la curva?'). La línea azul nunca baja de -72.1 dBm: margen de 9.9 dB. Explicar el roaming estable: make-before-break, igual que el equipo real. Traspaso peor caso 0.91 ms contra 150 permitidos.");

// ============ 9 · ESTRÉS + WMM (lámina multi-semilla) ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "La prioridad WMM protege lo crítico — con 10 semillas de evidencia");
s.addImage({ path: DIR + "wmm_semillas.png", x: 0.55, y: 1.75, w: 10.1, h: 4.8 });
card(s, 10.85, 1.75, 1.95, 4.8, HIELO);
s.addText([
  { text: "La lectura\n\n", options: { bold: true, color: AZUL, fontSize: 12.5 } },
  { text: "Cajas diminutas = resultados estables entre semillas.\n\n", options: { color: INK, fontSize: 10.5 } },
  { text: "Bajo estrés, los comandos suben a 6.8 ms — lejos del límite de 20.\n\n", options: { color: INK, fontSize: 10.5 } },
  { text: "La presión va a la latencia, nunca a las pérdidas.", options: { bold: true, color: VERDE, fontSize: 10.5 } },
], { x: 11.0, y: 1.95, w: 1.68, h: 4.4, fontFace: F_B, lineSpacingMultiple: 1.08 });
s.addNotes("60 segundos. Panel (a): la latencia de cada flujo con la dispersión de las 10 semillas — las cajas son diminutas: el resultado es estable, no una corrida afortunada. Comandos y telemetría ~3 ms, vídeo 36 ms. Panel (b): los 4 escenarios — bajo estrés de vídeo los comandos suben de 3.0 a 6.8 ms (×2.3) pero NUNCA se acercan al límite de 20: la clase AC_VO los protege. Pregunta anticipada '¿por qué la telemetría no tiene prioridad?': es tolerante al retardo (datos de estado); lo crítico es el mando. Y aun en AC_BE mide 3.08 ms — la prioridad es un seguro para cuando hay presión.");

// ============ 10 · PROFUNDIDAD TÉCNICA (802.11ac + antenas) ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "Del estándar físico a la antena: profundidad del análisis");
s.addImage({ path: DIR + "wlan_802_11ac.png", x: 0.75, y: 1.7, w: 7.3, h: 3.1 });
s.addText("Capa física 802.11ac real (WLAN Toolbox): PER vs SNR por esquema de modulación y constelación 256-QAM ecualizada tras el canal.",
  { x: 0.75, y: 4.85, w: 7.3, h: 0.6, fontFace: F_B, fontSize: 11, italic: true, color: GRIS, align: "center" });
s.addImage({ path: DIR + "patron_antenas_3d.png", x: 8.35, y: 1.7, w: 4.25, h: 3.1 });
s.addText("Los 12 AP irradiando con sus patrones reales (Antenna Toolbox) sobre la geometría de la mina.",
  { x: 8.35, y: 4.85, w: 4.25, h: 0.6, fontFace: F_B, fontSize: 11, italic: true, color: GRIS, align: "center" });
card(s, 0.75, 5.65, 11.8, 1.05, HIELO);
s.addText([
  { text: "Tres niveles de validación: ", options: { bold: true, color: AZUL } },
  { text: "modelo de canal calibrado con site survey real (TamoGraph) · simulación de red completa (NS-3) · capa física del estándar y patrones de antena (MATLAB). Cada decisión del diseño es trazable a evidencia.", options: { color: INK } },
], { x: 1.0, y: 5.78, w: 11.3, h: 0.85, fontFace: F_B, fontSize: 12.5, lineSpacingMultiple: 1.1, valign: "middle" });
s.addNotes("60 segundos. Este es el diferenciador técnico: no solo simulación de red — también la capa física del estándar (jerarquía de MCS correcta, constelación 256-QAM tras el canal) y los patrones reales de las antenas en la geometría de la mina. Mensaje: 'el análisis baja hasta el símbolo de modulación'.");

// ============ 10b · ANTENAS: PATRONES 3D DE DIRECTIVIDAD ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "Las antenas del diseño y sus patrones 3D");
s.addImage({ path: DIR + "patron3d_hawk.png", x: 0.55, y: 1.7, w: 4.15, h: 3.35 });
s.addImage({ path: DIR + "patron3d_cardinal.png", x: 4.85, y: 1.7, w: 4.15, h: 3.35 });
s.addImage({ path: DIR + "patron3d_lhd.png", x: 9.15, y: 1.7, w: 3.65, h: 3.35 });
const ANT = [
  ["Hawk — RCP-50 LHP/RHP (par)", "11 dBi · BIDIRECCIONAL: dos lóbulos a lo largo de la galería · pol. circular izq./der. (diversidad MIMO) · tramos largos", 0.55, 4.15],
  ["Cardinal — EPNT-7", "7.5 dBi · omnidireccional (la “dona” es su patrón real) · cruceros", 4.85, 4.15],
  ["LHD — HELI-40", "4.8 dBic · pol. circular · BIDIRECCIONAL: dos lóbulos por el túnel", 9.15, 3.65],
];
ANT.forEach(a => {
  card(s, a[2], 5.15, a[3], 1.05);
  s.addText(a[0], { x: a[2] + 0.2, y: 5.25, w: a[3] - 0.4, h: 0.35, fontFace: F_B, fontSize: 12.5, bold: true, color: AZUL });
  s.addText(a[1], { x: a[2] + 0.2, y: 5.6, w: a[3] - 0.4, h: 0.55, fontFace: F_B, fontSize: 10, color: INK, lineSpacingMultiple: 1.0 });
});
s.addText("Patrones de directividad calculados por método de momentos (Antenna Toolbox, 5 GHz); los bidireccionales (RCP-50 y HELI-40) sintetizados según la especificación de sus datasheets Poynting.",
  { x: 0.75, y: 6.5, w: 11.9, h: 0.55, fontFace: F_B, fontSize: 10.5, italic: true, color: GRIS, align: "center" });
s.addNotes("40 segundos. Justificación de cada antena según datasheet Poynting: el Hawk lleva el PAR RCP-50 LHP + RHP (11 dBi, BIDIRECCIONAL, 'Mine/tunnel installations'): dos lóbulos que cubren la galería en AMBOS sentidos, y las dos polarizaciones circulares (izquierda y derecha) dan la diversidad para los 2 streams MIMO — por eso va en los TRAMOS LARGOS. El Cardinal usa la EPNT-7 omni para los cruceros. El LHD lleva la HELI-40 (4.8 dBic), también bidireccional — el vehículo avanza y retrocede. La polarización circular mitiga el multitrayecto de la roca. Patrones calculados por método de momentos; los bidireccionales sintetizados según especificación.");

// ============ 10c · VALIDACIÓN CRUZADA DEL CANAL (ray-tracing) ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "Validación cruzada del modelo de canal");
s.addImage({ path: DIR + "raytracing_validacion.png", x: 0.75, y: 1.65, w: 8.0, h: 4.6 });
card(s, 9.0, 1.65, 3.55, 2.25, HIELO);
s.addText("Zona de concordancia", { x: 9.2, y: 1.82, w: 3.15, h: 0.4, fontFace: F_B, fontSize: 13, bold: true, color: VERDE });
s.addText("En campo cercano, el ray-tracing 3D (SBR, roca εr=6, σ=0.01 S/m) coincide con el modelo two-slope: error medio ≈ 5 dB.",
  { x: 9.2, y: 2.24, w: 3.2, h: 1.55, fontFace: F_B, fontSize: 11.5, color: INK, lineSpacingMultiple: 1.1 });
card(s, 9.0, 4.1, 3.55, 2.35, HIELO);
s.addText("Y donde divergen…", { x: 9.2, y: 4.27, w: 3.15, h: 0.4, fontFace: F_B, fontSize: 13, bold: true, color: AZUL });
s.addText("…el ray-tracing SUBESTIMA el alcance: no captura el modo guía de onda del túnel (Sun & Akyildiz). Justo por eso el diseño usa el two-slope calibrado con el site survey.",
  { x: 9.2, y: 4.69, w: 3.2, h: 1.7, fontFace: F_B, fontSize: 11.5, color: INK, lineSpacingMultiple: 1.1 });
s.addText("Comparación two-slope vs ray-tracing SBR sobre la geometría 3D de la galería (MATLAB).",
  { x: 0.75, y: 6.35, w: 8.0, h: 0.5, fontFace: F_B, fontSize: 11, italic: true, color: GRIS, align: "center" });
s.addNotes("45 segundos — la slide que blinda el modelo ante el jurado. Justificación paso a paso: (1) construí la galería en 3D con propiedades de roca (permitividad 6, conductividad 0.01 S/m); (2) lancé ray-tracing SBR con hasta 6 reflexiones; (3) en campo cercano AMBOS métodos coinciden (error ~5 dB) — el modelo queda validado por un método independiente; (4) a larga distancia el ray-tracing pierde los rayos porque no modela el guiado de onda del túnel — limitación documentada en la literatura — lo que JUSTIFICA usar el two-slope calibrado con el survey real. Doble validación + honestidad metodológica.");

// ============ 11 · IDONEIDAD ============
s = p.addSlide(); s.background = { color: BLANCO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
titulo(s, "Una solución idónea en todas sus dimensiones");
const DIM = [
  ["Idoneidad técnica", "Todos los KPIs cumplen con margen y respaldo estadístico de 10 semillas."],
  ["Idoneidad económica", "Inversión incremental sobre la infraestructura existente; despliegue gradual por frentes."],
  ["Idoneidad regulatoria", "Banda 5 GHz de uso libre (MTC); alineada al reglamento de seguridad minera (D.S. 024-2016-EM)."],
  ["Dimensión ética y social", "Retira al trabajador de la zona de riesgo; gestión responsable del cambio con el personal."],
];
DIM.forEach((d1, i) => {
  const y = 1.6 + i * 1.28;
  card(s, 0.75, y, 6.1, 1.1, HIELO);
  s.addText(d1[0], { x: 1.05, y: y + 0.12, w: 5.5, h: 0.4, fontFace: F_B, fontSize: 13.5, bold: true, color: AZUL });
  s.addText(d1[1], { x: 1.05, y: y + 0.52, w: 5.55, h: 0.55, fontFace: F_B, fontSize: 10.8, color: INK, lineSpacingMultiple: 1.0 });
});
s.addImage({ path: DIR + "fig_capex_opex.png", x: 7.25, y: 1.7, w: 5.35, h: 4.35 });
s.addText("Estructura económica: inversión, operación y mecanismos de retorno.",
  { x: 7.25, y: 6.1, w: 5.35, h: 0.5, fontFace: F_B, fontSize: 11, italic: true, color: GRIS, align: "center" });
s.addNotes("60 segundos. Recorrer las 4 dimensiones. En económica ser honesto: 'la estructura de costos y los mecanismos de retorno están definidos; la cuantificación exacta requiere cotizaciones vigentes y es el paso siguiente con planeamiento de la mina'.");

// ============ 12 · REFLEXIÓN FINAL (oscura) ============
s = p.addSlide(); s.background = { color: OSCURO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
s.addText("Reflexión final", { x: 0.85, y: 0.75, w: 5, h: 0.5, fontFace: F_B, fontSize: 14, bold: true, color: CELESTE, charSpacing: 3 });
s.addText("Diseñé una red que puede sacar a una persona de la zona de peligro dentro de una mina.",
  { x: 1.3, y: 1.7, w: 10.75, h: 1.7, align: "center", fontFace: F_H, fontSize: 31, bold: true, color: BLANCO, lineSpacingMultiple: 1.12 });
s.addText("Y demostré, con evidencia reproducible, que es viable.",
  { x: 1.3, y: 3.45, w: 10.75, h: 0.6, align: "center", fontFace: F_B, fontSize: 17, italic: true, color: CELESTE });
const REF = [
  ["Lo que logré", "Una red validada sobre la geometría real, con todos los KPIs cumplidos y trazabilidad completa de cada número."],
  ["Lo que aprendí", "A integrar propagación, redes y análisis de idoneidad — y a defender cada decisión con datos, no con opiniones."],
  ["Lo que sigue", "Un camino replicable hacia una minería peruana más segura — y la base de un artículo de investigación."],
];
REF.forEach((r, i) => {
  const x = 0.85 + i * 4.0;
  s.addShape(p.ShapeType.roundRect, { x, y: 4.45, w: 3.75, h: 2.3, rectRadius: 0.1, fill: { color: "0A2B66" }, line: { color: "1D4B99", width: 1 } });
  s.addText(r[0], { x: x + 0.25, y: 4.65, w: 3.25, h: 0.45, fontFace: F_B, fontSize: 14, bold: true, color: CELESTE });
  s.addText(r[1], { x: x + 0.25, y: 5.12, w: 3.25, h: 1.5, fontFace: F_B, fontSize: 11.5, color: "D7E4F5", lineSpacingMultiple: 1.1 });
});
s.addNotes("El cierre vendedor que pide el profesor, desde la plataforma de éxito: 60 segundos. Frase central con pausa. Tres columnas: logro, aprendizaje, proyección. Terminar mirando al jurado: 'la tecnología ya existe; lo que esta tesis aporta es la evidencia de que funciona donde más se necesita'.");

// ============ 13 · GRACIAS (oscura) ============
s = p.addSlide(); s.background = { color: OSCURO };
s.slideNumber = { x: 12.55, y: 7.05, fontFace: F_B, fontSize: 10, color: "8FA3BC" };
s.addImage({ path: DIR + "mina_realista_3d.png", x: 8.0, y: 3.6, w: 5.33, h: 3.9, rounding: true, transparency: 25 });
s.addText("Gracias", { x: 0.85, y: 2.6, w: 8, h: 1.2, fontFace: F_H, fontSize: 54, bold: true, color: BLANCO });
s.addText("¿Preguntas?", { x: 0.88, y: 3.85, w: 8, h: 0.6, fontFace: F_B, fontSize: 20, color: CELESTE });
s.addText("Adrián Álvaro López Pascual · Ingeniería de las Telecomunicaciones · PUCP",
  { x: 0.88, y: 6.6, w: 9, h: 0.45, fontFace: F_B, fontSize: 12, color: "B9CCE8" });
s.addNotes("Agradecer al jurado y al asesor. Respirar. Las preguntas se responden con la estructura: reconocer → responder con el dato → remitir a la evidencia (capítulo/anexo). Si no sé algo: reconocerlo y remitirlo a trabajo futuro.");

p.writeFile({ fileName: DIR + "sustentacion_tesis_v2.pptx" }).then(f => console.log("OK:", f));

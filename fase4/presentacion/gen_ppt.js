// Presentación de sustentación — Tesis 802.11ac teleoperación LHD NV1640
// Estructura minuto a minuto exigida por el profesor (TEL147). PUCP azul/celeste.
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
const DIR = "C:/Users/Adrian Lopez/Documents/tesis_proyecto/fase4/presentacion/";

// paleta PUCP
const AZUL = "0033A0", CELESTE = "5AA0DC", HIELO = "E6F0FA", INK = "1A2733",
      GRIS = "5B6670", BLANCO = "FFFFFF", VERDE = "2E8B57", AMBAR = "C8860B";
const F_H = "Cambria", F_B = "Calibri";

function bg(s, c){ s.background = { color: c }; }
function tag(s, txt){ // etiqueta de tiempo/sección arriba a la derecha
  s.addText(txt, { x: 9.3, y: 0.3, w: 3.7, h: 0.4, align: "right",
    fontFace: F_B, fontSize: 12, color: CELESTE, bold: true });
}

// ============ 1. CARÁTULA (obligatoria) ============
let s = p.addSlide(); bg(s, AZUL);
s.addText("PONTIFICIA UNIVERSIDAD CATÓLICA DEL PERÚ", { x:0.6, y:0.7, w:12.1, h:0.4, fontFace:F_B, fontSize:14, color:CELESTE, bold:true, align:"center", charSpacing:2 });
s.addText("Facultad de Ciencias e Ingeniería · Ingeniería de las Telecomunicaciones", { x:0.6, y:1.15, w:12.1, h:0.4, fontFace:F_B, fontSize:13, color:HIELO, align:"center" });
s.addText("Diseño de una red IEEE 802.11ac para la teleoperación\nde un vehículo LHD en la extracción de mineral\nen galerías subterráneas", { x:0.8, y:2.3, w:11.7, h:2.2, fontFace:F_H, fontSize:31, color:BLANCO, bold:true, align:"center", lineSpacingMultiple:1.05 });
s.addShape(p.ShapeType.line, { x:4.6, y:4.75, w:4.1, h:0, line:{ color:CELESTE, width:1.5 } });
s.addText([
  { text:"Tesista:  ", options:{ bold:true, color:CELESTE } },
  { text:"Adrián Álvaro López Pascual", options:{ color:BLANCO } },
], { x:0.8, y:5.15, w:11.7, h:0.45, fontFace:F_B, fontSize:17, align:"center" });
s.addText([
  { text:"Asesor:  ", options:{ bold:true, color:CELESTE } },
  { text:"Dr. Pastor David Chávez Muñoz", options:{ color:BLANCO } },
], { x:0.8, y:5.65, w:11.7, h:0.45, fontFace:F_B, fontSize:17, align:"center" });
s.addText("Trabajo de Tesis 2 · Sustentación", { x:0.8, y:6.7, w:11.7, h:0.4, fontFace:F_B, fontSize:13, color:GRIS, align:"center" });
s.addNotes("Buenos días señores miembros del jurado. Mi nombre es Adrián López y hoy presento el diseño de una red 802.11ac para teleoperar un vehículo LHD en minería subterránea. [Saludar con seguridad y hacer contacto visual.]");

// ============ 2. DESCRIPCIÓN DEL TRABAJO (obligatoria) ============
s = p.addSlide(); bg(s, BLANCO);
s.addText("¿De qué trata este trabajo?", { x:0.7, y:0.5, w:9, h:0.7, fontFace:F_H, fontSize:32, color:AZUL, bold:true });
s.addText("En una frase", { x:0.7, y:1.3, w:9, h:0.4, fontFace:F_B, fontSize:15, color:CELESTE, bold:true, italic:true });
s.addText("Se diseñó y validó por simulación una red Wi-Fi industrial que permite conducir a distancia un vehículo minero (LHD), retirando al operador de la zona de riesgo dentro de la mina.", { x:0.7, y:1.75, w:7.4, h:1.6, fontFace:F_B, fontSize:19, color:INK, lineSpacingMultiple:1.15 });
// 3 pilares en tarjetas
const pil = [
  ["Problema", "El operador conduce el LHD dentro de la galería, expuesto a desprendimientos, gases y maquinaria."],
  ["Solución", "Red 802.11ac que transmite video, comandos y telemetría para teleoperar el vehículo desde superficie."],
  ["Validación", "Simulación NS-3 sobre la geometría real del nivel NV1640 de Nexa Cerro Lindo."],
];
pil.forEach((c,i)=>{
  const y = 3.6 + i*1.15;
  s.addShape(p.ShapeType.roundRect, { x:0.7, y, w:7.4, h:1.0, rectRadius:0.08, fill:{ color:HIELO }, line:{ color:CELESTE, width:1 } });
  s.addText(c[0], { x:0.95, y:y+0.12, w:1.8, h:0.35, fontFace:F_B, fontSize:15, color:AZUL, bold:true });
  s.addText(c[1], { x:2.7, y:y+0.1, w:5.2, h:0.8, fontFace:F_B, fontSize:12.5, color:INK, valign:"middle" });
});
s.addImage({ path: DIR+"escena_mina_3d.png", x:8.35, y:1.7, w:4.5, h:2.65 });
s.addText("Entorno 3D real de la zona de producción y la red diseñada", { x:8.35, y:4.35, w:4.5, h:0.6, fontFace:F_B, fontSize:11, color:GRIS, italic:true, align:"center" });
s.addNotes("Este trabajo diseña una red que permite conducir el LHD a distancia. El operador ya no va dentro de la mina: opera desde superficie con video, comandos y telemetría. Lo validé simulando la red sobre la geometría REAL del nivel de la mina.");

// ============ 3. MOTIVACIÓN PERSONAL (3 min — el profesor le da mucho peso) ============
s = p.addSlide(); bg(s, AZUL); tag(s, "Motivación · 3 min");
s.addText("¿Por qué esta tesis?", { x:0.7, y:0.7, w:11, h:0.8, fontFace:F_H, fontSize:34, color:BLANCO, bold:true });
const mot = [
  ["Mi vínculo personal", "Mi cercanía con el mundo minero y las personas que trabajan en él me hizo ver de cerca los riesgos que enfrentan cada día bajo tierra."],
  ["La seguridad primero", "Cada año la minería subterránea peruana cobra vidas. Que la tecnología pueda sacar a una persona de la zona de peligro le da sentido a esta carrera."],
  ["El reto técnico", "Diseñar comunicaciones confiables dentro de una galería —con roca, curvas y movilidad— es de los desafíos más exigentes de las telecomunicaciones."],
  ["La innovación", "Ser parte de la transformación digital de la minería peruana: un camino replicable hacia operaciones más seguras."],
];
mot.forEach((c,i)=>{
  const x = 0.7 + (i%2)*6.15, y = 1.9 + Math.floor(i/2)*2.35;
  s.addShape(p.ShapeType.roundRect, { x, y, w:5.85, h:2.05, rectRadius:0.09, fill:{ color:"12275C" }, line:{ color:CELESTE, width:1 } });
  s.addText((i+1).toString(), { x:x+0.25, y:y+0.2, w:0.7, h:0.7, fontFace:F_H, fontSize:30, color:CELESTE, bold:true });
  s.addText(c[0], { x:x+1.05, y:y+0.28, w:4.5, h:0.5, fontFace:F_B, fontSize:17, color:BLANCO, bold:true });
  s.addText(c[1], { x:x+1.05, y:y+0.85, w:4.6, h:1.05, fontFace:F_B, fontSize:12.5, color:HIELO, lineSpacingMultiple:1.1 });
});
s.addNotes("[3 MINUTOS. Hablar desde el corazón, mirar al jurado.] Elegí este tema por mi vínculo personal con la minería y porque la seguridad del trabajador me importa de verdad. Vi de cerca los riesgos. Que una red bien diseñada pueda sacar a una persona de la zona de peligro le da sentido a todo lo que estudié. Y como ingeniero, el reto técnico de lograr comunicaciones confiables dentro de una galería me apasionó.");

// ============ 4. OBJETIVOS (3 min) ============
s = p.addSlide(); bg(s, BLANCO); tag(s, "Objetivos · 3 min");
s.addText("Objetivos", { x:0.7, y:0.5, w:9, h:0.7, fontFace:F_H, fontSize:32, color:AZUL, bold:true });
s.addShape(p.ShapeType.roundRect, { x:0.7, y:1.45, w:12, h:1.15, rectRadius:0.08, fill:{ color:AZUL } });
s.addText("Objetivo general", { x:1.0, y:1.6, w:4, h:0.35, fontFace:F_B, fontSize:14, color:CELESTE, bold:true });
s.addText("Diseñar una red IEEE 802.11ac que habilite la teleoperación segura y confiable de un vehículo LHD en las galerías del nivel NV1640, verificando su desempeño por simulación.", { x:1.0, y:1.95, w:11.4, h:0.6, fontFace:F_B, fontSize:14.5, color:BLANCO, valign:"top" });
s.addText("Objetivos específicos", { x:0.7, y:2.9, w:8, h:0.4, fontFace:F_B, fontSize:16, color:CELESTE, bold:true });
const obj = [
  "Caracterizar el canal de propagación en las galerías subterráneas.",
  "Diseñar la arquitectura física y lógica de la red (backbone + acceso).",
  "Dimensionar el subsistema de radio y antenas para el túnel.",
  "Establecer las políticas de calidad de servicio (QoS) y movilidad.",
  "Validar el desempeño extremo a extremo por simulación.",
  "Evaluar la viabilidad técnico-económica de la solución.",
];
obj.forEach((t,i)=>{
  const x = 0.7 + (i%2)*6.15, y = 3.5 + Math.floor(i/2)*1.15;
  s.addShape(p.ShapeType.ellipse, { x, y:y+0.05, w:0.55, h:0.55, fill:{ color:CELESTE } });
  s.addText((i+1).toString(), { x, y:y+0.05, w:0.55, h:0.55, align:"center", valign:"middle", fontFace:F_B, fontSize:18, color:BLANCO, bold:true });
  s.addText(t, { x:x+0.75, y, w:5.2, h:1.0, fontFace:F_B, fontSize:13, color:INK, valign:"middle" });
});
s.addNotes("[3 MIN, breve — el jurado ya los leyó.] El objetivo general fue diseñar la red y verificarla por simulación. Se desglosa en seis específicos: caracterizar el canal, diseñar la arquitectura, dimensionar radio y antenas, definir QoS y movilidad, validar por simulación y evaluar la viabilidad económica.");

// ============ 5-7. CÓMO LO HICE (5 min): metodología, geometría, arquitectura ============
s = p.addSlide(); bg(s, BLANCO); tag(s, "Cómo lo hice · 5 min");
s.addText("Metodología: Design Thinking aplicado al diseño", { x:0.7, y:0.5, w:12, h:0.7, fontFace:F_H, fontSize:28, color:AZUL, bold:true });
const dt = [["Empatizar","Entender al operador y el riesgo que enfrenta"],["Definir","Requisitos funcionales y no funcionales (KPIs)"],["Idear","Comparar tecnologías: Wi-Fi, LTE/5G, óptica"],["Prototipar","Simulación NS-3 con geometría real"],["Validar","Contraste con TamoGraph y análisis de idoneidad"]];
dt.forEach((c,i)=>{
  const x = 0.7 + i*2.45;
  s.addShape(p.ShapeType.roundRect, { x, y:1.7, w:2.2, h:2.3, rectRadius:0.08, fill:{ color: i%2? HIELO: AZUL } });
  s.addText((i+1).toString(), { x, y:1.95, w:2.2, h:0.6, align:"center", fontFace:F_H, fontSize:30, color: i%2? AZUL: CELESTE, bold:true });
  s.addText(c[0], { x:x+0.1, y:2.6, w:2.0, h:0.45, align:"center", fontFace:F_B, fontSize:15, color: i%2? AZUL: BLANCO, bold:true });
  s.addText(c[1], { x:x+0.15, y:3.05, w:1.9, h:0.9, align:"center", fontFace:F_B, fontSize:10.5, color: i%2? INK: HIELO, lineSpacingMultiple:1.05 });
  if(i<4) s.addText("→", { x:x+2.05, y:2.5, w:0.5, h:0.5, align:"center", fontFace:F_B, fontSize:22, color:CELESTE, bold:true });
});
s.addText("El proceso partió del usuario (el operador y su seguridad) y avanzó de forma iterativa hasta un prototipo simulado y validado.", { x:0.7, y:4.4, w:12, h:0.6, fontFace:F_B, fontSize:15, color:GRIS, italic:true, align:"center" });
s.addImage({ path: DIR+"plano_nv1640_pro.png", x:2.4, y:5.05, w:8.5, h:2.2 });
s.addNotes("[5 MIN — cómo lo hice.] Apliqué Design Thinking: empecé entendiendo al operador y su riesgo, definí los KPIs, comparé tecnologías y elegí 802.11ac, prototipé en NS-3 sobre la geometría REAL del nivel, y validé contra el site survey TamoGraph. [MENCIONAR Design Thinking explícitamente — el profesor lo exige.]");

s = p.addSlide(); bg(s, BLANCO); tag(s, "Cómo lo hice · 5 min");
s.addText("La arquitectura de la solución", { x:0.7, y:0.5, w:12, h:0.7, fontFace:F_H, fontSize:30, color:AZUL, bold:true });
s.addImage({ path: DIR+"arquitectura_red.png", x:0.6, y:1.4, w:7.6, h:5.6 });
const arq = [["Centro de control","Estación de teleoperación en superficie"],["Backbone óptico","Anillo de fibra + switches industriales"],["Malla de acceso","5 AP Hawk + 7 AP Cardinal (802.11ac)"],["Vehículo LHD","Radio embarcado + antena HELI-40"]];
arq.forEach((c,i)=>{
  const y = 1.7 + i*1.3;
  s.addShape(p.ShapeType.roundRect, { x:8.5, y, w:4.3, h:1.1, rectRadius:0.08, fill:{ color:HIELO }, line:{ color:CELESTE, width:1 } });
  s.addText(c[0], { x:8.75, y:y+0.15, w:3.9, h:0.4, fontFace:F_B, fontSize:15, color:AZUL, bold:true });
  s.addText(c[1], { x:8.75, y:y+0.55, w:3.9, h:0.45, fontFace:F_B, fontSize:12, color:INK });
});
s.addNotes("La arquitectura tiene tres capas: el centro de control en superficie, un backbone de fibra óptica en anillo, y la malla de acceso inalámbrico con 12 puntos de acceso. El vehículo lleva un radio embarcado. Todo sobre estándares abiertos: 802.11ac.");

// ============ 8-11. LOGROS Y RESULTADOS (7 min — LO MÁS IMPORTANTE) ============
s = p.addSlide(); bg(s, AZUL); tag(s, "Resultados · 7 min");
s.addText("Resultados: todos los KPIs se cumplen", { x:0.7, y:0.6, w:12, h:0.8, fontFace:F_H, fontSize:32, color:BLANCO, bold:true });
s.addText("18 ejecuciones · 10 semillas independientes · media ± intervalo de confianza al 95 %", { x:0.7, y:1.4, w:12, h:0.4, fontFace:F_B, fontSize:15, color:CELESTE, italic:true });
const kpi = [
  ["OWD comandos","3.04 ms","≤ 20 ms"],["Latencia vídeo E2E","35.9 ms","≤ 150 ms"],
  ["Jitter P95","0.28 ms","≤ 10 ms"],["Throughput vídeo","40.1 Mbps","≥ 38 Mbps"],
  ["PLR comandos","0.06 %","≤ 0.5 %"],["Disponibilidad","100 %","≥ 99.9 %"],
];
kpi.forEach((c,i)=>{
  const x = 0.7 + (i%3)*4.1, y = 2.15 + Math.floor(i/3)*2.35;
  s.addShape(p.ShapeType.roundRect, { x, y, w:3.85, h:2.1, rectRadius:0.09, fill:{ color:"12275C" }, line:{ color:CELESTE, width:1 } });
  s.addText(c[0], { x:x+0.2, y:y+0.2, w:3.5, h:0.4, fontFace:F_B, fontSize:14, color:HIELO });
  s.addText(c[1], { x:x+0.2, y:y+0.6, w:3.5, h:0.9, fontFace:F_H, fontSize:40, color:CELESTE, bold:true });
  s.addText([{text:"Requisito: ",options:{color:GRIS}},{text:c[2],options:{color:"9DC3E6",bold:true}}], { x:x+0.2, y:y+1.55, w:3.5, h:0.4, fontFace:F_B, fontSize:12 });
});
s.addNotes("[7 MIN — LO MÁS IMPORTANTE. Aquí me luzco.] Estos son los resultados. TODOS los indicadores cumplen, con margen amplio y respaldo estadístico de 10 semillas. La latencia de comandos: 3 ms cuando el límite es 20. El video llega con 36 ms cuando se permiten 150. Disponibilidad del 100%. No son números sueltos: cada uno viene de datos reproducibles.");

s = p.addSlide(); bg(s, BLANCO); tag(s, "Resultados · 7 min");
s.addText("La red cubre todo el recorrido del vehículo", { x:0.7, y:0.5, w:12, h:0.7, fontFace:F_H, fontSize:28, color:AZUL, bold:true });
s.addImage({ path: DIR+"grafico_rssi_asociado.png", x:0.6, y:1.4, w:8.1, h:4.0 });
s.addText("El enlace de servicio nunca cae", { x:8.9, y:1.7, w:4, h:0.5, fontFace:F_B, fontSize:17, color:AZUL, bold:true });
s.addText("Durante todo el ciclo de operación, el nivel de señal del enlace se mantiene 9.9 dB por encima del umbral mínimo utilizable.", { x:8.9, y:2.3, w:3.9, h:1.5, fontFace:F_B, fontSize:13.5, color:INK, lineSpacingMultiple:1.15 });
s.addShape(p.ShapeType.roundRect, { x:8.9, y:3.9, w:3.9, h:1.5, rectRadius:0.08, fill:{ color:HIELO } });
s.addText("−72.1 dBm", { x:8.9, y:4.05, w:3.9, h:0.7, align:"center", fontFace:F_H, fontSize:34, color:VERDE, bold:true });
s.addText("peor nivel de señal registrado\n(margen de 9.9 dB sobre el umbral)", { x:8.9, y:4.75, w:3.9, h:0.6, align:"center", fontFace:F_B, fontSize:11, color:GRIS });
s.addText("Diseño de roaming estable tipo make-before-break: el enlace se mantiene durante el desplazamiento continuo del LHD.", { x:0.7, y:5.6, w:12, h:0.6, fontFace:F_B, fontSize:14, color:GRIS, italic:true, align:"center" });
s.addNotes("Una pregunta natural es: ¿y la cobertura durante el movimiento? Aquí está la respuesta con datos: el enlace de servicio NUNCA baja de -72 dBm, con casi 10 dB de margen sobre el mínimo. La red mantiene al vehículo conectado en todo el recorrido. [Si preguntan por qué no salta al AP más cercano: es diseño deliberado, evita micro-cortes; el equipo real mejora aún más.]");

s = p.addSlide(); bg(s, BLANCO); tag(s, "Resultados · 7 min");
s.addText("El diseño resiste condiciones de estrés", { x:0.7, y:0.5, w:12, h:0.7, fontFace:F_H, fontSize:28, color:AZUL, bold:true });
s.addImage({ path: DIR+"resultados_escenarios.png", x:1.6, y:1.4, w:10.1, h:4.5 });
s.addText("Aun elevando el vídeo a 50 Mbps o la velocidad a 4 m/s, la red mantiene los criterios de aceptación: hay margen de diseño verificable.", { x:0.7, y:6.1, w:12, h:0.7, fontFace:F_B, fontSize:15, color:GRIS, italic:true, align:"center" });
s.addNotes("No solo probé la operación nominal. Sometí la red a estrés: subí el video a 50 Mbps, aceleré el vehículo a 4 m/s. Aun así cumple. Eso demuestra que el dimensionamiento tiene margen, no está al límite.");

// ============ 12. IDONEIDAD (parte de resultados / Cap 4) ============
s = p.addSlide(); bg(s, BLANCO); tag(s, "Resultados · 7 min");
s.addText("Una solución idónea en todas sus dimensiones", { x:0.7, y:0.5, w:12, h:0.7, fontFace:F_H, fontSize:27, color:AZUL, bold:true });
const idon = [
  ["Técnica","Todos los KPIs cumplen con margen y respaldo estadístico.",VERDE],
  ["Económica","Inversión incremental sobre la infraestructura existente; despliegue gradual.",AZUL],
  ["Regulatoria","Banda 5 GHz de uso libre; alineada al reglamento de seguridad minera.",CELESTE],
  ["Ética y social","Retira al trabajador del riesgo; gestión responsable del cambio.",AMBAR],
];
idon.forEach((c,i)=>{
  const y = 1.6 + i*1.35;
  s.addShape(p.ShapeType.roundRect, { x:0.7, y, w:7.6, h:1.15, rectRadius:0.08, fill:{ color:HIELO } });
  s.addShape(p.ShapeType.ellipse, { x:0.95, y:y+0.32, w:0.5, h:0.5, fill:{ color:c[2] } });
  s.addText(c[0], { x:1.65, y:y+0.15, w:6.4, h:0.45, fontFace:F_B, fontSize:17, color:c[2], bold:true });
  s.addText(c[1], { x:1.65, y:y+0.58, w:6.5, h:0.5, fontFace:F_B, fontSize:12.5, color:INK });
});
s.addImage({ path: DIR+"fig_capex_opex.png", x:8.5, y:2.2, w:4.4, h:2.9 });
s.addNotes("La tesis no se queda en lo técnico. La solución es idónea también en lo económico —inversión incremental—, lo regulatorio —banda libre, reglamento minero— y sobre todo en lo ético: retira al trabajador del riesgo. Esa es la esencia del proyecto.");

// ============ 13. REFLEXIÓN DE CIERRE (el pitch vendedor) ============
s = p.addSlide(); bg(s, AZUL);
s.addText("Reflexión final", { x:0.7, y:0.7, w:11, h:0.6, fontFace:F_B, fontSize:16, color:CELESTE, bold:true, charSpacing:2 });
s.addText("Diseñé una red que puede sacar a una persona\nde la zona de peligro dentro de una mina.", { x:0.8, y:1.7, w:11.7, h:1.6, fontFace:F_H, fontSize:30, color:BLANCO, bold:true, align:"center", lineSpacingMultiple:1.1 });
s.addText("Y demostré, con evidencia reproducible, que es viable.", { x:0.8, y:3.3, w:11.7, h:0.6, fontFace:F_B, fontSize:20, color:CELESTE, italic:true, align:"center" });
const cl = [
  ["Lo que logré","Una red validada sobre la geometría real, con todos los KPIs cumplidos y trazabilidad completa."],
  ["Lo que aprendí","A integrar propagación, redes y análisis de idoneidad; y a defender cada decisión con datos."],
  ["Lo que sigue","Un camino replicable hacia una minería peruana más segura — y la base para un artículo de investigación."],
];
cl.forEach((c,i)=>{
  const x = 0.7 + i*4.1;
  s.addShape(p.ShapeType.roundRect, { x, y:4.3, w:3.85, h:2.4, rectRadius:0.09, fill:{ color:"12275C" }, line:{ color:CELESTE, width:1 } });
  s.addText(c[0], { x:x+0.25, y:4.55, w:3.4, h:0.5, fontFace:F_B, fontSize:16, color:CELESTE, bold:true });
  s.addText(c[1], { x:x+0.25, y:5.1, w:3.4, h:1.5, fontFace:F_B, fontSize:13, color:HIELO, lineSpacingMultiple:1.15 });
});
s.addNotes("[REFLEXIÓN DE CIERRE — el pitch vendedor, desde una plataforma de éxito. Lo que el jurado se lleva.] Señores del jurado: diseñé una red que puede sacar a una persona de la zona de peligro. Y no lo afirmo: lo demostré con evidencia reproducible. Esta tesis integra todo lo que aprendí en la carrera, y abre un camino hacia una minería peruana más segura. Muchas gracias.");

// ============ 14. GRACIAS ============
s = p.addSlide(); bg(s, AZUL);
s.addText("Gracias", { x:0.8, y:2.6, w:11.7, h:1.2, fontFace:F_H, fontSize:54, color:BLANCO, bold:true, align:"center" });
s.addText("Adrián Álvaro López Pascual", { x:0.8, y:3.9, w:11.7, h:0.5, fontFace:F_B, fontSize:20, color:CELESTE, align:"center" });
s.addText("Diseño de una red IEEE 802.11ac para la teleoperación de un vehículo LHD", { x:0.8, y:4.5, w:11.7, h:0.5, fontFace:F_B, fontSize:14, color:HIELO, align:"center", italic:true });
s.addText("¿Preguntas?", { x:0.8, y:5.5, w:11.7, h:0.5, fontFace:F_B, fontSize:18, color:GRIS, align:"center" });
s.addNotes("Quedo atento a sus preguntas. [Respirar. Escuchar la pregunta completa antes de responder. Responder TODA la pregunta — es criterio de calificación.]");

p.writeFile({ fileName: DIR+"sustentacion_tesis.pptx" }).then(f=>console.log("OK:", f));

// Póster científico-técnico XpoSTEM — A1 vertical (59.4 x 84.1 cm), 2 columnas.
// Estructura oficial del curso: Resumen, Palabras clave, Introducción, Objetivos,
// Metodología, Resultados, Discusión, Conclusiones, Agradecimientos, Referencias.
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
// A1 en pulgadas: 59.4cm=23.386in ancho, 84.1cm=33.11in alto
const W = 23.386, H = 33.11;
p.defineLayout({ name: "A1", width: W, height: H });
p.layout = "A1";
const DIR = "C:/Users/Adrian Lopez/Documents/tesis_proyecto/fase4/presentacion/";

const AZUL="0033A0", CELESTE="5AA0DC", HIELO="EAF2FB", INK="1A2733", GRIS="5B6670",
      BLANCO="FFFFFF", VERDE="2E8B57";
const F_H="Cambria", F_B="Calibri";
const s = p.addSlide(); s.background = { color: BLANCO };

const M = 1.0;               // margen
const COLW = (W - 2*M - 0.8)/2;   // ancho de columna
const CX1 = M, CX2 = M + COLW + 0.8;

// ---------- ENCABEZADO NORMALIZADO ----------
s.addShape(p.ShapeType.rect, { x:0, y:0, w:W, h:5.2, fill:{ color:AZUL } });
s.addText("PONTIFICIA UNIVERSIDAD CATÓLICA DEL PERÚ", { x:M, y:0.5, w:W-2*M, h:0.5, fontFace:F_B, fontSize:20, color:CELESTE, bold:true, align:"center", charSpacing:3 });
s.addText("Facultad de Ciencias e Ingeniería  ·  Ingeniería de las Telecomunicaciones", { x:M, y:1.05, w:W-2*M, h:0.45, fontFace:F_B, fontSize:17, color:HIELO, align:"center" });
s.addText("Diseño de una red IEEE 802.11ac para la teleoperación de un vehículo LHD\nen la extracción de mineral en galerías subterráneas", { x:M, y:1.75, w:W-2*M, h:1.7, fontFace:F_H, fontSize:34, color:BLANCO, bold:true, align:"center", lineSpacingMultiple:1.05 });
s.addText([
  { text:"Adrián Álvaro López Pascual", options:{ bold:true, color:BLANCO } },
  { text:"      ·      Asesor: Dr. Pastor David Chávez Muñoz", options:{ color:HIELO } },
], { x:M, y:3.7, w:W-2*M, h:0.5, fontFace:F_B, fontSize:17, align:"center" });
s.addText("XpoSTEM · Trabajo de Tesis 2 · a.lopezp@pucp.edu.pe", { x:M, y:4.35, w:W-2*M, h:0.5, fontFace:F_B, fontSize:14, color:CELESTE, align:"center" });

// ---------- helpers de sección ----------
let yL = 5.7, yR = 5.7;   // cursores de cada columna
function head(col, num, titulo){
  const x = col===1?CX1:CX2; let y = col===1?yL:yR;
  s.addShape(p.ShapeType.rect, { x, y, w:COLW, h:0.85, fill:{ color:AZUL } });
  s.addText((num? num+".  ":"")+titulo, { x:x+0.35, y:y+0.05, w:COLW-0.6, h:0.75, fontFace:F_H, fontSize:22, color:BLANCO, bold:true, valign:"middle" });
  y += 1.02; if(col===1) yL=y; else yR=y;
}
function body(col, txt, size=15){
  const x = col===1?CX1:CX2; let y = col===1?yL:yR;
  const lines = txt.split("\n").length;
  const h = 0.30*Math.ceil(txt.length/72) + 0.26*lines;
  s.addText(txt, { x, y, w:COLW, h, fontFace:F_B, fontSize:size, color:INK, align:"justify", lineSpacingMultiple:1.12, valign:"top" });
  y += h + 0.45; if(col===1) yL=y; else yR=y;
}
function bullets(col, items, size=15){
  const x = col===1?CX1:CX2; let y = col===1?yL:yR;
  const arr = items.map((t,i)=>({ text:t, options:{ bullet:{ code:"2022", indent:18 }, breakLine:true, color:INK } }));
  const h = 0.42*items.length;
  s.addText(arr, { x, y, w:COLW, h, fontFace:F_B, fontSize:size, lineSpacingMultiple:1.1, valign:"top" });
  y += h + 0.45; if(col===1) yL=y; else yR=y;
}
const sizeOf = require("image-size").default || require("image-size");
const fs = require("fs");
function img(col, path, w, cap){
  const x = col===1?CX1:CX2; let y = col===1?yL:yR;
  const dim = sizeOf(fs.readFileSync(DIR+path));
  const hh = w * dim.height / dim.width;
  s.addImage({ path: DIR+path, x:x+(COLW-w)/2, y, w, h:hh });
  y += hh + 0.12;
  if(cap){ s.addText(cap, { x, y, w:COLW, h:0.55, fontFace:F_B, fontSize:12, color:GRIS, italic:true, align:"center" }); y += 0.65; }
  y += 0.3; if(col===1) yL=y; else yR=y;
}
function statRow(col, stats){
  const x = col===1?CX1:CX2; let y = col===1?yL:yR;
  const n = stats.length, gap=0.25, sw=(COLW-(n-1)*gap)/n;
  stats.forEach((st,i)=>{
    const sx = x + i*(sw+gap);
    s.addShape(p.ShapeType.roundRect, { x:sx, y, w:sw, h:1.8, rectRadius:0.08, fill:{ color:HIELO } });
    s.addText(st[0], { x:sx, y:y+0.2, w:sw, h:0.75, align:"center", fontFace:F_H, fontSize:26, color:VERDE, bold:true });
    s.addText(st[1], { x:sx+0.1, y:y+1.0, w:sw-0.2, h:0.7, align:"center", fontFace:F_B, fontSize:12, color:INK });
  });
  y += 1.8 + 0.4; if(col===1) yL=y; else yR=y;
}

// ============ COLUMNA IZQUIERDA ============
head(1, "", "Resumen");
body(1, "La operación manual de vehículos de carga LHD en minería subterránea expone al operador a desprendimientos, gases y tránsito de maquinaria. Este trabajo diseña y valida por simulación una red IEEE 802.11ac que habilita la teleoperación del vehículo desde superficie, transmitiendo vídeo, comandos y telemetría. La validación se realiza sobre la geometría real del nivel NV1640 (Nexa Cerro Lindo) mediante simulación de red NS-3. Todos los indicadores de desempeño se cumplen con margen y respaldo estadístico.", 15);

head(1, "", "Palabras clave");
body(1, "Teleoperación · IEEE 802.11ac · minería subterránea · LHD · propagación en túnel · calidad de servicio · simulación NS-3.", 14);

head(1, "1", "Introducción");
body(1, "La teleoperación retira al trabajador del frente de riesgo, pero exige una red que sostenga vídeo de conducción en tiempo real, comandos de baja latencia y telemetría continua, en un medio confinado con reflexiones, curvas, intersecciones y movilidad del nodo embarcado. El caso de estudio es el nivel NV1640 de la mina Nexa Cerro Lindo, con layout de block caving tipo El Teniente.", 15);

head(1, "2", "Antecedentes");
body(1, "Se realizó una revisión sistemática (método Kitchenham) de tecnologías de comunicación en túneles y minas. Frente a LPWAN/WSN (sin capacidad de vídeo), LTE/5G privado (mayor complejidad) y comunicación óptica (sensible a alineamiento), se selecciona 802.11ac industrial por su capacidad, disponibilidad de equipos y soporte de priorización de tráfico. La propagación se modela con un enfoque two-slope calibrado contra el site survey TamoGraph.", 15);

head(1, "3", "Objetivos");
bullets(1, [
  "Caracterizar el canal de propagación en las galerías.",
  "Diseñar la arquitectura física y lógica de la red.",
  "Dimensionar el subsistema de radio y antenas.",
  "Establecer las políticas de QoS y movilidad.",
  "Validar el desempeño extremo a extremo por simulación.",
  "Evaluar la viabilidad técnico-económica.",
], 15);

head(1, "4", "Metodología");
body(1, "Se aplicó Design Thinking: (1) empatizar con el operador y su riesgo; (2) definir requisitos y KPIs; (3) idear y comparar tecnologías; (4) prototipar en NS-3 sobre la geometría real; (5) validar contra TamoGraph. La red integra un backbone de fibra óptica en anillo y una malla de acceso de 12 puntos (5 AP Hawk de 30 dBm + 7 AP Cardinal de 23 dBm), con el LHD embarcando un radio y antena HELI-40. Se ejecutaron 18 simulaciones de 300 s (10 semillas de operación + referencia + estrés + traspaso).", 15);
img(1, "arquitectura_red.png", COLW-0.4, "Figura 1. Arquitectura de red en tres capas con clases de servicio (QoS).");

head(1, "6", "Discusión");
body(1, "El diseño privilegia un roaming estable (make-before-break) sobre la persecución del AP más cercano, evitando micro-cortes por reasociación. Los escenarios de estrés (vídeo a 50 Mbps, velocidad a 4 m/s) mantienen los criterios, evidenciando margen de dimensionamiento. El modelo es determinista y conservador: el equipo de malla industrial real sólo puede mejorar estos resultados. La validación es de diseño; las pruebas de campo se identifican como trabajo posterior.", 15);

// ============ COLUMNA DERECHA ============
head(2, "5", "Resultados");
body(2, "Sobre la geometría real de la zona de producción, todos los indicadores de desempeño se cumplen con margen, reportados como media e intervalo de confianza al 95 % sobre 10 semillas independientes:", 15);
statRow(2, [["3.04 ms","OWD comandos\n(≤ 20 ms)"],["35.9 ms","Latencia vídeo\n(≤ 150 ms)"],["100 %","Disponibilidad\n(≥ 99.9 %)"]]);
img(2, "escena_mina_3d.png", COLW, "Figura 2. Entorno 3D: galerías reales, 12 AP y patrón de radiación de la antena del LHD (MATLAB).");
img(2, "grafico_rssi_asociado.png", COLW, "Figura 3. RSSI del enlace asociado: nunca cae de −72.1 dBm (9.9 dB de margen sobre el umbral).");

head(2, "7", "Conclusiones");
body(2, "La red IEEE 802.11ac diseñada es idónea para la teleoperación del LHD en el nivel NV1640: cumple todos los KPIs con respaldo estadístico, es económicamente incremental sobre la infraestructura existente, cumple el marco regulatorio (banda 5 GHz de uso libre; reglamento de seguridad minera) y aporta un beneficio ético directo — retirar al trabajador de la zona de riesgo. Constituye un camino replicable hacia una minería peruana más segura.", 15);

head(2, "8", "Agradecimientos");
body(2, "Al Dr. Pastor David Chávez Muñoz por su asesoría, y a la PUCP por la formación recibida.", 14);

head(2, "9", "Referencias");
body(2, "[1] Z. Sun, I. F. Akyildiz, «Channel Modeling for Wireless Networks in Tunnels», IEEE Trans. Commun., 2010.\n[2] Rajant, «InstaMesh Whitepaper», 2015.\n[3] E. Egea-López et al., «Wireless Communications in Underground Mines», 2019.\n[4] The ns-3 Consortium, «ns-3.40 Documentation», 2024.", 12);

p.writeFile({ fileName: DIR+"poster_xpostem.pptx" }).then(f=>console.log("OK:", f));

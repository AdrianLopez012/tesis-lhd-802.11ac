// Flashcards de repaso rápido para la sustentación (pregunta + clave corta).
const pptxgen = require("pptxgenjs");
const p = new pptxgen(); p.defineLayout({ name:"W", width:13.333, height:7.5 }); p.layout="W";
const AZUL="0033A0", CEL="2E6FB0", VERDE="2E8B57", INK="1A2733", HIELO="EAF2FB", BL="FFFFFF", GRIS="5B6670";
const F_H="Cambria", F_B="Calibri";

// [pregunta, respuesta-clave (1-2 frases, lo que hay que recordar)]
const cards = [
["¿Por qué 802.11ac y no 5G privado?","Equipos ya son 802.11ac · sin licencia de espectro (5 GHz libre) · capacidad sobra para 1 LHD. 5G = evolución futura."],
["¿Simulación determinista sin shadowing?","Decisión metodológica: shadowing desestabiliza el roaming de NS-3. Variabilidad ±σ se analiza aparte (mapa + TamoGraph). Modelo conservador."],
["¿Cómo validó la propagación?","Validación de DISEÑO, no de campo. Modelo two-slope calibrado con el site survey TamoGraph real. Medición propia = trabajo futuro."],
["¿Por qué no se conecta al AP más cercano?","Roaming estable make-before-break (evita ping-pong). Enlace nunca baja de −72.1 dBm, 9.9 dB de margen. Traspaso < 1 ms."],
["¿La señal atraviesa la roca?","NO. A 5 GHz la roca bloquea. La señal viaja por labores abiertas (galerías + cruceros), +10 dB por galería cruzada. Supuesto conservador."],
["¿Qué metodología usó?","DESIGN THINKING: empatizar → definir → idear → prototipar (NS-3) → validar (TamoGraph). Centrado en la seguridad del operador."],
["¿Cuántas corridas? ¿Es casualidad?","18 simulaciones · 10 semillas independientes · media ± IC 95%. Respaldo estadístico, no una corrida afortunada."],
["Resultados principales (memorizar)","Comandos 3 ms (≤20) · Vídeo 36 ms (≤150) · Jitter 0.28 ms · Throughput 40 Mbps · Disponibilidad 100%. TODOS cumplen."],
["¿Jitter 0.28 ms es creíble?","Sí. Enlace sin congestión = jitter mínimo (deseable). Medido con resolución fina 0.05 ms. Vídeo VBR H.264 aporta jitter realista."],
["¿Estrés de vídeo 50 Mbps falla?","No falla. Comandos suben a 6.8 ms (< 20). Demuestra margen de dimensionamiento + la priorización WMM protege el tráfico crítico."],
["¿Cuánto cuesta?","Sin cifra (no invento sin cotización). Inversión incremental sobre infra existente. Retorno: menos accidentes + continuidad. Cuantificar = futuro."],
["¿Cumple normativa peruana?","Sí. 5 GHz uso libre (MTC) · D.S. 024-2016-EM (control de ingeniería) · Ley 29733 (datos del vídeo)."],
["¿Limitación: solo simulación?","Alcance DECLARADO: tesis de gabinete. Diseño trazable y reproducible, validado vs survey real. Campo = trabajo futuro. Honestidad = rigor."],
["¿Solo un LHD?","Sí, alcance definido desde Cap. 1. Arquitectura escalable; multi-vehículo exige recalcular capacidad/interferencia = trabajo futuro."],
["Si rehicieras la tesis, ¿qué cambias?","Mediciones de campo propias + ray-tracing 3D para validación independiente + multi-vehículo. (= mis recomendaciones)."],
["¿Por qué importa para el Perú?","Minería subterránea peruana: accidentes fatales cada año. Sacar al operador del riesgo = camino replicable y de bajo costo a minería más segura."],
];

cards.forEach((c,i)=>{
  const s = p.addSlide(); s.background={ color: BL };
  s.addText(`Tarjeta ${i+1} / ${cards.length}`, { x:11.4, y:0.3, w:1.6, h:0.4, align:"right", fontFace:F_B, fontSize:12, color:GRIS, bold:true });
  // pregunta (bloque azul arriba)
  s.addShape(p.ShapeType.roundRect, { x:0.8, y:1.2, w:11.7, h:2.5, rectRadius:0.1, fill:{ color:AZUL } });
  s.addText("PREGUNTA", { x:1.2, y:1.45, w:5, h:0.4, fontFace:F_B, fontSize:14, color:CEL, bold:true, charSpacing:2 });
  s.addText(c[0], { x:1.2, y:1.9, w:10.9, h:1.6, fontFace:F_H, fontSize:26, color:BL, bold:true, valign:"middle" });
  // respuesta clave (bloque hielo abajo)
  s.addShape(p.ShapeType.roundRect, { x:0.8, y:4.0, w:11.7, h:2.9, rectRadius:0.1, fill:{ color:HIELO }, line:{ color:VERDE, width:1.5 } });
  s.addText("LO QUE DEBO RECORDAR", { x:1.2, y:4.25, w:6, h:0.4, fontFace:F_B, fontSize:14, color:VERDE, bold:true, charSpacing:2 });
  s.addText(c[1], { x:1.2, y:4.75, w:10.9, h:1.9, fontFace:F_B, fontSize:20, color:INK, valign:"top", lineSpacingMultiple:1.15 });
});

p.writeFile({ fileName: "C:/Users/Adrian Lopez/Documents/tesis_proyecto/fase4/presentacion/flashcards_jurado.pptx" }).then(f=>console.log("OK:", f));

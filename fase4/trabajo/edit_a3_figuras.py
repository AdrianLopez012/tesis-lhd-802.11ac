# -*- coding: utf-8 -*-
# ETAPA A3 — Reemplazo de imágenes: Figura 9 (geometría) y Figura 10 (escenarios)
# Localiza los drawings por proximidad a sus captions, reemplaza el blob de la
# imagen y ajusta la altura del extent para conservar la proporción de la nueva.
import docx, sys, struct
sys.stdout.reconfigure(encoding="utf-8")

DOC = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
GS  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"

def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    w, h = struct.unpack(">II", head[16:24])
    return w, h

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}

d = docx.Document(DOC)

# localizar párrafos con drawing en el rango del Cap. 3 y mapear a captions
drawings = []
for i, p in enumerate(d.paragraphs):
    if 700 <= i <= 815:
        blips = p._element.findall(".//a:blip", NS)
        if blips:
            rid = blips[0].get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
            drawings.append((i, rid, p))
print("drawings en Cap.3:", [(i, r) for i, r, _ in drawings])

# el caption de Figura 9 es el párrafo 770; el de Figura 10 es el 802.
# el drawing correspondiente es el drawing más cercano ANTERIOR al caption.
def drawing_antes_de(caption_idx):
    cand = [t for t in drawings if t[0] < caption_idx]
    return cand[-1] if cand else None

reemplazos = [
    (770, rf"{GS}\plano_nv1640_pro.png",        "Figura 9"),
    (802, rf"{GS}\resultados_escenarios.png",   "Figura 10"),
]

for cap_idx, newimg, label in reemplazos:
    hit = drawing_antes_de(cap_idx)
    if not hit:
        print(f"{label}: NO se encontró drawing antes del caption {cap_idx}"); continue
    pi, rid, p = hit
    part = d.part.related_parts[rid]
    with open(newimg, "rb") as f:
        blob = f.read()
    part._blob = blob
    # ajustar proporción del extent manteniendo el ancho
    w_px, h_px = png_size(newimg)
    for ext in p._element.findall(".//wp:extent", NS) + p._element.findall(".//a:ext", NS):
        cx = int(ext.get("cx"))
        ext.set("cy", str(int(cx * h_px / w_px)))
    print(f"{label}: drawing en parrafo {pi} (rId {rid}) -> {newimg.split(chr(92))[-1]} ({w_px}x{h_px})")

d.save(DOC)
print("figuras reemplazadas")

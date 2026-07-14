# -*- coding: utf-8 -*-
# Corrige tablas que desbordan: reescala anchos de columna al ancho útil
# y activa autofit a ventana. No toca contenido.
import docx, sys
sys.stdout.reconfigure(encoding="utf-8")
from docx.oxml.ns import qn
DOC = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
d = docx.Document(DOC)
s = d.sections[-1]
util = int(s.page_width - s.left_margin - s.right_margin)

def ancho_tabla(t):
    return sum((c.width or 0) for c in t.rows[0].cells)

corregidas = 0
for ti, t in enumerate(d.tables):
    w = ancho_tabla(t)
    if not w or w <= util * 1.02:
        continue
    factor = util / w
    print(f"tabla {ti} ({t.cell(0,0).text.strip()[:35]!r}): {w/914400:.2f}in -> {util/914400:.2f}in")
    for row in t.rows:
        for c in row.cells:
            if c.width:
                c.width = int(c.width * factor)
    # tblW a ancho útil exacto en DXA
    tblPr = t._element.tblPr
    tblW = tblPr.find(qn('w:tblW'))
    if tblW is None:
        tblW = tblPr.makeelement(qn('w:tblW'), {})
        tblPr.append(tblW)
    tblW.set(qn('w:w'), str(int(util / 914400 * 1440)))
    tblW.set(qn('w:type'), 'dxa')
    corregidas += 1

d.save(DOC)
print(f"{corregidas} tablas reescaladas al ancho de página")

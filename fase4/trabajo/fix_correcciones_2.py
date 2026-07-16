# -*- coding: utf-8 -*-
# Correcciones parte 2: añadir "Fuente: Elaboración propia." a tablas y figuras
# del CUERPO que no tienen fuente (excluye entradas de índice).
# Tablas: la fuente va DEBAJO de la tabla. Figuras: tras el caption (debajo).
import docx, sys, re, copy
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")

F = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
d = docx.Document(F)
body = d.element.body

def ptext(el):
    if el is None or el.tag != qn('w:p'): return ''
    return ''.join(t.text or '' for t in el.iter(qn('w:t')))

def es_indice(el):
    # entrada de índice: termina en tab + número de página, o estilo TDC/TOC
    t = ptext(el)
    if re.search(r'\t\d+\s*$', t): return True
    ppr = el.find(qn('w:pPr'))
    if ppr is not None:
        st = ppr.find(qn('w:pStyle'))
        if st is not None and ('TDC' in (st.get(qn('w:val')) or '') or 'Tabla' in (st.get(qn('w:val')) or '') or 'ndice' in (st.get(qn('w:val')) or '').lower()):
            return True
    return False

def crear_fuente(referencia_p):
    """crea un párrafo 'Fuente: Elaboración propia.' copiando el formato del caption"""
    nuevo = copy.deepcopy(referencia_p)
    # borrar todos los runs y campos, dejar solo la estructura pPr
    for child in list(nuevo):
        if child.tag != qn('w:pPr'):
            nuevo.remove(child)
    # crear run con el texto
    r = nuevo.makeelement(qn('w:r'), {})
    rpr = r.makeelement(qn('w:rPr'), {})
    it = r.makeelement(qn('w:i'), {})
    sz = r.makeelement(qn('w:sz'), {qn('w:val'): '20'})   # 10 pt
    rpr.append(it); rpr.append(sz)
    r.append(rpr)
    t = r.makeelement(qn('w:t'), {})
    t.text = 'Fuente: Elaboración propia.'
    r.append(t)
    nuevo.append(r)
    return nuevo

els = list(body)
n_tab = n_fig = 0
i = 0
while i < len(els):
    el = els[i]
    t = ptext(el).strip()
    m = re.match(r'^(Tabla|Figura)\b', t)
    if m and len(t) > 8 and not es_indice(el):
        # ¿ya hay fuente en el caption o cerca?
        contexto = t
        for k in range(1, 4):
            if i+k < len(els): contexto += ' ' + ptext(els[i+k])
        if not re.search(r'Fuente|Adaptad|Tomad|Elaboraci', contexto, re.I):
            if m.group(1) == 'Tabla':
                # buscar la tabla siguiente y poner la fuente después de ella
                k = i+1
                while k < len(els) and els[k].tag != qn('w:tbl'): k += 1
                if k < len(els):
                    fu = crear_fuente(el)
                    els[k].addnext(fu)
                    n_tab += 1
            else:
                fu = crear_fuente(el)
                el.addnext(fu)
                n_fig += 1
        els = list(body)  # refrescar tras insertar
    i += 1

print(f"fuentes añadidas: {n_tab} tablas + {n_fig} figuras")
d.save(F)
print("GUARDADO OK")

# -*- coding: utf-8 -*-
# Correcciones parte 5: REDUCCIÓN DE PÁGINAS.
#  (1) Quitar el sectPr suelto incrustado en la referencia [24] (salto de página
#      en plena bibliografía que deja la [27] sola en una página).
#  (2) Asegurar titlePg + primera página sin folio en la sección final fusionada.
#  (3) Mover Tablas 7, 8 y 9 (detalle RSL, Cap. 2) a un nuevo "Anexo I",
#      renombradas Tabla I.1/I.2/I.3 (sin SEQ), con frases puente en el Cap. 2.
#  (4) Renumerar referencias en prosa: Tabla N -> N-3 para N>=10.
import docx, sys, re, copy
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")

F = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
d = docx.Document(F)
body = d.element.body

def ptext(el):
    if el is None or el.tag != qn('w:p'): return ''
    return ''.join(t.text or '' for t in el.iter(qn('w:t')))

# ---------- (1) sectPr suelto en [24] ----------
for el in list(body):
    t = ptext(el).strip()
    if t.startswith('[24] '):
        ppr = el.find(qn('w:pPr'))
        spr = ppr.find(qn('w:sectPr')) if ppr is not None else None
        if spr is not None:
            ppr.remove(spr)
            print("[1] sectPr suelto eliminado de la referencia [24]")
        break

# ---------- (3) mover Tablas 7, 8, 9 al nuevo Anexo I ----------
els = list(body)
def bloque(caption_regex):
    """devuelve [caption, tabla, fuente?] del cuerpo (no índice)"""
    for j, el in enumerate(els):
        t = ptext(el).strip()
        if re.match(caption_regex, t) and not re.search(r'\d+\s*$', t[-4:]):
            blk = [el]
            if j+1 < len(els) and els[j+1].tag == qn('w:tbl'):
                blk.append(els[j+1])
                if j+2 < len(els) and ptext(els[j+2]).strip().startswith('Fuente'):
                    blk.append(els[j+2])
                return j, blk
    return None, None

def caption_plana(p_el, nuevo_texto):
    """reemplaza el contenido del caption por texto plano (sin SEQ)"""
    for child in list(p_el):
        if child.tag != qn('w:pPr'):
            p_el.remove(child)
    r = p_el.makeelement(qn('w:r'), {})
    rpr = r.makeelement(qn('w:rPr'), {})
    b = r.makeelement(qn('w:b'), {})
    rpr.append(b); r.append(rpr)
    t = r.makeelement(qn('w:t'), {})
    t.text = nuevo_texto
    r.append(t)
    p_el.append(r)

def parrafo(texto, estilo=None, negrita=False):
    p = body.makeelement(qn('w:p'), {})
    if estilo:
        ppr = p.makeelement(qn('w:pPr'), {})
        st = p.makeelement(qn('w:pStyle'), {qn('w:val'): estilo})
        ppr.append(st); p.append(ppr)
    r = p.makeelement(qn('w:r'), {})
    if negrita:
        rpr = r.makeelement(qn('w:rPr'), {}); rpr.append(r.makeelement(qn('w:b'), {})); r.append(rpr)
    t = r.makeelement(qn('w:t'), {}); t.text = texto; r.append(t)
    p.append(r)
    return p

movidos = []
info = [
    (r'^Tabla 7 Strings de búsqueda', 'Tabla I.1. Strings de búsqueda utilizados en la RSL.',
     'Las cadenas de búsqueda completas utilizadas en la revisión se detallan en el Anexo I (Tabla I.1).'),
    (r'^Tabla 8 Estudios primarios', 'Tabla I.2. Estudios primarios núcleo de la revisión.', None),
    (r'^Tabla 9 Estudios secundarios', 'Tabla I.3. Estudios secundarios, revisiones y whitepapers de apoyo.', None),
]
for rgx, nuevo_cap, puente in info:
    els = list(body)
    j, blk = bloque(rgx)
    if blk is None:
        print(f"  NO ENCONTRADO: {rgx}"); continue
    # frase puente en el lugar original (solo para Tabla 7; 8 y 9 comparten la de 2.2.3)
    if puente:
        blk[0].addprevious(parrafo(puente))
    for el in blk:
        body.remove(el)
    caption_plana(blk[0], nuevo_cap)
    movidos.append(blk)
    print(f"  movido: {nuevo_cap}")

# reescribir la introducción de la subsección 2.2.3 como puente a Anexo I
for el in list(body):
    t = ptext(el).strip()
    if t.startswith('Para transparentar la trazabilidad de la RSL'):
        for child in list(el):
            if child.tag != qn('w:pPr'): el.remove(child)
        r = el.makeelement(qn('w:r'), {})
        tt = el.makeelement(qn('w:t'), {})
        tt.text = ('Para transparentar la trazabilidad de la RSL, las matrices completas de '
                   'estudios primarios y de estudios secundarios, revisiones y whitepapers de '
                   'apoyo se consolidan en el Anexo I (Tablas I.2 e I.3), preservando en este '
                   'capítulo únicamente su síntesis interpretativa.')
        r.append(tt); el.append(r)
        print("  puente 2.2.3 reescrito hacia Anexo I")
        break

# insertar el Anexo I al FINAL (antes del sectPr final del body)
spr_final = body[-1]
assert spr_final.tag == qn('w:sectPr')
anexoI = [
    parrafo('Anexo I. Detalle de la revisión sistemática de literatura', estilo='Ttulo2'),
    parrafo('Este anexo consolida el detalle metodológico de la revisión sistemática de '
            'literatura del Capítulo 2: las cadenas de búsqueda utilizadas y las matrices '
            'completas de estudios primarios y secundarios seleccionados.'),
]
for blk in movidos:
    anexoI.extend(blk)
    anexoI.append(parrafo(''))
for el in anexoI:
    spr_final.addprevious(el)
print(f"[3] Anexo I insertado con {len(movidos)} tablas")

# ---------- (4) renumerar referencias en prosa (N>=10 -> N-3) ----------
n_ren = 0
for p in d.paragraphs:
    t = p.text.strip()
    if re.match(r'^(Tabla|Figura)\b', t): continue          # caption
    if re.search(r'\t\d+\s*$', p.text): continue            # índice
    if 'Tabla' not in p.text: continue
    for r in p.runs:
        if 'Tabla' in (r.text or ''):
            def rep(m):
                n = int(m.group(1))
                return f'Tabla {n-3}' if n >= 10 else m.group(0)
            nuevo = re.sub(r'Tabla\s+(\d+)', rep, r.text)
            if nuevo != r.text:
                r.text = nuevo; n_ren += 1
print(f"[4] referencias en prosa renumeradas: {n_ren}")

d.save(F)
print("GUARDADO OK")

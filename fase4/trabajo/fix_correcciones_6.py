# -*- coding: utf-8 -*-
# Reducción final: mover a anexos (aprobado por el usuario)
#   1) §2.3 contenido (formalización matemática, 13 ecuaciones + tabla propagación) -> Anexo J
#   2) §3.5 contenido (vinculación competencias + tabla) -> Anexo K
#   3) Tabla áreas académicas PUCP (Cap 1) -> Anexo K
#   4) Tabla matriz normativa (Cap 4) -> Anexo K
# Los headings 2.3 y 3.5 SE QUEDAN con párrafo síntesis (no se desnumeran secciones).
# Renumeración de referencias en prosa ANTES de mover.
import docx, sys, re
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")

F = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
d = docx.Document(F)
body = d.element.body

def ptext(el):
    if el is None or el.tag != qn('w:p'): return ''
    return ''.join(t.text or '' for t in el.iter(qn('w:t')))

def parrafo(texto, estilo=None):
    p = body.makeelement(qn('w:p'), {})
    if estilo:
        ppr = p.makeelement(qn('w:pPr'), {})
        st = p.makeelement(qn('w:pStyle'), {qn('w:val'): estilo})
        ppr.append(st); p.append(ppr)
    r = p.makeelement(qn('w:r'), {})
    t = p.makeelement(qn('w:t'), {}); t.text = texto
    r.append(t); p.append(r)
    return p

def caption_plana(p_el, nuevo_texto):
    for child in list(p_el):
        if child.tag != qn('w:pPr'):
            p_el.remove(child)
    r = p_el.makeelement(qn('w:r'), {})
    rpr = r.makeelement(qn('w:rPr'), {}); rpr.append(r.makeelement(qn('w:b'), {})); r.append(rpr)
    t = r.makeelement(qn('w:t'), {}); t.text = nuevo_texto
    r.append(t); p_el.append(r)

# ============ PASO 0: renumerar referencias en prosa (antes de mover) ============
MAPEO = {1:'K.1', 7:'J.1', 21:'K.2', 23:'K.3',
         2:'1',3:'2',4:'3',5:'4',6:'5',8:'6',9:'7',10:'8',11:'9',12:'10',13:'11',
         14:'12',15:'13',16:'14',17:'15',18:'16',19:'17',20:'18',22:'19',24:'20',
         25:'21',26:'22',27:'23'}
n_ren = 0
for p in d.paragraphs:
    t = p.text.strip()
    if re.match(r'^(Tabla|Figura|Ecuación)\b', t): continue
    if re.search(r'\t[ivx0-9]+\s*$', p.text): continue
    if 'Tabla' not in p.text: continue
    for r in p.runs:
        if 'Tabla' in (r.text or ''):
            def rep(m):
                n = int(m.group(1))
                return f'Tabla {MAPEO[n]}' if n in MAPEO else m.group(0)
            nuevo = re.sub(r'Tabla\s+(\d+)', rep, r.text)
            if nuevo != r.text: r.text = nuevo; n_ren += 1
print(f"[0] referencias en prosa actualizadas: {n_ren}")

# ============ PASO 1: localizar límites (de nuevo, tras renumerar) ============
els = list(body)
idx = {}
for j, el in enumerate(els):
    t = ptext(el).strip()
    for h in ['2.3 Fundamentos','2.4 Síntesis','3.5 Vinculación','Capítulo 4.']:
        if t.startswith(h) and h not in idx: idx[h] = j
    if re.match(r'^Tabla \d+\.?\s*Áreas académicas', t) and el.getnext() is not None and el.getnext().tag == qn('w:tbl'):
        idx['tab_areas'] = j
    if re.match(r'^Tabla \d+\.?\s*Matriz normativa', t):
        idx['tab_norma'] = j
print(f"[1] hitos: { {k: v for k, v in idx.items()} }")

# ---- bloque §2.3: contenido tras el heading, hasta antes de 2.4 ----
blk23 = els[idx['2.3 Fundamentos']+1 : idx['2.4 Síntesis']]
# ---- bloque §3.5: contenido tras el heading, hasta antes del sectPr/Cap4 ----
fin35 = idx['Capítulo 4.']
# excluir el párrafo de salto de sección (vacío con sectPr) justo antes de Cap4
while True:
    cand = els[fin35-1]
    ppr = cand.find(qn('w:pPr')) if cand.tag == qn('w:p') else None
    if ppr is not None and ppr.find(qn('w:sectPr')) is not None:
        fin35 -= 1; continue
    break
blk35 = els[idx['3.5 Vinculación']+1 : fin35]
# ---- tabla áreas: caption + tbl + fuente ----
ja = idx['tab_areas']
blkA = [els[ja], els[ja+1]]
if ptext(els[ja+2]).strip().startswith('Fuente'): blkA.append(els[ja+2])
# ---- tabla normativa ----
jn = idx['tab_norma']
blkN = [els[jn], els[jn+1]]
if ptext(els[jn+2]).strip().startswith('Fuente'): blkN.append(els[jn+2])

print(f"[1] §2.3: {len(blk23)} elementos | §3.5: {len(blk35)} | áreas: {len(blkA)} | normativa: {len(blkN)}")

# ============ PASO 2: punteros en los huecos ============
els[idx['2.3 Fundamentos']].addnext(parrafo(
    'Esta sección se apoya en la formalización matemática y física del canal de '
    'propagación (Ecuaciones 1 a 13 y parámetros adoptados), cuyo desarrollo completo '
    'se presenta en el Anexo J. De dicho desarrollo se desprenden los resultados '
    'operativos utilizados en el diseño: el modelo two-slope con distancia de quiebre, '
    'el presupuesto de enlace en 5 GHz y las cotas de capacidad y latencia extremo a extremo.'))
els[idx['3.5 Vinculación']].addnext(parrafo(
    'La matriz de vinculación entre el diseño desarrollado y las competencias '
    'profesionales del programa se consolida en el Anexo K (Tabla K.2).'))
blkA[0].addprevious(parrafo(
    'La relación de áreas académicas del plan de estudios vinculadas a esta tesis se '
    'presenta en el Anexo K (Tabla K.1).'))
blkN[0].addprevious(parrafo(
    'La matriz normativa completa y su implicancia para el diseño se consolidan en el '
    'Anexo K (Tabla K.3).'))

# ============ PASO 3: extraer bloques ============
for blk in (blk23, blk35, blkA, blkN):
    for el in blk:
        body.remove(el)

# renombrar captions de tablas movidas (sin SEQ)
def renombrar_caption_en(blk, regex, nuevo):
    for el in blk:
        if re.match(regex, ptext(el).strip()):
            caption_plana(el, nuevo); return True
    return False
renombrar_caption_en(blk23, r'^Tabla \d+', 'Tabla J.1. Parámetros de propagación reportados y adoptados para el modelo del canal.')
renombrar_caption_en(blk35, r'^Tabla \d+', 'Tabla K.2. Competencias técnicas evidenciadas en el diseño de la solución.')
caption_plana(blkA[0], 'Tabla K.1. Áreas académicas de Ingeniería de las Telecomunicaciones PUCP relacionadas con la tesis.')
caption_plana(blkN[0], 'Tabla K.3. Matriz normativa aplicable y su implicancia para el diseño.')

# renombrar sub-headings 2.3.x -> J.x dentro del bloque movido
for el in blk23:
    t = ptext(el).strip()
    m = re.match(r'^2\.3\.(\d+)\s+(.*)', t)
    if m:
        caption_plana(el, f'J.{m.group(1)} {m.group(2)}')
        # mantener estilo de heading si lo tenia (caption_plana ya conserva pPr)

# ============ PASO 4: construir Anexos J y K al final ============
spr_final = body[-1]
assert spr_final.tag == qn('w:sectPr')
nuevos = []
nuevos.append(parrafo('Anexo J. Fundamentos teóricos del canal de propagación: formalización matemática y física', estilo='Ttulo2'))
nuevos.append(parrafo('Este anexo desarrolla la formalización matemática y física del canal de '
                      'propagación que sustenta el diseño del Capítulo 3, relocalizada desde la '
                      'sección 2.3 del cuerpo del documento: presupuesto de latencia, modelos de '
                      'espacio libre y log-distancia, propagación modal en túnel, presupuesto de '
                      'enlace y cotas de capacidad.'))
nuevos.extend(blk23)
nuevos.append(parrafo(''))
nuevos.append(parrafo('Anexo K. Vinculación académica, profesional y normativa', estilo='Ttulo2'))
nuevos.append(parrafo('Este anexo consolida las matrices de vinculación académica y profesional de '
                      'la tesis y la matriz normativa aplicable al diseño.'))
nuevos.extend(blkA)
nuevos.append(parrafo(''))
nuevos.extend(blk35)
nuevos.append(parrafo(''))
nuevos.extend(blkN)
for el in nuevos:
    spr_final.addprevious(el)
print(f"[4] Anexo J ({len(blk23)} elems) y Anexo K ({len(blkA)+len(blk35)+len(blkN)} elems) insertados")

d.save(F)
print("GUARDADO OK")

# -*- coding: utf-8 -*-
# Devolver §2.3 (formalización matemática) al cuerpo, DEJANDO la Tabla J.1
# (parámetros de propagación) en el Anexo J. Aterrizar en ~100 páginas.
#  - quitar el párrafo puntero tras el heading 2.3
#  - devolver el contenido (ecuaciones, prosa, sub-headings J.x -> 2.3.x)
#  - Anexo J queda solo con la Tabla J.1 + intro reescrita
import docx, sys, re
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")

F = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
d = docx.Document(F)
body = d.element.body

def ptext(el):
    if el is None or el.tag != qn('w:p'): return ''
    return ''.join(t.text or '' for t in el.iter(qn('w:t')))

def set_texto(p_el, texto):
    for child in list(p_el):
        if child.tag != qn('w:pPr'):
            p_el.remove(child)
    r = p_el.makeelement(qn('w:r'), {})
    t = p_el.makeelement(qn('w:t'), {}); t.text = texto
    r.append(t); p_el.append(r)

els = list(body)
# ---- localizar ----
i23 = next(j for j, el in enumerate(els) if ptext(el).strip().startswith('2.3 Fundamentos'))
iJ  = next(j for j, el in enumerate(els) if ptext(el).strip().startswith('Anexo J.'))
iK  = next(j for j, el in enumerate(els) if ptext(el).strip().startswith('Anexo K.'))

# ---- puntero tras 2.3 (lo quitamos) ----
puntero = els[i23+1]
assert 'formalización matemática' in ptext(puntero), 'puntero no encontrado'

# ---- contenido del Anexo J: heading(iJ), intro(iJ+1), contenido(iJ+2 .. iK) ----
contenido = els[iJ+2 : iK]
# separar el bloque de la tabla J.1 (caption + tbl + fuente) del resto
volver, quedar = [], []
k = 0
while k < len(contenido):
    el = contenido[k]
    if re.match(r'^Tabla J\.1\.', ptext(el).strip()):
        quedar.append(el)                     # caption
        if k+1 < len(contenido) and contenido[k+1].tag == qn('w:tbl'):
            quedar.append(contenido[k+1]); k += 1
        if k+1 < len(contenido) and ptext(contenido[k+1]).strip().startswith('Fuente'):
            quedar.append(contenido[k+1]); k += 1
    else:
        volver.append(el)
    k += 1
# quitar párrafos vacíos al final del bloque que vuelve
while volver and ptext(volver[-1]).strip() == '' and volver[-1].tag == qn('w:p'):
    volver.pop()
print(f'vuelven al cuerpo: {len(volver)} elementos | quedan en Anexo J: {len(quedar)}')

# ---- sub-headings J.x -> 2.3.x en lo que vuelve ----
n_sh = 0
for el in volver:
    t = ptext(el).strip()
    m = re.match(r'^J\.(\d+)\s+(.*)', t)
    if m:
        set_texto(el, f'2.3.{m.group(1)} {m.group(2)}'); n_sh += 1
print(f'sub-headings restaurados: {n_sh}')

# ---- mover: sacar del anexo, insertar tras el heading 2.3 (quitando el puntero) ----
for el in volver:
    body.remove(el)
body.remove(puntero)
ancla = els[i23]      # heading 2.3
for el in reversed(volver):
    ancla.addnext(el)

# ---- reescribir intro del Anexo J ----
intro_J = els[iJ+1]
set_texto(intro_J,
    'Este anexo consolida los parámetros de propagación reportados en la literatura '
    'y los valores adoptados para el modelo del canal de la sección 2.3, como respaldo '
    'documental del presupuesto de enlace del Capítulo 3.')
set_texto(els[iJ], 'Anexo J. Parámetros de propagación del modelo de canal')
# mantener estilo del heading (set_texto conserva pPr)

# ---- en el cuerpo §2.3: donde estaba la tabla, dejar puntero a J.1 si no existe ----
# (la referencia en prosa '(Tabla J.1)' ya existe; añadimos frase solo si no hay mención)
tiene_ref = any('Tabla J.1' in ptext(el) for el in volver)
print(f'referencia a Tabla J.1 en el cuerpo devuelto: {tiene_ref}')
if not tiene_ref:
    # añadir frase al final del bloque devuelto
    p = body.makeelement(qn('w:p'), {})
    r = p.makeelement(qn('w:r'), {}); t = p.makeelement(qn('w:t'), {})
    t.text = 'Los parámetros adoptados para el modelo se consolidan en el Anexo J (Tabla J.1).'
    r.append(t); p.append(r)
    volver[-1].addnext(p)

d.save(F)
print('GUARDADO OK')

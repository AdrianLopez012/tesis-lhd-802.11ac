# -*- coding: utf-8 -*-
# Reemplaza "v3-REAL" (nombre interno de versión) por "modelo de simulación NS-3"
# de forma gramaticalmente natural. NO toca los nombres de archivo reales
# (lhd-teleop-v3-real.cc) ni los volcados de código de los anexos.
import docx, re, sys
sys.stdout.reconfigure(encoding="utf-8")
DOC = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
d = docx.Document(DOC)

# reemplazos contextuales (orden importa: de más específico a más general)
SUBS = [
    # inglés (abstract)
    (r"Results from version v3-REAL, obtained", "Results from the NS-3 simulation model, obtained"),
    (r"version v3-REAL", "the NS-3 simulation model"),
    # español — construcciones frecuentes
    (r"prototipo ns-3 v3-REAL", "modelo de simulación NS-3"),
    (r"del prototipo ns-3 v3-REAL", "del modelo de simulación NS-3"),
    (r"prototipo\s*\(v3-REAL\)", "modelo de simulación NS-3"),
    (r"del prototipo v3-REAL", "del modelo de simulación NS-3"),
    (r"simulación del prototipo v3-REAL", "simulación del modelo NS-3"),
    (r"batería v3-REAL", "batería de simulación NS-3"),
    (r"la versión v3-REAL, obtenidos", "el modelo de simulación NS-3, con resultados obtenidos"),
    (r"La versión v3-REAL, ejecutada", "El modelo de simulación NS-3, ejecutado"),
    (r"versión v3-REAL", "modelo de simulación NS-3"),
    # genérico restante (por si queda alguno) — NO afecta nombres de archivo .cc
    (r"prototipo v3-REAL", "modelo de simulación NS-3"),
    (r"v3-REAL", "NS-3"),
    # "corridas" -> "ejecuciones" (formal). El nombre del archivo
    # lhd-teleop-v3-real.cc SE CONSERVA (nombre real del código; decisión del usuario).
    (r"\bcorridas\b", "ejecuciones"),
    (r"\bcorrida\b", "ejecución"),
]

def es_codigo(p):
    return p.style.name == "CodigoFuente" or "0001 |" in p.text[:8] or ".cc" in p.text and "|" in p.text

def tocar(texto):
    # proteger el nombre real del archivo (que contiene "v3-real")
    texto = texto.replace("lhd-teleop-v3-real.cc", "\x00CC\x00")
    for pat, rep in SUBS:
        texto = re.sub(pat, rep, texto)
    return texto.replace("\x00CC\x00", "lhd-teleop-v3-real.cc")

n_par = 0
# cuerpo (NO tocar los volcados de código de los anexos: ahí el nombre del
# archivo y el contenido deben quedar EXACTOS como el archivo real renombrado,
# que se maneja aparte con git mv + regeneración)
for p in d.paragraphs:
    if es_codigo(p):
        continue
    orig = p.text
    if not re.search(r"v3-REAL|v3-real|corrida", orig, re.I):
        continue
    tmp = tocar(orig)
    if tmp != orig and p.runs:
        p.runs[0].text = tmp
        for r in p.runs[1:]:
            r.text = ""
        n_par += 1

for t in d.tables:
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                if es_codigo(p): continue
                if not re.search(r"v3-REAL|v3-real|corrida", p.text, re.I): continue
                tmp = tocar(p.text)
                if tmp != p.text and p.runs:
                    p.runs[0].text = tmp
                    for r in p.runs[1:]: r.text = ""
                    n_par += 1

d.save(DOC)
print(f"{n_par} párrafos/celdas actualizados")
# verificar residuos (excluyendo nombres de archivo .cc)
d2 = docx.Document(DOC)
resid = []
for p in d2.paragraphs:
    if p.style.name == "CodigoFuente" or "0001 |" in p.text[:8]: continue
    for m in re.finditer(r"v3-REAL", p.text):
        ctx = p.text[max(0,m.start()-15):m.start()+10]
        if ".cc" not in ctx and "lhd-teleop" not in ctx:
            resid.append(ctx)
print("residuos en texto (no archivo):", resid if resid else "NINGUNO")

# -*- coding: utf-8 -*-
# AUDITORÍA-FIX v2: renumera los captions de TABLA a su valor de secuencia real
# (1,2,3,...30 por orden de aparición) y ajusta las referencias de texto que
# apuntaban a números viejos. Todo manual, coherente con las referencias.
import docx, re, sys
sys.stdout.reconfigure(encoding="utf-8")
DOC = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
d = docx.Document(DOC)

# 1) recolectar captions en orden y su número actual -> número correcto
caps = []
for i, p in enumerate(d.paragraphs):
    if p.style.name == "Caption" and re.match(r"\s*Tabla\s*\d+", p.text.strip()):
        m = re.match(r"\s*Tabla\s*(\d+)", p.text.strip())
        caps.append((i, int(m.group(1))))

# número correcto = posición secuencial
remap = {}   # (indice_parrafo) -> (viejo, nuevo)
for pos, (i, viejo) in enumerate(caps, start=1):
    remap[i] = (viejo, pos)

# 2) construir mapa viejo->nuevo SOLO donde cambia y es inequívoco.
# Como hay números viejos repetidos (16,20,21,22), NO podemos remapear
# referencias de texto por número a ciegas. Estrategia segura:
#  - renumerar los CAPTIONS por posición (siempre correcto).
#  - para las referencias de TEXTO, corregir solo las que apuntan a una tabla
#    cuyo número viejo era ÚNICO y cambió (evita ambigüedad).
viejo_count = {}
for _, (v, _) in remap.items():
    viejo_count[v] = viejo_count.get(v, 0) + 1

# aplicar renumeración a captions
nch = 0
for i, (viejo, nuevo) in remap.items():
    if viejo == nuevo:
        continue
    p = d.paragraphs[i]
    nuevo_txt = re.sub(r"(\s*Tabla\s*)\d+", rf"\g<1>{nuevo}", p.text, count=1)
    p.runs[0].text = nuevo_txt
    for r in p.runs[1:]:
        r.text = ""
    nch += 1
    print(f"  caption [{i}] Tabla {viejo} -> {nuevo}")

# 3) referencias de texto: las 4 referencias reales del documento ([787] T16,
# [871] T23, [874] T25, [893] T26) YA apuntan al número FINAL correcto por
# contenido (verificado a mano), así que NO se remapean automáticamente para
# evitar romperlas. El remapeo automático queda DESACTIVADO.
ref_map = {}
print(f"\n  referencias de texto remapeables (número viejo único): {ref_map}")
# aplicar a párrafos de texto (no captions, no índice, no código)
nref = 0
for i, p in enumerate(d.paragraphs):
    if p.style.name in ("Caption", "table of figures", "CodigoFuente"):
        continue
    if "0001 |" in p.text[:8]:
        continue
    def repl(m):
        n = int(m.group(1))
        return f"Tabla {ref_map[n]}" if n in ref_map else m.group(0)
    nuevo = re.sub(r"Tabla (\d+)", repl, p.text)
    if nuevo != p.text and p.runs:
        p.runs[0].text = nuevo
        for r in p.runs[1:]:
            r.text = ""
        nref += 1
        print(f"  ref texto [{i}] actualizada")

d.save(DOC)
print(f"\n{nch} captions renumerados, {nref} referencias de texto ajustadas")
print("REVISAR MANUAL: refs a Tablas cuyo número viejo estaba duplicado (16/20/21/22)")

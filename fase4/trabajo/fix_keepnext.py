# -*- coding: utf-8 -*-
# Fix de títulos huérfanos: activa keep_with_next en headings y captions para que
# ningún título quede solo al pie de página separado de su contenido.
import docx, sys
sys.stdout.reconfigure(encoding="utf-8")
DOC = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
d = docx.Document(DOC)
n = 0
for p in d.paragraphs:
    st = p.style.name
    if st.startswith("Heading") or st in ("Title", "Caption") or p.text.strip() in (
        "RECOMENDACIONES Y OBSERVACIONES", "CONCLUSIONES", "REFERENCIAS BIBLIOGRÁFICAS"):
        pf = p.paragraph_format
        if not pf.keep_with_next:
            pf.keep_with_next = True
            n += 1
d.save(DOC)
print(f"keep_with_next activado en {n} párrafos (títulos y captions)")

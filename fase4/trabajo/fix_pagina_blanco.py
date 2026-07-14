# -*- coding: utf-8 -*-
# Fix hoja en blanco: donde un heading tiene A LA VEZ salto de sección (sectPr)
# y page_break_before=True, se produce DOBLE salto = página vacía. Se quita el
# page_break_before en esos casos (el sectPr ya empieza en página nueva).
import docx, sys
sys.stdout.reconfigure(encoding="utf-8")
DOC = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
d = docx.Document(DOC)
n = 0
for p in d.paragraphs:
    xml = p._element.xml
    tiene_sect = "w:sectPr" in xml
    if tiene_sect and p.paragraph_format.page_break_before:
        p.paragraph_format.page_break_before = False
        n += 1
        print(f"  quitado page_break_before (ya tenía sectPr): {p.text.strip()[:45]!r}")
d.save(DOC)
print(f"{n} dobles saltos corregidos")

# -*- coding: utf-8 -*-
import fitz, sys
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.pdf")
claves = ["Capítulo 1.", "Capítulo 2.", "Capítulo 3.", "Capítulo 4. Análisis",
          "CONCLUSIONES", "RECOMENDACIONES Y OBSERVACIONES", "REFERENCIAS BIBLIOGRÁFICAS",
          "Anexo A.", "Anexo B.", "Anexo C. Código", "Anexo D. Fuente única", "Anexo E.",
          "Anexo F. Evidencia numérica", "Anexo G. Evidencia gráfica", "Anexo H.",
          "lhd-teleop-v3-real.cc", "4.11 Conclusiones del capítulo", "Figura 11.",
          "Tabla 26.", "SHA-256"]
enc = {k: None for k in claves}
for i in range(len(doc)):
    t = doc[i].get_text()
    for k in claves:
        if enc[k] is None and k in t:
            enc[k] = i + 1
for k in claves:
    print(("OK   " if enc[k] else "FALTA") + f" pag {enc[k]}: {k}")

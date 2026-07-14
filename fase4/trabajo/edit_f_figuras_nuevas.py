# -*- coding: utf-8 -*-
# Inserta la escena 3D (MATLAB) en 3.4.1 y la arquitectura en 3.4.2 como
# Figuras 10 y 11, renumerando las figuras posteriores (+2) y las referencias.
import docx, re, sys
from docx.shared import Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
sys.stdout.reconfigure(encoding="utf-8")

DOC = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
TRB = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo"
GS  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"

d = docx.Document(DOC)

# 1) RENUMERAR primero (de mayor a menor para no pisar): Figura N -> N+2 para N>=10
pat = re.compile(r"Figura (\d+)")
cambios = 0
for p in d.paragraphs:
    if "Figura" not in p.text or not p.runs:
        continue
    if p.style.name == "table of figures":   # los índices se regeneran con Word
        continue
    nums = [int(n) for n in pat.findall(p.text)]
    if not any(n >= 10 for n in nums):
        continue
    nuevo = pat.sub(lambda m: f"Figura {int(m.group(1))+2}" if int(m.group(1)) >= 10 else m.group(0), p.text)
    if nuevo != p.text:
        p.runs[0].text = nuevo
        for r in p.runs[1:]: r.text = ""
        cambios += 1
print(f"renumeradas {cambios} menciones de Figura>=10 (+2)")

# 2) localizar anclas: párrafo tras el cual insertar en 3.4.1 y 3.4.2
i341 = i342 = None
for i, p in enumerate(d.paragraphs):
    t = p.text.strip()
    if t.startswith("3.4.1 Arquitectura física"): i341 = i
    if t.startswith("3.4.2 Arquitectura lógica"): i342 = i
assert i341 and i342, (i341, i342)
# fin de 3.4.1 = párrafo anterior al heading 3.4.2
CAPTION_STYLE = None
for p in d.paragraphs:
    if p.text.strip().startswith("Figura 9."):
        CAPTION_STYLE = p.style; break

def insertar_figura(ref_par, img, cap_lines, texto_previo, ancho=15.5):
    ref = ref_par
    tp = ref.insert_paragraph_before(texto_previo)
    fp = ref.insert_paragraph_before("")
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run().add_picture(img, width=Cm(ancho))
    for cl in cap_lines:
        cp = ref.insert_paragraph_before(cl)
        if CAPTION_STYLE: cp.style = CAPTION_STYLE

# figura 3D al FINAL de 3.4.1 (antes del heading 3.4.2)
insertar_figura(
    d.paragraphs[i342],
    rf"{TRB}\escena_mina_3d.png",
    ["Figura 10. Entorno tridimensional de la zona de producción: galerías, los 12 AP en sus posiciones reales y patrón de radiación de la antena del LHD.",
     "Fuente: Elaboración propia; patrón calculado con MATLAB Antenna Toolbox (hélice en modo axial, 5.0 GHz) sobre la geometría de la fuente única de datos."],
    "La Figura 10 presenta el entorno en tres dimensiones: las galerías de sección 4×4 m, la ubicación real de los doce AP y el patrón de radiación "
    "calculado de una antena helicoidal en modo axial —representativa de la antena embarcada del LHD—, ilustrando la relación espacial entre la "
    "infraestructura de acceso y el vehículo en la galería central.")

# arquitectura al FINAL de 3.4.2: siguiente heading tras 3.4.2 es 3.4.3
i343 = None
for i, p in enumerate(d.paragraphs):
    if p.text.strip().startswith("3.4.3 Flujos"): i343 = i; break
assert i343
insertar_figura(
    d.paragraphs[i343],
    rf"{GS}\arquitectura_red.png",
    ["Figura 11. Arquitectura de la solución en tres capas: centro de control, backbone óptico y malla de acceso inalámbrico con el LHD móvil.",
     "Fuente: Elaboración propia con los equipos y parámetros documentados del proyecto."],
    "La Figura 11 sintetiza la arquitectura en sus tres capas —centro de control, backbone de fibra óptica en anillo y malla de acceso InstaMesh— "
    "con los equipos considerados y las clases de servicio del tráfico de teleoperación.")

d.save(DOC)
print("figuras 10 (escena 3D) y 11 (arquitectura) insertadas")

# 3) verificación de numeración resultante
d2 = docx.Document(DOC)
caps = [p.text.strip()[:72] for p in d2.paragraphs if re.match(r"^Figura \d+\.", p.text.strip())]
for c in caps: print(" ", c)

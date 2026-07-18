# -*- coding: utf-8 -*-
"""Llena la plantilla autorizada XpoSTEM con el contenido de la tesis (en inglés). v2 compacta."""
import re, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")

BASE = r"C:\Users\ADRIAN~1\AppData\Local\Temp\claude\C--Users-Adrian-Lopez-Documents-tesis-proyecto\b2e94106-6472-4498-8c8c-393624b7500f\scratchpad"
UNP = BASE + r"\plantilla_unpacked"
PRES = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\presentacion"

doc_path = UNP + r"\word\document.xml"
xml = open(doc_path, encoding="utf-8").read()

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------- 1) Título 96 -> 52 ----------
i = xml.find("Thesis or Project Title")
p0 = xml.rfind("<w:p ", 0, i); p1 = xml.find("</w:p>", i) + 6
xml = xml[:p0] + xml[p0:p1].replace('w:val="96"', 'w:val="52"') + xml[p1:]

# ---------- 2) Objectives como ítem de lista numerada ----------
i = xml.find(">3. Objectives<")
p0 = xml.rfind("<w:p ", 0, i)
pPr0 = xml.find("<w:pPr>", p0); pPr1 = xml.find("</w:pPr>", pPr0) + 8
PPR_HEAD = ('<w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/>'
            '<w:numId w:val="2"/></w:numPr><w:rPr><w:b/><w:bCs/><w:i/><w:iCs/>'
            '<w:color w:val="215E99" w:themeColor="text2" w:themeTint="BF"/>'
            '<w:sz w:val="40"/><w:szCs w:val="40"/><w:lang w:val="en-US"/></w:rPr></w:pPr>')
xml = xml[:pPr0] + PPR_HEAD + xml[pPr1:]

# ---------- 3) Clonar párrafo de Figura 2 -> Figura 3 ----------
i = xml.find(" Figure 2.")
p0 = xml.rfind("<w:p ", 0, i); p1 = xml.find("</w:p>", i) + 6
fig2 = xml[p0:p1]
fig3 = fig2.replace('r:embed="rId9"', 'r:embed="rId100"').replace(" Figure 2.", " FIGCAP3")
fig3 = re.sub(r'(<wp:docPr id=")(\d+)"', lambda m: m.group(1) + "990\"", fig3)
xml = xml[:p1] + fig3 + xml[p1:]

# ---------- 4) Extents: fija wp:extent Y a:ext dentro del párrafo ----------
def set_extents(xml, marker, w_cm, ratio):
    i = xml.find(marker)
    p0 = xml.rfind("<w:p ", 0, i); p1 = xml.find("</w:p>", i) + 6
    blk = xml[p0:p1]
    cx = str(int(w_cm * 360000)); cy = str(int(w_cm / ratio * 360000))
    blk = re.sub(r'<wp:extent cx="\d+" cy="\d+"/>', f'<wp:extent cx="{cx}" cy="{cy}"/>', blk)
    blk = re.sub(r'(<a:ext cx=")\d+(" cy=")\d+("/>)', rf'\g<1>{cx}\g<2>{cy}\g<3>', blk)
    return xml[:p0] + blk + xml[p1:]

xml = set_extents(xml, "Figure 1.",  8.6, 1352/1224)   # arquitectura_red (~9.1 cm alto)
xml = set_extents(xml, " Figure 2.", 11.2, 3080/1531)   # escena_mina_3d  (~6.4 cm alto)
xml = set_extents(xml, " FIGCAP3",   10.2, 2461/1401)   # grafico_rssi    (~6.7 cm alto)

# ---------- 5) Contenido compacto en inglés ----------
TITLE = "Design of an IEEE 802.11ac Network for the Teleoperation of an LHD Vehicle in Underground Mining Galleries"
ABSTRACT = ("Manual operation of load-haul-dump (LHD) vehicles in underground mining exposes operators to rockfalls, "
            "gases and moving machinery. This work designs and validates through simulation an IEEE 802.11ac network "
            "that enables teleoperation of an LHD from a safe control room, carrying real-time video, control "
            "commands and telemetry. Over the real geometry of level NV1640 at the Nexa Cerro Lindo mine, a "
            "fiber-optic ring backbone and a 12-node access mesh with WMM prioritization are dimensioned; propagation "
            "follows a two-slope tunnel model calibrated against a TamoGraph site survey, and performance is "
            "validated in ns-3. Every KPI is met with margin across ten independent runs.")
KEYWORDS = "Teleoperation, IEEE 802.11ac, underground mining, quality of service, network simulation."
INTRO = ("In 2024, 12 of the 14 fatal mining accidents reported by the Peruvian regulator OSINERGMIN — and 13 of "
         "their 15 victims — occurred underground. Teleoperation removes the operator from the production front, but "
         "demands a network that sustains real-time driving video, low-latency commands and continuous telemetry "
         "inside confined galleries with junctions, reflections and a moving on-board node. The case study is level "
         "NV1640 of the Nexa Cerro Lindo mine (El Teniente block-caving layout).")
BACKGROUND = ("A systematic review (Kitchenham method) compared communication technologies for tunnels and mines: "
              "LPWAN/WSN lack video capability, private LTE/5G adds complexity and cost, and optical links are "
              "alignment-sensitive. Industrial IEEE 802.11ac provides the required capacity, mining-grade equipment "
              "and standard WMM traffic prioritization.")
OBJ = ["Characterize the tunnel propagation channel and design the physical and logical network architecture.",
       "Dimension the radio and antenna subsystem and define the QoS and mobility policies.",
       "Validate end-to-end performance by packet-level simulation and assess technical-economic feasibility."]
METHODS = ("The work applies the Design Thinking methodology of TEL143/TEL147: empathize with the operator's risk, "
           "define requirements and KPIs, ideate and compare technologies, prototype in ns-3 over the real NV1640 "
           "geometry, and test against the site survey. The network combines a fiber-optic ring backbone with a "
           "12-node access mesh (five 30-dBm Hawk and seven 23-dBm Cardinal APs); the LHD carries an on-board radio "
           "with a HELI-40 antenna. Eighteen 300-s simulations cover ten operation seeds, a baseline, stress and "
           "handover scenarios.")
RES = ["Command one-way delay: 3.04 ± 0.26 ms (≤ 20 ms); control-loop RTT: 6.12 ms (≤ 40 ms).",
       "Video end-to-end latency: 35.9 ± 0.3 ms (≤ 150 ms); goodput 40 Mbps (≥ 38 Mbps).",
       "Video jitter P95: 0.28 ms (≤ 10 ms); packet loss: 0.01 % (≤ 1 %).",
       "Availability: 100 % (≥ 99.9 %); handover interruption: 0.88 ms (≤ 150 ms).",
       "All KPIs met in 10 of 10 seeds; margins hold under 50-Mbps video and 4-m/s stress."]
DISCUSSION = ("The design favors stable make-before-break roaming over chasing the nearest AP, avoiding reassociation "
              "micro-outages. Stress scenarios still meet every criterion, evidencing dimensioning margin. The "
              "deterministic, conservative model means real industrial mesh equipment can only improve these "
              "figures; field trials are identified as future work.")
CONC = ["The network meets every teleoperation KPI on the real NV1640 geometry, with statistical support.",
        "The solution is economically incremental and complies with Peruvian regulation (license-free 5 GHz band; mining safety code).",
        "Removing the operator from the hazard zone is a direct, replicable safety contribution for Peruvian mining."]
ACK = "To my advisor, Dr. Pastor David Chávez Muñoz, and to PUCP's Telecommunications Engineering program."
REFS = ['Z. Sun, I. F. Akyildiz, "Channel modeling for wireless networks in tunnels," 2010.',
        'Rajant Corp., "InstaMesh white paper," 2015.',
        'E. Egea-López et al., "Wireless comms. in underground mines," 2019.',
        'ns-3 Consortium, "ns-3.40 documentation," 2024.']
FIGCAP1 = "Figure 1. Network architecture and QoS classes."
FIGCAP2 = " Figure 2. Level NV1640 in 3D: galleries, the 12 APs and the LHD antenna pattern."
FIGCAP3 = " Figure 3. Serving-link RSSI: never below −72.1 dBm."

reemplazos = [
    ("Thesis or Project Title", TITLE),
    ("AUTHOR 1", "Adrián Álvaro López Pascual"),
    ("CAREER", "Telecommunications Engineering"),
    ("Email", "a.lopezp@pucp.edu.pe"),
    ("AUTHOR 1", ""), ("CAREER", ""), ("Email", ""),
    ("ADVISOR 1", "Advisor: Dr. Pastor David Chávez Muñoz"),
    ("ADVISOR 2", ""),
    ("Lorem ipsum dolor sit amet", ABSTRACT),
    ("inventore, deserunt, mollit, anim.", KEYWORDS),
    ("Sed ut perspiciatis unde omnis", INTRO),
    ("At vero eos et accusamus", BACKGROUND),
    ("Figure 1.", FIGCAP1),
    (">3. Objectives<", ">Objectives<"),
    ("Neque porro quisquam est", OBJ[0]),
    ("Sit amet, consectetur, adipisci velit", OBJ[1]),
    ("Sed quia non numquam eius modi tempora incident", OBJ[2]),
    ("Lorem ipsum dolor sit amet", METHODS),
    ("Neque porro quisquam est", RES[0]),
    ("Sit amet, consectetur, adipisci velit", RES[1]),
    ("Sed quia non numquam eius modi tempora incident", RES[2]),
    ("Neque porro quisquam est", RES[3]),
    ("Sit amet, consectetur, adipisci velit", RES[4]),
    (" Figure 2.", FIGCAP2),
    (" FIGCAP3", FIGCAP3),
    ("Sed ut perspiciatis unde omnis", DISCUSSION),
    ("Neque porro quisquam est", CONC[0]),
    ("Sit amet, consectetur, adipisci velit", CONC[1]),
    ("Sed quia non numquam eius modi tempora incident", CONC[2]),
    ("Nemo enim ipsam voluptatem", ACK),
    ("Nemo eni", REFS[0]),
    ("Sit amet Nemo eni", REFS[2]),
    ("Et harum", REFS[3]),
]

cursor = 0
for buscar, nuevo in reemplazos:
    i = xml.find(buscar, cursor)
    if i < 0:
        print(f"[AVISO] no encontrado desde cursor: {buscar[:40]}"); continue
    if buscar.startswith(">"):
        xml = xml[:i] + nuevo + xml[i+len(buscar):]
        cursor = i + len(nuevo)
        continue
    t0 = xml.rfind(">", 0, i) + 1
    t1 = xml.find("<", i)
    xml = xml[:t0] + esc(nuevo) + xml[t1:]
    cursor = t0 + len(esc(nuevo))

# REF2 ('Sit amet' suelto entre REF1 y REF3)
i1 = xml.find(esc(REFS[0])); i3 = xml.find(esc(REFS[2]))
seg = xml[i1:i3]
j = seg.find(">Sit amet<")
if j >= 0:
    xml = xml[:i1+j] + ">" + esc(REFS[1]) + "<" + xml[i1+j+len(">Sit amet<"):]
else:
    print("[AVISO] REF2 no encontrado")

# Reducción tipográfica para encajar en 1 página (cuerpo 13->10pt, headings 20->17pt, sub 16->14pt)
for a, b in [("26", "20"), ("40", "34"), ("32", "28")]:
    xml = xml.replace(f'<w:sz w:val="{a}"/>', f'<w:sz w:val="{b}"/>')
    xml = xml.replace(f'<w:szCs w:val="{a}"/>', f'<w:szCs w:val="{b}"/>')

# El párrafo vacío final (obligatorio tras la tabla de referencias) a 1pt para no crear página 2
i = xml.find('w14:paraId="1CB1393D"')
if i >= 0:
    p0 = xml.rfind("<w:p ", 0, i); p1 = xml.find("</w:p>", i) + 6
    blk = xml[p0:p1].replace('<w:sz w:val="34"/>', '<w:sz w:val="2"/>').replace('<w:szCs w:val="34"/>', '<w:szCs w:val="2"/>')
    blk = blk.replace('<w:pStyle w:val="Prrafodelista"/>', '<w:pStyle w:val="Prrafodelista"/><w:spacing w:before="0" w:after="0" w:line="10" w:lineRule="exact"/>', 1)
    xml = xml[:p0] + blk + xml[p1:]

open(doc_path, "w", encoding="utf-8").write(xml)

# ---------- 6) Relaciones y medios ----------
rels_path = UNP + r"\word\_rels\document.xml.rels"
rels = open(rels_path, encoding="utf-8").read()
if "rId100" not in rels:
    rels = rels.replace("</Relationships>",
        '<Relationship Id="rId100" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image4.png"/></Relationships>')
    open(rels_path, "w", encoding="utf-8").write(rels)

shutil.copy(PRES + r"\arquitectura_red.png",      UNP + r"\word\media\image2.png")
shutil.copy(PRES + r"\escena_mina_3d.png",        UNP + r"\word\media\image3.png")
shutil.copy(PRES + r"\grafico_rssi_asociado.png", UNP + r"\word\media\image4.png")

ct_path = UNP + r"\[Content_Types].xml"
ct = open(ct_path, encoding="utf-8").read()
if 'Extension="png"' not in ct:
    ct = ct.replace("</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')
    open(ct_path, "w", encoding="utf-8").write(ct)

print("[OK] plantilla llenada v2")

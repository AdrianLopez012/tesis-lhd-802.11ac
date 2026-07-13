# -*- coding: utf-8 -*-
# ETAPA D — Anexos C–H: reemplazo del material v8.2 por el vigente v3-REAL.
# Volcados con el mismo formato numerado; hashes SHA-256 calculados de verdad.
import docx, sys, os, glob, hashlib, csv
sys.stdout.reconfigure(encoding="utf-8")

DOC  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
SIM  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3"
GS   = os.path.join(SIM, "graficas_simulacion")
RES  = os.path.join(SIM, "results")

d = docx.Document(DOC)
paras = d.paragraphs

def find(pref, start=0):
    for i in range(start, len(paras)):
        if paras[i].text.strip().startswith(pref):
            return i
    raise ValueError(pref)

# ---- localizar los headings de anexos (en el doc ACTUAL) ----
iB  = find("Anexo B.")
iC  = find("Anexo C.")
iD  = find("Anexo D.")
iE  = find("Anexo E.")
iF  = find("Anexo F.")
iG  = find("Anexo G.")
iH  = find("Anexo H.")
print(f"anexos en: B={iB} C={iC} D={iD} E={iE} F={iF} G={iG} H={iH}")

# estilo de los volcados existentes: primer párrafo que empieza con "0001 |"
i_code = find("0001 |", iC)
CODE_STYLE = paras[i_code].style
BODY_STYLE = paras[iC+2].style if not paras[iC+2].text.startswith("0001") else None
H3_STYLE   = "Heading 3"

def delete_paras(i_from, i_to):
    """elimina párrafos [i_from, i_to) del cuerpo (no toca tablas)"""
    for p in paras[i_from:i_to]:
        p._element.getparent().remove(p._element)

def insert_h3(ref, txt):
    p = ref.insert_paragraph_before(txt, H3_STYLE); return p

def insert_body(ref, txt):
    p = ref.insert_paragraph_before(txt)
    if BODY_STYLE: p.style = BODY_STYLE
    return p

def insert_dump(ref, path, chunk=50, max_lines=None):
    """vuelca un archivo con formato NNNN | linea, en bloques con saltos internos"""
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    if max_lines: lines = lines[:max_lines]
    for b in range(0, len(lines), chunk):
        p = ref.insert_paragraph_before("")
        p.style = CODE_STYLE
        blk = lines[b:b+chunk]
        for j, ln in enumerate(blk):
            r = p.add_run(f"{b+j+1:04d} | {ln}")
            if j < len(blk)-1: r.add_break()
    return len(lines)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(65536), b""): h.update(ch)
    return h.hexdigest()

def replace_text(i, txt):
    p = paras[i]
    p.runs[0].text = txt
    for r in p.runs[1:]: r.text = ""

# ============ ANEXO C — código vigente ============
replace_text(iC, "Anexo C. Código fuente principal del prototipo ns-3 v3-REAL")
# borrar contenido viejo de C (todo entre iC+1 y iD)
delete_paras(iC+1, iD)
paras = d.paragraphs                      # re-enumerar
iD  = find("Anexo D."); ref = paras[iD]
insert_h3(ref, "C.1 lhd-teleop-v3-real.cc — simulación principal")
insert_body(ref, "Listado íntegro numerado para trazabilidad. Los encabezados de geometría, recorrido y parámetros (C.2 a C.4) son AUTOGENERADOS desde la fuente única de datos; no se editan a mano.")
n1 = insert_dump(ref, os.path.join(SIM, "lhd-teleop-v3-real.cc"))
insert_h3(ref, "C.2 geometria_nv1640.h — geometría real (autogenerado)")
n2 = insert_dump(ref, os.path.join(SIM, "geometria_nv1640.h"))
insert_h3(ref, "C.3 recorrido_nv1640.h — recorrido real del ciclo (autogenerado)")
n3 = insert_dump(ref, os.path.join(SIM, "recorrido_nv1640.h"))
insert_h3(ref, "C.4 parametros_rf.h — parámetros RF (autogenerado)")
n4 = insert_dump(ref, os.path.join(SIM, "parametros_rf.h"))
print(f"C: {n1}+{n2}+{n3}+{n4} lineas")

# ============ ANEXO D — cadena de generación ============
paras = d.paragraphs
iD = find("Anexo D."); iE = find("Anexo E.")
replace_text(iD, "Anexo D. Fuente única de datos y cadena de generación")
delete_paras(iD+1, iE)
paras = d.paragraphs
iE = find("Anexo E."); ref = paras[iE]
insert_body(ref, "La geometría, el recorrido y los parámetros RF tienen una fuente única en Python; tres generadores producen los encabezados C++ del Anexo C. Los scripts de figuras (plano, cobertura, presupuesto de enlace, contraste TamoGraph, resultados y comparaciones) se inventarían en el Anexo H y se entregan en el anexo digital.")
insert_h3(ref, "D.1 parametros_rf.py — fuente única de parámetros RF y del modelo de propagación")
insert_dump(ref, os.path.join(SIM, "parametros_rf.py"))
insert_h3(ref, "D.2 mapa_nv1640_datos.py — fuente única de la geometría y los AP")
insert_dump(ref, os.path.join(GS, "mapa_nv1640_datos.py"))
insert_h3(ref, "D.3 generar_geometria_h.py — geometría a C++")
insert_dump(ref, os.path.join(GS, "generar_geometria_h.py"))
insert_h3(ref, "D.4 generar_recorrido_h.py — recorrido real a C++ (grafo y maniobras)")
insert_dump(ref, os.path.join(GS, "generar_recorrido_h.py"))
insert_h3(ref, "D.5 generar_parametros_h.py — parámetros RF a C++")
insert_dump(ref, os.path.join(GS, "generar_parametros_h.py"))
print("D: fuentes únicas y generadores volcados")

# ============ ANEXO E — ejecución ============
paras = d.paragraphs
iE = find("Anexo E."); iF = find("Anexo F.")
delete_paras(iE+1, iF)
paras = d.paragraphs
iF = find("Anexo F."); ref = paras[iF]
insert_h3(ref, "E.1 run_escenarios_v3.sh — batería completa (18 corridas en serie)")
insert_body(ref, "La batería tarda aproximadamente cuatro horas en el entorno WSL utilizado y debe ejecutarse en serie. Los resultados se copian a results/ por nombre de escenario.")
insert_dump(ref, os.path.join(SIM, "run_escenarios_v3.sh"))
insert_h3(ref, "E.2 Parámetros verificados en la ejecución")
insert_body(ref, "Los parámetros efectivos de la corrida provienen de parametros_rf.py (Anexo D.1) vía parametros_rf.h (Anexo C.4); la tabla siguiente los consolida.")
print("E: script de bateria volcado")

# ============ ANEXO F — evidencia numérica ============
paras = d.paragraphs
iF = find("Anexo F."); iG = find("Anexo G.")
replace_text(iF, "Anexo F. Evidencia numérica de la batería de simulación v3-REAL")
delete_paras(iF+1, iG)
paras = d.paragraphs
iG = find("Anexo G."); ref = paras[iG]
insert_body(ref, "Este anexo reproduce íntegramente los archivos de estadísticas de flujo y los consolidados de traspaso, RTT y disponibilidad de las dieciocho corridas. Los registros de posición y asociación (aprox. 300 filas por corrida) y los XML de FlowMonitor se entregan en el anexo digital y se inventarían en el Anexo H.")
insert_h3(ref, "F.1 Estadísticas de flujo por corrida (flow_stats)")
tot = 0
for pth in sorted(glob.glob(os.path.join(RES, "*_v3_flow_stats.csv"))):
    nm = os.path.basename(pth)
    insert_body(ref, nm + ":")
    tot += insert_dump(ref, pth)
insert_h3(ref, "F.2 Traspasos del escenario dedicado (5 semillas)")
for pth in sorted(glob.glob(os.path.join(RES, "handover*_v3_handover.csv"))):
    insert_body(ref, os.path.basename(pth) + ":")
    insert_dump(ref, pth)
insert_h3(ref, "F.3 RTT del lazo de control y disponibilidad (10 semillas)")
for pat in ("principal_s*_v3_rtt.csv", "principal_s*_v3_disponibilidad.csv"):
    for pth in sorted(glob.glob(os.path.join(RES, pat))):
        insert_body(ref, os.path.basename(pth) + ":")
        insert_dump(ref, pth)
print(f"F: {tot} lineas de flow_stats + handover + rtt/disp")

# ============ ANEXO G — evidencia gráfica ============
paras = d.paragraphs
iG = find("Anexo G."); iH = find("Anexo H.")
replace_text(iG, "Anexo G. Evidencia gráfica del modelamiento y de los resultados v3-REAL")
delete_paras(iG+1, iH)
paras = d.paragraphs
iH = find("Anexo H."); ref = paras[iH]
FIGS = [
 ("plano_nv1640_pro.png","Plano de la zona de producción con los 12 AP (Figura 9 del Capítulo 3)."),
 ("mapa_cobertura_pro.png","Mapa de cobertura RSSI y tasa PHY con el mismo modelo de la simulación."),
 ("link_budget.png","Presupuesto de enlace del caso más exigente con radios máximos del modelo."),
 ("contraste_tamograph.png","Contraste de coherencia del modelo con el reporte TamoGraph."),
 ("recorrido_lhd.gif","Animación del ciclo real de operación del LHD (anexo digital)."),
 ("resultados_kpi_multiseed.png","Indicadores frente a requisitos, 10 semillas con IC 95 %."),
 ("resultados_escenarios.png","Comparación de escenarios (Figura 10 del Capítulo 3)."),
 ("resultados_handover.png","Análisis del traspaso: operación y escenario dedicado multi-semilla."),
 ("resultados_cobertura_ruta.png","RSSI del mejor AP y CDF a lo largo del recorrido."),
 ("kpi_v3_panel.png","Panel integral de KPIs de la corrida de operación."),
 ("kpi_v3_ruta_rssi.png","Ruta real coloreada por RSSI sobre la geometría."),
 ("comparacion_kpis.png","KPIs frente a requisitos y referencias (Figura 11 del Capítulo 4)."),
 ("arquitectura_red.png","Arquitectura de red en tres capas con QoS."),
]
insert_body(ref, "Las figuras siguientes constituyen la evidencia gráfica vigente; los archivos en resolución completa se incluyen en el anexo digital.")
for fn, desc in FIGS:
    insert_body(ref, f"— {fn}: {desc}")
print("G: inventario de 13 figuras")

# ============ ANEXO H — inventario con hashes ============
paras = d.paragraphs
iH = find("Anexo H.")
# reemplazar la descripcion posterior si existe (H.1) y añadir inventario con SHA-256
ref_end = None
for i in range(iH+1, len(paras)):
    if paras[i].style.name.startswith("Heading") and not paras[i].text.strip().startswith("H."):
        ref_end = i; break
insert_at = paras[ref_end] if ref_end else None
files = [os.path.join(SIM,"lhd-teleop-v3-real.cc"), os.path.join(SIM,"geometria_nv1640.h"),
         os.path.join(SIM,"recorrido_nv1640.h"), os.path.join(SIM,"parametros_rf.h"),
         os.path.join(SIM,"parametros_rf.py"), os.path.join(GS,"mapa_nv1640_datos.py"),
         os.path.join(SIM,"run_escenarios_v3.sh")] + \
        sorted(glob.glob(os.path.join(RES,"*_v3_flow_stats.csv")))
if insert_at is not None:
    p = insert_at.insert_paragraph_before("Huellas SHA-256 de los archivos principales de la versión vigente (verificables contra el anexo digital):")
    if BODY_STYLE: p.style = BODY_STYLE
    for f in files:
        q = insert_at.insert_paragraph_before(f"{os.path.basename(f)}  =  {sha256(f)}")
        q.style = CODE_STYLE
print(f"H: {len(files)} hashes SHA-256")

d.save(DOC)
print("ANEXOS C-H actualizados")

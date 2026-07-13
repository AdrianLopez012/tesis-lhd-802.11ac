# -*- coding: utf-8 -*-
# ETAPA A2 — Bloque 3.4.7 (resultados) + tablas del Cap. 3: v8.2 -> v3-REAL
# REGLA: los valores numéricos se LEEN de los CSVs de la batería (results/),
# nunca se escriben a mano. Cada edición verifica el contenido esperado.
import docx, sys, csv, glob, os
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")

DOC = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\tesis_v2.docx"
RES = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\results"

# ---------- leer KPIs de los CSVs (fuente única de números) ----------
def flows(path):
    return {r["name"]: {k: (float(v) if k != "name" else v) for k, v in r.items()}
            for r in csv.DictReader(open(path))}

def agg(name, key):
    v = [flows(p)[name][key] for p in sorted(glob.glob(os.path.join(RES, "principal_s*_v3_flow_stats.csv")))]
    a = np.array(v); return a.mean(), 1.96*a.std(ddof=1)/np.sqrt(len(a))

def metr(pat, key):
    v = []
    for p in sorted(glob.glob(os.path.join(RES, pat))):
        for r in csv.DictReader(open(p)):
            if r.get("metric") == key:
                v.append(float(r.get("value_ms") or r.get("value")))
    return v

owd_m, owd_ci = agg("Comandos", "owd_ms")
plr_m, plr_ci = agg("Comandos", "plr_pct")
e2e_m, e2e_ci = agg("Video", "e2e_ms")
jit_m, _      = agg("Video", "jitter_p95_ms")
gp_m, gp_ci   = agg("Video", "goodput_mbps")
plv_m, _      = agg("Video", "plr_pct")
rtt = np.array(metr("principal_s*_v3_rtt.csv", "rtt_media"))
rtt_m, rtt_ci = rtt.mean(), 1.96*rtt.std(ddof=1)/np.sqrt(len(rtt))
disp = np.array(metr("principal_s*_v3_disponibilidad.csv", "disponibilidad_pct")).mean()
ho_max = max(metr("handover*_v3_handover.csv", "max"))
ho_n   = int(sum(metr("handover*_v3_handover.csv", "eventos")))
ho_med = np.mean(metr("handover*_v3_handover.csv", "media"))

def esc(fname):
    f = flows(os.path.join(RES, fname))
    return (f["Video"]["goodput_mbps"], f["Video"]["e2e_ms"], f["Comandos"]["plr_pct"], f["Comandos"]["owd_ms"])
bl = esc("baseline_v3_flow_stats.csv")
ev = esc("estres_video_v3_flow_stats.csv")
el = esc("estres_lhd_v3_flow_stats.csv")
ho = esc("handover_v3_flow_stats.csv")

print(f"KPIs leidos: OWD {owd_m:.2f}±{owd_ci:.2f} | PLR {plr_m:.2f} | E2E {e2e_m:.2f} | gp {gp_m:.2f} | RTT {rtt_m:.2f} | disp {disp:.1f} | HO max {ho_max:.2f} (n={ho_n})")

d = docx.Document(DOC)

# ---------- párrafos del bloque 3.4.7 / 3.4.8 / síntesis ----------
R = {
795: ("El protocolo experimental del presente avance",
f"El protocolo experimental corresponde a la ejecución de la batería completa del prototipo ns-3 v3-REAL: dieciocho corridas de 300 s ejecutadas en serie, que comprenden el escenario de operación con diez semillas independientes, una referencia estática (baseline), dos escenarios de estrés (video a 50 Mbps y velocidad del LHD a 4 m/s) y un escenario dedicado de traspaso con cinco semillas. El escenario de operación utiliza la geometría real de la zona de producción, los doce AP en sus posiciones reales, velocidad nominal de 2.22 m/s, video VBR con media de 40 Mbps, comandos de 0.5 Mbps y telemetría de 0.1 Mbps. El modelo aplica pérdidas de sistema de 9.4 dB y penalización NLOS por galería cruzada; la posición del LHD y los eventos de asociación se registran a lo largo de todo el recorrido."),

796: ("Tabla 20. Escenarios ejecutados",
"Tabla 20. Escenarios de la batería de simulación v3-REAL."),

797: ("Los resultados del escenario principal se presentan",
f"Los resultados del escenario de operación se reportan como media e intervalo de confianza al 95 % sobre las diez semillas independientes. El criterio de goodput no exige recibir exactamente los 40 Mbps ofrecidos, sino al menos 38 Mbps de carga útil, equivalente al 95 % del flujo nominal; el valor reportado corresponde al payload de aplicación, descontadas las cabeceras de red. Para comandos, el resultado consolidado (PLR medio de {plr_m:.2f} %) cumple incluso la meta estricta de 0.1 % definida para enlace estable; el criterio operacional de movilidad (≤ 0.5 %) se mantiene como umbral de aceptación del diseño."),

798: ("Tabla 21. Resultados preliminares",
"Tabla 21. Resultados del escenario de operación (diez semillas, media ± IC 95 %) frente a los requisitos."),

799: ("Los registros de asociación del escenario principal",
f"Los registros de posición y asociación evidencian que el enlace se mantiene estable durante el recorrido: con el roaming conservador de tipo make-before-break, el LHD conserva su AP servidor hasta perderlo efectivamente, mientras el AP de mejor cobertura cambia veintiún veces a lo largo de la ruta. Para verificar el requisito de traspaso de forma explícita, el escenario dedicado (roaming sensible, cinco semillas) forzó traspasos duros medibles: {ho_n} eventos con duración media de {ho_med:.2f} ms y peor caso de {ho_max:.2f} ms, muy por debajo del requisito de 150 ms. La disponibilidad radioeléctrica del recorrido (RSSI del mejor AP sobre el umbral de enlace usable de −82 dBm) fue del {disp:.0f} %."),

800: ("Tabla 22. Comparación de escenarios",
"Tabla 22. Comparación de escenarios de la batería v3-REAL."),

802: ("Figura 10. Cumplimiento de criterios",
"Figura 10. Comparación de escenarios de la batería v3-REAL frente a los requisitos."),

803: ("Fuente: Elaboración propia a partir de resultados CSV/XML v8.2.",
"Fuente: Elaboración propia a partir de los resultados CSV de la batería de simulación v3-REAL."),

804: ("El escenario sin Cardinal fijo evidencia",
f"El escenario de estrés de video (50 Mbps) mantiene los criterios de aceptación, pero más que duplica la latencia de los comandos (OWD medio de {ev[3]:.1f} ms frente a {owd_m:.1f} ms en operación), lo que evidencia simultáneamente el margen del dimensionamiento a 40 Mbps y el efecto protector de la priorización WMM: la degradación ante sobrecarga se manifiesta primero en la latencia del tráfico priorizado y no en pérdidas. El estrés de velocidad (4 m/s) y la referencia estática cumplen todos los criterios. Por tanto, el dimensionamiento adoptado (video de 40 Mbps sobre 802.11ac con 40 MHz y MIMO 2×2) opera con holgura verificable en la geometría real de la zona de producción."),

806: ("La relación entre cada evidencia",
"La relación entre cada evidencia y la sección del capítulo que sustenta se encuentra sistematizada en el Anexo B. Esta organización permite distinguir la documentación fuente del proyecto, la evidencia generada por modelamiento y las salidas del prototipo ns-3 v3-REAL."),

807: ("La interoperabilidad de la solución se sustenta",
"La interoperabilidad de la solución se sustenta en el uso de IEEE 802.11ac y de un backbone Ethernet, pero la simulación no reproduce protocolos propietarios de gestión de malla —el roaming estable del mesh industrial se emula mediante histéresis de asociación—, ni mecanismos de handover del fabricante, seguridad operacional del LHD o integración con una plataforma de control. En un despliegue posterior, la configuración final deberá ser verificada con los fabricantes, con las áreas OT/TI y con seguridad y salud ocupacional."),

819: ("En síntesis, el Capítulo 3 entrega",
"En síntesis, el Capítulo 3 entrega una memoria de diseño coherente con los insumos técnicos disponibles y con el alcance de una tesis basada en prototipado conceptual. La versión v3-REAL, ejecutada sobre la geometría real de la zona de producción con una batería de dieciocho corridas, muestra el cumplimiento de todos los indicadores establecidos con respaldo estadístico (diez semillas, media e intervalo de confianza al 95 %); al mismo tiempo, identifica los aspectos que deberán validarse en el Capítulo 4 y en una futura fase de pruebas de campo."),
}

ok, fail = 0, []
for idx, (pref, nuevo) in R.items():
    p = d.paragraphs[idx]
    if not p.text.strip().startswith(pref[:45]):
        fail.append((idx, pref[:35], p.text.strip()[:35])); continue
    if p.runs:
        p.runs[0].text = nuevo
        for r in p.runs[1:]: r.text = ""
    else:
        p.text = nuevo
    ok += 1

# ---------- tablas ----------
def set_cell(t, r, c, txt):
    cell = t.cell(r, c)
    if cell.paragraphs and cell.paragraphs[0].runs:
        cell.paragraphs[0].runs[0].text = txt
        for rr in cell.paragraphs[0].runs[1:]: rr.text = ""
        for pp in cell.paragraphs[1:]:
            for rr in pp.runs: rr.text = ""
    else:
        cell.text = txt

def fill_row(t, r, vals):
    for c, v in enumerate(vals): set_cell(t, r, c, v)

def del_row(t, r):
    row = t.rows[r]._element
    row.getparent().remove(row)

# Tabla 16 (idx 17) — parámetros del modelo
t = d.tables[17]
assert "Parámetro" in t.cell(0,0).text
fill_row(t, 3, ["Potencia Cardinal", "23 dBm", "Nodos de refuerzo y radio embarcado del LHD."])
fill_row(t, 4, ["Pérdidas de sistema", "9.4 dB", "Fuente única de parámetros aplicada en simulación y figuras."])
fill_row(t, 6, ["NLOS", "Penalización de 10 dB por galería cruzada", "Distancia radioeléctrica por ruta de túnel."])
fill_row(t, 7, ["Roaming", "Beacon 102.4 ms; MaxMissedBeacons = 10", "Asociación estable tipo make-before-break; el escenario de traspaso usa 3."])
fill_row(t, 8, ["Velocidad principal", "2.22 m/s (8 km/h)", "Escenario operativo nominal; estrés a 4 m/s."])
r = t.add_row(); fill_row(t, len(t.rows)-1, ["Tráfico de video", "VBR tipo H.264, 30 fps, media 40 Mbps", "Cuadros de tamaño variable ±30 % acotado."])
r = t.add_row(); fill_row(t, len(t.rows)-1, ["AP modelados", "5 Hawk (30 dBm/11 dBi) + 7 Cardinal (23 dBm/7.5 dBi)", "Posiciones reales del plano NV1640."])

# Tabla 20 (idx 21) — escenarios de la batería
t = d.tables[21]
assert "Escenario" in t.cell(0,0).text
fill_row(t, 0, ["Escenario v3-REAL", "Configuración respecto de la operación", "Propósito"])
fill_row(t, 1, ["operación (principal_s1…s10)", "Geometría real; 12 AP; 2.22 m/s; video VBR 40 Mbps; 10 semillas independientes.", "Escenario principal del diseño; media ± IC 95 %."])
fill_row(t, 2, ["baseline", "LHD estático en la galería central, a media altura.", "Referencia sin movilidad ni traspasos."])
fill_row(t, 3, ["estres_video", "El video sube a 50 Mbps (125 % del nominal).", "Margen del dimensionamiento y efecto de la priorización."])
fill_row(t, 4, ["estres_lhd", "La velocidad sube a 4.0 m/s (180 % de la nominal).", "Sensibilidad frente a movilidad acelerada."])
fill_row(t, 5, ["handover (5 semillas)", "Roaming sensible (MaxMissedBeacons = 3) para forzar traspasos duros.", "Verificación explícita del requisito de traspaso."])
del_row(t, 6)

# Tabla 21 (idx 22) — resultados del escenario de operación
t = d.tables[22]
assert "Indicador" in t.cell(0,0).text
fill_row(t, 0, ["Indicador del escenario de operación", "Umbral", "Resultado (10 semillas, media ± IC 95 %)", "Interpretación"])
fill_row(t, 1, ["OWD medio de comandos", "≤ 20 ms", f"{owd_m:.2f} ± {owd_ci:.2f} ms", "Cumple."])
fill_row(t, 2, ["PLR de comandos en movilidad", "≤ 0.5 %", f"{plr_m:.2f} ± {plr_ci:.2f} %", "Cumple; satisface también la meta estricta (≤ 0.1 %) en promedio."])
fill_row(t, 3, ["E2E medio de video", "≤ 150 ms", f"{e2e_m:.2f} ± {e2e_ci:.2f} ms", "Cumple; incluye 35 ms de códec."])
fill_row(t, 4, ["Jitter P95 de video", "≤ 10 ms", f"{jit_m:.2f} ms", "Cumple."])
fill_row(t, 5, ["PLR de video", "≤ 1.0 %", f"{plv_m:.2f} %", "Cumple."])
fill_row(t, 6, ["Goodput útil de video", "≥ 38 Mbps", f"{gp_m:.2f} ± {gp_ci:.2f} Mbps", "Cumple; payload exacto, sin cabeceras."])
r = t.add_row(); fill_row(t, len(t.rows)-1, ["RTT del lazo de control", "≤ 40 ms", f"{rtt_m:.2f} ± {rtt_ci:.2f} ms", "Cumple; cota analítica (OWD de comando + OWD de telemetría)."])
r = t.add_row(); fill_row(t, len(t.rows)-1, ["Traspaso (handover)", "≤ 150 ms", f"peor caso {ho_max:.2f} ms ({ho_n} eventos, 5 semillas)", "Cumple; escenario dedicado de traspaso."])
r = t.add_row(); fill_row(t, len(t.rows)-1, ["Disponibilidad radioeléctrica", "≥ 99.9 %", f"{disp:.1f} % del recorrido", "Cumple; RSSI del mejor AP ≥ −82 dBm."])

# Tabla 22 (idx 23) — comparación de escenarios
t = d.tables[23]
assert "Escenario" in t.cell(0,0).text
fill_row(t, 0, ["Escenario", "Goodput video", "E2E video", "PLR comandos", "Lectura de diseño"])
fill_row(t, 1, ["operación (10 semillas)", f"{gp_m:.2f} Mbps", f"{e2e_m:.2f} ms", f"{plr_m:.2f} %", "Cumple todos los criterios con margen."])
fill_row(t, 2, ["baseline (estático)", f"{bl[0]:.2f} Mbps", f"{bl[1]:.2f} ms", f"{bl[2]:.2f} %", "Referencia controlada; cumple."])
fill_row(t, 3, ["estres_video (50 Mbps)", f"{ev[0]:.2f} Mbps", f"{ev[1]:.2f} ms", f"{ev[2]:.2f} %", f"Cumple; OWD de comandos sube a {ev[3]:.1f} ms: margen del dimensionamiento."])
fill_row(t, 4, ["estres_lhd (4 m/s)", f"{el[0]:.2f} Mbps", f"{el[1]:.2f} ms", f"{el[2]:.2f} %", "Cumple; robustez frente a movilidad acelerada."])
fill_row(t, 5, ["handover (roaming sensible)", f"{ho[0]:.2f} Mbps", f"{ho[1]:.2f} ms", f"{ho[2]:.2f} %", f"Cumple; traspasos duros de {ho_med:.2f} ms en promedio."])
del_row(t, 6)

# Tabla 23 (idx 24) — limitaciones declaradas
t = d.tables[24]
assert "Limitación" in t.cell(0,0).text
fill_row(t, 1, ["Modelo de propagación determinista (shadowing desactivado).", "Los KPIs de red no incluyen desvanecimiento aleatorio; la variabilidad ±σ se analiza en el mapa de cobertura y el contraste TamoGraph.", "Campaña de medición in situ punto a punto."])
fill_row(t, 3, ["Roaming emulado con histéresis de asociación de ns-3.", "Representa el comportamiento make-before-break del mesh industrial, no su firmware.", "Prueba con equipos y firmware reales."])
fill_row(t, 4, ["Video VBR sintético (distribución normal acotada).", "Aproxima cuadros I/P/B, pero no reproduce una traza real de códec.", "Pruebas con trazas de cámaras reales."])

d.save(DOC)
print(f"parrafos OK: {ok}/{len(R)}")
for f in fail: print("NO COINCIDE:", f)
print("tablas 16/20/21/22/23 actualizadas")

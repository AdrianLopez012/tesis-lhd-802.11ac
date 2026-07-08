"""
=============================================================================
ANÁLISIS DE RESULTADOS NS-3 - GRÁFICAS PARA CAPÍTULO 3
Tesis: Red IEEE 802.11ac para teleoperación LHD — Nexa Cerro Lindo
Versión 8.2 — usa CSVs v9 con escenarios mobility reales
=============================================================================

Lee los CSV generados por la simulación ns-3 v9 y produce:
  Gráfica 8:  Comparación de KPIs por escenario vs. umbrales
  Gráfica 9:  CDF de delay y jitter desde FlowMonitor XML
  Gráfica 10: Tabla resumen de validación (KPIs vs. umbrales) con P95
  Gráfica 11: Heatmap de cumplimiento de KPIs por escenario

Escenarios v9:
  mobility_5hawks_real    — PRINCIPAL tesis (5 Hawks reales, NLOS activo)
  mobility_4hawks_sin_h4  — Sin H4 ni CardFijo
  mobility_sin_cardfijo_bp— 5H reales, sin CardFijo
  lhd_rapido_mobility     — Sensibilidad velocidad (3.33 m/s)
  video_20mbps_mobility   — Sensibilidad bitrate (20 Mbps)
  baseline                — Referencia controlada (lineal, NLOS off)

KPIs v8:
  Video E2E media <= 150 ms (con codec 35ms)
  Video payload goodput >= 38 Mbps (carga útil de app)
  Video PLR <= 1%
  Video jitter P95 <= 10 ms
  Cmd OWD media <= 20 ms (one-way delay; RTT_req=40ms)
  Cmd PLR <= 0.5%

Uso: python3 analyze_results.py <directorio_resultados>
"""

import sys
import os
import csv
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

# Forzar UTF-8 en Windows (evita UnicodeEncodeError en consola cp1252)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================================
# UMBRALES DE ACEPTACIÓN (Tabla 6 del Capítulo 1)
# ============================================================================

THRESHOLDS = {
    "OWD cmd media (ms)":          {"limit": 20.0, "type": "max", "flow": "Comandos"},
    "PLR comandos (%)":            {"limit": 0.5,  "type": "max", "flow": "Comandos"},
    "Video E2E media (ms)":        {"limit": 150,  "type": "max", "flow": "Video"},
    "Video jitter P95 (ms)":       {"limit": 10,   "type": "max", "flow": "Video"},
    "Video PLR (%)":               {"limit": 1.0,  "type": "max", "flow": "Video"},
    "Video payload goodput (Mbps)":{"limit": 38.0, "type": "min", "flow": "Video"},
}

OUTPUT_DIR = "graficas_simulacion"


def generate_synthetic_data():
    """No genera datos sintéticos — v8 requiere resultados reales de simulación ns-3."""
    return {}, {}


def load_ns3_results(results_dir):
    """Carga resultados reales de ns-3 v9 desde CSV."""
    # Mapeo: nombre de archivo (sin _flow_stats.csv) → nombre canónico en gráficas
    name_map = {
        "mobility_5hawks_real_v9":    "mobility_5hawks_real",
        "mobility_4hawks_sin_h4_v9":  "mobility_4hawks_sin_h4",
        "mobility_sin_cardfijo_bp_v9":"mobility_sin_cardfijo_bp",
        "lhd_rapido_mobility_v9":     "lhd_rapido_mobility",
        "video_20mbps_mobility_v9":   "video_20mbps_mobility",
        "baseline_v9":                "baseline",
        "baseline_s2_v9": None,
        "baseline_s3_v9": None,
    }
    scenarios = {}
    for fname in os.listdir(results_dir):
        if fname.endswith("_flow_stats.csv"):
            raw_name = fname.replace("_flow_stats.csv", "")
            scenario_name = name_map.get(raw_name, raw_name)
            if scenario_name is None:
                continue
            filepath = os.path.join(results_dir, fname)

            scenario_data = {}
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    flow_name = row.get("flow_name", "Unknown")
                    if flow_name not in ("Video", "Comandos", "Telemetria"):
                        continue

                    # Campos nuevos v2.2 (con fallback para CSVs v2.1 sin P95)
                    delay_mean    = float(row.get("delay_mean_ms", 0))
                    delay_p95     = float(row.get("delay_p95_ms", delay_mean * 1.65))
                    jitter_mean   = float(row.get("jitter_mean_ms", 0))
                    jitter_p95    = float(row.get("jitter_p95_ms", jitter_mean * 1.65))
                    pdr           = float(row.get("pdr_pct", 0)) / 100.0
                    ip_tput       = float(row.get("ip_throughput_mbps",
                                          row.get("throughput_mbps", 0)))
                    goodput       = float(row.get("payload_goodput_mbps", ip_tput))
                    codec_delay   = float(row.get("codec_delay_ms", 0))
                    total_e2e     = float(row.get("total_e2e_ms",
                                          delay_mean + codec_delay))
                    total_e2e_p95 = float(row.get("total_e2e_p95_ms",
                                          delay_p95  + codec_delay))

                    scenario_data[flow_name] = {
                        "delay":        delay_mean,
                        "delay_p95":    delay_p95,
                        "jitter":       jitter_mean,
                        "jitter_p95":   jitter_p95,
                        "pdr":          pdr,
                        "throughput":   ip_tput,
                        "goodput":      goodput,
                        "codec_delay":  codec_delay,
                        "total_e2e":    total_e2e,
                        "total_e2e_p95": total_e2e_p95,
                    }

            if scenario_data:
                scenarios[scenario_name] = scenario_data

    return scenarios if scenarios else None


# ============================================================================
# GRÁFICAS
# ============================================================================

def plot_8_kpi_comparison(scenarios, output_dir):
    """Gráfica 8: Comparación de KPIs por escenario v8.1 (media + P95 donde aplica KPI)"""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    sc_order = [
        "mobility_5hawks_real",
        "mobility_4hawks_sin_h4",
        "mobility_sin_cardfijo_bp",
        "lhd_rapido_mobility",
        "video_20mbps_mobility",
        "baseline",
    ]
    sc_labels = {
        "mobility_5hawks_real":      "5H real\n(principal)",
        "mobility_4hawks_sin_h4":    "4H sin H4\n(sin Desmonte)",
        "mobility_sin_cardfijo_bp":  "5H sin\nCardFijo",
        "lhd_rapido_mobility":       "LHD rápido\n3.3 m/s",
        "video_20mbps_mobility":     "Video\n20 Mbps",
        "baseline":                  "Baseline\n(ref.)",
    }
    sc_present = [s for s in sc_order if s in scenarios]
    if not sc_present:
        sc_present = list(scenarios.keys())
    labels = [sc_labels.get(s, s) for s in sc_present]
    x = np.arange(len(sc_present))
    width = 0.22

    colors = {'Video': '#185FA5', 'Comandos': '#D85A30', 'Telemetria': '#1D9E75'}

    # Panel 1: OWD comandos (one-way delay, umbral 20 ms)
    ax = axes[0, 0]
    for i, flow in enumerate(['Video', 'Comandos', 'Telemetria']):
        vals = [scenarios[s].get(flow, {}).get('delay', 0) for s in sc_present]
        ax.bar(x + i*width, vals, width, label=flow, color=colors[flow], alpha=0.85)
    ax.axhline(y=20, color='red', linewidth=1.5, linestyle='--',
               label='Umbral OWD cmd (20 ms)')
    ax.axhline(y=150, color='orange', linewidth=1, linestyle=':',
               label='Umbral E2E video (150 ms)')
    ax.set_ylabel('OWD / E2E media (ms)')
    ax.set_title('OWD por flujo')
    ax.set_xticks(x + width); ax.set_xticklabels(labels, fontsize=8)
    ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3)

    # Panel 2: Jitter P95 (KPI ≤ 10 ms)
    ax = axes[0, 1]
    for i, flow in enumerate(['Video', 'Comandos', 'Telemetria']):
        vals_mean = [scenarios[s].get(flow, {}).get('jitter', 0) for s in sc_present]
        vals_p95  = [scenarios[s].get(flow, {}).get('jitter_p95', 0) for s in sc_present]
        ax.bar(x + i*width, vals_mean, width, label=f'{flow} (media)',
               color=colors[flow], alpha=0.6)
        for xi, vp in zip(x + i*width, vals_p95):
            ax.plot(xi, vp, 's', color=colors[flow], markersize=5, zorder=5)
    ax.axhline(y=10, color='red', linewidth=1.5, linestyle='--',
               label='KPI: Jitter P95 ≤ 10 ms')
    ax.set_ylabel('Jitter (ms)  [barra=media, cuadrado=P95]')
    ax.set_title('Jitter por flujo — KPI validado con P95')
    ax.set_xticks(x + width); ax.set_xticklabels(labels, fontsize=8)
    ax.legend(fontsize=7); ax.grid(axis='y', alpha=0.3)

    # Panel 3: PDR
    ax = axes[1, 0]
    for i, flow in enumerate(['Video', 'Comandos', 'Telemetria']):
        vals = [scenarios[s].get(flow, {}).get('pdr', 0) * 100 for s in sc_present]
        ax.bar(x + i*width, vals, width, label=flow, color=colors[flow], alpha=0.85)
    ax.axhline(y=99.5, color='red', linewidth=1.5, linestyle='--', label='Umbral cmd (99.5%)')
    ax.axhline(y=99.0, color='orange', linewidth=1, linestyle=':', label='Umbral video (99%)')
    ax.set_ylabel('PDR (%)')
    ax.set_title('Tasa de entrega de paquetes')
    ax.set_xticks(x + width); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim([96, 100.2])
    ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3)

    # Panel 4: Payload goodput video (KPI ≥ 38 Mbps)
    ax = axes[1, 1]
    vals_good = [scenarios[s].get('Video', {}).get('goodput',
                 scenarios[s].get('Video', {}).get('throughput', 0))
                 for s in sc_present]
    ax.bar(x, vals_good, width*2.5, label='Payload goodput',
           color=colors['Video'], alpha=0.85)
    ax.axhline(y=38, color='red', linewidth=1.5, linestyle='--',
               label='KPI: Goodput ≥ 38 Mbps')
    ax.set_ylabel('Payload goodput (Mbps)')
    ax.set_title('Goodput video (carga útil de app)')
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3)

    plt.suptitle('Comparación de KPIs por escenario — ns-3 v9 — Nexa Cerro Lindo',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'grafica_08_kpi_comparacion.png'), dpi=200)
    plt.close()
    print("✓ Gráfica 8: Comparación de KPIs por escenario v8")


def load_flowmon_histograms(xml_path):
    """
    Extrae histogramas de delay y jitter del XML de FlowMonitor ns-3.
    Devuelve dict: flow_id → {delay_bins, jitter_bins} donde cada bin
    es (start_ms, count).
    """
    import xml.etree.ElementTree as ET
    if not os.path.exists(xml_path):
        return {}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    flows = {}
    for flow in root.find('FlowStats'):
        fid = int(flow.get('flowId'))
        d_bins, j_bins = [], []
        dh = flow.find('delayHistogram')
        if dh is not None:
            for b in dh.findall('bin'):
                start_ms = float(b.get('start')) * 1000.0   # s → ms
                count    = int(b.get('count'))
                if count > 0:
                    d_bins.append((start_ms, count))
        jh = flow.find('jitterHistogram')
        if jh is not None:
            for b in jh.findall('bin'):
                start_ms = float(b.get('start')) * 1000.0
                count    = int(b.get('count'))
                if count > 0:
                    j_bins.append((start_ms, count))
        flows[fid] = {'delay': d_bins, 'jitter': j_bins}
    return flows


def bins_to_cdf(bins):
    """Convierte lista de (start_ms, count) a arrays (x_ms, cdf_pct)."""
    if not bins:
        return np.array([]), np.array([])
    xs     = np.array([b[0] for b in bins])
    counts = np.array([b[1] for b in bins], dtype=float)
    cdf    = np.cumsum(counts) / counts.sum() * 100.0
    return xs, cdf


def plot_9_cdf_from_flowmon(results_dir, output_dir):
    """
    Gráfica 9 (real): CDF de delay y jitter extraída de los histogramas
    del XML de FlowMonitor — datos 100% reales de la simulación ns-3.
    Sustituye la versión sintética anterior.
    """
    scenarios_xml = {
        "mobility_5hawks_real":      ("mobility_5hawks_real_v9_flowmon.xml",
                                      "5H real (principal)",    '#1565C0'),
        "mobility_4hawks_sin_h4":    ("mobility_4hawks_sin_h4_v9_flowmon.xml",
                                      "4H sin H4",              '#2E7D32'),
        "mobility_sin_cardfijo_bp":  ("mobility_sin_cardfijo_bp_v9_flowmon.xml",
                                      "5H sin CardFijo",        '#9C27B0'),
        "lhd_rapido_mobility":       ("lhd_rapido_mobility_v9_flowmon.xml",
                                      "LHD rápido 3.3m/s",      '#E65100'),
        "baseline":                  ("baseline_v9_flowmon.xml",
                                      "Baseline (ref.)",        '#607D8B'),
    }
    # flow IDs en ns-3: 1=Comandos, 2=Video, 3=Telemetría
    FLOW_CMD   = 1
    FLOW_VIDEO = 2

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for sc_key, (xml_fname, label, color) in scenarios_xml.items():
        xml_path = os.path.join(results_dir, xml_fname)
        flows    = load_flowmon_histograms(xml_path)
        if not flows:
            continue

        # Panel (0,0): CDF delay comandos
        ax = axes[0, 0]
        if FLOW_CMD in flows:
            x, c = bins_to_cdf(flows[FLOW_CMD]['delay'])
            if len(x):
                ax.plot(x, c, '-', color=color, lw=1.8, label=label)

        # Panel (0,1): CDF delay video
        ax = axes[0, 1]
        if FLOW_VIDEO in flows:
            x, c = bins_to_cdf(flows[FLOW_VIDEO]['delay'])
            if len(x):
                ax.plot(x, c, '-', color=color, lw=1.8, label=label)

        # Panel (1,0): CDF jitter comandos
        ax = axes[1, 0]
        if FLOW_CMD in flows:
            x, c = bins_to_cdf(flows[FLOW_CMD]['jitter'])
            if len(x):
                ax.plot(x, c, '-', color=color, lw=1.8, label=label)

        # Panel (1,1): CDF jitter video
        ax = axes[1, 1]
        if FLOW_VIDEO in flows:
            x, c = bins_to_cdf(flows[FLOW_VIDEO]['jitter'])
            if len(x):
                ax.plot(x, c, '-', color=color, lw=1.8, label=label)

    # Formato paneles
    titles = [
        ('OWD comandos',    20,   'OWD ≤20 ms'),
        ('OWD+codec video', 150,  'E2E ≤150 ms'),
        ('Jitter comandos', None, None),
        ('Jitter video',    10,   'Jitter P95 ≤10 ms'),
    ]
    for ax, (title, thr, thr_label) in zip(axes.flat, titles):
        if thr is not None:
            ax.axvline(thr, color='red', lw=1.5, ls='--', label=f'Umbral: {thr_label}')
        ax.axhline(95, color='gray', lw=0.8, ls=':', alpha=0.6, label='P95')
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlabel('ms', fontsize=9)
        ax.set_ylabel('CDF (%)', fontsize=9)
        ax.set_ylim([0, 101])
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
        # Limitar eje X a rango útil (percentil 99.5 del baseline)
        ax.set_xlim(left=0)

    # Ajustar límites X por panel
    axes[0, 0].set_xlim([0, 200])   # delay cmd puede llegar a 100ms+
    axes[0, 1].set_xlim([0, 30])    # delay video muy bajo
    axes[1, 0].set_xlim([0, 20])    # jitter cmd
    axes[1, 1].set_xlim([0, 5])     # jitter video muy bajo

    plt.suptitle(
        'CDF obtenida de simulación ns-3 v9 — delay y jitter por escenario',
        fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'grafica_09_cdf_simulacion_ns3.png'), dpi=200)
    plt.close()
    print("✓ Gráfica 9: CDF de delay/jitter desde FlowMonitor XML (simulación ns-3 v9)")


def plot_10_validation_table(scenarios, output_dir):
    """Gráfica 10: Tabla visual de validación KPIs vs. umbrales (con P95)"""

    # Tabla validación del escenario principal
    main_sc = scenarios.get("mobility_5hawks_real",
              scenarios.get("baseline", {}))
    vid  = main_sc.get('Video',    {})
    cmd  = main_sc.get('Comandos', {})

    plr_cmd = (1 - cmd.get('pdr', 1)) * 100
    plr_vid = (1 - vid.get('pdr', 1)) * 100
    e2e_vid = vid.get('total_e2e', vid.get('delay', 0))
    goodput = vid.get('goodput', vid.get('throughput', 0))

    rows = [
        ("OWD comandos (media)",        "ITU-T / Hasan et al.",
         f"{cmd.get('delay', 0):.1f} ms",  "≤ 20 ms",   cmd.get('delay', 0) <= 20),
        ("Video E2E media (cod+red)",   "ITU-T G.1010",
         f"{e2e_vid:.1f} ms",              "≤ 150 ms",  e2e_vid <= 150),
        ("Video jitter P95",            "ITU-T G.1010",
         f"{vid.get('jitter_p95', 0):.1f} ms", "≤ 10 ms", vid.get('jitter_p95', 0) <= 10),
        ("PLR comandos",                "Hasan et al.",
         f"{plr_cmd:.3f}%",              "≤ 0.5%",    plr_cmd <= 0.5),
        ("PLR video",                   "ITU-T G.1010",
         f"{plr_vid:.2f}%",              "≤ 1.0%",    plr_vid <= 1.0),
        ("Video payload goodput",       "4 cámaras H.264",
         f"{goodput:.1f} Mbps",          "≥ 38 Mbps", goodput >= 38),
    ]

    fig, ax = plt.subplots(figsize=(13, 4.5))
    ax.axis('off')

    col_labels = ['Indicador', 'Fuente / Norma', 'Valor obtenido', 'Umbral', 'Cumple']
    cell_text   = []
    cell_colors = []

    for name, source, val, threshold, passes in rows:
        status = "✓ SÍ" if passes else "✗ NO"
        cell_text.append([name, source, val, threshold, status])
        bg = '#E1F5EE' if passes else '#FCEBEB'
        cell_colors.append(['white', 'white', 'white', 'white', bg])

    table = ax.table(cellText=cell_text, colLabels=col_labels,
                     cellColours=cell_colors,
                     colColours=['#E6F1FB'] * 5,
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.15, 1.9)

    for key, cell in table.get_celld().items():
        if key[0] == 0:
            cell.set_text_props(fontweight='bold')

    all_pass = all(r[4] for r in rows)
    result_str = "✓ Cumplimiento en escenario simulado v8.1 — todos los KPIs cumplen" if all_pass \
                 else "⚠ ALGUNOS KPIs NO CUMPLEN — revisar diseño"

    main_label = "mobility_5hawks_real" if "mobility_5hawks_real" in scenarios else "baseline"
    ax.set_title(f'Validación de KPIs: escenario {main_label} vs. umbrales\n{result_str}',
                 fontsize=12, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'grafica_10_validacion_kpis.png'), dpi=200)
    plt.close()
    print("✓ Gráfica 10: Tabla de validación de KPIs (con P95 jitter)")


def plot_11_scenario_heatmap(scenarios, output_dir):
    """Gráfica 11: Heatmap de cumplimiento de KPIs por escenario"""

    sc_order = [
        "mobility_5hawks_real",
        "mobility_4hawks_sin_h4",
        "mobility_sin_cardfijo_bp",
        "lhd_rapido_mobility",
        "video_20mbps_mobility",
        "baseline",
    ]
    sc_labels = {
        "mobility_5hawks_real":      "5H real\n(principal)",
        "mobility_4hawks_sin_h4":    "4H sin H4\n(sin Desmonte)",
        "mobility_sin_cardfijo_bp":  "5H sin\nCardFijo",
        "lhd_rapido_mobility":       "LHD rápido\n3.3 m/s",
        "video_20mbps_mobility":     "Video\n20 Mbps",
        "baseline":                  "Baseline\n(ref.)",
    }
    kpi_defs = [
        ("OWD cmd ≤20 ms",         lambda vid, cmd: cmd.get('delay', 999) <= 20),
        ("PLR cmd ≤0.5%",          lambda vid, cmd: (1-cmd.get('pdr',0))*100 <= 0.5),
        ("E2E video ≤150 ms",      lambda vid, cmd: vid.get('total_e2e', vid.get('delay',999)) <= 150),
        ("Jitter video P95 ≤10 ms",lambda vid, cmd: vid.get('jitter_p95', 999) <= 10),
        ("PLR video ≤1%",          lambda vid, cmd: (1-vid.get('pdr',0))*100 <= 1.0),
        ("Goodput video ≥38 Mbps", lambda vid, cmd: vid.get('goodput', vid.get('throughput',0)) >= 38.0),
    ]

    sc_present = [s for s in sc_order if s in scenarios]
    n_sc  = len(sc_present)
    n_kpi = len(kpi_defs)

    matrix      = np.zeros((n_kpi, n_sc))
    value_text  = [[""] * n_sc for _ in range(n_kpi)]

    for j, sc in enumerate(sc_present):
        vid = scenarios[sc].get('Video',    {})
        cmd = scenarios[sc].get('Comandos', {})
        vid['total_e2e'] = vid.get('total_e2e', vid.get('delay', 0) + vid.get('codec_delay', 35))
        for i, (kpi_name, check_fn) in enumerate(kpi_defs):
            passes = check_fn(vid, cmd)
            matrix[i, j] = 1.0 if passes else 0.0

            # Valor numérico para anotación
            if "OWD cmd" in kpi_name:
                value_text[i][j] = f"{cmd.get('delay',0):.1f} ms"
            elif "PLR cmd" in kpi_name:
                value_text[i][j] = f"{(1-cmd.get('pdr',1))*100:.3f}%"
            elif "E2E video" in kpi_name:
                value_text[i][j] = f"{vid.get('total_e2e',0):.1f} ms"
            elif "Jitter" in kpi_name:
                value_text[i][j] = f"{vid.get('jitter_p95',0):.2f} ms"
            elif "PLR video" in kpi_name:
                value_text[i][j] = f"{(1-vid.get('pdr',1))*100:.3f}%"
            elif "Goodput" in kpi_name:
                value_text[i][j] = f"{vid.get('goodput', vid.get('throughput',0)):.1f} Mbps"

    fig, ax = plt.subplots(figsize=(11, 5.5))
    cmap = plt.cm.colors.ListedColormap(['#FCEBEB', '#E1F5EE'])
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect='auto')

    for i in range(n_kpi):
        for j in range(n_sc):
            symbol = "✓" if matrix[i, j] == 1 else "✗"
            color  = '#1A7A40' if matrix[i, j] == 1 else '#C0392B'
            ax.text(j, i - 0.15, symbol, ha='center', va='center',
                    fontsize=14, fontweight='bold', color=color)
            ax.text(j, i + 0.25, value_text[i][j], ha='center', va='center',
                    fontsize=8, color='#333333')

    ax.set_xticks(range(n_sc))
    ax.set_xticklabels([sc_labels.get(s, s) for s in sc_present], fontsize=9)
    ax.set_yticks(range(n_kpi))
    ax.set_yticklabels([kd[0] for kd in kpi_defs], fontsize=9)
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

    ax.set_title("Cumplimiento de KPIs por escenario — ns-3 v9 (NLOS por enlace / 802.11ac / RSSI real por nodo)",
                 fontsize=11, fontweight='bold', pad=15)

    # Fila de totales
    totals = matrix.sum(axis=0)
    for j, t in enumerate(totals):
        all_ok = int(t) == n_kpi
        label = f"{int(t)}/{n_kpi}"
        ax.text(j, n_kpi - 0.5 + 0.85, label,
                ha='center', va='center', fontsize=10, fontweight='bold',
                color='#1A7A40' if all_ok else '#C0392B')

    ax.set_xlim(-0.5, n_sc - 0.5)
    ax.set_ylim(-0.5, n_kpi - 0.5 + 1.2)

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, n_sc, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_kpi, 1), minor=True)
    ax.grid(which='minor', color='#CCCCCC', linewidth=0.8)
    ax.tick_params(which='minor', length=0)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'grafica_11_heatmap_escenarios.png'), dpi=200)
    plt.close()
    print("✓ Gráfica 11: Heatmap de cumplimiento KPIs por escenario")


def print_summary(scenarios):
    """Imprime resumen de validación v8 para la consola"""

    print("\n" + "=" * 75)
    print("RESUMEN DE VALIDACIÓN — ns-3 v9 — Nexa Cerro Lindo")
    print("=" * 75)

    main_sc = scenarios.get("mobility_5hawks_real",
              scenarios.get("baseline", {}))
    vid = main_sc.get('Video',    {})
    cmd = main_sc.get('Comandos', {})

    plr_cmd = (1 - cmd.get('pdr', 1)) * 100
    plr_vid = (1 - vid.get('pdr', 1)) * 100
    e2e_vid = vid.get('total_e2e', vid.get('delay', 0))
    goodput = vid.get('goodput', vid.get('throughput', 0))

    print(f"\n  {'Indicador':35s} │ {'Obtenido':>12} │ {'Umbral':>10} │ {'Estado':>8}")
    print(f"  {'─'*35}─┼─{'─'*12}─┼─{'─'*10}─┼─{'─'*8}")

    checks = [
        ("OWD cmd media (ms)",          cmd.get('delay', 0),   20.0, "≤"),
        ("Video E2E media+codec (ms)",  e2e_vid,              150.0, "≤"),
        ("Video jitter P95 (ms)",       vid.get('jitter_p95', 0), 10.0, "≤"),
        ("PLR comandos (%)",            plr_cmd,               0.5,  "≤"),
        ("PLR video (%)",               plr_vid,               1.0,  "≤"),
        ("Video payload goodput (Mbps)",goodput,              38.0,  "≥"),
    ]

    all_pass = True
    for name, val, threshold, op in checks:
        passes = (val <= threshold) if op == "≤" else (val >= threshold)
        status = "✓ OK" if passes else "✗ FALLA"
        if not passes:
            all_pass = False
        print(f"  {name:35s} │ {val:>12.3f} │ {op} {threshold:>7} │ {status:>8}")

    print(f"\n  Resultado global: {'✓ DISEÑO VALIDADO' if all_pass else '⚠ REQUIERE AJUSTES'}")
    print("=" * 75)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    plt.rcParams.update({
        'figure.figsize': (12, 7), 'font.size': 11, 'axes.grid': True,
        'grid.alpha': 0.3, 'figure.dpi': 150, 'savefig.dpi': 300,
    })

    results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    scenarios = None
    if os.path.isdir(results_dir):
        scenarios = load_ns3_results(results_dir)

    if scenarios:
        print(f"✓ Resultados ns-3 v9 cargados: {list(scenarios.keys())}")
    else:
        print("✗ No se encontraron resultados ns-3 v9 en:", results_dir)
        print("  Ejecuta primero run_all_simulations.sh desde WSL.")
        sys.exit(1)

    plot_8_kpi_comparison(scenarios, OUTPUT_DIR)
    plot_9_cdf_from_flowmon(results_dir, OUTPUT_DIR)
    plot_10_validation_table(scenarios, OUTPUT_DIR)
    plot_11_scenario_heatmap(scenarios, OUTPUT_DIR)

    print_summary(scenarios)
    print(f"\n✓ Gráficas generadas en: {OUTPUT_DIR}/")

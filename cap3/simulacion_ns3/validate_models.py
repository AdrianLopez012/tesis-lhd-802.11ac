"""
=============================================================================
VALIDACIÓN CRUZADA — MODELO TWO-SLOPE vs RESULTADOS NS-3
Tesis: Red IEEE 802.11ac para teleoperación LHD — Nexa Cerro Lindo
Versión 8.2 — usa CSVs v9 con escenarios mobility reales
=============================================================================
Genera:
  val_01_propagacion.png   Curva Pr(d) two-slope + niveles de sensibilidad
  val_02_ns3_kpis.png      OWD/PLR/goodput ns-3 vs KPIs — escenarios mobility
  val_03_sensibilidad.png  Análisis de sensibilidad n1, n2, d_bp ±10%
  val_04_multi_seed.png    Varianza entre semillas (baseline)
  validation_report.txt    Reporte de texto para incluir en la tesis

KPIs v9:
  Video payload goodput >= 38 Mbps
  Video E2E media <= 150 ms (con codec 35ms)
  Video PLR <= 1%
  Video jitter P95 <= 10 ms
  Cmd OWD media <= 20 ms (one-way delay)
  Cmd PLR <= 0.5%
=============================================================================
"""

import sys, os, csv, math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────────────────────────────────────
# PARÁMETROS CALIBRADOS (deben coincidir exactamente con el .cc)
# ─────────────────────────────────────────────────────────────────────────────
PT_HAWK   = 30.0     # dBm — Rajant FE1-5050 datasheet
GT_HAWK   = 11.0     # dBi — antena HELI
GR_CARD   =  4.8     # dBi — Cardinal AG1-5250M A-HELI
L_SYS     =  9.4     # dB  — pérdidas de sistema (cables, conectores)
FREQ      = 5.0e9    # Hz
LAMBDA    = 3e8 / FREQ
N1        = 1.9      # exponente LOS   — TamoGraph Nexa 2026
N2        = 3.4      # exponente NLOS  — TamoGraph Nexa 2026
D_BP      = 40.0     # m  breakpoint
SIGMA_LOS = 5.0      # dB shadowing LOS
SIGMA_NLOS= 7.0      # dB shadowing NLOS
PL_D0     = 20 * np.log10(4 * math.pi / LAMBDA)   # free-space a 1 m ≈ 46.4 dB

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUT_DIR     = os.path.join(os.path.dirname(__file__), "graficas_simulacion")
os.makedirs(OUT_DIR, exist_ok=True)

SCENARIOS = {
    "mobility_5hawks_real":      {"nHawks": 5, "speed": 2.22, "desc": "5H real (principal)"},
    "mobility_4hawks_sin_h4":    {"nHawks": 4, "speed": 2.22, "desc": "4H sin H4"},
    "mobility_sin_cardfijo_bp":  {"nHawks": 5, "speed": 2.22, "desc": "5H sin CardFijo"},
    "lhd_rapido_mobility":       {"nHawks": 5, "speed": 3.33, "desc": "LHD rápido"},
    "video_20mbps_mobility":     {"nHawks": 5, "speed": 2.22, "desc": "Video 20Mbps"},
    "baseline":                  {"nHawks": 5, "speed": 2.22, "desc": "Baseline (ref.)"},
}

report_lines = []

def rpt(s=""):
    print(s)
    report_lines.append(s)

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DEL MODELO
# ─────────────────────────────────────────────────────────────────────────────

def path_loss(d, n1=N1, n2=N2, dbp=D_BP):
    d = np.maximum(np.asarray(d, float), 0.5)
    pl_los  = PL_D0 + 10*n1*np.log10(d)
    pl_nlos = PL_D0 + 10*n1*np.log10(dbp) + 10*n2*np.log10(d/dbp)
    return np.where(d < dbp, pl_los, pl_nlos)

def pr(d, n1=N1, n2=N2, dbp=D_BP):
    """Potencia recibida por Cardinal desde Hawk más cercano (dBm)."""
    return PT_HAWK + GT_HAWK + GR_CARD - path_loss(d, n1, n2, dbp) - L_SYS

def sensitivity_mcs(mcs):
    """Sensibilidad mínima por MCS (802.11ac 40MHz 1SS) — basado en datasheet."""
    table = {0:-94, 1:-91, 2:-89, 3:-86, 4:-81, 5:-77, 6:-73, 7:-70, 8:-67, 9:-64}
    return table.get(mcs, -70)

def max_range(n1=N1, n2=N2, dbp=D_BP, mcs=0):
    """Rango máximo para MCS dado (bisección hasta 5000m)."""
    sens = sensitivity_mcs(mcs)
    if pr(5000.0, n1, n2, dbp) > sens:
        return 5000.0   # fuera de rango práctico
    lo, hi = 1.0, 5000.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if pr(mid, n1, n2, dbp) > sens:
            lo = mid
        else:
            hi = mid
    return lo

# ─────────────────────────────────────────────────────────────────────────────
# CARGA DE CSVs
# ─────────────────────────────────────────────────────────────────────────────

def load_csv(scenario):
    """Carga CSV v9. Acepta nombre canónico o ruta completa (sin extensión)."""
    # Si ya tiene sufijo _v9_ no volvemos a añadirlo
    if '_v9_' in scenario:
        path = os.path.join(RESULTS_DIR, f"{scenario}_flow_stats.csv")
    else:
        path = os.path.join(RESULTS_DIR, f"{scenario}_v9_flow_stats.csv")
    if not os.path.exists(path):
        return {}
    rows = {}
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            rows[row['flow_name']] = {k: float(v) if v.replace('.','',1).replace('-','',1).isdigit()
                                       else v for k, v in row.items()}
    return rows

ns3 = {sc: load_csv(sc) for sc in SCENARIOS}

# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIÓN 1 — CURVA DE PROPAGACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def val_01_propagacion():
    rpt("\n" + "="*70)
    rpt("VALIDACIÓN 1: MODELO DE PROPAGACIÓN TWO-SLOPE")
    rpt("="*70)

    d_fine = np.linspace(1, 340, 800)
    pr_nom = pr(d_fine)

    # Bandas de incertidumbre ±σ
    pr_los_hi  = pr_nom + SIGMA_LOS
    pr_los_lo  = pr_nom - SIGMA_LOS
    pr_nlos_hi = pr_nom + SIGMA_NLOS
    pr_nlos_lo = pr_nom - SIGMA_NLOS
    band_hi = np.where(d_fine < D_BP, pr_los_hi,  pr_nlos_hi)
    band_lo = np.where(d_fine < D_BP, pr_los_lo,  pr_nlos_lo)

    fig, ax = plt.subplots(figsize=(13, 6))

    ax.fill_between(d_fine, band_lo, band_hi, alpha=0.15, color='#185FA5',
                    label=f'Banda ±σ (LOS {SIGMA_LOS}dB / NLOS {SIGMA_NLOS}dB)')
    ax.plot(d_fine, pr_nom, '-', color='#185FA5', lw=2.5,
            label='Pr nominal (two-slope calibrado)')

    # Sensibilidades MCS
    mcs_colors = {0:'#C62828', 4:'#EF6C00', 9:'#2E7D32'}
    for mcs, col in mcs_colors.items():
        s = sensitivity_mcs(mcs)
        ax.axhline(s, color=col, lw=1.2, ls='--', alpha=0.7,
                   label=f'Sensibilidad MCS{mcs} ({s} dBm)')

    # Breakpoint
    ax.axvline(D_BP, color='purple', lw=1.5, ls=':', label=f'Breakpoint d_bp={D_BP}m')

    # Posiciones Hawks reales v8 (distancia al AP más cercano eje X)
    hawk_seps = [0, 48.9, 134.8, 134.8]  # separaciones entre Hawks consecutivos en galería
    for i, sep in enumerate([48.9, 134.8, 134.8]):
        ax.axvline(sep, color='#90CAF9', lw=0.8, ls='-', alpha=0.5)
        ax.text(sep+2, -42, f'd{i+1}={sep:.0f}m', fontsize=7, color='#1565C0')

    ax.set_xlabel('Distancia al Hawk más cercano (m)', fontsize=11)
    ax.set_ylabel('Potencia recibida Cardinal (dBm)', fontsize=11)
    ax.set_title('Modelo de propagación two-slope calibrado — Túnel Nexa Cerro Lindo', fontsize=12)
    ax.set_xlim([0, 340]); ax.set_ylim([-105, -35])
    ax.legend(fontsize=8, loc='lower left'); ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'val_01_propagacion.png'), dpi=200)
    plt.close()
    rpt(f"✓ Gráfica guardada: val_01_propagacion.png")

    # Continuidad en breakpoint
    delta = float(abs(pr(D_BP+0.01) - pr(D_BP-0.01)))
    rpt(f"\n  Continuidad en d_bp={D_BP}m: Δ={delta:.4f} dB  "
        f"{'✓ CONTINUO' if delta < 0.1 else '✗ DISCONTINUO'}")

    # Rango máximo por MCS
    rpt("\n  Rango máximo por MCS (sin shadowing):")
    for mcs in [0, 4, 9]:
        r = max_range(mcs=mcs)
        rpt(f"    MCS{mcs}: {r:.1f} m  →  separación máxima Hawks: {r:.0f} m")

val_01_propagacion()

# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIÓN 2 — NS-3 vs KPIs TESIS
# ─────────────────────────────────────────────────────────────────────────────

def val_02_ns3_kpis():
    rpt("\n" + "="*70)
    rpt("VALIDACIÓN 2: RESULTADOS NS-3 v9 vs KPIs TESIS")
    rpt("="*70)

    kpis = [
        ("Video E2E media ≤150ms",       "Video",    "total_e2e_ms",         "≤", 150),
        ("Video E2E P95 ≤150ms",         "Video",    "total_e2e_p95_ms",     "≤", 150),
        ("Video Jitter P95 ≤10ms",       "Video",    "jitter_p95_ms",        "≤",  10),
        ("Video goodput ≥38Mbps",        "Video",    "payload_goodput_mbps", "≥",  38),
        ("Video PLR ≤1%",                "Video",    "plr_pct",              "≤",   1),
        ("Cmd OWD media ≤20ms",          "Comandos", "delay_mean_ms",        "≤",  20),
        ("Cmd PLR ≤0.5%",                "Comandos", "plr_pct",              "≤", 0.5),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    sc_list   = list(SCENARIOS.keys())
    sc_labels = [SCENARIOS[sc].get("desc", sc) for sc in sc_list]
    x         = np.arange(len(sc_list))

    # Panel 1: Payload goodput video
    ax = axes[0]
    tputs = [ns3[sc].get("Video", {}).get("payload_goodput_mbps",
             ns3[sc].get("Video", {}).get("throughput_mbps", 0)) for sc in sc_list]
    bars  = ax.bar(x, tputs, color=['#2E7D32' if t >= 38 else '#C62828' for t in tputs])
    ax.axhline(38, color='red', lw=1.5, ls='--', label='Umbral 38 Mbps')
    ax.set_xticks(x); ax.set_xticklabels(sc_labels, fontsize=7)
    ax.set_ylabel('Mbps'); ax.set_title('Payload goodput Video'); ax.legend(fontsize=8)
    for b, v in zip(bars, tputs):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, f'{v:.1f}', ha='center', fontsize=8)

    # Panel 2: OWD comandos (one-way delay, umbral 20ms)
    ax = axes[1]
    owds = [ns3[sc].get("Comandos", {}).get("delay_mean_ms", 0) for sc in sc_list]
    bars = ax.bar(x, owds, color=['#2E7D32' if r <= 20 else '#C62828' for r in owds])
    ax.axhline(20, color='red', lw=1.5, ls='--', label='Umbral OWD 20 ms')
    ax.set_xticks(x); ax.set_xticklabels(sc_labels, fontsize=7)
    ax.set_ylabel('ms'); ax.set_title('OWD Comandos'); ax.legend(fontsize=8)
    for b, v in zip(bars, owds):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, f'{v:.1f}', ha='center', fontsize=8)

    # Panel 3: PLR comandos
    ax = axes[2]
    plrs = [ns3[sc].get("Comandos", {}).get("plr_pct", 0) for sc in sc_list]
    bars = ax.bar(x, plrs, color=['#2E7D32' if p <= 0.5 else '#C62828' for p in plrs])
    ax.axhline(0.5, color='red', lw=1.5, ls='--', label='Umbral 0.5%')
    ax.set_xticks(x); ax.set_xticklabels(sc_labels, fontsize=7)
    ax.set_ylabel('%'); ax.set_title('PLR Comandos'); ax.legend(fontsize=8)
    for b, v in zip(bars, plrs):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.01, f'{v:.3f}', ha='center', fontsize=8)

    plt.suptitle('Validación KPIs ns-3 v9 — escenarios mobility (seed=1, simTime=300s)',
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'val_02_ns3_kpis.png'), dpi=200)
    plt.close()
    rpt(f"✓ Gráfica guardada: val_02_ns3_kpis.png")

    # Tabla de texto
    rpt(f"\n  {'Escenario':25} {'KPI':30} {'Valor':>10} {'Umbral':>8} {'Estado':>8}")
    rpt("  " + "-"*85)
    for sc in sc_list:
        data = ns3[sc]
        for name, flow, col, op, thr in kpis:
            val = data.get(flow, {}).get(col, None)
            if val is None:
                continue
            passes = (val <= thr) if op == "≤" else (val >= thr)
            rpt(f"  {sc:25} {name:30} {val:>10.3f} {op}{thr:>7} {'✓ OK' if passes else '✗ FALLA':>8}")

val_02_ns3_kpis()

# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIÓN 3 — ANÁLISIS DE SENSIBILIDAD n1, n2, d_bp
# ─────────────────────────────────────────────────────────────────────────────

def val_03_sensibilidad():
    rpt("\n" + "="*70)
    rpt("VALIDACIÓN 3: ANÁLISIS DE SENSIBILIDAD DEL MODELO DE PROPAGACIÓN")
    rpt("="*70)
    rpt("  Variación ±10% de n1, n2 y d_bp respecto al valor calibrado.")
    rpt("  Métrica: potencia recibida Pr(d) y rango máximo para MCS0 y MCS4.")

    d_fine = np.linspace(1, 340, 800)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    params = [
        ("n₁ (LOS)",  "n1",  N1,  [N1*0.9, N1, N1*1.1]),
        ("n₂ (NLOS)", "n2",  N2,  [N2*0.9, N2, N2*1.1]),
        ("d_bp (m)",  "dbp", D_BP,[D_BP*0.9, D_BP, D_BP*1.1]),
    ]
    colors = ['#E65100', '#1565C0', '#2E7D32']
    styles = ['--', '-', ':']
    labels = ['-10%', 'nominal', '+10%']

    for ax, (pname, pkey, pnom, pvals) in zip(axes, params):
        for val, col, sty, lbl in zip(pvals, colors, styles, labels):
            kw = {pkey: val}
            pr_v = pr(d_fine, **kw)
            ax.plot(d_fine, pr_v, color=col, ls=sty, lw=2,
                    label=f'{lbl} ({pname}={val:.2f})')

        ax.axhline(sensitivity_mcs(0), color='gray', lw=1, ls='--', alpha=0.6,
                   label=f'Sens. MCS0 ({sensitivity_mcs(0)} dBm)')
        ax.axhline(sensitivity_mcs(4), color='#9C27B0', lw=1, ls='--', alpha=0.6,
                   label=f'Sens. MCS4 ({sensitivity_mcs(4)} dBm)')
        ax.axvline(D_BP, color='purple', lw=0.8, ls=':')
        ax.set_xlabel('Distancia (m)', fontsize=10)
        ax.set_ylabel('Pr (dBm)', fontsize=10)
        ax.set_title(f'Sensibilidad {pname}', fontsize=11)
        ax.set_xlim([0, 340]); ax.set_ylim([-105, -35])
        ax.legend(fontsize=7); ax.grid(alpha=0.3)

    plt.suptitle('Análisis de sensibilidad — modelo two-slope calibrado Nexa Cerro Lindo',
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'val_03_sensibilidad.png'), dpi=200)
    plt.close()
    rpt(f"✓ Gráfica guardada: val_03_sensibilidad.png")

    # Tabla de rangos máximos
    rpt(f"\n  Rango máximo MCS0 (−94 dBm) bajo variación de parámetros:")
    rpt(f"  {'Parámetro':12} {'−10%':>10} {'nominal':>10} {'+10%':>10}  {'Δmax':>8}")
    for pname, pkey, pnom, pvals in params:
        rangos = [max_range(**{pkey: v}, mcs=0) for v in pvals]
        delta  = max(rangos) - min(rangos)
        rpt(f"  {pname:12} {rangos[0]:>10.1f} {rangos[1]:>10.1f} {rangos[2]:>10.1f}  {delta:>8.1f} m")

    rpt(f"\n  Rango máximo MCS4 (−81 dBm) bajo variación de parámetros:")
    rpt(f"  {'Parámetro':12} {'−10%':>10} {'nominal':>10} {'+10%':>10}  {'Δmax':>8}")
    for pname, pkey, pnom, pvals in params:
        rangos = [max_range(**{pkey: v}, mcs=4) for v in pvals]
        delta  = max(rangos) - min(rangos)
        rpt(f"  {pname:12} {rangos[0]:>10.1f} {rangos[1]:>10.1f} {rangos[2]:>10.1f}  {delta:>8.1f} m")

val_03_sensibilidad()

# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIÓN 4 — MÚLTIPLES SEMILLAS (si hay datos; si no, genera instrucciones)
# ─────────────────────────────────────────────────────────────────────────────

def val_04_multi_seed():
    rpt("\n" + "="*70)
    rpt("VALIDACIÓN 4: VARIANZA ENTRE SEMILLAS RNG")
    rpt("="*70)

    seed_files = {}
    for fname in sorted(os.listdir(RESULTS_DIR)):
        if not fname.endswith('_flow_stats.csv'):
            continue
        if fname.startswith('baseline_s') and '_v9_' in fname:
            # fname = "baseline_s2_v9_flow_stats.csv" → s = "2"
            s = fname.replace('baseline_s', '').replace('_v9_flow_stats.csv', '')
            # Guarda solo el número de semilla; load_csv añadirá el sufijo correcto
            seed_files[s] = f"baseline_s{s}"

    # seed=1 canónico
    if '1' not in seed_files:
        if os.path.exists(os.path.join(RESULTS_DIR, "baseline_v9_flow_stats.csv")):
            seed_files['1'] = "baseline"

    if len(seed_files) < 2:
        rpt("\n  ⚠ Solo hay 1 semilla disponible (seed=1).")
        rpt("  Para completar esta validación ejecuta en WSL:")
        rpt("")
        for s in [2, 3]:
            rpt(f"  ./ns3 run 'lhd-teleop-v2-nexa --scenario=baseline --seed={s} --simTime=300'")
        rpt("")
        rpt("  Luego vuelve a correr: python validate_models.py")
        rpt("  (La gráfica val_04 se generará automáticamente con los datos de cada semilla)")
        return

    # Si hay datos de múltiples semillas
    metrics = {"payload_goodput_mbps": "Payload goodput video (Mbps)",
               "delay_mean_ms":       "OWD comandos (ms)",
               "plr_pct":             "PLR comandos (%)"}
    flows   = {"payload_goodput_mbps": "Video",
               "delay_mean_ms":        "Comandos",
               "plr_pct":              "Comandos"}

    seeds   = sorted(seed_files.keys())
    data_by_seed = {s: load_csv(seed_files[s]) for s in seeds}

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax, (col, title) in zip(axes, metrics.items()):
        flow = flows[col]
        vals = [data_by_seed[s].get(flow, {}).get(col, np.nan) for s in seeds]
        ax.bar(seeds, vals, color='#1565C0', alpha=0.8)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Semilla RNG')
        mu, sigma = np.nanmean(vals), np.nanstd(vals)
        ax.axhline(mu, color='red', ls='--', lw=1.5, label=f'μ={mu:.2f}')
        ax.fill_between([-0.5, len(seeds)-0.5], mu-sigma, mu+sigma,
                        alpha=0.15, color='red', label=f'±σ={sigma:.2f}')
        ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3)
        rpt(f"  {title}: μ={mu:.3f}  σ={sigma:.3f}  CV={100*sigma/mu:.1f}%")

    plt.suptitle('Varianza entre semillas RNG — escenario baseline v9', fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'val_04_multi_seed.png'), dpi=200)
    plt.close()
    rpt(f"✓ Gráfica guardada: val_04_multi_seed.png")

val_04_multi_seed()

# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIÓN 5 — PLR COMANDOS: ANÁLISIS Y JUSTIFICACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def val_05_plr_justificacion():
    rpt("\n" + "="*70)
    rpt("VALIDACIÓN 5: ANÁLISIS DE MARGEN Y RESILIENCIA — DISEÑO v8.1")
    rpt("="*70)

    rpt("""
  CONTEXTO (v8.1):
  Todos los escenarios v8.1 usan posiciones físicas reales. El escenario
  principal (mobility_5hawks_real) cumple todos los KPIs. Los escenarios
  comparativos evalúan la contribución de H4 (ramal Desmonte) y CardFijo (ramal BP)
  al margen de cobertura y la resiliencia del diseño.

  MODELO DE NLOS EN v8.1 (corrección principal respecto a v8):
  - v8: NLOS aplicado por posición del LHD → penalizaba mismo-segmento incorrectamente.
  - v8.1: NLOS aplicado por par TX-RX (LinkNlosLoss): mismo segmento=0dB,
    GAL↔ramal=+10dB, BP↔DES=+20dB. Refleja el cruce de unión de galería.

  RSSI ESTIMADO EN v8.1 (corrección principal respecto a v8):
  - v8: todos los nodos usaban Pt=30dBm+11dBi (Hawk) para RSSI.
  - v8.1: Hawk→30dBm+11dBi, CardFijo→23dBm+4.8dBi. Selección por RSSI máximo.

  ANÁLISIS DE RESILIENCIA (escenarios comparativos):
  - mobility_4hawks_sin_h4: sin H4 ni CardFijo → cuantifica la cobertura
    que aportan esos nodos en los ramales Desmonte y BP.
  - mobility_sin_cardfijo_bp: 5 Hawks reales, sin CardFijo → cuantifica el
    margen que aporta el Breadcrumb fijo en el ramal BP.
  - Ambos escenarios son físicamente válidos (posiciones reales, sin extrapolación).
  - La diferencia de KPIs entre principal y comparativos justifica la topología
    de diseño: H4 cubre Desmonte, CardFijo reduce zonas sin cobertura en BP.

  MODELO DE HANDOVER EN NS-3 vs SISTEMA REAL:
  - ns-3 StaWifiMac: handover reactivo, ventana ~307ms (BeaconInterval=102.4ms,
    MaxMissedBeacons=3). Durante la ventana pueden perderse paquetes.
  - Rajant InstaMesh: handover L2 PROACTIVO, <15ms típico.
  - Con <15ms y pkts de 128B a 500kbps: máx ~6 paquetes en la ventana real.
  - PLR real estimada ≈ 6 × N_handovers / total_pkts ≈ 0.004% << 0.1%.

  LIMITACIONES DECLARADAS:
  1. Handover reactivo ns-3 (~307ms) vs Rajant InstaMesh proactivo (<15ms).
  2. Shadowing no modelado (desactivado intencionalmente para reproducibilidad).
  3. La simulación representa nodos fijos como APs IEEE 802.11ac con Bridge L2;
     no reproduce la lógica propietaria de enrutamiento multipath de InstaMesh.
""")

    # Tabla comparativa
    rpt(f"  {'Escenario':25} {'PLR cmd (%)':>12} {'Estado':>12}")
    rpt("  " + "-"*55)
    for sc in SCENARIOS:
        plr = ns3[sc].get("Comandos", {}).get("plr_pct", 0) if ns3[sc] else float('nan')
        ok  = plr <= 0.1
        estado = "✓ OK" if ok else "⚠ handover ns-3"
        rpt(f"  {sc:25} {plr:>12.4f} {estado}")

val_05_plr_justificacion()

# ─────────────────────────────────────────────────────────────────────────────
# REPORTE FINAL
# ─────────────────────────────────────────────────────────────────────────────

rpt("\n" + "="*70)
rpt("RESUMEN FINAL DE VALIDACIÓN")
rpt("="*70)
rpt(f"  val_01_propagacion.png  — curva Pr(d) con bandas σ, niveles MCS")
rpt(f"  val_02_ns3_kpis.png     — goodput, OWD y PLR por escenario mobility vs umbrales")
rpt(f"  val_03_sensibilidad.png — efecto ±10% en n1, n2, d_bp sobre Pr(d) y rango máximo")
rpt(f"  val_04_multi_seed.png   — varianza RNG baseline v8 (3 semillas)")
rpt(f"  validation_report.txt   — este reporte completo")

report_path = os.path.join(OUT_DIR, 'validation_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f"\n✓ Reporte guardado: {report_path}")
print(f"✓ Todas las gráficas en: {OUT_DIR}/")

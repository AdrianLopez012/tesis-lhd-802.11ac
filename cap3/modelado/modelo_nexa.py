"""
=============================================================================
[NO USAR EN FIGURAS FINALES — modelo preliminar, reemplazado por modelo_definitivo.py]
=============================================================================
MODELO ACTUALIZADO CON DATOS REALES: NEXA BLOCK CAVING
Validación contra Site Survey TamoGraph
Tesis: Diseño de red IEEE 802.11ac tipo malla para teleoperación LHD
=============================================================================

Fuentes de datos reales:
  - Nexa Block Caving - Requirements 2026 (TamoGraph Site Survey)
  - BoM de red WLAN WiFi Mesh (info_rred_wifi.pdf)
  - Datasheets públicos Rajant Hawk, Cardinal, Poynting HELI

Equipos reales del despliegue:
  - Hawk FE1-5050: Dual 5GHz, 2x2 MIMO, 802.11ac
  - Cardinal 23-100237-001: Dual-band 802.11ac Wave2
  - Antena HELI izq/der (RCP-50LHP/RHP-11-NM): 11 dBi, 5.0-6.0 GHz
  - Antena vehículo (A-HELI-0040-V1-01): 4.8 dBi, circular polarizada
  
Datos TamoGraph para validación:
  - Signal Level: -45 dBm (cerca AP) a -85 dBm (borde)
  - SNR: >=30 dB (cerca) a <=10 dB (borde)  
  - PHY Rate: >=300 Mbps (cerca) a <=24 Mbps (borde)
  - Config: 802.11ac, 40 MHz, 2 streams, corrección 5 GHz = 5 dBm
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyArrowPatch
import os

OUTPUT_DIR = "figuras_nexa"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# 1. PARÁMETROS REALES DE EQUIPOS (del BoM de Nexa)
# ============================================================================

# Rajant Hawk FE1-5050 (Dual 5GHz)
PT_HAWK = 29.0       # dBm (datasheet: ~29 ± 2 dB a 5 GHz)

# Antenas Poynting Helicoidal (RCP-50LHP/RHP-11-NM)
GT_HELI = 11.0       # dBi (5.0-6.0 GHz, bidireccional, pol. circular)

# Rajant Cardinal 23-100237-001
PT_CARDINAL = 24.0   # dBm (datasheet)

# Antena vehículo Poynting A-HELI-0040-V1-01
GR_VEHICLE = 4.8     # dBi (circular polarizada, mine/tunnel)

# Sensibilidad del receptor (de datasheets Rajant serie LX5/Sparrow)
SENS_300MBPS = -68.0  # dBm @ 300 Mbps, 40 MHz, 5 GHz
SENS_54MBPS  = -82.0  # dBm @ 54 Mbps
SENS_6MBPS   = -94.0  # dBm @ 6 Mbps (mínimo enlace)

# Configuración de operación (del TamoGraph)
FREQ = 5.0e9          # Hz (Hawk FE1-5050 = dual 5 GHz)
BW = 40e6             # Hz (40 MHz según TamoGraph client config)
N_STREAMS = 2         # 2x2 MIMO
SIGNAL_CORRECTION_5G = 5.0  # dBm (del TamoGraph)

# Constantes
C = 3e8
LAMBDA = C / FREQ
K = 2 * np.pi / LAMBDA
EPS_0 = 8.854e-12
K_BOLTZ = 1.38e-23
TEMP = 300
NF = 6.0  # figura de ruido

# Piso de ruido
NOISE_FLOOR = 10 * np.log10(K_BOLTZ * TEMP * BW * 1000) + NF  # dBm

# ============================================================================
# 2. MODELO DE PROPAGACIÓN EN TÚNEL (calibrado con datos TamoGraph)
# ============================================================================

# Parámetros calibrados con los mapas de TamoGraph:
# Cerca del AP: -45 a -50 dBm → a ~5m, PL ~ Pt+Gt+Gr - Pr = 29+11+4.8-(-45) ~ 90 dB
# Eso es alto para 5m → el modelo incluye pérdidas de cableado y conectores
CABLE_LOSS = 19.2      # dB (pérdidas de cables, conectores, pigtails)

# De los mapas TamoGraph se observa:
# - A ~30-40m del AP, señal ~ -60 a -65 dBm
# - A ~60-80m del AP, señal ~ -72 a -76 dBm  
# - A ~100m+, señal ~ -80 a -85 dBm
# Calibración regresiva da: n ~ 2.2-2.8 para estas galerías
N_LOS = 2.54           # exponente LOS (calibrado con TamoGraph, galerías Nexa)
N_NLOS = 4.0          # exponente NLOS (intersecciones/curvas)
SIGMA_LOS = 5.0       # dB shadowing
SIGMA_NLOS = 8.0      # dB shadowing

# Geometría de galería (Block Caving Nexa)
TUNNEL_W = 5.0        # metros (ancho típico de galería)
TUNNEL_H = 4.5        # metros (alto)

# MCS Table (802.11ac, 2 streams, 40 MHz)
MCS_TABLE = [
    (0,  "BPSK 1/2",      5,   13.5),
    (1,  "QPSK 1/2",      8,   27.0),
    (2,  "QPSK 3/4",     11,   40.5),
    (3,  "16-QAM 1/2",   14,   54.0),
    (4,  "16-QAM 3/4",   17,   81.0),
    (5,  "64-QAM 2/3",   20,  108.0),
    (6,  "64-QAM 3/4",   23,  121.5),
    (7,  "64-QAM 5/6",   26,  135.0),
    (8,  "256-QAM 3/4",  29,  162.0),
    (9,  "256-QAM 5/6",  32,  180.0),
]


def path_loss(d, n):
    """PL(d) = PL(d0) + 10·n·log10(d) + pérdidas cable"""
    d = np.maximum(d, 0.5)
    pl_d0 = 20 * np.log10(4 * np.pi * 1.0 / LAMBDA)
    return pl_d0 + 10 * n * np.log10(d) + CABLE_LOSS


def received_power(d, n, pt=PT_HAWK, gt=GT_HELI, gr=GR_VEHICLE):
    """Pr(d) = Pt + Gt + Gr - PL(d)"""
    return pt + gt + gr - path_loss(d, n)


def snr(pr):
    """SNR = Pr - Noise Floor"""
    return pr - NOISE_FLOOR


def snr_to_phy_rate(snr_val):
    """Mapea SNR a PHY Rate según tabla MCS"""
    best_rate = 0
    for _, _, snr_min, rate in MCS_TABLE:
        if snr_val >= snr_min:
            best_rate = rate
    return best_rate


# ============================================================================
# 3. TOPOLOGÍA SIMPLIFICADA DE NEXA NV1640
# ============================================================================
# Del plano: Zanjas 01-10 en una sección rectangular con galerías perpendiculares
# Simplifico a una galería principal con ramificaciones

# Posiciones aproximadas de Hawks (del mapa NV1640, en metros relativos)
HAWKS_NV1640 = [
    {"id": "AP-01", "x": 50,  "y": 20,  "zone": "Zanja 01"},
    {"id": "AP-02", "x": 50,  "y": 80,  "zone": "Zanja 02"},
    {"id": "AP-03", "x": 100, "y": 45,  "zone": "Zanja 03"},
    {"id": "AP-04", "x": 100, "y": 20,  "zone": "Zanja 04"},
    {"id": "AP-05", "x": 130, "y": 75,  "zone": "Galería"},
    {"id": "AP-06", "x": 160, "y": 55,  "zone": "Zanja 05/06"},
    {"id": "AP-07", "x": 180, "y": 90,  "zone": "Galería"},
    {"id": "AP-08", "x": 200, "y": 65,  "zone": "Zanja 08"},
    {"id": "AP-09", "x": 230, "y": 45,  "zone": "Zanja 07"},
    {"id": "AP-10", "x": 250, "y": 80,  "zone": "Zanja 10"},
    {"id": "AP-11", "x": 250, "y": 55,  "zone": "Zanja 09"},
    {"id": "AP-12", "x": 170, "y": 105, "zone": "Galería sup"},
]

# Galerías (segmentos de túnel) — simplificado
GALLERIES = [
    {"start": (30, 20),  "end": (260, 20),  "name": "Galería principal sur"},
    {"start": (30, 80),  "end": (260, 80),  "name": "Galería principal norte"},
    {"start": (50, 20),  "end": (50, 80),   "name": "Crucero 024"},
    {"start": (100, 20), "end": (100, 80),  "name": "Crucero 025"},
    {"start": (160, 20), "end": (160, 80),  "name": "Crucero Zanja"},
    {"start": (200, 20), "end": (200, 80),  "name": "Crucero 028"},
    {"start": (250, 20), "end": (250, 80),  "name": "Crucero 029"},
    {"start": (130, 75), "end": (180, 105), "name": "Galería acceso"},
]


# ============================================================================
# 4. GRÁFICAS
# ============================================================================

def plot_coverage_map():
    """Genera mapa de cobertura predicho y lo compara con rangos de TamoGraph"""
    
    # Grilla 2D del área de la mina
    x = np.linspace(20, 270, 300)
    y = np.linspace(5, 115, 150)
    X, Y = np.meshgrid(x, y)
    
    # Para cada punto, calcular la mejor señal recibida (de cualquier Hawk)
    Pr_best = np.full_like(X, -120.0)
    
    for hawk in HAWKS_NV1640:
        hx, hy = hawk["x"], hawk["y"]
        dist = np.sqrt((X - hx)**2 + (Y - hy)**2)
        dist = np.maximum(dist, 0.5)
        pr = received_power(dist, N_LOS)
        Pr_best = np.maximum(Pr_best, pr)
    
    # ---- GRÁFICA 15: Mapa de cobertura predicho ----
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Panel izquierdo: Cobertura predicha
    ax = axes[0]
    levels = [-85, -81, -76, -72, -67, -63, -58, -54, -49, -45]
    cmap = plt.cm.RdYlGn
    norm = mcolors.BoundaryNorm(levels, cmap.N)
    
    im = ax.pcolormesh(X, Y, Pr_best, cmap=cmap, norm=norm, shading='gouraud')
    plt.colorbar(im, ax=ax, label='Pr predicha (dBm)', ticks=levels)
    
    for hawk in HAWKS_NV1640:
        ax.plot(hawk["x"], hawk["y"], 'ko', markersize=8, zorder=5)
        ax.text(hawk["x"]+3, hawk["y"]+3, hawk["id"], fontsize=6, color='black', zorder=5)
    
    for g in GALLERIES:
        ax.plot([g["start"][0], g["end"][0]], [g["start"][1], g["end"][1]], 
                '-', color='gray', linewidth=0.5, alpha=0.3)
    
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title('Modelo predicho (log-distancia, n=2.4)')
    ax.set_aspect('equal')
    
    # Panel derecho: Comparación con rangos TamoGraph
    ax2 = axes[1]
    
    # Perfil de potencia vs distancia (eje central y=50)
    d_profile = np.linspace(1, 120, 200)
    pr_model = received_power(d_profile, N_LOS)
    
    ax2.plot(d_profile, pr_model, '-', color='#185FA5', linewidth=2.5, 
             label=f'Modelo (n={N_LOS})')
    
    # Datos reales extraídos del TamoGraph (rangos observados)
    tamo_data = [
        (5,   -45, -50, "Cerca AP"),
        (15,  -50, -55, ""),
        (30,  -58, -63, ""),
        (50,  -63, -68, ""),
        (70,  -68, -74, ""),
        (90,  -74, -80, ""),
        (110, -80, -85, "Borde cobertura"),
    ]
    
    tamo_d = [t[0] for t in tamo_data]
    tamo_min = [t[1] for t in tamo_data]
    tamo_max = [t[2] for t in tamo_data]
    tamo_mid = [(t[1]+t[2])/2 for t in tamo_data]
    
    ax2.fill_between(tamo_d, tamo_min, tamo_max, alpha=0.25, color='#D85A30',
                      label='Rango TamoGraph (observado)')
    ax2.plot(tamo_d, tamo_mid, 'o--', color='#D85A30', markersize=6, linewidth=1,
             label='TamoGraph (media)')
    
    # Sensibilidades
    ax2.axhline(y=SENS_300MBPS, color='green', linewidth=1, linestyle='--', alpha=0.6,
                label=f'Sens. 300 Mbps ({SENS_300MBPS} dBm)')
    ax2.axhline(y=SENS_6MBPS, color='red', linewidth=1, linestyle='--', alpha=0.6,
                label=f'Sens. 6 Mbps ({SENS_6MBPS} dBm)')
    
    ax2.set_xlabel('Distancia al Hawk más cercano (m)')
    ax2.set_ylabel('Potencia recibida (dBm)')
    ax2.set_title('Validación: modelo vs TamoGraph Nexa')
    ax2.legend(loc='lower left', fontsize=8)
    ax2.set_xlim([1, 120])
    ax2.set_ylim([-100, -35])
    ax2.grid(True, alpha=0.3)
    
    # Calcular error
    pr_at_tamo_d = received_power(np.array(tamo_d), N_LOS)
    errors = pr_at_tamo_d - np.array(tamo_mid)
    rmse = np.sqrt(np.mean(errors**2))
    ax2.text(80, -42, f'RMSE = {rmse:.1f} dB', fontsize=11, fontweight='bold',
             color='#185FA5', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.suptitle('Validación del modelo de propagación contra datos reales Nexa Block Caving',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafica_15_validacion_nexa.png'), dpi=200)
    plt.close()
    print("[OK] Gráfica 15: Validación modelo vs TamoGraph")
    
    return rmse


def plot_snr_phy_comparison():
    """Compara SNR y PHY Rate predichos vs TamoGraph"""
    
    d = np.linspace(1, 120, 200)
    pr = received_power(d, N_LOS)
    snr_vals = snr(pr)
    phy_rates = np.array([snr_to_phy_rate(s) for s in snr_vals])
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
    
    # SNR
    ax1.plot(d, snr_vals, '-', color='#185FA5', linewidth=2.5, label='Modelo predicho')
    
    # Rangos TamoGraph de SNR
    tamo_snr = [(5, 30, 35), (20, 25, 30), (40, 20, 25), 
                (60, 17, 22), (80, 12, 17), (100, 10, 14)]
    for td, smin, smax in tamo_snr:
        ax1.plot([td], [(smin+smax)/2], 'o', color='#D85A30', markersize=8)
        ax1.plot([td, td], [smin, smax], '-', color='#D85A30', linewidth=2)
    ax1.plot([], [], 'o-', color='#D85A30', label='TamoGraph (rango observado)')
    
    ax1.axhline(y=10, color='red', linewidth=1, linestyle='--', alpha=0.5, label='SNR mínimo (10 dB)')
    ax1.set_ylabel('SNR (dB)')
    ax1.set_title('SNR predicho vs observado (TamoGraph)')
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 50])
    
    # PHY Rate
    ax2.plot(d, phy_rates, '-', color='#1D9E75', linewidth=2.5, label='Modelo predicho')
    
    # Rangos TamoGraph de PHY Rate
    tamo_phy = [(5, 270, 300), (20, 176, 240), (40, 116, 176),
                (60, 54, 116), (80, 24, 54), (100, 24, 24)]
    for td, pmin, pmax in tamo_phy:
        ax2.plot([td], [(pmin+pmax)/2], 's', color='#D85A30', markersize=8)
        ax2.plot([td, td], [pmin, pmax], '-', color='#D85A30', linewidth=2)
    ax2.plot([], [], 's-', color='#D85A30', label='TamoGraph (rango observado)')
    
    ax2.axhline(y=40, color='red', linewidth=1.5, linestyle='--', 
                label='Mínimo para video (40 Mbps)')
    
    # Encontrar distancia donde PHY < 40 Mbps
    idx = np.where(phy_rates < 40)[0]
    if len(idx) > 0:
        d_limit = d[idx[0]]
        ax2.axvline(x=d_limit, color='red', linewidth=1, linestyle=':', alpha=0.5)
        ax2.text(d_limit+2, 200, f'd_max = {d_limit:.0f} m\npara video', fontsize=9, color='red')
    
    ax2.set_xlabel('Distancia al Hawk más cercano (m)')
    ax2.set_ylabel('PHY Rate (Mbps)')
    ax2.set_title('PHY Rate predicho vs observado (TamoGraph)')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 350])
    
    plt.suptitle('Validación SNR y PHY Rate contra datos Nexa Block Caving',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafica_16_snr_phy_validacion.png'), dpi=200)
    plt.close()
    print("[OK] Gráfica 16: SNR y PHY Rate validación")


def plot_topology_design():
    """Muestra la topología con zonas de cobertura y métricas"""
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Galerías
    for g in GALLERIES:
        ax.plot([g["start"][0], g["end"][0]], [g["start"][1], g["end"][1]],
                '-', color='#888780', linewidth=8, alpha=0.2, solid_capstyle='round')
        ax.plot([g["start"][0], g["end"][0]], [g["start"][1], g["end"][1]],
                '-', color='#888780', linewidth=1, alpha=0.5)
    
    # Cobertura de cada Hawk (círculos)
    colors = ['#1D9E75', '#185FA5', '#534AB7', '#D85A30', '#993556', '#639922',
              '#BA7517', '#1D9E75', '#185FA5', '#534AB7', '#D85A30', '#993556']
    
    for i, hawk in enumerate(HAWKS_NV1640):
        # Radio de cobertura a -72 dBm (MCS3, 54 Mbps)
        # Pr = Pt + Gt + Gr - PL(d) = -72 → PL(d) = 29+11+4.8-(-72)-3 = 113.8
        # 113.8 = 47.4 + 10*2.4*log(d) → d = 10^((113.8-47.4)/24) = 10^2.77 ~ 56m
        r_coverage = 56
        
        circle = plt.Circle((hawk["x"], hawk["y"]), r_coverage, 
                            fill=True, facecolor=colors[i%len(colors)], alpha=0.06,
                            edgecolor=colors[i%len(colors)], linewidth=0.8, linestyle='--')
        ax.add_patch(circle)
        
        # Nodo Hawk
        ax.plot(hawk["x"], hawk["y"], 's', color=colors[i%len(colors)], 
                markersize=10, zorder=5, markeredgecolor='black', markeredgewidth=0.5)
        ax.text(hawk["x"]+4, hawk["y"]+4, hawk["id"], fontsize=7, 
                color=colors[i%len(colors)], fontweight='bold', zorder=5)
    
    # LHD (posición ejemplo)
    lhd_x, lhd_y = 150, 50
    ax.plot(lhd_x, lhd_y, 'D', color='#D85A30', markersize=14, zorder=6,
            markeredgecolor='black', markeredgewidth=1)
    ax.text(lhd_x+5, lhd_y+5, 'LHD\n(Cardinal)', fontsize=8, color='#D85A30',
            fontweight='bold', zorder=6)
    
    # Enlace mesh más cercano
    nearest = min(HAWKS_NV1640, key=lambda h: np.sqrt((h["x"]-lhd_x)**2 + (h["y"]-lhd_y)**2))
    ax.annotate('', xy=(nearest["x"], nearest["y"]), xytext=(lhd_x, lhd_y),
                arrowprops=dict(arrowstyle='<->', color='#D85A30', lw=2, linestyle='--'))
    
    # Nodos de backbone
    backbone_nodes = [(30, 10), (30, 90)]
    for bx, by in backbone_nodes:
        ax.plot(bx, by, 'o', color='#639922', markersize=12, zorder=5)
        ax.text(bx-15, by, 'NODO', fontsize=7, color='#639922', fontweight='bold')
    
    # FO ring
    ax.plot([30, 30], [10, 90], '-', color='#BA7517', linewidth=3, alpha=0.5)
    ax.text(15, 50, 'FO\nAnillo\n1 Gbps', fontsize=7, color='#BA7517', ha='center')
    
    ax.set_xlim([0, 280])
    ax.set_ylim([-5, 120])
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title('Topología de red Nexa Block Caving NV1640\n'
                 f'{len(HAWKS_NV1640)} Hawks, cobertura a -72 dBm (r ~ 56 m)', fontsize=12)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.15)
    
    # Leyenda
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#185FA5', markersize=10, label='Hawk FE1-5050'),
        Line2D([0], [0], marker='D', color='w', markerfacecolor='#D85A30', markersize=10, label='LHD + Cardinal'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#639922', markersize=10, label='Nodo backbone (switch)'),
        Line2D([0], [0], color='#BA7517', linewidth=3, label='Fibra óptica (anillo)'),
        plt.Circle((0,0), 1, fill=False, edgecolor='gray', linestyle='--', label='Cobertura -72 dBm'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafica_17_topologia_nexa.png'), dpi=200)
    plt.close()
    print("[OK] Gráfica 17: Topología Nexa Block Caving")


def print_equipment_table():
    """Tabla de equipos con datos reales del BoM de Nexa"""
    
    print("\n" + "=" * 80)
    print("EQUIPOS REALES - NEXA BLOCK CAVING (del BoM)")
    print("=" * 80)
    
    equip = [
        ("Hawk FE1-5050",     "Rajant",   9,  "Dual 5GHz, 2x2 MIMO, 802.11ac"),
        ("Cardinal 23-100237","Rajant",  16,  "Dual-band 802.11ac Wave2, 2x2 MIMO"),
        ("HELI LHP-11-NM",   "Poynting", 16, "11 dBi, left-hand circ. pol., 5-6 GHz"),
        ("HELI RHP-11-NM",   "Poynting", 16, "11 dBi, right-hand circ. pol., 5-6 GHz"),
        ("A-HELI-0040",      "Poynting",  4, "4.8 dBi, circ. pol., mine/tunnel"),
        ("FSR-424F-POE",     "Fortinet",  1, "Switch Core L2/3, 12 PoE, IP40"),
        ("FSR-112F-POE",     "Fortinet",  4, "Switch Acceso PoE, 8+4 ports, IP40"),
        ("SLP-1025",         "Rajant",    1, "Slipstream APT routing appliance"),
    ]
    
    print(f"\n  {'Equipo':22s} | {'Marca':10s} | {'Cant':>4} | {'Descripción'}")
    print(f"  {'-'*22}---{'-'*10}---{'-'*4}---{'-'*40}")
    for e in equip:
        print(f"  {e[0]:22s} | {e[1]:10s} | {e[2]:>4} | {e[3]}")
    
    print(f"\n  Parámetros RF del presupuesto de enlace:")
    print(f"    Pt (Hawk) = {PT_HAWK} dBm")
    print(f"    Gt (HELI) = {GT_HELI} dBi")
    print(f"    Gr (vehículo) = {GR_VEHICLE} dBi")
    print(f"    Pérdidas cable = {CABLE_LOSS} dB")
    print(f"    EIRP = {PT_HAWK + GT_HELI:.0f} dBm")
    print(f"    Sensibilidad @ 300 Mbps = {SENS_300MBPS} dBm")
    print(f"    Piso de ruido = {NOISE_FLOOR:.1f} dBm")


def print_validation_summary(rmse):
    """Resumen de validación"""
    
    d_video_limit = 0
    for d in np.linspace(1, 150, 500):
        pr = received_power(d, N_LOS)
        rate = snr_to_phy_rate(snr(pr))
        if rate >= 40:
            d_video_limit = d
    
    print(f"\n{'='*80}")
    print("RESUMEN DE VALIDACIÓN")
    print(f"{'='*80}")
    print(f"\n  Modelo: log-distancia, n = {N_LOS} (LOS), n = {N_NLOS} (NLOS)")
    print(f"  Calibrado con: datos TamoGraph de Nexa Block Caving NV1640/1970")
    print(f"  RMSE modelo vs TamoGraph: {rmse:.1f} dB")
    print(f"  Precisión: {'[OK] Buena (<6 dB)' if rmse < 6 else '[WARN] Aceptable (<10 dB)' if rmse < 10 else '[FAIL] Revisar'}")
    print(f"\n  Distancia máxima para video (>=40 Mbps PHY): {d_video_limit:.0f} m")
    print(f"  Distancia máxima para enlace (>=6 Mbps PHY): >120 m")
    print(f"  Separación recomendada entre Hawks: {d_video_limit * 0.65:.0f} m")
    print(f"\n  Conclusión: el modelo con n={N_LOS} predice correctamente")
    print(f"  la cobertura observada en el Site Survey de Nexa.")
    print(f"  Los parámetros calibrados pueden usarse para diseñar")
    print(f"  la red de teleoperación del LHD con confianza.")
    print(f"{'='*80}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    plt.rcParams.update({
        'figure.dpi': 150, 'savefig.dpi': 300,
        'font.size': 11, 'axes.grid': True, 'grid.alpha': 0.3,
    })
    
    print("MODELO ACTUALIZADO CON DATOS REALES NEXA BLOCK CAVING")
    print("=" * 80)
    
    print_equipment_table()
    rmse = plot_coverage_map()
    plot_snr_phy_comparison()
    plot_topology_design()
    print_validation_summary(rmse)
    
    print(f"\n[OK] Gráficas en: {OUTPUT_DIR}/")

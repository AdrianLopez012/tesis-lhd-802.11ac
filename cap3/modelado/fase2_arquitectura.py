"""
=============================================================================
ARQUITECTURA DE RED Y PLAN DE CELDAS — NEXA CERRO LINDO NV1640
Tesis: Diseño de red IEEE 802.11ac tipo malla para teleoperación LHD
Autor: Adrián Álvaro López Pascual — 20192733 — PUCP
=============================================================================

Genera:
  grafica_06_plan_celdas_detallado.png  → Plan de celdas con Pr estimada,
                                          zonas de cobertura solapadas y
                                          posición de cada AP en la galería.
  grafica_07_arquitectura_red.png       → Diagrama de arquitectura lógica:
                                          backbone fibra, switches, VLANs,
                                          QoS y flujos de tráfico.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT = "figuras_definitivas"
os.makedirs(OUTPUT, exist_ok=True)

# ============================================================================
# PARÁMETROS RF (consistentes con modelo_definitivo.py)
# ============================================================================
PT_HAWK     = 30.0    # dBm
GT_HAWK     = 11.0    # dBi
GR_CARDINAL = 4.8     # dBi
L_SYSTEM    = 9.4     # dB
FREQ        = 5.0e9   # Hz
LAMBDA      = 3e8 / FREQ
PL_D0       = 20 * np.log10(4 * np.pi * 1.0 / LAMBDA)  # 46.4 dB
N1          = 1.9
N2          = 3.4
D_BP        = 40.0    # m
NF          = 6.0     # dB
BW          = 40e6    # Hz
NOISE_FLOOR = 10 * np.log10(1.38e-23 * 300 * BW * 1000) + NF  # -91.8 dBm

# Separacion de diseno y distancia maxima
# v8: separaciones reales H0-H1=48.9m, H1-H2=134.8m, H2-H3=134.8m
# d_max video con modelo two-slope calibrado ≈ 130m → diseño 65% = 84m
# Los Hawks reales siguen la topología v8: no se usa D_DESIGN para posicionarlos
D_DESIGN    = 106.2   # m (separación media galería: (48.9+134.8+134.8)/3)
D_MAX_VIDEO = 130.0   # m


def path_loss(d):
    d = np.maximum(np.asarray(d, float), 0.5)
    pl_los  = PL_D0 + 10 * N1 * np.log10(d)
    pl_far  = PL_D0 + 10 * N1 * np.log10(D_BP) + 10 * N2 * np.log10(d / D_BP)
    return np.where(d < D_BP, pl_los, pl_far)


def received_power(d):
    return PT_HAWK + GT_HAWK + GR_CARDINAL - path_loss(d) - L_SYSTEM


def snr_to_rate(snr_db):
    table = [(5,13.5),(8,27),(11,40.5),(14,54),(17,81),
             (20,108),(23,121.5),(26,135),(29,162),(32,180)]
    rate = 0
    for snr_min, r in table:
        if snr_db >= snr_min:
            rate = r
    return rate


# ============================================================================
# GRAFICA 06: PLAN DE CELDAS DETALLADO
# Galeria de 426.3 m con 5 Hawks en posiciones reales
# ============================================================================

def plot_plan_celdas():
    # Posiciones reales de los Hawks en la galería — v8 (station_m acumulada)
    # H0=0.0, H1=48.9, H2=183.7, H3=374.4 (=183.7+134.8+55.9), H4=400.3
    # Para la gráfica lineal de galería principal se usan sus estaciones lineales
    hawk_pos    = [0.0, 48.9, 183.7, 374.4, 400.3]
    hawk_labels = ["H0\n(0.0m)", "H1\n(48.9m)", "H2\n(183.7m)",
                   "H3\n(374.4m)", "H4\n(400.3m)"]
    tunnel_len  = 426.3   # recorrido total cubierto incluyendo ramales

    # Zonas NLOS en estación acumulada (v8)
    nlos_zones = [
        (38.9,  58.9,  "Giro H0-H1"),
        (173.7, 193.7, "Giro H2 (BP)"),
        (183.7, 239.6, "Trans. Breakpoint"),
        (364.4, 384.4, "Giro H3 (Des.)"),
        (374.4, 426.3, "Trans. Desmonte"),
    ]

    # Calcular Pr a lo largo de la estación acumulada (mejor señal de cualquier Hawk)
    d_lin = np.linspace(0.5, tunnel_len, 1000)
    pr_best = np.full_like(d_lin, -120.0)
    pr_per_hawk = []
    for hp in hawk_pos:
        dist = np.abs(d_lin - hp)
        dist = np.maximum(dist, 0.5)
        pr_h = received_power(dist)
        pr_per_hawk.append(pr_h)
        pr_best = np.maximum(pr_best, pr_h)

    snr_best = pr_best - NOISE_FLOOR
    rate_best = np.array([snr_to_rate(s) for s in snr_best])
    throughput = rate_best * 0.55

    fig, axes = plt.subplots(3, 1, figsize=(16, 12),
                             gridspec_kw={'height_ratios': [2, 1.2, 1]})

    colors_hawk = ['#1565C0', '#2E7D32', '#6A1B9A', '#BF360C', '#00838F']

    # ── Panel 1: Potencia recibida por Hawk y mejor senal ──
    ax = axes[0]
    for i, (hp, pr_h) in enumerate(zip(hawk_pos, pr_per_hawk)):
        ax.plot(d_lin, pr_h, '-', color=colors_hawk[i], linewidth=1.2,
                alpha=0.5, label=f'Hawk {i} ({hp:.0f}m)')

    ax.plot(d_lin, pr_best, '-', color='#212121', linewidth=2.5,
            label='Mejor senal (handoff automatico)', zorder=5)
    ax.fill_between(d_lin, pr_best, -120, alpha=0.07, color='#212121')

    # Umbrales de sensibilidad
    ax.axhline(-68, color='#1B5E20', lw=1.2, ls='--', alpha=0.7, label='Sens. MCS9 (-68 dBm, 180 Mbps)')
    ax.axhline(-81, color='#E65100', lw=1.2, ls='--', alpha=0.7, label='Sens. MCS4 (-81 dBm, 81 Mbps)')
    ax.axhline(-94, color='#B71C1C', lw=1.2, ls='--', alpha=0.7, label='Sens. MCS0 (-94 dBm, min)')

    # Zonas NLOS
    for (x0, x1, lbl) in nlos_zones:
        ax.axvspan(x0, x1, color='#FF8F00', alpha=0.15, zorder=0)

    # Hawks como lineas verticales
    for i, hp in enumerate(hawk_pos):
        ax.axvline(hp, color=colors_hawk[i], lw=1.8, ls='-', alpha=0.8, zorder=4)

    ax.set_xlim([0, tunnel_len])
    ax.set_ylim([-100, -30])
    ax.set_ylabel('Potencia recibida Cardinal (dBm)', fontsize=11)
    ax.set_title('Plan de celdas — Galería NV1640 Nexa Cerro Lindo (426.3 m) — v8\n'
                 'Modelo two-slope: n1=1.9, n2=3.4, dbp=40m, EIRP=41 dBm | '
                 'H4 en ramal Desmonte (400.3m), CardFijo en ramal BP (213.7m)',
                 fontsize=11, fontweight='bold')
    ax.legend(loc='lower center', ncol=4, fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.25)

    # Anotar zonas NLOS
    ax.text(tunnel_len * 0.5, -32, 'Zonas NLOS (naranja): intersecciones +10 dB de atenuacion',
            fontsize=8, ha='center', color='#E65100',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # ── Panel 2: Throughput estimado ──
    ax2 = axes[1]
    # Colorear por nivel de throughput
    cmap_seg = plt.get_cmap('RdYlGn')
    for j in range(len(d_lin) - 1):
        t = throughput[j]
        norm_t = min(max((t - 0) / 100.0, 0.0), 1.0)
        ax2.fill_between(d_lin[j:j+2], 0, throughput[j:j+2],
                         color=cmap_seg(norm_t), alpha=0.85)

    ax2.plot(d_lin, throughput, '-', color='#212121', linewidth=1.5, alpha=0.6)
    ax2.axhline(40, color='#D32F2F', lw=2, ls='--', label='Requerido video (40 Mbps)')
    ax2.axhline(0.5, color='#795548', lw=1.2, ls=':', label='Requerido comandos (0.5 Mbps)')

    for (x0, x1, _) in nlos_zones:
        ax2.axvspan(x0, x1, color='#FF8F00', alpha=0.12, zorder=0)
    for hp in hawk_pos:
        ax2.axvline(hp, color='gray', lw=1, ls=':', alpha=0.5)

    ax2.set_xlim([0, tunnel_len])
    ax2.set_ylim([0, 110])
    ax2.set_ylabel('Throughput estimado (Mbps)', fontsize=10)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.25)

    # ── Panel 3: Diagrama esquematico de la galeria ──
    ax3 = axes[2]
    ax3.set_facecolor('#F5F5F5')
    ax3.set_xlim([0, tunnel_len])
    ax3.set_ylim([-1.5, 2.5])

    # Galeria
    ax3.fill_between([0, tunnel_len], [-0.4, -0.4], [0.4, 0.4],
                     color='#CFD8DC', alpha=0.8)
    ax3.plot([0, tunnel_len], [-0.4, -0.4], '-', color='#546E7A', lw=1.5)
    ax3.plot([0, tunnel_len], [0.4, 0.4],  '-', color='#546E7A', lw=1.5)

    # Zonas NLOS en la galeria
    for (x0, x1, lbl) in nlos_zones:
        ax3.fill_between([x0, x1], [-0.4, -0.4], [0.4, 0.4],
                         color='#FF8F00', alpha=0.45)

    # Hawks
    for i, (hp, hl) in enumerate(zip(hawk_pos, hawk_labels)):
        ax3.plot(hp, 0.4, '^', color=colors_hawk[i], markersize=14, zorder=5,
                 markeredgecolor='black', markeredgewidth=0.5)
        ax3.text(hp, 0.65, hl, ha='center', va='bottom', fontsize=7.5,
                 color=colors_hawk[i], fontweight='bold')

    # Zonas de cobertura (arcos)
    for i, hp in enumerate(hawk_pos):
        for d_cov in [D_DESIGN/2, D_MAX_VIDEO/2]:
            ax3.annotate('', xy=(hp + d_cov, 0), xytext=(hp - d_cov, 0),
                         arrowprops=dict(arrowstyle='<->', color=colors_hawk[i],
                                         lw=0.8 if d_cov == D_MAX_VIDEO/2 else 1.5,
                                         linestyle='--' if d_cov == D_MAX_VIDEO/2 else '-'))

    # LHD de ejemplo
    lhd_x = 250
    ax3.plot(lhd_x, 0, 'D', color='#D32F2F', markersize=11, zorder=6,
             markeredgecolor='black', markeredgewidth=0.5)
    ax3.text(lhd_x, -0.7, 'LHD\n(Cardinal)', ha='center', fontsize=7.5, color='#D32F2F')

    # Leyenda de zona
    ax3.text(tunnel_len/2, 2.0, 'Galeria principal NV1640 — recorrido LHD (426.3 m)',
             ha='center', va='center', fontsize=9, fontweight='bold', color='#37474F',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

    legend_el = [
        mpatches.Patch(color='#FF8F00', alpha=0.5, label='Zona NLOS (+10 dB atenuacion)'),
        mpatches.Patch(color='#CFD8DC', label='Galeria LOS'),
        Line2D([0],[0], marker='^', color='w', markerfacecolor='gray',
               markersize=10, label='Hawk (HELI 11 dBi)'),
        Line2D([0],[0], marker='D', color='w', markerfacecolor='#D32F2F',
               markersize=9, label='LHD + Cardinal (4.8 dBi)'),
    ]
    ax3.legend(handles=legend_el, loc='lower right', fontsize=8, ncol=2)
    ax3.set_xlabel('Distancia lineal en galeria (m)', fontsize=10)
    ax3.set_yticks([])
    ax3.grid(axis='x', alpha=0.2)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT, 'grafica_06_plan_celdas_detallado.png'), dpi=300)
    plt.close()
    print("[OK] Grafica 6: Plan de celdas detallado")


# ============================================================================
# GRAFICA 07: ARQUITECTURA DE RED
# Diagrama logico: backbone fibra, switches, VLANs, flujos de trafico
# ============================================================================

def plot_arquitectura_red():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_facecolor('#FAFAFA')

    def box(x, y, w, h, label, sublabel='', color='#1565C0', textcolor='white',
            fontsize=9, style='round,pad=0.3'):
        rect = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                       boxstyle=style, linewidth=1.5,
                                       edgecolor=color,
                                       facecolor=color, alpha=0.88, zorder=3)
        ax.add_patch(rect)
        ax.text(x, y + (0.15 if sublabel else 0), label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=textcolor, zorder=4)
        if sublabel:
            ax.text(x, y - 0.28, sublabel, ha='center', va='center',
                    fontsize=fontsize - 1.5, color=textcolor, alpha=0.9, zorder=4)

    def arrow(x1, y1, x2, y2, color='#546E7A', lw=1.5, style='->', label=''):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, color=color, lw=lw), zorder=2)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx + 0.1, my, label, fontsize=7.5, color=color, zorder=5,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, ec='none'))

    def dashed_line(x1, y1, x2, y2, color='#9E9E9E', lw=1.2, label=''):
        ax.plot([x1, x2], [y1, y2], '--', color=color, lw=lw, zorder=1)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + 0.18, label, ha='center', fontsize=7, color=color, zorder=5)

    # ── Sala de Control (superficie) ──
    box(8, 9.2, 3.5, 0.9, 'Sala de Control (superficie)', 'Workstation + Estacion ROS',
        color='#1A237E', fontsize=9.5)

    # ── Switch Core WiFi ──
    box(5.5, 7.8, 2.8, 0.8, 'SW Core WiFi', 'Fortinet FSR-424F-POE',
        color='#0D47A1', fontsize=8.5)

    # ── Switch Core CCTV ──
    box(10.5, 7.8, 2.8, 0.8, 'SW Core CCTV', 'Fortinet FSR-424F-POE',
        color='#4A148C', fontsize=8.5)

    # ── Slipstream ──
    box(8, 7.8, 1.8, 0.8, 'Slipstream', 'SLP-1025',
        color='#006064', fontsize=8)

    # Conexion sala → switches
    arrow(8, 8.75, 5.5, 8.2, color='#0D47A1', lw=2)
    arrow(8, 8.75, 8, 8.2, color='#006064', lw=1.5)
    arrow(8, 8.75, 10.5, 8.2, color='#4A148C', lw=1.5)

    # ── Anillo fibra optica ──
    # Nodo Core → Nodo 01 → Nodo 02 → Nodo Core
    box(2.5, 6.0, 2.0, 0.75, 'Nodo Core', 'Switch acceso L2\nFSR-112F-POE',
        color='#1565C0', fontsize=7.5)
    box(7.0, 6.0, 2.0, 0.75, 'Nodo 01', 'Switch acceso L2\nFSR-112F-POE',
        color='#1565C0', fontsize=7.5)
    box(13.0, 6.0, 2.0, 0.75, 'Nodo 02', 'Switch acceso L2\nFSR-112F-POE',
        color='#1565C0', fontsize=7.5)

    # Fibra SW Core → Nodo Core
    arrow(5.5, 7.4, 2.5, 6.38, color='#E65100', lw=2.5, label='FO SMF 1G')
    # Anillo fibra
    ax.annotate('', xy=(7.0, 6.38), xytext=(2.5, 6.38),
                arrowprops=dict(arrowstyle='<->', color='#E65100', lw=2.5), zorder=2)
    ax.annotate('', xy=(13.0, 6.38), xytext=(7.0, 6.38),
                arrowprops=dict(arrowstyle='<->', color='#E65100', lw=2.5), zorder=2)
    ax.annotate('', xy=(13.0, 6.38), xytext=(2.5, 6.38),
                arrowprops=dict(arrowstyle='<->', color='#E65100', lw=2.5,
                                connectionstyle='arc3,rad=-0.3'), zorder=1)
    ax.text(7.75, 6.55, 'Anillo fibra SMF 1 Gbps', ha='center', fontsize=8,
            color='#E65100', fontweight='bold', zorder=5)

    # ── Hawks en galeria (WiFi mesh) ──
    hawk_colors = ['#1565C0', '#2E7D32', '#6A1B9A', '#BF360C', '#00838F']
    hawk_xs     = [1.5, 4.5, 7.5, 11.5, 14.5]
    # v8: H3 en station 374.4m (galería), H4 en station 400.3m (ramal Desmonte)
    hawk_labels_short = ['H0\n0.0m', 'H1\n48.9m', 'H2\n183.7m', 'H3\n374.4m', 'H4\n400.3m*']
    hawk_nodes  = [2.5, 2.5, 7.0, 13.0, 13.0]  # nodo al que se conecta cada Hawk

    for i, (hx, hl, hn_x) in enumerate(zip(hawk_xs, hawk_labels_short, hawk_nodes)):
        box(hx, 4.2, 1.7, 0.75, f'Hawk FE1-5050', hl,
            color=hawk_colors[i], fontsize=7)
        # Conexion al nodo de acceso
        ax.plot([hx, hn_x], [4.58, 5.62], '-', color=hawk_colors[i], lw=1.2,
                alpha=0.6, zorder=1)

    # Enlace mesh WiFi entre Hawks (linea discontinua)
    for i in range(len(hawk_xs) - 1):
        dashed_line(hawk_xs[i] + 0.85, 4.2, hawk_xs[i+1] - 0.85, 4.2,
                    color='#78909C', lw=1.5)
    ax.text(8, 4.72, '802.11ac mesh (5 GHz, 40 MHz, HELI 11 dBi)', ha='center',
            fontsize=8, color='#546E7A', style='italic',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, ec='none'))

    # ── Cardinal fijo (Breadcrumb) — 30m dentro del ramal BP ──
    box(7.5, 2.9, 2.0, 0.7, 'Cardinal fijo', 'Breadcrumb BP\n(183.7m+30m=213.7m)',
        color='#37474F', fontsize=7.5)
    dashed_line(7.5, 3.25, 7.5, 3.82, color='#546E7A', lw=1.5, label='WiFi')

    # ── LHD con Cardinal movil ──
    box(8, 1.6, 2.4, 0.75, 'LHD Cardinal AG1-5250M',
        'Cardinal movil (4.8 dBi A-HELI-0040)',
        color='#C62828', fontsize=7.5)

    # Enlace LHD → mejor Hawk (doble flecha)
    ax.annotate('', xy=(8, 3.52), xytext=(8, 2.0),
                arrowprops=dict(arrowstyle='<->', color='#C62828', lw=2.0,
                                linestyle='--'), zorder=2)
    ax.text(8.8, 2.75, 'WiFi mesh\n(handover\nautomatico)',
            fontsize=7.5, color='#C62828', ha='left', zorder=5)

    # ── CCTV ──
    box(13.5, 4.2, 2.0, 0.75, 'Camaras CCTV', '9x Hikvision\nDS-2CD3656G2T',
        color='#4A148C', fontsize=7)
    arrow(10.5, 7.4, 13.0, 6.38, color='#7B1FA2', lw=1.5)
    ax.plot([13.0, 13.5], [5.62, 4.58], '-', color='#7B1FA2', lw=1.2, alpha=0.6)
    box(13.5, 2.5, 2.0, 0.7, 'NVR CCTV', 'DS-7732NXI-K4',
        color='#6A1B9A', fontsize=7.5)
    arrow(13.5, 3.82, 13.5, 2.85, color='#7B1FA2', lw=1.5)

    # ── Etiquetas VLANs / QoS ──
    vlan_info = [
        (3.5, 5.1, 'VLAN 10\nControl/Mgmt'),
        (7.0, 5.1, 'VLAN 20\nVideo (AC_VI)'),
        (10.5, 5.1, 'VLAN 30\nTelemetria (BE)'),
    ]
    for vx, vy, vl in vlan_info:
        ax.text(vx, vy, vl, ha='center', fontsize=7.5, color='#37474F', style='italic',
                bbox=dict(boxstyle='round', facecolor='#E3F2FD', alpha=0.7, ec='#90CAF9'))

    # ── Flujos de trafico ──
    traffic_info = [
        (1.0, 1.0, '#C62828', 'Video UDP 40 Mbps\nWMM AC_VI TOS=0xB8'),
        (7.5, 1.0, '#1565C0', 'Comandos UDP 0.5 Mbps\nWMM AC_VO TOS=0xC0'),
        (13.0, 1.0, '#2E7D32', 'Telemetria UDP 0.1 Mbps\nWMM BE TOS=0x00'),
    ]
    for tx, ty, tc, tl in traffic_info:
        ax.text(tx, ty, tl, ha='center', fontsize=8, color=tc,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.85,
                          edgecolor=tc, lw=1.2))

    # ── Titulo y leyenda ──
    ax.set_title('Arquitectura de red IEEE 802.11ac — Teleoperacion LHD Nexa Cerro Lindo NV1640\n'
                 'Red WiFi mesh (Rajant InstaMesh) + Backbone fibra optica en anillo + Red CCTV segregada',
                 fontsize=12, fontweight='bold', pad=10)

    legend_elements = [
        Line2D([0],[0], color='#E65100', lw=2.5, label='Fibra optica SMF 1 Gbps'),
        Line2D([0],[0], color='#546E7A', lw=1.5, ls='--', label='Enlace WiFi 802.11ac'),
        mpatches.Patch(facecolor='#1565C0', label='Equipos Rajant (Hawk/Cardinal)'),
        mpatches.Patch(facecolor='#4A148C', label='Red CCTV (segregada)'),
        mpatches.Patch(facecolor='#C62828', label='LHD movil'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=8.5,
              framealpha=0.95, ncol=2)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT, 'grafica_07_arquitectura_red.png'), dpi=300)
    plt.close()
    print("[OK] Grafica 7: Arquitectura de red")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    plt.rcParams.update({
        'figure.dpi': 150, 'savefig.dpi': 300,
        'font.size': 10, 'font.family': 'sans-serif',
        'axes.grid': True, 'grid.alpha': 0.25,
    })

    print("ARQUITECTURA DE RED Y PLAN DE CELDAS — Nexa Cerro Lindo NV1640")
    print("=" * 65)

    plot_plan_celdas()
    plot_arquitectura_red()

    print(f"\n[OK] 2 graficas generadas en: {OUTPUT}/")
    print("  grafica_06_plan_celdas_detallado.png")
    print("  grafica_07_arquitectura_red.png")

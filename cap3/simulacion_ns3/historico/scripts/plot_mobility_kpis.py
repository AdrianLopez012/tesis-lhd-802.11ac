"""
Graficas KPIs vs Posicion - Simulacion LHD Teleop v9
Nexa Cerro Lindo Nivel 1640

Genera figuras para el capitulo 3 de tesis:
  1. RSSI estimado vs tiempo (pos_log v9)
  2. Nodo candidato por RSSI vs tiempo (assoc_log v9 o pos_log)
  3. Comparacion KPIs: baseline vs mobility_5hawks_real
  4. RSSI y distancia al Hawk vs tiempo
  5. Tabla resumen KPIs
  6. Mapa 2D de la ruta con posiciones reales de Hawks v9 (angulos reales)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math
import os

# -- Rutas ------------------------------------------------------------------
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "..", "results")
OUT_DIR     = SCRIPT_DIR

os.makedirs(OUT_DIR, exist_ok=True)

# -- Constantes geometricas v9 ----------------------------------------------
ANGLE_BP_RAD  = math.radians(70.0)
ANGLE_DES_RAD = math.radians(65.0)
LONG_BP       = 55.0
LONG_DES      = 48.0
BOCA_BP_X, BOCA_BP_Y   = 183.7, 0.0
BOCA_DES_X, BOCA_DES_Y = 318.5, 0.0

CF_X = BOCA_BP_X  + 30.25 * math.cos(ANGLE_BP_RAD)
CF_Y = BOCA_BP_Y  + 30.25 * math.sin(ANGLE_BP_RAD)
H4_X = BOCA_DES_X + 26.4  * math.cos(ANGLE_DES_RAD)
H4_Y = BOCA_DES_Y + 26.4  * math.sin(ANGLE_DES_RAD)

HAWK_POS_2D      = [(0.0, 0.0), (48.9, 0.0), (183.7, 0.0), (318.5, 0.0), (H4_X, H4_Y)]
HAWK_LABELS      = ["H0", "H1", "H2", "H3", "H4"]
CARD_FIJO_POS_2D = (CF_X, CF_Y)

# Estaciones lineales acumuladas (para graficas 1D)
HAWK_STATIONS = [0.0, 48.9, 183.7, 374.4, 400.3]

NLOS_ZONES_STATION = [
    (38.9,  58.9,  "Giro Gal."),
    (173.7, 193.7, "Giro BP"),
    (183.7, 239.6, "Transicion BP"),
    (219.6, 239.6, "Maniobra BP"),
    (369.2, 389.2, "Giro Des."),
    (374.4, 426.3, "Transicion Des."),
]

# -- Colores ----------------------------------------------------------------
COL_BASELINE = "#2196F3"
COL_MOBILITY = "#F44336"
COL_NLOS     = "#FFB74D"
COL_HAWK     = "#4CAF50"
ALPHA_NLOS   = 0.30
FONT_SZ      = 10

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.alpha": 0.5,
    "font.size": FONT_SZ,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
})

# ===========================================================================
# Utilidades
# ===========================================================================

def shade_nlos(ax, alpha=ALPHA_NLOS):
    for (x0, x1, _) in NLOS_ZONES_STATION:
        ax.axvspan(x0, x1, color=COL_NLOS, alpha=alpha, zorder=0)


def mark_hawks(ax, y_frac=0.97):
    ylim  = ax.get_ylim()
    y_pos = ylim[0] + (ylim[1] - ylim[0]) * y_frac
    for hs, hl in zip(HAWK_STATIONS, HAWK_LABELS):
        ax.axvline(hs, color=COL_HAWK, linewidth=1.2, linestyle=":", alpha=0.8)
        ax.text(hs, y_pos, hl, ha="center", va="top", fontsize=7,
                color=COL_HAWK, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", alpha=0.7, ec="none"))


def save_fig(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Guardado: {path}")
    plt.close(fig)


def _pos_log_path(suffix=""):
    for s in [f"_v9{suffix}", f"_v8{suffix}"]:
        p = os.path.join(RESULTS_DIR, f"mobility_5hawks_real{s}_pos_log.csv")
        if os.path.exists(p):
            return p
    return os.path.join(RESULTS_DIR, f"mobility_5hawks_real_v9_pos_log.csv")


def _flow_stats_path(scenario):
    for s in ["_v9", "_v8"]:
        p = os.path.join(RESULTS_DIR, f"{scenario}{s}_flow_stats.csv")
        if os.path.exists(p):
            return p
    return os.path.join(RESULTS_DIR, f"{scenario}_v9_flow_stats.csv")


# ===========================================================================
# 1. RSSI estimado vs posicion
# ===========================================================================

def plot_rssi():
    path = _pos_log_path()
    if not os.path.exists(path):
        print(f"  [fig1] No encontrado: {path}")
        return
    df = pd.read_csv(path)
    if "time_s" not in df.columns:
        print("  [fig1] Columna time_s no encontrada")
        return
    fig, ax = plt.subplots(figsize=(12, 4))
    hawk_cols = [c for c in df.columns if c.startswith("rssi_")]
    colors = ["#1565C0","#0277BD","#00838F","#2E7D32","#558B2F","#FF8F00"]
    for col, color in zip(hawk_cols, colors):
        label = col.replace("rssi_", "").replace("_", " ")
        ax.plot(df["time_s"], df[col], label=label, linewidth=1.2,
                color=color, alpha=0.85)
    shade_nlos(ax)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("RSSI estimado (dBm)")
    ax.set_title("RSSI estimado vs Tiempo - Recorrido real LHD Nivel 1640 (v9)")
    ax.legend(fontsize=8, ncol=3, loc="lower right")
    mark_hawks(ax)
    fig.tight_layout()
    save_fig(fig, "fig1_rssi_vs_posicion.png")


# ===========================================================================
# 2. Nodo candidato por RSSI
# ===========================================================================

def plot_handover():
    path = _pos_log_path()
    if not os.path.exists(path):
        print(f"  [fig2] No encontrado: {path}")
        return
    df = pd.read_csv(path)
    if "time_s" not in df.columns:
        print("  [fig2] Columna time_s no encontrada")
        return
    hawk_cols = [c for c in df.columns if c.startswith("rssi_")]
    if "best_ap" not in df.columns and hawk_cols:
        df["best_ap"] = df[hawk_cols].idxmax(axis=1).str.replace("rssi_", "")
    ap_order = ["CardFijo", "H0", "H1", "H2", "H3", "H4"]
    ap_map   = {ap: i for i, ap in enumerate(ap_order)}
    colors   = ["#FF8F00","#1565C0","#0277BD","#00838F","#2E7D32","#558B2F"]
    fig, ax  = plt.subplots(figsize=(12, 4))
    for ap, color in zip(ap_order, colors):
        mask = df["best_ap"] == ap
        if mask.any():
            ax.scatter(df.loc[mask, "time_s"], [ap_map[ap]] * mask.sum(),
                       color=color, s=8, label=ap, alpha=0.8)
    ax.set_yticks(range(len(ap_order)))
    ax.set_yticklabels(ap_order)
    ax.set_xlabel("Tiempo de simulacion (s)")
    ax.set_ylabel("Nodo candidato (por RSSI estimado)")
    ax.set_title("Nodo candidato por RSSI durante el recorrido real - LHD Nivel 1640 (v9)")
    ax.legend(fontsize=8, ncol=3, loc="upper right")
    fig.tight_layout()
    save_fig(fig, "fig2_handover_hawks.png")


# ===========================================================================
# 3. Comparacion KPIs
# ===========================================================================

def plot_comparison_bars():
    scenarios = {
        "baseline":             "Baseline\n(estatico)",
        "mobility_5hawks_real": "5 Hawks\n(mobility)",
    }
    metrics = {
        "owd_mean_ms":  ("OWD cmd media (ms)",    20.0,  True),
        "video_e2e_ms": ("Video E2E media (ms)",  150.0,  True),
        "plr_cmd_pct":  ("PLR cmd (%)",             0.5,  True),
        "goodput_mbps": ("Goodput video (Mbps)",   38.0, False),
    }
    data = {}
    for sc in scenarios:
        p = _flow_stats_path(sc)
        if not os.path.exists(p):
            data[sc] = {}
            continue
        df = pd.read_csv(p)
        data[sc] = {col: df[col].mean() for col in metrics if col in df.columns}

    fig, axes = plt.subplots(1, 4, figsize=(14, 5))
    for ax, (col, (label, threshold, lower_better)) in zip(axes, metrics.items()):
        vals = [data[sc].get(col, np.nan) for sc in scenarios]
        labs = list(scenarios.values())
        clrs = []
        for v in vals:
            if np.isnan(v):
                clrs.append("#BDBDBD")
            elif (lower_better and v <= threshold) or (not lower_better and v >= threshold):
                clrs.append(COL_MOBILITY)
            else:
                clrs.append("#EF5350")
        bars = ax.bar(labs, vals, color=clrs, edgecolor="white")
        ax.axhline(threshold, color="#E53935", linestyle="--", linewidth=1.5,
                   label=f"Umbral={threshold}")
        ax.set_title(label, fontsize=9)
        ax.legend(fontsize=7)
        for bar, v in zip(bars, vals):
            if not np.isnan(v):
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() * 1.01, f"{v:.2f}",
                        ha="center", va="bottom", fontsize=8)
    fig.suptitle("Comparacion KPIs: Baseline vs mobility_5hawks_real - ns-3 v9",
                 fontsize=12)
    fig.tight_layout()
    save_fig(fig, "fig3_comparacion_kpis.png")


# ===========================================================================
# 4. RSSI y distancia al Hawk
# ===========================================================================

def plot_rssi_zoomed():
    path = _pos_log_path()
    if not os.path.exists(path):
        print(f"  [fig4] No encontrado: {path}")
        return
    df = pd.read_csv(path)
    if "time_s" not in df.columns:
        print("  [fig4] Columna time_s no encontrada")
        return
    fig, axes   = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    hawk_cols   = [c for c in df.columns if c.startswith("rssi_")]
    dist_cols   = [c for c in df.columns if c.startswith("dist_")]
    colors      = ["#1565C0","#0277BD","#00838F","#2E7D32","#558B2F","#FF8F00"]
    for col, color in zip(hawk_cols, colors):
        axes[0].plot(df["time_s"], df[col],
                     label=col.replace("rssi_","").replace("_"," "),
                     linewidth=1.2, color=color, alpha=0.85)
    axes[0].set_ylabel("RSSI estimado (dBm)")
    axes[0].legend(fontsize=8, ncol=3)
    shade_nlos(axes[0])
    for col, color in zip(dist_cols, colors):
        axes[1].plot(df["time_s"], df[col],
                     label=col.replace("dist_","").replace("_"," "),
                     linewidth=1.2, color=color, alpha=0.85)
    axes[1].set_ylabel("Distancia al AP (m)")
    axes[1].set_xlabel("Tiempo (s)")
    axes[1].legend(fontsize=8, ncol=3)
    shade_nlos(axes[1])
    fig.suptitle("RSSI y Distancia al AP vs Tiempo - Recorrido real LHD v9\n"
                 "(H4 en Desmonte, CardFijo en ramal BP)", fontsize=11)
    fig.tight_layout()
    save_fig(fig, "fig4_rssi_dist_hawk.png")


# ===========================================================================
# 5. Tabla resumen KPIs
# ===========================================================================

def plot_kpi_table():
    p = _flow_stats_path("mobility_5hawks_real")
    if not os.path.exists(p):
        print(f"  [fig5] No encontrado: {p}")
        return
    df   = pd.read_csv(p)
    rows = [
        ("OWD cmd media (ms)",   "owd_mean_ms",    20.0,  True),
        ("Video E2E media (ms)", "video_e2e_ms",  150.0,  True),
        ("Video jitter P95 (ms)","jitter_p95_ms",  10.0,  True),
        ("PLR comandos (%)",     "plr_cmd_pct",     0.5,  True),
        ("PLR video (%)",        "plr_video_pct",   1.0,  True),
        ("Goodput video (Mbps)", "goodput_mbps",   38.0, False),
    ]
    table_data, colors_row = [], []
    for label, col, thr, lower in rows:
        val = df[col].mean() if col in df.columns else float("nan")
        val_str = f"{val:.3f}" if not np.isnan(val) else "N/D"
        thr_str = f"<= {thr}" if lower else f">= {thr}"
        if np.isnan(val):
            ok, c = "N/D", ["#EEEEEE"]*4
        elif (lower and val <= thr) or (not lower and val >= thr):
            ok, c = "SI", ["#E8F5E9"]*3 + ["#C8E6C9"]
        else:
            ok, c = "NO", ["#FFEBEE"]*3 + ["#FFCDD2"]
        table_data.append([label, val_str, thr_str, ok])
        colors_row.append(c)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    tbl = ax.table(cellText=table_data,
                   colLabels=["Indicador", "Obtenido", "Umbral", "Cumple"],
                   cellColours=colors_row, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 2)
    ax.set_title("Resumen KPIs - mobility_5hawks_real (ns-3 v9)", fontsize=11, pad=12)
    fig.tight_layout()
    save_fig(fig, "fig5_tabla_kpis.png")


# ===========================================================================
# 6. Mapa 2D ruta LHD con angulos reales v9
# ===========================================================================

def plot_route_map():
    END_BP_X  = BOCA_BP_X  + LONG_BP  * math.cos(ANGLE_BP_RAD)
    END_BP_Y  = BOCA_BP_Y  + LONG_BP  * math.sin(ANGLE_BP_RAD)
    END_DES_X = BOCA_DES_X + LONG_DES * math.cos(ANGLE_DES_RAD)
    END_DES_Y = BOCA_DES_Y + LONG_DES * math.sin(ANGLE_DES_RAD)

    route_xy = [
        (0.0,        0.0),
        (48.9,       0.0),
        (BOCA_BP_X,  0.0),
        (CF_X,       CF_Y),
        (END_BP_X,   END_BP_Y),
        (CF_X,       CF_Y),
        (BOCA_BP_X,  0.0),
        (BOCA_DES_X, 0.0),
        (H4_X,       H4_Y),
        (END_DES_X,  END_DES_Y),
        (H4_X,       H4_Y),
        (BOCA_DES_X, 0.0),
    ]
    rx = [p[0] for p in route_xy]
    ry = [p[1] for p in route_xy]

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_facecolor("#F0F4F8")

    ax.plot([0, 318.5], [0, 0], color="#424242", linewidth=7,
            solid_capstyle="round", zorder=2, label="Galeria principal")
    ax.plot([BOCA_BP_X, END_BP_X], [BOCA_BP_Y, END_BP_Y],
            color="#1565C0", linewidth=5, solid_capstyle="round",
            zorder=2, label="Ramal BP (70 grados)")
    ax.plot([BOCA_DES_X, END_DES_X], [BOCA_DES_Y, END_DES_Y],
            color="#D32F2F", linewidth=5, solid_capstyle="round",
            zorder=2, label="Ramal Desmonte (65 grados)")

    ax.plot(rx, ry, color="#FF6F00", linewidth=2.5, linestyle="--",
            alpha=0.85, zorder=3, label="Ruta LHD")
    ax.plot(rx[0], ry[0], "o", color="#FF6F00", markersize=9, zorder=6)
    ax.text(rx[0]-2, ry[0]+3, "Inicio", fontsize=8,
            color="#FF6F00", fontweight="bold")

    for (hx, hy, hl), hc in zip(
            [(0.0,0.0,"H0"),(48.9,0.0,"H1"),(183.7,0.0,"H2"),(318.5,0.0,"H3")],
            ["#1565C0","#0277BD","#00838F","#2E7D32"]):
        ax.plot(hx, hy, "^", color=hc, markersize=13, zorder=5)
        ax.text(hx+2, hy-5, f"{hl}\n({hx:.0f},{hy:.0f})", fontsize=7.5,
                color=hc, fontweight="bold", ha="center")

    ax.plot(H4_X, H4_Y, "^", color="#558B2F", markersize=13, zorder=5)
    ax.text(H4_X+4, H4_Y+1, f"H4\n({H4_X:.0f},{H4_Y:.0f})", fontsize=7.5,
            color="#558B2F", fontweight="bold")

    ax.plot(CF_X, CF_Y, "D", color="#FF8F00", markersize=12, zorder=5)
    ax.text(CF_X+4, CF_Y+1, f"CardFijo\n({CF_X:.0f},{CF_Y:.0f})", fontsize=7.5,
            color="#FF6F00", fontweight="bold")

    ax.plot(END_BP_X, END_BP_Y, "s", color="#6A1B9A", markersize=9, zorder=6)
    ax.text(END_BP_X+3, END_BP_Y+1, "Breakpoint\n(fondo BP)",
            fontsize=7.5, color="#6A1B9A")
    ax.plot(END_DES_X, END_DES_Y, "s", color="#D32F2F", markersize=9, zorder=6)
    ax.text(END_DES_X+3, END_DES_Y+1, "Desmonte\n(fondo)",
            fontsize=7.5, color="#D32F2F")

    arc_r     = 18
    theta_bp  = [math.radians(a) for a in range(0, 71,  2)]
    theta_des = [math.radians(a) for a in range(0, 66,  2)]
    ax.plot([BOCA_BP_X  + arc_r*math.cos(t) for t in theta_bp],
            [BOCA_BP_Y  + arc_r*math.sin(t) for t in theta_bp],
            color="#1565C0", lw=1, alpha=0.7)
    ax.text(BOCA_BP_X+arc_r+2, BOCA_BP_Y+10, "70 deg",
            fontsize=8, color="#1565C0", fontstyle="italic")
    ax.plot([BOCA_DES_X + arc_r*math.cos(t) for t in theta_des],
            [BOCA_DES_Y + arc_r*math.sin(t) for t in theta_des],
            color="#D32F2F", lw=1, alpha=0.7)
    ax.text(BOCA_DES_X+arc_r+2, BOCA_DES_Y+8, "65 deg",
            fontsize=8, color="#D32F2F", fontstyle="italic")

    ax.annotate("", xy=(318.5, -12), xytext=(0, -12),
                arrowprops=dict(arrowstyle="<->", color="#616161", lw=1.5))
    ax.text(159, -16, "318.5 m (galeria principal)",
            ha="center", fontsize=8, color="#616161")

    ax.annotate("", xy=(END_BP_X, END_BP_Y), xytext=(BOCA_BP_X, BOCA_BP_Y),
                arrowprops=dict(arrowstyle="<->", color="#1565C0", lw=1.2))
    ax.text((BOCA_BP_X+END_BP_X)/2 - 9, (BOCA_BP_Y+END_BP_Y)/2,
            f"{LONG_BP:.0f} m", fontsize=8, color="#1565C0", ha="right")

    ax.annotate("", xy=(END_DES_X, END_DES_Y), xytext=(BOCA_DES_X, BOCA_DES_Y),
                arrowprops=dict(arrowstyle="<->", color="#D32F2F", lw=1.2))
    ax.text((BOCA_DES_X+END_DES_X)/2 - 9, (BOCA_DES_Y+END_DES_Y)/2,
            f"{LONG_DES:.0f} m", fontsize=8, color="#D32F2F", ha="right")

    ax.set_xlim(-25, 400)
    ax.set_ylim(-25, 75)
    ax.set_xlabel("Coordenada X (m) - galeria principal", fontsize=10)
    ax.set_ylabel("Coordenada Y (m) - ramales", fontsize=10)
    ax.set_title("Mapa 2D Nivel 1640 - Topologia y Ruta LHD (v9)\n"
                 "Ramal BP = 70 grados  |  Ramal Desmonte = 65 grados  |"
                 "  CardFijo y H4 en posiciones reales",
                 fontsize=11)
    ax.grid(alpha=0.3)
    ax.set_aspect("equal")

    legend_elements = [
        plt.Line2D([0],[0], color="#424242", lw=4,  label="Galeria principal"),
        plt.Line2D([0],[0], color="#1565C0", lw=4,  label="Ramal BP (70 grados)"),
        plt.Line2D([0],[0], color="#D32F2F", lw=4,  label="Ramal Desmonte (65 grados)"),
        plt.Line2D([0],[0], color="#FF6F00", lw=2,  linestyle="--", label="Ruta LHD"),
        plt.Line2D([0],[0], marker="^", color="w",  markerfacecolor=COL_HAWK,
                   markersize=10, label="Hawk (H0-H4)"),
        plt.Line2D([0],[0], marker="D", color="w",  markerfacecolor="#FF8F00",
                   markersize=10, label="Cardinal fijo (BP)"),
        plt.Line2D([0],[0], marker="s", color="w",  markerfacecolor="#6A1B9A",
                   markersize=9,  label="Breakpoint / Desmonte"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=8, ncol=2)
    fig.tight_layout()
    save_fig(fig, "fig6_mapa_ruta_lhd.png")


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    print("Generando graficas de tesis - LHD Teleop v9")
    print(f"  Directorio salida: {OUT_DIR}")

    plot_rssi()
    plot_handover()
    plot_comparison_bars()
    plot_rssi_zoomed()
    plot_kpi_table()
    plot_route_map()

    print("\nListo. Figuras generadas:")
    for i in range(1, 7):
        fname = {1:"fig1_rssi_vs_posicion.png", 2:"fig2_handover_hawks.png",
                 3:"fig3_comparacion_kpis.png", 4:"fig4_rssi_dist_hawk.png",
                 5:"fig5_tabla_kpis.png",       6:"fig6_mapa_ruta_lhd.png"}[i]
        print(f"  [{i}] {fname}")

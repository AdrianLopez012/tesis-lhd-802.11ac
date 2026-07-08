"""
Diagrama de arquitectura de la red 802.11ac — NV1640 (PNG para la tesis)
=======================================================================
Genera arquitectura_red.png: las tres capas de la arquitectura real
(centro de control, backbone de fibra en anillo, acceso inalámbrico mesh de 12 AP)
con el LHD móvil y la leyenda de flujos QoS. Estilo sobrio, coherente con las
demás figuras del capítulo.

Ejecutar:  python arquitectura_red.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = "DejaVu Sans"

fig, ax = plt.subplots(figsize=(11, 10)); ax.set_xlim(0, 100); ax.set_ylim(0, 100)
ax.axis("off"); fig.patch.set_facecolor("white")

def box(x, y, w, h, fc, ec, r=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.15,rounding_size={r}",
                                fc=fc, ec=ec, lw=1.3))
def txt(x, y, s, size=10, w="normal", c="#25303b", ha="center"):
    ax.text(x, y, s, fontsize=size, fontweight=w, color=c, ha=ha, va="center")
def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                 lw=1.6, color="#5B6470"))

# título
txt(50, 97, "Arquitectura de la red IEEE 802.11ac — teleoperación LHD, NV1640", 14, "bold", "#1f2933")
txt(50, 93.5, "Nexa Cerro Lindo · 5 GHz · 40 MHz · 2×2 MIMO · QoS 802.11e/WMM", 10, "normal", "#52606d")

# ===== Capa 1: Centro de control =====
txt(8, 89, "CENTRO DE CONTROL", 9.5, "bold", "#8895a3", ha="left")
box(6, 78, 88, 9, "#EEF3F8", "#C4D3E0")
box(9, 79.5, 25, 6, "#fff", "#9DB4C8"); txt(21.5, 83.3, "Estación de teleoperación", 9.5, "bold"); txt(21.5, 81, "vídeo · mando · telemetría", 8, "normal", "#52606d")
box(38, 79.5, 24, 6, "#fff", "#9DB4C8"); txt(50, 83.3, "Controlador de red", 9.5, "bold"); txt(50, 81, "gestión mesh · QoS", 8, "normal", "#52606d")
box(66, 79.5, 25, 6, "#fff", "#9DB4C8"); txt(78.5, 83.3, "Gateway InstaMesh", 9.5, "bold"); txt(78.5, 81, "Rajant SLP-1025", 8, "normal", "#52606d")
arrow(50, 78, 50, 74)

# ===== Capa 2: Backbone fibra =====
txt(8, 72, "BACKBONE — FIBRA ÓPTICA EN ANILLO (1 GbE)", 9.5, "bold", "#8895a3", ha="left")
box(6, 61, 88, 9, "#E8F0EA", "#B9CDBE")
box(10, 62.5, 28, 6, "#fff", "#8FB39A"); txt(24, 66.3, "Switch core", 9.5, "bold"); txt(24, 64, "Fortinet FSR-424F-POE", 8, "normal", "#52606d")
box(56, 62.5, 28, 6, "#fff", "#8FB39A"); txt(70, 66.3, "Switch de acceso", 9.5, "bold"); txt(70, 64, "Fortinet FSR-112F-POE", 8, "normal", "#52606d")
ax.plot([38, 56], [65.5, 65.5], color="#5B8A6A", lw=2.2)
ax.plot([38, 56], [64.2, 64.2], color="#5B8A6A", lw=2.0, ls=(0, (4, 3)))
txt(47, 67.2, "SMF 1310 nm · anillo", 8, "bold", "#3E5C49")
arrow(47, 61, 47, 57)

# ===== Capa 3: Acceso mesh =====
txt(8, 55, "ACCESO INALÁMBRICO — MALLA InstaMesh (12 AP)", 9.5, "bold", "#8895a3", ha="left")
box(6, 30, 88, 23, "#F4F1EA", "#D8D0BE")
# Hawk
txt(9, 50, "5 AP Hawk", 10, "bold", ha="left"); txt(9, 48, "galerías · 30 dBm / 11 dBi", 8, "normal", "#52606d", ha="left")
for i in range(5):
    x = 29 + i * 12
    box(x, 47, 10, 4.5, "#DCE7F2", "#7FA0C0"); txt(x + 5, 49.2, f"H{i+1}", 9.5, "bold")
# Cardinal
txt(9, 42, "7 AP Cardinal", 10, "bold", ha="left"); txt(9, 40, "cruceros · 23 dBm / 7.5 dBi", 8, "normal", "#52606d", ha="left")
for i in range(7):
    x = 28 + i * 9
    box(x, 38, 7.5, 4.5, "#E7DEF0", "#A98FC0"); txt(x + 3.75, 40.2, f"C{i+1}", 9, "bold")
txt(50, 35, "enlaces mesh L2 entre AP (make-before-break, sin root)", 8, "bold", "#3E5C49")
ax.plot([29, 91], [33.5, 33.5], color="#B0A98F", lw=1, ls=(0, (3, 3)))
arrow(50, 30, 50, 26); txt(53.5, 28, "roaming", 8, "normal", "#52606d", ha="left")

# ===== LHD =====
box(24, 18, 52, 7, "#FDF0E4", "#E0B98C")
txt(50, 22.8, "LHD teleoperado (móvil)", 10, "bold")
txt(50, 20.3, "radio Cardinal 23 dBm + antena HELI-40 (4.8 dBi) · 2×2 MIMO", 8, "normal", "#52606d")

# ===== Leyenda QoS =====
box(6, 8, 88, 6, "#F7F6F2", "#DDD8CC")
ax.add_patch(Circle((10, 11), 0.9, color="#C77D4A")); txt(12, 11, "Vídeo (AC_VI, 40 Mbps)", 8.5, "normal", "#52606d", ha="left")
ax.add_patch(Circle((38, 11), 0.9, color="#3E7D5A")); txt(40, 11, "Comandos (AC_VO, ≤0.5 Mbps)", 8.5, "normal", "#52606d", ha="left")
ax.add_patch(Circle((70, 11), 0.9, color="#7FA0C0")); txt(72, 11, "Telemetría (AC_BE, 0.1 Mbps)", 8.5, "normal", "#52606d", ha="left")

out = os.path.join(HERE, "arquitectura_red.png")
plt.savefig(out, dpi=155, bbox_inches="tight", facecolor="white"); plt.close()
print(f"[OK] {out}")

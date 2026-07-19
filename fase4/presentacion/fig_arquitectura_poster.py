# -*- coding: utf-8 -*-
"""
Architecture figure for the XpoSTEM poster (English, Visio-style, deep detail).
Conventions from the thesis: fiber optic = yellow, Cat6 = blue, radio = green
dashed, mesh = gray dashed. Real equipment models and RF parameters.
Output: arquitectura_poster_en.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Circle, RegularPolygon, Rectangle
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = "Calibri"

INK   = "#1A2733"; GRIS = "#5B6670"; AZULT = "#215E99"     # títulos (azul plantilla)
FO    = "#E0A800"                                           # fibra óptica (amarillo tesis)
CAT6  = "#2563EB"                                           # Cat6 (azul tesis)
RADIO = "#2E8B57"                                           # enlace 802.11ac
MESH  = "#8895A3"                                           # mesh
HAWK  = "#1565C0"; CARD = "#7B1FA2"; LHDC = "#C77D4A"

fig, ax = plt.subplots(figsize=(7.6, 8.4), dpi=300)
ax.set_xlim(0, 100); ax.set_ylim(0, 116); ax.axis("off")
fig.patch.set_facecolor("white")

def box(x, y, w, h, fc, ec, lw=1.1, r=1.6, z=3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.25,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z))
def txt(x, y, s, size=8.6, w="normal", c=INK, ha="center", style="normal", z=6):
    ax.text(x, y, s, fontsize=size, fontweight=w, color=c, ha=ha, va="center",
            style=style, zorder=z)
def band(y, label):
    ax.text(1.5, y, label, fontsize=7.2, fontweight="bold", color=GRIS,
            ha="left", va="center", rotation=0, zorder=6)

# ============ LAYER 1 — SURFACE CONTROL ROOM ============
band(113.4, "SURFACE — CONTROL ROOM")
box(6, 103, 42, 8.4, "#EEF3F8", "#9DB4C8")
txt(27, 108.8, "Teleoperation station", 9.2, "bold")
txt(27, 105.6, "video wall · driving controls · HMI", 7.6, c=GRIS)
box(52, 103, 42, 8.4, "#EEF3F8", "#9DB4C8")
txt(73, 108.8, "Network management", 9.2, "bold")
txt(73, 105.6, "QoS policies · security · monitoring", 7.6, c=GRIS)

# ============ LAYER 2 — CORE NODE ============
band(99.4, "CORE NODE")
box(20, 89.5, 60, 7.8, "#FFF8E6", FO)
txt(50, 94.6, "Core switch  Fortinet FSR-424F-POE", 9.2, "bold")
txt(50, 91.6, "InstaMesh gateway  Rajant SLP-1025", 8.2, c=GRIS)
# control room -> core (Cat6 azul)
for xx in (27, 73):
    ax.add_patch(FancyArrowPatch((xx, 103), (xx if abs(xx-50)<25 else (38 if xx<50 else 62), 97.6),
                 arrowstyle="-", lw=2.0, color=CAT6, zorder=2))

# ============ LAYER 3 — FIBER OPTIC RING ============
band(84.6, "BACKBONE")
ring = Ellipse((50, 73.5), 78, 17, fill=False, ec=FO, lw=3.2, zorder=2)
ax.add_patch(ring)
txt(50, 73.5, "Single-mode fiber-optic ring · 1 GbE\n(redundant path)", 8.6, "bold", c="#8A6A00")
# core -> anillo (FO amarillo doble)
ax.add_patch(FancyArrowPatch((46, 89.5), (46, 82.2), arrowstyle="-", lw=3.0, color=FO, zorder=2))
ax.add_patch(FancyArrowPatch((54, 89.5), (54, 82.2), arrowstyle="-", lw=3.0, color=FO, zorder=2))
# switches de acceso sobre el anillo
for sx, lbl in [(13.5, "Access switch\nFSR-112F-POE"), (86.5, "Access switch\nFSR-112F-POE")]:
    box(sx-9.5, 70.2, 19, 6.6, "white", FO, lw=1.4, z=4)
    txt(sx, 73.5, lbl, 7.4, "bold", z=6)

# ============ LAYER 4 — 802.11ac ACCESS MESH ============
band(63.2, "NV1640 ACCESS MESH")
box(4, 27.5, 92, 33.5, "#F7F6F2", "#D8D0BE", lw=1.2, z=1)
txt(50, 58.4, "IEEE 802.11ac (Wi-Fi 5) · 5 GHz · 40 MHz · 2×2 MIMO · WMM (802.11e)", 8.4, "bold", c=AZULT)

# Hawk row (galerías)
hawk_y = 50.5
txt(52, 54.6, "5 × Hawk AP — production galleries · 30 dBm · 11 dBi (RCP-50 L/R)", 7.8, "bold", c=HAWK)
hx = [14, 30, 46, 62, 78]
for x in hx:
    ax.add_patch(RegularPolygon((x, hawk_y), 3, radius=2.6, fc=HAWK, ec="white", lw=0.8, zorder=5))
    txt(x, hawk_y-4.3, f"H{hx.index(x)+1}", 7.0, c=HAWK)
# Cardinal row (cruceros)
card_y = 38.5
txt(52, 44.2, "7 × Cardinal AP — crosscuts · 23 dBm · 7.5 dBi (EPNT-7 omni)", 7.8, "bold", c=CARD)
cx = [10, 22.7, 35.4, 48.1, 60.8, 73.5, 86.2]
for i, x in enumerate(cx):
    ax.add_patch(Rectangle((x-2.1, card_y-2.1), 4.2, 4.2, fc=CARD, ec="white", lw=0.8, zorder=5))
    txt(x, card_y-4.6, f"C{i+1}", 7.0, c=CARD)
# mesh links (gris punteado) entre vecinos de cada fila y entre filas
for i in range(len(hx)-1):
    ax.plot([hx[i]+2.6, hx[i+1]-2.6], [hawk_y, hawk_y], ls=(0,(3,2)), lw=1.1, color=MESH, zorder=4)
for i in range(len(cx)-1):
    ax.plot([cx[i]+2.1, cx[i+1]-2.1], [card_y, card_y], ls=(0,(3,2)), lw=1.1, color=MESH, zorder=4)
for xh, xc in [(14,10),(30,22.7),(46,48.1),(62,60.8),(78,86.2)]:
    ax.plot([xh, xc], [hawk_y-2.6, card_y+2.1], ls=(0,(3,2)), lw=1.0, color=MESH, zorder=2, alpha=0.55)
txt(27, 31.3, "InstaMesh layer-2 roaming\nmake-before-break (no root node)", 7.6, style="italic", c=GRIS)

# Cat6 desde switches de acceso a APs cabecera (azul)
ax.add_patch(FancyArrowPatch((13.5, 70.2), (14, 53.3), arrowstyle="-", lw=2.0, color=CAT6, zorder=2))
ax.add_patch(FancyArrowPatch((86.5, 70.2), (78, 53.3), arrowstyle="-", lw=2.0, color=CAT6, zorder=2))

# ============ LAYER 5 — LHD ============
band(22.6, "MOBILE NODE")
box(24, 12.0, 52, 7.6, "#FDF0E4", LHDC)
txt(50, 17.0, "Teleoperated LHD vehicle", 9.2, "bold")
txt(50, 14.0, "on-board radio 23 dBm + HELI-40 antenna (4.8 dBic)", 7.8, c=GRIS)
# enlace radio (verde punteado) AP -> LHD (desde C5 y C6, sin cruzar textos)
ax.add_patch(FancyArrowPatch((62.3, card_y-2.3), (58, 19.9), arrowstyle="-",
             lw=1.8, color=RADIO, linestyle=(0,(4,2)), zorder=2))
ax.add_patch(FancyArrowPatch((75.0, card_y-2.3), (66, 19.9), arrowstyle="-",
             lw=1.8, color=RADIO, linestyle=(0,(4,2)), zorder=2))
txt(81.5, 25.0, "802.11ac link\n(seamless roaming)", 7.0, c=RADIO)

# ============ QoS flows (bajo el LHD) ============
txt(50, 9.4, "Video  AC_VI  40 Mbps ↑      ·      Commands  AC_VO  ≤ 0.5 Mbps ↓      ·      Telemetry  AC_BE  0.1 Mbps ↑",
    7.9, "bold", c=INK)

# ============ Leyenda ============
leg = [Line2D([0],[0], color=FO,   lw=3.0, label="Fiber optic (ring)"),
       Line2D([0],[0], color=CAT6, lw=2.0, label="Cat6"),
       Line2D([0],[0], color=RADIO, lw=1.8, ls=(0,(4,2)), label="802.11ac radio"),
       Line2D([0],[0], color=MESH, lw=1.2, ls=(0,(3,2)), label="InstaMesh link")]
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, -0.006), ncol=4,
          fontsize=7.4, frameon=False, handlelength=2.2, columnspacing=1.4)

out = os.path.join(HERE, "arquitectura_poster_en.png")
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
from PIL import Image
im = Image.open(out)
print(f"[OK] {out}  {im.width}x{im.height} (ratio {im.width/im.height:.3f})")

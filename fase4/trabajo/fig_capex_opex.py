# -*- coding: utf-8 -*-
# Figura estructural CAPEX/OPEX + mecanismos de retorno (sin montos: la
# cuantificación queda remitida a cotizaciones, como declara el 4.3).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BG = "#FFFFFF"; INK = "#2B2B28"
fig, ax = plt.subplots(figsize=(13, 7.2)); fig.patch.set_facecolor(BG)
ax.set_xlim(0, 13); ax.set_ylim(0, 7.2); ax.axis("off")

def caja(x, y, w, h, titulo, items, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                facecolor=fc, edgecolor=ec, linewidth=1.6))
    ax.text(x + w/2, y + h - 0.34, titulo, ha="center", fontsize=12.5,
            fontweight="bold", color=INK)
    for i, it in enumerate(items):
        ax.text(x + 0.25, y + h - 0.85 - i*0.46, "• " + it, fontsize=10.5, color="#333")

caja(0.3, 3.1, 4.1, 3.6, "CAPEX (inversión)",
     ["5 nodos Hawk + 7 nodos Cardinal",
      "Radio embarcado + antena HELI-40",
      "Switches, gateway del mesh, PoE",
      "Montaje y comisionamiento",
      "Estación de teleoperación"],
     "#EAF0F8", "#2E6FB0")

caja(0.3, 0.3, 4.1, 2.3, "OPEX (operación)",
     ["Mantenimiento preventivo y repuestos",
      "Monitoreo de KPIs y firmware",
      "Capacitación y soporte OT/TI"],
     "#F5EFE5", "#B9770E")

caja(8.6, 3.1, 4.1, 3.6, "Retorno (beneficios)",
     ["Menos exposición del personal",
      "Continuidad tras voladuras /",
      "  condiciones inseguras",
      "Más horas productivas por turno",
      "Reutiliza el backbone existente"],
     "#E7F2EA", "#3E7D5A")

caja(8.6, 0.3, 4.1, 2.3, "Cuantificación (siguiente paso)",
     ["Cotizaciones vigentes de fabricantes",
      "Datos operativos de la mina",
      "Costo-beneficio con planeamiento"],
     "#F0EAF5", "#7B1FA2")

# flechas centrales
ax.add_patch(FancyArrowPatch((4.6, 4.9), (8.4, 4.9), arrowstyle="-|>",
             mutation_scale=26, linewidth=2.2, color="#3E7D5A"))
ax.text(6.5, 5.15, "inversión incremental\nsobre infraestructura existente",
        ha="center", fontsize=10.5, color="#3E7D5A", fontweight="bold")
ax.add_patch(FancyArrowPatch((4.6, 1.4), (8.4, 1.4), arrowstyle="-|>",
             mutation_scale=26, linewidth=2.2, color="#7B1FA2"))
ax.text(6.5, 1.65, "despliegue gradual:\npiloto → expansión por frentes",
        ha="center", fontsize=10.5, color="#7B1FA2", fontweight="bold")

ax.set_title("Estructura económica de la solución: inversión, operación y mecanismos de retorno",
             fontsize=14, fontweight="bold", pad=14)
plt.savefig(r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\fig_capex_opex.png",
            dpi=180, bbox_inches="tight", facecolor=BG)
print("PNG OK")

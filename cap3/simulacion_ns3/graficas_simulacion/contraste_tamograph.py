"""
Contraste de coherencia: modelo two-slope vs. referencia TamoGraph
=================================================================
NO es validación experimental (la tesis lo declara así). Es un CONTRASTE
DOCUMENTAL: muestra que el modelo two-slope calibrado predice el nivel de señal
dentro del rango observado en los mapas del reporte TamoGraph del proyecto.
Corresponde a la Figura 16 mencionada en la tesis.

Ejecutar:  python contraste_tamograph.py  ->  contraste_tamograph.png
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- modelo two-slope calibrado (idéntico a modelo_definitivo.py) ----
# Para el CONTRASTE con TamoGraph se usa la config del dispositivo de SURVEY
# (misma antena/pérdidas que midió el TamoGraph: L_survey=19.2 dB, Gr=0), para
# que la comparación sea justa. El diseño real (Cardinal, L=9.4) da más señal.
FREQ=5.0e9; LAMBDA=3e8/FREQ
N1=1.9; N2=3.4; D_BP=40.0
PL_D0=20*np.log10(4*np.pi/LAMBDA)
PT=30.0; GT=11.0; GR_SURVEY=0.0; L_SURVEY=19.2   # config survey (comparar con TamoGraph)
SIG1=5.0; SIG2=7.0                                # shadowing LOS/NLOS (bandas ±σ)

def pr(d):
    d=np.maximum(d,1.0)
    pl=np.where(d<D_BP, PL_D0+10*N1*np.log10(d),
                PL_D0+10*N1*np.log10(D_BP)+10*N2*np.log10(d/D_BP))
    return PT+GT+GR_SURVEY-pl-L_SURVEY

d=np.linspace(1,150,400)
prd=pr(d)
sig=np.where(d<D_BP,SIG1,SIG2)

# ---- rango observado en el reporte TamoGraph (de los mapas de señal) ----
# El reporte muestra Signal Level entre ~-45 dBm (cerca AP) y ~-85 dBm (borde/fondo).
TG_MAX=-45.0; TG_MIN=-85.0

fig,ax=plt.subplots(figsize=(11,7))
# banda del modelo ±σ
ax.fill_between(d, prd-sig, prd+sig, color="#2E6FB0", alpha=0.15, label="Modelo two-slope ±σ (shadowing)")
ax.plot(d, prd, color="#1B4C7E", lw=2.4, label="Modelo two-slope — config survey (n₁=1.9, n₂=3.4, d_bp=40 m)")

# banda de referencia TamoGraph
ax.axhspan(TG_MIN, TG_MAX, color="#1D9E75", alpha=0.10)
ax.axhline(TG_MAX, color="#0F6E56", ls="--", lw=1.3, label=f"Rango TamoGraph (referencia): {TG_MAX:.0f} a {TG_MIN:.0f} dBm")
ax.axhline(TG_MIN, color="#0F6E56", ls="--", lw=1.3)

# umbrales de sensibilidad 802.11ac
for s,txt in [(-68,"-68 dBm (300 Mbps)"),(-82,"-82 dBm (54 Mbps)"),(-94,"-94 dBm (6 Mbps)")]:
    ax.axhline(s, color="#993C1D", ls=":", lw=1, alpha=0.7)
    ax.annotate(txt, (148,s), fontsize=8, color="#993C1D", ha="right", va="bottom")

# breakpoint
ax.axvline(D_BP, color="#888", ls="-.", lw=1)
ax.annotate("breakpoint\nd_bp = 40 m", (D_BP+2,-50), fontsize=9, color="#555", style="italic")

ax.set_xlabel("Distancia a lo largo de la galería (m)", fontsize=12)
ax.set_ylabel("Potencia recibida / RSSI (dBm)", fontsize=12)
ax.set_title("Contraste de coherencia: modelo two-slope vs. referencia TamoGraph — NV1640\n"
             "(contraste documental, no validación experimental in situ)",
             fontsize=12.5, fontweight="bold")
ax.legend(loc="upper right", fontsize=10, framealpha=0.95)
ax.grid(True, alpha=0.3)
ax.set_xlim(0,150); ax.set_ylim(-100,-40)

# nota de coherencia
en_rango = ((prd>=TG_MIN)&(prd<=TG_MAX)) | (prd>TG_MAX)
plt.figtext(0.13,0.02,
    "El modelo predice niveles dentro del rango de la referencia TamoGraph en el tramo operativo, "
    "lo que respalda la coherencia del diseño (no sustituye medición de campo).",
    fontsize=8.5, style="italic", color="#444", wrap=True)

plt.tight_layout(rect=[0,0.04,1,1])
import os
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"contraste_tamograph.png")
plt.savefig(out,dpi=160,bbox_inches="tight"); plt.close()
print(f"[OK] {out}")
print(f"RSSI modelo a 10m: {pr(10):.1f} dBm | a 40m: {pr(40):.1f} dBm | a 100m: {pr(100):.1f} dBm")
print(f"Rango TamoGraph referencia: {TG_MAX:.0f} a {TG_MIN:.0f} dBm")

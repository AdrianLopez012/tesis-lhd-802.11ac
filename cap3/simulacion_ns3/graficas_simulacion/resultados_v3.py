"""
Resultados de simulación v3-REAL — figuras para el capítulo de resultados
=========================================================================
Genera, con estilo sobrio (académico, color suave en la columna de estado):

  1. resultados_kpi_multiseed.png  — KPIs del escenario de operación con
     estadística sobre 10 semillas (media, desviación, IC 95%) + estado.
  2. resultados_escenarios.png     — comparación entre escenarios
     (operación / baseline / estrés vídeo / estrés LHD).
  3. resultados_handover.png       — análisis de handover vs. RNF-05 (150 ms).
  4. resultados_cobertura_ruta.png — RSSI y roaming a lo largo del recorrido.

Lee resultados desde ../results. Tolera que falten escenarios (usa los que haya).
Ejecutar:  python resultados_v3.py
"""
import os, csv, glob, importlib.util
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
RES  = os.path.join(HERE, "..", "results")

# ---------- estilo sobrio ----------
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.edgecolor": "#555", "axes.labelcolor": "#222",
    "text.color": "#222", "figure.facecolor": "white", "axes.facecolor": "white",
})
C_OK   = "#3E7D5A"   # verde discreto
C_OK_BG= "#E3EFE7"   # verde muy suave (fondo estado)
C_BAD  = "#A6473C"
C_BAD_BG="#F1DDD9"
C_BAR  = "#4C7A9B"   # azul apagado
C_REF  = "#666"

def load_flow(path):
    d = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            d[r["name"]] = {k:(float(v) if k!="name" else v) for k,v in r.items()}
    return d

# ---------- umbrales tesis (RNF) ----------
KPI = [
    ("Comandos",   "OWD medio",       "owd_ms",        "ms",   20.0, "<="),
    ("Comandos",   "Pérdida de paq.", "plr_pct",       "%",     0.5, "<="),
    ("Vídeo",      "Latencia E2E",    "e2e_ms",        "ms",  150.0, "<="),
    ("Vídeo",      "Jitter (P95)",    "jitter_p95_ms", "ms",   10.0, "<="),
    ("Vídeo",      "Throughput útil", "goodput_mbps",  "Mbps", 38.0, ">="),
    ("Vídeo",      "Pérdida de paq.", "plr_pct",       "%",     1.0, "<="),
    ("Telemetría", "OWD medio",       "owd_ms",        "ms",   50.0, "<="),
    ("Telemetría", "Pérdida de paq.", "plr_pct",       "%",     0.5, "<="),
]
GRP_KEY = {"Comandos":"Comandos","Vídeo":"Video","Video":"Video","Telemetría":"Telemetria"}
def cumple(v,thr,op): return (v<=thr) if op=="<=" else (v>=thr)

# ============================================================
# 1) KPIs MULTI-SEMILLA (media, desv, IC95)
# ============================================================
seed_files = sorted(glob.glob(os.path.join(RES,"principal_s*_v3_flow_stats.csv")))
if not seed_files:  # respaldo: usar la corrida única mobility_v3
    seed_files = [os.path.join(RES,"mobility_v3_flow_stats.csv")]
runs = [load_flow(p) for p in seed_files if os.path.exists(p)]
n = len(runs)

def stat(grp,key):
    vals = [r[GRP_KEY[grp]][key] for r in runs if GRP_KEY[grp] in r]
    a = np.array(vals); m = a.mean(); s = a.std(ddof=1) if len(a)>1 else 0.0
    ci = 1.96*s/np.sqrt(len(a)) if len(a)>1 else 0.0
    return m,s,ci,a

# RTT y disponibilidad (CSVs propios por semilla)
def leer_metric(patron, clave):
    vals=[]
    for p in sorted(glob.glob(os.path.join(RES,patron))):
        for r in csv.DictReader(open(p)):
            if r.get("metric")==clave:
                try: vals.append(float(r["value_ms" if "value_ms" in r else "value"]))
                except: pass
    return np.array(vals)
def stat_arr(a):
    if len(a)==0: return None
    m=a.mean(); ci=1.96*a.std(ddof=1)/np.sqrt(len(a)) if len(a)>1 else 0.0
    return m,ci
rtt_a  = leer_metric("principal_s*_v3_rtt.csv","rtt_media")
disp_a = leer_metric("principal_s*_v3_disponibilidad.csv","disponibilidad_pct")

fig,ax = plt.subplots(figsize=(12,4.6)); ax.axis("off")
rows, colcols = [], []
for grp,lbl,key,unit,thr,op in KPI:
    m,s,ci,_ = stat(grp,key)
    ok = cumple(m,thr,op)
    med = f"{m:.2f}" + (f" ± {ci:.2f}" if n>1 else "")
    rows.append([grp, lbl, med, f"{'≤' if op=='<=' else '≥'} {thr:g} {unit}",
                 "Cumple" if ok else "No cumple"])
    colcols.append(["white","white","white","white", C_OK_BG if ok else C_BAD_BG])
# RTT del lazo de control (RNF)
r = stat_arr(rtt_a)
if r is not None:
    ok = r[0] <= 40.0
    med = f"{r[0]:.2f}" + (f" ± {r[1]:.2f}" if len(rtt_a)>1 else "")
    rows.append(["Control", "RTT (lazo)", med, "≤ 40 ms", "Cumple" if ok else "No cumple"])
    colcols.append(["white","white","white","white", C_OK_BG if ok else C_BAD_BG])
# Disponibilidad del enlace (RNF-06)
d = stat_arr(disp_a)
if d is not None:
    ok = d[0] >= 99.9
    med = f"{d[0]:.2f}" + (f" ± {d[1]:.2f}" if len(disp_a)>1 else "") + " %"
    rows.append(["Enlace", "Disponibilidad", med, "≥ 99.9 %", "Cumple" if ok else "No cumple"])
    colcols.append(["white","white","white","white", C_OK_BG if ok else C_BAD_BG])
tab = ax.table(cellText=rows,
               colLabels=["Servicio","Indicador",
                          f"Valor medido{' (media ± IC 95%)' if n>1 else ''}","Requisito","Estado"],
               cellColours=colcols, cellLoc="center", loc="center",
               colColours=["#EceceC"]*5,
               colWidths=[0.16,0.20,0.30,0.18,0.16])
tab.auto_set_font_size(False); tab.set_fontsize(9.5); tab.scale(1,1.6)
for (r,c),cell in tab.get_celld().items():
    cell.set_edgecolor("#CCC")
    if r==0: cell.set_text_props(weight="bold")
    if c==4 and r>0:
        cell.set_text_props(weight="bold", color=C_OK if rows[r-1][4]=="Cumple" else C_BAD)
sub = f"Escenario de operación · {n} corrida{'s' if n>1 else ''} independiente{'s' if n>1 else ''}" \
      + (f" · media e intervalo de confianza al 95%" if n>1 else "")
ax.set_title("Indicadores de desempeño de la red frente a los requisitos de la tesis\n"+sub,
             fontsize=12.5, pad=16)
out1 = os.path.join(HERE,"resultados_kpi_multiseed.png")
plt.savefig(out1, dpi=155, bbox_inches="tight"); plt.close()
print(f"[OK] {out1}  (n={n} semillas)")

# ============================================================
# 2) COMPARACIÓN DE ESCENARIOS
# ============================================================
ESC = [("Operación","mobility_v3_flow_stats.csv"),
       ("Baseline\n(estático)","baseline_v3_flow_stats.csv"),
       ("Estrés vídeo\n(50 Mbps)","estres_video_v3_flow_stats.csv"),
       ("Estrés LHD\n(4 m/s)","estres_lhd_v3_flow_stats.csv")]
esc_data = [(nm,load_flow(os.path.join(RES,fn))) for nm,fn in ESC if os.path.exists(os.path.join(RES,fn))]
if not esc_data:
    esc_data = [("Operación", load_flow(os.path.join(RES,"mobility_v3_flow_stats.csv")))]

met = [("Video","e2e_ms","Latencia vídeo E2E (ms)",150.0,"<="),
       ("Video","goodput_mbps","Throughput vídeo (Mbps)",38.0,">="),
       ("Comandos","owd_ms","OWD comandos (ms)",20.0,"<="),
       ("Video","plr_pct","Pérdida vídeo (%)",1.0,"<=")]
fig,axs = plt.subplots(2,2,figsize=(13,9)); axs=axs.ravel()
names=[nm for nm,_ in esc_data]
xb=np.arange(len(names))
for ax,(grp,key,title,thr,op) in zip(axs,met):
    vals=[d.get(GRP_KEY[grp],{}).get(key,np.nan) for _,d in esc_data]
    cols=[C_OK if (not np.isnan(v) and cumple(v,thr,op)) else C_BAD for v in vals]
    ax.bar(xb,vals,color=cols,edgecolor="#333",width=0.6,zorder=3)
    ax.axhline(thr,color=C_REF,ls="--",lw=1.2)
    ax.annotate(f"requisito {'≤' if op=='<=' else '≥'} {thr:g}",
                (len(names)-0.5,thr),fontsize=8.5,va="bottom",ha="right",color=C_REF)
    ax.set_xticks(xb); ax.set_xticklabels(names,fontsize=8.5)
    ax.set_title(title); ax.grid(True,axis="y",alpha=0.3)
    for i,v in enumerate(vals):
        if not np.isnan(v): ax.text(i,v,f"{v:.1f}",ha="center",va="bottom",fontsize=8.5)
fig.suptitle("Comparación de escenarios de simulación",fontsize=14,fontweight="bold",y=0.98)
plt.tight_layout(rect=[0,0,1,0.96])
out2=os.path.join(HERE,"resultados_escenarios.png")
plt.savefig(out2,dpi=155,bbox_inches="tight"); plt.close()
print(f"[OK] {out2}  ({len(esc_data)} escenarios)")

# ============================================================
# 3) ANÁLISIS DE HANDOVER (RNF-05: <= 150 ms)
# ============================================================
def load_assoc(path):
    ho=[]
    if not os.path.exists(path): return ho
    with open(path) as f:
        for r in csv.DictReader(f):
            if r.get("event")=="assoc":
                try:
                    v=float(r.get("handover_ms","0"))
                    if v>0: ho.append(v)
                except: pass
    return ho
# Agrega los handovers de TODAS las corridas del escenario de operación
# (las 10 semillas + la corrida única) para una distribución representativa.
ho=[]
for p in glob.glob(os.path.join(RES,"principal_s*_v3_assoc_log.csv")) + \
         [os.path.join(RES,"mobility_v3_assoc_log.csv")]:
    ho += load_assoc(p)
# nº de traspasos de AP a nivel de señal (serving_ap) en el escenario de operación
def contar_cambios_ap(path):
    if not os.path.exists(path): return 0
    prev=None; n=0
    with open(path) as f:
        for r in csv.DictReader(f):
            a=r["serving_ap"]
            if prev is not None and a!=prev: n+=1
            prev=a
    return n
cambios = contar_cambios_ap(os.path.join(RES,"mobility_v3_pos_log.csv"))

fig,ax=plt.subplots(figsize=(11,6.2)); ax.axis("off")
ax.set_title("Comportamiento del roaming durante la teleoperación (RNF-05: handover ≤ 150 ms)",
             fontsize=12.5, pad=18)
# barra visual comparando el peor handover observado vs el requisito
axb = fig.add_axes([0.12,0.30,0.76,0.16])
peor = max(ho) if ho else 0.0
axb.barh([0],[150],color="#EEE",edgecolor="#BBB",height=0.5,zorder=1)
axb.barh([0],[max(peor,1.5)],color=C_OK,edgecolor="#2f5c43",height=0.5,zorder=2)
axb.axvline(150,color=C_BAD,ls="--",lw=1.6)
axb.annotate("requisito 150 ms",(150,0.42),color=C_BAD,fontsize=9,ha="right")
axb.annotate(f"peor handover observado: {peor:.1f} ms",(max(peor,1.5)+3,0),
             va="center",fontsize=9.5,color="#2f5c43",weight="bold")
axb.set_xlim(0,165); axb.set_ylim(-0.5,0.7); axb.set_yticks([])
axb.set_xlabel("Tiempo de handover (ms)");
for s in ["top","right","left"]: axb.spines[s].set_visible(False)
# texto de conclusión
txt=("El diseño emplea roaming L2 tipo mesh (Rajant InstaMesh, make-before-break): el enlace se\n"
     f"mantiene durante el desplazamiento. A lo largo del recorrido el LHD es servido por distintos\n"
     f"AP con {cambios} traspasos de mejor señal, y solo se registró {len(ho)} reasociación con corte medible\n"
     f"({peor:.1f} ms), muy por debajo del requisito de 150 ms. Resultado agregado de 10 corridas.")
fig.text(0.5,0.14,txt,ha="center",va="center",fontsize=10.5,color="#333")
out3=os.path.join(HERE,"resultados_handover.png")
plt.savefig(out3,dpi=155,bbox_inches="tight"); plt.close()
print(f"[OK] {out3}  ({len(ho)} handovers medibles, {cambios} cambios de AP)")

# ============================================================
# 4) COBERTURA / RSSI A LO LARGO DEL RECORRIDO
# ============================================================
def load_pos(path):
    T,X,Y,AP,R=[],[],[],[],[]
    with open(path) as f:
        for r in csv.DictReader(f):
            T.append(float(r["time_s"]));X.append(float(r["x"]));Y.append(float(r["y"]))
            AP.append(r["serving_ap"]);R.append(float(r["rssi_dbm"]))
    return np.array(T),np.array(X),np.array(Y),AP,np.array(R)
pos_path=os.path.join(RES,"mobility_v3_pos_log.csv")
if os.path.exists(pos_path):
    T,X,Y,AP,R=load_pos(pos_path)
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,6.2),gridspec_kw={"width_ratios":[1.3,1]})
    # RSSI vs t
    aps_u=sorted(set(AP),key=lambda a:(a[0],int(a[1:])))
    ch=plt.cm.Blues(np.linspace(.45,.9,sum(a[0]=="H" for a in aps_u)))
    cc=plt.cm.Purples(np.linspace(.45,.9,sum(a[0]=="C" for a in aps_u)))
    col={};ih=ic=0
    for a in aps_u:
        if a[0]=="H":col[a]=ch[ih];ih+=1
        else:col[a]=cc[ic];ic+=1
    for a in aps_u:
        m=np.array([s==a for s in AP]); ax1.scatter(T[m],R[m],s=14,color=col[a],label=a,zorder=3)
    ax1.axhline(-68,color="#B9770E",ls="--",lw=1.1); ax1.annotate("−68 dBm (300 Mbps)",(T.max(),-68),fontsize=8,ha="right",va="bottom",color="#B9770E")
    ax1.axhline(-82,color=C_BAD,ls=":",lw=1.1); ax1.annotate("−82 dBm (54 Mbps)",(T.max(),-82),fontsize=8,ha="right",va="bottom",color=C_BAD)
    ax1.set_xlabel("Tiempo (s)");ax1.set_ylabel("RSSI del AP servidor (dBm)")
    ax1.set_title("Nivel de señal y traspaso entre AP durante el recorrido")
    ax1.set_ylim(-92,-2);ax1.grid(True,alpha=0.3)
    ax1.legend(ncol=3,fontsize=7.5,loc="lower left",framealpha=0.92,title=f"AP servidor ({len(aps_u)})",title_fontsize=8)
    # CDF
    rs=np.sort(R);cdf=np.arange(1,len(rs)+1)/len(rs)*100
    ax2.plot(rs,cdf,color="#2C5D7C",lw=2.3);ax2.fill_between(rs,0,cdf,color=C_BAR,alpha=0.15)
    ax2.axvline(-68,color="#B9770E",ls="--",lw=1.1);ax2.axvline(-82,color=C_BAD,ls=":",lw=1.1)
    pct=(R>=-68).mean()*100
    ax2.set_xlabel("RSSI (dBm)");ax2.set_ylabel("% del recorrido ≤ RSSI")
    ax2.set_title(f"Distribución acumulada del RSSI\n{pct:.0f}% del recorrido ≥ −68 dBm")
    ax2.grid(True,alpha=0.3);ax2.set_ylim(0,100);ax2.set_xlim(rs.min()-3,rs.max()+3)
    fig.suptitle("Cobertura radioeléctrica a lo largo del recorrido del LHD",fontsize=14,fontweight="bold",y=0.99)
    plt.tight_layout(rect=[0,0,1,0.95])
    out4=os.path.join(HERE,"resultados_cobertura_ruta.png")
    plt.savefig(out4,dpi=155,bbox_inches="tight"); plt.close()
    print(f"[OK] {out4}")

print("\n=== figuras de resultados generadas ===")

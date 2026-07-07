"""
Genera recorrido_nv1640.h (waypoints C++) con el MISMO recorrido del GIF
=======================================================================
Reproduce la lógica del recorrido detallado (grafo Dijkstra + maniobras de
encarar/rodear/reversa) del GIF y exporta los waypoints (x, y, acción) a un
header C++, para que el .cc de NS-3 use EXACTAMENTE el mismo recorrido.

Salida: ../recorrido_nv1640.h
Ejecutar: python generar_recorrido_h.py
"""
import numpy as np, heapq, os, importlib.util

HERE=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("datos",os.path.join(HERE,"mapa_nv1640_datos.py"))
D=importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

# ---- (misma lógica de grafo que animacion_recorrido_lhd.py) ----
def key(p,prec=1): return (round(p[0],prec),round(p[1],prec))
def bez(p0,p1,p2,n=16):
    t=np.linspace(0,1,n)[:,None]; return (1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t**2*np.array(p2)
def densify(pts,cur,fillet=16.0):
    pts=[np.array(p,float) for p in pts]
    if len(pts)==2: return [tuple(pts[0]),tuple(pts[1])]
    o=[tuple(pts[0])]
    for i in range(1,len(pts)-1):
        pv,c,nx=pts[i-1],pts[i],pts[i+1]
        if i in cur:
            din=np.linalg.norm(c-pv);do=np.linalg.norm(nx-c);r=min(fillet,din*.45,do*.45)
            pin=c+(pv-c)/(din+1e-9)*r;po=c+(nx-c)/(do+1e-9)*r
            o.append(tuple(pin))
            for q in bez(pin,c,po)[1:]:o.append(tuple(q))
            o.append(tuple(po))
        else:o.append(tuple(c))
    o.append(tuple(pts[-1]));return o
def subdivide(a,b,step=2.0):
    d=np.hypot(b[0]-a[0],b[1]-a[1]);n=max(1,int(d/step))
    return [(a[0]+(b[0]-a[0])*k/n,a[1]+(b[1]-a[1])*k/n) for k in range(n+1)]

draw_set={(round(x,1),round(y,1)) for (x,y) in D.DRAWPOINTS}
def es_costilla(cam):
    p=cam[-1];return (round(p[0],1),round(p[1],1)) in draw_set
polylines=[]
for cam in D.PRODUCCION:
    if es_costilla(cam):continue
    de=[]
    for i in range(len(cam)-1):de+=subdivide(tuple(cam[i]),tuple(cam[i+1]))
    polylines.append(de)
for r in D.RAMPAS:
    b=densify(r["pts"],r.get("curvas",[]));de=[]
    for i in range(len(b)-1):de+=subdivide(b[i],b[i+1])
    polylines.append(de)
adj={}
def ae(a,b):
    ka,kb=key(a),key(b);d=np.hypot(a[0]-b[0],a[1]-b[1])
    if d<1e-6:return
    adj.setdefault(ka,[]).append((kb,d));adj.setdefault(kb,[]).append((ka,d))
for pl in polylines:
    for i in range(len(pl)-1):ae(pl[i],pl[i+1])
ks=list(adj.keys());grid={}
for k in ks:
    g=(int(k[0]//3),int(k[1]//3));grid.setdefault(g,[]).append(k)
for k in ks:
    gx,gy=int(k[0]//3),int(k[1]//3)
    for dx in(-1,0,1):
        for dy in(-1,0,1):
            for k2 in grid.get((gx+dx,gy+dy),[]):
                if k2==k:continue
                d=np.hypot(k[0]-k2[0],k[1]-k2[1])
                if 0<d<3.0:adj[k].append((k2,d))
def nn(p):return min(adj.keys(),key=lambda k:np.hypot(k[0]-p[0],k[1]-p[1]))
def dij(s,t):
    s,t=key(s),key(t)
    if s not in adj:s=nn(s)
    if t not in adj:t=nn(t)
    pq=[(0,s,[s])];seen=set()
    while pq:
        c,u,pa=heapq.heappop(pq)
        if u==t:return pa
        if u in seen:continue
        seen.add(u)
        for v,w in adj.get(u,[]):
            if v not in seen:heapq.heappush(pq,(c+w,v,pa+[v]))
    return [s,t]

# Para la SIMULACIÓN de teleoperación, el recorrido debe quedar dentro de la
# ZONA DE PRODUCCIÓN (donde hay cobertura y sí se teleopera). La rampa (-176 m)
# es solo acceso manual/contexto: NO se incluye en el recorrido simulado, porque
# ahí no hay AP y dispararía el PLR de forma artificial. Se arranca en el pie de
# la galería central, en el crucero inferior (dentro de cobertura).
Xg=D.X;YB,YT=D.YB,D.YT;entrada=(Xg[1],YB)
route=[];actions=[]
def append_path(path,st="avanza"):
    for k in path:route.append(k);actions.append(st)
def ir_por_grafo(desde,hasta):
    path=[(round(p[0],1),round(p[1],1)) for p in dij(desde,hasta)]
    append_path(path[1:] if route else path,"avanza")
def cur_pos():return route[-1] if route else entrada
def cargar_en(dp):
    info=D.COSTILLA_APPROACH.get((round(dp[0],1),round(dp[1],1)))
    if info is None:
        pie=dp;ir_por_grafo(cur_pos(),pie)
        append_path([pie,(dp[0],dp[1])],"avanza");actions[-1]="CARGA_FIN"
        append_path([(dp[0],dp[1]),pie],"reversa");return
    pie=info['pie'];gx=info['gal'];sent=info['sentido']
    OFF=10.0
    prev=(gx,max(YB,pie[1]-OFF)) if sent=='sube' else (gx,min(YT,pie[1]+OFF))
    ir_por_grafo(cur_pos(),prev)
    append_path([prev,pie],"avanza")
    append_path([pie,(dp[0],dp[1])],"avanza");actions[-1]="CARGA_FIN"
    append_path([(dp[0],dp[1]),pie],"reversa")
def descargar_en(b):
    ir_por_grafo(cur_pos(),b);actions[-1]="DESCARGA_FIN"

b1,b2=D.BOTADEROS[0],D.BOTADEROS[1]
todos=sorted(D.DRAWPOINTS,key=lambda p:p[1])
def acc_de(dp):
    for (x,y,a) in D.DRAWPOINTS_INFO:
        if abs(x-dp[0])<0.5 and abs(y-dp[1])<0.5:return a
    return '?'
dp_ab=next(d for d in todos if acc_de(d)=='abierto')
dp_ce=next(d for d in reversed(todos) if acc_de(d)=='cerrado')
append_path([entrada],"avanza")
cargar_en(dp_ab);descargar_en(b1)
cargar_en(dp_ce);descargar_en(b2)

# ---- generar tiempos (velocidad 2.22 m/s, mínimo 0.5s, pausas en carga/descarga) ----
SPEED=2.22; MIN_DT=0.5; PAUSA=6.0
wps=[]  # (t, x, y)
t=0.0; wps.append((t,route[0][0],route[0][1]))
for i in range(1,len(route)):
    d=np.hypot(route[i][0]-route[i-1][0],route[i][1]-route[i-1][1])
    t+=max(d/SPEED,MIN_DT); wps.append((t,route[i][0],route[i][1]))
    if actions[i] in ("CARGA_FIN","DESCARGA_FIN"):
        t+=PAUSA; wps.append((t,route[i][0],route[i][1]))  # pausa parado

# ---- escribir header C++ ----
out=os.path.join(HERE,"..","recorrido_nv1640.h")
with open(out,"w",encoding="utf-8") as f:
    f.write("// recorrido_nv1640.h — AUTOGENERADO desde generar_recorrido_h.py — NO EDITAR\n")
    f.write("// Recorrido REAL del LHD (mismo que el GIF): grafo Dijkstra + maniobras\n")
    f.write("// de encarar/rodear/reversa. Un ciclo carga-descarga; el .cc lo repite.\n")
    f.write("#ifndef RECORRIDO_NV1640_H\n#define RECORRIDO_NV1640_H\n#include <vector>\n\n")
    f.write("namespace rec {\nstruct WP { double t, x, y; };\n")
    f.write("static const std::vector<WP> RECORRIDO = {\n")
    for (tt,x,y) in wps:
        f.write(f"  {{{tt:.3f},{x:.2f},{y:.2f}}},\n")
    f.write("};\n")
    f.write(f"static const double CICLO_DUR = {wps[-1][0]:.3f}; // duración de un ciclo (s)\n")
    f.write("} // namespace rec\n#endif\n")
print(f"[OK] {os.path.abspath(out)}")
print(f"waypoints: {len(wps)} | duración ciclo: {wps[-1][0]:.1f}s")

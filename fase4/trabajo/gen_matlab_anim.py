# -*- coding: utf-8 -*-
# Genera anim_recorrido_3d.m: ANIMACIÓN del ciclo real del LHD en el entorno 3D.
# Fuente de la trayectoria y del AP servidor: pos_log REAL de la simulación
# (principal_s1): time_s,x,y,best_ap,rssi_dbm,assoc_ap,rssi_assoc_dbm.
import importlib.util, os, sys, csv
sys.stdout.reconfigure(encoding="utf-8")

GS  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
RES = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\results"
TRB = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo"
spec = importlib.util.spec_from_file_location("datos", os.path.join(GS, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

def ml_mat(segs):
    filas = []
    for cam in segs:
        for i in range(len(cam)-1):
            a, b = cam[i], cam[i+1]
            filas.append(f"{a[0]:.2f} {a[1]:.2f} {b[0]:.2f} {b[1]:.2f}")
    return ";\n".join(filas)

prod  = ml_mat(D.PRODUCCION)
aps   = list(D.HAWKS) + list(D.CARDINALS_AP)
ids   = [f"H{i+1}" for i in range(len(D.HAWKS))] + [f"C{i+1}" for i in range(len(D.CARDINALS_AP))]
ap_xy = ";".join(f"{x:.2f} {y:.2f}" for x, y in aps)
ap_id = ",".join(f"'{s}'" for s in ids)

# pos_log real -> t, x, y, idx del AP asociado, rssi
rows = list(csv.DictReader(open(os.path.join(RES, "principal_s1_v3_pos_log.csv"))))
log = []
for r in rows:
    ap = r["assoc_ap"].strip()
    idx = ids.index(ap) + 1 if ap in ids else 0
    log.append(f"{float(r['time_s']):.1f} {float(r['x']):.2f} {float(r['y']):.2f} {idx} {float(r['rssi_assoc_dbm']):.1f}")
log_m = ";\n".join(log)
trb = TRB.replace("\\", "\\\\")

m = f"""% anim_recorrido_3d.m — AUTOGENERADO. Animación del ciclo real (pos_log de NS-3).
try
SEG = [{prod}];
AP  = [{ap_xy}];
IDS = {{{ap_id}}};
G   = readmatrix('{trb}\\\\grid_rssi.csv');
LOG = [{log_m}];          %% t x y ap_idx rssi (datos reales de la simulación)
NF  = size(LOG,1);
W = 4; H = 4;
fig = figure('Position',[40 40 1280 760],'Color','w','Visible','off');
ax = axes(fig); hold(ax,'on');
for k = 1:size(SEG,1)
    x1=SEG(k,1); y1=SEG(k,2); x2=SEG(k,3); y2=SEG(k,4);
    L = hypot(x2-x1, y2-y1); if L < 0.5, continue; end
    ang = atan2(y2-y1, x2-x1);
    ux = -sin(ang)*W/2; uy = cos(ang)*W/2;
    vx = [x1+ux x1-ux x2-ux x2+ux]; vy = [y1+uy y1-uy y2-uy y2+uy];
    patch(ax, vx, vy, zeros(1,4), [0.90 0.92 0.95], 'EdgeColor',[0.7 0.74 0.8]);
end
scatter3(ax, G(:,1), G(:,2), 0.05*ones(size(G,1),1), 34, G(:,3), 'filled', 's');
colormap(ax, turbo); clim(ax,[-55 -10]);
scatter3(ax, AP(1:5,1), AP(1:5,2), 2*ones(5,1), 240, '^', 'MarkerFaceColor',[0.08 0.40 0.75],'MarkerEdgeColor','w');
scatter3(ax, AP(6:12,1), AP(6:12,2), 2*ones(7,1), 190, 's', 'MarkerFaceColor',[0.48 0.12 0.64],'MarkerEdgeColor','w');
for k = 1:12
    text(ax, AP(k,1), AP(k,2), 4.4, IDS{{k}}, 'FontWeight','bold','FontSize',10,'HorizontalAlignment','center');
end
axis(ax,'equal'); grid(ax,'on'); view(ax,-35,32);
xlim(ax,[-14 66]); ylim(ax,[-12 172]); zlim(ax,[0 20]);
xlabel(ax,'X (m)'); ylabel(ax,'Y (m)');
title(ax,'Teleoperación del LHD — ciclo real de la simulación NS-3 (NV1640)','FontSize',13);

% elementos dinámicos
hLHD = plot3(ax, LOG(1,2), LOG(1,3), 1.2, 's', 'MarkerSize',16, 'MarkerFaceColor',[0.95 0.75 0.10], 'MarkerEdgeColor',[0.3 0.2 0]);
hHALO = plot3(ax, AP(1,1), AP(1,2), 2, 'o', 'MarkerSize',26, 'Color',[0.95 0.35 0.05], 'LineWidth',2.6, 'Visible','off');
hLNK = plot3(ax, [0 0],[0 0],[1.2 2], '-', 'Color',[0.95 0.35 0.05], 'LineWidth',1.8, 'Visible','off');
hTXT = text(ax, -10, 168, 16, '', 'FontSize',12, 'FontWeight','bold', 'Color',[0.15 0.15 0.15]);

vw = VideoWriter('{trb}\\\\anim_recorrido_3d.mp4','MPEG-4');
vw.FrameRate = 10; vw.Quality = 92; open(vw);
for i = 1:NF
    set(hLHD, 'XData', LOG(i,2), 'YData', LOG(i,3));
    k = LOG(i,4);
    if k >= 1
        set(hHALO, 'XData', AP(k,1), 'YData', AP(k,2), 'Visible','on');
        set(hLNK, 'XData', [LOG(i,2) AP(k,1)], 'YData', [LOG(i,3) AP(k,2)], 'ZData', [1.2 2], 'Visible','on');
        set(hTXT, 'String', sprintf('t = %.0f s   |   AP servidor: %s   |   RSSI: %.0f dBm', LOG(i,1), IDS{{k}}, LOG(i,5)));
    else
        set(hTXT, 'String', sprintf('t = %.0f s', LOG(i,1)));
    end
    drawnow;
    writeVideo(vw, getframe(fig));
end
close(vw);
fprintf('VIDEO OK (%d frames)\\n', NF);
catch e
    fprintf('ERROR: %s\\n', e.message);
end
exit;
"""
with open(os.path.join(TRB, "anim_recorrido_3d.m"), "w", encoding="utf-8") as f:
    f.write(m)
print(f"anim_recorrido_3d.m generado ({len(log)} frames del pos_log real)")

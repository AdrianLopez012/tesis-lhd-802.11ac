# -*- coding: utf-8 -*-
# v2 — Genera escena_mina_3d.m: galerías 3D + heatmap RSSI en el piso (mismo
# modelo de la simulación) + recorrido real del LHD + 12 AP etiquetados +
# patrón 3D de hélice axial sobre el LHD. Todo desde la fuente única.
import importlib.util, os, sys
sys.stdout.reconfigure(encoding="utf-8")

GS  = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
TRB = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo"
OUT = os.path.join(TRB, "escena_mina_3d.m")
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
hawks = ";".join(f"{x:.2f} {y:.2f}" for x, y in D.HAWKS)
cards = ";".join(f"{x:.2f} {y:.2f}" for x, y in D.CARDINALS_AP)
lhd_x, lhd_y = D.X[1], 60.0
trb = TRB.replace("\\", "\\\\")

m = f"""% escena_mina_3d.m v2 — AUTOGENERADO desde la fuente única de datos
try
SEG = [{prod}];
HAWKS = [{hawks}];
CARDS = [{cards}];
G = readmatrix('{trb}\\\\grid_rssi.csv');       % x, y, RSSI (modelo de la simulación)
RT = readmatrix('{trb}\\\\ruta.csv');           % recorrido real del LHD
W = 4; H = 4;
fig = figure('Position',[40 40 1560 980],'Color','w');
ax = axes(fig); hold(ax,'on');

% --- galerías (paredes tenues + techo) ---
for k = 1:size(SEG,1)
    x1=SEG(k,1); y1=SEG(k,2); x2=SEG(k,3); y2=SEG(k,4);
    L = hypot(x2-x1, y2-y1); if L < 0.5, continue; end
    ang = atan2(y2-y1, x2-x1);
    ux = -sin(ang)*W/2; uy = cos(ang)*W/2;
    vx = [x1+ux x1-ux x2-ux x2+ux];
    vy = [y1+uy y1-uy y2-uy y2+uy];
    patch(ax, vx, vy, zeros(1,4), [0.88 0.90 0.94], 'EdgeColor',[0.65 0.70 0.78], 'FaceAlpha',1);
    patch(ax, vx, vy, H*ones(1,4), [0.92 0.94 0.97], 'EdgeColor',[0.7 0.75 0.82], 'FaceAlpha',0.10);
    patch(ax, [vx(1) vx(2) vx(2) vx(1)], [vy(1) vy(2) vy(2) vy(1)], [0 0 H H], [0.88 0.90 0.95], 'EdgeColor','none','FaceAlpha',0.10);
    patch(ax, [vx(4) vx(3) vx(3) vx(4)], [vy(4) vy(3) vy(3) vy(4)], [0 0 H H], [0.88 0.90 0.95], 'EdgeColor','none','FaceAlpha',0.10);
end

% --- HEATMAP de RSSI sobre el piso (mismo modelo two-slope de la simulación) ---
hHM = scatter3(ax, G(:,1), G(:,2), 0.06*ones(size(G,1),1), 46, G(:,3), 'filled', 's');
colormap(ax, turbo); clim(ax,[-55 -10]);
cb = colorbar(ax); cb.Label.String = 'RSSI del mejor AP en el piso de galería (dBm)'; cb.Label.FontSize = 11;

% --- recorrido real del LHD ---
hRT = plot3(ax, RT(:,1), RT(:,2), 0.35*ones(size(RT,1),1), '-', 'Color',[0.10 0.10 0.10], 'LineWidth', 2.0);

% --- AP con etiquetas ---
hH = scatter3(ax, HAWKS(:,1), HAWKS(:,2), 2*ones(size(HAWKS,1),1), 300, '^', ...
    'MarkerFaceColor',[0.08 0.40 0.75],'MarkerEdgeColor','w','LineWidth',1.4);
hC = scatter3(ax, CARDS(:,1), CARDS(:,2), 2*ones(size(CARDS,1),1), 230, 's', ...
    'MarkerFaceColor',[0.48 0.12 0.64],'MarkerEdgeColor','w','LineWidth',1.4);
for k = 1:size(HAWKS,1)
    text(ax, HAWKS(k,1), HAWKS(k,2), 4.6, sprintf('H%d',k), 'FontWeight','bold', ...
        'FontSize',11, 'Color',[0.05 0.28 0.55], 'HorizontalAlignment','center');
end
for k = 1:size(CARDS,1)
    text(ax, CARDS(k,1), CARDS(k,2), 4.6, sprintf('C%d',k), 'FontWeight','bold', ...
        'FontSize',11, 'Color',[0.35 0.08 0.48], 'HorizontalAlignment','center');
end

% --- LHD ---
lx = {lhd_x:.2f}; ly = {lhd_y:.2f};
lw=2.6; ll=9; lh=2.3;
[Xc,Yc,Zc] = ndgrid([-lw/2 lw/2],[-ll/2 ll/2],[0 lh]);
fv = [1 2 4 3; 5 6 8 7; 1 2 6 5; 3 4 8 7; 1 3 7 5; 2 4 8 6];
V = [Xc(:)+lx Yc(:)+ly Zc(:)];
hLHD = patch(ax,'Vertices',V,'Faces',fv,'FaceColor',[0.95 0.75 0.10],'EdgeColor',[0.4 0.3 0],'FaceAlpha',1);

% --- patrón 3D de hélice axial (~antena del LHD), color sólido ---
hx = helix('Radius',0.0091,'Width',0.0016,'Turns',7.5,'Spacing',0.0115);
f0 = 5.0e9;
[pat,az,el] = pattern(hx, f0);
P = pat - max(pat(:));
R = 10.^(P/20); R(R<0.05)=0.05;
esc = 15;
[AZ,EL] = meshgrid(deg2rad(az), deg2rad(el));
Rm = R * esc;
Xp = Rm .* cos(EL) .* cos(AZ) + lx;
Yp = Rm .* cos(EL) .* sin(AZ) + ly;
Zp = Rm .* sin(EL) + lh + 0.6;
hPT = surf(ax, Xp, Yp, Zp, 'FaceColor',[0.86 0.32 0.10], 'EdgeColor','none','FaceAlpha',0.42);

% --- estética ---
axis(ax,'equal'); grid(ax,'on'); view(ax, -35, 30);
camlight(ax,'headlight'); lighting(ax,'gouraud');
xlabel(ax,'X (m)'); ylabel(ax,'Y (m)'); zlabel(ax,'Z (m)');
xlim(ax,[-14 66]); ylim(ax,[-12 172]); zlim(ax,[0 22]);
title(ax, sprintf('Zona de producción NV1640 — cobertura RSSI calculada, recorrido real del LHD y patrón\\nde radiación de su antena helicoidal (modelo two-slope de la simulación · Antenna Toolbox, %.1f GHz)', f0/1e9), 'FontSize', 13);
legend(ax, [hH hC hRT hPT], {{'AP Hawk (30 dBm / 11 dBi)','AP Cardinal (23 dBm / 7.5 dBi)','Recorrido real del LHD (ciclo de operación)','Patrón de radiación antena LHD (hélice axial)'}}, ...
    'Location','northeastoutside','FontSize',10);
exportgraphics(fig, '{trb}\\\\escena_mina_3d.png', 'Resolution', 220);
fprintf('PNG OK\\n');
catch e
    fprintf('ERROR: %s\\n', e.message);
end
exit;
"""
with open(OUT, "w", encoding="utf-8") as f:
    f.write(m)
print("escena_mina_3d.m v2 generado")

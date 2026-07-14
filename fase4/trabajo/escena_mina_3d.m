% escena_mina_3d.m — AUTOGENERADO desde mapa_nv1640_datos.py (fuente única)
% Entorno 3D del NV1640: galerías reales (sección 4x4 m), 12 AP en posiciones
% reales y patrón de radiación 3D de una hélice axial (~HELI-40) sobre el LHD.
try
SEG = [0.00 0.00 0.00 134.85;
25.98 0.00 25.98 134.85;
51.96 0.00 51.96 134.85;
0.00 134.85 51.96 134.85;
0.00 0.00 51.96 0.00;
0.00 8.00 7.70 8.00;
25.98 8.00 33.68 8.00;
0.00 20.99 10.49 30.00;
25.98 39.01 15.49 30.00;
25.98 20.99 36.47 30.00;
51.96 39.01 41.47 30.00;
0.00 43.70 10.49 52.71;
25.98 61.72 15.49 52.71;
25.98 43.70 36.47 52.71;
51.96 61.72 41.47 52.71;
0.00 66.41 10.49 75.42;
25.98 84.44 15.49 75.42;
25.98 66.41 36.47 75.42;
51.96 84.44 41.47 75.42;
0.00 89.13 10.49 98.14;
25.98 107.15 15.49 98.14;
25.98 89.13 36.47 98.14;
51.96 107.15 41.47 98.14;
0.00 111.84 10.49 120.85;
25.98 129.86 15.49 120.85;
25.98 111.84 36.47 120.85;
51.96 129.86 41.47 120.85;
0.00 134.85 0.00 160.85;
25.98 134.85 25.98 160.85];
HAWKS = [-0.20 134.90;-0.10 88.60;25.90 43.40;25.90 -0.30;52.20 84.60];
CARDS = [-0.30 43.80;-0.10 8.00;26.10 129.10;26.30 87.20;26.30 21.40;52.00 38.50;52.40 129.70];
W = 4; H = 4;                        % sección de galería 4x4 m
fig = figure('Position',[50 50 1500 950],'Color','w');
ax = axes(fig); hold(ax,'on');

% --- galerías como prismas 3D ---
for k = 1:size(SEG,1)
    x1=SEG(k,1); y1=SEG(k,2); x2=SEG(k,3); y2=SEG(k,4);
    L = hypot(x2-x1, y2-y1); if L < 0.5, continue; end
    ang = atan2(y2-y1, x2-x1);
    ux = -sin(ang)*W/2; uy = cos(ang)*W/2;
    vx = [x1+ux x1-ux x2-ux x2+ux];
    vy = [y1+uy y1-uy y2-uy y2+uy];
    patch(ax, vx, vy, zeros(1,4), [0.82 0.86 0.92], 'EdgeColor',[0.45 0.52 0.62], 'FaceAlpha',0.95);          % piso
    patch(ax, vx, vy, H*ones(1,4), [0.90 0.92 0.96], 'EdgeColor',[0.6 0.65 0.75], 'FaceAlpha',0.18);          % techo
    patch(ax, [vx(1) vx(2) vx(2) vx(1)], [vy(1) vy(2) vy(2) vy(1)], [0 0 H H], [0.86 0.89 0.94], 'EdgeColor','none','FaceAlpha',0.15);
    patch(ax, [vx(4) vx(3) vx(3) vx(4)], [vy(4) vy(3) vy(3) vy(4)], [0 0 H H], [0.86 0.89 0.94], 'EdgeColor','none','FaceAlpha',0.15);
end

% --- AP: Hawk (triángulos azules) y Cardinal (cuadrados morados) a 2 m ---
scatter3(ax, HAWKS(:,1), HAWKS(:,2), 2*ones(size(HAWKS,1),1), 260, '^', ...
    'MarkerFaceColor',[0.08 0.40 0.75],'MarkerEdgeColor','w','LineWidth',1.2);
scatter3(ax, CARDS(:,1), CARDS(:,2), 2*ones(size(CARDS,1),1), 200, 's', ...
    'MarkerFaceColor',[0.48 0.12 0.64],'MarkerEdgeColor','w','LineWidth',1.2);

% --- LHD (caja) en la galería central ---
lx = 25.98; ly = 60.00;
lw=2.6; ll=9; lh=2.3;
[Xc,Yc,Zc] = ndgrid([-lw/2 lw/2],[-ll/2 ll/2],[0 lh]);
fv = [1 2 4 3; 5 6 8 7; 1 2 6 5; 3 4 8 7; 1 3 7 5; 2 4 8 6];
V = [Xc(:)+lx Yc(:)+ly Zc(:)];
patch(ax,'Vertices',V,'Faces',fv,'FaceColor',[0.95 0.75 0.10],'EdgeColor',[0.4 0.3 0],'FaceAlpha',0.95);

% --- patrón 3D de hélice axial (~HELI-40) sobre el LHD (Antenna Toolbox) ---
hx = helix('Radius',0.0091,'Width',0.0016,'Turns',7.5,'Spacing',0.0115);
f0 = 5.0e9;
[pat,az,el] = pattern(hx, f0);
P = pat - max(pat(:));
R = 10.^(P/20); R(R<0.05)=0.05;
esc = 16;                             % escala visual del lóbulo (m)
[AZ,EL] = meshgrid(deg2rad(az), deg2rad(el));
Rm = R * esc;
Xp = Rm .* cos(EL) .* cos(AZ) + lx;
Yp = Rm .* cos(EL) .* sin(AZ) + ly;
Zp = Rm .* sin(EL) + lh + 0.6;
surf(ax, Xp, Yp, Zp, pat, 'EdgeColor','none','FaceAlpha',0.55);
colormap(ax, jet); cb = colorbar(ax); cb.Label.String = 'Directividad de la antena del LHD (dBi)';

% --- estética ---
axis(ax,'equal'); grid(ax,'on'); view(ax, -35, 28);
camlight(ax,'headlight'); lighting(ax,'gouraud');
xlabel(ax,'X (m)'); ylabel(ax,'Y (m)'); zlabel(ax,'Z (m)');
xlim(ax,[-14 66]); ylim(ax,[-12 172]); zlim(ax,[0 24]);
title(ax, sprintf('Zona de producción NV1640 en 3D — 12 AP en posiciones reales y patrón de radiación\nde la antena helicoidal del LHD (hélice axial, %.1f GHz, Antenna Toolbox)', f0/1e9), 'FontSize', 13);
legend(ax, {'','','','','AP Hawk (30 dBm / 11 dBi)','AP Cardinal (23 dBm / 7.5 dBi)'}, 'Location','northeastoutside','AutoUpdate','off');
exportgraphics(fig, 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\escena_mina_3d.png', 'Resolution', 220);
fprintf('PNG OK\n');
catch e
    fprintf('ERROR: %s\n', e.message);
end
exit;

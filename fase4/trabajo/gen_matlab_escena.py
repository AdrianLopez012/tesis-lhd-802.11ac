# -*- coding: utf-8 -*-
# Genera escena_mina_3d.m con las coordenadas REALES desde la fuente única
# (mapa_nv1640_datos.py). El .m dibuja las galerías 3D, los 12 AP y el patrón
# de radiación de una hélice axial (Antenna Toolbox) sobre el LHD.
import importlib.util, os, sys
sys.stdout.reconfigure(encoding="utf-8")

GS = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\graficas_simulacion"
OUT = r"C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\escena_mina_3d.m"
spec = importlib.util.spec_from_file_location("datos", os.path.join(GS, "mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

def ml_mat(segs):
    """lista de tramos [(x1,y1,x2,y2),...] como matriz MATLAB"""
    filas = []
    for cam in segs:
        for i in range(len(cam)-1):
            a, b = cam[i], cam[i+1]
            filas.append(f"{a[0]:.2f} {a[1]:.2f} {b[0]:.2f} {b[1]:.2f}")
    return ";\n".join(filas)

# solo la zona de producción (galerías/cruceros/costillas); rampa fuera para el encuadre
prod = ml_mat(D.PRODUCCION)
hawks = ";".join(f"{x:.2f} {y:.2f}" for x, y in D.HAWKS)
cards = ";".join(f"{x:.2f} {y:.2f}" for x, y in D.CARDINALS_AP)
lhd_x, lhd_y = D.X[1], 60.0   # LHD en la galería central, a media ruta

m = f"""% escena_mina_3d.m — AUTOGENERADO desde mapa_nv1640_datos.py (fuente única)
% Entorno 3D del NV1640: galerías reales (sección 4x4 m), 12 AP en posiciones
% reales y patrón de radiación 3D de una hélice axial (~HELI-40) sobre el LHD.
try
SEG = [{prod}];
HAWKS = [{hawks}];
CARDS = [{cards}];
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
lx = {lhd_x:.2f}; ly = {lhd_y:.2f};
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
title(ax, sprintf('Zona de producción NV1640 en 3D — 12 AP en posiciones reales y patrón de radiación\\nde la antena helicoidal del LHD (hélice axial, %.1f GHz, Antenna Toolbox)', f0/1e9), 'FontSize', 13);
legend(ax, {{'','','','','AP Hawk (30 dBm / 11 dBi)','AP Cardinal (23 dBm / 7.5 dBi)'}}, 'Location','northeastoutside','AutoUpdate','off');
exportgraphics(fig, 'C:\\Users\\Adrian Lopez\\Documents\\tesis_proyecto\\fase4\\trabajo\\escena_mina_3d.png', 'Resolution', 220);
fprintf('PNG OK\\n');
catch e
    fprintf('ERROR: %s\\n', e.message);
end
exit;
"""
with open(OUT, "w", encoding="utf-8") as f:
    f.write(m)
print(f"generado {OUT} con {len(D.PRODUCCION)} caminos, {len(D.HAWKS)}+{len(D.CARDINALS_AP)} AP")

% ver_patrones_reales.m — VISTA INTERACTIVA en MATLAB: la mina con PATRONES DE
% RADIACIÓN REALES, grandes y bien orientados:
%   · Hawk: hélice axial con el lóbulo APUNTANDO A LO LARGO DE SU GALERÍA
%   · Cardinal: dipolo omni (su patrón real es la dona horizontal)
%   · LHD: ARREGLO HELICOIDAL 2x2 (4 hélices MIMO) — patrón del arreglo completo
% Rueda del mouse = zoom, arrastrar = rotar. NO usa exit: queda abierta.
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
REC = readmatrix([TRB 'anim_recorrido.csv']);
AP  = readmatrix([TRB 'anim_aps.csv']);      % x, y, tipo, angulo_galeria
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};
f0 = 5e9;
azf = -180:3:180; elf = -90:3:90;            % malla fina de patrón

fprintf('Calculando patrones reales (el arreglo 2x2 tarda ~1-2 min)...\n');
helHawk = helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115);
pH = pattern(helHawk, f0, azf, elf);
omni = dipole('Length',0.028,'Width',0.001);
pC = pattern(omni, f0, azf, elf);
% --- HELI-40 del LHD (datasheet real): 4.8 dBic, pol. circular, BI-DIRECCIONAL ---
% patrón bidireccional = lóbulo axial + su espejo (dos lóbulos opuestos por el túnel)
pHel = pattern(helix('Radius',0.0091,'Width',0.0016,'Turns',4,'Spacing',0.0115), f0, azf, elf);
pL = max(pHel, flipud(pHel));           % bi-direccional (túnel/NLOS, según datasheet)
nomL = 'HELI-40 bidireccional · 4.8 dBic · pol. circular';
fprintf('patrones listos.\n');

fig = figure('Name','Patrones de radiación reales — NV1640','Position',[20 20 1500 880], ...
    'Color',[0.04 0.04 0.06],'Renderer','opengl');
ax = axes(fig); hold(ax,'on'); set(ax,'Color',[0.05 0.05 0.07]);

% ---- mina (paredes + techo fantasma) ----
tr = stlread([TRB 'galeria_nv1640.stl']);
V = tr.Points; F = tr.ConnectivityList;
rng(1); vc = [0.46 0.40 0.34] + 0.10*(rand(size(V,1),1)-0.5);
patch(ax,'Faces',F,'Vertices',V,'FaceVertexCData',min(max(vc,0.15),0.62), ...
    'FaceColor','interp','EdgeColor','none','FaceLighting','gouraud', ...
    'AmbientStrength',0.4,'DiffuseStrength',0.9);
trT = stlread([TRB 'galeria_techo.stl']);
patch(ax,'Faces',trT.ConnectivityList,'Vertices',trT.Points, ...
    'FaceColor',[0.5 0.44 0.38],'EdgeColor','none','FaceAlpha',0.13,'FaceLighting','gouraud');

% ---- función: dibujar lóbulo GRANDE con orientación (lóbulo axial -> horizontal) ----
function dibujar(ax, pat, azv, elv, cx, cy, cz, esc, angulo, girar)
    P = pat - max(pat(:)); R = 10.^(P/20); R(R<0.05)=0.05;
    [AZ,EL] = meshgrid(deg2rad(azv), deg2rad(elv));
    Rm = R*esc;
    X = Rm.*cos(EL).*cos(AZ); Y = Rm.*cos(EL).*sin(AZ); Z = Rm.*sin(EL);
    if girar
        % la hélice axial radia hacia +Z: girar para que apunte por la galería
        Xn =  Z*cos(angulo) - Y*sin(angulo)*0;   % z -> dirección de galería
        Yn =  Z*sin(angulo);
        Zn = -X*cos(angulo) - Y.*0 + 0;          % aproximación: eje axial -> horizontal
        % rotación limpia: primero eje z->x (pitch 90°), luego yaw=angulo
        X1 = Z; Y1 = Y; Z1 = -X;
        Xn = X1*cos(angulo) - Y1*sin(angulo);
        Yn = X1*sin(angulo) + Y1*cos(angulo);
        Zn = Z1;
        X = Xn; Y = Yn; Z = Zn;
    end
    surf(ax, X+cx, Y+cy, Z+cz, pat, 'EdgeColor','none','FaceAlpha',0.5,'FaceLighting','none');
end

% ---- APs con patrones reales orientados ----
for k = 1:size(AP,1)
    angg = AP(k,4);
    if AP(k,3)==1
        dibujar(ax, pH, azf, elf, AP(k,1), AP(k,2), 3.0, 9, angg, true);   % Hawk: lóbulo POR el túnel
        col = [0.30 0.70 1.0];
    else
        dibujar(ax, pC, azf, elf, AP(k,1), AP(k,2), 3.0, 6, 0, false);     % Cardinal: dona omni real
        col = [0.80 0.50 1.0];
    end
    plot3(ax, AP(k,1), AP(k,2), 3.0, 'o','MarkerSize',9,'MarkerFaceColor',col,'MarkerEdgeColor','w','LineWidth',1.2);
    text(ax, AP(k,1), AP(k,2), 6.2, IDS{k}, 'FontWeight','bold','FontSize',11,'Color',col,'HorizontalAlignment','center');
end
colormap(ax, turbo);
cb = colorbar(ax); cb.Color = 'w'; cb.Label.String = 'Ganancia relativa del patrón (dB)'; cb.Label.Color = 'w';

% ---- LHD con el patrón del ARREGLO 2x2 ----
i0 = 100; x = REC(i0,2); y = REC(i0,3);
g = hgtransform('Parent',ax);
caja(g,[-4.0 -1.4 0.4],[3.0 2.8 1.9],[0.92 0.68 0.06]); caja(g,[0.3 -1.3 0.4],[2.4 2.6 1.5],[0.92 0.68 0.06]);
caja(g,[-1.5 -0.7 0.6],[1.4 1.4 1.2],[0.22 0.22 0.24]); caja(g,[2.6 -1.6 0.1],[1.5 3.2 1.7],[0.22 0.22 0.24]);
caja(g,[-2.9 -1.1 2.3],[1.6 2.2 1.1],[0.15 0.30 0.45]);
for wx=[-3.2 1.4], for wy=[-1.5 1.5], rueda(g,wx,wy,0.7,1.0,[0.08 0.08 0.08]); end, end
set(g,'Matrix',makehgtform('translate',[x y 0],'zrotate',pi/2));
angLHD = atan2(REC(i0+1,3)-y, REC(i0+1,2)-x);
dibujar(ax, pL, azf, elf, x, y, 4.2, 7, angLHD, true);
text(ax, x, y, 9.5, sprintf('LHD — %s', nomL), 'FontWeight','bold','FontSize',11,'Color',[1 0.8 0.2],'HorizontalAlignment','center');

axis(ax,'equal'); axis(ax,'off'); view(ax,-30,38);
xlim(ax,[-8 62]); ylim(ax,[-8 172]); zlim(ax,[0 22]);
light(ax,'Position',[26 80 100],'Style','infinite','Color',[0.65 0.65 0.7]);
light(ax,'Position',[90 -30 50],'Style','infinite','Color',[0.4 0.38 0.35]);
light(ax,'Position',[-40 40 60],'Style','infinite','Color',[0.35 0.32 0.30]);
title(ax,'Patrones reales (datasheets): Hawk HELI RCP-50 (11 dBi) por la galería · Cardinal EPNT-7 omni (7.5 dBi) · LHD HELI-40 bidireccional (4.8 dBic)', ...
    'FontSize',12,'Color','w');
rotate3d(fig,'on');
disp('VISTA INTERACTIVA LISTA: rota con el mouse, zoom con la rueda.');

function caja(par,o,s,c)
    [X,Y,Z]=ndgrid([o(1) o(1)+s(1)],[o(2) o(2)+s(2)],[o(3) o(3)+s(3)]);
    v=[X(:) Y(:) Z(:)]; f=[1 2 4 3;5 6 8 7;1 2 6 5;3 4 8 7;1 3 7 5;2 4 8 6];
    patch('Vertices',v,'Faces',f,'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end
function rueda(par,cx,cy,r,w,c)
    [th,zz]=meshgrid(linspace(0,2*pi,16),[cy-w/2 cy+w/2]);
    surf(cx+r*cos(th),zz,r+r*sin(th),'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end

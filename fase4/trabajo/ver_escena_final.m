% ver_escena_final.m — ESCENA DEFINITIVA (carga en segundos, todo precalculado):
%   · galería 3D con uniones limpias y techo fantasma
%   · los 12 AP con sus PATRONES REALES bien situados y orientados:
%       Hawk = RCP-50 LHP/RHP BIDIRECCIONAL a lo largo de su galería (tramos largos)
%       Cardinal = EPNT-7 omni (dona) en cruceros
%   · el LHD con su HELI-40 BIDIRECCIONAL
%   · 108 RAYOS SBR reales (H4 -> 12/24/38 m) coloreados por pérdida de trayecto
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
load([TRB 'escena_cache.mat']);              % pHawkBi pCard pLHDBi az el rayos k angH4
AP = readmatrix([TRB 'anim_aps.csv']);
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};

fig = figure('Name','Escena final — patrones reales + rayos SBR','Position',[15 15 1520 900], ...
    'Color',[0.04 0.04 0.06],'Renderer','opengl');
ax = axes(fig); hold(ax,'on'); set(ax,'Color',[0.05 0.05 0.07]);

% ---- mina ----
tr = stlread([TRB 'galeria_nv1640.stl']);
V = tr.Points; F = tr.ConnectivityList;
rng(1); vc = [0.46 0.40 0.34] + 0.10*(rand(size(V,1),1)-0.5);
patch(ax,'Faces',F,'Vertices',V,'FaceVertexCData',min(max(vc,0.15),0.62), ...
    'FaceColor','interp','EdgeColor','none','FaceLighting','gouraud','AmbientStrength',0.42);
trT = stlread([TRB 'galeria_techo.stl']);
patch(ax,'Faces',trT.ConnectivityList,'Vertices',trT.Points, ...
    'FaceColor',[0.5 0.44 0.38],'EdgeColor','none','FaceAlpha',0.10,'FaceLighting','gouraud');

% ---- patrones (desde caché, instantáneo) ----
function dib(ax, pat, azv, elv, cx, cy, cz, esc, ang, girar, alfa)
    P = pat - max(pat(:)); R = 10.^(P/20); R(R<0.05)=0.05;
    [AZ,EL] = meshgrid(deg2rad(azv), deg2rad(elv));
    Rm = R*esc;
    X = Rm.*cos(EL).*cos(AZ); Y = Rm.*cos(EL).*sin(AZ); Z = Rm.*sin(EL);
    if girar
        X1 = Z; Y1 = Y; Z1 = -X;                      % eje axial -> horizontal
        X = X1*cos(ang) - Y1*sin(ang);
        Y = X1*sin(ang) + Y1*cos(ang);
        Z = Z1;
    end
    surf(ax, X+cx, Y+cy, Z+cz, pat, 'EdgeColor','none','FaceAlpha',alfa,'FaceLighting','none');
end
for q = 1:size(AP,1)
    if AP(q,3)==1
        dib(ax, pHawkBi, az, el, AP(q,1), AP(q,2), 3.0, 6.5, AP(q,4), true, 0.45);   % BIDIRECCIONAL por la galería
        col=[0.30 0.70 1.0];
    else
        dib(ax, pCard, az, el, AP(q,1), AP(q,2), 3.0, 4.5, 0, false, 0.40);          % dona omni
        col=[0.80 0.50 1.0];
    end
    plot3(ax,AP(q,1),AP(q,2),3.0,'o','MarkerSize',8,'MarkerFaceColor',col,'MarkerEdgeColor','w');
    text(ax,AP(q,1),AP(q,2),6.2,IDS{q},'FontWeight','bold','FontSize',10,'Color',col,'HorizontalAlignment','center');
end
colormap(ax, turbo);

% ---- LHD en la posición de 24 m con su HELI-40 bidireccional ----
u = [cos(angH4), sin(angH4)];
PL = [AP(k,1), AP(k,2)] + u*24;
g = hgtransform('Parent',ax);
caja(g,[-4.0 -1.4 0.4],[3.0 2.8 1.9],[0.92 0.68 0.06]); caja(g,[0.3 -1.3 0.4],[2.4 2.6 1.5],[0.92 0.68 0.06]);
caja(g,[-1.5 -0.7 0.6],[1.4 1.4 1.2],[0.22 0.22 0.24]); caja(g,[2.6 -1.6 0.1],[1.5 3.2 1.7],[0.22 0.22 0.24]);
caja(g,[-2.9 -1.1 2.3],[1.6 2.2 1.1],[0.15 0.30 0.45]);
for wx=[-3.2 1.4], for wy=[-1.5 1.5], rueda(g,wx,wy,0.7,1.0,[0.08 0.08 0.08]); end, end
set(g,'Matrix',makehgtform('translate',[PL(1) PL(2) 0],'zrotate',angH4));
dib(ax, pLHDBi, az, el, PL(1), PL(2), 4.4, 4.0, angH4, true, 0.5);
text(ax, PL(1), PL(2), 9.6, 'LHD — HELI-40 bidireccional (4.8 dBic)', ...
    'FontWeight','bold','FontSize',11,'Color',[1 0.8 0.2],'HorizontalAlignment','center');

% ---- RAYOS SBR reales, coloreados por pérdida de trayecto ----
pls = cellfun(@(r) r.pl, rayos);
plmin = min(pls); plmax = max(pls);
cmap = turbo(256);
for q = 1:numel(rayos)
    R = rayos{q};
    f = (R.pl - plmin) / max(plmax - plmin, 1);
    cidx = max(1, min(256, round(1 + f*255)));
    c = cmap(257 - cidx, :);                          % menor pérdida = colores cálidos
    plot3(ax, R.pts(:,1), R.pts(:,2), R.pts(:,3), '-', 'Color', [c 0.55], 'LineWidth', 1.1);
end
fprintf('rayos dibujados: %d (pérdida %.0f a %.0f dB)\n', numel(rayos), plmin, plmax);

title(ax, sprintf(['Patrones reales + %d rayos SBR (H4 \\rightarrow 12/24/38 m) — ' ...
    'Hawk RCP-50 bidireccional · Cardinal EPNT-7 omni · HELI-40 en el LHD'], numel(rayos)), ...
    'FontSize',13,'Color','w');
annotation(fig,'textbox',[0.015 0.015 0.8 0.06],'EdgeColor','none','FontSize',11.5,'Color','w', ...
    'String','Rayos: color cálido = menor pérdida de trayecto. Roca: \epsilon_r = 6, \sigma = 0.01 S/m, hasta 5 reflexiones (SBR).');

axis(ax,'equal'); axis(ax,'off'); view(ax,-30,36);
xlim(ax,[-10 62]); ylim(ax,[-8 172]); zlim(ax,[0 20]);
light(ax,'Position',[26 80 100],'Style','infinite','Color',[0.65 0.65 0.7]);
light(ax,'Position',[90 -30 50],'Style','infinite','Color',[0.4 0.38 0.35]);
light(ax,'Position',[-40 40 60],'Style','infinite','Color',[0.35 0.32 0.30]);
rotate3d(fig,'on');
disp('ESCENA FINAL LISTA — rota con el mouse, zoom con la rueda.');

function caja(par,o,s,c)
    [X,Y,Z]=ndgrid([o(1) o(1)+s(1)],[o(2) o(2)+s(2)],[o(3) o(3)+s(3)]);
    v=[X(:) Y(:) Z(:)]; f=[1 2 4 3;5 6 8 7;1 2 6 5;3 4 8 7;1 3 7 5;2 4 8 6];
    patch('Vertices',v,'Faces',f,'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end
function rueda(par,cx,cy,r,w,c)
    [th,zz]=meshgrid(linspace(0,2*pi,16),[cy-w/2 cy+w/2]);
    surf(cx+r*cos(th),zz,r+r*sin(th),'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end

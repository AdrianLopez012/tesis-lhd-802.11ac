% ver_flujo_paquetes.m v2 — CÓMO VIAJAN LOS PAQUETES según la ARQUITECTURA
% DOCUMENTADA de la tesis (anillo de fibra):
%   LHD --RADIO 802.11ac--> AP servidor --CAT 6--> SW ACCESO --ANILLO FO 1Gbps-->
%   NODO CORE --> pique --> WORKSTATION (estación de teleoperación)
% Colores según la leyenda del diagrama de la tesis:
%   FO monomodo = AMARILLO · F/UTP Cat 6 = AZUL · radio = naranja punteado
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
REC = readmatrix([TRB 'anim_recorrido.csv']);
AP  = readmatrix([TRB 'anim_aps.csv']);
PTH = readmatrix([TRB 'flujo_paths.csv']);
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};
i0 = 100; xL = REC(i0,2); yL = REC(i0,3); kAP = REC(i0,4);

% ---- geometría del backbone (de la fuente única de la mina) ----
X0 = 0; X1 = 51.96; Y0 = 0; Y1 = 134.85; XC = 25.98; YPQ = 160.85;
ring = [X0 Y0; X0 Y1; X1 Y1; X1 Y0; X0 Y0];              % anillo de FO por las galerías perimetrales
SW   = [X0 Y0; X0 Y1; X1 Y1; X1 Y0];                     % 4 switches de acceso (esquinas)
SWn  = {'SW-01','SW-02','SW-03','SW-04'};
CORE = [XC Y1];                                          % nodo core en el crucero superior
zCat = 2.8; zFO = 3.2; zTop = 16;

% ---- tramo RADIO: LHD -> AP (por las galerías, del cálculo Dijkstra) ----
r = PTH(1,:); r = r(~isnan(r)); radio = [r(1:2:end)' r(2:2:end)'];

% ---- tramo CAT6: AP -> switch de acceso más cercano ----
apP = AP(kAP,1:2);
[~,isw] = min(vecnorm(SW - apP, 2, 2));
sw = SW(isw,:);

% ---- tramo FO: por el anillo del SW al CORE (el lado más corto) ----
% parametrizar el anillo y caminar de sw a CORE
segR = diff(ring); lenR = vecnorm(segR,2,2); cumR = [0; cumsum(lenR)]; LR = cumR(end);
sDe = pos_en_anillo(sw, ring, cumR);
sA  = pos_en_anillo(CORE, ring, cumR);
d1 = mod(sA - sDe, LR); d2 = mod(sDe - sA, LR);
if d1 <= d2, ss = mod(linspace(sDe, sDe + d1, 24), LR);
else,        ss = mod(linspace(sDe, sDe - d2, 24), LR); end
fo = zeros(numel(ss),2);
for q = 1:numel(ss), fo(q,:) = punto_anillo(ss(q), ring, cumR); end

% ---- tramo CORE -> pique -> superficie ----
subida = [CORE; XC YPQ];

% ---- camino completo con alturas ----
P = [ [radio,  2.2*ones(size(radio,1),1)] ;
      [sw,     zCat] ;
      [fo(2:end,:), zFO*ones(size(fo,1)-1,1)] ;
      [subida(2:end,:), zFO*ones(size(subida,1)-1,1)] ;
      [XC YPQ zTop] ];
dP = [0; cumsum(vecnorm(diff(P),2,2))];
Ltot = dP(end);
posEn = @(s) interp1(dP, P, mod(s, Ltot));

fig = figure('Name','¿Cómo viajan los paquetes? — arquitectura anillo','Position',[20 20 1500 880], ...
    'Color',[0.04 0.04 0.06],'Renderer','opengl');
ax = axes(fig); hold(ax,'on'); set(ax,'Color',[0.05 0.05 0.07]);

% ---- mina ----
tr = stlread([TRB 'galeria_nv1640.stl']);
V = tr.Points; F = tr.ConnectivityList;
rng(1); vc = [0.46 0.40 0.34] + 0.10*(rand(size(V,1),1)-0.5);
patch(ax,'Faces',F,'Vertices',V,'FaceVertexCData',min(max(vc,0.15),0.62), ...
    'FaceColor','interp','EdgeColor','none','FaceLighting','gouraud','AmbientStrength',0.4);
trT = stlread([TRB 'galeria_techo.stl']);
patch(ax,'Faces',trT.ConnectivityList,'Vertices',trT.Points, ...
    'FaceColor',[0.5 0.44 0.38],'EdgeColor','none','FaceAlpha',0.12,'FaceLighting','gouraud');

% ---- ANILLO DE FO (amarillo, como el diagrama de la tesis) ----
plot3(ax, ring(:,1), ring(:,2), zFO*ones(size(ring,1),1), '-', 'Color',[0.98 0.80 0.15], 'LineWidth',3);
text(ax, X1+3, (Y0+Y1)/2, 6, 'ANILLO DE FO — 1 Gbps SM', 'FontSize',10.5,'Color',[0.98 0.80 0.15],'FontWeight','bold','Rotation',90,'HorizontalAlignment','center');
% switches de acceso
for q = 1:4
    plot3(ax, SW(q,1), SW(q,2), zFO, 's', 'MarkerSize',13, 'MarkerFaceColor',[0.9 0.9 0.95], 'MarkerEdgeColor',[0.2 0.3 0.6], 'LineWidth',1.5);
    text(ax, SW(q,1), SW(q,2), 6.0, SWn{q}, 'FontSize',9.5,'Color',[0.9 0.9 1],'FontWeight','bold','HorizontalAlignment','center');
end
% nodo core
plot3(ax, CORE(1), CORE(2), zFO, 'h', 'MarkerSize',18, 'MarkerFaceColor',[1 1 0.85], 'MarkerEdgeColor',[0.6 0.45 0.1], 'LineWidth',1.5);
text(ax, CORE(1), CORE(2), 6.4, 'NODO CORE', 'FontSize',10.5,'Color',[1 0.95 0.7],'FontWeight','bold','HorizontalAlignment','center');

% ---- Cat6 AP->SW (azul) y radio LHD->AP (naranja punteado) ----
plot3(ax, [apP(1) sw(1)], [apP(2) sw(2)], [zCat zCat], '-', 'Color',[0.25 0.55 1], 'LineWidth',2.5);
plot3(ax, radio(:,1), radio(:,2), 2.2*ones(size(radio,1),1), '--', 'Color',[1 0.62 0.12], 'LineWidth',2);
% subida core -> pique -> workstation
plot3(ax, [CORE(1) XC], [CORE(2) YPQ], [zFO zFO], '-', 'Color',[0.98 0.80 0.15], 'LineWidth',3);
plot3(ax, [XC XC], [YPQ YPQ], [zFO zTop], '-', 'Color',[0.98 0.80 0.15], 'LineWidth',3);
plot3(ax, XC, YPQ, zTop, 's', 'MarkerSize',17, 'MarkerFaceColor',[0.95 0.95 1], 'MarkerEdgeColor',[0.2 0.4 0.8], 'LineWidth',2);
text(ax, XC, YPQ, zTop+2.2, 'WORKSTATION — ESTACIÓN DE TELEOPERACIÓN (superficie)', ...
    'FontWeight','bold','FontSize',11,'Color',[0.85 0.92 1],'HorizontalAlignment','center');

% ---- APs y LHD ----
for k2 = 1:size(AP,1)
    if AP(k2,3)==1, col=[0.30 0.70 1.0]; else, col=[0.80 0.50 1.0]; end
    plot3(ax,AP(k2,1),AP(k2,2),3.0,'o','MarkerSize',7,'MarkerFaceColor',col,'MarkerEdgeColor','w');
    text(ax,AP(k2,1),AP(k2,2),4.6,IDS{k2},'FontWeight','bold','FontSize',9,'Color',col,'HorizontalAlignment','center');
end
plot3(ax,AP(kAP,1),AP(kAP,2),3.0,'o','MarkerSize',20,'Color',[1 0.6 0.15],'LineWidth',2.5);
g = hgtransform('Parent',ax);
caja(g,[-4.0 -1.4 0.4],[3.0 2.8 1.9],[0.92 0.68 0.06]); caja(g,[0.3 -1.3 0.4],[2.4 2.6 1.5],[0.92 0.68 0.06]);
caja(g,[-1.5 -0.7 0.6],[1.4 1.4 1.2],[0.22 0.22 0.24]); caja(g,[2.6 -1.6 0.1],[1.5 3.2 1.7],[0.22 0.22 0.24]);
caja(g,[-2.9 -1.1 2.3],[1.6 2.2 1.1],[0.15 0.30 0.45]);
for wx=[-3.2 1.4], for wy=[-1.5 1.5], rueda(g,wx,wy,0.7,1.0,[0.08 0.08 0.08]); end, end
set(g,'Matrix',makehgtform('translate',[xL yL 0],'zrotate',pi/2));

% ---- partículas ----
nV = 26; nT = 6; nC = 9;
sV = linspace(0, Ltot, nV+1); sV = sV(1:end-1);
sT = linspace(0, Ltot, nT+1); sT = sT(1:end-1) + 3;
sC = linspace(0, Ltot, nC+1); sC = sC(1:end-1);
pV = plot3(ax, nan(nV,1), nan(nV,1), nan(nV,1), 'o', 'MarkerSize',7,  'MarkerFaceColor',[1 0.55 0.05], 'MarkerEdgeColor','none');
pT = plot3(ax, nan(nT,1), nan(nT,1), nan(nT,1), 'o', 'MarkerSize',6,  'MarkerFaceColor',[0.45 0.80 1],  'MarkerEdgeColor','none');
pC = plot3(ax, nan(nC,1), nan(nC,1), nan(nC,1), 'd', 'MarkerSize',8,  'MarkerFaceColor',[0.30 0.95 0.45],'MarkerEdgeColor','none');
leyenda = { '\color[rgb]{1,0.55,0.05}\bullet VÍDEO 40 Mbps (AC\_VI) — sube    \color[rgb]{0.45,0.8,1}\bullet TELEMETRÍA (AC\_BE) — sube    \color[rgb]{0.3,0.95,0.45}\diamondsuit COMANDOS (AC\_VO) — bajan', ...
            '\color[rgb]{1,0.62,0.12}- - RADIO 802.11ac    \color[rgb]{0.25,0.55,1}— F/UTP CAT 6 (AP a SW)    \color[rgb]{0.98,0.8,0.15}— FO MONOMODO 1 Gbps (anillo)' };
annotation(fig,'textbox',[0.015 0.015 0.75 0.1],'String',leyenda,'EdgeColor','none','FontSize',11.5,'Color','w');
title(ax, sprintf('El viaje de los paquetes por la arquitectura de anillo — t = 100 s, AP servidor %s (pos\\_log NS-3)', IDS{kAP}), ...
    'FontSize',13.5,'Color','w');

axis(ax,'equal'); axis(ax,'off'); view(ax,-32,40);
xlim(ax,[-10 62]); ylim(ax,[-8 178]); zlim(ax,[0 22]);
light(ax,'Position',[26 80 100],'Style','infinite','Color',[0.65 0.65 0.7]);
light(ax,'Position',[90 -30 50],'Style','infinite','Color',[0.4 0.38 0.35]);
light(ax,'Position',[-40 40 60],'Style','infinite','Color',[0.35 0.32 0.30]);

% ---- animación (graba MP4 y deja la figura abierta) ----
vw = VideoWriter([TRB 'flujo_paquetes.mp4'],'MPEG-4'); vw.FrameRate = 20; vw.Quality = 92; open(vw);
vel = 1.8; NF = 480;
for f = 1:NF
    if ~ishandle(fig), break; end
    QV = posEn(sV + f*vel);
    QT = posEn(sT + f*vel*0.9);
    QC = posEn(Ltot - mod(sC + f*vel*1.1, Ltot));
    set(pV,'XData',QV(:,1),'YData',QV(:,2),'ZData',QV(:,3));
    set(pT,'XData',QT(:,1),'YData',QT(:,2),'ZData',QT(:,3));
    set(pC,'XData',QC(:,1),'YData',QC(:,2),'ZData',QC(:,3));
    drawnow;
    writeVideo(vw, getframe(fig));
end
close(vw);
rotate3d(fig,'on');
disp('FLUJO v2 OK — arquitectura de anillo; mp4 grabado; figura abierta.');

function s = pos_en_anillo(P, ring, cumR)
    mejor = 1e9; s = 0;
    for q = 1:size(ring,1)-1
        A = ring(q,:); B = ring(q+1,:);
        u = B-A; L = norm(u); u = u/L;
        t = min(max(dot(P-A,u),0),L);
        Q = A + u*t; d = norm(P-Q);
        if d < mejor, mejor = d; s = cumR(q) + t; end
    end
end
function Q = punto_anillo(s, ring, cumR)
    q = find(s >= cumR(1:end-1) & s <= cumR(2:end), 1);
    if isempty(q), q = size(ring,1)-1; end
    A = ring(q,:); B = ring(q+1,:);
    f = (s - cumR(q)) / (cumR(q+1) - cumR(q));
    Q = A + f*(B-A);
end
function caja(par,o,s,c)
    [X,Y,Z]=ndgrid([o(1) o(1)+s(1)],[o(2) o(2)+s(2)],[o(3) o(3)+s(3)]);
    v=[X(:) Y(:) Z(:)]; f=[1 2 4 3;5 6 8 7;1 2 6 5;3 4 8 7;1 3 7 5;2 4 8 6];
    patch('Vertices',v,'Faces',f,'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end
function rueda(par,cx,cy,r,w,c)
    [th,zz]=meshgrid(linspace(0,2*pi,16),[cy-w/2 cy+w/2]);
    surf(cx+r*cos(th),zz,r+r*sin(th),'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end

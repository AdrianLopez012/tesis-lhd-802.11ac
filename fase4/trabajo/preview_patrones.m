% preview_patrones.m — escena de mina con LHD + PATRONES DE RADIACIÓN de las
% antenas (lóbulos 3D reales calculados con Antenna Toolbox) en cada AP.
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
STL = [TRB 'galeria_nv1640.stl'];
REC = readmatrix([TRB 'anim_recorrido.csv']);
AP  = readmatrix([TRB 'anim_aps.csv']);
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};
f0 = 5e9;

% ===== calcular patrones de radiación (una vez) =====
% Hawk: antena helicoidal RCP (11 dBi) ; Cardinal: omni EPNT-7 (7.5 dBi)
% LHD: HELI-40 (4.8 dBi). Usamos hélices/dipolos representativos.
helHawk = helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115);   % ~11 dBi
[pH,azH,elH] = pattern(helHawk,f0);
omni = dipole('Length',0.028,'Width',0.001);                                   % omni vertical
[pC,azC,elC] = pattern(omni,f0);
helLHD = helix('Radius',0.0091,'Width',0.0016,'Turns',5,'Spacing',0.0115);     % ~4.8 dBi
[pL,azL,elL] = pattern(helLHD,f0);

fig = figure('Position',[30 30 1500 900],'Color',[0.04 0.04 0.06],'Renderer','opengl');
ax = axes(fig); hold(ax,'on'); set(ax,'Color',[0.06 0.06 0.08]);
tr = stlread(STL);
trisurf(tr,'FaceColor',[0.52 0.47 0.42],'EdgeColor','none','FaceAlpha',1.0, ...
    'FaceLighting','gouraud','AmbientStrength',0.4,'DiffuseStrength',0.9,'Parent',ax);

% dibuja el lóbulo de un patrón centrado en (cx,cy,cz), escala en metros
function dibujarLobulo(ax, pat, az, el, cx, cy, cz, esc, cmap)
    P = pat - max(pat(:)); R = 10.^(P/20); R(R<0.06)=0.06;
    [AZ,EL] = meshgrid(deg2rad(az), deg2rad(el));
    Rm = R*esc;
    X = Rm.*cos(EL).*cos(AZ)+cx; Y = Rm.*cos(EL).*sin(AZ)+cy; Z = Rm.*sin(EL)+cz;
    surf(ax,X,Y,Z,pat,'EdgeColor','none','FaceAlpha',0.45,'FaceLighting','none');
end

% patrones en cada AP (Hawk azulado, Cardinal morado)
for k=1:size(AP,1)
    if AP(k,3)==1
        dibujarLobulo(ax, pH,azH,elH, AP(k,1),AP(k,2),3.0, 5, 'a');
        col=[0.20 0.65 1.0];
    else
        dibujarLobulo(ax, pC,azC,elC, AP(k,1),AP(k,2),3.0, 4.5, 'b');
        col=[0.75 0.45 1.0];
    end
    plot3(ax,AP(k,1),AP(k,2),3.0,'o','MarkerSize',7,'MarkerFaceColor',col,'MarkerEdgeColor','w');
    text(ax,AP(k,1),AP(k,2),5.0,IDS{k},'FontWeight','bold','FontSize',9,'Color',col,'HorizontalAlignment','center');
end
colormap(ax, turbo);

% ===== LHD con SU patrón de antena =====
i0=90; x=REC(i0,2); y=REC(i0,3);
g = hgtransform('Parent',ax);
grisO=[0.90 0.66 0.08]; grisD=[0.25 0.25 0.28]; negro=[0.10 0.10 0.10];
caja(g,[-4.0 -1.4 0.4],[3.0 2.8 1.9],grisO); caja(g,[0.3 -1.3 0.4],[2.4 2.6 1.5],grisO);
caja(g,[-1.5 -0.7 0.6],[1.4 1.4 1.2],grisD); caja(g,[2.6 -1.6 0.1],[1.5 3.2 1.7],grisD);
caja(g,[-2.9 -1.1 2.3],[1.6 2.2 1.1],[0.15 0.30 0.45]);
for wx=[-3.2 1.4], for wy=[-1.5 1.5], rueda(g,wx,wy,0.7,1.0,negro); end, end
set(g,'Matrix',makehgtform('translate',[x y 0],'zrotate',pi/2));
dibujarLobulo(ax, pL,azL,elL, x,y,4.0, 6, 'c');   % patrón del LHD sobre el vehículo

axis(ax,'equal'); axis(ax,'off'); view(ax,-28,42);
% vista amplia: ver TODA la red irradiando
xlim(ax,[-6 60]); ylim(ax,[-8 172]); zlim(ax,[0 20]);
light(ax,'Position',[26 80 80],'Style','infinite','Color',[0.75 0.75 0.8]);
light(ax,'Position',[26 40 40],'Style','infinite','Color',[0.5 0.5 0.55]);
title(ax,'Patrones de radiación de la red: 12 AP irradiando en la zona de producción','FontSize',15,'Color','w');
exportgraphics(fig,[TRB 'preview_patrones.png'],'Resolution',150);
fprintf('PREVIEW PATRONES OK\n'); exit;

function caja(par,o,s,c)
    [X,Y,Z]=ndgrid([o(1) o(1)+s(1)],[o(2) o(2)+s(2)],[o(3) o(3)+s(3)]);
    v=[X(:) Y(:) Z(:)]; f=[1 2 4 3;5 6 8 7;1 2 6 5;3 4 8 7;1 3 7 5;2 4 8 6];
    patch('Vertices',v,'Faces',f,'FaceColor',c,'EdgeColor',[0.1 0.1 0.1],'LineWidth',0.4,'FaceLighting','gouraud','AmbientStrength',0.3,'Parent',par);
end
function rueda(par,cx,cy,r,w,c)
    [th,zz]=meshgrid(linspace(0,2*pi,16),[cy-w/2 cy+w/2]);
    surf(cx+r*cos(th),zz,r+r*sin(th),'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end

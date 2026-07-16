% anim_lhd_realista.m v3 — animación con:
%  · geometría de uniones limpias (STL v3)
%  · enlace LHD->AP siguiendo LAS GALERÍAS (anim_enlace.csv, Dijkstra)
%  · patrones de radiación en los 12 AP (Antenna Toolbox) y lóbulo en el LHD
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
STL = [TRB 'galeria_nv1640.stl'];
REC = readmatrix([TRB 'anim_recorrido.csv']);
ENL = readmatrix([TRB 'anim_enlace.csv']);
AP  = readmatrix([TRB 'anim_aps.csv']);
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};
f0 = 5e9;

% ---- patrones de antena (una vez) ----
helHawk = helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115);
[pH,azH,elH] = pattern(helHawk,f0);
omni = dipole('Length',0.028,'Width',0.001);
[pC,azC,elC] = pattern(omni,f0);
helLHD = helix('Radius',0.0091,'Width',0.0016,'Turns',5,'Spacing',0.0115);
[pL,azL,elL] = pattern(helLHD,f0);

fig = figure('Position',[30 30 1440 810],'Color',[0.04 0.04 0.06],'Renderer','opengl');
ax = axes(fig); hold(ax,'on'); set(ax,'Color',[0.06 0.06 0.08]);

% ---- galería con textura de roca ----
tr = stlread(STL);
V = tr.Points; F = tr.ConnectivityList;
rng(1); base=[0.44 0.38 0.32];
vc = base + 0.10*(rand(size(V,1),1)-0.5); vc = min(max(vc,0.15),0.62);
patch(ax,'Faces',F,'Vertices',V,'FaceVertexCData',vc,'FaceColor','interp', ...
    'EdgeColor','none','FaceLighting','gouraud','AmbientStrength',0.35, ...
    'DiffuseStrength',0.9,'SpecularStrength',0.2);
% techo en arco FANTASMA (semitransparente): forma de herradura sin tapar el interior
trT = stlread([TRB 'galeria_techo.stl']);
patch(ax,'Faces',trT.ConnectivityList,'Vertices',trT.Points, ...
    'FaceColor',[0.50 0.44 0.38],'EdgeColor','none','FaceAlpha',0.16, ...
    'FaceLighting','gouraud','AmbientStrength',0.4);

% ---- lóbulos de los 12 AP ----
for k=1:size(AP,1)
    if AP(k,3)==1
        lobulo(ax, pH,azH,elH, AP(k,1),AP(k,2),3.0, 4.2, 0.35);
        col=[0.30 0.70 1.0];
    else
        lobulo(ax, pC,azC,elC, AP(k,1),AP(k,2),3.0, 3.6, 0.35);
        col=[0.80 0.50 1.0];
    end
    plot3(ax,AP(k,1),AP(k,2),3.0,'o','MarkerSize',8,'MarkerFaceColor',col,'MarkerEdgeColor','w','LineWidth',1);
    text(ax,AP(k,1),AP(k,2),4.8,IDS{k},'FontWeight','bold','FontSize',10,'Color',col,'HorizontalAlignment','center');
end
colormap(ax, turbo);

% ---- LHD con su lóbulo (dentro del grupo transformable) ----
g = hgtransform('Parent',ax);
grisO=[0.92 0.68 0.06]; grisD=[0.22 0.22 0.24]; negro=[0.08 0.08 0.08];
caja(g,[-4.0 -1.4 0.4],[3.0 2.8 1.9],grisO); caja(g,[0.3 -1.3 0.4],[2.4 2.6 1.5],grisO);
caja(g,[-1.5 -0.7 0.6],[1.4 1.4 1.2],grisD); caja(g,[2.6 -1.6 0.1],[1.5 3.2 1.7],grisD);
caja(g,[-2.9 -1.1 2.3],[1.6 2.2 1.1],[0.15 0.30 0.45]);
for wx=[-3.2 1.4], for wy=[-1.5 1.5], rueda(g,wx,wy,0.7,1.0,negro); end, end
% lóbulo del LHD sobre la cabina (viaja con el vehículo)
PL = pL - max(pL(:)); RL = 10.^(PL/20); RL(RL<0.06)=0.06;
[AZL,ELL] = meshgrid(deg2rad(azL), deg2rad(elL));
RmL = RL*2.6;
XL = RmL.*cos(ELL).*cos(AZL); YL = RmL.*cos(ELL).*sin(AZL); ZL = RmL.*sin(ELL)+3.6;
surf(XL,YL,ZL,PL,'EdgeColor','none','FaceAlpha',0.4,'FaceLighting','none','Parent',g);

% ---- enlace por las galerías (polilínea dinámica) ----
hLink = plot3(ax,[0 0],[0 0],[2.2 2.2],'-','Color',[1 0.62 0.12],'LineWidth',3.2,'Visible','off');
hInfo = annotation(fig,'textbox',[0.02 0.93 0.96 0.06],'String','','EdgeColor','none', ...
    'Color','w','FontSize',15,'FontWeight','bold','HorizontalAlignment','center','VerticalAlignment','middle');

axis(ax,'equal'); axis(ax,'off');
light(ax,'Position',[26 80 120],'Style','infinite','Color',[0.6 0.6 0.65]);
light(ax,'Position',[-40 40 60],'Style','infinite','Color',[0.35 0.32 0.30]);
light(ax,'Position',[90 -30 50],'Style','infinite','Color',[0.35 0.33 0.30]);
light(ax,'Position',[26 200 60],'Style','infinite','Color',[0.25 0.25 0.28]);
lfoco = light(ax,'Position',[0 0 15],'Style','local','Color',[1 0.95 0.8]);

vw = VideoWriter([TRB 'lhd_recorrido_3d.mp4'],'MPEG-4'); vw.FrameRate=14; vw.Quality=95; open(vw);
N = size(REC,1); ang = 0;
for i=1:N
    x=REC(i,2); y=REC(i,3); k=REC(i,4); rssi=REC(i,5);
    if i<N, ang=atan2(REC(i+1,3)-y,REC(i+1,2)-x); end
    set(g,'Matrix',makehgtform('translate',[x y 0],'zrotate',ang));
    set(ax,'XLim',[x-22 x+22],'YLim',[y-22 y+22],'ZLim',[0 13]);
    view(ax,-35,36);
    set(lfoco,'Position',[x y 15]);
    if k>=1
        % ruta del enlace: LHD -> puntos de galería -> AP
        pts = ENL(i,3:end); pts = pts(~isnan(pts));
        px = [x pts(1:2:end) AP(k,1)];
        py = [y pts(2:2:end) AP(k,2)];
        pz = [2.2, 2.2*ones(1,numel(pts)/2), 3.0];
        set(hLink,'XData',px,'YData',py,'ZData',pz,'Visible','on');
        set(hInfo,'String',sprintf('LHD teleoperado — NV1640   |   t = %.0f s   |   AP servidor: %s   |   RSSI: %.0f dBm   |   la señal viaja por las galerías', REC(i,1), IDS{k}, rssi));
    end
    drawnow; writeVideo(vw,getframe(fig));
end
close(vw);
fprintf('VIDEO v3 OK: %d frames\n', N);
exit;

function caja(par,o,s,c)
    [X,Y,Z]=ndgrid([o(1) o(1)+s(1)],[o(2) o(2)+s(2)],[o(3) o(3)+s(3)]);
    v=[X(:) Y(:) Z(:)]; f=[1 2 4 3;5 6 8 7;1 2 6 5;3 4 8 7;1 3 7 5;2 4 8 6];
    patch('Vertices',v,'Faces',f,'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','AmbientStrength',0.3,'Parent',par);
end
function rueda(par,cx,cy,r,w,c)
    [th,zz]=meshgrid(linspace(0,2*pi,16),[cy-w/2 cy+w/2]);
    surf(cx+r*cos(th),zz,r+r*sin(th),'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end
function h = lobulo(ax, pat, az, el, cx, cy, cz, esc, alfa)
    P = pat - max(pat(:)); R = 10.^(P/20); R(R<0.06)=0.06;
    [AZ,EL] = meshgrid(deg2rad(az), deg2rad(el));
    Rm = R*esc;
    X = Rm.*cos(EL).*cos(AZ)+cx; Y = Rm.*cos(EL).*sin(AZ)+cy; Z = Rm.*sin(EL)+cz;
    h = surf(ax,X,Y,Z,pat,'EdgeColor','none','FaceAlpha',alfa,'FaceLighting','none');
end


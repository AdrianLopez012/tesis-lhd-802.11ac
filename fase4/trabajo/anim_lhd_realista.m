% anim_lhd_realista.m — Animación 3D del LHD recorriendo la mina (datos NS-3).
% Mina de corte (sin techo, se ve el interior) + LHD articulado + cámara que
% SIGUE al vehículo de cerca (vista de simulador). Guarda MP4.
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
STL = [TRB 'galeria_nv1640.stl'];
REC = readmatrix([TRB 'anim_recorrido.csv']);
AP  = readmatrix([TRB 'anim_aps.csv']);
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};

fig = figure('Position',[30 30 1440 810],'Color',[0.04 0.04 0.06],'Renderer','opengl');
ax = axes(fig); hold(ax,'on'); set(ax,'Color',[0.06 0.06 0.08]);

tr = stlread(STL);
trisurf(tr,'FaceColor',[0.42 0.37 0.32],'EdgeColor','none','FaceAlpha',1.0, ...
    'FaceLighting','gouraud','AmbientStrength',0.25,'DiffuseStrength',0.9, ...
    'SpecularStrength',0.15,'Parent',ax);

hApTxt = gobjects(size(AP,1),1);
for k=1:size(AP,1)
    if AP(k,3)==1, col=[0.20 0.65 1.0]; else, col=[0.75 0.45 1.0]; end
    plot3(ax,AP(k,1),AP(k,2),3.0,'o','MarkerSize',9,'MarkerFaceColor',col,'MarkerEdgeColor','w','LineWidth',1);
    hApTxt(k)=text(ax,AP(k,1),AP(k,2),4.3,IDS{k},'FontWeight','bold','FontSize',10,'Color',col,'HorizontalAlignment','center');
end

% --- LHD articulado ---
g = hgtransform('Parent',ax);
grisO=[0.90 0.66 0.08]; grisD=[0.25 0.25 0.28]; negro=[0.10 0.10 0.10];
caja(g,[-4.0 -1.4 0.4],[3.0 2.8 1.9],grisO);
caja(g,[ 0.3 -1.3 0.4],[2.4 2.6 1.5],grisO);
caja(g,[-1.5 -0.7 0.6],[1.4 1.4 1.2],grisD);
caja(g,[ 2.6 -1.6 0.1],[1.5 3.2 1.7],grisD);
caja(g,[-2.9 -1.1 2.3],[1.6 2.2 1.1],[0.15 0.30 0.45]);
for wx=[-3.2 1.4]
  for wy=[-1.5 1.5]
    rueda(g,wx,wy,0.7,1.0,negro);
  end
end

hHalo = plot3(ax,AP(1,1),AP(1,2),3.0,'o','MarkerSize',26,'Color',[1 0.5 0.1],'LineWidth',3,'Visible','off');
hLink = plot3(ax,[0 0],[0 0],[2.5 3.0],'-','Color',[1 0.6 0.15],'LineWidth',2.5,'Visible','off');
% panel de texto fijo (arriba, en coords de figura)
hInfo = annotation(fig,'textbox',[0.02 0.93 0.96 0.06],'String','','EdgeColor','none',...
    'Color','w','FontSize',15,'FontWeight','bold','HorizontalAlignment','center','VerticalAlignment','middle');

axis(ax,'equal'); axis(ax,'off');
lgen = light(ax,'Position',[0 0 60],'Style','infinite','Color',[0.55 0.55 0.6]);
lfoco = light(ax,'Position',[0 0 15],'Style','local','Color',[1 0.95 0.8]);

vw = VideoWriter([TRB 'lhd_recorrido_3d.mp4'],'MPEG-4'); vw.FrameRate=14; vw.Quality=95; open(vw);
N = size(REC,1);
for i=1:N
    x=REC(i,2); y=REC(i,3); k=REC(i,4); rssi=REC(i,5);
    if i<N, ang=atan2(REC(i+1,3)-y,REC(i+1,2)-x); else, ang=ang; end
    set(g,'Matrix',makehgtform('translate',[x y 0],'zrotate',ang));
    % camara sigue al LHD
    set(ax,'XLim',[x-20 x+20],'YLim',[y-20 y+20],'ZLim',[0 12]);
    view(ax,-35,34);
    set(lfoco,'Position',[x y 15]);
    if k>=1
        set(hHalo,'XData',AP(k,1),'YData',AP(k,2),'Visible','on');
        set(hLink,'XData',[x AP(k,1)],'YData',[y AP(k,2)],'ZData',[2.5 3.0],'Visible','on');
        set(hInfo,'String',sprintf('LHD teleoperado en el nivel NV1640    |    t = %.0f s    |    AP servidor: %s    |    RSSI: %.0f dBm', REC(i,1), IDS{k}, rssi));
    end
    drawnow; writeVideo(vw,getframe(fig));
end
close(vw);
fprintf('VIDEO OK: %d frames\n', N);
exit;

function caja(par,o,s,c)
    [X,Y,Z]=ndgrid([o(1) o(1)+s(1)],[o(2) o(2)+s(2)],[o(3) o(3)+s(3)]);
    v=[X(:) Y(:) Z(:)]; f=[1 2 4 3;5 6 8 7;1 2 6 5;3 4 8 7;1 3 7 5;2 4 8 6];
    patch('Vertices',v,'Faces',f,'FaceColor',c,'EdgeColor',[0.1 0.1 0.1],'LineWidth',0.4,...
        'FaceLighting','gouraud','AmbientStrength',0.3,'Parent',par);
end
function rueda(par,cx,cy,r,w,c)
    [th,zz]=meshgrid(linspace(0,2*pi,16),[cy-w/2 cy+w/2]);
    xx=cx+r*cos(th); zzz=r+r*sin(th);
    surf(xx,zz,zzz,'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end

% preview_lhd.m — render estatico de 1 frame para validar el LHD y la mina.
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
STL = [TRB 'galeria_nv1640.stl'];
REC = readmatrix([TRB 'anim_recorrido.csv']);
AP  = readmatrix([TRB 'anim_aps.csv']);
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};

fig = figure('Position',[30 30 1500 900],'Color',[0.05 0.05 0.07],'Renderer','opengl');
ax = axes(fig); hold(ax,'on'); set(ax,'Color',[0.08 0.08 0.10]);

tr = stlread(STL);
trisurf(tr,'FaceColor',[0.42 0.37 0.32],'EdgeColor','none','FaceAlpha',1.0, ...
    'FaceLighting','gouraud','AmbientStrength',0.25,'DiffuseStrength',0.9, ...
    'SpecularStrength',0.15,'Parent',ax);

for k=1:size(AP,1)
    if AP(k,3)==1, col=[0.20 0.65 1.0]; else, col=[0.75 0.45 1.0]; end
    plot3(ax,AP(k,1),AP(k,2),3.2,'o','MarkerSize',9,'MarkerFaceColor',col,'MarkerEdgeColor','w','LineWidth',1);
    text(ax,AP(k,1),AP(k,2),4.4,IDS{k},'FontWeight','bold','FontSize',9,'Color',col,'HorizontalAlignment','center');
end
plot3(ax,REC(:,2),REC(:,3),0.25*ones(size(REC,1),1),'-','Color',[0.3 0.3 0.33],'LineWidth',1);

i0=90; x=REC(i0,2); y=REC(i0,3);
g = hgtransform('Parent',ax);
grisO=[0.90 0.66 0.08]; grisD=[0.25 0.25 0.28]; negro=[0.10 0.10 0.10];
% LHD articulado, ancho 3 m (cabe en galeria de 4 m), largo ~9 m
caja(g,[-4.0 -1.4 0.4],[3.0 2.8 1.9],grisO);   % chasis trasero (motor)
caja(g,[ 0.3 -1.3 0.4],[2.4 2.6 1.5],grisO);   % chasis delantero
caja(g,[-1.5 -0.7 0.6],[1.4 1.4 1.2],grisD);   % junta articulada
caja(g,[ 2.6 -1.6 0.1],[1.5 3.2 1.7],grisD);   % cuchara
caja(g,[-2.9 -1.1 2.3],[1.6 2.2 1.1],[0.15 0.30 0.45]); % cabina
for wx=[-3.2 1.4]
  for wy=[-1.5 1.5]
    rueda(g,wx,wy,0.7,1.0,negro);
  end
end
set(g,'Matrix',makehgtform('translate',[x y 0],'zrotate',pi/2));

k=REC(i0,4);
if k>=1
    plot3(ax,AP(k,1),AP(k,2),3.2,'o','MarkerSize',24,'Color',[1 0.5 0.1],'LineWidth',2.5);
    plot3(ax,[x AP(k,1)],[y AP(k,2)],[2.5 3.2],'-','Color',[1 0.6 0.15],'LineWidth',2);
end
title(ax,'LHD teleoperado en el nivel NV1640 - vista de prueba','FontSize',15,'Color','w');

axis(ax,'equal'); axis(ax,'off');
% CAMARA CERCANA que sigue al vehiculo (vista de simulador)
view(ax,-35,32);
xlim(ax,[x-22 x+22]); ylim(ax,[y-22 y+22]); zlim(ax,[0 12]);
light(ax,'Position',[x+10 y+20 40],'Style','infinite','Color',[0.6 0.6 0.65]);
light(ax,'Position',[x y 15],'Style','local','Color',[1 0.95 0.8]);

exportgraphics(fig,[TRB 'preview_lhd.png'],'Resolution',150);
fprintf('PREVIEW OK\n');
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

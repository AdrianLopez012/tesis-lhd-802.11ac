% mina_realista.m — Mina 3D MÁS REALISTA: textura de roca procedural en las
% paredes, piso irregular, iluminación tipo interior mina (oscuro + focos).
TRB='C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
STL=[TRB 'galeria_nv1640.stl'];
REC=readmatrix([TRB 'anim_recorrido.csv']);
AP =readmatrix([TRB 'anim_aps.csv']);
IDS={'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};

fig=figure('Position',[20 20 1560 900],'Color',[0.02 0.02 0.03],'Renderer','opengl');
ax=axes(fig); hold(ax,'on'); set(ax,'Color',[0.02 0.02 0.03]);

% --- galería con textura de roca procedural ---
tr = stlread(STL);
V = tr.Points; F = tr.ConnectivityList;
% color por vértice: roca marrón con variación (ruido) => textura
rng(1);
base = [0.40 0.34 0.28];
noise = 0.12*(rand(size(V,1),1)-0.5);            % variación de tono (grano de roca)
vc = base + noise;   vc = min(max(vc,0.12),0.62);
p = patch(ax,'Faces',F,'Vertices',V,'FaceVertexCData',vc,...
    'FaceColor','interp','EdgeColor','none',...
    'FaceLighting','gouraud','AmbientStrength',0.18,...
    'DiffuseStrength',0.95,'SpecularStrength',0.25,'SpecularExponent',8);

% --- polvo/niebla atmosférica (planos semitransparentes tenues) ---
for zz=[6 10]
    surf(ax,[-8 62;-8 62],[-8 -8;172 172],zz*ones(2),...
        'FaceColor',[0.15 0.14 0.13],'FaceAlpha',0.04,'EdgeColor','none');
end

% --- AP como luminarias (sin luz individual: excede el límite de 8) ---
for k=1:size(AP,1)
    if AP(k,3)==1, col=[0.35 0.75 1.0]; else, col=[0.85 0.55 1.0]; end
    plot3(ax,AP(k,1),AP(k,2),3.4,'o','MarkerSize',8,'MarkerFaceColor',col,'MarkerEdgeColor','w','LineWidth',1);
    text(ax,AP(k,1),AP(k,2),4.6,IDS{k},'FontWeight','bold','FontSize',8,'Color',col,'HorizontalAlignment','center');
end
plot3(ax,REC(:,2),REC(:,3),0.15*ones(size(REC,1),1),'-','Color',[0.35 0.30 0.22],'LineWidth',1.2);

% --- LHD con faros ---
i0=90; x=REC(i0,2); y=REC(i0,3);
g=hgtransform('Parent',ax);
grisO=[0.92 0.68 0.06]; grisD=[0.22 0.22 0.24]; negro=[0.08 0.08 0.08];
caja(g,[-4.0 -1.4 0.3],[3.0 2.8 1.9],grisO); caja(g,[0.3 -1.3 0.3],[2.4 2.6 1.5],grisO);
caja(g,[-1.5 -0.7 0.5],[1.4 1.4 1.2],grisD); caja(g,[2.6 -1.6 0.05],[1.5 3.2 1.7],grisD);
caja(g,[-2.9 -1.1 2.2],[1.6 2.2 1.1],[0.12 0.25 0.40]);
for wx=[-3.2 1.4], for wy=[-1.5 1.5], rueda(g,wx,wy,0.7,1.0,negro); end, end
set(g,'Matrix',makehgtform('translate',[x y 0],'zrotate',pi/2));
% faros del LHD (dos luces potentes hacia adelante)
plot3(ax,x+3.8,y,1.4,'o','MarkerSize',9,'MarkerFaceColor',[1 1 0.75],'MarkerEdgeColor','none');
light(ax,'Position',[x+8 y 3],'Style','local','Color',[1 0.95 0.75]);

% (sin línea de enlace recto: la señal NO atraviesa la roca; el enlace real
%  se muestra en el video y en las láminas de rayos, siguiendo las galerías)

axis(ax,'equal'); axis(ax,'off'); view(ax,-32,40);
xlim(ax,[-8 62]); ylim(ax,[-8 172]); zlim(ax,[0 18]);
% iluminación de mina: cenital principal + relleno lateral cálido + foco al LHD
light(ax,'Position',[26 80 120],'Style','infinite','Color',[0.55 0.55 0.60]);
light(ax,'Position',[-40 40 50],'Style','infinite','Color',[0.35 0.32 0.28]);
light(ax,'Position',[80 120 50],'Style','infinite','Color',[0.30 0.30 0.35]);
material(ax,'dull');
exportgraphics(fig,[TRB 'preview_mina_realista.png'],'Resolution',150,'BackgroundColor',[0.02 0.02 0.03]);
fprintf('MINA REALISTA OK\n'); exit;

function caja(par,o,s,c)
    [X,Y,Z]=ndgrid([o(1) o(1)+s(1)],[o(2) o(2)+s(2)],[o(3) o(3)+s(3)]);
    v=[X(:) Y(:) Z(:)]; f=[1 2 4 3;5 6 8 7;1 2 6 5;3 4 8 7;1 3 7 5;2 4 8 6];
    patch('Vertices',v,'Faces',f,'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','AmbientStrength',0.25,'SpecularStrength',0.4,'Parent',par);
end
function rueda(par,cx,cy,r,w,c)
    [th,zz]=meshgrid(linspace(0,2*pi,18),[cy-w/2 cy+w/2]);
    surf(cx+r*cos(th),zz,r+r*sin(th),'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
end

function ver_mesh_vivo()
% ver_mesh_vivo — LA MALLA EN ACCIÓN mientras el LHD recorre la mina:
%   · halos en los AP CANDIDATOS (top-3 por RSSI de ruta, modelo two-slope tesis)
%   · enlace FÍSICO al AP ASOCIADO (dato real NS-3) siguiendo las galerías
%   · capa LÓGICA de malla: la ruta AP->...->CORE se RE-ENRUTA sola al cambiar
%     de AP (selección por costo de enlace, comportamiento tipo InstaMesh)
% Graba mesh_vivo.mp4 y deja la figura abierta.
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
REC = readmatrix([TRB 'anim_recorrido.csv']);
ENL = readmatrix([TRB 'anim_enlace.csv']);
RS  = readmatrix([TRB 'mesh_rssi.csv']);
RUT = readmatrix([TRB 'mesh_rutas.csv']);
AP  = readmatrix([TRB 'anim_aps.csv']);
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};
NA = size(AP,1); CORE = [25.98 134.85];

fig = figure('Name','Mesh en vivo — NV1640','Position',[15 15 1500 880], ...
    'Color',[0.04 0.04 0.06],'Renderer','opengl');
ax = axes(fig); hold(ax,'on'); set(ax,'Color',[0.05 0.05 0.07]);

tr = stlread([TRB 'galeria_nv1640.stl']);
rng(1); vc = [0.46 0.40 0.34] + 0.10*(rand(size(tr.Points,1),1)-0.5);
patch(ax,'Faces',tr.ConnectivityList,'Vertices',tr.Points,'FaceVertexCData',min(max(vc,0.15),0.62), ...
    'FaceColor','interp','EdgeColor','none','FaceLighting','gouraud','AmbientStrength',0.42);
trT = stlread([TRB 'galeria_techo.stl']);
patch(ax,'Faces',trT.ConnectivityList,'Vertices',trT.Points, ...
    'FaceColor',[0.5 0.44 0.38],'EdgeColor','none','FaceAlpha',0.10,'FaceLighting','gouraud');

for q = 1:NA
    if AP(q,3)==1, col=[0.30 0.70 1.0]; else, col=[0.80 0.50 1.0]; end
    plot3(ax,AP(q,1),AP(q,2),3.0,'o','MarkerSize',8,'MarkerFaceColor',col,'MarkerEdgeColor','w');
    text(ax,AP(q,1),AP(q,2),4.8,IDS{q},'FontWeight','bold','FontSize',10,'Color',col,'HorizontalAlignment','center');
end
plot3(ax,CORE(1),CORE(2),3.2,'h','MarkerSize',17,'MarkerFaceColor',[1 1 0.85],'MarkerEdgeColor',[0.6 0.45 0.1],'LineWidth',1.5);
text(ax,CORE(1),CORE(2),6.4,'CORE','FontSize',11,'Color',[1 0.95 0.7],'FontWeight','bold','HorizontalAlignment','center');

g = hgtransform('Parent',ax);
caja(g,[-4.0 -1.4 0.4],[3.0 2.8 1.9],[0.92 0.68 0.06]); caja(g,[0.3 -1.3 0.4],[2.4 2.6 1.5],[0.92 0.68 0.06]);
caja(g,[-1.5 -0.7 0.6],[1.4 1.4 1.2],[0.22 0.22 0.24]); caja(g,[2.6 -1.6 0.1],[1.5 3.2 1.7],[0.22 0.22 0.24]);
caja(g,[-2.9 -1.1 2.3],[1.6 2.2 1.1],[0.15 0.30 0.45]);
for wx=[-3.2 1.4], for wy=[-1.5 1.5], rueda(g,wx,wy,0.7,1.0,[0.08 0.08 0.08]); end, end

hHalo = gobjects(3,1);
for h2 = 1:3, hHalo(h2) = plot3(ax,nan,nan,3.0,'o','MarkerSize',22,'LineWidth',2,'Visible','off'); end
hAssoc = plot3(ax,nan,nan,nan,'-','Color',[1 0.62 0.12],'LineWidth',3.4,'Visible','off');
hMesh  = plot3(ax,nan,nan,nan,'--','Color',[0.15 0.9 0.85],'LineWidth',2.4,'Visible','off');
hInfo = annotation(fig,'textbox',[0.02 0.9 0.96 0.09],'String','','EdgeColor','none', ...
    'Color','w','FontSize',13,'FontWeight','bold','HorizontalAlignment','center','VerticalAlignment','middle');
annotation(fig,'textbox',[0.015 0.015 0.9 0.06],'EdgeColor','none','FontSize',11,'Color','w','String', ...
    ['\color[rgb]{1,0.62,0.12}— enlace RADIO al AP asociado (dato NS-3, por las galerías)   ' ...
     '\color[rgb]{0.15,0.9,0.85}- - ruta LÓGICA por la malla al core (se re-enruta sola)   ' ...
     '\color[rgb]{0.9,0.9,0.4}\bullet halos = AP candidatos (top-3 RSSI)']);

axis(ax,'equal'); axis(ax,'off'); view(ax,-30,42);
xlim(ax,[-10 62]); ylim(ax,[-8 172]); zlim(ax,[0 18]);
light(ax,'Position',[26 80 100],'Style','infinite','Color',[0.65 0.65 0.7]);
light(ax,'Position',[90 -30 50],'Style','infinite','Color',[0.4 0.38 0.35]);
light(ax,'Position',[-40 40 60],'Style','infinite','Color',[0.35 0.32 0.30]);

vw = VideoWriter([TRB 'mesh_vivo.mp4'],'MPEG-4'); vw.FrameRate = 14; vw.Quality = 92; open(vw);
N = size(REC,1); ang = 0;
for f = 1:N
    if ~ishandle(fig), break; end
    x=REC(f,2); y=REC(f,3); a0=REC(f,4);
    if f<N, ang=atan2(REC(f+1,3)-y,REC(f+1,2)-x); end
    set(g,'Matrix',makehgtform('translate',[x y 0],'zrotate',ang));
    % candidatos top-3 por RSSI
    [rsv, orden] = sort(RS(f,:), 'descend');
    for h2 = 1:3
        q = orden(h2);
        col = [0.9 0.9 0.4]; if h2==1, col = [0.4 1 0.5]; end
        set(hHalo(h2),'XData',AP(q,1),'YData',AP(q,2),'Color',col,'Visible','on');
    end
    % enlace fisico al asociado (por galerias)
    if a0 >= 1
        pts = ENL(f,3:end); pts = pts(~isnan(pts));
        px2 = [x pts(1:2:end) AP(a0,1)]; py2 = [y pts(2:2:end) AP(a0,2)];
        set(hAssoc,'XData',px2,'YData',py2,'ZData',[2.2 2.2*ones(1,numel(pts)/2) 3.0],'Visible','on');
        % ruta logica de malla
        rr = RUT(f,:); rr = rr(~isnan(rr));
        mx = [AP(rr,1)' CORE(1)]; my = [AP(rr,2)' CORE(2)];
        set(hMesh,'XData',mx,'YData',my,'ZData',5.5*ones(1,numel(mx)),'Visible','on');
        cadena = strjoin(IDS(rr), ' > ');
        set(hInfo,'String',sprintf('t = %.0f s   |   asociado: %s (%.0f dBm)   |   candidatos: %s (%.0f) · %s (%.0f)   |   malla: %s > CORE', ...
            REC(f,1), IDS{a0}, RS(f,a0), IDS{orden(1)}, rsv(1), IDS{orden(2)}, rsv(2), cadena));
    end
    drawnow; writeVideo(vw, getframe(fig));
end
close(vw);
rotate3d(fig,'on');
disp('MESH VIVO OK — mp4 grabado; figura abierta.');

    function caja(par,o,s,c)
        [X,Y,Z]=ndgrid([o(1) o(1)+s(1)],[o(2) o(2)+s(2)],[o(3) o(3)+s(3)]);
        v=[X(:) Y(:) Z(:)]; ff=[1 2 4 3;5 6 8 7;1 2 6 5;3 4 8 7;1 3 7 5;2 4 8 6];
        patch('Vertices',v,'Faces',ff,'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
    end
    function rueda(par,cx,cy,r,w,c)
        [th,zz]=meshgrid(linspace(0,2*pi,16),[cy-w/2 cy+w/2]);
        surf(cx+r*cos(th),zz,r+r*sin(th),'FaceColor',c,'EdgeColor','none','FaceLighting','gouraud','Parent',par);
    end
end

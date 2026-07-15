% anim_lhd_3d.m — Animación 3D del LHD recorriendo la galería (datos reales NS-3).
% El vehículo avanza por el recorrido real; el AP servidor se ilumina y se dibuja
% el enlace. Se muestra EN VIVO y se guarda un MP4.
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
STL = [TRB 'galeria_nv1640.stl'];
REC = readmatrix([TRB 'anim_recorrido.csv']);   % t, x, y, idx_ap, rssi
AP  = readmatrix([TRB 'anim_aps.csv']);          % x, y, tipo
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};

% --- figura y galería (prismas desde el STL, tenues) ---
fig = figure('Position',[40 40 1400 850],'Color','w','Renderer','opengl');
ax = axes(fig); hold(ax,'on');
tr = stlread(STL);
trisurf(tr, 'FaceColor',[0.86 0.90 0.95], 'EdgeColor',[0.7 0.75 0.82], ...
    'FaceAlpha',0.12, 'EdgeAlpha',0.25, 'Parent',ax);

% --- AP: Hawk (triángulos azules) / Cardinal (cuadrados morados) + etiquetas ---
for k = 1:size(AP,1)
    if AP(k,3)==1, mk='^'; col=[0.08 0.40 0.75]; else, mk='s'; col=[0.48 0.12 0.64]; end
    plot3(ax, AP(k,1), AP(k,2), 2, mk, 'MarkerSize',13, 'MarkerFaceColor',col, 'MarkerEdgeColor','w','LineWidth',1.2);
    text(ax, AP(k,1), AP(k,2), 4.6, IDS{k}, 'FontWeight','bold','FontSize',10,'HorizontalAlignment','center','Color',col*0.7);
end

% --- traza del recorrido completo (tenue, de referencia) ---
plot3(ax, REC(:,2), REC(:,3), 0.3*ones(size(REC,1),1), '-', 'Color',[0.8 0.8 0.8], 'LineWidth',1);

% --- elementos dinámicos ---
hLHD  = plot3(ax, REC(1,2), REC(1,3), 1.2, 's', 'MarkerSize',22, 'MarkerFaceColor',[0.95 0.75 0.10], 'MarkerEdgeColor',[0.3 0.2 0],'LineWidth',2);
hTrail= plot3(ax, REC(1,2), REC(1,3), 0.5, '-', 'Color',[0.90 0.55 0.05], 'LineWidth',3);
hHalo = plot3(ax, AP(1,1), AP(1,2), 2, 'o', 'MarkerSize',30, 'Color',[0.95 0.35 0.05], 'LineWidth',3, 'Visible','off');
hLink = plot3(ax, [0 0],[0 0],[1.2 2], '-', 'Color',[0.95 0.35 0.05], 'LineWidth',2, 'Visible','off');
hTxt  = title(ax, '', 'FontSize',14);

axis(ax,'equal'); grid(ax,'on'); view(ax,-38,34);
camlight(ax,'headlight'); lighting(ax,'gouraud');
xlabel(ax,'X (m)'); ylabel(ax,'Y (m)'); zlabel(ax,'Z (m)');
xlim(ax,[-6 60]); ylim(ax,[-8 172]); zlim(ax,[0 16]);

% --- video ---
vw = VideoWriter([TRB 'lhd_recorrido_3d.mp4'],'MPEG-4');
vw.FrameRate = 12; vw.Quality = 92; open(vw);

N = size(REC,1);
for i = 1:N
    x = REC(i,2); y = REC(i,3); k = REC(i,4); rssi = REC(i,5);
    set(hLHD, 'XData',x, 'YData',y);
    set(hTrail, 'XData',REC(max(1,i-25):i,2), 'YData',REC(max(1,i-25):i,3), 'ZData',0.5*ones(min(i,26),1));
    if k>=1
        set(hHalo,'XData',AP(k,1),'YData',AP(k,2),'Visible','on');
        set(hLink,'XData',[x AP(k,1)],'YData',[y AP(k,2)],'ZData',[1.2 2],'Visible','on');
        set(hTxt,'String',sprintf('Teleoperación del LHD — t = %.0f s   |   AP servidor: %s   |   RSSI: %.0f dBm', REC(i,1), IDS{k}, rssi));
    end
    drawnow;
    writeVideo(vw, getframe(fig));
end
close(vw);
fprintf('VIDEO OK: %d frames -> lhd_recorrido_3d.mp4\n', N);

% editor_antenas.m — EDITOR INTERACTIVO: mueve y orienta cada antena a tu gusto.
%   · Menú para elegir la antena (H1..H5, C1..C7, LHD)
%   · Sliders: X, Y, altura Z y ORIENTACIÓN (0-360°)
%   · El patrón se redibuja en vivo (usa la caché, instantáneo)
%   · Botón "Trazar rayos" para ver los rayos SBR a la posición del LHD
%   · Botón "Guardar posiciones" -> antenas_editadas.csv
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
load([TRB 'escena_cache.mat']);                   % pHawkBi pCard pLHDBi az el k angH4
AP = readmatrix([TRB 'anim_aps.csv']);            % x y tipo ang
IDS = {'H1','H2','H3','H4','H5','C1','C2','C3','C4','C5','C6','C7'};
NA = size(AP,1);

% estado editable: x, y, z, ang, tipo
S = struct();
S.x = AP(:,1); S.y = AP(:,2); S.z = 3.0*ones(NA,1); S.ang = AP(:,4); S.tipo = AP(:,3);
S.sel = 4;                                        % antena seleccionada (H4)

fig = figure('Name','Editor de antenas — NV1640','Position',[10 10 1550 900], ...
    'Color',[0.05 0.05 0.07],'Renderer','opengl');
ax = axes('Parent',fig,'Position',[0.02 0.06 0.72 0.9]); hold(ax,'on');
set(ax,'Color',[0.05 0.05 0.07]);

% ---- mina (fija) ----
tr = stlread([TRB 'galeria_nv1640.stl']);
Vm = tr.Points; Fm = tr.ConnectivityList;
rng(1); vc = [0.46 0.40 0.34] + 0.10*(rand(size(Vm,1),1)-0.5);
patch(ax,'Faces',Fm,'Vertices',Vm,'FaceVertexCData',min(max(vc,0.15),0.62), ...
    'FaceColor','interp','EdgeColor','none','FaceLighting','gouraud','AmbientStrength',0.42);
trT = stlread([TRB 'galeria_techo.stl']);
patch(ax,'Faces',trT.ConnectivityList,'Vertices',trT.Points, ...
    'FaceColor',[0.5 0.44 0.38],'EdgeColor','none','FaceAlpha',0.10,'FaceLighting','gouraud');
colormap(ax, turbo);
axis(ax,'equal'); axis(ax,'off'); view(ax,-30,36);
xlim(ax,[-10 62]); ylim(ax,[-8 172]); zlim(ax,[0 20]);
light(ax,'Position',[26 80 100],'Style','infinite','Color',[0.65 0.65 0.7]);
light(ax,'Position',[-40 40 60],'Style','infinite','Color',[0.4 0.36 0.33]);
rotate3d(ax,'on');

hPat = gobjects(NA,1); hMk = gobjects(NA,1); hTx = gobjects(NA,1); hRays = [];

    function P = patronLobulo(pat, cx, cy, cz, esc, ang, girar)
        Pw = pat - max(pat(:)); R = 10.^(Pw/20); R(R<0.05)=0.05;
        [AZ,EL] = meshgrid(deg2rad(az), deg2rad(el));
        Rm = R*esc; X = Rm.*cos(EL).*cos(AZ); Y = Rm.*cos(EL).*sin(AZ); Z = Rm.*sin(EL);
        if girar
            X1 = Z; Y1 = Y; Z1 = -X;
            X = X1*cos(ang) - Y1*sin(ang); Y = X1*sin(ang) + Y1*cos(ang); Z = Z1;
        end
        P = {X+cx, Y+cy, Z+cz, pat};
    end

    function redibujar()
        for q = 1:NA
            if isgraphics(hPat(q)), delete(hPat(q)); end
            if isgraphics(hMk(q)),  delete(hMk(q));  end
            if isgraphics(hTx(q)),  delete(hTx(q));  end
            if S.tipo(q)==1
                D = patronLobulo(pHawkBi, S.x(q), S.y(q), S.z(q), 6.5, S.ang(q), true);
                col=[0.30 0.70 1.0];
            else
                D = patronLobulo(pCard, S.x(q), S.y(q), S.z(q), 4.5, 0, false);
                col=[0.80 0.50 1.0];
            end
            alfa = 0.45; if q==S.sel, alfa = 0.7; end
            hPat(q) = surf(ax, D{1},D{2},D{3},D{4},'EdgeColor','none','FaceAlpha',alfa,'FaceLighting','none');
            mkS = 8; if q==S.sel, mkS = 15; col2=[1 1 0.3]; else, col2=col; end
            hMk(q) = plot3(ax,S.x(q),S.y(q),S.z(q),'o','MarkerSize',mkS,'MarkerFaceColor',col2,'MarkerEdgeColor','w','LineWidth',1.2);
            hTx(q) = text(ax,S.x(q),S.y(q),S.z(q)+3.2,IDS{q},'FontWeight','bold','FontSize',10,'Color',col,'HorizontalAlignment','center');
        end
        drawnow;
    end

% ---- panel de controles (derecha) ----
px = 0.77; pw = 0.21;
uicontrol('Style','text','Units','normalized','Position',[px 0.93 pw 0.04], ...
    'String','EDITOR DE ANTENAS','FontWeight','bold','FontSize',12, ...
    'ForegroundColor','w','BackgroundColor',[0.05 0.05 0.07]);
lst = uicontrol('Style','popupmenu','Units','normalized','Position',[px 0.87 pw 0.04], ...
    'String',IDS,'Value',S.sel,'FontSize',11,'Callback',@onSelect);

function lab = mkslider(y, txt, mn, mx, val, cb)
    uicontrol('Style','text','Units','normalized','Position',[px y+0.035 pw 0.03], ...
        'String',txt,'FontSize',10,'ForegroundColor','w','BackgroundColor',[0.05 0.05 0.07],'HorizontalAlignment','left');
    lab = uicontrol('Style','slider','Units','normalized','Position',[px y pw 0.035], ...
        'Min',mn,'Max',mx,'Value',val,'Callback',cb);
end
sX  = mkslider(0.79, 'X (m)',        -10, 62,  S.x(S.sel),   @onX);
sY  = mkslider(0.71, 'Y (m)',        -8, 172,  S.y(S.sel),   @onY);
sZ  = mkslider(0.63, 'Altura Z (m)',  0.5, 6,  S.z(S.sel),   @onZ);
sA  = mkslider(0.55, 'Orientación (°)', 0, 360, rad2deg(mod(S.ang(S.sel),2*pi)), @onA);

uicontrol('Style','pushbutton','Units','normalized','Position',[px 0.45 pw 0.05], ...
    'String','Trazar rayos (H sel. -> LHD)','FontSize',10,'Callback',@onRays);
uicontrol('Style','pushbutton','Units','normalized','Position',[px 0.38 pw 0.05], ...
    'String','Guardar posiciones (CSV)','FontSize',10,'Callback',@onSave);
uicontrol('Style','pushbutton','Units','normalized','Position',[px 0.31 pw 0.05], ...
    'String','Restaurar originales','FontSize',10,'Callback',@onReset);
uicontrol('Style','text','Units','normalized','Position',[px 0.05 pw 0.24], ...
    'String',sprintf(['INSTRUCCIONES\n\n1. Elige la antena en el menu.\n' ...
    '2. Mueve X/Y/Z y la orientacion.\n3. El patron se actualiza al instante.\n' ...
    '4. "Trazar rayos" recalcula los rayos SBR desde la antena seleccionada.\n' ...
    '5. Guarda para exportar tus posiciones.\n\nRota la escena arrastrando con el mouse.']), ...
    'FontSize',9,'ForegroundColor',[0.8 0.85 0.95],'BackgroundColor',[0.08 0.08 0.11], ...
    'HorizontalAlignment','left');

    function sync()
        set(sX,'Value',min(max(S.x(S.sel),-10),62));
        set(sY,'Value',min(max(S.y(S.sel),-8),172));
        set(sZ,'Value',min(max(S.z(S.sel),0.5),6));
        set(sA,'Value',rad2deg(mod(S.ang(S.sel),2*pi)));
    end
    function onSelect(src,~), S.sel = src.Value; sync(); redibujar(); end
    function onX(src,~), S.x(S.sel)=src.Value; redibujar(); end
    function onY(src,~), S.y(S.sel)=src.Value; redibujar(); end
    function onZ(src,~), S.z(S.sel)=src.Value; redibujar(); end
    function onA(src,~), S.ang(S.sel)=deg2rad(src.Value); redibujar(); end
    function onReset(~,~)
        S.x=AP(:,1); S.y=AP(:,2); S.z=3.0*ones(NA,1); S.ang=AP(:,4);
        sync(); redibujar();
    end
    function onSave(~,~)
        M = [S.x S.y S.tipo S.ang S.z];
        writematrix(M, [TRB 'antenas_editadas.csv']);
        msgbox('Guardado en antenas_editadas.csv','Editor');
    end
    function onRays(~,~)
        for h = hRays(:)', if isgraphics(h), delete(h); end, end
        hRays = [];
        q = S.sel;
        pm = propagationModel('raytracing','Method','sbr','CoordinateSystem','cartesian', ...
            'MaxNumReflections',4,'SurfaceMaterial','custom', ...
            'SurfaceMaterialPermittivity',6.0,'SurfaceMaterialConductivity',0.01);
        tx = txsite('cartesian','AntennaPosition',[S.x(q); S.y(q); S.z(q)],'TransmitterFrequency',5e9);
        u = [cos(S.ang(q)) sin(S.ang(q))];
        cmap = turbo(256);
        for d = [12 24 38]
            Pl = [S.x(q) S.y(q)] + u*d;
            rx = rxsite('cartesian','AntennaPosition',[Pl(1); Pl(2); 1.2]);
            rr = raytrace(tx, rx, pm, 'Map', [TRB 'galeria_rt.stl']);
            if isempty(rr{1}), continue; end
            for r2 = 1:numel(rr{1})
                R = rr{1}(r2); pts = [S.x(q) S.y(q) S.z(q)];
                for it = 1:numel(R.Interactions), pts=[pts; R.Interactions(it).Location(:)']; end
                pts = [pts; Pl(1) Pl(2) 1.2];
                f2 = min(max((R.PathLoss-60)/60,0),1); c = cmap(max(1,257-round(1+f2*255)),:);
                hRays(end+1) = plot3(ax, pts(:,1),pts(:,2),pts(:,3),'-','Color',[c 0.5],'LineWidth',1);
            end
        end
        drawnow;
    end

redibujar();
disp('EDITOR LISTO: elige antena, mueve sliders, traza rayos. Rota con el mouse.');

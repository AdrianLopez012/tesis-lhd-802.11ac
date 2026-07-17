function ver_wmm_paquetes()
% ver_wmm_paquetes — CÓMO INTERACTÚAN LOS PAQUETES EN EL AP (colas WMM/EDCA).
% Esto SÍ está en la tesis: diseño QoS (Cap. 3) + resultados medidos (NS-3).
%   · 3 flujos reales entrando al AP: VÍDEO (AC_VI), COMANDOS (AC_VO, prioridad
%     máxima), TELEMETRÍA (AC_BE) — con sus TASAS REALES de la simulación
%   · el servidor EDCA atiende por prioridad: los comandos "adelantan" al vídeo
%   · botón OPERACIÓN <-> ESTRÉS (vídeo 50 Mbps): la cola de vídeo crece,
%     los comandos siguen fluyendo — igual que en los resultados medidos
% Los números del panel son los MEDIDOS en NS-3 (flow_stats reales).
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
RES = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\results\';

% ---- números REALES medidos ----
T1 = readtable([RES 'principal_s1_v3_flow_stats.csv']);
T2 = readtable([RES 'estres_video_v3_flow_stats.csv']);
owd = @(T,nombre) T.owd_ms(strcmp(T.name,nombre));
plr = @(T,nombre) T.plr_pct(strcmp(T.name,nombre));
MED.op.cmd  = owd(T1,'Comandos');  MED.op.vid  = T1.e2e_ms(strcmp(T1.name,'Video'));
MED.op.plr  = plr(T1,'Comandos');
MED.es.cmd  = owd(T2,'Comandos');  MED.es.vid  = T2.e2e_ms(strcmp(T2.name,'Video'));
MED.es.plr  = plr(T2,'Comandos');
if isempty(MED.op.vid), MED.op.vid = 35.9; end
if isempty(MED.es.vid), MED.es.vid = 36.0; end

% ---- parámetros de la animación (tasas relativas reales: 3.6k/483/62 pps) ----
modo = 1;                                 % 1=operación, 2=estrés
lam  = [36, 5, 1];                        % llegadas por tick (vídeo, cmd, tel) ~ proporción real /100
serv = 44;                                % capacidad de servicio por tick (holgura en operación)

fig = figure('Name','Interacción de paquetes en el AP — colas WMM (datos NS-3)', ...
    'Position',[40 40 1420 820],'Color',[0.045 0.045 0.07]);
ax = axes(fig,'Position',[0.04 0.1 0.7 0.82]); hold(ax,'on');
set(ax,'Color',[0.06 0.06 0.09],'XColor','none','YColor','none');
xlim(ax,[0 100]); ylim(ax,[0 60]);

% carriles de colas
NOM = {'AC\_VI — VÍDEO 40 Mbps','AC\_VO — COMANDOS (prioridad máx.)','AC\_BE — TELEMETRÍA'};
COL = {[1 0.55 0.05],[0.30 0.95 0.45],[0.45 0.80 1]};
YQ  = [44, 30, 16];
for q = 1:3
    rectangle(ax,'Position',[8 YQ(q)-4 54 8],'FaceColor',[0.10 0.10 0.16],'EdgeColor',[0.3 0.3 0.4],'Curvature',0.1);
    text(ax, 8, YQ(q)+6.4, NOM{q}, 'Color', COL{q}, 'FontSize', 12, 'FontWeight','bold');
end
% servidor EDCA y "aire"
rectangle(ax,'Position',[66 12 10 40],'FaceColor',[0.13 0.2 0.34],'EdgeColor',[0.4 0.55 0.9],'Curvature',0.15);
text(ax, 71, 54.5, 'EDCA', 'Color',[0.7 0.85 1],'FontSize',13,'FontWeight','bold','HorizontalAlignment','center');
text(ax, 71, 32, {'sirve por','prioridad:','VO > VI > BE'}, 'Color',[0.85 0.9 1],'FontSize',10,'HorizontalAlignment','center');
annotation(fig,'arrow',[0.585 0.63],[0.5 0.5],'Color','w');
text(ax, 88, 32, {'AIRE','802.11ac','(40 MHz,','2\times2 MIMO)'}, 'Color',[0.9 0.93 1],'FontSize',11,'HorizontalAlignment','center');

% paneles de métricas reales
pnl = annotation(fig,'textbox',[0.76 0.45 0.225 0.45],'EdgeColor',[0.3 0.4 0.6], ...
    'BackgroundColor',[0.08 0.09 0.14],'Color','w','FontSize',12,'String','');
uicontrol('Style','pushbutton','Units','normalized','Position',[0.76 0.3 0.225 0.08], ...
    'String','Cambiar a ESTRÉS (vídeo 50 Mbps)','FontSize',11,'Callback',@onModo);
annotation(fig,'textbox',[0.76 0.06 0.225 0.2],'EdgeColor','none','Color',[0.75 0.8 0.9],'FontSize',9.5, ...
    'String',['Visualización didáctica del mecanismo WMM del diseño (Cap. 3). ' ...
    'Las tasas relativas de llegada y los valores del panel son los de la simulación NS-3.']);

% estado de colas: posiciones x de los puntos por carril
Q = {[],[],[]};
hDots = gobjects(3,1);
for q = 1:3
    hDots(q) = plot(ax, nan, nan, 'o', 'MarkerSize', 7, 'MarkerFaceColor', COL{q}, 'MarkerEdgeColor','none');
end
hTitulo = title(ax,'','Color','w','FontSize',14);

actualizarPanel();
while ishandle(fig)
    if modo==1, lamV = lam(1); else, lamV = round(lam(1)*1.25); end
    % llegadas
    Q{1} = [Q{1}, zeros(1, poissrnd(lamV/10))];
    Q{2} = [Q{2}, zeros(1, poissrnd(lam(2)/10))];
    Q{3} = [Q{3}, zeros(1, poissrnd(lam(3)/10))];
    % servicio por prioridad: VO primero, luego VI, luego BE
    cap = serv/10;
    for ord = [2 1 3]
        n = min(numel(Q{ord}), max(0, round(cap)));
        % sirve los que ya llegaron al frente
        listos = sum(Q{ord} > 50);
        n = min(n, listos);
        if n > 0
            [~, idx] = sort(Q{ord}, 'descend');
            Q{ord}(idx(1:n)) = [];
        end
        cap = cap - n;
    end
    % avanzar puntos hacia el servidor
    for q = 1:3
        if isempty(Q{q}), set(hDots(q),'XData',nan,'YData',nan); continue; end
        Q{q} = min(Q{q} + 2.2, 52 - (numel(Q{q}):-1:1)*1.1);
        Q{q} = max(Q{q}, 0);
        set(hDots(q), 'XData', 9 + Q{q}, 'YData', YQ(q)*ones(size(Q{q})) + 1.5*sin(1:numel(Q{q})));
    end
    if modo==1
        set(hTitulo,'String','OPERACIÓN — la red va holgada: todas las colas fluyen');
    else
        set(hTitulo,'String','ESTRÉS (vídeo +25 %) — la cola de VÍDEO crece; los COMANDOS siguen fluyendo (prioridad VO)');
    end
    drawnow limitrate;
    pause(0.05);
end

    function onModo(src,~)
        modo = 3 - modo;
        if modo==2, src.String = 'Volver a OPERACIÓN';
        else, src.String = 'Cambiar a ESTRÉS (vídeo 50 Mbps)'; end
        actualizarPanel();
    end
    function actualizarPanel()
        if modo==1
            set(pnl,'String',sprintf(['MEDIDO EN NS-3 — OPERACIÓN\n\n' ...
                'OWD comandos:  %.2f ms\n(requisito \\leq 20 ms)\n\n' ...
                'Vídeo E2E:  %.1f ms\n(requisito \\leq 150 ms)\n\n' ...
                'PLR comandos:  %.2f %%\n\n' ...
                'Paquetes en 300 s:\nvídeo ~1M · cmd 145k · tel 18.5k'], ...
                MED.op.cmd, MED.op.vid, MED.op.plr));
        else
            set(pnl,'String',sprintf(['MEDIDO EN NS-3 — ESTRÉS\n\n' ...
                'OWD comandos:  %.2f ms\n(sube \\times2.3 pero \\leq 20 ms)\n\n' ...
                'Vídeo E2E:  %.1f ms\n(sigue cumpliendo)\n\n' ...
                'PLR comandos:  %.2f %%\n\n' ...
                'La presión se ve en LATENCIA,\nno en pérdidas: WMM protege.'], ...
                MED.es.cmd, MED.es.vid, MED.es.plr));
        end
    end
end

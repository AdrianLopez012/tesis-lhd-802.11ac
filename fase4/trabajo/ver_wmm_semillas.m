% fig_wmm_semillas.m — Lámina de calidad: QoS por flujo con las 10 SEMILLAS
% (boxchart) + efecto del estrés. Todos los datos de los flow_stats reales.
RES = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\cap3\simulacion_ns3\results\';
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';

% ---- leer 10 semillas ----
owd = struct('cmd',[],'tel',[],'vid',[]); plrc = []; jit = [];
for s = 1:10
    T = readtable(sprintf('%sprincipal_s%d_v3_flow_stats.csv', RES, s));
    owd.cmd(end+1) = T.owd_ms(strcmp(T.name,'Comandos'));
    owd.tel(end+1) = T.owd_ms(strcmp(T.name,'Telemetria'));
    owd.vid(end+1) = T.e2e_ms(strcmp(T.name,'Video'));
    plrc(end+1)    = T.plr_pct(strcmp(T.name,'Comandos'));
end
TE = readtable([RES 'estres_video_v3_flow_stats.csv']);
TL = readtable([RES 'estres_lhd_v3_flow_stats.csv']);
TB = readtable([RES 'baseline_v3_flow_stats.csv']);
esc = @(T,n,c) T.(c)(strcmp(T.name,n));
ic95 = @(v) 1.96*std(v)/sqrt(numel(v));

fig = figure('Color','w','Position',[30 30 1380 620],'Visible','on');
tl = tiledlayout(fig,1,2,'Padding','compact','TileSpacing','compact');
title(tl, 'Prioridad WMM en acción: latencia por flujo (10 semillas) y comportamiento bajo estrés', ...
    'FontSize',15,'FontWeight','bold');
subtitle(tl, 'Batería NS-3 sobre la geometría real NV1640 · cajas = 10 semillas independientes · requisitos en línea discontinua', ...
    'FontSize',11);

% ---------- Panel A: boxchart de las 10 semillas por flujo ----------
ax1 = nexttile; hold(ax1,'on'); grid(ax1,'on');
datos = [owd.cmd, owd.tel, owd.vid];
grupos = categorical([repmat("Comandos (AC_VO)",1,10), repmat("Telemetría (AC_BE)",1,10), repmat("Vídeo E2E (AC_VI)",1,10)], ...
    ["Comandos (AC_VO)","Telemetría (AC_BE)","Vídeo E2E (AC_VI)"]);
b = boxchart(ax1, grupos, datos, 'BoxFaceColor',[0.2 0.45 0.8],'MarkerStyle','.');
yline(ax1, 20, '--', 'requisito comandos \leq 20 ms', 'Color',[0.1 0.55 0.25],'LineWidth',1.4,'FontSize',10,'LabelHorizontalAlignment','left');
yline(ax1, 50, '--', 'objetivo OWD \leq 50 ms', 'Color',[0.75 0.45 0.05],'LineWidth',1.2,'FontSize',10,'LabelHorizontalAlignment','left');
ylabel(ax1,'Latencia (ms)','FontSize',12);
title(ax1,'(a) Latencia por flujo — dispersión de las 10 semillas','FontSize',12.5);
% anotar medias ± IC
med = [mean(owd.cmd) mean(owd.tel) mean(owd.vid)];
ics = [ic95(owd.cmd) ic95(owd.tel) ic95(owd.vid)];
for q = 1:3
    text(ax1, q, med(q)+4.5, sprintf('%.2f \\pm %.2f ms', med(q), ics(q)), ...
        'HorizontalAlignment','center','FontSize',10.5,'FontWeight','bold','Color',[0.15 0.3 0.55]);
end
ylim(ax1,[0 56]);

% ---------- Panel B: efecto del estrés (comandos y vídeo) ----------
ax2 = nexttile; hold(ax2,'on'); grid(ax2,'on');
esc_cmd = [esc(TB,'Comandos','owd_ms'), mean(owd.cmd), esc(TE,'Comandos','owd_ms'), esc(TL,'Comandos','owd_ms')];
esc_vid = [esc(TB,'Video','e2e_ms'),   mean(owd.vid), esc(TE,'Video','e2e_ms'),   esc(TL,'Video','e2e_ms')];
X = 1:4;
b1 = bar(ax2, X-0.18, esc_cmd, 0.32, 'FaceColor',[0.20 0.65 0.35]);
b2 = bar(ax2, X+0.18, esc_vid, 0.32, 'FaceColor',[0.90 0.55 0.10]);
errorbar(ax2, 2-0.18, mean(owd.cmd), ic95(owd.cmd), 'k','LineWidth',1.2,'CapSize',8);
errorbar(ax2, 2+0.18, mean(owd.vid), ic95(owd.vid), 'k','LineWidth',1.2,'CapSize',8);
set(ax2,'XTick',X,'XTickLabel',{'Baseline\newline(estático)','Operación\newline(10 semillas)','Estrés vídeo\newline(50 Mbps)','Estrés LHD\newline(4 m/s)'},'FontSize',10);
yline(ax2, 20, '--', 'req. comandos \leq 20 ms', 'Color',[0.1 0.55 0.25],'LineWidth',1.4,'FontSize',10);
ylabel(ax2,'Latencia (ms)','FontSize',12);
title(ax2,'(b) Bajo estrés la presión va a la latencia — nunca rompe el requisito','FontSize',12.5);
legend(ax2,[b1 b2],{'Comandos (OWD)','Vídeo (E2E)'},'Location','northwest','FontSize',10.5);
for q = 1:4
    text(ax2, q-0.18, esc_cmd(q)+1.3, sprintf('%.1f', esc_cmd(q)), 'HorizontalAlignment','center','FontSize',9.5,'FontWeight','bold');
    text(ax2, q+0.18, esc_vid(q)+1.3, sprintf('%.1f', esc_vid(q)), 'HorizontalAlignment','center','FontSize',9.5,'FontWeight','bold');
end
ylim(ax2,[0 46]);

disp('FIGURA ABIERTA EN MATLAB - explorala (zoom, data tips)');
fprintf('FIG OK: cmd %.2f±%.2f | tel %.2f±%.2f | vid %.2f±%.2f | PLR cmd %.3f%%\n', ...
    mean(owd.cmd), ic95(owd.cmd), mean(owd.tel), ic95(owd.tel), mean(owd.vid), ic95(owd.vid), mean(plrc));


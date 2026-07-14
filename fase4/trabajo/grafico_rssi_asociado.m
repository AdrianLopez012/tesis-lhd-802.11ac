% grafico_rssi_asociado.m — RSSI del enlace ASOCIADO a lo largo del recorrido
% (10 semillas) frente a los umbrales. Responde: ¿el AP servidor siempre tuvo
% señal suficiente aunque no fuera el más cercano? Datos: pos_log real de NS-3.
try
A = readmatrix('C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\rssi_assoc_10seeds.csv');
% columnas: semilla, t, rssi_asociado, rssi_mejor
fig = figure('Position',[50 50 1450 720],'Color','w','Visible','off');
ax = axes(fig); hold(ax,'on');

% zonas de referencia
yl = [-90 -5];
fill(ax,[0 300 300 0],[-82 -82 yl(1) yl(1)],[0.95 0.85 0.84],'EdgeColor','none');
fill(ax,[0 300 300 0],[-68 -68 -82 -82],[0.99 0.96 0.87],'EdgeColor','none');

% 10 semillas del asociado en gris; semilla 1 resaltada; mejor AP punteado
hg = gobjects(1);
for s = 1:10
    M = A(A(:,1)==s,:);
    hg = plot(ax, M(:,2), M(:,3), '-', 'Color',[0.62 0.66 0.72 0.5], 'LineWidth',0.8);
end
M1 = A(A(:,1)==1,:);
hA = plot(ax, M1(:,2), M1(:,3), '-', 'Color',[0.10 0.35 0.65], 'LineWidth',2.2);
hB = plot(ax, M1(:,2), M1(:,4), ':', 'Color',[0.20 0.55 0.30], 'LineWidth',1.6);

% umbrales
yline(ax,-68,'--','Umbral 300 Mbps (-68 dBm)','Color',[0.72 0.50 0.10],'LineWidth',1.3,'FontSize',10,'LabelHorizontalAlignment','left');
hU = yline(ax,-82,'-','Umbral de enlace usable (-82 dBm)','Color',[0.75 0.20 0.15],'LineWidth',1.8,'FontSize',10,'LabelHorizontalAlignment','left');

% peor caso global
[mn,ix] = min(A(:,3));
plot(ax, A(ix,2), mn, 'v', 'MarkerSize',10, 'MarkerFaceColor',[0.75 0.20 0.15], 'MarkerEdgeColor','w');
text(ax, A(ix,2)+4, mn-2.5, sprintf('peor caso global: %.1f dBm (margen de %.1f dB sobre el umbral)', mn, mn-(-82)), 'FontSize',11,'FontWeight','bold','Color',[0.6 0.15 0.1]);

xlim(ax,[0 300]); ylim(ax,yl); grid(ax,'on');
xlabel(ax,'Tiempo de simulación (s)','FontSize',12);
ylabel(ax,'RSSI del enlace (dBm)','FontSize',12);
title(ax, sprintf('RSSI del AP ASOCIADO durante el recorrido — 10 semillas independientes\nEl enlace de servicio nunca desciende de %.1f dBm: %.1f dB de margen sobre el umbral usable', mn, mn-(-82)), 'FontSize',13);
legend(ax,[hA hg hB],{'Enlace asociado (semilla 1)','Enlace asociado (semillas 2-10)','Mejor AP disponible (referencia)'},'Location','southeast','FontSize',11);
exportgraphics(fig,'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\grafico_rssi_asociado.png','Resolution',200);
fprintf('PNG OK\n');
catch e
    fprintf('ERROR: %s\n', e.message);
end
exit;

% fig_osinergmin.m — gráfico sobrio del dato OSINERGMIN (Tabla 2 de la tesis):
% accidentes mortales y víctimas 2024 por lugar (subterránea vs superficie).
OUT = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\presentacion\osinergmin_2024.png';
AZUL = [0 51 160]/255; GRISC = [0.78 0.82 0.87];

fig = figure('Color','w','Position',[60 60 1000 290],'Visible','off');
ax = axes(fig,'Position',[0.155 0.16 0.47 0.72]); hold(ax,'on');

cats = {'Víctimas mortales','Accidentes mortales'};
sub = [13 12]; sup = [2 2];
b = barh(ax, [1 2], [sub; sup]', 'stacked', 'BarWidth', 0.55);
b(1).FaceColor = AZUL;  b(1).EdgeColor = 'none';
b(2).FaceColor = GRISC; b(2).EdgeColor = 'none';
% etiquetas dentro de las barras
for k = 1:2
    text(ax, sub(k)/2, k, sprintf('%d', sub(k)), 'Color','w','FontWeight','bold', ...
        'FontSize',13,'HorizontalAlignment','center','FontName','Calibri');
    text(ax, sub(k)+sup(k)/2, k, sprintf('%d', sup(k)), 'Color',[0.25 0.3 0.35], ...
        'FontWeight','bold','FontSize',12,'HorizontalAlignment','center','FontName','Calibri');
end
set(ax,'YTick',[1 2],'YTickLabel',cats,'FontName','Calibri','FontSize',12.5, ...
    'XColor','none','YColor',[0.2 0.25 0.3],'Box','off');
xlim(ax,[0 16]); ylim(ax,[0.45 2.55]);
legend(ax, {'Minería subterránea','Superficie'}, 'Location','southoutside', ...
    'Orientation','horizontal','FontSize',11,'FontName','Calibri','Box','off');

% callout del porcentaje
annotation(fig,'textbox',[0.645 0.42 0.34 0.42],'EdgeColor','none', ...
    'String','86.7 %','FontName','Cambria','FontSize',44,'FontWeight','bold', ...
    'Color',AZUL,'HorizontalAlignment','center');
annotation(fig,'textbox',[0.645 0.14 0.34 0.30],'EdgeColor','none', ...
    'String',{'de las víctimas mortales de 2024','ocurrieron en minería subterránea','(OSINERGMIN, ene–dic 2024)'}, ...
    'FontName','Calibri','FontSize',11.5,'Color',[0.2 0.25 0.3],'HorizontalAlignment','center');

exportgraphics(fig, OUT, 'Resolution', 220);
disp('FIG OSINERGMIN OK');
exit;

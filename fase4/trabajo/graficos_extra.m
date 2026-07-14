% graficos_extra.m — (1) Prx vs distancia con umbrales del datasheet;
% (2) CDF del RSSI asociado y del mejor AP (10 semillas, pos_log real).
try
B = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';

% ---------- (1) Prx vs distancia (modelo two-slope, fuente única) ----------
N1=1.9; N2=3.4; DBP=40; LSYS=9.4; F=5.0e9;
PLD0 = 20*log10(4*pi/(3e8/F));
d = 1:1:340;
pl = PLD0 + 10*N1*log10(min(d,DBP)) + 10*N2*log10(max(d/DBP,1));
prxH = 30+11+4.8 - pl - LSYS;    % Hawk -> LHD
prxC = 23+7.5+4.8 - pl - LSYS;   % Cardinal -> LHD
f1 = figure('Position',[50 50 1250 640],'Color','w','Visible','off');
ax = axes(f1); hold(ax,'on'); grid(ax,'on');
fill(ax,[1 340 340 1],[-68 -68 -95 -95],[0.99 0.96 0.87],'EdgeColor','none');
fill(ax,[1 340 340 1],[-82 -82 -95 -95],[0.95 0.85 0.84],'EdgeColor','none');
hH = plot(ax,d,prxH,'-','Color',[0.08 0.40 0.75],'LineWidth',2.4);
hC = plot(ax,d,prxC,'-','Color',[0.48 0.12 0.64],'LineWidth',2.4);
yline(ax,-68,'--','Sensibilidad video: -68 dBm (300 Mbps)','Color',[0.72 0.50 0.10],'LineWidth',1.4,'FontSize',10);
yline(ax,-82,'-','Sensibilidad de borde: -82 dBm (54 Mbps)','Color',[0.75 0.20 0.15],'LineWidth',1.8,'FontSize',10);
xline(ax,60,':','Radio de diseño (60 m)','Color',[0.3 0.3 0.3],'LineWidth',1.4,'FontSize',10,'LabelVerticalAlignment','bottom');
% intersecciones Cardinal (enlace más exigente)
dV = interp1(prxC, d, -68); dB2 = interp1(prxC, d, -82);
plot(ax, dV, -68, 'o', 'MarkerSize',9,'MarkerFaceColor',[0.72 0.50 0.10],'MarkerEdgeColor','w');
plot(ax, dB2, -82, 'o', 'MarkerSize',9,'MarkerFaceColor',[0.75 0.20 0.15],'MarkerEdgeColor','w');
text(ax, dV+6, -66, sprintf('%.0f m', dV), 'FontSize',11,'FontWeight','bold','Color',[0.6 0.4 0.05]);
text(ax, dB2+6, -80, sprintf('%.0f m', dB2), 'FontSize',11,'FontWeight','bold','Color',[0.6 0.15 0.1]);
xlim(ax,[1 340]); ylim(ax,[-95 -10]);
xlabel(ax,'Distancia por ruta de túnel (m)','FontSize',12); ylabel(ax,'Potencia recibida en el LHD (dBm)','FontSize',12);
title(ax,'Potencia recibida frente a la distancia — modelo two-slope calibrado (LOS)','FontSize',13);
legend(ax,[hH hC],{'AP Hawk (30 dBm / 11 dBi)','AP Cardinal (23 dBm / 7.5 dBi)'},'Location','northeast','FontSize',11);
exportgraphics(f1,[B 'curva_prx_distancia.png'],'Resolution',200);

% ---------- (2) CDF del RSSI (10 semillas) ----------
A = readmatrix([B 'rssi_assoc_10seeds.csv']);
f2 = figure('Position',[50 50 1250 640],'Color','w','Visible','off');
ax2 = axes(f2); hold(ax2,'on'); grid(ax2,'on');
va = sort(A(:,3)); vb = sort(A(:,4));
ca = (1:numel(va))/numel(va)*100; cb = (1:numel(vb))/numel(vb)*100;
hA = plot(ax2, va, ca, '-', 'Color',[0.10 0.35 0.65], 'LineWidth',2.4);
hB = plot(ax2, vb, cb, '-', 'Color',[0.20 0.55 0.30], 'LineWidth',2.4);
xline(ax2,-68,'--','-68 dBm','Color',[0.72 0.50 0.10],'LineWidth',1.4,'FontSize',10);
xline(ax2,-82,'-','-82 dBm (usable)','Color',[0.75 0.20 0.15],'LineWidth',1.8,'FontSize',10);
xlabel(ax2,'RSSI (dBm)','FontSize',12); ylabel(ax2,'% de muestras \leq RSSI','FontSize',12);
title(ax2, sprintf('Distribución acumulada del RSSI durante el recorrido — 10 semillas (%d muestras)\nEl enlace asociado nunca cae bajo %.1f dBm; 0%% de muestras bajo el umbral usable', size(A,1), min(A(:,3))),'FontSize',13);
legend(ax2,[hA hB],{'Enlace asociado (servicio real)','Mejor AP disponible (cobertura)'},'Location','northwest','FontSize',11);
xlim(ax2,[-85 -5]); ylim(ax2,[0 100]);
exportgraphics(f2,[B 'cdf_rssi_10seeds.png'],'Resolution',200);
fprintf('2 PNG OK\n');
catch e
    fprintf('ERROR: %s\n', e.message);
end
exit;

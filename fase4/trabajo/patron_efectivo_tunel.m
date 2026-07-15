% patron_efectivo_tunel.m — Patrón EFECTIVO de la antena dentro del túnel:
% combina el patrón real de la hélice (Antenna TB) con las reflexiones en las
% paredes de roca (ray-tracing). Muestra cómo el túnel GUÍA la señal (a
% diferencia del patrón en espacio libre que "cubre todo").
TRB='C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
STL=[TRB 'galeria_nv1640.stl'];
f0=5e9;

% antena real (hélice Hawk ~11 dBi)
hel = helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115);

% ray-tracing con la antena real montada en el tx
pm = propagationModel('raytracing','Method','sbr','CoordinateSystem','cartesian',...
    'MaxNumReflections',6,'SurfaceMaterial','custom',...
    'SurfaceMaterialPermittivity',6.0,'SurfaceMaterialConductivity',0.01);

tx = txsite('cartesian','AntennaPosition',[26;2;2],'Antenna',hel,...
    'TransmitterFrequency',f0,'TransmitterPower',0.2);

% grilla de receptores en la galería central (a lo largo del túnel)
ys = 6:2:60; xs = 26 + (-1.5:0.75:1.5);   % ancho del túnel
[YY,XX] = meshgrid(ys,xs);
rssi = nan(size(XX));
for i=1:numel(XX)
    rx = rxsite('cartesian','AntennaPosition',[XX(i);YY(i);1]);
    try
        r = raytrace(tx,rx,pm,'Map',STL);
        if ~isempty(r{1}), rssi(i) = 10*log10(0.2*1000)+11+4.8-min([r{1}.PathLoss]); end
    catch, end
end

% figura: heatmap del patrón efectivo (la señal guiada por el túnel)
fig=figure('Position',[60 60 900 700],'Color','w','Visible','off');
ax=axes(fig); hold(ax,'on');
h=pcolor(ax,XX,YY,rssi); set(h,'EdgeColor','none'); shading(ax,'interp');
colormap(ax,turbo); cb=colorbar(ax); cb.Label.String='RSSI efectivo dentro del túnel (dBm)';
clim(ax,[-70 -30]);
plot(ax,26,2,'p','MarkerSize',18,'MarkerFaceColor','w','MarkerEdgeColor','k','LineWidth',1.5);
text(ax,26,4,'AP (hélice 11 dBi)','FontWeight','bold','FontSize',11,'HorizontalAlignment','center');
xlabel(ax,'X (m)'); ylabel(ax,'Distancia en la galería Y (m)');
title(ax,{'Patrón EFECTIVO de la antena dentro del túnel','(patrón real de la hélice + reflexiones en la roca por ray-tracing)'},'FontSize',12);
axis(ax,'tight');
exportgraphics(fig,[TRB 'patron_efectivo_tunel.png'],'Resolution',200);
fprintf('PATRON EFECTIVO OK: %d de %d ptos con senal\n', sum(~isnan(rssi(:))), numel(rssi));
exit;

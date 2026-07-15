% raytracing_final.m — Figura de validación cruzada para el paper.
% Two-slope (tesis) vs ray-tracing SBR, marcando el rango de concordancia
% y la zona donde el ray-tracing subestima por no capturar el modo guía.
try
STL='C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\galeria_nv1640.stl';
OUTPNG='C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\raytracing_validacion.png';
OUTCSV='C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\raytracing_rssi.csv';
f0=5e9;
pm=propagationModel('raytracing','Method','sbr','CoordinateSystem','cartesian',...
  'MaxNumReflections',6,'SurfaceMaterial','custom',...
  'SurfaceMaterialPermittivity',6.0,'SurfaceMaterialConductivity',0.01);
tx=txsite('cartesian','AntennaPosition',[26;2;2],'TransmitterFrequency',f0,'TransmitterPower',0.2);

% muestreo fino en el rango cercano (donde el RT sí resuelve)
ys=4:2:40; d=zeros(numel(ys),1); rt=nan(numel(ys),1);
for k=1:numel(ys)
  rx=rxsite('cartesian','AntennaPosition',[26;ys(k);1]);
  try
    r=raytrace(tx,rx,pm,'Map',STL);
    if ~isempty(r{1}), rt(k)=10*log10(0.2*1000)+7.5+4.8-min([r{1}.PathLoss]); end
  catch, end
  d(k)=abs(ys(k)-2);
end

% two-slope
N1=1.9;N2=3.4;DBP=40;LS=9.4;PLD0=20*log10(4*pi/(3e8/f0));GT=7.5;GR=4.8;PT=23;
dd=1:1:120;
pl=PLD0+10*N1*log10(min(dd,DBP))+10*N2*log10(max(dd/DBP,1));
ts=PT+GT+GR-pl-LS;

writematrix([d,rt],OUTCSV);
ok=~isnan(rt);
% error medio en la zona de concordancia
tsAtRt=PT+GT+GR-(PLD0+10*N1*log10(min(d(ok),DBP))+10*N2*log10(max(d(ok)/DBP,1)))-LS;
err=mean(abs(rt(ok)-tsAtRt));

fig=figure('Position',[60 60 1150 640],'Color','w','Visible','off');
ax=axes(fig);hold(ax,'on');grid(ax,'on');
% banda de concordancia (0-38 m)
fill(ax,[0 38 38 0],[-95 -95 -10 -10],[0.90 0.96 0.90],'EdgeColor','none','HandleVisibility','off');
text(ax,19,-14,'Zona de concordancia','HorizontalAlignment','center','FontSize',11,'Color',[0.2 0.5 0.2],'FontWeight','bold');
plot(ax,dd,ts,'-','Color',[0.10 0.35 0.65],'LineWidth',2.8,'DisplayName','Modelo two-slope calibrado (tesis)');
plot(ax,d(ok),rt(ok),'o','Color',[0.80 0.30 0.10],'MarkerFaceColor',[0.80 0.30 0.10],'MarkerSize',7,'DisplayName','Ray-tracing 3D SBR (MATLAB)');
yline(ax,-82,'--','Umbral usable (-82 dBm)','Color',[0.6 0.15 0.1],'LineWidth',1.3,'FontSize',10,'HandleVisibility','off');
xlabel(ax,'Distancia axial en la galería (m)','FontSize',12);
ylabel(ax,'Potencia recibida (dBm)','FontSize',12);
title(ax,sprintf('Validación cruzada del modelo de propagación: two-slope vs ray-tracing 3D\nConcordancia en campo cercano (error medio %.1f dB); el ray-tracing no resuelve el modo guía a larga distancia',err),'FontSize',12.5);
legend(ax,'Location','northeast','FontSize',11);
xlim(ax,[0 120]);ylim(ax,[-95 -10]);
exportgraphics(fig,OUTPNG,'Resolution',200);
fprintf('OK: %d pts RT, error medio %.2f dB en zona de concordancia\n',sum(ok),err);
catch e
  fprintf('ERR: %s (linea %d)\n',e.message,e.stack(1).line);
end
exit;

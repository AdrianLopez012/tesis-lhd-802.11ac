% raytracing_sbr.m v2 — Ray-tracing SBR sobre la geometría 3D de las galerías.
% Compara RSSI ray-tracing vs modelo two-slope de la tesis (validación cruzada).
try
STL = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\galeria_nv1640.stl';
OUTPNG = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\raytracing_comparacion.png';
OUTCSV = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\raytracing_rssi.csv';
f0 = 5.0e9;

% modelo de propagación por ray-tracing SBR con material personalizado (roca)
pm = propagationModel('raytracing', 'Method','sbr', ...
    'CoordinateSystem','cartesian', ...
    'MaxNumReflections', 8, ...
    'AngularSeparation','low', ...
    'SurfaceMaterial','custom', ...
    'SurfaceMaterialPermittivity', 6.0, ...
    'SurfaceMaterialConductivity', 0.01);

% transmisor en la galería central, cerca del crucero inferior
tx = txsite('cartesian', 'AntennaPosition',[26;2;2], ...
    'TransmitterFrequency', f0, 'TransmitterPower', 0.2);   % ~23 dBm

ys = 8:6:130;
d = zeros(numel(ys),1); rssi_rt = nan(numel(ys),1);
for k = 1:numel(ys)
    rx = rxsite('cartesian','AntennaPosition',[26; ys(k); 1]);
    try
        rays = raytrace(tx, rx, pm, 'Map', STL);
        if ~isempty(rays) && ~isempty(rays{1})
            pl = [rays{1}.PathLoss];
            rssi_rt(k) = 10*log10(0.2*1000) + 7.5 + 4.8 - min(pl);  % Pt+Gt+Gr-PL
        end
    catch, end
    d(k) = abs(ys(k)-2);
end

% modelo two-slope de la tesis (mismos parámetros)
N1=1.9; N2=3.4; DBP=40; LSYS=9.4; PLD0=20*log10(4*pi/(3e8/f0));
GT=7.5; GR=4.8; PT=23;
pl = PLD0 + 10*N1*log10(min(d,DBP)) + 10*N2*log10(max(d/DBP,1));
rssi_ts = PT + GT + GR - pl - LSYS;

writematrix([d, rssi_rt, rssi_ts], OUTCSV);

fig = figure('Position',[60 60 1100 620],'Color','w','Visible','off');
ax = axes(fig); hold(ax,'on'); grid(ax,'on');
plot(ax, d, rssi_ts, '-', 'Color',[0.10 0.35 0.65],'LineWidth',2.6,'DisplayName','Modelo two-slope (tesis)');
ok = ~isnan(rssi_rt);
plot(ax, d(ok), rssi_rt(ok), 'o--','Color',[0.80 0.30 0.10],'LineWidth',1.8,'MarkerFaceColor',[0.80 0.30 0.10],'DisplayName','Ray-tracing SBR (MATLAB)');
yline(ax,-82,'-','Umbral usable (-82 dBm)','Color',[0.6 0.15 0.1],'LineWidth',1.4,'FontSize',10);
xlabel(ax,'Distancia axial en la galería (m)','FontSize',12);
ylabel(ax,'Potencia recibida (dBm)','FontSize',12);
title(ax,'Validación cruzada: modelo two-slope vs ray-tracing 3D (SBR) — galería NV1640','FontSize',13);
legend(ax,'Location','northeast','FontSize',11);
exportgraphics(fig, OUTPNG,'Resolution',200);
fprintf('RT OK: %d de %d receptores con rayo; RSSI RT %.1f..%.1f dBm\n', sum(ok), numel(ys), min(rssi_rt(ok)), max(rssi_rt(ok)));
catch e
    fprintf('ERROR: %s\n', e.message);
    if ~isempty(e.stack), fprintf('  en linea %d\n', e.stack(1).line); end
end
exit;

% ver_raytracing_3d.m — Visor 3D EN VIVO: un AP y VARIOS receptores a distintas
% distancias, para ver dónde llegan los rayos y dónde se pierden (el fenómeno
% del alcance limitado del ray-tracing en túneles).
STL = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\galeria_nv1640.stl';
f0 = 5.0e9;

viewer = siteviewer('SceneModel', STL, 'Transparency', 0.35);

% AP en la galería central, cerca del crucero inferior
tx = txsite('cartesian', 'AntennaPosition',[26;2;2], ...
    'TransmitterFrequency', f0, 'TransmitterPower', 0.2);
show(tx);

% modelo de ray-tracing (roca, hasta 5 reflexiones)
pm = propagationModel('raytracing','Method','sbr', ...
    'CoordinateSystem','cartesian','MaxNumReflections',5, ...
    'SurfaceMaterial','custom', ...
    'SurfaceMaterialPermittivity',6.0,'SurfaceMaterialConductivity',0.01);

% receptores a distintas distancias a lo largo de la galería
distancias = [10 20 30 45 60 90 120];
fprintf('\n=== Rayos que llegan a cada receptor ===\n');
for yy = distancias
    rx = rxsite('cartesian', 'AntennaPosition',[26; yy; 1]);
    show(rx);
    rays = raytrace(tx, rx, pm, 'Map', STL);
    nr = numel(rays{1});
    if nr > 0
        plot(rays{1});   % DIBUJA los rayos en la escena 3D
        fprintf('  d = %3d m  ->  %d rayo(s)  [SÍ llega]\n', yy-2, nr);
    else
        fprintf('  d = %3d m  ->  0 rayos    [se pierde]\n', yy-2);
    end
end
fprintf('\nVentana 3D lista. Rota con el mouse: verás los rayos rebotando en\n');
fprintf('las paredes de roca cerca del AP, y cómo desaparecen a larga distancia.\n');

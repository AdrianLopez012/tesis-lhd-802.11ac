% mapa_cobertura_rf.m — Mapa de cobertura RF sobre la mina 3D (como los mapas
% de ciudad con antenas). Coloca los 12 AP en la galería y pinta la señal
% recibida sobre el entorno con ray-tracing (RF Propagation / Antenna Toolbox).
TRB='C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
STL=[TRB 'galeria_nv1640.stl'];
AP = readmatrix([TRB 'anim_aps.csv']);
f0=5e9;

% visor 3D de la mina (como el mapa de la ciudad)
viewer = siteviewer('SceneModel', STL, 'Transparency', 0.25);

% antenas reales: Hawk hélice (11 dBi), Cardinal dipolo omni (7.5 dBi)
helHawk = helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115);
omni = dipole('Length',0.028,'Width',0.001);

% colocar los AP como transmisores
txs = txsite.empty;
for k=1:size(AP,1)
    if AP(k,3)==1, ant=helHawk; pw=1.0; else, ant=omni; pw=0.2; end   % 30 vs 23 dBm
    txs(k) = txsite('cartesian','AntennaPosition',[AP(k,1);AP(k,2);2.5],...
        'Antenna',ant,'TransmitterFrequency',f0,'TransmitterPower',pw);
end
show(txs);

% modelo de ray-tracing con roca
pm = propagationModel('raytracing','Method','sbr','CoordinateSystem','cartesian',...
    'MaxNumReflections',4,'SurfaceMaterial','custom',...
    'SurfaceMaterialPermittivity',6.0,'SurfaceMaterialConductivity',0.01);

% pintar la cobertura sobre la escena (mapa de calor de RSSI)
coverage(txs, pm, 'Type','power', ...
    'SignalStrengths', -85:5:-30, ...
    'MaxRange', 60, 'Resolution', 3, ...
    'Transparency', 0.6);

disp('MAPA DE COBERTURA 3D generado. Explora con el mouse.');
% queda abierto para explorar

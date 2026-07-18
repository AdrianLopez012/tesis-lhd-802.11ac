% ver_rayos_reales.m — LO QUE FALTABA: en el Site Viewer de MATLAB,
%  · los RAYOS de verdad (ray-tracing SBR) rebotando en la roca del túnel
%  · los PATRONES REALES montados en las antenas (pattern() sobre el sitio)
% Justificación de cada paso en la consola.
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
AP  = readmatrix([TRB 'anim_aps.csv']);      % x, y, tipo, angulo_galeria
f0 = 5e9;

fprintf('[1] Escena: galería 3D real (paredes+techo herradura, %s)\n', 'galeria_rt.stl');
viewer = siteviewer('SceneModel', [TRB 'galeria_rt.stl'], 'Transparency', 0.55);

fprintf('[2] Transmisor: AP H4 con el PAR RCP-50 LHP/RHP del datasheet:\n');
fprintf('    BIDIRECCIONAL — dos hélices opuestas radiando en AMBOS sentidos de la galería.\n');
k = 4;                                        % H4
angH4 = AP(k,4);                              % dirección de su galería
ejeGal = [ -sin(angH4) cos(angH4) 0 ];
h1 = helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115,'Tilt', 90,'TiltAxis',ejeGal);
h2 = helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115,'Tilt',-90,'TiltAxis',ejeGal);
hawkBi = conformalArray('Element',{h1,h2},'ElementPosition',[0 0 0.03; 0 0 -0.03]);
tx = txsite('cartesian','AntennaPosition',[AP(k,1); AP(k,2); 2.5], ...
    'Antenna',hawkBi,'TransmitterFrequency',f0,'TransmitterPower',1.0);
show(tx);
pattern(tx, f0, 'Size', 10, 'Transparency', 0.45);   % PATRÓN BIDIRECCIONAL EN LA ESCENA

fprintf('[3] Receptores: 3 posiciones del LHD a lo largo de la galería de H4\n');
fprintf('    (12, 24 y 38 m) con antena HELI-40.\n');
u = [cos(angH4), sin(angH4)];
pm = propagationModel('raytracing','Method','sbr','CoordinateSystem','cartesian', ...
    'MaxNumReflections',5,'SurfaceMaterial','custom', ...
    'SurfaceMaterialPermittivity',6.0,'SurfaceMaterialConductivity',0.01);
fprintf('[4] Ray-tracing SBR: hasta 5 reflexiones; roca con εr=6, σ=0.01 S/m.\n');
for d = [12 24 38]
    P = [AP(k,1), AP(k,2)] + u*d;
    rx = rxsite('cartesian','AntennaPosition',[P(1); P(2); 1.2]);
    show(rx);
    rays = raytrace(tx, rx, pm);              % usa la escena del viewer
    if ~isempty(rays{1})
        plot(rays{1});                        % DIBUJA LOS RAYOS REBOTANDO
        fprintf('    d=%2d m: %d rayos (mín. pérdida %.1f dB, %d reflexiones máx.)\n', ...
            d, numel(rays{1}), min([rays{1}.PathLoss]), max([rays{1}.NumInteractions]));
    else
        fprintf('    d=%2d m: sin rayos resueltos\n', d);
    end
end

fprintf('[5] Patrón de un Cardinal cercano (EPNT-7 omni) para comparar formas.\n');
kc = 10;                                      % C5
card = dipole('Length',0.028,'Width',0.001);
tx2 = txsite('cartesian','AntennaPosition',[AP(kc,1); AP(kc,2); 2.5], ...
    'Antenna',card,'TransmitterFrequency',f0,'TransmitterPower',0.2);
show(tx2);
pattern(tx2, f0, 'Size', 8, 'Transparency', 0.45);

disp('=== LISTO: rota la escena; los colores de los rayos = pérdida de trayecto ===');
disp('Los patrones que ves montados en H4 y C5 son los calculados por método de momentos.');

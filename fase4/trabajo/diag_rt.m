try
STL='C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\galeria_nv1640.stl';
% caso minimo: tx y rx a 10 m en linea recta dentro de la galeria central
pm = propagationModel('raytracing','Method','sbr','MaxNumReflections',2);
tx = txsite('cartesian','AntennaPosition',[26;20;2],'TransmitterFrequency',5e9);
rx = rxsite('cartesian','AntennaPosition',[26;30;2]);
rays = raytrace(tx,rx,pm,'Map',STL);
fprintf('rayos con STL: %d\n', numel(rays{1}));
% sin STL (espacio libre) para confirmar que la API funciona
rays2 = raytrace(tx,rx,pm);
fprintf('rayos sin mapa: %d\n', numel(rays2{1}));
catch e
fprintf('ERR: %s\n', e.message);
end
exit;

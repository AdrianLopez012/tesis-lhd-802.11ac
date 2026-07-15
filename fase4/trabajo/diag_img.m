try
STL='C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\galeria_nv1640.stl';
pm = propagationModel('raytracing','Method','image','CoordinateSystem','cartesian','MaxNumReflections',2);
tx = txsite('cartesian','AntennaPosition',[26;2;2],'TransmitterFrequency',5e9);
for yy=[8 20 40 60 90 120]
  rx = rxsite('cartesian','AntennaPosition',[26;yy;1]);
  r = raytrace(tx,rx,pm,'Map',STL);
  fprintf('y=%d: %d rayos\n', yy, numel(r{1}));
end
catch e; fprintf('ERR: %s\n', e.message); end
exit;

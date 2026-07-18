% precalc_escena.m — precalcula UNA VEZ lo pesado y lo guarda en caché:
%   · patrones (hélice 9v -> RCP-50 bidireccional; dipolo -> EPNT-7; hélice 4v -> HELI-40 bi)
%   · rayos SBR de H4 a 3 posiciones del LHD (polilíneas extraídas)
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
AP  = readmatrix([TRB 'anim_aps.csv']);
f0 = 5e9;
az = -180:3:180; el = -90:3:90;

fprintf('1/3 patrones...\n');
p9 = pattern(helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115), f0, az, el);
pHawkBi = max(p9, flipud(p9));                       % RCP-50 bidireccional
pCard = pattern(dipole('Length',0.028,'Width',0.001), f0, az, el);
p4 = pattern(helix('Radius',0.0091,'Width',0.0016,'Turns',4,'Spacing',0.0115), f0, az, el);
pLHDBi = max(p4, flipud(p4));                        % HELI-40 bidireccional

fprintf('2/3 rayos SBR (H4 -> 3 posiciones)...\n');
k = 4; angH4 = AP(k,4);
u = [cos(angH4), sin(angH4)];
pm = propagationModel('raytracing','Method','sbr','CoordinateSystem','cartesian', ...
    'MaxNumReflections',5,'SurfaceMaterial','custom', ...
    'SurfaceMaterialPermittivity',6.0,'SurfaceMaterialConductivity',0.01);
tx = txsite('cartesian','AntennaPosition',[AP(k,1); AP(k,2); 2.5],'TransmitterFrequency',f0);
rayos = {};   % cada uno: struct(pts Nx3, pl, nref, d)
for d = [12 24 38]
    P = [AP(k,1), AP(k,2)] + u*d;
    rx = rxsite('cartesian','AntennaPosition',[P(1); P(2); 1.2]);
    rr = raytrace(tx, rx, pm, 'Map', [TRB 'galeria_rt.stl']);
    if isempty(rr{1}), fprintf('  d=%d: 0 rayos\n', d); continue; end
    for q = 1:numel(rr{1})
        R = rr{1}(q);
        pts = [AP(k,1) AP(k,2) 2.5];
        for it = 1:numel(R.Interactions)
            pts = [pts; R.Interactions(it).Location(:)'];
        end
        pts = [pts; P(1) P(2) 1.2];
        rayos{end+1} = struct('pts',pts,'pl',R.PathLoss,'nref',numel(R.Interactions),'d',d);
    end
    fprintf('  d=%d m: %d rayos\n', d, numel(rr{1}));
end

fprintf('3/4 rayos AP<->AP (enlaces de malla entre vecinos)...\n');
NA = size(AP,1);
D2 = squareform(pdist(AP(:,1:2)));
rayosAP = {};
hechos = zeros(NA);
for a = 1:NA
    [~, orden] = sort(D2(a,:));
    vecinos = orden(2:3);                      % los 2 AP más cercanos
    for b = vecinos
        if hechos(a,b) || hechos(b,a), continue; end
        hechos(a,b) = 1;
        txA = txsite('cartesian','AntennaPosition',[AP(a,1); AP(a,2); 2.5],'TransmitterFrequency',f0);
        rxB = rxsite('cartesian','AntennaPosition',[AP(b,1); AP(b,2); 2.5]);
        rr = raytrace(txA, rxB, pm, 'Map', [TRB 'galeria_rt.stl']);
        nr = 0;
        if ~isempty(rr{1})
            for q2 = 1:numel(rr{1})
                R = rr{1}(q2);
                pts = [AP(a,1) AP(a,2) 2.5];
                for it = 1:numel(R.Interactions)
                    pts = [pts; R.Interactions(it).Location(:)'];
                end
                pts = [pts; AP(b,1) AP(b,2) 2.5];
                rayosAP{end+1} = struct('pts',pts,'pl',R.PathLoss,'a',a,'b',b);
            end
            nr = numel(rr{1});
        end
        fprintf('  %d<->%d (%.0f m): %d rayos\n', a, b, D2(a,b), nr);
    end
end

fprintf('4/4 guardando cache...\n');
save([TRB 'escena_cache.mat'], 'pHawkBi','pCard','pLHDBi','az','el','rayos','rayosAP','k','angH4');
disp('PRECALC OK');
exit;

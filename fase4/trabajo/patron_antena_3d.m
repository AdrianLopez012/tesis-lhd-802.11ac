% patron_antena_3d.m v2 — genera las 3 vistas por separado (pattern crea sus
% propios ejes y no admite tiledlayout); se componen después en Python.
try
hx = helix('Radius',0.0091,'Width',0.0016,'Turns',7.5,'Spacing',0.0115);
f0 = 5.0e9;
B = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';

f1 = figure('Position',[60 60 720 620],'Color','w','Visible','off');
pattern(hx, f0);
exportgraphics(f1, [B 'pat_3d.png'], 'Resolution', 200); close(f1);

f2 = figure('Position',[60 60 620 620],'Color','w','Visible','off');
patternElevation(hx, f0, 0);
exportgraphics(f2, [B 'pat_elev.png'], 'Resolution', 200); close(f2);

f3 = figure('Position',[60 60 620 620],'Color','w','Visible','off');
patternAzimuth(hx, f0, 60);
exportgraphics(f3, [B 'pat_azim.png'], 'Resolution', 200); close(f3);
fprintf('3 VISTAS OK\n');
catch e
    fprintf('ERROR: %s\n', e.message);
end
exit;

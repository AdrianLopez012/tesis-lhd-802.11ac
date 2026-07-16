% export_patrones3d.m — genera y exporta los 3 patrones 3D nativos (batch).
TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
f0 = 5e9;

hawk = helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115);
f1 = figure('Color','w','Position',[40 40 660 540],'Visible','off');
pattern(hawk, f0);
title({'AP Hawk — antena HELI RCP-50 (11 dBi, pol. circular)','modelo: hélice axial de 9 vueltas'});
exportgraphics(f1, [TRB 'patron3d_hawk.png'], 'Resolution', 180);

card = dipole('Length',0.028,'Width',0.001);
f2 = figure('Color','w','Position',[40 40 660 540],'Visible','off');
pattern(card, f0);
title({'AP Cardinal — antena EPNT-7 (7.5 dBi, omnidireccional)','modelo: dipolo en 5 GHz'});
exportgraphics(f2, [TRB 'patron3d_cardinal.png'], 'Resolution', 180);

lhd = helix('Radius',0.0091,'Width',0.0016,'Turns',4,'Spacing',0.0115);
az = -180:3:180; el = -90:3:90;
pHel = pattern(lhd, f0, az, el);
pBi = max(pHel, flipud(pHel));
[AZ, EL] = meshgrid(az, el);
f3 = figure('Color','w','Position',[40 40 700 560],'Visible','off');
patternCustom(pBi(:), 90-EL(:), AZ(:));
title({'LHD — antena HELI-40 (4.8 dBic, pol. circular, BIDIRECCIONAL)','patrón sintetizado según datasheet: dos lóbulos opuestos'});
exportgraphics(f3, [TRB 'patron3d_lhd.png'], 'Resolution', 180);

disp('EXPORT 3 PATRONES OK');
exit;

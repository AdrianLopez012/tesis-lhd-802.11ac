% ver_patron3d_antenas.m — PATRONES 3D DE DIRECTIVIDAD NATIVOS (Antenna Toolbox)
% para las tres antenas reales del diseño (datasheets del proyecto):
%   Fig 1: Hawk — HELI RCP-50 (helicoidal axial, 11 dBi, pol. circular)
%   Fig 2: Cardinal — EPNT-7 (omnidireccional, 7.5 dBi)
%   Fig 3: LHD — HELI-40 (bidireccional túnel/NLOS, 4.8 dBic, pol. circular)
% Cada figura es el "globo" clásico con anillos az/el, dBi y la antena dibujada.
f0 = 5e9;

% ---------- Fig 1: HELI RCP-50 (Hawk) — hélice axial ----------
hawk = helix('Radius',0.0091,'Width',0.0016,'Turns',9,'Spacing',0.0115);
figure('Name','Hawk — HELI RCP-50 (modelo helicoidal axial)','Color','w','Position',[40 380 640 520]);
pattern(hawk, f0);
title({'AP Hawk — antena HELI RCP-50 (11 dBi, pol. circular)','modelo: hélice axial de 9 vueltas — patrón 3D de directividad'});

% ---------- Fig 2: EPNT-7 (Cardinal) — omni ----------
card = dipole('Length',0.028,'Width',0.001);
figure('Name','Cardinal — EPNT-7 (omni)','Color','w','Position',[700 380 640 520]);
pattern(card, f0);
title({'AP Cardinal — antena EPNT-7 (7.5 dBi, omnidireccional)','modelo: dipolo en 5 GHz — la dona es el patrón omni real'});

% ---------- Fig 3: HELI-40 (LHD) — bidireccional ----------
% El datasheet: 4.8 dBic, polarización circular, BI-DIRECCIONAL (túnel/NLOS).
% Se sintetiza el patrón bidireccional (lóbulo axial + espejo) y se grafica
% con patternCustom (globo 3D nativo).
lhd = helix('Radius',0.0091,'Width',0.0016,'Turns',4,'Spacing',0.0115);
az = -180:3:180; el = -90:3:90;
pHel = pattern(lhd, f0, az, el);
pBi = max(pHel, flipud(pHel));                 % dos lóbulos opuestos (bi-direccional)
[AZ, EL] = meshgrid(az, el);
figure('Name','LHD — HELI-40 (bidireccional)','Color','w','Position',[370 40 700 560]);
patternCustom(pBi(:), 90-EL(:), AZ(:));        % globo 3D nativo (theta = 90-el)
title({'LHD — antena HELI-40 (4.8 dBic, pol. circular, BI-DIRECCIONAL)','patrón sintetizado según datasheet: dos lóbulos opuestos a lo largo del túnel'});

disp('=== 3 FIGURAS ABIERTAS: rota cada globo con el mouse ===');
disp('Hawk RCP-50 (axial) · Cardinal EPNT-7 (dona omni) · LHD HELI-40 (bidireccional)');

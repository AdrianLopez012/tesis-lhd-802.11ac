% inventario_licencias.m — lista TODAS las toolboxes instaladas y cuales
% tienen licencia utilizable (probando license('checkout')).
fprintf('===== TOOLBOXES INSTALADAS Y LICENCIA =====\n\n');
v = ver;
% mapa nombre-producto -> feature de licencia (los mas relevantes para la tesis)
feats = containers.Map();
feats('WLAN Toolbox')='WLAN_Toolbox';
feats('5G Toolbox')='5G_Toolbox';
feats('Communications Toolbox')='Communication_Toolbox';
feats('Antenna Toolbox')='Antenna_Toolbox';
feats('Phased Array System Toolbox')='Phased_Array_System_Toolbox';
feats('RF Toolbox')='RF_Toolbox';
feats('RF PCB Toolbox')='RF_PCB_Toolbox';
feats('Signal Processing Toolbox')='Signal_Toolbox';
feats('DSP System Toolbox')='Signal_Blocks';
feats('Simulink')='SIMULINK';
feats('Statistics and Machine Learning Toolbox')='Statistics_Toolbox';
feats('Parallel Computing Toolbox')='Distrib_Computing_Toolbox';
feats('Optimization Toolbox')='Optimization_Toolbox';
feats('Mapping Toolbox')='Map_Toolbox';
feats('Sensor Fusion and Tracking Toolbox')='Tracking_Toolbox';
feats('Navigation Toolbox')='Navigation_Toolbox';
feats('Automated Driving Toolbox')='Automated_Driving_Toolbox';
feats('Radar Toolbox')='Radar_Toolbox';
feats('Satellite Communications Toolbox')='Satellite_Comm_Toolbox';

fprintf('%-48s | Instalada | Licencia\n', 'Toolbox');
fprintf('%s\n', repmat('-',1,72));
for i=1:numel(v)
    nm = v(i).Name;
    lic = '-';
    if isKey(feats, nm)
        try
            ok = license('checkout', feats(nm));
            lic = ternario(ok);
        catch
            lic = '?';
        end
    end
    fprintf('%-48s | %-9s | %s\n', nm(1:min(48,end)), 'SI', lic);
end
fprintf('\nTotal toolboxes instaladas: %d\n', numel(v)-1);
exit;

function s=ternario(x); if x, s='UTILIZABLE'; else, s='sin licencia'; end; end

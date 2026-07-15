tbs = {'WLAN Toolbox','Communications Toolbox','Antenna Toolbox','Phased Array System Toolbox','RF Toolbox','RF PCB Toolbox','5G Toolbox','Signal Processing Toolbox','DSP System Toolbox','Parallel Computing Toolbox','Statistics and Machine Learning Toolbox'};
lic = {'WLAN_Toolbox','Communication_Toolbox','Antenna_Toolbox','Phased_Array_System_Toolbox','RF_Toolbox','RF_PCB_Toolbox','5G_Toolbox','Signal_Toolbox','Signal_Blocks','Distrib_Computing_Toolbox','Statistics_Toolbox'};
fprintf('=== Toolboxes disponibles ===\n');
for i=1:numel(tbs)
  fprintf('  [%s] %s\n', ternario(license('test',lic{i})), tbs{i});
end
function s=ternario(x); if x, s='SI'; else, s='no'; end; end
exit;

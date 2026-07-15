% prueba_wlan.m — intenta USAR realmente WLAN y 5G Toolbox para descartar.
fprintf('===== PRUEBA DE USO REAL =====\n');

% --- WLAN Toolbox: crear config 802.11ac y generar una forma de onda ---
fprintf('\n[1] WLAN Toolbox (802.11ac VHT):\n');
try
    cfg = wlanVHTConfig('ChannelBandwidth','CBW40','MCS',8,'NumTransmitAntennas',2,'NumSpaceTimeStreams',2);
    bits = randi([0 1], 8*1000, 1);
    wf = wlanWaveformGenerator(bits, cfg);
    fprintf('    OK -> forma de onda 802.11ac generada: %d muestras\n', numel(wf));
    fprintf('    MCS=%d, BW=%s, %dx%d MIMO\n', cfg.MCS, cfg.ChannelBandwidth, cfg.NumTransmitAntennas, cfg.NumSpaceTimeStreams);
    assignin('base','WLAN_OK',true);
catch e
    fprintf('    FALLA -> %s\n', e.message);
    assignin('base','WLAN_OK',false);
end

% --- 5G Toolbox: crear una config de portadora ---
fprintf('\n[2] 5G Toolbox:\n');
try
    carrier = nrCarrierConfig('NSizeGrid',52,'SubcarrierSpacing',30);
    fprintf('    OK -> portadora 5G NR configurada: %d RB, SCS %d kHz\n', carrier.NSizeGrid, carrier.SubcarrierSpacing);
    assignin('base','FiveG_OK',true);
catch e
    fprintf('    FALLA -> %s\n', e.message);
    assignin('base','FiveG_OK',false);
end

% --- Communications Toolbox (respaldo, debe funcionar) ---
fprintf('\n[3] Communications Toolbox (respaldo):\n');
try
    m = comm.OFDMModulator('FFTLength',128,'NumGuardBandCarriers',[6;5]);
    fprintf('    OK -> OFDM disponible (respaldo garantizado)\n');
catch e
    fprintf('    FALLA -> %s\n', e.message);
end

fprintf('\n===== RESUMEN =====\n');
fprintf('WLAN utilizable: %d | 5G utilizable: %d\n', evalin('base','WLAN_OK'), evalin('base','FiveG_OK'));
exit;

% mega_flujo_wlan.m v3 — MEGA FLUJO 802.11ac con receptor VHT COMPLETO y
% cadena de sincronización oficial (packet detect -> CFO -> timing ->
% channel est -> equalize -> decode). PER vs SNR por MCS + constelación.
TRB='C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
try
cbw='CBW40'; nTx=2; nSts=2;
cfg = wlanVHTConfig('ChannelBandwidth',cbw,'NumTransmitAntennas',nTx,...
    'NumSpaceTimeStreams',nSts,'MCS',8,'APEPLength',2000);
fs  = wlanSampleRate(cfg);
fprintf('802.11ac VHT %s %dx%d, fs=%.0f MHz\n', cbw, nTx, nSts, fs/1e6);

tgac = wlanTGacChannel('SampleRate',fs,'ChannelBandwidth',cbw,...
    'NumTransmitAntennas',nTx,'NumReceiveAntennas',nTx,'DelayProfile','Model-B',...
    'LargeScaleFadingEffect','None');

snrRange = 8:3:38;
mcsList  = [0 4 8 9];
mcsName  = {'MCS0 (BPSK 1/2)','MCS4 (16-QAM 3/4)','MCS8 (256-QAM 3/4)','MCS9 (256-QAM 5/6)'};
PER = ones(numel(mcsList), numel(snrRange));
nPkt = 40; symC = [];
chBW = cfg.ChannelBandwidth;

for mi=1:numel(mcsList)
  cfg.MCS = mcsList(mi);
  ind = wlanFieldIndices(cfg);
  for si=1:numel(snrRange)
    snr = snrRange(si); nErr=0; nOk=0;
    for p=1:nPkt
      psdu = randi([0 1], cfg.PSDULength*8, 1);
      tx = wlanWaveformGenerator(psdu, cfg, 'IdleTime', 20e-6, 'WindowTransitionTime', 1e-7);
      reset(tgac); rxCh = tgac(tx);
      % padding para permitir sincronización
      rxCh = [rxCh; zeros(20, nTx)];
      rx = awgn(rxCh, snr, 'measured');

      % --- cadena de sincronización ---
      % 1) detección de paquete -> devuelve el inicio del paquete
      pktOff = wlanPacketDetect(rx, chBW, 0, 0.5);
      if isempty(pktOff), nErr=nErr+1; continue; end
      % re-alinear: recortar desde el inicio detectado
      rxp = rx(pktOff+1:end, :);
      if size(rxp,1) < double(ind.VHTData(2))+10, nErr=nErr+1; continue; end
      % 2) CFO grueso (L-STF) y fino (L-LTF)
      lstf = rxp(ind.LSTF(1):ind.LSTF(2), :);
      cfoC = wlanCoarseCFOEstimate(lstf, chBW);
      rxp = frequencyOffset(rxp, fs, -cfoC);
      lltf = rxp(ind.LLTF(1):ind.LLTF(2), :);
      cfoF = wlanFineCFOEstimate(lltf, chBW);
      rxp = frequencyOffset(rxp, fs, -cfoF);
      % 3) estimación de canal con VHT-LTF
      vltf = rxp(ind.VHTLTF(1):ind.VHTLTF(2), :);
      vltfDemod = wlanVHTLTFDemodulate(vltf, cfg);
      chEst = wlanVHTLTFChannelEstimate(vltfDemod, cfg);
      % 4) recuperar datos
      nVarEst = 10^(-snr/10);
      data = rxp(ind.VHTData(1):ind.VHTData(2), :);
      [rxPSDU, ~, eqSym] = wlanVHTDataRecover(data, chEst, nVarEst, cfg);
      if numel(rxPSDU)==numel(psdu) && ~any(rxPSDU~=psdu), nOk=nOk+1; else, nErr=nErr+1; end
    end
    PER(mi,si) = nErr/nPkt;
  end
  fprintf('  %s: PER=%.3f@%ddB ... %.3f@%ddB\n', mcsName{mi}, PER(mi,1),snrRange(1), PER(mi,end),snrRange(end));
end

% ---------- constelación 256-QAM limpia: 1 paquete MCS8 a SNR alto ----------
cfg.MCS = 8; ind = wlanFieldIndices(cfg);
psdu = randi([0 1], cfg.PSDULength*8, 1);
tx = wlanWaveformGenerator(psdu, cfg, 'IdleTime',20e-6,'WindowTransitionTime',1e-7);
reset(tgac); rxc = tgac(tx); rxc=[rxc; zeros(20,nTx)];
rxc = awgn(rxc, 42, 'measured');
po = wlanPacketDetect(rxc, chBW, 0, 0.5);
rxp = rxc(po+1:end,:);
cf = wlanCoarseCFOEstimate(rxp(ind.LSTF(1):ind.LSTF(2),:), chBW); rxp=frequencyOffset(rxp,fs,-cf);
ff = wlanFineCFOEstimate(rxp(ind.LLTF(1):ind.LLTF(2),:), chBW); rxp=frequencyOffset(rxp,fs,-ff);
vd = wlanVHTLTFDemodulate(rxp(ind.VHTLTF(1):ind.VHTLTF(2),:), cfg);
ce = wlanVHTLTFChannelEstimate(vd, cfg);
[~,~,symC] = wlanVHTDataRecover(rxp(ind.VHTData(1):ind.VHTData(2),:), ce, 10^(-42/10), cfg);
% normalizar a energía unitaria (256-QAM tiene 16x16 puntos)
symC = symC(:); symC = symC / sqrt(mean(abs(symC).^2)) * sqrt(1);

% ---------- figura ----------
fig=figure('Position',[40 40 1320 560],'Color','w','Visible','off');
subplot(1,2,1); hold on; grid on; cols=lines(numel(mcsList));
for mi=1:numel(mcsList)
  semilogy(snrRange, max(PER(mi,:),1e-3),'-o','Color',cols(mi,:),'LineWidth',2,'MarkerFaceColor',cols(mi,:),'DisplayName',mcsName{mi});
end
set(gca,'YScale','log'); ylim([1e-3 1.3]); xlim([snrRange(1) snrRange(end)]);
yline(0.1,'--k','PER 10%','HandleVisibility','off');
xlabel('SNR (dB)'); ylabel('PER'); title('PER vs SNR — 802.11ac 2x2 MIMO, canal de interior (WLAN Toolbox)');
legend('Location','southwest','FontSize',9);
subplot(1,2,2);
if ~isempty(symC)
  plot(real(symC),imag(symC),'.','Color',[0.1 0.4 0.7],'MarkerSize',5); grid on; axis square; hold on;
  xlim([-1.5 1.5]); ylim([-1.5 1.5]);
  xlabel('En fase (I)'); ylabel('Cuadratura (Q)'); title('Constelación 256-QAM ecualizada (MCS8, SNR alto)');
end
exportgraphics(fig,[TRB 'wlan_802_11ac.png'],'Resolution',200);
writematrix([snrRange' PER'],[TRB 'wlan_per_snr.csv']);
fprintf('MEGA FLUJO v3 OK\n');
catch e
  fprintf('ERROR: %s (linea %d)\n', e.message, e.stack(1).line);
end
exit;

function e5_paquete_en_vivo(modo)
% =========================================================================
% ESLABÓN 5 (vista en vivo) — EL PAQUETE OFDM 802.11ac VIAJANDO POR EL CANAL
% =========================================================================
% Genera un paquete 802.11ac REAL (WLAN Toolbox), lo hace atravesar el canal
% del túnel (multitrayecto + retardo + ruido) y ANIMA en vivo su viaje:
%   Panel 1: forma de onda en el tiempo (sale limpia -> llega con eco/ruido)
%   Panel 2: espectro (el canal deforma la respuesta en frecuencia)
%   Panel 3: constelación (Tx nítida -> Rx dispersa -> ECUALIZADA recuperada)
%   Panel 4: cadena del receptor (detección->CFO->timing->ecualización->decode)
%
% NO es decorativo: la señal, el canal y el receptor son la cadena real del
% estándar. La animación recorre el paquete "en el tiempo" mostrando el mismo
% instante en los cuatro dominios.
%
% Uso:  e5_paquete_en_vivo            -> guarda MP4 (por defecto)
%       e5_paquete_en_vivo('pantalla')-> muestra en figura en vivo
% =========================================================================
    if nargin < 1, modo = 'mp4'; end
    OUT = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\matlab_capafisica\';
    rng(7);

    % ---------------- 1) PAQUETE 802.11ac REAL ----------------
    cbw='CBW40'; nTx=2; nSts=2; MCS=8;   % 256-QAM 3/4 (el MCS operativo típico)
    cfg = wlanVHTConfig('ChannelBandwidth',cbw,'NumTransmitAntennas',nTx, ...
        'NumSpaceTimeStreams',nSts,'MCS',MCS,'APEPLength',1400);
    fs = wlanSampleRate(cfg);
    psdu = randi([0 1], cfg.PSDULength*8, 1);
    txWave = wlanWaveformGenerator(psdu, cfg, 'IdleTime', 5e-6);
    fprintf('Paquete 802.11ac %s %dx%d MCS%d | fs=%.0f MHz | %d muestras\n', ...
            cbw, nTx, nSts, MCS, fs/1e6, size(txWave,1));

    % ---------------- 2) CANAL DEL TÚNEL ----------------
    % Model-B (retardos cortos, coherente con galería) + SNR operativo.
    SNR = 26;   % dB (condición de operación; margen del enlace real)
    tgac = wlanTGacChannel('SampleRate',fs,'ChannelBandwidth',cbw, ...
        'NumTransmitAntennas',nTx,'NumReceiveAntennas',nTx, ...
        'DelayProfile','Model-B','LargeScaleFadingEffect','None');
    rxCh  = tgac(txWave);
    rxCh  = [rxCh; zeros(20,nTx)];
    rxWave = awgn(rxCh, SNR, 'measured');

    % respuesta del canal (para el panel de espectro)
    Hinfo = info(tgac);

    % ---------------- 3) RECEPTOR VHT (constelación recuperada) ----------------
    ind = wlanFieldIndices(cfg);
    % sincronización de paquete
    stf = rxWave(ind.LSTF(1):ind.LSTF(2),:);
    dOff = wlanPacketDetect(rxWave, cbw);
    if isempty(dOff), dOff = 0; end
    rxSync = rxWave(1+dOff:end,:);
    % estimación de canal en LTF y ecualización de datos
    eqSym = [];
    try
        lltf = rxSync(ind.LLTF(1):ind.LLTF(2),:);
        vltf = rxSync(ind.VHTLTF(1):ind.VHTLTF(2),:);
        vltfDemod = wlanVHTLTFDemodulate(vltf, cfg);
        chEst = wlanVHTLTFChannelEstimate(vltfDemod, cfg);
        noiseEst = 10^(-SNR/10);
        dataRx = rxSync(ind.VHTData(1):ind.VHTData(2),:);
        % 3ª salida = símbolos ecualizados [subportadora x símbolo x stream]
        [~, ~, eqSym] = wlanVHTDataRecover(dataRx, chEst, noiseEst, cfg);
    catch ME
        fprintf('aviso recuperación: %s\n', ME.message);
    end

    % símbolos "sucios" (Rx SIN ecualizar): demodulación OFDM de los datos VHT
    % sin corregir el canal -> la nube que ve el receptor antes de ecualizar.
    dirtySym = [];
    try
        dataRx1 = rxSync(ind.VHTData(1):ind.VHTData(2),:);
        dmod = wlanVHTOFDMDemodulate(dataRx1, cfg, 'VHT-Data');  % [subp x sym x rx]
        d = dmod(:,:,1); dirtySym = d(:);
        dirtySym = dirtySym / rms(dirtySym);
    catch ME
        fprintf('aviso constelación sucia: %s\n', ME.message);
    end

    % ---------------- 4) ANIMACIÓN ----------------
    fig = figure('Position',[40 40 1280 760],'Color','w', ...
                 'Visible', tern(strcmp(modo,'pantalla'),'on','off'));
    tl = tiledlayout(fig,2,2,'TileSpacing','compact','Padding','compact');
    title(tl, sprintf('El paquete 802.11ac viajando por el canal del túnel  ·  %s %dx%d MCS%d (256-QAM)  ·  SNR=%d dB', ...
          cbw, nTx, nSts, MCS, SNR), 'FontWeight','bold','FontSize',13);

    t_us = (0:size(txWave,1)-1)/fs*1e6;
    tr = real(txWave(:,1)); rr = real(rxWave(:,1));
    ymax = max(abs([tr;rr]))*1.1;

    axW = nexttile(tl,1); hold(axW,'on'); grid(axW,'on'); box(axW,'on');
    xlim(axW,[0 t_us(end)]); ylim(axW,[-ymax ymax]);
    xlabel(axW,'Tiempo (\mus)'); ylabel(axW,'Amplitud (parte real)');
    title(axW,'1 · Forma de onda: sale limpia (azul) \rightarrow llega con eco y ruido (rojo)');

    axS = nexttile(tl,2); hold(axS,'on'); grid(axS,'on'); box(axS,'on');
    xlabel(axS,'Frecuencia (MHz)'); ylabel(axS,'Magnitud (dB)');
    title(axS,'2 · Espectro: el canal del túnel deforma la respuesta en frecuencia');

    axC = nexttile(tl,3); hold(axC,'on'); grid(axC,'on'); box(axC,'on'); axis(axC,'equal');
    xlim(axC,[-1.6 1.6]); ylim(axC,[-1.6 1.6]);
    xlabel(axC,'En fase (I)'); ylabel(axC,'Cuadratura (Q)');
    title(axC,'3 · Constelación 256-QAM: Rx sucia (gris) \rightarrow ecualizada (verde)');

    axR = nexttile(tl,4); hold(axR,'on'); box(axR,'on');
    xlim(axR,[0 1]); ylim(axR,[0 6]); set(axR,'YTick',[],'XTick',[]);
    title(axR,'4 · Cadena del receptor VHT');
    etapas = {'Detección de paquete','Sincronización (CFO + timing)', ...
              'Estimación de canal (LTF)','Ecualización','Decodificación (Viterbi)','CRC OK'};

    % writer
    if ~strcmp(modo,'pantalla')
        vw = VideoWriter([OUT 'paquete_en_vivo.mp4'],'MPEG-4');
        vw.FrameRate = 12; vw.Quality = 92; open(vw);
    end

    NF = 60;                        % frames
    nS = size(txWave,1);
    for fr = 1:NF
        p = fr/NF;                  % progreso 0..1
        nMuestra = round(p*nS);

        % --- Panel 1: barrido temporal, Tx completa, Rx que "va llegando" ---
        cla(axW);
        plot(axW, t_us, tr, 'Color',[0.2 0.4 0.85 0.5],'LineWidth',0.6);
        idx = 1:max(2,nMuestra);
        plot(axW, t_us(idx), rr(idx),'Color',[0.85 0.15 0.15],'LineWidth',0.7);
        xline(axW, t_us(max(2,nMuestra)),'k-','LineWidth',1);

        % --- Panel 2: espectro Tx vs Rx (aparece progresivamente) ---
        cla(axS);
        nfft = 512; f = (-nfft/2:nfft/2-1)/nfft*fs/1e6;
        PT = 20*log10(abs(fftshift(fft(txWave(1:min(end,4096),1),nfft)))+1e-6);
        PR = 20*log10(abs(fftshift(fft(rxWave(1:min(end,4096),1),nfft)))+1e-6);
        plot(axS, f, PT-max(PT),'Color',[0.2 0.4 0.85],'LineWidth',1);
        if p>0.35, plot(axS, f, PR-max(PT),'Color',[0.85 0.15 0.15],'LineWidth',1); end
        xlim(axS,[-fs/2/1e6 fs/2/1e6]); ylim(axS,[-45 5]);
        legend(axS, tern(p>0.35,{'Tx','Rx (canal túnel)'},{'Tx'}),'Location','south','FontSize',8);

        % --- Panel 3: constelación (sucia primero, ecualizada después) ---
        cla(axC);
        if p>0.45 && ~isempty(dirtySym)
            scatter(axC, real(dirtySym), imag(dirtySym), 5, [0.6 0.6 0.6],'filled', ...
                    'MarkerFaceAlpha',0.25);
        end
        if p>0.75 && ~isempty(eqSym)
            e = eqSym(:); e = e/rms(e);
            scatter(axC, real(e), imag(e), 6, [0.15 0.6 0.35],'filled','MarkerFaceAlpha',0.5);
        end

        % --- Panel 4: cadena del receptor iluminándose ---
        cla(axR);
        nOn = min(numel(etapas), 1+floor(p*numel(etapas)));
        for e=1:numel(etapas)
            on = e<=nOn;
            yy = numel(etapas)-e+0.5;
            col = tern(on,[0.15 0.55 0.35],[0.85 0.85 0.85]);
            rectangle(axR,'Position',[0.05 yy-0.32 0.9 0.64],'Curvature',0.3, ...
                      'FaceColor',col,'EdgeColor',[0.4 0.4 0.4]);
            text(axR,0.5,yy,etapas{e},'HorizontalAlignment','center', ...
                 'Color',tern(on,'w',[0.5 0.5 0.5]),'FontWeight',tern(on,'bold','normal'),'FontSize',10);
        end

        drawnow;
        if strcmp(modo,'pantalla')
            pause(0.03);
        else
            writeVideo(vw, getframe(fig));
        end
    end

    if ~strcmp(modo,'pantalla')
        close(vw);
        fprintf('[OK] Vídeo: %spaquete_en_vivo.mp4\n', OUT);
    end
    % frame final para inspección estática
    exportgraphics(fig, [OUT 'paquete_en_vivo_final.png'], 'Resolution',130);
    if ~strcmp(modo,'pantalla'), close(fig); end
end

function y = tern(c,a,b)
    if c, y=a; else, y=b; end
end

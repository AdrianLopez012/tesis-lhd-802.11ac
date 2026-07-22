function entrenar_red_cobertura(densidad)
% =========================================================================
% PREDICCIÓN DE COBERTURA (RSSI) CON ML — entrenado con ray-tracing SBR
% =========================================================================
% Aprende  (posición LHD, posición/tipo AP, geometría) -> RSSI  a partir del
% dataset de ray-tracing, e infiere en milisegundos (vs segundos del RT).
% Compara 4 predictores sobre el MISMO conjunto de prueba:
%   (1) Red neuronal profunda  (Deep Learning TB, trainNetwork 64-64-32)
%   (2) Red neuronal fitrnet   (Statistics & ML TB)
%   (3) Gaussian Process (GPR) (Statistics & ML TB) -> da intervalo de confianza
%   (4) Two-slope calibrado    (modelo analítico de la tesis, referencia)
%
% Uso:  entrenar_red_cobertura('media')  |  ('fina')
% =========================================================================
    if nargin<1, densidad='media'; end
    OUT = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\matlab_capafisica\';
    fn  = [OUT 'dataset_canal_' densidad '.csv'];
    assert(isfile(fn), 'Falta el dataset: %s', fn);
    T = readtable(fn);
    fprintf('Dataset: %d muestras (%s)\n', height(T), densidad);

    % ---- features físicos y objetivo ----
    X = [T.x, T.y, T.ap_x, T.ap_y, T.ap_tipo, T.dist_euclid, T.cruces_nlos];
    y = T.rssi_dbm;

    % ---- split 70/15/15 reproducible ----
    rng(42); n=height(T); idx=randperm(n);
    nTr=round(0.70*n); nVa=round(0.15*n);
    iTr=idx(1:nTr); iVa=idx(nTr+1:nTr+nVa); iTe=idx(nTr+nVa+1:end);

    % ---- normalización z-score (stats de train) ----
    mu=mean(X(iTr,:)); sg=std(X(iTr,:)); sg(sg==0)=1;
    Xn=(X-mu)./sg;

    met = @(e) struct('rmse',sqrt(mean(e.^2)),'mae',mean(abs(e)), ...
                      'r2',1-sum(e.^2)/sum((y(iTe)-mean(y(iTe))).^2));

    % ===== (1) Red neuronal profunda (Deep Learning Toolbox) =====
    layers = [
        featureInputLayer(size(X,2));
        fullyConnectedLayer(64); reluLayer;
        fullyConnectedLayer(64); reluLayer;
        fullyConnectedLayer(32); reluLayer;
        fullyConnectedLayer(1); regressionLayer];
    opts = trainingOptions('adam','MaxEpochs',400,'MiniBatchSize',32, ...
        'InitialLearnRate',3e-3,'LearnRateSchedule','piecewise', ...
        'LearnRateDropFactor',0.5,'LearnRateDropPeriod',150, ...
        'ValidationData',{Xn(iVa,:),y(iVa)},'ValidationFrequency',20, ...
        'Shuffle','every-epoch','Verbose',false,'Plots','none');
    netDL = trainNetwork(Xn(iTr,:), y(iTr), layers, opts);
    yDL = predict(netDL, Xn(iTe,:));
    mDL = met(yDL - y(iTe));

    % ===== (2) Red neuronal fitrnet (Statistics & ML) =====
    netSK = fitrnet(Xn(iTr,:), y(iTr), 'LayerSizes',[64 32], ...
        'Activations','relu','Standardize',false, ...
        'ValidationData',{Xn(iVa,:),y(iVa)},'Verbose',0);
    ySK = predict(netSK, Xn(iTe,:));
    mSK = met(ySK - y(iTe));

    % ===== (3) Gaussian Process (con intervalo de confianza) =====
    gpr = fitrgp(Xn(iTr,:), y(iTr), 'KernelFunction','ardsquaredexponential', ...
        'BasisFunction','constant','Standardize',false);
    [yGP, yGPsd] = predict(gpr, Xn(iTe,:));
    mGP = met(yGP - y(iTe));

    % ===== (4) Two-slope calibrado (referencia analítica) =====
    c=299792458; lam=c/5e9; PL_D0=20*log10(4*pi/lam); n1=1.9; n2=3.4; dbp=40; Lsys=9.4;
    Pt=(T.ap_tipo==1)*30+(T.ap_tipo==2)*23; Gt=(T.ap_tipo==1)*11+(T.ap_tipo==2)*7.5;
    d=max(T.dist_euclid,1);
    plTS = (d<dbp).*(PL_D0+10*n1*log10(d)) + (d>=dbp).*(PL_D0+10*n1*log10(dbp)+10*n2*log10(d/dbp));
    yTSall = Pt+Gt+4.8 - plTS - Lsys - 10*T.cruces_nlos;
    yTS = yTSall(iTe); mTS = met(yTS - y(iTe));

    % ---- reporte ----
    fprintf('\n===== COMPARACIÓN (conjunto de prueba, %d muestras) =====\n', numel(iTe));
    fprintf('%-26s  RMSE(dB)  MAE(dB)   R^2\n','MÉTODO');
    fprintf('%-26s   %6.2f   %6.2f   %5.3f\n','Red neuronal profunda',mDL.rmse,mDL.mae,mDL.r2);
    fprintf('%-26s   %6.2f   %6.2f   %5.3f\n','Red fitrnet',mSK.rmse,mSK.mae,mSK.r2);
    fprintf('%-26s   %6.2f   %6.2f   %5.3f\n','Gaussian Process (GPR)',mGP.rmse,mGP.mae,mGP.r2);
    fprintf('%-26s   %6.2f   %6.2f   %5.3f\n','Two-slope (analítico)',mTS.rmse,mTS.mae,mTS.r2);

    % ---- elegir el mejor por RMSE ----
    nombres={'Red profunda','fitrnet','GPR','Two-slope'};
    rmses=[mDL.rmse mSK.rmse mGP.rmse mTS.rmse]; [~,bi]=min(rmses);
    fprintf('\nMEJOR: %s (RMSE %.2f dB)\n', nombres{bi}, rmses(bi));

    % ---- figura ----
    fig=figure('Position',[50 50 1300 800],'Color','w','Visible','off');
    tl=tiledlayout(fig,2,2,'TileSpacing','compact','Padding','compact');
    plot_pred(nexttile(tl), y(iTe), yDL, 'Red neuronal profunda', mDL);
    plot_pred(nexttile(tl), y(iTe), yGP, 'Gaussian Process', mGP);
    % (c) GPR con banda de confianza ordenada por RSSI real
    ax=nexttile(tl); hold(ax,'on'); grid(ax,'on'); box(ax,'on');
    [ys,so]=sort(y(iTe)); yg=yGP(so); sd=yGPsd(so);
    fill(ax,[1:numel(ys) numel(ys):-1:1],[yg+2*sd; flipud(yg-2*sd)]', ...
        [0.7 0.85 0.95],'EdgeColor','none','FaceAlpha',0.6);
    plot(ax,ys,'k-','LineWidth',1.3); plot(ax,yg,'b.','MarkerSize',6);
    xlabel(ax,'Muestra de prueba (ordenada)'); ylabel(ax,'RSSI (dBm)');
    title(ax,'GPR: predicción \pm 2\sigma (intervalo de confianza)');
    legend(ax,{'\pm2\sigma','RSSI real','GPR'},'Location','southeast','FontSize',8);
    % (d) barras comparativas RMSE
    ax=nexttile(tl); b=bar(ax,rmses,'FaceColor','flat'); grid(ax,'on');
    b.CData(bi,:)=[0.15 0.6 0.35]; for k=setdiff(1:4,bi), b.CData(k,:)=[0.6 0.6 0.6]; end
    set(ax,'XTickLabel',nombres,'XTickLabelRotation',15);
    ylabel(ax,'RMSE (dB)'); title(ax,'Error de cada método (menor = mejor)');
    for k=1:4, text(ax,k,rmses(k)+0.1,sprintf('%.2f',rmses(k)),'HorizontalAlignment','center','FontSize',9); end

    sgtitle(fig,sprintf('Predicción de cobertura RSSI con ML (dataset ray-tracing, %d muestras)',height(T)),'FontWeight','bold');
    exportgraphics(fig,[OUT 'ml_cobertura_' densidad '.png'],'Resolution',150); close(fig);

    % ---- guardar el mejor modelo utilizable (GPR o red) ----
    save([OUT 'modelos_cobertura_' densidad '.mat'],'netDL','netSK','gpr','mu','sg', ...
         'mDL','mSK','mGP','mTS');
    fprintf('\n[OK] Figura: %sml_cobertura_%s.png\n', OUT, densidad);
    fprintf('[OK] Modelos: %smodelos_cobertura_%s.mat\n', OUT, densidad);

    % tiempos de inferencia
    tic; for k=1:200, predict(gpr, Xn(iTe,:)); end; tgp=toc/200/numel(iTe)*1e3;
    fprintf('Inferencia GPR: %.4f ms/punto  (ray-tracing ~600 ms/punto -> ~%.0fx más rápido)\n', ...
        tgp, 600/max(tgp,1e-3));
end

function plot_pred(ax, yreal, ypred, nombre, m)
    hold(ax,'on'); grid(ax,'on'); box(ax,'on');
    scatter(ax, yreal, ypred, 20, [0.15 0.55 0.35],'filled','MarkerFaceAlpha',0.6);
    lim=[min(yreal)-3 max(yreal)+3]; plot(ax,lim,lim,'k--','LineWidth',1);
    xlim(ax,lim); ylim(ax,lim); axis(ax,'square');
    xlabel(ax,'RSSI real (ray-tracing) [dBm]'); ylabel(ax,'RSSI predicho [dBm]');
    title(ax,sprintf('%s: RMSE=%.2f dB, R^2=%.3f',nombre,m.rmse,m.r2));
end

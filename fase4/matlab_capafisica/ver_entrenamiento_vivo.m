function ver_entrenamiento_vivo(densidad)
% =========================================================================
% VER EL ENTRENAMIENTO DE LA RED NEURONAL EN VIVO
% =========================================================================
% Abre la ventana animada de MATLAB donde se ve, época a época, cómo el error
% de la red BAJA mientras aprende a predecir el RSSI. Al terminar, dibuja el
% MAPA DE COBERTURA que la red aprendió (predice toda la galería en ms).
%
% Ejecutar en MATLAB (NO en -batch, para ver la ventana):
%   >> ver_entrenamiento_vivo('fina')
% =========================================================================
    if nargin<1, densidad='fina'; end
    OUT = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\matlab_capafisica\';
    T = readtable([OUT 'dataset_canal_' densidad '.csv']);
    fprintf('Dataset: %d muestras — se abrirá la ventana de entrenamiento en vivo\n', height(T));

    % ---------- 1) preparar datos (entradas -> salida) ----------
    X = [T.x, T.y, T.ap_x, T.ap_y, T.ap_tipo, T.dist_euclid, T.cruces_nlos];
    y = T.rssi_dbm;
    rng(42); n=height(T); idx=randperm(n);
    nTr=round(0.7*n); nVa=round(0.15*n);
    iTr=idx(1:nTr); iVa=idx(nTr+1:nTr+nVa); iTe=idx(nTr+nVa+1:end);
    mu=mean(X(iTr,:)); sg=std(X(iTr,:)); sg(sg==0)=1;
    Xn=(X-mu)./sg;

    % ---------- 2) definir la red ----------
    layers = [
        featureInputLayer(size(X,2));
        fullyConnectedLayer(64); reluLayer;
        fullyConnectedLayer(64); reluLayer;
        fullyConnectedLayer(32); reluLayer;
        fullyConnectedLayer(1); regressionLayer];

    % ---------- 3) opciones CON VENTANA EN VIVO ----------
    % 'Plots','training-progress' abre la ventana animada del error por época.
    opts = trainingOptions('adam', ...
        'MaxEpochs',400, 'MiniBatchSize',32, 'InitialLearnRate',3e-3, ...
        'LearnRateSchedule','piecewise','LearnRateDropFactor',0.5,'LearnRateDropPeriod',150, ...
        'ValidationData',{Xn(iVa,:),y(iVa)}, 'ValidationFrequency',10, ...
        'Shuffle','every-epoch', 'Verbose',true, ...
        'Plots','training-progress');          % <-- LA VENTANA EN VIVO

    fprintf('\n>> Entrenando... observa la ventana: la curva de error baja = la red aprende.\n');
    net = trainNetwork(Xn(iTr,:), y(iTr), layers, opts);

    % ---------- 4) evaluar ----------
    yhat = predict(net, Xn(iTe,:));
    e = yhat - y(iTe);
    rmse = sqrt(mean(e.^2)); R2 = 1-sum(e.^2)/sum((y(iTe)-mean(y(iTe))).^2);
    fprintf('\nRed entrenada: RMSE = %.2f dB | R^2 = %.3f\n', rmse, R2);

    % ---------- 5) MAPA DE COBERTURA que aprendió la red ----------
    % Elegimos un AP (Hawk H1) y pedimos a la red el RSSI en toda la galería.
    apx=-0.2; apy=134.9; tipo=1;
    Xg=[0 25.98 51.96]; ys=0:1:135;
    [GX,GY]=meshgrid(Xg, ys);
    dist=sqrt((GX-apx).^2+(GY-apy).^2);
    galAP = 1;                       % H1 está en la galería x=0
    galP  = arrayfun(@(x) find(abs(x-Xg)==min(abs(x-Xg)),1), GX);
    cruces=abs(galP-galAP);
    Xg2=[GX(:) GY(:) apx*ones(numel(GX),1) apy*ones(numel(GX),1) ...
         tipo*ones(numel(GX),1) dist(:) cruces(:)];
    Xg2n=(Xg2-mu)./sg;
    tic; rssiPred = predict(net, Xg2n); tpred=toc;
    rssiMap = reshape(rssiPred, size(GX));
    fprintf('Mapa de cobertura de toda la galería predicho en %.1f ms (%d puntos)\n', ...
            tpred*1000, numel(GX));

    fig=figure('Position',[80 80 520 760],'Color','w');
    hold on;
    for gi=1:3
        plot([Xg(gi) Xg(gi)],[0 135],'-','Color',[0.8 0.8 0.8],'LineWidth',8);
    end
    sc = scatter(GX(:), GY(:), 60, rssiPred, 'filled','Marker','s');
    plot(apx,apy,'r^','MarkerFaceColor','r','MarkerSize',12);
    text(apx+2,apy,'H1 (AP)','Color','r','FontWeight','bold');
    colormap(turbo); cb=colorbar; cb.Label.String='RSSI predicho (dBm)';
    axis equal tight; xlabel('X (m)'); ylabel('Y (m)');
    title(sprintf('Mapa de cobertura APRENDIDO por la red\n(RMSE %.1f dB, predicho en %.0f ms)', rmse, tpred*1000));
    exportgraphics(fig,[OUT 'mapa_red_aprendido.png'],'Resolution',150);
    fprintf('[OK] Mapa guardado: %smapa_red_aprendido.png\n', OUT);
end

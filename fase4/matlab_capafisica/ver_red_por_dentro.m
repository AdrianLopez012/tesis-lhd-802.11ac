function ver_red_por_dentro(densidad)
% =========================================================================
% VER LA RED NEURONAL POR DENTRO — nodos, conexiones y PESOS aprendiendo
% =========================================================================
% "Abre la caja negra": en vez de solo la curva de error, dibuja la RED como
% neuronas (círculos) y conexiones (líneas). El COLOR y GROSOR de cada línea
% es el PESO aprendido: azul = positivo, rojo = negativo, grueso = importante.
% Anima cómo los pesos cambian época a época mientras la red aprende.
%
% Usa una red PEQUEÑA (7 -> 8 -> 6 -> 1) para que se puedan ver todas las
% conexiones. Entrena en bloques y refresca el dibujo entre bloques.
%
% Ejecutar en MATLAB (con ventana):
%   >> ver_red_por_dentro('fina')
% Genera además red_pesos_evolucion.mp4 con la animación.
% =========================================================================
    if nargin<1, densidad='fina'; end
    OUT = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\matlab_capafisica\';
    T = readtable([OUT 'dataset_canal_' densidad '.csv']);

    % ---------- datos ----------
    X = [T.x, T.y, T.ap_x, T.ap_y, T.ap_tipo, T.dist_euclid, T.cruces_nlos];
    y = T.rssi_dbm;
    entradas = {'x_{LHD}','y_{LHD}','x_{AP}','y_{AP}','tipo AP','distancia','cruces roca'};
    rng(42); n=height(T); idx=randperm(n); nTr=round(0.8*n);
    iTr=idx(1:nTr); iTe=idx(nTr+1:end);
    mu=mean(X(iTr,:)); sg=std(X(iTr,:)); sg(sg==0)=1; Xn=(X-mu)./sg;

    % ---------- red PEQUEÑA (visible) 7->8->6->1 ----------
    capas = [
        featureInputLayer(7,'Name','in');
        fullyConnectedLayer(8,'Name','fc1'); reluLayer('Name','r1');
        fullyConnectedLayer(6,'Name','fc2'); reluLayer('Name','r2');
        fullyConnectedLayer(1,'Name','out'); regressionLayer('Name','reg')];
    tam = [7 8 6 1];      % neuronas por capa (para dibujar)

    % ---------- figura ----------
    fig = figure('Position',[60 60 1180 720],'Color','w');
    tl = tiledlayout(fig,1,2,'TileSpacing','compact');
    axNet = nexttile(tl); axis(axNet,'off'); title(axNet,'La red por dentro: neuronas y pesos');
    axErr = nexttile(tl); hold(axErr,'on'); grid(axErr,'on');
    xlabel(axErr,'Bloque de entrenamiento'); ylabel(axErr,'RMSE (dB)');
    title(axErr,'Error mientras aprende');

    % posiciones de las neuronas por capa (coordenadas del dibujo)
    xc = linspace(0.1, 0.9, numel(tam));
    pos = cell(numel(tam),1);
    for c=1:numel(tam)
        yy = linspace(0.85, 0.15, tam(c));
        pos{c} = [repmat(xc(c),tam(c),1) yy(:)];
    end

    vw = VideoWriter([OUT 'red_pesos_evolucion.mp4'],'MPEG-4');
    vw.FrameRate=6; open(vw);

    NB = 25;                 % bloques de entrenamiento (frames de la animación)
    epB = 12;                % épocas por bloque
    net = [];                % se va reentrenando (warm start via layers actualizadas)
    rmseHist = [];

    for b = 1:NB
        opts = trainingOptions('adam','MaxEpochs',epB,'MiniBatchSize',32, ...
            'InitialLearnRate',3e-3,'Shuffle','every-epoch', ...
            'Verbose',false,'Plots','none');
        if isempty(net)
            net = trainNetwork(Xn(iTr,:), y(iTr), capas, opts);
        else
            net = trainNetwork(Xn(iTr,:), y(iTr), net.Layers, opts);
        end

        % --- extraer pesos aprendidos de cada capa densa ---
        L = net.Layers;
        W1 = L(2).Weights;   % 8x7
        W2 = L(4).Weights;   % 6x8
        W3 = L(6).Weights;   % 1x6
        Ws = {W1, W2, W3};
        wmax = max(cellfun(@(w) max(abs(w(:))), Ws));

        % --- dibujar la red ---
        cla(axNet); axis(axNet,[0 1 0 1]); axis(axNet,'off'); hold(axNet,'on');
        title(axNet, sprintf('La red por dentro — bloque %d/%d', b, NB));
        for c=1:numel(tam)-1
            W = Ws{c};                       % [neuronas_sig x neuronas_actual]
            P0 = pos{c}; P1 = pos{c+1};
            for i=1:size(P0,1)
                for j=1:size(P1,1)
                    w = W(j,i);
                    lw = 0.2 + 3.5*abs(w)/wmax;
                    if w>=0, col=[0.2 0.4 0.85]; else, col=[0.85 0.2 0.2]; end
                    plot(axNet,[P0(i,1) P1(j,1)],[P0(i,2) P1(j,2)], ...
                        'Color',[col 0.5],'LineWidth',lw);
                end
            end
        end
        % neuronas
        for c=1:numel(tam)
            P=pos{c};
            scatter(axNet, P(:,1),P(:,2), 260, [0.15 0.15 0.15],'filled');
            scatter(axNet, P(:,1),P(:,2), 200, [1 1 1],'filled');
            scatter(axNet, P(:,1),P(:,2), 200, [0.3 0.3 0.3]);
        end
        % etiquetas de entradas y salida
        for i=1:tam(1)
            text(axNet, pos{1}(i,1)-0.02, pos{1}(i,2), entradas{i}, ...
                'HorizontalAlignment','right','FontSize',8);
        end
        text(axNet, pos{end}(1,1)+0.02, pos{end}(1,2),'RSSI','FontSize',10,'FontWeight','bold');
        text(axNet,0.5,0.02,'azul = peso positivo · rojo = negativo · grosor = magnitud', ...
            'HorizontalAlignment','center','FontSize',8,'Color',[0.4 0.4 0.4]);

        % --- error ---
        yh = predict(net, Xn(iTe,:));
        rmse = sqrt(mean((yh-y(iTe)).^2)); rmseHist(end+1)=rmse; %#ok<AGROW>
        plot(axErr, 1:numel(rmseHist), rmseHist,'b-o','LineWidth',1.5,'MarkerFaceColor','b');
        ylim(axErr,[0 max(rmseHist)*1.1]);

        drawnow; writeVideo(vw, getframe(fig));
    end
    close(vw);
    fprintf('RMSE final: %.2f dB\n', rmseHist(end));
    fprintf('[OK] Animación: %sred_pesos_evolucion.mp4\n', OUT);
    exportgraphics(fig,[OUT 'red_por_dentro_final.png'],'Resolution',150);
end

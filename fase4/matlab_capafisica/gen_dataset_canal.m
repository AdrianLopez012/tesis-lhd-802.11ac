function gen_dataset_canal(densidad)
% =========================================================================
% GENERADOR DE DATASET DEL CANAL POR RAY-TRACING (para la red neuronal)
% =========================================================================
% Caracteriza el canal RIGUROSAMENTE: para una grilla de posiciones del LHD
% y cada AP, traza rayos SBR sobre la geometría 3D real (STL con roca) y
% registra, además del RSSI, descriptores físicos del canal:
%   RSSI (dBm), nº de rayos, path loss mínimo, delay spread (RMS), nº de
%   reflexiones del rayo dominante, y cruces NLOS (galerías distintas).
%
% Salida: dataset_canal.csv  con columnas
%   x,y,z, ap_x,ap_y,ap_tipo, dist_euclid, dist_ruta, cruces, ...
%   n_rayos, pl_min_db, rssi_dbm, delayspread_ns, refl_dom
%
% Uso:  gen_dataset_canal('prueba')  -> pocos puntos, mide tiempo paralelo
%       gen_dataset_canal('media')   -> grilla media (validar la red)
%       gen_dataset_canal('fina')    -> grilla densa (dataset final, horas)
% =========================================================================
    if nargin<1, densidad='prueba'; end
    TRB = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\';
    OUT = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\matlab_capafisica\';
    STL = [TRB 'galeria_rt.stl'];
    f0  = 5.0e9;

    % ---- posiciones reales de los AP (de la fuente única de la tesis) ----
    % [x  y  tipo(1=Hawk 30dBm/11dBi, 2=Cardinal 23dBm/7.5dBi)]
    HAWK = [ -0.2 134.9; -0.1 88.6; 25.9 43.4; 25.9 -0.3; 52.2 84.6];
    CARD = [ -0.3 43.8; -0.1 8.0; 26.1 129.1; 26.3 87.2; 26.3 21.4; 52.0 38.5; 52.4 129.7];
    APs = [HAWK ones(size(HAWK,1),1); CARD 2*ones(size(CARD,1),1)];
    Xg  = [0 25.98 51.96];           % x de las 3 galerías
    zAP = 2.0; zLHD = 1.0;

    % ---- densidad de la grilla ----
    switch densidad
        case 'prueba', paso = 20; apSel = 1;               % pocos puntos, 1 AP
        case 'media',  paso = 5;  apSel = 1:size(APs,1);   % todos los AP, grilla media
        case 'fina',   paso = 2;  apSel = 1:size(APs,1);   % todos los AP, grilla densa
        otherwise, error('densidad: prueba | media | fina');
    end
    ys = 0:paso:135;
    % puntos: LHD en cada galería, a lo largo de y
    pts = [];
    for gx = Xg
        for y = ys
            pts = [pts; gx y zLHD]; %#ok<AGROW>
        end
    end
    nP = size(pts,1); nA = numel(apSel);
    fprintf('Densidad=%s | %d posiciones x %d AP = %d enlaces a trazar\n', ...
            densidad, nP, nA, nP*nA);

    % ---- parallel pool (10 workers) ----
    p = gcp('nocreate');
    if isempty(p) || p.NumWorkers < 10
        delete(gcp('nocreate'));
        try parpool('Processes',10); catch, parpool('Processes'); end
    end

    % ---- funciones auxiliares (galería más cercana, cruces NLOS) ----
    galIdx = @(x) find(abs(x-Xg)==min(abs(x-Xg)),1);

    % ---- barrido: para cada AP, parfor sobre posiciones ----
    rows = cell(nA,1);
    tGlobal = tic;
    for ia = 1:nA
        a = APs(apSel(ia),:); apx=a(1); apy=a(2); tipo=a(3);
        Pt_dbm = (tipo==1)*30 + (tipo==2)*23;
        Gt     = (tipo==1)*11 + (tipo==2)*7.5;
        Gr     = 4.8;   % HELI-40 del LHD
        Rt = nan(nP, 6);   % [rssi, nrayos, plmin, ds_ns, refl, cruces]
        parfor ip = 1:nP
            px=pts(ip,1); py=pts(ip,2); pz=pts(ip,3);
            pm = propagationModel('raytracing','Method','sbr','CoordinateSystem','cartesian',...
                'MaxNumReflections',6,'SurfaceMaterial','custom',...
                'SurfaceMaterialPermittivity',6.0,'SurfaceMaterialConductivity',0.01);
            tx = txsite('cartesian','AntennaPosition',[apx;apy;zAP],...
                'TransmitterFrequency',f0,'TransmitterPower',10^((Pt_dbm-30)/10));
            rx = rxsite('cartesian','AntennaPosition',[px;py;pz]);
            v = nan(1,6);
            try
                rays = raytrace(tx, rx, pm, 'Map', STL);
                if ~isempty(rays) && ~isempty(rays{1})
                    R = rays{1};
                    pl = [R.PathLoss];
                    [plmin, kmin] = min(pl);
                    rssi = Pt_dbm + Gt + Gr - plmin;
                    delays = [R.PropagationDelay];
                    % delay spread RMS ponderado por potencia de cada rayo
                    pw = 10.^(-pl/10); pw = pw/sum(pw);
                    tau = delays - min(delays);
                    ds = sqrt(sum(pw.*(tau.^2)) - (sum(pw.*tau))^2);
                    v = [rssi, numel(pl), plmin, ds*1e9, R(kmin).NumInteractions, NaN];
                end
            catch
            end
            Rt(ip,:) = v;
        end
        % cruces NLOS (fuera del parfor, barato)
        for ip=1:nP
            Rt(ip,6) = abs(galIdx(pts(ip,1)) - galIdx(apx));
        end
        % ensamblar filas de este AP
        blk = [pts, repmat([apx apy tipo],nP,1), ...
               sqrt((pts(:,1)-apx).^2+(pts(:,2)-apy).^2), Rt];
        rows{ia} = blk;
        fprintf('  AP %d/%d (tipo %d) hecho | %.1f min acumulados\n', ...
                ia, nA, tipo, toc(tGlobal)/60);
    end

    D = cell2mat(rows);
    % quitar filas sin cobertura (sin rayos)
    D = D(~isnan(D(:,8)), :);
    hdr = {'x','y','z','ap_x','ap_y','ap_tipo','dist_euclid', ...
           'rssi_dbm','n_rayos','pl_min_db','delayspread_ns','refl_dom','cruces_nlos'};
    T = array2table(D,'VariableNames',hdr);
    fn = [OUT 'dataset_canal_' densidad '.csv'];
    writetable(T, fn);
    fprintf('\n[OK] %d muestras con cobertura -> %s\n', height(T), fn);
    fprintf('Tiempo total: %.1f min | %.2f s/enlace efectivo\n', ...
            toc(tGlobal)/60, toc(tGlobal)/(nP*nA));
    fprintf('RSSI: min %.1f / media %.1f / max %.1f dBm\n', ...
            min(T.rssi_dbm), mean(T.rssi_dbm), max(T.rssi_dbm));
end

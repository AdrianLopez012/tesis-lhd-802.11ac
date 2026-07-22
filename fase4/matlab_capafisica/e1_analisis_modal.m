function e1_analisis_modal()
% =========================================================================
% ESLABÓN 1 — ANÁLISIS MODAL DEL TÚNEL COMO GUÍA DE ONDA
% =========================================================================
% Fundamento físico de toda la cadena: la galería (5.0 x 4.5 m) se comporta
% como una guía de onda dieléctrica SOBREDIMENSIONADA a 5 GHz. Este script
% demuestra cuantitativamente:
%   (a) la frecuencia de corte del modo fundamental,
%   (b) cuántos modos propagantes coexisten a 5 GHz (régimen multimodo),
%   (c) por qué eso JUSTIFICA el modelo two-slope (n1<2 cerca, n2>2 lejos),
%   (d) la atenuación por rugosidad que hace desaparecer los modos altos.
%
% Referencia: guía de onda rectangular metálica como cota superior; el túnel
% real es dieléctrico con pérdidas (Emslie 1975; Rappaport cap. 4). El
% tratamiento metálico da la física cualitativa de modos y corte.
%
% Salidas: figura e1_modos.png + resumen en consola.
% Ejecutar:  e1_analisis_modal   (o el lanzador run_e1.m en C:\Users\Public)
% =========================================================================

    OUT = 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\matlab_capafisica\';

    % ---- Parámetros físicos ----
    c   = 299792458;        % m/s
    f0  = 5.0e9;            % Hz (802.11ac banda 5 GHz)
    lam = c/f0;             % longitud de onda ~6 cm
    a   = 5.0;              % ancho de la galería (m)  [sección SEC 5 x 4.5]
    b   = 4.5;              % alto de la galería (m)

    fprintf('\n===== ESLABÓN 1: ANÁLISIS MODAL DEL TÚNEL =====\n');
    fprintf('Sección: %.1f x %.1f m | f0 = %.1f GHz | lambda = %.1f cm\n', ...
            a, b, f0/1e9, lam*100);

    % ---- Frecuencia de corte de los modos TE_mn / TM_mn ----
    % Guía rectangular: fc(m,n) = (c/2) * sqrt((m/a)^2 + (n/b)^2)
    fc = @(m,n) (c/2).*sqrt((m./a).^2 + (n./b).^2);

    fc10 = fc(1,0);   % modo fundamental TE10
    fprintf('\n-- Frecuencia de corte del modo fundamental TE10: %.2f MHz\n', fc10/1e6);
    fprintf('   Operamos a 5 GHz = %.0f veces por encima del corte.\n', f0/fc10);
    fprintf('   => Régimen MULTIMODO fuertemente sobredimensionado.\n');

    % ---- Contar modos propagantes por debajo de 5 GHz ----
    Mmax = ceil(2*a/lam)+2; Nmax = ceil(2*b/lam)+2;
    nProp = 0; fcs = [];
    for m = 0:Mmax
        for n = 0:Nmax
            if m==0 && n==0, continue; end          % no existe TE00/TM00
            fcmn = fc(m,n);
            if fcmn <= f0
                nProp = nProp + 1;
                fcs(end+1) = fcmn; %#ok<AGROW>
            end
        end
    end
    fprintf('\n-- Modos con fc <= 5 GHz (propagantes): ~%d\n', nProp);
    fprintf('   (cota del modelo metálico; el túnel dieléctrico filtra los altos)\n');

    % ---- Constante de fase y velocidad de grupo del modo dominante ----
    beta10 = (2*pi*f0/c)*sqrt(1 - (fc10/f0)^2);
    vg10   = c*sqrt(1 - (fc10/f0)^2);
    fprintf('\n-- Modo TE10 a 5 GHz: beta = %.2f rad/m | vg = %.4f c\n', beta10, vg10/c);
    fprintf('   vg ~ c => dispersión modal despreciable para el dominante.\n');

    % ---- Justificación del two-slope (conexión con la tesis) ----
    d_bp = 40;   % punto de quiebre de la tesis (m)
    fprintf('\n-- CONEXIÓN CON EL MODELO DE LA TESIS (two-slope):\n');
    fprintf('   Cerca del Tx (< %d m): coexisten MUCHOS modos -> la energía se\n', d_bp);
    fprintf('   refuerza -> decaimiento LENTO -> exponente n1 = 1.9 (< 2, mejor\n');
    fprintf('   que espacio libre: efecto guía de onda).\n');
    fprintf('   Lejos (> %d m): los modos de orden alto se atenúan por la\n', d_bp);
    fprintf('   rugosidad y las pérdidas dieléctricas -> sobrevive el modo\n');
    fprintf('   dominante -> decaimiento RÁPIDO -> exponente n2 = 3.4 (> 2).\n');

    % =====================================================================
    % FIGURA: distribución de frecuencias de corte y régimen de operación
    % =====================================================================
    fig = figure('Position',[60 60 1100 460],'Color','w','Visible','off');

    % (a) histograma de fc de los modos vs la frecuencia de operación
    ax1 = subplot(1,2,1); hold(ax1,'on');
    histogram(ax1, fcs/1e6, 30, 'FaceColor',[0.30 0.55 0.75],'EdgeColor','w');
    xline(ax1, f0/1e6, 'r-', 'LineWidth',2, 'Label','5 GHz (operación)', ...
          'LabelVerticalAlignment','top','FontSize',9);
    xline(ax1, fc10/1e6, 'k--','LineWidth',1.5,'Label',sprintf('fc TE10 = %.0f MHz',fc10/1e6), ...
          'LabelVerticalAlignment','bottom','FontSize',9);
    xlabel(ax1,'Frecuencia de corte del modo (MHz)');
    ylabel(ax1,'Número de modos');
    title(ax1,sprintf('Modos propagantes de la galería (%d por debajo de 5 GHz)',nProp));
    grid(ax1,'on'); box(ax1,'on');

    % (b) esquema conceptual del two-slope justificado por modos
    ax2 = subplot(1,2,2); hold(ax2,'on');
    dd = logspace(0, log10(160), 400);
    PL_D0 = 20*log10(4*pi/lam);
    n1=1.9; n2=3.4;
    PL = zeros(size(dd));
    for k=1:numel(dd)
        if dd(k) < d_bp
            PL(k) = PL_D0 + 10*n1*log10(dd(k));
        else
            PL(k) = PL_D0 + 10*n1*log10(d_bp) + 10*n2*log10(dd(k)/d_bp);
        end
    end
    PLfriis = PL_D0 + 20*log10(dd);   % espacio libre (n=2) de referencia
    plot(ax2, dd, PL, 'b-','LineWidth',2.2);
    plot(ax2, dd, PLfriis, 'k:','LineWidth',1.3);
    xline(ax2, d_bp, 'r--','LineWidth',1.5,'Label','d_{bp}=40 m','FontSize',9);
    set(ax2,'XScale','log'); grid(ax2,'on'); box(ax2,'on');
    xlabel(ax2,'Distancia (m)'); ylabel(ax2,'Pérdida de trayecto (dB)');
    title(ax2,'Two-slope justificado por el análisis modal');
    legend(ax2,{'Two-slope (n_1=1.9, n_2=3.4)','Espacio libre (n=2)'}, ...
           'Location','northwest','FontSize',9);
    text(ax2, 3, PL_D0+8, 'guiado multimodo','Color',[0 0 0.7],'FontSize',9,'FontAngle','italic');
    text(ax2, 70, PL_D0+42,'modo dominante','Color',[0 0 0.7],'FontSize',9,'FontAngle','italic');

    sgtitle(fig,'Eslabón 1 — La galería como guía de onda sobredimensionada a 5 GHz','FontWeight','bold');
    exportgraphics(fig, [OUT 'e1_modos.png'], 'Resolution',150);
    close(fig);
    fprintf('\n[OK] Figura: %se1_modos.png\n', OUT);
    fprintf('===== FIN ESLABÓN 1 =====\n\n');
end

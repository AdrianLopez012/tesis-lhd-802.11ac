% crear_wmm_simevents.m v2 — modelo SimEvents del AP (WMM/EDCA), a prueba de
% numeración de puertos: 1º se cablean las ENTIDADES, 2º se activan las
% estadísticas y se conectan sus puertos NUEVOS por handle.
mdl = 'wmm_edca_nv1640';
if bdIsLoaded(mdl), close_system(mdl, 0); end
new_system(mdl); load_system('sldelib');

A = @(src, dst, pos) add_block(src, [mdl '/' dst], 'Position', pos);

% ---- FASE 1: bloques SIN estadísticas ----
gV = A('sldelib/Entity Generator', 'VIDEO 40Mbps AC_VI', [60  60 160 110]);
set_param(gV,'Period','1/3600','AttributeName','Prio','AttributeInitialValue','2');
gC = A('sldelib/Entity Generator', 'COMANDOS AC_VO',     [60 180 160 230]);
set_param(gC,'Period','1/483','AttributeName','Prio','AttributeInitialValue','1');
gT = A('sldelib/Entity Generator', 'TELEMETRIA AC_BE',   [60 300 160 350]);
set_param(gT,'Period','1/62','AttributeName','Prio','AttributeInitialValue','3');

sw = A('sldelib/Entity Input Switch', 'merge', [230 175 280 235]);
set_param(sw,'NumberInputPorts','3','ActivePortSelection','All');

q = A('sldelib/Entity Queue', 'COLA PRIORIDAD EDCA', [340 170 440 240]);
set_param(q,'QueueType','Priority','PrioritySource','Prio','SortingDirection','Ascending','Capacity','5000');

sv = A('sldelib/Entity Server', 'AIRE 802.11ac', [510 170 610 240]);
set_param(sv,'Capacity','1','ServiceTimeSource','Dialog','ServiceTimeValue','2.2e-4');

tm = A('sldelib/Entity Terminator', 'entregado', [680 180 730 230]);

s1 = A('simulink/Sinks/Scope', 'Cola (paquetes)',  [520 60 570 100]);
s2 = A('simulink/Sinks/Scope', 'Espera media (s)', [520 300 570 340]);
s3 = A('simulink/Sinks/Scope', 'Utilizacion aire', [680 60 730 100]);

% ---- FASE 2: cablear ENTIDADES (ahora los puertos 1 son inequívocos) ----
add_line(mdl, 'VIDEO 40Mbps AC_VI/1', 'merge/1');
add_line(mdl, 'COMANDOS AC_VO/1',     'merge/2');
add_line(mdl, 'TELEMETRIA AC_BE/1',   'merge/3');
add_line(mdl, 'merge/1', 'COLA PRIORIDAD EDCA/1');
add_line(mdl, 'COLA PRIORIDAD EDCA/1', 'AIRE 802.11ac/1');
add_line(mdl, 'AIRE 802.11ac/1', 'entregado/1');

% ---- FASE 3: activar estadísticas y conectar los puertos NUEVOS por handle ----
function conectarNuevos(mdl, blk, params, scopes)
    ph0 = get_param(blk, 'PortHandles'); antes = ph0.Outport;
    for i = 1:2:numel(params)
        set_param(blk, params{i}, params{i+1});
    end
    ph1 = get_param(blk, 'PortHandles');
    nuevos = setdiff(ph1.Outport, antes, 'stable');
    for i = 1:min(numel(nuevos), numel(scopes))
        phS = get_param(scopes{i}, 'PortHandles');
        add_line(mdl, nuevos(i), phS.Inport(1));
    end
end
conectarNuevos(mdl, q,  {'NumberEntitiesInBlock','on','AverageWait','on'}, ...
    {[mdl '/Cola (paquetes)'], [mdl '/Espera media (s)']});
conectarNuevos(mdl, sv, {'Utilization','on'}, {[mdl '/Utilizacion aire']});

% ---- anotación ----
add_block('built-in/Note', [mdl '/nota'], 'Position', [60 420], 'Text', ...
    ['MODELO WMM/EDCA DEL AP  -  tasas reales NS-3 (video 3600 pps, comandos 483 pps, telemetria 62 pps)' newline ...
     'Prio 1 = maxima (comandos AC_VO). Servidor ~4545 pps (~51 Mbps de payload).' newline ...
     'VER EN MOVIMIENTO: pestana DEBUG -> "Animation Speed" en lento -> RUN.' newline ...
     'ESTRES: Period del generador VIDEO a 1/4700 -> la cola crece, los comandos siguen saliendo primero.']);

set_param(mdl, 'StopTime', '30');
save_system(mdl, 'C:\Users\Adrian Lopez\Documents\tesis_proyecto\fase4\trabajo\wmm_edca_nv1640.slx');
open_system(mdl);
disp('MODELO v2 LISTO — dale RUN (Debug > Animation Speed para ver los paquetes).');

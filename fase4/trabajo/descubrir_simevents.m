% descubrir_simevents.m — inspecciona los parámetros reales de los bloques
% SimEvents en ESTA versión, para construir el modelo bien a la primera.
try
mdl = 'tmp_descubre';
new_system(mdl); load_system('sldelib'); lib='sldelib';
fprintf('libreria: %s%s', lib, newline);
blqs = strcat(lib, {'/Entity Generator','/Entity Queue', ...
        '/Entity Server','/Entity Terminator', ...
        '/Entity Input Switch'});
for i = 1:numel(blqs)
    partes = split(blqs{i},'/'); nombre = partes{end};
    h = add_block(blqs{i}, [mdl '/' strrep(nombre,' ','_')]);
    dp = get_param(h, 'DialogParameters');
    fprintf('\n===== %s =====\n', nombre);
    fn = fieldnames(dp);
    for j = 1:numel(fn)
        tipo = dp.(fn{j}).Type;
        if strcmp(tipo,'enum')
            fprintf('  %s (enum): %s\n', fn{j}, strjoin(dp.(fn{j}).Enum, ' | '));
        else
            fprintf('  %s (%s)\n', fn{j}, tipo);
        end
    end
end
close_system(mdl, 0);
disp('DESCUBRIMIENTO OK');
catch e
    fprintf('ERR: %s\n', e.message);
end
exit;

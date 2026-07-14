#!/bin/bash
# Arma el ANEXO DIGITAL de la tesis con la estructura declarada en el Anexo H.
# Re-ejecutable: borra y reconstruye. El ZIP no se versiona (regenerable).
set -e
BASE="/c/Users/Adrian Lopez/Documents/tesis_proyecto"
SIM="$BASE/cap3/simulacion_ns3"
OUT="$BASE/fase4/anexo_digital"

rm -rf "$OUT"
mkdir -p "$OUT"/{codigo,fuente_unica,scripts_figuras,results,figuras,ejecucion}

# codigo/: simulación + headers autogenerados
cp "$SIM"/lhd-teleop-v3-real.cc "$SIM"/geometria_nv1640.h "$SIM"/recorrido_nv1640.h "$SIM"/parametros_rf.h "$OUT/codigo/"

# fuente_unica/: datos y generadores
cp "$SIM"/parametros_rf.py "$SIM"/graficas_simulacion/mapa_nv1640_datos.py \
   "$SIM"/graficas_simulacion/generar_geometria_h.py "$SIM"/graficas_simulacion/generar_recorrido_h.py \
   "$SIM"/graficas_simulacion/generar_parametros_h.py "$OUT/fuente_unica/"

# scripts_figuras/: todos los scripts de figuras vigentes
for s in plano_nv1640_pro mapa_cobertura_pro contraste_tamograph resultados_v3 kpis_v3real \
         link_budget comparacion_kpis arquitectura_red animacion_recorrido_lhd; do
  cp "$SIM/graficas_simulacion/$s.py" "$OUT/scripts_figuras/"
done

# results/: CSV y XML íntegros de las 18 corridas
cp "$SIM"/results/*_v3_* "$OUT/results/"

# figuras/: PNG resolución completa + animación + escena 3D MATLAB
cp "$SIM"/graficas_simulacion/*.png "$SIM"/graficas_simulacion/recorrido_lhd.gif "$OUT/figuras/"
cp "$BASE/fase4/trabajo/escena_mina_3d.png" "$BASE/fase4/trabajo/escena_mina_3d.m" "$BASE/fase4/trabajo/patron_antena_3d.png" "$BASE/fase4/trabajo/patron_antena_3d.m" "$BASE/fase4/trabajo/grafico_rssi_asociado.png" "$BASE/fase4/trabajo/grafico_rssi_asociado.m" "$BASE/fase4/trabajo/curva_prx_distancia.png" "$BASE/fase4/trabajo/cdf_rssi_10seeds.png" "$BASE/fase4/trabajo/graficos_extra.m" "$BASE/fase4/trabajo/fig_capex_opex.png" "$OUT/figuras/"

# ejecucion/: batería + README de reproducción
cp "$SIM"/run_escenarios_v3.sh "$SIM"/README.md "$OUT/ejecucion/"

# README raíz del anexo
cat > "$OUT/README.txt" << 'EOF'
ANEXO DIGITAL COMPLEMENTARIO
Tesis: Diseño de una red IEEE 802.11ac para la teleoperación de un vehículo LHD
en la extracción de mineral en galerías subterráneas (Nexa Cerro Lindo, NV1640)
Tesista: Adrián Álvaro López Pascual — PUCP

Estructura (conforme al Anexo H del documento):
  codigo/           Simulación ns-3 vigente (lhd-teleop-v3-real.cc) y encabezados autogenerados
  fuente_unica/     parametros_rf.py y mapa_nv1640_datos.py + generadores de encabezados C++
  scripts_figuras/  Scripts Python de todas las figuras del Anexo G
  results/          CSV y XML íntegros de las 18 corridas de la batería v3-REAL
  figuras/          Figuras en resolución completa, animación del recorrido y escena 3D (MATLAB)
  ejecucion/        run_escenarios_v3.sh e instrucciones de reproducción (README)

Las huellas SHA-256 de los archivos principales están impresas en el Anexo H
del documento y son verificables contra este anexo.
Reproducción completa: ver ejecucion/README.md (requiere ns-3.40; la batería
tarda ~4 horas y debe ejecutarse en serie).
EOF

# ZIP
cd "$BASE/fase4"
rm -f anexo_digital_tesis_lopez.zip
powershell.exe -NoProfile -Command "Compress-Archive -Path '$(cygpath -w "$OUT")\\*' -DestinationPath '$(cygpath -w "$BASE/fase4")\\anexo_digital_tesis_lopez.zip' -Force" 2>/dev/null || (cd "$OUT" && zip -qr ../anexo_digital_tesis_lopez.zip .)

echo "--- contenido ---"
find "$OUT" -type f | wc -l
du -sh "$OUT" ../fase4/anexo_digital_tesis_lopez.zip 2>/dev/null || du -sh "$OUT" "$BASE/fase4/anexo_digital_tesis_lopez.zip"

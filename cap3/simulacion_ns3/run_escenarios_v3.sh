#!/bin/bash
# ============================================================================
# Batería de escenarios v3-REAL — NV1640 (EN SERIE)
# ============================================================================
# Corre el conjunto de pruebas del capítulo de resultados EN SERIE. Aunque cada
# simulación es independiente (semilla propia, ficheros de salida propios), en
# este entorno WSL la ejecución en paralelo (binario directo o varios
# `./ns3 run` a la vez) SE CUELGA por contención del directorio de build de
# ns-3. NO paralelizar: la batería completa en serie tarda ~3 HORAS (medido:
# 10714 s la corrida del 2026-07-09) pero es 100% fiable y reproducible.
#
#   1. principal  — 10 semillas (media +/- IC) del escenario de operación
#   2. baseline   — LHD estático (referencia sin movilidad)
#   3. estres_video   — vídeo 50 Mbps (sobrecarga del enlace)
#   4. estres_lhd     — LHD a 4.0 m/s (roaming más rápido)
#
# Uso:  bash run_escenarios_v3.sh
# ============================================================================
set -e
NS3=~/ns-allinone-3.40/ns-3.40
cd "$NS3"
BIN="lhd-teleop-v3-real"
T=300
# Ejecución EN SERIE con ./ns3 run: es la única forma fiable en este entorno WSL
# (la ejecución en paralelo del binario / de varios ./ns3 run se cuelga por
# contención del directorio de build de ns-3). En serie tarda ~30 min pero es
# 100% reproducible y estable.

echo "===== compilando ${BIN} ====="
./ns3 build scratch/${BIN} 2>&1 | tail -1
mkdir -p results

run () {  # $1=scenario  $2..=args extra
  local sc="$1"; shift
  ./ns3 run "${BIN} --scenario=${sc} --simTime=${T} $*" > "results/${sc}_v3_console.log" 2>&1
  echo ">>> ${sc} LISTO ($(grep -c 'TODOS LOS KPIs CUMPLEN' results/${sc}_v3_console.log) cumple-todo)"
}

echo ""
echo "########## Ejecutando batería en serie ##########"
t0=$(date +%s)

for s in $(seq 1 10); do run "principal_s${s}" --seed=${s}; done
run baseline
run estres_video --videoRate=50.0
run estres_lhd --lhdSpeed=4.0
run handover                       # roaming sensible => handovers medibles (RNF-05)

t1=$(date +%s)
echo ""
echo "===== BATERÍA COMPLETA en $((t1-t0)) s ====="
ls -1 results/*_v3_flow_stats.csv | wc -l
echo "archivos flow_stats"

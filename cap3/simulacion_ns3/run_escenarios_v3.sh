#!/bin/bash
# ============================================================================
# Batería de escenarios v3-REAL — NV1640 (geometría real + recorrido real)
# ============================================================================
# Corre el conjunto de pruebas que enriquece el capítulo de resultados:
#   1. principal  — 10 semillas (media +/- desv, IC) del escenario de operación
#   2. baseline   — LHD estático (referencia sin movilidad)
#   3. estres_video   — video 50 Mbps (sobrecarga del enlace)
#   4. estres_lhd     — LHD a 4.0 m/s (roaming más rápido)
#
# Uso:  bash run_escenarios_v3.sh
# Salidas en ~/ns-allinone-3.40/ns-3.40/results/*_v3_*  (luego se copian al repo)
# ============================================================================
set -e
NS3=~/ns-allinone-3.40/ns-3.40
cd "$NS3"
BIN="lhd-teleop-v3-real"
T=300

echo "===== compilando ${BIN} ====="
./ns3 build scratch/${BIN} 2>&1 | tail -1

run () {  # $1=scenario  $2..=args extra
  local sc="$1"; shift
  echo ">>> ${sc}  ($*)"
  ./ns3 run "${BIN} --scenario=${sc} --simTime=${T} $*" 2>&1 | grep -E "Handover|CUMPLE|RESULTADOS|\[Video\]|\[Comandos\]|\[Telemetria\]" || true
}

echo ""
echo "########## 1) PRINCIPAL — 10 semillas ##########"
for s in $(seq 1 10); do
  echo ">>> principal seed=${s}"
  ./ns3 run "${BIN} --scenario=principal_s${s} --simTime=${T} --seed=${s}" 2>&1 \
     | grep -E "CUMPLE|\[Video\]|\[Comandos\]|\[Telemetria\]|Handover" || true
done

echo ""
echo "########## 2) BASELINE (LHD estático) ##########"
run baseline

echo ""
echo "########## 3) ESTRÉS — video 50 Mbps ##########"
run estres_video --videoRate=50.0

echo ""
echo "########## 4) ESTRÉS — LHD rápido 4.0 m/s ##########"
run estres_lhd --lhdSpeed=4.0

echo ""
echo "===== BATERÍA COMPLETA ====="
ls -1 results/*_v3_flow_stats.csv | wc -l
echo "archivos flow_stats generados (arriba)"

#!/bin/bash
# =============================================================================
# run_all_simulations.sh — Ejecuta todos los escenarios v9 en ns-3
# Tesis: Red IEEE 802.11ac para teleoperación LHD — Nexa Cerro Lindo
# =============================================================================
# Uso:
#   cd ~/ns-allinone-3.40/ns-3.40
#   bash /mnt/c/Users/Adrian\ Lopez/Documents/tesis_proyecto/cap3/simulacion_ns3/run_all_simulations.sh
#
# Prerequisito: haber compilado el scratch
#   cp /mnt/c/Users/Adrian\ Lopez/Documents/tesis_proyecto/cap3/simulacion_ns3/lhd-teleop-v2-nexa.cc scratch/
#   ./ns3 build scratch/lhd-teleop-v2-nexa
# =============================================================================

set -e

NS3_DIR="$HOME/ns-allinone-3.40/ns-3.40"
SCRATCH="lhd-teleop-v2-nexa"
SIM_TIME=300
RESULTS_DIR="$NS3_DIR/results"
WIN_RESULTS="/mnt/c/Users/Adrian Lopez/Documents/tesis_proyecto/cap3/simulacion_ns3/results"

cd "$NS3_DIR"
mkdir -p "$RESULTS_DIR"

echo "========================================================"
echo " Simulación v9 — Nexa Cerro Lindo Nivel 1640"
echo " simTime=${SIM_TIME}s"
echo " Geometría: ramal BP 70°, ramal Desmonte 65°"
echo " ClassifyPosition: proyección paramétrica por eje de ramal"
echo " RouteDistance: distancia oblicua AlongBP/AlongDES"
echo " CardFijo: (194.0, 28.4) | H4: (329.7, 23.9)"
echo "========================================================"

run_scenario() {
    local name="$1"
    local extra="${2:-}"
    echo ""
    echo "--- Corriendo: $name $extra ---"
    ./ns3 run "$SCRATCH --scenario=$name --simTime=$SIM_TIME $extra" 2>&1 | \
        grep -E "(RESULTADOS|OWD|E2E|TODOS|ALGUNOS|CSV|POS|ASSOC|PLR|Tput|Goodput|CUMPLE|NO CUMPLE)" | \
        grep -v "Max Packets"
}

# ── Escenario principal (tesis) ───────────────────────────────────────────────
run_scenario "mobility_5hawks_real"

# ── Escenarios comparativos mobility (justificación de diseño) ────────────────
run_scenario "mobility_4hawks_sin_h4"
run_scenario "mobility_sin_cardfijo_bp"

# ── Escenarios de sensibilidad ────────────────────────────────────────────────
run_scenario "lhd_rapido_mobility"
run_scenario "video_20mbps_mobility"

# ── Baseline (referencia controlada) ─────────────────────────────────────────
run_scenario "baseline"

# ── Multi-seed baseline (robustez estadística — mínimo 10 semillas recomendado) ──
echo ""
echo "--- Corriendo: baseline seeds 2-10 ---"
for seed in 2 3 4 5 6 7 8 9 10; do
    echo "  seed=$seed"
    ./ns3 run "$SCRATCH --scenario=baseline --seed=$seed --simTime=$SIM_TIME" 2>&1 | \
        grep -E "(TODOS|ALGUNOS|CSV)" | grep -v "Max Packets"
done

# ── Copiar resultados a Windows ───────────────────────────────────────────────
echo ""
echo "--- Copiando resultados a Windows ---"
mkdir -p "$WIN_RESULTS"
cp "$RESULTS_DIR"/*_v9_*.csv     "$WIN_RESULTS/" 2>/dev/null && echo "  CSVs v9 copiados OK"     || true
cp "$RESULTS_DIR"/*_v9_*.xml     "$WIN_RESULTS/" 2>/dev/null && echo "  XMLs v9 copiados OK"     || true

echo ""
echo "========================================================"
echo " Todas las simulaciones v9 completadas."
echo " Resultados en: $WIN_RESULTS"
echo "========================================================"

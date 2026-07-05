#!/bin/bash
# =============================================================================
# compilar_v9.sh — Copia el .cc a ns-3 scratch y compila
# Uso: bash /mnt/c/.../compilar_v9.sh
# =============================================================================

NS3_DIR="$HOME/ns-allinone-3.40/ns-3.40"
SRC="/mnt/c/Users/Adrian Lopez/Documents/tesis_proyecto/cap3/simulacion_ns3/lhd-teleop-v2-nexa.cc"

echo "=== Copiando lhd-teleop-v2-nexa.cc a scratch ==="
cp "$SRC" "$NS3_DIR/scratch/"

echo "=== Compilando ==="
cd "$NS3_DIR"
./ns3 build scratch/lhd-teleop-v2-nexa 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Compilacion OK — listo para ejecutar ==="
    echo "Ejecuta un escenario de prueba rapida:"
    echo "  ./ns3 run \"lhd-teleop-v2-nexa --scenario=baseline --simTime=60\""
    echo ""
    echo "O ejecuta todos los escenarios v9:"
    echo "  bash /mnt/c/Users/Adrian\ Lopez/Documents/tesis_proyecto/cap3/simulacion_ns3/run_all_simulations.sh"
else
    echo ""
    echo "=== ERROR de compilacion ==="
fi

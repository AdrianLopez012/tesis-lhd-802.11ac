#!/bin/bash
# ==============================================================================
# SCRIPT DE EJECUCIÓN COMPLETA - TESIS NEXA
# Ejecuta todas las simulaciones Python y ns-3 con parámetros calibrados
# Autor: Adrián López - 20192733
# ==============================================================================

set -e  # Detener en caso de error

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="logs_${TIMESTAMP}"
mkdir -p "${LOG_DIR}"

echo "=============================================="
echo "INICIANDO SIMULACIONES COMPLETAS - ${TIMESTAMP}"
echo "=============================================="

# ------------------------------------------------------------------------------
# FASE 1: MODELOS PYTHON
# ------------------------------------------------------------------------------
echo ""
echo "[1/4] Ejecutando modelo_definitivo.py..."
cd cap3/modelado
python3 modelo_definitivo.py | tee "../../${LOG_DIR}/modelo_definitivo.log"
if [ $? -eq 0 ]; then
    echo "✓ modelo_definitivo.py completado"
    echo "  Gráficas generadas en: figuras_definitivas/"
else
    echo "✗ ERROR en modelo_definitivo.py"
    exit 1
fi

echo ""
echo "[2/4] Ejecutando raytracing_tunel.py (esto puede tardar 2-5 min)..."
cd ../raytracing
python3 raytracing_tunel.py | tee "../../${LOG_DIR}/raytracing.log"
if [ $? -eq 0 ]; then
    echo "✓ raytracing_tunel.py completado"
    echo "  Gráficas generadas en: figuras_raytracing/"
else
    echo "✗ ERROR en raytracing_tunel.py"
    exit 1
fi

cd ../..

# ------------------------------------------------------------------------------
# FASE 2: SIMULACIÓN NS-3
# ------------------------------------------------------------------------------
echo ""
echo "[3/4] Compilando simulación ns-3..."

# Detectar ruta de ns-3
NS3_PATH="${HOME}/ns-allinone-3.40/ns-3.40"
if [ ! -d "${NS3_PATH}" ]; then
    NS3_PATH="${HOME}/ns-3.40"
fi

if [ ! -d "${NS3_PATH}" ]; then
    echo "⚠ No se encontró ns-3 en ${HOME}/ns-allinone-3.40/ns-3.40"
    echo "  Por favor, edita NS3_PATH en este script"
    echo "  Simulaciones Python completadas, ns-3 omitido"
    exit 0
fi

echo "  Usando ns-3 en: ${NS3_PATH}"

# Copiar archivo actualizado
cp cap3/simulacion_ns3/lhd-teleop-v2-nexa.cc "${NS3_PATH}/scratch/"

# Compilar
cd "${NS3_PATH}"
./ns3 build scratch/lhd-teleop-v2-nexa 2>&1 | tee "${OLDPWD}/${LOG_DIR}/ns3_build.log"

if [ $? -ne 0 ]; then
    echo "✗ ERROR compilando ns-3"
    exit 1
fi

echo "✓ Compilación exitosa"

# ------------------------------------------------------------------------------
# FASE 3: EJECUTAR ESCENARIOS NS-3
# ------------------------------------------------------------------------------
echo ""
echo "[4/4] Ejecutando escenarios ns-3..."

mkdir -p results

SCENARIOS=(
    "baseline_v21:300:1"
    "sep_100m:300:1:--nHawks=4 --separation=100"
    "video_20mbps:300:1:--videoRate=20"
    "lhd_rapido:300:1:--lhdSpeed=3.33"
)

for scenario_config in "${SCENARIOS[@]}"; do
    IFS=':' read -r scenario simtime seed extra_args <<< "${scenario_config}"

    echo ""
    echo "  → Ejecutando escenario: ${scenario}"

    if [ -z "${extra_args}" ]; then
        ./ns3 run "lhd-teleop-v2-nexa --scenario=${scenario} --simTime=${simtime} --seed=${seed}" \
            2>&1 | tee "${OLDPWD}/${LOG_DIR}/ns3_${scenario}.log"
    else
        ./ns3 run "lhd-teleop-v2-nexa --scenario=${scenario} --simTime=${simtime} --seed=${seed} ${extra_args}" \
            2>&1 | tee "${OLDPWD}/${LOG_DIR}/ns3_${scenario}.log"
    fi

    if [ $? -eq 0 ]; then
        echo "  ✓ Escenario ${scenario} completado"
    else
        echo "  ✗ ERROR en escenario ${scenario}"
    fi
done

cd "${OLDPWD}"

# ------------------------------------------------------------------------------
# RESUMEN
# ------------------------------------------------------------------------------
echo ""
echo "=============================================="
echo "SIMULACIONES COMPLETADAS"
echo "=============================================="
echo ""
echo "Resultados guardados en:"
echo "  - Python:  cap3/modelado/figuras_definitivas/"
echo "  - Python:  cap3/raytracing/figuras_raytracing/"
echo "  - ns-3:    ${NS3_PATH}/results/"
echo "  - Logs:    ${LOG_DIR}/"
echo ""
echo "Próximo paso:"
echo "  python3 cap3/simulacion_ns3/analyze_results.py"
echo ""

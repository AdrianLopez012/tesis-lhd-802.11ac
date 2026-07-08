# Simulación NS-3 — Red IEEE 802.11ac para teleoperación de LHD (Nexa Cerro Lindo, NV1640)

Simulación a nivel de paquete de la red inalámbrica que da servicio a la teleoperación
de un vehículo LHD en las galerías de producción del nivel 1640 (layout block caving
tipo El Teniente). Corresponde al **Capítulo 3** de la tesis (diseño y validación por
simulación).

**Estándar:** IEEE 802.11ac (Wi-Fi 5), 5 GHz, 40 MHz, 2×2 MIMO · QoS 802.11e/WMM
**Escenario:** 5 AP Hawk + 7 AP Cardinal en malla InstaMesh + backbone de fibra en anillo.

---

## Requisitos (KPIs) que la simulación verifica

| Servicio | Indicador | Requisito |
|----------|-----------|-----------|
| Comandos | OWD / PLR | ≤ 20 ms / ≤ 0.5 % (movilidad) |
| Vídeo | Latencia E2E / jitter P95 / throughput / PLR | ≤ 150 ms / ≤ 10 ms / ≥ 38 Mbps / ≤ 1 % |
| Telemetría | OWD / PLR | ≤ 50 ms / ≤ 0.5 % |
| Handover | tiempo de traspaso | ≤ 150 ms (RNF-05) |

**Resultado (10 corridas, escenario de operación):** todos los KPIs se cumplen con
holgura (OWD comandos 2.36 ± 0.20 ms; vídeo E2E 35.77 ± 0.30 ms; PLR < 0.2 %).

---

## Estructura del proyecto

```
simulacion_ns3/
├── lhd-teleop-v3-real.cc        # simulación NS-3 (versión vigente)
├── geometria_nv1640.h           # geometría real (AUTOGENERADO)
├── recorrido_nv1640.h           # recorrido real del LHD (AUTOGENERADO)
├── parametros_rf.py             # parámetros RF de los datasheets (fuente única)
├── run_escenarios_v3.sh         # batería de escenarios (10 semillas + estrés)
├── results/                     # resultados de la simulación (CSV/XML, v3)
├── graficas_simulacion/         # scripts y figuras (ver abajo)
└── historico/                   # versiones anteriores (v2/v8/v9) archivadas
```

### `graficas_simulacion/` — fuente de verdad y figuras

**Fuente única de la geometría:** `mapa_nv1640_datos.py` define galerías, cruceros,
drawpoints, piques y posiciones reales de los AP. De aquí se generan los headers C++
y todas las figuras (evita inconsistencias por copia manual).

| Script | Genera | Descripción |
|--------|--------|-------------|
| `mapa_nv1640_datos.py` | — | **fuente única** de geometría y posiciones AP |
| `generar_geometria_h.py` | `geometria_nv1640.h` | exporta la geometría a C++ |
| `generar_recorrido_h.py` | `recorrido_nv1640.h` | exporta el recorrido del LHD a C++ |
| `plano_nv1640_pro.py` | `plano_nv1640_pro.png` | plano profesional de la zona |
| `mapa_cobertura_pro.py` | `mapa_cobertura_pro.png` | heatmap RSSI + tasa PHY (con ±σ) |
| `contraste_tamograph.py` | `contraste_tamograph.png` | contraste del modelo vs. TamoGraph |
| `animacion_recorrido_lhd.py` | `recorrido_lhd.gif` | animación del recorrido del LHD |
| `resultados_v3.py` | `resultados_*.png` | KPIs multi-semilla, escenarios, handover, cobertura |
| `kpis_v3real.py` | `kpi_v3_*.png` | panel de KPIs + ruta coloreada por RSSI |
| `link_budget.py` | `link_budget.png` | presupuesto de enlace formal |
| `comparacion_kpis.py` | `comparacion_kpis.png` | KPIs vs. requisitos y referencias |
| `arquitectura_red.py` | `arquitectura_red.png/.svg` | diagrama de arquitectura de red |

---

## Cómo reproducir

### 1. Regenerar la geometría y el recorrido (si se editó `mapa_nv1640_datos.py`)
```bash
cd graficas_simulacion
python generar_geometria_h.py     # -> ../geometria_nv1640.h
python generar_recorrido_h.py     # -> ../recorrido_nv1640.h
```

### 2. Compilar y correr la simulación (en WSL con ns-3.40)
```bash
# copiar a scratch/ de ns-3.40 y compilar
cp lhd-teleop-v3-real.cc geometria_nv1640.h recorrido_nv1640.h ~/ns-allinone-3.40/ns-3.40/scratch/
cd ~/ns-allinone-3.40/ns-3.40
./ns3 build scratch/lhd-teleop-v3-real
./ns3 run "lhd-teleop-v3-real --scenario=mobility --simTime=300"
```

**Parámetros (CommandLine):** `--scenario`, `--simTime`, `--lhdSpeed`, `--videoRate`, `--seed`.

### 3. Batería completa de escenarios (10 semillas + baseline + estrés)
```bash
bash run_escenarios_v3.sh          # deja resultados en ~/ns-3.40/results/*_v3_*
```
Copiar los `*_v3_*` a `results/` del repo.

### 4. Generar las figuras
```bash
cd graficas_simulacion
python resultados_v3.py
python kpis_v3real.py
python link_budget.py
python comparacion_kpis.py
python arquitectura_red.py
```

---

## Modelo y decisiones de diseño

- **Propagación:** modelo two-slope calibrado contra el site survey TamoGraph
  (n₁ = 1.9, n₂ = 3.4, d_bp = 40 m, L_sistema = 9.4 dB). Distancia por **ruta de túnel**
  (la señal sigue las galerías, no cruza roca) + penalización NLOS por galería cruzada.
- **Variabilidad de señal (shadowing ±σ):** se analiza en el mapa de cobertura y el
  contraste TamoGraph. La simulación de red es **determinista** (reproducible); el modelo
  de shadowing está en la clase de propagación pero desactivado por defecto, porque el
  roaming 802.11 de NS-3 es sensible a fluctuaciones (ver `historico/` para el detalle).
- **Roaming:** estable con histéresis, emulando el make-before-break del mesh Rajant
  InstaMesh del diseño real.
- **Recorrido de la simulación:** acotado a la **zona de producción** (donde hay
  teleoperación y cobertura); la rampa de acceso es contexto, no se teleopera.

`historico/` conserva las versiones previas (v2/v8/v9, geometría de galería recta) y
sus resultados, por trazabilidad. No forman parte de la versión vigente.

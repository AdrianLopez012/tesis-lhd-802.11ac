# CONTEXTO COMPLETO DEL PROYECTO DE TESIS
# Para usar con Claude Code u otro asistente de código
# Adrián Álvaro López Pascual — 20192733 — PUCP Telecomunicaciones

## OBJETIVO DE LA TESIS
Diseñar una red IEEE 802.11ac tipo malla para la teleoperación de un vehículo LHD 
en galerías subterráneas de la mina Nexa Cerro Lindo (Perú).

## CASO DE ESTUDIO REAL
- Mina: Nexa Cerro Lindo (antes referido como "Block Caving")
- Niveles operativos: NV1640 y NV1970
- Datos disponibles: Site Survey TamoGraph (febrero 2026), BoM real, planos de topología

---

## PARÁMETROS RF CALIBRADOS (USAR ESTOS, NO OTROS)

### Modelo de propagación: TWO-SLOPE (Ecuación 4b)
```
PL(d) = PL(d₀) + 10·n₁·log₁₀(d)                                    para d < d_bp
PL(d) = PL(d₀) + 10·n₁·log₁₀(d_bp) + 10·n₂·log₁₀(d/d_bp)          para d ≥ d_bp
```

Parámetros calibrados con TamoGraph Nexa Cerro Lindo:
- n₁ = 1.9 (near-field, efecto guía de onda, d < 40m)
- n₂ = 3.4 (far-field, modos atenuados, d ≥ 40m)
- d_bp = 40 m (breakpoint)
- σ_LOS = 5.0 dB (shadowing LOS — sincronizado en Python, ns-3 y ray-tracing)
- σ_NLOS = 7.0 dB (shadowing NLOS — sincronizado)
- NLOS_extra = 10 dB (atenuación adicional en intersecciones)
- RMSE del modelo vs TamoGraph: 7.9 dB
- PL(d₀) a 5 GHz, d₀=1m: 46.4 dB

### Equipos reales (del BoM de Nexa)
```
HAWK FE1-5050 (nodo fijo):
  - Pt = 29 dBm (±2 dB)
  - Dual 5 GHz (NO es 2.4+5, son DOS radios de 5 GHz)
  - 2×2 MIMO, 802.11ac
  - Cantidad: 9 (5 en NV1640, 2 en NV1970, + spares)

CARDINAL 23-100237-001 (nodo embarcado en LHD):
  - Pt = 24 dBm
  - Dual-band 802.11ac Wave2
  - 2×2 MIMO en cada radio
  - Cantidad: 16 (7 en NV1640, 9 en NV1970)

ANTENA HELI para Hawk (Poynting RCP-50LHP-11-NM / RCP-50RHP-11-NM):
  - Gt = 11 dBi
  - Bidireccional, polarización circular (izq + der)
  - 5.0-6.0 GHz
  - Se usan en pares (left-hand + right-hand) por Hawk
  - Cantidad: 32 (16 izq + 16 der)

ANTENA para Cardinal/vehículo (Poynting A-HELI-0040-V1-01):
  - Gr = 4.8 dBi
  - Circular polarizada, 2×2 MIMO
  - 2400-2500 MHz y 5000-6000 MHz
  - Cantidad: 4
```

### Presupuesto de enlace
```
EIRP Hawk = Pt + Gt = 29 + 11 = 40 dBm
Pérdidas del sistema (cables, conectores, desajuste pol.):
  - L_system_survey = 19.2 dB (para comparar con TamoGraph, que usa dispositivo ~0 dBi)
  - L_system_real = 9.4 dB (para diseño con Cardinal real + A-HELI-0040)
Pr(d) = Pt + Gt + Gr - PL(d) - L_system_real
       = 29 + 11 + 4.8 - PL(d) - 9.4

Piso de ruido: -91.8 dBm (BW=40MHz, NF=6dB, T=300K)
Frecuencia: 5 GHz
Ancho de banda: 40 MHz
Streams: 2 (MIMO 2×2)
```

### Sensibilidad por MCS (802.11ac, 2 streams, 40 MHz)
```
MCS0  BPSK 1/2     SNR≥5dB   13.5 Mbps   Sens ≈ -94 dBm
MCS1  QPSK 1/2     SNR≥8dB   27.0 Mbps
MCS2  QPSK 3/4     SNR≥11dB  40.5 Mbps
MCS3  16QAM 1/2    SNR≥14dB  54.0 Mbps
MCS4  16QAM 3/4    SNR≥17dB  81.0 Mbps   Sens ≈ -71 dBm
MCS5  64QAM 2/3    SNR≥20dB  108.0 Mbps
MCS6  64QAM 3/4    SNR≥23dB  121.5 Mbps
MCS7  64QAM 5/6    SNR≥26dB  135.0 Mbps
MCS8  256QAM 3/4   SNR≥29dB  162.0 Mbps
MCS9  256QAM 5/6   SNR≥32dB  180.0 Mbps  Sens ≈ -68 dBm
Throughput real ≈ 55% del PHY Rate (overhead protocolos)
```

### Dimensionamiento resultante
```
d_max para video (throughput ≥ 40 Mbps): ~130 m
Separación de diseño (65% de d_max): 84 m
Hawks necesarios para galería de 300m: 5
```

---

## TOPOLOGÍA REAL DE NEXA CERRO LINDO

### Nivel 1640 (NV1640)
- 3 nodos de backbone (Nodo Core, Nodo 01, Nodo 02)
- 5 AP Hawk (fijos en galerías principales)
- 7 AP Cardinal (en cruceros y zanjas)
- 3 barreras AIS láser (seguridad)
- Fibra óptica en anillo: Nodo Core → Nodo 01 → Nodo 02 → Nodo Core
- Galerías: Zanjas 01-10, Cruceros Cx 024-029

### Nivel 1970 (NV1970)
- 2 nodos de backbone (Nodo 03, Nodo 04)
- 2 AP Hawk
- 9 AP Cardinal
- 6 barreras AIS láser
- Fibra óptica: Nodo 03 → Nodo 04 → Nodo 03
- Galerías: Cx 861, 881, 889, 900, 930, etc.

### Infraestructura de backbone
- Switch Core: Fortinet FSR-424F-POE (L2/3, 12 PoE, IP40) × 1
- Switch Acceso: Fortinet FSR-112F-POE (L2, 8 PoE, IP40) × 4
- Módulos SFP: Fortinet FN-TRAN-LX (1G, SMF, 1310nm, 10km) × 10
- Fuente eléctrica: Fortinet SP-RGDIN-240-PS × 5
- Slipstream: Rajant SLP-1025 (APT routing) × 1
- Fibra: monomodo (SMF), 1 Gbps, en anillo

### Arquitectura separada WiFi + CCTV
- Red WiFi: Switch Core propio → switches acceso → Hawks/Cardinals
- Red CCTV: Switch Core propio → switches acceso → cámaras Hikvision
- Ambas comparten backbone de fibra óptica
- CCTV: 9 cámaras Hikvision DS-2CD3656G2T-IZSY, NVR DS-7732NXI-K4

### Sala de monitoreo (superficie)
- Workstation + Estación de operación de control remoto (ROS)
- Monitor CCTV con conexión HDMI al NVR
- Gabinete de comunicaciones con ambos switch core

---

## KPIs Y UMBRALES DE ACEPTACIÓN

| Indicador | Umbral | Fuente |
|-----------|--------|--------|
| RTT comandos | ≤ 40 ms | Hasan et al. [20], 3GPP TR 22.874 |
| Latencia E2E video | ≤ 150 ms | ITU-T G.1010 |
| Jitter P95 video | ≤ 10 ms | ITU-T G.1010 |
| PLR comandos | ≤ 0.1% | Hasan et al. [20] |
| PLR video | ≤ 1.0% | ITU-T G.1010 |
| Throughput uplink video | ≥ 40 Mbps | 4 cámaras H.264 @ 10 Mbps |
| Handover | ≤ 150 ms | Requisito teleoperación |
| Disponibilidad | ≥ 99.9% | Misión crítica |

### Perfiles de tráfico
| Flujo | Dirección | Protocolo | Tasa | Prioridad WMM |
|-------|-----------|-----------|------|---------------|
| Video (4 cámaras) | Uplink | UDP/RTP | 40 Mbps | VI (Video) |
| Comandos control | Bidireccional | TCP | 0.5 Mbps | VO (Voice) |
| Telemetría IoT | Uplink | UDP | 0.1 Mbps | BE |

---

## CÓDIGO PYTHON — ARCHIVOS Y FUNCIONES

### 1. modelo_definitivo.py (PRINCIPAL)
Modelo two-slope calibrado con TamoGraph Nexa.
```
Funciones principales:
  path_loss_two_slope(d, is_nlos) → PL en dB
  received_power_survey(d)        → Pr como TamoGraph (Gr=0, L=19.2)
  received_power_cardinal(d)      → Pr como Cardinal real (Gr=4.8, L=9.4)
  snr(pr)                         → SNR en dB
  snr_to_rate(snr_val)            → PHY Rate en Mbps

Genera 4 gráficas:
  definitiva_01_validacion_twoslope.png  → Modelo vs TamoGraph + bandas ±σ
  definitiva_02_cobertura_phyrate.png    → Mapa 2D cobertura + PHY Rate
  definitiva_03_snr_throughput.png       → SNR y throughput vs distancia
  definitiva_04_dimensionamiento.png     → Separación óptima entre Hawks
```

### 2. raytracing_tunel.py
Ray-tracing por método de imágenes.
```
Parámetros:
  εr = 7.0, σ = 0.02 S/m (roca mineral)
  M_MAX = N_MAX = 12 (625 fuentes imagen)
  Túnel: 5m × 4.5m × 300m

Funciones:
  complex_permittivity(freq, eps_r, sigma)
  fresnel_reflection_TE(theta_i, eps_c)
  fresnel_reflection_TM(theta_i, eps_c)
  image_sources(tx_x, tx_y, W, H, m_max, n_max)
  compute_field_at_point(rx_x, rx_y, rx_z, images, ...)

Genera 4 gráficas:
  grafica_11_mapa_campo_2D.png        → Campo eléctrico 2D en galería
  grafica_12_raytracing_vs_lognormal  → Validación RT vs log-normal
  grafica_13_power_delay_profile.png  → PDP a 25, 75, 150, 250 m
  grafica_14_seccion_transversal.png  → Modos EM en sección transversal
```

### 3. modelo_nexa.py
Topología real de Nexa NV1640 con Hawks y comparación TamoGraph.
```
Genera 3 gráficas:
  grafica_15_validacion_nexa.png      → Cobertura predicha + TamoGraph
  grafica_16_snr_phy_validacion.png   → SNR y PHY validación
  grafica_17_topologia_nexa.png       → Mapa topología con coberturas
```

### 4. validate_models.py (actualizado v2.2)
Validación cruzada Python vs ns-3.
```
Valida:
  - Continuidad del modelo en breakpoint (< 0.5 dB)
  - KPIs ns-3: Throughput, E2E Delay, Jitter P95 (NUEVO), PLR
  - Consistencia de parámetros (σ, n₁, n₂, freq, Pt)
Genera:
  validation_propagation_model.png
```

### 5. fase2_arquitectura.py
Arquitectura de red, QoS, VLANs, BoM.
```
Genera 2 gráficas:
  grafica_06_plan_celdas_detallado.png → Plan de celdas con Pr
  grafica_07_arquitectura_red.png      → Diagrama de arquitectura
```

### 5. analyze_results.py
Post-procesamiento de resultados ns-3.
```
Lee CSVs de ns-3 y genera:
  grafica_08_kpi_comparacion.png    → KPIs por escenario
  grafica_09_timeseries.png         → Métricas temporales
  grafica_10_validacion_kpis.png    → Tabla validación KPIs vs umbrales

Si no hay datos ns-3, genera datos sintéticos para previsualización.
```

---

## CÓDIGO NS-3 — lhd-teleop-v2-nexa.cc

### Estructura del código C++
```
1. TunnelPropagationLossModel (clase custom)
   - Extiende PropagationLossModel de ns-3
   - Implementa two-slope con n₁, n₂, d_bp
   - Zona NLOS en intersección (posición configurable)
   - Shadowing gaussiano con σ configurable

2. CodecDelayApp (clase custom)
   - Extiende Application de ns-3
   - Agrega retardo de codec (35 ms) antes de transmitir
   - Simula T_enc + T_dec de H.264

3. main()
   - Parámetros por línea de comandos (scenario, simTime, nHawks, etc.)
   - Topología: nHawks fijos + 1 LHD móvil + 1 centro de control
   - WiFi: 802.11ac, 40 MHz, 5 GHz, ad-hoc
   - Movilidad: WaypointMobilityModel (ciclo ida-vuelta con pausas)
   - Tráfico: video UDP 40Mbps + comandos TCP 0.5Mbps + telemetría UDP 0.1Mbps
   - OLSR como protocolo de enrutamiento
   - FlowMonitor para métricas
   - Exporta CSV + XML
```

### Parámetros actuales en lhd-teleop-v2-nexa.cc
```cpp
// Modelo de canal
ExponentLOS = 1.9    // n₁ (calibrado Nexa)
ExponentNLOS = 3.4   // n₂ (calibrado Nexa)
SigmaLOS = 5.0       // dB
SigmaNLOS = 7.0      // dB
Frequency = 5.0e9    // Hz
IntersectionX = 150  // posición zona NLOS

// Equipos
txPowHawk = 29.0     // dBm (Hawk FE1-5050)
txPowCard = 24.0     // dBm (Cardinal)
TxGain Hawks = 11.0  // dBi (HELI)
RxGain Hawks = 5.0   // dBi
TxGain Cardinal = 5.0
RxGain Cardinal = 11.0

// Topología
nHawks = 5
sep = 84.0           // metros (calibrado)
simTime = 300.0      // segundos (~2 ciclos acarreo)
lhdSpeed = 2.22      // m/s (8 km/h)
codecDelayMs = 35.0  // ms (H.264 encode+decode)

// WiFi
WIFI_STANDARD_80211ac
ChannelSettings = "{0, 40, BAND_5GHZ, 0}"
MinstrelHtWifiManager (rate adaptation)
AdhocWifiMac

// Tráfico
videoRate = 40 Mbps UDP (con CodecDelayApp)
cmdRate = 0.5 Mbps TCP (OnOff, constant)
telRate = 0.1 Mbps UDP (OnOff, 0.1s on / 0.9s off)
```

### Cómo compilar y correr
```bash
# Copiar a ns-3
cp lhd-teleop-v2-nexa.cc ~/ns-allinone-3.40/ns-3.40/scratch/

# Compilar
cd ~/ns-allinone-3.40/ns-3.40
./ns3 build scratch/lhd-teleop-v2-nexa

# Correr escenario baseline
mkdir -p results
./ns3 run "lhd-teleop-v2-nexa --scenario=baseline --simTime=300 --seed=1"

# Otros escenarios
./ns3 run "lhd-teleop-v2-nexa --scenario=sep_100m --nHawks=4 --separation=100 --seed=1"
./ns3 run "lhd-teleop-v2-nexa --scenario=video_20mbps --videoRate=20 --seed=1"
./ns3 run "lhd-teleop-v2-nexa --scenario=lhd_rapido --lhdSpeed=3.33 --seed=1"
```

### Parámetros actualizados en lhd-teleop-v2-nexa.cc (v5.0)
```cpp
SigmaLOS  = 5.0   // dB (coincide con modelo Python)
SigmaNLOS = 7.0   // dB
// Shadowing gaussiano ACTIVO en DoCalcRxPower (corr. A):
//   sigma = sigNLOS si está en zona NLOS, sigLOS si LOS
//   usa NormalRandomVariable de ns-3 → varía con cada semilla
// Handover más rápido en StaWifiMac del LHD (corr. B):
MaxMissedBeacons    = 3    // declara AP perdido tras 3 beacons (~300ms)
AssocRequestTimeout = 50ms // reintento de asociación más rápido
// FlowMonitor con histogramas activados:
DelayBinWidth   = 1 ms   (rango 0-500 ms)
JitterBinWidth  = 0.5 ms (rango 0-50 ms)
// Exporta columnas en CSV:
delay_p95_ms, jitter_p95_ms, total_e2e_p95_ms
// Salida: results/<scenario>_v5_flow_stats.csv (NO pisa v4)
```

### Versiones de resultados y qué usar en la tesis
```
v3 → escenario estático (LOS limpio, sin recorrido real 2D) → RESULTADOS PRINCIPALES
v4 → movilidad 2D real, shadowing OFF, handover lento → caso de referencia (PLR grave)
v5 → movilidad 2D real, shadowing ON, handover rápido → análisis complementario mejorado
```

### Problemas conocidos y soluciones
```
1. "ChannelWidth cannot be set" → usar ChannelSettings con BAND_5GHZ
2. "PointToPointHelper not declared" → ya eliminado, control usa WiFi
3. "No default channel found" → asegurar BAND_5GHZ (802.11ac solo 5GHz)
4. Resultados "demasiado perfectos" (v1) → v2 incluye codec delay + multi-hop
5. "P95 siempre 0" → verificar que FlowMonitor tenga histogramas activos (v2.2+)
6. "Semillas iguales" (v4) → shadowing estaba desactivado; corregido en v5 (corr. A)
7. "PLR video 8.76%" (v4) → handover ~200ms por defecto; reducido a ~50ms en v5 (corr. B)
```

---

## DATOS DE TAMOGRAPH PARA CALIBRACIÓN

Datos extraídos del Site Survey TamoGraph (NV1640):
```
Distancia (m) | Pr observada (dBm) | Rango
5             | -45 a -50          | Cerca del AP
15            | -50 a -55          |
30            | -58 a -63          |
50            | -63 a -68          |
70            | -68 a -74          |
90            | -74 a -80          |
110           | -80 a -85          | Borde de cobertura

Config TamoGraph: 802.11ac, 40 MHz, 2 streams
Signal correction 5 GHz: +5 dBm
```

Calibración por regresión:
```python
# Con dispositivo de survey (Gr ≈ 0 dBi):
# PL_obs = (Pt + Gt + Gr_survey) - Pr_tamo = 40 - Pr_tamo
# Regresión lineal por tramos da:
#   Zona 1 (d < 40m): n₁ = 1.9
#   Zona 2 (d ≥ 40m): n₂ = 3.4
#   L_system_survey = 19.2 dB
#   RMSE = 3.25 dB (regresión pura)
#   RMSE = 7.9 dB (modelo two-slope completo)
```

---

## QUÉ FALTA POR HACER

### Prioridad ALTA
1. Correr ns-3 v2 con parámetros Nexa (lhd-teleop-v2-nexa.cc)
2. Generar gráficas con datos reales de ns-3 (analyze_results.py)
3. Insertar gráficas en Capítulo 3 Word

### Prioridad MEDIA
4. Redactar Capítulo 4 (validación técnica + económica)
5. Actualizar modelo_definitivo.py si se obtienen más datos de Billy/Nexa

### Prioridad BAJA
6. Introducción + Conclusiones + Recomendaciones
7. Formato final (índices, portada, abstract)

---

## LIMITACIONES A DECLARAR EN LA TESIS

1. Paredes uniformes (εr y σ constantes, no modela irregularidades)
2. Sin obstáculos dinámicos (vehículos, ventiladores en galería)
3. Calibración contra un solo site survey (Nexa Cerro Lindo, feb 2026)
4. Modelo 2D (sin propagación vertical entre niveles)
5. NLOS simplificado (atenuación fija, no ray-tracing dinámico)
6. OLSR como aproximación de InstaMesh (OLSR es L3, InstaMesh es L2)
7. Un solo LHD (escalabilidad a múltiples LHDs se discute cualitativamente)
8. Sin mediciones in-situ propias (trabajo de gabinete)

---

## ESTRUCTURA DEL PROYECTO EN DISCO

```
tesis_proyecto/
├── cap3/
│   ├── modelado/
│   │   ├── modelo_definitivo.py      ← PRINCIPAL: two-slope calibrado
│   │   ├── modelo_nexa.py            ← Topología real Nexa NV1640
│   │   └── fase2_arquitectura.py     ← Arquitectura, QoS, VLANs
│   ├── raytracing/
│   │   └── raytracing_tunel.py       ← Método de imágenes, Fresnel
│   └── simulacion_ns3/
│       ├── lhd-teleop-v2-nexa.cc     ← ns-3 con parámetros calibrados
│       ├── run_simulation.sh         ← Script automatización
│       └── analyze_results.py        ← Post-proceso gráficas
├── figuras/                          ← 17 gráficas PNG
└── cap3_redaccion/
    └── Capitulo3_Completo.docx       ← Redacción completa
```

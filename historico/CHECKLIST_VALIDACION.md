# CHECKLIST DE VALIDACIÓN - TESIS
## Diseño de Red IEEE 802.11ac para Teleoperación LHD
**Autor:** Adrián López - 20192733
**Versión:** 2.1 (Calibrado con datasheets Rajant)

---

## 📋 PARTE 1: CONSISTENCIA DE PARÁMETROS

### 1.1. Verificar Parámetros de Equipos

| Parámetro | Valor Correcto | modelo_definitivo.py | raytracing_tunel.py | lhd-teleop-v2-nexa.cc | ✓ |
|-----------|----------------|---------------------|---------------------|-----------------------|---|
| PT_HAWK | 30.0 dBm | Línea 54 | Línea 81 | Línea 206 | ☐ |
| PT_CARDINAL | 23.0 dBm | Línea 58 | Línea 81 | Línea 207 | ☐ |
| GT_HAWK | 11.0 dBi | Línea 55 | Línea 83 | Línea 241 | ☐ |
| GR_CARDINAL | 4.8 dBi | Línea 59 | Línea 84 | Línea 242 | ☐ |
| FREQ | 5.0 GHz | Línea 68 | Línea 68 | Línea 224 | ☐ |

**Acción si NO coinciden:** Usar valores de datasheet oficial (ver PDFs en `Downloads/`)

---

### 1.2. Verificar Parámetros del Modelo de Propagación

| Parámetro | Valor Correcto | Python | ns-3 | Fuente |
|-----------|----------------|--------|------|--------|
| n₁ (near-field) | 1.9 | Línea 98 | Línea 52 | Calibración TamoGraph |
| n₂ (far-field) | 3.4 | Línea 99 | Línea 56 | Calibración TamoGraph |
| d_bp (breakpoint) | 40.0 m | Línea 95 | Línea 80 | Calibración TamoGraph |
| σ_LOS | 5.0 dB | Línea 100 | Línea 60 | Calibración TamoGraph |
| σ_NLOS | 7.0 dB | Línea 101 | Línea 64 | Calibración TamoGraph |
| NLOS_extra | 10.0 dB | Línea 106 | Línea 126 | Modelo teórico |

☐ **Todos los parámetros coinciden**

---

## 📋 PARTE 2: EJECUCIÓN Y RESULTADOS

### 2.1. Ejecutar Modelos Python

```bash
cd cap3/modelado
python3 modelo_definitivo.py
```

☐ Ejecutado sin errores
☐ Genera 4 gráficas en `figuras_definitivas/`:
- ☐ `definitiva_01_validacion_twoslope.png` (RMSE debe ser <8 dB)
- ☐ `definitiva_02_cobertura_phyrate.png`
- ☐ `definitiva_03_snr_throughput.png`
- ☐ `definitiva_04_dimensionamiento.png` (d_design ≈ 84m)

**Valores esperados:**
- RMSE ≈ 7.9 dB
- d_max video ≈ 130 m
- d_design ≈ 84 m
- Hawks para 300m: 5

---

```bash
cd cap3/raytracing
python3 raytracing_tunel.py  # Tarda 2-5 minutos
```

☐ Ejecutado sin errores
☐ Frecuencia mostrada: **5.0 GHz** (NO 2.4 GHz)
☐ Exponente efectivo n ≈ 1.8-2.0 (debe coincidir con n₁)
☐ Genera 4 gráficas en `figuras_raytracing/`:
- ☐ `grafica_11_mapa_campo_2D.png`
- ☐ `grafica_12_raytracing_vs_lognormal.png`
- ☐ `grafica_13_power_delay_profile.png`
- ☐ `grafica_14_seccion_transversal.png`

---

### 2.2. Compilar y Ejecutar ns-3

```bash
cd ~/ns-allinone-3.40/ns-3.40
cp /mnt/c/Users/Adrian\ Lopez/Documents/tesis_proyecto/cap3/simulacion_ns3/lhd-teleop-v2-nexa.cc scratch/
./ns3 build scratch/lhd-teleop-v2-nexa
```

☐ Compilación exitosa (0 errores, 0 warnings)
☐ Mensaje de versión muestra: "Simulacion v2.1 (calibrado Nexa)"

```bash
mkdir -p results
./ns3 run "lhd-teleop-v2-nexa --scenario=baseline_v21 --simTime=300 --seed=1"
```

☐ Ejecutado sin errores
☐ Archivos generados:
- ☐ `results/baseline_v21_v2_flow_stats.csv`
- ☐ `results/baseline_v21_v2_flowmon.xml`

**Verificar en la salida de consola:**
```
Modelo: Two-slope d_bp=40m n1=1.9 n2=3.4
Tx: Hawk=30dBm Cardinal=23dBm
```

☐ Modelo two-slope confirmado
☐ Potencias Tx correctas

---

### 2.3. Validar Resultados ns-3 contra KPIs

```bash
cd /mnt/c/Users/Adrian\ Lopez/Documents/tesis_proyecto/cap3/simulacion_ns3
python3 validate_models.py
```

☐ Script ejecutado sin errores
☐ **Validación 1 (Propagación):**
  - ☐ Discontinuidad en breakpoint < 0.5 dB
  - ☐ Gráfica `validation_propagation_model.png` generada

☐ **Validación 2 (KPIs ns-3):**
  - ☐ Video Throughput ≥ 40 Mbps: **✓ PASA**
  - ☐ Video E2E Delay ≤ 150 ms: **✓ PASA**
  - ☐ Video PLR ≤ 1%: **✓ PASA**
  - ☐ Comandos RTT ≤ 40 ms: **✓ PASA**
  - ☐ Comandos PLR ≤ 0.1%: **✓ PASA**

**Si algún KPI falla:**
- Revisar separación entre Hawks (puede necesitar ajuste)
- Verificar que modelo two-slope está activo
- Comparar con resultados Python

---

## 📋 PARTE 3: GRÁFICAS PARA LA TESIS

### 3.1. Gráficas Obligatorias (Capítulo 3)

| # | Nombre | Archivo | Sección Tesis | ✓ |
|---|--------|---------|---------------|---|
| 1 | Validación two-slope vs TamoGraph | `definitiva_01_validacion_twoslope.png` | 3.2.2 | ☐ |
| 2 | Mapa de cobertura + PHY Rate | `definitiva_02_cobertura_phyrate.png` | 3.2.3 | ☐ |
| 3 | SNR y throughput vs distancia | `definitiva_03_snr_throughput.png` | 3.2.4 | ☐ |
| 4 | Dimensionamiento óptimo | `definitiva_04_dimensionamiento.png` | 3.2.5 | ☐ |
| 11 | Ray-tracing: Mapa 2D campo | `grafica_11_mapa_campo_2D.png` | 3.3.1 | ☐ |
| 12 | Ray-tracing vs log-normal | `grafica_12_raytracing_vs_lognormal.png` | 3.3.2 | ☐ |

### 3.2. Gráficas Opcionales (Apéndices)

| # | Nombre | Archivo | Sección | ✓ |
|---|--------|---------|---------|---|
| 13 | Power Delay Profile | `grafica_13_power_delay_profile.png` | Apéndice A | ☐ |
| 14 | Sección transversal | `grafica_14_seccion_transversal.png` | Apéndice A | ☐ |
| - | Validación modelo | `validation_propagation_model.png` | Apéndice B | ☐ |

---

## 📋 PARTE 4: DOCUMENTACIÓN Y JUSTIFICACIÓN

### 4.1. Limitaciones Declaradas (Sección 3.2.1)

☐ **1. Paredes uniformes:** Declarado y justificado
☐ **2. Sin obstáculos dinámicos:** Declarado y justificado
☐ **3. Calibración contra un site survey:** Mencionado (TamoGraph feb 2026)
☐ **4. Modelo 2D:** Justificado (NV1640 y NV1970 separados)
☐ **5. NLOS simplificado:** Declarado (atenuación fija 10 dB)
☐ **6. OLSR vs InstaMesh:** Explicado en texto
☐ **7. Un solo LHD:** Justificado (escalabilidad discutida cualitativamente)
☐ **8. Sin mediciones propias:** Aclarado (trabajo de gabinete con datos Nexa)

### 4.2. Referencias a Datasheets

☐ **Hawk FE1-5050:** Referenciado en Capítulo 2 (Equipos)
☐ **Cardinal AG1-5250M:** Referenciado en Capítulo 2
☐ **Poynting HELI:** Referenciado con código exacto (RCP-50LHP/RHP-11-NM)
☐ **Poynting A-EPNT-0007:** Verificar con Billy si es la correcta

### 4.3. Justificación de Parámetros Calibrados

☐ **n₁ = 1.9:** Explicado como "near-field, efecto guía de onda"
☐ **n₂ = 3.4:** Explicado como "far-field, modos atenuados"
☐ **d_bp = 40m:** Justificado con regresión TamoGraph
☐ **RMSE = 7.9 dB:** Comparado con literatura (<10 dB aceptable)

---

## 📋 PARTE 5: VERIFICACIÓN FINAL PRE-ENTREGA

### 5.1. Consistencia General

☐ Todas las gráficas tienen títulos descriptivos
☐ Todas las gráficas tienen ejes con unidades
☐ Todas las gráficas están en alta resolución (300 dpi)
☐ Figuras numeradas consecutivamente (Fig. 3.1, 3.2, ...)
☐ Todas las figuras referenciadas en el texto

### 5.2. Código Entregable

☐ **modelo_definitivo.py:** Comentado y limpio
☐ **raytracing_tunel.py:** Comentado y limpio
☐ **lhd-teleop-v2-nexa.cc:** Comentado y limpio
☐ **validate_models.py:** Funciona y genera reporte
☐ **run_all_simulations.sh:** Funciona end-to-end
☐ **CONTEXTO_PROYECTO_TESIS.md:** Actualizado con v2.1

### 5.3. Archivos de Soporte

☐ `README.md` con instrucciones de ejecución
☐ `requirements.txt` para dependencias Python
☐ PDFs de datasheets en carpeta `documentacion/`
☐ Datos TamoGraph (o referencia a fuente)

---

## 📋 PARTE 6: CHECKLIST DE ENTREGA

### 6.1. Documento de Tesis (Word/PDF)

☐ **Capítulo 3 - Diseño de Red:**
  - ☐ Sección 3.1: Modelo de propagación (con Ec. 4b two-slope)
  - ☐ Sección 3.2: Calibración con TamoGraph
  - ☐ Sección 3.3: Validación por ray-tracing
  - ☐ Sección 3.4: Dimensionamiento (84m, 5 Hawks)
  - ☐ Sección 3.5: Topología Nexa (NV1640 y NV1970)

☐ **Capítulo 4 - Resultados:**
  - ☐ Tabla de KPIs (con valores obtenidos de ns-3)
  - ☐ Comparación contra umbrales
  - ☐ Análisis de validación

☐ **Capítulo 5 - Conclusiones:**
  - ☐ Modelo two-slope es adecuado (RMSE < 8 dB)
  - ☐ KPIs cumplen para teleoperación
  - ☐ Limitaciones y trabajos futuros

### 6.2. Código Fuente (GitHub/ZIP)

☐ Estructura de carpetas clara (`cap3/modelado`, `cap3/raytracing`, `cap3/simulacion_ns3`)
☐ Scripts ejecutables con permisos correctos
☐ Todos los archivos Python con encoding UTF-8
☐ Código ns-3 compatible con versión 3.40

---

## ✅ CHECKLIST FINAL

**Antes de entregar, verificar:**

- [ ] Todos los ☐ de este documento están marcados ✓
- [ ] Resultados ns-3 cumplen TODOS los KPIs
- [ ] Gráficas Python y ns-3 son consistentes
- [ ] Modelo two-slope funciona correctamente en ns-3
- [ ] Frecuencia 5 GHz en todos los modelos
- [ ] Potencias Tx según datasheets oficiales
- [ ] Documento de tesis referencia correctamente las gráficas
- [ ] Código está comentado y es reproducible

**Firma de revisión:**

Fecha: _______________
Revisor: _______________
Aprobado: ☐ SÍ  ☐ NO (motivo: ___________________)

---

**Última actualización:** 2026-05-03
**Versión del código:** 2.1 (Calibrado Nexa + Two-slope)

# PLAN DE MEJORAS CONTINUAS - FASE 2
## Tesis: Red IEEE 802.11ac para Teleoperación LHD - Nexa Cerro Lindo
**Autor:** Adrián López - 20192733
**Versión actual:** 2.1 (Calibrado con datasheets Rajant)

---

## ✅ COMPLETADO - FASE 1

- [x] Corregir potencias Tx según datasheets oficiales (Hawk 30dBm, Cardinal 23dBm)
- [x] Corregir frecuencia en ray-tracing (2.4 → 5.0 GHz) **CRÍTICO**
- [x] Implementar modelo two-slope con breakpoint en ns-3
- [x] Sincronizar parámetros entre Python, ray-tracing y ns-3
- [x] Scripts de ejecución y validación automática

---

## 🟡 FASE 2 - MEJORAS IMPORTANTES (Prioridad MEDIA)

### **2.1. Cálculo de Percentil 95 (P95) en ns-3** ⭐⭐⭐
**Problema:** FlowMonitor solo calcula promedio de jitter, pero KPI requiere P95
**Impacto:** MEDIO - Necesario para validar umbral jitter P95 ≤ 10ms
**Esfuerzo:** MEDIO (~2-3 horas)

**Implementación:**
```cpp
// En lhd-teleop-v2-nexa.cc, después de FlowMonitor:
std::vector<double> delays, jitters;

for (auto &it : stats) {
    // Agregar cada delay/jitter individual a vector
    // (requiere modificar FlowMonitor para exportar datos raw)
}

std::sort(delays.begin(), delays.end());
double p95_delay = delays[delays.size() * 0.95];

std::sort(jitters.begin(), jitters.end());
double p95_jitter = jitters[jitters.size() * 0.95];
```

**Alternativa más simple:**
- Usar `ns3::TimeSeriesAdaptor` para capturar cada muestra
- Post-procesar con Python: `np.percentile(jitter_samples, 95)`

**Referencias:**
- ns-3 manual sección 15.3: Custom metrics con flow monitor
- Tu KPI tabla línea 147: "Jitter P95 video ≤ 10 ms"

---

### **2.2. Actualizar Tabla de Sensibilidades** ⭐⭐
**Problema:** Sensibilidades en código son aproximadas, no del datasheet
**Impacto:** BAJO-MEDIO - Afecta precisión de d_max
**Esfuerzo:** BAJO (~30 min)

**Acción:**
1. Leer datasheet Rajant Hawk página 3 (ya lo tienes):
   - @ 6 Mbps, 20 MHz: -94 dBm
   - @ 866.7 Mbps, 80 MHz: -68 dBm
2. Interpolar para 40 MHz (tu BW):
   - MCS4 (81 Mbps, 40MHz): ≈ -71 dBm
   - MCS9 (180 Mbps, 40MHz): ≈ -68 dBm
3. Actualizar dict SENS en `modelo_definitivo.py:81-85`

---

### **2.3. Verificar Modelo de Antena Cardinal** ⭐⭐
**Problema:** BoM lista "A-EPNT-0007" pero código usa "A-HELI-0040"
**Impacto:** MEDIO - Puede afectar ganancia Gr
**Esfuerzo:** BAJO (~15 min + buscar datasheet)

**Acción:**
1. Confirmar con Billy/Nexa qué antena se usa realmente
2. Buscar datasheet de la correcta
3. Si Gr ≠ 4.8 dBi, recalibrar modelo

---

## 🟢 FASE 3 - MEJORAS OPCIONALES (Prioridad BAJA)

### **3.1. Modelo 2.5D con Alturas Variables** ⭐
**Descripción:** Hawks a alturas ligeramente diferentes (±0.5m) por irregularidades del terreno
**Impacto:** BAJO - Solo realismo
**Esfuerzo:** BAJO (~1 hora)

**Implementación:**
```python
# En modelo_definitivo.py, HAWKS con altura variable
HAWKS = [
    {"id": "AP-01", "x": 50,  "y": 20, "z": 2.2},  # +0.2m
    {"id": "AP-02", "x": 50,  "y": 80, "z": 1.8},  # -0.2m
    ...
]

# Calcular distancia 3D en vez de 2D
dist = np.sqrt((X - hawk["x"])**2 + (Y - hawk["y"])**2 + (Z - hawk["z"])**2)
```

---

### **3.2. Análisis de Sensibilidad de Parámetros** ⭐
**Descripción:** Variar n₁, n₂, d_bp, σ para ver impacto en KPIs
**Impacto:** BAJO - Para sección "limitaciones" de tesis
**Esfuerzo:** MEDIO (~1 día)

**Ejemplo:**
```python
# Script sensitivity_analysis.py
for n1 in [1.7, 1.8, 1.9, 2.0, 2.1]:
    for n2 in [3.0, 3.2, 3.4, 3.6, 3.8]:
        # Recalcular d_max, throughput
        # Graficar heatmap de impacto
```

---

### **3.3. Comparación con Otros Modelos de Túnel** ⭐
**Descripción:** Comparar tu two-slope vs modelos ITU-R, 3GPP
**Impacto:** BAJO - Enriquece Estado del Arte
**Esfuerzo:** MEDIO (~2 días)

**Referencias:**
- ITU-R P.1238-11 (2021): Indoor/tunnel propagation
- 3GPP TR 38.901: Channel model for 5G
- Comparar RMSE de cada modelo vs TamoGraph

---

### **3.4. Múltiples LHDs** ⭐
**Descripción:** Simular 2-3 LHDs simultáneos (escalabilidad)
**Impacto:** BAJO - Ya discutes cualitativamente
**Esfuerzo:** ALTO (~2-3 días, modificar ns-3)

**Limitación actual:** Tu limitación #7 dice "Un solo LHD"
**Si implementas:** Cambia a "Validado con 1 LHD, escalabilidad a N LHDs verificada por simulación"

---

## 🔴 FASE 4 - MEJORAS AVANZADAS (Solo si sobra tiempo)

### **4.1. Handover Explícito** ⭐
**Descripción:** Modelar handover L2 de InstaMesh (no solo OLSR L3)
**Esfuerzo:** ALTO - Requiere implementar custom MAC en ns-3

### **4.2. Interferencia de Equipos Externos** ⭐
**Descripción:** Modelar interferencia de otros equipos (ventiladores, vehículos)
**Esfuerzo:** ALTO - Requiere modelo de obstáculos dinámicos

### **4.3. Propagación Inter-Nivel (3D real)** ⭐
**Descripción:** Modelar túnel vertical entre NV1640 ↔ NV1970
**Esfuerzo:** MUY ALTO - Requiere datos 3D de la mina

---

## 📋 RECOMENDACIÓN FINAL

**Para completar tu tesis en tiempo:**

### **Hacer (2-3 días):**
1. ✅ Ejecutar `run_all_simulations.sh` con parámetros v2.1
2. ✅ Ejecutar `validate_models.py` para verificar consistencia
3. ✅ Implementar cálculo P95 de jitter (Mejora 2.1)
4. ✅ Verificar antena Cardinal (Mejora 2.3)
5. ✅ Generar todas las gráficas para Cap 3

### **Opcional (si sobra tiempo):**
6. ⭕ Actualizar sensibilidades (Mejora 2.2)
7. ⭕ Análisis de sensibilidad (Mejora 3.2)

### **NO hacer (dejar para futuras mejoras):**
- ❌ Modelo 3D real
- ❌ Múltiples LHDs
- ❌ Handover explícito

**Justificación:** Tu modelo ya está bien calibrado y validado. Las mejoras FASE 2 son suficientes para una tesis sólida. FASE 3-4 son para publicaciones futuras.

---

## 📊 TRACKING DE PROGRESO

| Mejora | Prioridad | Estado | Fecha | Notas |
|--------|-----------|--------|-------|-------|
| FASE 1: Calibración datasheets | 🔴 ALTA | ✅ COMPLETADO | 2026-05-03 | v2.1 |
| 2.1: P95 jitter y delay | 🟡 MEDIA | ✅ COMPLETADO | 2026-05-03 | v2.2 — histogramas FlowMonitor |
| 2.2: Sincronizar σ Python/ns-3 | 🟡 MEDIA | ✅ COMPLETADO | 2026-05-03 | σ_LOS=5, σ_NLOS=7 en todos |
| 2.3: Antena Cardinal | 🟡 MEDIA | ⭕ PENDIENTE | - | Confirmar con Billy: A-EPNT-0007 o A-HELI-0040 |
| 3.1: Modelo 2.5D | 🟢 BAJA | ⭕ PENDIENTE | - | - |
| 3.2: Análisis sensibilidad | 🟢 BAJA | ⭕ PENDIENTE | - | - |

---

## 🔗 REFERENCIAS ÚTILES

1. **ns-3 FlowMonitor Documentation:**
   https://www.nsnam.org/docs/release/3.40/models/html/flow-monitor.html

2. **ITU-R P.1238-11 (Indoor propagation):**
   https://www.itu.int/rec/R-REC-P.1238/

3. **Rajant Datasheets:**
   - Hawk FE1-5050: `Rajant_SpecSheet_Hawk_040926.pdf`
   - Cardinal AG1-5250M: `02-100157-001.pdf`

4. **TamoGraph Site Survey:**
   - Manual: https://www.tamos.com/products/wifi-site-survey/
   - Tutorial calibración: https://www.tamos.com/kb/calibration

---

**Última actualización:** 2026-05-03
**Próxima revisión:** Después de correr simulaciones v2.1

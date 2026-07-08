"""
Parámetros RF de los equipos reales — NV1640 Nexa Cerro Lindo
=============================================================
Extraídos de los datasheets oficiales (compendio 2026-07-06). Estándar de la
tesis: IEEE 802.11ac Wave 2, 5 GHz, MIMO 2x2, OFDM hasta 256-QAM.

Estos valores alimentan la simulación NS-3 (potencias, ganancias, sensibilidad).
Fuente única de verdad de los parámetros RF; el .cc los debe usar.
"""

# ---------------- ESTÁNDAR ----------------
WIFI_STANDARD   = "802.11ac"     # Wave 2
BANDA           = "5GHz"
FREQ_HZ         = 5.0e9          # frecuencia de referencia del modelo (802.11ac 5 GHz);
                                # consistente con el canal 40 MHz usado en la simulación NS-3
ANCHO_CANAL_MHZ = 40            # típico en túnel (40 MHz; 80 MHz posible)
MIMO_STREAMS    = 2             # 2x2 MIMO

# ---------------- AP HAWK (FE1-5050) — nodos fijos en galerías ----------------
HAWK = {
    "tx_power_dbm":   30.0,      # máx (±2 dB)
    "tx_gain_dbi":    11.0,      # antena HELI RCP-50 (circular pol., 5-6 GHz)
    "rx_gain_dbi":    11.0,
    "antenas":        2,         # 2x2 MIMO (par L/R para diversidad)
    "rate_max_mbps":  866.7,     # por transceptor (2 transceptores)
    # sensibilidad de recepción (dBm) por tasa/ancho (del datasheet)
    "rx_sens_min_dbm": -94.0,    # @6 Mbps / 20 MHz
    "rx_sens_max_dbm": -68.0,    # @866.7 Mbps / 80 MHz
    "conector":       "Type N",
}

# ---------------- AP CARDINAL (AG1-5250M) — breadcrumb / móvil ----------------
CARDINAL = {
    "tx_power_dbm":   23.0,      # 5 GHz (±2 dB); dual-band 22 dBm
    "tx_gain_dbi":    7.5,       # antena EPNT-7 (omni, 5-6 GHz)
    "rx_gain_dbi":    7.5,
    "antenas":        2,         # 2x2 MIMO Wave 2
    "rate_max_mbps":  866.7,
    "instamesh":      True,      # mesh Layer 2, sin root node
    "conector":       "SMA",
}

# ---------------- ANTENA DEL VEHÍCULO LHD (HELI-40) ----------------
# El LHD embarca un nodo (tipo Cardinal) con esta antena.
LHD_ANTENA = {
    "tx_power_dbm":   23.0,      # radio embarcado (Cardinal)
    "gain_dbic":      4.8,       # HELI-40, circular polarizada, bi-direccional
    "vswr":           2.0,
    "mimo":           2,
    "polarizacion":   "circular (LHCP/RHCP)",
    "direccional":    "bi-direccional (túnel/NLOS)",
    "conector":       "N-Type",
}

# ---------------- BACKBONE / RED ----------------
BACKBONE = {
    "switch_core":    "Fortinet FSR-424F-POE",   # 40/10 GE uplinks
    "switch_acceso":  "Fortinet FSR-112F-POE",
    "fibra":          "SMF 1GE LX 1310nm 10km (FN-TRAN-LX)",
    "gateway_mesh":   "Rajant SLP-1025 (APT routing)",
    "topologia":      "mesh InstaMesh entre AP + backbone fibra en anillo",
}

# ---------------- PÉRDIDAS DE SISTEMA (para el modelo de propagación) ----------------
# L_system: cables, conectores, margen de instalación. Con Cardinal + HELI-40
# el valor de referencia usado en el modelo two-slope fue ~9.4 dB.
L_SYSTEM_DB = 9.4

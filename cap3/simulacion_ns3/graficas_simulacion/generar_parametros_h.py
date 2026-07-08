"""
Genera parametros_rf.h (header C++) desde parametros_rf.py
==========================================================
Exporta los parámetros RF de los datasheets (fuente única de verdad) a un header
C++ que consume la simulación NS-3, para que el .cc no tenga valores hardcodeados
y todo provenga del mismo sitio (evita desincronización).

Salida: ../parametros_rf.h
Ejecutar: python generar_parametros_h.py
"""
import os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rf", os.path.join(HERE, "..", "parametros_rf.py"))
RF = importlib.util.module_from_spec(spec); spec.loader.exec_module(RF)

out = os.path.join(HERE, "..", "parametros_rf.h")
with open(out, "w", encoding="utf-8") as f:
    f.write("// parametros_rf.h — AUTOGENERADO desde parametros_rf.py — NO EDITAR\n")
    f.write("// Parametros RF de los datasheets (fuente unica). Regenerar con:\n")
    f.write("//   python graficas_simulacion/generar_parametros_h.py\n")
    f.write("#ifndef PARAMETROS_RF_H\n#define PARAMETROS_RF_H\n\n")
    f.write("namespace rf {\n")
    f.write(f"  // Estandar {RF.WIFI_STANDARD} {RF.BANDA} {RF.ANCHO_CANAL_MHZ}MHz {RF.MIMO_STREAMS}x{RF.MIMO_STREAMS} MIMO\n")
    f.write(f"  static const double FREQ_HZ        = {RF.FREQ_HZ:.6g};\n")
    f.write(f"  static const double ANCHO_CANAL_MHZ= {RF.ANCHO_CANAL_MHZ:.1f};\n\n")
    f.write("  // AP Hawk (galerias)\n")
    f.write(f"  static const double HAWK_TXP_DBM   = {RF.HAWK['tx_power_dbm']:.1f};\n")
    f.write(f"  static const double HAWK_GT_DBI    = {RF.HAWK['tx_gain_dbi']:.1f};\n\n")
    f.write("  // AP Cardinal (cruceros / mesh)\n")
    f.write(f"  static const double CARD_TXP_DBM   = {RF.CARDINAL['tx_power_dbm']:.1f};\n")
    f.write(f"  static const double CARD_GT_DBI    = {RF.CARDINAL['tx_gain_dbi']:.1f};\n\n")
    f.write("  // Antena del LHD (HELI-40)\n")
    f.write(f"  static const double LHD_TXP_DBM    = {RF.LHD_ANTENA['tx_power_dbm']:.1f};\n")
    f.write(f"  static const double LHD_GR_DBI     = {RF.LHD_ANTENA['gain_dbic']:.1f};\n\n")
    f.write("  // Perdidas de sistema (cables/conectores/margen)\n")
    f.write(f"  static const double L_SYSTEM_DB    = {RF.L_SYSTEM_DB:.1f};\n")
    f.write("} // namespace rf\n#endif\n")

print(f"[OK] {os.path.abspath(out)}")
print(f"  FREQ={RF.FREQ_HZ:.3g} Hz | Hawk {RF.HAWK['tx_power_dbm']}/{RF.HAWK['tx_gain_dbi']} "
      f"| Cardinal {RF.CARDINAL['tx_power_dbm']}/{RF.CARDINAL['tx_gain_dbi']} "
      f"| LHD Gr={RF.LHD_ANTENA['gain_dbic']} | L_sys={RF.L_SYSTEM_DB}")

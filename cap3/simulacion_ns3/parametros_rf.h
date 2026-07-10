// parametros_rf.h — AUTOGENERADO desde parametros_rf.py — NO EDITAR
// Parametros RF de los datasheets (fuente unica). Regenerar con:
//   python graficas_simulacion/generar_parametros_h.py
#ifndef PARAMETROS_RF_H
#define PARAMETROS_RF_H

namespace rf {
  // Estandar 802.11ac 5GHz 40MHz 2x2 MIMO
  static const double FREQ_HZ        = 5e+09;
  static const double ANCHO_CANAL_MHZ= 40.0;

  // AP Hawk (galerias)
  static const double HAWK_TXP_DBM   = 30.0;
  static const double HAWK_GT_DBI    = 11.0;

  // AP Cardinal (cruceros / mesh)
  static const double CARD_TXP_DBM   = 23.0;
  static const double CARD_GT_DBI    = 7.5;

  // Antena del LHD (HELI-40)
  static const double LHD_TXP_DBM    = 23.0;
  static const double LHD_GR_DBI     = 4.8;

  // Perdidas de sistema (cables/conectores/margen)
  static const double L_SYSTEM_DB    = 9.4;

  // Sensibilidades objetivo (link budget y disponibilidad RNF-06)
  static const double SENS_VIDEO_DBM = -68.0;
  static const double SENS_BORDE_DBM = -82.0;

  // Modelo de propagacion two-slope (calibrado TamoGraph) — fuente unica
  static const double PROP_N1        = 1.90;
  static const double PROP_N2        = 3.40;
  static const double PROP_DBP_M     = 40.0;
  static const double PROP_NLOS_DB   = 10.0;
} // namespace rf
#endif

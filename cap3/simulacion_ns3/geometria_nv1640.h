// ===========================================================================
// geometria_nv1640.h — AUTOGENERADO desde mapa_nv1640_datos.py — NO EDITAR
// Geometria real de la zona de teleoperacion NV1640 (Nexa Cerro Lindo).
// Regenerar con: python graficas_simulacion/generar_geometria_h.py
// ===========================================================================
#ifndef GEOMETRIA_NV1640_H
#define GEOMETRIA_NV1640_H
#include <vector>

namespace geo {

struct P { double x, y; };

static const double LARGO_CALLE = 134.8500;
static const double SEP_CALLES  = 25.9800;
static const std::vector<double> X_GAL = {0.000, 25.980, 51.960};
static const double Y_BASE = 0.000;
static const double Y_TOP  = 134.850;

// AP Hawk (5) — posiciones reales
static const std::vector<P> HAWKS = {{-0.200,134.900}, {-0.100,88.600}, {25.900,43.400}, {25.900,-0.300}, {52.200,84.600}};

// AP Cardinal (7) — posiciones reales
static const std::vector<P> CARDINALS = {{-0.300,43.800}, {-0.100,8.000}, {26.100,129.100}, {26.300,87.200}, {26.300,21.400}, {52.000,38.500}, {52.400,129.700}};

// Drawpoints (bocas de extraccion)
static const std::vector<P> DRAWPOINTS = {{7.700,8.000}, {33.680,8.000}, {10.490,30.000}, {15.490,30.000}, {36.470,30.000}, {41.470,30.000}, {10.490,52.712}, {15.490,52.712}, {36.470,52.712}, {41.470,52.712}, {10.490,75.425}, {15.490,75.425}, {36.470,75.425}, {41.470,75.425}, {10.490,98.137}, {15.490,98.137}, {36.470,98.137}, {41.470,98.137}, {10.490,120.850}, {15.490,120.850}, {36.470,120.850}, {41.470,120.850}};

// Piques de traspaso (descarga)
static const std::vector<P> PIQUES = {{0.000,164.850}, {25.980,164.850}};

static const double COBERTURA_AP = 60.0;

} // namespace geo
#endif

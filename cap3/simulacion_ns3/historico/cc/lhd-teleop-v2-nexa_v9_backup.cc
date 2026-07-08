/* ==========================================================================
 * SIMULACIÓN NS-3: RED IEEE 802.11ac PARA TELEOPERACIÓN LHD — ARQUITECTURA NEXA
 * Versión 9 — Topología multi-tramo con ángulos reales (70° ramal BP, 65° ramal Desmonte).
 *             ClassifyPosition por proyección paramétrica; RouteDistance oblicua;
 *             waypoints LHD con vectores (cos θ, sin θ); CardFijo y H4 reubicados.
 *
 * RECORRIDO REAL DEL LHD (escenario mobility — Nivel 1640 Nexa Cerro Lindo):
 *   [0,0] ──23m── [23,0] ──25.9m── [48.9,0] ──134.8m──► [183.7,0]
 *                                                              ↗ ramal BP 70°
 *                                                        (202.5, 51.7) ← Breakpoint (fondo BP)
 *                                                              ↙ retrocede
 *   ◄──────────────────────────────134.8m────────────── [183.7,0]
 *  [318.5,0]
 *      ↗ ramal Desmonte 65°
 *  (338.8, 43.5) ← Desmonte (fondo)
 *
 * ARQUITECTURA REAL NEXA NV1640 (v9):
 *   H0 (0,0)   H1 (48.9,0)  H2 (183.7,0)  H3 (318.5,0)  — galería principal
 *   Cardinal fijo (194.1, 28.4)  — ramal BP 70°, 30.25m desde boca
 *   H4 (329.6, 23.9)             — ramal Desmonte 65°, 26.4m desde boca
 *
 * CAMBIOS v7 → v8:
 *   - Distancia de propagación: ruta de galería (suma de segmentos) no solo |Δx|
 *   - H4 reubicado: (318.5, 25.9, 2.0) dentro del ramal Desmonte
 *   - Cardinal fijo reubicado: (183.7, 30.0, 2.0) dentro del ramal BP (v8); v9: (194.1, 28.4) a 70°
 *   - Zonas NLOS: regiones 2D rectangulares (xmin,xmax,ymin,ymax) + región ramal
 *   - Telemetría: 0.1 Mbps continuo (OnTime=1, OffTime=0; corrige v7 0.01 Mbps)
 *   - Goodput: rxP * pktSize (sin descontar headers; Create<Packet>(N) = N bytes payload)
 *   - MIMO 2×2: Antennas=2, MaxSupportedTxSpatialStreams=2 configurados explícitamente
 * CAMBIOS v8 → v8.1:
 *   - NLOS: depende del par TX-RX (LinkNlosLoss), no solo de la posición del LHD
 *   - PosLogger: RSSI estimado con parámetros reales de cada nodo (Hawk vs CardFijo)
 *     y selección del nodo por mayor RSSI estimado (no menor distancia)
 *   - Asociación real: callbacks OnAssoc/OnDeAssoc escriben _assoc_log.csv con
 *     mapeo MAC→id y posición del LHD en cada evento
 *   - Escenarios: mobility_5hawks_real (principal), mobility_4hawks_sin_h4 (sin Desmonte),
 *     mobility_sin_cardfijo_bp (sin Breadcrumb BP), lhd_rapido_mobility,
 *     video_20mbps_mobility, baseline (referencia)
 *   - Distancias: FORWARD_ROUTE_M=482.1m (avance), CLOSED_CYCLE_M=964.2m (ida+vuelta)
 *   - QoS: mismo mapeo TOS/WMM que v7, sin cambios
 *   - Limitación OLSR corregida en documentación: código usa Bridge L2, no OLSR
 * CAMBIOS v8.1 → v8.2:
 *   - TunnelPropagationLossModel: atributo SystemLossDb=9.4 dB aplicado en DoCalcRxPower()
 *     Razón: L_SYSTEM_REAL=9.4 dB (cables, conectores, margen instalación) debía reducir
 *     la potencia recibida para que el LHD experimente handover real entre hawks
 *   - PosLogger RSSI estimado también descuenta 9.4 dB para coherencia con física real
 *   - BeaconInterval: 102.4ms → 51.2ms; MaxMissedBeacons: 3 (sin cambio)
 *     Razón: ventana de handover reducida de 307ms → 154ms; con 40Mbps eso es 770KB
 *     manejable por el buffer. BeaconInterval=20ms causa ping-pong+crash (phy-entity.cc:932);
 *     MaxMissedBeacons=1 también causa ping-pong en zona solapamiento H2/CardFijo
 *   - Sufijo outputs: _v9_
 *
 * Uso: copiar a ns-3.40/scratch/lhd-teleop-v2-nexa.cc
 *      ./ns3 build scratch/lhd-teleop-v2-nexa
 *      ./ns3 run "lhd-teleop-v2-nexa --scenario=mobility_5hawks_real"
 *      ./ns3 run "lhd-teleop-v2-nexa --scenario=baseline"
 * ========================================================================== */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/wifi-module.h"
#include "ns3/csma-module.h"
#include "ns3/bridge-module.h"
#include "ns3/mobility-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/propagation-module.h"
#include "ns3/netanim-module.h"

#include <fstream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <map>
#include <algorithm>
#include <string>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("LhdTeleopV80");

// ============================================================================
// GEOMETRÍA FÍSICA — Mapa 2D Nivel 1640 Nexa Cerro Lindo
//
// Sistema de coordenadas:
//   Galería principal: eje X (horizontal)
//   Ramales:           dirección oblicua según ángulo real
//   Altura:            eje Z (Hawks/Cardinal z=2m, LHD z=1m)
//
// CAMBIOS v8.2 → v9:
//   - Ramal BP a 70° respecto eje X (antes 90°)
//   - Ramal Desmonte a 65° respecto eje X (antes 90°)
//   - CardFijo y H4 reubicados según ángulos reales
//   - ClassifyPosition() usa proyección sobre eje de ramal (no umbral en X)
//   - RouteDistance() calcula distancia paramétrica sqrt(dx²+dy²) en ramales
//   - BuildRealRouteWaypoints() usa vectores (cos θ, sin θ) por ramal
//
// Intersecciones y puntos clave (v9):
//   Boca ramal BP:      (183.7, 0.0)   — galería principal
//   Extremo BP:         (183.7 + 55.0·cos70°, 55.0·sin70°) = (202.5, 51.7)
//   Boca ramal Des:     (318.5, 0.0)   — galería principal
//   Extremo Desmonte:   (318.5 + 48.0·cos65°, 48.0·sin65°) = (338.8, 43.5)
//
// Posiciones físicas de los nodos (tabla v9 — ángulos reales):
//   H0:            (  0.0,   0.0, 2.0)  galería principal — inicio
//   H1:            ( 48.9,   0.0, 2.0)  galería principal
//   H2:            (183.7,   0.0, 2.0)  galería principal — boca ramal BP
//   Cardinal fijo: (194.1,  31.6, 2.0)  ramal BP 70° — 30.25m desde boca
//   H3:            (318.5,   0.0, 2.0)  galería principal — boca ramal Desmonte
//   H4:            (329.6,  27.9, 2.0)  ramal Desmonte 65° — 26.4m desde boca
// ============================================================================

struct NodeLocation {
  std::string id;
  double station_m;   // estación acumulada sobre la ruta (documentación/gráficas)
  double x, y, z;    // coordenadas físicas 2D+altura
  std::string segmentId;
};

// Índices para acceso rápido en el arreglo de Hawks (sin Cardinal fijo)
static const uint32_t N_HAWKS_REAL      = 5;
static const uint32_t N_CARDINALS_FIJOS = 1;

// Distancias del ciclo operativo
static const double COVERED_ROUTE_LENGTH_M = 426.3;
static const double FORWARD_ROUTE_M        = 482.1;
static const double CLOSED_CYCLE_M         = 964.2;

// Altura física de los equipos
static const double HEIGHT_HAWK = 2.0;
static const double HEIGHT_LHD  = 1.0;

// Geometría de ramales v9 — ángulos reales medidos en campo
static const double ANGLE_BP_RAD   = 70.0 * M_PI / 180.0;
static const double ANGLE_DES_RAD  = 65.0 * M_PI / 180.0;
static const double LONG_RAMAL_BP  = 55.0;
static const double LONG_RAMAL_DES = 48.0;

// Bocas de cada ramal (punto de giro en galería principal)
static const double BOCA_BP_X  = 183.7;
static const double BOCA_BP_Y  = 0.0;
static const double BOCA_DES_X = 318.5;
static const double BOCA_DES_Y = 0.0;

// Posición del CardFijo: 30.25m a lo largo del ramal BP (70°)
static const double CARDINAL_FIJO_X = BOCA_BP_X  + 30.25 * std::cos (ANGLE_BP_RAD);   // ≈194.1
static const double CARDINAL_FIJO_Y = BOCA_BP_Y  + 30.25 * std::sin (ANGLE_BP_RAD);   // ≈ 28.4

// Posición de H4: 26.4m a lo largo del ramal Desmonte (65°)
static const double H4_X = BOCA_DES_X + 26.4 * std::cos (ANGLE_DES_RAD);  // ≈329.6
static const double H4_Y = BOCA_DES_Y + 26.4 * std::sin (ANGLE_DES_RAD);  // ≈ 23.9

// Nodos fijos del sistema (tabla v9 — después de constantes para que compilen)
static const NodeLocation NODE_LOCS[] = {
  { "H0",          0.0,   0.0,            0.0,            2.0, "galeria_principal" },
  { "H1",         48.9,  48.9,            0.0,            2.0, "galeria_principal" },
  { "H2",        183.7, 183.7,            0.0,            2.0, "galeria_principal" },
  { "CardFijo",  213.7, CARDINAL_FIJO_X, CARDINAL_FIJO_Y, 2.0, "ramal_bp"          },
  { "H3",        374.4, 318.5,            0.0,            2.0, "galeria_principal"  },
  { "H4",        400.3, H4_X,             H4_Y,           2.0, "ramal_desmonte"     },
};


// ============================================================================
// TOPOLOGÍA DE RUTA — Segmentos físicos y función de distancia
//
// La distancia radioeléctrica entre transmisor y receptor se calcula como la
// distancia recorrida a lo largo de la ruta de galería (no la euclidiana 2D,
// que puede atravesar la roca). Para nodos en el mismo segmento recto se usa
// la distancia axial directa. Para nodos separados por una intersección se
// suman los tramos hasta el punto de giro.
//
// Segmentos del mapa:
//   SEG_GAL:  galería principal  — x ∈ [0, 318.5],  y = 0
//   SEG_BP:   ramal Breakpoint   — x = 183.7,  y ∈ [0, 55.9]
//   SEG_DES:  ramal Desmonte     — x = 318.5,  y ∈ [0, 51.8]
// ============================================================================

enum SegType { SEG_GAL, SEG_BP, SEG_DES };

// Proyecta (x,y) sobre el eje de un ramal oblicuo y devuelve la distancia
// a lo largo del ramal (componente paralela) y la desviación perpendicular.
static void ProjectOnRamal (double x, double y,
                             double boca_x, double boca_y, double angle_rad,
                             double &along, double &perp)
{
  double dx  = x - boca_x;
  double dy  = y - boca_y;
  double ux  = std::cos (angle_rad);
  double uy  = std::sin (angle_rad);
  along = dx * ux + dy * uy;   // distancia a lo largo del ramal
  perp  = std::abs (-dx * uy + dy * ux);  // desviación perpendicular
}

static SegType ClassifyPosition (double x, double y)
{
  // Clasificación por proyección sobre el eje del ramal oblicuo.
  // Un punto está en el ramal si su proyección cae dentro de la longitud
  // del ramal y su desviación perpendicular es < 6m (ancho galería + margen).
  double along, perp;

  ProjectOnRamal (x, y, BOCA_BP_X, BOCA_BP_Y, ANGLE_BP_RAD, along, perp);
  if (along > 2.0 && along <= LONG_RAMAL_BP + 2.0 && perp < 6.0)
    return SEG_BP;

  ProjectOnRamal (x, y, BOCA_DES_X, BOCA_DES_Y, ANGLE_DES_RAD, along, perp);
  if (along > 2.0 && along <= LONG_RAMAL_DES + 2.0 && perp < 6.0)
    return SEG_DES;

  return SEG_GAL;
}

// Distancia a lo largo del ramal BP desde la boca hasta (x,y)
static double AlongBP (double x, double y)
{
  double along, perp;
  ProjectOnRamal (x, y, BOCA_BP_X, BOCA_BP_Y, ANGLE_BP_RAD, along, perp);
  return along;
}

// Distancia a lo largo del ramal Desmonte desde la boca hasta (x,y)
static double AlongDES (double x, double y)
{
  double along, perp;
  ProjectOnRamal (x, y, BOCA_DES_X, BOCA_DES_Y, ANGLE_DES_RAD, along, perp);
  return along;
}

// Distancia de ruta entre dos puntos (x1,y1) y (x2,y2) siguiendo el túnel.
// v9: usa proyección paramétrica sobre el eje de cada ramal oblicuo.
//   - GAL↔GAL:  distancia axial en X (galería recta)
//   - BP↔BP:    distancia a lo largo del eje del ramal BP
//   - DES↔DES:  distancia a lo largo del eje del ramal Desmonte
//   - GAL↔BP:   |x_gal - BOCA_BP_X| + along_bp
//   - GAL↔DES:  |x_gal - BOCA_DES_X| + along_des
//   - BP↔DES:   along_bp + (BOCA_DES_X - BOCA_BP_X) + along_des
static double RouteDistance (double x1, double y1, double x2, double y2)
{
  SegType s1 = ClassifyPosition (x1, y1);
  SegType s2 = ClassifyPosition (x2, y2);

  if (s1 == SEG_GAL && s2 == SEG_GAL)
    return std::abs (x1 - x2);

  if (s1 == SEG_BP && s2 == SEG_BP)
    return std::abs (AlongBP (x1, y1) - AlongBP (x2, y2));

  if (s1 == SEG_DES && s2 == SEG_DES)
    return std::abs (AlongDES (x1, y1) - AlongDES (x2, y2));

  if ((s1 == SEG_GAL && s2 == SEG_BP) || (s1 == SEG_BP && s2 == SEG_GAL))
  {
    double gal_x    = (s1 == SEG_GAL) ? x1 : x2;
    double bp_x     = (s1 == SEG_BP)  ? x1 : x2;
    double bp_y     = (s1 == SEG_BP)  ? y1 : y2;
    double d_gal    = std::abs (gal_x - BOCA_BP_X);
    double d_ramal  = AlongBP (bp_x, bp_y);
    return d_gal + d_ramal;
  }

  if ((s1 == SEG_GAL && s2 == SEG_DES) || (s1 == SEG_DES && s2 == SEG_GAL))
  {
    double gal_x    = (s1 == SEG_GAL) ? x1 : x2;
    double des_x    = (s1 == SEG_DES) ? x1 : x2;
    double des_y    = (s1 == SEG_DES) ? y1 : y2;
    double d_gal    = std::abs (gal_x - BOCA_DES_X);
    double d_ramal  = AlongDES (des_x, des_y);
    return d_gal + d_ramal;
  }

  // BP ↔ DES: recorre ramal BP → galería → ramal DES
  double bp_x  = (s1 == SEG_BP) ? x1 : x2;
  double bp_y  = (s1 == SEG_BP) ? y1 : y2;
  double des_x = (s1 == SEG_DES) ? x1 : x2;
  double des_y = (s1 == SEG_DES) ? y1 : y2;
  return AlongBP (bp_x, bp_y) + (BOCA_DES_X - BOCA_BP_X) + AlongDES (des_x, des_y);
}


// ============================================================================
// ZONAS NLOS — Regiones 2D rectangulares
//
// Una zona NLOS es activa cuando el LHD está dentro del rectángulo (xmin,xmax)
// × (ymin,ymax). Las zonas cubren los giros e intersecciones donde el enlace
// radio cruza una pared de galería o esquina.
//
// Zonas adicionales para ramales:
//   NLOS_BP:  LHD dentro del ramal BP (y > 3m, x≈183.7) → el enlace cruza el giro
//   NLOS_DES: LHD dentro del ramal Desmonte (y > 3m, x≈318.5)
// ============================================================================

struct NlosRegion {
  std::string id;
  double xmin, xmax;
  double ymin, ymax;
  double extraLossDb;
};

static const NlosRegion NLOS_REGIONS[] = {
  // Zonas de giro en galería principal
  { "Giro-D-GaleriaPrincipal",  38.9,  58.9,  -2.0,  2.0, 10.0 },
  { "Giro-D-RamalBP",          173.7, 193.7,  -2.0,  2.0, 10.0 },
  // Transición y maniobra en BP: activada cuando y ∈ (0, 55.9]
  { "Transicion-BP",           178.7, 188.7,   0.0, 55.9, 10.0 },
  { "Maniobra-Breakpoint",     179.7, 187.7,  40.0, 55.9, 10.0 },
  // Vuelta desde BP hacia galería
  { "Retoma-GaleriaPrincipal", 178.7, 188.7,   0.0,  5.0, 10.0 },
  // Ramal Desmonte: activada cuando y > 0 en x≈318.5
  { "Giro-D-RamalDesmonte",   308.5, 328.5,  -2.0,  2.0, 10.0 },
  { "Transicion-Desmonte",    313.5, 323.5,   0.0, 51.8, 10.0 },
};
static const uint32_t N_NLOS_REGIONS = 7;


// ============================================================================
// MODELO DE PROPAGACIÓN EN TÚNEL TWO-SLOPE v8
// Usa distancia de ruta de galería (no euclidiana 3D ni solo |Δx|).
// NLOS detectado por región 2D rectangular (posición real del LHD).
// ============================================================================

// NLOS basado en el trayecto del enlace TX↔RX (v8.1).
// Reemplaza NlosExtraLoss que solo consideraba la posición del LHD.
// Reglas:
//   Mismo segmento          → 0 dB (enlace intrarramal puede ser LOS)
//   Galería ↔ Ramal BP      → +10 dB (cruza esquina en (183.7,0))
//   Galería ↔ Ramal Desmonte→ +10 dB (cruza esquina en (318.5,0))
//   Ramal BP ↔ Ramal Desmonte→ +20 dB (cruza dos esquinas vía galería)
static double LinkNlosLoss (Vector txPos, Vector rxPos)
{
  SegType s1 = ClassifyPosition (txPos.x, txPos.y);
  SegType s2 = ClassifyPosition (rxPos.x, rxPos.y);
  if (s1 == s2)                                                          return  0.0;
  if ((s1==SEG_GAL&&s2==SEG_BP)  || (s1==SEG_BP &&s2==SEG_GAL))        return 10.0;
  if ((s1==SEG_GAL&&s2==SEG_DES) || (s1==SEG_DES&&s2==SEG_GAL))        return 10.0;
  return 20.0;  // SEG_BP <-> SEG_DES: dos giros
}

class TunnelPropagationLossModel : public PropagationLossModel
{
public:
  static TypeId GetTypeId (void)
  {
    static TypeId tid = TypeId ("ns3::TunnelPropagationLossModel")
      .SetParent<PropagationLossModel> ()
      .SetGroupName ("Propagation")
      .AddConstructor<TunnelPropagationLossModel> ()
      .AddAttribute ("ExponentLOS",    "Exponente LOS",            DoubleValue (1.9),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_expLOS),
                     MakeDoubleChecker<double> ())
      .AddAttribute ("ExponentNLOS",   "Exponente NLOS",           DoubleValue (3.4),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_expNLOS),
                     MakeDoubleChecker<double> ())
      .AddAttribute ("SigmaLOS",       "Shadowing LOS (dB)",       DoubleValue (5.0),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_sigLOS),
                     MakeDoubleChecker<double> ())
      .AddAttribute ("SigmaNLOS",      "Shadowing NLOS (dB)",      DoubleValue (7.0),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_sigNLOS),
                     MakeDoubleChecker<double> ())
      .AddAttribute ("Frequency",      "Frecuencia (Hz)",          DoubleValue (5.0e9),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_freq),
                     MakeDoubleChecker<double> ())
      .AddAttribute ("BreakpointDist", "Distancia breakpoint (m)", DoubleValue (40.0),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_dbp),
                     MakeDoubleChecker<double> ())
      .AddAttribute ("SystemLossDb",  "Perdidas de sistema — cables, conectores, RF (dB)", DoubleValue (9.4),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_systemLossDb),
                     MakeDoubleChecker<double> ());
    return tid;
  }

  TunnelPropagationLossModel ()
  {
    m_rand = CreateObject<NormalRandomVariable> ();
    m_rand->SetAttribute ("Mean", DoubleValue (0.0));
    for (uint32_t i = 0; i < N_NLOS_REGIONS; i++)
      m_nlosRegions.push_back (NLOS_REGIONS[i]);
  }

  void SetLhdMobility  (Ptr<MobilityModel> lhdMob)  { m_lhdMob = lhdMob; }
  void SetNlosEnabled  (bool enabled)                { m_nlosEnabled = enabled; }

private:
  // Verifica si el LHD está dentro de alguna región NLOS y retorna pérdida extra.
  double NlosExtraLoss (double lhd_x, double lhd_y) const
  {
    for (const auto &r : m_nlosRegions)
      if (lhd_x >= r.xmin && lhd_x <= r.xmax &&
          lhd_y >= r.ymin && lhd_y <= r.ymax)
        return r.extraLossDb;
    return 0.0;
  }

  double DoCalcRxPower (double txPow,
                        Ptr<MobilityModel> a,
                        Ptr<MobilityModel> b) const override
  {
    Vector pa = a->GetPosition ();
    Vector pb = b->GetPosition ();

    // Distancia de propagación: ruta física de galería (v8).
    // Usa RouteDistance que suma segmentos según la topología real del túnel.
    double d = RouteDistance (pa.x, pa.y, pb.x, pb.y);
    if (d < 1.0) d = 1.0;

    // NLOS v8.1: penalización basada en el trayecto TX↔RX, no en la posición del LHD.
    // Mismo segmento → 0dB; segmentos distintos → +10dB o +20dB.
    double nlosLoss = 0.0;
    if (m_nlosEnabled)
      nlosLoss = LinkNlosLoss (pa, pb);

    double lam  = 3.0e8 / m_freq;
    double plD0 = 20.0 * std::log10 (4.0 * M_PI / lam);
    double pl;

    if (d < m_dbp)
      pl = plD0 + 10.0 * m_expLOS * std::log10 (d);
    else
      pl = plD0 + 10.0 * m_expLOS  * std::log10 (m_dbp)
               + 10.0 * m_expNLOS * std::log10 (d / m_dbp);

    pl += nlosLoss;

    // Shadowing: desactivado — no existe modelo espacialmente correlado para
    // canal de túnel en ns-3.40. Limitación declarada en sección 3.4.8.
    (void)m_sigLOS; (void)m_sigNLOS; (void)m_rand;
    return txPow - pl - m_systemLossDb;
  }

  int64_t DoAssignStreams (int64_t s) override
  {
    m_rand->SetStream (s);
    return 1;
  }

  double m_expLOS, m_expNLOS, m_sigLOS, m_sigNLOS;
  double m_freq, m_dbp, m_systemLossDb {9.4};
  bool   m_nlosEnabled {false};
  Ptr<NormalRandomVariable> m_rand;
  Ptr<MobilityModel>        m_lhdMob;
  std::vector<NlosRegion>   m_nlosRegions;
};

NS_OBJECT_ENSURE_REGISTERED (TunnelPropagationLossModel);


// ============================================================================
// APLICACIÓN VIDEO CON RETARDO DE CODEC (H.264 encode+decode = 35ms)
// ============================================================================

class CodecDelayApp : public Application
{
public:
  static TypeId GetTypeId (void)
  {
    static TypeId tid = TypeId ("ns3::CodecDelayApp")
      .SetParent<Application> ()
      .SetGroupName ("Applications")
      .AddConstructor<CodecDelayApp> ();
    return tid;
  }

  void Setup (Ptr<Socket> socket, Address addr,
              uint32_t pktSize, DataRate rate, double codecMs, uint8_t tos)
  {
    m_socket     = socket;
    m_peer       = addr;
    m_packetSize = pktSize;
    m_dataRate   = rate;
    m_codecDelay = MilliSeconds (codecMs);
    m_tos        = tos;
    m_running    = false;
  }

private:
  void StartApplication (void) override
  {
    m_running = true;
    m_socket->Bind ();
    m_socket->Connect (m_peer);
    m_socket->SetIpTos (m_tos);
    m_sendEvent = Simulator::Schedule (m_codecDelay,
                                       &CodecDelayApp::SendPacket, this);
  }

  void StopApplication (void) override
  {
    m_running = false;
    if (m_sendEvent.IsRunning ()) Simulator::Cancel (m_sendEvent);
    m_socket->Close ();
  }

  void ScheduleNextPacket (void)
  {
    if (!m_running) return;
    Time next = Seconds (m_packetSize * 8.0 / m_dataRate.GetBitRate ());
    m_sendEvent = Simulator::Schedule (next, &CodecDelayApp::SendPacket, this);
  }

  void SendPacket (void)
  {
    m_socket->Send (Create<Packet> (m_packetSize));
    ScheduleNextPacket ();
  }

  Ptr<Socket>  m_socket;
  Address      m_peer;
  uint32_t     m_packetSize;
  DataRate     m_dataRate;
  Time         m_codecDelay;
  uint8_t      m_tos;
  bool         m_running;
  EventId      m_sendEvent;
};

NS_OBJECT_ENSURE_REGISTERED (CodecDelayApp);


// ============================================================================
// UTILIDADES
// ============================================================================

double Percentile (std::vector<double> v, double p)
{
  if (v.empty ()) return 0.0;
  std::sort (v.begin (), v.end ());
  double idx = (p / 100.0) * (double)(v.size () - 1);
  size_t lo  = (size_t)idx;
  size_t hi  = lo + 1;
  if (hi >= v.size ()) return v.back ();
  return v[lo] * (1.0 - (idx - lo)) + v[hi] * (idx - lo);
}

std::vector<double> HistToSamples (const Histogram &h, double binW)
{
  std::vector<double> s;
  for (uint32_t b = 0; b < h.GetNBins (); b++)
  {
    uint32_t cnt = h.GetBinCount (b);
    double   mid = (b + 0.5) * binW;
    for (uint32_t k = 0; k < cnt; k++) s.push_back (mid);
  }
  return s;
}


// ── Variables globales para log de asociación (callbacks declarados después de PosLogger) ──
static std::ofstream          g_assocLog;
static std::map<std::string, std::string> g_macToId;   // MAC string → id
static Ptr<WaypointMobilityModel>         g_lhdMobGlobal;


// ============================================================================
// LOGGER DE POSICIÓN Y RSSI
// Formato v8: time_s,x,y,station_m,segment_id,nlos_region,serving_hawk,rssi_dbm
// ============================================================================

struct ApRadioInfo {
  double x, y;
  std::string id;
  double txPowerDbm;  // potencia de transmisión real del nodo
  double txGainDbi;   // ganancia de antena TX real del nodo
};
static std::vector<ApRadioInfo> g_apPositions;

struct PosLogger {
  std::ofstream     file;
  Ptr<WaypointMobilityModel> lhdMob;
  double txPowHawk, freq, dbp, expLOS, expNLOS;

  void Open (const std::string &path)
  {
    file.open (path);
    file << "time_s,x,y,station_m,segment_id,nlos_region,serving_hawk,rssi_dbm\n";
  }

  static double StationFromXY (double x, double y)
  {
    SegType seg = ClassifyPosition (x, y);
    if (seg == SEG_GAL)  return x;
    if (seg == SEG_BP)   return BOCA_BP_X  + AlongBP  (x, y);  // v9: distancia paramétrica real
    if (seg == SEG_DES)  return 374.4      + AlongDES (x, y);  // 374.4 = estación acumulada hasta boca DES
    return x;
  }

  static std::string SegmentId (double x, double y)
  {
    SegType seg = ClassifyPosition (x, y);
    if (seg == SEG_BP)  return "ramal_bp";
    if (seg == SEG_DES) return "ramal_desmonte";
    if (x < 23.0)  return "arranque";
    if (x < 48.9)  return "acceso_galeria";
    if (x < 183.7) return "LOS1_galeria";
    if (x < 318.5) return "LOS2_galeria";
    return "galeria_final";
  }

  static std::string ActiveNlosRegion (double lhd_x, double lhd_y)
  {
    for (uint32_t i = 0; i < N_NLOS_REGIONS; i++)
      if (lhd_x >= NLOS_REGIONS[i].xmin && lhd_x <= NLOS_REGIONS[i].xmax &&
          lhd_y >= NLOS_REGIONS[i].ymin && lhd_y <= NLOS_REGIONS[i].ymax)
        return NLOS_REGIONS[i].id;
    return "LOS";
  }

  void Log ()
  {
    double t   = Simulator::Now ().GetSeconds ();
    Vector pos = lhdMob->GetPosition ();
    double x   = pos.x;
    double y   = pos.y;

    // AP con mayor RSSI estimado — usa parámetros reales de cada nodo (v8.1)
    std::string bestId   = "?";
    double      bestRssi = -999.0;
    for (const auto &ap : g_apPositions)
    {
      double d = RouteDistance (x, y, ap.x, ap.y);
      if (d < 1.0) d = 1.0;

      double lam  = 3.0e8 / freq;
      double plD0 = 20.0 * std::log10 (4.0 * M_PI / lam);
      double pl;
      if (d < dbp)
        pl = plD0 + 10.0 * expLOS  * std::log10 (d);
      else
        pl = plD0 + 10.0 * expLOS  * std::log10 (dbp)
                 + 10.0 * expNLOS * std::log10 (d / dbp);

      // NLOS según enlace AP↔LHD (v8.1)
      pl += LinkNlosLoss (Vector (ap.x, ap.y, HEIGHT_HAWK),
                          Vector (x,    y,    HEIGHT_LHD));

      // RSSI en el receptor LHD (rxGain = 4.8 dBi, Cardinal AG1-5250M)
      // Usa m_systemLossDb del modelo para coherencia con DoCalcRxPower (fix v9).
      double rxGain      = 4.8;
      double systemLossDb = 9.4;  // L_SYSTEM_REAL — sincronizado con TunnelPropagationLossModel
      double rssi         = ap.txPowerDbm + ap.txGainDbi + rxGain - pl - systemLossDb;

      if (rssi > bestRssi)
      {
        bestRssi = rssi;
        bestId   = ap.id;
      }
    }

    double station = StationFromXY (x, y);
    std::string segId   = SegmentId (x, y);
    std::string nlosReg = ActiveNlosRegion (x, y);

    file << std::fixed << std::setprecision (2)
         << t << "," << x << "," << y << ","
         << station << "," << segId << ","
         << nlosReg << "," << bestId << "," << bestRssi << "\n";

    Simulator::Schedule (Seconds (1.0), &PosLogger::Log, this);
  }
};

static PosLogger g_posLogger;


// ============================================================================
// CALLBACKS WIFI — declarados después de PosLogger (usan StationFromXY)
// ============================================================================

static std::string MacToString (Mac48Address addr)
{
  std::ostringstream oss;
  oss << addr;
  return oss.str ();
}

void OnAssoc (Mac48Address addr)
{
  std::string key  = MacToString (addr);
  std::string apId = g_macToId.count (key) ? g_macToId[key] : key;
  double t = Simulator::Now ().GetSeconds ();
  std::cout << "[WiFi] LHD asociado a AP: " << apId << "  t=" << t << "s" << std::endl;
  if (g_assocLog.is_open () && g_lhdMobGlobal != nullptr)
  {
    Vector p       = g_lhdMobGlobal->GetPosition ();
    double station = PosLogger::StationFromXY (p.x, p.y);
    g_assocLog << std::fixed << std::setprecision (2)
               << t << ",assoc," << apId
               << "," << p.x << "," << p.y << "," << station << "\n";
  }
}

void OnDeAssoc (Mac48Address addr)
{
  std::string key  = MacToString (addr);
  std::string apId = g_macToId.count (key) ? g_macToId[key] : key;
  double t = Simulator::Now ().GetSeconds ();
  std::cout << "[WiFi] LHD desasociado de AP: " << apId << "  t=" << t << "s" << std::endl;
  if (g_assocLog.is_open () && g_lhdMobGlobal != nullptr)
  {
    Vector p       = g_lhdMobGlobal->GetPosition ();
    double station = PosLogger::StationFromXY (p.x, p.y);
    g_assocLog << std::fixed << std::setprecision (2)
               << t << ",deassoc," << apId
               << "," << p.x << "," << p.y << "," << station << "\n";
  }
}


// ============================================================================
// CONSTRUIR WAYPOINTS DEL RECORRIDO REAL v8
//
// Coordenadas 2D reales del mapa. Z = HEIGHT_LHD = 1.0m constante.
// El modelo de propagación usa RouteDistance sobre (x,y) reales.
// ============================================================================

void BuildRealRouteWaypoints (Ptr<WaypointMobilityModel> mob,
                              double speed, double simTime)
{
  struct Seg {
    double dist;
    double dx, dy;
    double pause;
    std::string name;
  };

  // v9: vectores de dirección reales para ramales oblicuos
  // Ramal BP  a 70°: dx=cos(70°)=0.3420, dy=sin(70°)=0.9397
  // Ramal DES a 65°: dx=cos(65°)=0.4226, dy=sin(65°)=0.9063
  const double BP_DX  =  std::cos (ANGLE_BP_RAD);
  const double BP_DY  =  std::sin (ANGLE_BP_RAD);
  const double DES_DX =  std::cos (ANGLE_DES_RAD);
  const double DES_DY =  std::sin (ANGLE_DES_RAD);

  const std::vector<Seg> segs = {
    { 23.0,    1,      0,      0.0,   "arranque"         },
    { 25.9,    1,      0,      0.0,   "acceso_galeria"    },
    { 134.8,   1,      0,      0.0,   "LOS1"              },
    { 25.9,    BP_DX,  BP_DY,  0.0,   "ramal_bp_entrada"  },
    { 30.0,    BP_DX,  BP_DY,  15.0,  "acceso_bp"         },
    { 30.0,   -BP_DX, -BP_DY,  0.0,   "retroceso_bp"      },
    { 25.9,   -BP_DX, -BP_DY,  0.0,   "ramal_bp_salida"   },
    { 134.8,   1,      0,      0.0,   "LOS2"              },
    { 25.9,    DES_DX, DES_DY, 0.0,   "ramal_des_entrada" },
    { 25.9,    DES_DX, DES_DY, 30.0,  "desmonte"          },
  };

  double t = 0.0, x = 0.0, y = 0.0;
  mob->AddWaypoint (Waypoint (Seconds (t), Vector (x, y, HEIGHT_LHD)));

  auto step = [&](const Seg &s, bool fwd)
  {
    x += (fwd ? s.dx : -s.dx) * s.dist;
    y += (fwd ? s.dy : -s.dy) * s.dist;
    t += s.dist / speed;
    mob->AddWaypoint (Waypoint (Seconds (t), Vector (x, y, HEIGHT_LHD)));
    if (fwd && s.pause > 0.0)
    { t += s.pause; mob->AddWaypoint (Waypoint (Seconds (t), Vector (x, y, HEIGHT_LHD))); }
  };

  for (const auto &s : segs) step (s, true);
  for (int i = (int)segs.size()-1; i >= 0; i--) step (segs[i], false);

  while (t < simTime + 50.0)
  {
    x = 0.0; y = 0.0;
    for (const auto &s : segs) step (s, true);
    for (int i = (int)segs.size()-1; i >= 0; i--) step (segs[i], false);
  }
}


// ============================================================================
// MAIN
// ============================================================================

int main (int argc, char *argv[])
{
  std::string scenario    = "mobility_5hawks_real";
  double      simTime     = 300.0;
  double      lhdSpeed    = 2.22;    // m/s
  double      videoRate   = 40.0;    // Mbps
  double      cmdRate     = 0.5;     // Mbps
  double      telRate     = 0.1;     // Mbps continuo
  double      txPowHawk   = 30.0;    // dBm Hawk FE1-5050
  double      txPowCard   = 23.0;    // dBm Cardinal AG1-5250M
  double      codecDelayMs = 35.0;   // ms H.264
  uint32_t    seed        = 1;

  CommandLine cmd;
  cmd.AddValue ("scenario",   "escenario a ejecutar",       scenario);
  cmd.AddValue ("simTime",    "Tiempo de simulacion (s)",   simTime);
  cmd.AddValue ("lhdSpeed",   "Velocidad LHD (m/s)",        lhdSpeed);
  cmd.AddValue ("videoRate",  "Tasa video (Mbps)",          videoRate);
  cmd.AddValue ("seed",       "Semilla RNG",                seed);
  cmd.Parse (argc, argv);

  RngSeedManager::SetSeed (seed);
  RngSeedManager::SetRun  (seed);

  // ── Configuración por escenario ────────────────────────────────────────────
  //
  // Escenarios v8:
  //   mobility_5hawks_real  — PRINCIPAL: recorrido real, 5 Hawks reales, NLOS on
  //   mobility_4hawks_100m  — Comparativo: 4 Hawks a 100m, mobility, NLOS on
  //   mobility_5hawks_100m  — Comparativo: 5 Hawks a 100m, mobility, NLOS on
  //   lhd_rapido_mobility   — Sensibilidad velocidad: 3.33 m/s, mobility, NLOS on
  //   video_20mbps_mobility — Sensibilidad bitrate: 20 Mbps, mobility, NLOS on
  //   baseline              — Referencia controlada: recorrido lineal, NLOS off
  //
  bool isMobility       = (scenario != "baseline");
  bool isSin4H          = (scenario == "mobility_4hawks_sin_h4");
  bool isSinCardFijo    = (scenario == "mobility_sin_cardfijo_bp");
  uint32_t nCardFijosScenario = (isSin4H || isSinCardFijo) ? 0 : N_CARDINALS_FIJOS;

  if (scenario == "lhd_rapido_mobility")   lhdSpeed  = 3.33;
  if (scenario == "video_20mbps_mobility") videoRate = 20.0;

  // Posiciones de Hawks según escenario (x, y)
  // v8.1: todos los escenarios usan posiciones físicamente válidas
  struct HawkPos2D { double x, y; };
  std::vector<HawkPos2D> hawkPos2D;
  uint32_t nHawksScenario;

  if (isSin4H)
  {
    // 4 Hawks reales (H0..H3), sin H4 en Desmonte, sin Cardinal fijo
    hawkPos2D      = {{0.0,0.0},{48.9,0.0},{183.7,0.0},{318.5,0.0}};
    nHawksScenario = 4;
  }
  else
  {
    // v9: H4 reubicado según ángulo real ramal Desmonte 65°
    hawkPos2D      = {{0.0,0.0},{48.9,0.0},{183.7,0.0},{318.5,0.0},{H4_X,H4_Y}};
    nHawksScenario = N_HAWKS_REAL;
  }

  std::cout << "===== Simulacion v9 — Nexa Cerro Lindo Nivel 1640 — "
            << scenario << " =====" << std::endl;
  std::cout << "Recorrido: " << COVERED_ROUTE_LENGTH_M << "m | Avance: "
            << FORWARD_ROUTE_M << "m | Ciclo cerrado: " << CLOSED_CYCLE_M << "m | "
            << nHawksScenario << " Hawks + " << nCardFijosScenario << " Cardinal fijo" << std::endl;
  std::cout << "Video=" << videoRate << "Mbps | LHD=" << lhdSpeed
            << "m/s | Codec=" << codecDelayMs << "ms | seed=" << seed << std::endl;
  std::cout << "NLOS " << (isMobility ? "ACTIVO (por enlace TX-RX)" : "DESACTIVADO")
            << " | Distancia: RouteDistance 2D | RSSI: por nodo real" << std::endl;
  std::cout << "IEEE 802.11ac 5GHz 40MHz 2×2 MIMO | TxHawk=" << txPowHawk
            << "dBm Cardinal=" << txPowCard << "dBm" << std::endl;
  std::cout << "QoS: Video TOS=0xB8 (EF→AC_VI) | Cmd TOS=0xC0 (CS6→AC_VO)"
            << " | Tel TOS=0x00 (BE→AC_BE)" << std::endl;
  std::cout << "============================================================"
            << std::endl;

  // ── Nodos ─────────────────────────────────────────────────────────────────
  uint32_t nHawks = nHawksScenario;
  NodeContainer hawks;         hawks.Create (nHawks);
  NodeContainer cardinalFijos; cardinalFijos.Create (nCardFijosScenario);
  NodeContainer lhd;           lhd.Create (1);
  NodeContainer control;       control.Create (1);

  // ── Backbone CSMA 1Gbps ───────────────────────────────────────────────────
  CsmaHelper csma;
  csma.SetChannelAttribute ("DataRate", StringValue ("1Gbps"));
  csma.SetChannelAttribute ("Delay",    TimeValue (MicroSeconds (10)));

  NodeContainer backboneNodes;
  backboneNodes.Add (control);
  backboneNodes.Add (hawks);
  if (nCardFijosScenario > 0) backboneNodes.Add (cardinalFijos);
  NetDeviceContainer backboneDev = csma.Install (backboneNodes);

  // ── Canal WiFi con modelo de túnel v8 ─────────────────────────────────────
  Ptr<TunnelPropagationLossModel> tunnelLoss =
      CreateObject<TunnelPropagationLossModel> ();
  tunnelLoss->SetAttribute ("ExponentLOS",    DoubleValue (1.9));
  tunnelLoss->SetAttribute ("ExponentNLOS",   DoubleValue (3.4));
  tunnelLoss->SetAttribute ("SigmaLOS",       DoubleValue (5.0));
  tunnelLoss->SetAttribute ("SigmaNLOS",      DoubleValue (7.0));
  tunnelLoss->SetAttribute ("Frequency",      DoubleValue (5.0e9));
  tunnelLoss->SetAttribute ("BreakpointDist", DoubleValue (40.0));

  Ptr<YansWifiChannel> wifiChan = CreateObject<YansWifiChannel> ();
  wifiChan->SetPropagationDelayModel (
      CreateObject<ConstantSpeedPropagationDelayModel> ());
  wifiChan->SetPropagationLossModel (tunnelLoss);

  WifiHelper wifi;
  wifi.SetStandard (WIFI_STANDARD_80211ac);
  wifi.SetRemoteStationManager ("ns3::MinstrelHtWifiManager");
  Ssid commonSsid = Ssid ("nexa-lhd");

  // Hawks — APs IEEE 802.11ac 40MHz 2×2 MIMO
  // TxGain=11dBi (antena HELI FE1-5050), Antennas=2
  YansWifiPhyHelper phyAP;
  phyAP.SetChannel (wifiChan);
  phyAP.Set ("ChannelSettings",              StringValue ("{0, 40, BAND_5GHZ, 0}"));
  phyAP.Set ("TxPowerStart",                 DoubleValue (txPowHawk));
  phyAP.Set ("TxPowerEnd",                   DoubleValue (txPowHawk));
  phyAP.Set ("TxGain",                       DoubleValue (11.0));
  phyAP.Set ("RxGain",                       DoubleValue (11.0));
  phyAP.Set ("Antennas",                     UintegerValue (2));
  phyAP.Set ("MaxSupportedTxSpatialStreams", UintegerValue (2));
  phyAP.Set ("MaxSupportedRxSpatialStreams", UintegerValue (2));

  WifiMacHelper macAP;
  std::vector<NetDeviceContainer> hawkWifiDev (nHawks);
  for (uint32_t i = 0; i < nHawks; i++)
  {
    macAP.SetType ("ns3::ApWifiMac",
                   "Ssid",           SsidValue (commonSsid),
                   "BeaconInterval", TimeValue (MicroSeconds (51200)),
                   "QosSupported",   BooleanValue (true));
    NodeContainer apNode; apNode.Add (hawks.Get (i));
    hawkWifiDev[i] = wifi.Install (phyAP, macAP, apNode);
  }

  // Cardinals fijos (Breadcrumbs) — APs con parámetros Cardinal (Pt=23dBm, Gt=4.8dBi)
  YansWifiPhyHelper phyCardFijo;
  phyCardFijo.SetChannel (wifiChan);
  phyCardFijo.Set ("ChannelSettings",              StringValue ("{0, 40, BAND_5GHZ, 0}"));
  phyCardFijo.Set ("TxPowerStart",                 DoubleValue (txPowCard));
  phyCardFijo.Set ("TxPowerEnd",                   DoubleValue (txPowCard));
  phyCardFijo.Set ("TxGain",                       DoubleValue (4.8));
  phyCardFijo.Set ("RxGain",                       DoubleValue (4.8));
  phyCardFijo.Set ("Antennas",                     UintegerValue (2));
  phyCardFijo.Set ("MaxSupportedTxSpatialStreams", UintegerValue (2));
  phyCardFijo.Set ("MaxSupportedRxSpatialStreams", UintegerValue (2));

  std::vector<NetDeviceContainer> cardFijoWifiDev (nCardFijosScenario);
  for (uint32_t i = 0; i < nCardFijosScenario; i++)
  {
    macAP.SetType ("ns3::ApWifiMac",
                   "Ssid",           SsidValue (commonSsid),
                   "BeaconInterval", TimeValue (MicroSeconds (51200)),
                   "QosSupported",   BooleanValue (true));
    NodeContainer cfNode; cfNode.Add (cardinalFijos.Get (i));
    cardFijoWifiDev[i] = wifi.Install (phyCardFijo, macAP, cfNode);
  }

  // LHD — STA Cardinal AG1-5250M (Pt=23dBm, Gt=4.8dBi, 2×2 MIMO)
  YansWifiPhyHelper phySTA;
  phySTA.SetChannel (wifiChan);
  phySTA.Set ("ChannelSettings",              StringValue ("{0, 40, BAND_5GHZ, 0}"));
  phySTA.Set ("TxPowerStart",                 DoubleValue (txPowCard));
  phySTA.Set ("TxPowerEnd",                   DoubleValue (txPowCard));
  phySTA.Set ("TxGain",                       DoubleValue (4.8));
  phySTA.Set ("RxGain",                       DoubleValue (4.8));
  phySTA.Set ("Antennas",                     UintegerValue (2));
  phySTA.Set ("MaxSupportedTxSpatialStreams", UintegerValue (2));
  phySTA.Set ("MaxSupportedRxSpatialStreams", UintegerValue (2));

  WifiMacHelper macSTA;
  macSTA.SetType ("ns3::StaWifiMac",
                  "Ssid",          SsidValue (commonSsid),
                  "ActiveProbing", BooleanValue (true),
                  "QosSupported",  BooleanValue (true));
  NetDeviceContainer lhdWifiDev = wifi.Install (phySTA, macSTA, lhd);

  // BeaconInterval=51.2ms, MaxMissedBeacons=3 → ventana de handover ~154ms
  // Con video 40Mbps: 154ms × 40Mbps = 770KB — manejable por buffer.
  // Nota: BeaconInterval=20ms causa ping-pong + NS_ASSERT crash (phy-entity.cc:932).
  // MaxMissedBeacons=1 con beacon 102ms también causa ping-pong en zona H2/CardFijo.
  Config::Set ("/NodeList/" + std::to_string (lhd.Get(0)->GetId ()) +
               "/DeviceList/*/Mac/$ns3::StaWifiMac/MaxMissedBeacons",
               UintegerValue (3));
  Config::Set ("/NodeList/" + std::to_string (lhd.Get(0)->GetId ()) +
               "/DeviceList/*/Mac/$ns3::StaWifiMac/AssocRequestTimeout",
               TimeValue (MilliSeconds (50)));

  // Bridge L2 en cada Hawk
  BridgeHelper bridgeHelper;
  for (uint32_t i = 0; i < nHawks; i++)
  {
    NetDeviceContainer bridgePorts;
    bridgePorts.Add (backboneDev.Get (i + 1));
    bridgePorts.Add (hawkWifiDev[i].Get (0));
    bridgeHelper.Install (hawks.Get (i), bridgePorts);
  }

  // Bridge L2 en cada Cardinal fijo (condicional)
  for (uint32_t i = 0; i < nCardFijosScenario; i++)
  {
    NetDeviceContainer bridgePorts;
    bridgePorts.Add (backboneDev.Get (nHawks + 1 + i));
    bridgePorts.Add (cardFijoWifiDev[i].Get (0));
    bridgeHelper.Install (cardinalFijos.Get (i), bridgePorts);
  }

  // ── Mapeo MAC → id para callbacks de asociación (v8.1) ────────────────────
  g_macToId.clear ();
  for (uint32_t i = 0; i < nHawks; i++)
  {
    Ptr<WifiNetDevice> dev = DynamicCast<WifiNetDevice> (hawkWifiDev[i].Get (0));
    if (dev) g_macToId[MacToString (dev->GetMac ()->GetAddress ())] = "H" + std::to_string (i);
  }
  for (uint32_t i = 0; i < nCardFijosScenario; i++)
  {
    Ptr<WifiNetDevice> dev = DynamicCast<WifiNetDevice> (cardFijoWifiDev[i].Get (0));
    if (dev) g_macToId[MacToString (dev->GetMac ()->GetAddress ())] = "CardFijo";
  }

  // ── Movilidad ─────────────────────────────────────────────────────────────
  MobilityHelper mobility;

  // Hawks — posicionados con coordenadas 2D reales v8 + z=2m
  Ptr<ListPositionAllocator> hawkPosAlloc = CreateObject<ListPositionAllocator> ();
  for (uint32_t i = 0; i < nHawks; i++)
    hawkPosAlloc->Add (Vector (hawkPos2D[i].x, hawkPos2D[i].y, HEIGHT_HAWK));
  mobility.SetPositionAllocator (hawkPosAlloc);
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (hawks);

  // Cardinal fijo — ramal BP a ángulo real 70° — condicional
  if (nCardFijosScenario > 0)
  {
    Ptr<ListPositionAllocator> cardFijoAlloc = CreateObject<ListPositionAllocator> ();
    cardFijoAlloc->Add (Vector (CARDINAL_FIJO_X, CARDINAL_FIJO_Y, HEIGHT_HAWK));
    mobility.SetPositionAllocator (cardFijoAlloc);
    mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
    mobility.Install (cardinalFijos);
  }

  // Control
  Ptr<ListPositionAllocator> ctrlPos = CreateObject<ListPositionAllocator> ();
  ctrlPos->Add (Vector (-80.0, 0.0, HEIGHT_HAWK));
  mobility.SetPositionAllocator (ctrlPos);
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (control);

  // LHD — waypoints según escenario
  mobility.SetMobilityModel ("ns3::WaypointMobilityModel");
  mobility.Install (lhd);

  Ptr<WaypointMobilityModel> lhdMob =
      lhd.Get (0)->GetObject<WaypointMobilityModel> ();

  tunnelLoss->SetLhdMobility (lhdMob);
  tunnelLoss->SetNlosEnabled (isMobility);

  if (isMobility)
  {
    BuildRealRouteWaypoints (lhdMob, lhdSpeed, simTime);
  }
  else
  {
    // Baseline: recorrido lineal a lo largo de X, NLOS desactivado.
    double t = 0.0, pos = 0.0;
    bool forward = true;
    while (t < simTime + 50.0)
    {
      lhdMob->AddWaypoint (Waypoint (Seconds (t), Vector (pos, 0.0, HEIGHT_LHD)));
      double target = forward ? COVERED_ROUTE_LENGTH_M : 0.0;
      double travel = std::abs (target - pos) / lhdSpeed;
      t  += travel;
      pos = target;
      forward = !forward;
      lhdMob->AddWaypoint (Waypoint (Seconds (t), Vector (pos, 0.0, HEIGHT_LHD)));
      t += 10.0;
    }
  }

  // Registrar APs para PosLogger con parámetros RF reales (v8.1)
  g_apPositions.clear ();
  for (uint32_t i = 0; i < nHawks; i++)
    g_apPositions.push_back ({hawkPos2D[i].x, hawkPos2D[i].y,
                               "H" + std::to_string (i), txPowHawk, 11.0});
  if (nCardFijosScenario > 0)
    g_apPositions.push_back ({CARDINAL_FIJO_X, CARDINAL_FIJO_Y, "CardFijo", txPowCard, 4.8});

  // Referencia global del LHD para callbacks de asociación (v8.1)
  g_lhdMobGlobal = lhdMob;

  // ── Internet Stack ─────────────────────────────────────────────────────────
  InternetStackHelper internet;
  internet.Install (control);
  internet.Install (lhd);

  Ipv4AddressHelper addr;
  addr.SetBase ("10.0.0.0", "255.255.255.0");

  NetDeviceContainer controlDev; controlDev.Add (backboneDev.Get (0));
  Ipv4InterfaceContainer controlIf = addr.Assign (controlDev);
  Ipv4InterfaceContainer lhdIf     = addr.Assign (lhdWifiDev);

  Ipv4Address ctrlAddr = controlIf.GetAddress (0);
  Ipv4Address lhdAddr  = lhdIf.GetAddress (0);

  std::cout << "\n[IP] Control = " << ctrlAddr << std::endl;
  std::cout << "[IP] LHD     = " << lhdAddr  << std::endl;

  // ── Callbacks WiFi ─────────────────────────────────────────────────────────
  Config::ConnectWithoutContext (
      "/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/$ns3::StaWifiMac/Assoc",
      MakeCallback (&OnAssoc));
  Config::ConnectWithoutContext (
      "/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/$ns3::StaWifiMac/DeAssoc",
      MakeCallback (&OnDeAssoc));

  double tStart = 3.0;

  // ── Flujos de tráfico ──────────────────────────────────────────────────────
  //
  // QoS mapeo completo (IEEE 802.11e WMM):
  //   Video:      TOS 0xB8 → DSCP EF  → TID 5 → UP 5 → AC_VI
  //   Comandos:   TOS 0xC0 → DSCP CS6 → TID 7 → UP 6 → AC_VO
  //   Telemetría: TOS 0x00 → DSCP BE  → TID 0 → UP 0 → AC_BE

  // Flujo 1: Video 40Mbps LHD→Control (TOS 0xB8)
  uint16_t vidPort = 5000;
  Ptr<Socket> vidSock = Socket::CreateSocket (
      lhd.Get (0), TypeId::LookupByName ("ns3::UdpSocketFactory"));
  Ptr<CodecDelayApp> vidApp = CreateObject<CodecDelayApp> ();
  vidApp->Setup (vidSock,
                 InetSocketAddress (ctrlAddr, vidPort),
                 1400,
                 DataRate (std::to_string ((uint64_t)(videoRate * 1e6)) + "bps"),
                 codecDelayMs, 0xb8);
  lhd.Get (0)->AddApplication (vidApp);
  vidApp->SetStartTime (Seconds (tStart));
  vidApp->SetStopTime  (Seconds (simTime));

  PacketSinkHelper vidSink ("ns3::UdpSocketFactory",
      InetSocketAddress (Ipv4Address::GetAny (), vidPort));
  ApplicationContainer vidSinkApp = vidSink.Install (control.Get (0));
  vidSinkApp.Start (Seconds (0.0));
  vidSinkApp.Stop  (Seconds (simTime + 5));

  // Flujo 2: Comandos 0.5Mbps Control→LHD (TOS 0xC0 → AC_VO)
  uint16_t cmdPort = 6000;
  InetSocketAddress cmdDst (lhdAddr, cmdPort);
  cmdDst.SetTos (0xC0);
  OnOffHelper cmdHelp ("ns3::UdpSocketFactory", cmdDst);
  cmdHelp.SetAttribute ("DataRate",
      DataRateValue (DataRate (std::to_string ((uint64_t)(cmdRate * 1e6)) + "bps")));
  cmdHelp.SetAttribute ("PacketSize", UintegerValue (128));
  cmdHelp.SetAttribute ("OnTime",
      StringValue ("ns3::ConstantRandomVariable[Constant=1]"));
  cmdHelp.SetAttribute ("OffTime",
      StringValue ("ns3::ConstantRandomVariable[Constant=0]"));
  ApplicationContainer cmdApp = cmdHelp.Install (control.Get (0));
  cmdApp.Start (Seconds (tStart));
  cmdApp.Stop  (Seconds (simTime));

  PacketSinkHelper cmdSink ("ns3::UdpSocketFactory",
      InetSocketAddress (Ipv4Address::GetAny (), cmdPort));
  ApplicationContainer cmdSinkApp = cmdSink.Install (lhd.Get (0));
  cmdSinkApp.Start (Seconds (0.0));
  cmdSinkApp.Stop  (Seconds (simTime + 5));

  // Flujo 3: Telemetría 0.1Mbps continuo LHD→Control (TOS 0x00 → AC_BE)
  // OnTime=1, OffTime=0 → transmisión continua → 0.1 Mbps real (corrige v7)
  uint16_t telPort = 7000;
  InetSocketAddress telDst (ctrlAddr, telPort);
  telDst.SetTos (0x00);
  OnOffHelper telHelp ("ns3::UdpSocketFactory", telDst);
  telHelp.SetAttribute ("DataRate",
      DataRateValue (DataRate (std::to_string ((uint64_t)(telRate * 1e6)) + "bps")));
  telHelp.SetAttribute ("PacketSize", UintegerValue (200));
  telHelp.SetAttribute ("OnTime",
      StringValue ("ns3::ConstantRandomVariable[Constant=1]"));
  telHelp.SetAttribute ("OffTime",
      StringValue ("ns3::ConstantRandomVariable[Constant=0]"));
  ApplicationContainer telApp = telHelp.Install (lhd.Get (0));
  telApp.Start (Seconds (tStart));
  telApp.Stop  (Seconds (simTime));

  PacketSinkHelper telSink ("ns3::UdpSocketFactory",
      InetSocketAddress (Ipv4Address::GetAny (), telPort));
  ApplicationContainer telSinkApp = telSink.Install (control.Get (0));
  telSinkApp.Start (Seconds (0.0));
  telSinkApp.Stop  (Seconds (simTime + 5));

  // ── Logger de posición (escenarios mobility) ───────────────────────────────
  if (isMobility)
  {
    g_posLogger.lhdMob    = lhdMob;
    g_posLogger.txPowHawk = txPowHawk;
    g_posLogger.freq      = 5.0e9;
    g_posLogger.dbp       = 40.0;
    g_posLogger.expLOS    = 1.9;
    g_posLogger.expNLOS   = 3.4;
    g_posLogger.Open ("results/" + scenario + "_v9_pos_log.csv");
    Simulator::Schedule (Seconds (tStart), &PosLogger::Log, &g_posLogger);

    // Assoc log v8.1
    g_assocLog.open ("results/" + scenario + "_v9_assoc_log.csv");
    g_assocLog << "time_s,event,ap_id,x,y,station_m\n";
  }

  // ── FlowMonitor ────────────────────────────────────────────────────────────
  FlowMonitorHelper fmHelp;
  fmHelp.SetMonitorAttribute ("DelayBinWidth",     DoubleValue (0.001));
  fmHelp.SetMonitorAttribute ("JitterBinWidth",     DoubleValue (0.0005));
  fmHelp.SetMonitorAttribute ("PacketSizeBinWidth", DoubleValue (20.0));
  Ptr<FlowMonitor> fm = fmHelp.InstallAll ();

  // ── NetAnim ────────────────────────────────────────────────────────────────
  std::string animFile = "results/" + scenario + "_v9_anim.xml";
  AnimationInterface anim (animFile);

  anim.UpdateNodeDescription (control.Get (0), "Control");
  anim.UpdateNodeColor       (control.Get (0), 128, 0, 128);
  anim.UpdateNodeSize        (control.Get (0), 5.0, 5.0);

  for (uint32_t i = 0; i < nHawks; i++)
  {
    std::string lbl = "H" + std::to_string (i)
                    + " (" + std::to_string ((int)hawkPos2D[i].x)
                    + "," + std::to_string ((int)hawkPos2D[i].y) + ")";
    anim.UpdateNodeDescription (hawks.Get (i), lbl);
    anim.UpdateNodeColor       (hawks.Get (i), 25, 118, 210);
    anim.UpdateNodeSize        (hawks.Get (i), 4.0, 4.0);
  }

  if (nCardFijosScenario > 0)
  {
    anim.UpdateNodeDescription (cardinalFijos.Get (0), "CardFijo\n(183.7,30)");
    anim.UpdateNodeColor       (cardinalFijos.Get (0), 100, 180, 100);
    anim.UpdateNodeSize        (cardinalFijos.Get (0), 4.0, 4.0);
  }

  anim.UpdateNodeDescription (lhd.Get (0), "LHD\nCardinal");
  anim.UpdateNodeColor       (lhd.Get (0), 46, 125, 50);
  anim.UpdateNodeSize        (lhd.Get (0), 5.0, 5.0);

  anim.EnablePacketMetadata (false);

  // ── Simulación ─────────────────────────────────────────────────────────────
  Simulator::Stop (Seconds (simTime + 10));
  Simulator::Run ();

  // ── Resultados y KPIs ──────────────────────────────────────────────────────
  fm->CheckForLostPackets ();
  Ptr<Ipv4FlowClassifier>         cls   = DynamicCast<Ipv4FlowClassifier> (fmHelp.GetClassifier ());
  FlowMonitor::FlowStatsContainer stats = fm->GetFlowStats ();

  std::string seedSuffix = (scenario == "baseline" && seed > 1)
                           ? "_s" + std::to_string (seed) : "";
  std::string resFile = "results/" + scenario + seedSuffix + "_v9_flow_stats.csv";
  std::ofstream out (resFile);
  out << "flow_id,flow_name,protocol,tx_pkts,rx_pkts,tx_bytes,rx_bytes,"
      << "delay_mean_ms,delay_p95_ms,jitter_mean_ms,jitter_p95_ms,"
      << "pdr_pct,plr_pct,ip_throughput_mbps,payload_goodput_mbps,"
      << "codec_delay_ms,total_e2e_ms,total_e2e_p95_ms,dst_port" << std::endl;

  std::cout << "\n===== RESULTADOS v9 (" << scenario << ") =====" << std::endl;
  std::cout << "Codec delay: " << codecDelayMs << " ms" << std::endl;

  std::cout << "\n[DEBUG] Flujos detectados: " << stats.size () << std::endl;
  for (auto &it : stats)
  {
    Ipv4FlowClassifier::FiveTuple ft = cls->FindFlow (it.first);
    std::cout << "  Flow " << it.first
              << " " << ft.sourceAddress << ":" << ft.sourcePort
              << " -> " << ft.destinationAddress << ":" << ft.destinationPort
              << " tx=" << it.second.txPackets
              << " rx=" << it.second.rxPackets << std::endl;
  }

  bool allKpiPass = true;

  for (auto &it : stats)
  {
    Ipv4FlowClassifier::FiveTuple ft = cls->FindFlow (it.first);
    FlowMonitor::FlowStats       &fs = it.second;

    double txP = fs.txPackets;
    double rxP = fs.rxPackets;
    if (txP == 0) continue;

    double pdr     = rxP / txP * 100.0;
    double plr     = 100.0 - pdr;
    double delMean = (rxP > 0)
                     ? fs.delaySum.GetSeconds () / rxP * 1000.0 : 0.0;
    double jitMean = (rxP > 1)
                     ? fs.jitterSum.GetSeconds () / (rxP - 1) * 1000.0 : 0.0;
    double dur     = (fs.timeLastRxPacket - fs.timeFirstTxPacket).GetSeconds ();
    double ipTput  = (dur > 0) ? (fs.rxBytes * 8.0 / dur / 1e6) : 0.0;

    std::vector<double> delVec = HistToSamples (fs.delayHistogram,  1.0);
    std::vector<double> jitVec = HistToSamples (fs.jitterHistogram, 0.5);
    double delP95 = Percentile (delVec, 95.0);
    double jitP95 = Percentile (jitVec, 95.0);

    std::string name        = "Other";
    std::string proto       = (ft.protocol == 6) ? "TCP" : "UDP";
    double      codecAdd    = 0.0;
    uint32_t    pktSizePay  = 0;

    if      (ft.destinationPort == vidPort) { name = "Video";      codecAdd = codecDelayMs; pktSizePay = 1400; }
    else if (ft.destinationPort == cmdPort) { name = "Comandos";   pktSizePay = 128; }
    else if (ft.destinationPort == telPort) { name = "Telemetria"; pktSizePay = 200; }
    else if (ft.sourcePort      == cmdPort) { name = "Cmd_ACK";    pktSizePay = 128; }
    else continue;

    double totalE2E    = delMean + codecAdd;
    double totalE2EP95 = delP95  + codecAdd;

    // Goodput de payload: Create<Packet>(N) genera N bytes de payload puro.
    // No descontar headers IP/UDP — esos los agrega la pila de red y ya están
    // contabilizados en rxBytes. El goodput mide throughput de carga útil de app.
    double payloadGoodput = (dur > 0 && rxP > 0)
                            ? ((double)rxP * pktSizePay * 8.0 / dur / 1e6) : 0.0;

    std::cout << std::fixed << std::setprecision (2);
    std::cout << "\n  [" << name << "] " << proto
              << " | tx=" << (uint32_t)txP << " rx=" << (uint32_t)rxP << std::endl;
    std::cout << "    OWD:    " << delMean << " ms media | " << delP95 << " ms P95" << std::endl;
    std::cout << "    Jitter: " << jitMean << " ms media | " << jitP95 << " ms P95" << std::endl;
    std::cout << "    E2E:    " << totalE2E << " ms media | " << totalE2EP95 << " ms P95" << std::endl;
    std::cout << "    PDR: " << pdr << "% | PLR: " << plr << "%"
              << " | IP Tput: " << ipTput << " Mbps"
              << " | Payload goodput: " << payloadGoodput << " Mbps" << std::endl;

    if (name == "Comandos")
    {
      // KPI: one-way delay <= 20ms (OWD = RTT/2; requisito teleoperacion RTT <=40ms)
      // PLR <= 0.5%: umbral operacional incluyendo eventos de handover 802.11 (~154ms c/u).
      // Hasan et al. 2023 especifica 0.1% para enlace estable; con handover reactivo
      // el PLR medio de 300s incluye la ventana de desconexion (~0.4% para 2 handovers).
      bool owdOk = (delMean <= 20.0);
      bool plrOk = (plr     <= 0.5);
      std::cout << "    OWD<=20ms: "  << (owdOk ? "CUMPLE" : "NO CUMPLE")
                << " | PLR<=0.5%: " << (plrOk ? "CUMPLE" : "NO CUMPLE") << std::endl;
      if (!owdOk || !plrOk) allKpiPass = false;
    }
    if (name == "Video")
    {
      // KPI throughput evaluado sobre payload_goodput_mbps (carga útil de app)
      bool e2eOk   = (totalE2E        <= 150.0);
      bool jitOk   = (jitP95          <= 10.0);
      bool goodOk  = (payloadGoodput  >= 38.0);
      bool plrOk   = (plr             <= 1.0);
      std::cout << "    E2E<=150ms: "        << (e2eOk  ? "CUMPLE" : "NO CUMPLE")
                << " | Jitter P95<=10ms: "  << (jitOk  ? "CUMPLE" : "NO CUMPLE")
                << " | Goodput>=38Mbps: "   << (goodOk ? "CUMPLE" : "NO CUMPLE")
                << " | PLR<=1%: "           << (plrOk  ? "CUMPLE" : "NO CUMPLE") << std::endl;
      if (!e2eOk || !jitOk || !goodOk || !plrOk) allKpiPass = false;
    }

    out << it.first << "," << name << "," << proto << ","
        << (uint32_t)txP << "," << (uint32_t)rxP << ","
        << fs.txBytes << "," << fs.rxBytes << ","
        << delMean << "," << delP95 << ","
        << jitMean << "," << jitP95 << ","
        << pdr << "," << plr << "," << ipTput << "," << payloadGoodput << ","
        << codecAdd << "," << totalE2E << "," << totalE2EP95 << ","
        << ft.destinationPort << std::endl;
  }

  out.close ();
  fm->SerializeToXmlFile ("results/" + scenario + seedSuffix + "_v9_flowmon.xml", true, true);

  std::cout << "\n===== VALIDACION GLOBAL =====" << std::endl;
  std::cout << (allKpiPass ? "TODOS LOS KPIs CUMPLEN" : "ALGUNOS KPIs NO CUMPLEN")
            << std::endl;
  std::cout << "CSV:  " << resFile << std::endl;
  if (isMobility)
  {
    std::cout << "POS:  results/" << scenario << "_v9_pos_log.csv" << std::endl;
    std::cout << "ASSOC: results/" << scenario << "_v9_assoc_log.csv" << std::endl;
    if (g_assocLog.is_open ()) g_assocLog.close ();
  }

  Simulator::Destroy ();
  return 0;
}

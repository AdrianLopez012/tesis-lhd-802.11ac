/* ==========================================================================
 * SIMULACIÓN NS-3: RED IEEE 802.11ac PARA TELEOPERACIÓN LHD — NEXA NV1640
 * Versión 3 REAL — geometría real de la zona de teleoperación (layout El Teniente).
 *
 * Reemplaza la galería recta simplificada (v8.2/v9) por la geometría REAL:
 *   - 3 galerías de producción paralelas (X=0, 26, 52 m), largo ~135 m.
 *   - Cruceros superior e inferior que las unen.
 *   - 5 AP Hawk (30 dBm, 11 dBi) + 7 AP Cardinal (23 dBm, 7.5 dBi) — posiciones reales.
 *   - LHD embarca radio Cardinal + antena HELI-40 (4.8 dBi).
 *   - Recorrido: entra por rampa, carga en drawpoint, descarga en pique de traspaso.
 *
 * Modelo de propagación: two-slope calibrado (TamoGraph): n1=1.9, n2=3.4, dbp=40m,
 *   L_system=9.4 dB. Distancia por ruta de túnel; NLOS entre galerías distintas.
 * Estándar: IEEE 802.11ac (Wi-Fi 5), 5 GHz, 40 MHz, 2x2 MIMO.
 *
 * KPIs objetivo (tesis, Tabla 12): OWD comandos<=20ms (RTT<=40ms), PLR comandos
 *   <=0.1% estable / <=0.5% movilidad, E2E video<=150ms (incl. 35ms codec),
 *   jitter P95 video<=10ms, PLR video<=1%, goodput video>=38 Mbps.
 *
 * Uso:  copiar a ns-3.40/scratch/ ; ./ns3 build scratch/lhd-teleop-v3-real
 *       ./ns3 run "lhd-teleop-v3-real --scenario=mobility"
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

#include "geometria_nv1640.h"   // geometría real autogenerada (namespace geo)
#include "recorrido_nv1640.h"   // recorrido real del LHD (mismo que el GIF, namespace rec)

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("LhdTeleopV3Real");

// ============================================================================
// GEOMETRÍA — 3 galerías de producción paralelas + cruceros (usa geometria_nv1640.h)
//   Galerías verticales en X = geo::X_GAL[0..2], de Y_BASE a Y_TOP.
//   Cruceros horizontales en Y_BASE y Y_TOP unen las galerías.
//   La señal viaja por las galerías: misma galería = distancia axial (LOS);
//   galerías distintas = rodea por crucero + penalización NLOS por cruce.
// ============================================================================

static const double HEIGHT_AP  = 2.0;   // altura antenas fijas
static const double HEIGHT_LHD = 1.0;   // altura antena del LHD

// índice de galería más cercana a un X dado
static int GalIndex (double x)
{
  int best = 0; double bd = 1e9;
  for (size_t i = 0; i < geo::X_GAL.size (); i++)
  { double d = std::abs (x - geo::X_GAL[i]); if (d < bd) { bd = d; best = (int)i; } }
  return best;
}

// Distancia por ruta de túnel entre dos puntos (x1,y1)-(x2,y2).
// Misma galería: |dy| + desvíos a la galería. Distinta: sube/baja al crucero
// más cercano (Y_BASE o Y_TOP), cruza en X, y baja/sube.
static double RouteDistance (double x1, double y1, double x2, double y2)
{
  int g1 = GalIndex (x1), g2 = GalIndex (x2);
  double gx1 = geo::X_GAL[g1], gx2 = geo::X_GAL[g2];
  if (g1 == g2)
    return std::abs (y1 - y2) + std::abs (x1 - gx1) + std::abs (x2 - gx2);
  double dtop = (geo::Y_TOP - y1) + std::abs (gx1 - gx2) + (geo::Y_TOP - y2);
  double dbot = (y1 - geo::Y_BASE) + std::abs (gx1 - gx2) + (y2 - geo::Y_BASE);
  return std::min (dtop, dbot) + std::abs (x1 - gx1) + std::abs (x2 - gx2);
}

// nº de galerías cruzadas (para penalización NLOS)
static int CrucesNlos (double x1, double x2)
{ return std::abs (GalIndex (x1) - GalIndex (x2)); }


// ============================================================================
// MODELO DE PROPAGACIÓN EN TÚNEL TWO-SLOPE (calibrado TamoGraph)
// ============================================================================
static const double NLOS_PENAL_DB = 10.0;   // dB por cada galería cruzada

class TunnelPropagationLossModel : public PropagationLossModel
{
public:
  static TypeId GetTypeId (void)
  {
    static TypeId tid = TypeId ("ns3::TunnelPropagationLossModel")
      .SetParent<PropagationLossModel> ()
      .SetGroupName ("Propagation")
      .AddConstructor<TunnelPropagationLossModel> ()
      .AddAttribute ("ExponentLOS",  "Exponente LOS",  DoubleValue (1.9),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_expLOS),  MakeDoubleChecker<double> ())
      .AddAttribute ("ExponentNLOS", "Exponente NLOS", DoubleValue (3.4),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_expNLOS), MakeDoubleChecker<double> ())
      .AddAttribute ("Frequency",    "Frecuencia (Hz)", DoubleValue (5.0e9),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_freq), MakeDoubleChecker<double> ())
      .AddAttribute ("BreakpointDist","Distancia breakpoint (m)", DoubleValue (40.0),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_dbp), MakeDoubleChecker<double> ())
      .AddAttribute ("SystemLossDb", "Perdidas de sistema (dB)", DoubleValue (9.4),
                     MakeDoubleAccessor (&TunnelPropagationLossModel::m_systemLossDb), MakeDoubleChecker<double> ());
    return tid;
  }
  TunnelPropagationLossModel () { m_rand = CreateObject<NormalRandomVariable> (); }
  void SetNlosEnabled (bool e) { m_nlosEnabled = e; }
private:
  double DoCalcRxPower (double txPow, Ptr<MobilityModel> a, Ptr<MobilityModel> b) const override
  {
    Vector pa = a->GetPosition (), pb = b->GetPosition ();
    double d = RouteDistance (pa.x, pa.y, pb.x, pb.y);
    if (d < 1.0) d = 1.0;
    double lam  = 3.0e8 / m_freq;
    double plD0 = 20.0 * std::log10 (4.0 * M_PI / lam);
    double pl;
    if (d < m_dbp) pl = plD0 + 10.0 * m_expLOS * std::log10 (d);
    else           pl = plD0 + 10.0 * m_expLOS * std::log10 (m_dbp)
                            + 10.0 * m_expNLOS * std::log10 (d / m_dbp);
    if (m_nlosEnabled) pl += NLOS_PENAL_DB * CrucesNlos (pa.x, pb.x);
    return txPow - pl - m_systemLossDb;
  }
  int64_t DoAssignStreams (int64_t s) override { m_rand->SetStream (s); return 1; }
  double m_expLOS {1.9}, m_expNLOS {3.4}, m_freq {5.0e9}, m_dbp {40.0}, m_systemLossDb {9.4};
  bool m_nlosEnabled {true};
  Ptr<NormalRandomVariable> m_rand;
};
NS_OBJECT_ENSURE_REGISTERED (TunnelPropagationLossModel);


// ============================================================================
// APLICACIÓN VIDEO CON RETARDO DE CODEC (H.264 encode+decode = 35 ms)
// ============================================================================
class CodecDelayApp : public Application
{
public:
  static TypeId GetTypeId (void)
  {
    static TypeId tid = TypeId ("ns3::CodecDelayApp")
      .SetParent<Application> ().SetGroupName ("Applications")
      .AddConstructor<CodecDelayApp> ();
    return tid;
  }
  void Setup (Ptr<Socket> s, Address a, uint32_t pkt, DataRate r, double codecMs, uint8_t tos)
  { m_socket=s; m_peer=a; m_pkt=pkt; m_rate=r; m_codec=MilliSeconds(codecMs); m_tos=tos; }
private:
  void StartApplication () override
  { m_running=true; m_socket->Bind(); m_socket->Connect(m_peer); m_socket->SetIpTos(m_tos);
    m_ev=Simulator::Schedule(m_codec,&CodecDelayApp::Send,this); }
  void StopApplication () override
  { m_running=false; if(m_ev.IsRunning()) Simulator::Cancel(m_ev); if(m_socket) m_socket->Close(); }
  void Send ()
  { m_socket->Send(Create<Packet>(m_pkt));
    if(m_running){ Time next=Seconds(m_pkt*8.0/m_rate.GetBitRate());
      m_ev=Simulator::Schedule(next,&CodecDelayApp::Send,this);} }
  Ptr<Socket> m_socket; Address m_peer; uint32_t m_pkt{1400}; DataRate m_rate;
  Time m_codec; uint8_t m_tos{0}; bool m_running{false}; EventId m_ev;
};
NS_OBJECT_ENSURE_REGISTERED (CodecDelayApp);


// ============================================================================
// UTILIDADES
// ============================================================================
static double Percentile (std::vector<double> v, double p)
{
  if (v.empty ()) return 0.0;
  std::sort (v.begin (), v.end ());
  double idx = (p/100.0)*(double)(v.size ()-1);
  size_t lo=(size_t)idx, hi=lo+1;
  if (hi>=v.size ()) return v.back ();
  return v[lo]*(1.0-(idx-lo))+v[hi]*(idx-lo);
}
static std::vector<double> HistToSamples (const Histogram &h, double bw)
{
  std::vector<double> s;
  for (uint32_t b=0;b<h.GetNBins ();b++){ uint32_t c=h.GetBinCount (b); double m=(b+0.5)*bw;
    for(uint32_t k=0;k<c;k++) s.push_back (m); }
  return s;
}

// logger de posición/RSSI y assoc
static std::ofstream g_posLog, g_assocLog;
static std::map<std::string,std::string> g_macToId;
static Ptr<WaypointMobilityModel> g_lhdMob;
struct ApInfo { double x,y; std::string id; double ptdbm, gtdbi; };
static std::vector<ApInfo> g_aps;

static std::string MacToString (Mac48Address a){ std::ostringstream o; o<<a; return o.str (); }

void OnAssoc (Mac48Address a)
{
  std::string k=MacToString(a); std::string id=g_macToId.count(k)?g_macToId[k]:k;
  double t=Simulator::Now().GetSeconds();
  std::cout<<"[WiFi] LHD asociado a "<<id<<"  t="<<t<<"s\n";
  if(g_assocLog.is_open() && g_lhdMob){ Vector p=g_lhdMob->GetPosition();
    g_assocLog<<std::fixed<<std::setprecision(2)<<t<<",assoc,"<<id<<","<<p.x<<","<<p.y<<"\n"; }
}
void OnDeAssoc (Mac48Address a)
{
  std::string k=MacToString(a); std::string id=g_macToId.count(k)?g_macToId[k]:k;
  double t=Simulator::Now().GetSeconds();
  if(g_assocLog.is_open() && g_lhdMob){ Vector p=g_lhdMob->GetPosition();
    g_assocLog<<std::fixed<<std::setprecision(2)<<t<<",deassoc,"<<id<<","<<p.x<<","<<p.y<<"\n"; }
}

// RSSI estimado del mejor AP (para el pos_log) — coherente con DoCalcRxPower
static void PosLog ()
{
  double t=Simulator::Now().GetSeconds();
  Vector p=g_lhdMob->GetPosition();
  double best=-999; std::string bid="?";
  double lam=3.0e8/5.0e9, plD0=20.0*std::log10(4.0*M_PI/lam);
  for(const auto &ap:g_aps){
    double d=RouteDistance(p.x,p.y,ap.x,ap.y); if(d<1)d=1;
    double pl = d<40.0 ? plD0+10*1.9*std::log10(d)
                       : plD0+10*1.9*std::log10(40.0)+10*3.4*std::log10(d/40.0);
    pl += NLOS_PENAL_DB*CrucesNlos(p.x,ap.x);
    double rssi=ap.ptdbm+ap.gtdbi+4.8-pl-9.4;   // rxGain LHD=4.8 (HELI-40)
    if(rssi>best){best=rssi;bid=ap.id;}
  }
  g_posLog<<std::fixed<<std::setprecision(2)<<t<<","<<p.x<<","<<p.y<<","<<bid<<","<<best<<"\n";
  Simulator::Schedule(Seconds(1.0),&PosLog);
}


// ============================================================================
// RECORRIDO DEL LHD — entra por rampa, carga en drawpoints, descarga en piques.
// Ruta por las galerías (no cruza roca). Ida y vuelta cíclica hasta simTime.
// ============================================================================
static void BuildRoute (Ptr<WaypointMobilityModel> mob, double speed, double simTime)
{
  // Usa el recorrido REAL del GIF (recorrido_nv1640.h): grafo Dijkstra + maniobras
  // de encarar/rodear/reversa/carga/descarga. Se repite el ciclo hasta simTime.
  (void)speed;
  const auto &R = rec::RECORRIDO;
  double tBase = 0.0;
  int ciclo = 0;
  while (tBase < simTime + 30.0)
  {
    for (size_t i = 0; i < R.size (); i++)
    {
      double t = tBase + R[i].t;
      // evita tiempo duplicado en el empalme entre ciclos
      if (ciclo > 0 && i == 0) continue;
      mob->AddWaypoint (Waypoint (Seconds (t), Vector (R[i].x, R[i].y, HEIGHT_LHD)));
    }
    tBase += rec::CICLO_DUR + 1.0;   // +1s de separación entre ciclos
    ciclo++;
  }
}


// ============================================================================
// MAIN
// ============================================================================
int main (int argc, char *argv[])
{
  std::string scenario = "mobility";
  double simTime=300.0, lhdSpeed=2.22, videoRate=40.0, cmdRate=0.5, telRate=0.1;
  double txPowHawk=30.0, txPowCard=23.0, codecMs=35.0;
  uint32_t seed=1;

  CommandLine cmd;
  cmd.AddValue("scenario","escenario",scenario);
  cmd.AddValue("simTime","Tiempo sim (s)",simTime);
  cmd.AddValue("lhdSpeed","Velocidad LHD (m/s)",lhdSpeed);
  cmd.AddValue("videoRate","Tasa video (Mbps)",videoRate);
  cmd.AddValue("seed","Semilla",seed);
  cmd.Parse(argc,argv);
  RngSeedManager::SetSeed(seed); RngSeedManager::SetRun(seed);

  bool isMobility = (scenario != "baseline");
  uint32_t nHawks = geo::HAWKS.size ();      // 5
  uint32_t nCards = geo::CARDINALS.size ();  // 7

  std::cout<<"===== Sim v3 REAL — NV1640 — "<<scenario<<" =====\n";
  std::cout<<nHawks<<" Hawk + "<<nCards<<" Cardinal | Video="<<videoRate
           <<"Mbps LHD="<<lhdSpeed<<"m/s | 802.11ac 5GHz 40MHz 2x2\n";

  // ── Nodos ──
  NodeContainer hawks;   hawks.Create(nHawks);
  NodeContainer cards;   cards.Create(nCards);
  NodeContainer lhd;     lhd.Create(1);
  NodeContainer control; control.Create(1);

  // ── Backbone CSMA 1Gbps (todos los AP + control) ──
  CsmaHelper csma;
  csma.SetChannelAttribute("DataRate",StringValue("1Gbps"));
  csma.SetChannelAttribute("Delay",TimeValue(MicroSeconds(10)));
  NodeContainer bb; bb.Add(control); bb.Add(hawks); bb.Add(cards);
  NetDeviceContainer bbDev = csma.Install(bb);

  // ── Canal WiFi con modelo de túnel ──
  Ptr<TunnelPropagationLossModel> loss = CreateObject<TunnelPropagationLossModel>();
  loss->SetNlosEnabled(isMobility);
  Ptr<YansWifiChannel> chan = CreateObject<YansWifiChannel>();
  chan->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());
  chan->SetPropagationLossModel(loss);

  WifiHelper wifi; wifi.SetStandard(WIFI_STANDARD_80211ac);
  wifi.SetRemoteStationManager("ns3::MinstrelHtWifiManager");
  Ssid ssid=Ssid("nexa-lhd");

  auto mkPhy=[&](double txp,double gain){
    YansWifiPhyHelper phy; phy.SetChannel(chan);
    phy.Set("ChannelSettings",StringValue("{0, 40, BAND_5GHZ, 0}"));
    phy.Set("TxPowerStart",DoubleValue(txp)); phy.Set("TxPowerEnd",DoubleValue(txp));
    phy.Set("TxGain",DoubleValue(gain)); phy.Set("RxGain",DoubleValue(gain));
    phy.Set("Antennas",UintegerValue(2));
    phy.Set("MaxSupportedTxSpatialStreams",UintegerValue(2));
    phy.Set("MaxSupportedRxSpatialStreams",UintegerValue(2));
    return phy;
  };

  WifiMacHelper macAp;
  std::vector<NetDeviceContainer> hawkDev(nHawks), cardDev(nCards);
  YansWifiPhyHelper phyHawk=mkPhy(txPowHawk,11.0);
  const Time BEACON=MicroSeconds(102400);
  for(uint32_t i=0;i<nHawks;i++){
    macAp.SetType("ns3::ApWifiMac","Ssid",SsidValue(ssid),
                  "BeaconInterval",TimeValue(BEACON),"QosSupported",BooleanValue(true));
    NodeContainer n; n.Add(hawks.Get(i)); hawkDev[i]=wifi.Install(phyHawk,macAp,n);
  }
  YansWifiPhyHelper phyCard=mkPhy(txPowCard,7.5);
  for(uint32_t i=0;i<nCards;i++){
    macAp.SetType("ns3::ApWifiMac","Ssid",SsidValue(ssid),
                  "BeaconInterval",TimeValue(BEACON),"QosSupported",BooleanValue(true));
    NodeContainer n; n.Add(cards.Get(i)); cardDev[i]=wifi.Install(phyCard,macAp,n);
  }
  // LHD: STA con antena HELI-40 (4.8 dBi), radio Cardinal (23 dBm)
  YansWifiPhyHelper phySta=mkPhy(txPowCard,4.8);
  WifiMacHelper macSta;
  macSta.SetType("ns3::StaWifiMac","Ssid",SsidValue(ssid),
                 "ActiveProbing",BooleanValue(false),"QosSupported",BooleanValue(true));
  NetDeviceContainer lhdDev=wifi.Install(phySta,macSta,lhd);

  // Roaming estable con histéresis: el STA solo se re-asocia cuando pierde de
  // verdad al AP servidor (varios beacons seguidos), evitando el ping-pong entre
  // APs de igual SSID. Emula el roaming L2 del mesh Rajant InstaMesh, que mantiene
  // el enlace (make-before-break) en vez de reasociar por cada beacon marginal.
  Config::Set("/NodeList/"+std::to_string(lhd.Get(0)->GetId())+
              "/DeviceList/*/Mac/$ns3::StaWifiMac/MaxMissedBeacons",UintegerValue(10));
  Config::Set("/NodeList/"+std::to_string(lhd.Get(0)->GetId())+
              "/DeviceList/*/Mac/$ns3::StaWifiMac/AssocRequestTimeout",TimeValue(MilliSeconds(50)));

  // Bridge L2 en cada AP (une su radio con el backbone)
  BridgeHelper br;
  for(uint32_t i=0;i<nHawks;i++){ NetDeviceContainer p; p.Add(bbDev.Get(1+i)); p.Add(hawkDev[i].Get(0)); br.Install(hawks.Get(i),p); }
  for(uint32_t i=0;i<nCards;i++){ NetDeviceContainer p; p.Add(bbDev.Get(1+nHawks+i)); p.Add(cardDev[i].Get(0)); br.Install(cards.Get(i),p); }

  // MAC->id para assoc log
  g_macToId.clear();
  for(uint32_t i=0;i<nHawks;i++){ Ptr<WifiNetDevice> d=DynamicCast<WifiNetDevice>(hawkDev[i].Get(0)); if(d) g_macToId[MacToString(d->GetMac()->GetAddress())]="H"+std::to_string(i+1); }
  for(uint32_t i=0;i<nCards;i++){ Ptr<WifiNetDevice> d=DynamicCast<WifiNetDevice>(cardDev[i].Get(0)); if(d) g_macToId[MacToString(d->GetMac()->GetAddress())]="C"+std::to_string(i+1); }

  // ── Movilidad: AP fijos en sus posiciones reales; LHD por waypoints ──
  MobilityHelper mob;
  Ptr<ListPositionAllocator> apAlloc=CreateObject<ListPositionAllocator>();
  for(const auto &h:geo::HAWKS)    apAlloc->Add(Vector(h.x,h.y,HEIGHT_AP));
  mob.SetPositionAllocator(apAlloc); mob.SetMobilityModel("ns3::ConstantPositionMobilityModel"); mob.Install(hawks);
  Ptr<ListPositionAllocator> cAlloc=CreateObject<ListPositionAllocator>();
  for(const auto &c:geo::CARDINALS) cAlloc->Add(Vector(c.x,c.y,HEIGHT_AP));
  mob.SetPositionAllocator(cAlloc); mob.SetMobilityModel("ns3::ConstantPositionMobilityModel"); mob.Install(cards);
  // control fuera de la zona
  Ptr<ListPositionAllocator> ctrlAlloc=CreateObject<ListPositionAllocator>();
  ctrlAlloc->Add(Vector(-100.0,geo::Y_TOP,HEIGHT_AP));
  mob.SetPositionAllocator(ctrlAlloc); mob.SetMobilityModel("ns3::ConstantPositionMobilityModel"); mob.Install(control);
  // LHD
  mob.SetMobilityModel("ns3::WaypointMobilityModel"); mob.Install(lhd);
  Ptr<WaypointMobilityModel> lhdMob=lhd.Get(0)->GetObject<WaypointMobilityModel>();
  g_lhdMob=lhdMob;
  if(isMobility) BuildRoute(lhdMob,lhdSpeed,simTime);
  else { double t=0; lhdMob->AddWaypoint(Waypoint(Seconds(0),Vector(geo::X_GAL[0],geo::Y_BASE,HEIGHT_LHD)));
         lhdMob->AddWaypoint(Waypoint(Seconds(simTime),Vector(geo::X_GAL[0],geo::Y_TOP,HEIGHT_LHD))); (void)t; }

  // registrar AP para PosLog
  g_aps.clear();
  for(uint32_t i=0;i<nHawks;i++) g_aps.push_back({geo::HAWKS[i].x,geo::HAWKS[i].y,"H"+std::to_string(i+1),txPowHawk,11.0});
  for(uint32_t i=0;i<nCards;i++) g_aps.push_back({geo::CARDINALS[i].x,geo::CARDINALS[i].y,"C"+std::to_string(i+1),txPowCard,7.5});

  // ── Internet ──
  InternetStackHelper inet; inet.Install(control); inet.Install(lhd);
  Ipv4AddressHelper addr; addr.SetBase("10.0.0.0","255.255.255.0");
  Ipv4InterfaceContainer ctrlIf=addr.Assign(bbDev.Get(0));
  Ipv4InterfaceContainer lhdIf=addr.Assign(lhdDev);
  Ipv4Address ctrlAddr=ctrlIf.GetAddress(0), lhdAddr=lhdIf.GetAddress(0);
  std::cout<<"[IP] Control="<<ctrlAddr<<" LHD="<<lhdAddr<<"\n";

  Config::ConnectWithoutContext("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/$ns3::StaWifiMac/Assoc",MakeCallback(&OnAssoc));
  Config::ConnectWithoutContext("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/$ns3::StaWifiMac/DeAssoc",MakeCallback(&OnDeAssoc));

  double tStart=3.0;

  // ── Tráfico (QoS WMM): Video 40Mbps up, Comandos 0.5Mbps down, Telemetría 0.1Mbps up ──
  uint16_t vidPort=5000;
  Ptr<Socket> vidSock=Socket::CreateSocket(lhd.Get(0),TypeId::LookupByName("ns3::UdpSocketFactory"));
  Ptr<CodecDelayApp> vidApp=CreateObject<CodecDelayApp>();
  vidApp->Setup(vidSock,InetSocketAddress(ctrlAddr,vidPort),1400,
                DataRate(std::to_string((uint64_t)(videoRate*1e6))+"bps"),codecMs,0xb8);
  lhd.Get(0)->AddApplication(vidApp); vidApp->SetStartTime(Seconds(tStart)); vidApp->SetStopTime(Seconds(simTime));
  PacketSinkHelper vidSink("ns3::UdpSocketFactory",InetSocketAddress(Ipv4Address::GetAny(),vidPort));
  ApplicationContainer a=vidSink.Install(control.Get(0)); a.Start(Seconds(0)); a.Stop(Seconds(simTime+5));

  uint16_t cmdPort=6000; InetSocketAddress cmdDst(lhdAddr,cmdPort); cmdDst.SetTos(0xC0);
  OnOffHelper cmdH("ns3::UdpSocketFactory",cmdDst);
  cmdH.SetAttribute("DataRate",DataRateValue(DataRate(std::to_string((uint64_t)(cmdRate*1e6))+"bps")));
  cmdH.SetAttribute("PacketSize",UintegerValue(128));
  cmdH.SetAttribute("OnTime",StringValue("ns3::ConstantRandomVariable[Constant=1]"));
  cmdH.SetAttribute("OffTime",StringValue("ns3::ConstantRandomVariable[Constant=0]"));
  ApplicationContainer ca=cmdH.Install(control.Get(0)); ca.Start(Seconds(tStart)); ca.Stop(Seconds(simTime));
  PacketSinkHelper cmdSink("ns3::UdpSocketFactory",InetSocketAddress(Ipv4Address::GetAny(),cmdPort));
  ApplicationContainer cas=cmdSink.Install(lhd.Get(0)); cas.Start(Seconds(0)); cas.Stop(Seconds(simTime+5));

  uint16_t telPort=7000; InetSocketAddress telDst(ctrlAddr,telPort); telDst.SetTos(0x00);
  OnOffHelper telH("ns3::UdpSocketFactory",telDst);
  telH.SetAttribute("DataRate",DataRateValue(DataRate(std::to_string((uint64_t)(telRate*1e6))+"bps")));
  telH.SetAttribute("PacketSize",UintegerValue(200));
  telH.SetAttribute("OnTime",StringValue("ns3::ConstantRandomVariable[Constant=1]"));
  telH.SetAttribute("OffTime",StringValue("ns3::ConstantRandomVariable[Constant=0]"));
  ApplicationContainer ta=telH.Install(lhd.Get(0)); ta.Start(Seconds(tStart)); ta.Stop(Seconds(simTime));
  PacketSinkHelper telSink("ns3::UdpSocketFactory",InetSocketAddress(Ipv4Address::GetAny(),telPort));
  ApplicationContainer tas=telSink.Install(control.Get(0)); tas.Start(Seconds(0)); tas.Stop(Seconds(simTime+5));

  // ── Logs de posición/assoc ──
  if(isMobility){
    g_posLog.open("results/"+scenario+"_v3_pos_log.csv");
    g_posLog<<"time_s,x,y,serving_ap,rssi_dbm\n";
    Simulator::Schedule(Seconds(tStart),&PosLog);
    g_assocLog.open("results/"+scenario+"_v3_assoc_log.csv");
    g_assocLog<<"time_s,event,ap_id,x,y\n";
  }

  // ── FlowMonitor ──
  FlowMonitorHelper fmH;
  fmH.SetMonitorAttribute("DelayBinWidth",DoubleValue(0.001));
  fmH.SetMonitorAttribute("JitterBinWidth",DoubleValue(0.0005));
  Ptr<FlowMonitor> fm=fmH.InstallAll();

  Simulator::Stop(Seconds(simTime+10));
  Simulator::Run();

  // ── KPIs ──
  fm->CheckForLostPackets();
  Ptr<Ipv4FlowClassifier> cls=DynamicCast<Ipv4FlowClassifier>(fmH.GetClassifier());
  auto stats=fm->GetFlowStats();
  std::string resFile="results/"+scenario+"_v3_flow_stats.csv";
  std::ofstream out(resFile);
  out<<"flow,name,tx,rx,pdr_pct,plr_pct,owd_ms,owd_p95_ms,jitter_p95_ms,ip_tput_mbps,goodput_mbps,e2e_ms\n";
  std::cout<<"\n===== RESULTADOS v3 REAL ("<<scenario<<") =====\n";
  bool allOk=true;
  for(auto &it:stats){
    auto ft=cls->FindFlow(it.first); auto &fs=it.second;
    double txP=fs.txPackets, rxP=fs.rxPackets; if(txP==0) continue;
    double pdr=rxP/txP*100.0, plr=100.0-pdr;
    double owd=(rxP>0)?fs.delaySum.GetSeconds()/rxP*1000.0:0.0;
    double dur=(fs.timeLastRxPacket-fs.timeFirstTxPacket).GetSeconds();
    double iptput=(dur>0)?fs.rxBytes*8.0/dur/1e6:0.0;
    auto dv=HistToSamples(fs.delayHistogram,1.0); auto jv=HistToSamples(fs.jitterHistogram,0.5);
    double owdP95=Percentile(dv,95.0), jitP95=Percentile(jv,95.0);
    std::string name="Other"; double codecAdd=0; uint32_t pktPay=0;
    if(ft.destinationPort==vidPort){name="Video";codecAdd=codecMs;pktPay=1400;}
    else if(ft.destinationPort==cmdPort){name="Comandos";pktPay=128;}
    else if(ft.destinationPort==telPort){name="Telemetria";pktPay=200;}
    else continue;
    double goodput=(dur>0&&rxP>0)?(double)rxP*pktPay*8.0/dur/1e6:0.0;
    double e2e=owd+codecAdd;
    std::cout<<"\n["<<name<<"] tx="<<(uint32_t)txP<<" rx="<<(uint32_t)rxP
             <<" | OWD="<<std::fixed<<std::setprecision(2)<<owd<<"ms P95="<<owdP95
             <<" | jitP95="<<jitP95<<"ms | PLR="<<plr<<"% | goodput="<<goodput<<"Mbps | E2E="<<e2e<<"ms\n";
    if(name=="Comandos"){ bool ok=(owd<=20.0)&&(plr<=0.5);
      std::cout<<"   KPI OWD<=20ms & PLR<=0.5%: "<<(ok?"CUMPLE":"NO CUMPLE")<<"\n"; if(!ok)allOk=false; }
    if(name=="Video"){ bool ok=(e2e<=150.0)&&(jitP95<=10.0)&&(goodput>=38.0)&&(plr<=1.0);
      std::cout<<"   KPI E2E<=150 jitP95<=10 goodput>=38 PLR<=1%: "<<(ok?"CUMPLE":"NO CUMPLE")<<"\n"; if(!ok)allOk=false; }
    out<<it.first<<","<<name<<","<<(uint32_t)txP<<","<<(uint32_t)rxP<<","<<pdr<<","<<plr<<","
       <<owd<<","<<owdP95<<","<<jitP95<<","<<iptput<<","<<goodput<<","<<e2e<<"\n";
  }
  out.close();
  fm->SerializeToXmlFile("results/"+scenario+"_v3_flowmon.xml",true,true);
  std::cout<<"\n===== "<<(allOk?"TODOS LOS KPIs CUMPLEN":"ALGUNOS KPIs NO CUMPLEN")<<" =====\n";
  std::cout<<"CSV: "<<resFile<<"\n";
  if(g_posLog.is_open()) g_posLog.close();
  if(g_assocLog.is_open()) g_assocLog.close();
  Simulator::Destroy();
  return 0;
}

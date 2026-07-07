"""
Genera geometria_nv1640.h (header C++) desde mapa_nv1640_datos.py
================================================================
Así el .cc de NS-3 usa EXACTAMENTE la misma geometría que el mapa/GIF, sin
copiar coordenadas a mano. Ejecutar cada vez que cambie la geometría.

Salida: ../geometria_nv1640.h  (en cap3/simulacion_ns3/)
"""
import os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("datos", os.path.join(HERE,"mapa_nv1640_datos.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)

def vec_de(lista):
    """convierte lista de (x,y) a inicializador C++ {{x,y},...}"""
    return ", ".join(f"{{{x:.3f},{y:.3f}}}" for (x,y) in lista)

out = os.path.join(HERE, "..", "geometria_nv1640.h")
with open(out, "w", encoding="utf-8") as f:
    f.write("// ===========================================================================\n")
    f.write("// geometria_nv1640.h — AUTOGENERADO desde mapa_nv1640_datos.py — NO EDITAR\n")
    f.write("// Geometria real de la zona de teleoperacion NV1640 (Nexa Cerro Lindo).\n")
    f.write("// Regenerar con: python graficas_simulacion/generar_geometria_h.py\n")
    f.write("// ===========================================================================\n")
    f.write("#ifndef GEOMETRIA_NV1640_H\n#define GEOMETRIA_NV1640_H\n#include <vector>\n\n")
    f.write("namespace geo {\n\n")
    f.write("struct P { double x, y; };\n\n")

    # galerias (X de cada una), largo, separacion
    f.write(f"static const double LARGO_CALLE = {D.LARGO_CALLE:.4f};\n")
    f.write(f"static const double SEP_CALLES  = {D.SEP:.4f};\n")
    f.write("static const std::vector<double> X_GAL = {" +
            ", ".join(f"{x:.3f}" for x in D.X) + "};\n")
    f.write(f"static const double Y_BASE = {D.YB:.3f};\n")
    f.write(f"static const double Y_TOP  = {D.YT:.3f};\n\n")

    # AP Hawk y Cardinal (posiciones reales del usuario)
    f.write("// AP Hawk (5) — posiciones reales\n")
    f.write("static const std::vector<P> HAWKS = {" + vec_de(D.HAWKS) + "};\n\n")
    f.write("// AP Cardinal (7) — posiciones reales\n")
    f.write("static const std::vector<P> CARDINALS = {" + vec_de(D.CARDINALS_AP) + "};\n\n")

    # drawpoints y piques
    f.write("// Drawpoints (bocas de extraccion)\n")
    f.write("static const std::vector<P> DRAWPOINTS = {" + vec_de(D.DRAWPOINTS) + "};\n\n")
    f.write("// Piques de traspaso (descarga)\n")
    f.write("static const std::vector<P> PIQUES = {" + vec_de(D.PIQUES) + "};\n\n")

    # radio de cobertura de referencia
    f.write(f"static const double COBERTURA_AP = {D.COBERTURA_AP:.1f};\n\n")

    f.write("} // namespace geo\n#endif\n")

print(f"[OK] {os.path.abspath(out)}")
print(f"Hawks: {len(D.HAWKS)} | Cardinals: {len(D.CARDINALS_AP)} | Drawpoints: {len(D.DRAWPOINTS)} | Piques: {len(D.PIQUES)}")

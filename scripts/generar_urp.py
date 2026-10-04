#!/usr/bin/env python3
"""Genera pick_and_place.urp en el formato nativo de PolyScope 3.15 (CB3).

El .urp es un XML comprimido con gzip. La estructura reproducida aqui es la
que escribe PolyScope: se tomo como referencia un programa guardado por el
propio simulador y las clases gui.program.persistence.* de PolyScope.
"""
import gzip
import os
import sys

VERSION = "3.15.8.106339"
SERIE = "20185500000"
DIRECTORIO = "/ursim/programs"
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "programs")

# ---------------------------------------------------------------- waypoints
# Pose cartesiana objetivo (base del robot) y solucion articular calculada por
# el propio controlador UR5 con get_inverse_kin().
WAYPOINTS = {
    "Home": (
        [0.400, 0.000, 0.350, 0.0, 3.1416, 0.0],
        [0.27638, -1.343897, -1.979615, -1.388884, 1.570798, 1.847176]),
    "Above_Pick_1": (
        [0.500, -0.200, 0.250, 0.0, 3.1416, 0.0],
        [-0.176406, -1.762947, -1.838356, -1.111094, 1.570795, 1.394391]),
    "Pick_1": (
        [0.500, -0.200, 0.050, 0.0, 3.1416, 0.0],
        [-0.176406, -2.095047, -2.022065, -0.595284, 1.570795, 1.394391]),
    "Above_Pick_2": (
        [0.500, 0.200, 0.250, 0.0, 3.1416, 0.0],
        [0.584606, -1.762947, -1.838356, -1.111093, 1.5708, 2.155403]),
    "Pick_2": (
        [0.500, 0.200, 0.050, 0.0, 3.1416, 0.0],
        [0.584606, -2.095048, -2.022065, -0.595282, 1.5708, 2.155403]),
    "Above_Drop": (
        [0.300, 0.350, 0.250, 0.0, 3.1416, 0.0],
        [1.101219, -1.584101, -2.039471, -1.088821, 1.570803, 2.672015]),
    "Drop_1": (
        [0.300, 0.350, 0.060, 0.0, 3.1416, 0.0],
        [1.101219, -1.954773, -2.240234, -0.517386, 1.570803, 2.672015]),
}

V_J, A_J = 1.0471975511965976, 1.3962634015954636   # rad/s, rad/s^2 (MoveJ)
V_L, A_L = 0.25, 0.5                                 # m/s,  m/s^2   (MoveL)
M_PIEZA = 1.0                                        # kg, carga util transportada

# Calibracion cinematica leida del controlador (paquete KINEMATICS_INFO de la
# interfaz primaria): UR5 nominal, sin linealizar, como corresponde al simulador.
DH_DELTA = [0.0] * 6
DH_A = [0.0, -0.425, -0.39225, 0.0, 0.0, 0.0]
DH_D = [0.089159, 0.0, 0.0, 0.10915, 0.09465, 0.0823]
DH_ALPHA = [1.570796327, 0.0, 0.0, 1.570796327, -1.570796327, 0.0]
CHECKSUM = [-1] * 6

SANGRIA = "  "


def num(v):
    """Formato de double igual al de Java."""
    if float(v) == int(v):
        return "%.1f" % v
    return repr(float(v))


def arr(valores):
    """PolyScope separa los arrays con coma y espacio."""
    return ", ".join(num(v) for v in valores)


class Nodo(object):
    def __init__(self, nombre, atributos=None, hijos=None, texto=None):
        self.nombre = nombre
        self.atributos = atributos or []
        self.hijos = hijos or []
        self.texto = texto

    def xml(self, nivel=0):
        pad = SANGRIA * nivel
        attr = "".join(' %s="%s"' % (k, v) for k, v in self.atributos)
        if self.texto is not None:
            return "%s<%s%s>%s</%s>" % (pad, self.nombre, attr, self.texto, self.nombre)
        if not self.hijos:
            return "%s<%s%s/>" % (pad, self.nombre, attr)
        partes = ["%s<%s%s>" % (pad, self.nombre, attr)]
        partes += [h.xml(nivel + 1) for h in self.hijos]
        partes.append("%s</%s>" % (pad, self.nombre))
        return "\n".join(partes)


def hijos(lista):
    return Nodo("children", hijos=lista)


def kinematics():
    return Nodo("kinematics", [
        ("status", "NOT_INITIALIZED"),
        ("validChecksum", "false"),
    ], [
        Nodo("deltaTheta", [("value", arr(DH_DELTA))]),
        Nodo("a", [("value", arr(DH_A))]),
        Nodo("d", [("value", arr(DH_D))]),
        Nodo("alpha", [("value", arr(DH_ALPHA))]),
        Nodo("jointChecksum", [("value", ", ".join(str(c) for c in CHECKSUM))]),
    ])


def waypoint(nombre_nodo, clave):
    """Waypoint de posicion fija: articulaciones, pose de TCP y pose de brida."""
    pose, joints = WAYPOINTS[clave]
    return Nodo("Waypoint", [
        ("type", "Fixed"),
        ("name", nombre_nodo),
        ("kinematicsFlags", "4"),
    ], [
        Nodo("motionParameters"),
        Nodo("position", [("joints", arr(joints)), ("pose", arr(pose))]),
        Nodo("poseInFeatureCoordinates", [("pose", arr(pose))]),
        Nodo("outputFlangePose", [("pose", arr(pose))]),
    ])


def mover(tipo, nombre_nodo, clave):
    vel, acc = (V_J, A_J) if tipo == "MoveJ" else (V_L, A_L)
    return Nodo("Move", [
        ("motionType", tipo),
        ("speed", num(vel)),
        ("acceleration", num(acc)),
        ("useActiveTCP", "true"),
    ], [hijos([waypoint(nombre_nodo, clave)])])


def set_salida(valor, payload=0.0):
    """Set de salida digital (efector final) y declaracion de carga util.

    Al cerrar la garra se declara la masa de la pieza; al abrirla se libera
    poniendo la carga util a cero en el mismo nodo.
    """
    return Nodo("Set", [
        ("type", "DigitalOutput"),
        ("payload", num(payload)),
        ("tcpAsCog", "true"),
    ], [
        Nodo("pin", [("ioName", "digital_out[0]")]),
        Nodo("digitalValue", texto="1" if valor else "0"),
    ])


def esperar(segundos):
    return Nodo("Wait", [("type", "Sleep")], [
        Nodo("waitTime", texto=num(segundos)),
    ])


def esperar_entrada():
    """Espera a la confirmacion del operador en digital_in[0]."""
    return Nodo("Wait", [("type", "DigitalInput")], [
        Nodo("pin", [("ioName", "digital_in[0]")]),
        Nodo("digitalValue", texto="1"),
    ])


def ciclo(indice):
    """Un ciclo completo de pick and place sobre el punto de recogida n."""
    arriba = "Above_Pick_%d" % indice
    recogida = "Pick_%d" % indice
    s = "_c%d" % indice
    return [
        mover("MoveJ", arriba, arriba),               # intermedio sobre recogida
        esperar(0.3),                                 # pausa en punto intermedio
        mover("MoveL", recogida, recogida),           # descenso vertical
        set_salida(True, M_PIEZA),                    # sujetar pieza y declarar carga
        esperar(0.5),                                 # actuacion del efector
        mover("MoveL", arriba + "_ret", arriba),      # ascenso con pieza
        mover("MoveJ", "Above_Drop" + s, "Above_Drop"),
        esperar(0.3),                                 # pausa en punto intermedio
        mover("MoveL", "Drop_1" + s, "Drop_1"),       # descenso a la entrega
        set_salida(False, 0.0),                       # liberar carga util (payload a 0)
        esperar(0.5),
        mover("MoveL", "Above_Drop" + s + "_ret", "Above_Drop"),
    ]


def construir():
    cuerpo = ciclo(1) + ciclo(2) + [
        mover("MoveJ", "Home_fin", "Home"),
        esperar_entrada(),                            # confirmacion del usuario
    ]
    bucle = Nodo("Loop", [("type", "Forever")], [hijos(cuerpo)])
    principal = Nodo("MainProgram", [
        ("runOnlyOnce", "true"),
        ("InitVariablesNode", "false"),
    ], [hijos([
        set_salida(False),                            # estado inicial del efector
        mover("MoveJ", "Home", "Home"),
        bucle,
    ])])
    raiz = Nodo("URProgram", [
        ("name", "pick_and_place"),
        ("installation", "default"),
        ("installationRelativePath", "default"),
        ("directory", DIRECTORIO),
        ("createdIn", VERSION),
        ("lastSavedIn", VERSION),
        ("robotSerialNumber", SERIE),
    ], [kinematics(), hijos([principal])])
    return raiz.xml() + "\n"


def main():
    destino = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SALIDA, "pick_and_place.urp")
    xml = construir()
    with open(destino + ".xml", "w") as f:
        f.write(xml)
    with gzip.open(destino, "wb") as f:
        f.write(xml.encode("utf-8"))
    print("Generado %s (%d bytes de XML)" % (destino, len(xml)))


if __name__ == "__main__":
    main()

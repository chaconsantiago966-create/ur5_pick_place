#!/usr/bin/env python3
"""Pide al controlador UR5 simulado la cinematica inversa de los waypoints.

Abre un socket de escucha en el host, envia un URScript por la interfaz
secundaria (30002) y recibe de vuelta las soluciones articulares calculadas
por el propio controlador con get_inverse_kin().
"""
import socket
import sys
import threading

ROBOT = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
HOST_IP = sys.argv[2] if len(sys.argv) > 2 else "172.17.0.1"
PUERTO = 40555

WAYPOINTS = [
    ("Home",         (0.400,  0.000, 0.350)),
    ("Above_Pick_1", (0.500, -0.200, 0.250)),
    ("Pick_1",       (0.500, -0.200, 0.050)),
    ("Above_Pick_2", (0.500,  0.200, 0.250)),
    ("Pick_2",       (0.500,  0.200, 0.050)),
    ("Above_Drop",   (0.300,  0.350, 0.250)),
    ("Drop_1",       (0.300,  0.350, 0.060)),
]
RX, RY, RZ = 0.0, 3.1416, 0.0

recibido = []


def servidor():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PUERTO))
    srv.listen(1)
    srv.settimeout(60)
    con, _ = srv.accept()
    con.settimeout(60)
    buf = b""
    while True:
        try:
            datos = con.recv(4096)
        except socket.timeout:
            break
        if not datos:
            break
        buf += datos
    for trozo in buf.decode(errors="replace").split(";"):
        if trozo.strip():
            recibido.append(trozo.strip())
    con.close()
    srv.close()


def construir_script():
    lineas = [
        "def calcular_ik():",
        '  socket_open("%s", %d, "pc")' % (HOST_IP, PUERTO),
        # Semilla: configuracion de referencia del UR5 (codo arriba, munieca abajo).
        "  qn = [0.0, -1.5708, -1.5708, -1.5708, 1.5708, 0.0]",
    ]
    for nombre, (x, y, z) in WAYPOINTS:
        lineas.append(
            "  q = get_inverse_kin(p[%.4f,%.4f,%.4f,%.4f,%.4f,%.4f], qn)"
            % (x, y, z, RX, RY, RZ)
        )
        lineas.append("  qn = q")
        lineas.append('  socket_send_string("%s=", "pc")' % nombre)
        lineas.append('  socket_send_string(to_str(q), "pc")')
        lineas.append('  socket_send_string(";", "pc")')
        lineas.append("  sync()")
    lineas += ['  socket_close("pc")', "end", ""]
    return "\n".join(lineas)


def main():
    hilo = threading.Thread(target=servidor, daemon=True)
    hilo.start()

    guion = construir_script()
    s = socket.create_connection((ROBOT, 30002), timeout=10)
    s.sendall(guion.encode())
    s.close()

    hilo.join(timeout=70)
    if len(recibido) < len(WAYPOINTS):
        print("Respuestas incompletas: %d de %d" % (len(recibido), len(WAYPOINTS)))
        for linea in recibido:
            print(linea)
        return 1
    for linea in recibido:
        print(linea)
    return 0


if __name__ == "__main__":
    sys.exit(main())

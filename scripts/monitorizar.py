#!/usr/bin/env python3
"""Traza en tiempo real los waypoints alcanzados y las E/S digitales.

Lee la interfaz de tiempo real del controlador (puerto 30003) y escribe una
linea cada vez que el robot alcanza un waypoint conocido o cambia una senal.
"""
import socket
import struct
import sys
import time

ROBOT = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
DURACION = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0

OFF_Q, OFF_DI, OFF_DO = 252, 684, 1044
TOL = 0.01

WAYPOINTS = {
    "Home":         [0.27638, -1.343897, -1.979615, -1.388884, 1.570798, 1.847176],
    "Above_Pick_1": [-0.176406, -1.762947, -1.838356, -1.111094, 1.570795, 1.394391],
    "Pick_1":       [-0.176406, -2.095047, -2.022065, -0.595284, 1.570795, 1.394391],
    "Above_Pick_2": [0.584606, -1.762947, -1.838356, -1.111093, 1.5708, 2.155403],
    "Pick_2":       [0.584606, -2.095048, -2.022065, -0.595282, 1.5708, 2.155403],
    "Above_Drop":   [1.101219, -1.584101, -2.039471, -1.088821, 1.570803, 2.672015],
    "Drop_1":       [1.101219, -1.954773, -2.240234, -0.517386, 1.570803, 2.672015],
}


def main():
    rt = socket.create_connection((ROBOT, 30003), timeout=10)
    rt.settimeout(10)
    resto = b""
    t0 = time.time()
    ult_wp = ult_do = ult_di = None
    while time.time() - t0 < DURACION:
        while len(resto) < 4:
            resto += rt.recv(8192)
        largo = struct.unpack(">i", resto[:4])[0]
        while len(resto) < largo:
            resto += rt.recv(8192)
        paquete, resto = resto[:largo], resto[largo:]
        if largo < 1060:
            continue
        q = struct.unpack(">6d", paquete[OFF_Q:OFF_Q + 48])
        do = int(struct.unpack(">d", paquete[OFF_DO:OFF_DO + 8])[0]) & 1
        di = int(struct.unpack(">d", paquete[OFF_DI:OFF_DI + 8])[0]) & 1
        t = time.time() - t0
        if do != ult_do:
            print("%7.2f s  digital_out[0] = %s" % (t, "HIGH" if do else "LOW"))
            ult_do = do
        if di != ult_di:
            print("%7.2f s  digital_in[0]  = %s" % (t, "HIGH" if di else "LOW"))
            ult_di = di
        for nombre, objetivo in WAYPOINTS.items():
            if all(abs(a - b) < TOL for a, b in zip(q, objetivo)):
                if nombre != ult_wp:
                    print("%7.2f s  waypoint %s" % (t, nombre))
                    ult_wp = nombre
                break
    rt.close()


if __name__ == "__main__":
    main()

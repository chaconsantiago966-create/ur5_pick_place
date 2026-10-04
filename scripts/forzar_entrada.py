#!/usr/bin/env python3
"""Fuerza digital_in[0] en el robot simulado sin detener el programa en curso.

Usa un programa secundario (sec) por el puerto 30002, que es el mecanismo que
emplea la propia pestana de E/S de PolyScope en modo simulacion.
"""
import socket
import sys

ROBOT = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
ESTADO = (sys.argv[2].lower() in ("1", "true", "high")) if len(sys.argv) > 2 else True

guion = (
    "sec forzar_entrada():\n"
    "  set_standard_digital_in(0, %s)\n"
    "end\n" % ("True" if ESTADO else "False")
)

s = socket.create_connection((ROBOT, 30002), timeout=10)
s.sendall(guion.encode())
s.close()
print("digital_in[0] = %s" % ("HIGH" if ESTADO else "LOW"))

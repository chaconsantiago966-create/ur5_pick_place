#!/usr/bin/env python3
"""Enciende y libera frenos del UR5 simulado mediante el Dashboard Server."""
import socket
import sys
import time

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"


def dashboard(cmds, espera=1.5):
    s = socket.create_connection((HOST, 29999), timeout=10)
    s.settimeout(10)
    print(s.recv(1024).decode().strip())
    for c in cmds:
        s.sendall((c + "\n").encode())
        time.sleep(espera)
        try:
            print("%-20s -> %s" % (c, s.recv(1024).decode().strip()))
        except socket.timeout:
            print("%-20s -> (sin respuesta)" % c)
    s.close()


if __name__ == "__main__":
    dashboard(["power on", "brake release"], espera=2.0)
    time.sleep(8)
    dashboard(["robotmode", "safetymode"], espera=1.0)

#!/usr/bin/env bash
# Levanta URSim CB3 (UR5) con PolyScope 3.x accesible por VNC web.
set -euo pipefail

NOMBRE=${NOMBRE:-ursim_ur5}
MODELO=${MODELO:-UR5}
PROGRAMAS=${PROGRAMAS:-$(cd "$(dirname "$0")/.." && pwd)/programs}

docker rm -f "$NOMBRE" >/dev/null 2>&1 || true

docker run -d --name "$NOMBRE" \
  -e ROBOT_MODEL="$MODELO" \
  -p 5900:5900 \
  -p 6080:6080 \
  -p 29999:29999 \
  -p 30001:30001 -p 30002:30002 -p 30003:30003 -p 30004:30004 \
  universalrobots/ursim_cb3:latest

echo "URSim $MODELO arrancando como '$NOMBRE'."
echo "PolyScope: http://localhost:6080/vnc.html  (VNC directo en localhost:5900)"
echo "Dashboard 29999, primaria 30001, secundaria 30002, RTDE 30004."

#!/usr/bin/env bash
# Instala el programa local dentro de URSim para abrirlo desde PolyScope.
set -euo pipefail

NOMBRE=${NOMBRE:-ursim_ur5}
ORIGEN=${ORIGEN:-$(cd "$(dirname "$0")/.." && pwd)/programs}

for f in pick_and_place.urp pick_and_place.txt; do
  [ -f "$ORIGEN/$f" ] && docker cp "$ORIGEN/$f" "$NOMBRE":/ursim/programs/"$f"
done

echo "Programa instalado en $NOMBRE:/ursim/programs"
echo "Abrirlo en PolyScope: File > Load Program > pick_and_place.urp"
echo "O por el Dashboard Server:"
echo "  printf 'load pick_and_place.urp\\n' | nc localhost 29999"

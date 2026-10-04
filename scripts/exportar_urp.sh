#!/usr/bin/env bash
# Copia los programas creados dentro del contenedor URSim al equipo local.
set -euo pipefail

NOMBRE=${NOMBRE:-ursim_ur5}
DESTINO=${DESTINO:-$(cd "$(dirname "$0")/.." && pwd)/programs}

mkdir -p "$DESTINO"

# El .urp es el programa; PolyScope escribe ademas el arbol (.txt) y el
# URScript generado (.script) cada vez que se guarda.
docker cp "$NOMBRE":/ursim/programs/pick_and_place.urp "$DESTINO"/pick_and_place.urp
docker cp "$NOMBRE":/ursim/programs/pick_and_place.txt "$DESTINO"/pick_and_place.txt
docker cp "$NOMBRE":/ursim/programs/pick_and_place.script \
          "$DESTINO"/pick_and_place_polyscope.script
docker cp "$NOMBRE":/ursim/programs/default.installation "$DESTINO"/default.installation

# Copia legible del .urp, que es XML comprimido con gzip.
zcat "$DESTINO"/pick_and_place.urp > "$DESTINO"/pick_and_place.urp.xml

echo "Programas exportados a $DESTINO"
ls -l "$DESTINO"

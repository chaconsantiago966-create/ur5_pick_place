# Formato interno del fichero .urp (PolyScope 3.x)

Un `.urp` es un XML serializado con XStream y comprimido con gzip. Para leerlo:

```bash
zcat pick_and_place.urp
```

Las clases `gui.program.persistence.*` de PolyScope definen los nombres de
elementos y atributos. Lo relevante para una rutina de Pick and Place:

## Raíz

```xml
<URProgram name="pick_and_place" installation="default"
           installationRelativePath="default" directory="/ursim/programs"
           createdIn="3.15.8.106339" lastSavedIn="3.15.8.106339"
           robotSerialNumber="..." crcValue="...">
```

`installation` e `installationRelativePath` son obligatorios: sin ellos
PolyScope busca `null.installation` y la carga falla.

Tras la raíz va la calibración cinemática, que PolyScope compara con la del
robot. Los arrays se escriben separados por coma y espacio:

```xml
<kinematics status="NOT_INITIALIZED" validChecksum="false">
  <deltaTheta value="0.0, 0.0, 0.0, 0.0, 0.0, 0.0"/>
  <a value="0.0, -0.425, -0.39225, 0.0, 0.0, 0.0"/>
  <d value="0.089159, 0.0, 0.0, 0.10915, 0.09465, 0.0823"/>
  <alpha value="1.570796327, 0.0, 0.0, 1.570796327, -1.570796327, 0.0"/>
  <jointChecksum value="-1, -1, -1, -1, -1, -1"/>
</kinematics>
```

Estos valores son los que el controlador publica en el paquete
`KINEMATICS_INFO` de la interfaz primaria (puerto 30001).

## Nodos del programa

Los hijos van siempre dentro de un elemento `<children>`.

```xml
<MainProgram runOnlyOnce="true" InitVariablesNode="false">
```

- **Move**: `<Move motionType="MoveJ|MoveL|MoveP" speed="…" acceleration="…"
  useActiveTCP="true">`. Para `MoveJ` la velocidad y la aceleración son
  articulares (rad/s y rad/s²); para `MoveL`, cartesianas (m/s y m/s²).
- **Waypoint**: dentro del `Move`.

  ```xml
  <Waypoint type="Fixed" name="Pick_1" kinematicsFlags="4">
    <motionParameters/>
    <position joints="…6 valores…" pose="x, y, z, rx, ry, rz"/>
    <poseInFeatureCoordinates pose="…"/>
    <outputFlangePose pose="…"/>
  </Waypoint>
  ```

  Si falta la pose articular o las poses auxiliares, PolyScope marca el
  waypoint como indefinido (aparece `?` en la miniatura) y el programa no se
  puede ejecutar.
- **Set**: salida digital y carga útil en el mismo nodo.

  ```xml
  <Set type="DigitalOutput" payload="1.0" tcpAsCog="true">
    <pin ioName="digital_out[0]"/>
    <digitalValue>1</digitalValue>
  </Set>
  ```

  `digitalValue` es un entero (`1`/`0`), no un booleano. Al guardar, PolyScope
  escribe el pin como `referencedName`; al leer acepta también `ioName`.
- **Wait**: por tiempo o por entrada digital.

  ```xml
  <Wait type="Sleep"><waitTime>0.5</waitTime></Wait>

  <Wait type="DigitalInput">
    <pin ioName="digital_in[0]"/>
    <digitalValue>1</digitalValue>
  </Wait>
  ```
- **Loop**: `<Loop type="Forever">` con sus hijos dentro de `<children>`.

## Generación

`scripts/generar_urp.py` construye este XML a partir de la tabla de waypoints y
lo comprime con gzip. El fichero resultante se carga en PolyScope, que al
guardarlo lo reescribe en su forma canónica y genera además el `.txt` con el
árbol y el `.script` con el URScript.

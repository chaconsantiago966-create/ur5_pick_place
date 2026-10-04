# Waypoints — Pick and Place UR5

Marco de referencia: base del robot. Unidades en metros y vector de rotacion
en radianes. Orientacion comun `(0, 3.1416, 0)`: eje Z de la herramienta
apuntando hacia abajo (-Z de la base).

| Waypoint        | X (m) | Y (m)  | Z (m) | Papel en la rutina                         |
|-----------------|-------|--------|-------|--------------------------------------------|
| Home            | 0.400 |  0.000 | 0.350 | Posicion de reposo e inicio de ciclo        |
| Above_Pick_1    | 0.500 | -0.200 | 0.250 | Intermedio de seguridad sobre Pick_1        |
| Pick_1          | 0.500 | -0.200 | 0.050 | Primer punto de recogida                    |
| Above_Pick_2    | 0.500 |  0.200 | 0.250 | Intermedio de seguridad sobre Pick_2        |
| Pick_2          | 0.500 |  0.200 | 0.050 | Segundo punto de recogida                   |
| Above_Drop      | 0.300 |  0.350 | 0.250 | Intermedio de seguridad sobre Drop_1        |
| Drop_1          | 0.300 |  0.350 | 0.060 | Punto de entrega comun a ambos ciclos       |

La distancia radial maxima utilizada es 0.539 m (Above_Pick_1 y Pick_1), muy
por debajo del alcance nominal de 0.850 m del UR5, y la altura minima es
0.050 m sobre la brida de base.

Los tramos verticales entre un punto intermedio y su punto de trabajo se
ejecutan con `MoveL` (250 mm/s, 500 mm/s^2) para mantener la trayectoria
rectilinea; los desplazamientos largos entre zonas usan `MoveJ` (60 deg/s,
80 deg/s^2), mas rapido y sin riesgo de singularidades.

Las soluciones articulares de cada waypoint no se escribieron a mano: se
pidieron al propio controlador UR5 con `get_inverse_kin()`, encadenando cada
punto con el anterior como semilla, de forma que toda la rutina usa la misma
configuracion de brazo. El procedimiento esta en
`scripts/calcular_cinematica.py`.

| Waypoint | Articulaciones (rad) |
|---|---|
| Home | 0.27638, -1.343897, -1.979615, -1.388884, 1.570798, 1.847176 |
| Above_Pick_1 | -0.176406, -1.762947, -1.838356, -1.111094, 1.570795, 1.394391 |
| Pick_1 | -0.176406, -2.095047, -2.022065, -0.595284, 1.570795, 1.394391 |
| Above_Pick_2 | 0.584606, -1.762947, -1.838356, -1.111093, 1.5708, 2.155403 |
| Pick_2 | 0.584606, -2.095048, -2.022065, -0.595282, 1.5708, 2.155403 |
| Above_Drop | 1.101219, -1.584101, -2.039471, -1.088821, 1.570803, 2.672015 |
| Drop_1 | 1.101219, -1.954773, -2.240234, -0.517386, 1.570803, 2.672015 |

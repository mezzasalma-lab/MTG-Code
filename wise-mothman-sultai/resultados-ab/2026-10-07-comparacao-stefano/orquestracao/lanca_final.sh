#!/bin/bash
# A/B final N=10.000 (19 variantes: Frank <- 9 cortes, Master <- 4 cortes, os dois, 3 sensibilidades) x 2 modos + smoke (200 partidas x 2 modos por variante). nice 19. Sinal: ../dados/final.done.
cd "$(dirname "$0")"
LOTES=10000 TAG=final PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_final.json smoke >> ../resumos/log_driver_final.txt 2>&1
LOTES=10000 TAG=final PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_final.json ab >> ../resumos/log_driver_final.txt 2>&1
echo "final rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_final.txt
echo fim > ../dados/final.done

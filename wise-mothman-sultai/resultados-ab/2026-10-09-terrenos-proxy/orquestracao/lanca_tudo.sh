#!/bin/bash
# Lote X (13 variantes x 2 modos) e lote Y (6 variantes, so' resiliencia, comandante-alvo 0.5), retomaveis por variante, nice 19; depois regressao 20.000 x 2 modos (c1 e v1). Sinal: ../dados/terrenos3.done. NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
LOTES=10000 TAG=terrenos3 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_x.json smoke >> ../resumos/log_driver_x.txt 2>&1
LOTES=10000 TAG=terrenos3 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_x.json ab >> ../resumos/log_driver_x.txt 2>&1
echo "x rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_x.txt
LOTES=10000 TAG=cmd50 MODOS=resiliencia PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_y.json ab >> ../resumos/log_driver_y.txt 2>&1
echo "y rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_y.txt
TAG=terrenos3 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_x.json reg 20000 >> ../resumos/log_driver_x.txt 2>&1
echo "reg rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_x.txt
echo fim > ../dados/terrenos3.done

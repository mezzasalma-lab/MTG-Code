#!/bin/bash
# Smoke + A/B N=10.000 (8 variantes x 2 modos, retomavel por variante) + regressao 20.000 x 2 modos (t3). nice 19. Sinal: ../dados/terrenos.done. NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
LOTES=10000 TAG=terrenos PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_terrenos.json smoke >> ../resumos/log_driver_terrenos.txt 2>&1
LOTES=10000 TAG=terrenos PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_terrenos.json ab >> ../resumos/log_driver_terrenos.txt 2>&1
echo "ab rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_terrenos.txt
TAG=terrenos PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_terrenos.json reg 20000 >> ../resumos/log_driver_terrenos.txt 2>&1
echo "reg rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_terrenos.txt
echo fim > ../dados/terrenos.done

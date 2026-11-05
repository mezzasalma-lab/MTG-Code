#!/bin/bash
# Smoke + A/B N=10.000 (10 variantes x 2 modos, retomavel por variante) + regressao 20.000 x 2 modos x 2 variantes. nice 19. Sinais: ../dados/cinco.done. NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
LOTES=10000 TAG=cinco PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_cinco.json smoke >> ../resumos/log_driver_cinco.txt 2>&1
LOTES=10000 TAG=cinco PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_cinco.json ab >> ../resumos/log_driver_cinco.txt 2>&1
echo "ab rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_cinco.txt
TAG=cinco PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_cinco.json reg 20000 >> ../resumos/log_driver_cinco.txt 2>&1
echo "reg rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_cinco.txt
echo fim > ../dados/cinco.done

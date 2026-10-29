#!/bin/bash
# A/B (base + w1) x 2 modos, retomavel, nice 10. Sinal: ../dados/vista.done. NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
LOTES=10000 TAG=vista PYTHONHASHSEED=0 nice -n 10 python3 driver_mm.py config_w.json smoke >> ../resumos/log_driver_w.txt 2>&1
LOTES=10000 TAG=vista PYTHONHASHSEED=0 nice -n 10 python3 driver_mm.py config_w.json ab >> ../resumos/log_driver_w.txt 2>&1
echo "w rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_w.txt
echo fim > ../dados/vista.done

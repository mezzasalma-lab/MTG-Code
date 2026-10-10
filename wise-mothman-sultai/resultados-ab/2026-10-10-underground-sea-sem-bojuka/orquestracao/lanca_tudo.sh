#!/bin/bash
# Lote U (12 variantes x 2 modos), retomavel por variante, nice 19. Sinal: ../dados/under.done. NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
LOTES=10000 TAG=under PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_u.json smoke >> ../resumos/log_driver_u.txt 2>&1
LOTES=10000 TAG=under PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_u.json ab >> ../resumos/log_driver_u.txt 2>&1
echo "u rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_u.txt
echo fim > ../dados/under.done

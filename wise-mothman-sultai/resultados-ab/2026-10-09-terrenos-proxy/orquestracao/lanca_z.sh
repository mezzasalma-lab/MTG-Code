#!/bin/bash
# Lote Z (5 variantes x 2 modos) e Z50 (4 variantes, so' resiliencia, comandante-alvo 0.5), apos o lote X/Y (../dados/terrenos3.done). Sinal: ../dados/terrenos4.done
cd "$(dirname "$0")"
until [ -f ../dados/terrenos3.done ]; do sleep 20; done
LOTES=10000 TAG=terrenos4 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_z.json smoke >> ../resumos/log_driver_z.txt 2>&1
LOTES=10000 TAG=terrenos4 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_z.json ab >> ../resumos/log_driver_z.txt 2>&1
echo "z rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_z.txt
LOTES=10000 TAG=z50 MODOS=resiliencia PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_z50.json ab >> ../resumos/log_driver_z.txt 2>&1
echo "z50 rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_z.txt
TAG=terrenos4 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_z.json reg 20000 >> ../resumos/log_driver_z.txt 2>&1
echo "regz rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_z.txt
echo fim > ../dados/terrenos4.done

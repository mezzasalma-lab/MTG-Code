#!/bin/bash
# 2o lote (quantos terrenos): smoke + A/B N=10.000 (6 variantes x 2 modos). Espera o 1o lote (../dados/terrenos.done). Sinal: ../dados/terrenos2.done
cd "$(dirname "$0")"
until [ -f ../dados/terrenos.done ]; do sleep 20; done
LOTES=10000 TAG=terrenos2 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_terrenos2.json smoke >> ../resumos/log_driver_terrenos2.txt 2>&1
LOTES=10000 TAG=terrenos2 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_terrenos2.json ab >> ../resumos/log_driver_terrenos2.txt 2>&1
echo "ab2 rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_terrenos2.txt
echo fim > ../dados/terrenos2.done

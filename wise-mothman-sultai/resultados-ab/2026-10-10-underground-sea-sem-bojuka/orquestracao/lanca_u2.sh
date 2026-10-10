#!/bin/bash
# Lote U2 (base + u11), depois do lote U. Sinal: ../dados/under2.done
cd "$(dirname "$0")"
until [ -f ../dados/under.done ]; do sleep 20; done
LOTES=10000 TAG=under2 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_u2.json ab >> ../resumos/log_driver_u2.txt 2>&1
echo "u2 rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_u2.txt
echo fim > ../dados/under2.done

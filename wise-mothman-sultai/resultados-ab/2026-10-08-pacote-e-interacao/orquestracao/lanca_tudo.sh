#!/bin/bash
# Smoke ja' feito (resumos/smoke_pacote.txt). Roda o A/B (retomavel por variante) e depois o cemiterio dos oponentes. Sinais: ../dados/pacote.done, ../dados/gy.done. NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
LOTES=10000 TAG=pacote PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_pacote.json ab >> ../resumos/log_driver_pacote.txt 2>&1
echo "pacote rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_pacote.txt
echo fim > ../dados/pacote.done

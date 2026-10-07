#!/bin/bash
# A/B final do Jace: 2 lotes (base + 5-6 variantes) x N=10.000 x 2 modos, no lugar. Sinal de fim: ../dados/final.done. NAO edite o simulador enquanto roda.
cd "$(dirname "$0")"
for k in 1 2; do
  LOTES=10000 TAG=final_$k PYTHONHASHSEED=0 python3 driver_mm.py config_final_$k.json smoke >> ../resumos/log_driver_final.txt 2>&1
  LOTES=10000 TAG=final_$k PYTHONHASHSEED=0 python3 driver_mm.py config_final_$k.json ab >> ../resumos/log_driver_final.txt 2>&1
  echo "lote $k rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_final.txt
done
echo fim > ../dados/final.done

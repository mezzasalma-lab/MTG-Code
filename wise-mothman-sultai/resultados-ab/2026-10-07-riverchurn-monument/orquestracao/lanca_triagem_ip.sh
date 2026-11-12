#!/bin/bash
# Triagem 2 (no lugar, SWAP_IN_PLACE=True): 6 lotes x (base + 14 cortes) x N=2000 x 2 modos. Sinal de fim: ../dados/triagem_ip.done. NAO edite o simulador enquanto roda.
cd "$(dirname "$0")"
for k in 1 2 3 4 5 6; do
  LOTES=2000 TAG=triagemip_$k PYTHONHASHSEED=0 python3 driver_mm.py config_triagem_ip_$k.json ab >> ../resumos/log_driver_triagem_ip.txt 2>&1
  echo "lote $k rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_triagem_ip.txt
done
echo fim > ../dados/triagem_ip.done

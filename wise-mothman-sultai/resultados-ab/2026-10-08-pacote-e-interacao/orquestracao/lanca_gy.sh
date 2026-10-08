#!/bin/bash
# Cemiterio dos oponentes por turno, N=10.000 x 2 modos (sementes 3.000.000+i), simulador congelado. Sinal: ../dados/gy.done
cd "$(dirname "$0")"
for modo in padrao resiliencia; do
  PYTHONHASHSEED=0 nice -n 19 python3 gy_opp.py 10000 $modo ../dados/gy_oponentes_${modo}.json.xz >> ../resumos/log_gy.txt 2>&1
done
echo fim > ../dados/gy.done

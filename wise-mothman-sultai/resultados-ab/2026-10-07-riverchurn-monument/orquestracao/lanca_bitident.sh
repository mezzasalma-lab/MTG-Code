#!/bin/bash
# Bit-identidade 20.000 x 2 modos em 4 fatias paralelas de 5.000 sementes (6.000.000..6.019.999). Sinal de fim: ../dados/bitident.done. NAO edite o simulador enquanto roda.
cd "$(dirname "$0")"
: > ../resumos/bitident_20000.txt
for k in 0 1 2 3; do
  ( PYTHONHASHSEED=0 python3 bitident_monument.py 5000 $((6000000 + k * 5000)) > ../resumos/bitident_fatia_$k.txt 2>&1; echo "rc=$?" >> ../resumos/bitident_fatia_$k.txt ) &
done
wait
for k in 0 1 2 3; do cat ../resumos/bitident_fatia_$k.txt >> ../resumos/bitident_20000.txt; done
echo fim > ../dados/bitident.done

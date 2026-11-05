#!/bin/bash
# Muldrotha por partida: N=10.000 x 2 modos x 2 variantes. Sinal de fim: ../dados/medicao.done. NAO edite o simulador enquanto roda.
cd "$(dirname "$0")"
python3 mede_muldrotha.py > ../resumos/log_medicao.txt 2>&1
echo "rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_medicao.txt
echo fim > ../dados/medicao.done

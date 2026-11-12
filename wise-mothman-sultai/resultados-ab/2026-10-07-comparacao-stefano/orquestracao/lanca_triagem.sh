#!/bin/bash
# Triagem N=2.000 das 42 variantes (Frank <- X, Master <- X) + base, nos 2 modos. Roda com nice 19 (nao atrapalha as validacoes do Jace). Sinal de fim: ../dados/triagem.done. NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
LOTES=2000 TAG=triagem PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_triagem.json ab >> ../resumos/log_driver_triagem.txt 2>&1
echo "triagem rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_triagem.txt
echo fim > ../dados/triagem.done

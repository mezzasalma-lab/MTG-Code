#!/bin/bash
# Smoke das 29 variantes finais + regressao 20.000 x 2 modos das 3 variantes de validacao (padrao, todas as chaves, remove+append). Sinal de fim: ../dados/validacao.done. NAO edite o simulador enquanto roda.
cd "$(dirname "$0")"
TAG=final PYTHONHASHSEED=0 python3 driver_mm.py config_final.json smoke > ../resumos/log_smoke.txt 2>&1
echo "smoke rc=$?" >> ../resumos/log_smoke.txt
TAG=validacao PYTHONHASHSEED=0 python3 driver_mm.py config_reg.json reg 20000 > ../resumos/log_regressao.txt 2>&1
echo "reg rc=$?" >> ../resumos/log_regressao.txt
echo fim > ../dados/validacao.done

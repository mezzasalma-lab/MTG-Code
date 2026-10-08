#!/bin/bash
# Regressao 20.000 x 2 modos x 2 variantes (p1, p3; sementes 5.000.000+i): 0 excecoes. Sinal: ../dados/reg.done
cd "$(dirname "$0")"
TAG=pacote PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_pacote.json reg 20000 >> ../resumos/log_driver_reg.txt 2>&1
echo "reg rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_reg.txt
echo fim > ../dados/reg.done

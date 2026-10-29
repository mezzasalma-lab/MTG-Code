#!/bin/bash
# Regressao 20.000 x 2 modos da variante l5 (2 terrenos no lugar de 2 magias). Sinal: ../dados/reg2.done
cd "$(dirname "$0")"
TAG=terrenos2 PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_terrenos2.json reg 20000 >> ../resumos/log_driver_terrenos2.txt 2>&1
echo "reg2 rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_terrenos2.txt
echo fim > ../dados/reg2.done

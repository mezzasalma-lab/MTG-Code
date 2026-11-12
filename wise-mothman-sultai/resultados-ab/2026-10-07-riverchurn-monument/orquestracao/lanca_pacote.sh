#!/bin/bash
# Monument SOBRE o pacote de 5 trocas + Master <- Negate (pendente, nao aplicado pelo usuario): base = pacote; variantes = pacote + Monument <- X. N=10.000 x 2 modos, no lugar. Sinal: ../dados/pacote.done
cd "$(dirname "$0")"
LOTES=10000 TAG=pacote PYTHONHASHSEED=0 python3 driver_mm.py config_pacote.json ab > ../resumos/log_driver_pacote.txt 2>&1
echo "pacote rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_pacote.txt
echo fim > ../dados/pacote.done

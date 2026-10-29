#!/bin/bash
# A/B N=10.000 do pacote (9 variantes) x 2 modos + smoke (200 partidas x 2 modos por variante). nice 19. Sinal: ../dados/pacote.done. NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
LOTES=10000 TAG=pacote PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_pacote.json smoke >> ../resumos/log_driver_pacote.txt 2>&1
LOTES=10000 TAG=pacote PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_pacote.json ab >> ../resumos/log_driver_pacote.txt 2>&1
echo "pacote rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_pacote.txt
echo fim > ../dados/pacote.done

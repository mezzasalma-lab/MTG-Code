#!/bin/bash
# Lote W (3 variantes x 2 modos) e lote V (3 variantes, so' resiliencia, comandante-alvo 0.5), retomaveis por variante, nice 19; depois regressao 20.000 x 2 modos (e1). Sinal: ../dados/swtrop.done. NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
LOTES=10000 TAG=swtrop PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_w.json smoke >> ../resumos/log_driver_w.txt 2>&1
LOTES=10000 TAG=swtrop PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_w.json ab >> ../resumos/log_driver_w.txt 2>&1
echo "w rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_w.txt
LOTES=10000 TAG=swtrop50 MODOS=resiliencia PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_v.json ab >> ../resumos/log_driver_v.txt 2>&1
echo "v rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_v.txt
TAG=swtrop PYTHONHASHSEED=0 nice -n 19 python3 driver_mm.py config_w.json reg 20000 >> ../resumos/log_driver_w.txt 2>&1
echo "regw rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_driver_w.txt
echo fim > ../dados/swtrop.done

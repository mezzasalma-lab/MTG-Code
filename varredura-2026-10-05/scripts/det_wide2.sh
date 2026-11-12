#!/bin/bash
# Determinismo entre processos no ESTADO FINAL da rodada de 2026-10-05 (ondas 1-5): 3 PYTHONHASHSEED x 1.500 sementes x 2 modos, campo a campo, nos 15 simuladores alterados
cd "$(dirname "$0")"
for spec in "edgar-markov-mardu edgar_markov_goldfish_v1.py 8" "ms-bumbleflower-bant bumbleflower_goldfish_v1.py 10" "azula-grixis azula_goldfish_v1.py 10" "captain-storm-izzet captainstorm_goldfish_v1.py 10" "kutzil-selesnya kutzil_goldfish_v1.py 8" "maralen-sultai maralen_goldfish_v1.py 8" "nekusar-grixis nekusar_goldfish_v1.py 8" "rat-king-verminister ratking_goldfish_v1.py 8" "ulalek-wurbg ulalek_goldfish_v1.py 8" "toph-naya toph_goldfish_v1.py 8" "ur-dragon-wurbg urdragon_goldfish_v1.py 8" "hei-bai-wurbg heibai_goldfish_v1.py 8" "thranduil-sultai thranduil_goldfish_v1.py 8"; do
  set -- $spec; nice -n 10 ./det_check.sh $1 $2 $3 1500
done
nice -n 10 ./det_check.sh prismatic-bridge-wurbg prismatic_bridge_goldfish_v1.py 8 1500 "[false]"
echo FIM_DET_WIDE2

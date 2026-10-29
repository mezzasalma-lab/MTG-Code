#!/bin/bash
# determinismo entre processos: mesma semente, PYTHONHASHSEED diferente
R=${ROOT:-/home/user/MTG-Code}
declare -A SIM=( [azula-grixis]="azula_goldfish_v1.py 10" [beorn-fierce]="beorn_goldfish_v1.py 8" [captain-storm-izzet]="captainstorm_goldfish_v1.py 10" [edgar-markov-mardu]="edgar_markov_goldfish_v1.py 8" [hei-bai-wurbg]="heibai_goldfish_v1.py 8" [kutzil-selesnya]="kutzil_goldfish_v1.py 8" [maralen-sultai]="maralen_goldfish_v1.py 8" [megatron-tyrant-mardu]="megatron_goldfish_v1.py 8" [ms-bumbleflower-bant]="bumbleflower_goldfish_v1.py 10" [nekusar-grixis]="nekusar_goldfish_v1.py 8" [rat-king-verminister]="ratking_goldfish_v1.py 8" [thranduil-sultai]="thranduil_goldfish_v1.py 8" [tom-bombadil-wubrg]="tom_goldfish_v1.py 10" [toph-naya]="toph_goldfish_v1.py 8" [ulalek-wurbg]="ulalek_goldfish_v1.py 8" [ur-dragon-wurbg]="urdragon_goldfish_v1.py 8" [vihaan-goldwaker-mardu]="vihaan_goldfish_v1.py 8" [prismatic-bridge-wurbg]="prismatic_bridge_goldfish_v1.py 8" )
for d in "${!SIM[@]}"; do
  set -- ${SIM[$d]}; f=$1; t=$2; ex=""; [ "$d" == "prismatic-bridge-wurbg" ] && ex="[false]"
  for modo in padrao resiliencia; do
    for hs in 1 2; do PYTHONHASHSEED=$hs python3 det_test.py $R/$d/$f $R/$d $modo 200 $t $ex > /tmp/det_${d}_${modo}_$hs.json 2>/tmp/det_err_${d}_${modo}_$hs.txt; done
    python3 - "$d" "$modo" <<'PY'
import json, sys
d, modo = sys.argv[1:]
try:
    a = json.load(open(f"/tmp/det_{d}_{modo}_1.json")); b = json.load(open(f"/tmp/det_{d}_{modo}_2.json"))
    print(f"{d:28s} {modo:12s} divergem entre hash seeds: {sum(x != y for x, y in zip(a, b))}/{len(a)}")
except Exception as e:
    print(f"{d:28s} {modo:12s} ERRO {type(e).__name__}: {str(e)[:80]}")
PY
  done
done

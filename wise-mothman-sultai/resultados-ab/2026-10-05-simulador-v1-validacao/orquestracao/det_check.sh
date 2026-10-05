#!/bin/bash
# uso: det_check.sh <deck> <sim.py> <turns> <N> [extra_json]   -> divergencia entre 3 hash seeds, por campo, nos 2 modos
d=$1; f=$2; t=$3; n=$4; ex=$5
# FLAGS (env, json) liga/desliga chaves do simulador (controle: chave da correcao desligada)
R=${ROOT:-/home/user/MTG-Code}
for modo in padrao resiliencia; do
  for hs in 11 22 33; do
    PYTHONHASHSEED=$hs python3 det_fields.py $R/$d/$f $R/$d $modo $n $t $ex > /tmp/dc_${d}_${modo}_$hs.json 2>/tmp/dc_err_${d}_${modo}_$hs.txt &
  done
  wait
  python3 - "$d" "$modo" "$n" <<'PY'
import json, sys, collections
d, modo, n = sys.argv[1:]
try:
    r = [json.load(open(f"/tmp/dc_{d}_{modo}_{hs}.json")) for hs in (11, 22, 33)]
except Exception as e:
    print(d, modo, "ERRO", type(e).__name__, str(e)[:100]); sys.exit()
c = collections.Counter(); seeds = []
for i in range(len(r[0])):
    dif = sorted({f for f in r[0][i] if not (r[0][i][f] == r[1][i].get(f) == r[2][i].get(f))})
    for f in dif: c[f] += 1
    if dif: seeds.append(1_000_000 + i)
print(f"{d:26s} {modo:12s} N={len(r[0])} sementes divergentes entre 3 hash seeds: {len(seeds)} {seeds[:5]} campos: {c.most_common(5)}")
PY
done

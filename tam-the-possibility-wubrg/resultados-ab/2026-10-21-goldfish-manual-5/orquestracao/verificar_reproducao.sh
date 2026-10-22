#!/bin/bash
# Refaz os resumos do goldfish manual #5 so' do bruto (dados/goldfish_manual_5_bruto.json) e compara byte a byte (cmp) com os salvos.
# Os 3 replays usam o simulador do repositorio (../../../tam_goldfish_v1.py): se o simulador mudar, os replays mudam.
cd "$(dirname "$0")"
ok=0; total=0; T=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$T/$1" "../resumos/$2"; then echo "IGUAL  $2"; ok=$((ok+1)); else echo "DIFERE $2"; fi; }
python3 linha_do_tempo.py > $T/a; cmpf a linha_do_tempo.md
python3 eventos_compactos.py > $T/b; cmpf b eventos_compactos.txt
python3 deltas_lealdade.py > $T/c; cmpf c deltas_lealdade.txt
for n in 1 2 3; do python3 replay_manual_5.py $n > $T/r$n 2>&1; cmpf r$n replay_semente_$n.txt; done
rm -rf $T
echo "$ok/$total saidas byte a byte iguais"

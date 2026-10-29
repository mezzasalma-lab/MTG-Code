#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte com os resumos salvos. Rodar de dentro de orquestracao/.
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
OUT=ablacao_vihaan.txt chk python3 vih_ablacao.py --sum
for m in off sim best; do OUT=ab_vihaan_10000_cor-$m.txt VIH_COLOR=$m chk python3 vih_ab.py 10000 --sum; done
OUT=castabilidade_cor_vihaan.txt chk python3 vih_cor.py --sum
OUT=enumeracao.txt chk python3 vih_enumeracao.py
echo "$ok/$total tabelas byte a byte iguais"

#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte com os resumos salvos. Rodar de dentro de orquestracao/.
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
for m in core early early_all fodder7 early_all_fodder7; do OUT=ab_powerdepot_10000_$m.txt PD_POLICY=$m chk python3 pd_ab.py 10000 --sum; done
for m in core early_all; do OUT=ab_powerdepot_10000_${m}_strict.txt PD_COLOR=strict PD_POLICY=$m chk python3 pd_ab.py 10000 --sum; done
OUT=enumeracao.txt chk python3 pd_enumeracao.py
echo "$ok/$total tabelas byte a byte iguais"

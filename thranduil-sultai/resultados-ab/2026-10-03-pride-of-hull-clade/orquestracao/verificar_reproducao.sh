#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte com os resumos salvos. Rodar de dentro de orquestracao/.
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
OUT=ab_8t.txt chk python3 thr_ab.py 6000 8 --sum
OUT=ab_10t.txt chk python3 thr_ab.py 6000 10 --sum
OUT=condicional_10t.txt chk python3 thr_condicional.py
OUT=ablacao_thranduil.txt chk python3 thr_ablacao.py --sum
OUT=toughness_por_turno.txt chk python3 thr_toughness.py
OUT=enumeracao.txt chk python3 thr_enumeracao.py
echo "$ok/$total tabelas byte a byte iguais"

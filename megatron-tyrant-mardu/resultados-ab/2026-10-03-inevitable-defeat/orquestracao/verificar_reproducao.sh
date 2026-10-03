#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte com os resumos salvos. Rodar de dentro de orquestracao/.
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
OUT=ablacao_megatron.txt chk python3 meg_ablacao.py --sum
OUT=ab_megatron_10000.txt chk python3 meg_ab.py 10000 --sum
OUT=defeat_alimenta_megatron.txt chk python3 meg_fed.py --sum
OUT=castabilidade_cor_megatron.txt chk python3 meg_cor.py --sum
OUT=enumeracao.txt chk python3 meg_enumeracao.py
echo "$ok/$total tabelas byte a byte iguais"

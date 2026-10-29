#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados e compara byte a byte (cmp) com os resumos salvos. Uso (de qualquer pasta): bash verificar_reproducao.sh
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
OUT=spellbook.txt chk python3 csb_tres.py --sum
OUT=estrato_fase_padrao.txt chk python3 estrato_fase.py padrao
OUT=estrato_fase_resiliencia.txt chk python3 estrato_fase.py resiliencia
echo "$ok/$total saidas byte a byte iguais"

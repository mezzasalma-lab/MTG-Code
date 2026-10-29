#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte com os resumos salvos. Rodar de dentro de orquestracao/.
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
OUT=ab_8t.txt chk python3 thr_ab.py 6000 8 --sum
OUT=ab_10t.txt chk python3 thr_ab.py 6000 10 --sum
OUT=condicional_10t.txt chk python3 thr_condicional.py
OUT=ablacao_thranduil.txt chk python3 thr_ablacao.py --sum
# 2026-10-05: esta tabela joga o simulador AO VIVO; (1) `thr_toughness.py` fixa as chaves de 2026-10-05 em False (comportamento da epoca) e (2) o simulador da epoca iterava um `set` de strings em ordem de hash
# (bug achado e corrigido em 2026-10-05, ver varredura-2026-10-05/), entao o resultado dependia do PYTHONHASHSEED (dos seeds 0 a 5, so' o 5 diferia): fixamos 0.
OUT=toughness_por_turno.txt chk env PYTHONHASHSEED=0 python3 thr_toughness.py
OUT=enumeracao.txt chk python3 thr_enumeracao.py
echo "$ok/$total tabelas byte a byte iguais"

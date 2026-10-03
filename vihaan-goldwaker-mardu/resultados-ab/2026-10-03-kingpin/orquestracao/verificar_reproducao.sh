#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte com os resumos salvos. Rodar de dentro de orquestracao/.
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
SL="Academy Manufactor|Monologue Tax|Back in Town|Teferi's Protection|Blasphemous Act|Life Insurance|Council's Judgment|Requisition Raid|Shoot the Sheriff|Path to Exile|Orochi Soul-Reaver|Lotho, Corrupt Shirriff|Sol Ring|Arcane Signet"
BL="Monologue Tax|Academy Manufactor|Back in Town"
for m in sim anim delib; do OUT=ab_kingpin_6000_$m.txt KP_POLICY=$m chk python3 kp_ab.py 6000 --sum; done
for m in sim anim delib; do OUT=ab_kingpin_6000_t12_${m}_slots.txt KP_POLICY=$m KP_TURNS=12 KP_SLOTS="$SL" chk python3 kp_ab.py 6000 --sum; done
OUT=ab_kingpin_6000_t12_delib_blank.txt KP_POLICY=delib KP_TURNS=12 KP_SLOTS="$BL" KP_BLANKS="$BL" chk python3 kp_ab.py 6000 --sum
OUT=kingpin_vs_blank.txt chk python3 kp_vs_blank.py
OUT=condicional_kingpin_vs_blank.txt chk python3 kp_cond.py
OUT=castabilidade_b_kingpin.txt chk python3 kp_cor.py
OUT=enumeracao.txt chk python3 kp_enumeracao.py
echo "$ok/$total tabelas byte a byte iguais"

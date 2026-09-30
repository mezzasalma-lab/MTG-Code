#!/bin/bash
# Refaz tudo que depende da resiliencia da Sisay com a politica final da Liliana (poupa a Sisay), depois regressao + bit-identidade.
cd /home/user/MTG-Code/prismatic-bridge-wurbg
SC=/tmp/claude-0/-home-user-MTG-Code/6f4db589-169e-5ac7-b0c5-42b29015f83f/scratchpad/pb
AB=$SC/ab
S="Sisay, Weatherlight Captain"
FRA="Tam, the Possibility|Arena Rector+Loyal Tutor|Swan Song"
ENT3="$FRA+Entrust the Spark|Veil of Summer"
for p in 0 1 2 3; do
  python3 ab_candidatas.py $p 4 3000 $AB/lil2 --res-only "${S}|Arena Rector@sisay_activate" "${S}|Arena Rector@sisay_pre_hand_all" "$FRA+${S}|Veil of Summer" "$ENT3+${S}|Oath of Nissa" > $AB/lil2_$p.log 2>&1 &
done
wait
V=("base" "${S}|Arena Rector" "Control Body (2/2 lendaria sem texto)|Arena Rector")
for prof in go_wide voltron low; do
  for p in 0 1 2; do
    python3 ab_candidatas.py $p 3 3000 $AB/sprof3_${prof} --res-only --profile "$prof" "${V[@]}" > $AB/sprof3_${prof}_$p.log 2>&1 &
  done
  wait
done
for p in 0 1 2 3; do
  python3 regress_candidatas.py $p 4 20000 $AB/reg4_$p.json > $AB/reg4_$p.log 2>&1 &
done
wait
python3 $SC/bitident.py 300 > $SC/bitident_lil.txt 2>&1
echo terminou > $AB/final_lil_done.txt

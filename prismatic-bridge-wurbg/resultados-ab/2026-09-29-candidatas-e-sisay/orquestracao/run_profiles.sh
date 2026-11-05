#!/bin/bash
# Sensibilidade a perfil de mesa (so' resiliencia): base + 4 candidatas + controle no slot Arena Rector.
cd /home/user/MTG-Code/prismatic-bridge-wurbg
OUT=/tmp/claude-0/-home-user-MTG-Code/6f4db589-169e-5ac7-b0c5-42b29015f83f/scratchpad/pb/ab
V=("base" "Dihada, Binder of Wills|Arena Rector" "Commodore Guff|Arena Rector" "Vronos, Masked Inquisitor|Arena Rector" "Sarkhan the Masterless|Arena Rector" "Control PW (inerte)|Arena Rector")
for prof in go_wide voltron low; do
  for p in 0 1 2 3; do
    python3 ab_candidatas.py $p 4 3000 "$OUT/prof_${prof}" --profile "$prof" "${V[@]}" > "$OUT/prof_${prof}_$p.log" 2>&1 &
  done
  wait
done
echo "perfis terminaram" > "$OUT/prof_done.txt"

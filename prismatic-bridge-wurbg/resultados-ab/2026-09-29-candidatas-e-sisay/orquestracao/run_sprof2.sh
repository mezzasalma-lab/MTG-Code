#!/bin/bash
# Perfis de mesa com a politica FINAL da Sisay (busca antes da mao): base + Sisay + corpo 2/2 no slot Arena Rector.
cd /home/user/MTG-Code/prismatic-bridge-wurbg
OUT=/tmp/claude-0/-home-user-MTG-Code/6f4db589-169e-5ac7-b0c5-42b29015f83f/scratchpad/pb/ab
while pgrep -f regress_candidatas.py > /dev/null; do sleep 5; done
V=("base" "Sisay, Weatherlight Captain|Arena Rector" "Control Body (2/2 lendaria sem texto)|Arena Rector")
for prof in go_wide voltron low; do
  for p in 0 1 2 3; do
    python3 ab_candidatas.py $p 4 3000 "$OUT/sprof2_${prof}" --res-only --profile "$prof" "${V[@]}" > "$OUT/sprof2_${prof}_$p.log" 2>&1 &
  done
  wait
done
echo terminou > "$OUT/sprof2_done.txt"

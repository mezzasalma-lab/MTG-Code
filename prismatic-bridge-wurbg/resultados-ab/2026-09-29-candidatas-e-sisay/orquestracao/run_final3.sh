#!/bin/bash
cd /home/user/MTG-Code/prismatic-bridge-wurbg
SC=/tmp/claude-0/-home-user-MTG-Code/6f4db589-169e-5ac7-b0c5-42b29015f83f/scratchpad/pb
AB=$SC/ab
for p in 0 1 2 3; do
  python3 regress_candidatas.py $p 4 20000 $AB/reg6_$p.json > $AB/reg6_$p.log 2>&1 &
done
wait
python3 $SC/bitident.py 300 > $SC/bitident_final3.txt 2>&1
echo terminou > $AB/final3_done.txt

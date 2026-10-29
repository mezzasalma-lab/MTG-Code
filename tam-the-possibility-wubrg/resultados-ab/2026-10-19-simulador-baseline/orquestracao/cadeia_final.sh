#!/bin/bash
cd /home/user/MTG-Code/tam-the-possibility-wubrg/resultados-ab/2026-10-19-simulador-baseline/orquestracao
S=/tmp/claude-0/-home-user-MTG-Code/6f4db589-169e-5ac7-b0c5-42b29015f83f/scratchpad
echo "reg_ini $(date +%T)" >> $S/chain_prog.txt
TAG=regressao python3 driver_tam.py config.json reg 20000 > $S/log_reg.txt 2>&1
echo "reg_fim $(date +%T)" >> $S/chain_prog.txt
python3 conservacao.py 20000 > $S/cons.txt 2>&1
echo "cons_fim $(date +%T)" >> $S/chain_prog.txt
REFAZ=1 TAG=baseline python3 driver_tam.py config.json ab > $S/log_ab.txt 2>&1
echo "ab_fim $(date +%T)" >> $S/chain_prog.txt
python3 bitident_ghost.py 1000 > $S/ghost_final.txt 2>&1
echo "ghost_fim $(date +%T)" >> $S/chain_prog.txt
cd /home/user/MTG-Code/varredura-2026-10-05/scripts
bash det_check.sh tam-the-possibility-wubrg tam_goldfish_v1.py 12 600 > $S/det_final.txt 2>&1
echo "det_fim $(date +%T)" >> $S/chain_prog.txt
echo FIM > $S/chain_done.txt

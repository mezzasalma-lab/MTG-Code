#!/bin/bash
# Validacao das 6 candidatas NO ARQUIVO VIVO: (1) bit-identidade 20.000 x 2 modos em 4 fatias de 5.000 (9.000.000..9.019.999), (2) regressao 20.000 x 2 modos das 4 variantes,
# (3) determinismo entre processos (3 PYTHONHASHSEED x 1.500 sementes x 2 modos). Sinal: ../dados/validacao.done. NAO edite o simulador enquanto roda.
cd "$(dirname "$0")"
: > ../resumos/bitident_20000.txt; : > ../resumos/log_validacao.txt
for k in 0 1 2 3; do
  ( PYTHONHASHSEED=0 python3 bitident_c2.py 5000 $((9000000 + k * 5000)) > ../resumos/bitident_fatia_$k.txt 2>&1; echo "rc=$?" >> ../resumos/bitident_fatia_$k.txt ) &
done
wait
for k in 0 1 2 3; do cat ../resumos/bitident_fatia_$k.txt >> ../resumos/bitident_20000.txt; done
echo "bitident fim $(date -u +%H:%M:%S)" >> ../resumos/log_validacao.txt
TAG=validacao PYTHONHASHSEED=0 python3 driver_mm.py config_reg.json reg 20000 > ../resumos/log_regressao.txt 2>&1
echo "reg rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_regressao.txt
echo "reg fim $(date -u +%H:%M:%S)" >> ../resumos/log_validacao.txt
DET=/home/user/MTG-Code/varredura-2026-10-05/scripts
SW='[["An Offer You Can'"'"'t Refuse","Fractured Sanity"],["Negate","Screeching Scorchbeast"],["Arcane Denial","Inexorable Tide"],["Toxic Deluge","Branching Evolution"],["Cold-Eyed Selkie","Loading Zone"],["Didn'"'"'t Say Please","The Earth Crystal"]]'
: > ../resumos/determinismo.txt
echo "Determinismo entre processos: 3 PYTHONHASHSEED (11, 22, 33) x 1.500 sementes x 2 modos, campo a campo no estado final, 12 turnos, arquivo vivo (varredura-2026-10-05/scripts/det_check.sh)" >> ../resumos/determinismo.txt
echo "## as seis no lugar, chaves padrao" >> ../resumos/determinismo.txt
( cd $DET && FLAGS='{"SWAPS": '"$SW"', "SWAP_IN_PLACE": true}' bash det_check.sh wise-mothman-sultai mothman_goldfish_v1.py 12 1500 ) >> ../resumos/determinismo.txt 2>&1
echo "## as seis, remove+append, chaves extremas (SCORCH_MIN_X 1, PERSIST_ZERO_TOUGHNESS_DIES False)" >> ../resumos/determinismo.txt
( cd $DET && FLAGS='{"SWAPS": '"$SW"', "SWAP_IN_PLACE": false, "SCORCH_MIN_X": 1, "PERSIST_ZERO_TOUGHNESS_DIES": false}' bash det_check.sh wise-mothman-sultai mothman_goldfish_v1.py 12 1500 ) >> ../resumos/determinismo.txt 2>&1
echo "determinismo fim $(date -u +%H:%M:%S)" >> ../resumos/log_validacao.txt
echo fim > ../dados/validacao.done

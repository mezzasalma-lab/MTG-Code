#!/bin/bash
# Validacao do Jace: (1) bit-identidade 20.000 x 2 modos em 4 fatias paralelas de 5.000 sementes (7.000.000..7.019.999), (2) regressao 20.000 x 2 modos das 4 variantes (base, Kozilek->Jace
# no lugar, Negate->Jace com TODAS as chaves, Yavimaya Hollow->Jace remove+append sem a linha de vitoria), (3) determinismo entre processos (3 PYTHONHASHSEED x 1.500 sementes x 2 modos, chaves padrao e extremas).
# Sinal de fim: ../dados/validacao.done. NAO edite o simulador enquanto roda.
cd "$(dirname "$0")"
: > ../resumos/bitident_20000.txt
for k in 0 1 2 3; do
  ( PYTHONHASHSEED=0 python3 bitident_jace.py 5000 $((7000000 + k * 5000)) > ../resumos/bitident_fatia_$k.txt 2>&1; echo "rc=$?" >> ../resumos/bitident_fatia_$k.txt ) &
done
wait
for k in 0 1 2 3; do cat ../resumos/bitident_fatia_$k.txt >> ../resumos/bitident_20000.txt; done
echo "bitident fim $(date -u +%H:%M:%S)" >> ../resumos/log_validacao.txt
TAG=validacao PYTHONHASHSEED=0 python3 driver_mm.py config_reg.json reg 20000 > ../resumos/log_regressao.txt 2>&1
echo "reg rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_regressao.txt
echo "reg fim $(date -u +%H:%M:%S)" >> ../resumos/log_validacao.txt
DET=/home/user/MTG-Code/varredura-2026-10-05/scripts
: > ../resumos/determinismo.txt
echo "Determinismo entre processos: 3 PYTHONHASHSEED (11, 22, 33) x 1.500 sementes x 2 modos, campo a campo no estado final, 12 turnos, arquivo vivo (varredura-2026-10-05/scripts/det_check.sh)" >> ../resumos/determinismo.txt
echo "## Kozilek -> Jace, no lugar, chaves padrao" >> ../resumos/determinismo.txt
( cd $DET && FLAGS='{"SWAPS": [["Kozilek, Butcher of Truth","Jace, Wielder of Mysteries"]], "SWAP_IN_PLACE": true}' bash det_check.sh wise-mothman-sultai mothman_goldfish_v1.py 12 1500 ) >> ../resumos/determinismo.txt 2>&1
echo "## Negate -> Jace, no lugar, chaves extremas (JACE_REMOVAL_PROB 0.5, JACE_WIN_LINE False)" >> ../resumos/determinismo.txt
( cd $DET && FLAGS='{"SWAPS": [["Negate","Jace, Wielder of Mysteries"]], "SWAP_IN_PLACE": true, "JACE_REMOVAL_PROB": 0.5, "JACE_WIN_LINE": false}' bash det_check.sh wise-mothman-sultai mothman_goldfish_v1.py 12 1500 ) >> ../resumos/determinismo.txt 2>&1
echo "determinismo fim $(date -u +%H:%M:%S)" >> ../resumos/log_validacao.txt
echo fim > ../dados/validacao.done

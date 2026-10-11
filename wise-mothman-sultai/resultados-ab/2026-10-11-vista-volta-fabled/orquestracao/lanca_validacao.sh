#!/bin/bash
# Validacao da lista APLICADA no simulador VIVO (SWAPS=()): smoke, regressao 20.000 x 2 modos, determinismo entre processos. NAO edite mothman_goldfish_v1.py enquanto roda. Sinal: ../resumos/.validacao_ok
cd "$(dirname "$0")"
TAG=vivo PYTHONHASHSEED=0 nice -n 10 python3 driver_mm.py config_vivo.json smoke >> ../resumos/log_validacao.txt 2>&1
TAG=vivo PYTHONHASHSEED=0 nice -n 10 python3 driver_mm.py config_vivo.json reg 20000 >> ../resumos/log_validacao.txt 2>&1
echo "reg rc=$? $(date -u +%H:%M:%S)" >> ../resumos/log_validacao.txt
OUT=../resumos/determinismo.txt
{ echo "Determinismo entre processos: 3 PYTHONHASHSEED (11, 22, 33) x 1.500 sementes x 2 modos, campo a campo no estado final, 12 turnos, arquivo vivo (varredura-2026-10-05/scripts/det_check.sh)"; echo "## lista APLICADA (simulador vivo, SWAPS=(), COMMANDER_REMOVAL_SHARE=0)"; (cd ../../../../varredura-2026-10-05/scripts && bash det_check.sh wise-mothman-sultai mothman_goldfish_v1.py 12 1500); echo "## lista aplicada com COMMANDER_REMOVAL_SHARE=0.5"; (cd ../../../../varredura-2026-10-05/scripts && FLAGS='{"COMMANDER_REMOVAL_SHARE": 0.5}' bash det_check.sh wise-mothman-sultai mothman_goldfish_v1.py 12 1500); } > $OUT 2>&1
echo fim > ../resumos/.validacao_ok

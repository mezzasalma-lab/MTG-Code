#!/bin/bash
# Roda em sequencia toda a validacao da correcao PLAZA_ENABLES_COMMANDER (CLAUDE.md Regras #1 e #10). NAO edite o simulador enquanto roda (re-simula o arquivo VIVO).
# Saidas: resumos/{smoke,ab_*,compacto_*,regressao_20000,bitident_20000,determinismo}.txt, dados/raw_ab_*.json.xz, resumos/status.txt (uma linha por etapa), resumos/log_driver.txt.
cd "$(dirname "$0")" || exit 2
R=$(cd .. && pwd); ST="$R/resumos/status.txt"; LOG="$R/resumos/log_driver.txt"
: > "$ST"; : > "$LOG"
marca() { echo "$(date -u +%H:%M:%S) $1" >> "$ST"; }
marca "inicio"
python3 driver_mm.py config.json smoke >> "$LOG" 2>&1;           marca "smoke fim"
python3 driver_mm.py config.json ab >> "$LOG" 2>&1;              marca "ab fim"
python3 driver_mm.py config.json reg 20000 >> "$LOG" 2>&1;       marca "regressao fim"
for k in 0 1 2 3; do
  PYTHONHASHSEED=0 python3 bitident.py 5000 $((5000000 + k * 5000)) > "$R/resumos/bitident_chunk_$k.txt" 2>&1 &
done
wait; cat "$R"/resumos/bitident_chunk_*.txt > "$R/resumos/bitident_20000.txt"; marca "bitident fim"
( cd /home/user/MTG-Code/varredura-2026-10-05/scripts && bash det_check.sh wise-mothman-sultai mothman_goldfish_v1.py 12 1500 ) > "$R/resumos/determinismo.txt" 2>&1; marca "determinismo fim"
marca "tudo fim"

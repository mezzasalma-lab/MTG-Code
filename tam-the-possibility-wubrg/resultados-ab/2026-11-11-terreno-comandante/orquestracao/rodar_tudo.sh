#!/bin/bash
# Validacao da correcao COMMANDER_ENABLING_LAND do Tam (CLAUDE.md Regras #1 e #10). NAO edite tam_goldfish_v1.py enquanto roda (re-simula o arquivo VIVO).
# Espera o sinal ESPERA (arquivo) antes de comecar, para nao disputar os 4 nucleos com outra cadeia. Saidas em ../resumos/ e ../dados/.
cd "$(dirname "$0")" || exit 2
R=$(cd .. && pwd); ST="$R/resumos/status.txt"; LOG="$R/resumos/log_driver.txt"
if [ -n "$ESPERA" ]; then while ! grep -q "tudo fim" "$ESPERA" 2>/dev/null; do sleep 30; done; fi
: > "$ST"; : > "$LOG"
marca() { echo "$(date -u +%H:%M:%S) $1" >> "$ST"; }
marca "inicio"
python3 driver.py config.json smoke >> "$LOG" 2>&1;           marca "smoke fim"
python3 driver.py config.json ab >> "$LOG" 2>&1;              marca "ab fim"
python3 driver.py config.json reg 20000 >> "$LOG" 2>&1;       marca "regressao fim"
for k in 0 1 2 3; do
  PYTHONHASHSEED=0 python3 bitident_tam.py 5000 $((5000000 + k * 5000)) > "$R/resumos/bitident_chunk_$k.txt" 2>&1 &
done
wait; cat "$R"/resumos/bitident_chunk_*.txt > "$R/resumos/bitident_20000.txt"; marca "bitident fim"
( cd /home/user/MTG-Code/varredura-2026-10-05/scripts && bash det_check.sh tam-the-possibility-wubrg tam_goldfish_v1.py 12 1500 ) > "$R/resumos/determinismo.txt" 2>&1; marca "determinismo fim"
marca "tudo fim"

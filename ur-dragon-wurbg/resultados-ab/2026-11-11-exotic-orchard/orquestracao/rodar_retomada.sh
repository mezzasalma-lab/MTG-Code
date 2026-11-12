#!/bin/bash
# Retomada (2026-11-12) depois de reinicio do conteiner em 2026-11-11 ~23:5x UTC, que matou a bit-identidade e o determinismo de rodar_tudo.sh.
# smoke, A/B e regressao ja' estavam fechados (status.txt); aqui so' as duas etapas finais, com o mesmo comando. NAO edite urdragon_goldfish_v1.py enquanto roda.
cd "$(dirname "$0")" || exit 2
R=$(cd .. && pwd); ST="$R/resumos/status.txt"
marca() { echo "$(date -u +%Y-%m-%dT%H:%M:%S) $1" >> "$ST"; }
marca "retomada: reinicio do conteiner matou bitident+determinismo de rodar_tudo.sh; relancando so' as 2 etapas finais"
for k in 0 1 2 3; do
  PYTHONHASHSEED=0 python3 bitident_orchard.py 5000 $((5000000 + k * 5000)) > "$R/resumos/bitident_chunk_$k.txt" 2>&1 &
done
wait; cat "$R"/resumos/bitident_chunk_[0-3].txt > "$R/resumos/bitident_20000.txt"; marca "bitident fim"
( cd /home/user/MTG-Code/varredura-2026-10-05/scripts && bash det_check.sh ur-dragon-wurbg urdragon_goldfish_v1.py 8 1500 ) > "$R/resumos/determinismo.txt" 2>&1; marca "determinismo fim"
marca "tudo fim"

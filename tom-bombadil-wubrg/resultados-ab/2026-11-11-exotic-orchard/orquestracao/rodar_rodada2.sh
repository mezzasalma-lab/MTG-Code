#!/bin/bash
# Rodada 2 do Tom (2026-11-11): a bit-identidade da rodada 1 usou um criterio estreito (vigiava `color_sources`; a Orchard NA MAO tambem muda a pontuacao de qual terreno jogar) e deu 331 divergencias
# no grupo "sem Orchard em campo" (ver LEIAME). Aqui: bit-identidade com o criterio `land_prod` (campo OU mao), determinismo e o CONTROLE do determinismo com a chave desligada (o `_mana_cache` do Tom diverge entre
# PYTHONHASHSEED; o controle mostra se isso ja' acontecia sem a correcao).
cd "$(dirname "$0")" || exit 2
R=$(cd .. && pwd); ST="$R/resumos/status.txt"
marca() { echo "$(date -u +%H:%M:%S) $1" >> "$ST"; }
marca "rodada2 inicio"
for k in 0 1 2 3; do
  PYTHONHASHSEED=0 python3 bitident_orchard.py 5000 $((5000000 + k * 5000)) > "$R/resumos/bitident_chunk_$k.txt" 2>&1 &
done
wait; cat "$R"/resumos/bitident_chunk_*.txt > "$R/resumos/bitident_20000.txt"; marca "rodada2 bitident fim"
( cd /home/user/MTG-Code/varredura-2026-10-05/scripts && bash det_check.sh tom-bombadil-wubrg tom_goldfish_v1.py 10 1500 ) > "$R/resumos/determinismo.txt" 2>&1; marca "rodada2 determinismo fim"
( cd /home/user/MTG-Code/varredura-2026-10-05/scripts && FLAGS='{"EXOTIC_ORCHARD_PROXY": false}' bash det_check.sh tom-bombadil-wubrg tom_goldfish_v1.py 10 1500 ) > "$R/resumos/determinismo_controle_chave_desligada.txt" 2>&1; marca "rodada2 determinismo controle fim"
marca "rodada2 tudo fim"

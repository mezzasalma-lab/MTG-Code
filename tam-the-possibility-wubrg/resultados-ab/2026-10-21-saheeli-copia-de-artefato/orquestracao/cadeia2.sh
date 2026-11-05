#!/bin/bash
# 2a cadeia (2026-10-21): refaz bit-identidade e A/B com `ignora_profundo: [copy_of]` (a 1a deu DIVERGE 20000/20000 so' porque todo Permanent ganhou o atributo `copy_of`; ver LEIAME). Nao editar tam_goldfish_v1.py enquanto roda.
cd "$(dirname "$0")"
H=../resumos/cadeia_horarios.txt
for etapa in "bitid 20000" "ab"; do
  echo "$(date -u +%FT%TZ) inicio $etapa (2a cadeia)" >> "$H"
  python3 driver.py config.json $etapa >> ../resumos/log_driver.txt 2>&1
  rc=$?
  echo "$(date -u +%FT%TZ) fim $etapa rc=$rc (2a cadeia)" >> "$H"
done
touch ../resumos/.cadeia2_feita

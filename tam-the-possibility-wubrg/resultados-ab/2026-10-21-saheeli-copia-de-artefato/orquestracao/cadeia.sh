#!/bin/bash
# Cadeia da correcao "Saheeli -2 copia de artefato de mana" (Tam). Roda no simulador VIVO: nao editar tam_goldfish_v1.py enquanto roda.
cd "$(dirname "$0")"
H=../resumos/cadeia_horarios.txt
: > "$H"
for etapa in "smoke" "bitid 20000" "reg 20000 20000" "ab"; do
  echo "$(date -u +%FT%TZ) inicio $etapa" >> "$H"
  python3 driver.py config.json $etapa >> ../resumos/log_driver.txt 2>&1
  rc=$?
  echo "$(date -u +%FT%TZ) fim $etapa rc=$rc" >> "$H"
done
touch ../resumos/.cadeia_feita

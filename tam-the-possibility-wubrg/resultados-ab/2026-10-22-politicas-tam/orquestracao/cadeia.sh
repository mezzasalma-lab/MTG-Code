#!/bin/bash
# Cadeia de validacao (2026-10-22): smoke, bit-identidade 20.000 x 2 modos (3 chaves desligadas == snapshot 2380566), A/B pareado 2.000 e 10.000 x 2 modos (antes, depois e 3 variantes de uma chave so'), regressao 20.000 x 2 modos.
# Nao editar tam_goldfish_v1.py enquanto roda.
cd "$(dirname "$0")"
H=../resumos/cadeia_horarios.txt
for etapa in "smoke" "bitid 20000" "ab" "reg 20000"; do
  echo "$(date -u +%FT%TZ) inicio $etapa" >> "$H"
  python3 driver.py config.json $etapa >> ../resumos/log_driver.txt 2>&1
  rc=$?
  echo "$(date -u +%FT%TZ) fim $etapa rc=$rc" >> "$H"
done
touch ../resumos/.cadeia_feita

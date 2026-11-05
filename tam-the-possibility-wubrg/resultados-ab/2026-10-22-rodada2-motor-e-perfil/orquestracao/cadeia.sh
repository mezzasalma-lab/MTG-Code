#!/bin/bash
# Cadeia de validacao da rodada 2 (2026-10-22): smoke, bit-identidade 20.000 x 2 modos (4 chaves desligadas == snapshot b7c0e19), A/B pareado 2.000 e 10.000 x 2 modos (antes, depois, 5 variantes), regressao 20.000 x 2 modos.
# O `config.json` aponta para codigo/tam_goldfish_v1_DEPOIS_rodada2.py (copia do arquivo vivo): editar o simulador vivo NAO afeta a cadeia.
cd "$(dirname "$0")"
H=../resumos/cadeia_horarios.txt
for etapa in "smoke" "bitid 20000" "ab" "reg 20000"; do
  echo "$(date -u +%FT%TZ) inicio $etapa" >> "$H"
  python3 driver.py config.json $etapa >> ../resumos/log_driver.txt 2>&1
  rc=$?
  echo "$(date -u +%FT%TZ) fim $etapa rc=$rc" >> "$H"
done
touch ../resumos/.cadeia_feita

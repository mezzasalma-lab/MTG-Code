#!/bin/bash
# Cadeia de validacao da troca Ram Through -> Herd Heirloom (2026-10-23): smoke, bit-identidade 20.000 x 2 modos (chaves desligadas == snapshot 1b7dd73), A/B pareado 2.000 e 10.000 x 2 modos,
# regressao 20.000 x 2 modos. Sinal de fim: resumos/.cadeia_feita (NAO commitar). O resultado de cada etapa se confere pelo `Traceback` no log_driver.txt, nunca pelo rc.
cd "$(dirname "$0")"
H=../resumos/cadeia_horarios.txt
for etapa in "smoke" "bitid 20000" "ab" "reg 20000"; do
  echo "$(date -u +%FT%TZ) inicio $etapa" >> "$H"
  python3 driver.py config.json $etapa >> ../resumos/log_driver.txt 2>&1
  echo "$(date -u +%FT%TZ) fim $etapa" >> "$H"
done
touch ../resumos/.cadeia_feita

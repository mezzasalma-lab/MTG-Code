#!/bin/bash
# Descomprime os resultados brutos (.json.xz) para ./dados_json/ (ignorado pelo git). Uso: bash descomprimir.sh
cd "$(dirname "$0")"
mkdir -p dados_json
for f in dados/*.json.xz; do
  xz -dkc "$f" > "dados_json/$(basename "${f%.xz}")"
done
echo "$(ls dados_json | wc -l) arquivos em $(pwd)/dados_json"

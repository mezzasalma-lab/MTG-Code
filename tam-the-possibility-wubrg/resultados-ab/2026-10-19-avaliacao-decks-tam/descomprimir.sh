#!/bin/bash
# Descomprime os dados brutos (.json.xz e .jsonl.xz) para ./dados_json/ (ignorado pelo git). Uso: bash descomprimir.sh
cd "$(dirname "$0")"
mkdir -p dados_json
for f in dados/*.xz; do
  b=$(basename "$f"); xz -dkc "$f" > "dados_json/${b%.xz}"
done
echo "$(ls dados_json | wc -l) arquivos em $(pwd)/dados_json"

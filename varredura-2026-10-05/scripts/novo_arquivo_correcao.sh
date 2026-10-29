#!/bin/bash
# Cria a pasta de arquivo (Regra #8) de uma correcao de simulador, a partir do harness generico (driver.py/abgen.py/verificar_reproducao.sh/descomprimir.sh/indice_dados.py)
# da pasta modelo `toph-naya/resultados-ab/2026-10-05-terreno-virado-primeiro`. Uso (da raiz do repositorio):
#   bash varredura-2026-10-05/scripts/novo_arquivo_correcao.sh <deck> <simulador.py> <AAAA-MM-DD-tema> <hash-do-commit-ANTES> <config.json>
# O snapshot "ANTES" e' o arquivo como esta' no commit indicado (git show); o `config.json` e' escrito pelo chamador (flags_off, ignora_campos, destaque).
set -e
DECK="$1"; SIM="$2"; TEMA="$3"; HASH="$4"; CFG="$5"
MODELO="toph-naya/resultados-ab/2026-10-05-terreno-virado-primeiro"
HARNESS="prismatic-bridge-wurbg/resultados-ab/2026-10-05-terreno-virado-primeiro/orquestracao"   # driver.py/abgen.py CORRIGIDOS: contam a biblioteca de simuladores baseados em dict (sem BASE_LIBRARY) e limitam inteiros astronomicos na media
DEST="$DECK/resultados-ab/$TEMA"
mkdir -p "$DEST"/{codigo,dados,orquestracao,resumos}
cp "$HARNESS/driver.py" "$HARNESS/abgen.py" "$DEST/orquestracao/"
cp "$MODELO/orquestracao/verificar_reproducao.sh" "$DEST/orquestracao/"
cp "$MODELO/descomprimir.sh" "$MODELO/indice_dados.py" "$DEST/"
cp "$CFG" "$DEST/orquestracao/config.json"
git show "$HASH:$DECK/$SIM" > "$DEST/codigo/${SIM%.py}_ANTES_$HASH.py"
printf 'dados_json/\n__pycache__/\n' > "$DEST/.gitignore"
echo "criado $DEST (snapshot ${SIM%.py}_ANTES_$HASH.py)"

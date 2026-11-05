#!/bin/bash
# Refaz as tabelas da calibracao e compara byte a byte (cmp) com as arquivadas. Usa o simulador VIVO (tam_goldfish_v1.py da pasta do deck): se ele mudou desde 2026-10-22, as saidas deixam de bater.
# Uso: bash verificar_reproducao.sh          (taxas, rapido)          |   bash verificar_reproducao.sh --tudo   (tambem refaz o ajuste e os replays; ~15 min)
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$tmp/$1" "../resumos/$1"; then echo "IGUAL  $1"; ok=$((ok+1)); else echo "DIFERE $1"; fi; }
PYTHONHASHSEED=0 python3 taxas_observadas.py > "$tmp/taxas_observadas.md"; cmpf taxas_observadas.md
if [ "$1" == "--tudo" ]; then
  OUT="$tmp" bash roda_calibracao.sh
  for f in ajuste_perfil_default.txt ajuste_perfil_playtester.txt; do cmpf $f; done
  for j in 3 4 5; do for v in padrao resiliencia_default resiliencia_playtester padrao_playtester; do cmpf replay_jogo${j}_${v}.txt; done; done
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

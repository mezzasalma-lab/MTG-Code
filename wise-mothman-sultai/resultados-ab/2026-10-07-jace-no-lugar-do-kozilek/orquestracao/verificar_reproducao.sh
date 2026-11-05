#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) `resumos/tabela_final.md` refeito SO' dos .json.xz;
#  --tudo      tambem RE-EXECUTA o lote 1 do A/B (N = 10.000, base + 5 variantes x 2 modos, ~25 min) numa pasta temporaria e compara os brutos descomprimidos
#              (os brutos do lote 1 sao os que contem o Kozilek -> Jace; o lote 2 usa o mesmo codigo e o mesmo driver).
# NAO edite o simulador enquanto roda (re-simula o arquivo VIVO).
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
total=$((total+1)); python3 rank_final.py > "$tmp/tabela_final.md"
if cmp -s "$tmp/tabela_final.md" ../resumos/tabela_final.md; then echo "IGUAL  tabela_final.md (refeita so' dos brutos)"; ok=$((ok+1)); else echo "DIFERE tabela_final.md"; fi
if [ "$1" == "--tudo" ]; then
  echo "re-simulando o lote 1 inteiro (sem editar o simulador!)..."
  mkdir -p "$tmp/o"
  DRIVER_OUT="$tmp/o" LOTES=10000 TAG=final_1 PYTHONHASHSEED=0 python3 driver_mm.py config_final_1.json ab > "$tmp/o/log.txt" 2>&1
  for r in raw_final_1_10000 raw_final_1_10000_resiliencia; do
    total=$((total+1))
    if [ -f "$tmp/o/dados/$r.json.xz" ] && cmp -s <(xz -dc "$tmp/o/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi
  done
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

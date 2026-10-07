#!/bin/bash
# Refaz a tabela dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) `resumos/muldrotha.md` refeito SO' dos .json.xz;
#  --tudo      tambem RE-EXECUTA a medicao inteira (10.000 x 2 modos x 2 variantes, ~7 min) numa pasta temporaria e compara os brutos descomprimidos e `recasts_por_nome.json`.
# NAO edite o simulador enquanto roda (re-simula o arquivo VIVO).
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
total=$((total+1)); python3 resume_muldrotha.py > "$tmp/muldrotha.md"
if cmp -s "$tmp/muldrotha.md" ../resumos/muldrotha.md; then echo "IGUAL  muldrotha.md (refeito so' dos brutos)"; ok=$((ok+1)); else echo "DIFERE muldrotha.md"; fi
if [ "$1" == "--tudo" ]; then
  MEDIDA_OUT="$tmp" python3 mede_muldrotha.py > /dev/null
  for r in raw_muldrotha_10000 raw_muldrotha_10000_resiliencia; do
    total=$((total+1))
    if cmp -s <(xz -dc "$tmp/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi
  done
  total=$((total+1))
  if cmp -s "$tmp/dados/recasts_por_nome.json" ../dados/recasts_por_nome.json; then echo "IGUAL  recasts_por_nome.json (re-simulado)"; ok=$((ok+1)); else echo "DIFERE recasts_por_nome.json"; fi
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) tabelas do A/B (driver_mm.py sum, compacto) + resumo_guarda.md;
#  --tudo      tambem RE-EXECUTA o lote de 2000 (tabelas e brutos .json.xz IDENTICOS aos arquivados). NAO re-executa o lote de 10.000 nem a regressao de 20.000 (saidas das execucoes originais).
# NAO edite o simulador enquanto roda (re-simula o arquivo VIVO).
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL  $1$2"; ok=$((ok+1)); else echo "DIFERE $1$2"; fi; }
DRIVER_OUT="$tmp" python3 driver_mm.py config.json sum > /dev/null
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt compacto_2000.txt compacto_10000.txt compacto_2000_resiliencia.txt compacto_10000_resiliencia.txt; do cmpf $f; done
python3 resumo_guarda.py > "$tmp/resumos/resumo_guarda.md"; cmpf resumo_guarda.md
if [ "$1" == "--tudo" ]; then
  LOTES=2000 DRIVER_OUT="$tmp" python3 driver_mm.py config.json ab > /dev/null
  for f in ab_2000.txt ab_2000_resiliencia.txt; do
    cmpf $f " (re-execucao)"
    r="raw_${f%.txt}"; total=$((total+1))
    if cmp -s <(xz -dc "$tmp/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi
  done
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

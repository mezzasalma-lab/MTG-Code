#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte (cmp) com os resumos salvos.
# Uso (de qualquer pasta):  bash verificar_reproducao.sh          -> so' as tabelas do A/B (de `driver_mm.py sum`, rapido)
#                           bash verificar_reproducao.sh --tudo   -> tambem RE-EXECUTA o lote de 2000 (pasta temporaria; o bruto re-simulado tem que ser IDENTICO ao arquivado)
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL  $1$2"; ok=$((ok+1)); else echo "DIFERE $1$2"; fi; }
DRIVER_OUT="$tmp" python3 driver_mm.py config.json sum > /dev/null
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt compacto_2000.txt compacto_10000.txt compacto_2000_resiliencia.txt compacto_10000_resiliencia.txt; do cmpf $f; done
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

#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) tabelas do A/B (driver_mm.py sum) + bit-identidade rapida (N=300 x 2 modos);
#  --tudo      tambem RE-EXECUTA o lote de 2000 (bruto re-simulado IDENTICO ao arquivado) e a regressao de 2.000 (nao e' a de 20.000: essa levou ~10 min e esta' em resumos/regressao_20000.txt).
# NAO edite o simulador enquanto roda.
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL  $1$2"; ok=$((ok+1)); else echo "DIFERE $1$2"; fi; }
DRIVER_OUT="$tmp" python3 driver_mm.py config.json sum > /dev/null
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt compacto_2000.txt compacto_10000.txt compacto_2000_resiliencia.txt compacto_10000_resiliencia.txt; do cmpf $f; done
total=$((total+1)); if python3 bitident.py 300 > "$tmp/bitident.txt" 2>&1; then echo "IGUAL  bitident.py 300: $(tail -1 "$tmp/bitident.txt" | cut -c1-200)"; ok=$((ok+1)); else echo "DIFERE bitident.py"; tail -3 "$tmp/bitident.txt"; fi
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

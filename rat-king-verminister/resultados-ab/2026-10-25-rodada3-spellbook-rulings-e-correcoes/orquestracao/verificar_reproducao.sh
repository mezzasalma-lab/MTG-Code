#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte (cmp) com os resumos salvos.
# Uso (de qualquer pasta):  bash verificar_reproducao.sh          -> so' as tabelas do A/B (de `driver.py sum`, rapido)
#                           bash verificar_reproducao.sh --tudo   -> tambem RE-EXECUTA smoke, bit-identidade, regressao e os 4 lotes do A/B (pasta temporaria; os brutos re-simulados
#                                                                    tem que ser IDENTICOS aos arquivados)
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL  $1$2"; ok=$((ok+1)); else echo "DIFERE $1$2"; fi; }
DRIVER_OUT="$tmp" python3 driver.py config.json sum > /dev/null
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do cmpf $f; done
# tabelas derivadas SO' dos brutos arquivados
python3 -I resumo_variantes.py ../dados/raw_ab_10000 ../dados/raw_ab_10000_resiliencia > "$tmp/resumos/resumo_variantes_10000.md"; cmpf resumo_variantes_10000.md
python3 -I resumo_novos.py ../dados/raw_ab_10000 ../dados/raw_ab_10000_resiliencia > "$tmp/resumos/resumo_novos_10000.txt"; cmpf resumo_novos_10000.txt
if [ "$1" == "--tudo" ]; then
  # o arquivo vivo tem de ser o mesmo que o A/B usou (NAO editar o simulador enquanto isto roda)
  total=$((total+1)); if cmp -s ../../../ratking_goldfish_v1.py ../codigo/ratking_goldfish_v1_DEPOIS.py; then echo "IGUAL  ratking_goldfish_v1.py == codigo/ratking_goldfish_v1_DEPOIS.py"; ok=$((ok+1)); else echo "DIFERE ratking_goldfish_v1.py (o vivo mudou depois do A/B)"; fi
  for etapa in smoke bitid ghost reg; do DRIVER_OUT="$tmp" python3 driver.py config.json $etapa > /dev/null; done
  cmpf smoke.txt; cmpf bitident_20000.txt; [ -f ../resumos/ghost_20000.txt ] && cmpf ghost_20000.txt; cmpf regressao_20000.txt
  DRIVER_OUT="$tmp" python3 driver.py config.json ab > /dev/null
  for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do
    cmpf $f " (re-execucao)"
    r="raw_${f%.txt}"; total=$((total+1))
    if cmp -s <(xz -dc "$tmp/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi
  done
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

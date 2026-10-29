#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte (cmp) com os resumos salvos.
# Uso (de qualquer pasta):  bash verificar_reproducao.sh          -> so' as tabelas derivadas dos brutos (rapido)
#                           bash verificar_reproducao.sh --tudo   -> tambem RE-EXECUTA smoke, bit-identidade, ghost, regressao, testes dirigidos, prova de nao-vacuidade do ghost e os 4 lotes do A/B
#                                                                    (pasta temporaria; os brutos re-simulados tem que ser IDENTICOS aos arquivados). NAO editar o simulador enquanto roda.
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d); mkdir -p "$tmp/resumos"
cmpf() { total=$((total+1)); if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL  $1$2"; ok=$((ok+1)); else echo "DIFERE $1$2"; fi; }
DRIVER_OUT="$tmp" python3 driver.py config.json sum > /dev/null
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do cmpf $f; done
# tabelas derivadas SO' dos brutos arquivados
python3 -I resumo_variantes.py ../dados/raw_ab_10000 ../dados/raw_ab_10000_resiliencia > "$tmp/resumos/resumo_variantes_10000.md"; cmpf resumo_variantes_10000.md
python3 -I diferem_entre_variantes.py ../dados > "$tmp/resumos/diferem_entre_variantes.txt"; cmpf diferem_entre_variantes.txt
python3 -I combos_antes_depois.py ../dados > "$tmp/resumos/combos_antes_depois.txt"; cmpf combos_antes_depois.txt
if [ "$1" == "--tudo" ]; then
  # o arquivo vivo tem de ser o mesmo que o A/B usou
  total=$((total+1)); if cmp -s ../../../ratking_goldfish_v1.py ../codigo/ratking_goldfish_v1_DEPOIS.py; then echo "IGUAL  ratking_goldfish_v1.py == codigo/ratking_goldfish_v1_DEPOIS.py"; ok=$((ok+1)); else echo "DIFERE ratking_goldfish_v1.py (o vivo mudou depois do A/B)"; fi
  for etapa in smoke bitid ghost reg; do DRIVER_OUT="$tmp" python3 driver.py config.json $etapa > /dev/null; done
  cmpf smoke.txt; cmpf bitident_20000.txt; cmpf ghost_20000.txt; cmpf regressao_20000.txt
  PYTHONHASHSEED=0 python3 -I testes_dirigidos.py config.json > "$tmp/resumos/testes_dirigidos.txt" 2>&1; cmpf testes_dirigidos.txt
  PYTHONHASHSEED=0 python3 -I ghost_vacuidade.py config.json > "$tmp/resumos/ghost_vacuidade.txt" 2>&1; cmpf ghost_vacuidade.txt
  DRIVER_OUT="$tmp" python3 driver.py config.json ab > /dev/null
  for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do
    cmpf $f " (re-execucao)"
    r="raw_${f%.txt}"; total=$((total+1))
    if cmp -s <(xz -dc "$tmp/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi
  done
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

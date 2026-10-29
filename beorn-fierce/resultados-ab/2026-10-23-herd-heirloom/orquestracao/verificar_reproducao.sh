#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte (cmp) com os resumos salvos.
# Uso (de qualquer pasta):  bash verificar_reproducao.sh          -> so' as tabelas (A/B de `driver.py sum`, comparacoes entre variantes, resumos descritivos, indice, Spellbook-resumo)
#                           bash verificar_reproducao.sh --tudo   -> tambem RE-EXECUTA smoke, bit-identidade, regressao e os 4 lotes do A/B numa pasta temporaria (os brutos re-simulados tem que ser IDENTICOS
#                                                                    aos arquivados). Nao edite `codigo/beorn_goldfish_v1_DEPOIS.py` nem o `config.json` enquanto roda.
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL  $1$2"; ok=$((ok+1)); else echo "DIFERE $1$2"; fi; }
DRIVER_OUT="$tmp" python3 driver.py config.json sum > /dev/null
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do cmpf $f; done
mkdir -p "$tmp/resumos"
python3 comparacoes.py 10000 > "$tmp/resumos/comparacoes_entre_variantes_10000.txt"; cmpf comparacoes_entre_variantes_10000.txt
for v in antes depois so_gatilho_beorn; do python3 resumo_descritivo.py $v 10000 > "$tmp/resumos/resumo_descritivo_${v}_10000.txt"; cmpf resumo_descritivo_${v}_10000.txt; done
python3 enumera_condicoes.py ../codigo/lista_ANTES.md /home/user/MTG-Code/scryfall-cache/oracle-cache.json > "$tmp/resumos/enumera_condicoes_lista_antes.txt"; cmpf enumera_condicoes_lista_antes.txt
(cd .. && python3 indice_dados.py) > "$tmp/resumos/indice_dados.md"; cmpf indice_dados.md
if [ "$1" == "--tudo" ]; then
  for etapa in smoke bitid reg; do DRIVER_OUT="$tmp" python3 driver.py config.json $etapa > /dev/null; done
  cmpf smoke.txt; cmpf bitident_20000.txt; cmpf regressao_20000.txt
  DRIVER_OUT="$tmp" python3 driver.py config.json ab > /dev/null
  for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do
    cmpf $f " (re-execucao)"
    r="raw_${f%.txt}"; total=$((total+1))
    if cmp -s <(xz -dc "$tmp/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi
  done
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte (cmp) com os resumos salvos.
# Uso (de qualquer pasta):  bash verificar_reproducao.sh          -> so' as tabelas (A/B de `driver.py sum`, resumos descritivos, extras, comparacoes entre variantes e indice; rapido)
#                           bash verificar_reproducao.sh --tudo   -> tambem RE-EXECUTA smoke, bit-identidade, regressao e os 4 lotes do A/B (pasta temporaria; os brutos re-simulados
#                                                                    tem que ser IDENTICOS aos arquivados; ~2 h; nao mude o `config.json` nem edite o simulador em `codigo/`)
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL  $1$2"; ok=$((ok+1)); else echo "DIFERE $1$2"; fi; }
DRIVER_OUT="$tmp" python3 driver.py config.json sum > /dev/null
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do cmpf $f; done
mkdir -p "$tmp/resumos"
for v in depois perfil_playtester; do
  python3 resumo_variante.py $v 10000 > "$tmp/resumos/resumo_descritivo_${v}_10000.txt"; cmpf resumo_descritivo_${v}_10000.txt
  python3 resumo_extra_variante.py $v 10000 > "$tmp/resumos/resumo_extra_${v}_10000.txt"; cmpf resumo_extra_${v}_10000.txt
done
python3 comparacoes.py > "$tmp/resumos/comparacoes_entre_variantes.txt"; cmpf comparacoes_entre_variantes.txt
(cd .. && python3 indice_dados.py) > "$tmp/resumos/indice_dados.md"; cmpf indice_dados.md
if [ "$1" == "--tudo" ]; then
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

#!/bin/bash
# Verificacao de reprodutibilidade (Regra #8) da pasta `<deck>/resultados-ab/2026-10-07-landfall-payoff-primeiro/`. Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) refaz as tabelas do A/B SO' dos brutos `.json.xz` (`driver.py sum`) e compara byte a byte (cmp) com os resumos arquivados (segundos);
#  --tudo      tambem RE-EXECUTA, numa pasta temporaria, o smoke (compara com cmp), o lote de 2.000 do A/B (tabelas e brutos `.json.xz` descomprimidos IDENTICOS aos arquivados), a bit-identidade (N=2.000 x 2 modos) e a
#              regressao (N=2.000, 0 excecoes). NAO re-executa os lotes de 10.000 (so' as tabelas a partir do bruto), a bit-identidade/regressao de 20.000 (saidas das execucoes originais) nem o determinismo.
# NAO edite o simulador enquanto roda (re-simula o arquivo VIVO).
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL  $1$2"; ok=$((ok+1)); else echo "DIFERE $1$2"; fi; }
DRIVER_OUT="$tmp" python3 driver.py config.json sum > /dev/null
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do cmpf $f; done
if [ "$1" == "--tudo" ]; then
  DRIVER_OUT="$tmp" python3 driver.py config.json smoke > /dev/null; cmpf smoke.txt " (re-execucao)"
  LOTES=2000 DRIVER_OUT="$tmp" python3 driver.py config.json ab > /dev/null
  for f in ab_2000.txt ab_2000_resiliencia.txt; do
    cmpf $f " (re-execucao)"
    r="raw_${f%.txt}"; total=$((total+1))
    if cmp -s <(xz -dc "$tmp/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi
  done
  DRIVER_OUT="$tmp" python3 driver.py config.json bitid 2000 > /dev/null; total=$((total+1))
  if [ "$(grep -c 'BIT-IDENTICO' "$tmp/resumos/bitident_2000.txt")" == "2" ]; then echo "IGUAL  bitident_2000.txt (chave desligada == snapshot, 2 modos)"; ok=$((ok+1)); else echo "DIFERE bitident_2000.txt"; fi
  DRIVER_OUT="$tmp" python3 driver.py config.json reg 0 2000 > /dev/null; total=$((total+1))
  if [ "$(grep -c 'excecoes=0 ' "$tmp/resumos/regressao_2000.txt")" == "4" ]; then echo "IGUAL  regressao_2000.txt (4 configuracoes x modos, 0 excecoes)"; ok=$((ok+1)); else echo "DIFERE regressao_2000.txt"; fi
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

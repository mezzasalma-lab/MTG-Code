#!/bin/bash
# Refaz as saidas a partir dos brutos arquivados e compara byte a byte (cmp) com os resumos salvos.
# Uso:  bash verificar_reproducao.sh          -> so' as tabelas derivadas dos brutos (rapido)
#       bash verificar_reproducao.sh --tudo   -> tambem RE-EXECUTA a medicao de mortes/potencial (8 s) e o A/B inteiro (~3 min; os brutos re-simulados tem que ser IDENTICOS). NAO editar o simulador enquanto roda.
# O Spellbook (API externa) NAO e' re-executado: so' o bruto da resposta esta arquivado (dados/spellbook_br_raw_2026-11-04.json.xz).
cd "$(dirname "$0")"
ok=0; total=0; tmp=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; fi; }
mkdir -p "$tmp/t"; python3 -I refaz_tabelas.py ../dados "$tmp/t"
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do cmpf "$tmp/t/$f" "../resumos/$f" "$f"; done
python3 -I resumo_br.py ../dados > "$tmp/r.md"; cmpf "$tmp/r.md" ../resumos/resumo_ab_10000.md resumo_ab_10000.md
if [ "$1" == "--tudo" ]; then
  total=$((total+1)); if cmp -s ../../../edgar_markov_goldfish_v1.py ../codigo/edgar_markov_goldfish_v1_VIVO_2026-11-04.py; then echo "IGUAL  edgar_markov_goldfish_v1.py == codigo/..._VIVO_2026-11-04.py"; ok=$((ok+1)); else echo "DIFERE edgar_markov_goldfish_v1.py (o vivo mudou depois do A/B)"; fi
  PYTHONHASHSEED=0 python3 -I medir_mortes_e_potencial.py 10000 > "$tmp/m.txt" 2>&1; cmpf "$tmp/m.txt" ../resumos/mortes_e_potencial_10000.txt mortes_e_potencial_10000.txt
  mkdir -p "$tmp/novo"
  echo "(re-simulando o A/B inteiro...)"; AB_OUT="$tmp/novo" PYTHONHASHSEED=0 python3 -I ab_br.py > "$tmp/ab.log" 2>&1
  for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do cmpf "$tmp/novo/resumos/$f" "../resumos/$f" "$f (re-execucao)"; done
  for r in raw_ab_2000 raw_ab_10000 raw_ab_2000_resiliencia raw_ab_10000_resiliencia; do total=$((total+1)); if cmp -s <(xz -dc "$tmp/novo/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi; done
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

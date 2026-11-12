#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) refaz SO' dos .json.xz: resumos/rank_triagem.txt, resumos/tabela_final.md, resumos/condicional.txt, resumos/resumo_spellbook.md e resumos/diff_listas.md (diff_listas.py le lista.md e o cache);
#  --tudo      tambem RE-EXECUTA a triagem do lote de 2.000 (43 variantes x 2 modos, ~35 min) com o simulador CONGELADO `codigo/mothman_goldfish_v1_HM_triagem.py` numa pasta temporaria e compara os brutos.
# NAO edite codigo/ enquanto roda.
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d)
cmpf () { total=$((total+1)); if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; fi; }
python3 rank_triagem.py 2000 triagem > "$tmp/rank_triagem.txt";   cmpf "$tmp/rank_triagem.txt" ../resumos/rank_triagem.txt "rank_triagem.txt (refeito so' dos brutos)"
python3 rank_final.py > "$tmp/tabela_final.md";                    cmpf "$tmp/tabela_final.md" ../resumos/tabela_final.md "tabela_final.md (refeita so' dos brutos)"
python3 condicional.py > "$tmp/condicional.txt";                    cmpf "$tmp/condicional.txt" ../resumos/condicional.txt "condicional.txt (refeito so' dos brutos)"
python3 resumo_spellbook.py > "$tmp/resumo_spellbook.md";           cmpf "$tmp/resumo_spellbook.md" ../resumos/resumo_spellbook.md "resumo_spellbook.md (refeito so' do JSON da API)"
if [ "$1" == "--tudo" ]; then
  echo "re-simulando a triagem inteira com o simulador congelado (sem editar codigo/!)..."
  mkdir -p "$tmp/o"
  python3 - <<PY
import json
c = json.load(open("config_triagem.json")); c["sim"] = "resultados-ab/2026-10-07-comparacao-stefano/codigo/mothman_goldfish_v1_HM_triagem.py"
json.dump(c, open("$tmp/config_triagem_congelada.json", "w"))
PY
  DRIVER_OUT="$tmp/o" LOTES=2000 TAG=triagem PYTHONHASHSEED=0 python3 driver_mm.py "$tmp/config_triagem_congelada.json" ab > "$tmp/o/log.txt" 2>&1
  for r in raw_triagem_2000 raw_triagem_2000_resiliencia; do
    total=$((total+1))
    if [ -f "$tmp/o/dados/$r.json.xz" ] && cmp -s <(xz -dc "$tmp/o/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi
  done
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"

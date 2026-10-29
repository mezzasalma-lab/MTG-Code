#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) refaz SO' dos .json.xz: tabela_cinco.md, conjuntos_entre_si.md, castabilidade.md, replicacao.txt e indice_dados.md;
#  --tudo      tambem RE-EXECUTA, com o simulador CONGELADO `codigo/mothman_goldfish_v1_DEPOIS.py`, base e s4 (sementes 3.000.000..3.000.999, 2 modos) e compara partida a partida com o bruto.
cd "$(dirname "$0")"
ok=0; total=0; tmp=$(mktemp -d)
cmpf () { total=$((total+1)); if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; fi; }
python3 rank_cinco.py > "$tmp/t.md";          cmpf "$tmp/t.md" ../resumos/tabela_cinco.md "tabela_cinco.md (refeita so' dos brutos)"
python3 compara_conjuntos.py > "$tmp/p.md";   cmpf "$tmp/p.md" ../resumos/conjuntos_entre_si.md "conjuntos_entre_si.md (refeito so' dos brutos)"
python3 resumo_cast.py > "$tmp/c.md";         cmpf "$tmp/c.md" ../resumos/castabilidade.md "castabilidade.md (refeito so' dos brutos)"
python3 confere_replicacao.py > "$tmp/r.txt"; cmpf "$tmp/r.txt" ../resumos/replicacao.txt "replicacao.txt (refeito so' dos brutos)"
(cd .. && python3 indice_dados.py > "$tmp/i.md"); cmpf "$tmp/i.md" ../resumos/indice_dados.md "indice_dados.md (refeito so' dos brutos)"
if [ "$1" == "--tudo" ]; then
  echo "re-simulando base e s4 (1.000 sementes x 2 modos) com o simulador congelado..."
  total=$((total+1))
  if PYTHONHASHSEED=0 python3 resimula_amostra.py; then echo "IGUAL  amostra re-simulada == bruto (4/4 series)"; ok=$((ok+1)); else echo "DIFERE amostra re-simulada"; fi
fi
rm -rf "$tmp"
echo "$ok/$total saidas iguais"

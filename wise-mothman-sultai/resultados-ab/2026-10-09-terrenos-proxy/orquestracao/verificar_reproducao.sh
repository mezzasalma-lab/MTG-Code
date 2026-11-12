#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) refaz SO' dos .json.xz: tabela_x.md (terrenos3), tabela_y.md (cmd50), tabela_z.md (terrenos4), tabela_z50.md (z50), base_aplicada.md, replicacao.txt e indice_dados.md;
#  --tudo      tambem RE-EXECUTA, com o simulador CONGELADO `codigo/mothman_goldfish_v1_DEPOIS.py`, base e d1 (sementes 3.000.000..3.000.999; padrao + resiliencia; e resiliencia com comandante-alvo 0.5) e compara partida a partida com o bruto.
cd "$(dirname "$0")"
ok=0; total=0; tmp=$(mktemp -d)
cmpf () { total=$((total+1)); if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; fi; }
python3 rank_proxy.py terrenos3 > "$tmp/x.md";  cmpf "$tmp/x.md" ../resumos/tabela_x.md   "tabela_x.md (refeita so' dos brutos)"
python3 rank_proxy.py cmd50 > "$tmp/y.md";      cmpf "$tmp/y.md" ../resumos/tabela_y.md   "tabela_y.md (refeita so' dos brutos)"
python3 rank_proxy.py terrenos4 > "$tmp/z.md";  cmpf "$tmp/z.md" ../resumos/tabela_z.md   "tabela_z.md (refeita so' dos brutos)"
python3 rank_proxy.py z50 > "$tmp/z50.md";      cmpf "$tmp/z50.md" ../resumos/tabela_z50.md "tabela_z50.md (refeita so' dos brutos)"
python3 base_aplicada.py > "$tmp/b.md";        cmpf "$tmp/b.md" ../resumos/base_aplicada.md "base_aplicada.md (refeita so' dos brutos)"
python3 confere_replicacao.py > "$tmp/r.txt";   cmpf "$tmp/r.txt" ../resumos/replicacao.txt "replicacao.txt (refeito so' dos brutos)"
(cd .. && python3 indice_dados.py > "$tmp/i.md"); cmpf "$tmp/i.md" ../resumos/indice_dados.md "indice_dados.md (refeito so' dos brutos)"
if [ "$1" == "--tudo" ]; then
  echo "re-simulando base e d1 (1.000 sementes) com o simulador congelado..."
  total=$((total+1))
  if PYTHONHASHSEED=0 python3 resimula_amostra.py; then echo "IGUAL  amostra re-simulada == bruto (6/6 series)"; ok=$((ok+1)); else echo "DIFERE amostra re-simulada"; fi
fi
rm -rf "$tmp"
echo "$ok/$total saidas iguais"

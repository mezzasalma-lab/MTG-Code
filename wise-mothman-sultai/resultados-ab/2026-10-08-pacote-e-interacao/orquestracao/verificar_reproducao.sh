#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) refaz SO' dos .json.xz: tabela_pacote.md, pacotes_entre_si.md, gy_oponentes.md, replicacao.txt e indice_dados.md;
#  --tudo      tambem RE-EXECUTA, com o simulador CONGELADO `codigo/mothman_goldfish_v1_estado_2026-10-08.py`, base e p1_offer_negate (sementes 3.000.000..3.000.999, 2 modos) e compara partida a partida com o bruto.
cd "$(dirname "$0")"
ok=0; total=0; tmp=$(mktemp -d)
cmpf () { total=$((total+1)); if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; fi; }
python3 rank_pacote.py > "$tmp/t.md";            cmpf "$tmp/t.md" ../resumos/tabela_pacote.md "tabela_pacote.md (refeita so' dos brutos)"
python3 compara_pares.py > "$tmp/p.md";          cmpf "$tmp/p.md" ../resumos/pacotes_entre_si.md "pacotes_entre_si.md (refeito so' dos brutos)"
python3 resumo_gy.py > "$tmp/g.md";              cmpf "$tmp/g.md" ../resumos/gy_oponentes.md "gy_oponentes.md (refeito so' dos brutos)"
python3 confere_replicacao.py > "$tmp/r.txt";    cmpf "$tmp/r.txt" ../resumos/replicacao.txt "replicacao.txt (refeito so' dos brutos)"
(cd .. && python3 indice_dados.py > "$tmp/i.md"); cmpf "$tmp/i.md" ../resumos/indice_dados.md "indice_dados.md (refeito so' dos brutos)"
if [ "$1" == "--tudo" ]; then
  echo "re-simulando base e p1 (1.000 sementes x 2 modos) com o simulador congelado..."
  total=$((total+1))
  if PYTHONHASHSEED=0 python3 resimula_amostra.py; then echo "IGUAL  amostra re-simulada == bruto (4/4 series)"; ok=$((ok+1)); else echo "DIFERE amostra re-simulada"; fi
fi
rm -rf "$tmp"
echo "$ok/$total saidas iguais"

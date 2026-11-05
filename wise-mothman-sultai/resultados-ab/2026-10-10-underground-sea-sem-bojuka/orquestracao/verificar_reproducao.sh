#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) refaz SO' dos .json.xz: tabela_u.md (under), tabela_u2.md (under2), pares_diretos.md, replicacao.txt e indice_dados.md, e refaz fontes_por_cor.md do simulador congelado;
#  --tudo      tambem RE-EXECUTA, com o simulador CONGELADO `codigo/mothman_goldfish_v1_ANTES.py`, base, u1, u3 e u8 (sementes 3.000.000..3.000.999; 2 modos) e compara partida a partida com o bruto.
cd "$(dirname "$0")"
ok=0; total=0; tmp=$(mktemp -d)
cmpf () { total=$((total+1)); if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; fi; }
python3 rank_proxy.py under > "$tmp/u.md";        cmpf "$tmp/u.md" ../resumos/tabela_u.md "tabela_u.md (refeita so' dos brutos)"
python3 rank_proxy.py under2 > "$tmp/u2.md";      cmpf "$tmp/u2.md" ../resumos/tabela_u2.md "tabela_u2.md (refeita so' dos brutos)"
python3 compara_candidatos.py > "$tmp/p.md";      cmpf "$tmp/p.md" ../resumos/pares_diretos.md "pares_diretos.md (refeito so' dos brutos)"
python3 fontes_por_cor.py > "$tmp/f.md";          cmpf "$tmp/f.md" ../resumos/fontes_por_cor.md "fontes_por_cor.md (refeito do simulador congelado)"
python3 confere_replicacao.py > "$tmp/r.txt";     cmpf "$tmp/r.txt" ../resumos/replicacao.txt "replicacao.txt (refeito so' dos brutos)"
(cd .. && python3 indice_dados.py > "$tmp/i.md"); cmpf "$tmp/i.md" ../resumos/indice_dados.md "indice_dados.md (refeito so' dos brutos)"
if [ "$1" == "--tudo" ]; then
  echo "re-simulando base, u1, u3 e u8 (1.000 sementes x 2 modos) com o simulador congelado..."
  total=$((total+1))
  if PYTHONHASHSEED=0 python3 resimula_amostra.py; then echo "IGUAL  amostra re-simulada == bruto (8/8 series)"; ok=$((ok+1)); else echo "DIFERE amostra re-simulada"; fi
fi
rm -rf "$tmp"
echo "$ok/$total saidas iguais"

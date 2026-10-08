#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) refaz SO' dos .json.xz: tabela_terrenos.md, tabela_terrenos2.md, terrenos_entre_si.md, comandante_e_cores.md, tipos_de_terreno.md, replicacao.txt, analise_terrenos.md e indice_dados.md;
#  --tudo      tambem RE-EXECUTA base e t3 (1.000 sementes x 2 modos) com o simulador CONGELADO e compara partida a partida com o bruto.
cd "$(dirname "$0")"
ok=0; total=0; tmp=$(mktemp -d)
cmpf () { total=$((total+1)); if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; fi; }
python3 rank_terrenos.py terrenos > "$tmp/a.md";   cmpf "$tmp/a.md" ../resumos/tabela_terrenos.md "tabela_terrenos.md (refeita so' dos brutos)"
python3 rank_terrenos.py terrenos2 > "$tmp/b.md";  cmpf "$tmp/b.md" ../resumos/tabela_terrenos2.md "tabela_terrenos2.md (refeita so' dos brutos)"
python3 compara_terrenos.py > "$tmp/c.md";         cmpf "$tmp/c.md" ../resumos/terrenos_entre_si.md "terrenos_entre_si.md (refeito so' dos brutos)"
python3 resumo_cmd_cor.py > "$tmp/d.md";           cmpf "$tmp/d.md" ../resumos/comandante_e_cores.md "comandante_e_cores.md (refeito so' dos brutos)"
python3 resumo_tipos.py > "$tmp/e.md";             cmpf "$tmp/e.md" ../resumos/tipos_de_terreno.md "tipos_de_terreno.md (refeito so' dos brutos)"
python3 confere_replicacao.py > "$tmp/f.txt";      cmpf "$tmp/f.txt" ../resumos/replicacao.txt "replicacao.txt (refeito so' dos brutos)"
python3 analise_terrenos.py > "$tmp/g.md";         cmpf "$tmp/g.md" ../resumos/analise_terrenos.md "analise_terrenos.md (refeita do simulador vivo)"
(cd .. && python3 indice_dados.py > "$tmp/h.md");  cmpf "$tmp/h.md" ../resumos/indice_dados.md "indice_dados.md (refeito so' dos brutos)"
if [ "$1" == "--tudo" ]; then
  echo "re-simulando base e t3 (1.000 sementes x 2 modos) com o simulador congelado..."
  total=$((total+1))
  if PYTHONHASHSEED=0 python3 resimula_amostra.py; then echo "IGUAL  amostra re-simulada == bruto (4/4 series)"; ok=$((ok+1)); else echo "DIFERE amostra re-simulada"; fi
fi
rm -rf "$tmp"
echo "$ok/$total saidas iguais"

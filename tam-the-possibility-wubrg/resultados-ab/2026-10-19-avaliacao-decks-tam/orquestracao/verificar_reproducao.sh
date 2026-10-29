#!/bin/bash
# Refaz as saidas que dependem so' dos dados arquivados (+ lista.md e scryfall-cache/oracle-cache.json do repositorio) e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh
#  Refeitos offline (5): comparacao_estrutural.md, decks_parecidos.md, inclusao_cartas.md, pacote_efeitos.md, indice_dados.md.
#  Se lista.md do deck mudar (troca aplicada), as 4 primeiras mudam de proposito: refazer e arquivar de novo.
#  NAO refeitos offline (consultam APIs ao vivo; o bruto da resposta esta' em dados/): coleta_edhrec.py (EDHREC), oraculos_referencia.py (Scryfall), csb_adicoes.py / csb_trocas.py / csb_carth_detalhe.py (Spellbook), rulings_candidatas.py (Scryfall).
cd "$(dirname "$0")"
export PYTHONHASHSEED=${PYTHONHASHSEED:-0}
ok=0; total=0; tmp=$(mktemp -d)
cmpf () { total=$((total+1)); if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; fi; }
for s in comparacao_estrutural decks_parecidos inclusao_cartas pacote_efeitos indice_dados; do
  python3 "$s.py" > "$tmp/$s.md"; cmpf "$tmp/$s.md" "../resumos/$s.md" "$s.md (refeito so' dos dados arquivados)"
done
rm -rf "$tmp" __pycache__
echo "$ok/$total saidas iguais"

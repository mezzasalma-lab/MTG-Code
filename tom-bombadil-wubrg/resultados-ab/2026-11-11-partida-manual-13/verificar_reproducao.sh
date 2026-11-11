#!/bin/bash
# Refaz, a partir dos .xz de dados/, cada saída arquivada em resumos/ e compara com `cmp`; confere os .xz e o SHA256SUMS.
# NÃO compara resumos/rulings_scryfall.json (vem da API do Scryfall ao vivo: não reproduz por construção).
# Uso: bash verificar_reproducao.sh   (de qualquer pasta). Sai com 1 se alguma comparação falhar.
cd "$(dirname "$0")" || exit 2
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
ok=0; ruim=0
cmpf() { # nome gerado esperado
  if cmp -s "$2" "$3"; then echo "IGUAL   | $1"; ok=$((ok+1)); else echo "DIFERE  | $1"; ruim=$((ruim+1)); fi
}
for f in dados/*.xz; do if xz -t "$f"; then echo "XZ ok   | $f"; ok=$((ok+1)); else echo "XZ RUIM | $f"; ruim=$((ruim+1)); fi; done
python3 -I analisa_partida.py dados/partida.json.xz > "$tmp/trace.md" 2>"$tmp/trace_stderr.txt";            cmpf "resumos/trace.md" "$tmp/trace.md" resumos/trace.md
cmpf "resumos/trace_stderr.txt (vazio)" "$tmp/trace_stderr.txt" resumos/trace_stderr.txt
python3 -I ledger_compras.py > "$tmp/lc.md";                                                                cmpf "resumos/ledger_compras.md" "$tmp/lc.md" resumos/ledger_compras.md
python3 -I ledger_mana.py > "$tmp/lm.md";                                                                   cmpf "resumos/ledger_mana.md" "$tmp/lm.md" resumos/ledger_mana.md
python3 -I ledger_fichas.py > "$tmp/lf.md";                                                                 cmpf "resumos/ledger_fichas.md" "$tmp/lf.md" resumos/ledger_fichas.md
python3 -I orquestracao/estado_por_turno.py > "$tmp/est.txt";                                               cmpf "resumos/estado_por_turno.txt" "$tmp/est.txt" resumos/estado_por_turno.txt
python3 -I orquestracao/sequencia_bruta.py 1 7 > "$tmp/seq.txt";                                           cmpf "resumos/sequencia_bruta.txt" "$tmp/seq.txt" resumos/sequencia_bruta.txt
python3 -I orquestracao/extrair_cr_trechos.py > "$tmp/cr.txt";                                              cmpf "resumos/cr_2026-09-25_trechos.txt" "$tmp/cr.txt" resumos/cr_2026-09-25_trechos.txt
python3 -I testes_manual13.py > "$tmp/testes.txt" 2>&1;                                                     cmpf "resumos/testes_manual13.txt (1 linha por teste)" "$tmp/testes.txt" resumos/testes_manual13.txt
if [ -f SHA256SUMS ]; then if sha256sum -c --quiet SHA256SUMS; then echo "SHA256  | SHA256SUMS confere"; ok=$((ok+1)); else echo "SHA256  | SHA256SUMS NAO confere"; ruim=$((ruim+1)); fi; fi
echo "---"; echo "$ok conferências ok, $ruim falhas"
[ "$ruim" -eq 0 ]

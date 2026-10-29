#!/bin/bash
# Refaz TODAS as saidas de resumos/ a partir de dados/partida.json.xz e compara com `cmp`. Uso: bash verificar_reproducao.sh
# Nao verifica: a extracao do JSON da conversa (depende do registro da sessao, fora do repositorio) nem rulings_scryfall.json (depende da API).
set -u
AQUI="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"
ok=0; falha=0
cmp_ok() { if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; falha=$((falha+1)); fi; }
cd "$AQUI"
PYTHONHASHSEED=11 python3 analisa_partida.py > "$T/trace.md";                    cmp_ok "$T/trace.md" resumos/trace.md "trace.md"
PYTHONHASHSEED=12 python3 orquestracao/estado_por_turno.py > "$T/estado.txt";    cmp_ok "$T/estado.txt" resumos/estado_por_turno.txt "estado_por_turno.txt"
PYTHONHASHSEED=13 python3 mana_por_turno.py > "$T/mana.md";                      cmp_ok "$T/mana.md" resumos/mana_por_turno.md "mana_por_turno.md"
PYTHONHASHSEED=14 python3 ledger_contadores.py > "$T/ledger.md";                 cmp_ok "$T/ledger.md" resumos/ledger_contadores.md "ledger_contadores.md"
PYTHONHASHSEED=15 python3 orquestracao/confere_simulador.py > "$T/confere.txt";  cmp_ok "$T/confere.txt" resumos/confere_simulador.txt "confere_simulador.txt (simulador vivo: 5 conferencias)"
[ -s "$T/trace.md" ] && [ -s "$T/ledger.md" ] || { echo "VACUO: saida vazia"; falha=$((falha+1)); }
echo "$ok iguais, $falha diferentes"; rm -rf "$T"; [ "$falha" -eq 0 ] && [ "$ok" -gt 0 ]

#!/bin/bash
# Refaz, a partir dos .xz de dados/ e das copias arquivadas do simulador, cada saida de resumos/ e compara com `cmp`; testa os .xz e confere o SHA256SUMS.
# NAO compara resumos/rulings_scryfall.json (vem da API ao vivo). `--tudo` tambem RE-EXECUTA a medicao da Plaza (N=10.000 no modo padrao, ~5 min) e compara com dados/medicao_plaza_ANTES_padrao_N10000.json.
# O confere_simulador_DEPOIS roda no simulador VIVO (com a correcao): NAO edite o simulador enquanto roda. Uso: bash verificar_reproducao.sh [--tudo]
cd "$(dirname "$0")" || exit 2
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
ok=0; ruim=0
cmpf() { if cmp -s "$2" "$3"; then echo "IGUAL   | $1"; ok=$((ok+1)); else echo "DIFERE  | $1"; ruim=$((ruim+1)); fi; }
for f in dados/*.xz; do if xz -t "$f"; then echo "XZ ok   | $f"; ok=$((ok+1)); else echo "XZ RUIM | $f"; ruim=$((ruim+1)); fi; done
python3 -I analisa_partida.py dados/partida.json.xz > "$tmp/trace.md" 2>"$tmp/e.txt";                 cmpf "resumos/trace.md" "$tmp/trace.md" resumos/trace.md
python3 -I orquestracao/estado_por_turno.py > "$tmp/est.txt";                                         cmpf "resumos/estado_por_turno.txt" "$tmp/est.txt" resumos/estado_por_turno.txt
python3 -I orquestracao/sequencia_bruta.py 1 6 > "$tmp/seq.txt";                                      cmpf "resumos/sequencia_bruta.txt" "$tmp/seq.txt" resumos/sequencia_bruta.txt
python3 -I orquestracao/checagens_preliminares.py > "$tmp/chk.txt";                                   cmpf "resumos/checagens_preliminares.txt" "$tmp/chk.txt" resumos/checagens_preliminares.txt
python3 -I ledger_contadores.py > "$tmp/led.md";                                                      cmpf "resumos/ledger_contadores.md" "$tmp/led.md" resumos/ledger_contadores.md
python3 -I orquestracao/confere_simulador.py > "$tmp/cA.txt";                                         cmpf "resumos/confere_simulador_ANTES_plaza.txt (copia arquivada c59226f)" "$tmp/cA.txt" resumos/confere_simulador_ANTES_plaza.txt
python3 -I orquestracao/confere_simulador.py ../../mothman_goldfish_v1.py > "$tmp/cD.txt";            cmpf "resumos/confere_simulador_DEPOIS_plaza.txt (simulador vivo)" "$tmp/cD.txt" resumos/confere_simulador_DEPOIS_plaza.txt
python3 -I testes_manual3.py > "$tmp/t.txt" 2>&1;                                                     cmpf "resumos/testes_manual3.txt (1 linha por teste)" "$tmp/t.txt" resumos/testes_manual3.txt
python3 -I orquestracao/extrair_cr_trechos.py > "$tmp/cr.txt";                                        cmpf "resumos/cr_trechos.txt" "$tmp/cr.txt" resumos/cr_trechos.txt
if [ "$1" == "--tudo" ]; then
  PYTHONHASHSEED=0 python3 -I orquestracao/medir_plaza.py 10000 1000000 padrao > "$tmp/m.json";       cmpf "dados/medicao_plaza_ANTES_padrao_N10000.json (re-execucao)" "$tmp/m.json" dados/medicao_plaza_ANTES_padrao_N10000.json
fi
if [ -f SHA256SUMS ]; then if sha256sum -c --quiet SHA256SUMS; then echo "SHA256  | SHA256SUMS confere"; ok=$((ok+1)); else echo "SHA256  | SHA256SUMS NAO confere"; ruim=$((ruim+1)); fi; fi
echo "---"; echo "$ok conferencias ok, $ruim falhas"
[ "$ruim" -eq 0 ]

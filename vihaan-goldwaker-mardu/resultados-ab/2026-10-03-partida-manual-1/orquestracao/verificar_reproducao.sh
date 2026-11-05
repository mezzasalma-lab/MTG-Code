#!/bin/bash
# Refaz as saidas a partir do log arquivado e dos snapshots de codigo e compara byte a byte (cmp) com os resumos salvos. Rodar de qualquer pasta.
# Nao refaz (precisa de rede): oraculo_com_rulings.py (Scryfall ao vivo; a resposta bruta esta em dados/oraculo_rulings_ao_vivo.json).
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
OUT=sequencia_bruta.txt chk python3 sequencia_bruta.py ../dados/partida.json.xz
OUT=ledger_treasures.txt chk python3 ledger_treasures.py ../dados/partida.json.xz
OUT=ledger_mana.txt chk python3 ledger_mana.py ../dados/partida.json.xz ../dados/oraculo_rulings_ao_vivo.json
OUT=atacantes_vs_criacao.txt chk python3 atacantes_vs_criacao.py ../dados/partida.json.xz
OUT=lacunas_simulador_c04840d.txt chk python3 lacunas_simulador_c04840d.py
OUT=comparacao_simulador_padrao.txt chk python3 comparacao_simulador.py 10000 3000000
OUT=comparacao_simulador_resiliencia.txt FX_MODO=resiliencia chk python3 comparacao_simulador.py 10000 3000000
echo "$ok/$total saidas byte a byte iguais"

#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte (cmp) com os resumos salvos.
# Uso (de qualquer pasta):  bash verificar_reproducao.sh          -> so' as tabelas que vem dos brutos + verificacao cruzada (rapido)
#                           bash verificar_reproducao.sh --tudo   -> tambem RE-EXECUTA testes dirigidos, bit-identidade 20.000 e regressao 20.000 (alguns minutos)
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
OUT=ab_2000.txt chk python3 fx_ab.py 2000 --sum
OUT=ab_10000.txt chk python3 fx_ab.py 10000 --sum
OUT=ab_2000_resiliencia.txt FX_MODO=resiliencia chk python3 fx_ab.py 2000 --sum
OUT=verificacao_cruzada_blunt_vs_early_all.txt chk python3 fx_cruzada.py
OUT=mulligan_topo.txt chk python3 mulligan_topo.py
OUT=smoke.txt chk python3 smoke.py
if [ "$1" == "--tudo" ]; then
  OUT=testes_dirigidos.txt chk python3 testes_dirigidos.py
  OUT=bitident_flags_off_20000.txt chk python3 bitident.py 20000 1000000
  OUT=regressao_20000.txt chk python3 fx_regressao.py 20000
fi
echo "$ok/$total saidas byte a byte iguais"

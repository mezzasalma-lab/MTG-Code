#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte (cmp) com os resumos salvos.
# Uso (de qualquer pasta):  bash verificar_reproducao.sh          -> so' as tabelas que vem dos brutos (rapido)
#                           bash verificar_reproducao.sh --tudo   -> tambem RE-EXECUTA smoke, testes dirigidos, enumeracao por script, efeitos unilaterais e os 4 lotes do ensaio a seco
#                                                                    (10.000 partidas x 2 modos e a regressao de 20.000 x 2 modos; 4 processos em paralelo, ~15 min)
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
OUT=dry_run_padrao_10000.txt chk python3 sac_dry_run.py --sum --bruto ../dados/raw_dry_run_padrao_10000.json.xz
OUT=dry_run_resiliencia_10000.txt chk python3 sac_dry_run.py --sum --bruto ../dados/raw_dry_run_resiliencia_10000.json.xz
OUT=paridade_oponente_padrao.txt chk python3 paridade_oponente.py ../dados/raw_dry_run_padrao_10000.json.xz
OUT=paridade_oponente_resiliencia.txt chk python3 paridade_oponente.py ../dados/raw_dry_run_resiliencia_10000.json.xz
OUT=enumeracao.txt chk python3 enumeracao_sac.py
if [ "$1" == "--tudo" ]; then
  OUT=smoke.txt chk python3 smoke.py
  OUT=testes_dirigidos.txt chk python3 testes_dirigidos.py
  OUT=efeitos_unilaterais.txt chk python3 efeitos_unilaterais.py 5000 3000000
  tmp=$(mktemp -d)
  (python3 sac_dry_run.py 10000 3000000 > "$tmp/a.txt" 2>&1) &
  (FX_MODO=resiliencia python3 sac_dry_run.py 10000 3000000 > "$tmp/b.txt" 2>&1) &
  (python3 sac_dry_run.py 20000 5000000 > "$tmp/c.txt" 2>&1) &
  (FX_MODO=resiliencia python3 sac_dry_run.py 20000 5000000 > "$tmp/d.txt" 2>&1) &
  wait
  for par in "a.txt:dry_run_padrao_10000.txt" "b.txt:dry_run_resiliencia_10000.txt" "c.txt:regressao_dry_run_padrao_20000.txt" "d.txt:regressao_dry_run_resiliencia_20000.txt"; do
    total=$((total+1)); if cmp -s "$tmp/${par%%:*}" "../resumos/${par##*:}"; then echo "IGUAL  ${par##*:} (re-execucao)"; ok=$((ok+1)); else echo "DIFERE ${par##*:} (re-execucao)"; fi
  done
  rm -rf "$tmp"
fi
echo "$ok/$total saidas byte a byte iguais"

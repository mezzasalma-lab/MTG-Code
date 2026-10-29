#!/bin/bash
# Refaz as tabelas a partir dos brutos arquivados (.json.xz) e compara byte a byte (cmp) com os resumos salvos.
# Uso (de qualquer pasta):  bash verificar_reproducao.sh          -> so' as saidas que vem dos brutos / dos dados de API arquivados (rapido)
#                           bash verificar_reproducao.sh --tudo   -> tambem RE-EXECUTA smoke, testes do repositorio, testes dirigidos em estados naturais, bit-identidade 20.000 x 2 modos,
#                                                                    regressao 20.000 x 6, o diagnostico do invariante e os 4 lotes do A/B (re-simulados em pasta temporaria, sem tocar nos brutos); ~8 min
# Nao refaz (precisa de rede): csb_troca.py e oraculo_mythos.py SEM --sum (as respostas brutas da API estao em ../dados/).
cd "$(dirname "$0")"
ok=0; total=0
chk() { total=$((total+1)); if cmp -s <("$@") "../resumos/$OUT"; then echo "IGUAL  $OUT"; ok=$((ok+1)); else echo "DIFERE $OUT"; fi; }
OUT=ab_2000.txt chk python3 fx_ab.py 2000 --sum
OUT=ab_10000.txt chk python3 fx_ab.py 10000 --sum
OUT=ab_2000_resiliencia.txt FX_MODO=resiliencia chk python3 fx_ab.py 2000 --sum
OUT=ab_10000_resiliencia.txt FX_MODO=resiliencia chk python3 fx_ab.py 10000 --sum
OUT=spellbook.txt chk python3 csb_troca.py --sum
OUT=oraculo_mythos.txt chk python3 oraculo_mythos.py --sum
OUT=confere_cores.txt chk python3 confere_cores.py
if [ "$1" == "--tudo" ]; then
  OUT=smoke.txt chk python3 smoke.py
  OUT=testes_repo.txt chk bash -c "cd ../../.. && python3 test_vihaan_goldfish.py"
  OUT=testes_dirigidos.txt chk python3 testes_dirigidos.py 400
  OUT=bitident_20000.txt chk python3 bitident.py 20000 5000000
  OUT=regressao_20000.txt chk python3 fx_regressao.py 20000
  OUT=diagnostico_resto.txt chk bash -c "python3 diag_resto.py; python3 diag_resto2.py"
  tmp=$(mktemp -d)
  for par in "2000:padrao:ab_2000.txt" "10000:padrao:ab_10000.txt" "2000:resiliencia:ab_2000_resiliencia.txt" "10000:resiliencia:ab_10000_resiliencia.txt"; do
    n=${par%%:*}; resto=${par#*:}; modo=${resto%%:*}; saida=${resto#*:}
    OUT=$saida; total=$((total+1))
    if cmp -s <(FX_RAW="$tmp/raw_$n$modo" FX_MODO=$modo python3 fx_ab.py $n) "../resumos/$saida"; then
      # alem da tabela, o bruto re-simulado tem que ser IDENTICO ao arquivado (descomprimido: nao depende da versao do xz)
      arq="../dados/raw_ab_$n$([ $modo == resiliencia ] && echo _resiliencia).json.xz"
      if cmp -s <(xz -dc "$tmp/raw_$n$modo.json.xz") <(xz -dc "$arq"); then echo "IGUAL  $saida (re-execucao + bruto identico)"; ok=$((ok+1)); else echo "DIFERE $saida (tabela igual, bruto diferente)"; fi
    else echo "DIFERE $saida (re-execucao)"; fi
  done
  rm -rf "$tmp"
fi
echo "$ok/$total saidas byte a byte iguais"

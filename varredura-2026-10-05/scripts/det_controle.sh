#!/bin/bash
# controle x correcao do determinismo, 3 hash seeds, N=1500, dois modos. Saida: det_ctrl_<deck>.txt
cd "$(dirname "$0")"
for spec in "hei-bai-wurbg heibai_goldfish_v1.py 8" "thranduil-sultai thranduil_goldfish_v1.py 8" "ms-bumbleflower-bant bumbleflower_goldfish_v1.py 10" "edgar-markov-mardu edgar_markov_goldfish_v1.py 8"; do
  set -- $spec; d=$1
  { echo "Determinismo entre processos: mesma semente, 3 PYTHONHASHSEED diferentes (11, 22, 33), N=1500 sementes (1_000_000+i), modos padrao e resiliencia; compara campo a campo o estado final."
    echo "CONTROLE (DETERMINISTIC_SET_ORDER_ENABLED=False, o iterador antigo):"
    FLAGS='{"DETERMINISTIC_SET_ORDER_ENABLED": false}' nice -n 5 ./det_check.sh $1 $2 $3 1500
    echo "CORRECAO (arquivo vivo, DETERMINISTIC_SET_ORDER_ENABLED=True):"
    nice -n 5 ./det_check.sh $1 $2 $3 1500
  } > det_ctrl_$d.txt 2>&1
  echo "feito $d"
done
echo FIM_CTRL

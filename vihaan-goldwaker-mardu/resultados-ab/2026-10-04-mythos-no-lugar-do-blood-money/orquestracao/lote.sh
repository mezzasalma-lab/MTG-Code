#!/bin/bash
# A/B da 12a rodada: 2.000 e 10.000 partidas pareadas, modos padrao e resiliencia. Uso: bash lote.sh (de dentro de orquestracao/)
cd "$(dirname "$0")"
mkdir -p ../resumos
python3 fx_ab.py 2000 > ../resumos/ab_2000.txt
python3 fx_ab.py 10000 > ../resumos/ab_10000.txt
FX_MODO=resiliencia python3 fx_ab.py 2000 > ../resumos/ab_2000_resiliencia.txt
FX_MODO=resiliencia python3 fx_ab.py 10000 > ../resumos/ab_10000_resiliencia.txt

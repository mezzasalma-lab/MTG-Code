#!/bin/bash
# Roda os quatro lotes do A/B (padrao 2000 e 10000, resiliencia 2000 e 10000) e salva os resumos. Uso: bash lote.sh
cd "$(dirname "$0")"
python3 fx_ab.py 2000 > ../resumos/ab_2000.txt
python3 fx_ab.py 10000 > ../resumos/ab_10000.txt
FX_MODO=resiliencia python3 fx_ab.py 2000 > ../resumos/ab_2000_resiliencia.txt
FX_MODO=resiliencia python3 fx_ab.py 10000 > ../resumos/ab_10000_resiliencia.txt
echo FIM

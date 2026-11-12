#!/bin/bash
# Re-roda a regressao 20.000 x 6 e os testes dirigidos em estados naturais (apos corrigir o invariante de sobreviventes). Uso: bash rodar_validacao_final.sh
cd "$(dirname "$0")"
python3 fx_regressao.py 20000 > ../resumos/regressao_20000.txt 2>&1
python3 testes_dirigidos.py 400 > ../resumos/testes_dirigidos.txt 2>&1
python3 diag_resto.py > ../resumos/diagnostico_resto.txt 2>&1
python3 diag_resto2.py >> ../resumos/diagnostico_resto.txt 2>&1
echo FIM > ../resumos/.fim_validacao_final

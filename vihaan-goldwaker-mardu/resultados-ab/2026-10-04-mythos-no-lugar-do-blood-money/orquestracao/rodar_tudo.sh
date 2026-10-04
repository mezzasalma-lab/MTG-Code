#!/bin/bash
# Bateria completa da 12a rodada, em sequencia (4 nucleos): smoke, testes do repo, bit-identidade 20.000 x 2 modos, regressao 20.000, A/B 2k/10k x 2 modos. Uso: bash rodar_tudo.sh
cd "$(dirname "$0")"
mkdir -p ../resumos
python3 smoke.py > ../resumos/smoke.txt 2>&1
(cd ../../.. && python3 test_vihaan_goldfish.py) > ../resumos/testes_repo.txt 2>&1
python3 bitident.py 20000 5000000 > ../resumos/bitident_20000.txt 2>&1
python3 fx_regressao.py 20000 > ../resumos/regressao_20000.txt 2>&1
bash lote.sh
echo FIM > ../resumos/.fim_bateria

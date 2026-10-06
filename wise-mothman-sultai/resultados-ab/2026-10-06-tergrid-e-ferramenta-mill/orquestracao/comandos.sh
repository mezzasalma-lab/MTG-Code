#!/bin/bash
# Comandos EXATOS que geraram os dois lotes brutos desta pasta (rodados a partir de /home/user/MTG-Code; ~5 min cada, 4 processos).
# Simulador: wise-mothman-sultai/mothman_goldfish_v1.py no commit 91b1a3d. Desde 2026-10-06 o padrao do simulador liga LANDFALL_PAYOFF_FIRST (terreno depois do payoff); estes lotes sao da ordem antiga: `--fixa LANDFALL_PAYOFF_FIRST=false` (bit-identico a 91b1a3d) os reproduz. Ferramenta: wise-mothman-sultai/ferramentas/mill_oponentes.py.
R=wise-mothman-sultai/resultados-ab/2026-10-06-tergrid-e-ferramenta-mill
python3 wise-mothman-sultai/ferramentas/mill_oponentes.py --fixa LANDFALL_PAYOFF_FIRST=false -n 5000 --modo padrao \
  -v base -v pacote5 -v pacote5+master -v bruvac -v sem_kozilek \
  -o $R/resumos/mill_oponentes_padrao_5000.txt --bruto $R/dados/mill_oponentes_padrao_5000.json.xz
python3 wise-mothman-sultai/ferramentas/mill_oponentes.py --fixa LANDFALL_PAYOFF_FIRST=false -n 5000 --modo resiliencia \
  -v base -v pacote5+master \
  -o $R/resumos/mill_oponentes_resiliencia_5000.txt --bruto $R/dados/mill_oponentes_resiliencia_5000.json.xz
# Annihilator (teto de partidas em que a Tergrid poderia disparar por sacrificio):
python3 $R/orquestracao/frequencia_annihilator.py 10000 padrao
python3 $R/orquestracao/frequencia_annihilator.py 10000 resiliencia
# Teto do elo Lantern -> crime -> Deepmuck/Freestrider (N=5000, sementes 3.000.000+i):
(PYTHONHASHSEED=0 python3 $R/orquestracao/crime_deepmuck.py 5000 padrao; PYTHONHASHSEED=0 python3 $R/orquestracao/crime_deepmuck.py 5000 resiliencia) > $R/resumos/crime_deepmuck.txt

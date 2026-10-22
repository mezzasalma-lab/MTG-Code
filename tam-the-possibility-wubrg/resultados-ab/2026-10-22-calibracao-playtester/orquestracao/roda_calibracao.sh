#!/bin/bash
# Roda o ajuste do perfil e as validacoes por replay no simulador VIVO (tam_goldfish_v1.py da pasta do deck; no commit da rodada 2 e' identico a ../../2026-10-22-rodada2-motor-e-perfil/codigo/tam_goldfish_v1_DEPOIS_rodada2.py). Saidas em "$OUT" (padrao: ../resumos).
cd "$(dirname "$0")"
OUT=${OUT:-../resumos}; mkdir -p "$OUT"
export PYTHONHASHSEED=0
export TAM_SIM=/home/user/MTG-Code/tam-the-possibility-wubrg/tam_goldfish_v1.py
for p in default playtester; do python3 ajuste_perfil.py 2000 $p > "$OUT"/ajuste_perfil_$p.txt 2>&1; done
for j in 3 4 5; do
  python3 replay_perfil.py 300 $j padrao default            > "$OUT"/replay_jogo${j}_padrao.txt 2>&1
  python3 replay_perfil.py 300 $j resiliencia default       > "$OUT"/replay_jogo${j}_resiliencia_default.txt 2>&1
  python3 replay_perfil.py 300 $j resiliencia playtester    > "$OUT"/replay_jogo${j}_resiliencia_playtester.txt 2>&1
  python3 replay_perfil.py 300 $j padrao playtester         > "$OUT"/replay_jogo${j}_padrao_playtester.txt 2>&1
done
touch "$OUT"/.calibracao_feita

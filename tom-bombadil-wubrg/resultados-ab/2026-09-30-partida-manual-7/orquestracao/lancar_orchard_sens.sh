#!/bin/bash
# Lança a sensibilidade do Exotic Orchard em 4 processos (N=3000 pares, sementes 1_000_000+i) e junta a saída.
# Uso (a partir da pasta da partida #7):  bash orquestracao/lancar_orchard_sens.sh <pasta_temporaria>
# Depois:  xz -9 <pasta>/o_N.json  e mover para dados/orchard_sens_N.json.xz ; resumo: python3 orchard_sens.py sum dados/orchard_sens
set -e
D="${1:?pasta temporaria}"
mkdir -p "$D"
for p in 0 1 2 3; do
  nohup python3 orchard_sens.py run $p 4 3000 "$D/o_$p.json" > "$D/log_$p.txt" 2>&1 &
  echo $! > "$D/pid_$p"
done
echo "4 processos lançados; esperar pelos arquivos $D/o_*.json (não usar pgrep -f/pkill -f: casa com o próprio shell; matar por PID em $D/pid_*)"

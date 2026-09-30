#!/bin/bash
# Uso: run_ab.sh <out_prefix> <N> <profile> -- variantes...
cd /home/user/MTG-Code/prismatic-bridge-wurbg
OUT="$1"; N="$2"; PROFILE="$3"; shift 4
for p in 0 1 2 3; do
  nohup python3 ab_candidatas.py $p 4 "$N" "$OUT" --profile "$PROFILE" "$@" > "${OUT}_$p.log" 2>&1 &
  echo $! >> "${OUT}.pids"
done
echo launched

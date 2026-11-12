#!/usr/bin/env python3
"""Replicacao: a base e a variante Branching <- Negate desta pasta tem de ser BIT-IDENTICA (fingerprint partida a partida + todos os campos numericos) as da pasta `candidatas-stefano-2` (mesmo simulador, mesmas
sementes 3.000.000+i, mesmos 2 modos). Prova que o simulador congelado aqui == o de la e que o harness retomavel (parcial por variante) nao mudou nada. Uso: python3 confere_replicacao.py > ../resumos/replicacao.txt"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
OUT = os.path.join(ARQ, "..", "2026-10-07-candidatas-stefano-2", "dados")
tot = ok = 0
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    novo = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_pacote_10000{suf}")); velho = A.carregar_raw(os.path.join(OUT, f"raw_final_10000{suf}"))
    for a, b in (("base", "base"), ("b__negate", "branching__negate")):
        n, v = novo[a], velho[b]; assert len(n) == len(v) == 10000
        iguais = sum(1 for x, y in zip(n, v) if x[0] == y[0] and x[1] == y[1])
        tot += 1; ok += iguais == 10000
        print(f"{modo:12s} {a:10s} (aqui) == {b:18s} (candidatas-stefano-2): {iguais}/10000 partidas identicas (fingerprint + todos os campos)")
print(f"{ok}/{tot} series bit-identicas")

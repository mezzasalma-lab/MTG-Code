#!/usr/bin/env python3
"""Replicacao cruzada: a `base` desta pasta (simulador ANTES, lista de antes da troca) tem de ser BIT-IDENTICA (todos os campos numericos, 10.000 partidas x 2 modos) a `u3_swamp` de `../2026-10-10-underground-sea-sem-bojuka` (a MESMA lista, obtida la' por 1 troca `no lugar`
sobre a lista de 2026-10-09). Uso: python3 confere_replicacao.py > ../resumos/replicacao.txt"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
ANT = os.path.join(ARQ, "..", "2026-10-10-underground-sea-sem-bojuka", "dados")
tot = ok = 0
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    novo = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_vista_10000{suf}"))["base"]; velho = A.carregar_raw(os.path.join(ANT, f"raw_under_10000{suf}"))["u3_swamp"]
    assert len(novo) == len(velho) == 10000
    iguais = sum(1 for x, y in zip(novo, velho) if set(x[1]) == set(y[1]) and all(x[1][c] == v for c, v in y[1].items()))
    tot += 1; ok += iguais == 10000
    print(f"{modo:12s} base[vista] == u3_swamp[under]: {iguais}/10000 partidas identicas")
print(f"{ok}/{tot} series bit-identicas")

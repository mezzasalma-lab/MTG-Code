#!/usr/bin/env python3
"""Replicacao cruzada desta pasta: a `base` do lote W (`swtrop`, simulador ANTES, lista de antes da troca) tem de ser BIT-IDENTICA (todos os campos numericos) a `d1_hollow_bayou_passage_vista` do lote Z de
`../2026-10-09-terrenos-proxy` (a mesma lista, la' obtida por 2 trocas `no lugar` sobre o DEPOIS), 10.000 partidas x 2 modos; e a `base` do lote V (`swtrop50`, comandante-alvo 0.5) a `d1` do z50, resiliencia, 10.000.
Uso: python3 confere_replicacao.py > ../resumos/replicacao.txt"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
ANT = os.path.join(ARQ, "..", "2026-10-09-terrenos-proxy", "dados")
tot = ok = 0
def comp(novo, velho, rot):
    global tot, ok
    assert len(novo) == len(velho) == 10000, (rot, len(novo), len(velho))
    iguais = sum(1 for x, y in zip(novo, velho) if set(x[1]) == set(y[1]) and all(x[1][c] == v for c, v in y[1].items()))
    tot += 1; ok += iguais == 10000
    print(f"{rot}: {iguais}/10000 partidas identicas")
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    comp(A.carregar_raw(os.path.join(ARQ, "dados", f"raw_swtrop_10000{suf}"))["base"], A.carregar_raw(os.path.join(ANT, f"raw_terrenos4_10000{suf}"))["d1_hollow_bayou_passage_vista"], f"(1) {modo:12s} base[swtrop] == d1[terrenos4]      ")
comp(A.carregar_raw(os.path.join(ARQ, "dados", "raw_swtrop50_10000_resiliencia"))["base"], A.carregar_raw(os.path.join(ANT, "raw_z50_10000_resiliencia"))["d1_hollow_bayou_passage_vista"], "(2) resiliencia   base[swtrop50] == d1[z50] (0,5)    ")
print(f"{ok}/{tot} series bit-identicas")

#!/usr/bin/env python3
"""Replicacao cruzada desta pasta com `../2026-10-09-swarmyard-tropical` (10.000 partidas x 2 modos, todos os campos numericos):
 (1) `base` daqui (simulador VIVO congelado, lista atual) == `e1_swarmyard_tropical` de la' (ANTES + Swarmyard -> Tropical `no lugar`);
 (2) `u0_bojuka_bog` daqui (Bojuka Bog -> Underground Sea sobre a lista atual) == `e2_e1_mais_bog_sea` de la' (as duas trocas `no lugar` sobre o ANTES): a MESMA lista obtida por dois caminhos;
 (3) `base` do lote U2 == `base` do lote U (mesmas sementes, lotes rodados em momentos diferentes).
Uso: python3 confere_replicacao.py > ../resumos/replicacao.txt"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
ANT = os.path.join(ARQ, "..", "2026-10-09-swarmyard-tropical", "dados")
tot = ok = 0
def comp(novo, velho, rot):
    global tot, ok
    assert len(novo) == len(velho) == 10000, (rot, len(novo), len(velho))
    iguais = sum(1 for x, y in zip(novo, velho) if set(x[1]) == set(y[1]) and all(x[1][c] == v for c, v in y[1].items()))
    tot += 1; ok += iguais == 10000
    print(f"{rot}: {iguais}/10000 partidas identicas")
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    u = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_under_10000{suf}")); u2 = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_under2_10000{suf}")); w = A.carregar_raw(os.path.join(ANT, f"raw_swtrop_10000{suf}"))
    comp(u["base"], w["e1_swarmyard_tropical"], f"(1) {modo:12s} base[under] == e1[swtrop]            ")
    comp(u["u0_bojuka_bog"], w["e2_e1_mais_bog_sea"], f"(2) {modo:12s} u0[under] == e2[swtrop]              ")
    comp(u2["base"], u["base"], f"(3) {modo:12s} base[under2] == base[under]       ")
print(f"{ok}/{tot} series bit-identicas")

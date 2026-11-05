#!/usr/bin/env python3
"""Comparacao direta (A - B, pareado) entre variantes do lote 1 de terrenos, so' dos brutos: Swamp+Forest (t3) x Swamp+Swamp (t4) x cada troca sozinha (t1, t2). Uso: python3 compara_terrenos.py > ../resumos/terrenos_entre_si.md"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
R = {m: A.carregar_raw(os.path.join(ARQ, "dados", f"raw_terrenos_10000{s}")) for m, s in (("padrao", ""), ("resiliencia", "_resiliencia"))}
CAMPOS = [("commander_cast_turn__ate_T4", "comandante até T4 (pp)"), ("cleared_T8", "T8 (pp)"), ("cleared_T10", "T10 (pp)"), ("first_elim_T6", "1º oponente fora até T6 (pp)")]
PARES = [("t3_ambos_swamp_forest", "t4_ambos_swamp_swamp"), ("t3_ambos_swamp_forest", "t6_t3_mais_island_swamp"), ("t3_ambos_swamp_forest", "t1_swarmyard_swamp"), ("t3_ambos_swamp_forest", "t2_hollow_forest"), ("t2_hollow_forest", "t1_swarmyard_swamp")]
print("Diferença pareada (A − B), N = 10.000; `*` = excede o IC95%.\n")
for modo in R:
    print(f"### {modo}\n\n| A − B | " + " | ".join(r for _, r in CAMPOS) + " |\n|---|" + "---|" * len(CAMPOS))
    for a, b in PARES:
        cel = []
        for c, _ in CAMPOS:
            m, h = A.ic([x[1].get(c, 0.0) for x in R[modo][b]], [x[1].get(c, 0.0) for x in R[modo][a]]); cel.append("%+.2f ± %.2f%s" % (100 * m, 100 * h, " *" if abs(m) > h else ""))
        print(f"| {a} − {b} | " + " | ".join(cel) + " |")
    print()

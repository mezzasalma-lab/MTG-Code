#!/usr/bin/env python3
"""Nova linha de base (lista aplicada em 2026-10-11 = variante `w1_vista_fabled` deste A/B, N = 10.000, sementes 3.000.000+i, 12 turnos) ao lado da anterior (com a Prismatic Vista), mais a diferenca pareada com IC95%.
Lido SO' dos brutos arquivados desta pasta. O simulador vivo com SWAPS=() e' bit-identico a `w1_vista_fabled` (resumos/bitident_lista.txt). Uso: python3 base_nova.py > ../resumos/base_nova.md"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
def m(rs, c): return st.mean(y[1].get(c, 0.0) for y in rs)
R = {md: A.carregar_raw(os.path.join(ARQ, "dados", f"raw_vista_10000{suf}")) for md, suf in (("p", ""), ("r", "_resiliencia"))}
N = {md: R[md]["w1_vista_fabled"] for md in R}; B = {md: R[md]["base"] for md in R}
assert len(N["p"]) == len(B["p"]) == 10000 and m(N["p"], "cleared_T8") > 0 and m(B["p"], "cleared_T8") > 0
print("## Nova linha de base (lista aplicada em 2026-10-11: Prismatic Vista → Fabled Passage; N = 10.000, sementes 3.000.000+i, 12 turnos)\n")
print("| métrica | modo padrão (nova / anterior / diferença pareada ± IC95%) | modo resiliência (nova / anterior / diferença pareada ± IC95%) |\n|---|---|---|")
LIN = [("comandante conjurado até T3 (%)", "commander_cast_turn__ate_T3", 100), ("comandante conjurado até T4 (%)", "commander_cast_turn__ate_T4", 100), ("comandante conjurado até T5 (%)", "commander_cast_turn__ate_T5", 100), ("mesa limpa até T7 (%)", "cleared_T7", 100),
       ("mesa limpa até T8 (%)", "cleared_T8", 100), ("mesa limpa até T10 (%)", "cleared_T10", 100), ("1º oponente fora até T6 (%)", "first_elim_T6", 100), ("eu perco por deck-out (%)", "self_lost", 100), ("vida mínima (média, unid.)", "life_min", 1)]
def cel(md, c, esc):
    d, h = A.ic([x[1].get(c, 0.0) for x in B[md]], [y[1].get(c, 0.0) for y in N[md]])
    return "%.2f / %.2f / %+.2f ± %.2f%s" % (esc * m(N[md], c), esc * m(B[md], c), esc * d, esc * h, " \\*" if abs(d) > h else "")
for rot, c, esc in LIN: print(f"| {rot} | {cel('p', c, esc)} | {cel('r', c, esc)} |")

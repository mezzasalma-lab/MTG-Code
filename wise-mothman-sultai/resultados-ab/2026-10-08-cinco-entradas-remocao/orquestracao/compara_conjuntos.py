#!/usr/bin/env python3
"""Comparacao DIRETA entre os conjuntos de corte (A - B, pareado, mesmas sementes), so' dos brutos: a escolha dos 3 cortes variaveis importa? Campos: cleared_T8, cleared_T10, self_lost,
counterspells_cast, protection_used_total, smart_removals_total, interaction_plays. Uso: python3 compara_conjuntos.py > ../resumos/conjuntos_entre_si.md"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
R = {m: A.carregar_raw(os.path.join(ARQ, "dados", f"raw_cinco_10000{s}")) for m, s in (("padrao", ""), ("resiliencia", "_resiliencia"))}
CAMPOS = [("cleared_T8", 100, "T8 (pp)"), ("cleared_T10", 100, "T10 (pp)"), ("self_lost", 100, "deck-out (pp)"), ("counterspells_cast", 1, "contramágicas conjuradas"), ("smart_removals_total", 1, "peças do motor removidas"), ("interaction_plays", 1, "jogadas de interação (proxy)")]
PARES = [("s4_vats_wave_dsp", "s1_vats_wave_deluge"), ("s4_vats_wave_dsp", "s3_vats_wave_arcane"), ("s4_vats_wave_dsp", "s6_vats_deluge_dsp"), ("s4_vats_wave_dsp", "s2_vats_arcane_dsp"), ("s4_vats_wave_dsp", "s7_tear_wave_deluge"),
         ("s6_vats_deluge_dsp", "s5_vats_deluge_arcane"), ("s2_vats_arcane_dsp", "s1_vats_wave_deluge"), ("s1_vats_wave_deluge", "p1_so_o_par"), ("s4_vats_wave_dsp", "p1_so_o_par")]
print("Diferença pareada entre conjuntos (A − B), N = 10.000; `*` = excede o IC95%. Positivo em T8/T10 = A é mais rápido que B. `p1_so_o_par` = só Frank + Branching (Offer, Negate saem).\n")
for modo in R:
    print(f"### {modo}\n\n| A − B | " + " | ".join(r for _, _, r in CAMPOS) + " |\n|---|" + "---|" * len(CAMPOS))
    for a, b in PARES:
        cel = []
        for c, esc, _ in CAMPOS:
            m, h = A.ic([x[1].get(c, 0.0) for x in R[modo][b]], [x[1].get(c, 0.0) for x in R[modo][a]])
            cel.append("%+.2f ± %.2f%s" % (esc * m, esc * h, " *" if abs(m) > h else ""))
        print(f"| {a} − {b} | " + " | ".join(cel) + " |")
    print()

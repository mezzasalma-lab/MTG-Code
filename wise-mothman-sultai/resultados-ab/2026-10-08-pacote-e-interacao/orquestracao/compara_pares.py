#!/usr/bin/env python3
"""Comparacao DIRETA entre os pacotes (variante A - variante B, pareado, mesmas sementes), so' dos brutos: a escolha do 2o corte importa? Campos: cleared_T8, cleared_T10, self_lost,
smart_removals_total (pecas do meu motor removidas), protection_used_total. Uso: python3 compara_pares.py > ../resumos/pacotes_entre_si.md"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
R = {m: A.carregar_raw(os.path.join(ARQ, "dados", f"raw_pacote_10000{s}")) for m, s in (("padrao", ""), ("resiliencia", "_resiliencia"))}
CAMPOS = [("cleared_T8", 100, "T8 (pp)"), ("cleared_T10", 100, "T10 (pp)"), ("self_lost", 100, "deck-out (pp)"), ("smart_removals_total", 1, "peças do motor removidas"), ("protection_used_total", 1, "proteções usadas")]
PARES = [("p1_offer_negate", "p3_offer_wave"), ("p1_offer_negate", "p4_offer_deluge"), ("p1_offer_negate", "p5_offer_tear"), ("p1_offer_negate", "p6_offer_arcane"), ("p1_offer_negate", "p2_offer_dsp"), ("p2_offer_dsp", "p3_offer_wave")]
print("Diferença pareada entre pacotes (A − B), N = 10.000; `*` = excede o IC95%. Positivo em T8/T10 = A é mais rápido que B.\n")
for modo in R:
    print(f"### {modo}\n\n| A − B | " + " | ".join(r for _, _, r in CAMPOS) + " |\n|---|" + "---|" * len(CAMPOS))
    for a, b in PARES:
        cel = []
        for c, esc, _ in CAMPOS:
            m, h = A.ic([x[1].get(c, 0.0) for x in R[modo][b]], [x[1].get(c, 0.0) for x in R[modo][a]])
            cel.append("%+.2f ± %.2f%s" % (esc * m, esc * h, " *" if abs(m) > h else ""))
        print(f"| {a} − {b} | " + " | ".join(cel) + " |")
    print()

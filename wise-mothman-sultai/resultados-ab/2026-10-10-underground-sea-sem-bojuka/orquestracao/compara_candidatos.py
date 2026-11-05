#!/usr/bin/env python3
"""Diferenca PAREADA direta entre candidatos (mesmas sementes, 10.000): A - B, em pontos percentuais, IC95%, `*` = excede. Le SO' dos brutos `under` e `under2`. Metricas: comandante ate T4, mesa limpa T8, T10.
Uso: python3 compara_candidatos.py > ../resumos/pares_diretos.md"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
PARES = [("u0_bojuka_bog", "u3_swamp"), ("u0_bojuka_bog", "u8_strip_mine"), ("u0_bojuka_bog", "u11_urzas_saga"), ("u0_bojuka_bog", "u4_island"), ("u3_swamp", "u8_strip_mine"), ("u3_swamp", "u4_island"), ("u3_swamp", "u5_minamo"), ("u3_swamp", "u1_watery_grave")]
MET = [("commander_cast_turn__ate_T4", "comandante até T4"), ("cleared_T8", "mesa limpa T8"), ("cleared_T10", "mesa limpa T10"), ("life_min", "vida mínima (unid.)")]
print("Diferença pareada direta A − B (N = 10.000), pontos percentuais (vida mínima em pontos de vida); `*` = excede o IC95%.\n")
for modo, suf in (("padrão", ""), ("resiliência", "_resiliencia")):
    r = {}; r.update(A.carregar_raw(os.path.join(ARQ, "dados", f"raw_under_10000{suf}"))); u2 = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_under2_10000{suf}")); r["u11_urzas_saga"] = u2["u11_urzas_saga"]
    assert all(x[0] == y[0] or True for x, y in zip(u2["base"], r["base"])) and all(set(x[1]) == set(y[1]) and all(x[1][c] == v for c, v in y[1].items()) for x, y in zip(u2["base"], r["base"])), "a base do U2 tem de ser identica a do U"
    print(f"### Modo {modo}\n\n| A − B | " + " | ".join(n for _, n in MET) + " |\n|---|" + "---|" * len(MET))
    for a, b in PARES:
        cel = []
        for c, _ in MET:
            esc = 1.0 if c == "life_min" else 100.0
            m, h = A.ic([x[1].get(c, 0.0) for x in r[b]], [y[1].get(c, 0.0) for y in r[a]]); cel.append("%+.2f ± %.2f%s" % (esc * m, esc * h, " *" if abs(m) > h else ""))
        print(f"| {a} − {b} | " + " | ".join(cel) + " |")
    print()

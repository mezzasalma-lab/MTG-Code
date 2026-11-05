#!/usr/bin/env python3
"""Resume dados/cmd_cor.json.xz (cmd_cor.py). Uso: python3 resumo_cmd_cor.py > ../resumos/comandante_e_cores.md"""
import json, lzma, os
ARQ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
d = json.load(lzma.open(os.path.join(ARQ, "dados", "cmd_cor.json.xz"), "rt")); J = d["jogos"]; assert len(J) == d["n"] == 10000
print(f"### Comandante nao conjurado no fim do turno T (modo padrao, N = {d['n']}, lista atual)\n")
print("| fim do turno | partidas ainda sem comandante | por falta de mana (< 4 terrenos) | ≥ 4 terrenos, falta B | falta G | falta U | falta ≥ 2 cores | ≥ 4 terrenos e as 3 cores (outro motivo) |\n|---|---|---|---|---|---|---|---|")
for T in (4, 5, 6, 7):
    sem = mana = fB = fG = fU = f2 = outro = 0; tot = 0
    for j in J:
        r = next((x for x in j if x[0] == T), None)
        if r is None: continue
        tot += 1; _, nl, cores, feito = r
        if feito: continue
        sem += 1
        if nl < 4: mana += 1; continue
        falt = [c for c in "BGU" if c not in cores]
        if not falt: outro += 1
        elif len(falt) >= 2: f2 += 1
        else:
            if falt[0] == "B": fB += 1
            elif falt[0] == "G": fG += 1
            else: fU += 1
    p = lambda x: f"{100 * x / tot:.1f}%"
    print(f"| T{T} (n = {tot}) | {p(sem)} | {p(mana)} | {p(fB)} | {p(fG)} | {p(fU)} | {p(f2)} | {p(outro)} |")

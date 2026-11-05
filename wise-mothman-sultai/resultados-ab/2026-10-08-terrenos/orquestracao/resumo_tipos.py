#!/usr/bin/env python3
"""Resume dados/tipos_terreno.json.xz. Uso: python3 resumo_tipos.py > ../resumos/tipos_de_terreno.md"""
import json, lzma, os
ARQ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
d = json.load(lzma.open(os.path.join(ARQ, "dados", "tipos_terreno.json.xz"), "rt")); J = d["jogos"]; assert len(J) == d["n"] == 10000
print(f"### Terreno 'check' entraria desvirado? (fim do turno T-1 = antes da jogada de terreno do turno T; modo padrão, N = {d['n']})\n")
print("| ao jogar o terreno do turno | tenho Swamp ou Forest (Woodland Cemetery) | Island ou Swamp (Drowned Catacomb) | Forest ou Island (Hinterland Harbor) | qualquer um dos três pares |\n|---|---|---|---|---|")
for T in (2, 3, 4, 5):
    n = a = b = c = qq = 0
    for j in J:
        r = next((x for x in j if x[0] == T - 1), None)
        if r is None: continue
        n += 1; ts = set(r[2])
        a += bool(ts & {"Swamp", "Forest"}); b += bool(ts & {"Island", "Swamp"}); c += bool(ts & {"Forest", "Island"}); qq += bool(ts)
    print(f"| T{T} (n = {n}) | {100 * a / n:.1f}% | {100 * b / n:.1f}% | {100 * c / n:.1f}% | {100 * qq / n:.1f}% |")

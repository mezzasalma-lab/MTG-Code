#!/usr/bin/env python3
"""Resume dados/cast_{padrao,resiliencia}.json.xz (castabilidade.py): por carta, % das partidas em que foi vista ate' T6 / T8 / T12, % em que foi conjurada, e entre as vistas ate' T8 quantas foram conjuradas;
e a fracao de partidas com >= 2 terrenos B e >= 2 G (BBGG) e >= 6 terrenos no fim de T5..T9. Uso: python3 resumo_cast.py > ../resumos/castabilidade.md"""
import json, lzma, os, statistics as st
ARQ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NOM = ["Atomize", "Casualties of War", "Assassin's Trophy"]
for modo in ("padrao", "resiliencia"):
    p = os.path.join(ARQ, "dados", f"cast_{modo}.json.xz")
    if not os.path.exists(p): continue
    d = json.load(lzma.open(p, "rt")); J = d["jogos"]; assert len(J) == d["n"] == 10000
    print(f"### {modo} (N = {d['n']}; {d['variante']})\n\n| carta | vista até T6 | até T8 | até T12 | conjurada (T12) | das vistas até T8, conjuradas | turno mediano da 1ª vez vista | turno mediano do cast |\n|---|---|---|---|---|---|---|---|")
    for k, nome in enumerate(NOM):
        vis = {}; cast = {}
        for gi, j in enumerate(J):
            for t, nl, b, g, v, c in j:
                if v[k] and gi not in vis: vis[gi] = t
                if c[k] > 0 and gi not in cast: cast[gi] = t
        n = len(J); f = lambda T: 100 * sum(1 for t in vis.values() if t <= T) / n
        v8 = [gi for gi, t in vis.items() if t <= 8]
        print(f"| {nome} | {f(6):.1f}% | {f(8):.1f}% | {f(12):.1f}% | {100 * len(cast) / n:.1f}% | {100 * sum(1 for gi in v8 if gi in cast) / max(1, len(v8)):.1f}% | {st.median(vis.values()):.0f} | {st.median(cast.values()) if cast else float('nan'):.0f} |")
    print("\n| fim do turno | partidas com ≥ 2 terrenos B e ≥ 2 G (BBGG) | ≥ 6 terrenos | BBGG e ≥ 6 terrenos | ≥ 1 B e ≥ 1 G (BG) e ≥ 2 terrenos |\n|---|---|---|---|---|")
    for T in range(4, 10):
        tot = bg2 = l6 = both = bg = 0
        for j in J:
            r = next((x for x in j if x[0] == T), None)
            if r is None: continue
            tot += 1; _, nl, b, g, _, _ = r
            bg2 += b >= 2 and g >= 2; l6 += nl >= 6; both += b >= 2 and g >= 2 and nl >= 6; bg += b >= 1 and g >= 1 and nl >= 2
        print(f"| T{T} (n = {tot}) | {100 * bg2 / tot:.1f}% | {100 * l6 / tot:.1f}% | {100 * both / tot:.1f}% | {100 * bg / tot:.1f}% |")
    print()

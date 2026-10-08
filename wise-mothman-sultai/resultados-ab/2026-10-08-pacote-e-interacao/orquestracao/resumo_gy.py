#!/usr/bin/env python3
"""Cemiterio dos oponentes por turno (Drown in the Loch conta o cemiterio do CONTROLADOR do alvo): le SO' dos brutos dados/gy_oponentes_{padrao,resiliencia}.json.xz.
Por turno T (fim do MEU turno), sobre (partida, oponente VIVO): mediana, media, % com >= 3/5/7/10 cartas; e, por partida, % em que o MELHOR oponente vivo tem >= k.
So' conta o que o MEU mill poe: os oponentes do simulador sao passivos (sem magias, sem criaturas mortas), entao e' PISO do cemiterio real. Uso: python3 resumo_gy.py > ../resumos/gy_oponentes.md"""
import json, lzma, os, statistics as st
ARQ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for modo in ("padrao", "resiliencia"):
    p = os.path.join(ARQ, "dados", f"gy_oponentes_{modo}.json.xz")
    if not os.path.exists(p): print(f"(sem {modo})"); continue
    d = json.load(lzma.open(p, "rt")); J = d["jogos"]; assert len(J) == d["n"] == 10000 and sum(len(j) for j in J) > 0
    print(f"### Modo {modo} (N = {d['n']}, sementes {d['sementes']})\n")
    print("| fim do meu turno | pares (partida, oponente vivo) | mediana | média | ≥3 | ≥5 | ≥7 | ≥10 | melhor oponente vivo ≥5 | ≥7 |\n|---|---|---|---|---|---|---|---|---|---|")
    for T in range(2, 11):
        xs = []; mx = []
        for j in J:
            for t, ops in j:
                if t == T:
                    v = [a for a, e in ops if not e]; xs += v
                    if v: mx.append(max(v))
        if not xs: continue
        n = len(xs); f = lambda k: "%.0f%%" % (100 * sum(1 for x in xs if x >= k) / n)
        g = lambda k: "%.0f%%" % (100 * sum(1 for x in mx if x >= k) / len(mx))
        print(f"| T{T} | {n} | {st.median(xs):.0f} | {st.mean(xs):.1f} | {f(3)} | {f(5)} | {f(7)} | {f(10)} | {g(5)} | {g(7)} |")
    print()

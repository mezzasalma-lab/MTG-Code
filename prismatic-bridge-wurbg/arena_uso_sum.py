"""Resumo de arena_uso.py: o que a Arena Rector entrega no simulador e o que acontece com a Sisay no mesmo slot.
Uso: python3 arena_uso_sum.py <prefixo>   (le <prefixo>_*.json)"""
import glob
import json
import statistics as st
import sys
from collections import Counter

AR, SIS = "Arena Rector", "Sisay, Weatherlight Captain"
D = {"base": {"std": [], "res": []}, "sisay": {"std": [], "res": []}}
for f in sorted(glob.glob(f"{sys.argv[1]}_*.json")):
    r = json.load(open(f))
    for lista in D:
        for m in D[lista]:
            D[lista][m] += r[lista][m]


def rel(lista, modo, nome):
    g = D[lista][modo]
    n = len(g)
    ent = [x for x in g if nome in x.get("entered_turns", {})]
    morreu = [x for x in ent if any(c[0] == nome and not c[2] for c in x.get("left", []))]
    exilou = [x for x in ent if any(c[0] == nome and c[2] for c in x.get("left", []))]
    trig = [x for x in ent if x.get("triggers")] if nome == AR else []
    primeiro = [min(x["entered_turns"][nome]) for x in ent]
    fontes = Counter()
    for x in ent:
        vistos = {(c[1], "exílio" if c[2] else "morte") for c in x.get("left", []) if c[0] == nome}
        for s in vistos:
            fontes[s] += 1
    print(f"### lista {lista} / {modo} / {nome}: n={n}; entrou em {len(ent)} ({100 * len(ent) / n:.1f}%); turno mediano {st.median(primeiro) if primeiro else '-'}")
    print(f"- saiu por morte: {len(morreu)} ({100 * len(morreu) / max(1, len(ent)):.1f}% das que entraram); por exílio: {len(exilou)} ({100 * len(exilou) / max(1, len(ent)):.1f}%)")
    if nome == AR:
        print(f"- gatilho (busca de PW) disparou: {len(trig)} ({100 * len(trig) / max(1, len(ent)):.1f}% das que entraram; {100 * len(trig) / n:.1f}% de todas as partidas)")
        achou, fonte = Counter(), Counter()
        for x in trig:
            t = x["triggers"][0]
            achou[t[1]] += 1
            fonte[t[0]] += 1
        print("- PW buscado (1º disparo):", achou.most_common(8))
        print("- fonte da morte que disparou:", fonte.most_common())
    print("- fontes de saída (nº de partidas):", fontes.most_common())
    print()


for m in ("std", "res"):
    rel("base", m, AR)
for m in ("std", "res"):
    rel("sisay", m, SIS)

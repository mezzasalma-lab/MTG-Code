"""Sensibilidade da convenção do Exotic Orchard no simulador do Tom (Regra #5: convenção do simulador != regra real).
Convenção atual (tom_goldfish_v1.py, add_land): Orchard produz 1 mana SEM cor (não há terreno de oponente no goldfish).
Na mesa real (Commander, 3 oponentes) o Orchard quase sempre faz qualquer cor. Variante 'orchard_any' = Orchard produz W/U/B/R/G.
Pareado: mesma semente (1_000_000+i) nas duas variantes; 10 turnos; modo padrão (simulate_one).
Uso:  python3 orchard_sens.py run <parte> <npartes> <N> <saida.json>
      python3 orchard_sens.py sum <prefixo>          (lê <prefixo>_*.json)"""
import dataclasses
import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tom_goldfish_v1 as tg

ORIG = tg.CARD_DB["Exotic Orchard"]


def set_variant(v):
    tg.CARD_DB["Exotic Orchard"] = ORIG if v == "base" else dataclasses.replace(ORIG, produces=frozenset(tg.WUBRG))


def run(part, nparts, N, out):
    res = {"base": [], "orchard_any": []}
    for v in res:
        set_variant(v)
        for i in range(part, N, nparts):
            s = tg.simulate_one(1_000_000 + i, turns=10)
            orch = any(tg.eff_name(p) == "Exotic Orchard" for p in s.battlefield)
            res[v].append({"i": i, "tom": s.commander_cast_turn, "trig": s.tom_triggers, "put": s.tom_sagas_put,
                           "mana": s.mana_by_turn, "orch": orch, "lethal": s.lethal_turn})
    json.dump(res, open(out, "w"))
    print("ok", part, flush=True)


def load(prefix):
    D = {"base": [], "orchard_any": []}
    for f in sorted(glob.glob(f"{prefix}_*.json")):
        d = json.load(open(f))
        for v in D:
            D[v].extend(d[v])
    for v in D:
        D[v].sort(key=lambda r: r["i"])
    return D


def pdiff(a, b):
    d = [y - x for x, y in zip(a, b)]
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1))
    return m, 1.96 * sd / math.sqrt(len(d))


def fmt(m, ci, pct=True):
    s = f"{100 * m:+.1f} pp ±{100 * ci:.1f}" if pct else f"{m:+.2f} ±{ci:.2f}"
    return f"**{s}**" if abs(m) > ci else s


def summarize(prefix):
    D = load(prefix)
    B, A = D["base"], D["orchard_any"]
    n = len(B)
    print(f"N = {n} partidas pareadas (sementes 1_000_000+i, 10 turnos, modo padrão)\n")
    print("| métrica | convenção atual (Orchard incolor) | Orchard qualquer cor | Δ pareado (IC95%) |")
    print("|---|---|---|---|")
    for T in (4, 5, 6, 7, 8):
        a = [1 if r["tom"] is not None and r["tom"] <= T else 0 for r in B]
        b = [1 if r["tom"] is not None and r["tom"] <= T else 0 for r in A]
        print(f"| Tom lançado até o T{T} | {100 * sum(a) / n:.1f}% | {100 * sum(b) / n:.1f}% | {fmt(*pdiff(a, b))} |")
    a = [1 if r["tom"] is None else 0 for r in B]
    b = [1 if r["tom"] is None else 0 for r in A]
    print(f"| Tom nunca lançado em 10 turnos | {100 * sum(a) / n:.1f}% | {100 * sum(b) / n:.1f}% | {fmt(*pdiff(a, b))} |")
    for k in (1, 2):
        a = [1 if r["trig"] >= k else 0 for r in B]
        b = [1 if r["trig"] >= k else 0 for r in A]
        print(f"| ≥ {k} gatilho(s) do Tom até o T10 | {100 * sum(a) / n:.1f}% | {100 * sum(b) / n:.1f}% | {fmt(*pdiff(a, b))} |")
    for T in (4, 5, 6):
        a = [r["mana"][T - 1] for r in B]
        b = [r["mana"][T - 1] for r in A]
        print(f"| mana gasta/disponível no T{T} (média de `mana_by_turn`) | {sum(a) / n:.2f} | {sum(b) / n:.2f} | {fmt(*pdiff(a, b), pct=False)} |")
    idx = [i for i in range(n) if B[i]["orch"] or A[i]["orch"]]
    print(f"\nCondicional: partidas com Exotic Orchard em campo no fim (em alguma das variantes): {len(idx)} de {n} ({100 * len(idx) / n:.1f}%)")
    for T in (5, 6):
        a = [1 if B[i]["tom"] is not None and B[i]["tom"] <= T else 0 for i in idx]
        b = [1 if A[i]["tom"] is not None and A[i]["tom"] <= T else 0 for i in idx]
        print(f"- Tom lançado até o T{T} nessas partidas: {100 * sum(a) / len(a):.1f}% → {100 * sum(b) / len(b):.1f}% ({fmt(*pdiff(a, b))})")
    dif = sum(1 for i in range(n) if B[i]["tom"] != A[i]["tom"])
    print(f"\nPartidas em que o turno de lançamento do Tom mudou: {dif} de {n} ({100 * dif / n:.1f}%)")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        summarize(sys.argv[2])

"""Pares que ocupam o slot da Arena Rector (2026-09-29): Sisay + Loyal Tutor / Sisay + Tam / Tam + Loyal Tutor.
Uso: python3 ab_pares_sum.py <prefixo_main...> -- <prefixo_pares...>
Diferencas SEMPRE pareadas (mesmas seeds), IC95%; negrito = intervalo nao cruza 0.
Tabela 1: cada variante contra a lista atual. Tabela 2: contra o par Tam + Loyal Tutor (o pacote FRA sem o Entrust)."""
import glob
import json
import math
import sys

args = sys.argv[1:]
k = args.index("--")
data = {}
for prefix in args[:k] + args[k + 1:]:
    for f in sorted(glob.glob(f"{prefix}_*.json")):
        for key, v in json.load(open(f)).items():
            if key == "base" and "base" in data:
                continue
            data.setdefault(key, {}).update(v)   # modos (std/res) se juntam; prefixo posterior sobrescreve o mesmo modo
SIS, TAM, LT = "Sisay, Weatherlight Captain", "Tam, the Possibility", "Loyal Tutor"
COLS = [("padrão: 1º ult (turno)", "std", "first_ult", lambda x: x, False),
        ("padrão: P(ult ≤ T8)", "std", "first_ult", lambda x: 1 if x <= 8 else 0, True),
        ("resil.: vida ≤ 0", "res", "died", lambda x: x, True),
        ("resil.: 1º ult", "res", "first_ult", lambda x: x, False),
        ("resil.: PW-turnos vivos", "res", "pw_turns_alive", lambda x: x, False),
        ("resil.: P(dano ≥ 40)", "res", "our_dmg", lambda x: 1 if x >= 40 else 0, True),
        ("resil.: P(dano ≥ 120)", "res", "our_dmg", lambda x: 1 if x >= 120 else 0, True)]
PARES = [("Sisay + Loyal Tutor (saem Arena Rector + Swan Song)", f"{SIS}|Arena Rector+{LT}|Swan Song"),
         ("Sisay + Tam (saem Arena Rector + Swan Song)", f"{SIS}|Arena Rector+{TAM}|Swan Song"),
         ("Tam + Loyal Tutor (saem Arena Rector + Swan Song)", f"{TAM}|Arena Rector+{LT}|Swan Song")]


def diff(v, w, mode, key, fn):
    a = [fn(g[key]) for g in data[w][mode]]
    b = [fn(g[key]) for g in data[v][mode]]
    d = [y - x for x, y in zip(a, b)]
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1))
    return m, 1.96 * sd / math.sqrt(len(d))


def fmt(t, pct):
    m, ci = t
    s = f"{100 * m:+.2f} pp ±{100 * ci:.2f}" if pct else f"{m:+.3f} ±{ci:.3f}"
    return f"**{s}**" if abs(m) > ci else s


def table(title, rows, ref):
    print(f"#### {title}\n")
    print("| variante | " + " | ".join(c[0] for c in COLS) + " |")
    print("|---|" + "---|" * len(COLS))
    for label, v in rows:
        if v not in data:
            continue
        print(f"| {label} | " + " | ".join(fmt(diff(v, ref, m, kk, fn), pct) if m in data[v] and m in data[ref] else "—"
                                          for _, m, kk, fn, pct in COLS) + " |")
    print()


CORTES = [(f"Sisay no lugar de {c}", f"{SIS}|{c}") for c in
          ("Arena Rector", "Swan Song", "Veil of Summer", "Oath of Nissa", "Farseek", "Doubling Season")]
table("0. Sisay sozinha em cada corte (padrão: dados sem mudança; resiliência: política final da Liliana, que poupa a Sisay)",
      CORTES + [("Sisay no lugar de Arena Rector, política ANTIGA da Liliana (sacrifica a Sisay)",
                 f"{SIS}|Arena Rector@liliana_spares_sisay")], "base")
table("1. Cada par contra a lista atual", PARES, "base")
table("2. Cada par contra Tam + Loyal Tutor (positivo em 'P(...)' e negativo em 'vida ≤ 0/1º ult' = melhor que o par FRA)",
      PARES[:2], PARES[2][1])

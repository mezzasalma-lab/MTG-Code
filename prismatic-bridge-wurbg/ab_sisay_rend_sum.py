"""Sisay com a janela de fim de rodada (busca no end step do ultimo oponente com a mana que sobrou; chave `sisay_round_end`).
Uso: python3 ab_sisay_rend_sum.py <prefixo...>   (le <prefixo>_*.json; std/res de rodadas diferentes se juntam)
Chaves com "@sisay_round_end" = janela LIGADA (o padrao e' desligada). Diferencas SEMPRE pareadas, IC95%; negrito = IC nao cruza 0."""
import glob
import json
import math
import sys

data = {}
for prefix in sys.argv[1:]:
    for f in sorted(glob.glob(f"{prefix}_*.json")):
        for key, v in json.load(open(f)).items():
            if key == "base" and "base" in data:
                continue
            data.setdefault(key, {}).update(v)
S, TAM, LT = "Sisay, Weatherlight Captain", "Tam, the Possibility", "Loyal Tutor"
R = "@sisay_round_end"
COLS = [("padrão: 1º ult (turno)", "std", "first_ult", lambda x: x, False),
        ("padrão: P(ult ≤ T8)", "std", "first_ult", lambda x: 1 if x <= 8 else 0, True),
        ("resil.: vida ≤ 0", "res", "died", lambda x: x, True),
        ("resil.: 1º ult", "res", "first_ult", lambda x: x, False),
        ("resil.: PW-turnos vivos", "res", "pw_turns_alive", lambda x: x, False),
        ("resil.: P(dano ≥ 40)", "res", "our_dmg", lambda x: 1 if x >= 40 else 0, True),
        ("resil.: P(dano ≥ 120)", "res", "our_dmg", lambda x: 1 if x >= 120 else 0, True)]


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
        if v not in data or ref not in data:
            continue
        print(f"| {label} | " + " | ".join(fmt(diff(v, ref, m, kk, fn), pct) if m in data[v] and m in data[ref] else "—"
                                          for _, m, kk, fn, pct in COLS) + " |")
    print()


FRA = f"{TAM}|Arena Rector+{LT}|Swan Song"
table("1. Sisay COM a janela de fim de rodada, no lugar de cada carta (Δ sobre a lista atual)",
      [("Sisay no lugar de Arena Rector", f"{S}|Arena Rector{R}"), ("Sisay no lugar de Swan Song", f"{S}|Swan Song{R}"),
       ("Sisay no lugar de Veil of Summer", f"{S}|Veil of Summer{R}"),
       ("Sisay + Loyal Tutor (saem Arena Rector + Swan Song)", f"{S}|Arena Rector+{LT}|Swan Song{R}"),
       ("Sisay + Tam (saem Arena Rector + Swan Song)", f"{S}|Arena Rector+{TAM}|Swan Song{R}"),
       ("Tam + Loyal Tutor + Sisay (a Sisay no lugar do Veil of Summer)", f"{FRA}+{S}|Veil of Summer{R}")], "base")
for titulo, rows in (("2. O que a janela SOMA à Sisay (com a janela − sem a janela, mesmo slot)",
                      [("Sisay no lugar de Arena Rector", f"{S}|Arena Rector{R}", f"{S}|Arena Rector"),
                       ("Sisay no lugar de Swan Song", f"{S}|Swan Song{R}", f"{S}|Swan Song"),
                       ("Sisay no lugar de Veil of Summer", f"{S}|Veil of Summer{R}", f"{S}|Veil of Summer"),
                       ("Sisay + Loyal Tutor", f"{S}|Arena Rector+{LT}|Swan Song{R}", f"{S}|Arena Rector+{LT}|Swan Song"),
                       ("Sisay + Tam", f"{S}|Arena Rector+{TAM}|Swan Song{R}", f"{S}|Arena Rector+{TAM}|Swan Song"),
                       ("Tam + Loyal Tutor + Sisay", f"{FRA}+{S}|Veil of Summer{R}", f"{FRA}+{S}|Veil of Summer")]),):
    print(f"#### {titulo}\n")
    print("| variante | " + " | ".join(c[0] for c in COLS) + " |")
    print("|---|" + "---|" * len(COLS))
    for label, v, w in rows:
        if v not in data or w not in data:
            continue
        print(f"| {label} | " + " | ".join(fmt(diff(v, w, m, kk, fn), pct) if m in data[v] and m in data[w] else "—"
                                          for _, m, kk, fn, pct in COLS) + " |")
    print()
table("3. Sisay COM a janela contra as outras cartas no MESMO slot da Arena Rector (Sisay − outra; negativo em 1º ult/vida = Sisay melhor)",
      [("Sisay (com a janela) − Tam", f"{S}|Arena Rector{R}"), ], f"{TAM}|Arena Rector")
table("3b. idem contra o Loyal Tutor", [("Sisay (com a janela) − Loyal Tutor", f"{S}|Arena Rector{R}")], f"{LT}|Arena Rector")
table("3c. Par Sisay (com a janela) + Loyal Tutor contra Tam + Loyal Tutor", [("Sisay+LT (janela) − Tam+LT", f"{S}|Arena Rector+{LT}|Swan Song{R}")], FRA)

print("#### 4. Uso da janela (partidas em que a Sisay entrou; slot Arena Rector)\n")
print("| modo | partidas em que entrou | com ≥ 1 busca no fim da rodada | média de buscas no fim da rodada (das que entraram) | média de buscas no total |")
print("|---|---|---|---|---|")
for m in ("std", "res"):
    g = [x["cs"] for x in data[f"{S}|Arena Rector{R}"][m] if x["cs"].get("entered_" + S, 0) > 0]
    n = len(g)
    if not n:
        continue
    re_ = sum(1 for c in g if c.get("sisay_round_end_activations", 0) > 0)
    print(f"| {m} | {n} | {re_} ({100 * re_ / n:.1f}%) | {sum(c.get('sisay_round_end_activations', 0) for c in g) / n:.2f} | "
          f"{sum(c.get('sisay_activations', 0) for c in g) / n:.2f} |")
print()

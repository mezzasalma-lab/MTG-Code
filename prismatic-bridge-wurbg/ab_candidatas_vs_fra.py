"""As 4 candidatas de 2026-09-29 contra as 3 de Reality Fracture (Tam, Loyal Tutor, Entrust the Spark) NOS MESMOS slots.
Uso: python3 ab_candidatas_vs_fra.py <prefixo_main> <prefixo_fra>
  main = saida de ab_candidatas.py (base + candidatas sozinhas); fra = saida de ab_candidatas.py com as variantes:
  singles no slot Arena Rector; pacote FRA (Tam→Arena Rector, Loyal Tutor→Swan Song, Entrust→Veil of Summer);
  terceiro slot trocado (Veil of Summer sai; entra a candidata no lugar do Entrust); quarta carta (candidata→Oath of Nissa).
Diferencas SEMPRE pareadas (mesmas seeds), IC95%; negrito = intervalo nao cruza 0."""
import glob
import json
import math
import sys

data = {}
for prefix in sys.argv[1:]:
    for f in sorted(glob.glob(f"{prefix}_*.json")):
        for k, v in json.load(open(f)).items():
            if k == "base" and "base" in data:
                continue
            data.setdefault(k, {}).update(v)   # junta std/res de rodadas diferentes; prefixo posterior sobrescreve o mesmo modo
base = "base"
N = len(data[base]["res"])
D, G, V, S = "Dihada, Binder of Wills", "Commodore Guff", "Vronos, Masked Inquisitor", "Sarkhan the Masterless"
SIS = "Sisay, Weatherlight Captain"
FRA = "Tam, the Possibility|Arena Rector+Loyal Tutor|Swan Song"
ENT3 = f"{FRA}+Entrust the Spark|Veil of Summer"
COLS = [("padrão: 1º ult (turno)", "std", "first_ult", lambda x: x, False),
        ("padrão: P(ult ≤ T8)", "std", "first_ult", lambda x: 1 if x <= 8 else 0, True),
        ("resil.: vida ≤ 0", "res", "died", lambda x: x, True),
        ("resil.: 1º ult", "res", "first_ult", lambda x: x, False),
        ("resil.: P(dano ≥ 40)", "res", "our_dmg", lambda x: 1 if x >= 40 else 0, True)]


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
        print(f"| {label} | " + " | ".join(fmt(diff(v, ref, m, k, fn), pct) for _, m, k, fn, pct in COLS) + " |")
    print()


table("1. Uma carta por vez no slot Arena Rector (Δ sobre a lista atual)",
      [("Loyal Tutor (FRA)", "Loyal Tutor|Arena Rector"), ("Tam (FRA)", "Tam, the Possibility|Arena Rector"),
       ("Entrust the Spark (FRA)", "Entrust the Spark|Arena Rector"), ("Dihada", f"{D}|Arena Rector"),
       ("Guff", f"{G}|Arena Rector"), ("Vronos", f"{V}|Arena Rector"), ("Sarkhan", f"{S}|Arena Rector"),
       ("Sisay", f"{SIS}|Arena Rector")], base)
table("2. Terceiro slot (Tam→Arena Rector e Loyal Tutor→Swan Song fixos; Veil of Summer sai). Δ sobre a lista atual",
      [("Tam + Loyal Tutor + **Entrust**", ENT3), ("Tam + Loyal Tutor + **Dihada**", f"{FRA}+{D}|Veil of Summer"),
       ("Tam + Loyal Tutor + **Guff**", f"{FRA}+{G}|Veil of Summer"), ("Tam + Loyal Tutor + **Vronos**", f"{FRA}+{V}|Veil of Summer"),
       ("Tam + Loyal Tutor + **Sarkhan**", f"{FRA}+{S}|Veil of Summer"),
       ("Tam + Loyal Tutor + **Sisay**", f"{FRA}+{SIS}|Veil of Summer")], base)
table("3. O mesmo terceiro slot, Δ sobre o pacote com Entrust (positivo em 'P(...)' e negativo em 'vida ≤ 0/1º ult' = melhor que o Entrust)",
      [("Dihada no lugar do Entrust", f"{FRA}+{D}|Veil of Summer"), ("Guff no lugar do Entrust", f"{FRA}+{G}|Veil of Summer"),
       ("Vronos no lugar do Entrust", f"{FRA}+{V}|Veil of Summer"), ("Sarkhan no lugar do Entrust", f"{FRA}+{S}|Veil of Summer"), ("Sisay no lugar do Entrust", f"{FRA}+{SIS}|Veil of Summer")], ENT3)
table("4. Quarta carta por cima do pacote FRA completo (Tam + Loyal Tutor + Entrust), entrando no lugar do Oath of Nissa. Δ sobre o pacote FRA",
      [("+ Dihada (sai Oath of Nissa)", f"{ENT3}+{D}|Oath of Nissa"), ("+ Guff (sai Oath of Nissa)", f"{ENT3}+{G}|Oath of Nissa"),
       ("+ Vronos (sai Oath of Nissa)", f"{ENT3}+{V}|Oath of Nissa"), ("+ Sarkhan (sai Oath of Nissa)", f"{ENT3}+{S}|Oath of Nissa"),
       ("+ Sisay (sai Oath of Nissa)", f"{ENT3}+{SIS}|Oath of Nissa")], ENT3)

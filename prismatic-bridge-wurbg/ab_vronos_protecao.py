"""Vronos +1 (phase out): o que o phase out protege de verdade? Le a saida de
`ab_candidatas.py --res-only` com as variantes base, Vronos, Vronos@vronos_phase (sem phase out) e o PW inerte.
Uso: python3 ab_vronos_protecao.py <prefixo>
Metricas alem das de sempre: soma da lealdade dos PWs no fim (`loy_end`), PWs no T10 e, com o phase out ligado,
quantos PWs foram tirados de fase. O A/B agregado de mortes de PW nao enxerga a QUALIDADE do que sobrevive
(o oponente simulado bate no de maior lealdade fora de fase; o phase out desvia o dano pros outros)."""
import glob
import json
import math
import sys

data = {}
for f in sorted(glob.glob(f"{sys.argv[1]}_*.json")):
    data.update(json.load(open(f)))
V = "Vronos, Masked Inquisitor|Arena Rector"
NO = V + "@vronos_phase"
CT = "Control PW (inerte)|Arena Rector"
base = data["base"]["res"]
N = len(base)


def paired(a_key, b_key, metric, fn=lambda x: x, sub=None):
    a = [fn(g[metric]) for g in data[a_key]["res"]]
    b = [fn(g[metric]) for g in data[b_key]["res"]]
    idx = sub if sub is not None else range(N)
    d = [b[i] - a[i] for i in idx]
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1))
    return m, 1.96 * sd / math.sqrt(len(d)), len(d)


def fmt(t, pct=False):
    m, ci, n = t
    s = f"{100 * m:+.2f} pp ±{100 * ci:.2f}" if pct else f"{m:+.3f} ±{ci:.3f}"
    return f"**{s}**" if abs(m) > ci else s


ent = [i for i, g in enumerate(data[V]["res"]) if g["cs"].get("entered_Vronos, Masked Inquisitor", 0) > 0]
ROWS = [("Δ soma da lealdade dos PWs no fim (cap 1000)", "loy_end", lambda x: min(x, 1000), False),
        ("Δ PWs vivos no T10 (cap 50)", "pw_end", lambda x: min(x, 50), False),
        ("Δ PW-turnos vivos", "pw_turns_alive", lambda x: x, False),
        ("Δ PWs mortos em combate", "pw_combat_deaths", lambda x: x, False),
        ("Δ dano de combate recebido pelos PWs (cap 1000)", "pw_combat_damage", lambda x: min(x, 1000), False),
        ("Δ remoções sofridas", "removals", lambda x: x, False),
        ("Δ vida ≤ 0", "died", lambda x: x, True),
        ("Δ 1º ultimate (turno)", "first_ult", lambda x: x, False)]
for title, sub in (("todas as partidas", None), (f"só as {len(ent)} partidas em que o Vronos entrou", ent)):
    print(f"#### Vronos: onde o phase out aparece ({title}; n={N if sub is None else len(sub)})\n")
    print("| métrica | Vronos completo − base | Vronos sem phase out − base | phase out (completo − sem) | Vronos − PW inerte |")
    print("|---|---|---|---|---|")
    for label, key, fn, pct in ROWS:
        print(f"| {label} | {fmt(paired('base', V, key, fn, sub), pct)} | {fmt(paired('base', NO, key, fn, sub), pct)} | "
              f"{fmt(paired(NO, V, key, fn, sub), pct)} | {fmt(paired(CT, V, key, fn, sub), pct)} |")
    print()
phased = [g["cs"].get("vronos_phased_out", 0) for i, g in enumerate(data[V]["res"]) if i in set(ent)]
print(f"PWs tirados de fase por partida em que o Vronos entrou: média {sum(phased) / len(phased):.2f}, "
      f"P(>0) {100 * sum(1 for x in phased if x > 0) / len(phased):.1f}%")

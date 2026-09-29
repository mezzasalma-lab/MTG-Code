"""Arena Rector com a linha DELIBERADA (Damn/Void Rend na propria Arena Rector) contra a lista atual e contra a Sisay no slot dela.
Uso: python3 ab_arena_outlet_sum.py <prefixo...>   (le <prefixo>_*.json; std/res de rodadas diferentes se juntam)
Chaves: "base@arena_rector_outlet" = linha ligada ANTES da mao (teto);
        "base@arena_rector_outlet,arena_rector_outlet_pre_hand" = linha ligada so' com a mana que sobra depois da mao."""
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
SIS = "Sisay, Weatherlight Captain"
PRE, POST = "base@arena_rector_outlet", "base@arena_rector_outlet,arena_rector_outlet_pre_hand"
SISAY_AR = f"{SIS}|Arena Rector"
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
        if v not in data:
            continue
        print(f"| {label} | " + " | ".join(fmt(diff(v, ref, m, kk, fn), pct) if m in data[v] and m in data[ref] else "—"
                                          for _, m, kk, fn, pct in COLS) + " |")
    print()


table("1. O que a linha deliberada vale PRA Arena Rector (lista atual com a linha ligada − lista atual)",
      [("linha antes da mão (teto)", PRE), ("linha só com a mana que sobra", POST)], "base")
for titulo, ref in (("2. Sisay no lugar da Arena Rector − Arena Rector com a linha ANTES da mão (negativo em 1º ult/vida = Sisay melhor)", PRE),
                    ("3. Sisay no lugar da Arena Rector − Arena Rector com a linha SÓ com a mana que sobra", POST)):
    table(titulo, [("Sisay", SISAY_AR)], ref)

print("#### 4. Uso da linha deliberada (por partida, N = 3.000 por modo)\n")
print("| variante | modo | partidas com a linha usada | Damn | Void Rend |")
print("|---|---|---|---|---|")
for label, v in (("antes da mão", PRE), ("só com a mana que sobra", POST)):
    for m in ("std", "res"):
        g = data[v][m]
        n = len(g)
        d = sum(1 for x in g if x["cs"].get("arena_rector_outlet_Damn", 0) > 0)
        r = sum(1 for x in g if x["cs"].get("arena_rector_outlet_Void Rend", 0) > 0)
        alg = sum(1 for x in g if x["cs"].get("arena_rector_outlet_Damn", 0) + x["cs"].get("arena_rector_outlet_Void Rend", 0) > 0)
        print(f"| {label} | {m} | {alg} ({100 * alg / n:.1f}%) | {d} | {r} |")
print()

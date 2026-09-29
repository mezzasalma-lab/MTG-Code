"""Resumo do A/B pareado das candidatas de 2026-09-29 (Dihada, Guff, Vronos, Sarkhan).
Uso: python3 ab_candidatas_sum.py <prefixo> [<prefixo2> ...]
Le <prefixo>_*.json (saida de ab_candidatas.py; varios prefixos sao fundidos, o "base" vem do
primeiro que o tiver) e imprime tabelas em markdown.
Diferencas SEMPRE pareadas (mesma seed, a carta nova entra na linha da cortada); IC95%;
negrito = intervalo nao cruza 0. 'Condicional' = so' as partidas em que a candidata
entrou em campo (a mesma posicao da biblioteca nas duas versoes da partida)."""
import glob
import json
import math
import statistics as st
import sys

CANDS = {"Dihada, Binder of Wills": "Dihada", "Commodore Guff": "Guff",
         "Vronos, Masked Inquisitor": "Vronos", "Sarkhan the Masterless": "Sarkhan",
         "Control PW (inerte)": "CONTROLE (PW sem habilidade)"}
SLOTS = ["Arena Rector", "Swan Song", "Veil of Summer", "Oath of Nissa", "Farseek", "Doubling Season"]
PACK = ("Dihada, Binder of Wills|Arena Rector+Commodore Guff|Swan Song+"
        "Vronos, Masked Inquisitor|Veil of Summer+Sarkhan the Masterless|Oath of Nissa")

data = {}
for prefix in sys.argv[1:]:
    for f in sorted(glob.glob(f"{prefix}_*.json")):
        for k, v in json.load(open(f)).items():
            if k == "base" and "base" in data:
                continue
            data[k] = v
base = data["base"]
modes = [m for m in ("std", "res") if m in base]
N = len(base["res"])


def paired(v, mode, key, fn=lambda x: x, sub=None):
    a = [fn(g[key]) for g in base[mode]]
    b = [fn(g[key]) for g in data[v][mode]]
    idx = sub if sub is not None else range(len(a))
    d = [b[i] - a[i] for i in idx]
    if len(d) < 2:
        return 0.0, 0.0, len(d)
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1))
    return m, 1.96 * sd / math.sqrt(len(d)), len(d)


def fmt(t, pct=False):
    m, ci, _ = t
    s = f"{100 * m:+.2f} pp ±{100 * ci:.2f}" if pct else f"{m:+.3f} ±{ci:.3f}"
    return f"**{s}**" if abs(m) > ci else s


def entered(v, mode, cand):
    return [i for i, g in enumerate(data[v][mode]) if g["cs"].get("entered_" + cand, 0) > 0]


def cap(x):
    return min(x, 1000)


def mean(mode, key, fn=lambda x: x):
    return sum(fn(g[key]) for g in base[mode]) / N


print(f"### Base (n={N}, lista atual)\n")
if "std" in base:
    print(f"- padrão: 1º ultimate no turno {mean('std', 'first_ult'):.3f} | P(ult ≤ T8) "
          f"{100 * mean('std', 'first_ult', lambda x: 1 if x <= 8 else 0):.1f}% | turnos com ultimate {mean('std', 'turns_ult'):.3f}")
print(f"- resiliência: vida ≤ 0 {100 * mean('res', 'died'):.1f}% | "
      f"1º ult {mean('res', 'first_ult'):.3f} | PW-turnos vivos {mean('res', 'pw_turns_alive'):.2f} | "
      f"PWs mortos em combate {mean('res', 'pw_combat_deaths'):.3f} | PWs no T10 {mean('res', 'pw_end'):.2f}\n")

STD_COLS = [("Δ 1º ult (turno)", "first_ult", lambda x: x, False),
            ("Δ P(ult ≤ T8)", "first_ult", lambda x: 1 if x <= 8 else 0, True),
            ("Δ turnos c/ ult", "turns_ult", lambda x: x, False)]
RES_COLS = [("Δ vida ≤ 0", "died", lambda x: x, True),
            ("Δ 1º ult", "first_ult", lambda x: x, False),
            ("Δ PW-turnos vivos", "pw_turns_alive", lambda x: x, False),
            ("Δ PWs mortos em combate", "pw_combat_deaths", lambda x: x, False),
            ("Δ P(dano nosso ≥ 40)", "our_dmg", lambda x: 1 if x >= 40 else 0, True),
            ("Δ P(dano nosso ≥ 120)", "our_dmg", lambda x: 1 if x >= 120 else 0, True)]


def table(title, mode, cols, sub_mode=None):
    print(f"#### {title}\n")
    print("| candidata ↓ / sai → | " + " | ".join(SLOTS) + " |")
    print("|---|" + "---|" * len(SLOTS))
    for cname, short in CANDS.items():
        for label, key, fn, pct in cols:
            cells = []
            for slot in SLOTS:
                v = f"{cname}|{slot}"
                if v not in data:
                    cells.append("—")
                    continue
                sub = entered(v, mode, cname) if sub_mode else None
                cells.append(fmt(paired(v, mode, key, fn, sub), pct))
            print(f"| {short}: {label} | " + " | ".join(cells) + " |")
    print()


if "std" in base:
    table("Modo padrão — todas as partidas (incondicional)", "std", STD_COLS)
table("Resiliência — todas as partidas (incondicional)", "res", RES_COLS)
if "std" in base:
    table("Modo padrão — só as partidas em que a candidata entrou em campo (condicional)", "std", STD_COLS, sub_mode=True)
table("Resiliência — só as partidas em que a candidata entrou em campo (condicional)", "res", RES_COLS, sub_mode=True)

CTRL = "Control PW (inerte)"


def paired_vs(v, w, mode, key, fn=lambda x: x, sub=None):
    """Diferenca pareada entre duas variantes (v menos w), mesmas seeds."""
    a = [fn(g[key]) for g in data[w][mode]]
    b = [fn(g[key]) for g in data[v][mode]]
    idx = sub if sub is not None else range(len(a))
    d = [b[i] - a[i] for i in idx]
    if len(d) < 2:
        return 0.0, 0.0, len(d)
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1))
    return m, 1.96 * sd / math.sqrt(len(d)), len(d)


CTRL_SLOTS = [s for s in ("Arena Rector", "Swan Song") if f"{CTRL}|{s}" in data]
if CTRL_SLOTS:
    for cond in (False, True):
        print("#### Efeito das HABILIDADES: candidata menos o PW inerte no mesmo slot "
              f"({'só partidas em que ela entrou' if cond else 'todas as partidas'}; negativo em 1º ult/vida ≤ 0 = melhor)\n")
        print("| candidata | métrica | " + " | ".join(f"sai {s}" for s in CTRL_SLOTS) + " |")
        print("|---|---|" + "---|" * len(CTRL_SLOTS))
        for cname, short in list(CANDS.items())[:4]:
            for mode, cols in (("std", STD_COLS), ("res", RES_COLS)):
                if mode not in base:
                    continue
                for label, key, fn, pct in cols:
                    cells = []
                    for s in CTRL_SLOTS:
                        v, w = f"{cname}|{s}", f"{CTRL}|{s}"
                        if v not in data:
                            cells.append("—")
                            continue
                        sub = entered(v, mode, cname) if cond else None
                        cells.append(fmt(paired_vs(v, w, mode, key, fn, sub), pct))
                    print(f"| {short} | {'padrão' if mode == 'std' else 'resil.'} {label} | " + " | ".join(cells) + " |")
        print()

print("#### Presença: partidas em que a candidata entrou em campo\n")
print("| candidata | " + " | ".join(SLOTS) + " |")
print("|---|" + "---|" * len(SLOTS))
for cname, short in CANDS.items():
    for mode in modes:
        cells = []
        for slot in SLOTS:
            v = f"{cname}|{slot}"
            cells.append(f"{100 * len(entered(v, mode, cname)) / N:.1f}%" if v in data else "—")
        print(f"| {short} ({mode}) | " + " | ".join(cells) + " |")
print()

print("#### Uso por partida em que a carta entrou (slot Arena Rector; mediana | média limitada | P(>0))\n")
USE = {"Dihada, Binder of Wills": ["dihada_minus3", "dihada_plus2_targets", "dihada_legends_to_hand", "dihada_pws_to_hand",
                                  "dihada_milled", "dihada_milled_pw_or_creature", "dihada_treasures", "dihada_treasures_spent",
                                  "dihada_ult", "dihada_stolen_power"],
       "Commodore Guff": ["guff_plus1", "guff_wizards", "guff_wizard_mana", "guff_minus3", "guff_minus3_cards",
                          "guff_end_triggers", "guff_end_counters"],
       "Vronos, Masked Inquisitor": ["vronos_plus1", "vronos_phased_out", "vronos_minus2", "vronos_bounced", "vronos_ult",
                                     "vronos_attack_damage"],
       "Sarkhan the Masterless": ["sarkhan_plus1", "sarkhan_animated", "sarkhan_ready_attackers",
                                  "sarkhan_attack_power_potential", "sarkhan_attack_damage", "sarkhan_minus3",
                                  "sarkhan_ping_kills", "sarkhan_ping_damage"]}
for cname, keys in USE.items():
    v = f"{cname}|Arena Rector"
    if v not in data:
        continue
    for mode in modes:
        ent = [data[v][mode][i]["cs"] for i in entered(v, mode, cname)]
        if not ent:
            continue
        print(f"**{CANDS[cname]} — {mode}** (n={len(ent)} partidas com a carta em campo, de {N})\n")
        print("| métrica | mediana | média (cap 1000/partida) | P(>0) |")
        print("|---|---|---|---|")
        for k in keys:
            vals = [r.get(k, 0) for r in ent]
            print(f"| {k} | {st.median(vals):g} | {sum(min(x, 1000) for x in vals) / len(vals):.2f} | "
                  f"{100 * sum(1 for x in vals if x > 0) / len(vals):.1f}% |")
        ft = [r.get('first_turn_' + cname) for r in ent if r.get('first_turn_' + cname) is not None]
        if ft:
            print(f"| 1º turno em campo | {st.median(ft):g} | {sum(ft) / len(ft):.2f} | — |")
        print()

if PACK in data:
    print("#### Pacote: as 4 juntas (Dihada→Arena Rector, Guff→Swan Song, Vronos→Veil of Summer, Sarkhan→Oath of Nissa)\n")
    print("| métrica | Δ pareado |")
    print("|---|---|")
    if "std" in base:
        for label, key, fn, pct in STD_COLS:
            print(f"| padrão {label} | {fmt(paired(PACK, 'std', key, fn), pct)} |")
    for label, key, fn, pct in RES_COLS:
        print(f"| resiliência {label} | {fmt(paired(PACK, 'res', key, fn), pct)} |")
    print()

SENS = {"Dihada, Binder of Wills": ("dihada_minus3", "sem o −3 (só +2)"),
        "Commodore Guff": ("guff_minus3", "sem o −3 (só +1 e o gatilho de end step)"),
        "Vronos, Masked Inquisitor": ("vronos_phase", "+1 sem phase out (só +1 de lealdade)"),
        "Sarkhan the Masterless": ("sarkhan_animate", "+1 sem animar (só +1 de lealdade; Dragões do −3 e o estático ficam)")}
rows = [(c, f, d) for c, (f, d) in SENS.items() if f"{c}|Arena Rector@{f}" in data]
if rows:
    print("#### Sensibilidade: desligar o que carrega a carta (slot Arena Rector, Δ pareado vs base)\n")
    print("| candidata / política | " + " | ".join("padrão " + l for l, *_ in STD_COLS if "std" in base) + " | " +
          " | ".join("resil. " + l for l, *_ in RES_COLS[:5]) + " |")
    print("|---|" + "---|" * ((len(STD_COLS) if "std" in base else 0) + 5))
    for cname, flag, desc in rows:
        for label, v in (("política completa", f"{cname}|Arena Rector"), (desc, f"{cname}|Arena Rector@{flag}")):
            cells = []
            if "std" in base:
                cells += [fmt(paired(v, "std", key, fn), pct) for _, key, fn, pct in STD_COLS]
            cells += [fmt(paired(v, "res", key, fn), pct) for _, key, fn, pct in RES_COLS[:5]]
            print(f"| {CANDS[cname]}: {label} | " + " | ".join(cells) + " |")
    print()

"""
Reteste pareado — Magda, Brazen Outlaw DENTRO (com a implementacao real
corrigida: Firdoch Core e' um Dwarf via Changeling, dispara o gatilho
dela; a tag 'treasure_tutor_dragon' nunca tinha sido implementada antes)
vs. FORA (trocada por Ruby, Daring Tracker, decisao original de
2026-08-27 — invalidada pelo usuario, que apontou a sinergia real com
Firdoch Core que eu tinha ignorado).

Talisman of Impulse (a outra metade da troca original, cortando Lightning
Greaves) fica FIXO nas duas variantes — so a pergunta Magda-vs-Ruby e'
testada aqui.
"""

import statistics

import urdragon_goldfish_v1 as sim


def build_library(cuts, adds):
    lib = sim.BASE_LIBRARY[:]
    for c in cuts:
        lib.remove(c)
    for a in adds:
        lib.append(a)
    assert len(lib) == 99, len(lib)
    return lib


def run_variant(seed_base: int, n: int, library: list, turns: int = 8):
    original = sim.BASE_LIBRARY
    sim.BASE_LIBRARY = library
    try:
        states = [sim.simulate_one(seed_base + i, turns=turns) for i in range(n)]
    finally:
        sim.BASE_LIBRARY = original
    return states


def avg(vals):
    return sum(vals) / len(vals) if vals else 0.0


def summarize(label, states, n):
    cmd_turn = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    screwed = [s.first_color_screw_turn for s in states if s.first_color_screw_turn is not None]
    r = {
        "cmd_turn_avg": avg(cmd_turn),
        "never_cast_pct": 100*sum(1 for s in states if s.commander_cast_turn is None)/n,
        "color_screw_turns_avg": avg([s.color_screw_turns for s in states]),
        "color_screw_pct": 100*len(screwed)/n,
        "dragon_count_avg": avg([sim.dragon_count(s) for s in states]),
        "proxy_damage_avg": avg([s.proxy_damage_total for s in states]),
        "cards_drawn_avg": avg([s.cards_drawn_extra for s in states]),
        "magda_tutors_avg": avg([s.magda_tutors_total for s in states]),
        "tutors_used_avg": avg([s.tutors_used_total for s in states]),
    }
    print(f"--- {label} ---")
    for k, v in r.items():
        print(f"  {k}: {v:.3f}")
    print()
    return r


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    N = 3000
    SEED_BASE = 8400000

    # baseline atual da lista.md = Magda dentro, Talisman ja aplicado (Lightning Greaves ja cortada antes)
    lib_magda = sim.BASE_LIBRARY[:]
    assert len(lib_magda) == 99
    lib_ruby = build_library(["Magda, Brazen Outlaw"], ["Ruby, Daring Tracker"])

    print(f"n={N}, seed_base={SEED_BASE}, turns=8 (mesmas seeds)")
    print()

    states_magda = run_variant(SEED_BASE, N, lib_magda)
    r_magda = summarize("COM Magda (implementacao real corrigida)", states_magda, N)

    states_ruby = run_variant(SEED_BASE, N, lib_ruby)
    r_ruby = summarize("COM Ruby (Magda cortada)", states_ruby, N)

    print("=== Delta (Ruby - Magda) ===")
    for k in r_magda:
        print(f"  {k}: {r_ruby[k] - r_magda[k]:+.3f}")

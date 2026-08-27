"""
Teste comparativo pareado (mesmas seeds) — as DUAS trocas de B/U por R/G
e R/W juntas: Watery Grave -> Karplusan Forest (Teste #2) + Island ->
Battlefield Forge (este teste). Island e' o segundo candidato "puro"
(so U, nao toca nenhuma cor que falta) depois de Watery Grave — Swamp
(B puro) era a outra opcao, mas U tem o gap pior (-11,2pp vs -10,4pp de
B, auditoria 2026-08-24).

Battlefield Forge (R/W) foi escolhida em vez de outra R/G de proposito,
pra nao dobrar em cima do verde (que ja tem o menor gap dos 3
sub-representados, +5,5pp) e reforcar R (o maior gap, +23,0pp) + W
(+7,0/+8,6pp) ao mesmo tempo.
"""

import statistics

import urdragon_goldfish_v1 as sim


def build_double_swap_library():
    lib = sim.BASE_LIBRARY[:]
    lib.remove("Watery Grave")
    lib.append("Karplusan Forest")
    lib.remove("Island")
    lib.append("Battlefield Forge")
    assert len(lib) == 99
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
    print(f"--- {label} ---")
    print(f"Turno medio de conjuracao da Ur-Dragon: {avg(cmd_turn):.3f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em 8 turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.2f}%")
    print(f"Avg turnos com color screw: {avg([s.color_screw_turns for s in states]):.3f}")
    print(f"% jogos com >=1 turno de color screw: {100*len(screwed)/n:.2f}% | turno medio 1o screw: {avg(screwed):.3f}" if screwed else "0 jogos com color screw")
    print(f"Avg contagem de Dragoes em campo (fim): {avg([sim.dragon_count(s) for s in states]):.3f}")
    print()
    return {
        "cmd_turn_avg": avg(cmd_turn),
        "never_cast_pct": 100*sum(1 for s in states if s.commander_cast_turn is None)/n,
        "color_screw_turns_avg": avg([s.color_screw_turns for s in states]),
        "color_screw_pct": 100*len(screwed)/n,
        "dragon_count_avg": avg([sim.dragon_count(s) for s in states]),
    }


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    N = 3000
    SEED_BASE = 3300000

    lib_base = sim.BASE_LIBRARY[:]
    assert len(lib_base) == 99
    lib_swapped = build_double_swap_library()

    print(f"n={N}, seed_base={SEED_BASE}, turns=8 (mesmas seeds nas duas variantes)")
    print()

    states_base = run_variant(SEED_BASE, N, lib_base)
    r_base = summarize("BASELINE (Watery Grave + Island)", states_base, N)

    states_swapped = run_variant(SEED_BASE, N, lib_swapped)
    r_swapped = summarize("2 TROCAS (Karplusan Forest + Battlefield Forge)", states_swapped, N)

    print("=== Delta (2 trocas - baseline) ===")
    for k in r_base:
        d = r_swapped[k] - r_base[k]
        print(f"{k}: {d:+.3f}")

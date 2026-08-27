"""
Teste comparativo pareado (mesmas seeds) — Watery Grave vs. Karplusan
Forest no deck da Ur-Dragon, agora com o simulador de mana POR COR
(urdragon_goldfish_v1.py, reescrito em 2026-08-27).

Watery Grave (U/B) e a unica terra desta lista cujas DUAS cores sao as
mais sobre-representadas frente a demanda real de pips (auditoria
2026-08-27: U a -11,2pp, B a -10,4pp). Karplusan Forest (R/G, sem
tapped) cobre exatamente as 2 cores mais sub-representadas (R a
+23,0pp, G a +5,5pp).
"""

import statistics

import urdragon_goldfish_v1 as sim


def build_variant_library(cut_name: str, add_name: str):
    lib = sim.BASE_LIBRARY[:]
    lib.remove(cut_name)
    lib.append(add_name)
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
    print(f"% jogos com pelo menos 1 turno de color screw: {100*len(screwed)/n:.2f}% | turno medio 1o screw: {avg(screwed):.3f}" if screwed else "0 jogos com color screw")
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

    CUT = "Watery Grave"
    ADD = "Karplusan Forest"
    N = 3000
    SEED_BASE = 2200000

    lib_watery = sim.BASE_LIBRARY[:]
    assert len(lib_watery) == 99
    lib_karplusan = build_variant_library(CUT, ADD)

    print(f"n={N}, seed_base={SEED_BASE}, turns=8 (mesmas seeds nas duas variantes)")
    print()

    states_watery = run_variant(SEED_BASE, N, lib_watery)
    r_watery = summarize("COM Watery Grave (lista.md atual)", states_watery, N)

    states_karplusan = run_variant(SEED_BASE, N, lib_karplusan)
    r_karplusan = summarize(f"COM Karplusan Forest (Watery Grave trocada)", states_karplusan, N)

    print("=== Delta (Karplusan - Watery Grave) ===")
    for k in r_watery:
        d = r_karplusan[k] - r_watery[k]
        print(f"{k}: {d:+.3f}")

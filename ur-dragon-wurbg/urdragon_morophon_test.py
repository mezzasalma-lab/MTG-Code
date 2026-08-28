"""
Teste comparativo pareado (mesmas seeds) — adicionar Morophon, the
Boundless ao Ur-Dragon, testando 6 candidatos de corte diferentes contra
o baseline real (deck atual, sem Morophon).

Candidatos testados (cobrindo teorias diferentes de "carta mais fraca"):
- Sarkhan, Soul Aflame (CMC3): redundante com a propria Morophon (mesmo
  papel, redutor de custo de Dragao), mas barato — corta do slot de CMC
  mais cheio da curva (CMC3: 15 cartas) pra empilhar CMC7 (ja com 6).
- Ramos, Dragon Engine (CMC6): engine lento (precisa 5 contadores de cor
  acumulados), TAMBEM e' Dragao — trocar por Morophon mantem a contagem de
  Dragoes em campo neutra e desloca a curva so' +1 (CMC6->CMC7).
- Orb of Dragonkind (CMC2): mana restrita (so' Dragao) + tutor redundante
  com Sarkhan's Triumph, que ja esta na lista.
- Ruby, Daring Tracker (CMC2): dork so' 2 cores (R/G) num deck 5 cores,
  sem sinergia de Dragao nenhuma.
- Talisman of Impulse (CMC2): rock so' 2 cores (R/G), mesma logica da Ruby.
- Firdoch Core (CMC3): rock 5 cores real + ja e' Dragao (changeling) —
  candidato "controle", esperado ser um corte RUIM (fixacao de mana boa
  igual Morophon nao substitui).

Uso: python3 urdragon_morophon_test.py
"""

import statistics

import urdragon_goldfish_v1 as sim

CANDIDATES = [
    "Sarkhan, Soul Aflame",
    "Ramos, Dragon Engine",
    "Orb of Dragonkind",
    "Ruby, Daring Tracker",
    "Talisman of Impulse",
    "Firdoch Core",
]


def build_variant_library(cut_name: str, add_name: str = "Morophon, the Boundless"):
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
    d = {
        "label": label,
        "cmd_turn_avg": avg(cmd_turn),
        "never_cast_pct": 100 * sum(1 for s in states if s.commander_cast_turn is None) / n,
        "dragon_count_avg": avg([sim.dragon_count(s) for s in states]),
        "proxy_damage_avg": avg([s.proxy_damage_total for s in states]),
        "cards_drawn_extra_avg": avg([s.cards_drawn_extra for s in states]),
        "treasures_avg": avg([s.treasures_created_total for s in states]),
        "dragon_tokens_avg": avg([s.dragon_tokens for s in states]),
        "color_screw_pct": 100 * len(screwed) / n,
        "color_screw_turns_avg": avg([s.color_screw_turns for s in states]),
        "hand_final_avg": avg([len(s.hand) for s in states]),
    }
    print(f"--- {label} ---")
    print(f"Turno medio Ur-Dragon: {d['cmd_turn_avg']:.3f} | nunca conjurada: {d['never_cast_pct']:.2f}%")
    print(f"Avg Dragoes em campo (fim): {d['dragon_count_avg']:.3f} | Dragon tokens: {d['dragon_tokens_avg']:.3f}")
    print(f"Avg dano proxy total: {d['proxy_damage_avg']:.2f}")
    print(f"Avg cartas compradas extra: {d['cards_drawn_extra_avg']:.3f} | Treasures: {d['treasures_avg']:.3f}")
    print(f"Avg turnos color screw: {d['color_screw_turns_avg']:.3f} | % jogos com screw: {d['color_screw_pct']:.2f}%")
    print(f"Avg mao final: {d['hand_final_avg']:.3f}")
    print()
    return d


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    N = 3000
    SEED_BASE = 7600000  # mesmo seed_base oficial do urdragon_goldfish_v1.py, pra comparabilidade real

    baseline_states = run_variant(SEED_BASE, N, sim.BASE_LIBRARY)
    baseline = summarize("BASELINE (deck atual, sem Morophon)", baseline_states, N)

    results = [baseline]
    for cut in CANDIDATES:
        lib = build_variant_library(cut)
        states = run_variant(SEED_BASE, N, lib)
        results.append(summarize(f"CORTA {cut} + Morophon", states, N))

    print("=" * 100)
    print(f"{'Variante':45s} {'T.Ur-Dragon':>11s} {'NuncaCast%':>10s} {'Dragoes':>8s} {'DanoProxy':>10s} {'Draw':>6s} {'Screw%':>7s}")
    for r in results:
        print(f"{r['label']:45s} {r['cmd_turn_avg']:11.3f} {r['never_cast_pct']:10.2f} {r['dragon_count_avg']:8.3f} "
              f"{r['proxy_damage_avg']:10.2f} {r['cards_drawn_extra_avg']:6.2f} {r['color_screw_pct']:7.2f}")

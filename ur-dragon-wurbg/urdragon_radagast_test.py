"""
Teste comparativo pareado (mesmas seeds) — Radagast of Rhosgobel dentro vs.
fora do deck da Ur-Dragon. Mesma pergunta do usuario ja respondida pro
Ulalek, agora pro Ur-Dragon, DEPOIS da Correcao #2 (bug que excluia a
propria comandante de 5 dos 6 redutores de custo de Dragao — ver
goldfish-log.md).

Radagast of Rhosgobel ({2}{G}{G}, Legendary Creature — Avatar Wizard,
colors=['G'] — NAO e Dragao): "The first creature spell you cast each turn
costs {2} less to cast and can be cast as though it had flash."

Metodologia identica ao teste equivalente do Ulalek (`ulalek_radagast_test.py`):
monkeypatch temporario de `sim.BASE_LIBRARY`, mesma seed nas duas variantes.
"""

import random
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
    print(f"--- {label} ---")
    print(f"Turno medio de conjuracao da Ur-Dragon: {avg(cmd_turn):.3f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em 8 turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.2f}%")
    print(f"Avg contagem de Dragoes em campo (fim de jogo): {avg([sim.dragon_count(s) for s in states]):.3f}")
    print(f"Avg dobras via Roaming Throne: {avg([s.roaming_throne_doubles_total for s in states]):.3f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.3f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.3f}")
    print()
    return {
        "cmd_turn_avg": avg(cmd_turn),
        "never_cast_pct": 100*sum(1 for s in states if s.commander_cast_turn is None)/n,
        "dragon_count_avg": avg([sim.dragon_count(s) for s in states]),
        "roaming_throne_doubles_avg": avg([s.roaming_throne_doubles_total for s in states]),
        "draw_avg": avg([s.cards_drawn_extra for s in states]),
    }


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Firdoch Core NAO e mais um bom parceiro de troca de baixa
    # interferencia — o usuario apontou (corretamente, corrigido em
    # 2026-08-23) que ele e Changeling (tem o tipo Dragao em toda zona),
    # pega desconto de Eminence/etc e dispara dragon_enters() ao entrar. Um
    # corte dele confundiria o teste. Anguished Unmaking (remoção pontual,
    # proxy sem efeito colateral proprio neste simulador sem oponente real)
    # e um parceiro de troca de fato neutro em relacao as metricas medidas
    # aqui (turno de comandante, contagem de Dragao, motor de ETB).
    CUT = "Anguished Unmaking"
    ADD = "Radagast of Rhosgobel"
    N = 3000
    SEED_BASE = 5500000

    lib_without = sim.BASE_LIBRARY[:]
    assert len(lib_without) == 99
    lib_with = build_variant_library(CUT, ADD)

    print(f"n={N}, seed_base={SEED_BASE}, turns=8 (mesmas seeds nas duas variantes)")
    print()

    states_without = run_variant(SEED_BASE, N, lib_without)
    r_without = summarize("SEM Radagast (baseline, lista.md atual)", states_without, N)

    states_with = run_variant(SEED_BASE, N, lib_with)
    r_with = summarize(f"COM Radagast (corta 1x {CUT})", states_with, N)

    print("=== Delta (COM - SEM) ===")
    for k in r_without:
        d = r_with[k] - r_without[k]
        print(f"{k}: {d:+.3f}")

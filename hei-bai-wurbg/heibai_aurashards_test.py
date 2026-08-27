"""
Teste comparativo pareado (mesmas seeds) — Farewell vs. Aura Shards no
deck da Hei Bai. Pedido do usuario: trocar Farewell POR Aura Shards (nao
so adicionar), comparando os dois decks resultantes lado a lado.

Farewell e Aura Shards sao AMBAS Game Changers reais (confirmado contra
`is:gamechanger` ao vivo) — entao esta troca especifica MANTEM o deck em
3/3 Game Changers (perde uma, ganha outra), continua no teto do Bracket 3.
Isso e diferente de simplesmente ADICIONAR Aura Shards por cima da lista
atual, que empurraria pra 4/4 e Bracket 4 automaticamente.

Aura Shards ({1}{G}{W}, Enchantment): "Whenever a creature you control
enters, you may destroy target artifact or enchantment." Sem oponente
real modelado, tratada como interacao proxy disparada por ETB de
criatura (o deck cria MUITOS tokens de criatura — Honden of Life's Web,
Go-Shintai of Shared Purpose, Crescent Island Temple, o ativado da propria
Hei Bai, Hallowed Haunting a cada encantamento conjurado — entao a
frequencia real do gatilho e o que este teste mede).

Farewell (`{4}{W}{W}`, Sorcery, modal): tratada como interacao proxy de
1 uso (sorcery, sem gatilho repetivel).
"""

import random
import statistics

import heibai_goldfish_v1 as sim


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
    print(f"Turno medio de conjuracao da Hei Bai: {avg(cmd_turn):.3f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em 8 turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.2f}%")
    print(f"Avg Shrines em campo (fim): {avg([sim.shrine_count(s) for s in states]):.3f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.3f}")
    print(f"Avg tokens criados: {avg([s.tokens_created_total for s in states]):.3f}")
    print(f"Avg spells de interacao conjurados (proxy, TOTAL incl. Aura Shards): {avg([s.interaction_spells_cast_total for s in states]):.3f}")
    print(f"Avg destruicoes via Aura Shards: {avg([s.aura_shards_destroys_total for s in states]):.3f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.3f}")
    print()
    return {
        "cmd_turn_avg": avg(cmd_turn),
        "never_cast_pct": 100*sum(1 for s in states if s.commander_cast_turn is None)/n,
        "shrine_count_avg": avg([sim.shrine_count(s) for s in states]),
        "draw_avg": avg([s.cards_drawn_extra for s in states]),
        "tokens_avg": avg([s.tokens_created_total for s in states]),
        "interaction_avg": avg([s.interaction_spells_cast_total for s in states]),
        "aura_shards_avg": avg([s.aura_shards_destroys_total for s in states]),
    }


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    CUT = "Farewell"
    ADD = "Aura Shards"
    N = 3000
    SEED_BASE = 4400000

    lib_farewell = sim.BASE_LIBRARY[:]
    assert len(lib_farewell) == 99
    lib_aurashards = build_variant_library(CUT, ADD)

    print(f"n={N}, seed_base={SEED_BASE}, turns=8 (mesmas seeds nas duas variantes)")
    print()

    states_farewell = run_variant(SEED_BASE, N, lib_farewell)
    r_farewell = summarize("COM Farewell (lista.md atual)", states_farewell, N)

    states_aurashards = run_variant(SEED_BASE, N, lib_aurashards)
    r_aurashards = summarize("COM Aura Shards (Farewell trocado por Aura Shards)", states_aurashards, N)

    print("=== Delta (Aura Shards - Farewell) ===")
    for k in r_farewell:
        d = r_aurashards[k] - r_farewell[k]
        print(f"{k}: {d:+.3f}")

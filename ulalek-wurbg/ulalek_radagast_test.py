"""
Teste comparativo pareado (mesmas seeds) — Radagast of Rhosgobel dentro vs.
fora do deck da Ulalek, Fused Atrocity. Pergunta do usuario: "Vale a pena
incluir um Radagast no deck do Ulalek?"

Metodologia identica aos testes pareados anteriores desta biblioteca
(Maralen flash-vs-Radagast, Thranduil mana-fix): monkeypatch temporario de
`sim.BASE_LIBRARY` pra trocar 1 carta por Radagast of Rhosgobel, mesma seed
em ambas as variantes, restaura o estado original no final.

Carta cortada pro teste: **Null Elemental Blast** (interacao de 1 mana bem
estreita — "Counter target multicolored spell. / Destroy target
multicolored permanent." — em goldfish solo, sem oponente real, e a carta
com menor valor esperado medido por este simulador: so conta como
"interaction spell conjurado" generico, sem nenhum efeito colateral
proprio). Isso NAO e uma recomendacao de corte real — e so o parceiro de
troca escolhido pra manter a lista em 99 cartas nao-comandante durante o
teste, com o mínimo de interferencia possivel nas metricas medidas (turno
de Eldrazi, copias da Ulalek, janelas de flash).

Radagast of Rhosgobel ({2}{G}{G}, Legendary Creature — Avatar Wizard,
colors=['G'] — NAO colorless, NAO Eldrazi): "The first creature spell you
cast each turn costs {2} less to cast and can be cast as though it had
flash." Empilha com Conduit of Ruin (ja no deck, mesmo gatilho de "primeira
criatura do turno") — a mesma criatura recebe -2 de cada fonte presente, o
gatilho nao dobra pra descontar 2 criaturas por turno.
"""

import random
import statistics

import ulalek_goldfish_v1 as sim


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
    print(f"Turno medio de conjuracao da Ulalek: {avg(cmd_turn):.3f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em 8 turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.2f}%")
    print(f"Avg copias pagas da Ulalek (CC): {avg([s.ulalek_copies_total for s in states]):.3f}")
    print(f"Avg tokens-copia de permanentes: {avg([s.spell_token_copies_total for s in states]):.3f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.3f}")
    print(f"Avg turnos com flash online (qualquer fonte): {avg([s.flash_online_turns for s in states]):.3f}")
    print(f"Avg descontos de 'primeira criatura do turno' aplicados: {avg([s.first_creature_discount_events_total for s in states]):.3f}")
    print(f"Avg flash concedido pelo Radagast: {avg([s.radagast_flash_grants_total for s in states]):.3f}")
    print(f"Avg spells de interacao conjurados (proxy): {avg([s.interaction_spells_cast_total for s in states]):.3f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.3f}")
    print()
    return {
        "cmd_turn_avg": avg(cmd_turn),
        "never_cast_pct": 100*sum(1 for s in states if s.commander_cast_turn is None)/n,
        "ulalek_copies_avg": avg([s.ulalek_copies_total for s in states]),
        "spell_copies_avg": avg([s.spell_token_copies_total for s in states]),
        "draw_avg": avg([s.cards_drawn_extra for s in states]),
        "flash_online_avg": avg([s.flash_online_turns for s in states]),
        "first_creature_discount_avg": avg([s.first_creature_discount_events_total for s in states]),
        "radagast_flash_grants_avg": avg([s.radagast_flash_grants_total for s in states]),
    }


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    CUT = "Null Elemental Blast"
    ADD = "Radagast of Rhosgobel"
    N = 3000
    SEED_BASE = 9900000

    lib_without = sim.BASE_LIBRARY[:]
    assert len(lib_without) == 99
    lib_with = build_variant_library(CUT, ADD)

    print(f"n={N}, seed_base={SEED_BASE}, turns=8 (mesmas seeds nas duas variantes)")
    print()

    states_without = run_variant(SEED_BASE, N, lib_without)
    r_without = summarize(f"SEM Radagast (baseline, lista.md atual)", states_without, N)

    states_with = run_variant(SEED_BASE, N, lib_with)
    r_with = summarize(f"COM Radagast (corta 1x {CUT})", states_with, N)

    print("=== Delta (COM - SEM) ===")
    for k in r_without:
        d = r_with[k] - r_without[k]
        print(f"{k}: {d:+.3f}")

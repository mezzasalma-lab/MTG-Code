"""
Teste comparativo pareado (mesmas seeds) — adicionar Talisman of Impulse
(rock R/G) e Ruby, Daring Tracker (dork R/G, haste) no deck da Ur-Dragon,
pedido do usuario 2026-08-27 depois das 2 trocas de terreno ja aplicadas
(Watery Grave->Karplusan Forest, Island->Battlefield Forge).

Como sao NAO-terrenos, precisam cortar 2 cartas nao-terreno pra abrir
espaco (ao contrario das trocas de terreno anteriores). Candidatos de
corte escolhidos com justificativa, nao so palpite:

- **Lightning Greaves** (equipment, {2}, haste+shroud, equip {0}): util
  mas nao produz vantagem de carta nem mana — o deck ja tem Temur
  Ascendancy e Dragon Tempest dando haste de granca (`haste_all`,
  `haste_flying`), tornando Lightning Greaves parcialmente redundante
  como fonte de haste. Shroud e real mas situacional sem oponente
  modelado pra testar a protecao.
- **Magda, Brazen Outlaw** ({1}{R}, unico Dwarf do deck): "Other Dwarves
  get +1/+0" nunca dispara (so ela mesma), "whenever a Dwarf becomes
  tapped, create Treasure" so dispara nela mesma atacando (1
  Treasure/turno na melhor das hipoteses) — o unico texto realmente forte
  e "Sacrifice five Treasures: tutor artifact/Dragon pro campo", que
  exige acumular 5 Treasures primeiro (lento). Corpo fraco (nao e Dragao,
  nao tem ETB proprio).

Ambos os cortes sao testados TAMBEM isolados (so 1 troca por vez) alem
da combinacao das 2 juntas, pra saber a contribuicao de cada uma.
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
    SEED_BASE = 7100000

    variants = {
        "BASELINE": ([], []),
        "SO Talisman of Impulse (corta Lightning Greaves)": (["Lightning Greaves"], ["Talisman of Impulse"]),
        "SO Ruby, Daring Tracker (corta Magda)": (["Magda, Brazen Outlaw"], ["Ruby, Daring Tracker"]),
        "AMBAS (corta Lightning Greaves + Magda)": (["Lightning Greaves", "Magda, Brazen Outlaw"],
                                                       ["Talisman of Impulse", "Ruby, Daring Tracker"]),
    }

    print(f"n={N}, seed_base={SEED_BASE}, turns=8 (mesmas seeds em todas as variantes)")
    print()

    results = {}
    for label, (cuts, adds) in variants.items():
        lib = build_library(cuts, adds)
        states = run_variant(SEED_BASE, N, lib)
        results[label] = summarize(label, states, N)

    base = results["BASELINE"]
    for label in variants:
        if label == "BASELINE":
            continue
        print(f"=== Delta ({label} - BASELINE) ===")
        for k in base:
            print(f"  {k}: {results[label][k] - base[k]:+.3f}")
        print()

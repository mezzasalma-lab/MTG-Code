"""
Teste comparativo pareado (mesmas seeds) — 3 cartas do primer real que o
usuario usou de base pra montar o deck (compartilhado em 2026-08-29),
confirmadas fisicamente possuidas mas fora tanto do `lista.md` quanto do
`lista-fisica.md`: Chromatic Lantern, Kindred Discovery e Sarkhan
Unbroken. Rodado 1-a-1, 2-a-2 e as 3 juntas, sempre contra o mesmo pool de
corte (3 candidatas ja identificadas como as mais fracas do `lista.md`:
Birds of Paradise, Delighted Halfling, Ruby, Daring Tracker), pra isolar o
efeito real de cada adicao sem confundir com escolha de corte diferente a
cada teste.

Pareamento 1:1 candidata-nova <-> corte (mesma categoria/CMC aproximado):
- Birds of Paradise (dork, CMC1, WUBRG so' pra legendary via regra propria)
  <-> Chromatic Lantern (rock CMC4, fixacao real pra QUALQUER spell)
- Delighted Halfling (dork, CMC1, so' desconta legendary)
  <-> Kindred Discovery (enchantment CMC3, motor de draw real)
- Ruby, Daring Tracker (dork, CMC2, so' R/G)
  <-> Sarkhan Unbroken (planeswalker CMC5, GUR, ultimate poe TODOS os
       Dragoes da biblioteca em campo)

Efeitos implementados com mecanica real (Regra 3), verificados via
Scryfall (WebSearch, 2026-08-29), nao so tag:

- **Chromatic Lantern** ({4}, artifact): "Lands you control have '{T}: Add
  one mana of any color.' {T}: Add one mana of any color." Estatica
  poderosa — TODA terra em campo vira fonte de qualquer cor, alem da
  habilidade normal dela (nao substitui, adiciona). Implementado via patch
  em `color_sources()`: qualquer terra em campo conta pra qualquer cor
  quando Chromatic Lantern esta em campo (exceto a que acabou de entrar
  tapped nesse turno, igual todo resto). A propria Lantern tambem e' rock
  (+1 em `rocks_mana()`).
- **Kindred Discovery** ({3}, enchantment C17/CLB/LCC): "As this
  enchantment enters, choose a creature type. Whenever a creature you
  control of the chosen type enters or attacks, draw a card." Tipo
  escolhido = Dragao (obvio, tema central). Achado real: a versao inicial
  que eu tinha em mente ("combat damage to a player") estava ERRADA —
  conferido via Scryfall antes de implementar (Regra 1) e corrigido pra
  "enters or attacks", bem mais forte (dispara em ataque mesmo bloqueado/
  sem dano, e tambem no ETB). Implementado via 2 patches: `dragon_enters()`
  (ETB, nomeado ou token, sem "nontoken" no oraculo) e `combat_step()`
  (1 compra por Dragao atacante, MESMO calculo de `attacking_dragons` ja
  usado la). NAO e' dobrado por Roaming Throne — a habilidade pertence a
  Kindred Discovery (enchantment), nao a criatura Dragao em si (mesma
  distincao ja documentada pro Dragon's Hoard).
- **Sarkhan Unbroken** ({2}{G}{U}{R}, Planeswalker — Sarkhan, lealdade
  inicial 4): "+1: Draw a card, then add one mana of any color. -2: Create
  a 4/4 red Dragon creature token with flying. -8: Search your library for
  any number of Dragon creature cards, put them onto the battlefield, then
  shuffle." Lealdade rastreada de verdade (`state.sarkhan_loyalty`,
  atributo dinamico — GameState e' um dataclass sem __slots__, aceita
  atributo novo), 1 ativacao por TURNO (nao por main_phase — o jogo chama
  main_phase() 2x por turno, guardado via `state.sarkhan_activated_turn`).
  Heuristica documentada (Regra 9 categoria 12, precisa validacao do
  usuario): sempre +1 ate lealdade >= 8, depois sempre usa o ultimate na
  primeira chance — nunca usa o -2 (token unico nao compensa desviar do
  caminho pro ultimate, que poe TODOS os Dragoes da biblioteca em campo de
  graca). Num goldfish de 8 turnos, com lealdade inicial 4, o ultimate so'
  fica alcancavel se Sarkhan for conjurado ate o turno 4 (4 ativacoes de
  +1 = turno de cast +4). Morre por regra de estado (lealdade 0) assim que
  usa o ultimate — removido de battlefield/adicionado ao graveyard aqui.

Uso: python3 urdragon_primer3_test.py
"""

import random

import urdragon_goldfish_v1 as sim

# --- Registro dos 3 candidatos ------------------------------------------
sim.add("Chromatic Lantern", 4, "artifact", {"rock1"}, produces=set("WUBRG"))
sim.add("Kindred Discovery", 3, "enchantment", {"kindred_discovery"}, pips={"G": 1})
sim.add("Sarkhan Unbroken", 5, "planeswalker", {"sarkhan_unbroken"},
        pips={"G": 1, "U": 1, "R": 1})

PAIRS = [
    ("Birds of Paradise", "Chromatic Lantern"),
    ("Delighted Halfling", "Kindred Discovery"),
    ("Ruby, Daring Tracker", "Sarkhan Unbroken"),
]

# --- Monkeypatches: mecanica real dos 3 candidatos ----------------------

_orig_rocks_mana = sim.rocks_mana


def _rocks_mana(state):
    total = _orig_rocks_mana(state)
    if "Chromatic Lantern" in state.battlefield:
        total += 1
    return total


sim.rocks_mana = _rocks_mana

_orig_color_sources = sim.color_sources


def _color_sources(state, color, dragon_creature_spell=False, legendary_spell=False):
    if "Chromatic Lantern" not in state.battlefield:
        return _orig_color_sources(state, color, dragon_creature_spell, legendary_spell)
    n = 0
    ready = set(sim.ready_creatures(state))
    for card in state.battlefield:
        base = card.split(" (copia)")[0]
        if base not in sim.CARD_DB:
            continue
        if base == state.tapped_land_this_turn:
            continue
        c = sim.CARD_DB[base]
        if base in sim.LAND_NAMES:
            # Chromatic Lantern: "Lands you control have '{T}: Add one
            # mana of any color.'" - incondicional, qualquer spell.
            produces = set("WUBRG")
        elif dragon_creature_spell and base in sim.DRAGON_ANY_COLOR_LANDS:
            produces = set("WUBRG")
        elif legendary_spell and base == "Delighted Halfling":
            produces = set("WUBRG")
        else:
            produces = c.produces
        if color not in produces:
            continue
        if sim.is_creature_card(base) and card not in ready and base not in sim.LAND_NAMES:
            continue
        n += 1
    return n


sim.color_sources = _color_sources

_orig_dragon_enters = sim.dragon_enters


def _dragon_enters(state, name, is_token):
    _orig_dragon_enters(state, name, is_token)
    if "Kindred Discovery" in state.battlefield:
        sim.draw_cards(state, 1)


sim.dragon_enters = _dragon_enters

_orig_combat_step = sim.combat_step


def _combat_step(state):
    ready = sim.ready_creatures(state)
    ready_dragons = [n for n in ready if sim.is_dragon(n)]
    ur_dragon_attacking = sim.COMMANDER in state.battlefield and sim.COMMANDER in ready
    attacking_dragons = ready_dragons if ready_dragons else (
        [sim.COMMANDER] if ur_dragon_attacking else [])
    _orig_combat_step(state)
    if "Kindred Discovery" in state.battlefield and attacking_dragons:
        sim.draw_cards(state, len(attacking_dragons))


sim.combat_step = _combat_step

_orig_enter_battlefield = sim.enter_battlefield


def _enter_battlefield(state, name, from_hand=True, count_as_cast=True):
    _orig_enter_battlefield(state, name, from_hand, count_as_cast)
    if name == "Sarkhan Unbroken" and not hasattr(state, "sarkhan_loyalty"):
        state.sarkhan_loyalty = 4


sim.enter_battlefield = _enter_battlefield

_orig_main_phase = sim.main_phase


def _main_phase(state):
    _orig_main_phase(state)
    if "Sarkhan Unbroken" in state.battlefield:
        if getattr(state, "sarkhan_activated_turn", None) != state.turn:
            state.sarkhan_activated_turn = state.turn
            loyalty = getattr(state, "sarkhan_loyalty", 4)
            if loyalty >= 8:
                state.sarkhan_loyalty = loyalty - 8
                targets = [n for n in state.library
                           if sim.is_dragon(n) and sim.is_creature_card(n)]
                for t in targets:
                    if t not in state.library:
                        continue
                    state.library.remove(t)
                    sim.enter_battlefield(state, t, from_hand=False)
                    state.dragons_free_entry_total += 1
                if state.sarkhan_loyalty <= 0:
                    state.battlefield.remove("Sarkhan Unbroken")
                    state.graveyard.append("Sarkhan Unbroken")
            else:
                state.sarkhan_loyalty = loyalty + 1
                sim.draw_cards(state, 1)
                state.bonus_mana_pool += 1


sim.main_phase = _main_phase


def build_variant_library(cuts, adds):
    lib = sim.BASE_LIBRARY[:]
    for c in cuts:
        lib.remove(c)
    for a in adds:
        lib.append(a)
    assert len(lib) == 99, len(lib)
    return lib


def run_variant(seed_base, n, library, turns=8):
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
        "dragons_free_entry_avg": avg([s.dragons_free_entry_total for s in states]),
        # Sarkhan Unbroken so' vai pro cemiterio neste simulador via a
        # morte por regra de estado apos usar o ultimate (-8, lealdade
        # chega a 0) - nenhum outro caminho de remocao existe no goldfish
        # solo, entao "esta no cemiterio" == "usou o ultimate".
        "sarkhan_ultimates_pct": 100 * sum(1 for s in states if "Sarkhan Unbroken" in s.graveyard) / n,
        "hand_final_avg": avg([len(s.hand) for s in states]),
    }
    print(f"--- {label} ---")
    print(f"Turno medio Ur-Dragon: {d['cmd_turn_avg']:.3f} | nunca conjurada: {d['never_cast_pct']:.2f}%")
    print(f"Avg Dragoes em campo (fim): {d['dragon_count_avg']:.3f} | Dragon tokens: {d['dragon_tokens_avg']:.3f}")
    print(f"Avg dano proxy total: {d['proxy_damage_avg']:.2f}")
    print(f"Avg cartas compradas extra: {d['cards_drawn_extra_avg']:.3f} | Treasures: {d['treasures_avg']:.3f}")
    print(f"Avg Dragoes entrando sem pagar custo: {d['dragons_free_entry_avg']:.3f} | %jogos c/ ultimate Sarkhan: {d['sarkhan_ultimates_pct']:.2f}%")
    print(f"Avg turnos color screw: {d['color_screw_turns_avg']:.3f} | % jogos com screw: {d['color_screw_pct']:.2f}%")
    print(f"Avg mao final: {d['hand_final_avg']:.3f}")
    print()
    return d


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    N = 3000
    SEED_BASE = 7600000  # mesmo seed_base oficial, comparabilidade real

    baseline_states = run_variant(SEED_BASE, N, sim.BASE_LIBRARY)
    baseline = summarize("BASELINE (lista.md atual, sem as 3 novas)", baseline_states, N)
    results = [baseline]

    # --- 1-a-1 ---
    for cut, add in PAIRS:
        lib = build_variant_library([cut], [add])
        states = run_variant(SEED_BASE, N, lib)
        results.append(summarize(f"1x: -{cut} +{add}", states, N))

    # --- 2-a-2 ---
    from itertools import combinations
    for combo in combinations(PAIRS, 2):
        cuts = [p[0] for p in combo]
        adds = [p[1] for p in combo]
        lib = build_variant_library(cuts, adds)
        states = run_variant(SEED_BASE, N, lib)
        label = "2x: " + " & ".join(f"-{c} +{a}" for c, a in combo)
        results.append(summarize(label, states, N))

    # --- 3 juntas ---
    cuts = [p[0] for p in PAIRS]
    adds = [p[1] for p in PAIRS]
    lib = build_variant_library(cuts, adds)
    states = run_variant(SEED_BASE, N, lib)
    results.append(summarize("3x: as 3 juntas", states, N))

    print("=" * 130)
    print(f"{'Variante':50s} {'T.Ur-Dragon':>11s} {'NuncaCast%':>10s} {'Dragoes':>8s} "
          f"{'DanoProxy':>10s} {'Draw':>6s} {'Screw%':>7s} {'MaoFinal':>8s}")
    for r in results:
        print(f"{r['label']:50s} {r['cmd_turn_avg']:11.3f} {r['never_cast_pct']:10.2f} "
              f"{r['dragon_count_avg']:8.3f} {r['proxy_damage_avg']:10.2f} "
              f"{r['cards_drawn_extra_avg']:6.2f} {r['color_screw_pct']:7.2f} {r['hand_final_avg']:8.3f}")

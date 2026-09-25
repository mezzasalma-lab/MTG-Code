"""
Testes dirigidos do simulador do Vihaan (CLAUDE.md, Regra #1: cada correcao
tem que DISPARAR de verdade). Rodada 2026-09-25: Kambal sem limite de 1x/turno
na 2a habilidade, metrica de combate + `win_turn` limitada, e a candidata
Draconic Visitor (substitui toda ficha de artefato por Dragao 5/5, combo com
Pitiless Plunderer + Ashnod's Altar).

Rodar: python3 test_vihaan_goldfish.py   (sem pytest -- executor proprio no fim)
"""
import random
import traceback

import vihaan_goldfish_v1 as vg

FILLER = "Mountain"


def fresh(turn: int = 5, library=None, hand=None) -> vg.GameState:
    s = vg.GameState(library=list(library) if library is not None else [FILLER] * 40)
    s.turn = turn
    s.hand = list(hand or [])
    return s


def put(s, *names, cast_turn=0):
    for n in names:
        s.battlefield.append(n)
        if vg.is_creature_card(n):
            s.creature_cast_turn[n] = cast_turn


def test_kambal_drains_every_token_event():
    # "Whenever one or more tokens you control enter, each opponent loses 1
    # life and you gain 1 life." -- o "only once each turn" e' da 1a habilidade.
    s = fresh()
    put(s, "Kambal, Profiteering Mayor")
    vg.create_treasures(s, 1)
    vg.create_treasures(s, 1)
    vg.create_constructs(s, 1)
    assert s.drain_damage_total == 3, s.drain_damage_total
    assert s.table_damage_total == 3 * vg.NUM_OPPONENTS


def test_visitor_replaces_treasures():
    s = fresh()
    put(s, "Draconic Visitor")
    vg.create_treasures(s, 2)
    assert s.treasures == 0 and s.treasures_created_total == 0
    assert s.dragons == 2 and s.dragons_sick == 2 and s.visitor_replaced_artifact_tokens == 2


def test_visitor_replacement_order_xorn_anointed_manufactor():
    # Xorn (+1) -> Anointed (x2) -> Manufactor (Clue+Food+Treasure) -> Visitor
    s = fresh()
    put(s, "Draconic Visitor", "Xorn", "Anointed Procession", "Academy Manufactor")
    vg.create_treasures(s, 1)
    assert s.dragons == (1 + 1) * 2 * 3, s.dragons
    assert s.clues == 0 and s.foods == 0 and s.treasures == 0


def test_visitor_replaces_constructs():
    s = fresh()
    put(s, "Draconic Visitor", "Anointed Procession")
    vg.create_constructs(s, 3)
    assert s.constructs == 0 and s.dragons == 6


def test_visitor_dragons_trigger_token_payoffs():
    s = fresh()
    put(s, "Draconic Visitor", "Mirkwood Bats")
    vg.create_treasures(s, 3)
    assert s.drain_damage_total == 3  # Mirkwood Bats: 1 por ficha criada


def test_dragons_attack_after_summoning_sickness():
    s = fresh(turn=5)
    s.dragons = 2
    s.dragons_sick = 0
    vg.combat_step(s)
    assert s.combat_attacks_total == 1
    assert s.combat_damage_proxy_total == 10


def test_sick_dragons_do_not_attack():
    s = fresh(turn=5)
    s.dragons = 2
    s.dragons_sick = 2
    vg.combat_step(s)
    assert s.combat_attacks_total == 0 and s.combat_damage_proxy_total == 0


def test_end_step_clears_dragon_sickness():
    s = fresh(turn=5)
    s.dragons = 3
    s.dragons_sick = 3
    vg.end_step(s)
    assert s.dragons_sick == 0


def test_combat_proxy_animated_treasures_and_creatures():
    s = fresh(turn=5)
    put(s, vg.COMMANDER, "Zulaport Cutthroat")
    s.commander_in_play = True
    s.treasures = 2
    vg.combat_step(s)
    # 2 Treasures animados 3/3 + Zulaport 1 (poder impresso)
    assert s.combat_damage_proxy_total == 2 * 3 + vg.CREATURE_POWER["Zulaport Cutthroat"]


def test_opponent_creature_wipe_kills_dragons():
    s = fresh(turn=5)
    s.interaction_rng = random.Random(1)
    put(s, "Zulaport Cutthroat")
    s.dragons = 3
    orig_c, orig_w = vg.interaction_chance, dict(vg.WIPE_TYPE_WEIGHTS)
    vg.interaction_chance = lambda st: 1000.0
    try:
        r = vg.try_smart_opponent_wipe(s)
    finally:
        vg.interaction_chance = orig_c
    assert r is not None
    assert s.dragons == 0


def test_blasphemous_act_kills_dragons():
    s = fresh()
    s.dragons = 2
    vg.resolve_instant_sorcery(s, "Blasphemous Act")
    assert s.dragons == 0


def test_visitor_combo_detected_with_payoff():
    s = fresh(turn=6)
    put(s, "Draconic Visitor", "Pitiless Plunderer", "Ashnod's Altar", "Zulaport Cutthroat")
    vg.check_visitor_combo(s)
    assert s.visitor_combo_turn == 6 and s.win_turn == 6


def test_visitor_combo_needs_all_three_pieces():
    s = fresh(turn=6)
    put(s, "Draconic Visitor", "Pitiless Plunderer", "Zulaport Cutthroat")
    vg.check_visitor_combo(s)
    assert s.visitor_combo_turn is None and s.win_turn is None


def test_visitor_combo_without_payoff_is_not_a_win():
    s = fresh(turn=6)
    put(s, "Draconic Visitor", "Pitiless Plunderer", "Ashnod's Altar")
    s.dragons = 1
    vg.check_visitor_combo(s)
    assert s.visitor_combo_turn == 6 and s.win_turn is None


def test_agent_needs_commander_for_combo():
    s = fresh(turn=6)
    put(s, "Draconic Visitor", "Pitiless Plunderer", "Ashnod's Altar", "Agent of the Iron Throne")
    vg.check_visitor_combo(s)
    assert s.win_turn is None
    s = fresh(turn=6)
    put(s, "Draconic Visitor", "Pitiless Plunderer", "Ashnod's Altar", "Agent of the Iron Throne", vg.COMMANDER)
    s.commander_in_play = True
    s.dragons = 1  # Agent e' Encantamento (Background) -- precisa de 1 criatura pra comecar o loop
    vg.check_visitor_combo(s)
    assert s.win_turn == 6


def test_revel_in_riches_win_at_upkeep():
    s = fresh(turn=5)
    put(s, "Revel in Riches")
    s.treasures = 10
    vg.play_turn(s, is_first_turn=False, on_play=True)
    assert s.win_turn == 6


def test_each_opponent_drain_weighted_single_target_not():
    s = fresh()
    vg.drain(s, 2, each_opp=True)
    vg.drain(s, 2)
    assert s.drain_damage_total == 4
    assert s.table_damage_total == 2 * vg.NUM_OPPONENTS + 2


def test_reaver_cleaver_creates_that_many_treasures():
    # "create that many Treasure tokens" = dano de combate do portador (poder + 1 do +1/+1)
    s = fresh(turn=5)
    put(s, "The Reaver Cleaver", "Mayhem Devil")
    s.reaver_cleaver_host = "Mayhem Devil"
    s.reaver_cleaver_equipped = True
    vg.combat_step(s)
    assert s.reaver_cleaver_treasures_total == vg.CREATURE_POWER["Mayhem Devil"] + 1
    assert s.treasures_created_total == vg.CREATURE_POWER["Mayhem Devil"] + 1


def test_reaver_cleaver_needs_host_attacking():
    s = fresh(turn=5)
    put(s, "The Reaver Cleaver", "Zulaport Cutthroat")
    put(s, "Mayhem Devil", cast_turn=5)  # doente (nao e' outlaw, sem Vihaan)
    s.reaver_cleaver_host = "Mayhem Devil"
    s.reaver_cleaver_equipped = True
    vg.combat_step(s)
    assert s.reaver_cleaver_treasures_total == 0


def test_reaver_cleaver_equips_biggest_noncommander_and_pays():
    s = fresh(turn=5)
    put(s, "The Reaver Cleaver", "Zulaport Cutthroat", "Mayhem Devil", vg.COMMANDER, "Mountain", "Mountain", "Mountain")
    s.commander_in_play = True
    vg.try_equip_reaver_cleaver(s)
    assert s.reaver_cleaver_host == "Mayhem Devil" and s.mana_spent_this_turn == 3
    # portador sai -> reequipar custa de novo
    s.battlefield.remove("Mayhem Devil")
    s.mana_spent_this_turn = 0
    vg.try_equip_reaver_cleaver(s)
    assert s.reaver_cleaver_host == "Zulaport Cutthroat" and s.mana_spent_this_turn == 3


def test_swap_is_positional():
    base = vg.BASE_LIBRARY
    out_card = "Swan Song" if "Swan Song" in base else next(c for c in base if vg.CARD_DB[c].ctype != "land")
    lib = vg.library_with_swap((out_card, "Draconic Visitor"))
    i = base.index(out_card)
    assert lib[i] == "Draconic Visitor" and len(lib) == len(base)
    assert [c for j, c in enumerate(lib) if j != i] == [c for j, c in enumerate(base) if j != i]


def test_swap_none_is_bit_identical():
    a = vg.simulate_one(6_000_123)
    b = vg.simulate_one(6_000_123, swap=None)
    assert a.drain_damage_total == b.drain_damage_total and a.hand == b.hand


def run_all():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for n, f in tests:
        try:
            f()
            print(f"PASS {n}")
        except Exception:
            failed += 1
            print(f"FAIL {n}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} testes passaram")
    return failed


if __name__ == "__main__":
    raise SystemExit(1 if run_all() else 0)

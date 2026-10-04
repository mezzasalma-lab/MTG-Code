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


# ---------------------------------------------------------------------------
# 12a rodada (2026-10-04): Mythos of Snapdax no lugar do Blood Money.
# Oraculo (Scryfall, 2026-10-04): "Each player chooses an artifact, a creature, an enchantment, and a planeswalker from among the nonland permanents they control,
# then sacrifices the rest. If {B}{R} was spent to cast this spell, you choose the permanents for each player instead."
# Rulings 2020-04-17: o mesmo objeto pode valer por varios tipos; confere as cores GASTAS; terrenos com outro tipo nao podem ser escolhidos nem sao sacrificados; simultaneo.
# ---------------------------------------------------------------------------
MYTHOS = "Mythos of Snapdax"


def test_mythos_keeps_engine_creature_best_artifact_and_enchantment():
    s = fresh()
    vg.create_treasures(s, 2)   # antes do Anointed Procession entrar (ele dobraria a criacao de fichas)
    put(s, "Vihaan, Goldwaker", "Mahadi, Emporium Master", "Sol Ring", "Arcane Signet", "Anointed Procession", "Revel in Riches", "Plains", "Swamp")
    s.commander_in_play = True
    sel = vg._mythos_selection(s)
    sobrevive = {"Vihaan, Goldwaker", "Sol Ring", "Anointed Procession"}
    assert set(sel["cre"]) | set(sel["outros"]) == {"Mahadi, Emporium Master", "Arcane Signet", "Revel in Riches"}, sel
    assert sel["inan"] == 2 and sel["anim"] == 0 and sobrevive.isdisjoint(sel["cre"] + sel["outros"])
    n = vg._mass_sacrifice(s, sel)
    assert n == 3 + 2
    assert set(s.battlefield) == sobrevive | {"Plains", "Swamp"}, s.battlefield   # terrenos nao sao permanentes escolhiveis nem sao sacrificados


def test_mythos_sacrifice_is_not_destroy_mayhem_devil_triggers_for_each():
    # Mayhem Devil: "Whenever a player sacrifices a permanent, Mayhem Devil deals 1 damage to any target": 1 por permanente sacrificada, ele proprio incluido (mortes simultaneas)
    s = fresh()
    vg.create_treasures(s, 2)   # antes do Anointed Procession entrar (ele dobraria a criacao de fichas)
    put(s, "Vihaan, Goldwaker", "Mayhem Devil", "Sol Ring", "Anointed Procession")
    s.commander_in_play = True
    s.clues, s.foods, s.constructs = 1, 1, 1
    d0 = s.drain_damage_total
    n = vg._mass_sacrifice(s, vg._mythos_selection(s))
    # sacrificados: Mayhem Devil + 2 Treasures + 1 Clue + 1 Food + 1 Construct = 6 (o Construct e' criatura E artefato: o Sol Ring fica como artefato, o Vihaan como criatura)
    assert n == 6, n
    assert s.drain_damage_total - d0 == 6
    assert "Mayhem Devil" not in s.battlefield and "Mayhem Devil" in s.graveyard
    assert s.treasures == 0 and s.clues == 0 and s.foods == 0 and s.constructs == 0


def test_mythos_spell_in_flight_is_not_a_permanent():
    # cascade poe a magia no campo antes de resolver: ela nao e' permanente, nao e' sacrificada, e a remocao do campo depois nao pode falhar (achado na validacao)
    s = fresh()
    put(s, "Vihaan, Goldwaker", MYTHOS)
    s.commander_in_play = True
    sel = vg._mythos_selection(s)
    assert MYTHOS not in sel["cre"] + sel["outros"], sel
    vg.resolve_instant_sorcery(s, MYTHOS)
    assert MYTHOS in s.battlefield and "Vihaan, Goldwaker" in s.battlefield


def test_mythos_cascade_hit_does_not_crash_and_is_declined_when_held():
    base = vg.CASCADE_DECLINE_HELD_WIPES_ENABLED
    try:
        for flag, esperado in ((True, 0), (False, 1)):
            vg.CASCADE_DECLINE_HELD_WIPES_ENABLED = flag
            s = fresh(library=[MYTHOS] + [FILLER] * 5)
            put(s, "Vihaan, Goldwaker", "Sol Ring")
            s.commander_in_play = True
            vg.do_cascade(s, 5)   # a unica carta nao-terreno do topo e' a Mythos (MV 4 < 5)
            assert s.mythos_cast_total == esperado, (flag, s.mythos_cast_total)
            if flag:
                assert MYTHOS in s.library and MYTHOS not in s.graveyard   # recusada: vai pro fundo
            else:
                assert MYTHOS in s.graveyard and MYTHOS not in s.battlefield
    finally:
        vg.CASCADE_DECLINE_HELD_WIPES_ENABLED = base


def test_mythos_needs_two_white_sources():
    def casta(*campo, treasures=0):
        s = fresh()
        put(s, *campo)
        s.hand = [MYTHOS]
        if treasures:
            vg.create_treasures(s, treasures)
        return vg.can_cast(s, MYTHOS)
    assert not casta("Plains", "Mountain", "Mountain", "Swamp")                    # {W}{W}: so' 1 fonte de W
    assert casta("Plains", "Plains", "Mountain", "Swamp")
    assert casta("Plains", "Command Tower", "Mountain", "Swamp")                   # Command Tower produz W
    assert casta("Plains", "Mountain", "Mountain", treasures=1)                    # Treasure produz qualquer cor
    assert not casta("Mountain", "Mountain", "Mountain", "Swamp")
    vg.MYTHOS_COLOR_CHECK_ENABLED = False
    try:
        assert casta("Mountain", "Mountain", "Mountain", "Swamp")                  # chave desligada: so' o custo
    finally:
        vg.MYTHOS_COLOR_CHECK_ENABLED = True


def test_mythos_br_proxy_requires_four_distinct_colored_sources():
    # {B}{R} gastos NO LUGAR do {2}: precisa de W,W,B,R em 4 fontes DISTINTAS (ruling: vale o que foi gasto de fato)
    def cast(*campo):
        s = fresh()
        put(s, *campo)
        s.hand = [MYTHOS]
        vg.cast_card(s, MYTHOS)
        return s
    s = cast("Plains", "Plains", "Swamp", "Mountain")
    assert s.mythos_cast_total == 1 and s.mythos_br_spent_total == 1 and not s.mythos_br_pending
    s = cast("Plains", "Plains", "Mountain", "Mountain")                            # sem fonte de B
    assert s.mythos_cast_total == 1 and s.mythos_br_spent_total == 0
    s = cast("Plains", "Plains", "Blood Crypt", "Mountain")                         # Blood Crypt produz B ou R: serve de B, o Mountain de R
    assert s.mythos_br_spent_total == 1
    s = cast("Plains", "Plains", "Blood Crypt", "Plains")                           # B/R de uma fonte so': falta a 4a cor
    assert s.mythos_br_spent_total == 0


def test_mythos_replaces_blood_money_in_library_and_flag_off_restores_it():
    assert MYTHOS in vg.BASE_LIBRARY and "Blood Money" not in vg.BASE_LIBRARY and len(vg.BASE_LIBRARY) == 99
    vg.MYTHOS_REPLACES_BLOOD_MONEY_ENABLED = False
    try:
        lib = vg.build_library()
        assert "Blood Money" in lib and MYTHOS not in lib and len(lib) == 99
        assert lib[lib.index("Blood Crypt") + 1] == "Blood Money"
        assert sorted(x for x in lib if x != "Blood Money") == sorted(x for x in vg.BASE_LIBRARY if x != MYTHOS)
    finally:
        vg.MYTHOS_REPLACES_BLOOD_MONEY_ENABLED = True


def test_mythos_swap_pairs_with_blood_money_position():
    flag = vg.MYTHOS_REPLACES_BLOOD_MONEY_ENABLED
    vg.MYTHOS_REPLACES_BLOOD_MONEY_ENABLED = False
    base = vg.BASE_LIBRARY
    try:
        vg.BASE_LIBRARY = vg.build_library()
        lib = vg.library_with_swap(("Blood Money", MYTHOS))
        i = vg.BASE_LIBRARY.index("Blood Money")
        assert lib[i] == MYTHOS and len(lib) == 99 and "Blood Money" not in lib
    finally:
        vg.MYTHOS_REPLACES_BLOOD_MONEY_ENABLED = flag
        vg.BASE_LIBRARY = base


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

"""
Testes dirigidos do simulador do Ur-Dragon (CLAUDE.md, Regra #1: cada
correcao tem que DISPARAR de verdade). Rodada 2026-09-25: fichas de Dragao
viram criaturas de verdade (atacam, disparam gatilhos de entrada, morrem em
wipe), Faerie Dragons do Ancient Gold sao Dragoes, Dragon Broodmother cria
em CADA upkeep, Roaming Throne dobra Terror of the Peaks/Broodmother, e a
candidata Draconic Visitor (substitui Treasure por Dragao 5/5).

Rodar: python3 test_urdragon_goldfish.py   (sem pytest -- executor proprio no fim)
"""
import random
import traceback

import urdragon_goldfish_v1 as ud

FILLER = "Forest"


def fresh(turn: int = 5, library=None, hand=None) -> ud.GameState:
    s = ud.GameState(library=list(library) if library is not None else [FILLER] * 40)
    s.turn = turn
    s.hand = list(hand or [])
    return s


def put(s, *names, cast_turn=0):
    for n in names:
        s.battlefield.append(n)
        if ud.is_creature_card(n):
            s.creature_cast_turn[n] = cast_turn


def test_dragon_tokens_attack_and_count_for_ur_dragon_draw():
    # "Whenever one or more Dragons you control attack, draw that many cards"
    s = fresh()
    put(s, ud.COMMANDER)
    s.commander_in_play = True
    s.dragon_token_list = [[5, 3, True], [6, 4, True]]
    s.dragon_tokens = 2
    ud.combat_step(s)
    assert s.urdragon_attack_draws_total == 3, s.urdragon_attack_draws_total
    # 10 (Ur-Dragon) + 5 + 6
    assert s.combat_damage_proxy_total == ud.effective_power(s, ud.COMMANDER) + 11


def test_token_born_this_turn_is_summoning_sick():
    s = fresh(turn=5)
    put(s, ud.COMMANDER)
    s.commander_in_play = True
    s.dragon_token_list = [[5, 5, True]]
    s.dragon_tokens = 1
    ud.combat_step(s)
    assert s.urdragon_attack_draws_total == 1


def test_dragon_tempest_gives_haste_to_new_flying_token():
    s = fresh(turn=5)
    put(s, "Dragon Tempest")
    s.dragon_token_list = [[5, 5, True]]
    s.dragon_tokens = 1
    assert len(ud.ready_dragon_tokens(s)) == 1


def test_lathliss_token_triggers_scourge_and_terror():
    s = fresh()
    put(s, "Lathliss, Dragon Queen", "Scourge of Valkas", "Terror of the Peaks")
    before_events = s.dragon_etb_damage_events_total
    ud.create_dragon_tokens(s, 1, 5, source="lathliss")
    # Scourge: 1 evento com X = Dragoes (Lathliss + Scourge + Terror + ficha = 4);
    # Terror: 5 (poder da ficha). Total 9.
    assert s.dragon_etb_damage_events_total == before_events + 1
    assert s.proxy_damage_total == 4 + 5, s.proxy_damage_total
    assert s.dragon_tokens == 1 and len(s.dragon_token_list) == 1


def test_utvara_tokens_fire_etb_triggers():
    s = fresh(turn=6)
    put(s, "Utvara Hellkite", "Scourge of Valkas")
    ud.combat_step(s)
    # 2 Dragoes atacam -> 2 fichas 6/6, cada uma dispara a Scourge
    assert s.dragon_tokens == 2 and s.dragon_tokens_created_total == 2
    assert s.dragon_etb_damage_events_total == 2


def test_faerie_dragons_are_dragons():
    s = fresh(turn=6)
    put(s, "Ancient Gold Dragon")
    ud.combat_step(s)
    assert s.dragon_tokens == 10
    assert all(t[0] == 1 for t in s.dragon_token_list)
    assert s.other_tokens == 0


def test_broodmother_each_upkeep():
    s = fresh(turn=6)
    put(s, "Dragon Broodmother")
    ud.upkeep_step(s)
    assert s.dragon_tokens == 1
    ud.end_step(s)
    assert s.dragon_tokens == 1 + ud.NUM_OPPONENTS


def test_roaming_throne_doubles_broodmother_and_terror():
    s = fresh(turn=6)
    put(s, "Dragon Broodmother", "Roaming Throne")
    ud.upkeep_step(s)
    assert s.dragon_tokens == 2
    s = fresh()
    put(s, "Terror of the Peaks", "Roaming Throne")
    ud.create_dragon_tokens(s, 1, 5, source="test")
    assert s.proxy_damage_total == 10


def test_wipe_clears_dragon_tokens():
    s = fresh(turn=6)
    s.interaction_rng = random.Random(1)
    put(s, "Forest")
    s.dragon_token_list = [[5, 3, True]] * 4
    s.dragon_tokens = 4
    # sem outra criatura: o unico tipo disponivel pro wipe e' "creature" (so' fichas).
    # Forca a rolagem de "algum wipe acontece" (a escolha do TIPO segue real).
    orig = ud.interaction_chance
    ud.interaction_chance = lambda st: 1000.0
    try:
        r = ud.try_smart_opponent_wipe(s)
    finally:
        ud.interaction_chance = orig
    assert r is not None
    assert s.dragon_tokens == 0 and s.dragon_token_list == []


def test_visitor_replaces_treasures_with_dragons():
    s = fresh()
    put(s, "Draconic Visitor")
    ud.create_and_use_treasures(s, 3)
    assert s.treasures_created_total == 0 and s.bonus_mana_pool == 0
    assert s.dragon_tokens == 3 and s.visitor_dragons_total == 3
    assert all(t[0] == 5 for t in s.dragon_token_list)
    ud.create_treasures(s, 1)
    assert s.dragon_tokens == 4


def test_visitor_with_goldspan_counts_lost_mana():
    s = fresh()
    put(s, "Draconic Visitor", "Goldspan Dragon")
    ud.create_and_use_treasures(s, 2)
    assert s.visitor_mana_lost_total == 4 and s.bonus_mana_pool == 0


def test_visitor_tithe_dragon_born_on_opponent_turn():
    # Smothering Tithe dispara no turno do oponente -> o Dragao ja' ataca no meu turno
    s = fresh(turn=6)
    put(s, "Draconic Visitor", "Smothering Tithe")
    ud.upkeep_step(s)
    assert s.dragon_tokens == 1 and s.dragon_token_list[0][1] == 5
    assert len(ud.ready_dragon_tokens(s)) == 1


def test_visitor_stops_magda_tutor():
    s = fresh(turn=6)
    put(s, "Draconic Visitor", "Magda, Brazen Outlaw", "Firdoch Core")
    ud.do_magda_treasures(s)
    assert s.magda_treasures == 0 and s.dragon_tokens == 2


def test_no_visitor_treasures_unchanged():
    s = fresh()
    ud.create_and_use_treasures(s, 3)
    assert s.treasures_created_total == 3 and s.bonus_mana_pool == 3 and s.dragon_tokens == 0


def test_token_cap():
    s = fresh()
    ud.create_dragon_tokens(s, ud.DRAGON_TOKEN_CAP + 50, 1, source="test")
    assert s.dragon_tokens == ud.DRAGON_TOKEN_CAP and s.dragon_token_cap_hits == 1


def test_swap_is_positional():
    base = ud.BASE_LIBRARY
    out_card = next(c for c in base if c not in ud.LAND_NAMES)
    lib = ud.library_with_swap((out_card, "Draconic Visitor"))
    i = base.index(out_card)
    assert lib[i] == "Draconic Visitor" and len(lib) == len(base)
    assert [c for j, c in enumerate(lib) if j != i] == [c for j, c in enumerate(base) if j != i]


def test_swap_none_is_bit_identical():
    a = ud.simulate_one(7_600_123)
    b = ud.simulate_one(7_600_123, swap=None)
    assert a.proxy_damage_total == b.proxy_damage_total and a.hand == b.hand


def test_lethal_turn_set():
    found = 0
    for seed in range(7_600_000, 7_600_200):
        st = ud.simulate_one(seed)
        if st.lethal_proxy_turn is not None:
            found += 1
            assert st.proxy_damage_total + st.combat_damage_proxy_total >= ud.LETHAL_PROXY
    assert found > 0


def test_cost_reduction_only_generic():
    # CR 601.2f: Scourge of Valkas {2}{R}{R}{R} com Eminence (-1) + Dragonspeaker (-2) = 3, nao 2
    s = fresh()
    put(s, "Dragonspeaker Shaman")
    assert ud.effective_cost(s, "Scourge of Valkas") == 3
    # Ur-Dragon {4}{W}{U}{B}{R}{G}: nunca abaixo de 5
    put(s, "Dragonlord's Servant", "Urza's Incubator", "Herald's Horn")
    assert ud.effective_cost(s, ud.COMMANDER) == 5
    # Great Henge {7}{G}{G}: nunca abaixo de 2
    put(s, "Atarka, World Render", "Old Gnawbone")
    s.battlefield.append("Utvara Hellkite")
    assert ud.effective_cost(s, "The Great Henge") >= 2


def test_rhythm_of_the_wild_mv_3():
    assert ud.CARD_DB["Rhythm of the Wild"].mv == 3


def test_joint_color_check_hall():
    s = fresh()
    put(s, "Command Tower", "Forest", "Forest", "Forest", "Forest", "Forest")
    assert not ud.has_color_sources_for(s, ud.COMMANDER)  # 1 fonte pra W/U/B/R
    s = fresh()
    put(s, "Command Tower", "Plains", "Island", "Swamp", "Mountain")
    assert ud.has_color_sources_for(s, ud.COMMANDER)


def test_tiamat_tutors_five_when_cast():
    s = fresh(library=["Scourge of Valkas", "Forest", "Terror of the Peaks", "Lathliss, Dragon Queen",
                       "Utvara Hellkite", "Old Gnawbone", "Goldspan Dragon"])
    s.hand = ["Tiamat"]
    put(s, "Command Tower", "Plains", "Island", "Swamp", "Mountain", "Forest")
    ud.cast_card(s, "Tiamat")
    assert s.tiamat_tutored_total == 5 and "Goldspan Dragon" not in s.hand and "Forest" not in s.hand


def test_tiamat_put_onto_battlefield_does_not_tutor():
    s = fresh(library=["Scourge of Valkas", "Terror of the Peaks"])
    s.hand = ["Tiamat"]
    ud.enter_battlefield(s, "Tiamat")
    assert s.tiamat_tutored_total == 0 and "Scourge of Valkas" not in s.hand


def test_ur_dragon_trigger_prefers_other_permanent_over_tiamat():
    s = fresh(turn=6)
    put(s, ud.COMMANDER)
    s.commander_in_play = True
    s.creature_cast_turn[ud.COMMANDER] = 1
    s.hand = ["Tiamat", "Scourge of Valkas"]
    ud.combat_step(s)
    assert "Tiamat" in s.hand and "Scourge of Valkas" in s.battlefield


def test_sarkhans_triumph_fetches_tiamat_with_five_colors():
    s = fresh(library=["Utvara Hellkite", "Tiamat", "Scourge of Valkas"])
    put(s, "Command Tower", "Plains", "Island", "Swamp", "Mountain")
    ud.resolve_instant_sorcery(s, "Sarkhan's Triumph")
    assert "Tiamat" in s.hand
    s = fresh(library=["Utvara Hellkite", "Tiamat", "Scourge of Valkas"])
    put(s, "Mountain", "Mountain", "Forest")
    ud.resolve_instant_sorcery(s, "Sarkhan's Triumph")
    assert "Utvara Hellkite" in s.hand


def test_tiamat_waits_in_normal_queue_behind_ramp():
    # politica escolhida por sensibilidade (goldfish-log 2026-09-28): ramp antes
    s = fresh(library=["Scourge of Valkas", "Terror of the Peaks"] + [FILLER] * 20)
    s.hand = ["Tiamat", "Farseek"]
    put(s, "Command Tower", "Plains", "Island", "Swamp", "Mountain", "Forest", "Forest")
    ud.main_phase(s)
    assert "Farseek" not in s.hand and s.tiamat_casts == 0


def test_orb_sacrifice_only_sees_top_seven():
    s = fresh(library=[FILLER] * 7 + ["Utvara Hellkite"] + [FILLER] * 5)
    put(s, "Orb of Dragonkind", "Mountain", "Forest")
    ud.do_orb_dragonkind(s)
    assert "Utvara Hellkite" not in s.hand and "Orb of Dragonkind" not in s.battlefield
    assert s.library[0] == "Utvara Hellkite" and len(s.library) == 13
    s = fresh(library=[FILLER] * 3 + ["Utvara Hellkite"] + [FILLER] * 5)
    put(s, "Orb of Dragonkind", "Mountain", "Forest")
    ud.do_orb_dragonkind(s)
    assert "Utvara Hellkite" in s.hand and len(s.library) == 8


def test_orb_mana_pays_commander_in_first_main_phase():
    # 8 terrenos (5 cores) + Orb: 8 - 1 + 2 = 9 = custo da Ur-Dragon
    s = fresh(turn=8)
    put(s, "Orb of Dragonkind", "Command Tower", "Plains", "Island", "Swamp", "Mountain", "Forest", "Forest", "Forest")
    assert not ud.can_cast(s, ud.COMMANDER)
    ud.main_phase(s)
    assert s.commander_in_play and s.orb_mana_activations_total == 1


def test_orb_mana_counts_as_color_for_dragon_spells():
    s = fresh()
    put(s, "Forest", "Forest", "Forest", "Forest", "Forest")
    s.dragon_mana_pool = 2
    assert ud.has_color_sources_for(s, "Scourge of Valkas") is False  # RRR, so' 2 da Orb
    assert not ud.has_color_sources_for(s, "Rhythm of the Wild")  # nao-Dragao: a Orb nao paga o {R}
    put(s, "Mountain")
    assert ud.has_color_sources_for(s, "Scourge of Valkas")




def test_roaming_throne_doubles_tiamat_search():
    lib = ["Scourge of Valkas", "Terror of the Peaks", "Lathliss, Dragon Queen", "Utvara Hellkite", "Old Gnawbone",
           "Goldspan Dragon", "Atarka, World Render", "Hellkite Charger", "Savage Ventmaw", "Balefire Dragon", "Forest"]
    s = fresh(library=lib)
    s.hand = ["Tiamat"]
    put(s, "Roaming Throne", "Command Tower", "Plains", "Island", "Swamp", "Mountain", "Forest", "Forest")
    ud.cast_card(s, "Tiamat")
    assert s.tiamat_tutored_total == 10 and s.library == ["Forest"]


def test_haven_returns_tiamat_to_hand_when_dragons_remain():
    s = fresh(library=["Scourge of Valkas"] + [FILLER] * 10)
    s.graveyard = ["Utvara Hellkite", "Tiamat"]
    put(s, ud.HAVEN_RECURSION_LAND, "Forest", "Forest", "Mountain")
    ud.try_haven_recursion(s)
    assert "Tiamat" in s.hand


def test_sarkhans_triumph_needs_dragon_creature_card():
    s = fresh(library=["Firdoch Core", FILLER])
    ud.resolve_instant_sorcery(s, "Sarkhan's Triumph")
    assert "Firdoch Core" not in s.hand


def test_tiamat_can_fetch_changeling_dragon_cards():
    # "Dragon cards" (nao "creature"): Firdoch Core/Morophon tem Changeling
    s = fresh(library=["Firdoch Core", "Morophon, the Boundless", FILLER])
    ud.tiamat_tutor(s)
    assert "Firdoch Core" in s.hand and "Morophon, the Boundless" in s.hand


def test_cleanup_keeps_lands_and_ramp_before_commander():
    s = fresh()
    s.hand = ["Forest", "Farseek", "Herald's Horn", "Scourge of Valkas", "Utvara Hellkite", "Old Gnawbone",
              "Terror of the Peaks", "Atarka, World Render", "Goldspan Dragon"]
    ud.end_step(s)
    assert len(s.hand) == 7 and {"Forest", "Farseek", "Herald's Horn"} <= set(s.hand)
    # com a comandante em campo, a ordem antiga (terreno primeiro) volta
    s = fresh()
    put(s, ud.COMMANDER); s.commander_in_play = True
    s.hand = ["Forest", "Mountain", "Farseek", "Scourge of Valkas", "Utvara Hellkite", "Old Gnawbone",
              "Terror of the Peaks", "Atarka, World Render"]
    ud.end_step(s)
    assert "Forest" not in s.hand or "Mountain" not in s.hand


class _AlwaysRng:
    def random(self):
        return 0.0


def test_counter_prevented_by_dromoka_rhythm_cavern():
    for prot in ("Dragonlord Dromoka", "Rhythm of the Wild", "Cavern of Souls"):
        s = fresh(turn=ud.INTERACTION_SETUP_TURNS + 2)
        s.interaction_rng = _AlwaysRng()
        put(s, prot)
        assert ud.try_smart_opponent_counter(s) is False
        assert s.counters_prevented_by == {prot: 1} and s.smart_counters_total == 0
    s = fresh(turn=ud.INTERACTION_SETUP_TURNS + 2)
    s.interaction_rng = _AlwaysRng()
    assert ud.try_smart_opponent_counter(s) is True


def test_own_counterspell_answers_the_counter():
    s = fresh(turn=ud.INTERACTION_SETUP_TURNS + 2)
    s.interaction_rng = _AlwaysRng()
    s.hand = ["Swan Song"]
    put(s, "Island")
    assert ud.try_smart_opponent_counter(s) is False
    assert "Swan Song" in s.graveyard and s.counters_answered_total == 1


def test_dromoka_lifelink_in_combat():
    s = fresh(turn=6)
    put(s, "Dragonlord Dromoka", cast_turn=1)
    life = s.life
    ud.combat_step(s)
    assert s.life == life + 5 and s.dromoka_lifelink_total == 5


def test_heroic_intervention_answers_wipe_that_hits_commander():
    s = fresh(turn=ud.INTERACTION_SETUP_TURNS + 2)
    s.interaction_rng = ud.random.Random(0)
    put(s, ud.COMMANDER, "Scourge of Valkas", "Forest", "Forest")
    s.commander_in_play = True
    s.hand = ["Heroic Intervention"]
    assert ud.try_protection_response(s, "wipe", [ud.COMMANDER, "Scourge of Valkas"])
    assert "Heroic Intervention" in s.graveyard and ud.COMMANDER in s.battlefield


def test_teferis_protection_covers_rest_of_round():
    s = fresh(turn=ud.INTERACTION_SETUP_TURNS + 2)
    put(s, ud.COMMANDER, "Plains", "Forest", "Forest")
    s.hand = ["Teferi's Protection"]
    assert ud.try_protection_response(s, "wipe", [ud.COMMANDER])
    assert s.teferi_protected and "Teferi's Protection" not in s.graveyard
    s.interaction_rng = _AlwaysRng()
    s.interaction_rng.choice = lambda seq: seq[-1]
    life = s.life
    ud.try_smart_opponent_attack(s)
    assert s.life == life


def test_small_wipe_not_answered_and_no_mana_no_answer():
    s = fresh()
    put(s, "Forest", "Forest")
    s.hand = ["Heroic Intervention"]
    assert not ud.try_protection_response(s, "wipe", ["Birds of Paradise"])
    s.mana_spent_this_turn = 2
    assert not ud.try_protection_response(s, "wipe", [ud.COMMANDER])


def test_greaves_shroud_redirects_removal():
    s = fresh(turn=ud.INTERACTION_SETUP_TURNS + 2)
    s.interaction_rng = _AlwaysRng()
    put(s, "Roaming Throne", "Scourge of Valkas", "Lightning Greaves")
    s.lightning_greaves_equipped_to = "Roaming Throne"
    assert ud.try_smart_opponent_removal(s) == "Scourge of Valkas"
    assert "Roaming Throne" in s.battlefield


# ---------------------------------------------------------------------------
# Rodada 2026-09-28: varredura das demais cartas e mecanicas
# ---------------------------------------------------------------------------

WUBRG_LANDS = ("Command Tower", "Plains", "Island", "Swamp", "Mountain", "Forest")


def test_roaming_throne_spell_is_not_a_dragon_spell():
    s = fresh()
    put(s, "Dragonspeaker Shaman", "Dragonlord's Servant")
    assert ud.effective_cost(s, "Roaming Throne") == 4  # Golem na pilha: sem Eminence/Servant/Dragonspeaker
    s.dragon_mana_pool = 2
    assert ud.remaining_mana_for(s, "Roaming Throne") == ud.remaining_mana(s)  # Orb nao paga


def test_ancient_tomb_makes_two():
    s = fresh()
    put(s, "Ancient Tomb", "Forest")
    assert ud.total_mana(s) == 3


def test_commander_tax_in_can_cast():
    s = fresh(turn=8)
    s.commander_cast_count = 2
    put(s, *WUBRG_LANDS, "Forest", "Forest", "Forest")
    assert ud.effective_cost(s, ud.COMMANDER) == 13 and not ud.can_cast(s, ud.COMMANDER)


def test_two_tapped_lands_same_turn():
    s = fresh(library=["Plains", "Mountain"] + [FILLER] * 10)
    s.hand = ["Ketria Triome"]
    put(s, "Forest", "Forest")
    ud.play_land(s)
    ud.resolve_instant_sorcery(s, "Farseek")
    assert len(s.tapped_lands_this_turn) == 2 and ud.total_mana(s) == 2


def test_cultivate_one_tapped_one_to_hand():
    s = fresh(library=["Mountain", "Plains"] + [FILLER] * 10)
    put(s, "Forest")
    s.library = ["Mountain", "Plains", "Island"]
    ud.resolve_instant_sorcery(s, "Cultivate")
    lands_bf = [n for n in s.battlefield if n in ud.LAND_NAMES]
    assert len(lands_bf) == 2 and len(s.tapped_lands_this_turn) == 1
    assert sum(1 for n in s.hand if n in ud.LAND_NAMES) == 1


def test_life_costs_paid():
    s = fresh(library=["Blood Crypt"] + [FILLER] * 5)
    s.hand = ["Bloodstained Mire"]
    ud.play_land(s)
    assert s.life_paid == {"fetch": 1, "shock": 2} and s.life == 37
    s.hand = ["Anguished Unmaking"]
    put(s, "Plains", "Swamp", "Forest")
    ud.cast_card(s, "Anguished Unmaking")
    assert s.life == 34


def test_ur_dragon_trigger_land_from_hand_enters_tapped():
    s = fresh(turn=6)
    put(s, ud.COMMANDER)
    s.commander_in_play = True
    s.hand = ["Zagoth Triome"]
    ud.combat_step(s)
    assert "Zagoth Triome" in s.battlefield and "Zagoth Triome" in s.tapped_lands_this_turn


def test_heralds_horn_only_dragon_creature_cards():
    for top in ("Firdoch Core", "Roaming Throne"):
        s = fresh(library=[top, FILLER])
        put(s, "Herald's Horn")
        ud.upkeep_step(s)
        assert top not in s.hand
    s = fresh(library=["Scourge of Valkas", FILLER])
    put(s, "Herald's Horn")
    ud.upkeep_step(s)
    assert "Scourge of Valkas" in s.hand


def test_bladewing_graveyard_type_and_throne_doubling():
    s = fresh()
    s.graveyard = ["Roaming Throne"]
    ud.enter_battlefield(s, "Bladewing the Risen", from_hand=False)
    assert "Roaming Throne" in s.graveyard
    s = fresh()
    put(s, "Roaming Throne")
    s.graveyard = ["Scourge of Valkas", "Hellkite Charger"]
    ud.enter_battlefield(s, "Bladewing the Risen", from_hand=False)
    assert not s.graveyard


def test_haven_and_voyage_skip_throne():
    s = fresh()
    s.graveyard = ["Roaming Throne"]
    put(s, ud.HAVEN_RECURSION_LAND, "Forest", "Forest", "Forest")
    ud.try_haven_recursion(s)
    assert "Roaming Throne" in s.graveyard
    ud.reanimate_dragons_from_graveyard(s)
    assert "Roaming Throne" in s.graveyard


def test_hoard_draws_once_per_turn_and_uses_its_mana():
    s = fresh()
    put(s, "Dragon's Hoard", "Forest", "Forest")
    s.dragon_hoard_gold_counters = 3
    before = ud.remaining_mana(s)
    ud.try_dragon_hoard_draw(s)
    ud.try_dragon_hoard_draw(s)
    assert s.dragon_hoard_draws_total == 1 and ud.remaining_mana(s) == before - 1


def test_commander_cast_as_soon_as_ramp_makes_it_castable():
    # 6 terrenos + Dragonspeaker: a Ur-Dragon custa 7. Sol Ring (1 -> +2) deixa
    # 7; antes o loop gastava em Hellkite Charger e ela ficava pra depois.
    s = fresh(turn=7)
    put(s, *WUBRG_LANDS, "Dragonspeaker Shaman")
    s.hand = ["Sol Ring", "Hellkite Charger"]
    s.phase = "main1"
    assert not ud.can_cast(s, ud.COMMANDER)
    ud.main_phase(s)
    assert s.commander_in_play


def test_sarkhan_unbroken_plus_one_before_casting():
    s = fresh()
    put(s, "Sarkhan Unbroken", "Forest", "Forest")
    s.sarkhan_loyalty = 4
    s.hand = ["Dragon Tempest"]  # {1}{R}: precisa da mana do +1 (cor qualquer)
    put(s, "Mountain")
    s.mana_spent_this_turn = 2
    s.phase = "main1"
    ud.main_phase(s)
    assert "Dragon Tempest" in s.battlefield and s.sarkhan_loyalty == 5


def test_pumps_only_before_combat():
    s = fresh()
    put(s, "Lathliss, Dragon Queen", "Mountain", "Mountain", "Mountain", "Mountain")
    s.phase = "main2"
    s.hand = []
    ud.main_phase(s)
    assert s.lathliss_pumps == 0
    s.phase = "main1"
    ud.main_phase(s)
    assert s.lathliss_pumps == 1


def test_bladewing_pump_needs_black():
    s = fresh()
    put(s, "Bladewing the Risen", "Mountain", "Mountain", "Mountain")
    s.phase = "main1"
    ud.try_dragon_pumps(s)
    assert s.bladewing_pumps == 0


def test_greaves_moves_to_commander_cast_this_turn():
    s = fresh(turn=6)
    put(s, "Lightning Greaves", "Birds of Paradise")
    s.lightning_greaves_equipped_to = "Birds of Paradise"
    put(s, ud.COMMANDER, cast_turn=6)
    s.commander_in_play = True
    s.phase = "main1"
    ud.try_lightning_greaves_equip(s)
    assert s.lightning_greaves_equipped_to == ud.COMMANDER


def test_riot_choice():
    s = fresh()
    put(s, "Rhythm of the Wild")
    s.phase = "main1"
    ud.enter_battlefield(s, "Scourge of Valkas", from_hand=False)
    assert "Scourge of Valkas" in s.riot_haste
    put(s, "Temur Ascendancy")
    ud.enter_battlefield(s, "Lathliss, Dragon Queen", from_hand=False)
    assert s.riot_counters.get("Lathliss, Dragon Queen") == 1
    assert ud.effective_power(s, "Lathliss, Dragon Queen") == 7


def test_terror_sees_great_henge_counter():
    s = fresh()
    put(s, "Terror of the Peaks", "The Great Henge")
    ud.enter_battlefield(s, "Hellkite Charger", from_hand=False)
    assert s.proxy_damage_total == 6  # 5 + contador do Henge


def test_tokens_count_as_creatures_you_control():
    s = fresh()
    s.dragon_token_list = [[6, 1, True, None]]
    s.dragon_tokens = 1
    assert ud.effective_cost(s, "The Great Henge") == 1 + 2  # {7}{G}{G} - 6
    s.library = [FILLER] * 20
    ud.resolve_instant_sorcery(s, "Return of the Wildspeaker")
    assert len(s.hand) == 6


def test_throne_doubles_ur_dragon_trigger_even_if_she_does_not_attack():
    s = fresh(turn=6)
    put(s, ud.COMMANDER, cast_turn=6)  # doente, nao ataca
    s.commander_in_play = True
    put(s, "Roaming Throne", "Scourge of Valkas")
    ud.combat_step(s)
    # atacam Throne (4/4 Dragao) e Scourge: 2 Dragoes, gatilho x2 = 4 cartas
    assert s.urdragon_attack_draws_total == 4


def test_twinflame_doubles_commander_damage_and_gnawbone():
    s = fresh(turn=6)
    put(s, ud.COMMANDER, "Twinflame Tyrant", "Old Gnawbone")
    s.commander_in_play = True
    s.hand = []
    ud.combat_step(s)
    assert s.commander_damage_dealt == 20
    assert s.treasures_created_total == (10 + 3 + 7) * 2


def test_magda_deals_combat_damage():
    s = fresh(turn=6)
    put(s, "Magda, Brazen Outlaw")
    ud.combat_step(s)
    assert s.combat_damage_proxy_total == 2


def test_firdoch_animated_attacks_as_dragon():
    s = fresh(turn=6)
    put(s, ud.COMMANDER, "Firdoch Core", *WUBRG_LANDS)
    s.firdoch_entered_turn = 2
    s.commander_in_play = True
    s.hand = []
    ud.try_firdoch_animate(s)
    assert s.firdoch_animated_turn == 6
    ud.combat_step(s)
    assert s.urdragon_attack_draws_total == 2 and s.combat_damage_proxy_total == 14


def test_return_of_the_wildspeaker_pump_for_lethal():
    s = fresh(turn=6)
    s.dragon_token_list = [[6, 1, True, None]] * 5
    s.dragon_tokens = 5
    s.proxy_damage_total = 85   # 85 + 30 = 115 < 120; +15 fecha
    s.hand = ["Return of the Wildspeaker"]
    put(s, *WUBRG_LANDS)
    ud.combat_step(s)
    assert s.rotw_pumps_total == 1 and s.combat_damage_proxy_total == 45


def test_d20_uses_rng():
    s = fresh()
    s.dice_rng = random.Random(3)
    rolls = {ud.roll_d20(s) for _ in range(30)}
    assert len(rolls) > 5 and min(rolls) >= 1 and max(rolls) <= 20


def test_miirym_copy_of_scourge_has_scourge_trigger():
    s = fresh()
    put(s, "Miirym, Sentinel Wyrm")
    ud.enter_battlefield(s, "Scourge of Valkas", from_hand=False)
    assert ud.sources(s, "Scourge of Valkas") == 2
    before = s.proxy_damage_total
    ud.enter_battlefield(s, "Hellkite Charger", from_hand=False)
    # Charger entra: 2 Scourges disparam, e a copia do Charger tambem entra (2 de novo)
    assert s.proxy_damage_total - before >= 2 * 5


def test_miirym_copy_of_ur_dragon_doubles_attack_trigger():
    s = fresh(turn=6)
    put(s, "Miirym, Sentinel Wyrm")
    ud.enter_battlefield(s, ud.COMMANDER, from_hand=False, count_as_cast=False)
    s.creature_cast_turn[ud.COMMANDER] = 1
    s.commander_in_play = True
    s.dragon_token_list[0][1] = 1  # copia pronta
    s.hand = []
    ud.combat_step(s)
    # atacam Ur-Dragon, Miirym e a copia (3 Dragoes); 2 gatilhos -> 6 cartas
    assert s.urdragon_attack_draws_total == 6
    assert ud.dragon_discount_others(s, "Scourge of Valkas") == 2  # Eminence da copia


def test_miirym_copy_of_courser_puts_commander():
    s = fresh()
    put(s, "Miirym, Sentinel Wyrm", ud.COMMANDER)
    s.commander_in_play = True
    ud.enter_battlefield(s, "Hellkite Courser", from_hand=False)
    s2 = fresh()
    put(s2, "Miirym, Sentinel Wyrm")
    s2.creature_cast_turn["Miirym, Sentinel Wyrm"] = 0
    ud.create_dragon_tokens(s2, 1, 6, source="miirym_copy", copy_of="Hellkite Courser")
    assert s2.commander_in_play


def test_miirym_copy_of_firdoch_is_an_artifact():
    s = fresh(turn=6)
    put(s, "Miirym, Sentinel Wyrm")
    ud.enter_battlefield(s, "Firdoch Core", from_hand=False)
    assert s.firdoch_token_copies == 1 and s.dragon_tokens == 0
    assert ud.rocks_mana(s) == 2


def test_sarkhan_soul_aflame_copies_utvara_and_attacks():
    s = fresh(turn=6)
    put(s, ud.SARKHAN_SA, cast_turn=2)
    s.phase = "main1"
    ud.enter_battlefield(s, "Utvara Hellkite", from_hand=False)
    ud.choose_sarkhan_copy(s)
    assert s.sarkhan_copy_of == "Utvara Hellkite"
    assert ud.effective_power(s, ud.SARKHAN_SA) == 6 and ud.dragon_count(s) == 2
    assert ud.dragon_discount_others(s, "Scourge of Valkas") == 1  # perdeu o proprio desconto
    ud.combat_step(s)
    # so' o Sarkhan-Utvara ataca (a Utvara nomeada esta' doente): 2 Utvaras x 1 atacante
    assert s.dragon_tokens == 2
    ud.end_step(s)
    assert s.sarkhan_copy_of is None


def test_arcane_denial_draw_next_turn():
    s = fresh()
    put(s, "Island", "Forest")
    s.hand = ["Arcane Denial"]
    ud.cast_card(s, "Arcane Denial")
    n = len(s.hand)
    ud.play_turn(s, is_first_turn=False, on_play=True)
    assert s.arcane_denial_draws_total == 1


def test_path_scry_bottoms_land_when_flooded():
    s = fresh(library=["Forest", "Scourge of Valkas"])
    put(s, "Path of Ancestry", *WUBRG_LANDS, "Forest")
    s.hand = ["Hellkite Charger"]
    s.mana_spent_this_turn = 0
    ud.cast_card(s, "Hellkite Charger")
    assert s.path_scries_total == 1 and s.library[0] == "Scourge of Valkas"


def test_triome_cycling_in_main2():
    s = fresh(library=["Scourge of Valkas"] + [FILLER] * 20)
    put(s, *WUBRG_LANDS, "Forest")
    s.hand = ["Ketria Triome"]
    s.phase = "main2"
    ud.try_triome_cycling(s)
    assert s.triome_cycles_total == 1 and "Scourge of Valkas" in s.hand


def test_voyage_foretold_needs_bb_and_triggers_beanstalk():
    s = fresh(turn=7)
    s.haunting_voyage_foretold_turn = 5
    put(s, "Up the Beanstalk", "Mountain", "Mountain", "Mountain", "Forest", "Forest", "Forest", "Swamp")
    s.phase = "main1"
    ud.main_phase(s)
    assert s.haunting_voyage_foretold_turn == 5  # 1 fonte de B so'
    put(s, "Bayou")
    ud.main_phase(s)
    assert s.haunting_voyage_foretold_turn is None and "Haunting Voyage" in s.graveyard


def test_opponent_attacks_sarkhan_unbroken():
    s = fresh(turn=ud.INTERACTION_SETUP_TURNS + 2)
    s.interaction_rng = _AlwaysRng()
    s.interaction_rng.choice = lambda seq: ("Elemental Token", 3)
    put(s, "Sarkhan Unbroken")
    s.sarkhan_loyalty = 5
    life = s.life
    ud.try_smart_opponent_attack(s)
    assert s.sarkhan_loyalty == 2 and s.life == life
    ud.try_smart_opponent_attack(s)
    assert "Sarkhan Unbroken" in s.graveyard


def test_pain_and_henge_life():
    s = fresh()
    put(s, "Ancient Tomb", "Forest", "The Great Henge")
    s.mana_spent_this_turn = 2   # cabe nas fontes sem dor (Forest + Henge)
    ud.settle_mana_life(s)
    assert s.life == 42
    s.mana_spent_this_turn = 5
    ud.settle_mana_life(s)
    assert s.life == 42 + 2 - 2


def test_sylvan_library_pays_four():
    s = fresh(library=[FILLER] * 20)
    put(s, "Sylvan Library")
    ud.play_turn(s, is_first_turn=False, on_play=True)
    assert s.life_paid.get("sylvan_library") == 4


def test_treasure_mana_pays_a_pip():
    s = fresh()
    put(s, "Forest", "Forest", "Forest")
    assert not ud.can_cast(s, "Dragon Tempest")
    ud.create_and_use_treasures(s, 1)
    assert ud.can_cast(s, "Dragon Tempest")


def test_deck_out_is_a_loss_and_stops_the_game():
    s = fresh(turn=6, library=[FILLER] * 3)
    put(s, ud.COMMANDER)
    s.commander_in_play = True
    ud.draw_cards(s, 5)
    assert s.decked_turn == 6 and s.lethal_proxy_turn is None and s.game_over
    t = s.turn
    ud.play_turn(s, is_first_turn=False, on_play=True)
    assert s.turn == t


def test_deck_out_after_lethal_damage_is_a_win():
    s = fresh(turn=6, library=[])
    s.proxy_damage_total = ud.LETHAL_PROXY
    ud.draw_cards(s, 1)
    assert s.lethal_proxy_turn == 6 and s.decked_turn is None


def test_attackers_limited_to_not_deck():
    s = fresh(turn=6, library=[FILLER] * 4)
    put(s, ud.COMMANDER)
    s.commander_in_play = True
    s.dragon_token_list = [[5, 1, True, None] for _ in range(10)]
    s.dragon_tokens = 10
    s.hand = []
    ud.combat_step(s)
    assert s.decked_turn is None and s.urdragon_attack_draws_total == 3 and len(s.library) == 1
    assert s.attackers_held_back_total == 8


def test_optional_draws_refused_with_low_library():
    s = fresh(library=[FILLER] * 5)
    put(s, "Dragon's Hoard", "Forest", "Forest")
    s.dragon_hoard_gold_counters = 2
    ud.try_dragon_hoard_draw(s)
    assert s.dragon_hoard_draws_total == 0


def test_miirym_bladewing_terror_loop_is_lethal():
    # Commander Spellbook 380-1110-3362
    s = fresh(turn=7, library=[FILLER] * 40)
    put(s, "Miirym, Sentinel Wyrm", "Terror of the Peaks")
    ud.enter_battlefield(s, "Bladewing the Risen", from_hand=False)
    assert s.bladewing_loop_turn == 7 and s.bladewing_loop_iterations_total > 0
    assert s.proxy_damage_total >= ud.LETHAL_PROXY
    assert "Bladewing the Risen" in s.battlefield and s.decked_turn is None


def test_bladewing_without_killer_does_not_loop():
    s = fresh(turn=7)
    put(s, "Miirym, Sentinel Wyrm")
    ud.enter_battlefield(s, "Bladewing the Risen", from_hand=False)
    assert s.bladewing_loop_turn is None and s.bladewing_loop_iterations_total == 0


def test_bladewing_loop_stops_before_decking():
    # Elemental Bond + Garruk's Uprising: 2 compras obrigatorias por Dragao que entra
    s = fresh(turn=7, library=[FILLER] * 12)
    put(s, "Miirym, Sentinel Wyrm", "Terror of the Peaks", "Elemental Bond", "Garruk's Uprising")
    ud.enter_battlefield(s, "Bladewing the Risen", from_hand=False)
    assert s.decked_turn is None and len(s.library) >= 1
    assert s.proxy_damage_total < ud.LETHAL_PROXY


def test_scourge_can_be_the_killer_with_four_dragons():
    s = fresh(turn=7, library=[FILLER] * 40)
    put(s, "Miirym, Sentinel Wyrm", "Scourge of Valkas", "Hellkite Charger")
    ud.enter_battlefield(s, "Bladewing the Risen", from_hand=False)
    assert s.bladewing_loop_iterations_total > 0 and s.proxy_damage_total >= ud.LETHAL_PROXY


def test_gnawbone_charger_loop_repeats_combats():
    # Commander Spellbook 1800-3398: cada combate da' >= 12 Treasures, paga o proximo
    s = fresh(turn=7, library=[FILLER] * 40)
    put(s, "Old Gnawbone", "Hellkite Charger", "Mountain", "Mountain", "Forest", "Forest", "Forest", "Forest", "Forest")
    s.phase = "combat"
    ud.combat_step(s)
    ud.try_hellkite_charger_extra_combat(s)
    assert s.hellkite_charger_extra_combats >= 3
    assert s.proxy_damage_total + s.combat_damage_proxy_total >= ud.LETHAL_PROXY


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

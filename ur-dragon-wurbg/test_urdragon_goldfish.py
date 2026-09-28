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

"""
Testes dirigidos do simulador da Toph (CLAUDE.md, Regra #1: cada correcao
tem que DISPARAR de verdade). Rodada 2026-09-26 (reescrita do motor: mana
por permanente com cor, fichas reais, P/T/combate, fases, protecoes).

Rodar: python3 test_toph_goldfish.py   (sem pytest -- executor proprio no fim)
"""
import random
import traceback

import toph_goldfish_v1 as tg

C = tg.COLORLESS
ANY = tg.ANY


def fresh(turn: int = 5, library=None, hand=None) -> tg.GameState:
    s = tg.GameState(library=list(library) if library is not None else ["Forest"] * 40)
    s.turn = turn
    s.hand = list(hand or [])
    return s


def put(s, *names, turn=0, token=False, tapped=False):
    out = []
    for n in names:
        p = tg.mk_perm(s, n, token=token)
        p.entered_turn = turn
        p.tapped = tapped
        s.battlefield.append(p)
        if n == tg.COMMANDER:
            s.commander_in_play = True
        if n == "Wrenn and Realmbreaker":
            s.wrenn_loyalty = 4
        out.append(p)
    tg.touch(s)
    return out[0] if len(out) == 1 else out


def enter(s, name, token=False):
    p = tg.mk_perm(s, name, token=token)
    tg.enter_battlefield(s, p, [])
    return p


# --- dados das cartas --------------------------------------------------------

def test_commander_mv_is_4():
    assert tg.CARD_DB[tg.COMMANDER].mv == 4
    assert dict(tg.CARD_DB[tg.COMMANDER].pips) == {"R": 1, "G": 1, "W": 1}


# --- mana -------------------------------------------------------------------

def test_toph_artifact_land_has_no_mana_without_grant():
    s = fresh()
    put(s, tg.COMMANDER)
    clamp = put(s, "Skullclamp")
    assert tg.is_land(clamp, s) and tg.mana_units(clamp, s) == []


def test_wrenn_yavimaya_omen_give_artifact_lands_mana():
    s = fresh()
    put(s, tg.COMMANDER)
    clamp = put(s, "Skullclamp")
    put(s, "Yavimaya, Cradle of Growth")
    assert tg.mana_units(clamp, s) == [frozenset("G")]
    put(s, "Wrenn and Realmbreaker")
    assert tg.mana_units(clamp, s) == [ANY]


def test_sol_ring_under_toph_still_two():
    s = fresh()
    put(s, tg.COMMANDER)
    ring = put(s, "Sol Ring")
    assert tg.mana_units(ring, s) == [C, C]


def test_bounceland_taps_for_two():
    s = fresh()
    turf = put(s, "Gruul Turf")
    assert tg.mana_units(turf, s) == [frozenset("R"), frozenset("G")]


def test_lotus_cobra_mana_is_spendable():
    s = fresh(hand=["Forest"])
    put(s, "Lotus Cobra")
    assert not tg.pay(s, 1, (), dry=True)
    tg.play_land(s, [])
    # Forest (1) + Cobra (1 flutuando)
    assert tg.pay(s, 2, (), dry=True)


def test_treasure_is_consumed():
    s = fresh()
    tg.create_token(s, "Treasure", [])
    assert not tg.pay(s, 1, (("R", 1),), dry=True)  # 1 Treasure = 1 mana so'
    s2 = fresh()
    tg.create_token(s2, "Treasure", [])
    tg.pay(s2, 0, (("R", 1),), [])
    assert not any(p.card.name == "Treasure" for p in s2.battlefield)
    assert not tg.pay(s2, 0, (("R", 1),), dry=True)


def test_ashaya_creature_land_is_sick():
    s = fresh(turn=5)
    put(s, "Ashaya, Soul of the Wild")
    cub = put(s, "Badgermole Cub", turn=5)
    assert tg.is_land(cub, s) and tg.mana_units(cub, s) == []
    cub.entered_turn = 4
    assert tg.mana_units(cub, s) == [frozenset("G")]


def test_ba_sing_se_tap_is_not_also_mana():
    s = fresh()
    bss = put(s, "Ba Sing Se")
    put(s, "Forest", "Forest")
    assert not tg.can_activate(s, bss, 2, (("G", 1),))  # precisa de 3 OUTRAS fontes
    put(s, "Forest")
    assert tg.can_activate(s, bss, 2, (("G", 1),))


def test_mycosynth_spends_as_any_color():
    s = fresh()
    put(s, "Sol Ring")
    assert not tg.pay(s, 0, (("W", 1),), dry=True)
    put(s, "Mycosynth Lattice")
    assert tg.pay(s, 0, (("W", 1),), dry=True)


def test_badgermole_adds_g_for_creature_tapped():
    s = fresh()
    put(s, "Badgermole Cub", "Enduring Vitality")
    # 2 criaturas tapando (EV da' a habilidade) -> 2 + 2 G extra
    assert tg.available_mana(s) == 4


def test_great_divide_guide_allies_tap():
    s = fresh()
    put(s, "Great Divide Guide", "Earthbending Student")
    assert tg.available_mana(s) == 2


def test_talon_gates_filter_costs_one():
    s = fresh()
    put(s, "Talon Gates of Madara", "Forest")
    assert tg.pay(s, 0, (("W", 1),), dry=True)       # Forest paga o {1} do filtro
    assert not tg.pay(s, 1, (("W", 1),), dry=True)


def test_commander_needs_three_colors():
    s = fresh()
    put(s, "Command Tower", "Forest", "Sol Ring")
    assert not tg.can_cast(s, tg.COMMANDER)  # R e W so' no Command Tower
    put(s, "Plains")
    assert tg.can_cast(s, tg.COMMANDER)


# --- landfall / terrenos -------------------------------------------------------

def test_fetch_triggers_two_landfalls():
    s = fresh(hand=["Wooded Foothills"])
    put(s, "Toph, Earthbending Master")
    tg.play_land(s, [])
    assert s.experience_counters == 2


def test_fetch_finds_typed_dual():
    s = fresh(library=["Stomping Ground"], hand=["Wooded Foothills"])
    tg.play_land(s, [])
    assert any(p.card.name == "Stomping Ground" for p in s.battlefield)


def test_horizon_explorer_untaps_earthbend_return():
    s = fresh()
    put(s, "Horizon Explorer")
    land = put(s, "Forest")
    tg.apply_earthbend(s, 1, [], "test", triggered=False, target=land)
    tg.leave_battlefield(s, land, [], reason="destroy")
    back = next(p for p in s.battlefield if p.card.name == "Forest")
    assert back.tapped is False and s.motor16_recursions == 1


def test_nissa_reveals_elf_or_elemental():
    s = fresh(library=["Forest", "Mountain", "Mossborn Hydra", "Plains"])
    put(s, "Nissa, Resurgent Animist")
    enter(s, "Forest")
    enter(s, "Forest")
    assert "Mossborn Hydra" in s.hand and "Mountain" not in s.hand


def test_tannuk_second_resolution_and_damage():
    s = fresh(library=["Plains"] * 5)
    put(s, "Tannuk, Memorial Ensign")
    enter(s, "Forest")
    assert s.table_damage_total == 3 and len(s.hand) == 0
    enter(s, "Forest")
    assert s.table_damage_total == 6 and len(s.hand) == 1


def test_bounceland_returns_tapped_basic():
    s = fresh()
    a = put(s, "Forest", tapped=True)
    put(s, "Command Tower")
    enter(s, "Gruul Turf")
    assert "Forest" in s.hand and a not in s.battlefield


def test_fetch_put_by_kodama_is_cracked():
    s = fresh(library=["Mountain"], hand=["Wooded Foothills"])
    put(s, "Kodama of the East Tree")
    enter(s, "Forest")
    assert any(p.card.name == "Mountain" for p in s.battlefield)
    assert "Wooded Foothills" in s.graveyard


def test_per_turn_counters_reset_on_opponent_turn():
    s = fresh(turn=5, library=["Plains"] * 5)
    s.interaction_rng = random.Random(0)
    tan = put(s, "Tannuk, Memorial Ensign")
    enter(s, "Forest")
    assert tan.landfall_resolutions == 1
    tg.try_smart_opponent_turn(s, [])
    assert tan.landfall_resolutions == 0 and s.token_drawn_this_turn is False


def test_commander_damage_tracked():
    s = fresh(turn=5)
    put(s, tg.COMMANDER)
    tg.combat_step(s, [])
    assert s.commander_damage_dealt == 3


# --- fichas -------------------------------------------------------------------

def test_scute_insect_is_permanent_and_skullclamp_fodder():
    s = fresh(library=["Plains"] * 10)
    put(s, "Scute Swarm", "Skullclamp", "Forest", "Forest")
    enter(s, "Forest")
    insect = next(p for p in s.battlefield if p.card.name == "Insect")
    assert tg.is_creature_type(insect, s)
    tg.skullclamp_loop(s, [])
    assert s.skullclamp_draws >= 1 and insect not in s.battlefield


def test_earthbend_token_does_not_return():
    s = fresh()
    ev = tg.create_token(s, "Everywhere", [])
    tg.apply_earthbend(s, 1, [], "test", triggered=False, target=ev)
    tg.leave_battlefield(s, ev, [], reason="destroy")
    assert not any(p.card.name == "Everywhere" for p in s.battlefield)


def test_earthbend_zero_kills_and_returns():
    s = fresh()
    put(s, "Toph, Earthbending Master")
    land = put(s, "Forest", tapped=True)
    tg.apply_earthbend(s, 0, [], "Toph EM X=0")
    assert land not in s.battlefield and s.motor16_recursions == 1
    assert s.experience_counters == 1  # landfall do retorno


def test_horizon_explorer_one_lander_per_player():
    s = fresh(turn=5)
    put(s, "Horizon Explorer")
    put(s, "Forest", "Forest", "Forest")
    for _ in range(3):
        put(s, "Scute Swarm")
    tg.combat_step(s, [])
    assert sum(1 for p in s.battlefield if p.card.name == "Lander") == 3


def test_lander_fetches_basic():
    s = fresh(library=["Mountain"])
    put(s, "Forest", "Forest")
    tg.create_token(s, "Lander", [])
    tg.lander_activations(s, [])
    assert any(p.card.name == "Mountain" for p in s.battlefield)


# --- gatilhos compartilhados --------------------------------------------------

def test_kodama_triggers_on_noncreature_and_no_chain():
    s = fresh(hand=["Mox Opal", "Zuran Orb"])
    put(s, "Kodama of the East Tree")
    enter(s, "Mishra's Bauble")   # valor de mana 0, NAO criatura
    assert s.kodama_cheats == 1   # Mox Opal/Zuran Orb (0) -- o que entrou pelo Kodama nao re-dispara
    assert len(s.hand) == 1


def test_kodama_ignores_mdfc_in_hand():
    s = fresh(hand=["Bala Ged Recovery // Bala Ged Sanctuary"])
    put(s, "Kodama of the East Tree")
    enter(s, "Forest")
    assert s.kodama_cheats == 0


def test_earth_kingdom_general_counts_bumi_counters():
    s = fresh(turn=5)
    put(s, "Earth Kingdom General")
    bumi = put(s, "Bumi, Eclectic Earthbender")
    land = put(s, "Forest")
    land.earthbent = True
    tg.combat_step(s, [])
    assert s.life_total >= 42  # 2 contadores do Bumi -> ganha 2


def test_bristly_bill_doubles_only_creature_plus1():
    s = fresh()
    put(s, "Bristly Bill, Spine Sower")
    asc = put(s, "Earthbender Ascension")
    asc.quest_counters = 3
    hydra = put(s, "Mossborn Hydra")
    hydra.counters = 3
    put(s, "Forest", "Forest", "Forest", "Forest", "Forest")
    tg.try_bristly_bill_double(s, [])
    assert asc.quest_counters == 3 and hydra.counters >= 6


def test_ozolith_ignores_noncreature():
    s = fresh()
    put(s, "The Ozolith")
    asc = put(s, "Earthbender Ascension")
    asc.counters = 3  # (nao-criatura)
    tg.leave_battlefield(s, asc, [], reason="destroy")
    assert s.ozolith_counters == 0


def test_resonator_never_copies_earthshape_or_ba_sing_se():
    s = fresh(hand=["Earthshape"])
    put(s, "Strionic Resonator", "Forest", "Forest", "Forest", "Plains", "Forest", "Forest")
    tg.cast_spell(s, "Earthshape", [])
    assert s.resonator_copies == 0
    tg.apply_earthbend(s, 2, [], "Badgermole (ETB)")  # gatilho de verdade: copia
    assert s.resonator_copies == 1


def test_toph_greatest_x_is_mana_spent():
    s = fresh(hand=["Toph, Greatest Earthbender"])
    put(s, "Stomping Ground", "Forest", "Forest", "Forest")
    tg.cast_spell(s, "Toph, Greatest Earthbender", [])
    assert max(p.counters for p in s.battlefield) == 4
    s2 = fresh(hand=["Toph, Greatest Earthbender"])
    put(s2, "Kodama of the East Tree", "Forest")
    enter(s2, "Iron Spider, Stark Upgrade")  # MV 3 < 4: Kodama nao pode
    assert s2.kodama_cheats == 0


# --- custos / habilidades ------------------------------------------------------

def test_urza_saga_iii_uses_mana_cost_not_mv():
    s = fresh(library=["Esper Sentinel", "Zuran Orb"])
    saga = put(s, "Urza's Saga")
    saga.saga_chapter = 2
    tg.upkeep_and_draw(s, [])
    assert any(p.card.name == "Zuran Orb" for p in s.battlefield)
    assert not any(p.card.name == "Esper Sentinel" for p in s.battlefield)


def test_wrenn_ultimate_pays_loyalty():
    s = fresh()
    w = put(s, "Wrenn and Realmbreaker")
    s.wrenn_loyalty = 7
    tg.wrenn_loyalty_ability(s, [])
    assert s.wrenn_emblem and w not in s.battlefield


def test_iron_spider_tap_respects_summoning_sickness():
    s = fresh(turn=5)
    sp = put(s, "Iron Spider, Stark Upgrade", turn=5)
    tg.iron_spider_abilities(s, [])
    assert sp.tapped is False


def test_germination_paradigm_once_per_turn_and_exiled():
    s = fresh(hand=["Germination Practicum"])
    hydra = put(s, "Mossborn Hydra")
    put(s, "Forest", "Forest", "Forest", "Forest", "Forest")
    tg.cast_spell(s, "Germination Practicum", [])
    assert "Germination Practicum" in s.exile and "Germination Practicum" not in s.graveyard
    c0 = hydra.counters
    s.turn += 1
    tg.main_phase(s, [], first=True)
    tg.main_phase(s, [], first=True)
    assert hydra.counters == c0 + 2


def test_overlord_impending():
    s = fresh(hand=["Overlord of the Hauntwoods"])
    put(s, "Forest", "Forest", "Forest")
    tg.cast_loop(s, [], None)
    ov = next(p for p in s.battlefield if p.card.name == "Overlord of the Hauntwoods")
    assert ov.impending and ov.time_counters == 4 and not tg.is_creature_type(ov, s)
    assert any(p.card.name == "Everywhere" for p in s.battlefield)
    for _ in range(4):
        tg.end_step(s, [])
    assert tg.is_creature_type(ov, s)


def test_springheart_bestow_copies_host():
    s = fresh(hand=["Springheart Nantuko"])
    put(s, "Earthbending Student", "Forest", "Forest", "Forest", "Forest")
    tg.cast_loop(s, [], None)
    sp = next(p for p in s.battlefield if p.card.name == "Springheart Nantuko")
    assert sp.bestowed
    enter(s, "Forest")
    assert s.springheart_copies == 1


def test_sapling_affinity_for_forests():
    s = fresh()
    for _ in range(6):
        put(s, "Forest")
    assert tg.cast_cost(s, "Sapling Nursery")[0] == 0


def test_great_henge_cost_reduced_by_greatest_power():
    s = fresh()
    put(s, "Avatar Kyoshi, Earthbender")
    assert tg.cast_cost(s, "The Great Henge")[0] == 1


def test_talon_gates_from_hand():
    s = fresh(hand=["Talon Gates of Madara"])
    put(s, "Forest", "Forest", "Forest", "Forest")
    s.lands_played_this_turn = 1
    tg.talon_gates_from_hand(s, [])
    assert any(p.card.name == "Talon Gates of Madara" for p in s.battlefield)


def test_jetmir_cycling():
    s = fresh(hand=["Jetmir's Garden"], library=["Plains"])
    for _ in range(7):
        put(s, "Forest")
    s.lands_played_this_turn = 1
    tg.jetmir_cycling(s, [])
    assert "Jetmir's Garden" in s.graveyard and "Plains" in s.hand


def test_skullclamp_repeats():
    s = fresh(library=["Plains"] * 10)
    put(s, "Skullclamp", "Forest", "Forest", "Forest")
    for _ in range(3):
        tg.create_token(s, "Insect", [])
    tg.skullclamp_loop(s, [])
    assert s.skullclamp_draws == 3 and len(s.hand) == 6


def test_kci_sacrifices_returner_for_mana_and_landfall():
    s = fresh()
    put(s, tg.COMMANDER, "Krark-Clan Ironworks", "Toph, Earthbending Master")
    art = put(s, "Crucible of Worlds")
    tg.apply_earthbend(s, 1, [], "t", triggered=False, target=art)
    exp0 = s.experience_counters
    tg.sacrifice_engine(s, [])
    assert s.kci_sacrifices_of_recurring == 1 and s.experience_counters == exp0 + 1
    assert tg.COLORLESS in s.floating


def test_removal_is_held_not_cast():
    s = fresh(hand=["Swords to Plowshares"])
    put(s, "Plains")
    tg.cast_loop(s, [], None)
    assert "Swords to Plowshares" in s.hand


def test_discard_to_seven():
    s = fresh(hand=["Forest"] * 5 + ["Krang, Utrom Warlord"] * 4)
    tg.cleanup(s, [])
    assert len(s.hand) == 7


# --- P/T e combate --------------------------------------------------------------

def test_earthbend_sets_base_zero():
    s = fresh()
    put(s, tg.COMMANDER)
    spider = put(s, "Iron Spider, Stark Upgrade")
    tg.apply_earthbend(s, 1, [], "t", triggered=False, target=spider)
    assert tg.pt(spider, s) == (1, 1)


def test_double_strike_land_creatures():
    s = fresh(turn=5)
    put(s, "Toph, Greatest Earthbender")
    land = put(s, "Forest")
    tg.apply_earthbend(s, 3, [], "t", triggered=False, target=land)
    tg.combat_step(s, [])
    assert s.combat_damage_proxy_total == 3 * 2 + 3  # terreno 3 x2 + Toph GE 3


def test_sword_untaps_lands():
    s = fresh(turn=5)
    k = put(s, "Kodama of the East Tree")
    sw = put(s, "Sword of Feast and Famine")
    sw.attached_to = k.uid
    f = put(s, "Forest", tapped=True)
    tg.touch(s)
    tg.combat_step(s, [])
    assert f.tapped is False and s.sword_untaps == 1


def test_greaves_gives_haste():
    s = fresh(turn=5)
    b = put(s, "Bumi, Eclectic Earthbender", turn=5)
    put(s, "Lightning Greaves")
    tg.equip_lightning_greaves(s, [])
    assert not tg.is_sick(b, s)


def test_krang_gives_other_artifact_creatures_haste_and_indestructible():
    s = fresh(turn=5)
    put(s, "Krang, Utrom Warlord")
    ul = put(s, "Ultron, Artificial Malevolence", turn=5)
    assert not tg.is_sick(ul, s) and tg.is_indestructible(ul, s)


def test_caretaker_level3_pumps_creature_tokens():
    s = fresh()
    ct = put(s, "Caretaker's Talent")
    ct.level = 3
    tg.touch(s)
    ins = tg.create_token(s, "Insect", [])
    assert tg.pt(ins, s) == (3, 3)


def test_construct_counts_artifacts():
    s = fresh()
    put(s, "Sol Ring", "Mox Opal")
    c = tg.create_token(s, "Construct", [])
    assert tg.pt(c, s) == (3, 3)


def test_enduring_vitality_returns_as_enchantment():
    s = fresh()
    ev = put(s, "Enduring Vitality")
    tg.leave_battlefield(s, ev, [], reason="destroy")
    back = next(p for p in s.battlefield if p.card.name == "Enduring Vitality")
    assert back.enchantment_only and not tg.is_creature_type(back, s)


# --- resiliencia ------------------------------------------------------------------

def test_heroic_intervention_saves_from_wipe():
    s = fresh(turn=5, hand=["Heroic Intervention"])
    s.interaction_rng = random.Random(1)
    put(s, "Forest", "Forest")
    k = put(s, "Kodama of the East Tree")
    tg.try_protection_response(s, [], "wipe_creature", [k])
    assert tg.is_indestructible(k, s)


def test_teferis_protection_phases_out_and_blocks_attacks():
    s = fresh(turn=5, hand=["Teferi's Protection"])
    s.interaction_rng = random.Random(1)
    put(s, "Plains", "Forest", "Forest")
    ks = [put(s, "Kodama of the East Tree") for _ in range(3)]
    tg.try_protection_response(s, [], "wipe_creature", ks)
    assert all(p.phased_out for p in s.battlefield) and "Teferi's Protection" in s.exile
    assert s.tp_protected_until == s.turn


def test_greaves_shroud_blocks_removal_target():
    s = fresh(turn=5)
    ul = put(s, "Ultron, Artificial Malevolence")
    gr = put(s, "Lightning Greaves")
    gr.attached_to = ul.uid
    tg.touch(s)
    assert not tg.is_targetable_by_opponent(ul, s)


# --- reprodutibilidade ---------------------------------------------------------

def test_simulate_deterministic():
    a = tg.simulate_one(9_123_456)[0]
    b = tg.simulate_one(9_123_456)[0]
    assert (a.turn, a.table_damage_total, a.cards_drawn_extra, len(a.battlefield)) == \
           (b.turn, b.table_damage_total, b.cards_drawn_extra, len(b.battlefield))


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

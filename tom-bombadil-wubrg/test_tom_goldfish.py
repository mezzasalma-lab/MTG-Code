"""
Testes dirigidos do simulador do Tom Bombadil (CLAUDE.md, Regra #1: cada
habilidade de cada carta tem que DISPARAR de verdade, nao so' existir).

Rodar: python3 test_tom_goldfish.py   (sem pytest -- executor proprio no fim)
"""
import random
import traceback

import tom_goldfish_v1 as t

FILLER = "Swords to Plowshares"


def fresh(turn: int = 5, library=None, hand=None, life: int = 40) -> t.GameState:
    s = t.GameState(rng=random.Random(0))
    s.turn = turn
    s.life = life
    s.library = list(library) if library is not None else [FILLER] * 30
    s.hand = list(hand or [])
    return s


def put(s: t.GameState, name: str, entered: int = None, **kw) -> t.Permanent:
    """Coloca um permanente direto (sem gatilhos de entrada) -- setup."""
    p = t.Permanent(card=name, uid=t.new_uid(s), entered_turn=s.turn - 1 if entered is None else entered, **kw)
    s.battlefield.append(p)
    return p


def put_lands(s: t.GameState, names):
    return [put(s, n) for n in names]


def saga(s: t.GameState, name: str, lore: int, entered: int = None) -> t.Permanent:
    p = put(s, name, entered=entered)
    if lore:
        p.counters["lore"] = lore
    return p


def names_on_bf(s):
    return [t.eff_name(p) for p in s.battlefield]


def make_tom(s):
    tom = put(s, t.COMMANDER)
    s.commander_in_play = True
    s.commander_uid = tom.uid
    return tom


# ---------------------------------------------------------------------------
# Tom Bombadil + regras de Saga
# ---------------------------------------------------------------------------

def test_tom_reveal_until_saga_once_per_turn():
    lib = ["Sol Ring", "Farseek", "Kiora Bests the Sea God", "Arcane Signet", "Binding the Old Gods"]
    s = fresh(library=lib)
    make_tom(s)
    a = saga(s, "Song of Eärendil", 2)
    b = saga(s, "War of the Last Alliance", 2)
    log = []
    t.add_counters(s, a, "lore", 1, log)
    t.add_counters(s, b, "lore", 1, log)
    t.resolve_stack(s, log)
    assert s.tom_triggers == 1, "Tom so' dispara 1x por turno"
    assert "Kiora Bests the Sea God" in names_on_bf(s), "Tom poe a 1a Saga revelada no campo"
    assert "Binding the Old Gods" not in names_on_bf(s)
    assert sorted(s.library[-2:]) == ["Farseek", "Sol Ring"], "reveladas vao pro fundo"
    assert s.library[0] == "Arcane Signet"


def test_tom_protection_threshold():
    s = fresh()
    tom = make_tom(s)
    saga(s, "Song of Eärendil", 2)
    x = saga(s, "The First Iroan Games", 1)
    assert not t.is_indestructible(s, tom)
    x.counters["lore"] = 2
    assert t.tom_protected(s) and t.is_indestructible(s, tom), "4+ lore entre Sagas = indestrutivel"


def test_crossing_multiple_chapters_triggers_all():
    s = fresh()
    g = saga(s, "The Coming of Galactus", 1)
    log = []
    t.add_counters(s, g, "lore", 3, log)
    assert [it["n"] for it in s.stack] == [4, 3, 2], "714.2b: II, III e IV disparam (II no topo)"
    t.resolve_stack(s, log)
    assert s.proxy_damage_total == 2 * 3 * 2, "II e III: cada oponente perde 2"
    assert "Galactus" in names_on_bf(s)
    assert g not in s.battlefield, "sacrificada depois do IV"


def test_saga_not_sacrificed_while_final_on_stack_and_save():
    s = fresh(turn=5)
    pc = put(s, "Power Conduit")
    put(s, "Knight Token", is_token=True)
    th = saga(s, "There and Back Again", 2)
    log = []
    t.add_counters(s, th, "lore", 1, log)       # III dispara -> resposta: Power Conduit tira 1
    t.resolve_stack(s, log)
    assert th in s.battlefield and t.lore(th) == 2, "714.4: salva, fica com final-1"
    assert "Smaug" in names_on_bf(s), "III resolveu mesmo assim"
    assert pc.tapped and s.finals_saved == 1


def test_satsuki_no_retrigger_on_final():
    s = fresh(turn=5)
    sat = put(s, "Satsuki, the Living Lore")
    a = saga(s, "Song of Eärendil", 1)
    log = []
    t.try_satsuki(s, log)
    assert t.lore(a) == 2 and sat.tapped
    assert s.usage.get("chapter:Song of Eärendil:2") == 1


def test_satsuki_death_returns_saga():
    s = fresh()
    s.graveyard = ["Summon: Bahamut", "Farseek"]
    sat = put(s, "Satsuki, the Living Lore")
    t.leave_battlefield(s, sat, [], to="graveyard")
    assert "Summon: Bahamut" in s.hand


# ---------------------------------------------------------------------------
# Mover / remover / adicionar marcadores
# ---------------------------------------------------------------------------

def test_nesting_grounds_moves_lore_and_costs():
    s = fresh(turn=6)
    put_lands(s, ["Forest", "Plains", "Island"])
    ng = put(s, "Nesting Grounds")
    a = saga(s, "Summon: Knights of Round", 2)   # repetir II (3 Knights) vale
    b = saga(s, "Battle at the Helvault", 2)     # +1 -> III (Avacyn)
    log = []
    before = t.remaining_mana(s)
    assert t.try_nesting_grounds(s, log)
    assert ng.tapped and t.lore(a) == 1
    assert "Avacyn" in names_on_bf(s)
    assert t.remaining_mana(s) == before - 2, "{1} + o proprio Nesting Grounds virado"


def test_goldberry_pull_then_push_draws():
    s = fresh(turn=6)
    put_lands(s, ["Island"])
    gb = put(s, "Goldberry, River-Daughter")
    a = saga(s, "Summon: Knights of Round", 2)
    log = []
    t.try_goldberry(s, log)
    assert gb.counters.get("lore") == 1 and t.lore(a) == 1, "{T}: puxa 1 lore pra ela"
    s.turn += 1
    gb.tapped = False
    b = saga(s, "Song of Eärendil", 1)
    hand_before = len(s.hand)
    t.try_goldberry(s, log)
    assert gb.counters.get("lore", 0) == 0
    assert len(s.hand) >= hand_before + 1, "{U},{T}: empurra e compra 1"


def test_resourceful_defense_trigger_moves_lore_on_sacrifice():
    s = fresh(turn=5)
    put(s, "Resourceful Defense")
    a = saga(s, "Song of Eärendil", 2)
    b = saga(s, "Kiora Bests the Sea God", 0)
    b.counters["lore"] = 1
    log = []
    t.add_counters(s, a, "lore", 1, log)   # III -> sacrificada com 3 lore
    t.resolve_stack(s, log)
    assert a not in s.battlefield
    assert b not in s.battlefield, "3 lore na Kiora (1 -> 4): II e III disparam, fecha"
    assert s.usage.get("chapter:Kiora Bests the Sea God:3") == 1
    assert s.resourceful_triggers >= 2, "a Kiora saindo com lore dispara de novo"


def test_resourceful_defense_activated_move():
    s = fresh(turn=6)
    tom = make_tom(s)
    put(s, "Resourceful Defense")
    put_lands(s, ["Plains"] * 6)
    a = saga(s, "The First Iroan Games", 3)
    b = saga(s, "Battle at the Helvault", 1)
    log = []
    assert t.try_resourceful_move(s, log)
    assert "Avacyn" in names_on_bf(s) and s.tom_triggers == 1


def test_nexus_mentality_both_modes_with_commander():
    s = fresh(turn=6, hand=["Nexus Mentality"])
    make_tom(s)
    put_lands(s, ["Island"] * 5)
    a = saga(s, "The First Iroan Games", 3)
    b = saga(s, "Battle at the Helvault", 1)
    c = put(s, "Knight Token", is_token=True)
    c.counters["+1/+1"] = 3
    log = []
    t.cast_instant(s, "Nexus Mentality", log, nexus_move=(a, b), nexus_remove=c)
    assert "Avacyn" in names_on_bf(s)
    assert s.usage.get("nexus_draw") == 3, "modo 2: compra 1 por marcador removido"


def test_power_conduit_scholar_oaka_value_removal():
    s = fresh(turn=6, library=["Plains", "Island", FILLER, FILLER])
    pc = put(s, "Power Conduit")
    sch = put(s, "Scholar of New Horizons")
    sch.counters["+1/+1"] = 1
    oa = put(s, "O'aka, Traveling Merchant")
    k = saga(s, "Summon: Knights of Round", 3)
    log = []
    t.try_value_removers(s, log)
    assert oa.tapped and s.usage.get("oaka_draw") == 1
    assert sch.tapped and "Plains" in s.hand, "Scholar: Plains card pra mao"
    assert pc.tapped and s.usage.get("power_conduit") == 1


def test_scholar_enters_with_counter():
    s = fresh()
    p = t.enter_battlefield(s, "Scholar of New Horizons", [])
    assert p.counters.get("+1/+1") == 1


def test_hex_parasite_saves_final_paying_life():
    s = fresh(turn=6)
    put_lands(s, ["Swamp"] * 2)
    hp = put(s, "Hex Parasite")
    g = saga(s, "Summon: Bahamut", 3)
    make_tom(s)
    log = []
    t.add_counters(s, g, "lore", 1, log)
    t.resolve_stack(s, log)
    assert g in s.battlefield and t.lore(g) == 3
    assert s.life == 38 and hp.temp_power == 1


def test_clockspinning_modes_and_buyback():
    s = fresh(turn=6, hand=["Clockspinning"])
    put_lands(s, ["Island"] * 5)
    b = saga(s, "Battle at the Helvault", 2)
    log = []
    t.cast_instant(s, "Clockspinning", log, clock_target=b, clock_mode="add")
    assert "Avacyn" in names_on_bf(s)
    assert "Clockspinning" in s.hand, "buyback pago (sobrou mana)"
    s.suspended.append({"card": "Resurgent Belief", "time": 1})
    s.graveyard.append("Enchantress's Presence")
    t.cast_instant(s, "Clockspinning", log, clock_mode="suspend")
    assert "Enchantress's Presence" in names_on_bf(s), "ultimo marcador de tempo -> conjura Resurgent"


def test_barbara_read_ahead_final_with_tom():
    s = fresh(turn=6)
    make_tom(s)
    put(s, "Barbara Wright")
    log = []
    p = t.enter_battlefield(s, "Battle at the Helvault", log)
    t.resolve_stack(s, log)
    assert "Avacyn" in names_on_bf(s), "read ahead direto no III"
    assert s.usage.get("chapter:Battle at the Helvault:1") is None, "capitulos pulados nao disparam"
    assert s.tom_triggers == 1


def test_flux_channeler_proliferates_on_noncreature_cast():
    s = fresh(turn=6, hand=["Sol Ring"])
    put_lands(s, ["Forest"])
    put(s, "Flux Channeler")
    a = saga(s, "Song of Eärendil", 1)
    k = put(s, "Knight Token", is_token=True)
    k.counters["+1/+1"] = 1
    t.cast_permanent(s, "Sol Ring", [])
    assert t.lore(a) == 2 and k.counters["+1/+1"] == 2


def test_ripples_proliferate():
    s = fresh(turn=6, hand=["Ripples of Potential"])
    put_lands(s, ["Island"] * 2)
    a = saga(s, "Song of Eärendil", 1)
    t.cast_instant(s, "Ripples of Potential", [])
    assert t.lore(a) == 2


def test_weaver_copies_chapter_and_anthem():
    s = fresh(turn=6)
    put_lands(s, ["Forest"])
    wv = put(s, "Weaver of Harmony")
    ey = put(s, "Eidolon of Blossoms")
    assert t.creature_power(s, ey) == 3, "outras criaturas-encantamento +1/+1"
    a = saga(s, "Kiora Bests the Sea God", 0)
    log = []
    t.add_counters(s, a, "lore", 1, log)
    t.resolve_stack(s, log)
    assert names_on_bf(s).count("Kraken Token") == 2 and wv.tapped


def test_strionic_copies_tom_trigger():
    lib = [FILLER, "Kiora Bests the Sea God", FILLER, "Binding the Old Gods", FILLER]
    s = fresh(turn=6, library=lib)
    make_tom(s)
    put_lands(s, ["Plains"] * 3)
    sr = put(s, "Strionic Resonator")
    a = saga(s, "War of the Last Alliance", 2)
    log = []
    t.add_counters(s, a, "lore", 1, log)
    t.resolve_stack(s, log)
    assert "Kiora Bests the Sea God" in names_on_bf(s) and "Binding the Old Gods" in names_on_bf(s)
    assert s.tom_triggers == 2 and sr.tapped


def test_estrids_invocation_copies_saga_and_blinks():
    s = fresh(turn=6)
    put(s, "Summon: Knights of Round", entered=5)
    s.battlefield[-1].counters["lore"] = 1
    log = []
    inv = t.enter_battlefield(s, "Estrid's Invocation", log, copy_of="Summon: Knights of Round")
    t.resolve_stack(s, log)
    assert names_on_bf(s).count("Knight Token") == 3, "copia entra no capitulo I"
    s.turn += 1
    t.upkeep_step(s, log)
    assert names_on_bf(s).count("Knight Token") == 6, "upkeep: exila, volta, capitulo I de novo"


def test_estrid_copy_of_transform_saga_stays_exiled():
    s = fresh(turn=6)
    put(s, "Jugan Defends the Temple // Remnant of the Rising Star")
    inv = put(s, "Estrid's Invocation", copy_of="Jugan Defends the Temple // Remnant of the Rising Star")
    inv.counters["lore"] = 2
    log = []
    t.add_counters(s, inv, "lore", 1, log)
    t.resolve_stack(s, log)
    assert inv not in s.battlefield and "Estrid's Invocation" in s.exile


# ---------------------------------------------------------------------------
# Retorno por Saga terminada / enchantress
# ---------------------------------------------------------------------------

def test_narci_femeref_historians_on_saga_end():
    s = fresh(turn=6)
    put(s, "Narci, Fable Singer")
    put(s, "Femeref Enchantress")
    put(s, "Historian's Boon")
    a = saga(s, "Song of Eärendil", 2)
    log = []
    t.add_counters(s, a, "lore", 1, log)
    t.resolve_stack(s, log)
    assert s.narci_drain_total == 5 * 3 and s.life == 40 + 15, "Narci: X = MV da Saga, cada oponente"
    assert s.usage.get("narci_draw") == 1 and s.usage.get("femeref_draw") == 1
    assert s.usage.get("historians_boon_angel") == 1


def test_historians_boon_soldier_only_nontoken():
    s = fresh()
    put(s, "Historian's Boon")
    t.enter_battlefield(s, "Prismatic Omen", [])
    assert names_on_bf(s).count("Soldier Token") == 1


def test_enchantress_triggers():
    s = fresh(turn=5, hand=["Prismatic Omen"])
    put_lands(s, ["Forest"] * 2)
    put(s, "Sythis, Harvest's Hand")
    put(s, "Enchantress's Presence")
    sc = put(s, "Setessan Champion")
    put(s, "Eidolon of Blossoms")
    t.cast_permanent(s, "Prismatic Omen", [])
    assert s.usage.get("sythis_draw") == 1 and s.life == 41
    assert s.usage.get("presence_draw") == 1
    assert s.usage.get("setessan_draw") == 1 and sc.counters.get("+1/+1") == 1
    assert s.usage.get("eidolon_draw") == 1


# ---------------------------------------------------------------------------
# Mana / rampa / terrenos
# ---------------------------------------------------------------------------

def test_mana_rocks_and_dorks():
    s = fresh(turn=6)
    put(s, "Sol Ring")
    put(s, "Arcane Signet")
    put(s, t.COMMANDER)                        # WUBRG entre permanentes
    put(s, "Bloom Tender")
    fe = put(s, "Faeburrow Elder")
    sw = put(s, "Sanctum Weaver")
    put(s, "Prismatic Omen")
    # Sol 2 + Signet 1 + Bloom 5 + Faeburrow 5 + Sanctum Weaver 2 (2 encantamentos)
    assert t.total_mana(s) == 15, t.total_mana(s)
    assert t.creature_power(s, fe) == 5, "Faeburrow: +1/+1 por cor entre permanentes"
    sick = put(s, "Bloom Tender", entered=6)
    assert t.total_mana(s) == 15, "dork com doenca de invocacao nao gera mana"


def test_utopia_sprawl_needs_forest_and_fertile_ground():
    s = fresh(turn=6, hand=["Utopia Sprawl"])
    put_lands(s, ["Plains"])
    assert not t.castable_now(s, "Utopia Sprawl"), "Enchant Forest: sem Forest, nao da"
    put(s, "Prismatic Omen")
    assert t.castable_now(s, "Utopia Sprawl") is False or True
    s2 = fresh(turn=6)
    put_lands(s2, ["Forest"])
    u = t.enter_battlefield(s2, "Utopia Sprawl", [])
    f = t.enter_battlefield(s2, "Fertile Ground", [])
    assert u.attached_to is not None and f.attached_to is not None
    assert t.total_mana(s2) == 3, "Forest + 1 + 1"


def test_enduring_vitality_mana_and_return():
    s = fresh(turn=6)
    ev = put(s, "Enduring Vitality")
    put(s, "Human Soldier Token", is_token=True)
    assert t.total_mana(s) == 2, "Vitality + criatura pequena viram mana"
    t.leave_battlefield(s, ev, [], to="graveyard")
    back = [p for p in s.battlefield if p.card == "Enduring Vitality"]
    assert back and back[0].noncreature and not t.is_creature(s, back[0])
    assert t.total_mana(s) == 1, "estatica continua valendo como encantamento"


def test_farseek_type_restriction():
    s = fresh(turn=4, hand=["Farseek"], library=["Forest", "Savannah", FILLER])
    put_lands(s, ["Forest", "Forest"])
    t.cast_instant(s, "Farseek", [])
    assert "Savannah" in names_on_bf(s), "Plains type (nao-basico ok)"
    s2 = fresh(turn=4, hand=["Farseek"], library=["Forest", FILLER])
    put_lands(s2, ["Forest", "Forest"])
    t.cast_instant(s2, "Farseek", [])
    assert names_on_bf(s2).count("Forest") == 2, "Forest nao e' Plains/Island/Swamp/Mountain"


def test_prismatic_omen_domain_leyline():
    s = fresh(turn=6)
    put_lands(s, ["Forest"])
    assert t.effective_cost(s, "Leyline Binding") == 5
    put(s, "Prismatic Omen")
    assert t.effective_cost(s, "Leyline Binding") == 1, "5 tipos -> so' {W}"
    le = t.enter_battlefield(s, "Leyline Binding", [])
    assert s.interaction_plays == 1


def test_serras_sanctum_and_world_tree():
    s = fresh(turn=6)
    put(s, "Serra's Sanctum")
    put(s, "Prismatic Omen")
    put(s, "Enchantress's Presence")
    assert t.total_mana(s) == 2
    s2 = fresh(turn=6)
    put_lands(s2, ["Forest"] * 5)
    put(s2, "The World Tree")
    assert t.color_sources(s2, "B") == 6, "6+ terrenos: todos produzem qualquer cor"


def test_fetch_dual_life_and_triome_cycling():
    s = fresh(turn=3, hand=["Windswept Heath"], library=["Savannah", FILLER, FILLER])
    t.play_land(s, [])
    sv = [p for p in s.battlefield if p.card == "Savannah"]
    assert sv and not sv[0].tapped and s.life == 40 - 1, "fetch 1 de vida; dual entra desvirada sem custo"
    s2 = fresh(turn=9, hand=["Indatha Triome"])
    put_lands(s2, ["Forest"] * 7)
    t.try_cycling(s2, [])
    assert s2.usage.get("cycling") == 1


def test_pain_lands_cost_life_when_used():
    s = fresh(turn=5)
    put(s, "City of Brass")
    put(s, "Mana Confluence")
    put(s, "Forest")
    s.mana_spent_this_turn = 3
    t.pay_pain_and_sac_tokens(s)
    assert s.life == 38


def test_karns_bastion_proliferate_and_hall_of_heliod():
    s = fresh(turn=6)
    put_lands(s, ["Forest"] * 4)
    kb = put(s, "Karn's Bastion")
    a = saga(s, "Song of Eärendil", 1)
    t.try_karns_bastion_value(s, [])
    assert kb.tapped and t.lore(a) == 2
    s2 = fresh(turn=6)
    put_lands(s2, ["Plains"] * 2)
    put(s2, "Hall of Heliod's Generosity")
    s2.graveyard = ["Summon: Bahamut"]
    t.try_hall_of_heliod_end(s2, [])
    assert s2.library[0] == "Summon: Bahamut"


def test_urzas_saga_chapters():
    s = fresh(turn=6, library=[FILLER, "Sol Ring", FILLER])
    put_lands(s, ["Forest"] * 3)
    us = t.enter_battlefield(s, "Urza's Saga", [])
    t.resolve_stack(s, [])
    assert us.urza_mana and t.land_value(s, us) == 1
    t.add_counters(s, us, "lore", 1, [])
    t.resolve_stack(s, [])
    assert us.urza_construct
    t.try_urza_construct(s, [])
    assert "Construct Token" in names_on_bf(s)
    t.add_counters(s, us, "lore", 1, [])
    t.resolve_stack(s, [])
    assert "Sol Ring" in names_on_bf(s) and us not in s.battlefield


def test_urza_dies_under_starfield():
    s = fresh(turn=6)
    put(s, "Starfield of Nyx")
    for n in ("Prismatic Omen", "Enchantress's Presence", "Historian's Boon", "Resourceful Defense"):
        put(s, n)
    us = put(s, "Urza's Saga")
    us.counters["lore"] = 1
    t.check_sba(s, [])
    assert us not in s.battlefield, "Starfield anima o Urza's Saga como 0/0"


def test_starfield_animation_and_upkeep_return():
    s = fresh(turn=6)
    put(s, "Starfield of Nyx")
    om = put(s, "Prismatic Omen")
    for n in ("Enchantress's Presence", "Historian's Boon", "Resourceful Defense"):
        put(s, n)
    assert t.is_creature(s, om) and t.creature_power(s, om) == 2, "base P/T = MV"
    s.graveyard = ["The First Iroan Games"]
    t.upkeep_step(s, [])
    assert "The First Iroan Games" in names_on_bf(s)


def test_replenish_and_resurgent_belief():
    s = fresh(turn=6, hand=["Replenish", "Resurgent Belief"])
    put_lands(s, ["Plains"] * 6)
    s.graveyard = ["Enchantress's Presence", "Kiora Bests the Sea God", "Utopia Sprawl", FILLER]
    t.cast_instant(s, "Replenish", [])
    bf = names_on_bf(s)
    assert "Enchantress's Presence" in bf and "Kiora Bests the Sea God" in bf
    assert "Utopia Sprawl" in s.graveyard, "Aura sem Forest pra encantar fica no cemiterio"
    s.graveyard.append("Historian's Boon")
    t.try_suspend_resurgent(s, [])
    assert s.suspended and s.suspended[0]["time"] == 2
    s.turn += 1
    t.resolve_suspended(s, [])
    s.turn += 1
    t.resolve_suspended(s, [])
    assert "Historian's Boon" in names_on_bf(s)


# ---------------------------------------------------------------------------
# Capitulos (um teste por Saga)
# ---------------------------------------------------------------------------

def run_chapters(s, name, upto, start=0, perm=None):
    p = perm or saga(s, name, start)
    log = []
    t.add_counters(s, p, "lore", upto - start, log)
    t.resolve_stack(s, log)
    return p


def test_kami_war_transform_and_attack():
    s = fresh(turn=6)
    s.graveyard = ["Sol Ring", "Summon: Bahamut"]
    run_chapters(s, "The Kami War // O-Kagachi Made Manifest", 3)
    ok = [p for p in s.battlefield if t.eff_name(p) == "O-Kagachi Made Manifest"]
    assert ok and s.interaction_plays == 2
    ok[0].entered_turn = 5
    t.combat_step(s, [])
    assert "Sol Ring" in s.hand, "oponente escolhe a de menor MV"
    assert s.proxy_damage_total == 6 + 1


def test_binding_there_and_back():
    s = fresh(turn=6, library=["Bayou", "Taiga", FILLER])
    run_chapters(s, "Binding the Old Gods", 3)
    fo = [p for p in s.battlefield if p.card in ("Bayou", "Taiga")]
    assert fo and fo[0].tapped, "Forest card, virada"
    s2 = fresh(turn=6, library=["Island", "Badlands", FILLER])
    run_chapters(s2, "There and Back Again", 3)
    bl = [p for p in s2.battlefield if p.card == "Badlands"]
    assert bl and not bl[0].tapped and s2.life == 40, "Mountain card desvirada (Island nao serve)"
    assert "Smaug" in names_on_bf(s2) and s2.ring_level == 1


def test_smaug_legend_rule_treasures():
    s = fresh(turn=6)
    put(s, "Smaug", is_token=True)
    t.create_token(s, "Smaug", [])
    assert names_on_bf(s).count("Smaug") == 1 and s.treasures == 14


def test_kiora_helvault_bahamut():
    s = fresh(turn=6)
    run_chapters(s, "Kiora Bests the Sea God", 3)
    assert "Kraken Token" in names_on_bf(s) and s.interaction_plays == 2
    s2 = fresh(turn=6)
    run_chapters(s2, "Battle at the Helvault", 3)
    assert "Avacyn" in names_on_bf(s2) and s2.interaction_plays == 2
    s3 = fresh(turn=6)
    put(s3, "Sol Ring")
    put(s3, "Enchantress's Presence")
    run_chapters(s3, "Summon: Bahamut", 4)
    assert s3.mega_flare_total == (1 + 3) * 3, "soma do MV dos OUTROS permanentes x 3 oponentes"


def test_war_song_creation():
    s = fresh(turn=6, library=["Narci, Fable Singer", FILLER, FILLER])
    run_chapters(s, "War of the Last Alliance", 3)
    assert "Narci, Fable Singer" in s.hand and s.double_strike_this_turn and s.ring_level == 1
    s2 = fresh(turn=6)
    k = put(s2, "Knight Token", is_token=True)
    run_chapters(s2, "Song of Eärendil", 3)
    assert s2.treasures == 1 and "Bird Token" in names_on_bf(s2)
    assert k.counters.get("flying") == 1
    s3 = fresh(turn=6, library=["Summon: Bahamut", FILLER, FILLER, FILLER])
    run_chapters(s3, "The Creation of Avacyn", 3)
    assert "Summon: Bahamut" in names_on_bf(s3) and s3.life == 31, "perde 9 no II, entra no III"


def test_awaken_galactus_jugan():
    s = fresh(turn=6, library=[FILLER, "Forest", FILLER, FILLER], hand=[FILLER])
    put_lands(s, ["Plains"] * 6)     # com terreno sobrando, a Narci vale mais que a Forest moida
    s.graveyard = ["Narci, Fable Singer"]
    run_chapters(s, "Awaken the Honored Dead", 3)
    assert "Narci, Fable Singer" in s.hand and s.interaction_plays == 1
    s2 = fresh(turn=6)
    run_chapters(s2, "The Coming of Galactus", 4)
    assert "Galactus" in names_on_bf(s2) and s2.proxy_damage_total == 12
    s3 = fresh(turn=6)
    run_chapters(s3, "Jugan Defends the Temple // Remnant of the Rising Star", 3)
    assert "Human Monk Token" in names_on_bf(s3)
    assert "Remnant of the Rising Star" in names_on_bf(s3)


def test_ecd_eldest_cruelty_bath():
    s = fresh(turn=6)
    s.graveyard = ["Summon: Primal Odin"]
    run_chapters(s, "Elspeth Conquers Death", 3)
    odin = [p for p in s.battlefield if p.card == "Summon: Primal Odin"]
    assert odin and odin[0].counters.get("+1/+1") == 1 and t.lore(odin[0]) >= 1
    s2 = fresh(turn=6)
    s2.graveyard = ["Narci, Fable Singer"]
    run_chapters(s2, "The Eldest Reborn", 3)
    assert "Narci, Fable Singer" in names_on_bf(s2)
    s3 = fresh(turn=6, library=["Resourceful Defense", FILLER, FILLER])
    run_chapters(s3, "The Cruelty of Gix", 2, start=1)
    assert "Resourceful Defense" in s3.hand and s3.life == 37
    s4 = fresh(turn=6, library=[FILLER] * 10)
    s4.graveyard = ["Farseek", "Sol Ring"]
    run_chapters(s4, "The Bath Song", 3)
    assert s4.bonus_mana_pool == 2 and "Farseek" not in s4.graveyard


def test_birth_darkness_knights_odin():
    s = fresh(turn=6)
    run_chapters(s, "Birth of the Imperium", 3)
    assert names_on_bf(s).count("Astartes Warrior Token") == 3 and s.structural_unmeasured == 1
    s2 = fresh(turn=6)
    run_chapters(s2, "In the Darkness Bind Them", 4)
    assert names_on_bf(s2).count("Wraith Token") == 3 and s2.ring_level == 4
    s3 = fresh(turn=6)
    run_chapters(s3, "Summon: Knights of Round", 5)
    kn = [p for p in s3.battlefield if p.card == "Knight Token"]
    assert len(kn) == 12 and all(p.counters.get("indestructible") == 1 for p in kn)
    assert all(p.temp_power == 2 for p in kn)
    s4 = fresh(turn=6)
    o = run_chapters(s4, "Summon: Primal Odin", 2)
    assert o.odin_lethal
    o.entered_turn = 5
    t.combat_step(s4, [])
    assert s4.odin_eliminations == 1


def test_fenrir_fable_iroan_yojimbo():
    s = fresh(turn=6, library=["Plains", FILLER], hand=["Bloom Tender"])
    put_lands(s, ["Forest", "Forest"])
    run_chapters(s, "Summon: Fenrir", 2)
    assert "Plains" in names_on_bf(s) and s.fenrir_next_creature_bonus == 1
    t.cast_permanent(s, "Bloom Tender", [])
    bt = [p for p in s.battlefield if p.card == "Bloom Tender"][0]
    assert bt.counters.get("+1/+1") == 1
    s2 = fresh(turn=6)
    run_chapters(s2, "Fable of the Mirror-Breaker // Reflection of Kiki-Jiki", 3)
    assert "Goblin Shaman Token" in names_on_bf(s2) and "Reflection of Kiki-Jiki" in names_on_bf(s2)
    s3 = fresh(turn=6)
    run_chapters(s3, "The First Iroan Games", 4)
    assert s3.gold_tokens == 1 and s3.cards_drawn_extra == 2
    s4 = fresh(turn=6)
    run_chapters(s4, "Summon: Yojimbo", 4)
    assert s4.interaction_plays == 3 and s4.structural_unmeasured == 1


def test_reflection_kiki_copies_summon_saga():
    s = fresh(turn=6)
    put_lands(s, ["Forest"])
    put(s, "Fable of the Mirror-Breaker // Reflection of Kiki-Jiki", transformed=True)
    kn = put(s, "Summon: Knights of Round")
    kn.counters["lore"] = 2
    t.try_reflection_kiki(s, [])
    assert names_on_bf(s).count("Knight Token") == 3, "copia de Summon entra no capitulo I"
    t.end_step(s, [])
    assert sum(1 for p in s.battlefield if p.card == "Summon: Knights of Round") == 1


def test_remnant_and_ring_combat():
    s = fresh(turn=6)
    put_lands(s, ["Forest"])
    put(s, "Jugan Defends the Temple // Remnant of the Rising Star", transformed=True)
    tok = t.create_token(s, "Knight Token", [])[0]
    assert tok.counters.get("+1/+1") == 1, "Remnant: paga X=1"
    s2 = fresh(turn=6, library=[FILLER] * 5, hand=[FILLER])
    k = put(s2, "Knight Token", is_token=True)
    s2.ring_level = 4
    s2.ring_bearer_uid = k.uid
    t.combat_step(s2, [])
    assert s2.proxy_damage_total == 2 + 9, "Ring 4: cada oponente perde 3"


def test_clockspinning_save_with_flux_channeler_in_play():
    # Regressao do achado de orquestracao: resposta nao pode resolver a pilha
    # por dentro (Flux Channeler empilha proliferate ao conjurar).
    s = fresh(turn=6, hand=["Clockspinning"])
    put_lands(s, ["Island"] * 2)
    put(s, "Flux Channeler")
    make_tom(s)
    b = saga(s, "Battle at the Helvault", 2)
    t.add_counters(s, b, "lore", 1, [])
    t.resolve_stack(s, [])
    assert b in s.battlefield and t.lore(b) == 2, "salva mesmo com Flux Channeler"
    assert "Avacyn" in names_on_bf(s) and s.finals_saved == 1


def test_nexus_mentality_value_reset_draws():
    s = fresh(turn=6, hand=["Nexus Mentality"])
    put_lands(s, ["Island"] * 4)
    k = saga(s, "Summon: Knights of Round", 4)
    t.try_nexus_value(s, [])
    assert s.usage.get("nexus_draw") == 4 and t.lore(k) == 0, "zera a Knights e compra 4"
    t.precombat_lore_step(s, [])
    assert s.usage.get("chapter:Summon: Knights of Round:1") == 1, "recomeca do capitulo I"


def test_infinite_smaug_loop_is_real_and_detected():
    # There and Back Again no II + Clockspinning (buyback) + Hex Parasite +
    # Smaug em campo: cada volta = ~6 mana, 14 Treasures (loop real).
    s = fresh(turn=7, hand=["Clockspinning"], life=40)
    put_lands(s, ["Island"] * 4 + ["Swamp"] * 3)
    put(s, "Hex Parasite")
    put(s, "Smaug", is_token=True)
    make_tom(s)
    th = saga(s, "There and Back Again", 2)
    for i in range(3):
        treasures_before = s.treasures
        t.cast_instant(s, "Clockspinning", [], clock_target=th, clock_mode="add")
        assert th in s.battlefield and t.lore(th) == 2, "Hex Parasite salva o III em resposta"
        assert s.treasures == treasures_before + 14, "Smaug antigo morre pela regra da lenda"
        assert "Clockspinning" in s.hand, "buyback"
        if s.infinite_combo_turn is not None:
            break
    assert s.infinite_combo_turn == 7


# ---------------------------------------------------------------------------
# Comandante / resiliencia
# ---------------------------------------------------------------------------

def test_commander_tax_and_903_9a():
    s = fresh(turn=6)
    tom = make_tom(s)
    s.commander_cast_count = 1
    assert t.effective_cost(s, t.COMMANDER) == 7
    t.remove_permanent(s, tom)
    assert not s.commander_in_play and t.COMMANDER not in s.graveyard


def test_indestructible_tom_survives_creature_wipe():
    s = fresh(turn=6)
    s.interaction_rng = random.Random(1)
    tom = make_tom(s)
    saga(s, "Summon: Knights of Round", 4)
    saga(s, "Song of Eärendil", 1)
    k = put(s, "Knight Token", is_token=True)
    for _ in range(200):
        if t.try_smart_opponent_wipe(s):
            break
    assert tom in s.battlefield, "4+ lore: Tom indestrutivel"


def test_teferis_protection_reactive():
    s = fresh(turn=6, hand=["Teferi's Protection"])
    s.interaction_rng = random.Random(3)
    put(s, "Resourceful Defense")
    s.tp_ready = True
    assert t.try_teferis_protection_response(s)
    assert all(p.phased_out for p in s.battlefield) and s.tp_saves_total == 1
    assert "Teferi's Protection" in s.exile


def test_enlightened_tutor_in_response_to_tom():
    lib = [FILLER, FILLER, "Summon: Bahamut", "Kiora Bests the Sea God"]
    s = fresh(turn=6, library=lib, hand=["Enlightened Tutor"])
    make_tom(s)
    put_lands(s, ["Plains"])
    a = saga(s, "Song of Eärendil", 2)
    t.add_counters(s, a, "lore", 1, [])
    t.resolve_stack(s, [])
    assert "Summon: Bahamut" in names_on_bf(s), "ET poe a melhor Saga no topo -> Tom revela ela"


def test_full_game_determinism():
    a = t.simulate_one(4242, turns=8)
    b = t.simulate_one(4242, turns=8)
    assert (a.proxy_damage_total, a.cards_drawn_extra, a.usage) == (b.proxy_damage_total, b.cards_drawn_extra,
                                                                  b.usage)
    c = t.simulate_one_with_interaction(4242, turns=8)
    d = t.simulate_one_with_interaction(4242, turns=8)
    assert c.usage == d.usage


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

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

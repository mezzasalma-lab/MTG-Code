"""
Testes dirigidos do modelo de combate do simulador da Prismatic Bridge
(CLAUDE.md, Regra #1: cada clausula implementada tem que DISPARAR de
verdade, nao so' existir). Cada teste monta um estado minimo e chama a
funcao real do simulador.

Rodar: python3 test_prismatic_bridge_goldfish.py   (sem pytest -- executor proprio no fim)
"""
import random
import traceback

import prismatic_bridge_goldfish_v1 as pb

FILLER = "Snow-Covered Forest"


def fresh(turn: int = 5, library=None, hand=None, life: int = 40, profile: str = "mixed") -> pb.GameState:
    s = pb.GameState(rng=random.Random(0), library=list(library) if library is not None else [FILLER] * 30,
                     interaction_rng=random.Random(1))
    s.turn = turn
    s.life = life
    s.hand = list(hand or [])
    s.attack_profile = profile
    s.opp_archetypes = ["go_wide", "voltron", "low"]
    s.opp_boards = [[], [], []]
    s.opp_cmd_cooldown = [0, 0, 0]
    s.opp_cmd_bonus = [0, 0, 0]
    return s


def opp(p, t=None, **kw) -> dict:
    """Criatura de oponente ja' pronta pra atacar (sem doenca)."""
    c = pb._new_opp_creature(p, p if t is None else t, flying=kw.pop("flying", False),
                             haste=True, **kw)
    return c


def creature(s: pb.GameState, name: str, cast_turn: int = 1):
    s.battlefield.append(name)
    s.creature_cast_turn[name] = cast_turn


def token(s: pb.GameState, name: str, n: int = 1, old: bool = True):
    pb.make_pw_token(s, name, n, [])
    if old:
        s.new_tokens_this_turn = {}


def pw(s: pb.GameState, name: str, loyalty: int, entered: int = 1):
    s.battlefield.append(name)
    s.loyalty[name] = loyalty
    s.pw_enter_turn[name] = entered


# ---------------------------------------------------------------------------
# Pillowfort
# ---------------------------------------------------------------------------

def test_silent_arbiter_only_one_attacker():
    s = fresh()
    creature(s, "Silent Arbiter")
    s.opp_boards[0] = [opp(2), opp(3), opp(1)]
    pb.opponent_combat(s, 0, [])
    assert s.opp_attackers_total == 1, s.opp_attackers_total
    assert s.attackers_limited_total == 2
    assert s.life == 37  # so' o 3/3 ataca; Arbiter 1/5 nao chumpa na vida alta


def test_dueling_grounds_only_one_attacker_and_one_blocker():
    s = fresh()
    s.battlefield.append("Dueling Grounds")
    pw(s, "Kaya, Intangible Slayer", 2)
    token(s, "Soldier Token", 3)
    s.opp_boards[0] = [opp(2), opp(2)]
    pb.opponent_combat(s, 0, [])
    assert s.opp_attackers_total == 1 and s.attackers_limited_total == 1
    assert s.blocks_total <= 1


def test_sphere_of_safety_tax_per_enchantment():
    s = fresh(turn=6)  # orcamento do oponente = int(0.5 * 6) = 3
    s.battlefield += ["Sphere of Safety", "Doubling Season", "Rhystic Study"]  # X = 3
    s.opp_boards[0] = [opp(2), opp(2), opp(2)]
    pb.opponent_combat(s, 0, [])
    assert s.opp_attackers_total == 1, s.opp_attackers_total
    assert s.attackers_stopped_by_tax_total == 2
    assert s.life == 38


def test_ghostly_prison_redirects_unpaid_face_attacker_to_planeswalker():
    s = fresh(turn=4)  # orcamento 2 -> paga so' 1 atacante na vida
    s.battlefield.append("Ghostly Prison")
    pw(s, "Kaya, Intangible Slayer", 2)
    s.opp_boards[0] = [opp(2), opp(2), opp(2)]
    pb.opponent_combat(s, 0, [])
    assert s.attackers_redirected_to_pw_total == 1
    assert "Kaya, Intangible Slayer" not in s.loyalty  # 2 atacantes nela (1 original + 1 redirecionado)
    assert s.pw_combat_deaths_total == 1
    assert s.life == 38


def test_eternal_wanderer_static_only_one_attacker_at_it():
    s = fresh()
    pw(s, "The Eternal Wanderer", 5)
    s.opp_boards[0] = [opp(3), opp(3)]
    pb.opponent_combat(s, 0, [])
    assert s.loyalty["The Eternal Wanderer"] == 2
    assert s.life == 37


# ---------------------------------------------------------------------------
# Combate: bloqueio, palavras-chave
# ---------------------------------------------------------------------------

def test_chump_block_triggers_liliana_static_draw():
    s = fresh()
    pw(s, "Liliana, Dreadhorde General", 6)
    token(s, "Zombie Token", 1)
    s.opp_boards[0] = [opp(4)]
    hand0 = len(s.hand)
    pb.opponent_combat(s, 0, [])
    assert s.loyalty["Liliana, Dreadhorde General"] == 6
    assert s.liliana_static_draws_total == 1 and len(s.hand) == hand0 + 1
    assert "Zombie Token" not in s.battlefield


def test_trample_excess_hits_planeswalker():
    s = fresh()
    pw(s, "Kaya, Intangible Slayer", 10)
    token(s, "Soldier Token", 1)
    s.opp_boards[0] = [opp(6, trample=True)]
    pb.opponent_combat(s, 0, [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 5, s.loyalty


def test_atraxa_deathtouch_lifelink_trade_saves_planeswalker():
    s = fresh()
    pw(s, "Kaya, Intangible Slayer", 4)
    creature(s, "Atraxa, Praetors' Voice")
    s.opp_boards[0] = [opp(5)]
    pb.opponent_combat(s, 0, [])
    assert s.opp_boards[0] == []
    assert s.loyalty["Kaya, Intangible Slayer"] == 4
    assert "Atraxa, Praetors' Voice" in s.graveyard
    assert s.life == 44  # lifelink: 4 de dano causado


def test_double_strike_blocker_kills_first():
    s = fresh()
    pw(s, "Kaya, Intangible Slayer", 5)
    token(s, "Samurai Token", 1)
    s.opp_boards[0] = [opp(2)]
    pb.opponent_combat(s, 0, [])
    assert s.opp_boards[0] == [] and "Samurai Token" in s.battlefield
    assert s.our_blockers_lost_total == 0


def test_flying_attacker_needs_flying_blocker_elspeth_emblem():
    s = fresh()
    pw(s, "Kaya, Intangible Slayer", 2)
    token(s, "Soldier Token", 1)
    s.opp_boards[0] = [opp(2, flying=True)]
    pb.opponent_combat(s, 0, [])
    assert "Kaya, Intangible Slayer" not in s.loyalty  # soldado 1/1 nao voa
    s = fresh()
    pw(s, "Kaya, Intangible Slayer", 2)
    token(s, "Soldier Token", 1)
    s.elspeth_emblem = True  # +2/+2 e voar
    s.opp_boards[0] = [opp(2, flying=True)]
    pb.opponent_combat(s, 0, [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 2 and s.opp_boards[0] == []


def test_attacked_creatures_stay_tapped_and_cannot_block():
    s = fresh()
    token(s, "Elk Token", 1)
    pb.our_combat_step(s, [])
    assert s.our_combat_damage_proxy_total == 3 and len(s.our_tapped) == 1
    pw(s, "Kaya, Intangible Slayer", 3)
    s.opp_boards[0] = [opp(3)]
    pb.opponent_combat(s, 0, [])
    assert s.blocks_total == 0 and "Kaya, Intangible Slayer" not in s.loyalty


def test_new_tokens_are_summoning_sick():
    s = fresh()
    token(s, "Soldier Token", 3, old=False)
    pb.our_combat_step(s, [])
    assert s.our_combat_damage_proxy_total == 0


def test_frozen_creature_skips_next_attack():
    s = fresh()
    s.opp_boards[0] = [opp(5)]
    pb._freeze_biggest_threats(s, 1, [], source="test")
    s.interaction_rng = random.Random(99)
    s.opp_archetypes[0] = "low"
    s.turn = 1  # sem crescimento de campo no "low" antes do T3
    pb._opp_turn_start(s, 0)
    s.turn = 5
    pb.opponent_combat(s, 0, [])
    assert s.opp_attackers_total == 0
    s.turn = 1
    pb._opp_turn_start(s, 0)
    s.turn = 5
    pb.opponent_combat(s, 0, [])
    assert s.opp_attackers_total == 1


# ---------------------------------------------------------------------------
# Gatilhos de criatura / contadores
# ---------------------------------------------------------------------------

def test_arena_rector_death_puts_planeswalker_onto_battlefield():
    s = fresh(library=[FILLER] * 5 + ["Ugin, the Spirit Dragon"] + [FILLER] * 5)
    creature(s, "Arena Rector")
    pb.remove_permanent(s, "Arena Rector", [], source="test")
    assert s.loyalty.get("Ugin, the Spirit Dragon") == 7
    assert "Arena Rector" not in s.graveyard  # "you may exile it"
    assert s.arena_rector_triggers_total == 1


def test_innkeeper_level1_counter_and_doubling():
    s = fresh()
    s.battlefield.append("Innkeeper's Talent")
    creature(s, "Carth the Lion")
    pb.our_combat_step(s, [])
    assert s.creature_counters["Carth the Lion"] == 1
    s = fresh()
    s.battlefield += ["Innkeeper's Talent", "Doubling Season"]
    creature(s, "Carth the Lion")
    pb.our_combat_step(s, [])
    assert s.creature_counters["Carth the Lion"] == 2


def test_proliferate_and_deepglow_reach_creature_counters():
    s = fresh()
    creature(s, "Carth the Lion")
    s.creature_counters["Carth the Lion"] = 1
    pb.proliferate_loyalty(s, [], source="test")
    assert s.creature_counters["Carth the Lion"] == 2
    pb._double_creature_counters(s)
    assert s.creature_counters["Carth the Lion"] == 4


def test_oko_copies_creature_at_beginning_of_combat():
    s = fresh()
    pw(s, "Oko, the Ringleader", 3, entered=3)
    token(s, "Elk Token", 1)
    pb.our_combat_step(s, [])
    assert s.oko_combat_copies_total == 1 and s.our_combat_damage_proxy_total == 6
    s = fresh()
    pw(s, "Oko, the Ringleader", 3, entered=5)  # entrou neste turno: copia, mas nao ataca
    token(s, "Elk Token", 1)
    pb.our_combat_step(s, [])
    assert s.oko_combat_copies_total == 1 and s.our_combat_damage_proxy_total == 3


def test_oko_never_copies_legendary():
    s = fresh()
    pw(s, "Oko, the Ringleader", 3, entered=1)
    creature(s, "Atraxa, Praetors' Voice")
    pb.our_combat_step(s, [])
    assert s.oko_combat_copies_total == 0


def test_artifact_wipe_hits_peregrine_dynamo():
    class AlwaysArtifact:
        def random(self):
            return 0.0

        def choices(self, pop, weights):
            return ["artifact"]
    s = fresh()
    pw(s, "Liliana, Dreadhorde General", 6)
    creature(s, "The Peregrine Dynamo")
    s.interaction_rng = AlwaysArtifact()
    pb.try_smart_opponent_wipe(s, [])
    assert "The Peregrine Dynamo" not in s.battlefield and "The Peregrine Dynamo" in s.graveyard
    assert s.liliana_static_draws_total == 1


# ---------------------------------------------------------------------------
# Planeswalkers: modos de remocao/controle com alvo real
# ---------------------------------------------------------------------------

def test_kaya_minus3_exiles_and_makes_spirit():
    s = fresh()
    pw(s, "Kaya, Intangible Slayer", 6)
    s.opp_boards[1] = [opp(4)]
    pb.resolve_planeswalker(s, "Kaya, Intangible Slayer", [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 3
    assert s.opp_boards[1] == [] and "Spirit Token" in s.battlefield


def test_bolas_minus3_destroys():
    s = fresh()
    pw(s, "Nicol Bolas, Dragon-God", 4)
    s.opp_boards[0] = [opp(3)]
    pb.resolve_planeswalker(s, "Nicol Bolas, Dragon-God", [])
    assert s.loyalty["Nicol Bolas, Dragon-God"] == 1 and s.opp_boards[0] == []


def test_vraska_minus2_commander_cooldown():
    s = fresh()
    pw(s, "Vraska, Betrayal's Sting", 3)
    s.opp_boards[1] = [opp(6, cmd=True, trample=True)]
    pb.resolve_planeswalker(s, "Vraska, Betrayal's Sting", [])
    assert s.loyalty["Vraska, Betrayal's Sting"] == 1
    assert s.opp_boards[1] == [] and s.opp_cmd_cooldown[1] == 2 and s.opp_cmd_bonus[1] == 1


def test_teferi_raveler_minus3_bounces_token():
    s = fresh()
    pw(s, "Teferi, Time Raveler", 3)
    s.opp_boards[0] = [opp(2, token=True)]
    pb.resolve_planeswalker(s, "Teferi, Time Raveler", [])
    assert s.opp_boards[0] == []


def test_tamiyo_sage_plus1_freezes():
    s = fresh()
    pw(s, "Tamiyo, Compleated Sage", 5)
    s.opp_boards[0] = [opp(4)]
    pb.resolve_planeswalker(s, "Tamiyo, Compleated Sage", [])
    assert s.opp_boards[0][0]["frozen"] == 1


def test_tamiyo_researcher_minus2_freezes_two():
    s = fresh()
    pw(s, "Tamiyo, Field Researcher", 3)
    s.opp_boards[0] = [opp(3), opp(4)]
    pb.resolve_planeswalker(s, "Tamiyo, Field Researcher", [])
    assert s.loyalty["Tamiyo, Field Researcher"] == 1
    assert all(c["frozen"] == 1 for c in s.opp_boards[0])


def test_tamiyo_researcher_plus1_draws_on_combat_damage():
    s = fresh()
    pw(s, "Tamiyo, Field Researcher", 4)
    token(s, "Elk Token", 1)
    pb.resolve_planeswalker(s, "Tamiyo, Field Researcher", [])
    assert s.loyalty["Tamiyo, Field Researcher"] == 5 and s.tamiyo_fr_marked
    hand0 = len(s.hand)
    pb.our_combat_step(s, [])
    assert s.tamiyo_fr_combat_draws_total == 1 and len(s.hand) == hand0 + 1


def test_liliana_minus4_and_ultimate():
    s = fresh()
    pw(s, "Liliana, Dreadhorde General", 5)
    s.opp_boards[0] = [opp(1), opp(1), opp(5)]
    s.opp_boards[2] = [opp(3)]
    pb.resolve_planeswalker(s, "Liliana, Dreadhorde General", [])
    assert s.loyalty["Liliana, Dreadhorde General"] == 1
    assert [c["p"] for c in s.opp_boards[0]] == [5] and s.opp_boards[2] == []
    s = fresh()
    pw(s, "Liliana, Dreadhorde General", 9)
    s.opp_boards[0] = [opp(5), opp(1)]
    s.opp_boards[1] = [opp(2)]
    pb.resolve_planeswalker(s, "Liliana, Dreadhorde General", [])
    assert [c["p"] for c in s.opp_boards[0]] == [5] and len(s.opp_boards[1]) == 1


def test_eternal_wanderer_minus4_each_player_keeps_one():
    s = fresh()
    pw(s, "The Eternal Wanderer", 5)
    s.opp_boards[0] = [opp(1), opp(2), opp(3)]
    s.opp_boards[1] = [opp(4), opp(5)]
    token(s, "Soldier Token", 1)
    token(s, "Elk Token", 1)
    pb.resolve_planeswalker(s, "The Eternal Wanderer", [])
    assert s.loyalty["The Eternal Wanderer"] == 1
    assert [c["p"] for c in s.opp_boards[0]] == [1] and [c["p"] for c in s.opp_boards[1]] == [4]
    assert "Elk Token" in s.battlefield and "Soldier Token" not in s.battlefield


def test_elspeth_minus3_power_four_or_greater():
    s = fresh()
    pw(s, "Elspeth, Sun's Champion", 4)
    s.opp_boards[0] = [opp(4), opp(5), opp(2)]
    pb.resolve_planeswalker(s, "Elspeth, Sun's Champion", [])
    assert s.loyalty["Elspeth, Sun's Champion"] == 1
    assert [c["p"] for c in s.opp_boards[0]] == [2]


def test_ugin_minus_zero_exiles_all_tokens():
    s = fresh()
    pw(s, "Ugin, the Spirit Dragon", 7)
    s.opp_boards[0] = [opp(1, token=True) for _ in range(10)]
    token(s, "Soldier Token", 1)
    pb.resolve_planeswalker(s, "Ugin, the Spirit Dragon", [])
    assert s.ugin_minus_x_total == 1 and s.loyalty["Ugin, the Spirit Dragon"] == 7
    assert s.opp_boards[0] == [] and "Soldier Token" not in s.battlefield


def test_ugin_plus2_pings_small_threat():
    s = fresh()
    pw(s, "Ugin, the Spirit Dragon", 7)
    s.opp_boards[0] = [opp(3)]
    pb.resolve_planeswalker(s, "Ugin, the Spirit Dragon", [])
    assert s.loyalty["Ugin, the Spirit Dragon"] == 9 and s.opp_boards[0] == []


def test_teferi_hero_emblem_exiles_on_draw():
    s = fresh()
    s.teferi_hero_emblem = True
    s.opp_boards[2] = [opp(7)]
    s.draw(1)
    assert s.opp_boards[2] == [] and s.teferi_emblem_exiles_total == 1


# ---------------------------------------------------------------------------
# Nossas magicas de remocao com efeito real
# ---------------------------------------------------------------------------

def test_toxic_deluge_pays_life_and_wipes():
    s = fresh(hand=["Toxic Deluge"])
    s.battlefield += ["Snow-Covered Swamp", "Bayou", "Underground Sea"]
    s.opp_boards[0] = [opp(3), opp(3), opp(3)]
    pb._cast_defensive_spells(s, [], 0)
    assert s.opp_boards[0] == [] and s.life == 37 and s.our_wipes_cast_total == 1
    assert "Toxic Deluge" in s.graveyard


def test_swords_on_big_threat():
    s = fresh(hand=["Swords to Plowshares"])
    s.battlefield += ["Snow-Covered Plains"]
    s.opp_boards[0] = [opp(5)]
    pb._cast_defensive_spells(s, [], 0)
    assert s.opp_boards[0] == [] and s.our_spot_removal_cast_total == 1


def test_damn_needs_two_black_sources():
    s = fresh(hand=["Damn"])
    s.battlefield += ["Snow-Covered Swamp", "Snow-Covered Forest"]
    s.opp_boards[0] = [opp(5)]
    pb._cast_defensive_spells(s, [], 0)
    assert s.opp_boards[0] != [] and "Damn" in s.hand
    s.battlefield.append("Bayou")
    pb._cast_defensive_spells(s, [], 0)
    assert s.opp_boards[0] == [] and "Damn" not in s.hand


def test_removal_is_held_without_threat():
    assert pb._held_for_threat("Swords to Plowshares") and pb._held_for_threat("Toxic Deluge")
    assert not pb._held_for_threat("Nicol Bolas, Dragon-God")


# ---------------------------------------------------------------------------
# Bugs pre-existentes corrigidos na mesma rodada (valem no modo padrao tambem)
# ---------------------------------------------------------------------------

def std_state(turn=5, library=None):
    s = pb.GameState(rng=random.Random(0), library=list(library) if library is not None else [FILLER] * 30)
    s.turn = turn
    return s


def test_bridge_hit_creature_is_summoning_sick_and_fires_etb():
    s = std_state(library=["Bloom Tender"] + [FILLER] * 10)
    s.battlefield.append("Snow-Covered Forest")
    pb.bridge_upkeep_trigger(s, [])
    assert s.creature_cast_turn["Bloom Tender"] == 5
    assert pb.total_mana(s) == 1  # dork nao gera mana no turno em que a Bridge o poe em campo
    s = std_state(library=["Deepglow Skate"] + [FILLER] * 10)
    pw(s, "Kaya, Intangible Slayer", 6)
    pb.bridge_upkeep_trigger(s, [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 12  # ETB da Deepglow vindo da Bridge
    s = std_state(library=["Carth the Lion"] + [FILLER] * 3 + ["Ugin, the Spirit Dragon"] + [FILLER] * 10)
    pb.bridge_upkeep_trigger(s, [])
    assert "Ugin, the Spirit Dragon" in s.hand and s.carth_tutors_total == 1


def test_sphinx_additional_beginning_phase_full_turn():
    """Regra #6: roda play_turn inteiro, nao so' a funcao isolada."""
    lib = [FILLER, "Tamiyo, Field Researcher"] + [FILLER] * 30
    s = std_state(turn=0, library=lib)
    s.battlefield += ["Sphinx of the Second Sun", pb.COMMANDER, "Snow-Covered Forest", "Snow-Covered Island"]
    s.creature_cast_turn["Sphinx of the Second Sun"] = 0
    s.bridge_in_play = True
    s.hand = []
    pb.play_turn(s, 1, [])
    # upkeep normal: Bridge revela o FILLER (terreno, vai pro fundo) e acha a
    # Tamiyo; fase adicional: 2o gatilho da Bridge + 1 compra extra.
    assert s.sphinx_extra_beginning_phases_total == 1
    assert s.bridge_triggers == 2
    assert s.mana_held_back == pb.total_mana(s)  # untap: toda a mana volta (so' instantaneo)
    assert "Sphinx of the Second Sun" in s.battlefield  # nao existe sacrificio
    assert s.extra_turns_pending == 0  # nao existe turno extra


def test_sphinx_extra_upkeep_not_doubled_by_paradox_haze():
    s = std_state(library=[FILLER] * 30)
    s.battlefield += ["Paradox Haze", pb.COMMANDER]
    s.bridge_in_play = True
    pb.sphinx_additional_beginning_phase(s, [])
    assert s.bridge_triggers == 1


def test_atraxa_end_step_proliferate():
    s = std_state(turn=0, library=[FILLER] * 30)
    s.battlefield += ["Atraxa, Praetors' Voice"]
    s.creature_cast_turn["Atraxa, Praetors' Voice"] = 0
    pw(s, "Teferi, Hero of Dominaria", 4)
    pb.play_turn(s, 1, [])
    # +1 do Teferi (5) e depois proliferate no end step (6)
    assert s.loyalty["Teferi, Hero of Dominaria"] == 6, s.loyalty


def test_doubling_season_doubles_tokens_and_copies_stack():
    s = std_state()
    s.battlefield.append("Doubling Season")
    pb.make_pw_token(s, "Soldier Token", 3, [])
    assert s.battlefield.count("Soldier Token") == 6 and s.pw_tokens_created_total == 6
    s.battlefield.append("Doubling Season")  # ficha copia via Tamiyo, Compleated Sage
    assert pb.counter_doubler_multiplier(s) == 4
    pb.make_pw_token(s, "Zombie Token", 1, [])
    assert s.battlefield.count("Zombie Token") == 4


def test_vorinclex_does_not_double_tokens():
    s = std_state()
    s.battlefield.append("Vorinclex, Monstrous Raider")
    pb.make_pw_token(s, "Elk Token", 1, [])
    assert s.battlefield.count("Elk Token") == 1


def test_oath_of_teferi_and_urza_iii_do_not_stack_but_chain_veil_does():
    s = std_state()
    s.battlefield.append("Oath of Teferi")
    s.urza_chapter_iii_this_turn = True
    assert pb.extra_pw_activation_sources(s) == 1
    s.chain_veil_activated_this_turn = True
    assert pb.extra_pw_activation_sources(s) == 2


def test_urza_lore_counters_doubled_with_read_ahead():
    # sem dobrador: entra com 1 -> capitulo I
    s = std_state(library=["Kaya, Intangible Slayer"] + [FILLER] * 10)
    s.battlefield.append("Urza Assembles the Titans")
    pb.try_urza_saga_tick(s, [])
    assert s.urza_chapter == 1 and "Kaya, Intangible Slayer" in s.hand
    # com Doubling Season: entra com 2 -> Read ahead so' deixa o II disparar
    s = std_state(library=["Kaya, Intangible Slayer"] + [FILLER] * 10)
    s.battlefield += ["Urza Assembles the Titans", "Doubling Season"]
    s.hand = ["Liliana, Dreadhorde General"]
    pb.try_urza_saga_tick(s, [])
    assert s.urza_chapter == 2 and "Kaya, Intangible Slayer" not in s.hand
    assert s.loyalty.get("Liliana, Dreadhorde General") == 12  # cap. II + Doubling Season
    # proximo turno: +2 -> passa do III (dispara) e sacrifica
    s.turn += 1
    pb.try_urza_saga_tick(s, [])
    assert s.urza_chapter_iii_this_turn and "Urza Assembles the Titans" in s.graveyard


def test_all_will_be_one_triggers_on_each_counter_placement():
    s = std_state()
    s.battlefield.append("All Will Be One")
    pw(s, "Kaya, Intangible Slayer", 6)
    pw(s, "Teferi, Hero of Dominaria", 4)
    pb.proliferate_loyalty(s, [], source="test")  # 2 permanentes -> 2 gatilhos de 1
    assert s.all_will_be_one_triggers_total == 2 and s.all_will_be_one_face_damage_total == 2
    s.battlefield.append("Doubling Season")
    pb.planeswalker_enters(s, "Ugin, the Spirit Dragon", [])  # entra com 14 -> 14 de dano
    assert s.all_will_be_one_triggers_total == 3 and s.all_will_be_one_face_damage_total == 16


def test_all_will_be_one_kills_biggest_killable_creature_in_combat_model():
    s = fresh()
    s.battlefield.append("All Will Be One")
    pw(s, "Kaya, Intangible Slayer", 6)
    s.opp_boards[0] = [opp(2), opp(5)]
    s.opp_boards[1] = [opp(9)]
    pb.add_loyalty(s, "Kaya, Intangible Slayer", 2, [], reason="test")  # +2 -> 2 de dano
    assert [c["p"] for c in s.opp_boards[0]] == [5] and s.all_will_be_one_kills_total == 1
    s.battlefield.append("Doubling Season")
    pb.add_loyalty(s, "Kaya, Intangible Slayer", 3, [], reason="test")  # +6 -> mata a 5/5
    assert s.opp_boards[0] == [] and len(s.opp_boards[1]) == 1


def test_real_life_gain_and_chain_veil_loss():
    s = std_state(turn=0, library=[FILLER] * 30)
    s.life = 40
    s.battlefield.append("The Chain Veil")
    pb.play_turn(s, 1, [])  # nenhum PW ativado -> perde 2
    assert s.life == 38 and s.chain_veil_life_lost_total == 2
    pw(s, "Kaya, Intangible Slayer", 6)
    pb.play_turn(s, 2, [])  # Kaya +2: ganha 3; ativou -> Chain Veil nao dispara
    assert s.life == 41, s.life


def test_died_turn_marked_when_life_hits_zero():
    s = fresh(life=3)
    s.opp_boards[0] = [opp(5)]
    pb.opponent_combat(s, 0, [])
    assert s.life == -2 and s.died_turn == 5


def test_damn_color_is_black_only():
    assert pb.C("Damn").colors == {"B"}


# ---------------------------------------------------------------------------
# Runner de A/B e isolamento do modo padrao
# ---------------------------------------------------------------------------

def test_swap_replaces_card_only_in_that_simulation():
    s = pb.simulate_one_with_interaction(123, turns=0, swap=("Oath of Nissa", "Silent Arbiter"))
    cards = s.library + s.hand
    assert len(cards) == 99 and "Silent Arbiter" in cards and "Oath of Nissa" not in cards
    assert "1 Oath of Nissa\n" in pb.DECKLIST_TEXT
    try:
        pb.simulate_one_with_interaction(1, turns=0, swap=("Carta Inexistente", "Silent Arbiter"))
        raise RuntimeError("deveria ter falhado")
    except AssertionError:
        pass


def test_profiles_run_without_exceptions():
    for prof in pb.ATTACK_PROFILES + (None,):
        for seed in range(20):
            pb.simulate_one_with_interaction(7000000 + seed, turns=10, attack_profile=prof)


def test_standard_mode_has_no_combat_state():
    r = pb.simulate_one(5, 10, False)
    assert "opp_boards" not in r


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

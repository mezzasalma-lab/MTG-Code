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
    pb.beginning_of_combat(s, [])
    assert s.creature_counters["Carth the Lion"] == 1
    s = fresh()
    s.battlefield += ["Innkeeper's Talent", "Doubling Season"]
    creature(s, "Carth the Lion")
    pb.beginning_of_combat(s, [])
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
    pw(s, "Kaya, Intangible Slayer", 5)  # < 6: a politica usa +2 (com 6+ e mao curta ela compra 2 com o 0)
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
# Rodada de gaps (2026-09-24): auditoria completa das 100 cartas
# ---------------------------------------------------------------------------

LANDS3 = ["Snow-Covered Forest", "Snow-Covered Island", "Snow-Covered Plains"]


def test_lands_in_hand_are_not_cast_as_spells():
    s = std_state(turn=3, library=[FILLER] * 30)
    s.battlefield += LANDS3
    s.hand = ["Bayou", "Taiga", "Savannah"]
    s.land_played = True
    pb.main_phase(s, [])
    assert sum(1 for c in s.battlefield if pb.is_land(c)) == 3 and len(s.hand) == 3


def test_planeswalker_cast_from_hand_gets_loyalty():
    s = std_state(turn=5)
    s.battlefield += LANDS3 + ["Snow-Covered Swamp", "Tundra"]
    s.hand = ["Teferi, Hero of Dominaria"]
    s.land_played = True
    pb.main_phase(s, [])
    # Entra com 4 e (CORRIGIDO 2026-09-25, CR 606.3) ja' ativa o +1 no mesmo
    # main phase -- antes so' ativava no turno seguinte.
    assert s.loyalty.get("Teferi, Hero of Dominaria") == 5
    assert "Teferi, Hero of Dominaria" in s.pw_activated_this_turn


def test_doubling_season_does_not_double_loyalty_cost_but_vorinclex_does():
    s = std_state()
    s.battlefield.append("Doubling Season")
    pw(s, "Kaya, Intangible Slayer", 5)
    pb.resolve_planeswalker(s, "Kaya, Intangible Slayer", [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 7  # +2 de custo nao e' dobrado (ruling)
    s = std_state()
    s.battlefield.append("Vorinclex, Monstrous Raider")
    pw(s, "Kaya, Intangible Slayer", 5)
    pb.resolve_planeswalker(s, "Kaya, Intangible Slayer", [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 9  # Vorinclex: "If you would put" -> dobra


def test_carth_adds_plus_one_loyalty_to_costs():
    s = std_state()
    s.battlefield.append("Carth the Lion")
    pw(s, "Kaya, Intangible Slayer", 4)
    pb.resolve_planeswalker(s, "Kaya, Intangible Slayer", [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 7  # [+2] vira [+3]
    s = std_state()
    s.battlefield.append("Carth the Lion")
    pw(s, "Elspeth, Sun's Champion", 6)  # [-7] vira [-6]: da' pra ultar com 6
    pb.resolve_planeswalker(s, "Elspeth, Sun's Champion", [])
    assert s.elspeth_emblem == 1 and "Elspeth, Sun's Champion" not in s.loyalty


def test_mulligan_bottom_is_not_shuffled():
    orig = pb.should_keep
    calls = {"n": 0}

    def keep_third(hand):
        calls["n"] += 1
        return calls["n"] >= 3
    pb.should_keep = keep_third
    try:
        s = pb.simulate_one_with_interaction(42, turns=0, attack_profile=None)
    finally:
        pb.should_keep = orig
    assert len(s.hand) == 6  # 2 mulligans, o 1o e' gratis -> 1 carta pro fundo
    bottomed = s.library[-1]
    assert bottomed not in s.hand


def test_halfling_and_plaza_colored_mana_for_legendary():
    s = std_state()
    s.battlefield += ["Delighted Halfling"]
    s.creature_cast_turn["Delighted Halfling"] = 1
    assert pb.color_sources(s, "B", legendary_spell=True) == 1
    assert pb.color_sources(s, "B", legendary_spell=False) == 0
    s = std_state()
    s.battlefield += ["Plaza of Heroes", pb.COMMANDER]
    assert pb.color_sources(s, "R") >= 1  # "any color among legendary permanents": a Bridge e' 5 cores


def test_oath_of_nissa_static_and_etb():
    s = std_state()
    s.battlefield += ["Oath of Nissa", "Snow-Covered Forest"]
    assert pb.color_sources(s, "B", pw_spell=True) >= 1
    s = std_state(library=[FILLER, "Ugin, the Spirit Dragon", "Swords to Plowshares"] + [FILLER] * 5)
    s.battlefield.append("Oath of Nissa")
    pb.noncreature_etb(s, "Oath of Nissa", [])
    assert "Ugin, the Spirit Dragon" in s.hand


def test_bloom_tender_ignores_land_colors():
    s = std_state()
    s.battlefield += ["Bloom Tender", "Bayou", "Taiga"]
    s.creature_cast_turn["Bloom Tender"] = 1
    assert pb.total_mana(s) == 2 + 1  # 2 terrenos + Bloom Tender (so' ela mesma e' verde)


def test_shockland_and_painlands_and_world_tree():
    s = std_state(turn=3)
    s.battlefield += ["Snow-Covered Forest", "Snow-Covered Island"]
    s.hand = ["Breeding Pool", "Evolution Sage"]  # 3 mana: so' com a shock desvirada
    pb.play_land(s, [])
    assert s.life == 38 and "Breeding Pool" not in s.tapped_lands_this_turn
    s = std_state(turn=3)
    s.battlefield += ["Snow-Covered Forest", "Snow-Covered Island"]
    s.hand = ["Breeding Pool", "Sol Ring"]  # 1 mana basta: entra virada, sem pagar
    pb.play_land(s, [])
    assert s.life == 40 and "Breeding Pool" in s.tapped_lands_this_turn
    s = std_state(turn=3)
    s.battlefield += ["City of Brass", "Mana Confluence", "Snow-Covered Forest"]
    s.mana_spent_this_turn = 3
    pb._apply_pain(s)
    assert s.life == 38
    s = std_state(turn=3)
    s.hand = ["The World Tree"]
    pb.play_land(s, [])
    assert "The World Tree" in s.tapped_lands_this_turn


def test_bridge_cast_triggers_tide_flux_gauntlet_and_beacon():
    s = std_state()
    s.battlefield += ["Inexorable Tide", "Flux Channeler", "Ichormoon Gauntlet", "Interplanar Beacon"]
    pw(s, "Kaya, Intangible Slayer", 5)
    pb.on_spell_cast(s, pb.COMMANDER, [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 8  # Tide +1, Flux +1, Gauntlet +1
    pb.on_spell_cast(s, "Teferi, Hero of Dominaria", [])
    assert s.life == 41  # Beacon: +1 vida por magia de PW


def test_kaya_zero_narset_selection_vraska_life():
    s = std_state()
    pw(s, "Kaya, Intangible Slayer", 6)
    pb.resolve_planeswalker(s, "Kaya, Intangible Slayer", [])
    assert len(s.hand) == 2
    s = std_state(library=["Bayou", "Arena Rector", "Doubling Season", FILLER] + [FILLER] * 5)
    pw(s, "Narset, Parter of Veils", 5)
    pb.resolve_planeswalker(s, "Narset, Parter of Veils", [])
    assert s.hand == ["Doubling Season"]
    s = std_state()
    pw(s, "Vraska, Betrayal's Sting", 6)
    pb.resolve_planeswalker(s, "Vraska, Betrayal's Sting", [])
    assert s.life == 39


def test_aminatou_plus1_tops_pw_for_bridge_and_minus1_blinks_deepglow():
    s = std_state()
    s.bridge_in_play = True
    s.battlefield.append(pb.COMMANDER)
    pw(s, "Aminatou, the Fateshifter", 3)
    s.hand = ["Ugin, the Spirit Dragon"]
    pb._eff_aminatou_plus1(s, "Aminatou, the Fateshifter", [], None)
    assert s.library[0] == "Ugin, the Spirit Dragon"
    s = std_state()
    creature(s, "Deepglow Skate")
    pw(s, "Aminatou, the Fateshifter", 3)
    pw(s, "Kaya, Intangible Slayer", 6)
    pb.resolve_planeswalker(s, "Aminatou, the Fateshifter", [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 12 and s.blinks_total == 1


def test_oath_of_teferi_blinks_pw_back_at_end_step():
    s = std_state(turn=0, library=[FILLER] * 30)
    pw(s, "Kaya, Intangible Slayer", 2)
    s.battlefield.append("Oath of Teferi")
    pb.noncreature_etb(s, "Oath of Teferi", [])
    assert "Kaya, Intangible Slayer" not in s.battlefield
    pb.play_turn(s, 1, [])
    assert s.loyalty.get("Kaya, Intangible Slayer") == 6  # voltou cheia no end step


def test_oko_plus1_crime_and_minus5_copies():
    s = std_state(library=["Bayou", "Swords to Plowshares"] + [FILLER] * 10)
    pw(s, "Oko, the Ringleader", 2)
    s.crime_this_turn = True
    pb._eff_oko_plus1(s, "Oko, the Ringleader", [], None)
    assert len(s.hand) == 1 and s.discards_total == 1
    s = std_state()
    pw(s, "Oko, the Ringleader", 6)
    pw(s, "Kaya, Intangible Slayer", 2)
    s.battlefield += ["Sol Ring", "Paradox Haze", "Doubling Season"]
    pb._eff_oko_minus5(s, "Oko, the Ringleader", [], None)
    assert s.battlefield.count("Sol Ring") == 3 and s.battlefield.count("Paradox Haze") == 3  # x2 (Doubling Season)
    assert s.loyalty["Kaya, Intangible Slayer"] >= 12  # ficha entra com 6 x2, regra de lenda fica a maior
    assert s.battlefield.count("Kaya, Intangible Slayer") == 1


def test_paradox_haze_copies_add_upkeeps():
    s = std_state(turn=0, library=[FILLER] * 40)
    s.battlefield += [pb.COMMANDER, "Paradox Haze", "Paradox Haze"]
    s.bridge_in_play = True
    pb.play_turn(s, 1, [])
    assert s.bridge_triggers == 3


def test_teferi_untap_effects_and_ta_emblem_windows():
    s = std_state(turn=0, library=["Sphinx of the Second Sun"] * 30)
    s.battlefield += LANDS3
    s.hand = ["Evolution Sage"]  # gasta os 3 terrenos
    pw(s, "Teferi, Hero of Dominaria", 4)
    pb.play_turn(s, 1, [])
    assert s.mana_held_back == 2  # 0 sobrando + 2 terrenos desvirados no end step
    s = std_state(turn=0, library=[FILLER] * 30)
    s.teferi_ta_emblem = True
    pw(s, "Kaya, Intangible Slayer", 5)
    pb.instant_speed_pw_window(s, [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 7 and s.instant_pw_windows_total == 1


def test_tamiyo_fr_emblem_free_cast_and_notebook():
    s = std_state()
    s.tamiyo_free_cast = True
    s.hand = ["Doubling Season", "Farewell"]
    s.land_played = True
    pb.main_phase(s, [])
    assert "Doubling Season" in s.battlefield
    s = std_state()
    s.battlefield.append("Tamiyo's Notebook")
    assert pb.spell_cost(s, "Doubling Season") == 3 and pb.spell_cost(s, pb.COMMANDER) == 5
    s.battlefield += ["Arena Rector", "Carth the Lion"]
    assert pb.spell_cost(s, "Blasphemous Act") == 5  # 9 - 2 criaturas - 2 do Notebook


def test_bolas_borrows_other_planeswalker_ability():
    s = std_state()
    pw(s, "Nicol Bolas, Dragon-God", 4)
    pw(s, "Elspeth, Sun's Champion", 4)
    pb.resolve_planeswalker(s, "Nicol Bolas, Dragon-God", [])
    assert s.battlefield.count("Soldier Token") == 3 and s.loyalty["Nicol Bolas, Dragon-God"] == 5
    assert s.bolas_borrowed_total == 1


def test_gauntlet_extra_turn_comes_before_opponents():
    order = []
    orig_play, orig_opp = pb.play_turn, pb.try_smart_opponent_turn

    def fake_play(state, t, game_log, skip_legacy_removal=False):
        order.append(("nos", t))
        if t == 1:
            state.extra_turns_pending = 1
        game_log.append([])

    def fake_opp(state, log, opp_index=0):
        order.append(("op", opp_index))
    pb.play_turn, pb.try_smart_opponent_turn = fake_play, fake_opp
    try:
        pb.simulate_one_with_interaction(1, turns=3, attack_profile=None)
    finally:
        pb.play_turn, pb.try_smart_opponent_turn = orig_play, orig_opp
    assert order == [("nos", 1), ("nos", 2), ("op", 0), ("op", 1), ("op", 2), ("nos", 3), ("op", 0), ("op", 1), ("op", 2)], order


def test_gauntlet_abilities():
    s = std_state()
    s.battlefield.append("Ichormoon Gauntlet")
    pw(s, "Teferi, Time Raveler", 12)
    pb.resolve_planeswalker(s, "Teferi, Time Raveler", [])
    assert s.extra_turns_pending == 1 and "Teferi, Time Raveler" not in s.loyalty  # [-12] com 12: turno extra, ele morre
    s = std_state()
    s.battlefield.append("Ichormoon Gauntlet")
    pw(s, "Teferi, Time Raveler", 2)
    pw(s, "Kaya, Intangible Slayer", 5)
    pw(s, "Elspeth, Sun's Champion", 5)
    pb.resolve_planeswalker(s, "Teferi, Time Raveler", [])  # +1 fraco com 3 PWs -> [0] proliferate
    assert s.loyalty["Kaya, Intangible Slayer"] == 6 and s.loyalty["Elspeth, Sun's Champion"] == 6


def test_vraska_ult_poison_proliferate_kills_and_vorinclex_doubles():
    s = std_state()
    pw(s, "Vraska, Betrayal's Sting", 9)
    pb.resolve_planeswalker(s, "Vraska, Betrayal's Sting", [])
    assert sorted(s.opp_poison) == [0, 0, 9]
    pb.proliferate_loyalty(s, [], source="test")
    assert s.opp_eliminated_total == 1 and s.opp_alive.count(False) == 1
    s = std_state()
    s.battlefield.append("Vorinclex, Monstrous Raider")
    pw(s, "Vraska, Betrayal's Sting", 9)
    pb.resolve_planeswalker(s, "Vraska, Betrayal's Sting", [])
    assert s.opp_eliminated_total == 1  # 9 x2 = 18 veneno


def test_dynamo_copies_best_activation():
    s = std_state()
    s.battlefield += ["The Peregrine Dynamo"] + LANDS3
    pw(s, "Elspeth, Sun's Champion", 4)
    pb.resolve_planeswalker(s, "Elspeth, Sun's Champion", [])
    pb.try_dynamo_copy_activation(s, [])
    assert s.battlefield.count("Soldier Token") == 6 and s.dynamo_copies_total == 1
    assert s.loyalty["Elspeth, Sun's Champion"] == 5  # a copia nao paga custo


def test_nesting_grounds_moves_counter_to_reach_ult():
    s = std_state()
    s.battlefield += ["Nesting Grounds"] + LANDS3
    pw(s, "Elspeth, Sun's Champion", 6)
    pw(s, "Kaya, Intangible Slayer", 5)
    pb.try_nesting_grounds(s, [])
    assert s.loyalty["Elspeth, Sun's Champion"] == 7 and s.loyalty["Kaya, Intangible Slayer"] == 4


def test_sterling_grove_tutor_only_without_bridge():
    s = std_state(library=[FILLER] * 5 + ["Doubling Season"] + [FILLER] * 5)
    s.battlefield += ["Sterling Grove"] + LANDS3
    assert pb.try_sterling_grove_tutor(s, [])
    assert s.library[0] == "Doubling Season" and "Sterling Grove" in s.graveyard
    s = std_state(library=[FILLER] * 5 + ["Doubling Season"])
    s.battlefield += ["Sterling Grove", pb.COMMANDER] + LANDS3
    s.bridge_in_play = True
    assert not pb.try_sterling_grove_tutor(s, [])


def res_state(turn=5, held=4):
    s = fresh(turn=turn)
    s.battlefield += ["Snow-Covered Island", "Snow-Covered Island", "Snow-Covered Forest", "Snow-Covered Plains"]
    s.mana_held_back = held

    class Always:
        def random(self):
            return 0.0

        def choice(self, x):
            return x[0]

        def choices(self, pop, weights):
            return [pop[0]]
    s.interaction_rng = Always()
    return s


def test_counterspell_stops_removal_and_swan_song_gives_bird():
    s = res_state()
    pw(s, "Teferi, Hero of Dominaria", 6)
    s.hand = ["Counterspell"]
    assert pb.try_smart_opponent_removal(s, [], opp_index=0) is None
    assert "Teferi, Hero of Dominaria" in s.loyalty and "Counterspell" in s.graveyard
    s = res_state()
    pw(s, "Teferi, Hero of Dominaria", 6)
    s.hand = ["Swan Song"]
    pb.try_smart_opponent_removal(s, [], opp_index=1)
    assert any(c["flying"] and c["p"] == 2 for c in s.opp_boards[1])


def test_mana_drain_gives_mana_next_main_phase():
    s = res_state()
    pw(s, "Teferi, Hero of Dominaria", 6)
    s.hand = ["Mana Drain"]
    pb.try_smart_opponent_removal(s, [], opp_index=0)
    assert s.mana_drain_pending == 2


def test_kaya_hexproof_not_targeted():
    s = res_state()
    pw(s, "Kaya, Intangible Slayer", 9)
    pw(s, "Elspeth, Sun's Champion", 3)
    target = pb.try_smart_opponent_removal(s, [], opp_index=0)
    assert target == "Elspeth, Sun's Champion" and "Kaya, Intangible Slayer" in s.loyalty


def test_ripples_and_mutational_save_pw_in_combat():
    s = res_state()
    pw(s, "Kaya, Intangible Slayer", 3)
    s.hand = ["Ripples of Potential"]
    s.opp_boards[0] = [opp(5)]
    pb.opponent_combat(s, 0, [])
    assert s.loyalty.get("Kaya, Intangible Slayer") == 4  # proliferate + phasing: sem dano
    s = res_state()
    pw(s, "Kaya, Intangible Slayer", 3)
    s.hand = ["Mutational Advantage"]
    s.opp_boards[0] = [opp(5)]
    pb.opponent_combat(s, 0, [])
    assert s.loyalty.get("Kaya, Intangible Slayer") == 4


def test_bridge_counter_blocked_by_teferi_tr_halfling_veil():
    s = res_state()
    s.battlefield.append("Teferi, Time Raveler")
    assert not pb.try_smart_opponent_counter(s, [], our_turn=True)
    s = res_state()
    s.bridge_uncounterable = True
    assert not pb.try_smart_opponent_counter(s, [], our_turn=True)
    s = res_state(turn=5)
    s.battlefield += ["Snow-Covered Swamp", "Snow-Covered Mountain", "Bayou", "Taiga"]
    creature(s, "Delighted Halfling")
    pb.cast_bridge(s, [], via_flash=False)
    assert pb.COMMANDER in s.battlefield and s.bridge_uncounterable


def test_plaza_saves_legendary_creature_and_ward_stops_early_removal():
    s = res_state(held=5)
    s.battlefield.append("Plaza of Heroes")
    creature(s, "Vorinclex, Monstrous Raider")
    assert pb.try_smart_opponent_removal(s, [], opp_index=0) is None
    assert "Vorinclex, Monstrous Raider" in s.battlefield and s.plaza_saves_total == 1
    s = res_state(turn=3, held=0)
    s.battlefield.append("Innkeeper's Talent")
    s.innkeepers_talent_level = 2
    pw(s, "Teferi, Hero of Dominaria", 6)
    assert pb.try_smart_opponent_removal(s, [], opp_index=0) is None and s.ward_stops_total == 1


def test_innkeeper_level1_fires_in_standard_mode_and_feeds_all_will_be_one():
    s = std_state(turn=0, library=[FILLER] * 30)
    s.battlefield += ["Innkeeper's Talent", "All Will Be One"]
    creature(s, "Carth the Lion", cast_turn=0)
    pb.play_turn(s, 1, [])
    assert s.creature_counters.get("Carth the Lion") == 1 and s.all_will_be_one_triggers_total >= 1


def test_ugin_ult_lands_trigger_landfall():
    s = std_state(library=["Bayou"] * 7 + [FILLER] * 10)
    s.battlefield.append("Evolution Sage")
    pw(s, "Ugin, the Spirit Dragon", 10)
    pw(s, "Kaya, Intangible Slayer", 5)
    pb.resolve_planeswalker(s, "Ugin, the Spirit Dragon", [])
    assert s.evolution_sage_proliferates == 7


def test_tamiyo_copy_of_urza_restarts_saga():
    s = std_state(library=["Kaya, Intangible Slayer"] + [FILLER] * 10)
    s.graveyard.append("Urza Assembles the Titans")
    s.urza_chapter = 3
    pw(s, "Tamiyo, Compleated Sage", 5)
    pb.resolve_planeswalker(s, "Tamiyo, Compleated Sage", [])
    assert "Urza Assembles the Titans" in s.battlefield and s.urza_chapter == 1
    assert "Kaya, Intangible Slayer" in s.hand


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
# Rodada Reality Fracture (2026-09-25): correcoes de motor + candidatas FRA
# ---------------------------------------------------------------------------

WUBRG5 = ["Snow-Covered Plains", "Snow-Covered Island", "Snow-Covered Swamp", "Snow-Covered Mountain",
          "Snow-Covered Forest"]


def test_generic_mana_table_for_cost_reduction():
    # Tamiyo's Notebook "Spells you cast cost {2} less" so' abate generico:
    # Nicol Bolas {U}{B}{B}{B}{R} fica 5; Counterspell {U}{U} fica 2; Elspeth {4}{W}{W} 6 -> 4.
    s = std_state()
    s.battlefield.append("Tamiyo's Notebook")
    assert pb.spell_cost(s, "Nicol Bolas, Dragon-God") == 5
    assert pb.spell_cost(s, "Counterspell") == 2
    assert pb.spell_cost(s, "Narset, Parter of Veils") == 2  # {1}{U}{U}: so' 1 de generico
    assert pb.spell_cost(s, "Elspeth, Sun's Champion") == 4


def test_tam_reduces_only_planeswalker_generic():
    s = std_state()
    creature(s, "Tam, the Possibility")
    assert pb.spell_cost(s, "Elspeth, Sun's Champion") == 5
    assert pb.spell_cost(s, "Ugin, the Spirit Dragon") == 7
    assert pb.spell_cost(s, "Aminatou, the Fateshifter") == 3   # {W}{U}{B}: sem generico
    assert pb.spell_cost(s, "Nicol Bolas, Dragon-God") == 5
    assert pb.spell_cost(s, "Doubling Season") == 5            # nao e' PW
    s.battlefield.append("Tamiyo's Notebook")
    assert pb.spell_cost(s, "Elspeth, Sun's Champion") == 3    # 4 de generico: -2 -1
    assert pb.spell_cost(s, "Narset, Parter of Veils") == 2    # 1 de generico: nao cai mais


def test_tam_round_end_proliferates_x_types():
    # Teferi Hero + Teferi TR (1 tipo) + Ugin (outro tipo) -> X = 2 proliferates
    s = std_state(turn=6)
    s.battlefield += WUBRG5
    creature(s, "Tam, the Possibility", cast_turn=4)
    pw(s, "Teferi, Hero of Dominaria", 4)
    pw(s, "Teferi, Time Raveler", 3)
    pw(s, "Ugin, the Spirit Dragon", 7)
    s.mana_held_back = 5
    pb.try_tam_proliferate(s, [], window="round_end")
    assert s.tam_activations_total == 1 and s.tam_proliferates_total == 2
    assert s.loyalty == {"Teferi, Hero of Dominaria": 6, "Teferi, Time Raveler": 5, "Ugin, the Spirit Dragon": 9}
    assert s.mana_held_back == 0


def test_tam_proliferate_doubled_by_doubling_season():
    s = std_state(turn=6)
    s.battlefield += WUBRG5 + ["Doubling Season"]
    creature(s, "Tam, the Possibility", cast_turn=4)
    pw(s, "Oko, the Ringleader", 3)
    pw(s, "Narset, Parter of Veils", 3)
    s.mana_held_back = 5
    pb.try_tam_proliferate(s, [], window="round_end")
    assert s.loyalty == {"Oko, the Ringleader": 7, "Narset, Parter of Veils": 7}  # 2 tipos x (+1 x2)


def test_peregrine_dynamo_copies_tam_at_round_end():
    # Dynamo: "Copy target activated ... ability ... from another legendary
    # source that's not a commander" -- a Tam e' lendaria: X proliferates de novo.
    s = std_state(turn=6)
    s.battlefield += WUBRG5
    creature(s, "Tam, the Possibility", cast_turn=3)
    creature(s, "The Peregrine Dynamo", cast_turn=3)
    pw(s, "Teferi, Hero of Dominaria", 4)
    pw(s, "Ugin, the Spirit Dragon", 7)
    s.mana_held_back = 6
    pb.try_tam_proliferate(s, [], window="round_end")
    assert s.tam_dynamo_copies_total == 1 and s.tam_proliferates_total == 4
    assert s.loyalty == {"Teferi, Hero of Dominaria": 8, "Ugin, the Spirit Dragon": 11}
    # Dynamo que atacou no meu turno (virada no fim da rodada) nao copia
    s = std_state(turn=6)
    s.battlefield += WUBRG5
    creature(s, "Tam, the Possibility", cast_turn=3)
    creature(s, "The Peregrine Dynamo", cast_turn=3)
    pw(s, "Ugin, the Spirit Dragon", 7)
    s.round_end_tapped = {("The Peregrine Dynamo", None)}
    s.mana_held_back = 6
    pb.try_tam_proliferate(s, [], window="round_end")
    assert s.tam_dynamo_copies_total == 0 and s.loyalty["Ugin, the Spirit Dragon"] == 8


def test_tam_summoning_sickness_and_colors():
    # Conjurada no meu turno anterior (5): no end step dos oponentes ainda esta'
    # doente (CR 302.6, "since their most recent turn began").
    s = std_state(turn=6)
    s.battlefield += WUBRG5
    creature(s, "Tam, the Possibility", cast_turn=5)
    pw(s, "Ugin, the Spirit Dragon", 7)
    s.mana_held_back = 5
    pb.try_tam_proliferate(s, [], window="round_end")
    assert s.tam_activations_total == 0
    # Sem fonte de vermelho: {W}{U}{B}{R}{G} nao paga.
    s = std_state(turn=6)
    s.battlefield += [l for l in WUBRG5 if l != "Snow-Covered Mountain"] + ["Snow-Covered Forest"]
    creature(s, "Tam, the Possibility", cast_turn=3)
    pw(s, "Ugin, the Spirit Dragon", 7)
    s.mana_held_back = 5
    pb.try_tam_proliferate(s, [], window="round_end")
    assert s.tam_activations_total == 0


def test_tam_main_window_only_when_it_reaches_an_ultimate():
    s = std_state(turn=6)
    s.battlefield += WUBRG5
    creature(s, "Tam, the Possibility", cast_turn=3)
    pw(s, "Elspeth, Sun's Champion", 5)  # ult -7: 1 tipo -> +1 = 6, nao alcanca
    pb.try_tam_proliferate(s, [], window="main")
    assert s.tam_activations_total == 0
    pw(s, "Ugin, the Spirit Dragon", 7)   # 2 tipos -> Elspeth 5 -> 7
    pb.try_tam_proliferate(s, [], window="main")
    assert s.tam_activations_total == 1 and s.loyalty["Elspeth, Sun's Champion"] == 7
    assert s.tam_used_turn == 6
    s.mana_held_back = 5  # ja' virou no main: nao ativa de novo no end step dos oponentes
    s.turn = 7
    pb.try_tam_proliferate(s, [], window="round_end")
    assert s.tam_activations_total == 1


def test_tam_never_attacks():
    s = fresh(turn=6)
    creature(s, "Tam, the Possibility", cast_turn=3)
    creature(s, "Carth the Lion", cast_turn=3)
    pb.our_combat_step(s, [])
    assert ("Tam, the Possibility", None) not in s.our_tapped
    assert ("Carth the Lion", None) in s.our_tapped


def test_loyal_tutor_with_bridge_puts_best_pw_onto_battlefield():
    lib = [FILLER] * 10 + ["Ugin, the Spirit Dragon"] + [FILLER] * 10 + ["Narset, Parter of Veils"]
    s = std_state(turn=6, library=lib)
    s.battlefield += LANDS3 + [pb.COMMANDER]
    s.bridge_in_play = True
    s.hand = ["Loyal Tutor"]
    pb.play_turn(s, 6, [])
    assert "Ugin, the Spirit Dragon" in s.loyalty
    assert s.loyal_tutor_bridge_total == 1 and "Loyal Tutor" in s.graveyard
    # Ugin entrou no upkeep pela Bridge -> ativou no main phase do mesmo turno
    assert "Ugin, the Spirit Dragon" in s.pw_activated_this_turn


def test_loyal_tutor_uses_held_mana_at_round_end():
    s = std_state(turn=6, library=[FILLER] * 5 + ["Kaya, Intangible Slayer"] + [FILLER] * 5)
    s.battlefield += LANDS3 + [pb.COMMANDER]
    s.bridge_in_play = True
    s.hand = ["Loyal Tutor"]
    s.mana_held_back = 1
    pb.try_loyal_tutor(s, [], window="round_end")
    assert s.library[0] == "Kaya, Intangible Slayer" and s.mana_held_back == 0


def test_loyal_tutor_held_without_bridge_early_then_draw_line():
    lib = [FILLER] * 5 + ["Teferi, Hero of Dominaria"] + [FILLER] * 5
    s = std_state(turn=3, library=lib)
    s.battlefield += LANDS3
    s.hand = ["Loyal Tutor"]
    pb.try_loyal_tutor(s, [], window="upkeep")
    assert "Loyal Tutor" in s.hand  # segura pra linha da Bridge
    s.turn = pb.LOYAL_TUTOR_DRAW_MIN_TURN
    pb.try_loyal_tutor(s, [], window="upkeep")
    assert s.library[0] == "Teferi, Hero of Dominaria" and s.loyal_tutor_draw_total == 1


def test_entrust_sacrifices_lowest_fetches_best_and_activates():
    lib = ["Ugin, the Spirit Dragon"] + [FILLER] * 20
    s = std_state(turn=6, library=lib)
    s.battlefield += WUBRG5 + [pb.COMMANDER]
    s.bridge_in_play = True
    pw(s, "Teferi, Time Raveler", 1)
    pw(s, "Elspeth, Sun's Champion", 3)
    s.hand = ["Entrust the Spark"]
    s.land_played = True
    pb.main_phase(s, [])  # passada: TR 1 -> 2, Elspeth 3 -> 4; depois Entrust
    assert "Teferi, Time Raveler" in s.graveyard and "Teferi, Time Raveler" not in s.loyalty
    assert "Ugin, the Spirit Dragon" in s.loyalty and s.entrust_casts_total == 1
    assert s.pw_deaths_total == 1 and "Elspeth, Sun's Champion" in s.loyalty
    assert "Ugin, the Spirit Dragon" in s.pw_activated_this_turn  # CR 606.3: ativa no mesmo main phase
    assert s.loyalty["Ugin, the Spirit Dragon"] == 9  # entrou com 7, +2 na hora


def test_entrust_carth_trigger_resolves_after_the_search():
    # A busca acontece na resolucao; o gatilho do Carth (morte do PW) so' depois:
    # o Carth nao "rouba" o Ugin -- acha o Narset nas 7 do topo ja' embaralhadas.
    lib = ["Ugin, the Spirit Dragon", "Narset, Parter of Veils"]
    s = std_state(turn=6, library=lib)
    creature(s, "Carth the Lion", cast_turn=2)
    pw(s, "Teferi, Time Raveler", 1)
    pb.resolve_entrust_the_spark(s, [])
    assert "Ugin, the Spirit Dragon" in s.loyalty
    assert "Narset, Parter of Veils" in s.hand and s.carth_tutors_total == 1


def test_entrust_stays_in_hand_without_planeswalker():
    s = std_state(turn=6, library=["Ugin, the Spirit Dragon"] + [FILLER] * 20)
    s.battlefield += WUBRG5
    s.hand = ["Entrust the Spark"]
    s.land_played = True
    pb.main_phase(s, [])
    assert s.hand == ["Entrust the Spark"] and s.entrust_casts_total == 0


def test_proliferate_advances_urza_to_chapter_ii_only_when_useful():
    s = std_state(turn=6)
    s.battlefield.append("Urza Assembles the Titans")
    s.urza_chapter = 1
    pw(s, "Narset, Parter of Veils", 3)
    pb.proliferate_loyalty(s, [], source="test")
    assert s.urza_chapter == 1  # sem PW MV<=6 na mao: deixa a saga de fora
    s.hand = ["Oko, the Ringleader"]
    pb.proliferate_loyalty(s, [], source="test")
    assert s.urza_chapter == 2 and "Oko, the Ringleader" in s.loyalty
    # II -> III fora da janela pre-ativacao: nao inclui (perderia o "this turn")
    s.pre_activation_window = False
    pb.proliferate_loyalty(s, [], source="test")
    assert s.urza_chapter == 2
    s.pre_activation_window = True
    pb.proliferate_loyalty(s, [], source="test")
    assert s.urza_chapter == 3 and s.urza_chapter_iii_this_turn
    assert "Urza Assembles the Titans" in s.graveyard


def test_apply_swaps_keeps_line_position():
    base = pb.build_decklist(False)
    out = pb.apply_swaps(base, [("Oath of Nissa", "Tam, the Possibility"), ("Swan Song", "Loyal Tutor")])
    a, b = pb.parse_decklist(base), pb.parse_decklist(out)
    assert len(b) == 99
    assert b.index("Tam, the Possibility") == a.index("Oath of Nissa")
    assert b.index("Loyal Tutor") == a.index("Swan Song")


# ---------------------------------------------------------------------------
# Candidatas 2026-09-29: Dihada, Commodore Guff, Vronos, Sarkhan the Masterless
# (um teste por clausula do oraculo + as interacoes com os motores da lista)
# ---------------------------------------------------------------------------
DIHADA, GUFF, VRONOS, SARKHAN = pb.CANDIDATE_PWS
BOLAS = "Nicol Bolas, Dragon-God"


def run_ability(s, name, key, x=None):
    """Paga o custo real de `key` (com Carth etc.) e resolve o efeito."""
    pb.activate_ability(s, name, name, key, x, [])


def test_candidates_are_inert_in_the_current_list():
    deck = pb.parse_decklist(pb.build_decklist(False))
    assert not any(c in deck for c in pb.CANDIDATE_PWS)
    assert all(pb.C(c).type == "Planeswalker" and pb.PLANESWALKER_STARTING_LOYALTY[c] == 5 for c in pb.CANDIDATE_PWS)
    for seed in range(8):
        assert pb.simulate_one(3_000_000 + seed, 10, False)["cand_stats"] == {}
        assert pb.simulate_one_with_interaction(6_000_000 + seed, turns=10).cand_stats == {}


def test_dihada_plus2_shields_the_legendary_creature_that_gains_most():
    s = fresh()
    pw(s, DIHADA, 5)
    creature(s, "The Peregrine Dynamo")  # lendaria sem vigilancia/lifelink: ganha os 3
    creature(s, "Atraxa, Praetors' Voice")  # ja' tem vigilancia e lifelink
    creature(s, "Bloom Tender")             # nao lendaria: nunca e' alvo
    run_ability(s, DIHADA, "+2")
    assert s.loyalty[DIHADA] == 7 and s.dihada_shield == "The Peregrine Dynamo"
    assert {"vigilance", "lifelink", "indestructible"} <= pb._pt(s, ("The Peregrine Dynamo", None))[2]
    assert "indestructible" not in pb._pt(s, ("Bloom Tender", None))[2]
    s = fresh()
    pw(s, DIHADA, 5)
    creature(s, "Carth the Lion")
    run_ability(s, DIHADA, "+2")  # imposto do Carth: o [+2] vira [+3] (ruling); e' lendaria, entao e' alvo
    assert s.loyalty[DIHADA] == 8 and s.dihada_shield == "Carth the Lion"
    s = fresh()
    pw(s, DIHADA, 5)
    run_ability(s, DIHADA, "+2")  # "up to one": sem criatura lendaria so' ganha a lealdade
    assert s.loyalty[DIHADA] == 7 and s.dihada_shield is None


def test_dihada_shield_wall_in_combat_and_survives_destroy_wipes():
    s = res_state()
    creature(s, "The Peregrine Dynamo")
    pw(s, "Kaya, Intangible Slayer", 3)
    s.opp_boards[0] = [opp(6)]  # 6 de dano mataria um Carth 3/5 normal
    pb.opponent_combat(s, 0, [])
    assert "Kaya, Intangible Slayer" not in s.loyalty  # controle: sem o escudo ninguem bloqueia e a Kaya morre
    s = res_state()
    creature(s, "The Peregrine Dynamo")
    pw(s, "Kaya, Intangible Slayer", 3)
    s.dihada_shield = "The Peregrine Dynamo"
    s.opp_boards[0] = [opp(6)]
    pb.opponent_combat(s, 0, [])
    assert "The Peregrine Dynamo" in s.battlefield and s.loyalty["Kaya, Intangible Slayer"] == 3
    # wipe "destroy all creatures" do oponente: com o escudo Carth fica; sem, morre
    s = res_state()
    creature(s, "The Peregrine Dynamo")
    s.dihada_shield = "The Peregrine Dynamo"
    pb.try_smart_opponent_wipe(s, [], opp_index=0)
    assert "The Peregrine Dynamo" in s.battlefield
    s.dihada_shield = None
    pb.try_smart_opponent_wipe(s, [], opp_index=0)
    assert "The Peregrine Dynamo" not in s.battlefield
    # meus proprios wipes: "destroy" nao leva, "exile" leva
    s = fresh()
    creature(s, "The Peregrine Dynamo")
    s.dihada_shield = "The Peregrine Dynamo"
    pb._mass_creature_removal(s, "destroy", [])
    assert "The Peregrine Dynamo" in s.battlefield
    pb._mass_creature_removal(s, "exile", [])
    assert "The Peregrine Dynamo" not in s.battlefield


def test_dihada_shield_ends_at_my_next_untap():
    s = std_state(turn=5, library=[FILLER] * 30)
    s.dihada_shield = "Carth the Lion"
    pb.play_turn(s, 6, [])
    assert s.dihada_shield is None


def test_dihada_minus3_legendary_to_hand_rest_milled_one_treasure_each():
    top = ["Kaya, Intangible Slayer", "Snow-Covered Forest", "Carth the Lion", "Farseek"]
    s = fresh(library=top + [FILLER] * 10)
    pw(s, DIHADA, 5)
    run_ability(s, DIHADA, "-3")
    assert s.loyalty[DIHADA] == 2
    assert s.hand == ["Kaya, Intangible Slayer", "Carth the Lion"]  # "put into your hand": nao e' compra
    assert s.graveyard == ["Snow-Covered Forest", "Farseek"] and len(s.library) == 10
    assert s.treasure_stock == 2 and s.pw_draws_total == 0
    assert s.cand_stats["dihada_legends_to_hand"] == 2 and s.cand_stats["dihada_milled"] == 2
    # Doubling Season dobra as fichas: 2 cartas pro cemiterio = 4 Treasures
    s = fresh(library=top + [FILLER] * 10)
    s.battlefield.append("Doubling Season")
    pw(s, DIHADA, 5)
    run_ability(s, DIHADA, "-3")
    assert s.treasure_stock == 4
    # biblioteca com menos de 4 cartas: revela so' o que tem
    s = fresh(library=["Farseek", "Kaya, Intangible Slayer"])
    pw(s, DIHADA, 5)
    run_ability(s, DIHADA, "-3")
    assert s.hand == ["Kaya, Intangible Slayer"] and s.treasure_stock == 1 and s.library == []


def test_treasure_is_any_color_mana_and_is_consumed_only_when_spent():
    s = fresh()
    s.treasure_stock = 2
    assert pb.total_mana(s) == 2 and pb.color_sources(s, "B") == 2 and pb.color_sources(s, "R") == 2
    s.mana_spent_this_turn = 1
    pb._settle_treasures(s)  # sem outra fonte: o 1 gasto saiu de um Treasure
    assert s.treasure_stock == 1 and s.mana_spent_this_turn == 0 and pb.remaining_mana(s) == 1
    s = fresh()
    s.battlefield += [FILLER] * 3
    s.treasure_stock = 2
    s.mana_spent_this_turn = 3  # os 3 terrenos cobrem: Treasure intocado (persiste entre turnos)
    pb._settle_treasures(s)
    assert s.treasure_stock == 2
    s.mana_spent_this_turn = 4
    pb._settle_treasures(s)
    assert s.treasure_stock == 1
    s = std_state(turn=5, library=[FILLER] * 30)
    s.treasure_stock = 3
    pb.play_turn(s, 6, [])  # nada pra conjurar: os 3 Treasures sobrevivem e contam como mana guardada
    assert s.treasure_stock == 3 and s.mana_held_back == 4


def test_dihada_ult_untaps_nonland_mana_and_steals_opponent_creatures_for_combat():
    s = res_state()
    pw(s, DIHADA, 11)
    s.battlefield += ["Sol Ring", "Arcane Signet"]
    s.opp_boards = [[opp(4), opp(2)], [opp(3)], []]
    run_ability(s, DIHADA, "-11")
    assert DIHADA not in s.loyalty  # 11 -> 0
    assert s.mana_bonus_this_turn == 3  # Sol Ring (2) + Arcane Signet (1) desviram
    assert s.stolen_power_this_turn == 9
    pb.our_combat_step(s, [])
    assert s.our_combat_damage_proxy_total == 9 and s.cand_stats["dihada_attack_damage"] == 9


def test_dihada_policy_minus3_by_default_ult_only_with_a_board_to_steal():
    s = res_state()
    pw(s, DIHADA, 12)
    s.opp_boards = [[opp(3)], [], []]
    assert pb.choose_pw_ability(s, DIHADA, 12)[1] == "-3"  # so' 3 de poder pra roubar
    s.opp_boards = [[opp(6), opp(5)], [], []]
    assert pb.choose_pw_ability(s, DIHADA, 12)[1] == "-11"
    s = std_state()
    pw(s, DIHADA, 12)
    assert pb.choose_pw_ability(s, DIHADA, 12)[1] == "-3"  # modo padrao: sem oponente, nunca ult
    s = std_state()
    pw(s, DIHADA, 3)
    assert pb.choose_pw_ability(s, DIHADA, 3)[1] == "+2"  # nao se mata no -3


def test_guff_end_step_counter_on_another_pw_doubled_and_feeds_all_will_be_one():
    s = fresh()
    pw(s, GUFF, 5)
    pw(s, "Teferi, Hero of Dominaria", 6)
    pb.guff_end_step(s, [])
    assert s.loyalty["Teferi, Hero of Dominaria"] == 7 and s.loyalty[GUFF] == 5  # "another": nunca ela mesma
    s = fresh()
    pw(s, GUFF, 5)
    pb.guff_end_step(s, [])  # sem outro PW: sem alvo legal
    assert s.loyalty[GUFF] == 5 and s.cand_stats.get("guff_end_triggers") is None
    s = fresh()
    s.battlefield += ["Doubling Season", "All Will Be One"]
    pw(s, GUFF, 5)
    pw(s, "Teferi, Hero of Dominaria", 6)
    pb.guff_end_step(s, [])
    assert s.loyalty["Teferi, Hero of Dominaria"] == 8  # Doubling Season: 1 marcador vira 2
    assert s.all_will_be_one_triggers_total == 1
    s = fresh()
    pw(s, GUFF, 5)
    pw(s, "Teferi, Hero of Dominaria", 6)
    s.phased_out = {GUFF}  # fora de fase nao tem gatilho
    pb.guff_end_step(s, [])
    assert s.loyalty["Teferi, Hero of Dominaria"] == 6


def test_guff_end_step_fires_every_turn_in_play_turn_including_extra_turns():
    s = std_state(turn=0, library=[FILLER] * 40)
    pw(s, GUFF, 5)
    pw(s, "Elspeth, Sun's Champion", 4)  # +1 dela na passada + 1 do Guff = 6
    pb.play_turn(s, 1, [])
    assert s.cand_stats["guff_end_triggers"] == 1 and s.loyalty["Elspeth, Sun's Champion"] == 6
    pb.play_turn(s, 2, [])
    assert s.cand_stats["guff_end_triggers"] == 2


def test_guff_plus1_wizard_sick_then_pays_generic_of_planeswalker_spells_only():
    s = fresh()
    pw(s, GUFF, 5)
    run_ability(s, GUFF, "+1")
    assert s.battlefield.count("Wizard Token") == 1 and s.loyalty[GUFF] == 6
    assert s.wizard_pool == 0 and pb.spell_cost(s, "Ugin, the Spirit Dragon") == 8  # doenca: so' vale no turno seguinte
    s.wizard_pool = 1
    assert pb.spell_cost(s, "Ugin, the Spirit Dragon") == 7  # magia de PW: -1 generico
    assert pb.spell_cost(s, "Farseek") == 2  # "only to cast a planeswalker spell"
    assert pb.spell_cost(s, BOLAS) == 5  # {U}{B}{B}{B}{R}: nada generico pra abater (conservador)
    s = fresh()
    s.battlefield.append("Doubling Season")
    pw(s, GUFF, 5)
    run_ability(s, GUFF, "+1")
    assert s.battlefield.count("Wizard Token") == 2  # Doubling Season dobra fichas


def test_guff_wizard_mana_is_spent_once_when_the_planeswalker_is_cast():
    s = std_state(turn=6)
    s.battlefield += [FILLER] * 7
    token(s, "Wizard Token")
    s.wizard_pool = 1
    s.hand = ["Ugin, the Spirit Dragon"]  # {8}: 7 terrenos + 1 Wizard
    pb.main_phase(s, [])
    assert "Ugin, the Spirit Dragon" in s.battlefield
    assert s.wizard_pool == 0 and s.cand_stats["guff_wizard_mana"] == 1
    assert s.mana_spent_this_turn == 7


def test_guff_minus3_draws_and_damages_x_planeswalkers_and_policy():
    s = fresh(library=[FILLER] * 20)
    pw(s, GUFF, 5)
    pw(s, "Kaya, Intangible Slayer", 6)
    pw(s, "Elspeth, Sun's Champion", 4)
    run_ability(s, GUFF, "-3")
    assert len(s.hand) == 3 and s.loyalty[GUFF] == 2 and s.pw_draws_total == 3  # X = 3 PWs (ela inclusa)
    assert s.pw_life_lost_opponent_total == 3 * sum(s.opp_alive)
    s = std_state(library=[FILLER] * 20)
    pw(s, GUFF, 5)
    pw(s, "Kaya, Intangible Slayer", 6)
    assert pb.choose_pw_ability(s, GUFF, 5)[1] == "+1"  # X = 2: nao compensa
    pw(s, "Elspeth, Sun's Champion", 4)
    pw(s, "Narset, Parter of Veils", 5)
    assert pb.choose_pw_ability(s, GUFF, 5)[1] == "-3"  # X = 4 e a mao aguenta
    assert pb.choose_pw_ability(s, GUFF, 3)[1] == "+1"  # nao se mata (o gatilho de end step depende dela)


def test_vronos_plus1_phases_out_two_other_pws_at_the_end_step_until_my_untap():
    s = res_state()
    pw(s, VRONOS, 5)
    pw(s, "Teferi, Hero of Dominaria", 7)
    pw(s, "Kaya, Intangible Slayer", 5)
    pw(s, "Narset, Parter of Veils", 3)
    pw(s, "Teferi, Time Raveler", 9)  # fora da escolha: fora de fase perderia o estatico que protege a Bridge
    run_ability(s, VRONOS, "+1")
    assert s.pending_phase_out == ["Teferi, Hero of Dominaria", "Kaya, Intangible Slayer"]  # "up to two": os 2 maiores
    assert not s.phased_out  # so' no "beginning of the next end step"
    pb.vronos_phase_out_step(s, [])
    assert s.phased_out == {"Teferi, Hero of Dominaria", "Kaya, Intangible Slayer"} and s.pending_phase_out == []
    s.opp_boards[0] = [opp(3)]
    pb.opponent_combat(s, 0, [])  # quem esta' fora de fase nao existe pro ataque
    assert s.loyalty["Teferi, Hero of Dominaria"] == 7 and s.loyalty["Kaya, Intangible Slayer"] == 5
    assert s.loyalty["Teferi, Time Raveler"] == 6
    target = pb.try_smart_opponent_removal(s, [], opp_index=0)
    assert target not in s.phased_out
    s.loyalty.pop(VRONOS, None)
    if VRONOS in s.battlefield:
        s.battlefield.remove(VRONOS)
    pb.play_turn(s, 6, [], skip_legacy_removal=True)  # meu untap: voltam de fase
    assert not s.phased_out


def test_vronos_guff_counter_resolves_before_the_phase_out_at_end_step():
    s = std_state(turn=0, library=[FILLER] * 40)
    pw(s, GUFF, 5)
    pw(s, VRONOS, 5)
    pw(s, "Teferi, Hero of Dominaria", 6)
    pb.play_turn(s, 1, [])
    # Teferi: +1 dela na passada (7) + 1 do Guff no end step (8), ANTES de sair de fase
    assert s.loyalty["Teferi, Hero of Dominaria"] == 8
    assert s.phased_out == {GUFF, "Teferi, Hero of Dominaria"}


def test_vronos_minus2_bounces_one_creature_per_opponent():
    s = res_state()
    pw(s, VRONOS, 5)
    a, b = opp(5), opp(3)
    s.opp_boards = [[a, opp(2)], [b], []]
    run_ability(s, VRONOS, "-2")
    assert a["frozen"] == 1 and b["frozen"] == 1 and s.loyalty[VRONOS] == 3
    assert s.pw_removal_proxy_total == sum(s.opp_alive) and s.crime_this_turn
    s = res_state()
    pw(s, VRONOS, 5)
    s.opp_boards[0] = [opp(5)]
    assert pb.choose_pw_ability(s, VRONOS, 5)[1] == "-2"  # ameaca real: modo defensivo
    s = res_state()
    pw(s, VRONOS, 5)
    assert pb.choose_pw_ability(s, VRONOS, 5)[1] == "+1"


def test_vronos_ult_construct_9_9_unblockable_attacks_if_artifact_was_there_at_turn_start():
    s = res_state(turn=5)
    pw(s, VRONOS, 7)
    s.battlefield += ["Arcane Signet", "Sol Ring"]
    s.artifact_enter_turn = {"Arcane Signet": 2, "Sol Ring": 2}
    s.opp_boards[0] = [opp(2)]
    assert pb.choose_pw_ability(s, VRONOS, 7)[1] == "-7"
    run_ability(s, VRONOS, "-7")
    assert s.vronos_constructs == ["Arcane Signet"] and VRONOS not in s.loyalty
    pb.our_combat_step(s, [])  # ruling 2023-07-28: ataca no MESMO turno se o artefato ja' estava em campo
    assert s.our_combat_damage_proxy_total == 9 and s.our_tapped == []  # vigilancia
    pb.try_smart_opponent_wipe(s, [], opp_index=0)  # "destroy all artifacts": o Construct e' indestrutivel
    assert "Arcane Signet" in s.battlefield and "Sol Ring" not in s.battlefield
    s = res_state(turn=5)  # controle: artefato que entrou NESTE turno tem doenca de invocacao
    pw(s, VRONOS, 7)
    s.battlefield.append("Arcane Signet")
    pb.noncreature_etb(s, "Arcane Signet", [])
    assert s.artifact_enter_turn["Arcane Signet"] == 5
    run_ability(s, VRONOS, "-7")
    pb.our_combat_step(s, [])
    assert s.our_combat_damage_proxy_total == 0
    s.turn = 6
    pb.our_combat_step(s, [])
    assert s.our_combat_damage_proxy_total == 9


def test_sarkhan_plus1_animates_all_pws_ready_ones_attack_they_still_activate_but_lose_gauntlet():
    s = res_state(turn=6)
    pw(s, SARKHAN, 5, entered=6)
    pw(s, "Kaya, Intangible Slayer", 3, entered=2)
    pw(s, "Elspeth, Sun's Champion", 4, entered=6)
    run_ability(s, SARKHAN, "+1")
    assert s.sarkhan_animated == {SARKHAN, "Kaya, Intangible Slayer", "Elspeth, Sun's Champion"}
    assert s.cand_stats["sarkhan_animated"] == 3 and s.cand_stats["sarkhan_ready_attackers"] == 1
    # ruling 2019-05-03: "you can still activate their loyalty abilities if you haven't done so yet this turn"
    pb.resolve_planeswalker(s, "Kaya, Intangible Slayer", [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 5
    pw(s, "Narset, Parter of Veils", 5, entered=6)  # entrou depois: o efeito so' pegou quem ja' estava (CR 611.2c)
    assert "Narset, Parter of Veils" not in s.sarkhan_animated
    pb.resolve_planeswalker(s, "Narset, Parter of Veils", [])
    assert s.loyalty["Narset, Parter of Veils"] == 3
    pb.our_combat_step(s, [])
    assert s.our_combat_damage_proxy_total == 4 and s.cand_stats["sarkhan_attack_damage"] == 4  # so' a Kaya 4/4 voadora
    s.elspeth_emblem = 1
    assert pb._candidate_attackers(s)[0][1] == 6  # o emblema da Elspeth (+2/+2) vale pro Dragao
    # "Planeswalkers you control have '[0]: Proliferate ...[-12]: extra turn'": o PW animado nao e' planeswalker
    s = res_state(turn=6)
    s.battlefield.append("Ichormoon Gauntlet")
    pw(s, "Kaya, Intangible Slayer", 12, entered=2)
    assert pb.choose_pw_ability(s, "Kaya, Intangible Slayer", 12)[:2] == ("Ichormoon Gauntlet", "-12")
    s.sarkhan_animated.add("Kaya, Intangible Slayer")
    assert pb.choose_pw_ability(s, "Kaya, Intangible Slayer", 12)[:2] == ("Kaya, Intangible Slayer", "0")


def test_sarkhan_activates_last_and_animation_ends_at_the_end_step():
    s = std_state(turn=0, library=[FILLER] * 40)
    pw(s, SARKHAN, 5)  # primeiro no dict: mesmo assim ativa por ultimo
    pw(s, "Kaya, Intangible Slayer", 3)
    assert pb._activation_order(s)[-1] == SARKHAN
    pb.play_turn(s, 2, [])
    assert s.loyalty["Kaya, Intangible Slayer"] == 5  # +2 antes da animacao (se a Sarkhan fosse primeiro ficaria 3)
    assert s.cand_stats["sarkhan_plus1"] == 1 and s.sarkhan_animated == set()


def test_sarkhan_dragons_ping_every_attacker_before_damage():
    s = res_state(turn=6)
    pw(s, SARKHAN, 5)
    pw(s, "Kaya, Intangible Slayer", 3)
    token(s, "Dragon Token", 2)  # 2 Dragoes: 2 de dano em CADA atacante
    small, big = opp(2), opp(6)
    s.opp_boards[0] = [small, big]
    pb.opponent_combat(s, 0, [])
    assert s.cand_stats["sarkhan_ping_kills"] == 1 and s.cand_stats["sarkhan_ping_damage"] == 4
    assert s.opp_boards[0] == []  # o 2/2 morre no gatilho; o 6/6 (4 restantes) morre na troca com o Dragao 4/4
    s = res_state(turn=6)  # controle: sem a Sarkhan (Dragoes so' de bloqueio) o 6/6 sobrevive
    pw(s, "Kaya, Intangible Slayer", 3)
    token(s, "Dragon Token", 2)
    small, big = opp(2), opp(6)
    s.opp_boards[0] = [small, big]
    pb.opponent_combat(s, 0, [])
    assert big in s.opp_boards[0] and "sarkhan_ping_kills" not in s.cand_stats
    s = res_state(turn=6)  # o dano marcado some no fim do turno
    pw(s, SARKHAN, 5)
    pw(s, "Kaya, Intangible Slayer", 3)
    token(s, "Dragon Token", 1)
    tough = opp(5, 7)
    s.opp_boards[0] = [tough]
    pb.opponent_combat(s, 0, [])
    assert tough["t"] == 7 and s.cand_stats["sarkhan_ping_damage"] == 1
    s.phased_out = {SARKHAN}
    assert pb._sarkhan_ping_count(s) == 0  # fora de fase: sem gatilho


def test_sarkhan_minus3_dragon_token_and_defensive_policy():
    s = fresh()
    pw(s, SARKHAN, 5)
    run_ability(s, SARKHAN, "-3")
    assert s.battlefield.count("Dragon Token") == 1 and s.loyalty[SARKHAN] == 2
    s = fresh()
    s.battlefield.append("Doubling Season")
    pw(s, SARKHAN, 5)
    run_ability(s, SARKHAN, "-3")
    assert s.battlefield.count("Dragon Token") == 2
    s = res_state()
    pw(s, SARKHAN, 5)
    assert pb.choose_pw_ability(s, SARKHAN, 5)[1] == "+1"  # sem ameaca: anima os PWs
    s.opp_boards[0] = [opp(5)]
    assert pb.choose_pw_ability(s, SARKHAN, 5)[1] == "-3"  # com ameaca: Dragao de guarda
    token(s, "Dragon Token", 2)
    assert pb.choose_pw_ability(s, SARKHAN, 5)[1] == "+1"  # ja' tem 2


def test_bolas_borrows_guff_and_dihada_minus3():
    s = fresh(library=[FILLER] * 20)
    for name, loy in ((BOLAS, 6), (GUFF, 5), ("Narset, Parter of Veils", 5), ("Ashiok, Dream Render", 5),
                      ("Vraska, Betrayal's Sting", 6)):
        pw(s, name, loy)
    choice = pb._bolas_borrowed_choice(s, BOLAS, 6)
    assert choice[:2] == (GUFF, "-3")
    pb.activate_ability(s, BOLAS, choice[0], choice[1], None, [])
    assert s.loyalty[BOLAS] == 3 and len(s.hand) == 5  # o custo sai da lealdade do Bolas; X = 5 PWs
    s = fresh(library=[FILLER] * 20)
    for name, loy in ((BOLAS, 6), (DIHADA, 5), ("Narset, Parter of Veils", 5)):
        pw(s, name, loy)
    assert pb._bolas_borrowed_choice(s, BOLAS, 6)[:2] == (DIHADA, "-3")


def test_candidates_run_full_games_without_exceptions():
    for cand in pb.CANDIDATE_PWS:
        for seed in range(12):
            r = pb.simulate_one(3_000_000 + seed, 10, False, swap=[("Arena Rector", cand)])
            assert isinstance(r["cand_stats"], dict)
            for prof in ("mixed", "go_wide", "voltron", "low"):
                pb.simulate_one_with_interaction(6_000_000 + seed, turns=10, attack_profile=prof,
                                                 swap=[("Arena Rector", cand)])
    # os 4 juntos
    sw = [("Arena Rector", DIHADA), ("Swan Song", GUFF), ("Veil of Summer", VRONOS), ("Oath of Nissa", SARKHAN)]
    for seed in range(12):
        pb.simulate_one(3_000_000 + seed, 10, False, swap=sw)
        pb.simulate_one_with_interaction(6_000_000 + seed, turns=10, swap=sw)


# ---------------------------------------------------------------------------
# Sisay, Weatherlight Captain (candidata de 2026-09-29): um teste por clausula do oraculo ao vivo
# ---------------------------------------------------------------------------
SISAY = pb.SISAY
FIVE_COLOR_LANDS = ["Snow-Covered Plains", "Snow-Covered Island", "Snow-Covered Swamp", "Snow-Covered Mountain",
                    "Snow-Covered Forest"]


def sisay_state(lands=None, library=None, bridge=True, turn=6):
    s = std_state(turn=turn, library=library if library is not None else [FILLER] * 30)
    s.battlefield += list(lands if lands is not None else FIVE_COLOR_LANDS)
    if bridge:
        s.battlefield.append(pb.COMMANDER)
        s.bridge_in_play = True
    creature(s, SISAY, cast_turn=1)
    return s


def test_sisay_power_is_2_plus_colors_among_OTHER_legendary_permanents():
    s = std_state()
    creature(s, SISAY, cast_turn=1)
    assert pb._pt(s, (SISAY, None))[:2] == (2, 2)  # sozinha: 2/2
    s.battlefield.append("Arena Rector")  # criatura branca NAO lendaria: nao conta
    assert pb._sisay_bonus(s) == 0
    pw(s, "Teferi, Hero of Dominaria", 4)  # lendaria branca e azul
    assert pb._pt(s, (SISAY, None))[:2] == (4, 4)
    pw(s, "Elspeth, Sun's Champion", 4)  # branca de novo: a cor nao conta 2x
    assert pb._pt(s, (SISAY, None))[:2] == (4, 4)
    s.battlefield.append(pb.COMMANDER)  # The Prismatic Bridge: "Legendary Enchantment" de 5 cores
    assert pb._pt(s, (SISAY, None))[:2] == (7, 7)
    s.creature_counters[SISAY] = 1  # marcador +1/+1 soma por cima
    assert pb._pt(s, (SISAY, None))[:2] == (8, 8)
    s.phased_out = {"Teferi, Hero of Dominaria", "Elspeth, Sun's Champion"}
    s.battlefield.remove(pb.COMMANDER)
    assert pb._sisay_bonus(s) == 0  # fora de fase nao existe


def test_sisay_search_limited_by_power_legendary_permanent_and_not_already_controlled():
    lib = ["Kaya, Intangible Slayer", "Ugin, the Spirit Dragon", "Elspeth, Sun's Champion", "Doubling Season",
           "Counterspell", "Oko, the Ringleader", "Narset, Parter of Veils", "Carth the Lion", "Teferi, Hero of Dominaria"]
    s = sisay_state(library=lib)  # com a Bridge: 7/7 -> MV < 7
    t = pb.sisay_targets(s)
    assert "Elspeth, Sun's Champion" in t and "Teferi, Hero of Dominaria" in t and "Carth the Lion" in t
    assert "Kaya, Intangible Slayer" not in t and "Ugin, the Spirit Dragon" not in t  # MV 7 e 8
    assert "Doubling Season" not in t and "Counterspell" not in t  # nao lendarias
    pw(s, "Narset, Parter of Veils", 5)  # ja' controlo: regra da lenda
    assert "Narset, Parter of Veils" not in pb.sisay_targets(s)
    s = sisay_state(library=lib, bridge=False)  # sem a Bridge e sem outras lendarias: 2/2 -> MV < 2
    assert pb.sisay_targets(s) == []
    pw(s, "Teferi, Time Raveler", 4)  # W+U -> 4/4 -> MV < 4
    t = pb.sisay_targets(s)
    assert "Narset, Parter of Veils" in t and "Oko, the Ringleader" not in t and "Carth the Lion" not in t


def test_sisay_activation_costs_five_mana_of_all_colors_and_fetched_pw_activates_same_turn():
    s = sisay_state(library=["Liliana, Dreadhorde General"] + [FILLER] * 12)
    pb.main_phase(s, [])
    assert "Liliana, Dreadhorde General" in s.battlefield and "Liliana, Dreadhorde General" not in s.library
    assert s.mana_spent_this_turn == 5 and s.cand_stats["sisay_activations"] == 1
    assert s.loyalty["Liliana, Dreadhorde General"] == 7 and "Zombie Token" in s.battlefield  # entrou com 6 e ja' ativou (+1)
    assert s.cand_stats["sisay_power_sum"] == 7
    # sem as 5 cores nao ativa, por mais mana que haja
    s = sisay_state(lands=["Snow-Covered Forest"] * 7, library=["Liliana, Dreadhorde General"] + [FILLER] * 12)
    pb.main_phase(s, [])
    assert "Liliana, Dreadhorde General" not in s.battlefield
    # sem mana suficiente (4) tambem nao
    s = sisay_state(lands=FIVE_COLOR_LANDS[:4], library=["Liliana, Dreadhorde General"] + [FILLER] * 12)
    assert pb.sisay_activate(s, [], 0, 0) == 0


def test_sisay_fetch_enters_with_doubling_season_etbs_and_shuffles_before_them():
    s = sisay_state(library=["Vraska, Betrayal's Sting"] + [FILLER] * 12)
    s.battlefield.append("Doubling Season")
    pb.sisay_activate(s, [], 0, 0)
    assert s.loyalty["Vraska, Betrayal's Sting"] == 12  # 6 x2 (Doubling Season)
    s = sisay_state(library=["Oath of Teferi"] + [FILLER] * 12)
    pw(s, "Kaya, Intangible Slayer", 6)
    pw(s, "Elspeth, Sun's Champion", 4)
    pb.sisay_activate(s, [], 0, 0)
    assert "Oath of Teferi" in s.battlefield and s.oath_etbs_total == 1  # o ETB da Oath dispara
    # Carth: o ETB ("look at the top seven") resolve DEPOIS da busca e do "then shuffle": com a biblioteca cheia de PWs
    # o topo tem PW de qualquer jeito, entao o gatilho acha um (e a Carth so' entra se a Sisay a buscou)
    lib = ["Carth the Lion"] + ["Ashiok, Dream Render"] * 12
    s = sisay_state(library=lib)
    pb.sisay_activate(s, [], 0, 0)
    assert "Carth the Lion" in s.battlefield or "Ashiok, Dream Render" in s.battlefield
    s = sisay_state(library=["Carth the Lion"] + ["Ashiok, Dream Render"] * 12, lands=FIVE_COLOR_LANDS)
    pw(s, "Ashiok, Dream Render", 5)  # Ashiok ja' em campo: so' a Carth e' alvo valido
    pb.sisay_activate(s, [], 0, 0)
    assert "Carth the Lion" in s.battlefield and s.carth_tutors_total == 1 and s.cand_stats["sisay_fetches"] == 1


def test_sisay_pick_policy_pw_first_then_oath_with_two_pws_then_engine_pieces():
    s = sisay_state(library=["Oath of Teferi", "Elspeth, Sun's Champion", "Liliana, Dreadhorde General", "Carth the Lion"] + [FILLER] * 5)
    assert pb._sisay_pick(s, pb.sisay_targets(s)) in ("Elspeth, Sun's Champion", "Liliana, Dreadhorde General")  # sem PW: o melhor PW
    pw(s, "Kaya, Intangible Slayer", 6)
    assert pb._sisay_pick(s, pb.sisay_targets(s)) in ("Elspeth, Sun's Champion", "Liliana, Dreadhorde General")  # 1 PW: ainda PW
    pw(s, "Narset, Parter of Veils", 5)
    assert pb._sisay_pick(s, pb.sisay_targets(s)) == "Oath of Teferi"  # 2+ PWs: a Oath (ativa 2x)
    s = sisay_state(library=["The Chain Veil", "Vorinclex, Monstrous Raider", "Carth the Lion"] + [FILLER] * 5)
    assert pb._sisay_pick(s, pb.sisay_targets(s)) == "The Chain Veil"  # sem PW na biblioteca: peca de motor
    assert pb._sisay_pick(s, []) is None


def test_sisay_dynamo_copies_the_activation_for_one_more_search():
    s = sisay_state(lands=FIVE_COLOR_LANDS + [FILLER], library=["Liliana, Dreadhorde General", "Elspeth, Sun's Champion"] + [FILLER] * 12)
    creature(s, "The Peregrine Dynamo", cast_turn=1)
    assert pb.sisay_activate(s, [], 0, 0) == 1
    assert "Liliana, Dreadhorde General" in s.battlefield and "Elspeth, Sun's Champion" in s.battlefield
    assert s.mana_spent_this_turn == 6 and s.dynamo_copies_total == 1 and s.cand_stats["sisay_dynamo_copies"] == 1


def test_sisay_respects_reserve_min_mv_phase_out_and_policy_key():
    s = sisay_state(lands=FIVE_COLOR_LANDS + [FILLER] * 2, library=["Aminatou, the Fateshifter"] + [FILLER] * 12)
    assert pb.sisay_activate(s, [], 3, 0) == 0  # 7 de mana - 3 reservados < 5
    assert pb.sisay_activate(s, [], 0, 6) == 0  # o alvo (MV 3) e' menor que o minimo pedido antes da mao
    s.phased_out = {SISAY}
    assert pb.sisay_activate(s, [], 0, 0) == 0  # fora de fase nao ativa
    s.phased_out = set()
    pb.CAND_POLICY["sisay_activate"] = False
    try:
        assert pb.sisay_activate(s, [], 0, 0) == 0
    finally:
        pb.CAND_POLICY["sisay_activate"] = True
    assert pb.sisay_activate(s, [], 0, 0) == 1


def test_sisay_never_attacks_and_counts_as_bridge_target_and_legendary_spell():
    s = res_state()
    creature(s, SISAY, cast_turn=1)
    s.battlefield.append(pb.COMMANDER)
    s.opp_boards[0] = [opp(1)]
    pb.our_combat_step(s, [])
    assert s.our_combat_damage_proxy_total == 0  # peca de motor: nao ataca
    s = std_state(library=[SISAY] + [FILLER] * 10)
    pb.bridge_upkeep_trigger(s, [])  # criatura: a Bridge acerta e ela entra doente
    assert SISAY in s.battlefield and s.creature_cast_turn[SISAY] == s.turn and s.cand_stats["entered_" + SISAY] == 1
    assert SISAY in pb.LEGENDARY_CARD_NAMES  # Delighted Halfling / Plaza pagam a Sisay


def test_sisay_search_goes_before_the_hand_by_default_and_after_it_with_the_old_policy_key():
    def run():
        s = sisay_state(lands=FIVE_COLOR_LANDS, library=["Teferi, Time Raveler"] + [FILLER] * 12)
        s.hand = ["Farseek"]  # 2 de mana: com os 5 terrenos so' dá pra Farseek OU pra busca
        pb.main_phase(s, [])
        return s
    s = run()
    assert "Teferi, Time Raveler" in s.battlefield and "Farseek" in s.hand  # busca primeiro (alvo de MV 3)
    pb.CAND_POLICY["sisay_pre_hand_all"] = False
    try:
        s = run()
    finally:
        pb.CAND_POLICY["sisay_pre_hand_all"] = True
    assert "Teferi, Time Raveler" not in s.battlefield and "Farseek" not in s.hand  # politica antiga: mao primeiro


def test_liliana_minus4_spares_sisay_and_is_skipped_when_it_would_force_her_sacrifice():
    def base():
        s = fresh()
        s.battlefield += list(FIVE_COLOR_LANDS)
        pw(s, "Liliana, Dreadhorde General", 6)
        s.opp_boards[0] = [opp(3), opp(3), opp(3), opp(3)]  # 4 ameacas: o -4 e' considerado
        creature(s, SISAY, cast_turn=1)
        return s
    # so' a Sisay de criatura minha: o -4 me obrigaria a sacrificar ela -> fica o +1 (None = sem modo de controle)
    s = base()
    assert pb._defensive_choice(s, "Liliana, Dreadhorde General", 6) is None
    pb.CAND_POLICY["liliana_spares_sisay"] = False
    try:
        assert pb._defensive_choice(base(), "Liliana, Dreadhorde General", 6) == ("Liliana, Dreadhorde General", "-4", None)
    finally:
        pb.CAND_POLICY["liliana_spares_sisay"] = True
    # com 3 criaturas o -4 vale, e o sacrificio recai nas 2 mais fracas (fichas), nunca na Sisay
    s = base()
    token(s, "Zombie Token", 2)
    creature(s, "Bloom Tender", cast_turn=1)
    assert pb._defensive_choice(s, "Liliana, Dreadhorde General", 6) == ("Liliana, Dreadhorde General", "-4", None)
    pb._eff_liliana_minus4(s, "Liliana, Dreadhorde General", [], None)
    assert SISAY in s.battlefield and "Bloom Tender" in s.battlefield and s.battlefield.count("Zombie Token") == 0
    # sem a Sisay em campo nada muda (base bit-identica): o -4 continua escolhido com 1 criatura minha
    s = fresh()
    pw(s, "Liliana, Dreadhorde General", 6)
    s.opp_boards[0] = [opp(3), opp(3), opp(3), opp(3)]
    creature(s, "Arena Rector", cast_turn=1)
    assert pb._defensive_choice(s, "Liliana, Dreadhorde General", 6) == ("Liliana, Dreadhorde General", "-4", None)


def test_arena_rector_outlet_damn_or_void_rend_on_own_arena_rector_fetches_the_top_mv_planeswalker():
    def base(hand):
        s = std_state(turn=6, library=["Ugin, the Spirit Dragon", "Kaya, Intangible Slayer"] + [FILLER] * 12)
        s.battlefield += list(FIVE_COLOR_LANDS) + ["Snow-Covered Swamp"]  # Damn e' {B}{B}: 2 fontes pretas distintas
        creature(s, "Arena Rector", cast_turn=1)
        s.hand = list(hand)
        return s
    # padrao: linha desligada, nada acontece
    s = base(["Damn"])
    assert pb.try_arena_rector_outlet(s, [], 0) == 0 and "Arena Rector" in s.battlefield
    pb.CAND_POLICY["arena_rector_outlet"] = True
    try:
        s = base(["Damn"])
        assert pb.try_arena_rector_outlet(s, [], 0) == 1
        assert "Ugin, the Spirit Dragon" in s.battlefield and "Arena Rector" not in s.battlefield  # PW de maior MV
        assert "Arena Rector" not in s.graveyard  # "you may exile it"
        assert "Damn" in s.graveyard and "Damn" not in s.hand
        # sem Damn, Void Rend serve ({W}{U}{B}); sem nenhum dos dois, nada
        s = base(["Void Rend"])
        assert pb.try_arena_rector_outlet(s, [], 0) == 1 and "Ugin, the Spirit Dragon" in s.battlefield
        s = base(["Farseek"])
        assert pb.try_arena_rector_outlet(s, [], 0) == 0 and "Arena Rector" in s.battlefield
        # sem PW na biblioteca o gatilho nao tem o que buscar: nao gasta a carta
        s = base(["Damn"])
        s.library = [FILLER] * 10
        assert pb.try_arena_rector_outlet(s, [], 0) == 0 and "Damn" in s.hand
        # sem mana (reserva) nao conjura
        s = base(["Damn"])
        assert pb.try_arena_rector_outlet(s, [], 5) == 0  # 6 de mana - 5 reservados < 2
        # a linha entra no main_phase (antes da mao por padrao) e o PW buscado ativa no mesmo turno
        s = base(["Damn"])
        s.battlefield.append(pb.COMMANDER)  # Bridge ja' em campo: nao gasta a mana do turno conjurando ela
        s.bridge_in_play = True
        pb.main_phase(s, [])
        assert "Ugin, the Spirit Dragon" in s.battlefield and s.cand_stats.get("arena_rector_outlet_Damn") == 1
    finally:
        pb.CAND_POLICY["arena_rector_outlet"] = False


def test_sisay_round_end_window_uses_leftover_mana_at_the_opponents_end_step():
    def base(target="Teferi, Time Raveler", held=5):
        s = sisay_state(library=[target] + [FILLER] * 12)
        s.mana_held_back = held
        return s
    # padrao: janela desligada
    s = base()
    assert pb.try_sisay_round_end(s, []) == 0 and "Teferi, Time Raveler" not in s.battlefield
    pb.CAND_POLICY["sisay_round_end"] = True
    try:
        s = base()
        assert pb.try_sisay_round_end(s, []) == 1
        assert "Teferi, Time Raveler" in s.battlefield and s.mana_held_back == 0
        assert s.cand_stats.get("sisay_round_end_activations") == 1
        # sem 5 de mana sobrando nao busca
        s = base(held=4)
        assert pb.try_sisay_round_end(s, []) == 0
        # criatura buscada entra no end step do oponente: sem doenca de invocacao no meu turno seguinte
        s = base(target="Atraxa, Praetors' Voice")
        assert pb.try_sisay_round_end(s, []) == 1
        assert s.creature_cast_turn["Atraxa, Praetors' Voice"] == s.turn - 1
        # Peregrine Dynamo copia por {1}: segunda busca na mesma janela
        s = base(held=6)
        s.library = ["Teferi, Time Raveler", "Aminatou, the Fateshifter"] + [FILLER] * 12
        creature(s, "The Peregrine Dynamo", cast_turn=1)
        assert pb.try_sisay_round_end(s, []) == 1
        assert s.cand_stats.get("sisay_fetches") == 2 and s.mana_held_back == 0
        # a janela roda no topo do play_turn (fim de rodada) e o resto do turno segue normal
        s = base()
        pb.play_turn(s, s.turn + 1, [])
        assert s.cand_stats.get("sisay_round_end_activations", 0) >= 1
    finally:
        pb.CAND_POLICY["sisay_round_end"] = False


def test_sisay_runs_full_games_without_exceptions():
    for slot in ("Arena Rector", "Swan Song", "Doubling Season"):
        for seed in range(10):
            r = pb.simulate_one(3_000_000 + seed, 10, False, swap=[(slot, SISAY)])
            assert isinstance(r["cand_stats"], dict)
            for prof in ("mixed", "go_wide", "voltron", "low"):
                pb.simulate_one_with_interaction(6_000_000 + seed, turns=10, attack_profile=prof, swap=[(slot, SISAY)])
    sw = [("Arena Rector", SISAY), ("Swan Song", DIHADA), ("Veil of Summer", GUFF), ("Oath of Nissa", SARKHAN)]
    for seed in range(10):
        pb.simulate_one(3_000_000 + seed, 10, False, swap=sw)
        pb.simulate_one_with_interaction(6_000_000 + seed, turns=10, swap=sw)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Payoff de landfall antes do terreno (2026-10-07, LANDFALL_PAYOFF_FIRST)
# ---------------------------------------------------------------------------

def _com_chave(valor, f):
    antigo = pb.LANDFALL_PAYOFF_FIRST
    pb.LANDFALL_PAYOFF_FIRST = valor
    try:
        return f()
    finally:
        pb.LANDFALL_PAYOFF_FIRST = antigo


def _turno_de_terreno(s):
    """O trecho de `play_turn` entre a compra e a fase principal: payoff primeiro (se ligado), `play_land`."""
    s.land_played = False
    s.mana_spent_this_turn = 0
    s.tapped_lands_this_turn = set()
    pb.cast_landfall_payoffs_first(s, [])
    pb.play_land(s, [])
    return s


def _cena_sage(hand, lands=3, bridge=True, land=FILLER):
    s = fresh(turn=5, hand=hand)
    s.interaction_rng = None
    s.bridge_in_play = bridge
    s.battlefield += [land] * lands
    pw(s, "Elspeth, Sun's Champion", 3)
    return s


def test_payoff_primeiro_evolution_sage_antes_do_terreno_prolifera_o_planeswalker():
    def rodar():
        return _turno_de_terreno(_cena_sage(["Evolution Sage", FILLER]))
    s = _com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and "Evolution Sage" in s.battlefield
    assert s.evolution_sage_proliferates == 1                       # o terreno do turno disparou o landfall da Sage
    assert s.loyalty["Elspeth, Sun's Champion"] == 5                # 3 + 1 (+1 da Elspeth ativando ao fim do cast, CR 606.3) + 1 (proliferate)
    s0 = _com_chave(False, rodar)   # ordem antiga: o terreno entra primeiro, a Sage so' e' conjurada depois (na fase principal)
    assert s0.payoff_first_casts == 0 and "Evolution Sage" not in s0.battlefield and s0.evolution_sage_proliferates == 0


def test_payoff_primeiro_nao_desloca_a_bridge():
    def rodar():
        s = _cena_sage(["Evolution Sage", FILLER], lands=4, bridge=False, land="Command Tower")
        return _turno_de_terreno(s)
    s = _com_chave(True, rodar)    # Bridge (5) cabe com o terreno do turno (4 + 1); a Sage (3) a impediria
    assert s.payoff_first_casts == 0 and "Evolution Sage" not in s.battlefield
    sem_cores = _com_chave(True, lambda: _turno_de_terreno(_cena_sage(["Evolution Sage", FILLER], lands=4, bridge=False)))
    assert sem_cores.payoff_first_casts == 1   # 4 Snow-Covered Forest nao pagam as 5 cores da Bridge nem com o terreno: nada a proteger, a Sage sai antes


def test_payoff_primeiro_nao_dispara_sem_terreno_nem_com_terreno_ja_jogado():
    s = _com_chave(True, lambda: _turno_de_terreno(_cena_sage(["Evolution Sage"])))
    assert s.payoff_first_casts == 0
    s2 = _cena_sage(["Evolution Sage", FILLER])
    s2.land_played = True
    _com_chave(True, lambda: pb.cast_landfall_payoffs_first(s2, []))
    assert s2.payoff_first_casts == 0 and "Evolution Sage" in s2.hand


def test_payoff_primeiro_respeita_a_mana_de_agora():
    s = _com_chave(True, lambda: _turno_de_terreno(_cena_sage(["Evolution Sage", FILLER], lands=2)))
    assert s.payoff_first_casts == 0   # 2 de mana nao paga a Sage (3): o terreno vem primeiro como antes


def test_main_phase_extraido_continua_conjurando_o_resto_da_mao():
    s = _cena_sage(["Evolution Sage"], lands=3)
    _com_chave(False, lambda: pb.main_phase(s, []))
    assert "Evolution Sage" in s.battlefield and s.mana_spent_this_turn == 3   # o loop generico usa `_cast_hand_spell`


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

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

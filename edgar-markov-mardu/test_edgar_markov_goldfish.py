"""
Testes dirigidos do simulador do Edgar Markov (CLAUDE.md, Regra #1: cada
correcao tem que DISPARAR de verdade). Rodada 2026-09-25: planeswalker ativa
no turno em que entra (CR 606.3), Sorin +1 so' sacrifica Vampiro, remocao de
oponente num PW passa pela cascata de morte (Cruel Celebrant).

Rodar: python3 test_edgar_markov_goldfish.py   (sem pytest -- executor proprio no fim)
"""
import random
import traceback

import edgar_markov_goldfish_v1 as em

FILLER = "Swamp"


def fresh(turn: int = 5, library=None, hand=None) -> em.GameState:
    s = em.GameState(rng=random.Random(0), library=list(library) if library is not None else [FILLER] * 30)
    s.turn = turn
    s.hand = list(hand or [])
    return s


def test_sorin_cast_from_hand_activates_same_turn():
    # Sorin {2}{B}, lealdade 4. Sem ficha de Vampiro e sem Vampiro na mao:
    # +1 (contador). Antes da correcao ficava em 4 ate' o turno seguinte.
    s = fresh(hand=["Sorin, Imperious Bloodlord"])
    s.battlefield += ["Swamp", "Swamp", "Swamp"]
    s.land_played = True
    em.cast_available_spells(s, [])
    assert "Sorin, Imperious Bloodlord" in s.battlefield
    assert s.loyalty["Sorin, Imperious Bloodlord"] == 5
    assert s.pw_activations_total == 1 and s.late_pw_activations_total == 1


def test_planeswalker_activates_only_once_per_turn():
    s = fresh(hand=["Sorin, Imperious Bloodlord"])
    s.battlefield += ["Swamp", "Swamp", "Swamp"]
    s.land_played = True
    em.cast_available_spells(s, [])
    em.cast_available_spells(s, [])        # 2a passada (depois do sac_loop)
    em.activate_unactivated_planeswalkers(s, [])
    assert s.pw_activations_total == 1


def test_planeswalker_already_in_play_not_activated_twice():
    s = fresh()
    s.battlefield += ["Swamp", "Sorin, Imperious Bloodlord"]
    s.loyalty["Sorin, Imperious Bloodlord"] = 4
    em.activate_planeswalkers(s, [])
    em.cast_available_spells(s, [])
    assert s.pw_activations_total == 1


def test_play_turn_resets_activation_each_turn():
    s = fresh(turn=0)
    s.battlefield += ["Swamp", "Sorin, Imperious Bloodlord"]
    s.loyalty["Sorin, Imperious Bloodlord"] = 4
    em.play_turn(s, 1, [])
    em.play_turn(s, 2, [])
    assert s.pw_activations_total == 2


def test_sorin_plus1_sacrifices_only_vampires():
    # "You may sacrifice a Vampire." -- Human Soldier/Snake nao servem.
    s = fresh()
    s.battlefield += ["Sorin, Imperious Bloodlord", "Human Soldier Token", "Snake Token"]
    s.tokens = ["Human Soldier Token", "Snake Token"]
    s.loyalty["Sorin, Imperious Bloodlord"] = 2
    em.resolve_planeswalker(s, "Sorin, Imperious Bloodlord", [])
    assert s.tokens == ["Human Soldier Token", "Snake Token"] and s.sorin_vampire_sacs_total == 0
    assert s.drain_total == 0
    s = fresh()
    s.battlefield += ["Sorin, Imperious Bloodlord", "Vampire Token", "Human Soldier Token"]
    s.tokens = ["Vampire Token", "Human Soldier Token"]
    s.loyalty["Sorin, Imperious Bloodlord"] = 2
    em.resolve_planeswalker(s, "Sorin, Imperious Bloodlord", [])
    assert s.tokens == ["Human Soldier Token"] and s.sorin_vampire_sacs_total == 1
    assert s.drain_total == 3 and s.loyalty["Sorin, Imperious Bloodlord"] == 3


def test_opponent_removal_of_sorin_is_a_planeswalker_death():
    # Cruel Celebrant: "Whenever this creature or another creature or
    # planeswalker you control dies, each opponent loses 1 life and you gain 1 life."
    s = fresh()
    s.battlefield += ["Sorin, Imperious Bloodlord", "Cruel Celebrant"]
    s.loyalty["Sorin, Imperious Bloodlord"] = 5
    em.remove_permanent(s, [], "Sorin, Imperious Bloodlord", source="opponent_removal")
    assert "Sorin, Imperious Bloodlord" not in s.battlefield
    assert "Sorin, Imperious Bloodlord" in s.graveyard
    assert "Sorin, Imperious Bloodlord" not in s.loyalty
    assert s.pw_deaths_total == 1 and s.death_trigger_events == 1


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

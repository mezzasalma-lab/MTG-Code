"""Testes dirigidos do simulador do Beorn (CLAUDE.md, Regra #1: cada correcao tem que DISPARAR de verdade).
Rodada 2026-10-07: payoff de landfall antes do terreno (LANDFALL_PAYOFF_FIRST).
Rodar (de dentro de beorn-fierce/): python3 test_beorn_goldfish.py   (sem pytest -- executor proprio no fim)"""
import random
import traceback

import beorn_goldfish_v1 as bg


def fresh(turn=5, hand=None, battlefield=None, library=None):
    s = bg.GameState(rng=random.Random(0), library=list(library) if library is not None else ["Forest"] * 40)
    s.turn = turn
    s.hand = list(hand or [])
    s.battlefield = list(battlefield or [])
    return s


def com_chave(valor, f):
    antigo = bg.LANDFALL_PAYOFF_FIRST
    bg.LANDFALL_PAYOFF_FIRST = valor
    try:
        return f()
    finally:
        bg.LANDFALL_PAYOFF_FIRST = antigo


def turno(s):
    s.land_played = False
    s.tapped_lands_this_turn = set()
    s.mana_spent_this_turn = 0
    s.bonus_mana_this_turn = 0
    s.tapped_basics_this_turn = 0
    log = []
    bg.cast_landfall_payoffs_first(s, log)
    bg.play_land(s, log)
    bg.main_phase(s, log)
    return s


def test_payoff_primeiro_cobra_antes_do_terreno_da_a_mana_do_landfall():
    def rodar():
        return turno(fresh(turn=2, hand=["Lotus Cobra", "Forest"], battlefield=["Forest", "Forest"]))
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and "Lotus Cobra" in s.battlefield
    assert s.bonus_mana_this_turn == 1            # o terreno do turno disparou o landfall do Cobra
    s0 = com_chave(False, rodar)                  # ordem antiga: terreno primeiro, o Cobra entra depois dele
    assert s0.payoff_first_casts == 0 and "Lotus Cobra" in s0.battlefield and s0.bonus_mana_this_turn == 0


def test_payoff_primeiro_tracker_antes_do_terreno_investiga():
    def rodar():
        return turno(fresh(turn=2, hand=["Tireless Tracker", "Forest"], battlefield=["Forest", "Forest", "Forest"]))
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and "Tireless Tracker" in s.battlefield and s.clues == 1
    s0 = com_chave(False, rodar)
    assert "Tireless Tracker" in s0.battlefield and s0.clues == 0


def test_payoff_primeiro_nao_desloca_o_comandante():
    def rodar():
        return turno(fresh(turn=5, hand=["Lotus Cobra", "Forest"], battlefield=["Forest"] * 4))
    s = com_chave(True, rodar)   # Beorn (5) cabe com o terreno do turno (4 + 1); o Cobra (2) o impediria
    assert s.commander_in_play and s.payoff_first_casts == 0


def test_payoff_primeiro_conta_o_mana_de_landfall_que_ja_esta_em_campo_para_nao_atrasar_o_comandante():
    def rodar():
        # 2 terrenos + Lotus Cobra (mana de dork) em campo = 3 de mana agora; o terreno do turno (+1) e o landfall do Cobra (+1) pagam a Beorn (5); o Provisioner (3) antes do terreno a impediria
        return turno(fresh(turn=3, hand=["Tireless Provisioner", "Forest"], battlefield=["Forest"] * 2 + ["Lotus Cobra"], library=["Forest"] * 40))
    s = com_chave(True, rodar)
    assert s.commander_in_play and s.payoff_first_casts == 0     # a formula antiga (mana de agora + 1 = 4 < 5) deixava o Provisioner passar e atrasava a Beorn
    s0 = com_chave(False, rodar)
    assert s0.commander_in_play


def test_payoff_primeiro_nao_tira_a_rocha_de_mana_que_a_ordem_antiga_conjuraria():
    def rodar():
        # 1 terreno + Llanowar = 2 de mana agora; com o terreno do turno 3 paga a Firdoch Core (3, rocha de mana, prioridade maior); a Hospitality (2) antes do terreno a deixaria de fora
        return turno(fresh(turn=2, hand=["Beorn's Hospitality", "Firdoch Core", "Forest"], battlefield=["Forest", "Llanowar Elves"]))
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 0 and "Firdoch Core" in s.battlefield and "Beorn's Hospitality" in s.hand
    assert "Firdoch Core" in com_chave(False, rodar).battlefield


def test_payoff_primeiro_nao_dispara_sem_terreno_nem_com_terreno_ja_jogado():
    s = com_chave(True, lambda: turno(fresh(turn=2, hand=["Lotus Cobra"], battlefield=["Forest", "Forest"])))
    assert s.payoff_first_casts == 0 and "Lotus Cobra" in s.battlefield     # a fase principal conjura do mesmo jeito
    s2 = fresh(turn=2, hand=["Lotus Cobra", "Forest"], battlefield=["Forest", "Forest"])
    s2.land_played = True
    com_chave(True, lambda: bg.cast_landfall_payoffs_first(s2, []))
    assert s2.payoff_first_casts == 0 and "Lotus Cobra" in s2.hand


def test_payoff_primeiro_em_play_turn_completo():
    def rodar():
        s = fresh(turn=0, hand=["Lotus Cobra", "Forest"], battlefield=["Forest", "Forest"])
        bg.play_turn(s, 2, [])
        return s
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and s.bonus_mana_this_turn >= 1
    assert com_chave(False, rodar).bonus_mana_this_turn == 0


def test_simulate_one_deterministico():
    a = bg.simulate_one(9_123_456)
    b = bg.simulate_one(9_123_456)
    assert a == b


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

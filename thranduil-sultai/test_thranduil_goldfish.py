"""Testes dirigidos do simulador do Thranduil (CLAUDE.md, Regra #1: cada correcao tem que DISPARAR de verdade).
Rodada 2026-10-07: payoff de landfall antes do terreno (LANDFALL_PAYOFF_FIRST).
Rodar (de dentro de thranduil-sultai/): python3 test_thranduil_goldfish.py   (sem pytest -- executor proprio no fim)"""
import random
import traceback

import thranduil_goldfish_v1 as tg

SINDARIN = "Thranduil, Sindarin Liege // Silvan Rally"


def fresh(turn=5, hand=None, battlefield=None, commander_em_campo=True):
    s = tg.GameState(rng=random.Random(0), library=["Forest"] * 40)
    s.turn = turn
    s.hand = list(hand or [])
    s.battlefield = list(battlefield or [])
    if commander_em_campo:
        s.battlefield.append(tg.COMMANDER)
        s.commander_in_play = True
    return s


def com_chave(valor, f):
    antigo = tg.LANDFALL_PAYOFF_FIRST
    tg.LANDFALL_PAYOFF_FIRST = valor
    try:
        return f()
    finally:
        tg.LANDFALL_PAYOFF_FIRST = antigo


def terrenos_do_turno(s):
    """O trecho de `play_turn` entre o compra e a fase principal: payoff primeiro (se ligado), 2 chamadas de `play_land`, fase principal."""
    s.land_played = False
    s.lands_played_this_turn = 0
    s.tapped_lands_this_turn = set()
    s.mana_spent_this_turn = 0
    log = []
    tg.cast_landfall_payoffs_first(s, log)
    tg.play_land(s, log)
    tg.play_land(s, log)
    tg.main_phase(s, log)
    return s


LANDS4 = ["Forest", "Forest", "Island", "Forest"]


def test_company_antes_dos_terrenos_libera_o_segundo_land_drop_e_dispara_o_landfall():
    def rodar():
        return terrenos_do_turno(fresh(hand=["Thranduil's Company", "Forest", "Forest"], battlefield=LANDS4 + ["Llanowar Elves"]))
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and "Thranduil's Company" in s.battlefield
    assert s.lands_played_this_turn == 2           # a Company concede o 2o land drop
    assert s.thranduils_company_counters == 4      # 2 contadores por terreno, nos dois terrenos
    s0 = com_chave(False, rodar)                   # ordem antiga: 1 terreno, a Company entra depois e o 2o land drop nunca e' usado
    assert s0.payoff_first_casts == 0 and "Thranduil's Company" in s0.battlefield
    assert s0.lands_played_this_turn == 1 and s0.thranduils_company_counters == 0


def test_sindarin_liege_antes_do_terreno_cria_o_token_do_landfall():
    def rodar():
        return terrenos_do_turno(fresh(hand=["Thranduil, Sindarin Liege // Silvan Rally", "Forest"], battlefield=LANDS4))
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and s.landfall_elf_tokens == 1
    s0 = com_chave(False, rodar)
    assert s0.payoff_first_casts == 0 and s0.landfall_elf_tokens == 0


def test_payoff_primeiro_nao_desloca_o_comandante():
    def rodar():
        return terrenos_do_turno(fresh(hand=["Thranduil, Sindarin Liege // Silvan Rally", "Forest"], battlefield=["Forest", "Island", "Swamp", "Forest"], commander_em_campo=False))
    s = com_chave(True, rodar)    # comandante (5) cabe com o terreno do turno (4 + 1); o payoff (4) o impediria
    assert s.commander_in_play and s.payoff_first_casts == 0


def test_payoff_primeiro_conta_o_segundo_land_drop_da_company_para_nao_atrasar_o_comandante():
    def rodar():
        # Company + Elfo em campo (2 land drops), comandante com imposto (7): 4 terrenos + Llanowar (5) + 2 terrenos = 7 paga; o payoff (4) antes dos terrenos deixaria 1 + 2 = 3
        s = fresh(hand=[SINDARIN, "Forest", "Forest"], battlefield=["Forest", "Island", "Swamp", "Forest", "Llanowar Elves", "Thranduil's Company"], commander_em_campo=False)
        s.commander_cast_count = 1
        return terrenos_do_turno(s)
    s = com_chave(True, rodar)
    assert s.commander_in_play and s.payoff_first_casts == 0     # a formula antiga (mana de agora + 1 = 6 < 7) deixava o payoff passar e atrasava o comandante
    assert com_chave(False, rodar).commander_in_play


def test_payoff_primeiro_nao_dispara_sem_terreno_na_mao_nem_com_terreno_ja_jogado():
    s = com_chave(True, lambda: terrenos_do_turno(fresh(hand=["Thranduil, Sindarin Liege // Silvan Rally"], battlefield=LANDS4)))
    assert s.payoff_first_casts == 0 and "Thranduil, Sindarin Liege // Silvan Rally" in s.battlefield   # a fase principal conjura do mesmo jeito
    s2 = fresh(hand=["Thranduil, Sindarin Liege // Silvan Rally", "Forest"], battlefield=LANDS4)
    s2.lands_played_this_turn = 1
    com_chave(True, lambda: tg.cast_landfall_payoffs_first(s2, []))
    assert s2.payoff_first_casts == 0 and "Thranduil, Sindarin Liege // Silvan Rally" in s2.hand


def test_payoff_primeiro_em_play_turn_completo():
    def rodar():
        s = fresh(turn=0, hand=["Thranduil, Sindarin Liege // Silvan Rally", "Forest"], battlefield=LANDS4)
        tg.play_turn(s, 5, [])
        return s
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and s.landfall_elf_tokens >= 1
    assert com_chave(False, rodar).landfall_elf_tokens == 0


def test_simulate_one_deterministico():
    a = tg.simulate_one(9_123_456)
    b = tg.simulate_one(9_123_456)
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

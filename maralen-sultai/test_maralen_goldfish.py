"""Testes dirigidos do simulador da Maralen (CLAUDE.md, Regra #1: cada correcao tem que DISPARAR de verdade).
Rodada 2026-10-07: payoff de landfall antes do terreno (LANDFALL_PAYOFF_FIRST).
Rodar (de dentro de maralen-sultai/): python3 test_maralen_goldfish.py   (sem pytest -- executor proprio no fim)"""
import traceback

import maralen_goldfish_v1 as mg

SINDARIN = "Thranduil, Sindarin Liege // Silvan Rally"


def fresh(turn=5, hand=None, battlefield=None, commander_em_campo=True):
    s = mg.GameState(hand=list(hand or []), library=["Forest"] * 40)
    s.turn = turn
    s.battlefield = list(battlefield or [])
    if commander_em_campo:
        s.battlefield.append(mg.COMMANDER)
        s.commander_in_play = True
    return s


def com_chave(valor, f):
    antigo = mg.LANDFALL_PAYOFF_FIRST
    mg.LANDFALL_PAYOFF_FIRST = valor
    try:
        return f()
    finally:
        mg.LANDFALL_PAYOFF_FIRST = antigo


def terrenos_do_turno(s):
    """O trecho de `play_turn` entre o compra e a fase principal: payoff primeiro (se ligado), `play_land`, fase principal."""
    s.lands_played_this_turn = 0
    s.mana_spent_this_turn = 0
    s.tapped_lands_this_turn = set()
    mg.cast_landfall_payoffs_first(s)
    mg.play_land(s)
    mg.main_phase(s, is_first_main=True)
    return s


LANDS4 = ["Forest"] * 4


def test_company_antes_dos_terrenos_libera_o_segundo_land_drop_e_dispara_o_landfall():
    def rodar():
        return terrenos_do_turno(fresh(hand=["Thranduil's Company", "Forest", "Forest"], battlefield=LANDS4 + ["Llanowar Elves"]))
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and "Thranduil's Company" in s.battlefield
    assert s.lands_played_this_turn == 2 and s.landfall_counters_total == 2   # 2o land drop da Company; landfall nos dois terrenos
    s0 = com_chave(False, rodar)       # ordem antiga: 1 terreno; a Company entra depois e o 2o land drop nunca e' usado
    assert s0.payoff_first_casts == 0 and "Thranduil's Company" in s0.battlefield
    assert s0.lands_played_this_turn == 1 and s0.landfall_counters_total == 0


def test_sindarin_liege_antes_do_terreno_cria_o_token_do_landfall():
    def rodar():
        return terrenos_do_turno(fresh(hand=[SINDARIN, "Forest"], battlefield=LANDS4))
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and s.landfall_elf_tokens_total == 1
    s0 = com_chave(False, rodar)
    assert s0.payoff_first_casts == 0 and s0.landfall_elf_tokens_total == 0


def test_payoff_primeiro_nao_desloca_o_comandante():
    def rodar():
        return terrenos_do_turno(fresh(hand=[SINDARIN, "Forest"], battlefield=LANDS4, commander_em_campo=False))
    s = com_chave(True, rodar)    # Maralen (5) cabe com o terreno do turno (4 + 1); o payoff (4) o impediria
    assert s.commander_in_play and s.payoff_first_casts == 0


def test_payoff_primeiro_nao_dispara_sem_terreno_na_mao_nem_com_terreno_ja_jogado():
    s = com_chave(True, lambda: terrenos_do_turno(fresh(hand=[SINDARIN], battlefield=LANDS4)))
    assert s.payoff_first_casts == 0 and SINDARIN in s.battlefield     # a fase principal conjura do mesmo jeito
    s2 = fresh(hand=[SINDARIN, "Forest"], battlefield=LANDS4)
    s2.lands_played_this_turn = 1
    com_chave(True, lambda: mg.cast_landfall_payoffs_first(s2))
    assert s2.payoff_first_casts == 0 and SINDARIN in s2.hand


def test_payoff_primeiro_em_play_turn_completo():
    def rodar():
        s = fresh(turn=4, hand=[SINDARIN, "Forest"], battlefield=LANDS4)
        mg.play_turn(s, is_first_turn=False, on_play=True)
        return s
    s = com_chave(True, rodar)
    assert s.payoff_first_casts == 1 and s.landfall_elf_tokens_total >= 1
    assert com_chave(False, rodar).landfall_elf_tokens_total == 0


def test_simulate_one_deterministico():
    a = mg.simulate_one(9_123_456)
    b = mg.simulate_one(9_123_456)
    assert (a.turn, a.mana_spent_this_turn, a.lands_played_total, len(a.battlefield)) == (b.turn, b.mana_spent_this_turn, b.lands_played_total, len(b.battlefield))


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

"""Testes dirigidos do simulador do Beorn (CLAUDE.md, Regra #1: cada correcao tem que DISPARAR de verdade).
Rodada 2026-10-07: payoff de landfall antes do terreno (LANDFALL_PAYOFF_FIRST).
Rodada 2026-10-23: Ram Through -> Herd Heirloom (HERD_HEIRLOOM_IN_DECK / _MANA / _DRAW) e o gatilho da Beorn no INICIO DO COMBATE (BEORN_TRIGGER_AT_BEGINNING_OF_COMBAT).
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


# ---------------------------------------------------------------------------
# Rodada 2026-10-23: Herd Heirloom ("{T}: Add one mana of any color. Spend this mana only to cast a creature spell." / "{T}: Until end of turn, target creature you control with power
# 4 or greater gains trample and 'Whenever this creature deals combat damage to a player, draw a card.'") e o gatilho da Beorn no inicio do combate.
# ---------------------------------------------------------------------------
import contextlib


@contextlib.contextmanager
def chaves(**kw):
    antigos = {k: getattr(bg, k) for k in kw}
    for k, v in kw.items():
        setattr(bg, k, v)
    try:
        yield
    finally:
        for k, v in antigos.items():
            setattr(bg, k, v)


def veterano(s, *cartas):
    """Marca as criaturas como em campo desde antes deste turno (sem doenca de invocacao)."""
    for c in cartas:
        s.creature_entered_turn[c] = s.turn - 1
    return s


def test_heirloom_mana_paga_magia_de_criatura_que_nao_caberia():
    s = fresh(turn=4, hand=["Eternal Witness"], battlefield=["Forest", "Forest", "Herd Heirloom"])
    assert not bg.can_cast(s, "Eternal Witness")                  # 2 de mana < 3
    bg.arm_heirloom(s)
    assert s.heirloom_mana_armed                                  # sem alvo de compra: o {T} vira mana de criatura
    assert bg.can_cast(s, "Eternal Witness")                      # 2 + 1 restrito = 3, e o G pode vir do Heirloom (qualquer cor)
    bg.cast_spell(s, "Eternal Witness", [])
    assert "Eternal Witness" in s.battlefield and s.heirloom_mana_uses == 1
    assert s.heirloom_tapped_this_turn and not s.heirloom_mana_armed
    assert bg.remaining_mana(s) == 0                              # custo 3 = 2 do campo + 1 do Heirloom


def test_heirloom_mana_nao_paga_magia_que_nao_e_de_criatura_nem_ativacao():
    s = fresh(turn=4, hand=["Cultivate"], battlefield=["Forest", "Forest", "Herd Heirloom"])
    bg.arm_heirloom(s)
    assert s.heirloom_mana_armed and not bg.can_cast(s, "Cultivate")          # {2}{G}: magia nao-criatura, o mana restrito nao conta
    s2 = fresh(turn=4, battlefield=["Forest", "Forest", "Maskwood Nexus", "Herd Heirloom"])
    bg.arm_heirloom(s2)
    bg.try_maskwood_nexus(s2, [])                                              # {3},{T}: habilidade ativada, 2 de mana livre + 1 restrito nao bastam
    assert s2.mana_spent_this_turn == 0 and "Bear Token" not in s2.battlefield
    assert not s2.heirloom_tapped_this_turn


def test_heirloom_um_unico_tap_por_turno_mana_ou_compra():
    # (a) o mana ja foi gasto: a habilidade 2 nao pode mais ser ativada, mesmo com alvo elegivel
    s = veterano(fresh(turn=5, hand=["Eternal Witness"], battlefield=["Forest"] * 3 + [bg.COMMANDER, "Herd Heirloom"], library=["Forest"] * 30), bg.COMMANDER)
    s.commander_in_play = True
    s.heirloom_mana_armed = True
    bg.cast_spell(s, "Eternal Witness", [])
    assert s.heirloom_tapped_this_turn and s.heirloom_mana_uses == 1
    n = len(s.hand)
    bg.try_heirloom_draw(s, [])
    assert s.heirloom_draw_activations == 0 and len(s.hand) == n
    # (b) a compra ja foi ativada: o mana restrito deixa de existir e a criatura nao cabe
    t = veterano(fresh(turn=5, hand=["Eternal Witness"], battlefield=["Forest", "Forest", bg.COMMANDER, "Herd Heirloom"], library=["Forest"] * 30), bg.COMMANDER)
    t.commander_in_play = True
    bg.arm_heirloom(t)
    assert not t.heirloom_mana_armed                                          # alvo elegivel (Beorn, poder 6): o {T} fica guardado para a compra
    bg.try_heirloom_draw(t, [])
    assert t.heirloom_draw_activations == 1 and t.heirloom_tapped_this_turn
    assert not bg.can_cast(t, "Eternal Witness")                              # 2 de mana < 3, e o Heirloom ja foi virado


def test_heirloom_compra_uma_carta_com_beorn_apta_a_atacar():
    s = veterano(fresh(turn=6, battlefield=[bg.COMMANDER, "Herd Heirloom"], library=["Forest"] * 30), bg.COMMANDER)
    s.commander_in_play = True
    h = len(s.hand)
    bg.combat_step(s, [])
    assert s.heirloom_draw_activations == 1 and s.heirloom_draws == 1 and len(s.hand) == h + 1
    assert s.heirloom_tapped_this_turn


def test_heirloom_exige_poder_4_e_criatura_apta_a_atacar():
    s = veterano(fresh(turn=6, battlefield=["Llanowar Elves", "Herd Heirloom"], library=["Forest"] * 30), "Llanowar Elves")
    bg.combat_step(s, [])
    assert s.heirloom_draw_activations == 0                                   # Llanowar tem poder 1
    # Beorn (poder 6) conjurada NESTE turno: doente de invocacao, nao ataca, nao e' alvo valido
    d = fresh(turn=6, battlefield=[bg.COMMANDER, "Herd Heirloom"], library=["Forest"] * 30)
    d.commander_in_play = True
    d.creature_entered_turn[bg.COMMANDER] = d.turn
    bg.combat_step(d, [])
    assert d.heirloom_draw_activations == 0
    # Gigantic Big Bear tem haste: pode atacar no turno em que entra
    h = fresh(turn=6, battlefield=["Gigantic Big Bear", "Herd Heirloom"], library=["Forest"] * 30)
    h.creature_entered_turn["Gigantic Big Bear"] = h.turn
    bg.combat_step(h, [])
    assert h.heirloom_draw_activations == 1


def test_heirloom_contadores_agregados_levam_a_maior_criatura_a_poder_4():
    s = veterano(fresh(turn=6, battlefield=["Llanowar Elves", "Herd Heirloom"], library=["Forest"] * 30), "Llanowar Elves")
    s.counters_on_board = 3                                                   # poder 1 + 3 contadores (assumidos na maior criatura) = 4
    bg.combat_step(s, [])
    assert s.heirloom_draw_activations == 1
    # contadores NAO ajudam uma criatura que nao e' a de maior poder
    t = veterano(fresh(turn=6, battlefield=["Llanowar Elves", "Birds of Paradise", "Herd Heirloom"], library=["Forest"] * 30), "Llanowar Elves", "Birds of Paradise")
    t.counters_on_board = 2                                                   # o maior e' o Llanowar (1+2=3 < 4); o Birds (0) nunca chega a 4
    bg.combat_step(t, [])
    assert t.heirloom_draw_activations == 0


def test_heirloom_roaming_throne_dobra_o_gatilho_concedido_a_outro_urso_nao_a_propria_throne():
    s = veterano(fresh(turn=6, battlefield=[bg.COMMANDER, "Roaming Throne", "Herd Heirloom"], library=["Forest"] * 30), bg.COMMANDER, "Roaming Throne")
    s.commander_in_play = True
    h = len(s.hand)
    bg.combat_step(s, [])
    assert s.heirloom_draws == 2 and len(s.hand) == h + 2                    # alvo = Beorn (Urso, outra criatura): o gatilho concedido dispara 2x
    t = veterano(fresh(turn=6, battlefield=["Roaming Throne", "Herd Heirloom"], library=["Forest"] * 30), "Roaming Throne")
    bg.combat_step(t, [])
    assert t.heirloom_draw_activations == 1 and t.heirloom_draws == 1        # unica elegivel e' a propria Throne: "another creature", nao dobra
    assert bg.bear_trigger_times(t, "Roaming Throne") == 1


def test_heirloom_guarda_o_tap_para_a_compra_se_ha_alvo_e_arma_o_mana_se_nao_ha():
    s = veterano(fresh(turn=6, battlefield=[bg.COMMANDER, "Herd Heirloom"]), bg.COMMANDER)
    s.commander_in_play = True
    bg.arm_heirloom(s)
    assert not s.heirloom_mana_armed and s.heirloom_mana_turns_reserved_for_draw == 1
    t = fresh(turn=2, battlefield=["Llanowar Elves", "Herd Heirloom"])
    bg.arm_heirloom(t)
    assert t.heirloom_mana_armed and t.heirloom_mana_turns_reserved_for_draw == 0
    with chaves(HERD_HEIRLOOM_DRAW=False):                                    # sem a habilidade 2, o {T} e' sempre mana
        u = veterano(fresh(turn=6, battlefield=[bg.COMMANDER, "Herd Heirloom"]), bg.COMMANDER)
        u.commander_in_play = True
        bg.arm_heirloom(u)
        assert u.heirloom_mana_armed


def test_heirloom_excecao_do_comandante_que_so_cabe_com_o_mana_dele():
    s = veterano(fresh(turn=5, battlefield=["Forest"] * 4 + ["Herd Heirloom", "Chameleon Colossus"]), "Chameleon Colossus")
    assert bg.heirloom_draw_target(s) == "Chameleon Colossus"               # ha alvo elegivel (poder 4): o padrao seria guardar o {T} para a compra
    bg.arm_heirloom(s)
    assert s.heirloom_mana_armed and s.heirloom_mana_turns_reserved_for_draw == 0   # mas a Beorn (5) so' cabe com o mana do Heirloom: 4 + 1
    bg.main_phase(s, [])
    assert s.commander_in_play and s.heirloom_mana_uses == 1
    with chaves(HERD_HEIRLOOM_MANA=False):
        t = veterano(fresh(turn=5, battlefield=["Forest"] * 4 + ["Herd Heirloom", "Chameleon Colossus"]), "Chameleon Colossus")
        bg.main_phase(t, [])
        assert not t.commander_in_play                                       # sem a habilidade 1 a Beorn nao cabe neste turno


def test_heirloom_play_turn_completo_rocha_barata_primeiro_e_depois_a_criatura():
    def rodar():
        s = fresh(turn=2, hand=["Herd Heirloom", "Eternal Witness"], battlefield=["Forest"] * 4)
        s.land_played = True
        bg.main_phase(s, [])
        return s
    s = rodar()
    assert "Herd Heirloom" in s.battlefield and "Eternal Witness" in s.battlefield    # 4 de mana: Heirloom (2) e depois a Witness (3) com 2 livres + 1 restrito
    assert s.heirloom_cast_turn == 2 and s.heirloom_mana_uses == 1 and bg.remaining_mana(s) == 0
    with chaves(HERD_HEIRLOOM_MANA=False):
        s0 = rodar()
        assert "Herd Heirloom" in s0.battlefield and "Eternal Witness" not in s0.battlefield


def test_heirloom_custo_medallion_devocao_artefato_e_sem_tag_de_rampa():
    s = fresh(turn=3, battlefield=["Forest"])
    assert bg.effective_cost(s, "Herd Heirloom") == 2
    s.battlefield.append("Emerald Medallion")
    assert bg.effective_cost(s, "Herd Heirloom") == 1                       # "Green spells you cast cost {1} less": tem {G} no custo
    assert bg.C("Herd Heirloom").g_pips == 1 and bg.is_artifact("Herd Heirloom") and not bg.is_creature("Herd Heirloom")
    assert not bg.has_tag("Herd Heirloom", "ramp")
    base = bg.total_mana(s)
    s.battlefield.append("Herd Heirloom")
    assert bg.total_mana(s) == base                                          # o mana restrito nunca entra no total geral
    assert bg.green_devotion(s) == bg.green_devotion(fresh(battlefield=["Forest", "Emerald Medallion"])) + 1


def test_beorn_gatilho_no_inicio_do_combate_dispara_mesmo_doente_de_invocacao():
    def rodar():
        s = fresh(turn=5, battlefield=[bg.COMMANDER, "Llanowar Elves", "Little Bear", "Ayula, Queen Among Bears"], library=["Forest"] * 30)
        s.commander_in_play = True
        s.creature_entered_turn[bg.COMMANDER] = s.turn                        # Beorn conjurada neste turno
        h = len(s.hand)
        bg.combat_step(s, [])
        return s, len(s.hand) - h
    with chaves(BEORN_TRIGGER_AT_BEGINNING_OF_COMBAT=True):
        s, comprou = rodar()
        assert "Llanowar Elves" in s.converted_to_bear and s.beorn_combat_triggers == 1
        assert comprou >= 2 and s.beorn_bear_draws == 1                       # Beorn + Little Bear + Ayula + Elves = 4 Ursos: compra 2
    with chaves(BEORN_TRIGGER_AT_BEGINNING_OF_COMBAT=False):
        s0, comprou0 = rodar()
        assert s0.beorn_combat_triggers == 0 and s0.beorn_bear_draws == 0 and comprou0 == 0   # comportamento de antes: doente de invocacao, sem gatilho


def test_baralho_de_antes_tem_ram_through_na_mesma_posicao_do_heirloom():
    with chaves(HERD_HEIRLOOM_IN_DECK=True):
        novo = bg.current_decklist()
    with chaves(HERD_HEIRLOOM_IN_DECK=False):
        velho = bg.current_decklist()
    assert len(novo) == len(velho) == 99 and "Herd Heirloom" in novo and "Ram Through" not in novo
    assert "Ram Through" in velho and "Herd Heirloom" not in velho
    assert [i for i, (a, b) in enumerate(zip(novo, velho)) if a != b] == [novo.index("Herd Heirloom")] == [velho.index("Ram Through")]


def test_heirloom_partidas_inteiras_disparam_e_nao_quebram_nenhuma_invariante():
    ativ = comprou = mana = 0
    for sd in range(7_000_000, 7_000_300):
        r = bg.simulate_one(sd, turns=8)
        ativ += r["heirloom_draw_activations"]; comprou += r["heirloom_draws"]; mana += r["heirloom_mana_uses"]
        st = bg.simulate_one_with_interaction(sd, turns=8)
        assert st.heirloom_draws >= st.heirloom_draw_activations >= 0
    assert ativ > 0 and comprou >= ativ and mana > 0                          # nao-vacuo: a habilidade 1 e a 2 acontecem de verdade


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

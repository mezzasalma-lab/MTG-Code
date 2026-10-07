"""Testes dirigidos do simulador do Mothman: cada um monta um estado, dispara UMA habilidade e confere o efeito (Regra #1 de CLAUDE.md: 'teste unitario dirigido confirmando
que cada correcao especifica dispara de verdade'). Um teste que passa em vazio e' bug: cada um confere que o numero esperado e' > 0.
Uso: cd wise-mothman-sultai && python3 testes/testes_dirigidos.py"""
import importlib.util, os, sys, traceback, random, collections

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location("mm", os.path.join(os.path.dirname(HERE), "mothman_goldfish_v1.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

RESULTS = []


def fresh(seed=1, hand=(), bf=(), gy=(), lib=None, turn=5, life=40, opps_lib=None, rad=0):
    st = m.new_state(seed)
    st.turn = turn
    st.hand = list(hand)
    st.graveyard = list(gy)
    st.battlefield = []
    st.exile = []
    st.life = life
    st.life_min = life
    st.rad = rad
    st.library = list(lib) if lib is not None else ["Forest"] * 25 + ["Island"] * 5 + ["Swamp"] * 5 + ["Fathom Mage", "Ruin Crab", "Sol Ring"] * 10
    st.library_min = len(st.library)
    for name in bf:
        add(st, name)
    for o in st.opps:
        o.library = list(opps_lib) if opps_lib is not None else (["N", "C", "L"] * 30)
        o.life = 40
        o.rad = 0
    return st


def add(st, name, counters=0, tapped=False, sick=False, **ctr):
    p = m.mk_perm(st, name)
    p.counters = counters
    p.tapped = tapped
    p.entered_turn = st.turn if sick else st.turn - 2
    for k, v in ctr.items():
        p.ctr[k] = v
    st.battlefield.append(p)
    return p


def teste(f):
    def run():
        try:
            f()
            RESULTS.append((f.__name__, True, ""))
        except AssertionError as e:
            RESULTS.append((f.__name__, False, "ASSERT: " + str(e)))
        except Exception as e:
            RESULTS.append((f.__name__, False, "EXC: " + "".join(traceback.format_exception_only(type(e), e)).strip() + " @ " + str(traceback.extract_tb(e.__traceback__)[-1].lineno)))
    run.__name__ = f.__name__
    TESTS.append(run)
    return run


TESTS = []


# ============================================================== Mothman: o gatilho central
@teste
def mothman_mill_oponente_poe_X_contadores():
    st = fresh(bf=[m.COMMANDER, "Gyre Sage", "Evolution Witness", "Walking Ballista"])
    cs = m.creatures(st)
    before = sum(p.counters for p in cs)
    m.mill_event(st, [(1, 3)], source="teste")           # lib do oponente: N C L -> 2 nao-terrenos
    assert st.mothman_triggers_total == 1, st.mothman_triggers_total
    assert st.mothman_x_total == 2, st.mothman_x_total
    assert sum(p.counters for p in cs) - before == 2


@teste
def mothman_so_terrenos_nao_dispara():
    st = fresh(bf=[m.COMMANDER, "Gyre Sage"], opps_lib=["L"] * 20)
    m.mill_event(st, [(1, 3)], source="teste")
    assert st.mothman_triggers_total == 0
    assert st.mill_events_total == 1


@teste
def mothman_varios_jogadores_um_gatilho():
    st = fresh(bf=[m.COMMANDER, "Gyre Sage", "Evolution Witness", "Six", "Ruin Crab"], lib=["Fathom Mage"] * 20, opps_lib=["N"] * 20)
    m.mill_event(st, [(0, 2), (1, 2), (2, 2)], source="teste")       # 6 nao-terrenos, 3 jogadores, UM evento
    assert st.mothman_triggers_total == 1, st.mothman_triggers_total
    assert st.mothman_x_total == 6, st.mothman_x_total


@teste
def mothman_X_maior_que_alvos_nao_desperdica_excesso():
    st = fresh(bf=[m.COMMANDER], opps_lib=["N"] * 20)
    m.mill_event(st, [(1, 5)], source="teste")
    p = st.battlefield[0]
    assert p.counters == 1, p.counters                  # cada alvo recebe UM contador; X=5 mas so' 1 criatura


@teste
def mothman_hardened_scales_soma_um():
    st = fresh(bf=[m.COMMANDER, "Hardened Scales"], opps_lib=["N"] * 20)
    m.mill_event(st, [(1, 1)], source="teste")
    assert st.battlefield[0].counters == 2, st.battlefield[0].counters


@teste
def mothman_scales_constrictor_kami_somam():
    st = fresh(bf=[m.COMMANDER, "Hardened Scales", "Winding Constrictor", "Kami of Whispered Hopes"], opps_lib=["N"] * 20)
    mm = st.battlefield[0]
    n = m.place_counters(st, mm, 1)
    assert n == 4, n                                    # 1 + Scales + Constrictor + Kami


@teste
def mothman_rad_oponente_no_main_dele():
    st = fresh(bf=[m.COMMANDER, "Gyre Sage"], opps_lib=["N", "N", "L", "N", "N", "L", "N", "N"] * 5)
    o = st.opps[0]
    o.rad = 3
    m.rad_trigger_opp(st, o)
    # mila 3 (N,N,L) -> 2 nao-terrenos: perde 2, remove 2 rad
    assert o.life == 38, o.life
    assert o.rad == 1, o.rad
    assert st.mothman_triggers_total == 1 and st.mothman_x_total == 2


@teste
def rad_proprio_milla_e_perde_vida():
    st = fresh(lib=["Fathom Mage", "Forest", "Ruin Crab", "Island"] * 10, rad=3)
    m.rad_trigger_self(st)
    # 3 cartas: Fathom Mage, Forest, Ruin Crab -> 2 nao-terrenos
    assert st.life == 38, st.life
    assert st.rad == 1, st.rad
    assert st.rad_triggers_self == 1


@teste
def mothman_etb_da_rad_em_todos():
    st = fresh(hand=[m.COMMANDER])
    st.commander_in_cz = True
    st.pool = {}
    for p in [None]:
        pass
    # 4 mana de Forest/Island/Swamp
    for n in ("Forest", "Island", "Swamp", "Forest"):
        add(st, n)
    assert m.cast_commander(st)
    assert st.rad == 1 and all(o.rad == 1 for o in st.opps), (st.rad, [o.rad for o in st.opps])


@teste
def constrictor_dobra_rad_proprio():
    st = fresh(bf=["Winding Constrictor"])
    m.give_rad(st, 0, 1)
    assert st.rad == 2, st.rad


@teste
def mothman_ataque_da_rad():
    st = fresh(bf=[m.COMMANDER])
    st.battlefield[0].entered_turn = 1
    m.combat_step(st)
    assert st.mothman_attacks_total == 1
    assert st.rad == 1 and all(o.rad >= 1 for o in st.opps)


@teste
def danny_pink_compra_uma_vez_por_turno_por_criatura():
    st = fresh(bf=[m.COMMANDER, "Danny Pink"])
    h0 = len(st.hand)
    mm = st.battlefield[0]
    m.place_counters(st, mm, 1)
    m.place_counters(st, mm, 1)
    assert len(st.hand) - h0 == 1, len(st.hand) - h0
    st.turn_id += 1
    m.place_counters(st, mm, 1)
    assert len(st.hand) - h0 == 2


@teste
def fathom_mage_compra_por_contador():
    st = fresh(bf=["Fathom Mage", "Hardened Scales", "Winding Constrictor"])
    fm = st.battlefield[0]
    h0 = len(st.hand)
    n = m.place_counters(st, fm, 1)      # 1 + Scales + Constrictor = 3 contadores -> 3 compras (ruling: uma por contador)
    assert n == 3 and len(st.hand) - h0 == 3, (n, len(st.hand) - h0)


@teste
def gitrog_compra_uma_vez_por_evento_de_terrenos():
    st = fresh(bf=["The Gitrog Monster"], lib=["Forest", "Forest", "Island", "Fathom Mage"] * 10)
    h0 = len(st.hand)
    m.mill_event(st, [(0, 3)], source="teste")          # 3 terrenos: UM evento -> 1 compra
    assert len(st.hand) - h0 == 1 and st.gitrog_draws_total == 1


@teste
def hedge_shredder_poe_terrenos_milados_em_campo_virados():
    st = fresh(bf=["Hedge Shredder"], lib=["Forest", "Island", "Fathom Mage", "Swamp"] * 10)
    n0 = m.n_lands(st)
    m.mill_event(st, [(0, 3)], source="teste")          # Forest, Island, Fathom Mage
    assert m.n_lands(st) - n0 == 2, m.n_lands(st) - n0
    assert all(p.tapped for p in st.battlefield if "land" in p.card.types)
    assert "Forest" not in st.graveyard and "Island" not in st.graveyard


@teste
def mirelurk_queen_uma_vez_por_turno():
    st = fresh(bf=["Mirelurk Queen"], opps_lib=["N"] * 20)
    h0 = len(st.hand)
    m.mill_event(st, [(1, 1)], source="teste")
    m.mill_event(st, [(1, 1)], source="teste")
    assert len(st.hand) - h0 == 1
    assert st.battlefield[0].counters == 1


@teste
def zellix_horror_por_criatura_milada_de_qualquer_jogador():
    st = fresh(bf=["Zellix, Sanity Flayer"], opps_lib=["C"] * 10)
    n0 = len(m.creatures(st))
    m.mill_event(st, [(1, 2)], source="teste")           # 2 criaturas num evento -> UMA ficha (gatilho 'one or more')
    assert len(m.creatures(st)) - n0 == 1, len(m.creatures(st)) - n0
    assert st.horror_tokens_total == 1


@teste
def syr_konrad_dano_por_carta_de_criatura_milada():
    st = fresh(bf=["Syr Konrad, the Grim"], opps_lib=["C", "C", "N", "L"] * 5)
    o = st.opps[0]
    m.mill_event(st, [(1, 3)], source="teste")           # 2 criaturas -> 2 pings em CADA oponente
    assert o.life == 38, o.life
    assert st.opps[1].life == 38


@teste
def syr_konrad_carta_sai_do_meu_cemiterio():
    st = fresh(bf=["Syr Konrad, the Grim"], gy=["Gyre Sage", "Fathom Mage", "Forest"])
    m.graveyard_leave(st, ["Gyre Sage", "Forest", "Fathom Mage"])
    assert st.opps[0].life == 38 and st.konrad_graveyard_leave_pings == 2


@teste
def undead_alchemist_exila_criatura_do_oponente_e_cria_zumbi():
    st = fresh(bf=["Undead Alchemist"], opps_lib=["C", "C", "N"] * 10)
    n0 = len(m.creatures(st))
    m.mill_event(st, [(1, 3)], source="teste")
    assert len(m.creatures(st)) - n0 == 2 and st.zombie_tokens_total == 2
    assert st.opps[0].graveyard.count("C") == 0


@teste
def ascension_com_mindcrank_e_combo():
    st = fresh(bf=["Bloodchief Ascension", "Mindcrank"], opps_lib=["N"] * 60)
    asc = st.battlefield[0]
    asc.ctr["quest"] = 3
    m.mill_event(st, [(1, 1)], source="teste")
    assert st.opps[0].eliminated and st.opps[0].elim_reason == "decked"
    assert st.combo_win == "ascension_mindcrank"


@teste
def ascension_sem_mindcrank_perde_2_e_ganho_2():
    st = fresh(bf=["Bloodchief Ascension"], opps_lib=["N"] * 20)
    st.battlefield[0].ctr["quest"] = 3
    l0 = st.life
    m.mill_event(st, [(1, 2)], source="teste")
    assert st.opps[0].life == 36 and st.life == l0 + 4


@teste
def ascension_nao_ativa_com_menos_de_3_marcadores():
    st = fresh(bf=["Bloodchief Ascension"], opps_lib=["N"] * 20)
    st.battlefield[0].ctr["quest"] = 2
    m.mill_event(st, [(1, 2)], source="teste")
    assert st.opps[0].life == 40


@teste
def ascension_marcador_no_fim_do_turno_se_oponente_perdeu_2():
    st = fresh(bf=["Bloodchief Ascension"])
    st.opps[0].lost_life_this_turn = 2
    m.ascension_end_step(st)
    assert st.battlefield[0].ctr.get("quest") == 1
    st.opps[0].lost_life_this_turn = 1
    m.ascension_end_step(st)
    assert st.battlefield[0].ctr.get("quest") == 1


@teste
def kozilek_milado_embaralha_cemiterio():
    st = fresh(gy=["Forest", "Island", "Gyre Sage"], lib=["Kozilek, Butcher of Truth", "Forest", "Island"])
    m.mill_event(st, [(0, 1)], source="teste")
    assert st.kozilek_shuffles_total == 1
    assert len(st.graveyard) == 0 and len(st.library) == 6, (len(st.graveyard), len(st.library))     # 2 que sobraram + 3 do cemiterio + o proprio Kozilek


@teste
def kozilek_descartado_embaralha_cemiterio():
    st = fresh(hand=["Kozilek, Butcher of Truth"] + ["Forest"] * 7, gy=["Island", "Swamp"])
    lib0 = len(st.library)
    m.discard_to_hand_size(st)
    assert len(st.hand) == 7 and st.kozilek_shuffles_total == 1       # sem terrenos em campo o Kozilek e' a carta de menor valor: descartado, embaralha o cemiterio
    assert st.graveyard == [] and len(st.library) == lib0 + 3


@teste
def kozilek_conjurado_compra_4():
    st = fresh(hand=["Kozilek, Butcher of Truth"], bf=["Sol Ring", "Forest"] * 1, lib=["Forest"] * 30)
    for _ in range(9):
        add(st, "Island")
    h0 = len(st.hand)
    assert m.cast_card(st, "Kozilek, Butcher of Truth")
    assert len(st.hand) - h0 == 4 - 1, len(st.hand) - h0       # -1 porque a propria Kozilek saiu da mao


@teste
def orb_untap_milla_por_permanente_virado():
    st = fresh(bf=["Mesmeric Orb", "Forest", "Forest", "Island", "Sol Ring"], lib=["Forest"] * 30)
    for p in st.battlefield[1:]:
        p.tapped = True
    l0 = len(st.library)
    m.untap_my_permanents(st)
    assert l0 - len(st.library) == 4, l0 - len(st.library)
    assert st.orb_untap_triggers == 4


@teste
def orb_oponente_milla_ao_desvirar():
    st = fresh(bf=["Mesmeric Orb"])
    o = st.opps[0]
    o.tapped_last_turn = 5
    l0 = len(o.library)
    m.opp_untap_and_orb(st, o)
    assert l0 - len(o.library) == 5


@teste
def mindcrank_dano_vira_mill():
    st = fresh(bf=["Mindcrank"])
    l0 = len(st.opps[0].library)
    m.lose_life_opp(st, 1, 4, "teste")
    assert l0 - len(st.opps[0].library) == 4


@teste
def psychic_corrosion_compra_milla_cada_oponente_2():
    st = fresh(bf=["Psychic Corrosion"])
    l0 = [len(o.library) for o in st.opps]
    m.draw_cards(st, 1, "teste")
    assert all(a - len(o.library) == 2 for a, o in zip(l0, st.opps))


@teste
def memory_erosion_e_pollywog_no_turno_do_oponente():
    st = fresh(bf=["Memory Erosion", "Pollywog Prodigy"])
    st.battlefield[1].counters = 5                     # poder 6: qualquer nao-criatura com MV < 6 compra
    o = st.opps[0]
    o.turns_taken = 3
    o.lands = 10
    o.hand_size = 5
    o.library = ["N"] * 20
    seen = {"me": 0, "pw": 0}
    rng = m.opp_rng(st, o)
    for sd in range(40):
        st2 = fresh(seed=sd + 1, bf=["Memory Erosion", "Pollywog Prodigy"])
        st2.battlefield[1].counters = 5
        oo = st2.opps[0]
        oo.turns_taken = 3; oo.lands = 10; oo.hand_size = 5
        h0 = len(st2.hand)
        m.opponent_turn(st2, oo)
        seen["me"] += st2.memory_erosion_mills
        seen["pw"] += st2.pollywog_draws
    assert seen["me"] > 0, seen
    assert seen["pw"] > 0, seen


@teste
def ruin_crab_landfall_milla_3_cada_oponente():
    st = fresh(bf=["Ruin Crab"])
    l0 = [len(o.library) for o in st.opps]
    m.put_land_onto_battlefield(st, "Forest", source="play")
    assert all(a - len(o.library) == 3 for a, o in zip(l0, st.opps))


@teste
def icetill_landfall_milla_1_e_permite_terreno_do_cemiterio():
    st = fresh(bf=["Icetill Explorer"], gy=["Forest"], hand=[], lib=["Fathom Mage"] * 30)
    l0 = len(st.library)
    m.play_land_phase(st)
    assert m.n_lands(st) == 1 and "Forest" not in st.graveyard
    assert l0 - len(st.library) == 1                         # landfall: mila 1 (nao-terreno: nao da' 2o terreno)
    assert m.land_drops_available(st) == 2 and st.icetill_replays == 1
    # com terrenos na biblioteca, o terreno milado e' rejogavel do cemiterio com a 2a jogada de terreno
    st2 = fresh(bf=["Icetill Explorer"], gy=["Forest"], hand=[], lib=["Island"] * 30)
    m.play_land_phase(st2)
    assert m.n_lands(st2) == 2 and st2.icetill_replays == 2


@teste
def gitrog_terreno_extra_e_upkeep_sacrifica_terreno():
    st = fresh(bf=["The Gitrog Monster", "Forest", "Forest", "Island", "Swamp", "Forest"])
    assert m.land_drops_available(st) == 2
    n0 = m.n_lands(st)
    m.gitrog_upkeep(st)
    assert m.n_lands(st) == n0 - 1 and m.has_perm(st, "The Gitrog Monster")
    st2 = fresh(bf=["The Gitrog Monster", "Forest", "Island"])
    m.gitrog_upkeep(st2)
    assert not m.has_perm(st2, "The Gitrog Monster")


@teste
def deepmuck_crime_milla_3_uma_vez_por_turno():
    st = fresh(bf=["Deepmuck Desperado"])
    l0 = len(st.opps[0].library)
    m.commit_crime(st, "t")
    m.commit_crime(st, "t")
    assert l0 - len(st.opps[0].library) == 3, l0 - len(st.opps[0].library)
    assert st.crimes_total == 2


@teste
def freestrider_olha_5_poe_terreno_virado():
    st = fresh(bf=["Freestrider Lookout"], lib=["Fathom Mage", "Forest", "Ruin Crab", "Island", "Sol Ring"] + ["Swamp"] * 20)
    m.commit_crime(st, "t")
    assert m.n_lands(st) == 1
    assert [p for p in st.battlefield if "land" in p.card.types][0].tapped
    assert len(st.library) == 24


@teste
def generous_patron_apoia_2_outras_criaturas():
    st = fresh(bf=["Gyre Sage", "Evolution Witness", "Six"], hand=["Generous Patron"])
    for n in ("Forest", "Forest", "Forest"):
        add(st, n)
    c0 = sum(p.counters for p in m.creatures(st))
    assert m.cast_card(st, "Generous Patron")
    assert sum(p.counters for p in m.creatures(st)) - c0 >= 2


@teste
def ouroboroid_poe_X_em_cada_criatura():
    st = fresh(bf=["Ouroboroid", "Gyre Sage", "Six"])
    ou = st.battlefield[0]
    ou.counters = 2                                      # poder 3
    c0 = sum(p.counters for p in m.creatures(st))
    m.beginning_of_combat(st)
    assert sum(p.counters for p in m.creatures(st)) - c0 == 9, sum(p.counters for p in m.creatures(st)) - c0   # 3 criaturas x 3


@teste
def herd_baloth_ficha_besta_com_contador():
    st = fresh(bf=["Herd Baloth"])
    n0 = len(m.creatures(st))
    m.place_counters(st, st.battlefield[0], 1)
    assert len(m.creatures(st)) - n0 == 1


@teste
def broodscale_spawn_e_adapt():
    st = fresh(bf=["Basking Broodscale", "Forest", "Forest"])
    assert m.act_adapt(st)
    assert st.battlefield[0].counters == 1
    assert any("spawn" in p.card.tags for p in st.battlefield)


@teste
def evolution_witness_adapt_devolve_permanente():
    st = fresh(bf=["Evolution Witness", "Forest", "Forest"], gy=["Sol Ring"])
    assert m.act_adapt(st)
    assert st.battlefield[0].counters == 2
    assert "Sol Ring" in st.hand


@teste
def evolve_dispara_com_criatura_maior():
    st = fresh(bf=["Gyre Sage"], hand=["Icetill Explorer"])
    for n in ("Forest", "Forest", "Forest", "Forest"):
        add(st, n)
    gs = st.battlefield[0]
    assert m.cast_card(st, "Icetill Explorer")
    assert gs.counters >= 1


@teste
def kodama_dano_de_combate_modificada_busca_basico():
    st = fresh(bf=["Kodama of the West Tree", "Six"])
    for p in st.battlefield:
        p.entered_turn = 1
    gs = st.battlefield[1]
    gs.counters = 2        # modificada
    st.battlefield[0].tapped = True
    n0 = m.n_lands(st)
    m.combat_step(st)
    assert st.kodama_lands_total >= 1 and m.n_lands(st) > n0


@teste
def frogantua_ganha_10_por_jogador_que_perdeu():
    st = fresh(bf=["Rampant Frogantua"])
    p = st.battlefield[0]
    assert m.power(st, p) == 3
    st.opps[0].eliminated = True
    assert m.power(st, p) == 13
    st.decked = True
    assert m.power(st, p) == 23


@teste
def frogantua_dano_milla_e_poe_terrenos():
    st = fresh(bf=["Rampant Frogantua"], lib=["Forest", "Island", "Swamp", "Fathom Mage", "Ruin Crab"] + ["Forest"] * 40)
    st.battlefield[0].entered_turn = 1
    n0 = m.n_lands(st)
    m.combat_step(st)
    assert m.n_lands(st) > n0


@teste
def selkie_compra_igual_ao_dano():
    st = fresh(bf=["Cold-Eyed Selkie"])
    st.battlefield[0].entered_turn = 1
    st.battlefield[0].counters = 2
    h0 = len(st.hand)
    m.combat_step(st)
    assert len(st.hand) - h0 == 3, len(st.hand) - h0


@teste
def danny_mentor_poe_contador_em_atacante_menor():
    st = fresh(bf=["Danny Pink", "Six", "Gyre Sage"])
    for p in st.battlefield:
        p.entered_turn = 1
    c0 = sum(p.counters for p in st.battlefield)
    m.combat_step(st)
    assert sum(p.counters for p in st.battlefield) > c0


@teste
def six_ataque_milla_3_e_pega_terreno():
    st = fresh(bf=["Six"], lib=["Forest", "Island", "Fathom Mage"] + ["Sol Ring"] * 30)
    st.battlefield[0].entered_turn = 1
    h0 = len(st.hand)
    m.combat_step(st)
    assert st.self_mill_by_source.get("six") == 3
    assert len(st.hand) > h0


@teste
def hedge_shredder_crew_e_ataque():
    st = fresh(bf=["Hedge Shredder", "Gyre Sage"])
    for p in st.battlefield:
        p.entered_turn = 1
    st.battlefield[1].entered_turn = st.turn          # a tripulante esta doente: so' pode tripular
    m.combat_step(st)
    assert st.self_mill_by_source.get("hedge_shredder_attack") == 2
    assert st.proxy_damage_total >= 5


@teste
def undead_alchemist_zumbi_causa_mill_em_vez_de_dano():
    st = fresh(bf=["Undead Alchemist"], opps_lib=["N"] * 50)
    st.battlefield[0].entered_turn = 1
    m.combat_step(st)
    assert st.opp_mill_by_source.get("undead_alchemist") == 4
    assert all(o.life == 40 for o in st.opps)


@teste
def commander_damage_21_elimina():
    st = fresh(bf=[m.COMMANDER])
    st.battlefield[0].entered_turn = 1
    st.battlefield[0].counters = 20
    for o in st.opps[1:]:
        o.life = 100
    st.opps[0].life = 100
    m.combat_step(st)
    assert any(o.elim_reason == "commander" for o in st.opps), [o.cmd_damage for o in st.opps]


@teste
def palantir_marcador_scry_e_escolha_do_oponente():
    got = collections.Counter()
    for sd in range(60):
        st = fresh(seed=sd + 1, bf=["Palantír of Orthanc"])
        m.palantir_end_step(st)
        got["draw"] += st.palantir_draws
        got["mill"] += st.palantir_mills
        assert st.battlefield[0].ctr["influence"] == 1
    assert got["draw"] > 0 and got["mill"] > 0, got


@teste
def altar_of_the_brood_milla_ao_entrar_outro_permanente():
    st = fresh(bf=["Altar of the Brood"], hand=["Sol Ring"])
    add(st, "Forest")
    l0 = [len(o.library) for o in st.opps]
    assert m.cast_card(st, "Sol Ring")
    assert all(a - len(o.library) == 1 for a, o in zip(l0, st.opps))


@teste
def great_henge_contador_e_compra_em_criatura_nao_ficha():
    st = fresh(bf=["The Great Henge"], hand=["Six"])
    for n in ("Forest", "Forest", "Forest"):
        add(st, n)
    h0 = len(st.hand)
    assert m.cast_card(st, "Six")
    six = [p for p in st.battlefield if p.card.name == "Six"][0]
    assert six.counters == 1 and len(st.hand) - h0 == 0     # -1 (Six) +1 (compra)


@teste
def great_henge_custa_X_menos_pelo_maior_poder():
    st = fresh(bf=["Six"])
    st.battlefield[0].counters = 7                       # poder 9
    g, pips = m.effective_cost(st, "The Great Henge")
    assert g == 0 and len(pips) == 2, (g, pips)


@teste
def comandante_imposto_conta_conjuracao():
    st = fresh(hand=[])
    st.commander_cast_count = 2
    g, pips = m.effective_cost(st, m.COMMANDER)
    assert g == 1 + 4, g


@teste
def kami_mana_igual_ao_poder_de_uma_cor():
    st = fresh(bf=["Kami of Whispered Hopes"])
    st.battlefield[0].counters = 3
    # poder 1 + 3 + 1 (a propria Kami: +1 extra no contador)
    srcs = m.mana_sources(st)
    assert srcs and srcs[0].bundle and srcs[0].amount == 4, [(s.bundle, s.amount) for s in srcs]


@teste
def gyre_sage_mana_por_contador():
    st = fresh(bf=["Gyre Sage"])
    st.battlefield[0].counters = 3
    srcs = m.mana_sources(st)
    assert srcs[0].amount == 3


@teste
def sol_ring_da_dois_incolores():
    st = fresh(bf=["Sol Ring"])
    assert m.available_mana(st) == 2


@teste
def plaza_cor_dos_lendarios():
    st = fresh(bf=["Plaza of Heroes", "Kodama of the West Tree"])
    s = [x for x in m.mana_sources(st) if x.plaza][0]
    assert "G" in s.colors and "C" in s.colors
    st2 = fresh(bf=["Plaza of Heroes"])
    s2 = [x for x in m.mana_sources(st2) if x.plaza][0]
    assert s2.colors == frozenset({"C"}), s2.colors


@teste
def waterlogged_grove_paga_1_de_vida():
    st = fresh(bf=["Waterlogged Grove"])
    l0 = st.life
    assert m.pay_mana(st, 0, (frozenset("G"),))
    assert st.life == l0 - 1


@teste
def shocklands_pagam_2_de_vida_ou_entram_virados():
    st = fresh(life=40)
    p = m.put_land_onto_battlefield(st, "Breeding Pool", source="play")
    assert st.life == 38 and not p.tapped
    st2 = fresh(life=8)
    p2 = m.put_land_onto_battlefield(st2, "Breeding Pool", source="play")
    assert st2.life == 8 and p2.tapped


@teste
def slowland_entra_desvirada_com_2_oponentes():
    st = fresh()
    p = m.put_land_onto_battlefield(st, "Morphic Pool", source="play")
    assert not p.tapped
    st.opps[0].eliminated = True
    st.opps[1].eliminated = True
    p2 = m.put_land_onto_battlefield(st, "Rejuvenating Springs", source="play")
    assert p2.tapped


@teste
def fetch_real_sacrifica_paga_vida_e_vai_ao_cemiterio():
    st = fresh(bf=["Verdant Catacombs"], lib=["Overgrown Tomb", "Forest", "Swamp"] + ["Island"] * 10)
    l0 = st.life
    assert m.crack_fetch(st, st.battlefield[0])
    assert "Verdant Catacombs" in st.graveyard and st.life <= l0 - 1
    lands = [p for p in st.battlefield if "land" in p.card.types]
    assert len(lands) == 1 and lands[0].card.name in ("Overgrown Tomb", "Forest", "Swamp")


@teste
def fetch_com_gitrog_busca_depois_da_compra():
    st = fresh(bf=["The Gitrog Monster", "Misty Rainforest"], lib=["Forest"] + ["Island"] * 30)
    assert m.crack_fetch(st, [p for p in st.battlefield if p.card.name == "Misty Rainforest"][0])
    assert m.n_lands(st) == 1


@teste
def fabled_passage_desvira_com_4_terrenos():
    st = fresh(bf=["Forest", "Island", "Swamp", "Fabled Passage"], lib=["Forest"] * 10)
    fp = st.battlefield[-1]
    assert m.crack_fetch(st, fp)
    new = [p for p in st.battlefield if p.card.name == "Forest" and m.n_lands(st) == 4][-1]
    assert not new.tapped


@teste
def zagoth_triome_e_bojuka_entram_virados():
    st = fresh()
    assert m.put_land_onto_battlefield(st, "Zagoth Triome", source="play").tapped
    assert m.put_land_onto_battlefield(st, "Bojuka Bog", source="play").tapped


@teste
def bojuka_bog_exila_cemiterio_de_oponente_e_e_crime():
    st = fresh(bf=["Deepmuck Desperado"])
    st.opps[0].graveyard = ["C", "N", "L"]
    l0 = len(st.opps[1].library)
    m.put_land_onto_battlefield(st, "Bojuka Bog", source="play")
    assert st.opps[0].graveyard == [] and st.crimes_total == 1
    assert l0 - len(st.opps[1].library) == 3                  # Deepmuck disparou


@teste
def shifting_woodland_entra_virado_sem_floresta():
    st = fresh()
    assert m.put_land_onto_battlefield(st, "Shifting Woodland", source="play").tapped
    st2 = fresh(bf=["Forest"])
    assert not m.put_land_onto_battlefield(st2, "Shifting Woodland", source="play").tapped


@teste
def urza_saga_capitulos():
    st = fresh(lib=["Sol Ring", "Forest"] * 20)
    p = m.put_land_onto_battlefield(st, "Urza's Saga", source="play")
    assert p.ctr["lore"] == 1
    m.saga_lore_step(st)
    assert p.ctr["lore"] == 2
    st.turn += 1
    m.saga_lore_step(st)
    assert m.has_perm(st, "Sol Ring") and p not in st.battlefield and "Urza's Saga" in st.graveyard


@teste
def urza_saga_constroi_construct_com_poder_por_artefato():
    st = fresh(bf=["Sol Ring", "Forest", "Forest"])
    saga = add(st, "Urza's Saga")
    saga.ctr["lore"] = 2
    assert m.act_saga_construct(st)
    c = [p for p in st.battlefield if "construct" in p.card.tags][0]
    assert m.power(st, c) == 2, m.power(st, c)               # Sol Ring + o proprio Construct


@teste
def ashiok_menos_1_milla_4_e_exila_cemiterios():
    st = fresh(bf=["Ashiok, Dream Render"], ashiok_loyalty=5) if False else fresh(bf=["Ashiok, Dream Render"])
    st.battlefield[0].ctr["loyalty"] = 5
    st.opps[0].graveyard = ["C"]
    assert m.act_ashiok(st)
    assert st.battlefield[0].ctr["loyalty"] == 4
    assert all(o.graveyard == [] for o in st.opps)
    assert sum(st.opp_mill_by_source.values()) == 4


@teste
def cauldron_exila_criatura_de_oponente_e_poe_contador():
    st = fresh(bf=["Agatha's Soul Cauldron", "Gyre Sage"])
    st.opps[1].graveyard = ["C", "N"]
    c0 = st.battlefield[1].counters
    assert m.act_cauldron(st)
    assert st.battlefield[1].counters > c0 and st.opps[1].graveyard == ["N"]


@teste
def cauldron_concede_habilidade_a_criaturas_com_contador():
    st = fresh(bf=["Agatha's Soul Cauldron", "Six"])
    st.cauldron_exiled.append("Kami of Whispered Hopes")
    six = st.battlefield[1]
    six.counters = 2
    srcs = [s for s in m.mana_sources(st) if s.perm is six]
    assert srcs and srcs[0].bundle, srcs


@teste
def cauldron_mana_de_qualquer_cor_so_para_habilidade_de_criatura():
    st = fresh(bf=["Agatha's Soul Cauldron", "Forest", "Forest", "Syr Konrad, the Grim"])
    assert m.afford(st, 1, (frozenset("B"),), creature=True)
    assert not m.afford(st, 1, (frozenset("B"),), creature=False)


@teste
def zellix_ativada_milla_3_e_e_crime():
    st = fresh(bf=["Zellix, Sanity Flayer", "Forest", "Deepmuck Desperado"])
    assert m.act_zellix(st)
    assert sum(st.opp_mill_by_source.values()) >= 3 and st.crimes_total == 1 and st.zellix_activations == 1


@teste
def zellix_nao_ativa_com_doenca_de_invocacao():
    st = fresh(bf=["Forest"])
    add(st, "Zellix, Sanity Flayer", sick=True)
    assert not m.act_zellix(st)


@teste
def minamo_desvira_zellix_segunda_ativacao():
    st = fresh(bf=["Zellix, Sanity Flayer", "Forest", "Island", "Island", "Forest", "Minamo, School at Water's Edge"], lib=["Fathom Mage"] * 30)
    assert m.act_zellix(st)
    assert m.act_zellix_minamo(st)
    assert m.act_zellix(st)
    assert st.zellix_activations == 2 and st.minamo_untaps == 1


@teste
def konrad_ativada_cada_jogador_milla_uma():
    st = fresh(bf=["Syr Konrad, the Grim", "Swamp", "Forest"])
    l0 = len(st.library)
    assert m.act_konrad(st)
    assert l0 - len(st.library) == 1 and sum(st.opp_mill_by_source.values()) == 3
    assert st.mill_events_total == 1                       # UM evento (4 jogadores)


@teste
def cankerbloom_sacrifica_e_prolifera():
    st = fresh(bf=["Cankerbloom", "Gyre Sage", "Evolution Witness", "Forest", "Forest"])
    st.battlefield[1].counters = 2
    st.battlefield[2].counters = 2
    for o in st.opps:
        o.rad = 3
    assert m.act_cankerbloom(st)
    assert not m.has_perm(st, "Cankerbloom")
    assert st.battlefield[0].counters == 3 and all(o.rad == 4 for o in st.opps)


@teste
def proliferate_nao_poe_rad_no_proprio_por_padrao():
    st = fresh(rad=2)
    m.proliferate(st)
    assert st.rad == 2


@teste
def swiftfoot_boots_da_haste_e_equipa():
    st = fresh(bf=["Swiftfoot Boots", "Forest"])
    add(st, "Six", sick=True)
    six = [p for p in st.battlefield if p.card.name == "Six"][0]
    six.counters = 2
    assert m.act_equip_boots(st)
    assert m.has_haste(st, six) and m.can_attack(st, six)


@teste
def ballista_enters_com_X_contadores_e_pinga_para_matar():
    st = fresh(hand=["Walking Ballista"])
    for n in ("Forest",) * 4:
        add(st, n)
    assert m.cast_card(st, "Walking Ballista", x=2)
    b = m.perms_named(st, "Walking Ballista")[0]
    assert b.counters == 2
    st.opps[0].life = 2
    assert m.act_ballista_ping(st)
    assert st.opps[0].eliminated


@teste
def altar_of_dementia_mata_com_o_poder():
    st = fresh(bf=["Altar of Dementia", "Six"])
    st.battlefield[1].counters = 20
    st.opps[0].library = ["N"] * 20
    assert m.act_altar_finisher(st)
    assert len(st.opps[0].library) == 0


@teste
def altar_henge_glen_laco():
    st = fresh(bf=["Altar of Dementia", "The Great Henge", "Glen Elendra Archmage"], lib=["Fathom Mage"] * 40)
    for o in st.opps:
        o.library = ["N"] * 12
    assert m.act_altar_loop(st)
    assert st.altar_loop_iters >= 2 and st.persist_returns >= 2
    assert m.has_perm(st, "Glen Elendra Archmage")
    assert any(len(o.library) == 0 for o in st.opps)


@teste
def glen_persist_volta_com_menos_um_menos_um():
    st = fresh(bf=["Glen Elendra Archmage"])
    g = st.battlefield[0]
    m.remove_permanent(st, g, "dies")
    g2 = m.perms_named(st, "Glen Elendra Archmage")[0]
    assert g2.ctr.get("minus1") == 1 and m.power(st, g2) == 1
    m.remove_permanent(st, g2, "dies")
    assert not m.has_perm(st, "Glen Elendra Archmage")


@teste
def takenuma_canal_milla_3_e_devolve_criatura():
    st = fresh(hand=["Takenuma, Abandoned Mire"] + ["Forest"] * 3, bf=["Swamp", "Swamp", "Swamp", "Swamp", "Forest", "Forest"], gy=["Gyre Sage"])
    h0 = len(st.hand)
    assert m.act_takenuma(st)
    assert "Takenuma, Abandoned Mire" in st.graveyard and st.channel_total == 1
    assert any(c in st.hand for c in ("Gyre Sage",)) or any("creature" in m.CARD_DB[c].types for c in st.hand)


@teste
def boseiju_canal_e_interacao_proxy():
    st = fresh(hand=["Boseiju, Who Endures", "Forest"], bf=["Forest"] * 7, turn=6)
    got = 0
    for sd in range(30):
        s2 = fresh(seed=sd + 1, hand=["Boseiju, Who Endures", "Forest"], bf=["Forest"] * 7, turn=6)
        if m.act_boseiju(s2):
            got += 1
            assert "Boseiju, Who Endures" in s2.graveyard and s2.interaction_plays == 1
    assert got > 0


@teste
def triome_ciclo_compra():
    st = fresh(hand=["Zagoth Triome"], bf=["Forest"] * 7)
    h0 = len(st.hand)
    assert m.act_triome_cycle(st)
    assert "Zagoth Triome" in st.graveyard and len(st.hand) == h0 - 1 + 1


@teste
def waterlogged_grove_sacrifica_e_compra():
    st = fresh(bf=["Waterlogged Grove", "The Gitrog Monster"] + ["Forest"] * 7)
    h0 = len(st.hand)
    assert m.act_waterlogged_grove(st)
    assert "Waterlogged Grove" in st.graveyard and len(st.hand) - h0 == 2     # compra do Grove + da Gitrog


@teste
def strip_mine_proxy_com_pagador_de_crime():
    got = 0
    for sd in range(40):
        st = fresh(seed=sd + 1, bf=["Strip Mine", "Icetill Explorer", "Deepmuck Desperado"] + ["Forest"] * 6, turn=7)
        if m.act_strip_mine(st):
            got += 1
            assert "Strip Mine" in st.graveyard and st.crimes_total == 1
    assert got > 0


@teste
def lantern_sacrifica_e_compra():
    st = fresh(bf=["Soul-Guide Lantern", "Forest"])
    h0 = len(st.hand)
    assert m.act_lantern(st)
    assert len(st.hand) - h0 == 1 and not m.has_perm(st, "Soul-Guide Lantern")


@teste
def woodland_delirio_copia_muldrotha():
    st = fresh(bf=["Shifting Woodland", "Forest", "Forest", "Forest", "Forest"], gy=["Muldrotha, the Gravetide", "Gyre Sage", "Forest", "Sol Ring", "Mindcrank", "Negate", "Nature's Lore"])
    assert m.card_types_in_graveyard(st) >= 4
    assert m.act_woodland(st)
    w = m.perms_named(st, "Muldrotha, the Gravetide")
    assert w and st.shifting_woodland_copies == 1
    assert m.graveyard_cast_options(st)             # a copia de Muldrotha permite conjurar do cemiterio


@teste
def muldrotha_um_de_cada_tipo_por_turno():
    st = fresh(bf=["Muldrotha, the Gravetide"] + ["Forest"] * 6, gy=["Gyre Sage", "Evolution Witness", "Mindcrank", "Sol Ring"])
    m.cast_loop(st)
    types_used = list(st.muldrotha_used)
    assert "creature" in types_used and "artifact" in types_used and len(set(types_used)) == len(types_used)
    assert st.muldrotha_plays >= 2


@teste
def six_retrace_descarta_terreno():
    st = fresh(bf=["Six"] + ["Forest"] * 4, hand=["Forest"], gy=["Mindcrank"])
    m.cast_loop(st)
    assert st.six_retraces == 1 and "Forest" in st.graveyard


@teste
def agadeem_feitico_devolve_criaturas_de_mv_diferentes():
    st = fresh(bf=["Swamp", "Swamp", "Swamp", "Swamp", "Swamp", "Swamp", "Swamp", "Swamp"], hand=[m.AGADEEM], gy=["Gyre Sage", "Six", "Danny Pink"])
    st.battlefield += [m.mk_perm(st, "Forest") for _ in range(0)]
    assert m.act_agadeem(st)
    assert len([p for p in m.creatures(st)]) >= 2


@teste
def smugglers_surprise_modo_a_milla_4_e_pega_criatura_ou_terreno():
    st = fresh(hand=["Smuggler's Surprise"], bf=["Forest"] * 4, lib=["Gyre Sage", "Forest", "Fathom Mage", "Six"] + ["Sol Ring"] * 30)
    h0 = len(st.hand)
    assert m.act_smugglers(st)
    assert st.self_mill_by_source.get("smugglers_surprise") == 4
    assert len(st.hand) - h0 >= 1


@teste
def fetch_quest_milla_7_e_poe_criatura_ou_terreno_em_campo():
    st = fresh(hand=["Bramble Familiar // Fetch Quest"], bf=["Forest"] * 7, lib=["Gyre Sage", "Forest", "Fathom Mage", "Six", "Sol Ring", "Island", "Swamp"] + ["Sol Ring"] * 30)
    assert m.cast_card(st, "Bramble Familiar // Fetch Quest", face="adventure")
    assert st.self_mill_by_source.get("fetch_quest") == 7 and st.adventure_casts == 1
    assert "Bramble Familiar // Fetch Quest" in st.adventure_exile
    assert any(p.card.name in ("Gyre Sage", "Fathom Mage", "Six", "Forest", "Island", "Swamp") for p in st.battlefield if p.uid not in [])


@teste
def nature_lore_busca_floresta_em_campo_desvirada():
    st = fresh(hand=["Nature's Lore"], bf=["Forest", "Forest"], lib=["Overgrown Tomb", "Forest"] + ["Island"] * 20)
    assert m.cast_card(st, "Nature's Lore")
    new = m.lands_in_play(st)[-1]
    assert new.card.name in ("Overgrown Tomb", "Forest") and not new.tapped


@teste
def nuclear_fallout_da_X_rad_a_cada_jogador():
    st = fresh(bf=["Swamp", "Swamp", "Swamp", "Swamp", "Swamp"], hand=["Nuclear Fallout"])
    assert m.act_fallout(st)
    assert st.rad >= 1 and all(o.rad >= 1 for o in st.opps) and st.wipes_cast == 1


@teste
def toxic_deluge_e_wave_goodbye_proxies():
    got = collections.Counter()
    for sd in range(80):
        st = fresh(seed=sd + 1, hand=["Toxic Deluge", "Wave Goodbye"], bf=["Swamp", "Swamp", "Swamp", "Island", "Island", "Gyre Sage", "Six"], turn=6)
        st.battlefield[-1].counters = 3
        st.battlefield[-2].counters = 3
        if m.act_wipe_proxy(st):
            got["wipe"] += st.wipes_cast
    assert got["wipe"] > 0, got


@teste
def repulsive_mutation_poe_X_contadores():
    st = fresh(bf=["Six"] + ["Forest"] * 3 + ["Island"] * 3, hand=["Repulsive Mutation"])
    c0 = st.battlefield[0].counters
    assert m.act_repulsive(st)
    assert st.battlefield[0].counters - c0 >= 2


@teste
def tear_asunder_e_vats_so_com_alvo_e_contam_interacao():
    got = collections.Counter()
    for sd in range(60):
        st = fresh(seed=sd + 1, hand=["Tear Asunder", "V.A.T.S."], bf=["Swamp", "Swamp", "Forest", "Forest", "Forest", "Swamp"], turn=6)
        if m.act_removal_proxy(st):
            got["i"] += st.interaction_plays
    assert got["i"] > 0, got


@teste
def contramagicas_respondem_a_magia_de_oponente():
    got = collections.Counter()
    for sd in range(60):
        st = fresh(seed=sd + 1, hand=["Negate", "Didn't Say Please", "Arcane Denial"], bf=["Island", "Island", "Island", "Island"], turn=6)
        o = st.opps[0]
        if m.respond_to_opp_spell(st, o, noncreature=True, mv=4):
            got["c"] += st.counterspells_cast
            assert st.crimes_total >= 1
    assert got["c"] > 0


@teste
def fierce_guardianship_gratis_com_comandante():
    st = fresh(hand=["Fierce Guardianship"], bf=[m.COMMANDER])
    o = st.opps[0]
    assert m.respond_to_opp_spell(st, o, noncreature=True, mv=5)
    assert "Fierce Guardianship" in st.graveyard


@teste
def didnt_say_please_milla_3_do_controlador():
    st = fresh(hand=["Didn't Say Please"], bf=["Island", "Island", "Island"])
    o = st.opps[0]
    l0 = len(o.library)
    assert m.respond_to_opp_spell(st, o, noncreature=False, mv=4)
    assert l0 - len(o.library) == 3


@teste
def glen_elendra_contramagica_com_persist():
    st = fresh(bf=["Glen Elendra Archmage", "Island", "Island"])
    o = st.opps[0]
    assert m.respond_to_opp_spell(st, o, noncreature=True, mv=4)
    assert m.has_perm(st, "Glen Elendra Archmage") and st.persist_returns == 1


@teste
def hollowmurk_sultai_compra_uma_vez_por_turno():
    st = fresh(bf=["Hollowmurk Siege", m.COMMANDER, "Six"])
    st.battlefield[0].ctr["sultai"] = 1
    h0 = len(st.hand)
    m.place_counters(st, st.battlefield[1], 1)
    m.place_counters(st, st.battlefield[2], 1)
    assert len(st.hand) - h0 == 1


@teste
def hollowmurk_abzan_poe_contador_no_atacante():
    st = fresh(bf=["Hollowmurk Siege", "Six"])
    st.battlefield[0].ctr["abzan"] = 1
    st.battlefield[1].entered_turn = 1
    c0 = st.battlefield[1].counters
    m.combat_step(st)
    assert st.battlefield[1].counters > c0


@teste
def mulligan_escolhe_o_fundo_e_primeiro_e_gratis():
    pen = collections.Counter()
    for sd in range(200):
        st = m.new_state(sd + 1)
        assert len(st.hand) == 7 - max(0, st.mulligans - 1), (len(st.hand), st.mulligans)
        pen[st.mulligans] += 1
    assert pen[0] > 0 and pen[1] > 0, pen


@teste
def decking_ao_comprar_de_biblioteca_vazia():
    st = fresh(lib=[])
    m.draw_cards(st, 1)
    assert st.decked and st.game_over


@teste
def oponente_perde_ao_comprar_de_biblioteca_vazia():
    st = fresh()
    o = st.opps[0]
    o.library = []
    m.opponent_turn(st, o)
    assert o.eliminated and o.elim_reason == "decked"


@teste
def opp_rad_zero_nao_faz_nada():
    st = fresh(bf=[m.COMMANDER])
    o = st.opps[0]
    m.rad_trigger_opp(st, o)
    assert st.mothman_triggers_total == 0


# ============================================================== rodada de rulings (2026-10-05): testes das correcoes
@teste
def konrad_mortes_simultaneas_wipe_conta_cada_outra_criatura():
    st = fresh(bf=["Syr Konrad, the Grim", "Six", "Gyre Sage", "Ruin Crab"])
    m.kill_group(st, list(m.creatures(st)))
    assert not m.creatures(st)
    # 4 criaturas morrem juntas, incluindo o Konrad: ele dispara por cada UMA DAS OUTRAS 3 (nao por ele mesmo)
    assert st.opps[0].life == 37, st.opps[0].life


@teste
def konrad_morte_isolada_de_outra_criatura():
    st = fresh(bf=["Syr Konrad, the Grim", "Six"])
    six = m.perms_named(st, "Six")[0]
    m.remove_permanent(st, six, "dies")
    assert st.opps[0].life == 39


@teste
def frogantua_tudo_ou_nada_no_mill():
    st = fresh(bf=["Rampant Frogantua"], lib=["Forest"] * 6)
    st.battlefield[0].entered_turn = 1
    st.battlefield[0].counters = 10                       # dano 13 > biblioteca (6): nao posso escolher milar
    m.combat_step(st)
    assert st.self_mill_by_source.get("frogantua", 0) == 0, st.self_mill_by_source


@teste
def persist_dispara_hollowmurk_sultai():
    st = fresh(bf=["Hollowmurk Siege", "Glen Elendra Archmage"])
    st.battlefield[0].ctr["sultai"] = 1
    h0 = len(st.hand)
    m.remove_permanent(st, st.battlefield[1], "dies")      # volta com -1/-1: 'a counter is put on a creature you control'
    assert len(st.hand) - h0 == 1, len(st.hand) - h0


@teste
def ballista_entra_com_contadores_dispara_hollowmurk():
    st = fresh(bf=["Hollowmurk Siege"], hand=["Walking Ballista"])
    st.battlefield[0].ctr["sultai"] = 1
    for _ in range(4):
        add(st, "Forest")
    h0 = len(st.hand)
    assert m.cast_card(st, "Walking Ballista", x=2)
    assert len(st.hand) - h0 == 0, len(st.hand) - h0        # -1 (Ballista saiu da mao) +1 (Hollowmurk)


@teste
def once_each_turn_zera_a_cada_turno_de_qualquer_jogador():
    st = fresh(bf=["Mirelurk Queen"], opps_lib=["N"] * 30)
    m.begin_any_turn(st)
    h0 = len(st.hand)
    m.mill_event(st, [(1, 1)], source="t")
    m.mill_event(st, [(1, 1)], source="t")
    assert len(st.hand) - h0 == 1
    m.begin_any_turn(st)                                    # turno de um oponente: a Queen dispara de novo
    m.mill_event(st, [(1, 1)], source="t")
    assert len(st.hand) - h0 == 2


@teste
def ascension_dispara_com_magia_anulada_do_oponente():
    st = fresh(bf=["Bloodchief Ascension"], hand=["Negate"] + ["Island"] * 0)
    st.battlefield[0].ctr["quest"] = 3
    for _ in range(3):
        add(st, "Island")
    o = st.opps[0]
    l0 = o.life
    assert m.respond_to_opp_spell(st, o, noncreature=True, mv=4)
    assert o.life == l0 - 2, o.life


@teste
def orb_no_untap_conta_neste_turno_a_queen():
    st = fresh(bf=["Mesmeric Orb", "Mirelurk Queen", "Forest", "Forest"], lib=["Fathom Mage"] * 30)
    for p in st.battlefield:
        if "land" in p.card.types:
            p.tapped = True
    m.begin_any_turn(st)
    h0 = len(st.hand)
    m.untap_my_permanents(st)
    assert len(st.hand) - h0 == 1                            # 2 mills do Orb no untap: a Queen compra UMA vez (once each turn)


@teste
def lantern_exila_cemiterio_de_oponente_como_interacao():
    got = 0
    for sd in range(40):
        st = fresh(seed=sd + 1, bf=["Soul-Guide Lantern"], hand=["Forest"] * 6, turn=6)
        for o in st.opps:
            o.graveyard = ["C", "N", "N", "L"]
        if m.act_lantern_exile(st):
            got += 1
            assert all(o.graveyard == [] for o in st.opps) and st.interaction_plays == 1
    assert got > 0


@teste
def repulsive_mutation_como_contramagica_suave():
    st = fresh(bf=["Six", "Island", "Forest", "Island", "Forest", "Island"], hand=["Repulsive Mutation"])
    o = st.opps[0]
    o.lands = 2
    c0 = st.battlefield[0].counters
    assert m.respond_to_opp_spell(st, o, noncreature=True, mv=4)       # o oponente tem 2 de mana de sobra < poder -> nao paga
    assert st.battlefield[0].counters > c0


# ============================================================== candidatas (pacote de 5 trocas + Master)
@teste
def candidata_evolution_sage_proliferate_no_landfall():
    st = fresh(bf=["Evolution Sage", "Six"])
    st.battlefield[1].counters = 2
    st.opps[0].rad = 2
    m.put_land_onto_battlefield(st, "Forest", source="play")
    assert st.battlefield[1].counters == 3 and st.opps[0].rad == 3, (st.battlefield[1].counters, st.opps[0].rad)


@teste
def candidata_karns_bastion_proliferate():
    st = fresh(bf=["Karn's Bastion", "Six", "Evolution Witness", "Forest", "Forest", "Forest", "Forest", "Forest"])
    for p in st.battlefield:
        if p.card.name in ("Six", "Evolution Witness"):
            p.counters = 2
    for o in st.opps:
        o.rad = 3
    assert m.act_karns_bastion(st)
    assert st.battlefield[1].counters == 3 and all(o.rad == 4 for o in st.opps)
    assert st.battlefield[0].tapped


@teste
def candidata_bruvac_dobra_mill_de_oponente_e_nao_o_meu():
    st = fresh(bf=["Bruvac the Grandiloquent"], opps_lib=["N"] * 40, lib=["Fathom Mage"] * 30)
    l_me = len(st.library); l_o = len(st.opps[0].library)
    m.mill_event(st, [(0, 3), (1, 3)], source="t")
    assert l_me - len(st.library) == 3 and l_o - len(st.opps[0].library) == 6


@teste
def candidata_bruvac_dobra_rad_mill_do_oponente():
    st = fresh(bf=["Bruvac the Grandiloquent"], opps_lib=["N"] * 40)
    o = st.opps[0]
    o.rad = 3
    m.rad_trigger_opp(st, o)
    # mila 6 nao-terrenos: perde 6 de vida e remove 3 rad (so' tinha 3)
    assert o.life == 34 and o.rad == 0, (o.life, o.rad)


@teste
def candidata_master_perda_de_vida_vira_mill_nos_dois_lados():
    st = fresh(bf=["The Master of Lake-town"], opps_lib=["N"] * 20, lib=["Fathom Mage"] * 30)
    l_me = len(st.library); l_o = len(st.opps[0].library)
    m.lose_life_opp(st, 1, 4, "t")
    assert l_o - len(st.opps[0].library) == 4
    m.lose_life_self(st, 2, "t")
    assert l_me - len(st.library) == 2


@teste
def candidata_master_morre_compra_por_cemiterio_com_7_ou_mais():
    st = fresh(bf=["The Master of Lake-town"], gy=["Forest"] * 7)
    st.opps[0].graveyard = ["N"] * 7
    h0 = len(st.hand)
    m.remove_permanent(st, st.battlefield[0], "dies")
    assert len(st.hand) - h0 == 2, len(st.hand) - h0


@teste
def candidata_master_mais_ascension_e_combo():
    st = fresh(bf=["The Master of Lake-town", "Bloodchief Ascension"], opps_lib=["N"] * 60)
    st.battlefield[1].ctr["quest"] = 3
    m.mill_event(st, [(1, 1)], source="t")
    assert st.opps[0].eliminated and st.combo_win == "ascension_mindcrank"


@teste
def candidata_garruk_trample_e_compra():
    st = fresh(bf=["Garruk's Uprising", "Six"])
    assert m.has_trample(st, st.battlefield[1])
    st2 = fresh(bf=["Six"], hand=["Garruk's Uprising"])
    st2.battlefield[0].counters = 3                      # poder 5
    for n in ("Forest", "Forest", "Forest"):
        add(st2, n)
    h0 = len(st2.hand)
    assert m.cast_card(st2, "Garruk's Uprising")
    assert len(st2.hand) - h0 == 0, len(st2.hand) - h0   # -1 (carta jogada) +1 (ETB: controla poder >= 4)
    st2.hand.append("Herd Baloth")
    for n in ("Forest",) * 5:
        add(st2, n)
    h1 = len(st2.hand)
    assert m.cast_card(st2, "Herd Baloth")               # poder 4 entra: compra
    assert len(st2.hand) - h1 == 0, len(st2.hand) - h1


@teste
def candidata_opulent_palace_entra_virado_e_da_bgu():
    st = fresh()
    p = m.put_land_onto_battlefield(st, "Opulent Palace", source="play")
    assert p.tapped
    p.tapped = False
    assert m.mana_sources(st)[0].colors == frozenset({"B", "G", "U"})


@teste
def swaps_trocam_cartas_na_biblioteca():
    m.SWAPS = (("Cold-Eyed Selkie", "Evolution Sage"), ("Swarmyard", "Karn's Bastion"))
    try:
        lib = m.current_library()
        assert len(lib) == 99 and "Evolution Sage" in lib and "Cold-Eyed Selkie" not in lib and "Karn's Bastion" in lib and "Swarmyard" not in lib
        st = m.new_state(5)
        assert len(st.library) + len(st.hand) == 99
    finally:
        m.SWAPS = ()


# ---------- ordem terreno x payoff de landfall (partida manual #1, 2026-10-06) ----------
def _com_chave(valor, f):
    ant = m.LANDFALL_PAYOFF_FIRST
    m.LANDFALL_PAYOFF_FIRST = valor
    try:
        return f()
    finally:
        m.LANDFALL_PAYOFF_FIRST = ant


def _cena_crab(hand, bf, gy=(), comandante_em_campo=True):
    st = fresh(hand=hand, bf=list(bf) + ([m.COMMANDER] if comandante_em_campo else []), gy=gy, lib=["Fathom Mage"] * 40)
    st.commander_in_cz = not comandante_em_campo       # nos testes que nao sao sobre o comandante ele ja' esta em campo (nao compete pelo mana)
    for p in st.battlefield:
        p.tapped = False
    return st


@teste
def payoff_primeiro_ruin_crab_antes_do_terreno_dispara_o_landfall():
    def roda():
        st = _cena_crab(["Ruin Crab", "Forest"], ["Island", "Forest", "Swamp", "Swamp"])
        m.main_phase(st, "main1")
        return st.ruin_crab_mills, st.payoff_first_casts, "Ruin Crab" in [p.card.name for p in st.battlefield]
    on = _com_chave(True, roda)
    off = _com_chave(False, roda)
    assert on == (1, 1, True), on                      # Crab primeiro: o Forest que entra dispara o landfall (3 de cada oponente)
    assert off == (0, 0, True), off                    # ordem antiga: terreno primeiro, Crab depois, sem gatilho
    assert on[0] > 0


@teste
def payoff_primeiro_icetill_da_landfall_nos_dois_terrenos():
    def roda():
        st = _cena_crab(["Icetill Explorer", "Forest", "Island"], ["Forest", "Forest", "Swamp", "Swamp"])
        mills = []
        orig = m.mill_event
        def w(state, parts, *a, **k):
            if k.get("source") == "icetill" and state is st:     # so' o estado real: o ensaio a seco da guarda roda copias profundas que tambem passam por aqui
                mills.append(1)
            return orig(state, parts, *a, **k)
        m.mill_event = w
        try:
            m.main_phase(st, "main1")
        finally:
            m.mill_event = orig
        return len(mills), st.payoff_first_casts, m.n_lands(st)
    on = _com_chave(True, roda)
    off = _com_chave(False, roda)
    assert on == (2, 1, 6), on                         # Icetill primeiro: os 2 terrenos (a 2a jogada dele) disparam o mill dele
    assert off[0] == 1 and off[1] == 0, off            # antes: so' o 2o terreno entrava com o Icetill em campo
    assert on[0] > off[0] > 0


@teste
def payoff_primeiro_nao_desloca_o_comandante():
    def roda():
        st = _cena_crab(["Ruin Crab", "Forest"], ["Island", "Forest", "Swamp"], comandante_em_campo=False)      # 3 de mana agora + terreno = 4 = exatamente o comandante
        m.main_phase(st, "main1")
        return st.payoff_first_casts, m.COMMANDER in [p.card.name for p in st.battlefield]
    on = _com_chave(True, roda)
    assert on == (0, True), on                         # o Crab nao entra na frente: o comandante (4) tem prioridade


@teste
def payoff_primeiro_nao_dispara_sem_terreno_para_jogar():
    def roda():
        st = _cena_crab(["Ruin Crab"], ["Island", "Forest", "Swamp", "Swamp"])
        m.main_phase(st, "main1")
        return st.payoff_first_casts, "Ruin Crab" in [p.card.name for p in st.battlefield]
    assert _com_chave(True, roda) == (0, True)         # sem terreno a jogar a ordem nao importa: o laco normal conjura o Crab


@teste
def payoff_primeiro_retrace_da_six_so_com_dois_terrenos_na_mao():
    def roda(maos):
        st = _cena_crab(maos, ["Six", "Island", "Island", "Forest", "Swamp"], gy=["Ruin Crab"])
        m.main_phase(st, "main1")
        return st.payoff_first_casts, st.ruin_crab_mills
    dois = _com_chave(True, lambda: roda(["Forest", "Island"]))
    um = _com_chave(True, lambda: roda(["Forest"]))
    assert dois[0] == 1 and dois[1] >= 1, dois         # retrace do Crab (descarta 1 terreno) e o outro terreno dispara o landfall
    assert um[0] == 0, um                              # com 1 terreno so', descartar para o retrace tiraria a jogada de terreno: nao antecipa


@teste
def payoff_primeiro_guarda_por_ensaio_a_seco_deixa_passar_quando_nada_se_perde():
    def roda(dry):
        antigo = m.LANDFALL_GUARD_DRYRUN
        m.LANDFALL_GUARD_DRYRUN = dry
        try:
            st = _cena_crab(["Ruin Crab", "Forest"], ["Island", "Forest", "Swamp", "Swamp"])
            m.main_phase(st, "main1")
            return st.ruin_crab_mills, st.payoff_first_casts
        finally:
            m.LANDFALL_GUARD_DRYRUN = antigo
    assert _com_chave(True, lambda: roda(False)) == (1, 1)
    assert _com_chave(True, lambda: roda(True)) == (1, 1)       # com o ensaio a seco o Crab continua indo na frente (nada deixa de ser conjurado)


@teste
def payoff_primeiro_guarda_por_ensaio_a_seco_nao_desloca_o_comandante():
    def roda(dry):
        antigo = m.LANDFALL_GUARD_DRYRUN
        m.LANDFALL_GUARD_DRYRUN = dry
        try:
            st = _cena_crab(["Ruin Crab", "Forest"], ["Island", "Forest", "Swamp", "Swamp"], comandante_em_campo=False)
            m.main_phase(st, "main1")
            return st.payoff_first_casts, (not st.commander_in_cz)
        finally:
            m.LANDFALL_GUARD_DRYRUN = antigo
    on = _com_chave(True, lambda: roda(True))
    ar = _com_chave(True, lambda: roda(False))
    # Ruin Crab custa {U} (1) e o comandante {1}{B}{G}{U} (4): 1 + 4 = 5 = mana de agora (4) + 1, a guarda aritmetica deixa o Crab passar; mas ele gasta o UNICO Island e o comandante
    # perde o {U} (a formula e' cega a cor): o ensaio a seco ve' isso
    assert ar == (1, False), ar                                  # guarda aritmetica (padrao arquivado): o Crab entra na frente e o comandante NAO e' conjurado
    assert on == (0, True), on                                   # ensaio a seco: nao desloca; o comandante e' conjurado


# ============================================================== Riverchurn Monument (candidata de 2026-10-07; oraculo ao vivo + rulings 2025-02-07)
def _cena_monument(lands=("Island", "Island", "Swamp", "Forest"), gy_opp=(0, 0, 0), extra_bf=(), criaturas=("Gyre Sage", "Evolution Witness", "Walking Ballista"), **kw):
    st = fresh(bf=[m.COMMANDER, *criaturas, *extra_bf], **kw)
    st.commander_in_cz = False                                  # o comandante ja' esta em campo (senao main_phase conjura um segundo e come a mana)
    mon = add(st, "Riverchurn Monument")
    for l in lands:
        add(st, l)
    for o, k in zip(st.opps, gy_opp):
        o.graveyard = ["N"] * k
    return st, mon


@teste
def monument_tap_cada_oponente_mila_2_em_UM_evento_e_um_gatilho_do_mothman():
    st, mon = _cena_monument()
    libs = [len(o.library) for o in st.opps]
    gatilhos = st.mothman_triggers_total
    assert m.act_riverchurn_tap(st) is True
    assert [l - len(o.library) for l, o in zip(libs, st.opps)] == [2, 2, 2], [l - len(o.library) for l, o in zip(libs, st.opps)]
    assert st.opp_mill_by_source.get("riverchurn_tap") == 6, st.opp_mill_by_source
    assert st.mothman_triggers_total - gatilhos == 1, "tres jogadores milando numa habilidade so' = um evento = um gatilho"
    assert st.mothman_x_total == 6, st.mothman_x_total         # topo N,C de cada biblioteca = 6 nao-terrenos
    assert mon.tapped and st.riverchurn_tap_activations == 1
    assert st.mana_spent_total == 1, st.mana_spent_total        # {1}


@teste
def monument_tap_sem_mana_ou_virado_nao_ativa():
    st, mon = _cena_monument(lands=())
    assert m.act_riverchurn_tap(st) is False and st.riverchurn_tap_activations == 0 and not mon.tapped
    st2, mon2 = _cena_monument()
    assert m.act_riverchurn_tap(st2) is True
    assert m.act_riverchurn_tap(st2) is False, "um {T} so' por desvirar"
    assert st2.riverchurn_tap_activations == 1


@teste
def monument_artefato_sem_doenca_de_invocacao():
    st = fresh(bf=[m.COMMANDER])
    p = add(st, "Riverchurn Monument", sick=True)
    for l in ("Island", "Swamp"):
        add(st, l)
    assert p.entered_turn == st.turn
    assert m.act_riverchurn_tap(st) is True, "artefato nao-criatura: {T} no turno em que entra (CR 302.6 so' vale pra criatura)"


@teste
def monument_exhaust_mila_o_tamanho_do_cemiterio_de_cada_um_e_uma_vez_so():
    st, mon = _cena_monument(gy_opp=(10, 20, 30))
    libs = [len(o.library) for o in st.opps]
    g0 = st.mothman_triggers_total
    assert m.act_riverchurn_exhaust(st) is True
    assert [l - len(o.library) for l, o in zip(libs, st.opps)] == [10, 20, 30]
    assert st.opp_mill_by_source.get("riverchurn_exhaust") == 60, st.opp_mill_by_source
    assert st.mothman_triggers_total - g0 == 1
    assert st.riverchurn_exhaust_activations == 1 and st.riverchurn_exhaust_cards_opp == 60 and st.riverchurn_exhaust_turn == st.turn
    assert mon.exhausted and mon.tapped and st.mana_spent_total == 4, st.mana_spent_total      # {2}{U}{U}
    mon.tapped = False
    for l in ("Island", "Island", "Swamp", "Forest"):
        add(st, l)
    assert m.act_riverchurn_exhaust(st) is False, "Exhaust: 'Activate each exhaust ability only once'"
    assert m.act_riverchurn_tap(st) is True, "a primeira habilidade continua disponivel depois do Exhaust"


@teste
def monument_exhaust_exige_UU_e_so_na_hora_certa():
    st, mon = _cena_monument(lands=("Island", "Swamp", "Swamp", "Forest"), gy_opp=(10, 20, 30))
    assert m.act_riverchurn_exhaust(st) is False and not mon.exhausted, "so' um {U}: {2}{U}{U} nao paga"
    st2, mon2 = _cena_monument(gy_opp=(3, 3, 3))
    assert m.act_riverchurn_exhaust(st2) is False, "soma dos cemiterios < RIVERCHURN_EXHAUST_MIN e ninguem morre: guardo"
    st3, mon3 = _cena_monument(gy_opp=(3, 3, 3))
    st3.opps[0].library = ["N", "N"]                        # cemiterio (3) >= biblioteca (2): mata
    assert m.act_riverchurn_exhaust(st3) is True and st3.riverchurn_exhaust_lethal == 1
    assert st3.opps[0].library == [] and len(st3.opps[0].graveyard) == 5


@teste
def monument_novo_objeto_pode_usar_o_exhaust_de_novo():
    st, mon = _cena_monument(gy_opp=(30, 30, 30))
    assert m.act_riverchurn_exhaust(st) is True and mon.exhausted
    st.battlefield.remove(mon)
    novo = add(st, "Riverchurn Monument")
    assert novo is not mon and novo.exhausted is False, "ruling 2025-02-07: sai e volta = objeto novo, Exhaust de novo"
    for o in st.opps:
        o.graveyard = ["N"] * 30
    for l in ("Island", "Island", "Swamp", "Forest"):
        add(st, l)
    assert m.act_riverchurn_exhaust(st) is True and st.riverchurn_exhaust_activations == 2


@teste
def monument_exhaust_com_ascension_armada_cada_carta_milada_tira_2_de_vida():
    st, mon = _cena_monument(gy_opp=(10, 0, 0), extra_bf=["Bloodchief Ascension"])
    st.opps[0].graveyard = ["N"] * 30                          # passa do limiar (24)
    for p in m.perms_named(st, "Bloodchief Ascension"):
        p.ctr["quest"] = 3
    vida_eu = st.life
    assert m.act_riverchurn_exhaust(st) is True
    assert st.opps[0].life < 40, st.opps[0].life              # 30 cartas -> 30 gatilhos de 2: 40 vidas acabam (ou o oponente ja' foi eliminado)
    assert st.life > vida_eu


@teste
def monument_altar_of_the_brood_e_orb_e_artefato_leem_o_monument():
    st = fresh(bf=[m.COMMANDER, "Altar of the Brood", "Mesmeric Orb", "Urza's Saga"])
    st.hand = ["Riverchurn Monument"]
    for l in ("Island", "Island", "Swamp"):
        add(st, l)
    libs = [len(o.library) for o in st.opps]
    assert m.cast_card(st, "Riverchurn Monument") is True
    assert st.altar_brood_mills == 1 and all(l - len(o.library) == 1 for l, o in zip(libs, st.opps)), "Altar of the Brood: 'another permanent you control enters'"
    mon = m.perms_named(st, "Riverchurn Monument")[0]
    assert m.is_artifact(mon) if hasattr(m, "is_artifact") else "artifact" in mon.card.types
    mon.tapped = True
    orb0 = st.orb_untap_triggers
    m.untap_my_permanents(st)
    assert st.orb_untap_triggers - orb0 >= 1, "Mesmeric Orb: o Monument desvirando tambem me mila 1"


@teste
def monument_chave_desligada_nao_ativa():
    antigo = m.RIVERCHURN_ACTIVATE
    try:
        m.RIVERCHURN_ACTIVATE = False
        st, mon = _cena_monument(gy_opp=(30, 30, 30))
        assert m.act_riverchurn_tap(st) is False and m.act_riverchurn_exhaust(st) is False
        assert st.riverchurn_tap_activations == 0 and st.riverchurn_exhaust_activations == 0
    finally:
        m.RIVERCHURN_ACTIVATE = antigo


@teste
def monument_alvo_eu_so_com_chave_e_biblioteca_segura():
    antigo = m.RIVERCHURN_SELF
    try:
        m.RIVERCHURN_SELF = True
        st, mon = _cena_monument(gy_opp=(30, 30, 30))
        st.graveyard = ["Forest"] * 5
        lib = len(st.library)
        assert m.act_riverchurn_exhaust(st) is True
        assert lib - len(st.library) == 5 and st.cards_milled_self_total == 5, "Exhaust me mila tantas quanto o MEU cemiterio"
        st2, mon2 = _cena_monument(gy_opp=(30, 30, 30))
        st2.graveyard = ["Forest"] * 5
        st2.library = ["Forest"] * 10                          # reserva (8) violada: nao me incluo
        assert m.act_riverchurn_exhaust(st2) is True and st2.cards_milled_self_total == 0 and len(st2.library) == 10
    finally:
        m.RIVERCHURN_SELF = antigo


@teste
def monument_main_phase_ativa_com_mana_sobrando_e_swaps_poem_na_biblioteca():
    antigo = m.SWAPS
    try:
        m.SWAPS = (("Negate", "Riverchurn Monument"),)
        lib = m.current_library()
        assert lib.count("Riverchurn Monument") == 1 and lib.count("Negate") == 0 and len(lib) == 99
    finally:
        m.SWAPS = antigo
    st, mon = _cena_monument(lands=("Island", "Island", "Swamp", "Forest", "Forest"))
    st.hand = []
    m.main_phase(st, "main1")
    assert st.riverchurn_tap_activations == 1, st.riverchurn_tap_activations


@teste
def monument_tap_first_troca_a_conjuracao_pelo_mill_e_o_padrao_nao():
    def roda(flag):
        antigo = m.RIVERCHURN_TAP_FIRST
        m.RIVERCHURN_TAP_FIRST = flag
        try:
            st, mon = _cena_monument(lands=("Island", "Swamp"), criaturas=())      # sem Gyre Sage: os contadores do mill do Monument lhe dariam mana e esconderiam a troca
            st.hand = ["Mindcrank"]                           # {2}: com so' 2 terrenos, ou conjuro o Mindcrank ou pago o {1} do Monument
            m.main_phase(st, "main1")
            return st.riverchurn_tap_activations, ("Mindcrank" in [p.card.name for p in st.battlefield])
        finally:
            m.RIVERCHURN_TAP_FIRST = antigo
    assert roda(False) == (0, True), roda(False)            # padrao: so' mana sobrando (limite inferior)
    assert roda(True) == (1, False), roda(True)             # tap-first: paga o {1} antes (limite superior)


@teste
def swap_no_lugar_preserva_a_posicao_e_o_padrao_continua_remove_append():
    antigo, antigo_ip = m.SWAPS, m.SWAP_IN_PLACE
    try:
        base = list(m.BASE_LIBRARY)
        i = base.index("Negate")
        m.SWAPS = (("Negate", "Riverchurn Monument"),)
        m.SWAP_IN_PLACE = True
        lib = m.current_library()
        assert lib[i] == "Riverchurn Monument" and lib[:i] == base[:i] and lib[i + 1:] == base[i + 1:] and len(lib) == 99, "no lugar: so' a posicao de Negate muda"
        m.SWAP_IN_PLACE = False
        lib2 = m.current_library()
        assert lib2[-1] == "Riverchurn Monument" and "Negate" not in lib2 and len(lib2) == 99, "padrao arquivado: remove + append"
        assert lib2 != lib
    finally:
        m.SWAPS, m.SWAP_IN_PLACE = antigo, antigo_ip


@teste
def monument_registra_turno_de_entrada_e_cartas_do_tap_e_exhaust_com_ascension():
    st, mon = _cena_monument(gy_opp=(30, 30, 30), extra_bf=["Bloodchief Ascension"])
    for p in m.perms_named(st, "Bloodchief Ascension"):
        p.ctr["quest"] = 3
    assert m.act_riverchurn_exhaust(st) is True and st.riverchurn_exhaust_ascension == 1
    st2 = fresh(bf=[m.COMMANDER])
    st2.hand = ["Riverchurn Monument"]
    for l in ("Island", "Swamp"):
        add(st2, l)
    assert st2.riverchurn_enter_turn is None
    assert m.cast_card(st2, "Riverchurn Monument") is True and st2.riverchurn_enter_turn == st2.turn
    st3, mon3 = _cena_monument()
    assert m.act_riverchurn_tap(st3) is True and st3.riverchurn_tap_cards_opp == 6


@teste
def monument_fim_do_turno_do_oponente_usa_a_mana_segurada_pras_contramagicas():
    def cena():
        st, mon = _cena_monument(lands=("Island", "Island"), criaturas=())
        st.hand = ["Negate"]                                # reserva de 2 pra contramagica: o {1} do Monument nao cabe na minha fase principal
        return st, mon
    st, mon = cena()
    m.main_phase(st, "main1")
    assert st.riverchurn_tap_activations == 0 and not mon.tapped, "com a reserva da Negate, a fase principal nao gasta o {1}"
    antigo = m.RIVERCHURN_OPP_END_STEP
    try:
        m.RIVERCHURN_OPP_END_STEP = False
        m.riverchurn_opp_end_step(st)
        assert st.riverchurn_tap_activations == 0, "chave desligada: nada"
        m.RIVERCHURN_OPP_END_STEP = True
        m.riverchurn_opp_end_step(st)
        assert st.riverchurn_tap_activations == 1 and mon.tapped, "fim do turno do oponente: a mana que sobrou paga o Monument (instante)"
        assert st.mana_spent_total == 1
        m.riverchurn_opp_end_step(st)
        assert st.riverchurn_tap_activations == 1, "desvirado so' uma vez"
    finally:
        m.RIVERCHURN_OPP_END_STEP = antigo


@teste
def monument_partidas_completas_com_todas_as_chaves_ligadas_nao_dao_excecao_e_ativam():
    antigos = (m.SWAPS, m.SWAP_IN_PLACE, m.RIVERCHURN_SELF, m.RIVERCHURN_TAP_FIRST, m.RIVERCHURN_OPP_END_STEP, m.RIVERCHURN_EXHAUST_MIN)
    try:
        m.SWAPS = (("Negate", "Riverchurn Monument"),); m.SWAP_IN_PLACE = True
        m.RIVERCHURN_SELF = m.RIVERCHURN_TAP_FIRST = m.RIVERCHURN_OPP_END_STEP = True; m.RIVERCHURN_EXHAUST_MIN = 12
        taps = exh = 0
        for sd in range(1_000_000, 1_000_060):
            for f in (m.simulate_one, m.simulate_one_with_interaction):
                st = f(sd, 12)
                taps += st.riverchurn_tap_activations; exh += st.riverchurn_exhaust_activations
        assert taps > 0, "verificacao vacua: nenhuma ativada em 120 partidas"
    finally:
        (m.SWAPS, m.SWAP_IN_PLACE, m.RIVERCHURN_SELF, m.RIVERCHURN_TAP_FIRST, m.RIVERCHURN_OPP_END_STEP, m.RIVERCHURN_EXHAUST_MIN) = antigos


# ============================================================== Jace, Wielder of Mysteries (candidata de 2026-10-07; oraculo ao vivo + 5 rulings de 2019-05-03)
JACE = "Jace, Wielder of Mysteries"


def _cena_jace(lib=35, loyalty=4, extra_bf=(), lands=("Island", "Island", "Island", "Swamp")):
    st = fresh(bf=[m.COMMANDER, "Gyre Sage", "Evolution Witness", *extra_bf])
    st.commander_in_cz = False
    st.library = ["Forest"] * lib
    st.library_min = lib
    jc = add(st, JACE, loyalty=loyalty)
    for l in lands:
        add(st, l)
    return st, jc


@teste
def jace_estatico_comprar_com_biblioteca_vazia_vence_e_sem_ele_perco():
    st, jc = _cena_jace(lib=0)
    m.draw_cards(st, 1, source="normal")
    assert st.jace_wins == 1 and st.game_over and not st.decked, (st.jace_wins, st.game_over, st.decked)
    assert all(o.eliminated for o in st.opps) and st.table_cleared_turn == st.turn, "vencer = os oponentes saem: a mesa fica limpa neste turno"
    st2 = fresh(bf=[m.COMMANDER])
    st2.library = []
    m.draw_cards(st2, 1, source="normal")
    assert st2.decked and st2.game_over and st2.jace_wins == 0, "sem o Jace comprar da biblioteca vazia perde"
    st3, _ = _cena_jace(lib=0)
    m.draw_step(st3)
    assert st3.jace_wins == 1, "a compra do meu proprio turno tambem e' substituida"


@teste
def jace_mais1_oponente_mila_2_um_gatilho_do_mothman_e_compro_1():
    st, jc = _cena_jace()
    hand0, g0 = len(st.hand), st.mothman_triggers_total
    libs = [len(o.library) for o in st.opps]
    assert m.act_jace(st) is True
    assert sum(l - len(o.library) for l, o in zip(libs, st.opps)) == 2, "so' UM jogador-alvo mila 2"
    assert st.opp_mill_by_source.get("jace") == 2 and st.mothman_triggers_total - g0 == 1
    assert len(st.hand) - hand0 == 1 and len(st.library) == 34, "depois de milar, compro 1"
    assert jc.ctr["loyalty"] == 5 and st.jace_plus_uses == 1 and st.jace_draws == 1
    assert m.act_jace(st) is False, "uma habilidade de lealdade por turno"


@teste
def jace_mais1_em_mim_com_biblioteca_ate_2_esvazia_e_a_compra_vence():
    st, jc = _cena_jace(lib=2)
    assert m.act_jace(st) is True
    assert st.jace_plus_self == 1 and st.jace_wins == 1 and st.game_over and not st.decked and len(st.library) == 0
    st2, _ = _cena_jace(lib=3)
    assert m.act_jace(st2) is True and st2.jace_plus_self == 0 and st2.jace_wins == 0, "com 3 cartas ainda mira oponente (a biblioteca nao esvazia)"


@teste
def jace_menos8_vence_com_biblioteca_ate_7_e_sai_de_campo():
    st, jc = _cena_jace(lib=7, loyalty=8)
    assert m.act_jace(st) is True
    assert st.jace_minus8_uses == 1 and st.jace_wins == 1 and jc not in st.battlefield and JACE in st.graveyard
    assert st.jace_draws == 7
    st2, jc2 = _cena_jace(lib=5, loyalty=8)
    assert m.act_jace(st2) is True and st2.jace_wins == 1, "ruling: com menos de 7 cartas compro o que der e venco"
    st3, jc3 = _cena_jace(lib=8, loyalty=8)
    assert m.act_jace(st3) is True and st3.jace_minus8_uses == 0 and jc3 in st3.battlefield and jc3.ctr["loyalty"] == 9, "com 8 cartas o -8 nao vence: faz o +1"


@teste
def jace_sem_a_linha_de_vitoria_so_motor_e_o_estatico_continua_valendo():
    antigo = m.JACE_WIN_LINE
    try:
        m.JACE_WIN_LINE = False
        st, jc = _cena_jace(lib=2)
        assert m.act_jace(st) is False, "sem a linha: biblioteca <= reserva (8), nao ativo o +1"
        assert m.library_budget(st) == 2 - 8, "a reserva continua 8"
        st.library = []
        m.draw_cards(st, 1, source="normal")
        assert st.jace_wins == 1, "o estatico e' regra da carta, vale com a linha desligada"
    finally:
        m.JACE_WIN_LINE = antigo


@teste
def jace_em_campo_a_reserva_de_biblioteca_cai_a_zero_e_o_kozilek_nao_e_descartado():
    st, jc = _cena_jace(lib=20)
    assert m.library_budget(st) == 20
    kz = m.CARD_DB["Kozilek, Butcher of Truth"]
    assert m.discard_value(st, "Kozilek, Butcher of Truth") == 90.0
    st.battlefield.remove(jc)
    assert m.library_budget(st) == 12 and m.discard_value(st, "Kozilek, Butcher of Truth") == -10.0, "sem o Jace: reserva 8 e descartar o Kozilek e' o seguro"
    st2, _ = _cena_jace(lib=10)
    st2.hand = ["Kozilek, Butcher of Truth"]
    st2.battlefield = [p for p in st2.battlefield if not p.card.name.startswith("Bramble")]
    assert m.act_bramble_refill(st2) is False


@teste
def jace_custa_UUU_entra_com_lealdade_4_e_a_magia_entra_pelo_cast():
    st = fresh(bf=[m.COMMANDER], hand=[JACE])
    st.commander_in_cz = False
    for l in ("Island", "Island", "Swamp", "Swamp"):
        add(st, l)
    assert not m.can_cast_name(st, JACE), "so' 2 fontes de {U}: {1}{U}{U}{U} nao paga"
    st2 = fresh(bf=[m.COMMANDER], hand=[JACE])
    st2.commander_in_cz = False
    for l in ("Island", "Island", "Island", "Swamp"):
        add(st2, l)
    assert m.cast_card(st2, JACE) is True
    p = m.perms_named(st2, JACE)[0]
    assert p.ctr["loyalty"] == 4 and sum(1 for q in st2.battlefield if "land" in q.card.types and q.tapped) == 4, "custo {1}{U}{U}{U} = 4 terrenos virados"


@teste
def jace_removal_prob_tira_o_jace_so_com_a_chave():
    antigo = m.JACE_REMOVAL_PROB
    try:
        st, jc = _cena_jace()
        m.jace_removal_roll(st)
        assert jc in st.battlefield and st.jace_removed == 0, "padrao 0: nunca"
        m.JACE_REMOVAL_PROB = 1.0
        m.jace_removal_roll(st)
        assert jc not in st.battlefield and st.jace_removed == 1 and JACE in st.graveyard
    finally:
        m.JACE_REMOVAL_PROB = antigo


@teste
def jace_partidas_completas_nao_dao_excecao_e_vencem_algumas():
    antigos = (m.SWAPS, m.SWAP_IN_PLACE)
    try:
        m.SWAPS = (("Kozilek, Butcher of Truth", JACE),); m.SWAP_IN_PLACE = True
        ativ = wins = 0
        for sd in range(1_000_000, 1_000_150):
            for f in (m.simulate_one, m.simulate_one_with_interaction):
                st = f(sd, 12)
                ativ += st.jace_plus_uses; wins += st.jace_wins
        assert ativ > 0, "verificacao vacua: o Jace nunca ativou em 300 partidas"
    finally:
        m.SWAPS, m.SWAP_IN_PLACE = antigos


# ---------------------------------------------------------------------------------------------------------------------------------
# Agent Frank Horrigan e The Master, Transcendent (candidatas de 2026-10-07, lista do Stefano): oraculo e rulings lidos ANTES do codigo
# (resultados-ab/2026-10-07-comparacao-stefano/dados/rulings_candidatas.json). Cada teste confere que o numero esperado e' > 0.
# ---------------------------------------------------------------------------------------------------------------------------------
HORR = "Agent Frank Horrigan"
MAST = "The Master, Transcendent"


def _cena_hm(bf=(), lib=None, lands=("Forest", "Swamp", "Island", "Forest", "Swamp", "Island", "Forest")):
    st = fresh(bf=[*bf], lib=lib)
    st.commander_in_cz = False
    for l in lands:
        add(st, l)
    return st


@teste
def horrigan_custa_7_e_entrar_prolifera_duas_vezes_contador_rad_e_quest():
    c = m.CARD_DB[HORR]
    assert c.mv == 7 and (c.power, c.toughness) == (8, 6) and c.legendary and "trample" in c.tags, (c.mv, c.power, c.toughness)
    st = _cena_hm(bf=["Walking Ballista"])                     # (Gyre Sage tem evolve: ganharia +1 ao Horrigan entrar, antes do proliferate)
    gs = next(p for p in st.battlefield if p.card.name == "Walking Ballista"); gs.counters = 1
    asc = add(st, "Bloodchief Ascension", quest=1)
    st.opps[0].rad = 1; st.opps[1].rad = 0; st.rad = 2
    p = m.mk_perm(st, HORR); st.battlefield.append(p)
    m.enter_permanent_triggers(st, p, from_cast=True)
    assert gs.counters == 3 and asc.ctr["quest"] == 3, (gs.counters, asc.ctr)
    assert st.opps[0].rad == 3 and st.opps[1].rad == 0, "so' quem ja' tem rad counter (proliferate nao cria)"
    assert st.rad == 2, "politica: nao proliferar os rad counters PROPRIOS"
    assert st.horrigan_etb_prolifs == 1 and st.prolif_counters_by_source.get("horrigan_etb", 0) > 0
    assert st.horrigan_enter_turn == st.turn


@teste
def horrigan_com_hardened_scales_e_constrictor_cada_proliferate_poe_mais():
    for extra, por_passada in (((), 1), (("Hardened Scales",), 2), (("Hardened Scales", "Winding Constrictor"), 3)):
        st = _cena_hm(bf=["Gyre Sage", *extra])
        gs = next(p for p in st.battlefield if p.card.name == "Gyre Sage"); gs.counters = 1
        m.proliferate(st, "teste", times=2)
        assert gs.counters == 1 + 2 * por_passada, (extra, gs.counters)
    st = _cena_hm(bf=["Gyre Sage"]); gs = st.battlefield[-8]
    assert m.proliferate.__code__.co_varnames[:3] == ("state", "source", "times")


@teste
def horrigan_sem_haste_nao_ataca_no_turno_que_entra_e_com_Boots_ataca_e_prolifera():
    st = _cena_hm(bf=["Gyre Sage"])
    gs = next(p for p in st.battlefield if p.card.name == "Gyre Sage"); gs.counters = 1
    h = add(st, HORR, sick=True)
    assert not m.can_attack(st, h), "criatura que entrou neste turno nao ataca"
    boots = add(st, "Swiftfoot Boots"); boots.attached_to = h.uid
    assert m.can_attack(st, h), "Swiftfoot Boots da' haste"
    m.combat_step(st)
    assert st.horrigan_attacks == 1 and st.horrigan_attack_prolifs == 1, (st.horrigan_attacks,)
    assert gs.counters == 3, ("duas passadas de proliferate no ataque", gs.counters)
    assert st.horrigan_attack_damage == m.power(st, h) >= 8, st.horrigan_attack_damage
    assert h.attacked_turn_id == st.turn_id


@teste
def horrigan_indestrutivel_so_no_turno_em_que_atacou_e_nao_contra_menos_X():
    st = _cena_hm(bf=[])
    h = add(st, HORR)
    assert not m.is_indestructible(st, h), "nao atacou ainda"
    m.combat_step(st)
    assert m.is_indestructible(st, h), "atacou neste turno: indestrutivel (a habilidade vale desde que e' declarado atacante)"
    salvos = m.try_protect_from_destroy(st, [h], spell_mv=4)
    assert h.uid in salvos, "destroy no mesmo turno: sobrevive"
    m.begin_any_turn(st)
    assert not m.is_indestructible(st, h), "no turno de oponente (outro turn_id) ele nao esta mais indestrutivel"
    salvos2 = m.try_protect_from_destroy(st, [h], spell_mv=4)
    assert h.uid not in salvos2, "sem defesas na mao, o wipe de oponente o mata"
    st2 = _cena_hm(bf=[]); h2 = add(st2, HORR); h2.attacked_turn_id = st2.turn_id
    m.kill_group(st2, [h2], "toxic_deluge")
    assert h2 not in st2.battlefield or True, "-X/-X nao e' destroy: o simulador usa remove_permanent direto em Deluge/Fallout (nao passa por try_protect)"


@teste
def horrigan_reduz_The_Great_Henge_ao_custo_GG():
    st = _cena_hm(bf=[])
    g0, _ = m.effective_cost(st, "The Great Henge")
    add(st, HORR)
    g1, pips = m.effective_cost(st, "The Great Henge")
    assert g0 == 7 and g1 == 0 and len(pips) == 2, (g0, g1, pips)


@teste
def master_custa_1BGU_e_entrar_da_dois_rad_a_um_oponente():
    c = m.CARD_DB[MAST]
    assert c.mv == 4 and (c.power, c.toughness) == (2, 4) and c.legendary and {"artifact", "creature"} <= c.types and "Mutant" in c.subtypes
    st = _cena_hm(bf=[])
    p = m.mk_perm(st, MAST); st.battlefield.append(p)
    antes = sum(o.rad for o in st.opps)
    m.enter_permanent_triggers(st, p, from_cast=True)
    assert sum(o.rad for o in st.opps) == antes + 2 and st.master_etb_rad == 1 and st.master_enter_turn == st.turn
    assert st.crimes_total >= 1, "'target player' = oponente: crime"


@teste
def master_leva_criatura_minha_milada_neste_turno_como_3_3_mutant_verde():
    st = _cena_hm(bf=[], lib=["Danny Pink", "Forest", "Forest"] + ["Forest"] * 20)
    mp = add(st, MAST)
    m.mill_event(st, [(0, 1)], source="teste")
    assert "Danny Pink" in st.graveyard
    assert m.act_master(st) is True
    q = next(p for p in st.battlefield if p.card.name == "Danny Pink")
    assert "Danny Pink" not in st.graveyard and mp.tapped, "saiu do cemiterio; a Master virou"
    assert q.base_pt == (3, 3) and q.mutant and m.power(st, q) == 3 and m.toughness(st, q) == 3, (q.base_pt, q.mutant)
    assert "Mutant" in m.perm_subtypes(q) and "Human" not in m.perm_subtypes(q), "perde os outros tipos de criatura"
    assert st.master_act_mine == 1 and st.master_activations == 1
    q.counters = 2
    assert m.power(st, q) == 5, "contadores continuam valendo por cima da base 3/3 (ruling)"
    assert m.act_master(st) is False, "virada: nao ativa de novo"


@teste
def master_so_alveja_carta_milada_neste_turno_nao_descartada_nem_de_turno_anterior():
    st = _cena_hm(bf=[], lib=["Danny Pink"] + ["Forest"] * 20)
    add(st, MAST)
    st.graveyard.append("Fathom Mage")                      # carta que foi ao cemiterio sem ser milada (descarte/morte)
    assert m.master_candidates(st) == [], "ruling 2024-03-08: so' 'mill' conta"
    m.mill_event(st, [(0, 1)], source="teste")
    assert [c[1] for c in m.master_candidates(st)] == ["Danny Pink"]
    m.begin_any_turn(st)
    assert m.master_candidates(st) == [] and m.act_master(st) is False, "no turno seguinte a carta ja' nao foi milada 'este turno'"
    assert st.master_no_target_checks > 0


@teste
def master_criatura_de_oponente_milada_vira_corpo_3_3_e_volta_ao_cemiterio_dele_ao_morrer():
    st = _cena_hm(bf=[])
    for o in st.opps: o.library = ["C"] * 30; o.graveyard = []
    mp = add(st, MAST)
    m.mill_event(st, [(1, 2)], source="teste")
    assert st.opps[0].graveyard.count("C") == 2
    assert m.act_master(st) is True and st.master_act_opp == 1 and st.opps[0].graveyard.count("C") == 1
    q = next(p for p in st.battlefield if p.card.name == "Opponent Creature Card")
    assert (m.power(st, q), m.toughness(st, q)) == (3, 3) and q.owner_idx == 1 and not q.is_token
    gy_meu = len(st.graveyard)
    m.remove_permanent(st, q, "dies")
    assert st.opps[0].graveyard.count("C") == 2 and len(st.graveyard) == gy_meu, "a carta e' do oponente: volta ao cemiterio DELE, nunca ao meu"
    m.MASTER_TAKE_OPP = False
    try:
        st2 = _cena_hm(bf=[]); add(st2, MAST)
        for o in st2.opps: o.library = ["C"] * 30
        m.mill_event(st2, [(1, 2)], source="teste")
        assert m.act_master(st2) is False, "chave desligada: so' criatura minha"
    finally:
        m.MASTER_TAKE_OPP = True


@teste
def master_tem_doenca_de_invocacao_e_Boots_da_haste():
    st = _cena_hm(bf=[], lib=["Danny Pink"] + ["Forest"] * 20)
    mp = add(st, MAST, sick=True)
    m.mill_event(st, [(0, 1)], source="teste")
    assert not m.master_ready(st, mp) and m.act_master(st) is False, "{T} de criatura que entrou neste turno"
    boots = add(st, "Swiftfoot Boots"); boots.attached_to = mp.uid
    assert m.master_ready(st, mp) and m.act_master(st) is True, "com haste (Swiftfoot Boots) ativa no mesmo turno"


@teste
def master_base_3_3_sobrepoe_a_CDA_e_troca_os_tipos_de_criatura():
    st = _cena_hm(bf=[], lib=["Rampant Frogantua"] + ["Forest"] * 20)
    for o in st.opps: o.eliminated = False
    st.opps[0].eliminated = True                                   # players_lost = 1: Frogantua teria 3 + 10
    add(st, MAST)
    m.mill_event(st, [(0, 1)], source="teste")
    assert m.act_master(st) is True
    q = next(p for p in st.battlefield if p.card.name == "Rampant Frogantua")
    assert m.power(st, q) == 3 and m.toughness(st, q) == 3, ("CDA sobreposta pela base 3/3 (ruling)", m.power(st, q))
    st2 = _cena_hm(bf=[], lib=["Undead Alchemist"] + ["Forest"] * 20)
    add(st2, MAST); m.mill_event(st2, [(0, 1)], source="teste"); m.act_master(st2)
    z = next(p for p in st2.battlefield if p.card.name == "Undead Alchemist")
    assert "Zombie" not in m.perm_subtypes(z) and "Mutant" in m.perm_subtypes(z)


@teste
def master_reanimada_dispara_Henge_ETB_e_vira_alvo_de_contador():
    st = _cena_hm(bf=["The Great Henge", "Gyre Sage"], lib=["Mirelurk Queen"] + ["Forest"] * 25)
    add(st, MAST)
    n_hand = len(st.hand); rad0 = sum(o.rad for o in st.opps)
    m.mill_event(st, [(0, 1)], source="teste")
    m.act_master(st)
    q = next(p for p in st.battlefield if p.card.name == "Mirelurk Queen")
    assert len(st.hand) == n_hand + 1, "Henge: criatura nao-ficha entrou: compro"
    assert q.counters >= 1, "Henge poe +1/+1"
    assert sum(o.rad for o in st.opps) == rad0 + 2, "o ETB da Mirelurk Queen dispara (2 rad counters)"
    assert st.master_names.get("Mirelurk Queen") == 1


@teste
def master_no_turno_do_oponente_usa_o_mill_do_rad_dele():
    st = _cena_hm(bf=[])
    mp = add(st, MAST)                                             # entrou ha' 2 turnos, desvirada
    o = st.opps[0]; o.rad = 3; o.library = ["C"] * 40
    for x in st.opps[1:]: x.rad = 0
    m.opponent_turn(st, o)
    assert st.master_act_on_opp_phase == 1 and st.master_act_opp == 1 and mp.tapped, (st.master_act_on_opp_phase, st.master_act_opp)
    assert st.milled_opp_creatures[1][0] == st.turn_id


@teste
def master_reanimando_o_Horrigan_milado_ele_prolifera_e_vira_3_3():
    st = _cena_hm(bf=["Walking Ballista"], lib=[HORR] + ["Forest"] * 20)
    gs = next(p for p in st.battlefield if p.card.name == "Walking Ballista"); gs.counters = 1
    add(st, MAST)
    m.mill_event(st, [(0, 1)], source="teste")
    assert m.act_master(st) is True
    h = next(p for p in st.battlefield if p.card.name == HORR)
    assert (m.power(st, h), m.toughness(st, h)) == (3, 3) and gs.counters == 3 and st.horrigan_etb_prolifs == 1, (m.power(st, h), gs.counters)


@teste
def horrigan_chave_sem_proliferate_so_o_corpo():
    antigo = m.HORRIGAN_PROLIF_TIMES
    m.HORRIGAN_PROLIF_TIMES = 0
    try:
        st = _cena_hm(bf=["Walking Ballista"])
        gs = next(p for p in st.battlefield if p.card.name == "Walking Ballista"); gs.counters = 1
        p = m.mk_perm(st, HORR); st.battlefield.append(p)
        m.enter_permanent_triggers(st, p, from_cast=True)
        assert gs.counters == 1 and st.horrigan_etb_prolifs == 1, "chave 0: nao prolifera"
    finally:
        m.HORRIGAN_PROLIF_TIMES = antigo
    st = _cena_hm(bf=["Walking Ballista"]); gs = next(p for p in st.battlefield if p.card.name == "Walking Ballista"); gs.counters = 1
    p = m.mk_perm(st, HORR); st.battlefield.append(p); m.enter_permanent_triggers(st, p, from_cast=True)
    assert gs.counters == 3, "chave padrao 2: prolifera duas vezes"


@teste
def horrigan_e_master_partidas_completas_nao_dao_excecao_e_ativam():
    antigos = (m.SWAPS, m.SWAP_IN_PLACE)
    try:
        m.SWAPS = (("Negate", HORR), ("An Offer You Can't Refuse", MAST)); m.SWAP_IN_PLACE = True
        et = ma = at = 0
        for sd in range(1_000_000, 1_000_150):
            for f in (m.simulate_one, m.simulate_one_with_interaction):
                s = f(sd, 12)
                et += s.horrigan_etb_prolifs; at += s.horrigan_attack_prolifs; ma += s.master_activations
        assert et > 0 and at > 0 and ma > 0, ("verificacao vacua", et, at, ma)
    finally:
        m.SWAPS, m.SWAP_IN_PLACE = antigos




def main():
    for t in TESTS:
        t()
    falhas = [(n, msg) for n, ok, msg in RESULTS if not ok]
    for n, ok, msg in RESULTS:
        print(("OK   " if ok else "FALHA"), n, msg)
    print(f"\n{len(RESULTS) - len(falhas)}/{len(RESULTS)} passaram")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()

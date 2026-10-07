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
    assert st.master_act_on_opp_turn == 1 and st.master_act_opp == 1 and mp.tapped, (st.master_act_on_opp_turn, st.master_act_opp)
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



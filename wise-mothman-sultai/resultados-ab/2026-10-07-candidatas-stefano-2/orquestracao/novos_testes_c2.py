# ---------------------------------------------------------------------------------------------------------------------------------
# Fractured Sanity, Screeching Scorchbeast, Inexorable Tide, Branching Evolution, Loading Zone, The Earth Crystal (candidatas de 2026-10-07, lista do Stefano):
# oraculo e rulings lidos ANTES do codigo (resultados-ab/2026-10-07-candidatas-stefano-2/dados/rulings_candidatas2.json). Cada teste confere que o numero esperado e' > 0.
# ---------------------------------------------------------------------------------------------------------------------------------
FS, SCB, TIDE, BRE, LZ, EC = "Fractured Sanity", "Screeching Scorchbeast", "Inexorable Tide", "Branching Evolution", "Loading Zone", "The Earth Crystal"


def _cena_c2(bf=(), lands=("Island", "Island", "Island", "Swamp", "Forest", "Forest", "Forest", "Swamp", "Island", "Forest"), hand=(), lib=None, opp_cards=None):
    st = fresh(bf=[*bf], hand=list(hand), lib=lib)
    st.commander_in_cz = False
    for l in lands:
        add(st, l)
    if opp_cards is not None:
        for o in st.opps:
            o.library = list(opp_cards); o.graveyard = []
    return st


@teste
def fractured_sanity_custa_UUU_e_cada_oponente_mila_14_num_unico_evento():
    c = m.CARD_DB[FS]
    assert c.mv == 3 and "sorcery" in c.types and c.pips == (frozenset("U"),) * 3
    st = _cena_c2(bf=[m.COMMANDER, "Gyre Sage"], hand=[FS], opp_cards=["N", "C", "L"] * 30)
    n0 = st.mill_events_total; trig0 = st.mothman_triggers_total
    assert m.cast_card(st, FS) is True
    assert all(len(o.graveyard) == 14 and len(o.library) == 90 - 14 for o in st.opps), [len(o.graveyard) for o in st.opps]
    assert st.mill_events_total == n0 + 1 and st.mothman_triggers_total == trig0 + 1, "tres oponentes mila-ndo ao mesmo tempo = UM gatilho do Mothman, X = soma dos nao-terrenos"
    assert FS in st.graveyard and st.fractured_casts == 1 and st.opp_mill_by_source.get("fractured_sanity") == 42
    st2 = _cena_c2(hand=[FS], opp_cards=["N"] * 40)
    st2.battlefield.append(m.mk_perm(st2, "Bruvac the Grandiloquent"))
    m.cast_card(st2, FS)
    assert all(len(o.graveyard) == 28 for o in st2.opps), "Bruvac dobra (substituicao): 14 -> 28"


@teste
def fractured_sanity_ciclar_mila_4_antes_de_comprar_e_so_cicla_sem_UUU():
    st = _cena_c2(bf=[m.COMMANDER], hand=[FS], lands=("Island", "Swamp", "Forest", "Forest", "Forest", "Swamp"), opp_cards=["N"] * 40)
    assert not m.can_cast_name(st, FS), "so' 1 {U}: UUU nao fecha"
    topo = st.library[0]; mao0 = len(st.hand)
    assert m.act_fractured_cycle(st) is True
    assert all(len(o.graveyard) == 4 for o in st.opps) and FS in st.graveyard and st.fractured_cycles == 1
    assert len(st.hand) == mao0 - 1 + 1 and topo in st.hand, "cartas na mao: -Fractured +1 comprada"
    st2 = _cena_c2(bf=[m.COMMANDER], hand=[FS], opp_cards=["N"] * 40)
    assert m.can_cast_name(st2, FS) and m.act_fractured_cycle(st2) is False, "com UUU conjuro em vez de ciclar"


@teste
def scorchbeast_custa_4BB_ataca_2_rad_em_cada_jogador_e_cria_zumbis_uma_vez_por_turno():
    c = m.CARD_DB[SCB]
    assert c.mv == 6 and (c.power, c.toughness) == (5, 5) and {"Bat", "Mutant"} <= c.subtypes
    st = _cena_c2(bf=[SCB, "Winding Constrictor"], opp_cards=["N"] * 40)
    m.combat_step(st)
    assert st.scorch_attacks == 1 and all(o.rad == 2 for o in st.opps), [o.rad for o in st.opps]
    assert st.rad == 3, "eu tambem: 2 + 1 do Winding Constrictor"
    st2 = _cena_c2(bf=[SCB], opp_cards=["N"] * 40)
    n_cre = len(m.creatures(st2))
    m.mill_event(st2, [(1, 5)], source="teste")
    assert st2.scorch_tokens == 5 and len(m.creatures(st2)) == n_cre + 5, (st2.scorch_tokens, len(m.creatures(st2)))
    z = [p for p in st2.battlefield if p.card.name == "Zombie Mutant Token"]
    assert z and all((m.power(st2, p), m.toughness(st2, p)) == (2, 2) and {"Zombie", "Mutant"} <= m.perm_subtypes(p) for p in z)
    m.mill_event(st2, [(2, 5)], source="teste")
    assert st2.scorch_tokens == 5, "so' uma vez por turno"
    m.begin_any_turn(st2)
    m.mill_event(st2, [(2, 4)], source="teste")
    assert st2.scorch_tokens == 9, "no turno seguinte (outro turn_id) volta a valer"


@teste
def scorchbeast_evento_pequeno_nao_usa_o_unico_do_turno_e_conta_cartas_de_qualquer_jogador():
    st = _cena_c2(bf=[SCB], opp_cards=["N"] * 40)
    m.mill_event(st, [(1, 2)], source="teste")
    assert st.scorch_tokens == 0 and st.scorch_skipped == 1, "abaixo de SCORCH_MIN_X: 'you may' nao criar, o gatilho volta"
    m.mill_event(st, [(2, 6)], source="teste")
    assert st.scorch_tokens == 6, "o evento seguinte do mesmo turno ainda cria (o 'once each turn' nao foi gasto)"
    st2 = _cena_c2(bf=[SCB], lib=["Fathom Mage"] * 6 + ["Forest"] * 20, opp_cards=["N"] * 40)
    m.mill_event(st2, [(0, 3), (1, 2)], source="teste")
    assert st2.scorch_tokens == 5, "milladas por TODOS os jogadores no mesmo evento: 3 minhas + 2 do oponente = 5 (um gatilho)"


@teste
def scorchbeast_zumbis_viram_mill_com_o_Undead_Alchemist():
    def cena(com_ficha):
        st = _cena_c2(bf=["Undead Alchemist"], opp_cards=["N"] * 40)
        if com_ficha:
            z = m.mk_perm(st, "Zombie Mutant Token"); z.entered_turn = st.turn - 2; st.battlefield.append(z)
        m.combat_step(st)
        return st
    a, b = cena(False), cena(True)
    milla_a = sum(40 - len(o.library) for o in a.opps); milla_b = sum(40 - len(o.library) for o in b.opps)
    assert milla_b - milla_a == 2, ("o Zumbi Mutant (poder 2) ataca como Zumbi: o dano vira mill (Alchemist)", milla_a, milla_b)
    assert [o.life for o in b.opps] == [40, 40, 40], "dano substituido: ninguem perde vida"


@teste
def inexorable_tide_prolifera_em_toda_conjuracao_inclusive_comandante_cemiterio_e_custom():
    c = m.CARD_DB[TIDE]
    assert c.mv == 5 and c.pips == (frozenset("U"),) * 2
    st = _cena_c2(bf=[TIDE, "Walking Ballista"], hand=["Sol Ring", "Nature's Lore"], lib=["Forest"] * 30)
    b = next(p for p in st.battlefield if p.card.name == "Walking Ballista"); b.counters = 1
    st.opps[0].rad = 1
    assert m.cast_card(st, "Sol Ring") is True
    assert st.tide_triggers == 1 and b.counters == 2 and st.opps[0].rad == 2, (st.tide_triggers, b.counters, st.opps[0].rad)
    st.commander_in_cz = True
    assert m.cast_commander(st) is True and st.tide_triggers == 2, "conjurar o comandante tambem dispara"
    assert m.cast_custom(st, "Nature's Lore", 1, (frozenset("G"),)) is True and st.tide_triggers == 3, "caminho 'custom' tambem"
    st2 = _cena_c2(bf=["Muldrotha, the Gravetide", TIDE], lib=["Forest"] * 30)
    st2.graveyard.append("Hardened Scales"); st2.hand = []
    t = ("Hardened Scales", "graveyard:muldrotha", "enchantment")
    assert m.execute_cast(st2, t) is True and st2.tide_triggers == 1, "conjurar do cemiterio (Muldrotha) dispara"
    st3 = _cena_c2(bf=[], hand=[TIDE], lib=["Forest"] * 30)
    m.cast_card(st3, TIDE)
    assert st3.tide_triggers == 0, "a propria Inexorable Tide nao dispara ao ser conjurada (ainda nao esta em campo)"


@teste
def branching_evolution_dobra_contador_em_criatura_e_ao_entrar_com_contadores():
    c = m.CARD_DB[BRE]
    assert c.mv == 3 and "enchantment" in c.types
    for extra, esperado in (((), 2), (("Hardened Scales",), 4), (("Hardened Scales", "Winding Constrictor"), 6)):
        st = _cena_c2(bf=[BRE, "Gyre Sage", *extra])
        gs = next(p for p in st.battlefield if p.card.name == "Gyre Sage"); gs.counters = 0
        assert m.place_counters(st, gs, 1, source="teste") == esperado, (extra, esperado)
    st = _cena_c2(bf=[BRE], hand=["Walking Ballista"])
    assert m.cast_card(st, "Walking Ballista", x=3) is True
    b = next(p for p in st.battlefield if p.card.name == "Walking Ballista")
    assert b.counters == 6, ("entra com 3 contadores -> 6 (ruling 2020-06-23)", b.counters)
    st2 = _cena_c2(bf=["Gyre Sage"]); st2.battlefield.append(m.mk_perm(st2, "Opulent Palace"))
    assert m.counter_modifiers(st2, st2.battlefield[-1], "+1/+1") == (0, 1), "so' criatura"


@teste
def the_earth_crystal_verdes_custam_1_a_menos_so_no_generico_dobra_e_ativa_6_mana():
    c = m.CARD_DB[EC]
    assert c.mv == 4 and "artifact" in c.types and c.legendary
    st = _cena_c2(bf=[])
    antes = {n: m.effective_cost(st, n)[0] for n in ("Gyre Sage", "Hardened Scales", "Cold-Eyed Selkie", "Sol Ring", "The Great Henge", "Fathom Mage", "Mirelurk Queen")}
    add(st, EC)
    depois = {n: m.effective_cost(st, n)[0] for n in antes}
    assert depois["Gyre Sage"] == antes["Gyre Sage"] - 1, "{1}{G} -> {G}"
    assert depois["Hardened Scales"] == antes["Hardened Scales"] == 0, "so' o generico: {G} fica {G}"
    assert depois["Cold-Eyed Selkie"] == antes["Cold-Eyed Selkie"] - 1, "pip hibrido {G/U} e' verde"
    assert depois["Fathom Mage"] == antes["Fathom Mage"] - 1, "multicolorida com G e' verde"
    assert depois["Sol Ring"] == antes["Sol Ring"] and depois["Mirelurk Queen"] == antes["Mirelurk Queen"], "incolor e azul nao"
    assert depois["The Great Henge"] <= antes["The Great Henge"] - 1
    g0, _ = m.effective_cost(_cena_c2(bf=[]), m.COMMANDER)
    assert m.effective_cost(st, m.COMMANDER)[0] == g0 - 1, "o comandante (B G U) e' verde: {1} a menos (o imposto vem antes)"
    st2 = _cena_c2(bf=[EC, "Gyre Sage"]); gs = next(p for p in st2.battlefield if p.card.name == "Gyre Sage")
    assert m.place_counters(st2, gs, 1, source="teste") == 2, "dobra +1/+1 em criatura"


@teste
def the_earth_crystal_ativada_distribui_2_contadores_em_um_ou_dois_alvos():
    st = _cena_c2(bf=[EC, "Gyre Sage", "Walking Ballista", "Hardened Scales"], lands=("Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Island", "Swamp"))
    cr = next(p for p in st.battlefield if p.card.name == EC)
    assert m.act_earth_crystal(st) is True and cr.tapped
    assert st.crystal_activations == 1 and st.crystal_counters > 0
    cs = sorted(p.counters for p in st.battlefield if m.is_creature(p))
    assert cs[-1] >= 4 and cs[-2] >= 4, ("dois alvos: cada 1 contador, +1 (Scales) x2 (Crystal) = 4", cs)
    assert m.act_earth_crystal(st) is False, "virada"
    st2 = _cena_c2(bf=[EC, "Gyre Sage"], lands=("Forest",) * 6 + ("Island",))
    m.act_earth_crystal(st2)
    gs = next(p for p in st2.battlefield if p.card.name == "Gyre Sage")
    assert gs.counters == 4 and st2.crystal_counters == 4, ("um alvo so': 2 contadores x2 (Crystal) = 4", gs.counters)
    st3 = _cena_c2(bf=[EC, "Gyre Sage"], lands=("Forest", "Forest", "Island"))
    assert m.act_earth_crystal(st3) is False, "sem 6 de mana nao ativa"


@teste
def loading_zone_dobra_todos_os_contadores_warp_G_exila_no_end_step_e_recasta_do_exilio():
    c = m.CARD_DB[LZ]
    assert c.mv == 4 and "enchantment" in c.types
    st = _cena_c2(bf=["Gyre Sage"], hand=[LZ], lands=("Forest", "Swamp"))
    assert not m.can_cast_name(st, LZ), "custo cheio {3}{G} nao cabe"
    assert (LZ, "hand", "warp") in m.castable_candidates(st, "main1"), "Warp {G} disponivel (ha criatura para receber contador)"
    assert m.execute_cast(st, (LZ, "hand", "warp")) is True
    lz = next(p for p in st.battlefield if p.card.name == LZ)
    assert lz.warped and st.warp_casts == 1
    gs = next(p for p in st.battlefield if p.card.name == "Gyre Sage")
    assert m.place_counters(st, gs, 1, source="teste") == 2, "dobra enquanto esta em campo"
    m.end_step(st)
    assert not any(p.card.name == LZ for p in st.battlefield) and st.warp_exiled == 1 and [n for n, _ in st.warp_exile] == [LZ], "exilada no end step"
    assert LZ not in st.graveyard, "exilio, nao cemiterio"
    assert not [t for t in m.castable_candidates(st, "main1") if t[1] == "warpexile"], "so' em turno POSTERIOR"
    st.turn += 1
    for l in ("Forest", "Forest"): add(st, l)
    assert (LZ, "warpexile", "front") in m.castable_candidates(st, "main1")
    assert m.execute_cast(st, (LZ, "warpexile", "front")) is True and st.warp_recasts == 1
    lz2 = next(p for p in st.battlefield if p.card.name == LZ)
    assert not lz2.warped and not st.warp_exile, "recastada do exilio pelo custo cheio e fica"


@teste
def persist_da_Glen_Elendra_com_dobrador_ou_Constrictor_volta_0_0_e_morre_sem_persist():
    st = _cena_c2(bf=["Glen Elendra Archmage"])
    g = next(p for p in st.battlefield if p.card.name == "Glen Elendra Archmage")
    m.remove_permanent(st, g, "sacrificed", sacrificed=True)
    q = next(p for p in st.battlefield if p.card.name == "Glen Elendra Archmage")
    assert q.ctr.get("minus1") == 1 and m.toughness(st, q) == 1, "sem dobrador/Constrictor: persist volta 1/1 com um -1/-1"
    for extra, minus in (((LZ,), 2), (("Winding Constrictor",), 2)):
        st2 = _cena_c2(bf=["Glen Elendra Archmage", *extra])
        g2 = next(p for p in st2.battlefield if p.card.name == "Glen Elendra Archmage")
        m.remove_permanent(st2, g2, "sacrificed", sacrificed=True)
        assert not any(p.card.name == "Glen Elendra Archmage" for p in st2.battlefield), (extra, "volta com 2 contadores -1/-1 = 0/0: morre (CR 704.5f)")
        assert "Glen Elendra Archmage" in st2.graveyard and st2.persist_zero_deaths == 1 and st2.persist_returns == 1, (extra, st2.persist_zero_deaths)
    m.PERSIST_ZERO_TOUGHNESS_DIES = False
    try:
        st3 = _cena_c2(bf=["Glen Elendra Archmage", LZ])
        g3 = next(p for p in st3.battlefield if p.card.name == "Glen Elendra Archmage")
        m.remove_permanent(st3, g3, "sacrificed", sacrificed=True)
        q3 = next(p for p in st3.battlefield if p.card.name == "Glen Elendra Archmage")
        assert q3.ctr.get("minus1") == 2 and st3.persist_zero_deaths == 0, "chave desligada: o 0/0 fica em campo (comportamento antigo)"
    finally:
        m.PERSIST_ZERO_TOUGHNESS_DIES = True
    st4 = _cena_c2(bf=["Glen Elendra Archmage", "The Great Henge"])
    g4 = next(p for p in st4.battlefield if p.card.name == "Glen Elendra Archmage")
    m.remove_permanent(st4, g4, "sacrificed", sacrificed=True)
    q4 = next((p for p in st4.battlefield if p.card.name == "Glen Elendra Archmage"), None)
    assert q4 is not None and q4.ctr.get("minus1", 0) == 0 and q4.counters == 0, "combo Altar + Henge + Glen sem Constrictor: a Henge cancela o -1/-1 (continua funcionando)"


@teste
def seis_candidatas_partidas_completas_nao_dao_excecao_e_ativam():
    antigos = (m.SWAPS, m.SWAP_IN_PLACE)
    try:
        m.SWAPS = (("An Offer You Can't Refuse", FS), ("Negate", SCB), ("Arcane Denial", TIDE), ("Toxic Deluge", BRE), ("Cold-Eyed Selkie", LZ), ("Didn't Say Please", EC)); m.SWAP_IN_PLACE = True
        tot = collections.Counter()
        for sd in range(1_000_000, 1_000_150):
            for f in (m.simulate_one, m.simulate_one_with_interaction):
                s = f(sd, 12)
                for k in ("fractured_casts", "fractured_cycles", "scorch_attacks", "scorch_tokens", "tide_triggers", "crystal_activations", "warp_casts"):
                    tot[k] += getattr(s, k)
        assert all(tot[k] > 0 for k in ("fractured_casts", "fractured_cycles", "scorch_attacks", "scorch_tokens", "tide_triggers", "crystal_activations", "warp_casts")), ("verificacao vacua", dict(tot))
    finally:
        m.SWAPS, m.SWAP_IN_PLACE = antigos



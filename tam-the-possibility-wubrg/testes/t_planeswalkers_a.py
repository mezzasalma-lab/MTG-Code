from harness import *


def P(name, **kw):
    return (name, kw)


# ======================= Chandra, Legacy of Fire =======================
@test("Chandra +1: {R} por planeswalker que voce controla")
def _():
    st = mk(bf=[P("Chandra, Legacy of Fire", loyalty=3), P("Garruk Wildspeaker"), P("Oko, Thief of Crowns")])
    check(act(st, "Chandra, Legacy of Fire", "Chandra, Legacy of Fire", "+1"))
    check(st.pool.get("R") == 3 and loy(st, "Chandra, Legacy of Fire") == 4, f"{st.pool} {loy(st, 'Chandra, Legacy of Fire')}")


@test("Chandra 0: tira 1 contador de cada permanente escolhido, exila essa quantidade do topo, jogavel neste turno")
def _():
    st = mk(bf=[P("Chandra, Legacy of Fire", loyalty=4), P("Minsc & Boo, Timeless Heroes", loyalty=5), P("Garruk, Veiled Butcher", loyalty=5)], lib=["Sol Ring", "Arcane Signet", "Command Tower", "Baxter Building", "Fellwar Stone"])
    check(act(st, "Chandra, Legacy of Fire", "Chandra, Legacy of Fire", "0"))
    check(len(st.impulse) == 3 and st.impulse == ["Sol Ring", "Arcane Signet", "Command Tower"], str(st.impulse))
    check(loy(st, "Minsc & Boo, Timeless Heroes") == 4 and loy(st, "Garruk, Veiled Butcher") == 4 and loy(st, "Chandra, Legacy of Fire") == 3)
    # jogavel: a carta exilada e' conjuravel
    st.pool = {"C": 5}
    check(T.act_cast_impulse(st) and perm(st, "Sol Ring") is not None, "devia conjurar Sol Ring do exilio")


@test("Chandra (gatilho): no MEU end step X de dano a CADA oponente, X = planeswalkers")
def _():
    st = mk(bf=[P("Chandra, Legacy of Fire", loyalty=3), P("Garruk Wildspeaker"), P("Oko, Thief of Crowns")])
    T.end_step(st)
    check(all(o.life == 37 for o in st.opps), [o.life for o in st.opps])


# ======================= Domri, Chaos Bringer =======================
@test("Domri +1: {R} ou {G} no pool; -3: olha 4, ate 2 criaturas pra mao, resto no fundo; -8: emblema da Fera 4/4 em TODO end step")
def _():
    st = mk(hand=["Dreamtide Whale"], bf=[P("Domri, Chaos Bringer", loyalty=5)])
    check(act(st, "Domri, Chaos Bringer", "Domri, Chaos Bringer", "+1"))
    check(st.pool.get("R", 0) + st.pool.get("G", 0) == 1 and st.riot_pool == 1)
    st = mk(bf=[P("Domri, Chaos Bringer", loyalty=5)], lib=["Birds of Paradise", "Sol Ring", "Noble Hierarch", "Faeburrow Elder", "Command Tower"])
    check(act(st, "Domri, Chaos Bringer", "Domri, Chaos Bringer", "-3"))
    check(sorted(st.hand) == sorted(["Faeburrow Elder", "Birds of Paradise"]) or len(st.hand) == 2, str(st.hand))
    check(len(st.library) == 5 - 2 and "Command Tower" in st.library, str(st.library))
    st = mk(bf=[P("Domri, Chaos Bringer", loyalty=8)])
    check(act(st, "Domri, Chaos Bringer", "Domri, Chaos Bringer", "-8"))
    check("domri" in st.emblems)
    T.end_step(st)
    check(count(st, "Beast Token") == 1, "Fera no meu end step")
    T.opponent_turn(st, st.opps[0])
    check(count(st, "Beast Token") == 2, "Fera tambem no end step de oponente")


@test("Domri riot: criatura paga com mana da Domri entra com +1/+1 (ou haste se for mana-dork / grande)")
def _():
    st = mk(hand=["Displacer Kitten"], bf=[P("Domri, Chaos Bringer", loyalty=5), "Chromatic Orrery"], turn=6)
    st.pool = {"G": 1}
    st.riot_pool = 1
    check(T.cast_card(st, "Displacer Kitten"))
    k = perm(st, "Displacer Kitten")
    check(k is not None and k.ctr.get("p1p1", 0) == 1, "Kitten recebe o contador do riot")
    st = mk(hand=["Birds of Paradise"], bf=[P("Domri, Chaos Bringer", loyalty=5)])
    st.pool = {"G": 1}
    st.riot_pool = 1
    check(T.cast_card(st, "Birds of Paradise"))
    check(perm(st, "Birds of Paradise").haste_until_eot, "dork com riot ganha haste")
    st = mk(hand=["Displacer Kitten"], bf=[P("Domri, Chaos Bringer", loyalty=5), "Chromatic Orrery"])
    st.pool = {}
    st.riot_pool = 0
    check(T.cast_card(st, "Displacer Kitten"))
    check(perm(st, "Displacer Kitten").ctr.get("p1p1", 0) == 0, "sem mana da Domri nao tem riot")


# ======================= Garruk Wildspeaker =======================
@test("Garruk W: +1 desvira 2 terrenos; -1 Fera 3/3; -4 Overrun (+3/+3 e trample ate o fim do turno)")
def _():
    st = mk(bf=[P("Garruk Wildspeaker", loyalty=3), P("Command Tower", tapped=True), P("Baxter Building", tapped=True), P("Boseiju, Who Endures", tapped=True)])
    check(act(st, "Garruk Wildspeaker", "Garruk Wildspeaker", "+1"))
    check(sum(1 for p in T.lands_of(st) if p.tapped) == 1, "desvirou 2")
    st = mk(bf=[P("Garruk Wildspeaker", loyalty=3)])
    check(act(st, "Garruk Wildspeaker", "Garruk Wildspeaker", "-1"))
    b = perm(st, "Beast3 Token")
    check(b is not None and T.power(st, b) == 3 and T.toughness(st, b) == 3 and loy(st, "Garruk Wildspeaker") == 2)
    st = mk(bf=[P("Garruk Wildspeaker", loyalty=4), "Beast3 Token", "Birds of Paradise"])
    check(act(st, "Garruk Wildspeaker", "Garruk Wildspeaker", "-4"))
    check(T.power(st, perm(st, "Beast3 Token")) == 6 and perm(st, "Beast3 Token").ctr.get("trample_eot") == 1)


# ======================= Wrenn and Realmbreaker =======================
@test("Wrenn +1: terreno vira 3/3 vigilancia/haste ate o meu proximo turno (e volta a ser so' terreno)")
def _():
    st = mk(bf=[P("Wrenn and Realmbreaker", loyalty=4), "Command Tower", "Baxter Building"])
    check(act(st, "Wrenn and Realmbreaker", "Wrenn and Realmbreaker", "+1"))
    c = [p for p in T.lands_of(st) if T.is_creature(p)]
    check(len(c) == 1 and T.power(st, c[0]) == 3 and T.has_haste(st, c[0]))
    T.upkeep_step(st)
    check(not any(T.is_creature(p) for p in T.lands_of(st)), "volta a ser so' terreno no meu proximo turno")


@test("Wrenn -2: mill 3 e pega UMA carta permanente (inclui terreno); -7: emblema (jogar terreno e conjurar permanente do cemiterio)")
def _():
    st = mk(bf=[P("Wrenn and Realmbreaker", loyalty=4)], lib=["Ajani Unrelenting", "Ripples of Potential", "Sol Ring", "Command Tower"])
    check(act(st, "Wrenn and Realmbreaker", "Wrenn and Realmbreaker", "-2"))
    check(len(st.hand) == 1 and st.hand[0] in ("Ajani Unrelenting", "Sol Ring"), str(st.hand))
    check(len(st.graveyard) == 2, f"3 milled - 1 pega = 2 no cemiterio: {st.graveyard}")
    st = mk(bf=[P("Wrenn and Realmbreaker", loyalty=7)], gy=["Sol Ring", "Ripples of Potential"])
    check(act(st, "Wrenn and Realmbreaker", "Wrenn and Realmbreaker", "-7"))
    check("wrenn" in st.emblems)
    st.pool = {"C": 5}
    cands = T.cast_candidates(st)
    check(("Sol Ring", "graveyard") in cands, "permanente conjuravel do cemiterio")
    check(not any(n == "Ripples of Potential" for n, z in cands), "instantanea NAO: so' permanente")


# ======================= Dack Fayden =======================
@test("Dack +1: compra 2 e descarta 2; -2: roubar artefato (proxy); -6: emblema")
def _():
    st = mk(bf=[P("Dack Fayden", loyalty=3)], hand=["Command Tower", "Baxter Building"])
    n = len(st.hand)
    check(act(st, "Dack Fayden", "Dack Fayden", "+1"))
    check(len(st.hand) == n and st.m["cards_discarded"] == 2 and st.draws_by_source.get("dack") == 2)
    st = mk(bf=[P("Dack Fayden", loyalty=3)])
    st.target_ok = True
    check(act(st, "Dack Fayden", "Dack Fayden", "-2") and st.m["proxy_steal_artifact"] == 1)
    st = mk(bf=[P("Dack Fayden", loyalty=6)])
    check(act(st, "Dack Fayden", "Dack Fayden", "-6") and "dack" in st.emblems)


# ======================= Dihada =======================
@test("Dihada +2: criatura lendaria ganha vigilancia, lifelink e indestrutivel; o lifelink vira vida no combate; vigilancia nao vira")
def _():
    st = mk(bf=[P("Dihada, Binder of Wills", loyalty=5), "Tam, the Possibility", P("Boo Token", ctr={"p1p1": 3}, token=True)], life=30)
    st.opps[0].life = 40
    check(act(st, "Dihada, Binder of Wills", "Dihada, Binder of Wills", "+2"))
    check(st.dihada_shield is not None)
    T.combat_step(st)
    boo = perm(st, "Boo Token")
    check(st.life > 30, f"lifelink: vida {st.life}")
    check(st.dihada_shield != boo.uid or not boo.tapped, "o alvo ataca sem virar (vigilancia)")


@test("Dihada -3: revela 4, lendarias pra mao, resto pro cemiterio e 1 Treasure por carta no cemiterio; -11: ganha controle de tudo (dano de resiliencia)")
def _():
    st = mk(bf=[P("Dihada, Binder of Wills", loyalty=5)], lib=["Oko, Thief of Crowns", "Chromatic Orrery", "Sol Ring", "Command Tower", "Fellwar Stone"])
    check(act(st, "Dihada, Binder of Wills", "Dihada, Binder of Wills", "-3"))
    # lendarias entre as 4: Oko (PW lendario), Chromatic Orrery (artefato lendario), Command Tower nao
    check(set(st.hand) == {"Oko, Thief of Crowns", "Chromatic Orrery"}, str(st.hand))
    check(count(st, "Treasure Token") == 2 and set(st.graveyard) == {"Sol Ring", "Command Tower"}, f"{count(st, 'Treasure Token')} {st.graveyard}")
    st = mk(res=True, bf=[P("Dihada, Binder of Wills", loyalty=11)])
    add_opp_creature(st, 1, 5, 5); add_opp_creature(st, 2, 4, 4)
    check(act(st, "Dihada, Binder of Wills", "Dihada, Binder of Wills", "-11"))
    check(sum(o.life for o in st.opps) == 120 - 9, "o poder dos permanentes de oponente vira dano")


# ======================= Garruk, Curse Breaker =======================
@test("Garruk CB: criatura de poder >= 4 que entra compra 1; +2 desvira 2 terrenos; -3 Fera 4/4 trample (e compra); -4 buff de ataque")
def _():
    st = mk(bf=[P("Garruk, Curse Breaker", loyalty=5), P("Command Tower", tapped=True), P("Baxter Building", tapped=True)])
    check(act(st, "Garruk, Curse Breaker", "Garruk, Curse Breaker", "-3"))
    check(count(st, "Beast Token") == 1 and st.draws_by_source.get("garruk_curse_breaker") == 1, "a Fera 4/4 entra e dispara a compra da propria Garruk")
    st = mk(bf=[P("Garruk, Curse Breaker", loyalty=5), P("Command Tower", tapped=True), P("Baxter Building", tapped=True)])
    check(act(st, "Garruk, Curse Breaker", "Garruk, Curse Breaker", "+2"))
    check(not any(p.tapped for p in T.lands_of(st)), "desvirou ate 2")
    st = mk(bf=[P("Garruk, Curse Breaker", loyalty=5), "Birds of Paradise", "Faeburrow Elder", "Beast Token"])
    check(act(st, "Garruk, Curse Breaker", "Garruk, Curse Breaker", "-4") and st.cb_buff)
    T.combat_step(st)
    check(st.m["cb_buff_applied"] >= 1, "atacantes ganham +2/+2")
    T.upkeep_step(st)
    check(not st.cb_buff, "expira no meu proximo turno")


@test("Garruk CB: entrar com poder < 4 NAO compra (Soldier 1/1, Cadet 2/2)")
def _():
    st = mk(bf=[P("Garruk, Curse Breaker", loyalty=5)])
    T.create_token(st, "Soldier Token", 3)
    check(st.draws_by_source.get("garruk_curse_breaker", 0) == 0)


# ======================= Minsc & Boo =======================
@test("Minsc & Boo: ETB e upkeep criam Boo (so' um: lendario); +1 poe 3 contadores em criatura com trample/haste; -2 sacrifica, X de dano, compra X se Hamster")
def _():
    st = mk(hand=["Minsc & Boo, Timeless Heroes"], bf=["Sol Ring", "Chromatic Orrery"])
    check(T.cast_card(st, "Minsc & Boo, Timeless Heroes"))
    check(count(st, "Boo Token") == 1)
    T.upkeep_step(st)
    check(count(st, "Boo Token") == 1, "regra da lenda: nao cria outro enquanto Boo vive")
    boo = perm(st, "Boo Token")
    check(boo.haste_until_eot or "haste" in boo.card.tags, "Boo tem haste e trample")
    st = mk(bf=[P("Minsc & Boo, Timeless Heroes", loyalty=3), P("Boo Token", token=True)])
    check(act(st, "Minsc & Boo, Timeless Heroes", "Minsc & Boo, Timeless Heroes", "+1"))
    check(perm(st, "Boo Token").ctr.get("p1p1") == 3 and T.power(st, perm(st, "Boo Token")) == 4)
    st = mk(bf=[P("Minsc & Boo, Timeless Heroes", loyalty=5), P("Boo Token", token=True, ctr={"p1p1": 6})], lib=["Sol Ring"] * 1 + filler_library({"Sol Ring"}))
    n = len(st.hand)
    check(act(st, "Minsc & Boo, Timeless Heroes", "Minsc & Boo, Timeless Heroes", "-2"))
    check(perm(st, "Boo Token") is None, "sacrificou")
    check(sum(40 - o.life for o in st.opps) == 7 and len(st.hand) == n + 7, f"dano 7 (1 + 6 contadores) e compra 7: {sum(40 - o.life for o in st.opps)} {len(st.hand) - n}")


# ======================= Narset Transcendent =======================
@test("Narset +1: topo nao-criatura e nao-terreno vai pra mao; -2: rebound pra instantanea/feitico conjurado da MAO; -9: oponentes nao conjuram nao-criatura")
def _():
    st = mk(bf=[P("Narset Transcendent", loyalty=6)], lib=["Sol Ring", "Command Tower"])
    check(act(st, "Narset Transcendent", "Narset Transcendent", "+1") and st.hand == ["Sol Ring"])
    st = mk(bf=[P("Narset Transcendent", loyalty=6)], lib=["Birds of Paradise", "Command Tower"])
    check(act(st, "Narset Transcendent", "Narset Transcendent", "+1") and st.hand == [], "criatura nao")
    st = mk(bf=[P("Narset Transcendent", loyalty=6)], lib=["Command Tower", "Sol Ring"])
    check(act(st, "Narset Transcendent", "Narset Transcendent", "+1") and st.hand == [], "terreno nao")
    st = mk(hand=["Ripples of Potential"], bf=[P("Narset Transcendent", loyalty=6), "Sol Ring", "Arcane Signet"])
    check(act(st, "Narset Transcendent", "Narset Transcendent", "-2") and st.rebound_armed)
    check(T.cast_card(st, "Ripples of Potential"))
    check("Ripples of Potential" in st.rebound_pending and "Ripples of Potential" in st.exile, "exilada com rebound")
    st.turn += 1
    T.upkeep_step(st)
    check("Ripples of Potential" in st.graveyard and not st.rebound_pending and st.m["rebounds_cast"] == 1, "conjurada de graca no upkeep")
    st = mk(bf=[P("Narset Transcendent", loyalty=9)])
    check(act(st, "Narset Transcendent", "Narset Transcendent", "-9") and "narset" in st.emblems)
    # efeito real: com Patrolling Peacemaker em campo, a magia nao-criatura do oponente e' crime (proliferate); com o emblema elas nao existem
    def crimes(emblem):
        s2 = mk(bf=["Patrolling Peacemaker"], seed=5)
        if emblem:
            s2.emblems.append("narset")
        for i in range(120):
            for o in s2.opps:
                s2.turn += 1
                T.opponent_turn(s2, o)
        return s2.m["opp_crimes_total"], s2.m["opp_spells_blocked_narset"]
    c0, b0 = crimes(False)
    c1, b1 = crimes(True)
    check(c0 > 0 and c1 == 0 and b1 > 0 and b0 == 0, f"sem emblema crimes={c0}; com emblema crimes={c1} bloqueadas={b1}")


@test("Narset -2: rebound NAO dispara em magia que nao foi conjurada da mao (exilio da Chandra, Kasmina)")
def _():
    st = mk(bf=[P("Narset Transcendent", loyalty=6), "Sol Ring", "Arcane Signet"])
    st.rebound_armed = True
    st.impulse = ["Ripples of Potential"]
    check(T.cast_card(st, "Ripples of Potential", zone="impulse"))
    check(st.rebound_armed and not st.rebound_pending, "continua armado: ainda nao conjurei da mao")


# ======================= Professor Dellian Fel =======================
@test("Dellian +2: 3 de vida; 0: compra e perde 1; -3: destroi criatura; -6: emblema (ganhar vida drena o oponente)")
def _():
    st = mk(bf=[P("Professor Dellian Fel", loyalty=5)], life=30)
    check(act(st, "Professor Dellian Fel", "Professor Dellian Fel", "+2") and st.life == 33)
    st = mk(bf=[P("Professor Dellian Fel", loyalty=5)], life=30)
    n = len(st.hand)
    check(act(st, "Professor Dellian Fel", "Professor Dellian Fel", "0") and st.life == 29 and len(st.hand) == n + 1)
    st = mk(res=True, bf=[P("Professor Dellian Fel", loyalty=5)])
    add_opp_creature(st, 1, 5, 5)
    check(act(st, "Professor Dellian Fel", "Professor Dellian Fel", "-3") and not st.opps[0].board)
    st = mk(bf=[P("Professor Dellian Fel", loyalty=6)])
    check(act(st, "Professor Dellian Fel", "Professor Dellian Fel", "-6") and "dellian" in st.emblems)
    T.gain_life(st, 4, "x")
    check(sum(40 - o.life for o in st.opps) == 4, "oponente perde o tanto que eu ganhei")


# ======================= Tamiyo, Field Researcher =======================
@test("Tamiyo +1: ate 2 criaturas marcadas: compro ao darem dano de combate (atacando E bloqueando); -2: tap e nao desvira; -7: compra 3 e emblema de magias gratis")
def _():
    st = mk(bf=[P("Tamiyo, Field Researcher", loyalty=4), "Birds of Paradise", "Faeburrow Elder", "Beast Token"])
    check(act(st, "Tamiyo, Field Researcher", "Tamiyo, Field Researcher", "+1"))
    check(len(st.tamiyo_marked) == 2)
    n = len(st.hand)
    T.combat_step(st)
    check(len(st.hand) > n, "comprou no combate")
    st = mk(res=True, bf=[P("Tamiyo, Field Researcher", loyalty=4), P("Garruk, Curse Breaker", loyalty=1), "Beast Token"])
    check(act(st, "Tamiyo, Field Researcher", "Tamiyo, Field Researcher", "+1"))
    check(perm(st, "Beast Token").uid in st.tamiyo_marked)
    st.turn += 1
    st.attention = True
    c = T.new_opp_creature(3, 3, token=True); c["sick"] = False
    st.opps[0].board.append(c)
    n = len(st.hand)
    T.opponent_combat(st, st.opps[0])
    check(st.m["blocks_total"] == 1 and st.m["tamiyo_block_draws"] == 1 and len(st.hand) == n + 1, f"bloqueios {st.m['blocks_total']} compras {st.m['tamiyo_block_draws']}")
    st = mk(res=True, bf=[P("Tamiyo, Field Researcher", loyalty=4)])
    c = add_opp_creature(st, 1, 4, 4)
    check(act(st, "Tamiyo, Field Researcher", "Tamiyo, Field Researcher", "-2") and c["frozen"] == 1)
    st = mk(bf=[P("Tamiyo, Field Researcher", loyalty=7)])
    n = len(st.hand)
    check(act(st, "Tamiyo, Field Researcher", "Tamiyo, Field Researcher", "-7") and "tamiyo" in st.emblems and len(st.hand) == n + 3)


@test("Emblema da Tamiyo: magias da MAO sem pagar o custo (Tam da zona de comando paga normal)")
def _():
    st = mk(hand=["Elspeth, Sun's Champion", "Land"] if False else ["Elspeth, Sun's Champion"])
    check(not T.can_cast_name(st, "Elspeth, Sun's Champion"), "sem mana nao conjura")
    st.emblems.append("tamiyo")
    check(T.can_cast_name(st, "Elspeth, Sun's Champion"), "com o emblema conjura de graca")
    check(T.cast_card(st, "Elspeth, Sun's Champion") and perm(st, "Elspeth, Sun's Champion") is not None)
    check(not T.can_cast_name(st, "Tam, the Possibility", "cz"), "comandante na zona de comando NAO e' da mao: paga o custo")


# ======================= Teferi, Hero of Dominaria =======================
@test("Teferi H +1: compra e desvira 2 terrenos no proximo end step; -3: tuck (alvo de oponente); -8: emblema (cada compra exila permanente de oponente)")
def _():
    st = mk(bf=[P("Teferi, Hero of Dominaria", loyalty=4), P("Command Tower", tapped=True), P("Baxter Building", tapped=True), P("Boseiju, Who Endures", tapped=True)])
    n = len(st.hand)
    check(act(st, "Teferi, Hero of Dominaria", "Teferi, Hero of Dominaria", "+1") and len(st.hand) == n + 1 and st.end_step_untap == 2)
    T.end_step(st)
    check(sum(1 for p in T.lands_of(st) if p.tapped) == 1, "2 desvirados no end step")
    st = mk(res=True, bf=[P("Teferi, Hero of Dominaria", loyalty=5)])
    c = add_opp_creature(st, 1, 5, 5)
    check(act(st, "Teferi, Hero of Dominaria", "Teferi, Hero of Dominaria", "-3") and not st.opps[0].board)
    st = mk(res=True, bf=[P("Teferi, Hero of Dominaria", loyalty=8)])
    add_opp_creature(st, 1, 5, 5); add_opp_creature(st, 2, 3, 3)
    check(act(st, "Teferi, Hero of Dominaria", "Teferi, Hero of Dominaria", "-8") and "teferi_hero" in st.emblems)
    T.draw_cards(st, 2)
    check(sum(len(o.board) for o in st.opps) == 0, "cada compra exila um permanente de oponente")


# ======================= Teferi, Temporal Archmage =======================
@test("Teferi TA +1: olha 2, um pra mao e o outro no fundo; -1: desvira ate 4; -10: emblema (ativar lealdade no turno de oponente)")
def _():
    st = mk(bf=[P("Teferi, Temporal Archmage", loyalty=5)], lib=["Oko, Thief of Crowns", "Command Tower", "Sol Ring"])
    check(act(st, "Teferi, Temporal Archmage", "Teferi, Temporal Archmage", "+1"))
    check(len(st.hand) == 1 and st.library[-1] in ("Oko, Thief of Crowns", "Command Tower"), f"{st.hand} {st.library}")
    st = mk(bf=[P("Teferi, Temporal Archmage", loyalty=5), P("Sol Ring", tapped=True), P("Chromatic Orrery", tapped=True), P("Command Tower", tapped=True), P("Baxter Building", tapped=True), P("Boseiju, Who Endures", tapped=True)])
    check(act(st, "Teferi, Temporal Archmage", "Teferi, Temporal Archmage", "-1"))
    check(sum(1 for p in st.battlefield if p.tapped) == 1, "desvirou 4")
    st = mk(bf=[P("Teferi, Temporal Archmage", loyalty=10), P("Oko, Thief of Crowns", loyalty=4)])
    check(act(st, "Teferi, Temporal Archmage", "Teferi, Temporal Archmage", "-10") and "teferi_ta" in st.emblems)
    o = perm(st, "Oko, Thief of Crowns")
    st.turn_id += 1
    check(T.pw_can_activate(st, o, "opp"), "pode ativar no turno do oponente")
    T.activate_ability(st, o, "Oko, Thief of Crowns", "+2", 0, "opp")
    check(not T.pw_can_activate(st, o, "opp"), "1 por planeswalker por turno de oponente")


# ======================= Way of the Mind Sculptor (estatico) =======================
@test("Way of the Mind Sculptor: ativacao que REMOVE 2+ contadores compra 1; +N nao")
def _():
    st = mk(bf=["Way of the Mind Sculptor", P("Oko, Thief of Crowns", loyalty=6)])
    n = len(st.hand)
    check(act(st, "Oko, Thief of Crowns", "Oko, Thief of Crowns", "-5") and len(st.hand) == n + 1)
    st = mk(bf=["Way of the Mind Sculptor", P("Oko, Thief of Crowns", loyalty=4)])
    n = len(st.hand)
    check(act(st, "Oko, Thief of Crowns", "Oko, Thief of Crowns", "+2") and len(st.hand) == n)
    st = mk(bf=["Way of the Mind Sculptor", P("Garruk Wildspeaker", loyalty=3)])
    n = len(st.hand)
    check(act(st, "Garruk Wildspeaker", "Garruk Wildspeaker", "-1") and len(st.hand) == n, "remover 1 nao compra")

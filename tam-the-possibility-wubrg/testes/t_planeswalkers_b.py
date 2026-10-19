from harness import *


def P(name, **kw):
    return (name, kw)


# ======================= Garruk, Veiled Butcher =======================
@test("Garruk VB +2: -4/-1 ate o meu proximo turno na maior ameaca (restaura no upkeep); com resistencia 1 a criatura morre exilada (sem ir pro cemiterio dele)")
def _():
    st = mk(res=True, bf=[P("Garruk, Veiled Butcher", loyalty=5)])
    c = add_opp_creature(st, 1, 6, 6)
    check(act(st, "Garruk, Veiled Butcher", "Garruk, Veiled Butcher", "+2"))
    check(c["p"] == 2 and c["t"] == 5, f"{c['p']}/{c['t']}")
    T.upkeep_step(st)
    check(c["p"] == 6 and c["t"] == 6, "restaurado no meu proximo upkeep")
    st = mk(res=True, bf=[P("Garruk, Veiled Butcher", loyalty=5)])
    c = add_opp_creature(st, 1, 3, 1)
    cg0 = st.opps[0].cgy
    check(act(st, "Garruk, Veiled Butcher", "Garruk, Veiled Butcher", "+2") and not st.opps[0].board and st.opps[0].cgy == cg0, "morreu exilada: nao entra no cemiterio dele")


@test("Garruk VB -2: CADA jogador sacrifica (eu tambem); se EU sacrifiquei crio Fera 4/4 trample; sem criatura minha, so' eles")
def _():
    st = mk(res=True, bf=[P("Garruk, Veiled Butcher", loyalty=5), "Soldier Token"])
    add_opp_creature(st, 1, 5, 5); add_opp_creature(st, 1, 2, 2); add_opp_creature(st, 2, 3, 3)
    check(act(st, "Garruk, Veiled Butcher", "Garruk, Veiled Butcher", "-2"))
    check(perm(st, "Soldier Token") is None and count(st, "Beast Token") == 1, "sacrifiquei a ficha e criei a Fera")
    check(len(st.opps[0].board) == 1 and len(st.opps[1].board) == 0, "cada oponente sacrificou uma")
    st = mk(res=True, bf=[P("Garruk, Veiled Butcher", loyalty=5), "Tam, the Possibility"])
    add_opp_creature(st, 1, 5, 5)
    check(not any(o[2] == "-2" for o in T.ability_options(st, perm(st, "Garruk, Veiled Butcher"))), "a IA nao escolhe o -2 se isso custa a Tam")
    T.activate_ability(st, perm(st, "Garruk, Veiled Butcher"), "Garruk, Veiled Butcher", "-2", 0)
    check(perm(st, "Tam, the Possibility") is None, "obrigatorio: sem ficha eu sacrifico a unica criatura (a Tam)")


@test("Garruk VB -3: cada oponente descarta 2; nao descartou 2 nao-terrenos -> eu compro")
def _():
    st = mk(bf=[P("Garruk, Veiled Butcher", loyalty=5)])
    check(act(st, "Garruk, Veiled Butcher", "Garruk, Veiled Butcher", "-3"))
    check(all(o.hand_size == 5 for o in st.opps) and st.m["opp_discards"] == 3)


# ======================= Nissa, Ascended Animist =======================
@test("Nissa +1: ficha X/X onde X = lealdade DELA (apos o custo); -1: destroi artefato/encantamento (proxy); -7: +1/+1 por Forest e trample")
def _():
    st = mk(bf=[P("Nissa, Ascended Animist", loyalty=7)])
    check(act(st, "Nissa, Ascended Animist", "Nissa, Ascended Animist", "+1"))
    h = perm(st, "Horror Token")
    check(T.power(st, h) == 8 and T.toughness(st, h) == 8, f"{T.power(st, h)}/{T.toughness(st, h)}")
    st = mk(bf=[P("Nissa, Ascended Animist", loyalty=7), "Breeding Pool", "Temple Garden", "Command Tower", "Beast Token"])
    check(act(st, "Nissa, Ascended Animist", "Nissa, Ascended Animist", "-7"))
    b = perm(st, "Beast Token")
    check(T.power(st, b) == 4 + 2 and b.ctr.get("trample_eot") == 1, "2 Forests (Breeding Pool, Temple Garden): +2")
    st = mk(bf=[P("Nissa, Ascended Animist", loyalty=7)])
    st.target_ok = True
    check(act(st, "Nissa, Ascended Animist", "Nissa, Ascended Animist", "-1") and st.m["proxy_artifact_enchantment_destroy"] == 1)


@test("Nissa +1 com Garruk Curse Breaker: o Horror X/X com X >= 4 compra")
def _():
    st = mk(bf=[P("Nissa, Ascended Animist", loyalty=7), P("Garruk, Curse Breaker", loyalty=5)])
    check(act(st, "Nissa, Ascended Animist", "Nissa, Ascended Animist", "+1") and st.draws_by_source.get("garruk_curse_breaker") == 1)


# ======================= Oko =======================
@test("Oko +2: Food; +1: artefato/criatura perde habilidades e vira Elk 3/3; -5: troca controle (resiliencia: criatura de oponente de poder <= 3)")
def _():
    st = mk(bf=[P("Oko, Thief of Crowns", loyalty=4)])
    check(act(st, "Oko, Thief of Crowns", "Oko, Thief of Crowns", "+2") and count(st, "Food Token") == 1)
    st = mk(bf=[P("Oko, Thief of Crowns", loyalty=4), "Food Token"])
    check(act(st, "Oko, Thief of Crowns", "Oko, Thief of Crowns", "+1"))
    f = perm(st, "Food Token")
    check(T.is_creature(f) and T.power(st, f) == 3 and f.lost_abilities, "Food virou Elk 3/3 sem habilidades")
    st = mk(res=True, bf=[P("Oko, Thief of Crowns", loyalty=5), "Soldier Token"])
    add_opp_creature(st, 1, 3, 3); add_opp_creature(st, 2, 5, 5)
    check(act(st, "Oko, Thief of Crowns", "Oko, Thief of Crowns", "-5"))
    check(len(st.opps[0].board) == 0 and len(st.opps[1].board) == 1 and count(st, "Elk Token") == 1, "troquei a ficha pela de poder 3 (a de 5 nao pode)")


# ======================= The Eternal Wanderer =======================
@test("Eternal Wanderer 0: Samurai 2/2 double strike; -4: cada jogador sacrifica o resto (EU escolho a criatura que fica: a mais fraca dos oponentes)")
def _():
    st = mk(bf=[P("The Eternal Wanderer", loyalty=5)])
    check(act(st, "The Eternal Wanderer", "The Eternal Wanderer", "0"))
    s_ = perm(st, "Samurai Token")
    check(T.power(st, s_) == 2 and "double_strike" in s_.card.tags)
    st = mk(res=True, bf=[P("The Eternal Wanderer", loyalty=6), "Soldier Token", "Beast Token", "Elk Token"])
    add_opp_creature(st, 1, 6, 6); add_opp_creature(st, 1, 2, 2); add_opp_creature(st, 2, 1, 1); add_opp_creature(st, 2, 4, 4)
    check(act(st, "The Eternal Wanderer", "The Eternal Wanderer", "-4"))
    check(len(T.creatures(st)) == 1, "so' sobra uma criatura minha")
    check(len(st.opps[0].board) == 1 and st.opps[0].board[0]["p"] == 2, "eu escolhi a MAIS FRACA do oponente 1")
    check(len(st.opps[1].board) == 1 and st.opps[1].board[0]["p"] == 1, "e a mais fraca do oponente 2")


@test("Eternal Wanderer +1: exila criatura/artefato e devolve no END STEP do dono (objeto novo: Sanctum Lurker entra de novo = empower 1 de novo)")
def _():
    st = mk(bf=[P("The Eternal Wanderer", loyalty=5), "Sanctum Lurker", P("Jace Token", loyalty=7, token=True)])
    j0 = loy(st, "Jace Token")
    check(act(st, "The Eternal Wanderer", "The Eternal Wanderer", "+1"))
    check(perm(st, "Sanctum Lurker") is None, "exilado")
    T.end_step(st)
    check(perm(st, "Sanctum Lurker") is not None and loy(st, "Jace Token") == j0 + 1, f"voltou e deu empower 1: {loy(st, 'Jace Token')}")


@test("Eternal Wanderer: no MAXIMO uma criatura ataca ela por combate (estatico)")
def _():
    st = mk(res=True, bf=[P("The Eternal Wanderer", loyalty=6)])
    st.attention = True
    for _ in range(3):
        c = T.new_opp_creature(2, 2); c["sick"] = False; st.opps[0].board.append(c)
    T.opponent_combat(st, st.opps[0])
    check(st.m["pw_combat_damage_total"] == 2, f"so' uma das 3 criaturas pode atacar a Wanderer: {st.m['pw_combat_damage_total']}")
    check(st.m["face_combat_damage_total"] == 4, "as outras 2 vao em mim")


# ======================= Vraska =======================
@test("Vraska 0: compra, perde 1 de vida, proliferate; -2: criatura vira Treasure (resiliencia: remove a maior ameaca); -9: veneno ate 9 (10 e' a derrota: o proliferate seguinte fecha)")
def _():
    st = mk(bf=[P("Vraska, Betrayal's Sting", loyalty=6), P("Garruk Wildspeaker", loyalty=3)], life=30)
    n = len(st.hand)
    check(act(st, "Vraska, Betrayal's Sting", "Vraska, Betrayal's Sting", "0"))
    check(len(st.hand) == n + 1 and st.life == 29 and loy(st, "Garruk Wildspeaker") == 4 and loy(st, "Vraska, Betrayal's Sting") == 7, "proliferate soma 1 nos dois")
    st = mk(res=True, bf=[P("Vraska, Betrayal's Sting", loyalty=6)])
    add_opp_creature(st, 1, 5, 5)
    check(act(st, "Vraska, Betrayal's Sting", "Vraska, Betrayal's Sting", "-2") and not st.opps[0].board)
    st = mk(bf=[P("Vraska, Betrayal's Sting", loyalty=9)])
    check(act(st, "Vraska, Betrayal's Sting", "Vraska, Betrayal's Sting", "-9"))
    o = T.lowest_opp(st)
    check(max(o2.poison for o2 in st.opps) == 9 and not any(o2.eliminated for o2 in st.opps), "9 de veneno nao elimina")
    T.proliferate(st, "test")
    check(any(o2.eliminated and o2.elim_reason == "poison" for o2 in st.opps), "o proliferate leva a 10: derrota por veneno")


# ======================= Ajani Unrelenting =======================
@test("Ajani: TODA ativacao de lealdade cria um Cadet 2/2; +1: +1/+0 e haste; -2: descarta a mao e compra 1 por criatura; -3: 4 de dano em cada criatura exceto minhas fichas")
def _():
    st = mk(bf=[P("Ajani Unrelenting", loyalty=5), P("Garruk Wildspeaker", loyalty=3)])
    check(act(st, "Garruk Wildspeaker", "Garruk Wildspeaker", "-1"))
    check(count(st, "Cadet Token") == 1, "ativacao de OUTRO planeswalker tambem cria Cadet")
    st = mk(bf=[P("Ajani Unrelenting", loyalty=5), "Beast Token", "Birds of Paradise"])
    check(act(st, "Ajani Unrelenting", "Ajani Unrelenting", "+1"))
    check(T.power(st, perm(st, "Beast Token")) == 5 and perm(st, "Beast Token").haste_until_eot, "+1/+0 e haste")
    cad = perm(st, "Cadet Token")
    check(T.power(st, cad) == 3 and T.has_haste(st, cad), "o Cadet criado pela propria +1 tambem recebe o bonus (entra antes de resolver)")
    st = mk(hand=["Sol Ring", "Arcane Signet"], bf=[P("Ajani Unrelenting", loyalty=5), "Beast Token", "Soldier Token", "Birds of Paradise"], lib=filler_library({"Sol Ring", "Arcane Signet"}))
    check(act(st, "Ajani Unrelenting", "Ajani Unrelenting", "-2"))
    check(set(["Sol Ring", "Arcane Signet"]) <= set(st.graveyard) and len(st.hand) >= 3, f"descartou 2 e comprou {len(st.hand)}")
    st = mk(res=True, bf=[P("Ajani Unrelenting", loyalty=5), "Beast Token", "Birds of Paradise", "Tam, the Possibility", "Dreamtide Whale"])
    add_opp_creature(st, 1, 3, 3); add_opp_creature(st, 1, 2, 5)
    check(act(st, "Ajani Unrelenting", "Ajani Unrelenting", "-3"))
    check(perm(st, "Beast Token") is not None, "ficha minha sobrevive")
    check(perm(st, "Birds of Paradise") is None and perm(st, "Tam, the Possibility") is None, "Birds (0/1) e Tam (2/4: 4 de dano mata) morrem")
    check(perm(st, "Dreamtide Whale") is not None, "Whale 7/5 sobrevive")
    check(len(st.opps[0].board) == 1 and st.opps[0].board[0]["t"] == 5, "do oponente morre quem tem resistencia <= 4")


@test("Ajani -3 nao e' escolhido se mataria a Tam de graca")
def _():
    st = mk(res=True, bf=[P("Ajani Unrelenting", loyalty=5), "Tam, the Possibility"])
    add_opp_creature(st, 1, 3, 3)
    opts = T.ability_options(st, perm(st, "Ajani Unrelenting"))
    check(not any(o[2] == "-3" for o in opts), "ameaca pequena nao compensa perder a Tam")


# ======================= Elspeth =======================
@test("Elspeth +1: 3 Soldiers 1/1; -3: destroi criaturas de poder >= 4 (as minhas tambem); -7: emblema +2/+2 e voo")
def _():
    st = mk(bf=[P("Elspeth, Sun's Champion", loyalty=4)])
    check(act(st, "Elspeth, Sun's Champion", "Elspeth, Sun's Champion", "+1") and count(st, "Soldier Token") == 3)
    st = mk(res=True, bf=[P("Elspeth, Sun's Champion", loyalty=4), "Beast Token", "Birds of Paradise", "Tam, the Possibility"])
    add_opp_creature(st, 1, 4, 4); add_opp_creature(st, 1, 3, 3)
    check(act(st, "Elspeth, Sun's Champion", "Elspeth, Sun's Champion", "-3"))
    check(perm(st, "Beast Token") is None and perm(st, "Birds of Paradise") is not None and perm(st, "Tam, the Possibility") is not None, "so' poder >= 4")
    check(len(st.opps[0].board) == 1 and st.opps[0].board[0]["p"] == 3)
    st = mk(bf=[P("Elspeth, Sun's Champion", loyalty=7), "Soldier Token"])
    check(act(st, "Elspeth, Sun's Champion", "Elspeth, Sun's Champion", "-7") and "elspeth" in st.emblems)
    s_ = perm(st, "Soldier Token")
    check(T.power(st, s_) == 3 and T.toughness(st, s_) == 3 and T.has_flying(st, s_))


# ======================= Kasmina =======================
@test("Kasmina: os OUTROS planeswalkers tem as habilidades dela (+2 scry 1, -X Fractal, -8 tutor); +2 scry; -8 busca instantanea/feitico que compartilha cor com o planeswalker que ATIVOU")
def _():
    st = mk(bf=[P("Kasmina, Enigma Sage", loyalty=2), P("Garruk Wildspeaker", loyalty=3)])
    opts = T.own_abilities(st, perm(st, "Garruk Wildspeaker"))
    check(("Kasmina, Enigma Sage", "-X", "X") in opts and ("Kasmina, Enigma Sage", "+2", 2) in opts, str(opts))
    check(act(st, "Garruk Wildspeaker", "Kasmina, Enigma Sage", "+2") and loy(st, "Garruk Wildspeaker") == 5, "Kasmina +2 nos outros planeswalkers")
    st = mk(bf=[P("Kasmina, Enigma Sage", loyalty=2), P("Garruk Wildspeaker", loyalty=9)])
    check(act(st, "Garruk Wildspeaker", "Kasmina, Enigma Sage", "-X", 6))
    f = perm(st, "Fractal Token")
    check(f is not None and f.ctr.get("p1p1") == 6 and loy(st, "Garruk Wildspeaker") == 3, "Fractal 6/6 e a Garruk perdeu 6")
    # -8 do Garruk Wildspeaker (verde): busca instantanea/feitico VERDE na biblioteca: nenhuma na lista (Ripples azul, Entrust verde-azul compartilha G)
    st = mk(bf=[P("Kasmina, Enigma Sage", loyalty=2), P("Garruk Wildspeaker", loyalty=9)], lib=["Entrust the Spark", "Ripples of Potential", "Sol Ring"])
    st.battlefield.append(T.mk_perm(st, "Oko, Thief of Crowns")); perm(st, "Oko, Thief of Crowns").ctr["loyalty"] = 9
    check(act(st, "Garruk Wildspeaker", "Kasmina, Enigma Sage", "-8"))
    check("Entrust the Spark" in st.exile or "Entrust the Spark" in st.graveyard or st.m["kasmina_tutor"] == 1, "achou a magia verde")


# ======================= Kiora of Salt and Sand =======================
@test("Kiora: planeswalkers tem -8 (Leviatã 8/8 hexproof); ao atacar com lealdade ativada, desvira o atacante e ele nao pode ser bloqueado")
def _():
    st = mk(bf=["Kiora of Salt and Sand", P("Garruk Wildspeaker", loyalty=9)])
    check(act(st, "Garruk Wildspeaker", "Kiora of Salt and Sand", "-8") and count(st, "Leviathan Token") == 1)
    st = mk(bf=["Kiora of Salt and Sand", "Beast Token", P("Garruk Wildspeaker", loyalty=3)])
    st.activated_loyalty_this_turn = True
    T.combat_step(st)
    check(st.m["kiora_triggers"] == 1 and not perm(st, "Beast Token").tapped and perm(st, "Beast Token").unblockable)


# ======================= Saheeli =======================
@test("Saheeli: magia nao-criatura cria Servo 1/1 artefato; -2: artefato vira copia da criatura/artefato ate o fim do turno")
def _():
    st = mk(hand=["Sol Ring"], bf=["Saheeli, Sublime Artificer" if False else P("Saheeli, Sublime Artificer", loyalty=5)])
    st.pool = {"C": 1}
    T.cast_card(st, "Sol Ring")
    check(count(st, "Servo Token") == 1 and T.power(st, perm(st, "Servo Token")) == 1)
    st = mk(bf=[P("Saheeli, Sublime Artificer", loyalty=5), P("Servo Token", token=True), P("Dreamtide Whale", ctr={"time": 2})], phase="main1")
    check(act(st, "Saheeli, Sublime Artificer", "Saheeli, Sublime Artificer", "-2"))
    sv = perm(st, "Servo Token")
    check(T.power(st, sv) == 7 and T.toughness(st, sv) == 5, f"copia da Whale 7/5: {T.power(st, sv)}/{T.toughness(st, sv)}")
    T.end_step(st)
    check(T.power(st, sv) == 1, "volta ao normal no fim do turno")


# ======================= Vronos =======================
@test("Vronos +1: ate 2 outros planeswalkers saem de fase no proximo end step (voltam no meu turno); -2: devolve permanente de cada oponente; -7: artefato vira 9/9 Construct com vigilancia, indestrutivel e nao bloqueavel")
def _():
    st = mk(res=True, bf=[P("Vronos, Masked Inquisitor", loyalty=5), P("Garruk Wildspeaker", loyalty=5), P("Oko, Thief of Crowns", loyalty=4)])
    check(act(st, "Vronos, Masked Inquisitor", "Vronos, Masked Inquisitor", "+1"))
    check(not any(p.phased for p in st.battlefield), "ainda nao: so' no end step")
    T.end_step(st)
    check(sum(1 for p in st.battlefield if p.phased) == 2)
    check(len(T.pws(st)) == 1, "fora de fase nao existem")
    T.untap_my_permanents(st)
    check(not any(p.phased for p in st.battlefield), "voltam no meu proximo turno")
    st = mk(res=True, bf=[P("Vronos, Masked Inquisitor", loyalty=5)])
    add_opp_creature(st, 1, 5, 5); add_opp_creature(st, 2, 3, 3)
    check(act(st, "Vronos, Masked Inquisitor", "Vronos, Masked Inquisitor", "-2") and sum(len(o.board) for o in st.opps) == 0)
    st = mk(bf=[P("Vronos, Masked Inquisitor", loyalty=7), "Sol Ring"])
    check(act(st, "Vronos, Masked Inquisitor", "Vronos, Masked Inquisitor", "-7"))
    sr = perm(st, "Sol Ring")
    check(T.is_creature(sr) and T.power(st, sr) == 9 and sr.ctr.get("indestructible") and sr.ctr.get("vigilance") and sr.unblockable)
    T.combat_step(st)
    check(not sr.tapped and st.opps[0].life + st.opps[1].life + st.opps[2].life == 120 - 9, "ataca no mesmo turno (estava em campo) com vigilancia")


# ======================= Aminatou =======================
@test("Aminatou +1: compra e poe uma carta no topo; -1: pisca outro permanente meu (objeto novo: Way de novo empower); -6: nunca usada (troca todo o meu campo)")
def _():
    st = mk(bf=[P("Aminatou, the Fateshifter", loyalty=3)], hand=["Command Tower"])
    top0 = len(st.library)
    check(act(st, "Aminatou, the Fateshifter", "Aminatou, the Fateshifter", "+1"))
    check(len(st.library) == top0 and len(st.hand) == 1, "comprou 1 e devolveu 1 pro topo")
    st = mk(bf=[P("Aminatou, the Fateshifter", loyalty=3), "Way of the Mind Sculptor", P("Jace Token", loyalty=2, token=True)])
    check(act(st, "Aminatou, the Fateshifter", "Aminatou, the Fateshifter", "-1"))
    check(loy(st, "Jace Token") == 7, f"piscar a Way: empower 5 de novo: {loy(st, 'Jace Token')}")
    st = mk(bf=[P("Aminatou, the Fateshifter", loyalty=6)])
    check(not any(o[2] == "-6" for o in T.ability_options(st, perm(st, "Aminatou, the Fateshifter"))), "ultimate nao e' escolhido (cede o campo todo)")


# ======================= Tezzeret =======================
@test("Tezzeret +1: desvira ate 2 artefatos; -X: busca artefato de MV <= X pro campo; -5: artefatos viram 5/5 ate o fim do turno")
def _():
    st = mk(bf=[P("Tezzeret the Seeker", loyalty=4), P("Sol Ring", tapped=True), P("Chromatic Orrery", tapped=True)])
    check(act(st, "Tezzeret the Seeker", "Tezzeret the Seeker", "+1"))
    check(not perm(st, "Sol Ring").tapped and not perm(st, "Chromatic Orrery").tapped)
    st = mk(bf=[P("Tezzeret the Seeker", loyalty=4)], lib=["The Chain Veil", "Sol Ring", "Command Tower"])
    check(act(st, "Tezzeret the Seeker", "Tezzeret the Seeker", "-X", 4))
    check(perm(st, "The Chain Veil") is not None and loy(st, "Tezzeret the Seeker") == 0 or perm(st, "The Chain Veil") is not None, "buscou MV 4 (Chain Veil)")
    st = mk(bf=[P("Tezzeret the Seeker", loyalty=5), "Sol Ring", "Arcane Signet"])
    check(act(st, "Tezzeret the Seeker", "Tezzeret the Seeker", "-5"))
    check(T.power(st, perm(st, "Sol Ring")) == 5)
    T.end_step(st)
    check(not T.is_creature(perm(st, "Sol Ring")))


# ======================= Jace token =======================
@test("Ficha de Jace: -1 Surveil 1, -3 compra 1; nasce com 0 de lealdade (empower poe os contadores)")
def _():
    st = mk(bf=[P("Jace Token", loyalty=5, token=True)])
    n = len(st.hand)
    check(act(st, "Jace Token", "Jace Token", "-3") and len(st.hand) == n + 1 and loy(st, "Jace Token") == 2)
    st = mk(bf=[P("Jace Token", loyalty=2, token=True)])
    check(act(st, "Jace Token", "Jace Token", "-1") and st.m["surveil_events"] == 1)
    st = mk()
    T.empower_jace(st, 5, "t")
    check(loy(st, "Jace Token") == 5 and count(st, "Jace Token") == 1)
    T.empower_jace(st, 2, "t")
    check(loy(st, "Jace Token") == 7 and count(st, "Jace Token") == 1, "ja' controlo uma: NAO cria outra")

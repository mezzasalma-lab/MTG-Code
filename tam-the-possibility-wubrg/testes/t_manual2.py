"""Cada clausula operacional do relato do usuario (goldfish manual #2, 2026-10-20) e' uma afirmacao testavel sobre o simulador (CLAUDE.md Regra #6). Estes testes reproduzem as jogadas dele
JA' COM AS CORRECOES que ele deu (T4: a Saheeli foi undo e entrou so' no T5; T7: a Eternal Wanderer NAO recebe contador do proliferate da Whale, porque entra depois do gatilho, e faltou o Servo dela)."""
from harness import *


def P(name, **kw):
    return (name, kw)


def opp_all_colors(st):
    for o in st.opps:
        o.land_colors = ["W", "U", "B", "R", "G"]


@test("Manual #2 T3: a Tam ({1}{G}{U}) sai com Zagoth Triome + Starting Town + Fellwar Stone (a City of Brass pode ficar desvirada)")
def _():
    st = mk(turn=3, bf=["Zagoth Triome", "Starting Town", "Fellwar Stone", "City of Brass"])
    opp_all_colors(st)
    check(T.can_cast_name(st, "Tam, the Possibility", "cz") and T.cast_card(st, "Tam, the Possibility", "cz"))
    check(perm(st, "Tam, the Possibility") is not None)
    st = mk(turn=3, bf=["Zagoth Triome", "Starting Town", "Fellwar Stone"])
    opp_all_colors(st)
    check(T.can_cast_name(st, "Tam, the Possibility", "cz"), "so' com as 3 fontes")


@test("Manual #2 T4: Way of the Deathbringer sem ficha de Jace cria a ficha com 5; Jace -3 compra e deixa 2; a Tam (entrou no T3) ja' pode atacar")
def _():
    st = mk(turn=4, hand=["Way of the Deathbringer"], bf=["Tam, the Possibility", "Zagoth Triome", "Starting Town", "Fellwar Stone", "Plaza of Heroes", "City of Brass"])
    opp_all_colors(st)
    check(T.cast_card(st, "Way of the Deathbringer"))
    check(loy(st, "Jace Token") == 5, str(loy(st, "Jace Token")))
    n = len(st.hand)
    check(act(st, "Jace Token", "Jace Token", "-3") and len(st.hand) == n + 1 and loy(st, "Jace Token") == 2)
    tam = perm(st, "Tam, the Possibility")
    check(T.is_creature(tam) and not T.sick(st, tam), "a Tam foi conjurada no T3: sem doenca de invocacao no T4 (REGRA: ela pode atacar)")
    check("Tam, the Possibility" in T.NON_ATTACKERS, "POLITICA do simulador: a Tam nunca ataca (reservada ao {T} de proliferate); o usuario atacou com ela no T4 sem mana WUBRG pra ativar")


@test("Manual #2 T5: com a Tam, Saheeli custa 2 e Aminatou 3 (a reducao so' abate generico); Town + Fellwar + Triome + Plaza (so' lendaria) + City pagam as duas; Saheeli em campo faz Servo na Aminatou")
def _():
    st = mk(turn=5, hand=["Saheeli, Sublime Artificer", "Aminatou, the Fateshifter"],
            bf=["Tam, the Possibility", "Zagoth Triome", "Starting Town", "Fellwar Stone", "Plaza of Heroes", "City of Brass", "Boseiju, Who Endures", P("Jace Token", loyalty=2, token=True)])
    opp_all_colors(st)
    check(T.effective_cost(st, "Saheeli, Sublime Artificer")[0] == 0 and len(T.effective_cost(st, "Saheeli, Sublime Artificer")[1]) == 2, str(T.effective_cost(st, "Saheeli, Sublime Artificer")))
    check(T.effective_cost(st, "Aminatou, the Fateshifter") == (0, tuple(T.CARD_DB["Aminatou, the Fateshifter"].pips)), str(T.effective_cost(st, "Aminatou, the Fateshifter")))
    check(T.cast_card(st, "Saheeli, Sublime Artificer") and loy(st, "Saheeli, Sublime Artificer") == 5)
    check(count(st, "Servo Token") == 0, "Saheeli nao dispara na propria conjuracao")
    check(T.cast_card(st, "Aminatou, the Fateshifter"), "5 mana no total")
    check(loy(st, "Aminatou, the Fateshifter") == 3 and count(st, "Servo Token") == 1, "Servo da Saheeli na conjuracao da Aminatou")


@test("Manual #2 T5: Aminatou +1 (3 -> 4) compra 1 e devolve 1 carta da mao pro TOPO da biblioteca (a escolha da carta e' da IA; o usuario devolveu a Eternal Wanderer, que comprou de novo no T6)")
def _():
    st = mk(turn=5, hand=["The Eternal Wanderer"], lib=["Teferi, Hero of Dominaria", "Sol Ring", "Command Tower"], bf=[P("Aminatou, the Fateshifter", loyalty=3)])
    check(act(st, "Aminatou, the Fateshifter", "Aminatou, the Fateshifter", "+1") and loy(st, "Aminatou, the Fateshifter") == 4)
    check(len(st.hand) == 1 and len(st.library) == 3, "comprou 1 e devolveu 1 pro topo")
    check(st.library[0] in ("The Eternal Wanderer", "Teferi, Hero of Dominaria"), "a carta do topo e' uma das duas da mao: " + st.library[0])


@test("Manual #2 T6: Wooded Foothills (Mountain ou Forest) busca Spara's Headquarters (Forest Plains Island, entra virado)")
def _():
    st = mk(turn=6, bf=["Wooded Foothills"], lib=["Spara's Headquarters", "Watery Grave", "Command Tower", "Sol Ring"])
    check("Spara's Headquarters" in T.fetch_targets(st, perm(st, "Wooded Foothills")))
    check(T.crack_fetch(st, perm(st, "Wooded Foothills")))
    sp = perm(st, "Spara's Headquarters")
    check(sp is not None and sp.tapped and "Wooded Foothills" in st.graveyard and perm(st, "Wooded Foothills") is None)


@test("Manual #2 T6: Whale (1a magia) + Teferi (2a): o gatilho da Whale resolve ANTES de Teferi entrar, entao Teferi fica em 4 e Saheeli/Aminatou/Jace/contador de tempo da Whale ganham +1; Teferi +1 -> 5 e compra")
def _():
    st = mk(turn=6, hand=["Dreamtide Whale", "Teferi, Hero of Dominaria"], lib=["Windswept Heath", "Sol Ring", "Command Tower"],
            bf=["Tam, the Possibility", "Zagoth Triome", "Starting Town", "Boseiju, Who Endures", "Plaza of Heroes", "City of Brass", "Fellwar Stone", "Spara's Headquarters",
                P("Saheeli, Sublime Artificer", loyalty=3), P("Aminatou, the Fateshifter", loyalty=4), P("Jace Token", loyalty=2, token=True)])
    opp_all_colors(st)
    check(T.cast_card(st, "Dreamtide Whale"))
    w = perm(st, "Dreamtide Whale")
    check(w.ctr.get("time") == 2)
    check(T.cast_card(st, "Teferi, Hero of Dominaria"), "Teferi custa 4 com a Tam")
    check(loy(st, "Teferi, Hero of Dominaria") == 4, "Teferi nao e' proliferado: ainda estava na pilha: %s" % loy(st, "Teferi, Hero of Dominaria"))
    check(loy(st, "Saheeli, Sublime Artificer") == 4 and loy(st, "Aminatou, the Fateshifter") == 5 and loy(st, "Jace Token") == 3 and w.ctr.get("time") == 3,
          f"{loy(st, 'Saheeli, Sublime Artificer')} {loy(st, 'Aminatou, the Fateshifter')} {loy(st, 'Jace Token')} {w.ctr.get('time')}")
    n = len(st.hand)
    check(act(st, "Teferi, Hero of Dominaria", "Teferi, Hero of Dominaria", "+1") and loy(st, "Teferi, Hero of Dominaria") == 5 and len(st.hand) == n + 1)


@test("Manual #2 T7: Chandra +1 com 5 planeswalkers da' {R}x5; esse mana paga o generico da Eternal Wanderer ({4}{W}{W} - 1) junto de City of Brass + Spara's HQ (os dois W)")
def _():
    st = mk(turn=7, hand=["The Eternal Wanderer"],
            bf=["Tam, the Possibility", "City of Brass", "Spara's Headquarters", P("Chandra, Legacy of Fire", loyalty=3), P("Jace Token", loyalty=3, token=True), P("Saheeli, Sublime Artificer", loyalty=4),
                P("Aminatou, the Fateshifter", loyalty=5), P("Teferi, Hero of Dominaria", loyalty=5)])
    check(act(st, "Chandra, Legacy of Fire", "Chandra, Legacy of Fire", "+1") and st.pool.get("R") == 5 and loy(st, "Chandra, Legacy of Fire") == 4, str(st.pool))
    check(T.can_cast_name(st, "The Eternal Wanderer") and T.cast_card(st, "The Eternal Wanderer"), "Wanderer: 3 generico (R) + WW (City + Spara)")
    check(loy(st, "The Eternal Wanderer") == 5)


@test("Manual #2 T7 (corrigido): Chandra e Wanderer (2a magia, dispara a Whale) -> a Wanderer NAO e' proliferada (fica 5); Chandra 4 -> 5; cada magia nao-criatura faz Servo (2 Servos: o usuario esqueceu o da Wanderer)")
def _():
    st = mk(turn=7, hand=["Chandra, Legacy of Fire", "The Eternal Wanderer"],
            bf=["Tam, the Possibility", "Dreamtide Whale", "Zagoth Triome", "Starting Town", "Boseiju, Who Endures", "Plaza of Heroes", "City of Brass", "Fellwar Stone", "Spara's Headquarters", "Watery Grave",
                P("Jace Token", loyalty=3, token=True), P("Saheeli, Sublime Artificer", loyalty=4), P("Aminatou, the Fateshifter", loyalty=5), P("Teferi, Hero of Dominaria", loyalty=6)])
    opp_all_colors(st)
    perm(st, "Dreamtide Whale").ctr["time"] = 2
    check(T.cast_card(st, "Chandra, Legacy of Fire") and loy(st, "Chandra, Legacy of Fire") == 3 and count(st, "Servo Token") == 1)
    check(act(st, "Chandra, Legacy of Fire", "Chandra, Legacy of Fire", "+1") and loy(st, "Chandra, Legacy of Fire") == 4)
    check(T.cast_card(st, "The Eternal Wanderer"), "Wanderer 5 de mana (com a Tam)")
    check(loy(st, "The Eternal Wanderer") == 5, "o gatilho da Whale resolve antes de a Wanderer entrar: %s" % loy(st, "The Eternal Wanderer"))
    check(loy(st, "Chandra, Legacy of Fire") == 5 and loy(st, "Teferi, Hero of Dominaria") == 7 and loy(st, "Jace Token") == 4 and loy(st, "Aminatou, the Fateshifter") == 6 and loy(st, "Saheeli, Sublime Artificer") == 5)
    check(perm(st, "Dreamtide Whale").ctr.get("time") == 3)
    check(count(st, "Servo Token") == 2, "Servo na Chandra e na Wanderer (Saheeli em campo): %d" % count(st, "Servo Token"))


@test("Manual #2 T7: Eternal Wanderer 0: Samurai 2/2 double strike (a lealdade nao muda)")
def _():
    st = mk(turn=7, bf=[P("The Eternal Wanderer", loyalty=5)])
    check(act(st, "The Eternal Wanderer", "The Eternal Wanderer", "0") and loy(st, "The Eternal Wanderer") == 5 and count(st, "Samurai Token") == 1)


@test("Manual #2 T7: o piscar da Aminatou -1 num Fellwar Stone VIRADO o devolve DESVIRADO (objeto novo) e ele rende mana de novo no mesmo turno: paga os {G}{G} da Wrenn (4 -> 2 com a Tam) junto da Triome")
def _():
    st = mk(turn=7, hand=["Wrenn and Realmbreaker"], bf=["Tam, the Possibility", P("Fellwar Stone", tapped=True), "Zagoth Triome", P("Aminatou, the Fateshifter", loyalty=6)])
    opp_all_colors(st)
    check(not T.can_cast_name(st, "Wrenn and Realmbreaker"), "so' a Triome desvirada: 1 mana")
    fw = T.blink(st, perm(st, "Fellwar Stone"), "Aminatou")
    check(fw is not None and not fw.tapped and fw in st.battlefield, "voltou desvirado")
    check(T.can_cast_name(st, "Wrenn and Realmbreaker") and T.cast_card(st, "Wrenn and Realmbreaker") and loy(st, "Wrenn and Realmbreaker") == 4)
    check(T.blink_value(st, fw) == 0.0, "POLITICA do simulador: `best_blink_target` nunca escolhe um Fellwar/rocha de mana virado (valor 0); o usuario fez isso no T7 pra pagar a Wrenn")


@test("Manual #2 T7: Wrenn and Realmbreaker (4) +1 (-> 5): terreno vira 3/3 Elemental vigilancia/hexproof/haste ate o proximo turno, e os terrenos viram 'T: qualquer cor'")
def _():
    st = mk(turn=7, bf=["Boseiju, Who Endures", "Zagoth Triome", P("Wrenn and Realmbreaker", loyalty=4)])
    check(act(st, "Wrenn and Realmbreaker", "Wrenn and Realmbreaker", "+1") and loy(st, "Wrenn and Realmbreaker") == 5)
    animated = [p for p in st.battlefield if "land" in p.card.types and T.is_creature(p)]
    check(len(animated) == 1 and T.power(st, animated[0]) == 3 and T.toughness(st, animated[0]) == 3, "um terreno virou 3/3")
    check(T.lands_any_color(st), "Wrenn: terrenos tocam por qualquer cor")


@test("Manual #2 T7: Jace -3 (4 -> 1) compra a Yavimaya; no modo de resiliencia a remocao do oponente (Swift End: destruir criatura ou planeswalker) mata um planeswalker meu")
def _():
    st = mk(turn=7, lib=["Yavimaya, Cradle of Growth", "Sol Ring"], bf=[P("Jace Token", loyalty=4, token=True)])
    check(act(st, "Jace Token", "Jace Token", "-3") and loy(st, "Jace Token") == 1 and "Yavimaya, Cradle of Growth" in st.hand)
    st = mk(turn=7, res=True, bf=[P("Teferi, Hero of Dominaria", loyalty=7), P("Chandra, Legacy of Fire", loyalty=5)])
    old = T.interaction_chance
    T.interaction_chance = lambda s: 1.0
    try:
        alvo = T.try_smart_opponent_removal(st, st.opps[0])
    finally:
        T.interaction_chance = old
    check(alvo in ("Teferi, Hero of Dominaria", "Chandra, Legacy of Fire") and perm(st, alvo) is None and st.m["smart_removals"] == 1, str(alvo))


@test("Manual #2 T8: Yavimaya, Cradle of Growth: cada terreno e' tambem Forest (a Triome e o Spara ja' eram; a Starting Town e a Plaza passam a produzir {G})")
def _():
    st = mk(turn=8, bf=["Starting Town", "Plaza of Heroes", "Yavimaya, Cradle of Growth"])
    opp_all_colors(st)
    check(T.yavimaya_forest(st), "Yavimaya em campo")
    check(T.can_pay(st, 0, (frozenset("G"), frozenset("G"), frozenset("G"))), "tres {G}: Town, Plaza e a propria Yavimaya")


@test("Manual #2 T6: Whale (3) + Teferi (4) = 7 de mana com 6 fontes (Spara entra virado): Saheeli -2 faz o Servo virar copia do Fellwar ate' o fim do turno, rende o 7o mana e paga o Teferi; no fim do turno volta a ser Servo 1/1 criatura")
def _():
    st = mk(turn=6, hand=["Dreamtide Whale", "Teferi, Hero of Dominaria"],
            bf=["Tam, the Possibility", P("Saheeli, Sublime Artificer", loyalty=5), P("Servo Token", token=True), "Fellwar Stone", "Zagoth Triome", "Starting Town", "Boseiju, Who Endures", "Plaza of Heroes", "City of Brass"])
    opp_all_colors(st)
    check(T.cast_card(st, "Dreamtide Whale"))
    check(not T.can_cast_name(st, "Teferi, Hero of Dominaria"), "Whale (3) + Teferi (4) = 7 > 6 fontes: falta 1")
    check(act(st, "Saheeli, Sublime Artificer", "Saheeli, Sublime Artificer", "-2") and loy(st, "Saheeli, Sublime Artificer") == 3)
    sv = perm(st, "Servo Token")
    check(sv.copy_of == "Fellwar Stone" and not T.is_creature(sv), "copia de artefato nao-criatura (sem doenca de invocacao)")
    check(T.can_cast_name(st, "Teferi, Hero of Dominaria") and T.cast_card(st, "Teferi, Hero of Dominaria") and sv.tapped, "o Servo-Fellwar foi virado pra pagar")
    T.end_step(st)
    check(sv.copy_of is None and T.is_creature(sv) and T.power(st, sv) == 1, "volta a ser Servo 1/1 criatura (virado)")


@test("Saheeli -2 em copia de artefato de MANA: Sol Ring rende 2 (Arcane Signet e Fellwar 1); Chromatic Orrery e The Chain Veil NAO sao copiados (lendarios: regra da lenda); sem carta que passe a caber, nao gasta lealdade na copia de mana")
def _():
    st = mk(turn=6, hand=["The Eternal Wanderer"], bf=["Tam, the Possibility", P("Saheeli, Sublime Artificer", loyalty=5), P("Servo Token", token=True), "Sol Ring", "Chromatic Orrery", "Arcane Signet", "Zagoth Triome", "Starting Town"])
    ch = T.saheeli_mana_choice(st)
    check(ch is not None and ch[1].card.name == "Sol Ring" and ch[2] == 2, str(ch and ch[1].card.name))
    st = mk(turn=6, bf=["Tam, the Possibility", P("Saheeli, Sublime Artificer", loyalty=5), P("Servo Token", token=True), "Chromatic Orrery", "The Chain Veil"])
    check(T.saheeli_mana_choice(st) is None, "so' lendarios: nada a copiar")
    st = mk(turn=6, hand=[], bf=["Tam, the Possibility", P("Saheeli, Sublime Artificer", loyalty=5), P("Servo Token", token=True), "Sol Ring", "Zagoth Triome", "Starting Town"])
    check(T.saheeli_mana_wanted(st) is None, "mao vazia: a copia de mana nao ajuda")
    T.SAHEELI_COPY_MANA_ARTIFACT = False
    try:
        st = mk(turn=6, hand=["Teferi, Hero of Dominaria"], bf=["Tam, the Possibility", P("Saheeli, Sublime Artificer", loyalty=5), P("Servo Token", token=True), "Fellwar Stone", "Zagoth Triome", "Starting Town", "Plaza of Heroes"])
        opp_all_colors(st)
        check(T.saheeli_mana_choice(st) is None and T.saheeli_mana_wanted(st) is None, "chave desligada: comportamento antigo")
    finally:
        T.SAHEELI_COPY_MANA_ARTIFACT = True


@test("Saheeli -2 vira mana ANTES de conjurar: numa partida inteira a IA usa a copia de mana (contador `saheeli_mana_copies`) em alguma semente, e nunca deixa mana fantasma (pool negativo = excecao)")
def _():
    hits = 0
    for sd in range(1, 41):
        r = T.simulate_one(sd, 10)
        hits += r.m.get("saheeli_mana_copies", 0) if hasattr(r, "m") else 0
    check(hits > 0, "a copia de mana tem de disparar em pelo menos uma das 40 partidas")

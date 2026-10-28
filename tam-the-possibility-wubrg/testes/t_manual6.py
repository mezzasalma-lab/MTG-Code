"""Cada clausula operacional do relato do usuario (goldfish manual #6, 2026-10-23; 11 blocos T1..T11, com foto da mao inicial) e' uma afirmacao testavel sobre o simulador (CLAUDE.md Regra #6).
Respostas do usuario de 2026-10-28 em `resultados-ab/2026-10-23-goldfish-manual-6/dados/respostas_usuario_2026-10-28.txt`: 2 e 7 CONFIRMADAS; 3 ("Lurker") e 9 respondidas; 1 e 6 "nao me lembro"; 4 respondida com uma
explicacao que o proprio log refuta para o T9 (o Gauntlet so' entra no T10 e o Flux Channeler no T11). Estes testes reproduzem as jogadas PELAS REGRAS (oraculo do cache do Scryfall), nao a leitura do usuario.
Os testes M6-T9 e M6-T4b documentam DIVERGENCIAS entre o relato e as regras (o simulador esta certo nos dois: a Tam proliferaria 4 vezes; o Oko do T4 nao cabe no mana)."""
from harness import *


def P(name, **kw):
    return (name, kw)


def opp_all_colors(st):
    for o in st.opps:
        o.land_colors = ["W", "U", "B", "R", "G"]


@test("Manual #6 T3: Tam ({1}{G}{U}) paga com Plaza of Heroes ({G}: so' pra magia LENDARIA, e a Tam e' lendaria) + Steam Vents ({U}) + Hallowed Fountain (generico); sem a Plaza nao ha {G}")
def _():
    st = mk(turn=3, bf=["Plaza of Heroes", "Steam Vents", "Hallowed Fountain"])
    check(T.can_cast_name(st, "Tam, the Possibility", "cz") and T.cast_card(st, "Tam, the Possibility", "cz") and perm(st, "Tam, the Possibility") is not None)
    st = mk(turn=3, bf=["Steam Vents", "Hallowed Fountain", "Watery Grave"])
    opp_all_colors(st)
    for o in st.opps:
        o.land_colors = ["W", "U", "B", "R"]
    check(not T.can_cast_name(st, "Tam, the Possibility", "cz"), "sem fonte de {G}: nao conjura")


@test("Manual #6 T4: Way of the Paradox ({2}{G}, lendaria: a Plaza paga o {G}) com 3 terrenos; ETB empower Jace 5 cria a ficha de Jace com 5 de lealdade; depois dela, o Oko (2 com a Tam) NAO cabe no mana")
def _():
    st = mk(turn=4, hand=["Way of the Paradox", "Oko, Thief of Crowns"], bf=["Tam, the Possibility", "Plaza of Heroes", "Steam Vents", "Hallowed Fountain"])
    check(T.cast_card(st, "Way of the Paradox"), "Paradox: Plaza ({G}, legendaria) + 2 terrenos")
    check(loy(st, "Jace Token") == 5, "empower 5: ficha de Jace com 5: %s" % loy(st, "Jace Token"))
    check(not T.can_cast_name(st, "Oko, Thief of Crowns"), "com 3 terrenos tapados pelo Paradox, o Oko ({G}{U} depois da Tam) nao cabe: o clique do Oko no T4 nao pode ter sido uma conjuracao paga (resposta 1: 'nao me lembro')")


@test("Manual #6 T4 (aritmetica da mao, apoio a duvida 1): 8 cartas no fim do turno -> descarta 1 (a Promise of Loyalty do usuario); com o Oko CONJURADO seriam 7 e nao haveria descarte")
def _():
    mao8 = ["Promise of Loyalty", "Oko, Thief of Crowns", "Dihada, Binder of Wills", "Domri, Chaos Bringer", "Liliana's Talent", "Wrenn and Realmbreaker", "Sanctum Lurker", "Way of the Mind Sculptor"]
    st = mk(turn=4, hand=list(mao8), bf=["Tam, the Possibility", "Plaza of Heroes", "Steam Vents", "Hallowed Fountain"])
    gy0 = len(st.graveyard)
    T.end_step(st)
    check(len(st.hand) == 7 and len(st.graveyard) == gy0 + 1, "8 -> 7, 1 descartada")
    st = mk(turn=4, hand=[c for c in mao8 if c != "Oko, Thief of Crowns"], bf=["Tam, the Possibility", "Plaza of Heroes", "Steam Vents", "Hallowed Fountain"])
    gy0 = len(st.graveyard)
    T.end_step(st)
    check(len(st.hand) == 7 and len(st.graveyard) == gy0, "7 cartas: nenhum descarte (se o Oko tivesse saido da mao, o log nao teria o descarte)")


@test("Manual #6 T4 (resposta 2: SIM): Jace `-3` compra 1 carta (L5 -> L2); o Way of the Paradox da' 1 de vida e um 2o terreno por ativacao de lealdade")
def _():
    st = mk(turn=4, hand=[], lib=["Way of the Mind Sculptor", "Sol Ring"], bf=["Tam, the Possibility", "Way of the Paradox", P("Jace Token", loyalty=5, token=True)])
    life = st.life
    check(act(st, "Jace Token", "Jace Token", "-3") and loy(st, "Jace Token") == 2 and st.hand == ["Way of the Mind Sculptor"], "compra 1: %s" % st.hand)
    check(st.life == life + 1 and st.extra_land_drops == 1 and T.land_drops_available(st) == 2, "Paradox: +1 de vida, 2o terreno")


@test("Manual #6 T5: Oko ({1}{G}{U} - 1 pela Tam) com Plaza + Mossfire Valley (filtro {1},{T}: {R}{G}) + Steam Vents; `+2` cria uma Food (L4 -> L6)")
def _():
    st = mk(turn=5, hand=["Oko, Thief of Crowns"], bf=["Tam, the Possibility", "Plaza of Heroes", "Steam Vents", "Hallowed Fountain", "Mossfire Valley"])
    opp_all_colors(st)
    check(T.can_cast_name(st, "Oko, Thief of Crowns") and T.cast_card(st, "Oko, Thief of Crowns") and loy(st, "Oko, Thief of Crowns") == 4)
    check(act(st, "Oko, Thief of Crowns", "Oko, Thief of Crowns", "+2") and loy(st, "Oko, Thief of Crowns") == 6 and count(st, "Food Token") == 1, "Oko +2: L6 e 1 Food")


@test("Manual #6 T6: Wrenn ({1}{G}{G} - 1 pela Tam) com Overflowing Basin (filtro {G}{U}) + Plaza + Mossfire; `+1` anima o Steam Vents (3/3 Elemental, vigilancia, hexproof, haste); o Oko `+1` faz da Food um Elk 3/3")
def _():
    st = mk(turn=6, hand=["Wrenn and Realmbreaker"], bf=["Tam, the Possibility", "Plaza of Heroes", "Steam Vents", "Hallowed Fountain", "Mossfire Valley", "Overflowing Basin", P("Oko, Thief of Crowns", loyalty=6), P("Food Token", token=True)])
    opp_all_colors(st)
    check(T.can_cast_name(st, "Wrenn and Realmbreaker") and T.cast_card(st, "Wrenn and Realmbreaker") and loy(st, "Wrenn and Realmbreaker") == 4)
    check(act(st, "Wrenn and Realmbreaker", "Wrenn and Realmbreaker", "+1") and loy(st, "Wrenn and Realmbreaker") == 5)
    animated = [p for p in st.battlefield if "land" in p.card.types and T.is_creature(p)]
    check(len(animated) == 1 and T.power(st, animated[0]) == 3 and T.toughness(st, animated[0]) == 3, "um terreno virou criatura 3/3")
    check(act(st, "Oko, Thief of Crowns", "Oko, Thief of Crowns", "+1") and loy(st, "Oko, Thief of Crowns") == 7, "Oko +1: L7 (a Food vira Elk)")
    elk = [p for p in st.battlefield if p.card.name == "Food Token"]
    check(len(elk) == 1 and T.is_creature(elk[0]) and T.power(st, elk[0]) == 3, "Food -> Elk 3/3")


@test("Manual #6 T7: Wooded Foothills (1 de vida, sacrificada) busca Indatha Triome (Plains Swamp Forest: e' Forest), que entra virada")
def _():
    st = mk(turn=7, hand=["Wooded Foothills"], lib=["Indatha Triome", "Sol Ring"], bf=["Tam, the Possibility", "Plaza of Heroes"])
    life = st.life
    T.play_land_phase(st)
    tri = perm(st, "Indatha Triome")
    check(tri is not None and tri.tapped and perm(st, "Wooded Foothills") is None and "Wooded Foothills" in st.graveyard and st.life == life - 1, "Triome em campo virada, fetch no cemiterio, -1 de vida")


@test("Manual #6 T8: Sanctum Lurker ({2}{B}, sem desconto da Tam: nao e' planeswalker) entra e empower Jace 1 cria a ficha de Jace com 1 de lealdade; da' a TODO planeswalker o `+2` (1 dano em cada oponente e 1 de vida). O L2 do log (resposta 3: 'Lurker') nao sai das regras: 1 -> L2 seria +1")
def _():
    st = mk(turn=8, hand=["Sanctum Lurker"], bf=["Tam, the Possibility", "Fellwar Stone", "Hallowed Fountain", "Overflowing Basin", "Indatha Triome", "Mossfire Valley", P("Oko, Thief of Crowns", loyalty=10)])
    opp_all_colors(st)
    check(T.can_cast_name(st, "Sanctum Lurker") and T.cast_card(st, "Sanctum Lurker"))
    check(loy(st, "Jace Token") == 1, "empower 1: L1 (nao L2): %s" % loy(st, "Jace Token"))
    life = st.life
    check(act(st, "Jace Token", "Sanctum Lurker", "+2") and loy(st, "Jace Token") == 3 and st.life == life + 1, "o +2 concedido pelo Lurker vale pra ficha de Jace: L3, +1 de vida")


@test("Manual #6 T8: o Prismari Command do oponente (`2 damage to any target`) mata o Sanctum Lurker: o Lurker e' 3/2 no oraculo (resposta 9: 'Prismari matou pelo 2 de dano'); a ficha de Jace fica em campo com o Lurker fora? (o texto estatico dele so' vale com ele em campo)")
def _():
    lurker = T.CARD_DB["Sanctum Lurker"]
    check((lurker.power, lurker.toughness) == (3, 2), "Lurker %s/%s" % (lurker.power, lurker.toughness))
    st = mk(turn=8, bf=["Tam, the Possibility", "Sanctum Lurker", P("Jace Token", loyalty=2, token=True)])
    lk = perm(st, "Sanctum Lurker")
    check(T.toughness(st, lk) == 2)


@test("Manual #6 T9 (DIVERGENCIA DO RELATO): Tam `{W}{U}{B}{R}{G},{T}: Proliferate X times`, X = tipos de planeswalker (Oko, Domri, Wrenn, Jace = 4): proliferaria 4 VEZES (+4 em cada um); o log do usuario tem UMA onda de +1")
def _():
    st = mk(turn=9, bf=["Tam, the Possibility", "Undergrowth Stadium", "Steam Vents", "Overflowing Basin", "Indatha Triome", "Hallowed Fountain", "Mossfire Valley",
                        P("Oko, Thief of Crowns", loyalty=10), P("Domri, Chaos Bringer", loyalty=7), P("Wrenn and Realmbreaker", loyalty=7), P("Jace Token", loyalty=2, token=True)])
    opp_all_colors(st)
    check(T.pw_types(st) == 4, "4 tipos")
    check(T.act_tam_proliferate(st), "a Tam ativa")
    got = (loy(st, "Oko, Thief of Crowns"), loy(st, "Domri, Chaos Bringer"), loy(st, "Wrenn and Realmbreaker"), loy(st, "Jace Token"))
    check(got == (14, 11, 11, 6), "4 proliferates: +4 em cada um; recebi %s (o log do usuario: 11, 8, 8, 3)" % (got,))


@test("Manual #6 T9: Wrenn `-7` (L8 -> L1) cria o emblema ('play lands and cast permanent spells from your graveyard'); Jace `-1` faz Surveil 1")
def _():
    st = mk(turn=9, bf=["Tam, the Possibility", P("Wrenn and Realmbreaker", loyalty=8), P("Jace Token", loyalty=3, token=True)], lib=["Stomping Ground", "Sol Ring"])
    check(act(st, "Wrenn and Realmbreaker", "Wrenn and Realmbreaker", "-7") and loy(st, "Wrenn and Realmbreaker") == 1 and "wrenn" in st.emblems)
    check(act(st, "Jace Token", "Jace Token", "-1") and loy(st, "Jace Token") == 2)


@test("Manual #6 T10: com o emblema da Wrenn, o Stomping Ground do cemiterio e' jogado como terreno e o Way of the Mind Sculptor ({4}{U} = 5, SEM desconto: nao e' planeswalker) e' conjurado do cemiterio; empower Jace 5: L2 -> L7")
def _():
    st = mk(turn=10, gy=["Stomping Ground", "Way of the Mind Sculptor"], bf=["Tam, the Possibility", "Hallowed Fountain", "Fellwar Stone", "Steam Vents", "Overflowing Basin", "Way of the Paradox", P("Wrenn and Realmbreaker", loyalty=1), P("Jace Token", loyalty=2, token=True)])
    st.emblems.append("wrenn")
    opp_all_colors(st)
    T.play_land_phase(st)
    check(perm(st, "Stomping Ground") is not None and "Stomping Ground" not in st.graveyard, "terreno jogado do cemiterio")
    check(T.can_cast_name(st, "Way of the Mind Sculptor", "graveyard") and T.cast_card(st, "Way of the Mind Sculptor", "graveyard") and loy(st, "Jace Token") == 7, "Jace %s" % loy(st, "Jace Token"))


@test("Manual #6 T10: Jace `-3` com o Way of the Mind Sculptor em campo compra 2 (a habilidade + 'if you removed two or more loyalty counters, draw a card'): Vronos e City of Brass; o Paradox da' o 2o terreno")
def _():
    st = mk(turn=10, lib=["Vronos, Masked Inquisitor", "City of Brass", "Sol Ring"], bf=["Tam, the Possibility", "Way of the Paradox", "Way of the Mind Sculptor", P("Jace Token", loyalty=7, token=True)])
    life = st.life
    check(act(st, "Jace Token", "Jace Token", "-3") and loy(st, "Jace Token") == 4 and st.hand == ["Vronos, Masked Inquisitor", "City of Brass"], "compra 2: %s" % st.hand)
    check(st.life == life + 1 and T.land_drops_available(st) == 2)


@test("Manual #6 T10: Tezzeret the Seeker ({3}{U}{U} - 1 = 4) entra com 4; `-X` com X=3 busca um artefato de MV <= 3 (Ichormoon Gauntlet) direto pro campo (L4 -> L1)")
def _():
    st = mk(turn=10, hand=["Tezzeret the Seeker"], lib=["Ichormoon Gauntlet", "Command Tower"], bf=["Tam, the Possibility", "Undergrowth Stadium", "Plaza of Heroes", "Indatha Triome", "Hallowed Fountain", "Steam Vents", "Overflowing Basin"])
    opp_all_colors(st)
    check(T.can_cast_name(st, "Tezzeret the Seeker") and T.cast_card(st, "Tezzeret the Seeker") and loy(st, "Tezzeret the Seeker") == 4)
    check(act(st, "Tezzeret the Seeker", "Tezzeret the Seeker", "-X", x=3) and loy(st, "Tezzeret the Seeker") == 1 and perm(st, "Ichormoon Gauntlet") is not None, "Gauntlet em campo (library -> battlefield)")


@test("Manual #6 T10 (DIFERENCA DE POLITICA, nao de regra): com Sol Ring E Gauntlet na biblioteca, o `-X` do simulador busca o Sol Ring (TEZZ_PRIORITY 55 > 50); o usuario buscou o Gauntlet (com 4 planeswalkers + Tam, o Gauntlet vale mais). O log nao diz se o Sol Ring estava na biblioteca")
def _():
    st = mk(turn=10, hand=[], lib=["Ichormoon Gauntlet", "Sol Ring"], bf=["Tam, the Possibility", P("Tezzeret the Seeker", loyalty=4)])
    check(T.tezzeret_pick(st, 3) == "Sol Ring", "politica atual: Sol Ring")
    check(T.tezzeret_pick(st, 3) != "Ichormoon Gauntlet")


@test("Manual #6 T11 (resposta 5): a Kiora ({1}{G}{U}) e' ANULADA pelo contra-feitico do simulador de interacao e vai ao cemiterio; com o emblema da Wrenn e' conjurada de novo do cemiterio e entra (custo de novo: 3)")
def _():
    st = mk(turn=11, res=True, hand=["Kiora of Salt and Sand"], bf=["Tam, the Possibility", "Undergrowth Stadium", "Plaza of Heroes", "Indatha Triome", "Hallowed Fountain", "Steam Vents", "Overflowing Basin"])
    st.emblems.append("wrenn")
    opp_all_colors(st)
    old = T.interaction_chance
    T.interaction_chance = lambda s: 1.0
    try:
        T.cast_card(st, "Kiora of Salt and Sand")
    finally:
        T.interaction_chance = old
    check(perm(st, "Kiora of Salt and Sand") is None and "Kiora of Salt and Sand" in st.graveyard and st.m["our_spells_countered"] == 1, "anulada: cemiterio")
    T.interaction_chance = lambda s: 0.0
    try:
        check(T.can_cast_name(st, "Kiora of Salt and Sand", "graveyard") and T.cast_card(st, "Kiora of Salt and Sand", "graveyard") and perm(st, "Kiora of Salt and Sand") is not None, "do cemiterio pelo emblema")
    finally:
        T.interaction_chance = old


@test("Manual #6 T11: Ichormoon Gauntlet `[0]: Proliferate` em 3 planeswalkers (Wrenn, Tezzeret, Domri) = 3 proliferates: +3 em TODOS os planeswalkers; Oko `-12` (Gauntlet) 15 -> 3 enfileira o turno extra (resposta 7: CONFERE; ele nao passou o turno)")
def _():
    st = mk(turn=11, bf=["Tam, the Possibility", "Ichormoon Gauntlet", P("Wrenn and Realmbreaker", loyalty=1), P("Tezzeret the Seeker", loyalty=1), P("Domri, Chaos Bringer", loyalty=10), P("Oko, Thief of Crowns", loyalty=14), P("Jace Token", loyalty=4, token=True)])
    for n in ("Wrenn and Realmbreaker", "Tezzeret the Seeker", "Domri, Chaos Bringer"):
        check(act(st, n, "Ichormoon Gauntlet", "0"), "[0] do Gauntlet em " + n)
    check((loy(st, "Wrenn and Realmbreaker"), loy(st, "Tezzeret the Seeker"), loy(st, "Domri, Chaos Bringer"), loy(st, "Oko, Thief of Crowns"), loy(st, "Jace Token")) == (4, 4, 13, 17, 7),
          "3 proliferates em todos: %s" % ((loy(st, "Wrenn and Realmbreaker"), loy(st, "Tezzeret the Seeker"), loy(st, "Domri, Chaos Bringer"), loy(st, "Oko, Thief of Crowns"), loy(st, "Jace Token")),))
    check(act(st, "Oko, Thief of Crowns", "Ichormoon Gauntlet", "-12") and loy(st, "Oko, Thief of Crowns") == 5 and st.extra_turns_queued == 1, "turno extra enfileirado")


@test("Manual #6 T11: Dihada ({1}{R}{W}{B} - 1 = 3) entra com 5 e recebe a onda de proliferate pelo `[0]` dela mesma (L5 -> L6), depois que o Gauntlet ja' estava em campo")
def _():
    st = mk(turn=11, hand=["Dihada, Binder of Wills"], bf=["Tam, the Possibility", "Ichormoon Gauntlet", "Plaza of Heroes", "Steam Vents", "Hallowed Fountain", "Indatha Triome"])
    opp_all_colors(st)
    check(T.can_cast_name(st, "Dihada, Binder of Wills") and T.cast_card(st, "Dihada, Binder of Wills") and loy(st, "Dihada, Binder of Wills") == 5)
    check(act(st, "Dihada, Binder of Wills", "Ichormoon Gauntlet", "0") and loy(st, "Dihada, Binder of Wills") == 6, "[0]: proliferate no proprio Dihada: L6")


@test("Manual #6 (apoio a duvida 6): dos 11 turnos so' 2 compras de Jace (-3) no T10 e no T11 + 1 do WotMS cada; o Dack Fayden do T11 (library -> hand) NAO tem fonte de compra no log: o Staff of Compleation ({T}, 4 de vida: compra) nunca foi conjurado")
def _():
    import json, os
    log = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados-ab", "2026-10-23-goldfish-manual-6", "dados", "goldfish_manual_6_bruto.json")))
    t11 = log[10]
    nomes_t11 = [e["name"] for e in t11]
    check("Dack Fayden" in nomes_t11 and "Staff of Compleation" in nomes_t11)
    staff = [e for e in t11 if e["name"] == "Staff of Compleation"]
    check(all(e["toZone"] != "battlefield" for e in staff), "Staff: library -> hand e mais nada")
    check(all(e["name"] != "Dihada, Binder of Wills" or e["toZone"] == "battlefield" for e in t11 if e["fromZone"] == "hand"), "o Dihada so' entra DEPOIS do Dack no log (indice)")
    i_dack = next(i for i, e in enumerate(t11) if e["name"] == "Dack Fayden")
    i_dihada = next(i for i, e in enumerate(t11) if e["name"] == "Dihada, Binder of Wills" and e["toZone"] == "battlefield")
    check(i_dack < i_dihada, "o -3 do Dihada (revela 4 e pega as lendarias) nao explica o Dack: ele ja' estava na mao antes da conjuracao do Dihada")

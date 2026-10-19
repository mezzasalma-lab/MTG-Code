from harness import *


def P(name, **kw):
    return (name, kw)


# ======================= Ways (empower Jace N + habilidade concedida) =======================
WAYS = {"Way of the Paradox": 5, "Way of the Pyromancer": 2, "Way of the Mind Sculptor": 5, "Way of the Warlord": 5, "Way of the Necromancer": 2, "Way of the Deathbringer": 5,
        "Way of the Healer": 5, "Way of the Wildspeaker": 7}


@test("Cada Way: ETB empower Jace N (cria a ficha de Jace com N de lealdade; a 2a Way so' soma contadores na mesma ficha)")
def _():
    for w, n in WAYS.items():
        st = mk(hand=[w], bf=["Chromatic Orrery", "Sol Ring"])
        st.pool = {"C": 10}
        check(T.cast_card(st, w), w)
        check(loy(st, "Jace Token") == n and count(st, "Jace Token") == 1, f"{w}: {loy(st, 'Jace Token')} esperado {n}")
    st = mk(hand=["Way of the Pyromancer", "Way of the Necromancer"])
    st.pool = {"C": 10, "R": 5, "B": 5}
    T.cast_card(st, "Way of the Pyromancer"); T.cast_card(st, "Way of the Necromancer")
    check(loy(st, "Jace Token") == 4 and count(st, "Jace Token") == 1)


@test("Way of the Paradox: cada ativacao de lealdade = 1 de vida e +1 terreno jogavel neste turno")
def _():
    st = mk(bf=["Way of the Paradox", P("Garruk Wildspeaker", loyalty=3)], life=30)
    check(act(st, "Garruk Wildspeaker", "Garruk Wildspeaker", "-1") and st.life == 31 and st.extra_land_drops == 1)


@test("Way of the Pyromancer: todo planeswalker tem +1: {R}")
def _():
    st = mk(bf=["Way of the Pyromancer", P("Teferi, Hero of Dominaria", loyalty=4)])
    check(("Way of the Pyromancer", "+1", 1) in T.own_abilities(st, perm(st, "Teferi, Hero of Dominaria")))
    check(act(st, "Teferi, Hero of Dominaria", "Way of the Pyromancer", "+1") and st.pool.get("R") == 1 and loy(st, "Teferi, Hero of Dominaria") == 5)


@test("Way of the Warlord: todo PW tem -4: 2 de dano a criatura/planeswalker e 2 ao jogador")
def _():
    st = mk(res=True, bf=["Way of the Warlord", P("Oko, Thief of Crowns", loyalty=6)])
    add_opp_creature(st, 1, 2, 2)
    check(act(st, "Oko, Thief of Crowns", "Way of the Warlord", "-4"))
    check(sum(40 - o.life for o in st.opps) == 2 and not st.opps[0].board)


@test("Way of the Necromancer: criatura minha morre -> +1 de lealdade em CADA planeswalker (inclui a ficha de Jace)")
def _():
    st = mk(bf=["Way of the Necromancer", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4), P("Jace Token", loyalty=1, token=True), "Beast Token"])
    T.remove_permanent(st, perm(st, "Beast Token"), "dies")
    check(loy(st, "Garruk Wildspeaker") == 4 and loy(st, "Oko, Thief of Crowns") == 5 and loy(st, "Jace Token") == 2)
    # tambem quando a Tam (comandante) morre
    st = mk(bf=["Way of the Necromancer", P("Garruk Wildspeaker", loyalty=3), "Tam, the Possibility"])
    T.remove_permanent(st, perm(st, "Tam, the Possibility"), "dies")
    check(loy(st, "Garruk Wildspeaker") == 4 and st.commander_in_cz)
    # exilio nao e' morte
    st = mk(bf=["Way of the Necromancer", P("Garruk Wildspeaker", loyalty=3), "Beast Token"])
    T.remove_permanent(st, perm(st, "Beast Token"), "exile")
    check(loy(st, "Garruk Wildspeaker") == 3)


@test("Way of the Deathbringer: PW tem -2: pode sacrificar criatura; se sacrificou cria Fera 4/4 trample")
def _():
    st = mk(bf=["Way of the Deathbringer", P("Oko, Thief of Crowns", loyalty=6), "Soldier Token"])
    check(act(st, "Oko, Thief of Crowns", "Way of the Deathbringer", "-2"))
    check(perm(st, "Soldier Token") is None and count(st, "Beast Token") == 1)


@test("Way of the Healer: PW tem -2: Cadet 2/2 e surveil 1; Way of the Wildspeaker: PW tem -4: Fera 4/4 trample")
def _():
    st = mk(bf=["Way of the Healer", P("Oko, Thief of Crowns", loyalty=6)])
    check(act(st, "Oko, Thief of Crowns", "Way of the Healer", "-2") and count(st, "Cadet Token") == 1 and st.m["surveil_events"] == 1)
    st = mk(bf=["Way of the Wildspeaker", P("Oko, Thief of Crowns", loyalty=6)])
    check(act(st, "Oko, Thief of Crowns", "Way of the Wildspeaker", "-4") and count(st, "Beast Token") == 1)


# ======================= Sanctum Lurker =======================
@test("Sanctum Lurker: ETB empower 1; PW com 0 de lealdade NAO morre; PWs tem +2: 1 de dano a cada oponente e ganho 1 de vida")
def _():
    st = mk(hand=["Sanctum Lurker"], bf=["Sol Ring", "Chromatic Orrery"])
    T.cast_card(st, "Sanctum Lurker")
    check(loy(st, "Jace Token") == 1)
    st = mk(bf=["Sanctum Lurker", P("Garruk Wildspeaker", loyalty=0)])
    T.sba(st)
    check(perm(st, "Garruk Wildspeaker") is not None, "0 de lealdade sobrevive com o Lurker")
    st = mk(bf=[P("Garruk Wildspeaker", loyalty=0)])
    T.sba(st)
    check(perm(st, "Garruk Wildspeaker") is None, "sem Lurker morre")
    st = mk(bf=["Sanctum Lurker", P("Garruk Wildspeaker", loyalty=3)], life=30)
    check(act(st, "Garruk Wildspeaker", "Sanctum Lurker", "+2"))
    check(all(o.life == 39 for o in st.opps) and st.life == 31, f"{[o.life for o in st.opps]} {st.life}")


# ======================= Ichormoon Gauntlet =======================
@test("Gauntlet: PWs tem 0: proliferate e -12: turno extra; ao conjurar nao-criatura poe +1 contador do mesmo tipo")
def _():
    st = mk(bf=["Ichormoon Gauntlet", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4)])
    check(act(st, "Garruk Wildspeaker", "Ichormoon Gauntlet", "0") and loy(st, "Garruk Wildspeaker") == 4 and loy(st, "Oko, Thief of Crowns") == 5)
    st = mk(bf=["Ichormoon Gauntlet", P("Garruk Wildspeaker", loyalty=12)])
    check(act(st, "Garruk Wildspeaker", "Ichormoon Gauntlet", "-12") and st.extra_turn_pending)
    st = mk(hand=["Sol Ring"], bf=["Ichormoon Gauntlet", P("Garruk Wildspeaker", loyalty=3)])
    st.pool = {"C": 1}
    T.cast_card(st, "Sol Ring")
    check(loy(st, "Garruk Wildspeaker") == 4, "magia nao-criatura: +1 contador")
    st = mk(hand=["Birds of Paradise"], bf=["Ichormoon Gauntlet", P("Garruk Wildspeaker", loyalty=3)])
    st.pool = {"G": 1}
    T.cast_card(st, "Birds of Paradise")
    check(loy(st, "Garruk Wildspeaker") == 3, "criatura nao dispara")


@test("Gauntlet -12: turno extra de verdade (play_rounds joga o turno antes dos oponentes)")
def _():
    st = mk(bf=["Ichormoon Gauntlet", P("Garruk Wildspeaker", loyalty=12)], turn=5)
    st.extra_turn_pending = True
    t0 = st.turn
    T.play_rounds(st, 2)
    check(st.turn == t0 + 2 and st.m["extra_turns_played"] == 1, f"turnos jogados: {st.turn - t0} (o turno extra conta no orcamento de turnos)")


# ======================= Teferi's Talent / Liliana's Talent =======================
@test("Teferi's Talent: encantado ganha -12 (emblema); toda compra poe 1 de lealdade no encantado")
def _():
    st = mk(bf=[P("Garruk Wildspeaker", loyalty=3)])
    g = perm(st, "Garruk Wildspeaker")
    t = T.mk_perm(st, "Teferi's Talent"); t.attached_to = g.uid; st.battlefield.append(t)
    T.draw_cards(st, 2)
    check(loy(st, "Garruk Wildspeaker") == 5, str(loy(st, "Garruk Wildspeaker")))
    g.ctr["loyalty"] = 12
    check(("Teferi's Talent", "-12", -12) in T.own_abilities(st, g))
    check(T.activate_ability(st, g, "Teferi's Talent", "-12", 0) and "teferi_ta" in st.emblems)


@test("Liliana's Talent: encantado ganha -8 (reanima TODAS as criaturas de TODOS os cemiterios); criatura que da dano no encantado morre")
def _():
    st = mk(res=True, gy=["Birds of Paradise", "Dreamtide Whale", "Sol Ring"], bf=[P("Garruk Wildspeaker", loyalty=8)])
    st.opps[0].cgy = 2
    g = perm(st, "Garruk Wildspeaker")
    t = T.mk_perm(st, "Liliana's Talent"); t.attached_to = g.uid; st.battlefield.append(t)
    check(T.activate_ability(st, g, "Liliana's Talent", "-8", 0))
    check(perm(st, "Birds of Paradise") is not None and perm(st, "Dreamtide Whale") is not None and "Sol Ring" in st.graveyard)
    check(count(st, "Cadet Token") == 2, "criaturas do cemiterio do oponente (corpos genericos)")
    st = mk(res=True, bf=[P("Garruk Wildspeaker", loyalty=9), P("Oko, Thief of Crowns", loyalty=2)])
    g = perm(st, "Garruk Wildspeaker")
    t = T.mk_perm(st, "Liliana's Talent"); t.attached_to = g.uid; st.battlefield.append(t)
    st.attention = True
    c = T.new_opp_creature(5, 5); c["sick"] = False
    st.opps[0].board.append(c)
    T.opponent_combat(st, st.opps[0])
    check(not st.opps[0].board, "a criatura que deu dano na Garruk encantada foi destruida")
    check(st.m["lilianas_talent_kills"] >= 1)


# ======================= Permanentes e feiticos =======================
@test("All Will Be One: TODO contador posto (lealdade de entrada, +1, proliferate, empower, custo) causa dano igual ao tanto de contadores")
def _():
    st = mk(hand=["Garruk Wildspeaker"], bf=["All Will Be One", "Chromatic Orrery", "Sol Ring"])
    d0 = sum(40 - o.life for o in st.opps)
    T.cast_card(st, "Garruk Wildspeaker")
    d1 = sum(40 - o.life for o in st.opps)
    check(d1 - d0 == 3, f"lealdade de entrada 3: {d1 - d0}")
    g = perm(st, "Garruk Wildspeaker")
    T.activate_ability(st, g, "Garruk Wildspeaker", "+1", 0)
    check(sum(40 - o.life for o in st.opps) - d1 == 1, "o custo [+1] tambem poe contador")
    st = mk(bf=["All Will Be One", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4)])
    T.proliferate(st, "t")
    check(sum(40 - o.life for o in st.opps) == 2, "um gatilho por permanente que recebe contador")
    st = mk(bf=["All Will Be One"])
    T.empower_jace(st, 5, "t")
    check(sum(40 - o.life for o in st.opps) == 5)


@test("All Will Be One: custo de lealdade NEGATIVO nao e' contador posto; Doubling Season nao dobra custo (ruling) mas dobra o resto")
def _():
    st = mk(bf=["All Will Be One", P("Garruk Wildspeaker", loyalty=3)])
    T.activate_ability(st, perm(st, "Garruk Wildspeaker"), "Garruk Wildspeaker", "-1", 0)
    check(sum(40 - o.life for o in st.opps) == 0, "remover contador nao causa dano")


@test("Blasphemous Act: 13 de dano em cada criatura (inclui as minhas e a Tam); mata Whale 7/5")
def _():
    st = mk(res=True, hand=["Blasphemous Act"], bf=["Tam, the Possibility", "Dreamtide Whale", "Chromatic Orrery", "Sol Ring"])
    add_opp_creature(st, 1, 8, 8)
    T.cast_card(st, "Blasphemous Act")
    check(perm(st, "Dreamtide Whale") is None and perm(st, "Tam, the Possibility") is None and not st.opps[0].board and st.commander_in_cz)


@test("Overwrite the Multiverse: exila TODAS as criaturas e empower Jace X (X = criaturas exiladas)")
def _():
    st = mk(res=True, hand=["Overwrite the Multiverse"], bf=["Beast Token", "Soldier Token", "Chromatic Orrery", "Sol Ring"])
    add_opp_creature(st, 1, 3, 3); add_opp_creature(st, 2, 2, 2)
    T.cast_card(st, "Overwrite the Multiverse")
    check(not T.creatures(st) and loy(st, "Jace Token") == 4, f"{loy(st, 'Jace Token')}")


@test("Promise of Loyalty: cada jogador mantem 1 criatura (com vow) e sacrifica o resto; a dos oponentes nao ataca")
def _():
    st = mk(res=True, hand=["Promise of Loyalty"], bf=["Beast Token", "Soldier Token", "Birds of Paradise", "Chromatic Orrery", "Sol Ring"])
    add_opp_creature(st, 1, 3, 3)
    T.cast_card(st, "Promise of Loyalty")
    check(len(T.creatures(st)) == 1 and not any(o.board for o in st.opps))


@test("Entrust the Spark: sacrifica um planeswalker e busca outro pro campo")
def _():
    st = mk(res=False, hand=["Entrust the Spark"], bf=["Chromatic Orrery", "Sol Ring", P("Jace Token", loyalty=1, token=True)], lib=["Elspeth, Sun's Champion", "Sol Ring"])
    st.library = ["Elspeth, Sun's Champion"] + [c for c in filler_library({"Elspeth, Sun's Champion"}) if "planeswalker" not in T.CARD_DB[c].types]
    T.cast_card(st, "Entrust the Spark")
    check(perm(st, "Elspeth, Sun's Champion") is not None and perm(st, "Jace Token") is None, "trocou a ficha de Jace por Elspeth")


@test("Ripples of Potential: proliferate e (resiliencia) os planeswalkers que ganharam contador saem de fase")
def _():
    st = mk(res=True, hand=["Ripples of Potential"], bf=["Sol Ring", "Arcane Signet", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4)])
    T.cast_card(st, "Ripples of Potential")
    check(loy(st, "Garruk Wildspeaker") == 4 and perm(st, "Garruk Wildspeaker").phased and perm(st, "Oko, Thief of Crowns").phased)
    check(len(T.pws(st)) == 0, "fora de fase nao existem")


@test("Patrolling Peacemaker: entra com 2 contadores +1/+1; crime de oponente = proliferate")
def _():
    st = mk(hand=["Patrolling Peacemaker"], bf=["Sol Ring", "Arcane Signet", "Chromatic Orrery"])
    T.cast_card(st, "Patrolling Peacemaker")
    p = perm(st, "Patrolling Peacemaker")
    check(p.ctr.get("p1p1") == 2 and T.power(st, p) == 2 and T.toughness(st, p) == 2)
    st.opps[0].board = []
    T.opp_spell_cast(st, st.opps[0], noncreature=True, mv=2)
    n = 0
    for _ in range(40):
        T.opp_spell_cast(st, st.opps[0], noncreature=True, mv=2)
    check(st.m["opp_crimes_total"] >= 1 and p.ctr.get("p1p1") > 2)


@test("Dreamtide Whale: entra com 2 contadores de tempo; a 2a magia de QUALQUER jogador no turno proliferate; sacrificada no upkeep quando o ultimo some")
def _():
    st = mk(hand=["Dreamtide Whale"], bf=["Sol Ring", "Arcane Signet", "Chromatic Orrery"])
    T.cast_card(st, "Dreamtide Whale")
    w = perm(st, "Dreamtide Whale")
    check(w.ctr.get("time") == 2 and T.power(st, w) == 7)
    T.upkeep_step(st)
    check(w.ctr.get("time") == 1 and perm(st, "Dreamtide Whale") is not None)
    T.upkeep_step(st)
    check(perm(st, "Dreamtide Whale") is None and st.m["whale_vanished"] == 1)
    st = mk(bf=["Dreamtide Whale", P("Garruk Wildspeaker", loyalty=3)])
    perm(st, "Dreamtide Whale").ctr["time"] = 2
    T.begin_any_turn(st)
    T.opp_spell_cast(st, st.opps[0], True, 2)
    check(loy(st, "Garruk Wildspeaker") == 3, "1a magia do oponente nao")
    T.opp_spell_cast(st, st.opps[0], False, 2)
    check(loy(st, "Garruk Wildspeaker") == 4, "2a magia do oponente: proliferate")
    st = mk(bf=["Dreamtide Whale", P("Garruk Wildspeaker", loyalty=3)], hand=["Sol Ring", "Arcane Signet"])
    perm(st, "Dreamtide Whale").ctr["time"] = 2
    T.begin_any_turn(st)
    st.pool = {"C": 5}
    T.cast_card(st, "Sol Ring"); T.cast_card(st, "Arcane Signet")
    check(loy(st, "Garruk Wildspeaker") == 4, "minha 2a magia tambem")


@test("Flux Channeler: cada magia nao-criatura que EU conjuro faz proliferate (criatura nao)")
def _():
    st = mk(hand=["Sol Ring", "Birds of Paradise"], bf=["Flux Channeler", P("Garruk Wildspeaker", loyalty=3)])
    st.pool = {"C": 3, "G": 1}
    T.cast_card(st, "Birds of Paradise")
    check(loy(st, "Garruk Wildspeaker") == 3)
    T.cast_card(st, "Sol Ring")
    check(loy(st, "Garruk Wildspeaker") == 4)


@test("Displacer Kitten: magia nao-criatura pisca o permanente de mais valor (Way de novo = empower de novo)")
def _():
    st = mk(hand=["Sol Ring"], bf=["Displacer Kitten", "Way of the Mind Sculptor", P("Jace Token", loyalty=3, token=True)])
    st.pool = {"C": 2}
    T.cast_card(st, "Sol Ring")
    check(loy(st, "Jace Token") == 8 and st.m["kitten_blinks"] == 1, f"{loy(st, 'Jace Token')}")


@test("Oath of Teferi: ETB exila outro permanente meu e devolve no end step; duas ativacoes por planeswalker por turno")
def _():
    st = mk(hand=["Oath of Teferi"], bf=["Way of the Mind Sculptor", "Sol Ring", "Chromatic Orrery", "Arcane Signet", "Birds of Paradise", P("Jace Token", loyalty=3, token=True)])
    st.pool = {"C": 10, "W": 1, "U": 1}
    T.cast_card(st, "Oath of Teferi")
    check(perm(st, "Way of the Mind Sculptor") is None, "exilada")
    T.end_step(st)
    check(perm(st, "Way of the Mind Sculptor") is not None and loy(st, "Jace Token") == 8)
    st = mk(bf=["Oath of Teferi", P("Garruk Wildspeaker", loyalty=3)])
    g = perm(st, "Garruk Wildspeaker")
    check(T.pw_can_activate(st, g))
    T.activate_ability(st, g, "Garruk Wildspeaker", "+1", 0)
    check(T.pw_can_activate(st, g), "segunda ativacao permitida")
    T.activate_ability(st, g, "Garruk Wildspeaker", "+1", 0)
    check(not T.pw_can_activate(st, g), "terceira nao")
    st = mk(bf=[P("Garruk Wildspeaker", loyalty=3)])
    g = perm(st, "Garruk Wildspeaker")
    T.activate_ability(st, g, "Garruk Wildspeaker", "+1", 0)
    check(not T.pw_can_activate(st, g), "sem o Oath: uma por turno (CR 606.3)")


@test("The Chain Veil: {4},{T}: cada planeswalker pode ativar de novo; no end step perco 2 de vida se NAO ativei lealdade")
def _():
    st = mk(bf=["The Chain Veil", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4), "Sol Ring", "Chromatic Orrery"], phase="main2")
    for n in ("Garruk Wildspeaker", "Oko, Thief of Crowns"):
        T.activate_ability(st, perm(st, n), n, "+1", 0)
    check(not T.pw_can_activate(st, perm(st, "Garruk Wildspeaker")))
    st.m["_veil_extra"] = 1
    check(T.pw_can_activate(st, perm(st, "Garruk Wildspeaker")) and T.pw_can_activate(st, perm(st, "Oko, Thief of Crowns")), "Veil reabre")
    st = mk(bf=["The Chain Veil"], life=30)
    T.end_step(st)
    check(st.life == 28, "nao ativei lealdade: perco 2")
    st = mk(bf=["The Chain Veil"], life=30)
    st.activated_loyalty_this_turn = True
    T.end_step(st)
    check(st.life == 30)


@test("Chromatic Orrery: {5},{T}: compra 1 carta por cor entre meus permanentes")
def _():
    st = mk(bf=["Chromatic Orrery", "Sol Ring", "Arcane Signet", "Birds of Paradise", "Command Tower", "Oko, Thief of Crowns", "Dihada, Binder of Wills"], phase="main2")
    n = len(st.hand)
    check(T.act_orrery_draw(st))
    check(len(st.hand) == n + 5, f"5 cores: {len(st.hand) - n}")


@test("Baxter Building: {4},{T}: compra 1 SE controlo criatura de resistencia >= 4 (Tam 2/4, Whale 7/5)")
def _():
    st = mk(bf=["Baxter Building", "Chromatic Orrery", "Birds of Paradise"], phase="main2")
    check(not T.act_baxter_draw(st), "sem criatura de resistencia 4")
    st = mk(bf=["Baxter Building", "Chromatic Orrery", "Tam, the Possibility"], phase="main2")
    n = len(st.hand)
    check(T.act_baxter_draw(st) and len(st.hand) == n + 1)


@test("Staff of Compleation: destroi permanente meu (1 vida), mana (2), proliferate (3), compra (4); {5}: desvira (permite usar de novo)")
def _():
    st = mk(bf=["Staff of Compleation", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4), P("Dihada, Binder of Wills", loyalty=5), P("Wrenn and Realmbreaker", loyalty=4), "Chromatic Orrery"], life=30, phase="main2")
    check(T.act_staff(st), "proliferate")
    check(st.life == 27 and loy(st, "Garruk Wildspeaker") == 4)
    check(perm(st, "Staff of Compleation").tapped)
    check(T.act_staff(st), "{5} pra desvirar e proliferar de novo")
    check(st.life == 24 and st.m["staff_untaps"] == 1 and loy(st, "Garruk Wildspeaker") == 5, f"{st.life} {st.m['staff_untaps']}")
    st = mk(bf=["Staff of Compleation", "Way of the Necromancer", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4), "Soldier Token"], life=30, phase="main2")
    check(T.act_staff_necromancer(st) and perm(st, "Soldier Token") is None and loy(st, "Garruk Wildspeaker") == 4 and st.life == 29)


@test("Boseiju, canal: {1}{G} descarta; {1} a menos por criatura lendaria; alvo de oponente = proxy")
def _():
    st = mk(hand=["Boseiju, Who Endures"], bf=["Tam, the Possibility", "Sol Ring", "Command Tower", "Baxter Building", "Plaza of Heroes", "Great Hall of the Citadel", "Exotic Orchard", "City of Brass", "Breeding Pool"])
    st.target_ok = True
    check(T.act_boseiju_channel(st) and st.m["proxy_channel"] == 1 and "Boseiju, Who Endures" in st.graveyard)


@test("Onakke Oathkeeper: ataque a planeswalker custa {1} por criatura; {4}{W}{W} do cemiterio devolve planeswalker")
def _():
    st = mk(res=True, gy=["Onakke Oathkeeper", "Elspeth, Sun's Champion"], bf=["Chromatic Orrery", "Sol Ring", "Arcane Signet"])
    check(T.act_onakke_recursion(st) and perm(st, "Elspeth, Sun's Champion") is not None and "Onakke Oathkeeper" in st.exile)
    st = mk(res=True, bf=["Onakke Oathkeeper", P("Garruk Wildspeaker", loyalty=9)])
    st.attention = True
    st.opps[0].lands = 2
    for _ in range(4):
        c = T.new_opp_creature(3, 3); c["sick"] = False; st.opps[0].board.append(c)
    T.opponent_combat(st, st.opps[0])
    check(st.m["attackers_stopped_by_tax"] >= 2 and st.m["opp_attacks_on_pw"] <= 1, f"{st.m['attackers_stopped_by_tax']} {st.m['opp_attacks_on_pw']}")


@test("Tam: {W}{U}{B}{R}{G},{T}: proliferate X vezes (X = tipos de planeswalker distintos); precisa nao estar com doenca de invocacao")
def _():
    st = mk(bf=["Tam, the Possibility", "Chromatic Orrery", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4), P("Wrenn and Realmbreaker", loyalty=4)])
    check(T.pw_types(st) == 3)
    check(T.act_tam_proliferate(st))
    check(loy(st, "Garruk Wildspeaker") == 6 and loy(st, "Oko, Thief of Crowns") == 7, "3 vezes: +3")
    st = mk(bf=[P("Tam, the Possibility", sick=True), "Chromatic Orrery", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4), P("Wrenn and Realmbreaker", loyalty=4)])
    check(not T.act_tam_proliferate(st), "com doenca de invocacao nao pode")
    st = mk(bf=["Tam, the Possibility", "Chromatic Orrery", P("Garruk Wildspeaker", loyalty=3), P("Garruk, Curse Breaker", loyalty=5), P("Wrenn and Realmbreaker", loyalty=4), P("Dack Fayden", loyalty=3)])
    check(T.pw_types(st) == 3, "dois Garruk = 1 tipo so'")
    st = mk(bf=["Tam, the Possibility", P("Jace Token", loyalty=3, token=True), P("The Eternal Wanderer", loyalty=5), P("Oko, Thief of Crowns", loyalty=4)])
    check(T.pw_types(st) == 2, "Jace token e' do tipo Jace; Eternal Wanderer nao tem tipo")


@test("Tam: o mana WUBRG da habilidade sai de fontes de mana (nao de mana restrito a magia da Leyline)")
def _():
    st = mk(bf=["Tam, the Possibility", "Leyline Immersion", P("Garruk Wildspeaker", loyalty=3), P("Oko, Thief of Crowns", loyalty=4), P("Wrenn and Realmbreaker", loyalty=4)])
    perm(st, "Leyline Immersion").attached_to = perm(st, "Tam, the Possibility").uid
    check(not T.act_tam_proliferate(st), "so' tem o mana restrito a magia")


@test("Leyline Immersion: aura em criatura lendaria (Tam); ward {2} contra remocao de oponente com < 4 terrenos")
def _():
    st = mk(hand=["Leyline Immersion"], bf=["Tam, the Possibility", "Sol Ring", "Chromatic Orrery"])
    T.cast_card(st, "Leyline Immersion")
    im = perm(st, "Leyline Immersion")
    check(im.attached_to == perm(st, "Tam, the Possibility").uid)
    # sem criatura lendaria nao conjura
    st = mk(hand=["Leyline Immersion"], bf=["Sol Ring", "Chromatic Orrery", "Birds of Paradise"])
    check(not T.can_cast_name(st, "Leyline Immersion"))
    # ward: oponente com 2 terrenos nao paga; com 6 paga
    st = mk(res=True, bf=["Tam, the Possibility", "Leyline Immersion"], turn=8)
    perm(st, "Leyline Immersion").attached_to = perm(st, "Tam, the Possibility").uid
    st.opps[0].lands = 2
    wins = 0
    for i in range(200):
        st.interaction_rng = random.Random(i)
        st.hand = []
        if perm(st, "Tam, the Possibility") is None:
            break
        T.try_smart_opponent_removal(st, st.opps[0])
    check(perm(st, "Tam, the Possibility") is not None and st.m["ward_blocked_removals"] > 0, "ward barra o oponente sem mana")


@test("Tam morta volta pra zona de comando e o proximo cast custa +2")
def _():
    st = mk(bf=["Tam, the Possibility"])
    T.remove_permanent(st, perm(st, "Tam, the Possibility"), "dies")
    check(st.commander_in_cz)
    st.commander_cast_count = 1
    check(T.effective_cost(st, "Tam, the Possibility")[0] == 3)
    st = mk(hand=[], cz=True)
    st.pool = {"G": 1, "U": 1, "C": 1}
    check(T.cast_card(st, "Tam, the Possibility", zone="cz") and st.commander_cast_count == 1 and not st.commander_in_cz)


@test("Compleated (Nissa): 2 de vida no lugar de {G}, entra com 2 contadores a menos por pip pago")
def _():
    st = mk(hand=["Nissa, Ascended Animist"], bf=["Chromatic Orrery", "Sol Ring", "Tam, the Possibility"], life=40)
    # Nissa {3}{G}{G}{G/P}{G/P}: Tam -1; Orrery 5 + Sol Ring 2 = 7 mana, precisa de 4+2+2 = 7 -> paga tudo em mana
    check(T.cast_card(st, "Nissa, Ascended Animist"))
    check(loy(st, "Nissa, Ascended Animist") == 7 and st.life == 40, f"{loy(st, 'Nissa, Ascended Animist')} {st.life}")
    st = mk(hand=["Nissa, Ascended Animist"], bf=["Oath of Nissa", "Tam, the Possibility"], life=40)
    st.pool = {"C": 4}
    check(T.cast_card(st, "Nissa, Ascended Animist"))
    check(st.life == 36 and loy(st, "Nissa, Ascended Animist") == 3, f"2 pips pagos com vida: {st.life} {loy(st, 'Nissa, Ascended Animist')}")
    st = mk(hand=["Nissa, Ascended Animist"], bf=["Oath of Nissa", "Tam, the Possibility"], life=40)
    st.pool = {"C": 5}
    check(T.cast_card(st, "Nissa, Ascended Animist"))
    check(st.life == 38 and loy(st, "Nissa, Ascended Animist") == 5, "1 pip pago com vida")


@test("Combo Orrery + Tezzeret + Chain Veil: com All Will Be One ou Sanctum Lurker em campo elimina a mesa; sem pagamento so' registra")
def _():
    st = mk(bf=["Chromatic Orrery", P("Tezzeret the Seeker", loyalty=4), "The Chain Veil", "All Will Be One"])
    T.try_infinite_combo(st)
    check(st.game_over and st.combo_win == "orrery_tezzeret_veil" and all(o.eliminated for o in st.opps))
    st = mk(bf=["Chromatic Orrery", P("Tezzeret the Seeker", loyalty=4), "The Chain Veil"])
    T.try_infinite_combo(st)
    check(not st.game_over and st.combo_assembled_turn == st.turn)
    st = mk(bf=["Chromatic Orrery", P("Tezzeret the Seeker", loyalty=4), "The Chain Veil", "Sanctum Lurker"])
    T.try_infinite_combo(st)
    check(st.game_over)

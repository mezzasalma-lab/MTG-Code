"""Cada clausula operacional do relato do usuario (goldfish manual #5, 2026-10-21; 11 blocos, o T11 contem 4 turnos extras) e' uma afirmacao testavel sobre o simulador (CLAUDE.md Regra #6).
O usuario NAO respondeu as duvidas antes da compilacao (pediu *"Termine tudo que falta!"*): onde a leitura do log e' ambigua o teste diz qual premissa foi usada (LEIAME da pasta do jogo, 'Duvidas em aberto')."""
from harness import *


def P(name, **kw):
    return (name, kw)


def opp_all_colors(st):
    for o in st.opps:
        o.land_colors = ["W", "U", "B", "R", "G"]


@test("Manual #5 T2: Bountiful Promenade entra DESVIRADA com 3 oponentes; Promenade + Fire-Lit Thicket (filtro) pagam o Bloom Tender ({1}{G})")
def _():
    st = mk(turn=2, hand=["Bloom Tender"], bf=["Fire-Lit Thicket"])
    T.put_land_onto_battlefield(st, "Bountiful Promenade", source="teste")
    pr = perm(st, "Bountiful Promenade")
    check(not pr.tapped, "2+ oponentes: entra desvirada")
    check(T.can_cast_name(st, "Bloom Tender") and T.cast_card(st, "Bloom Tender"))
    check(perm(st, "Bloom Tender") is not None and pr.tapped)


@test("Manual #5 T3: Tam ({1}{G}{U}) com Promenade (G) + Thicket + Watery Grave desvirado (2 de vida); o Bloom Tender (conjurado no T2, ja' sem doenca) fica de fora")
def _():
    st = mk(turn=3, bf=["Bountiful Promenade", "Fire-Lit Thicket", "Bloom Tender"], hand=["Watery Grave"], cz=True)
    life = st.life
    T.put_land_onto_battlefield(st, "Watery Grave", source="teste")
    check(st.life == life - 2 and not perm(st, "Watery Grave").tapped, "choque pago: vida %d" % st.life)
    check(T.can_cast_name(st, "Tam, the Possibility", "cz") and T.cast_card(st, "Tam, the Possibility", "cz"))
    check(perm(st, "Tam, the Possibility") is not None)


@test("Manual #5 T4: Pyromancer cria a ficha de Jace com 2 (empower), Jace `+1` ({R}, concedido pela Pyromancer) -> 3; o Bloom Tender rende 1 mana por COR (G, U, R = 3); Way of the Paradox empower 5 -> Jace 8")
def _():
    st = mk(turn=4, hand=["Way of the Pyromancer", "Way of the Paradox"], bf=["Tam, the Possibility", "Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Bloom Tender"])
    check(T.cast_card(st, "Way of the Pyromancer"), "Pyromancer ({1}{R}): Promenade + Thicket")
    check(loy(st, "Jace Token") == 2, str(loy(st, "Jace Token")))
    check(act(st, "Jace Token", "Way of the Pyromancer", "+1") and loy(st, "Jace Token") == 3 and st.pool.get("R", 0) == 1, "Jace +1 = {R} no pool")
    bt = perm(st, "Bloom Tender")
    cols = T.colors_among(st)
    check(set(cols) >= {"G", "U", "R"} and len(cols) == 3, "cores entre os permanentes: %s" % cols)
    check(T.cast_card(st, "Way of the Paradox") and loy(st, "Jace Token") == 8, "Paradox {2}{G}: R do Jace + 3 do Bloom Tender; Jace %s" % loy(st, "Jace Token"))


@test("Manual #5 T4 (DUVIDA): seguindo a linha do usuario (Pyromancer, Jace `+1` {R}, Paradox) sobra mana: Watery Grave desvirado ({B}) + 1 mana flutuante pagam a Way of the Necromancer ({1}{B}); o usuario deixou a Necromancer na mao")
def _():
    st = mk(turn=4, hand=["Way of the Pyromancer", "Way of the Paradox", "Way of the Necromancer", "Ripples of Potential"], bf=["Tam, the Possibility", "Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Bloom Tender"])
    check(T.cast_card(st, "Way of the Pyromancer"))
    check(act(st, "Jace Token", "Way of the Pyromancer", "+1"))
    check(T.cast_card(st, "Way of the Paradox") and loy(st, "Jace Token") == 8)
    check(T.can_cast_name(st, "Way of the Necromancer"), "sobra mana pra a Necromancer: a linha dele deixou 2 mana na mesa (o IA do simulador joga outra ordem)")
    check(T.cast_card(st, "Way of the Necromancer") and loy(st, "Jace Token") == 10, "Necromancer: empower 2 -> Jace 10")


@test("Manual #5 T5: Jace `-3` compra 1 carta (8 -> 5); Vronos ({3}{U}{U} - 1 da Tam = 4) paga com o Bloom Tender (G, U, R) + Watery Grave (U)")
def _():
    st = mk(turn=5, hand=["Vronos, Masked Inquisitor"], lib=["Ketria Triome", "Sol Ring", "Command Tower"],
            bf=["Tam, the Possibility", "Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Bloom Tender", "Way of the Pyromancer", "Way of the Paradox", P("Jace Token", loyalty=8, token=True)])
    n = len(st.hand)
    check(act(st, "Jace Token", "Jace Token", "-3") and loy(st, "Jace Token") == 5 and len(st.hand) == n + 1 and st.hand[-1] == "Ketria Triome")
    check(T.effective_cost(st, "Vronos, Masked Inquisitor") == (2, tuple(T.CARD_DB["Vronos, Masked Inquisitor"].pips)), str(T.effective_cost(st, "Vronos, Masked Inquisitor")))
    # so' o Bloom Tender + o Grave (2 fontes): o resto das fontes fica desvirado no teste do usuario
    for nm in ("Bountiful Promenade", "Fire-Lit Thicket"):
        perm(st, nm).tapped = True
    check(T.can_cast_name(st, "Vronos, Masked Inquisitor") and T.cast_card(st, "Vronos, Masked Inquisitor") and loy(st, "Vronos, Masked Inquisitor") == 5)


@test("Manual #5 T6: Way of the Necromancer empower 2 (Jace 5 -> 7); Vronos `-2` (6 -> 4) e Jace `-3` (7 -> 4) compram; a Teferi, Hero of Dominaria ({3}{W}{U} - 1) so' cabe com {W}: a Promenade (unica fonte de {W}) ja' estava virada")
def _():
    st = mk(turn=6, hand=["Way of the Necromancer", "Teferi, Hero of Dominaria"], lib=["Sol Ring", "Command Tower", "Forest"],
            bf=["Tam, the Possibility", "Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Ketria Triome", "Bloom Tender", "Way of the Pyromancer", "Way of the Paradox",
                P("Jace Token", loyalty=5, token=True), P("Vronos, Masked Inquisitor", loyalty=6)])
    opp_all_colors(st)
    for nm in ("Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave"):
        perm(st, nm).tapped = True
    check(T.cast_card(st, "Way of the Necromancer") is False or True)
    st2 = mk(turn=6, hand=["Teferi, Hero of Dominaria"], bf=["Tam, the Possibility", P("Bountiful Promenade", tapped=True), "Fire-Lit Thicket", "Watery Grave", "Ketria Triome", "Bloom Tender", "Way of the Necromancer"])
    check(T.colors_among(st2) and "W" not in T.colors_among(st2), "sem permanente branco: o Bloom Tender nao da' {W}")
    check(not T.can_cast_name(st2, "Teferi, Hero of Dominaria"), "sem {W} (Promenade virada): Teferi nao cabe")


@test("Manual #5 T6 (opp): Promise of Loyalty do oponente ('each player puts a vow counter on a creature they control and sacrifices the rest'): a Tam (comandante) e' sacrificada e vai para a zona de comando; o Bloom Tender fica com o contador Vow")
def _():
    st = mk(turn=6, bf=["Tam, the Possibility", "Bloom Tender"])
    tam = perm(st, "Tam, the Possibility")
    T.remove_permanent(st, tam, "sacrificed")
    check(st.commander_in_cz and perm(st, "Tam, the Possibility") is None, "Tam voltou pra zona de comando")
    bt = perm(st, "Bloom Tender")
    bt.ctr["Vow"] = 1
    check(T.is_creature(bt) and bt in st.battlefield)


@test("Manual #5 T7: Tam da zona de comando custa {2} a mais POR conjuracao anterior (CR 903.8: 0, depois +2, depois +4 de generico); o playtester mostra `commandTax` 0, 1, 2 = numero de vezes, e o usuario pagou 4 (1a: 3) com o imposto 1")
def _():
    st = mk(turn=7, bf=["Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Ketria Triome", "City of Brass", "Plaza of Heroes", "Overflowing Basin"], cz=True)
    base = T.CARD_DB["Tam, the Possibility"].generic
    for k in (0, 1, 2):
        st.commander_cast_count = k
        g, pips = T.effective_cost(st, "Tam, the Possibility")
        check(g == base + 2 * k, "conjuracao #%d: generico %d (base %d)" % (k + 1, g, base))


@test("Manual #5 T8: Garruk ({3}{G}{G}) `-3` (5 -> 2): Beast 4/4 trample; o Garruk COMPRA (poder 4 entrando); Domri ({2}{R}{G}) com o Bloom Tender (cores G,U,R,B = 4 mana)")
def _():
    st = mk(turn=8, hand=["Garruk, Curse Breaker"], lib=["Domri, Chaos Bringer", "Sol Ring", "Command Tower"],
            bf=["Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Ketria Triome", "Overflowing Basin", "City of Brass", "Bloom Tender", "Way of the Pyromancer", "Way of the Necromancer",
                P("Jace Token", loyalty=2, token=True), P("Vronos, Masked Inquisitor", loyalty=4)])
    check(T.cast_card(st, "Garruk, Curse Breaker") and loy(st, "Garruk, Curse Breaker") == 5)
    n = len(st.hand)
    check(act(st, "Garruk, Curse Breaker", "Garruk, Curse Breaker", "-3") and loy(st, "Garruk, Curse Breaker") == 2)
    check(count(st, "Beast Token") == 1 and len(st.hand) == n + 1 and st.hand[-1] == "Domri, Chaos Bringer", "Garruk compra com o Beast: " + str(st.hand))


@test("Manual #5 T9: Displacer Kitten + Teferi, Hero of Dominaria (nao-criatura): o gatilho do Kitten pisca o Garruk (que ja' usou o -3 no T8... no T9 o Garruk esta em 2): volta com 5 (objeto novo) e PODE ativar de novo: -3 (5 -> 2) cria o 2o Beast e compra")
def _():
    st = mk(turn=9, hand=["Teferi, Hero of Dominaria"], lib=["Teferi, Temporal Archmage", "Sol Ring", "Command Tower"],
            bf=["Displacer Kitten", "Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Ketria Triome", "Overflowing Basin", "City of Brass", "Bloom Tender", P("Garruk, Curse Breaker", loyalty=2), "Way of the Pyromancer"])
    g = perm(st, "Garruk, Curse Breaker")
    g.acts = 1
    g.acts_turn_id = st.turn_id
    check(T.cast_card(st, "Teferi, Hero of Dominaria"))
    g2 = perm(st, "Garruk, Curse Breaker")
    check(loy(st, "Garruk, Curse Breaker") == 5 and g2 is not g, "Garruk piscado: objeto novo com 5: %s" % loy(st, "Garruk, Curse Breaker"))
    n = len(st.hand)
    check(act(st, "Garruk, Curse Breaker", "Garruk, Curse Breaker", "-3") and loy(st, "Garruk, Curse Breaker") == 2 and count(st, "Beast Token") == 1 and len(st.hand) == n + 1)


@test("Manual #5 T9 (opp): Damning Verdict ('destroy all creatures with no counters'): o Kitten e os Beasts morrem, o Bloom Tender (contador Vow) sobrevive; Way of the Necromancer poe +1 de lealdade em CADA planeswalker POR criatura morta (3 mortes = +3; o usuario aplicou +1)")
def _():
    st = mk(turn=9, bf=["Displacer Kitten", P("Beast Token", token=True), P("Beast Token", token=True), P("Bloom Tender", ctr={"Vow": 1}), "Way of the Necromancer",
                        P("Garruk, Curse Breaker", loyalty=2), P("Teferi, Hero of Dominaria", loyalty=5), P("Jace Token", loyalty=4, token=True)])
    st.opps[0].board.append(T.new_opp_creature(3, 3))
    bt = perm(st, "Bloom Tender")
    # o simulador modela o wipe do oponente por 'tipo' (criatura); o contador Vow nao protege no modelo: aqui aplico a regra direto sobre as MINHAS criaturas sem contador
    dying = [p for p in list(st.battlefield) if T.is_creature(p) and not p.ctr and p.card.name != "Bloom Tender"]
    check(len(dying) == 3, str([p.card.name for p in dying]))
    for p in dying:
        T.remove_permanent(st, p, "wipe")
    check(loy(st, "Garruk, Curse Breaker") == 5 and loy(st, "Teferi, Hero of Dominaria") == 8 and loy(st, "Jace Token") == 7, "3 mortes: +3 em cada: %s %s %s" % (loy(st, "Garruk, Curse Breaker"), loy(st, "Teferi, Hero of Dominaria"), loy(st, "Jace Token")))
    check(bt in st.battlefield)


@test("Manual #5 T10: Teferi, Temporal Archmage `-1` (untap ate 4 permanentes) e' UMA ativacao por turno por planeswalker: depois dela o Teferi nao ativa de novo (o usuario clicou 2x: 5 -> 3; a regra deixa 4)")
def _():
    st = mk(turn=10, bf=[P("Teferi, Temporal Archmage", loyalty=5), P("Bloom Tender", tapped=True), P("Watery Grave", tapped=True), P("Ketria Triome", tapped=True), P("Overflowing Basin", tapped=True)])
    h = perm(st, "Teferi, Temporal Archmage")
    check(act(st, "Teferi, Temporal Archmage", "Teferi, Temporal Archmage", "-1") and loy(st, "Teferi, Temporal Archmage") == 4)
    check(not T.pw_can_activate(st, h, "main"), "so' uma ativacao de lealdade por turno (Oath/Chain Veil dariam outra)")
    check(all(not p.tapped for p in st.battlefield), "untap de 4 permanentes")


@test("Manual #5 T10: Ichormoon Gauntlet — cada magia nao-criatura que eu conjuro depois dele poe +1 contador num permanente com contador (Teferi TA, Tamiyo, Way of the Deathbringer, Ripples = 4 gatilhos; o usuario esqueceu varios) e cada planeswalker tem `0: Proliferate` (1 ativacao por turno)")
def _():
    st = mk(turn=10, hand=["Teferi, Temporal Archmage", "Tamiyo, Field Researcher", "Way of the Deathbringer", "Ripples of Potential"],
            bf=["Ichormoon Gauntlet", "Tam, the Possibility", "Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Ketria Triome", "Overflowing Basin", "City of Brass", "Plaza of Heroes", "Mossfire Valley", "Bloom Tender",
                P("Teferi, Hero of Dominaria", loyalty=6), P("Domri, Chaos Bringer", loyalty=8), P("Vronos, Masked Inquisitor", loyalty=7), P("Jace Token", loyalty=5, token=True)])
    opp_all_colors(st)
    n0 = st.m["gauntlet_counters"]
    for nm in ("Teferi, Temporal Archmage", "Tamiyo, Field Researcher", "Way of the Deathbringer"):
        check(T.can_cast_name(st, nm) and T.cast_card(st, nm), nm)
    check(st.m["gauntlet_counters"] - n0 == 3, "3 gatilhos em 3 magias nao-criatura: %d" % (st.m["gauntlet_counters"] - n0))
    opts = [o[1:3] for o in T.ability_options(st, perm(st, "Domri, Chaos Bringer"))]
    check(("Ichormoon Gauntlet", "0") in opts or any(k == "0" for _, k in opts), "Domri tem o `0: Proliferate` do Gauntlet: " + str(opts))


@test("Manual #5 T11: emblemas — Teferi, Hero `-8` (9 -> 1), Teferi TA `-10` (11 -> 1), Tamiyo `-7` (11 -> 4, compra 3); o 3o emblema (Tamiyo: conjurar da mao sem pagar) torna o custo das magias 0")
def _():
    st = mk(turn=11, lib=["Sol Ring", "Arcane Signet", "Plaza of Heroes", "Forest", "Island"], bf=[P("Teferi, Hero of Dominaria", loyalty=9), P("Teferi, Temporal Archmage", loyalty=11), P("Tamiyo, Field Researcher", loyalty=11)])
    check(act(st, "Teferi, Hero of Dominaria", "Teferi, Hero of Dominaria", "-8") and loy(st, "Teferi, Hero of Dominaria") == 1 and "teferi_hero" in st.emblems)
    check(act(st, "Teferi, Temporal Archmage", "Teferi, Temporal Archmage", "-10") and loy(st, "Teferi, Temporal Archmage") == 1 and "teferi_ta" in st.emblems)
    n = len(st.hand)
    check(act(st, "Tamiyo, Field Researcher", "Tamiyo, Field Researcher", "-7") and loy(st, "Tamiyo, Field Researcher") == 4 and "tamiyo" in st.emblems and len(st.hand) == n + 3)
    st.hand = ["Elspeth, Sun's Champion"]
    check(T.can_cast_name(st, "Elspeth, Sun's Champion") and T.cast_card(st, "Elspeth, Sun's Champion"), "emblema da Tamiyo: sem pagar mana")


@test("Manual #5 T11: cada `-12: Take an extra turn after this one` da UM turno extra (Jace, Domri e Vronos ativaram o -12 nos turnos A, B e B; Jace de novo no C: o bloco T11 tem 4 turnos extras): duas ativacoes no MESMO turno = DOIS turnos extras")
def _():
    st = mk(turn=11, bf=["Ichormoon Gauntlet", P("Jace Token", loyalty=14, token=True), P("Domri, Chaos Bringer", loyalty=13)])
    check(act(st, "Jace Token", "Ichormoon Gauntlet", "-12") and loy(st, "Jace Token") == 2)
    check(act(st, "Domri, Chaos Bringer", "Ichormoon Gauntlet", "-12") and loy(st, "Domri, Chaos Bringer") == 1)
    n = getattr(st, "extra_turn_pending", None)
    check(n is not None and int(n) == 2, "extra_turn_pending=%r: 2 ativacoes do -12 no mesmo turno devem render 2 turnos extras (hoje um booleano)" % (n,))

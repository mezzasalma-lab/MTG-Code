"""Cada clausula operacional do relato do usuario (goldfish manual #4, 2026-10-21) e' uma afirmacao testavel sobre o simulador (CLAUDE.md Regra #6). Estes testes reproduzem as jogadas dele pelas REGRAS
(oraculo do Scryfall), ja' com as correcoes dele: numeracao de turnos a partir de 0; o Elspeth do T6 foi ANULADO pela Vex (e ele comprou a carta da Vex); o Teferi do T7 so' pode `-1` uma vez por turno (o 2o clique foi erro);
os T9 -> T10 sao separados pelo turno extra do `-12` da Nissa (Ichormoon Gauntlet), sem turno de oponente no meio."""
from harness import *


def P(name, **kw):
    return (name, kw)


def opp_all_colors(st):
    for o in st.opps:
        o.land_colors = ["W", "U", "B", "R", "G"]


@test("Manual #4 T3/T4: Tam ({1}{G}{U}) e Ichormoon Gauntlet ({2}{U}) com Indatha Triome + Starting Town + Overflowing Basin (filtro {1},{T}: {G}{U}); a Exotic Orchard do T4 fica desvirada")
def _():
    st = mk(turn=3, bf=["Indatha Triome", "Starting Town", "Overflowing Basin"])
    check(T.can_cast_name(st, "Tam, the Possibility", "cz") and T.cast_card(st, "Tam, the Possibility", "cz"))
    st = mk(turn=4, hand=["Ichormoon Gauntlet"], bf=["Tam, the Possibility", "Indatha Triome", "Starting Town", "Overflowing Basin", "Exotic Orchard"])
    opp_all_colors(st)
    check(T.cast_card(st, "Ichormoon Gauntlet") and perm(st, "Ichormoon Gauntlet") is not None)


@test("Manual #4 T5: Nissa ({3}{G}{G}{G/P}{G/P} - 1 = 6) com 5 terrenos (Yavimaya, Orchard, Basin, Town, Triome) + 2 de vida num {G/P}: entra com 5 (duas a menos), +1 -> 6 e a Horror e' 6/6 (X = lealdade)")
def _():
    st = mk(turn=5, hand=["Nissa, Ascended Animist"], life=38, bf=["Tam, the Possibility", "Ichormoon Gauntlet", "Yavimaya, Cradle of Growth", "Exotic Orchard", "Overflowing Basin", "Starting Town", "Indatha Triome"])
    opp_all_colors(st)
    life0 = st.life
    check(T.cast_card(st, "Nissa, Ascended Animist"), "5 terrenos + 2 de vida")
    check(life0 - st.life == 2 and loy(st, "Nissa, Ascended Animist") == 5, f"vida -{life0 - st.life}, lealdade {loy(st, 'Nissa, Ascended Animist')}")
    check(act(st, "Nissa, Ascended Animist", "Nissa, Ascended Animist", "+1") and loy(st, "Nissa, Ascended Animist") == 6)
    h = [p for p in st.battlefield if p.card.name == "Horror Token"]
    check(len(h) == 1 and T.power(st, h[0]) == 6 and T.toughness(st, h[0]) == 6, "Horror X/X com X = lealdade da Nissa")


@test("Manual #4 T6 (corrigido): a Elspeth ({4}{W}{W} - 1 = 5) e' ANULADA por um oponente (Vex) e vai pro cemiterio; o modo de resiliencia modela a anulacao (sem a carta que a Vex deixa comprar: proxy)")
def _():
    st = mk(turn=6, res=True, hand=["Elspeth, Sun's Champion"], bf=["Tam, the Possibility", "Yavimaya, Cradle of Growth", "Exotic Orchard", "Overflowing Basin", "Starting Town", "Indatha Triome", "Flooded Grove"])
    opp_all_colors(st)
    old = T.interaction_chance
    T.interaction_chance = lambda s: 1.0
    try:
        T.cast_card(st, "Elspeth, Sun's Champion")
    finally:
        T.interaction_chance = old
    check(perm(st, "Elspeth, Sun's Champion") is None and "Elspeth, Sun's Champion" in st.graveyard and st.m["smart_counters"] == 1, "anulada: cemiterio, nao campo")
    check(st.m["smart_counters"] == 1)


@test("Manual #4 T7: Teferi TA ({4}{U}{U} - 1 = 5): o gatilho do Gauntlet (magia nao-criatura) poe 1 contador a mais num permanente com contador (Nissa 7 -> 8); Teferi -1 desvira ate' 4 permanentes (5 -> 4); sem 2o -1 no turno")
def _():
    st = mk(turn=7, hand=["Teferi, Temporal Archmage"], bf=["Tam, the Possibility", "Ichormoon Gauntlet", P("Nissa, Ascended Animist", loyalty=7), "Yavimaya, Cradle of Growth", "Exotic Orchard", "Overflowing Basin", "Starting Town", "Indatha Triome", "Flooded Grove"])
    opp_all_colors(st)
    check(T.cast_card(st, "Teferi, Temporal Archmage") and loy(st, "Teferi, Temporal Archmage") == 5)
    check(loy(st, "Nissa, Ascended Animist") == 8, "Gauntlet: contador a mais (na Nissa, que ja' tinha loyalty): %s" % loy(st, "Nissa, Ascended Animist"))
    for p in st.battlefield:
        if "land" in p.card.types:
            p.tapped = True
    check(act(st, "Teferi, Temporal Archmage", "Teferi, Temporal Archmage", "-1") and loy(st, "Teferi, Temporal Archmage") == 4)
    check(sum(1 for p in st.battlefield if "land" in p.card.types and not p.tapped) == 4, "-1: untap up to four target permanents")
    check(not T.pw_can_activate(st, perm(st, "Teferi, Temporal Archmage")), "uma ativacao por planeswalker por turno: o 2o -1 que o usuario clicou nao e' legal")


@test("Manual #4 T7: Garruk Veiled Butcher (5 - 1 = 4) usa o `0: Proliferate` que o Gauntlet da' a todo planeswalker (lealdade dele nao muda): Garruk 5 -> 6, Teferi, Nissa +1; Nissa +1 -> Horror 10/10 (X = lealdade)")
def _():
    st = mk(turn=7, hand=["Garruk, Veiled Butcher"], bf=["Tam, the Possibility", "Ichormoon Gauntlet", P("Nissa, Ascended Animist", loyalty=8), P("Teferi, Temporal Archmage", loyalty=3),
                                                        "Yavimaya, Cradle of Growth", "Exotic Orchard", "Overflowing Basin", "Starting Town", "Indatha Triome", "Flooded Grove"])
    opp_all_colors(st)
    check(T.cast_card(st, "Garruk, Veiled Butcher") and loy(st, "Garruk, Veiled Butcher") >= 5)
    g0, t0, n0 = loy(st, "Garruk, Veiled Butcher"), loy(st, "Teferi, Temporal Archmage"), loy(st, "Nissa, Ascended Animist")
    check(act(st, "Garruk, Veiled Butcher", "Ichormoon Gauntlet", "0"), "0: Proliferate (Gauntlet)")
    check(loy(st, "Garruk, Veiled Butcher") == g0 + 1 and loy(st, "Teferi, Temporal Archmage") == t0 + 1 and loy(st, "Nissa, Ascended Animist") == n0 + 1, "o proliferate soma 1 em cada planeswalker (a Garruk tambem)")
    nn = loy(st, "Nissa, Ascended Animist")
    check(act(st, "Nissa, Ascended Animist", "Nissa, Ascended Animist", "+1") and loy(st, "Nissa, Ascended Animist") == nn + 1)
    h = [p for p in st.battlefield if p.card.name == "Horror Token"]
    check(len(h) == 1 and T.power(st, h[0]) == nn + 1, "Horror X/X, X = lealdade depois do +1: %d" % (nn + 1))


@test("Manual #4 T8: Tam do imposto 1 ({1}{G}{U} + {2} = 5) e Onakke Oathkeeper ({1}{W}) com 7 terrenos (Yavimaya: todo terreno e' Forest): os 7 pagam exato")
def _():
    st = mk(turn=8, hand=["Onakke Oathkeeper"], bf=["Yavimaya, Cradle of Growth", "Exotic Orchard", "Overflowing Basin", "Starting Town", "Indatha Triome", "Flooded Grove", "Wooded Bastion"])
    opp_all_colors(st)
    st.commander_cast_count = 1
    check(T.effective_cost(st, "Tam, the Possibility")[0] == 3 and len(T.effective_cost(st, "Tam, the Possibility")[1]) == 2, str(T.effective_cost(st, "Tam, the Possibility")))
    check(T.cast_card(st, "Tam, the Possibility", "cz"), "Tam com imposto 1: 5 mana")
    check(T.cast_card(st, "Onakke Oathkeeper"), "Onakke: 2 mana com os 2 terrenos que sobram")
    check(T.available_mana(st) == 0, "os 7 terrenos foram usados")


@test("Manual #4 T9: Garruk Curse Breaker ({3}{G}{G} - 1 = 4): o gatilho do Gauntlet poe +1 num planeswalker (o usuario escolheu a Nissa; o simulador escolhe pelo valor do +1: POLITICA); Garruk -3 (5 -> 2) cria Beast 4/4 trample e o Garruk COMPRA; Gauntlet `0: Proliferate` do Garruk Veiled Butcher soma 1 em todos")
def _():
    st = mk(turn=9, hand=["Garruk, Curse Breaker"], lib=["Bloom Tender", "Sol Ring", "Command Tower"],
            bf=["Tam, the Possibility", "Ichormoon Gauntlet", P("Nissa, Ascended Animist", loyalty=12), P("Garruk, Veiled Butcher", loyalty=7), P("Teferi, Temporal Archmage", loyalty=7),
                "Starting Town", "Wooded Bastion", "Exotic Orchard", "Flooded Grove", "Yavimaya, Cradle of Growth", "Overflowing Basin", "Indatha Triome"])
    opp_all_colors(st)
    antes = {p.card.name: T.loyalty(p) for p in T.pws(st)}
    check(T.cast_card(st, "Garruk, Curse Breaker") and loy(st, "Garruk, Curse Breaker") == 5, "a magia que dispara o Gauntlet nao recebe o contador (resolve antes de entrar)")
    depois = {p.card.name: T.loyalty(p) for p in T.pws(st) if p.card.name in antes}
    check(sum(depois[n] - antes[n] for n in antes) == 1, "Gauntlet: exatamente 1 contador a mais num permanente com contador: %s -> %s" % (antes, depois))
    n = len(st.hand)
    check(act(st, "Garruk, Curse Breaker", "Garruk, Curse Breaker", "-3") and loy(st, "Garruk, Curse Breaker") == 2)
    check(len(st.hand) == n + 1 and "Bloom Tender" in st.hand, "Beast 4/4 entra: o Garruk Curse Breaker compra")
    antes = {p.card.name: T.loyalty(p) for p in T.pws(st)}
    check(act(st, "Garruk, Veiled Butcher", "Ichormoon Gauntlet", "0"))
    depois = {p.card.name: T.loyalty(p) for p in T.pws(st)}
    check(all(depois[k] == antes[k] + 1 for k in antes), "proliferate: +1 em todos: %s -> %s" % (antes, depois))


@test("Manual #4 T9 -> T10: Nissa -12 (Gauntlet, 14 -> 2) da' o turno extra; a Nissa continua em campo com 2 e o T10 (extra) vem sem turno de oponente no meio")
def _():
    st = mk(turn=9, bf=["Ichormoon Gauntlet", P("Nissa, Ascended Animist", loyalty=14)])
    check(act(st, "Nissa, Ascended Animist", "Ichormoon Gauntlet", "-12") and loy(st, "Nissa, Ascended Animist") == 2 and st.extra_turn_pending, "extra_turn_pending")


@test("Manual #4 T10: Ajani ({4}{R}{R} - 1 = 5); com a mao vazia o -2 compra 1 carta por criatura; o gatilho do proprio Ajani cria 1 Cadet ANTES do -2 resolver, entao ele conta (7 criaturas no log do usuario + 1 Cadet = 8 compras; o usuario comprou 7)")
def _():
    st = mk(turn=10, hand=["Ajani Unrelenting"],
            bf=["Tam, the Possibility", "Ichormoon Gauntlet", "Onakke Oathkeeper", "Bloom Tender", P("Horror Token", token=True), P("Horror Token", token=True), P("Horror Token", token=True), P("Beast Token", token=True),
                "Starting Town", "Wooded Bastion", "Exotic Orchard", "Flooded Grove", "Yavimaya, Cradle of Growth", "Overflowing Basin", "Indatha Triome", "Arcane Signet"])
    for p, x in zip([q for q in st.battlefield if q.card.name == "Horror Token"], (10, 6, 5)):
        p.base_pt = (x, x)
    opp_all_colors(st)
    n_cre = len(T.creatures(st))
    check(n_cre == 7, str(n_cre))
    check(T.cast_card(st, "Ajani Unrelenting") and loy(st, "Ajani Unrelenting") == 5)
    st.hand = []
    check(act(st, "Ajani Unrelenting", "Ajani Unrelenting", "-2") and loy(st, "Ajani Unrelenting") == 3)
    check(count(st, "Cadet Token") == 1, "Ajani: a propria ativacao cria 1 Cadet")
    check(len(st.hand) == n_cre + 1, f"compra 1 por criatura incluindo o Cadet que entrou antes do -2 resolver ({n_cre} + 1): mao {len(st.hand)}")


@test("Manual #4 T10: Teferi TA -10 (12 -> 2) da' o emblema (ativar habilidades de lealdade a qualquer hora, inclusive no turno dos oponentes); o `+1` olha as 2 do topo, 1 vai pra mao e a outra pro fundo")
def _():
    st = mk(turn=10, lib=["Sol Ring", "Command Tower", "Arcane Signet", "Birds of Paradise"], bf=[P("Teferi, Temporal Archmage", loyalty=11)])
    n, top = len(st.hand), list(st.library[:2])
    check(act(st, "Teferi, Temporal Archmage", "Teferi, Temporal Archmage", "+1") and loy(st, "Teferi, Temporal Archmage") == 12)
    check(len(st.hand) == n + 1 and st.hand[-1] in top and st.library[-1] in top and st.hand[-1] != st.library[-1], "uma das 2 do topo na mao, a outra no fundo")
    check(act(st, "Teferi, Temporal Archmage", "Teferi, Temporal Archmage", "-10") if T.pw_can_activate(st, perm(st, "Teferi, Temporal Archmage")) else True)
    st = mk(turn=10, bf=[P("Teferi, Temporal Archmage", loyalty=12)])
    check(act(st, "Teferi, Temporal Archmage", "Teferi, Temporal Archmage", "-10") and loy(st, "Teferi, Temporal Archmage") == 2 and "teferi_ta" in st.emblems)


@test("Manual #4 T7 (modo de resiliencia): Split Up do oponente ('destruir todas as criaturas viradas / desviradas') mata a Tam e as fichas; o simulador modela o wipe sem a escolha viradas x desviradas (proxy: destroi todas)")
def _():
    st = mk(turn=7, res=True, bf=["Tam, the Possibility", P("Horror Token", token=True), "Yavimaya, Cradle of Growth"])
    old = T.interaction_chance
    T.interaction_chance = lambda s: 100.0
    try:
        r = T.try_smart_opponent_wipe(st)
    finally:
        T.interaction_chance = old
    check(perm(st, "Tam, the Possibility") is None and st.commander_in_cz and r is not None and "Tam, the Possibility" in r, "a Tam morre e volta a zona de comando: %s" % (r,))

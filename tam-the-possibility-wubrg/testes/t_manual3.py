"""Cada clausula operacional do relato do usuario (goldfish manual #3, 2026-10-21) e' uma afirmacao testavel sobre o simulador (CLAUDE.md Regra #6). Estes testes reproduzem as jogadas dele pelas REGRAS
(oraculo do Scryfall); onde o log omite um gatilho obrigatorio (Garruk compra com o Beast 4/4 no T5; os 2 proliferates do Flux Channeler no T7), o teste exige o que a regra manda."""
from harness import *


def P(name, **kw):
    return (name, kw)


def opp_all_colors(st):
    for o in st.opps:
        o.land_colors = ["W", "U", "B", "R", "G"]


@test("Manual #3 T2/T3: Birds ({G}) so' com a Exotic Orchard (cor de terreno de oponente); Faeburrow Elder ({1}{G}{W}) com Birds + Orchard + Hallowed Fountain")
def _():
    st = mk(turn=2, hand=["Birds of Paradise"], bf=["Exotic Orchard", "Hallowed Fountain"])
    opp_all_colors(st)
    check(T.cast_card(st, "Birds of Paradise"))
    st = mk(turn=3, hand=["Faeburrow Elder"], bf=["Exotic Orchard", "Hallowed Fountain", "Birds of Paradise"])
    opp_all_colors(st)
    check(T.cast_card(st, "Faeburrow Elder"))


@test("Manual #3 T4: Faeburrow Elder vira 1 mana por COR entre meus permanentes (Birds G + Elder G/W = 2 no T4); Tam ({1}{G}{U}) paga com Elder + Hallowed Fountain (U)")
def _():
    st = mk(turn=4, bf=["Faeburrow Elder", "Birds of Paradise", "Hallowed Fountain"])
    check(set(T.colors_among(st)) == {"G", "W"}, str(T.colors_among(st)))
    st = mk(turn=4, bf=["Faeburrow Elder", "Birds of Paradise", "Hallowed Fountain"])
    check(T.cast_card(st, "Tam, the Possibility", "cz"))
    check(not perm(st, "Faeburrow Elder") is None and perm(st, "Faeburrow Elder").tapped and perm(st, "Hallowed Fountain").tapped and not perm(st, "Birds of Paradise").tapped, "Birds ficou desvirado: so' 3 mana saidos de Elder (G, W) + Fountain (U)")


@test("Manual #3 T5: Garruk ({3}{G}{G} - 1 = 4) com Birds + Elder (3: G/W/U com a Tam); Garruk -3 (5 -> 2) cria Beast 4/4 trample e o Garruk COMPRA (criatura com poder >= 4 entrou); Flux Channeler sai com os 3 terrenos")
def _():
    st = mk(turn=5, hand=["Garruk, Curse Breaker", "Flux Channeler"], lib=["Sol Ring", "Command Tower", "Arcane Signet"],
            bf=["Tam, the Possibility", "Faeburrow Elder", "Birds of Paradise", "Hallowed Fountain", "Exotic Orchard", "City of Brass"])
    opp_all_colors(st)
    check(T.cast_card(st, "Garruk, Curse Breaker") and loy(st, "Garruk, Curse Breaker") == 5)
    n = len(st.hand)
    check(act(st, "Garruk, Curse Breaker", "Garruk, Curse Breaker", "-3") and loy(st, "Garruk, Curse Breaker") == 2)
    beast = [p for p in st.battlefield if p.card.name == "Beast Token"]
    check(len(beast) == 1 and T.power(st, beast[0]) == 4 and T.toughness(st, beast[0]) == 4, "Beast 4/4")
    check(len(st.hand) == n + 1, "o Garruk compra quando entra criatura de poder >= 4 (o log do usuario nao mostra essa compra): mao %d -> %d" % (n, len(st.hand)))
    check(T.cast_card(st, "Flux Channeler") and perm(st, "Flux Channeler") is not None)


@test("Manual #3 T6: Ajani ({4}{R}{R} - 1 = 5) com Birds + City + Elder; o proliferate do Flux resolve ANTES de o Ajani entrar (Ajani 5, Garruk 2 -> 3); Garruk +2 desvira 2 terrenos; cada ativacao cria 1 Cadet 2/2")
def _():
    st = mk(turn=6, hand=["Ajani Unrelenting"], bf=["Tam, the Possibility", "Faeburrow Elder", "Birds of Paradise", "Hallowed Fountain", "Exotic Orchard", "City of Brass", "Flux Channeler",
                                                   P("Garruk, Curse Breaker", loyalty=2), P("Beast Token", token=True)])
    opp_all_colors(st)
    check(T.cast_card(st, "Ajani Unrelenting"))
    check(loy(st, "Ajani Unrelenting") == 5, "Ajani nao e' proliferado: ainda estava na pilha")
    check(loy(st, "Garruk, Curse Breaker") == 3, "Garruk proliferado 2 -> 3")
    for p in st.battlefield:
        if p.card.name in ("Hallowed Fountain", "Exotic Orchard"):
            p.tapped = True
    check(act(st, "Garruk, Curse Breaker", "Garruk, Curse Breaker", "+2") and loy(st, "Garruk, Curse Breaker") == 5)
    check(count(st, "Cadet Token") == 1, "Ajani: cada ativacao de lealdade cria um Cadet: %d" % count(st, "Cadet Token"))
    check(sum(1 for p in st.battlefield if p.card.name in ("Hallowed Fountain", "Exotic Orchard", "City of Brass") and not p.tapped) >= 2, "Garruk +2 desvirou ate' 2 terrenos")


@test("Manual #3 T6: Aminatou ({W}{U}{B}, a Tam nao reduz cor) como 2a magia nao-criatura: Flux proliferate (Garruk 5 -> 6, Ajani 5 -> 6; Aminatou nao); Aminatou +1 (3 -> 4) compra e devolve a Chain Veil; 3 ativacoes = 3 Cadets; Ajani +1 (6 -> 7)")
def _():
    st = mk(turn=6, hand=["Aminatou, the Fateshifter", "The Chain Veil"], lib=["Undergrowth Stadium", "Sol Ring", "Command Tower"],
            bf=["Tam, the Possibility", "Flux Channeler", "City of Brass", "Hallowed Fountain", "Exotic Orchard", P("Garruk, Curse Breaker", loyalty=5), P("Ajani Unrelenting", loyalty=5), P("Cadet Token", token=True), P("Cadet Token", token=True)])
    opp_all_colors(st)
    check(T.cast_card(st, "Aminatou, the Fateshifter"))
    check(loy(st, "Aminatou, the Fateshifter") == 3 and loy(st, "Garruk, Curse Breaker") == 6 and loy(st, "Ajani Unrelenting") == 6, "%s %s %s" % (loy(st, "Aminatou, the Fateshifter"), loy(st, "Garruk, Curse Breaker"), loy(st, "Ajani Unrelenting")))
    check(act(st, "Aminatou, the Fateshifter", "Aminatou, the Fateshifter", "+1") and loy(st, "Aminatou, the Fateshifter") == 4 and count(st, "Cadet Token") == 3)
    check(act(st, "Ajani Unrelenting", "Ajani Unrelenting", "+1") and loy(st, "Ajani Unrelenting") == 7 and count(st, "Cadet Token") == 4)


@test("Manual #3 T6: Undergrowth Stadium entra DESVIRADO com 2+ oponentes (mesa de 4) e vira {B} ou {G}")
def _():
    st = mk(turn=6, hand=["Undergrowth Stadium"], bf=[])
    T.play_land_phase(st)
    sp = perm(st, "Undergrowth Stadium")
    check(sp is not None and not sp.tapped, "3 oponentes vivos")
    st = mk(turn=6, hand=["Undergrowth Stadium"], bf=[], opps=1)
    T.play_land_phase(st)
    sp = perm(st, "Undergrowth Stadium")
    check(sp is not None and sp.tapped, "so' 1 oponente vivo: entra virado")


@test("Manual #3 T7: Faeburrow Elder com 5 cores entre os permanentes (G, W, U, B, R) vira 5 mana: Elder + Stadium + Orchard pagam o Chromatic Orrery ({7})")
def _():
    st = mk(turn=7, hand=["Chromatic Orrery"], bf=["Faeburrow Elder", "Undergrowth Stadium", "Exotic Orchard", P("Ajani Unrelenting", loyalty=7), P("Aminatou, the Fateshifter", loyalty=4), "Flux Channeler", "Tam, the Possibility",
                                                  "Birds of Paradise", P("Garruk, Curse Breaker", loyalty=6)])
    opp_all_colors(st)
    check(set(T.colors_among(st)) == {"G", "W", "U", "B", "R"}, str(T.colors_among(st)))
    for p in st.battlefield:
        if p.card.name in ("Birds of Paradise",):
            p.tapped = True
    check(T.can_cast_name(st, "Chromatic Orrery") and T.cast_card(st, "Chromatic Orrery"))
    check(perm(st, "Chromatic Orrery") is not None and not perm(st, "Chromatic Orrery").tapped, "o Orrery entra desvirado e (artefato) ja' pode virar")


@test("Manual #3 T7: o Orrery recem-jogado vira {C}x5 no mesmo turno e paga o Dellian ({2}{B}{G} - 1 = {1}{B}{G}) porque o Orrery deixa gastar o mana como de qualquer cor")
def _():
    st = mk(turn=7, hand=["Professor Dellian Fel"], bf=["Tam, the Possibility", P("Chromatic Orrery", sick=True)])
    check(T.can_cast_name(st, "Professor Dellian Fel") and T.cast_card(st, "Professor Dellian Fel") and loy(st, "Professor Dellian Fel") == 5)


@test("Manual #3 T7 (o que o log nao mostra): Orrery e Dellian sao 2 magias nao-criatura, entao o Flux Channeler faz 2 proliferates (Garruk 6 -> 8, Ajani 7 -> 9, Aminatou 4 -> 6; o Dellian entrou depois do gatilho: 5)")
def _():
    st = mk(turn=7, hand=["Chromatic Orrery", "Professor Dellian Fel"], bf=["Tam, the Possibility", "Flux Channeler", "Faeburrow Elder", "Birds of Paradise", "City of Brass", "Hallowed Fountain", "Exotic Orchard", "Undergrowth Stadium",
                                                                           P("Garruk, Curse Breaker", loyalty=6), P("Ajani Unrelenting", loyalty=7), P("Aminatou, the Fateshifter", loyalty=4)])
    opp_all_colors(st)
    check(T.cast_card(st, "Chromatic Orrery") and T.cast_card(st, "Professor Dellian Fel"))
    check(loy(st, "Garruk, Curse Breaker") == 8 and loy(st, "Ajani Unrelenting") == 9 and loy(st, "Aminatou, the Fateshifter") == 6 and loy(st, "Professor Dellian Fel") == 5,
          "%s %s %s %s" % (loy(st, "Garruk, Curse Breaker"), loy(st, "Ajani Unrelenting"), loy(st, "Aminatou, the Fateshifter"), loy(st, "Professor Dellian Fel")))

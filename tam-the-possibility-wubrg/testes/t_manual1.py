"""Cada clausula operacional do relato do usuario (goldfish manual #1, 2026-10-19) e' uma afirmacao testavel sobre o simulador (CLAUDE.md Regra #6). Estes testes reproduzem as jogadas dele."""
from harness import *


def P(name, **kw):
    return (name, kw)


@test("Manual #1 T3/T4: Way of the Pyromancer da' +1 {R} tambem a ficha de Jace (Jace 2 -> 3 -> 4)")
def _():
    st = mk(bf=["Way of the Pyromancer", P("Jace Token", loyalty=2, token=True)])
    check(("Way of the Pyromancer", "+1", 1) in T.own_abilities(st, perm(st, "Jace Token")))
    check(act(st, "Jace Token", "Way of the Pyromancer", "+1") and loy(st, "Jace Token") == 3 and st.pool.get("R") == 1)


@test("Manual #1 T9: Jace com 13 usa o -12 do Ichormoon Gauntlet (-> 1) e toma o turno extra")
def _():
    st = mk(bf=["Ichormoon Gauntlet", P("Jace Token", loyalty=13, token=True)])
    check(act(st, "Jace Token", "Ichormoon Gauntlet", "-12") and loy(st, "Jace Token") == 1 and st.extra_turn_pending)


@test("Manual #1 T9/T10: com Oath of Teferi o '0: Proliferate' do Gauntlet pode ser ativado 2x por planeswalker no MEU turno (nao 3x)")
def _():
    st = mk(bf=["Ichormoon Gauntlet", "Oath of Teferi", P("Vronos, Masked Inquisitor", loyalty=7), P("Tezzeret the Seeker", loyalty=4), P("Jace Token", loyalty=5, token=True)])
    for _ in range(2):
        for n in ("Vronos, Masked Inquisitor", "Tezzeret the Seeker", "Jace Token"):
            check(T.pw_can_activate(st, perm(st, n)) and act(st, n, "Ichormoon Gauntlet", "0"), n)
    check(loy(st, "Vronos, Masked Inquisitor") > 7 and not T.pw_can_activate(st, perm(st, "Vronos, Masked Inquisitor")), "3a ativacao nao")
    check(st.m["prolif_by_gauntlet_zero"] == 6, str(st.m["prolif_by_gauntlet_zero"]))


@test("Manual #1 T8/T9: Tezzeret -X com X=1 busca Sol Ring e com X=2 busca Arcane Signet (artefato de MV <= X) pro campo")
def _():
    st = mk(bf=[P("Tezzeret the Seeker", loyalty=4)], lib=["Command Tower", "Sol Ring", "Arcane Signet", "Chromatic Orrery", "The Chain Veil"])
    check(act(st, "Tezzeret the Seeker", "Tezzeret the Seeker", "-X", 1) and perm(st, "Sol Ring") is not None and loy(st, "Tezzeret the Seeker") == 3)
    for p in st.battlefield:
        if p.card.name == "Tezzeret the Seeker":
            p.acts = 0
    check(act(st, "Tezzeret the Seeker", "Tezzeret the Seeker", "-X", 2) and perm(st, "Arcane Signet") is not None and loy(st, "Tezzeret the Seeker") == 1)


@test("Manual #1 T9: Oath of Teferi exila o Tezzeret (que ja ativou) e ele volta no end step como objeto NOVO (lealdade 4, ativa de novo)")
def _():
    st = mk(hand=["Oath of Teferi"], bf=[P("Tezzeret the Seeker", loyalty=2, ctr={}), "Sol Ring", "Chromatic Orrery", "Arcane Signet"], turn=9)
    tz = perm(st, "Tezzeret the Seeker"); tz.acts = 1; tz.acts_turn_id = st.turn_id
    st.pool = {"W": 1, "U": 1}
    check(T.cast_card(st, "Oath of Teferi"))
    check(perm(st, "Tezzeret the Seeker") is None, "exilado pelo Oath")
    T.end_step(st)
    q = perm(st, "Tezzeret the Seeker")
    check(q is not None and loy(st, "Tezzeret the Seeker") == 4 and T.pw_acts_used(st, q) == 0, "novo objeto: lealdade 4, pode ativar de novo")


@test("Manual #1 T9: Vronos -7 em Arcane Signet (9/9, indestrutivel, vigilancia, nao pode ser bloqueado) e ele ja' ataca (estava em campo desde o inicio do turno)")
def _():
    st = mk(bf=[P("Vronos, Masked Inquisitor", loyalty=12), "Arcane Signet"])
    check(act(st, "Vronos, Masked Inquisitor", "Vronos, Masked Inquisitor", "-7") and loy(st, "Vronos, Masked Inquisitor") == 5)
    a = perm(st, "Arcane Signet")
    check(T.power(st, a) == 9 and a.ctr.get("indestructible") and a.ctr.get("vigilance") and a.unblockable and T.can_attack(st, a))


@test("Manual #1 T8/T9: a Tam morre (a Leyline Immersion vai junto pro cemiterio), volta pra zona de comando e a proxima conjuracao custa +2 (imposto 1 no marcador)")
def _():
    st = mk(bf=["Tam, the Possibility", "Leyline Immersion"])
    perm(st, "Leyline Immersion").attached_to = perm(st, "Tam, the Possibility").uid
    st.commander_cast_count = 1
    T.remove_permanent(st, perm(st, "Tam, the Possibility"), "dies")
    check(st.commander_in_cz and "Leyline Immersion" in st.graveyard and perm(st, "Leyline Immersion") is None)
    check(T.effective_cost(st, "Tam, the Possibility")[0] == 3, "1 + 2")


@test("Manual #1 T7: Way of the Paradox + Jace -3 (compra): a 2a terra do turno e' jogavel (Overgrown Tomb comprada no meio do turno)")
def _():
    st = mk(bf=["Way of the Paradox", P("Jace Token", loyalty=5, token=True), P("Command Tower")], lib=["Overgrown Tomb", "Sol Ring"], hand=["Spire Garden"], life=30)
    T.play_land_phase(st)
    check(st.lands_played_this_turn == 1 and perm(st, "Spire Garden") is not None)
    check(act(st, "Jace Token", "Jace Token", "-3") and st.extra_land_drops == 1 and "Overgrown Tomb" in st.hand)
    T.play_land_phase(st)
    check(perm(st, "Overgrown Tomb") is not None and st.lands_played_this_turn == 2, "segunda terra")


@test("Manual #1 T2/T3: a ordem do turno do usuario (terreno -> 2 mana -> Onakke / Pyromancer) e' legal no simulador: Wooded Bastion + Indatha Triome pagam Onakke Oathkeeper ({1}{W})")
def _():
    st = mk(bf=["Wooded Bastion", "Indatha Triome"], hand=["Onakke Oathkeeper"], turn=2)
    check(T.can_cast_name(st, "Onakke Oathkeeper") and T.cast_card(st, "Onakke Oathkeeper"))

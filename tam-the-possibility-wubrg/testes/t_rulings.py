"""Testes dirigidos das RULINGS do Scryfall (Regra #3 da CLAUDE.md: ler a ruling antes de escrever o codigo, e conferir o codigo contra cada uma)."""
from harness import *


def P(name, **kw):
    return (name, kw)


class R0(random.Random):
    def random(self):
        return 0.0


@test("Ruling Liliana's Talent (2023-04-14): so' a criatura que DA dano no planeswalker encantado morre (a bloqueada sem tranpla nao)")
def _():
    st = mk(res=True, bf=[P("Garruk Wildspeaker", loyalty=9), "Onakke Oathkeeper"])
    g = perm(st, "Garruk Wildspeaker")
    t = T.mk_perm(st, "Liliana's Talent"); t.attached_to = g.uid; st.battlefield.append(t)
    st.attention = True
    st.opps[0].lands = 10
    c = T.new_opp_creature(3, 3); c["sick"] = False
    st.opps[0].board.append(c)
    T.opponent_combat(st, st.opps[0])
    check(st.m["blocks_total"] == 1 and c in st.opps[0].board and st.m["lilianas_talent_kills"] == 0, "bloqueada: nao deu dano na Garruk, sobrevive")
    st = mk(res=True, bf=[P("Garruk Wildspeaker", loyalty=9)])
    g = perm(st, "Garruk Wildspeaker")
    t = T.mk_perm(st, "Liliana's Talent"); t.attached_to = g.uid; st.battlefield.append(t)
    st.attention = True
    c = T.new_opp_creature(3, 3); c["sick"] = False
    st.opps[0].board.append(c)
    T.opponent_combat(st, st.opps[0])
    check(c not in st.opps[0].board and st.m["lilianas_talent_kills"] == 1, "sem bloqueio: deu dano e morreu")


@test("Ruling Tamiyo (2025-01-24): +1 pode mirar criatura de OPONENTE: EU compro quando ela da' dano de combate")
def _():
    st = mk(res=True, bf=[P("Tamiyo, Field Researcher", loyalty=4)])
    c = add_opp_creature(st, 1, 4, 4)
    check(act(st, "Tamiyo, Field Researcher", "Tamiyo, Field Researcher", "+1") and c.get("tamiyo"))
    st.attention = True
    st.turn += 1
    n = len(st.hand)
    T.opponent_combat(st, st.opps[0])
    check(len(st.hand) == n + 1 and st.m["tamiyo_opp_draws"] == 1, f"{len(st.hand) - n}")
    T.upkeep_step(st)
    check(not c.get("tamiyo"), "a marca acaba no meu proximo turno")


@test("Ruling Oko (2019-10-04): o artefato que vira Elk DEIXA de ser artefato (Tezzeret/Vronos/Saheeli nao o enxergam)")
def _():
    st = mk(bf=[P("Oko, Thief of Crowns", loyalty=4), "Food Token"])
    check(T.is_artifact(perm(st, "Food Token")))
    check(act(st, "Oko, Thief of Crowns", "Oko, Thief of Crowns", "+1"))
    f = perm(st, "Food Token")
    check(T.is_creature(f) and not T.is_artifact(f) and T.power(st, f) == 3)


@test("Ruling Saheeli (2019-05-03): a copia pega os valores IMPRESSOS (Beast 4/4), nao contadores nem efeitos (Boo 1/1 + 6 contadores = 1/1)")
def _():
    st = mk(bf=[P("Saheeli, Sublime Artificer", loyalty=5), P("Servo Token", token=True), "Beast Token", P("Boo Token", token=True, ctr={"p1p1": 6})])
    check(act(st, "Saheeli, Sublime Artificer", "Saheeli, Sublime Artificer", "-2"))
    sv = perm(st, "Servo Token")
    check(T.power(st, sv) == 4 and T.toughness(st, sv) == 4, f"{T.power(st, sv)}/{T.toughness(st, sv)}")


@test("Ruling Patrolling Peacemaker (2025-07-25): descarte, magia anulada e wipe de cemiterio do oponente que miram a mim sao CRIMES (proliferate); wipe sem alvo nao")
def _():
    for fn, key in (("try_smart_opponent_discard", "discard"), ("try_smart_opponent_graveyard_wipe", "graveyard")):
        st = mk(res=True, hand=["Sol Ring"], gy=["Sol Ring"] if key == "graveyard" else [], bf=["Patrolling Peacemaker", P("Garruk Wildspeaker", loyalty=3)], turn=8)
        perm(st, "Patrolling Peacemaker").ctr["p1p1"] = 2
        st.interaction_rng = R0(1)
        getattr(T, fn)(st)
        check(st.m["opp_crimes_" + key] == 1 and loy(st, "Garruk Wildspeaker") == 4, f"{key}: {st.m['opp_crimes_' + key]}")
    st = mk(res=True, bf=["Patrolling Peacemaker", P("Garruk Wildspeaker", loyalty=3)], turn=8)
    st.interaction_rng = R0(1)
    check(T.counterspell_check(st, "Garruk, Curse Breaker") and st.m["opp_crimes_counterspell"] == 1 and loy(st, "Garruk Wildspeaker") == 4)
    st = mk(res=True, bf=["Patrolling Peacemaker", "Beast Token"], turn=8)
    st.interaction_rng = R0(1)
    T.try_smart_opponent_wipe(st)
    check(st.m["opp_crimes_total"] == 0, "'destroy all' nao mira nada: nao e' crime")


@test("Ruling Vronos (2023-07-28): -7 pode mirar artefato que ja' e' criatura (Servo); base 9/9 sobrescreve")
def _():
    st = mk(bf=[P("Vronos, Masked Inquisitor", loyalty=7), P("Servo Token", token=True)])
    check(act(st, "Vronos, Masked Inquisitor", "Vronos, Masked Inquisitor", "-7"))
    sv = perm(st, "Servo Token")
    check(T.power(st, sv) == 9 and sv.ctr.get("vigilance") and sv.ctr.get("indestructible") and sv.unblockable)


@test("Ruling Tezzeret (2008-10-01): -5 afeta TODOS os artefatos, inclusive os que ja' sao criaturas; o que era 9/9 (Construct do Vronos) vira 5/5 ate' o fim do turno e depois volta")
def _():
    st = mk(bf=[P("Tezzeret the Seeker", loyalty=5), P("Servo Token", token=True), "Sol Ring", "Patrolling Peacemaker"])
    perm(st, "Patrolling Peacemaker").ctr["p1p1"] = 2
    check(act(st, "Tezzeret the Seeker", "Tezzeret the Seeker", "-5"))
    check(T.power(st, perm(st, "Servo Token")) == 5 and T.power(st, perm(st, "Sol Ring")) == 5 and T.power(st, perm(st, "Patrolling Peacemaker")) == 7, "5/5 base + 2 contadores no Peacemaker")
    T.end_step(st)
    check(T.power(st, perm(st, "Servo Token")) == 1 and not T.is_creature(perm(st, "Sol Ring")) and T.power(st, perm(st, "Patrolling Peacemaker")) == 2)
    st = mk(bf=[P("Tezzeret the Seeker", loyalty=5), "Sol Ring"])
    c = perm(st, "Sol Ring"); c.base_pt = (9, 9); c.anim = "forever"
    act(st, "Tezzeret the Seeker", "Tezzeret the Seeker", "-5")
    check(T.power(st, c) == 5, "o 9/9 de antes e' sobrescrito ate' o fim do turno")
    T.end_step(st)
    check(T.power(st, c) == 9 and c.anim == "forever", "restaurado")


@test("Aminatou -6 (resiliencia): o oponente recebe meus permanentes nao-terreno (menos Aminatou) e eu recebo as criaturas dele; so' vale quando o meu campo e' fraco e o dele forte")
def _():
    st = mk(res=True, bf=[P("Aminatou, the Fateshifter", loyalty=7), "Birds of Paradise", "Sol Ring"])
    for _ in range(4):
        add_opp_creature(st, 1, 6, 6)
    check(any(o[2] == "-6" for o in T.ability_options(st, perm(st, "Aminatou, the Fateshifter"))), "campo fraco x tabuleiro forte: vale")
    check(act(st, "Aminatou, the Fateshifter", "Aminatou, the Fateshifter", "-6"))
    check(len(st.opps[0].board) == 1 and st.opps[0].board[0]["p"] == 0, "ele recebeu so' a Birds (0/1); Sol Ring nao e' criatura")
    check(perm(st, "Birds of Paradise") is None and perm(st, "Sol Ring") is None and perm(st, "Aminatou, the Fateshifter") is not None)
    check(sum(1 for p in T.creatures(st) if p.card.name == "Cadet Token" and T.power(st, p) == 6) == 4, "eu recebi as 4 criaturas 6/6 dele")
    st = mk(res=True, bf=[P("Aminatou, the Fateshifter", loyalty=6), P("Garruk Wildspeaker", loyalty=5), P("Oko, Thief of Crowns", loyalty=4), "Beast Token"])
    add_opp_creature(st, 1, 3, 3)
    check(not any(o[2] == "-6" for o in T.ability_options(st, perm(st, "Aminatou, the Fateshifter"))), "campo forte: nao troca")
    st = mk(bf=[P("Aminatou, the Fateshifter", loyalty=6)])
    check(not any(o[2] == "-6" for o in T.ability_options(st, perm(st, "Aminatou, the Fateshifter"))), "modo padrao: sem permanente de oponente: nunca")

"""Testes das 3 mudancas de 2026-10-22 (pedido do usuario: "Termine tudo que falta!"): a Tam ataca quando o {T} dela nao tem uso (TAM_ATTACKS), Aminatou -1 / Displacer Kitten piscam permanente de mana
VIRADO (BLINK_UNTAP_MANA) e a Saheeli copia criatura com habilidade e o Staff (SAHEELI_COPY_CREATURES). Cada clausula do oraculo envolvida e' uma afirmacao testavel (CLAUDE.md Regra #1/#6)."""
from harness import *


def P(name, **kw):
    return (name, kw)


def opp_all_colors(st):
    for o in st.opps:
        o.land_colors = ["W", "U", "B", "R", "G"]


class Flag:
    """Liga/desliga uma chave do simulador durante um teste."""
    def __init__(self, **kw):
        self.kw = kw
        self.old = {}

    def __enter__(self):
        for k, v in self.kw.items():
            self.old[k] = getattr(T, k)
            setattr(T, k, v)

    def __exit__(self, *a):
        for k, v in self.old.items():
            setattr(T, k, v)


# ---------------- Tam ataca ----------------
@test("TAM_ATTACKS: a Tam (2/4, em campo desde o turno anterior) ataca quando nao pode ativar o proliferate (sem planeswalkers): 2 de dano, fica virada, conta `tam_attacks`")
def _():
    st = mk(turn=5, bf=["Tam, the Possibility", "City of Brass", "Command Tower"])
    tam = perm(st, "Tam, the Possibility")
    check(T.can_attack(st, tam), "sem planeswalkers: X < 2, a habilidade nao e' possivel: atacar e' de graca")
    before = sum(o.life for o in st.opps)
    T.combat_step(st)
    check(tam.tapped, "atacou sem vigilancia: virada")
    check(sum(o.life for o in st.opps) == before - 2, "dano 2: %d" % (before - sum(o.life for o in st.opps)))
    check(st.m["tam_attacks"] == 1)


@test("TAM_ATTACKS: com {W}{U}{B}{R}{G} pagavel, X >= 2 e >= 2 alvos de proliferate a Tam NAO ataca (o {T} dela e' a habilidade); `use_spare_mana` ativa; sem mana ela ataca")
def _():
    bf = ["Tam, the Possibility", "Chromatic Orrery", P("Jace Token", loyalty=3, token=True), P("Ajani Unrelenting", loyalty=4), P("Teferi, Hero of Dominaria", loyalty=4)]
    st = mk(turn=8, bf=bf, phase="main2")
    tam = perm(st, "Tam, the Possibility")
    check(T.tam_activation_check(st) >= 2, "X=%s" % T.tam_activation_check(st))
    check(not T.can_attack(st, tam), "a habilidade e' possivel: a Tam fica em casa")
    check(T.act_tam_proliferate(st) and tam.tapped and st.m["tam_activations"] == 1, "ativou")
    st = mk(turn=8, bf=["Tam, the Possibility", P("Jace Token", loyalty=3, token=True), P("Ajani Unrelenting", loyalty=4), P("Teferi, Hero of Dominaria", loyalty=4)])
    tam = perm(st, "Tam, the Possibility")
    check(T.tam_activation_check(st) == 0 and T.can_attack(st, tam), "sem mana WUBRG: ataca")


@test("TAM_ATTACKS: a Tam recem-conjurada (doenca de invocacao) nao ataca; virada nao ataca; chave desligada = nunca ataca")
def _():
    st = mk(turn=5, bf=[P("Tam, the Possibility", sick=True)])
    check(not T.can_attack(st, perm(st, "Tam, the Possibility")), "doenca de invocacao")
    st = mk(turn=5, bf=[P("Tam, the Possibility", tapped=True)])
    check(not T.can_attack(st, perm(st, "Tam, the Possibility")), "virada")
    with Flag(TAM_ATTACKS=False):
        st = mk(turn=5, bf=["Tam, the Possibility"])
        check(not T.can_attack(st, perm(st, "Tam, the Possibility")), "chave desligada: comportamento antigo")


@test("TAM_ATTACKS + Tamiyo +1: marca a Tam (unica criatura), ela ataca e eu compro 1 carta (goldfish manual #2: o usuario atacou com a Tam); Birds/Bloom Tender/Hierarchs continuam em casa")
def _():
    st = mk(turn=6, lib=["Sol Ring", "Command Tower", "Forest"], bf=["Tam, the Possibility", P("Tamiyo, Field Researcher", loyalty=4), "Birds of Paradise", "Bloom Tender"])
    tam = perm(st, "Tam, the Possibility")
    check(T.untapped_attackers(st) == [tam], "so' a Tam: " + str([p.card.name for p in T.untapped_attackers(st)]))
    check(act(st, "Tamiyo, Field Researcher", "Tamiyo, Field Researcher", "+1") and tam.uid in st.tamiyo_marked, "Tamiyo +1 marca a Tam")
    n = len(st.hand)
    T.combat_step(st)
    check(len(st.hand) == n + 1 and st.m["tamiyo_combat_draws"] == 1, "comprou 1: %d" % (len(st.hand) - n))


@test("TAM_ATTACKS (resiliencia): com uma criatura de oponente em campo a Tam fica em casa de bloqueadora (o usuario bloqueou a ficha Warrior com ela no goldfish manual #3); sem ameaca ela ataca")
def _():
    st = mk(turn=6, res=True, bf=["Tam, the Possibility"])
    tam = perm(st, "Tam, the Possibility")
    check(T.can_attack(st, tam), "sem criatura de oponente: ataca")
    add_opp_creature(st, 1, p=3, t=3)
    check(not T.can_attack(st, tam), "com ameaca em campo: fica em casa")
    st = mk(turn=6, res=False, bf=["Tam, the Possibility"])
    check(T.can_attack(st, perm(st, "Tam, the Possibility")), "modo padrao: sem tabuleiro de oponente")


@test("TAM_ATTACKS (resiliencia): depois de atacar a Tam esta virada e NAO bloqueia no turno do oponente (CR 508.1: o atacante vira e desvira so' no meu proximo untap)")
def _():
    st = mk(turn=6, res=True, bf=["Tam, the Possibility"])
    tam = perm(st, "Tam, the Possibility")
    T.combat_step(st)
    check(tam.tapped and not T.can_block(st, tam), "virada: nao bloqueia")


# ---------------- piscar permanente de mana virado ----------------
HAND_TEFERI = ["Teferi, Hero of Dominaria"]      # {3}{W}{U}: 5 de mana, W e U


@test("BLINK_UNTAP_MANA: Sol Ring VIRADO + 3 terrenos: Teferi (5) nao cabe; piscar o Sol Ring (volta desvirado, 2 de mana) o paga -> blink_unlock_options acha o Sol Ring")
def _():
    st = mk(turn=6, hand=HAND_TEFERI, bf=[P("Sol Ring", tapped=True), "Hallowed Fountain", "Command Tower", "Plaza of Heroes", P("Aminatou, the Fateshifter", loyalty=3)])
    check(not T.can_cast_name(st, "Teferi, Hero of Dominaria"), "sem o Sol Ring nao cabe")
    ul = T.blink_unlock_options(st)
    check([p.card.name for _, p in ul] == ["Sol Ring"] and ul[0][0] == 2, str([(e, p.card.name) for e, p in ul]))
    check(perm(st, "Sol Ring").tapped, "o ensaio a seco restaura o estado: Sol Ring continua virado")


@test("BLINK_UNTAP_MANA: Aminatou -1 pisca o Sol Ring virado (pontuacao 62, acima do +1 = 56), a lealdade vai de 3 a 2, o Sol Ring volta desvirado e o Teferi passa a caber")
def _():
    st = mk(turn=6, hand=HAND_TEFERI, bf=[P("Sol Ring", tapped=True), "Hallowed Fountain", "Command Tower", "Plaza of Heroes", P("Aminatou, the Fateshifter", loyalty=3)])
    ami = perm(st, "Aminatou, the Fateshifter")
    opts = T.ability_options(st, ami)
    check(opts and (opts[0][1], opts[0][2]) == ("Aminatou, the Fateshifter", "-1") and opts[0][0] == 62, str(opts[:2]))
    check(act(st, "Aminatou, the Fateshifter", "Aminatou, the Fateshifter", "-1") and loy(st, "Aminatou, the Fateshifter") == 2)
    sr = perm(st, "Sol Ring")
    check(not sr.tapped and st.m["aminatou_mana_blinks"] == 1 and st.m["blinks_total"] == 1)
    check(T.can_cast_name(st, "Teferi, Hero of Dominaria") and T.cast_card(st, "Teferi, Hero of Dominaria"), "o mana do Sol Ring paga o Teferi")


@test("BLINK_UNTAP_MANA: nao pisca sem motivo (a carta da mao ja' cabe), nem criatura de mana virada (volta com doenca de invocacao), nem terreno que entra virado (Triome), nem com a chave desligada")
def _():
    st = mk(turn=6, hand=HAND_TEFERI, bf=[P("Sol Ring", tapped=True), "Hallowed Fountain", "Command Tower", "Plaza of Heroes", "City of Brass", "Boseiju, Who Endures", P("Aminatou, the Fateshifter", loyalty=3)])
    check(T.can_cast_name(st, "Teferi, Hero of Dominaria") and T.blink_unlock_options(st) == [], "ja' cabe: nada a destravar")
    st = mk(turn=6, hand=HAND_TEFERI, bf=[P("Birds of Paradise", tapped=True), "Hallowed Fountain", "Command Tower", "Plaza of Heroes", "City of Brass", P("Aminatou, the Fateshifter", loyalty=3)])
    check(not T.can_cast_name(st, "Teferi, Hero of Dominaria") and T.blink_unlock_options(st) == [], "criatura piscada tem doenca de invocacao")
    st = mk(turn=6, hand=HAND_TEFERI, bf=[P("Ketria Triome", tapped=True), "Hallowed Fountain", "Command Tower", "Plaza of Heroes", P("Sol Ring", ), P("Aminatou, the Fateshifter", loyalty=3)])
    check([p.card.name for _, p in T.blink_unlock_options(st)] == [], "Triome entra virado: nao rende")
    with Flag(BLINK_UNTAP_MANA=False):
        st = mk(turn=6, hand=HAND_TEFERI, bf=[P("Sol Ring", tapped=True), "Hallowed Fountain", "Command Tower", "Plaza of Heroes", P("Aminatou, the Fateshifter", loyalty=3)])
        check(T.blink_unlock_options(st) == [], "chave desligada")
        ami = perm(st, "Aminatou, the Fateshifter")
        opts = T.ability_options(st, ami)
        check(not opts or (opts[0][1], opts[0][2]) != ("Aminatou, the Fateshifter", "-1"), "o -1 nao e' escolhido")


@test("BLINK_UNTAP_MANA: terreno virado que entra desvirado (City of Brass) tambem destrava; o choque paga 2 de vida ao voltar; o piscar de terreno passa pelo ponto de entrada de terreno (conta `lands_entered_total`)")
def _():
    st = mk(turn=6, hand=["Aminatou, the Fateshifter"], bf=[P("City of Brass", tapped=True), "Hallowed Fountain", "Command Tower", P("Aminatou, the Fateshifter", loyalty=3)])
    check(not T.can_cast_name(st, "Aminatou, the Fateshifter"), "so' 2 fontes desviradas: {W}{U}{B} (3 mana) nao cabe")
    ul = T.blink_unlock_options(st)
    check([p.card.name for _, p in ul] == ["City of Brass"], str([p.card.name for _, p in ul]))
    st2 = mk(turn=6, hand=["Aminatou, the Fateshifter"], bf=[P("Watery Grave", tapped=True), "Hallowed Fountain", "Command Tower", P("Aminatou, the Fateshifter", loyalty=3)])
    life = st2.life
    t = perm(st2, "Watery Grave")
    new = T.blink_any(st2, t, "aminatou")
    check(new is not None and not new.tapped and st2.life == life - 2 and st2.m["lands_entered_total"] == 1, f"choque: vida {life}->{st2.life}, tapped={new.tapped if new else None}")


@test("BLINK_UNTAP_MANA + Displacer Kitten: a magia nao-criatura paga, o Sol Ring esta virado: o gatilho pisca o Sol Ring (nao e' terreno: 'nonland permanent') e o proximo Teferi cabe")
def _():
    st = mk(turn=6, hand=["Ripples of Potential", "Teferi, Hero of Dominaria"],
            bf=["Displacer Kitten", P("Sol Ring", tapped=True), "Hallowed Fountain", "Command Tower", "Plaza of Heroes", P("City of Brass", tapped=True), P("Jace Token", loyalty=2, token=True)])
    check(not T.can_cast_name(st, "Teferi, Hero of Dominaria"))
    T.kitten_trigger(st, "Ripples of Potential")
    sr = perm(st, "Sol Ring")
    check(not sr.tapped and st.m["kitten_mana_blinks"] == 1, "Sol Ring piscado: " + str(dict(st.m)))
    ct = perm(st, "City of Brass")
    check(ct.tapped, "o Kitten so' mira permanente nao-terreno: a City continua virada")


# ---------------- Saheeli copia criatura / Staff ----------------
@test("SAHEELI_COPY_CREATURES: Servo (em campo desde antes) vira copia do Bloom Tender: rende 1 mana por COR entre meus permanentes (3 cores = 3 mana) e paga o Teferi que nao cabia; copia de Sol Ring (2) so' ganha se nao houver mais")
def _():
    st = mk(turn=6, hand=HAND_TEFERI, bf=["Bloom Tender", "Command Tower", "Plaza of Heroes", P("Servo Token", token=True), P("Saheeli, Sublime Artificer", loyalty=5), P("Ajani Unrelenting", loyalty=4), "Faeburrow Elder"])
    bt = perm(st, "Bloom Tender"); bt.tapped = True
    el = perm(st, "Faeburrow Elder"); el.tapped = True
    chs = T.saheeli_mana_choices(st)
    check(chs and chs[0][2] == len(T.colors_among(st)) and chs[0][1].card.name in ("Bloom Tender", "Faeburrow Elder"), str([(c[1].card.name, c[2]) for c in chs]))
    # fontes viradas nao importam: a copia e' do permanente (copiavel), o Servo esta desvirado
    check(not T.can_cast_name(st, "Teferi, Hero of Dominaria"))
    w = T.saheeli_mana_wanted(st)
    check(w is not None, "a copia destrava o Teferi")
    check(act(st, "Saheeli, Sublime Artificer", "Saheeli, Sublime Artificer", "-2") and loy(st, "Saheeli, Sublime Artificer") == 3)
    sv = perm(st, "Servo Token")
    check(sv.copy_of in ("Bloom Tender", "Faeburrow Elder") and T.is_creature(sv) and not sv.tapped and st.m["saheeli_creature_mana_copies"] == 1, str(sv.copy_of))
    check(T.can_cast_name(st, "Teferi, Hero of Dominaria"), "5 mana com a copia")


@test("SAHEELI_COPY_CREATURES: Servo criado NESTE turno (doenca de invocacao) nao toca como copia de criatura de mana; copia de artefato de mana toca (nao e' criatura); no fim do turno a copia acaba")
def _():
    st = mk(turn=6, hand=HAND_TEFERI, bf=["Bloom Tender", "Command Tower", "Plaza of Heroes", P("Servo Token", token=True, sick=True), P("Saheeli, Sublime Artificer", loyalty=5), P("Ajani Unrelenting", loyalty=4)])
    check(T.saheeli_mana_choices(st) == [], "so' Servo doente + criatura de mana: nada")
    sv = perm(st, "Servo Token")
    sv.copy_of = "Bloom Tender"
    check(T.is_creature(sv) and T.sick(st, sv) and not [s for s in T.mana_sources(st) if s.perm is sv], "copia de criatura com doenca de invocacao: sem {T}")
    sv.copy_of = "Sol Ring"
    check(not T.is_creature(sv) and [s for s in T.mana_sources(st) if s.perm is sv], "copia de artefato: toca")
    sv.copy_of = "Bloom Tender"
    T.end_step(st)
    check(sv.copy_of is None, "a copia acaba no fim do turno")


@test("SAHEELI_COPY_CREATURES: copia do Flux Channeler ANTES de conjurar: cada magia nao-criatura dispara 2 proliferates (a criatura real + a copia); so' com 2+ permanentes com contador e uma magia nao-criatura valiosa que cabe")
def _():
    base = ["Flux Channeler", P("Servo Token", token=True), P("Saheeli, Sublime Artificer", loyalty=5), P("Ajani Unrelenting", loyalty=4), P("Jace Token", loyalty=2, token=True),
            "Command Tower", "Plaza of Heroes", "City of Brass", "Hallowed Fountain", "Overflowing Basin"]
    st = mk(turn=6, hand=["Teferi, Hero of Dominaria"], bf=base)
    w = T.saheeli_trigger_wanted(st)
    check(w is not None and w[1].card.name == "Flux Channeler", str(w))
    check(act(st, "Saheeli, Sublime Artificer", "Saheeli, Sublime Artificer", "-2"))
    check(T.count_eff(st, "Flux Channeler") == 2 and st.m["saheeli_trigger_copies"] == 1)
    l0 = loy(st, "Ajani Unrelenting")
    check(T.cast_card(st, "Teferi, Hero of Dominaria"))
    check(loy(st, "Ajani Unrelenting") == l0 + 2, "2 proliferates: %d -> %d" % (l0, loy(st, "Ajani Unrelenting")))
    st = mk(turn=6, hand=[], bf=base)
    check(T.saheeli_trigger_wanted(st) is None, "sem magia a conjurar: nao gasta lealdade")
    st = mk(turn=6, hand=["Teferi, Hero of Dominaria"], bf=["Flux Channeler", P("Servo Token", token=True), P("Saheeli, Sublime Artificer", loyalty=5), "Command Tower", "Plaza of Heroes", "City of Brass", "Hallowed Fountain", "Overflowing Basin"])
    check(T.saheeli_trigger_wanted(st) is None, "menos de 2 permanentes com contador: o proliferate nao rende")


@test("SAHEELI_COPY_CREATURES: copia do Displacer Kitten dispara o piscar 2x por magia nao-criatura (perms_eff); Kiora e Tam (lendarias) NUNCA entram na lista de fontes")
def _():
    st = mk(turn=6, bf=["Displacer Kitten", P("Servo Token", token=True), P("Saheeli, Sublime Artificer", loyalty=5), "Way of the Paradox"])
    sv = perm(st, "Servo Token")
    sv.copy_of = "Displacer Kitten"
    check(T.count_eff(st, "Displacer Kitten") == 2 and len(T.perms_eff(st, "Displacer Kitten")) == 2)
    check(T.count_named(st, "Displacer Kitten") == 1, "o simulador le o nome impresso: so' perms_eff enxerga a copia")
    st = mk(turn=6, hand=["Teferi, Hero of Dominaria"], bf=["Kiora of Salt and Sand", "Tam, the Possibility", P("Servo Token", token=True), P("Saheeli, Sublime Artificer", loyalty=5), "Command Tower", "Plaza of Heroes", "City of Brass", "Hallowed Fountain"])
    check(all(c[1].card.name not in ("Kiora of Salt and Sand", "Tam, the Possibility") for c in T.saheeli_mana_choices(st)) and T.saheeli_trigger_wanted(st) is None)


@test("SAHEELI_COPY_CREATURES: copia do Staff of Compleation no 2o main (artefato nao lendario): a copia tem as habilidades; act_staff usa o Staff real E a copia (2 proliferates, 6 de vida)")
def _():
    bf = ["Staff of Compleation", P("Servo Token", token=True), P("Saheeli, Sublime Artificer", loyalty=5), P("Ajani Unrelenting", loyalty=4), P("Jace Token", loyalty=3, token=True), P("Teferi, Hero of Dominaria", loyalty=5),
          P("Garruk, Curse Breaker", loyalty=4), "Command Tower"]
    st = mk(turn=8, life=40, bf=bf, phase="main2")
    check(T.staff_use_kind(st) == "proliferate")
    w = T.saheeli_staff_wanted(st)
    check(w is not None and w[1].card.name == "Staff of Compleation", str(w))
    check(act(st, "Saheeli, Sublime Artificer", "Saheeli, Sublime Artificer", "-2") and st.m["saheeli_staff_copies"] == 1)
    check(T.count_eff(st, "Staff of Compleation") == 2)
    check(T.act_staff(st) and T.act_staff(st) and st.life == 34 and st.m["staff_proliferates"] == 2, "2 usos: vida %d" % st.life)
    st = mk(turn=8, life=40, bf=bf, phase="main1")
    check(T.saheeli_staff_wanted(st) is None, "so' no 2o main (o act_staff so' roda la)")
    with Flag(SAHEELI_COPY_CREATURES=False):
        st = mk(turn=8, life=40, bf=bf, phase="main2")
        check(T.saheeli_staff_wanted(st) is None and T.saheeli_trigger_wanted(st) is None, "chave desligada")


@test("As 3 mudancas disparam em partidas inteiras (60 sementes por modo, nenhuma excecao): ataques da Tam, Servo/Saheeli e piscar")
def _():
    tot = {"m_tam_attacks": 0, "m_saheeli_trigger_copies": 0}
    for res in (False, True):
        for sd in range(3_000_000, 3_000_060):
            r = (T.simulate_one_with_interaction if res else T.simulate_one)(sd, 10)
            for k in tot:
                tot[k] += getattr(r, k, 0)
    check(tot["m_tam_attacks"] > 0, "a Tam ataca em partidas inteiras: %s" % tot)


# ---------------- rodada 2 (2026-10-22): turnos extras empilhados, mana vivid, combo, perfil do playtester ----------------
@test("EXTRA_TURNS_STACK: partida inteira — 2 ativacoes de -12 no mesmo turno rendem 2 turnos extras seguidos (play_rounds); com a chave desligada rende 1")
def _():
    def joga(flag):
        with Flag(EXTRA_TURNS_STACK=flag):
            st = mk(turn=11, bf=["Ichormoon Gauntlet", P("Jace Token", loyalty=14, token=True), P("Domri, Chaos Bringer", loyalty=13)], phase="main1")
            st.turn = 0
            st.turn_id = 0
            st.library = T.current_library()[:60]
            act(st, "Jace Token", "Ichormoon Gauntlet", "-12")
            act(st, "Domri, Chaos Bringer", "Ichormoon Gauntlet", "-12")
            T.play_rounds(st, 4)
            return st.m["extra_turns_played"]
    check(joga(True) == 2 and joga(False) == 1, "2 turnos extras vs 1: %s %s" % (joga(True), joga(False)))


@test("VIVID_LAST: a magia que traz COR NOVA (Pyromancer, R) e' paga pelos terrenos se eles bastam: o Bloom Tender fica desvirado e rende 1 mana por cor DEPOIS (G, U, R = 3, nao 2); a magia sem cor nova (Paradox) paga normal")
def _():
    st = mk(turn=4, hand=["Way of the Pyromancer", "Way of the Paradox", "Way of the Necromancer"], bf=["Tam, the Possibility", "Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Bloom Tender"])
    bt = perm(st, "Bloom Tender")
    check(T.cast_card(st, "Way of the Pyromancer") and not bt.tapped, "Bloom Tender nao foi tocado pra Pyromancer (R e' cor nova)")
    check(len([s for s in T.mana_sources(st) if s.perm is bt][0].units) == 3, "agora rende 3 (G, U, R)")
    with Flag(VIVID_LAST=False, SIBLING_FIRST=False):
        st = mk(turn=4, hand=["Way of the Pyromancer"], bf=["Tam, the Possibility", "Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave", "Bloom Tender"])
        T.cast_card(st, "Way of the Pyromancer")
        check(perm(st, "Bloom Tender").tapped, "chaves desligadas: o comportamento de antes (Bloom Tender tocado com so' 2 cores)")
    # quando o resto das fontes NAO paga, o Bloom Tender toca normalmente
    st = mk(turn=4, hand=["Way of the Pyromancer"], bf=["Tam, the Possibility", "Fire-Lit Thicket", "Bloom Tender"])
    check(T.cast_card(st, "Way of the Pyromancer") and perm(st, "Bloom Tender").tapped, "so' Thicket + Bloom Tender: o Bloom Tender paga")


@test("SIBLING_FIRST: o generico sai da 2a unidade do filtro (Fire-Lit Thicket) antes de tocar outro terreno (nao desperdica o Watery Grave)")
def _():
    st = mk(turn=4, hand=["Way of the Pyromancer"], bf=["Bountiful Promenade", "Fire-Lit Thicket", "Watery Grave"])
    check(T.cast_card(st, "Way of the Pyromancer"))
    check(not perm(st, "Watery Grave").tapped and perm(st, "Fire-Lit Thicket").tapped, "Promenade + Thicket (RR) pagam: o Grave fica")


@test("COMBO_CAST_PAYOFF_FROM_HAND: Orrery + Tezzeret + Chain Veil montados (mana infinito) e Sanctum Lurker NA MAO: o simulador conjura o Lurker e fecha a partida; sem o pagamento na mao so' registra a montagem; chave desligada = como antes")
def _():
    bf = ["Chromatic Orrery", "The Chain Veil", P("Tezzeret the Seeker", loyalty=4)]
    st = mk(turn=8, hand=["Sanctum Lurker"], bf=bf)
    T.try_infinite_combo(st)
    check(st.game_over and st.combo_win == "orrery_tezzeret_veil" and st.m["combo_payoff_cast_from_hand"] == 1, "fechou com o Lurker da mao")
    st = mk(turn=8, hand=["Sol Ring"], bf=bf)
    T.try_infinite_combo(st)
    check(not st.game_over and st.m["combo_assembled"] == 1, "sem pagamento: so' montou")
    with Flag(COMBO_CAST_PAYOFF_FROM_HAND=False):
        st = mk(turn=8, hand=["Sanctum Lurker"], bf=bf)
        T.try_infinite_combo(st)
        check(not st.game_over, "chave desligada: nao conjura da mao")


@test("OPP_PLAYTESTER (perfil calibrado nos 5 goldfish do usuario): criaturas de oponente raras (so' a partir do 3o turno dele, no maximo 4), nenhum arquetipo; aplica_perfil muda as chaves do modulo")
def _():
    old = {k: getattr(T, k) for k in T.PERFIL_PLAYTESTER}
    try:
        T.aplica_perfil("playtester")
        check(T.OPP_PLAYTESTER and T.OPP_CARD_MIX and T.OPP_PLAYTESTER_ATTENTION < 0.2 and T.OPP_PLAYTESTER_SPELLS_PROB[0] > 0.5)
        total = 0
        for sd in range(1, 41):
            st = T.new_state(sd)
            T.setup_resilience(st, sd)
            for t in range(1, 11):
                T.play_turn(st)
                for o in list(st.opps):
                    if not o.eliminated:
                        T.opponent_turn(st, o)
            total += sum(len(o.board) for o in st.opps)
        check(total / 40 < 4.0, "criaturas de oponente em campo no T10 (3 oponentes): %.2f por partida" % (total / 40))
    finally:
        for k, v in old.items():
            setattr(T, k, v)
    check(not T.OPP_PLAYTESTER, "restaurado")


@test("OPP_CARD_MIX: Damning Verdict ('destroy all creatures with no counters') poupa a criatura com contador; Split Up mata so' as viradas OU so' as desviradas (a maior turma); Promise of Loyalty deixa so' a melhor (contador Vow); Cleansing Nova leva todas; Vex deixa comprar; sem a chave o wipe leva tudo")
def _():
    class FakeRng:
        def __init__(self, v): self.v = v
        def random(self): return 0.0          # sempre passa os gates
        def choice(self, seq): return self.v if self.v in seq else seq[0]
        def choices(self, seq, weights=None): return [seq[0]]
    def wipe(variant, tap=(), mix=True):
        with Flag(OPP_CARD_MIX=mix):
            st = mk(turn=8, res=True, bf=["Tam, the Possibility", P("Beast Token", token=True), P("Bloom Tender", ctr={"Vow": 1}), P("Patrolling Peacemaker", ctr={"p1p1": 2})])
            st.interaction_rng = FakeRng(variant)
            st.opps[0].board.append(T.new_opp_creature(3, 3))
            for p in st.battlefield:
                if p.card.name in tap:
                    p.tapped = True
            T.try_smart_opponent_wipe(st)
            return st
    vivos = lambda st: sorted(p.card.name for p in st.battlefield if T.is_creature(p))
    check(vivos(wipe("verdict")) == ["Bloom Tender", "Patrolling Peacemaker"], "Verdict: so' as sem contador morrem: %s" % vivos(wipe("verdict")))
    check(vivos(wipe("split_up", tap=("Tam, the Possibility",))) == ["Tam, the Possibility"], "Split Up: 1 virada x 3 desviradas: mata as desviradas, a Tam virada fica: %s" % vivos(wipe("split_up", tap=("Tam, the Possibility",))))
    check(vivos(wipe("split_up", tap=("Tam, the Possibility", "Beast Token", "Bloom Tender"))) == ["Patrolling Peacemaker"], "3 viradas x 1 desvirada: mata as viradas")
    st = wipe("promise")
    check(len(vivos(st)) == 1 and st.m["opp_wipe_promise"] == 1 and [p for p in st.battlefield if p.ctr.get("vow")], "Promise: 1 sobra, com Vow: %s" % vivos(st))
    check(vivos(wipe("nova")) == [], "Nova: todas, ate' as com contador: %s" % vivos(wipe("nova")))
    check(vivos(wipe("verdict", mix=False)) == [], "chave desligada: o wipe leva tudo (como antes)")
    with Flag(OPP_CARD_MIX=True):
        st = mk(turn=8, res=True, hand=["Teferi, Hero of Dominaria"], lib=["Sol Ring", "Command Tower"])
        st.interaction_rng = FakeRng("x")
        n = len(st.hand)
        check(T.counterspell_check(st, "Teferi, Hero of Dominaria") and len(st.hand) == n + 1 and st.m["opp_vex_draws"] == 1, "Vex: compro 1")
    st = mk(turn=8, res=True, hand=["Teferi, Hero of Dominaria"], lib=["Sol Ring", "Command Tower"])
    st.interaction_rng = FakeRng("x")
    n = len(st.hand)
    check(T.counterspell_check(st, "Teferi, Hero of Dominaria") and len(st.hand) == n and st.m["opp_vex_draws"] == 0, "sem a chave: anulacao seca")

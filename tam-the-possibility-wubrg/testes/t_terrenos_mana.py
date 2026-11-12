from harness import *

U, G, W, B, R = (frozenset(c) for c in "UGWBR")


def pips(*cs):
    return tuple(frozenset(c) for c in cs)


# ---------------- entrada dos terrenos (arquetipo do oraculo de cada um) ----------------
@test("Breeding Pool (choque): paga 2 de vida se vida >= 10, senao entra virado")
def _():
    st = mk(life=30)
    p = T.put_land_onto_battlefield(st, "Breeding Pool", source="play")
    check(not p.tapped and st.life == 28, f"vida {st.life} virado {p.tapped}")
    st = mk(life=9)
    p = T.put_land_onto_battlefield(st, "Breeding Pool", source="play")
    check(p.tapped and st.life == 9, "com vida < 10 deve entrar virado sem pagar")


@test("Todos os 7 choques: Hallowed Fountain, Overgrown Tomb, Steam Vents, Stomping Ground, Temple Garden, Watery Grave")
def _():
    for n in ("Hallowed Fountain", "Overgrown Tomb", "Steam Vents", "Stomping Ground", "Temple Garden", "Watery Grave"):
        st = mk(life=30)
        p = T.put_land_onto_battlefield(st, n)
        check(not p.tapped and st.life == 28, n)


@test("Triomes (5) e The World Tree entram virados")
def _():
    for n in ("Indatha Triome", "Jetmir's Garden", "Ketria Triome", "Spara's Headquarters", "Zagoth Triome", "The World Tree"):
        st = mk()
        check(T.put_land_onto_battlefield(st, n).tapped, n)


@test("Slowlands (Promenade, Springs, Spire Garden, Stadium): desvirados com >= 2 oponentes, virados com 1")
def _():
    for n in ("Bountiful Promenade", "Rejuvenating Springs", "Spire Garden", "Undergrowth Stadium"):
        st = mk(opps=3)
        check(not T.put_land_onto_battlefield(st, n).tapped, n + " com 3 oponentes")
        st = mk(opps=1)
        check(T.put_land_onto_battlefield(st, n).tapped, n + " com 1 oponente")


@test("Starting Town: desvirado no meu 1o/2o/3o turno, virado depois")
def _():
    for t, exp in ((1, False), (3, False), (4, True), (9, True)):
        st = mk(turn=t)
        check(T.put_land_onto_battlefield(st, "Starting Town").tapped == exp, f"turno {t}")


@test("Terrenos sem condicao entram desvirados: filtros, Baxter, Great Hall, Plaza, City of Brass, Command Tower, Orchard, Boseiju, Yavimaya, Mossfire, Basin")
def _():
    for n in ("Fire-Lit Thicket", "Flooded Grove", "Twilight Mire", "Wooded Bastion", "Baxter Building", "Great Hall of the Citadel", "Plaza of Heroes", "City of Brass", "Command Tower",
              "Exotic Orchard", "Boseiju, Who Endures", "Yavimaya, Cradle of Growth", "Mossfire Valley", "Overflowing Basin"):
        st = mk()
        check(not T.put_land_onto_battlefield(st, n).tapped, n)


# ---------------- fetch ----------------
@test("Fetch: 1 de vida, sacrifica (vai pro cemiterio), busca por SUBTIPO e o terreno entra desvirado")
def _():
    st = mk(hand=["Windswept Heath"], life=30, lib=["Temple Garden", "Command Tower", "Steam Vents"])
    T.play_land_phase(st)
    check(perm(st, "Windswept Heath") is None and "Windswept Heath" in st.graveyard, "fetch devia estar no cemiterio")
    check(perm(st, "Temple Garden") is not None, "devia buscar Temple Garden (Forest Plains)")
    check(st.life == 30 - 1 - 2, f"1 (fetch) + 2 (choque) de vida: {st.life}")
    check(not perm(st, "Temple Garden").tapped, "choque pago entra desvirado")


@test("Fetch NAO acha terreno sem o subtipo (Command Tower / Yavimaya nao viram Forest na biblioteca)")
def _():
    st = mk(hand=["Windswept Heath"], bf=["Yavimaya, Cradle of Growth"], lib=["Command Tower", "Exotic Orchard", "City of Brass"])
    T.play_land_phase(st)
    check(perm(st, "Windswept Heath") is not None, "sem alvo a fetch fica em campo")
    check(st.m["fetch_no_target"] >= 1)


@test("Cada fetch busca so' os subtipos dela (Misty: Forest/Island; Verdant: Swamp/Forest; Foothills: Mountain/Forest)")
def _():
    lib = ["Hallowed Fountain", "Overgrown Tomb", "Steam Vents", "Watery Grave", "Stomping Ground", "Temple Garden", "Command Tower"]
    st = mk(bf=["Misty Rainforest"], lib=list(lib))
    got = set(T.fetch_targets(st, perm(st, "Misty Rainforest")))
    check(got == {"Hallowed Fountain", "Overgrown Tomb", "Steam Vents", "Watery Grave", "Stomping Ground", "Temple Garden"}, str(got))
    st = mk(bf=["Verdant Catacombs"], lib=list(lib))
    got = set(T.fetch_targets(st, perm(st, "Verdant Catacombs")))
    check(got == {"Overgrown Tomb", "Watery Grave", "Stomping Ground", "Temple Garden"}, str(got))
    st = mk(bf=["Wooded Foothills"], lib=list(lib))
    got = set(T.fetch_targets(st, perm(st, "Wooded Foothills")))
    check(got == {"Steam Vents", "Stomping Ground", "Overgrown Tomb", "Temple Garden"}, str(got))
    st = mk(bf=["Windswept Heath"], lib=list(lib))
    got = set(T.fetch_targets(st, perm(st, "Windswept Heath")))
    check(got == {"Hallowed Fountain", "Overgrown Tomb", "Stomping Ground", "Temple Garden"}, str(got))


@test("Fetch devolvida do cemiterio so' com o emblema da Wrenn: terreno do cemiterio e' jogavel")
def _():
    st = mk(gy=["Misty Rainforest"], lib=["Steam Vents"])
    T.play_land_phase(st)
    check("Misty Rainforest" in st.graveyard, "sem emblema nao joga do cemiterio")
    st = mk(gy=["Misty Rainforest"], lib=["Steam Vents"])
    st.emblems.append("wrenn")
    T.play_land_phase(st)
    check(perm(st, "Steam Vents") is not None, "com o emblema, joga a Misty do cemiterio e busca")


# ---------------- mana ----------------
@test("Sol Ring: 2 de {C}; Arcane Signet/Command Tower: qualquer cor (identidade WUBRG)")
def _():
    st = mk(bf=["Sol Ring"])
    check(T.available_mana(st) == 2)
    check(T.can_pay(st, 2, ()), "2 genericos")
    check(not T.can_pay(st, 0, pips("G")), "Sol Ring so' faz incolor")
    st = mk(bf=["Arcane Signet", "Command Tower"])
    check(T.can_pay(st, 0, pips("W", "B")), "Signet e Tower pagam W e B")


@test("Birds / Noble Hierarch / Ignoble Hierarch: cores certas, e nao com doenca de invocacao")
def _():
    st = mk(bf=["Birds of Paradise"])
    check(T.can_pay(st, 0, pips("R")))
    st = mk(bf=["Noble Hierarch"])
    check(T.can_pay(st, 0, pips("W")) and T.can_pay(st, 0, pips("U")) and not T.can_pay(st, 0, pips("B")), "Noble: G W U")
    st = mk(bf=["Ignoble Hierarch"])
    check(T.can_pay(st, 0, pips("B")) and T.can_pay(st, 0, pips("R")) and not T.can_pay(st, 0, pips("W")), "Ignoble: B R G")
    st = mk(bf=[("Birds of Paradise", {"sick": True})])
    check(not T.can_pay(st, 0, pips("R")), "criatura com doenca de invocacao nao toca")


@test("Bloom Tender / Faeburrow Elder: um mana de CADA cor entre os permanentes; Elder tem vigilancia e P/T = cores")
def _():
    st = mk(bf=["Bloom Tender", "Birds of Paradise", "Noble Hierarch"])
    # cores entre permanentes: Bloom Tender (G), Birds (G), Noble (G): so' G
    check(T.colors_among(st) == ["G"], str(T.colors_among(st)))
    st = mk(bf=["Bloom Tender", "Oko, Thief of Crowns", "Dihada, Binder of Wills"])
    check(set(T.colors_among(st)) == {"G", "U", "R", "W", "B"}, str(T.colors_among(st)))
    check(T.available_mana(st) == 5, f"Bloom Tender com 5 cores = 5 mana: {T.available_mana(st)}")
    st = mk(bf=["Faeburrow Elder", "Oko, Thief of Crowns"])
    e = perm(st, "Faeburrow Elder")
    check(T.power(st, e) == 3 and T.toughness(st, e) == 3, f"G,W,U = 3 cores: {T.power(st, e)}/{T.toughness(st, e)}")
    check(T.can_attack(st, e) and "vigilance" in e.card.tags)


@test("Chromatic Orrery: {C}x5, gasta como qualquer cor; Leyline Immersion: Tam toca por 5 mana de qualquer cor (so' magia)")
def _():
    st = mk(bf=["Chromatic Orrery"])
    check(T.available_mana(st) == 5)
    check(T.can_pay(st, 0, pips("W", "U", "B", "R", "G")), "Orrery gasta como qualquer cor")
    st = mk(bf=["Tam, the Possibility", "Leyline Immersion"])
    im = perm(st, "Leyline Immersion")
    im.attached_to = perm(st, "Tam, the Possibility").uid
    check(T.can_pay(st, 0, pips("W", "U", "B", "R", "G")), "Tam + Immersion paga 5 cores de magia")
    check(not T.can_pay(st, 0, pips("W", "U", "B", "R", "G"), T.CTX_ABILITY), "o mana da Immersion so' vale pra magia, nao pra habilidade")


@test("Fellwar Stone / Exotic Orchard: so' cores que um terreno de OPONENTE produz")
def _():
    st = mk(bf=["Fellwar Stone", "Exotic Orchard"])
    check(T.available_mana(st) == 0, "sem terreno de oponente nao produz nada")
    st.opps[0].land_colors = ["R"]
    check(T.can_pay(st, 0, pips("R", "R")), "R apos oponente ter terreno que produz R")
    check(not T.can_pay(st, 0, pips("G")), "G nao")


@test("City of Brass: 1 de dano ao virar; Starting Town: 1 de vida so' pelo mana colorido")
def _():
    st = mk(bf=["City of Brass"], life=30)
    T.pay_mana(st, 0, pips("W"))
    check(st.life == 29, f"City: {st.life}")
    st = mk(bf=["Starting Town"], life=30)
    T.pay_mana(st, 1, ())
    check(st.life == 30, "Town incolor nao custa vida")
    st = mk(bf=["Starting Town"], life=30)
    T.pay_mana(st, 0, pips("U"))
    check(st.life == 29, "Town colorido custa 1")


@test("Staff of Compleation: 2 de vida por mana de qualquer cor")
def _():
    st = mk(bf=["Staff of Compleation"], life=30)
    T.pay_mana(st, 0, pips("B"))
    check(st.life == 28 and perm(st, "Staff of Compleation").tapped, f"{st.life}")


@test("Treasure: sacrifica pra 1 mana de qualquer cor")
def _():
    st = mk(bf=["Treasure Token"])
    T.pay_mana(st, 0, pips("U"))
    check(perm(st, "Treasure Token") is None)


@test("Filtros: Fire-Lit Thicket paga {R}{G} com 1 mana de G de outro terreno; paga RR com G; Twilight Mire BB; nunca fabrica cor que nao filtra")
def _():
    st = mk(bf=["Fire-Lit Thicket", "Breeding Pool"])
    check(T.can_pay(st, 0, pips("R", "G")), "Pool(G)->Thicket {R}{G}")
    check(T.can_pay(st, 0, pips("R", "R")), "Pool(G)->Thicket {R}{R}")
    check(not T.can_pay(st, 0, pips("U", "R")), "Pool U nao e' R/G: Thicket nao filtra U; Pool vira U e Thicket ficaria so' {C}: UC")
    st = mk(bf=["Twilight Mire", "Overgrown Tomb"])
    check(T.can_pay(st, 0, pips("B", "B")), "Tomb(B) -> Mire BB")
    st = mk(bf=["Wooded Bastion", "Temple Garden"])
    check(T.can_pay(st, 0, pips("W", "W")), "Garden(W)->Bastion WW")
    st = mk(bf=["Flooded Grove", "Breeding Pool"])
    check(T.can_pay(st, 0, pips("U", "U")), "Pool(U)->Grove UU")


@test("Mossfire Valley ({1},{T}: RG) e Overflowing Basin ({1},{T}: GU): precisam de 1 mana de entrada")
def _():
    st = mk(bf=["Mossfire Valley", "Sol Ring"])
    check(T.can_pay(st, 0, pips("R", "G")), "Sol Ring(C)->Valley RG")
    st = mk(bf=["Mossfire Valley"])
    check(not T.can_pay(st, 0, pips("R", "G")), "sozinha nao paga")
    st = mk(bf=["Overflowing Basin", "Sol Ring"])
    check(T.can_pay(st, 0, pips("G", "U")))


@test("Great Hall of the Citadel: {1},{T}: 2 manas de qualquer cor SO' pra magia LENDARIA (Tam sim, Sol Ring nao)")
def _():
    st = mk(bf=["Great Hall of the Citadel", "Sol Ring"])
    tam = T.ctx_for("Tam, the Possibility")
    g, p = T.effective_cost(st, "Tam, the Possibility")
    check(T.can_pay(st, g, p, tam), "Tam (lendaria): Hall converte")
    check(not T.can_pay(st, 0, pips("G", "U"), T.ctx_for("Birds of Paradise")), "magia nao lendaria nao usa o mana restrito")


@test("Plaza of Heroes: cor entre permanentes lendarios (Tam: G/U) pra qualquer magia; qualquer cor so' pra lendaria; incolor sempre")
def _():
    st = mk(bf=["Plaza of Heroes", "Tam, the Possibility"])
    check(T.can_pay(st, 0, pips("G"), T.CTX_SPELL), "G (cor do Tam) pra qualquer magia")
    check(not T.can_pay(st, 0, pips("R"), T.CTX_SPELL), "R so' pra lendaria")
    check(T.can_pay(st, 0, pips("R"), T.ctx_for("Dihada, Binder of Wills")), "R pra magia lendaria")
    st = mk(bf=["Plaza of Heroes"])
    check(T.can_pay(st, 1, ()), "incolor")


@test("Baxter Building: {4},{T}: 4 manas de qualquer cor (so' converte; custa 4 de entrada)")
def _():
    st = mk(bf=["Baxter Building"])
    st.pool = {"C": 4}
    check(T.can_pay(st, 0, pips("W", "U", "B", "R")), "Baxter fixa as cores")
    st = mk(bf=["Baxter Building"])
    st.pool = {"C": 3}
    check(not T.can_pay(st, 0, pips("W", "U", "B")), "com 3 de entrada nao converte")


@test("Wrenn: terrenos tocam por qualquer cor; The World Tree: so' com 6+ terrenos")
def _():
    st = mk(bf=["Wrenn and Realmbreaker", "Boseiju, Who Endures", "Baxter Building"])
    check(T.can_pay(st, 0, pips("W", "U")), "Wrenn da' qualquer cor aos terrenos")
    st = mk(bf=["The World Tree", "Baxter Building", "Boseiju, Who Endures"])
    check(not T.can_pay(st, 0, pips("W")), "com < 6 terrenos so' G")
    st = mk(bf=["The World Tree", "Baxter Building", "Boseiju, Who Endures", "Great Hall of the Citadel", "Plaza of Heroes", "Exotic Orchard"])
    check(T.can_pay(st, 0, pips("W", "U", "B")), "6+ terrenos: qualquer cor")


@test("Yavimaya: todo terreno vira Forest (toca G) e Nissa conta todos como Forest")
def _():
    st = mk(bf=["Yavimaya, Cradle of Growth", "Baxter Building", "Plaza of Heroes"])
    check(T.can_pay(st, 0, pips("G", "G", "G")), "3 terrenos tocam G")
    check(T.forest_count(st) == 3)


@test("Ciclo {3} dos triomes: descarta e compra 1 (so' com mana sobrando)")
def _():
    st = mk(hand=["Zagoth Triome"], bf=["Sol Ring", "Baxter Building", "Boseiju, Who Endures", "Great Hall of the Citadel", "Plaza of Heroes", "Exotic Orchard", "City of Brass"], phase="main2")
    st.lands_played_this_turn = 1
    n = len(st.hand)
    check(T.act_cycle_triome(st), "devia ciclar")
    check("Zagoth Triome" in st.graveyard and len(st.hand) == n, "descartou o triome e comprou 1")


# ---------------- custos ----------------
@test("Tam: magia de planeswalker custa {1} a menos (so' o generico); imposto do comandante +2 por conjuracao; reducao nunca abaixo de 0")
def _():
    st = mk(bf=["Tam, the Possibility"])
    g, p = T.effective_cost(st, "Teferi, Hero of Dominaria")
    check(g == 2 and len(p) == 2, f"{g} {p}")
    g, p = T.effective_cost(st, "Aminatou, the Fateshifter")
    check(g == 0 and len(p) == 3, "Aminatou {W}{U}{B}: generico ja' e' 0")
    g, p = T.effective_cost(st, "Sol Ring")
    check(g == 1, "nao-planeswalker nao reduz")
    st = mk(cz=True)
    check(T.effective_cost(st, "Tam, the Possibility")[0] == 1)
    st.commander_cast_count = 2
    check(T.effective_cost(st, "Tam, the Possibility")[0] == 5, "imposto 2 por conjuracao anterior: 1 + 4")


@test("Nissa/Vraska (Compleated): {G/P}/{B/P} paga 2 de vida, entra com 2 contadores a menos por pip pago")
def _():
    st = mk(hand=["Vraska, Betrayal's Sting"], bf=["Sol Ring", "Chromatic Orrery"], life=40)
    # custo {4}{B}{B/P}; sem Tam: 5 genericos + B + B/P. Orrery+Sol Ring = 7 mana: paga tudo em mana
    check(T.cast_card(st, "Vraska, Betrayal's Sting"))
    check(loy(st, "Vraska, Betrayal's Sting") == 6, str(loy(st, "Vraska, Betrayal's Sting")))
    st = mk(hand=["Vraska, Betrayal's Sting"], bf=["Chromatic Orrery"], life=40)
    # so' 5 mana: {4}{B} + vida por {B/P}
    check(T.cast_card(st, "Vraska, Betrayal's Sting"), "paga o ultimo pip com vida")
    check(st.life == 38 and loy(st, "Vraska, Betrayal's Sting") == 4, "vida %s lealdade %s" % (st.life, loy(st, "Vraska, Betrayal's Sting")))


@test("Blasphemous Act: custa {1} a menos por criatura em campo (de qualquer jogador)")
def _():
    st = mk(res=True, bf=["Birds of Paradise", "Noble Hierarch"])
    add_opp_creature(st, 1); add_opp_creature(st, 2)
    g, p = T.effective_cost(st, "Blasphemous Act")
    check(g == 8 - 4, f"{g}")


@test("Oath of Nissa: gasta como qualquer cor SO' pra planeswalker; Oath of Nissa ETB: olha 3, pega criatura/terreno/PW, resto no fundo")
def _():
    st = mk(bf=["Oath of Nissa", "Sol Ring"])
    check(T.can_pay(st, 0, pips("W", "W"), T.ctx_for("Garruk Wildspeaker")), "Sol Ring (C) paga W via Oath of Nissa (so' pra planeswalker)")
    check(not T.can_pay(st, 0, pips("W", "W"), T.ctx_for("Sol Ring")), "mas nao pra outra magia")
    st = mk(bf=["Oath of Nissa", "Arcane Signet", "Sol Ring"])
    check(T.can_pay(st, 0, pips("G"), T.ctx_for("Garruk Wildspeaker")))
    st = mk(hand=["Oath of Nissa"], lib=["Ajani Unrelenting", "Sol Ring", "Command Tower", "Overgrown Tomb"] + filler_library({"Ajani Unrelenting", "Sol Ring", "Command Tower", "Overgrown Tomb", "Oath of Nissa"}), bf=["Sol Ring"])
    T.apply_etb(st, T.mk_perm(st, "Oath of Nissa"), True)
    check("Ajani Unrelenting" in st.hand, "pega o planeswalker dos 3 de cima")
    check(st.library[-2:] == ["Sol Ring", "Command Tower"] or set(st.library[-2:]) == {"Sol Ring", "Command Tower"} or {"Sol Ring", "Command Tower"} <= set(st.library[-2:]), "o resto vai pro fundo: " + str(st.library[-3:]))

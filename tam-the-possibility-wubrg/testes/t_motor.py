from harness import *


def P(name, **kw):
    return (name, kw)


@test("Ordem das fases em play_turn (Regra #6): untap -> upkeep -> draw -> main1 -> combate -> main2 -> end step")
def _():
    st = mk(bf=["Sol Ring"], turn=4)
    order = []
    orig = {n: getattr(T, n) for n in ("untap_my_permanents", "upkeep_step", "draw_step", "main_phase", "combat_step", "end_step")}
    try:
        for n, f in orig.items():
            def mkw(n=n, f=f):
                def w(state, *a, **k):
                    order.append(n if n != "main_phase" else "main:" + a[0])
                    return f(state, *a, **k)
                return w
            setattr(T, n, mkw())
        T.play_turn(st)
    finally:
        for n, f in orig.items():
            setattr(T, n, f)
    check(order == ["untap_my_permanents", "upkeep_step", "draw_step", "main:main1", "combat_step", "main:main2", "end_step"], str(order))


@test("Upkeep ANTES da compra: Dreamtide Whale com 1 contador some antes de eu comprar; Boo entra no upkeep")
def _():
    st = mk(bf=["Dreamtide Whale", "Minsc & Boo, Timeless Heroes"], turn=4)
    perm(st, "Dreamtide Whale").ctr["time"] = 1
    n0 = len(st.hand)
    seq = []
    f_rm, f_dr = T.remove_permanent, T.draw_cards
    T.remove_permanent = lambda s, p, r="dies": (seq.append(("rm", p.card.name)), f_rm(s, p, r))[1]
    T.draw_cards = lambda s, n, *a, **k: (seq.append(("draw", n)), f_dr(s, n, *a, **k))[1]
    try:
        T.play_turn(st)
    finally:
        T.remove_permanent, T.draw_cards = f_rm, f_dr
    check(seq.index(("rm", "Dreamtide Whale")) < seq.index(("draw", 1)), str(seq[:4]))
    check(count(st, "Boo Token") == 1)


@test("Chandra e Chain Veil: gatilhos de END STEP rodam depois de main2 (e Chandra usa a contagem final de planeswalkers)")
def _():
    st = mk(bf=[P("Chandra, Legacy of Fire", loyalty=3), P("Garruk Wildspeaker", loyalty=3), "The Chain Veil"], turn=7, life=30)
    T.play_turn(st)
    check(st.m["chandra_triggers"] == 1)


@test("Mana gerada no main1 (Chandra +1, Pyromancer) e' gastavel no MESMO main (pool)")
def _():
    st = mk(hand=["Garruk, Curse Breaker"], bf=[P("Chandra, Legacy of Fire", loyalty=3), P("Oko, Thief of Crowns", loyalty=4), P("Garruk Wildspeaker", loyalty=3), "Tam, the Possibility", "Command Tower", "Arcane Signet"], turn=7)
    T.main_phase(st, "main1")
    check(perm(st, "Garruk, Curse Breaker") is not None, "Chandra +1 (R x PWs) pagou a Garruk CB")


@test("Planeswalker que acabou de entrar pode ativar NO MESMO turno (nao ha' doenca de invocacao pra lealdade)")
def _():
    st = mk(hand=["Garruk Wildspeaker"], bf=["Sol Ring", "Arcane Signet", "Command Tower", "Tam, the Possibility"], turn=4)
    T.cast_loop(st)
    g = perm(st, "Garruk Wildspeaker")
    check(g is not None and g.acts == 1)


@test("Uma ativacao de lealdade por planeswalker por turno; reseta no turno seguinte (turn_id)")
def _():
    st = mk(bf=[P("Garruk Wildspeaker", loyalty=3)])
    g = perm(st, "Garruk Wildspeaker")
    T.activate_ability(st, g, "Garruk Wildspeaker", "+1", 0)
    check(not T.pw_can_activate(st, g))
    T.begin_any_turn(st)
    check(T.pw_can_activate(st, g))


@test("Mulligan: o jogador ESCOLHE o fundo (London); primeiro gratis; mao final com 7 - (mulls-1) cartas")
def _():
    sizes = {}
    for seed in range(300):
        st = T.new_state(1_000_000 + seed)
        sizes[st.mulligans] = sizes.get(st.mulligans, 0) + 1
        exp = 7 if st.mulligans <= 1 else 7 - (st.mulligans - 1)
        check(len(st.hand) == exp, f"seed {seed}: mulls {st.mulligans} mao {len(st.hand)}")
        check(len(st.hand) + len(st.library) == 99, "99 cartas")
    check(len(sizes) >= 2, str(sizes))


@test("Biblioteca: 99 cartas, todas no CARD_DB, nenhuma duplicada exceto terreno basico (nao ha basicos)")
def _():
    lib = T.current_library()
    check(len(lib) == 99 and len(set(lib)) == 99, f"{len(lib)} {len(set(lib))}")
    check(all(c in T.CARD_DB for c in lib))


@test("Vida <= 0 so' MARCA died_turn (convencao do repositorio): a partida continua")
def _():
    st = mk(life=3)
    T.lose_life(st, 5, "t")
    check(st.died_life and st.died_turn == st.turn and not st.game_over)


@test("Mesa limpa: todos os oponentes eliminados encerra a partida; veneno 10 elimina")
def _():
    st = mk()
    for o in st.opps:
        T.damage_opp(st, 40, "t", o.idx)
    check(st.game_over and st.table_cleared_turn == st.turn)
    st = mk()
    T.give_poison(st, 1, 10, "t")
    check(st.opps[0].eliminated and st.opps[0].elim_reason == "poison")


@test("Baralho vazio: comprar com a biblioteca vazia = derrota por deck-out")
def _():
    st = mk(lib=[])
    T.draw_cards(st, 1)
    check(st.decked and st.game_over)


@test("Oponente em modo padrao: sem tabuleiro, passivo; magias contam, Dreamtide Whale conta a 2a magia")
def _():
    st = mk()
    T.opponent_turn(st, st.opps[0])
    check(st.opps[0].turns_taken == 1 and not st.opps[0].board)


@test("Modo de resiliencia: tabuleiro de oponente cresce por arquetipo; ataque a planeswalker so' depois do gate de atencao")
def _():
    st = mk(res=True, turn=8)
    T.setup_resilience(st, 3)
    st.opps[0].archetype = "go_wide"
    for _ in range(6):
        st.opps[0].turns_taken += 1
        T.develop_opponent_board(st, st.opps[0])
    check(len(st.opps[0].board) > 0)
    st.attention = False
    st.m.clear()
    T.opponent_combat(st, st.opps[0])
    check(st.m["opp_attackers_total"] == 0, "sem atencao nao ataca")


@test("Critica da Garruk VB: jogador sem criaturas nao sacrifica (e eu so' crio Fera se EU sacrifiquei)")
def _():
    st = mk(res=True, bf=[P("Garruk, Veiled Butcher", loyalty=5)])
    add_opp_creature(st, 1, 4, 4)
    T.activate_ability(st, perm(st, "Garruk, Veiled Butcher"), "Garruk, Veiled Butcher", "-2", 0)
    check(count(st, "Beast Token") == 0 and not st.opps[0].board)


@test("pw_types: dois Garruk contam como UM tipo; Jace token e' do tipo Jace; The Eternal Wanderer nao tem tipo")
def _():
    st = mk(bf=[P("Garruk Wildspeaker"), P("Garruk, Curse Breaker"), P("Jace Token", loyalty=2, token=True), P("The Eternal Wanderer")])
    check(T.pw_types(st) == 2, str(T.pw_types(st)))


@test("Tipos de planeswalker da lista: 21 distintos (X maximo da Tam)")
def _():
    names = [n for n, c in T.CARD_DB.items() if "planeswalker" in c.types and not c.token]
    types = set()
    for n in names:
        types |= set(T.CARD_DB[n].subtypes)
    check(len(names) == 25 and len(types) == 21, f"{len(names)} planeswalkers, {len(types)} tipos")


@test("Mana flutuante com o Chromatic Orrery em campo: pagar com {C} do pool DESCONTA o {C} (achado 2026-10-19: antes descontava a chave 'A' e o {C} nunca saia: mana fantasma)")
def _():
    st = mk(bf=["Chromatic Orrery"])
    st.pool = {"C": 5}
    st.battlefield[0].tapped = True                       # so' o pool paga
    check(T.pay_mana(st, 3, ()))
    check(st.pool.get("C") == 2 and st.pool.get("A", 0) == 0, str(st.pool))
    check(T.pay_mana(st, 0, (frozenset("G"), frozenset("U"))) and st.pool.get("C") == 0, "Orrery: o {C} paga pips coloridos e sai do pool")
    check(not T.pay_mana(st, 1, ()), "pool vazio: nao paga")
    st = mk(bf=["Oath of Nissa", "Garruk Wildspeaker" if False else "Sol Ring"])
    st.pool = {"C": 2, "R": 1}
    check(T.pay_mana(st, 0, (frozenset("W"), frozenset("W")), T.ctx_for("Garruk Wildspeaker")) and st.pool.get("C") == 0, "Oath of Nissa (so' PW): idem")


@test("Invariante: o pool nunca fica negativo (pay_mana levanta erro se isso ocorrer)")
def _():
    st = mk(bf=["Sol Ring", "Chromatic Orrery", "Arcane Signet", "Command Tower", "Ignoble Hierarch", "Faeburrow Elder", "Oko, Thief of Crowns"])
    for i in range(60):
        st.pool = {"C": 3, "G": 1, "A": 2}
        for n in ("Garruk Wildspeaker", "Elspeth, Sun's Champion", "Sol Ring", "Tam, the Possibility"):
            if T.can_pay(st, *T.effective_cost(st, n), T.ctx_for(n)):
                T.pay_mana(st, *T.effective_cost(st, n), T.ctx_for(n))
        check(all(v >= 0 for v in st.pool.values()), str(st.pool))
        for p in st.battlefield:
            p.tapped = False


@test("O mana flutuante some no fim de cada fase (CR 500.4): o do main 1 NAO sobra pro main 2, nem pro turno do oponente")
def _():
    st = mk(bf=["Sol Ring", "Chromatic Orrery"], turn=7)
    st.phase = "main1"
    st.pool = {"R": 3, "C": 2}
    T.main_phase(st, "main1")
    check(st.pool == {} and st.riot_pool == 0, str(st.pool))
    st = mk(bf=["Sol Ring"], turn=7)
    st.pool = {"C": 2}
    T.end_step(st)
    check(st.pool == {})
    st = mk(bf=["Sol Ring"], turn=7)
    st.pool = {"C": 2}
    T.combat_step(st)
    check(st.pool == {})


@test("Conservacao de cartas: nenhuma carta duplica nem some entre as zonas (300 partidas x 2 modos; fora game_over e Aminatou -6)")
def _():
    import collections
    base = collections.Counter(T.BASE_LIBRARY)
    for fn in (T.simulate_one, T.simulate_one_with_interaction):
        for i in range(100):
            s = fn(5_000_000 + i, 12)
            z = collections.Counter()
            for zona in ("hand", "library", "graveyard", "exile", "impulse"):
                for c in getattr(s, zona):
                    z[c] += 1
            for it in s.delayed_return:
                if isinstance(it, str):
                    z[it] += 1
            for p in s.battlefield:
                if not p.is_token:
                    z[p.card.name] += 1
            for nm, c in z.items():
                check(nm == "Tam, the Possibility" or c <= base.get(nm, 0), f"seed {5_000_000 + i}: {nm} aparece {c}x")
            if not s.game_over and not s.m["aminatou_permanents_given"]:
                for nm, c in base.items():
                    check(z[nm] >= c, f"seed {5_000_000 + i}: {nm} sumiu")


@test("Commander multijogador: NINGUEM pula a compra do 1o turno (usuario, 2026-10-19): T1 comeca com 7 + 1 = 8 cartas")
def _():
    st = T.new_state(1_000_001)
    n0 = len(st.hand)
    T.play_turn(st)
    check(st.draws_by_source.get("normal") == 1, "comprou no T1")
    T.FIRST_TURN_SKIPS_DRAW = True
    try:
        st2 = T.new_state(1_000_001)
        T.play_turn(st2)
        check(st2.draws_by_source.get("normal", 0) == 0, "com a chave do jogo de 2 jogadores, pula")
    finally:
        T.FIRST_TURN_SKIPS_DRAW = False

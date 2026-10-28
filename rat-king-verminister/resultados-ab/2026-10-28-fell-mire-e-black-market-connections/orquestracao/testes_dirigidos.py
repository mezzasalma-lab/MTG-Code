"""Testes dirigidos da Rodada 4 do Rat King (2026-10-28): cada teste confere o COMPORTAMENTO que a mudanca promete, com a chave ligada E com ela desligada (caminho antigo).
  FM1-3   Fell the Profane // Fell Mire como TERRENO: jogado so' quando nao ha outro terreno na mao e ha menos de FELL_MIRE_MAX_LANDS_IN_PLAY terrenos em campo
  FM4-6   "As this land enters, you may pay 3 life. If you don't, it enters tapped": paga so' se (ensaio a seco) rende mais mana no turno e a vida depois fica >= piso
  FM7     {T}: Add {B}; so' e' Swamp sob Urborg (Cabal Coffers/Crypt Ghast/Castle Locthwain leem isso)
  FM8     should_keep conta a MDFC como terreno (3 terrenos, ou 2 + abertura boa)
  FM9     a FACE DE FEITICO continua existindo (conta como interacao); ruling 2024-06-07: fora do campo a carta nao e' terreno
  FM10    o ensaio a seco nao muta o estado nem o RNG global
  FM11    uma MDFC = uma carta: em partidas inteiras nunca aparece em campo E em outra zona
  BM1-2   Black Market Connections: sem lifegain so' o modo 1 (Treasure, -1); com lifegain os 3 (-6)
  BM3     cada permanente de LIFEGAIN_ENGINES liga os modos 2/3; Gray Merchant (so' ETB) nao
  BM4     LIFEGAIN_ENGINES == permanentes da lista com ganho de vida REPETIVEL no oraculo ao vivo (lido do JSON arquivado, nao de memoria)
  BM5     nunca escolhe um modo que leve a vida a 0 ou menos (politica MINHA: o oraculo diz "You lose N life", efeito, nao custo; a regra permitiria)
  BM6     chave desligada = o caminho antigo (os 3 modos, sempre)
  BM7     Mercenary do modo 3 recebe o Thornbite Staff (changeling = Shaman); sem o modo 3 nao ha ficha
  TF1-2   terreno virado primeiro (T1/T2): o ensaio mede o MANA GASTO e por isso ve o comandante (que nao esta na mao): T2 com Bojuka Bog + Swamp na mao joga o Swamp e conjura o Rat King
  BM8     partidas inteiras: modo 2/3 so' acontecem com lifegain em campo (instrumentado no passo do BMC, nao so' no estado final)
Uso: python3 testes_dirigidos.py config.json"""
import contextlib, copy, dataclasses, json, os, random, re, sys, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
M = A.carrega(os.path.join(DECK, cfg["sim"]), "td_r4", DECK)
FELL = M.FELL_CARD
resultados = []


def teste(nome):
    def deco(f):
        try:
            f()
            resultados.append((nome, True, ""))
        except Exception:
            resultados.append((nome, False, traceback.format_exc(limit=4)))
        return f
    return deco


@contextlib.contextmanager
def chaves(**kw):
    """Liga/desliga chaves do modulo; todas as demais ficam como estao no arquivo vivo."""
    antigo = {k: getattr(M, k) for k in kw}
    for k, v in kw.items():
        setattr(M, k, v)
    try:
        yield
    finally:
        for k, v in antigo.items():
            setattr(M, k, v)


def novo(turno=5, campo=(), mao=(), swamps=0, tokens=0, treasures=0, cemiterio=(), vida=40, biblioteca=None):
    s = M.GameState()
    s.turn = turno
    s.battlefield = list(campo) + ["Swamp"] * swamps
    s.hand = list(mao)
    s.graveyard = list(cemiterio)
    s.rat_tokens, s.treasure_tokens = tokens, treasures
    s.life = vida
    s.library = list(biblioteca) if biblioteca is not None else ["Swamp"] * 30
    for n in s.battlefield:
        if M.is_creature_card(n):
            s.creature_cast_turn[n] = 1
    s.commander_in_play = M.COMMANDER in s.battlefield
    return s


# ------------------------------------------------------------------ Fell Mire
@teste("FM1 sem outro terreno na mao e com poucos terrenos em campo, a MDFC entra como terreno (Fell Mire); chave desligada: fica na mao")
def _():
    with chaves(FELL_MIRE_LAND_ENABLED=True):
        s = novo(campo=[], mao=[FELL], swamps=3)
        M.play_land(s)
        assert "Fell Mire" in s.battlefield and FELL not in s.hand and s.lands_played_this_turn == 1 and s.fell_mire_land_plays_total == 1
    with chaves(FELL_MIRE_LAND_ENABLED=False):
        s = novo(campo=[], mao=[FELL], swamps=3)
        M.play_land(s)
        assert "Fell Mire" not in s.battlefield and FELL in s.hand and s.lands_played_this_turn == 0


@teste("FM2 com outro terreno na mao, joga o terreno de verdade e guarda a MDFC (face de feitico)")
def _():
    with chaves(FELL_MIRE_LAND_ENABLED=True):
        s = novo(mao=[FELL, "Swamp"], swamps=2)
        M.play_land(s)
        assert s.battlefield.count("Swamp") == 3 and FELL in s.hand and "Fell Mire" not in s.battlefield


@teste("FM3 com FELL_MIRE_MAX_LANDS_IN_PLAY terrenos em campo a MDFC NAO vira terreno; com um a menos, vira")
def _():
    with chaves(FELL_MIRE_LAND_ENABLED=True, FELL_MIRE_MAX_LANDS_IN_PLAY=6):
        s = novo(mao=[FELL], swamps=6)
        M.play_land(s)
        assert FELL in s.hand and "Fell Mire" not in s.battlefield
        s = novo(mao=[FELL], swamps=5)
        M.play_land(s)
        assert "Fell Mire" in s.battlefield


@teste("FM4 paga os 3 de vida (entra desvirado) quando isso deixa conjurar o que a versao virada nao conjuraria: (a) comandante em campo, 2 Swamps + MDFC + Black Market Connections {2}{B}; (b) T2, 1 Swamp + MDFC, comandante na zona de comando ({1}{B})")
def _():
    with chaves(FELL_MIRE_LAND_ENABLED=True, BMC_MODES_NEED_LIFEGAIN=False):
        s = novo(campo=[M.COMMANDER], mao=[FELL, "Black Market Connections"], swamps=2, vida=40)
        M.play_land(s)
        assert s.life == 37 and s.fell_mire_paid_total == 1 and "Fell Mire" not in s.tapped_lands_this_turn, (s.life, s.tapped_lands_this_turn)
        assert M.lands_mana(s) == 3
        s = novo(campo=[], mao=[FELL], swamps=1, vida=40)
        M.play_land(s)
        assert s.life == 37 and s.fell_mire_paid_total == 1 and M.lands_mana(s) == 2, (s.life, M.lands_mana(s))
        M.main_phase(s, is_first_main=True)
        assert M.COMMANDER in s.battlefield                      # o terreno desvirado pagou o comandante no T2


@teste("FM5 nao paga quando a vida depois de pagar ficaria abaixo do piso (vida 12, piso 10): entra virado")
def _():
    with chaves(FELL_MIRE_LAND_ENABLED=True, FELL_MIRE_LIFE_FLOOR=10, BMC_MODES_NEED_LIFEGAIN=False):
        s = novo(mao=[FELL, "Black Market Connections"], swamps=2, vida=12)
        M.play_land(s)
        assert s.life == 12 and s.fell_mire_tapped_total == 1 and "Fell Mire" in s.tapped_lands_this_turn
        assert M.lands_mana(s) == 2


@teste("FM6 nao paga quando entrar desvirado nao rende nada (so' a MDFC na mao, empate no ensaio): vida intacta, entra virado")
def _():
    with chaves(FELL_MIRE_LAND_ENABLED=True):
        s = novo(mao=[FELL], swamps=3, vida=40)
        M.play_land(s)
        assert s.life == 40 and s.fell_mire_tapped_total == 1


@teste("FM7 Fell Mire rende {B} desvirado; nao e' Swamp (Castle Locthwain entra virado), mas e' Swamp sob Urborg (swamp_count)")
def _():
    s = novo(campo=["Fell Mire"], swamps=0)
    assert M.lands_mana(s) == 1 and M.swamp_count(s) == 0
    s.battlefield.append("Urborg, Tomb of Yawgmoth")
    assert M.swamp_count(s) == 2 and M.lands_mana(s) == 2
    s.tapped_lands_this_turn.add("Fell Mire")
    assert M.lands_mana(s) == 1
    with chaves(FELL_MIRE_LAND_ENABLED=True):
        s2 = novo(mao=["Castle Locthwain"], campo=["Fell Mire"])
        M.play_land(s2)
        assert "Castle Locthwain" in s2.tapped_lands_this_turn      # "unless you control a Swamp": Fell Mire nao e' Swamp


@teste("FM8 should_keep: MDFC + 2 terrenos + 4 magias = mantem (3); chave desligada = descarta; MDFC + 1 terreno + 5 magias nao mantem de jeito nenhum")
def _():
    spells = ["Skullclamp", "Ripples of Undeath", "Damnation", "Echoing Return"]
    h = [FELL, "Swamp", "Swamp"] + spells
    with chaves(FELL_MIRE_COUNTS_FOR_KEEP=True):
        assert M.should_keep(h) is True
        assert M.should_keep([FELL, "Swamp"] + spells + ["Reanimate"]) is False       # 2 terrenos contando a MDFC e nenhuma abertura boa
    with chaves(FELL_MIRE_COUNTS_FOR_KEEP=False):
        assert M.should_keep(h) is False
    with chaves(FELL_MIRE_COUNTS_FOR_KEEP=True):
        assert M.should_keep([FELL, "Swamp", "Sol Ring"] + spells) is True        # 2 terrenos contando a MDFC + abertura boa


@teste("FM9 a face de feitico segue existindo: instant {2}{B}{B} conta como interacao; no cemiterio/mao/biblioteca a carta NAO e' terreno (ruling 2024-06-07)")
def _():
    assert FELL not in M.LAND_NAMES and "Fell Mire" in M.LAND_NAMES and M.CARD_DB[FELL].ctype == "instant" and M.CARD_DB[FELL].mv == 4
    s = novo(mao=[FELL], swamps=4)
    i0 = s.interaction_spells_cast_total
    M.resolve_cast(s, FELL)
    assert s.interaction_spells_cast_total == i0 + 1 and FELL in s.graveyard


@teste("FM10 o ensaio a seco do Fell Mire nao muta o estado nem o RNG global")
def _():
    import random as _r
    s = novo(mao=[FELL, "Black Market Connections", "Rat Colony"], swamps=2, vida=40)
    antes = repr(dataclasses.asdict(s)); rng = _r.getstate()
    with chaves(FELL_MIRE_LAND_ENABLED=True):
        M._fm_dry_run_mv(s, True); M._fm_dry_run_mv(s, False)
    assert repr(dataclasses.asdict(s)) == antes and _r.getstate() == rng


@teste("FM11 partidas inteiras (3.000, modo padrao): a MDFC e' UMA carta (nunca em campo como terreno E em outra zona) e a regra de pagamento so' roda com vida >= piso + 3")
def _():
    n_land = n_pay = 0
    for sd in range(5_000_000, 5_003_000):
        r = M.simulate_one(sd, turns=8)
        zonas = ("hand", "library", "graveyard")
        fora = sum((FELL in getattr(r, z)) for z in zonas)
        dentro = 1 if "Fell Mire" in r.battlefield else 0
        assert fora + dentro <= 1, (sd, fora, dentro)
        assert r.battlefield.count("Fell Mire") <= 1
        n_land += r.fell_mire_land_plays_total; n_pay += r.fell_mire_paid_total
    assert n_land > 0 and n_pay > 0, (n_land, n_pay)               # verificacao que da' zero e' vacua


# ------------------------------------------------------------------ Black Market Connections
BMC = "Black Market Connections"


@teste("BM1 sem lifegain em campo so' o modo 1: Treasure +1, vida -1, sem compra e sem Mercenary")
def _():
    with chaves(BMC_MODES_NEED_LIFEGAIN=True):
        s = novo(campo=[BMC], swamps=3, vida=40, biblioteca=["Swamp"] * 5)
        m0, h0 = s.mercenary_tokens, len(s.hand)
        M.black_market_connections_step(s)
        assert s.life == 39 and s.treasure_tokens == 1 and len(s.hand) == h0 and s.mercenary_tokens == m0
        assert (s.bmc_mode1_total, s.bmc_mode2_total, s.bmc_mode3_total, s.bmc_modes_skipped_total) == (1, 0, 0, 2)


@teste("BM2 com Ayara em campo os 3 modos: Treasure, compra 1, Mercenary; vida -6")
def _():
    with chaves(BMC_MODES_NEED_LIFEGAIN=True):
        s = novo(campo=[BMC, "Ayara, First of Locthwain"], swamps=3, vida=40, biblioteca=["Swamp"] * 5)
        h0 = len(s.hand)
        M.black_market_connections_step(s)
        assert s.life == 34 and s.treasure_tokens == 1 and len(s.hand) == h0 + 1 and s.mercenary_tokens == 1
        assert (s.bmc_mode1_total, s.bmc_mode2_total, s.bmc_mode3_total) == (1, 1, 1)


@teste("BM3 cada permanente de LIFEGAIN_ENGINES liga os modos 2 e 3; Gray Merchant (so' ETB) e Syr Konrad (sem ganho) nao")
def _():
    with chaves(BMC_MODES_NEED_LIFEGAIN=True):
        for eng in sorted(M.LIFEGAIN_ENGINES):
            s = novo(campo=[BMC, eng], swamps=2, vida=40, biblioteca=["Swamp"] * 5)
            M.black_market_connections_step(s)
            assert (s.bmc_mode1_total, s.bmc_mode2_total, s.bmc_mode3_total) == (1, 1, 1), eng
        for nao in ("Gray Merchant of Asphodel", "Syr Konrad, the Grim", "Skullclamp"):
            s = novo(campo=[BMC, nao], swamps=2, vida=40, biblioteca=["Swamp"] * 5)
            M.black_market_connections_step(s)
            assert (s.bmc_mode1_total, s.bmc_mode2_total, s.bmc_mode3_total) == (1, 0, 0), nao


@teste("BM4 LIFEGAIN_ENGINES == permanentes da lista cujo oraculo (ao vivo, arquivado) tem ganho de vida REPETIVEL: lido do JSON, nao de memoria")
def _():
    caminho = os.path.join(AQUI, "..", "..", "2026-10-25-rodada3-spellbook-rulings-e-correcoes", "dados", "scryfall_oraculo_rulings_2026-10-25.json")
    d = json.load(open(caminho, encoding="utf-8"))
    achados = set()
    for nome, c in d.items():
        for f in c["faces"]:
            tl = f["type_line"]
            if "Instant" in tl or "Sorcery" in tl or "Land" in tl:
                continue
            for linha in f["oracle_text"].split("\n"):
                if re.search(r"you gain|gain that much|lifelink|extort", linha, re.I) and not re.match(r"(When|As) this (creature|enchantment|artifact) enters", linha):
                    achados.add(nome)
    assert achados == set(M.LIFEGAIN_ENGINES), (sorted(achados), sorted(M.LIFEGAIN_ENGINES))


@teste("BM5 nunca escolhe modo que leve a vida a 0 ou menos (politica minha): vida 4 + lifegain -> modos 1 e 2 (4->3->1), modo 3 nao; vida 1 -> nenhum modo")
def _():
    with chaves(BMC_MODES_NEED_LIFEGAIN=True):
        s = novo(campo=[BMC, "Ayara, First of Locthwain"], swamps=2, vida=4, biblioteca=["Swamp"] * 5)
        M.black_market_connections_step(s)
        assert s.life == 1 and (s.bmc_mode1_total, s.bmc_mode2_total, s.bmc_mode3_total) == (1, 1, 0)
        s = novo(campo=[BMC, "Ayara, First of Locthwain"], swamps=2, vida=1, biblioteca=["Swamp"] * 5)
        M.black_market_connections_step(s)
        assert s.life == 1 and (s.bmc_mode1_total, s.bmc_mode2_total, s.bmc_mode3_total) == (0, 0, 0)


@teste("BM6 chave desligada = o caminho antigo: os 3 modos sempre, mesmo sem lifegain e mesmo ate a vida ficar negativa")
def _():
    with chaves(BMC_MODES_NEED_LIFEGAIN=False):
        s = novo(campo=[BMC], swamps=2, vida=4, biblioteca=["Swamp"] * 5)
        M.black_market_connections_step(s)
        assert s.life == -2 and s.treasure_tokens == 1 and s.mercenary_tokens == 1 and s.bmc_triggers_total == 0


@teste("BM7 o Mercenary do modo 3 recebe o Thornbite Staff (changeling = Shaman); sem lifegain nao ha Mercenary, entao o Staff fica solto")
def _():
    with chaves(BMC_MODES_NEED_LIFEGAIN=True, THORNBITE_STAFF_ENABLED=True):
        s = novo(campo=[BMC, "Thornbite Staff", "Zulaport Cutthroat"], swamps=2, vida=40, biblioteca=["Swamp"] * 5)
        M.black_market_connections_step(s)
        assert s.staff_holder == "__mercenary__" and s.mercenary_tokens == 1
        s = novo(campo=[BMC, "Thornbite Staff"], swamps=2, vida=40, biblioteca=["Swamp"] * 5)
        M.black_market_connections_step(s)
        assert s.staff_holder is None and s.mercenary_tokens == 0


@teste("BM8 partidas inteiras (3.000): modo 2/3 so' acontecem com lifegain em campo NO MOMENTO do passo (instrumentado), e o modo 1 acontece sempre que a vida permite")
def _():
    log = []
    orig = M.black_market_connections_policy_step

    def spy(state):
        eng = M.lifegain_engine_in_play(state); v0 = state.life
        m1, m2, m3 = state.bmc_mode1_total, state.bmc_mode2_total, state.bmc_mode3_total
        orig(state)
        log.append((eng, v0, state.bmc_mode1_total - m1, state.bmc_mode2_total - m2, state.bmc_mode3_total - m3, state.life))
    M.black_market_connections_policy_step = spy
    try:
        with chaves(BMC_MODES_NEED_LIFEGAIN=True):
            for sd in range(5_000_000, 5_003_000):
                M.simulate_one(sd, turns=8)
    finally:
        M.black_market_connections_policy_step = orig
    assert len(log) > 100, len(log)                                  # vacuo se o BMC nunca disparou
    assert any(e for e, *_ in log) and any(not e for e, *_ in log)
    for eng, v0, a, b, c, v1 in log:
        assert a == (1 if v0 - 1 >= 1 else 0)
        if not eng:
            assert b == 0 and c == 0, (eng, v0, a, b, c)
        assert v1 >= 1 or v0 < 1


# ------------------------------------------------------------------ terreno virado primeiro
@teste("TF1 T2, 1 Swamp em campo, mao [Bojuka Bog (entra virado), Swamp]: com a chave o Swamp entra e o Rat King e' conjurado; sem a chave (MV da mao) joga o virado e perde o T2")
def _():
    for flag, esperado in ((True, True), (False, False)):
        with chaves(TAPPED_FIRST_COUNTS_MANA=flag, TAPPED_LAND_FIRST_ENABLED=True):
            s = novo(turno=2, campo=[], mao=["Bojuka Bog", "Swamp"], swamps=1)
            M.play_land(s)
            M.main_phase(s, is_first_main=True)
            assert (M.COMMANDER in s.battlefield) is esperado, (flag, s.battlefield)


@teste("TF2 quando nenhuma jogada depende do terreno desvirado (nada a conjurar, comandante ja' em campo) o virado continua sendo jogado primeiro")
def _():
    with chaves(TAPPED_FIRST_COUNTS_MANA=True, TAPPED_LAND_FIRST_ENABLED=True):
        s = novo(turno=2, campo=[M.COMMANDER], mao=["Bojuka Bog", "Swamp"], swamps=1)
        M.play_land(s)
        assert "Bojuka Bog" in s.battlefield and "Swamp" in s.hand


for nome, ok, tb in resultados:
    print(("PASS " if ok else "FAIL ") + nome)
    if not ok:
        print("     " + tb.strip().replace("\n", "\n     "))
print()
print(f"{sum(1 for _, ok, _ in resultados if ok)}/{len(resultados)} testes passaram")
sys.exit(0 if all(ok for _, ok, _ in resultados) else 1)

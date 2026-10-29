"""Testes dirigidos da Rodada 3 do Rat King (2026-10-25): cada teste confere o COMPORTAMENTO que a correcao promete, com a chave ligada E com ela desligada (caminho antigo).
  TM1-3  Treasure vira mana (so' depois da mana de terrenos/pedras), gastar dispara o Disappear do Rat King
  RO1    Valley Rotcaller: X = Rats que controlo + Esquilos (sem o "-1", sem filtro de "pronto")
  MA1    Marrow-Gnawer: X conta os Rats DEPOIS de sacrificar (ruling 2004-12-01)
  BA1    Big Apple: uma ficha por oponente (NUM_OPPONENTS)
  AY1-3  Ayara: ficha de Rat dispara (Squirrel e Mercenary nao), sacrifica ficha antes de carta, Plague paga tudo menos 1 com Ayara em campo
  JF1-2  Jet Medallion reduz magia preta (so' o generico); com Jet + Bontu's o piso e' a mana colorida (Rat Colony custa {B}, nao 0)
  GM1    Gray Merchant: dreno = devocao, ganho = X * oponentes
  NT1-2  Ninja Teen: nivel 1 sem pagar (3 mana vao ao nivel 3, nao 5); dreno 1 por criatura que sai
  RK1    Rat King so' reanima com 3 Rats ALEM do comandante
  SS1    Soul Stone: Harness {6}{B} + {T} da pedra (8 de mana disponivel, a pedra fica virada)
  PR1-2  Priest: sem perda de vida propria, nunca sacrifica a si mesmo
  EM1    Emeritus entra preparado (Demonic Tutor ja no turno em que entra)
  EX1-2  Extort do Crypt Ghast: paga se nao tira jogada; ganho = total perdido
  ZU1    Zulaport: a morte do proprio Zulaport tambem dispara
  DF1    Deadly Dispute / Culling the Weak nao sao conjuradas sem o que sacrificar
  TS1-6  Thornbite Staff: auto-attach no Mercenary (changeling = Shaman), Equip {4} no Marrow-Gnawer, ping {2},{T}, untap quando criatura morre, combo Marrow + Staff (R -> 2R-2)
Uso: python3 testes_dirigidos.py config.json"""
import contextlib, dataclasses, json, os, random, sys, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
M = A.carrega(os.path.join(DECK, cfg["sim"]), "td_r3", DECK)
FLAGS = list(cfg["flags_off"])
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
    """Liga/desliga chaves do modulo; todas as demais ficam como estao no arquivo vivo (ligadas)."""
    antigo = {k: getattr(M, k) for k in kw}
    for k, v in kw.items():
        setattr(M, k, v)
    try:
        yield
    finally:
        for k, v in antigo.items():
            setattr(M, k, v)


def novo(turno=5, campo=(), mao=(), swamps=0, tokens=0, squirrels=0, mercenary=0, treasures=0, cemiterio=(), biblioteca=None, vida=40):
    s = M.GameState()
    s.turn = turno
    s.battlefield = list(campo) + ["Swamp"] * swamps
    s.hand = list(mao)
    s.graveyard = list(cemiterio)
    s.rat_tokens, s.squirrel_tokens, s.mercenary_tokens, s.treasure_tokens = tokens, squirrels, mercenary, treasures
    s.life = vida
    s.library = list(biblioteca) if biblioteca is not None else ["Swamp"] * 30
    for n in s.battlefield:
        if M.is_creature_card(n):
            s.creature_cast_turn[n] = 1            # pronta (sem doenca de invocacao)
    s.commander_in_play = M.COMMANDER in s.battlefield
    return s


@teste("TM1 Treasure paga a conjuracao quando nao ha mana de terreno; as Treasures saem do campo")
def _():
    s = novo(mao=["Rat Colony"], treasures=2)
    with chaves(TREASURE_MANA_ENABLED=True):
        assert M.can_cast(s, "Rat Colony")
        M.cast_card(s, "Rat Colony")
        assert s.treasure_tokens == 0 and s.treasure_mana_used_total == 2 and s.treasures_spent_this_turn == 2, (s.treasure_tokens, s.treasure_mana_used_total)
        assert M.remaining_mana(s) == 0
    s = novo(mao=["Rat Colony"], treasures=2)
    with chaves(TREASURE_MANA_ENABLED=False):
        assert not M.can_cast(s, "Rat Colony") and s.treasure_tokens == 2        # caminho antigo: Treasure nunca era mana


@teste("TM2 a mana dos terrenos gasta primeiro: com 3 Swamps e 2 Treasures, um feitico de 2 nao toca nas Treasures")
def _():
    s = novo(mao=["Rat Colony"], swamps=3, treasures=2)
    with chaves(TREASURE_MANA_ENABLED=True, COST_REDUCTION_COLORED_FLOOR=True):
        M.cast_card(s, "Rat Colony")
        assert s.treasure_tokens == 2 and s.treasure_mana_used_total == 0
        assert M.remaining_mana(s) == 3 + 2 - 2


@teste("TM3 gastar Treasure como mana faz uma permanente sair do campo: o Disappear do Rat King cria o Rat no fim do turno")
def _():
    s = novo(campo=[M.COMMANDER], mao=["Rat Colony"], treasures=2)
    with chaves(TREASURE_MANA_ENABLED=True):
        M.cast_card(s, "Rat Colony")
        assert s.permanent_left_battlefield_this_turn
        r0 = s.rat_tokens
        M.end_step(s)
        assert s.rat_tokens == r0 + 1 and s.rat_king_counters == 1
    s = novo(campo=[M.COMMANDER], mao=["Rat Colony"], swamps=2, treasures=2)           # so' paga com terreno: nada saiu do campo, Disappear nao dispara
    with chaves(TREASURE_MANA_ENABLED=True):
        M.cast_card(s, "Rat Colony")
        assert not s.permanent_left_battlefield_this_turn
        M.end_step(s)
        assert s.rat_tokens == 0


@teste("RO1 Valley Rotcaller: X = Rats que controlo + Esquilos (3 fichas + 1 Mercenary + Ashcoat + 2 Esquilos = 7); antigo: n_rat_attackers - 1")
def _():
    for flag, esperado in ((True, 7), (False, 4)):          # antigo: Ashcoat pronta (1) + 3 fichas + 1 Mercenary = 5, menos 1
        s = novo(campo=["Valley Rotcaller", "Ashcoat of the Shadow Swarm"], tokens=3, squirrels=2, mercenary=1)
        v0 = s.life
        with chaves(ROTCALLER_EXACT_X=flag):
            M.combat_step(s)
        assert s.life - v0 == esperado, (flag, s.life - v0)


@teste("RO2 Valley Rotcaller conta Rat que ainda nao pode atacar (doente de invocacao): controlar basta")
def _():
    s = novo(campo=["Valley Rotcaller", "Ashcoat of the Shadow Swarm"])
    s.creature_cast_turn["Ashcoat of the Shadow Swarm"] = s.turn        # entrou neste turno: nao esta pronta
    v0 = s.life
    with chaves(ROTCALLER_EXACT_X=True):
        M.combat_step(s)
    assert s.life - v0 == 1, s.life - v0


@teste("MA1 Marrow-Gnawer: 4 Rats (Marrow, Rat Colony, 2 fichas) -> sacrifica 1 ficha -> X = 3 (nao 4) -> 2 - 1 + 3 = 4 fichas")
def _():
    for flag, fichas in ((True, 4), (False, 5)):
        s = novo(campo=["Marrow-Gnawer", "Rat Colony"], tokens=2)
        with chaves(MARROW_X_AFTER_SACRIFICE=flag, THORNBITE_STAFF_ENABLED=False, AYARA_TOKEN_TRIGGER=False):
            M.marrow_gnawer_activation(s)
        assert s.rat_tokens == fichas, (flag, s.rat_tokens)


@teste("MA2 Marrow-Gnawer + comandante e mais nada: nao se sacrifica (so' restaria o proprio Marrow ou o comandante)")
def _():
    s = novo(campo=["Marrow-Gnawer", M.COMMANDER])
    with chaves(MARROW_X_AFTER_SACRIFICE=True):
        M.marrow_gnawer_activation(s)
    assert "Marrow-Gnawer" in s.battlefield and s.rat_tokens == 0


@teste("BA1 Big Apple: 5 de mana -> 3 fichas (NUM_OPPONENTS) com a chave; 1 sem ela")
def _():
    for flag, n in ((True, M.NUM_OPPONENTS), (False, 1)):
        s = novo(campo=["Big Apple, 3 a.m."], swamps=6)
        with chaves(BIG_APPLE_PER_OPPONENT=flag, AYARA_TOKEN_TRIGGER=False):
            M.big_apple_activation(s)
        assert s.rat_tokens == n, (flag, s.rat_tokens)
    assert M.NUM_OPPONENTS == 3


@teste("AY1 Ayara: ficha de Rat (preta) dispara +1 de vida e +1 de dreno; Esquilo (verde) e Mercenary (incolor) nao")
def _():
    s = novo(campo=["Ayara, First of Locthwain"])
    with chaves(AYARA_TOKEN_TRIGGER=True):
        v0, d0 = s.life, s.proxy_damage_total
        M.create_rat_token(s)
        assert (s.life - v0, s.proxy_damage_total - d0) == (1, 1)
        M.create_squirrel_tokens(s, 2)
        assert (s.life - v0, s.proxy_damage_total - d0) == (1, 1)
        s.hand = []
        M.black_market_connections_step  # (o Mercenary nasce no BMC; nao dispara Ayara)
    s = novo(campo=["Ayara, First of Locthwain"])
    with chaves(AYARA_TOKEN_TRIGGER=False):
        M.create_rat_token(s)
        assert s.life == 40 and s.proxy_damage_total == 0


@teste("AY2 Ayara sacrifica FICHA de Rat antes de carta nomeada (compra 1); sem a chave sacrificava a carta")
def _():
    for flag in (True, False):
        s = novo(campo=["Ayara, First of Locthwain", "Zulaport Cutthroat"], tokens=2)
        with chaves(AYARA_SACRIFICE_TOKENS=flag, AYARA_TOKEN_TRIGGER=False):
            h0 = len(s.hand)
            M.ayara_activation(s)
        assert len(s.hand) == h0 + 1
        assert (s.rat_tokens == 1 and "Zulaport Cutthroat" in s.battlefield) if flag else (s.rat_tokens == 2 and "Zulaport Cutthroat" not in s.battlefield), (flag, s.rat_tokens, s.battlefield)


@teste("AY3 Plague of Vermin com Ayara: paga tudo menos 1 (39 fichas) e a vida VOLTA (cada ficha devolve 1); antigo: 10 fichas, vida 30")
def _():
    s = novo(campo=["Ayara, First of Locthwain"], vida=40)
    with chaves(PLAGUE_PAYS_WITH_AYARA=True, AYARA_TOKEN_TRIGGER=True):
        M.resolve_instant_sorcery(s, "Plague of Vermin")
    assert s.rat_tokens == 39 and s.life == 40 and s.combo_ayara_plague_turn == 5 and s.combo_any_turn == 5, (s.rat_tokens, s.life, s.combo_ayara_plague_turn)
    s = novo(campo=["Ayara, First of Locthwain"], vida=40)
    with chaves(PLAGUE_PAYS_WITH_AYARA=False, AYARA_TOKEN_TRIGGER=False):
        M.resolve_instant_sorcery(s, "Plague of Vermin")
    assert s.rat_tokens == 10 and s.life == 30
    s = novo(vida=40)                                           # sem Ayara a regra antiga vale
    with chaves(PLAGUE_PAYS_WITH_AYARA=True, AYARA_TOKEN_TRIGGER=True):
        M.resolve_instant_sorcery(s, "Plague of Vermin")
    assert s.rat_tokens == 10 and s.combo_ayara_plague_turn is None


@teste("JF1 Jet Medallion reduz magia PRETA (so' o generico): Deadly Dispute {1}{B} 2 -> 1; Secret Salvage {3}{B}{B} 5 -> 4; Dark Ritual {B} continua 1")
def _():
    s = novo(campo=["Jet Medallion"])
    with chaves(JET_MEDALLION_BLACK_SPELLS=True, COST_REDUCTION_COLORED_FLOOR=True):
        assert (M.effective_cost(s, "Deadly Dispute"), M.effective_cost(s, "Secret Salvage"), M.effective_cost(s, "Dark Ritual")) == (1, 4, 1)
    with chaves(JET_MEDALLION_BLACK_SPELLS=False, COST_REDUCTION_COLORED_FLOOR=False):
        assert (M.effective_cost(s, "Deadly Dispute"), M.effective_cost(s, "Secret Salvage")) == (2, 5)


@teste("JF2 piso de mana colorida: Jet + Bontu's em campo, Rat Colony {1}{B} custa 1 (nao 0); Lord Skitter {2}{B} 1; Ayara {B}{B}{B} 3")
def _():
    s = novo(campo=["Jet Medallion", "Bontu's Monument"])
    with chaves(COST_REDUCTION_COLORED_FLOOR=True):
        assert (M.effective_cost(s, "Rat Colony"), M.effective_cost(s, "Lord Skitter, Sewer King"), M.effective_cost(s, "Ayara, First of Locthwain")) == (1, 1, 3)
    with chaves(COST_REDUCTION_COLORED_FLOOR=False):
        assert M.effective_cost(s, "Rat Colony") == 0


@teste("GM1 Gray Merchant: devocao 4 (Rat King 1 + Zulaport 1 + ele 2) -> dreno 4, ganho 4 x 3 oponentes = 12")
def _():
    for flag in (True, False):
        s = novo(campo=[M.COMMANDER, "Zulaport Cutthroat"], mao=["Gray Merchant of Asphodel"])
        with chaves(GRAY_MERCHANT_ETB=flag, EXTORT_ENABLED=False):
            v0, d0 = s.life, s.proxy_damage_total
            M.resolve_cast(s, "Gray Merchant of Asphodel", free=True)
        if flag:
            assert s.life - v0 == 12 and s.proxy_damage_total - d0 == 4 and s.gray_merchant_drain_total == 4, (s.life - v0, s.proxy_damage_total - d0)
        else:
            assert s.life == v0 and s.proxy_damage_total == d0


@teste("NT1 Ninja Teen entra no nivel 1 sem pagar: 3 de mana chegam ao nivel 3 (2 + 1); antigo cobrava um nivel fantasma e parava no 1")
def _():
    s = novo(campo=["Ninja Teen"], swamps=3)
    with chaves(NINJA_TEEN_LEVELS_AND_DRAIN=True):
        M.ninja_teen_level_up(s)
    assert s.ninja_teen_level == 3 and s.mana_spent_this_turn == 3
    s = novo(campo=["Ninja Teen"], swamps=3)
    with chaves(NINJA_TEEN_LEVELS_AND_DRAIN=False):
        M.ninja_teen_level_up(s)
    assert s.ninja_teen_level == 1 and s.mana_spent_this_turn == 2


@teste("NT2 Ninja Teen nivel 1: cada criatura minha que sai do campo drena 1 (ficha sacrificada; criatura exilada pela Soul Stone)")
def _():
    s = novo(campo=["Ninja Teen"], tokens=2)
    with chaves(NINJA_TEEN_LEVELS_AND_DRAIN=True):
        d0 = s.proxy_damage_total
        M.sacrifice_any_creature(s, 2)
        assert s.proxy_damage_total - d0 == 2 and s.ninja_teen_drain_total == 2
    s = novo(campo=["Ninja Teen"], tokens=2)
    with chaves(NINJA_TEEN_LEVELS_AND_DRAIN=False):
        M.sacrifice_any_creature(s, 2)
        assert s.proxy_damage_total == 0


@teste("RK1 Rat King: comandante + 2 fichas NAO bastam pra reanimar (so' 2 Rats sacrificaveis); com 3 fichas reanima e sacrifica 3")
def _():
    for flag, reanima in ((True, False), (False, True)):
        s = novo(campo=[M.COMMANDER], tokens=2, cemiterio=["Syr Konrad, the Grim"])
        with chaves(RAT_KING_REANIMATE_COST=flag):
            M.rat_king_reanimate(s)
        assert ("Syr Konrad, the Grim" in s.battlefield) == reanima, (flag, s.battlefield)
    s = novo(campo=[M.COMMANDER], tokens=3, cemiterio=["Syr Konrad, the Grim"])
    with chaves(RAT_KING_REANIMATE_COST=True):
        M.rat_king_reanimate(s)
    assert "Syr Konrad, the Grim" in s.battlefield and s.rat_tokens == 0


@teste("SS1 Soul Stone: Harness exige 8 de mana disponivel (a pedra gasta o {T}); 7 nao bastam; depois dele a pedra nao rende mais mana no turno")
def _():
    s = novo(campo=["The Soul Stone"], swamps=6, tokens=1)         # 6 terrenos + a pedra = 7
    with chaves(SOUL_STONE_SHARED_TAP=True):
        M.try_harness_soul_stone(s)
        assert not s.soul_stone_harnessed
    s = novo(campo=["The Soul Stone"], swamps=7, tokens=1)         # 8
    with chaves(SOUL_STONE_SHARED_TAP=True):
        M.try_harness_soul_stone(s)
        assert s.soul_stone_harnessed and s.soul_stone_tapped and M.remaining_mana(s) == 0, (M.remaining_mana(s),)
    s = novo(campo=["The Soul Stone"], swamps=6, tokens=1)
    with chaves(SOUL_STONE_SHARED_TAP=False):
        M.try_harness_soul_stone(s)
        assert s.soul_stone_harnessed                              # antigo: 7 bastavam (a pedra tapava pra mana E pro Harness)


@teste("PR1 Priest of Forgotten Gods: sem perda de vida propria; antigo perdia 2")
def _():
    for flag, vida in ((True, 40), (False, 38)):
        s = novo(campo=["Priest of Forgotten Gods"], tokens=2)
        with chaves(PRIEST_EXACT=flag, AYARA_TOKEN_TRIGGER=False):
            M.priest_activation(s)
        assert s.life == vida and s.proxy_damage_total == 2, (flag, s.life)


@teste("PR2 Priest nunca sacrifica a si mesmo ('two OTHER creatures'): token + Zulaport morrem, o Priest fica; o caminho antigo sacrificava o Priest (mv igual, vem primeiro)")
def _():
    s = novo(campo=["Priest of Forgotten Gods", "Zulaport Cutthroat"], tokens=1)
    with chaves(PRIEST_EXACT=True, ZULAPORT_SELF_DEATH=False):
        M.priest_activation(s)
    assert "Priest of Forgotten Gods" in s.battlefield and "Zulaport Cutthroat" not in s.battlefield and s.rat_tokens == 0
    s = novo(campo=["Priest of Forgotten Gods", "Zulaport Cutthroat"], tokens=1)
    with chaves(PRIEST_EXACT=False, ZULAPORT_SELF_DEATH=False):
        M.priest_activation(s)
    assert "Priest of Forgotten Gods" not in s.battlefield


@teste("EM1 Emeritus entra preparado: a copia do Demonic Tutor ja' sai no turno em que ele e' conjurado (1 tutor, 2 de mana); sem a chave nao")
def _():
    for flag, tutores in ((True, 1), (False, 0)):
        s = novo(campo=[M.COMMANDER], mao=["Emeritus of Woe // Demonic Tutor"], swamps=6, biblioteca=["Rat Colony", "Swamp", "Swamp", "Swamp"])
        with chaves(EMERITUS_ENTERS_PREPARED=flag, EXTORT_ENABLED=False):
            M.main_phase(s, is_first_main=False)
        assert s.tutors_used_total == tutores, (flag, s.tutors_used_total)


@teste("EX1 Extort: Crypt Ghast em campo, conjurar paga {1} extra se nada mais seria conjurado: ganho = 3 (um por oponente), dreno proxy 1")
def _():
    s = novo(campo=["Crypt Ghast"], mao=["Rat Colony"], swamps=0)
    saved = M.remaining_mana
    try:
        M.remaining_mana = lambda st: 3 - st.mana_spent_this_turn
        with chaves(EXTORT_ENABLED=True):
            v0 = s.life
            M.cast_card(s, "Rat Colony")
            assert s.extort_paid_total == 1 and s.life - v0 == 3 and s.mana_spent_this_turn == 3, (s.extort_paid_total, s.life - v0, s.mana_spent_this_turn)
        s = novo(campo=["Crypt Ghast"], mao=["Rat Colony"])
        with chaves(EXTORT_ENABLED=False):
            M.cast_card(s, "Rat Colony")
            assert s.extort_paid_total == 0 and s.mana_spent_this_turn == 2
    finally:
        M.remaining_mana = saved


@teste("EX2 Extort nao paga se isso tira outra conjuracao que o mana de agora ainda cobre")
def _():
    s = novo(campo=["Crypt Ghast"], mao=["Rat Colony", "Piper of the Swarm"])
    saved = M.remaining_mana
    try:
        M.remaining_mana = lambda st: 4 - st.mana_spent_this_turn           # Rat Colony custa 2 -> sobram 2 = exatamente o Piper
        with chaves(EXTORT_ENABLED=True):
            M.cast_card(s, "Rat Colony")
        assert s.extort_paid_total == 0 and s.mana_spent_this_turn == 2
    finally:
        M.remaining_mana = saved


@teste("ZU1 a morte do proprio Zulaport Cutthroat tambem dispara ('this creature OR another creature you control dies')")
def _():
    for flag, v in ((True, 1), (False, 0)):
        s = novo(campo=["Zulaport Cutthroat"])
        with chaves(ZULAPORT_SELF_DEATH=flag):
            M.leave_battlefield(s, "Zulaport Cutthroat", to_graveyard=True)
        assert s.life - 40 == v and s.proxy_damage_total == v, (flag, s.life)


@teste("DF1 Deadly Dispute sem nada pra sacrificar nao e' conjurada; com Treasure ou ficha e': Culling the Weak so' vale como ritual")
def _():
    for flag, conjurou in ((True, False), (False, True)):
        s = novo(mao=["Deadly Dispute", "Culling the Weak"], swamps=6)
        with chaves(SACRIFICE_COST_NEEDS_FODDER=flag, EXTORT_ENABLED=False):
            M.main_phase(s, is_first_main=False)
        assert ("Deadly Dispute" not in s.hand) == conjurou, (flag, s.hand)
    s = novo(mao=["Deadly Dispute"], swamps=6, tokens=1)
    with chaves(SACRIFICE_COST_NEEDS_FODDER=True, EXTORT_ENABLED=False):
        M.main_phase(s, is_first_main=False)
    assert "Deadly Dispute" not in s.hand and s.rat_tokens == 0


@teste("TS1 Thornbite Staff: o Mercenary (changeling = todo tipo, inclusive Shaman) entra e o Staff se atribui sozinho, de graca")
def _():
    for flag in (True, False):
        s = novo(campo=["Thornbite Staff", "Black Market Connections"])
        with chaves(THORNBITE_STAFF_ENABLED=flag):
            M.black_market_connections_step(s)
        assert s.mercenary_tokens == 1
        assert (s.staff_holder == "__mercenary__" and s.staff_auto_attach_total == 1) if flag else (s.staff_holder is None), (flag, s.staff_holder)


@teste("TS2 Equip {4}: com o Marrow-Gnawer em campo e 4 de mana, o Staff vai pro Marrow; sem Marrow nao equipa")
def _():
    s = novo(campo=["Thornbite Staff", "Marrow-Gnawer"], swamps=4)
    with chaves(THORNBITE_STAFF_ENABLED=True):
        M.staff_equip_policy(s)
    assert s.staff_holder == "Marrow-Gnawer" and s.mana_spent_this_turn == 4 and s.staff_equips_total == 1
    s = novo(campo=["Thornbite Staff", "Rat Colony"], swamps=4)
    with chaves(THORNBITE_STAFF_ENABLED=True):
        M.staff_equip_policy(s)
    assert s.staff_holder is None and s.mana_spent_this_turn == 0


@teste("TS3 ping {2},{T}: 1 de dano proxy; o holder desvira quando QUALQUER criatura morre e pinga de novo")
def _():
    s = novo(campo=["Thornbite Staff", "Marrow-Gnawer"], swamps=4, tokens=1)
    s.staff_holder = "Marrow-Gnawer"
    with chaves(THORNBITE_STAFF_ENABLED=True, NINJA_TEEN_LEVELS_AND_DRAIN=False, AYARA_TOKEN_TRIGGER=False):
        M.staff_ping_policy(s)
        assert s.staff_pings_total == 1 and s.proxy_damage_total == 1 and "Marrow-Gnawer" in s.tapped_creatures_this_turn
        M.staff_ping_policy(s)                                   # virado: nao pinga de novo
        assert s.staff_pings_total == 1
        M.sacrifice_any_creature(s, 1)                           # uma criatura morre -> o Staff desvira o Marrow
        assert "Marrow-Gnawer" not in s.tapped_creatures_this_turn
        M.staff_ping_policy(s)
        assert s.staff_pings_total == 2 and s.proxy_damage_total >= 2


@teste("TS4 COMBO Marrow-Gnawer + Thornbite Staff: R -> 2R-2 a cada volta (4 -> 6 -> 10 -> 18 -> 34 -> 66) e para no teto de 40 Rats; combo_marrow_staff_turn marcado")
def _():
    s = novo(campo=["Marrow-Gnawer", M.COMMANDER, "Thornbite Staff"], tokens=2)
    s.staff_holder = "Marrow-Gnawer"
    with chaves(THORNBITE_STAFF_ENABLED=True, AYARA_TOKEN_TRIGGER=False, MARROW_X_AFTER_SACRIFICE=True):
        assert M.rat_count(s) == 4
        M.marrow_gnawer_activation(s)
    assert s.marrow_staff_loop_iters_total == 5 and M.rat_count(s) == 66, (s.marrow_staff_loop_iters_total, M.rat_count(s))
    assert s.combo_marrow_staff_turn == 5 and s.combo_any_turn == 5
    assert "Marrow-Gnawer" not in s.tapped_creatures_this_turn        # o Staff deixou o Marrow desvirado


@teste("TS5 sem o Staff no Marrow o Marrow-Gnawer faz UMA ativacao por turno (nao e' combo): 4 Rats -> 4 fichas")
def _():
    s = novo(campo=["Marrow-Gnawer", M.COMMANDER, "Thornbite Staff"], tokens=2)
    with chaves(THORNBITE_STAFF_ENABLED=True, AYARA_TOKEN_TRIGGER=False, MARROW_X_AFTER_SACRIFICE=True):
        M.marrow_gnawer_activation(s)
        M.marrow_gnawer_activation(s)                            # 2a chamada no mesmo turno: {T} ja' gasto
    assert s.marrow_staff_loop_iters_total == 0 and s.rat_tokens == 4 and s.combo_marrow_staff_turn is None


@teste("TS6 combo com Ayara em campo: cada ficha criada no loop dispara Ayara (dreno proxy cresce com as fichas); sem a chave THORNBITE nada disso")
def _():
    s = novo(campo=["Marrow-Gnawer", M.COMMANDER, "Thornbite Staff", "Ayara, First of Locthwain"], tokens=2)
    s.staff_holder = "Marrow-Gnawer"
    with chaves(THORNBITE_STAFF_ENABLED=True, AYARA_TOKEN_TRIGGER=True, NINJA_TEEN_LEVELS_AND_DRAIN=False):
        M.marrow_gnawer_activation(s)
    assert s.ayara_token_triggers_total == s.tokens_created_total and s.tokens_created_total > 50, (s.ayara_token_triggers_total, s.tokens_created_total)
    s = novo(campo=["Marrow-Gnawer", M.COMMANDER, "Thornbite Staff"], tokens=2)
    s.staff_holder = "Marrow-Gnawer"
    with chaves(THORNBITE_STAFF_ENABLED=False, AYARA_TOKEN_TRIGGER=False, MARROW_X_AFTER_SACRIFICE=True):
        M.marrow_gnawer_activation(s)
    assert s.marrow_staff_loop_iters_total == 0


@teste("TS7 COMBO com so' 1 Rat adicional (R=2, como no Spellbook): nao cresce, mas faz as 12 voltas (morte + entrada a cada uma) e marca o combo")
def _():
    s = novo(campo=["Marrow-Gnawer", "Thornbite Staff"], tokens=1)
    s.staff_holder = "Marrow-Gnawer"
    with chaves(THORNBITE_STAFF_ENABLED=True, AYARA_TOKEN_TRIGGER=False, MARROW_X_AFTER_SACRIFICE=True):
        d0 = s.creatures_died_this_turn
        M.marrow_gnawer_activation(s)
    assert s.marrow_staff_loop_iters_total == M.MARROW_STAFF_LOOP_MAX_ITERS == 12 and M.rat_count(s) == 2, (s.marrow_staff_loop_iters_total, M.rat_count(s))
    assert s.creatures_died_this_turn - d0 == 12 and s.combo_marrow_staff_turn == 5


@teste("BT1 Bontu's Monument: 'Whenever you cast a creature spell' dispara UMA vez por criatura conjurada da mao (antes 2x: cast_card e resolve_cast); comandante tambem")
def _():
    for flag, n in ((True, 1), (False, 2)):
        s = novo(campo=["Bontu's Monument"], mao=["Rat Colony"], swamps=8)
        with chaves(BONTU_TRIGGER_ONCE=flag, AYARA_TOKEN_TRIGGER=False, EXTORT_ENABLED=False):
            p0, v0 = s.proxy_damage_total, s.life
            M.cast_card(s, "Rat Colony")
        assert (s.proxy_damage_total - p0, s.life - v0) == (n, n), (flag, s.proxy_damage_total - p0)
        s = novo(campo=["Bontu's Monument"], mao=[], swamps=8)
        s.commander_in_play = False
        with chaves(BONTU_TRIGGER_ONCE=flag, AYARA_TOKEN_TRIGGER=False, EXTORT_ENABLED=False, THORNBITE_STAFF_ENABLED=False):
            p0 = s.proxy_damage_total
            M.main_phase(s, is_first_main=False)
        assert M.COMMANDER in s.battlefield and s.proxy_damage_total - p0 == n, (flag, s.proxy_damage_total - p0)


@teste("BT2 conjurar de graca (ripple do Thrumming Stone) tambem e' conjurar: o Bontu's dispara uma vez por copia")
def _():
    s = novo(campo=["Bontu's Monument", "Thrumming Stone"], mao=["Rat Colony"], swamps=8, biblioteca=["Rat Colony", "Swamp", "Swamp", "Swamp"])
    with chaves(BONTU_TRIGGER_ONCE=True, AYARA_TOKEN_TRIGGER=False, EXTORT_ENABLED=False):
        M.cast_card(s, "Rat Colony")
    assert s.thrumming_stone_free_casts_total == 1 and s.proxy_damage_total == 2, (s.thrumming_stone_free_casts_total, s.proxy_damage_total)


@teste("SN1 Ninja Teen nivel 3, sneak no declare blockers: paga {3}{B}, DEVOLVE um atacante (ficha de ontem), a criatura do cemiterio e' conjurada e entra; main phase nao faz mais sneak")
def _():
    s = novo(campo=["Ninja Teen"], swamps=4, tokens=1, cemiterio=["Syr Konrad, the Grim"])
    s.ninja_teen_level = 3
    with chaves(NINJA_TEEN_SNEAK_RULING=True, NINJA_TEEN_LEVELS_AND_DRAIN=True, AYARA_TOKEN_TRIGGER=False):
        M.ninja_teen_sneak(s)                                       # main phase: nao faz nada
        assert "Syr Konrad, the Grim" in s.graveyard and s.rat_tokens == 1
        M.combat_step(s)
    assert "Syr Konrad, the Grim" in s.battlefield and s.rat_tokens == 0 and s.mana_spent_this_turn == 4, (s.battlefield, s.rat_tokens, s.mana_spent_this_turn)
    assert s.sneak_casts_total == 1 and s.ninja_teen_drain_total >= 1 and s.permanent_left_battlefield_this_turn
    s = novo(campo=["Ninja Teen"], swamps=4, tokens=1, cemiterio=["Syr Konrad, the Grim"])
    s.ninja_teen_level = 3
    with chaves(NINJA_TEEN_SNEAK_RULING=False):
        M.ninja_teen_sneak(s)                                       # caminho antigo: main phase, 4 de mana, SEM devolver ninguem
    assert "Syr Konrad, the Grim" in s.battlefield and s.rat_tokens == 1


@teste("SN2 sem atacante nao bloqueado pra devolver nao ha sneak: ficha criada neste turno (doente) e comandante nao servem")
def _():
    s = novo(campo=["Ninja Teen", M.COMMANDER], swamps=4, cemiterio=["Syr Konrad, the Grim"])
    s.ninja_teen_level = 3
    s.rat_tokens = 1; s.rat_tokens_created_this_turn = 1
    with chaves(NINJA_TEEN_SNEAK_RULING=True, THORNBITE_STAFF_ENABLED=False):
        M.ninja_teen_sneak_combat(s)
    assert "Syr Konrad, the Grim" in s.graveyard and s.sneak_casts_total == 0 and s.mana_spent_this_turn == 0


@teste("SN3 o custo do sneak {3}{B} aceita reducao so' do generico: com Jet Medallion + Bontu's custa 2, com os dois e piso {B} nunca menos de 1; a conjuracao dispara o Bontu's")
def _():
    s = novo(campo=["Ninja Teen", "Jet Medallion", "Bontu's Monument"], swamps=4, tokens=1, cemiterio=["Gray Merchant of Asphodel"])
    s.ninja_teen_level = 3
    with chaves(NINJA_TEEN_SNEAK_RULING=True, BONTU_TRIGGER_ONCE=True, AYARA_TOKEN_TRIGGER=False, GRAY_MERCHANT_ETB=False, EXTORT_ENABLED=False):
        p0 = s.proxy_damage_total
        M.ninja_teen_sneak_combat(s)
    assert s.mana_spent_this_turn == 2 and s.proxy_damage_total - p0 >= 1, (s.mana_spent_this_turn, s.proxy_damage_total - p0)


for nome, ok, tb in resultados:
    print(("PASS " if ok else "FAIL ") + nome)
    if not ok:
        print("     " + tb.strip().replace("\n", "\n     "))
print()
print(f"{sum(1 for _, ok, _ in resultados if ok)}/{len(resultados)} testes passaram")
sys.exit(0 if all(ok for _, ok, _ in resultados) else 1)

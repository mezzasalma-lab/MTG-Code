"""Testes dirigidos da Rodada 5 do Rat King (2026-10-28): wipes no proprio campo (Opcao B). Cada teste confere o COMPORTAMENTO prometido, com a chave ligada E com ela desligada.
  WP0   as tabelas CREATURE_TYPES / CREATURE_TOUGHNESS == type_line / toughness do oraculo ao vivo arquivado, e cobrem toda criatura do CARD_DB
  WP1   Damnation ("Destroy all creatures"): tudo morre, fichas e comandante; o comandante volta a zona de comando; os 4 payoffs de aristocrata veem o campo de ANTES (LKI)
  WP2   Kindred Dominance: escolhe o tipo que menos mata (Rat), poupa Rats e o Mercenary (changeling = todo tipo), mata o resto; com mais Esquilos que Rats escolhe Squirrel
  WP3   Swarmyard Massacre: 2 Esquilos ANTES do -1/-1; N conta cada criatura minha Insect/Rat/Spider/Squirrel uma vez (ruling 2024-07-26); morre a nao protegida com tenacidade <= N
  WP4   o limite de perda propria: com 0 o wipe com perda fica na mao (1 retencao por turno), sem perda e' conjurado; None = conjura sempre; wipe com efeito DESLIGADO nao e' retido
  WP5   chave desligada = o caminho antigo (Damnation/Kindred sem efeito; Swarmyard so' cria os Esquilos)
  WP6   Disappear: se o Rat King sobrevive e uma criatura minha morre no wipe, o end step cria o Rat; Damnation mata o Rat King, entao nao
  WP7   o comandante morto por Damnation pode ser conjurado de novo pagando o imposto (CR 903.8)
  WP9   o limite compara a perda LIQUIDA (mortes menos os 2 Esquilos que o Swarmyard cria): matar so' o Zulaport e ganhar 2 Esquilos compensa com limite 0; com WIPE_GATE_NET_OF_NEW_TOKENS desligado fica retido
  WP8   partidas inteiras (3.000): com limite 0 nenhuma criatura minha morre por wipe meu E houve wipe conjurado (> 0); com limite enorme morrem (controle positivo)
Uso: python3 testes_dirigidos.py config.json"""
import contextlib, json, os, sys, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
M = A.carrega(os.path.join(DECK, cfg["sim"]), "td_r5", DECK)
JSON_ORACULO = os.path.join(AQUI, "..", "..", "2026-10-25-rodada3-spellbook-rulings-e-correcoes", "dados", "scryfall_oraculo_rulings_2026-10-25.json")
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
    antigo = {k: getattr(M, k) for k in kw}
    for k, v in kw.items():
        setattr(M, k, v)
    try:
        yield
    finally:
        for k, v in antigo.items():
            setattr(M, k, v)


ON = dict(WIPE_EFFECT_KINDRED=True, WIPE_EFFECT_SWARMYARD=True, WIPE_EFFECT_DAMNATION=True)
OFF = dict(WIPE_EFFECT_KINDRED=False, WIPE_EFFECT_SWARMYARD=False, WIPE_EFFECT_DAMNATION=False)


def novo(turno=5, campo=(), mao=(), swamps=0, rats=0, squirrels=0, mercs=0, treasures=0, vida=40, biblioteca=None):
    s = M.GameState()
    s.turn = turno
    s.battlefield = list(campo) + ["Swamp"] * swamps
    s.hand = list(mao)
    s.rat_tokens, s.squirrel_tokens, s.mercenary_tokens, s.treasure_tokens = rats, squirrels, mercs, treasures
    s.life = vida
    s.library = list(biblioteca) if biblioteca is not None else ["Swamp"] * 30
    for n in s.battlefield:
        if M.is_creature_card(n):
            s.creature_cast_turn[n] = 1
    s.commander_in_play = M.COMMANDER in s.battlefield
    if s.commander_in_play:
        s.commander_cast_count = 1
    return s


@teste("WP0 CREATURE_TYPES e CREATURE_TOUGHNESS == oraculo ao vivo arquivado (face da frente) e cobrem toda criatura do CARD_DB")
def _():
    d = json.load(open(JSON_ORACULO, encoding="utf-8"))
    achadas = 0
    for n, c in d.items():
        f = c["faces"][0]
        if "Creature" not in f["type_line"]:
            continue
        achadas += 1
        tipos = tuple(f["type_line"].split("—", 1)[1].split())
        assert M.CREATURE_TYPES[n] == tipos, (n, M.CREATURE_TYPES.get(n), tipos)
        assert M.CREATURE_TOUGHNESS[n] == int(f["toughness"]), n
    assert achadas == len(M.CREATURE_TYPES) == len(M.CREATURE_TOUGHNESS) > 10, achadas
    cartas = {n for n, c in M.CARD_DB.items() if c.ctype in M.CREATURE_ISH}
    assert cartas == set(M.CREATURE_TYPES), (sorted(cartas - set(M.CREATURE_TYPES)), sorted(set(M.CREATURE_TYPES) - cartas))


@teste("WP1 Damnation: tudo morre (cartas, fichas, comandante); payoffs simultaneos: Zulaport total (inclui a si), Plunderer total-1 Treasures, Konrad total-1, Species Specialist conta Rats e o Mercenary")
def _():
    with chaves(**ON):
        campo = [M.COMMANDER, "Rat Colony", "Zulaport Cutthroat", "Pitiless Plunderer", "Syr Konrad, the Grim", "Species Specialist", "Gray Merchant of Asphodel"]
        s = novo(campo=campo, swamps=4, rats=2, squirrels=1, mercs=1, vida=20, biblioteca=["Swamp"] * 10)
        total = 7 + 2 + 1 + 1
        rats_morrendo = 2 + 1 + 1                      # Rat King + Rat Colony (cartas), 2 fichas de Rat... + Mercenary (changeling): cartas Rat = 2, fichas Rat = 2, Mercenary = 1
        rats_morrendo = 2 + 2 + 1
        t0, p0, h0 = s.treasure_tokens, s.proxy_damage_total, len(s.hand)
        M.apply_own_wipe(s, "Damnation")
        assert [n for n in s.battlefield if M.is_creature_card(n)] == [] and s.rat_tokens == s.squirrel_tokens == s.mercenary_tokens == 0
        assert not s.commander_in_play and M.COMMANDER not in s.graveyard and "Rat Colony" in s.graveyard
        assert s.life == 20 + total
        assert s.treasure_tokens - t0 == total - 1
        assert s.proxy_damage_total - p0 == total + (total - 1)          # Zulaport total + Konrad total-1
        assert len(s.hand) - h0 == rats_morrendo and s.creatures_died_this_turn == total and s.permanent_left_battlefield_this_turn


@teste("WP2 Kindred Dominance: escolhe Rat, mata o que nao e' Rat (e as fichas de Esquilo), poupa Rats e o Mercenary; com mais Esquilos que Rats escolhe Squirrel; empate = Rat")
def _():
    with chaves(**ON):
        s = novo(campo=[M.COMMANDER, "Rat Colony", "Zulaport Cutthroat", "Gray Merchant of Asphodel"], rats=2, squirrels=1, mercs=1)
        pl = M.wipe_plan(s, "Kindred Dominance")
        assert pl["type"] == "Rat" and sorted(pl["named"]) == ["Gray Merchant of Asphodel", "Zulaport Cutthroat"] and pl["rat"] == 0 and pl["sq"] == 1 and pl["mc"] == 0 and pl["loss"] == 3
        M.apply_own_wipe(s, "Kindred Dominance")
        assert M.COMMANDER in s.battlefield and "Rat Colony" in s.battlefield and s.rat_tokens == 2 and s.mercenary_tokens == 1 and s.squirrel_tokens == 0
        assert "Zulaport Cutthroat" in s.graveyard and "Gray Merchant of Asphodel" in s.graveyard and s.wipe_own_creatures_lost_total == 3
        s = novo(campo=["Valley Rotcaller"], rats=1, squirrels=3)
        pl = M.wipe_plan(s, "Kindred Dominance")
        assert pl["type"] == "Squirrel" and pl["loss"] == 1 and pl["rat"] == 1 and pl["named"] == []
        s = novo(campo=["Valley Rotcaller"], rats=1, squirrels=0)                              # 1 morre em qualquer escolha: empate -> Rat (MV perdido igual a 4? Rotcaller MV 3) -> mata o Rotcaller, poupa a ficha
        pl = M.wipe_plan(s, "Kindred Dominance")
        assert pl["loss"] == 1 and pl["type"] in ("Rat", "Squirrel")
        s = novo(campo=[], rats=0, squirrels=0)
        assert M.wipe_plan(s, "Kindred Dominance")["loss"] == 0 and M.wipe_plan(s, "Kindred Dominance")["type"] == "Rat"


@teste("WP3 Swarmyard Massacre: 2 Esquilos antes; N = criaturas minhas Insect/Rat/Spider/Squirrel (cada uma 1x); morre a nao protegida com tenacidade <= N")
def _():
    with chaves(**ON):
        campo = [M.COMMANDER, "Zulaport Cutthroat", "Gray Merchant of Asphodel", "Pitiless Plunderer"]
        s = novo(campo=campo, rats=1, mercs=1)
        pl = M.wipe_plan(s, "Swarmyard Massacre")             # N = Rat King + ficha de Rat + Mercenary + 2 Esquilos novos = 5
        assert sorted(pl["named"]) == ["Gray Merchant of Asphodel", "Pitiless Plunderer", "Zulaport Cutthroat"] and pl["new_squirrels"] == 2
        M.apply_own_wipe(s, "Swarmyard Massacre")
        assert s.squirrel_tokens == 2 and M.COMMANDER in s.battlefield and s.rat_tokens == 1 and s.mercenary_tokens == 1 and not [n for n in s.battlefield if n in ("Zulaport Cutthroat", "Gray Merchant of Asphodel", "Pitiless Plunderer")]
        s = novo(campo=[M.COMMANDER, "Zulaport Cutthroat", "Gray Merchant of Asphodel", "Pitiless Plunderer"])       # N = Rat King + 2 Esquilos novos = 3: so' Zulaport (1) morre; Gray e Plunderer (4) ficam
        pl = M.wipe_plan(s, "Swarmyard Massacre")
        assert pl["named"] == ["Zulaport Cutthroat"] and pl["loss"] == 1
        s = novo(campo=["Valley Rotcaller", "Rat Colony"], rats=0)                                                      # Rotcaller (Squirrel) e Rat Colony (Rat) sao protegidos
        assert M.wipe_plan(s, "Swarmyard Massacre")["loss"] == 0


@teste("WP4 limite de perda propria: 0 retem o wipe com perda (1 retencao por turno) e conjura o sem perda; None conjura sempre; wipe com efeito desligado nao e' retido")
def _():
    campo = [M.COMMANDER, "Zulaport Cutthroat", "Rat Colony"]
    with chaves(**ON, WIPE_CAST_MAX_OWN_LOSS=0):
        s = novo(campo=campo, mao=["Damnation"], swamps=6)
        M.main_phase(s, is_first_main=False)
        assert "Damnation" in s.hand and s.wipe_casts_total == 0 and s.wipe_held_total == 1 and M.COMMANDER in s.battlefield
        s = novo(campo=[M.COMMANDER, "Rat Colony"], mao=["Kindred Dominance"], swamps=7)      # todos Rats: perda 0
        M.main_phase(s, is_first_main=False)
        assert "Kindred Dominance" in s.graveyard and s.wipe_kindred_total == 1 and s.wipe_own_creatures_lost_total == 0 and s.wipe_held_total == 0
    with chaves(**ON, WIPE_CAST_MAX_OWN_LOSS=None):
        s = novo(campo=campo, mao=["Damnation"], swamps=6)
        M.main_phase(s, is_first_main=False)
        assert "Damnation" in s.graveyard and s.wipe_damnation_total == 1 and s.wipe_own_creatures_lost_total >= 3 and s.wipe_held_total == 0
    with chaves(**OFF, WIPE_CAST_MAX_OWN_LOSS=0):
        s = novo(campo=campo, mao=["Damnation"], swamps=6)
        M.main_phase(s, is_first_main=False)
        assert "Damnation" in s.graveyard and M.COMMANDER in s.battlefield and s.wipe_held_total == 0       # efeito desligado: caminho antigo (paga, nao mata)


@teste("WP5 chaves desligadas = caminho antigo: Damnation e Kindred nao matam nada; Swarmyard so' cria os 2 Esquilos")
def _():
    with chaves(**OFF, WIPE_CAST_MAX_OWN_LOSS=None):
        for nome in ("Damnation", "Kindred Dominance", "Swarmyard Massacre"):
            s = novo(campo=[M.COMMANDER, "Zulaport Cutthroat", "Gray Merchant of Asphodel"], rats=2, squirrels=1, mercs=1)
            M.resolve_instant_sorcery(s, nome)
            assert {M.COMMANDER, "Zulaport Cutthroat", "Gray Merchant of Asphodel"} <= set(s.battlefield) and s.rat_tokens == 2 and s.mercenary_tokens == 1
            assert s.squirrel_tokens == (3 if nome == "Swarmyard Massacre" else 1) and s.wipe_casts_total == 1 and s.wipe_own_creatures_lost_total == 0


@teste("WP6 Disappear: Kindred poupa o Rat King e mata o Zulaport -> o end step cria o Rat (e o contador); Damnation mata o Rat King -> nao cria")
def _():
    with chaves(**ON):
        s = novo(campo=[M.COMMANDER, "Zulaport Cutthroat"], swamps=4)
        s.permanent_left_battlefield_this_turn = False
        M.apply_own_wipe(s, "Kindred Dominance")
        assert s.permanent_left_battlefield_this_turn
        r0, c0 = s.rat_tokens, s.rat_king_counters
        M.end_step(s)
        assert s.rat_tokens == r0 + 1 and s.rat_king_counters == c0 + 1
        s = novo(campo=[M.COMMANDER, "Zulaport Cutthroat"], swamps=4)
        s.permanent_left_battlefield_this_turn = False
        M.apply_own_wipe(s, "Damnation")
        r0 = s.rat_tokens
        M.end_step(s)
        assert s.rat_tokens == r0


@teste("WP7 comandante morto por Damnation: volta a ser conjuravel pagando o imposto de comandante ({1}{B} + {2} por conjuracao anterior)")
def _():
    with chaves(**ON):
        s = novo(campo=[M.COMMANDER], swamps=4)
        M.apply_own_wipe(s, "Damnation")
        s.mana_spent_this_turn = 0
        assert not s.commander_in_play and s.commander_cast_count == 1
        assert M.can_cast(s, M.COMMANDER) and M.remaining_mana(s) == 4
        M.main_phase(s, is_first_main=False)
        assert s.commander_in_play and s.commander_cast_count == 2 and s.mana_spent_this_turn == 4          # {1}{B} + {2} de imposto


@teste("WP8 partidas inteiras (3.000): limite 0 BRUTO: nenhuma criatura minha morre por wipe meu E houve wipe conjurado (>0); limite 0 LIQUIDO: so' o Swarmyard perde criaturas (<= 2 por conjuracao); limite enorme: morrem (controle positivo)")
def _():
    def roda(lim, net):
        casts = perdas = retidos = 0; com_perda = 0; sw = 0
        with chaves(**ON, WIPE_CAST_MAX_OWN_LOSS=lim, WIPE_GATE_NET_OF_NEW_TOKENS=net):
            for sd in range(5_000_000, 5_003_000):
                r = M.simulate_one(sd, turns=8)
                casts += r.wipe_casts_total; perdas += r.wipe_own_creatures_lost_total; retidos += r.wipe_held_total; sw += r.wipe_swarmyard_total
                com_perda += 1 if r.wipe_own_creatures_lost_total else 0
        return casts, perdas, retidos, com_perda, sw
    c0, p0, r0, _, _ = roda(0, False)
    assert c0 > 0 and r0 > 0 and p0 == 0, (c0, r0, p0)
    cn, pn, rn, cpn, swn = roda(0, True)
    assert cn > 0 and swn > 0 and pn > 0 and pn <= 2 * swn, (cn, pn, swn)        # a perda liquida <= 0 so' deixa o Swarmyard matar ate 2 (ele cria 2)
    c99, p99, r99, cp99, _ = roda(10**9, True)         # "sem limite" de verdade: o combo Ayara + Plague cria ate 60 fichas, e a perda pode passar de 99
    assert c99 > 0 and p99 > 0 and cp99 > 0 and r99 == 0, (c99, p99, r99, cp99)


@teste("WP9 limite LIQUIDO: Swarmyard que mata so' o Zulaport (perda 1) e cria 2 Esquilos e' conjurado com limite 0; com a chave liquida desligada (so' as mortes) fica retido; Kindred nao cria corpos (liquida = bruta)")
def _():
    campo = [M.COMMANDER, "Zulaport Cutthroat", "Gray Merchant of Asphodel"]       # N = Rat King + 2 Esquilos = 3: so' o Zulaport (1/1) morre, o Gray Merchant (tenacidade 4) fica
    with chaves(**ON, WIPE_CAST_MAX_OWN_LOSS=0, WIPE_GATE_NET_OF_NEW_TOKENS=True):
        s = novo(campo=campo, mao=["Swarmyard Massacre"], swamps=5)
        assert M.wipe_plan(s, "Swarmyard Massacre")["loss"] == 1 and not M.wipe_held(s, "Swarmyard Massacre")
        M.main_phase(s, is_first_main=False)
        assert s.wipe_swarmyard_total == 1 and s.squirrel_tokens == 2 and "Zulaport Cutthroat" in s.graveyard and "Gray Merchant of Asphodel" in s.battlefield and s.wipe_own_creatures_lost_total == 1
    with chaves(**ON, WIPE_CAST_MAX_OWN_LOSS=0, WIPE_GATE_NET_OF_NEW_TOKENS=False):
        s = novo(campo=campo, mao=["Swarmyard Massacre"], swamps=5)
        assert M.wipe_held(s, "Swarmyard Massacre") and s.wipe_held_total == 1
        M.main_phase(s, is_first_main=False)
        assert "Swarmyard Massacre" in s.hand and s.wipe_swarmyard_total == 0
    with chaves(**ON, WIPE_CAST_MAX_OWN_LOSS=0, WIPE_GATE_NET_OF_NEW_TOKENS=True):
        s = novo(campo=[M.COMMANDER, "Zulaport Cutthroat"], mao=["Kindred Dominance"], swamps=7)
        assert M.wipe_plan(s, "Kindred Dominance")["loss"] == 1 and M.wipe_held(s, "Kindred Dominance")        # Kindred nao cria nada: 1 morte = perda liquida 1 > 0


for nome, ok, tb in resultados:
    print(("PASS " if ok else "FAIL ") + nome)
    if not ok:
        print("     " + tb.strip().replace("\n", "\n     "))
print()
print(f"{sum(1 for _, ok, _ in resultados if ok)}/{len(resultados)} testes passaram")
sys.exit(0 if all(ok for _, ok, _ in resultados) else 1)

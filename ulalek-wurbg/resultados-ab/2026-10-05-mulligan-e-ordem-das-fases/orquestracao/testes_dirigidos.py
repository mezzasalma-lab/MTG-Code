"""Testes dirigidos das correcoes de 2026-10-05 (mulligan com escolha do fundo; imposto do comandante do Hei Bai; upkeep antes do draw em Maralen/Rat King). Cada teste
confere o COMPORTAMENTO que a correcao promete, nao so' que o codigo roda. Uso: python3 testes_dirigidos.py config.json"""
import collections, json, os, sys, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
M = A.carrega(os.path.join(DECK, cfg["sim"]), "td_vivo", DECK)
resultados = []


def teste(nome):
    def deco(f):
        try:
            f()
            resultados.append((nome, True, ""))
        except Exception:
            resultados.append((nome, False, traceback.format_exc(limit=3)))
        return f
    return deco


LANDS = sorted(n for n in M.LAND_NAMES if n in M.CARD_DB and "etb_tapped" not in M.CARD_DB[n].tags)
NONLANDS = sorted((n for n in M.CARD_DB if n not in M.LAND_NAMES and M.CARD_DB[n].ctype not in ("token",) and n != getattr(M, "COMMANDER", None)), key=lambda n: (M.CARD_DB[n].mv, n))
PROT = sorted(n for n in getattr(M, "MULLIGAN_PROTECTED", ()) if n in M.CARD_DB and n not in M.LAND_NAMES and n != getattr(M, "COMMANDER", None))
LIVRES = [n for n in NONLANDS if n not in getattr(M, "MULLIGAN_PROTECTED", ())]

if hasattr(M, "MULLIGAN_SMART_BOTTOM_ENABLED"):
    @teste("M1 com 5 terrenos na mao devolve um TERRENO (sobram mais de 4)")
    def _():
        hand = LANDS[:5] + [LIVRES[-1], LIVRES[0]]
        assert M.choose_bottom(hand, 1)[0] in M.LAND_NAMES

    @teste("M2 com 3 terrenos devolve a carta nao-terreno de MAIOR custo que nao e' protegida")
    def _():
        alto, baixo = LIVRES[-1], LIVRES[0]
        hand = LANDS[:3] + [PROT[0], baixo, alto]
        assert M.choose_bottom(hand, 1) == [alto], (M.choose_bottom(hand, 1), alto)

    @teste("M3 com 4 terrenos (nao 'mais de 4') ainda devolve nao-terreno, nunca o 4o terreno")
    def _():
        hand = LANDS[:4] + [LIVRES[-1], LIVRES[0], LIVRES[1]]
        assert M.choose_bottom(hand, 1)[0] not in M.LAND_NAMES

    @teste("M4 se so' ha' cartas protegidas como nao-terreno, devolve a de maior custo entre elas (nao trava)")
    def _():
        hand = LANDS[:3] + PROT[:2]
        b = M.choose_bottom(hand, 1)[0]
        assert b in PROT[:2] and M.CARD_DB[b].mv == max(M.CARD_DB[p].mv for p in PROT[:2])

    @teste("M5 n=2: duas cartas distintas da mao, na ordem de decisao, sem mutar a mao original")
    def _():
        hand = LANDS[:3] + [PROT[0], LIVRES[-1], LIVRES[-2]]
        antes = list(hand)
        b = M.choose_bottom(hand, 2)
        assert hand == antes and b == [LIVRES[-1], LIVRES[-2]], (b, [LIVRES[-1], LIVRES[-2]])

    @teste("M6 mulligan(): mao final = 7 - penalidade, as devolvidas vao pro FUNDO e nada some nem aparece (conservacao)")
    def _():
        import random
        achou = 0
        for sd in range(2000):
            rng = random.Random(sd)
            hand, lib, mulls = M.mulligan(rng)
            pen = max(0, mulls - 1)
            if pen == 0:
                continue
            achou += 1
            assert len(hand) == 7 - pen, (sd, len(hand), pen)
            assert collections.Counter(hand + lib) == collections.Counter(M.BASE_LIBRARY), sd
            assert len(lib) == len(M.BASE_LIBRARY) - 7 + pen
        assert achou > 50, achou

    @teste("M7 politica real: nas maos com penalidade, a escolha devolve carta de custo >= a media das nao-protegidas devolviveis (nao um Sol Ring/Signet)")
    def _():
        import random
        ruins = 0; tot = 0
        for sd in range(3000):
            rng = random.Random(sd)
            hand, lib, mulls = M.mulligan(rng)
            pen = max(0, mulls - 1)
            if pen:
                tot += 1
                fundo = lib[-pen:]
                if any(c in M.MULLIGAN_PROTECTED and c not in M.LAND_NAMES and any(h not in M.MULLIGAN_PROTECTED and h not in M.LAND_NAMES for h in hand + fundo) for c in fundo):
                    ruins += 1
        assert tot > 50 and ruins == 0, (tot, ruins)

    @teste("M8 com a chave desligada o caminho antigo (sorteio) volta e a conservacao continua valendo")
    def _():
        import random
        M.MULLIGAN_SMART_BOTTOM_ENABLED = False
        try:
            for sd in range(500):
                hand, lib, mulls = M.mulligan(random.Random(sd))
                assert collections.Counter(hand + lib) == collections.Counter(M.BASE_LIBRARY)
        finally:
            M.MULLIGAN_SMART_BOTTOM_ENABLED = True

if hasattr(M, "COMMANDER_TAX_ENABLED"):
    @teste("T1 imposto: o custo efetivo do comandante cresce {2} por cast anterior (CR 903.8)")
    def _():
        s = M.GameState()
        base = M.effective_cost(s, M.COMMANDER)
        for k in range(1, 4):
            s.commander_cast_count = k
            assert M.effective_cost(s, M.COMMANDER) == base + 2 * k
        M.COMMANDER_TAX_ENABLED = False
        try:
            assert M.effective_cost(s, M.COMMANDER) == base
        finally:
            M.COMMANDER_TAX_ENABLED = True

    @teste("T2 imposto: can_cast respeita a taxa (mana que paga o 1o cast nao paga o recast)")
    def _():
        s = M.GameState(); base = M.CARD_DB[M.COMMANDER].mv
        s.battlefield = [LANDS[0]] * base
        s.commander_cast_count = 0
        assert M.can_cast(s, M.COMMANDER)
        s.commander_cast_count = 1
        assert not M.can_cast(s, M.COMMANDER)

    @teste("T3 imposto: cast_card conta o cast (e so' o do comandante) e o proximo custa mais")
    def _():
        s = M.GameState(); base = M.CARD_DB[M.COMMANDER].mv
        s.battlefield = [LANDS[0]] * (base + 4)
        M.cast_card(s, M.COMMANDER)
        assert s.commander_cast_count == 1 and s.commander_in_play
        assert M.effective_cost(s, M.COMMANDER) == base + 2

    @teste("T4 imposto: cast ANULADO tambem conta (CR 903.8: each previous time it was cast) -- contramagica forcada")
    def _():
        s = M.GameState(); base = M.CARD_DB[M.COMMANDER].mv
        s.battlefield = [LANDS[0]] * (base + 4)
        orig = M.try_smart_opponent_counter
        M.try_smart_opponent_counter = lambda st, *a, **k: True
        try:
            M.cast_card(s, M.COMMANDER)
        finally:
            M.try_smart_opponent_counter = orig
        assert s.commander_cast_count == 1 and not s.commander_in_play

    @teste("T5 imposto: no modo de resiliencia a taxa aparece (algum jogo recasta o comandante pagando mais que o custo base)")
    def _():
        base = M.CARD_DB[M.COMMANDER].mv
        recast = sum(1 for sd in range(400) if M.simulate_one_with_interaction(sd).commander_cast_count >= 2)
        assert recast > 20, recast
        sem = sum(1 for sd in range(400) if M.simulate_one(sd).commander_cast_count >= 2)
        assert sem == 0, sem   # goldfish padrao: o comandante nunca morre

if hasattr(M, "UPKEEP_BEFORE_DRAW_ENABLED"):
    @teste("O1 ordem: com a chave ligada o upkeep roda ANTES do draw (mao ainda sem a carta comprada); desligada, depois")
    def _():
        visto = []
        orig = M.upkeep_step
        def espia(state):
            visto.append(len(state.hand))
            return orig(state)
        M.upkeep_step = espia
        try:
            for ligada, esperado in ((True, 3), (False, 4)):
                M.UPKEEP_BEFORE_DRAW_ENABLED = ligada
                s = M.GameState(hand=list(LANDS[:3]), library=list(LIVRES[:10]))
                visto.clear()
                M.play_turn(s, True, True)
                assert visto == [esperado], (ligada, visto)
        finally:
            M.upkeep_step = orig
            M.UPKEEP_BEFORE_DRAW_ENABLED = True

falhas = [r for r in resultados if not r[1]]
for nome, ok, tb in resultados:
    print(("PASS " if ok else "FAIL ") + nome)
    if not ok:
        print(tb)
print(f"\n{len(resultados) - len(falhas)}/{len(resultados)} testes passaram")
sys.exit(1 if falhas else 0)

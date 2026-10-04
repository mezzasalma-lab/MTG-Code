"""Testes dirigidos da 6a rodada (preferencias do usuario): (1) SEMPRE jogar a magia exilada antes das da mao, tambem a que nao expira neste turno
(Inspired Tinkering) e a que acabou de ser exilada no meio do main; (2) Dictate of Erebos em campo tambem aciona o sacrificio dos Treasures animados,
mesmo sem Mahadi/Pitiless Plunderer. Cada teste monta um GameState a mao e chama a funcao real. Uso: python3 testes_dirigidos.py"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

V = F.flags(F.carrega(F.DEPOIS, "vih_6a_testes"))
res = []


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def novo(bf=(), hand=(), lands=12, turn=7, library=None):
    s = V.GameState(hand=list(hand), battlefield=list(bf) + ["Mountain"] * lands, library=list(library) if library is not None else ["Swamp"] * 30)
    s.turn = turn
    s.commander_in_play = True
    s.battlefield.append(V.COMMANDER)
    return s


def modo(allfirst=True, dictate=True):
    F.flags(V, allfirst=allfirst, dictate=dictate)


def pact_calls(fn):
    calls = {"n": 0}
    orig = V.create_treasures
    def ct(state, n, source=""):
        if source == "Prosper Pact Boon":
            calls["n"] += 1
        orig(state, n, source)
    V.create_treasures = ct
    try:
        fn()
    finally:
        V.create_treasures = orig
    return calls["n"]


PROSPER, MAHADI, LOTHO, PLUNDERER, DICTATE = "Prosper, Tome-Bound", "Mahadi, Emporium Master", "Lotho, Corrupt Shirriff", "Pitiless Plunderer", "Dictate of Erebos"
# ------------------------------------------------------------------ 1. sempre jogar o exilio primeiro
s = novo([PROSPER], hand=[MAHADI], lands=3, turn=7); s.impulse_pool = [(LOTHO, 8)]  # prazo 8 > turno 7: poderia esperar
n_pact = pact_calls(lambda: V.main_phase(s))
teste("A1 carta do exilio que NAO expira neste turno (prazo 8) tambem vai ANTES da mao: Lotho entra, o Mahadi espera, Pact Boon cria 1 Treasure",
      LOTHO in s.battlefield and MAHADI in s.hand and n_pact == 1 and s.impulse_all_first_total == 1, str((LOTHO in s.battlefield, s.hand, n_pact)))
modo(allfirst=False)
s = novo([PROSPER], hand=[MAHADI], lands=3, turn=7); s.impulse_pool = [(LOTHO, 8)]
V.main_phase(s)
teste("A2 chave desligada = comportamento da rodada anterior: so' as que expiram neste turno vao antes; a que pode esperar fica depois da mao", MAHADI in s.battlefield and (LOTHO, 8) in s.impulse_pool)
modo()
# Inspired Tinkering: exila 3 cartas e elas aparecem no MEIO do main, depois de a Tinkering ser conjurada da mao. Com exatamente 5 terrenos a Tinkering
# gasta todos e so' sobram os 3 Treasures que ela cria (3 de mana): cabe UMA carta de 2 (Lotho do exilio OU Zulaport da mao).
def cena_tinkering(allfirst):
    modo(allfirst=allfirst)
    s = novo([PROSPER], hand=["Inspired Tinkering", "Zulaport Cutthroat"], lands=5, turn=6, library=[LOTHO, "Monologue Tax", "Mirkwood Bats"] + ["Swamp"] * 20)
    n = pact_calls(lambda: V.main_phase(s))
    modo()
    return s, n
s, n = cena_tinkering(True)
teste("A3 Inspired Tinkering com so' 3 de mana sobrando: a carta recem-exilada (Lotho, 2) entra ANTES do Zulaport da mao; Pact Boon +1; o Zulaport fica na mao",
      LOTHO in s.battlefield and "Zulaport Cutthroat" in s.hand and n == 1, str((LOTHO in s.battlefield, s.hand, n)))
s, n = cena_tinkering(False)
teste("A4 chave desligada (so' as que expiram vao antes): o Zulaport da mao vai primeiro e a carta da Tinkering fica esperando no pool, sem Pact Boon",
      "Zulaport Cutthroat" in s.battlefield and LOTHO not in s.battlefield and (LOTHO, 7) in s.impulse_pool and n == 0, str((s.hand, LOTHO in s.battlefield, n)))
s = V.GameState(hand=[MAHADI], battlefield=["Mountain"] * 3 + [PROSPER], library=["Swamp"] * 30); s.turn = 7; s.impulse_pool = [(LOTHO, 8)]
V.main_phase(s)
teste("A5 o comandante continua sendo conjurado antes de tudo, inclusive antes do exilio", V.COMMANDER in s.battlefield and LOTHO not in s.battlefield)
s = novo([PROSPER], hand=[MAHADI], lands=3, turn=7); s.impulse_pool = [(LOTHO, 8), ("Sol Ring", 8), ("Arcane Signet", 8)]
n = pact_calls(lambda: V.main_phase(s))
teste("A6 varias do exilio (prazo 8): todas entram, com 1 Pact Boon por carta (3 Treasures) antes de qualquer carta da mao", all(c in s.battlefield for c in ("Sol Ring", LOTHO, "Arcane Signet")) and n == 3 and s.impulse_all_first_total == 3, str((n, s.impulse_all_first_total)))

# ------------------------------------------------------------------ 2. Dictate aciona o sacrificio de animados
def cena(bf, treasures, animados):
    s = novo(bf, lands=0)
    s.treasures, s.treasures_animated_alive = treasures, animados
    return s
s = cena([DICTATE], 5, 5)
V.farm_animated_treasures(s)
teste("D1 Dictate em campo, SEM Mahadi/Plunderer: sacrifica os 5 animados (custa 5 Treasures): 5 criaturas mortas, 5 gatilhos do Dictate = 5 x 3 oponentes sacrificando uma criatura (proxy)",
      s.treasures == 0 and s.creature_deaths_total == 5 and s.dictate_triggers_total == 5 and s.treasure_farm_dictate_total == 5 and s.dictate_triggers_total * V.NUM_OPPONENTS == 15,
      str((s.treasures, s.creature_deaths_total, s.dictate_triggers_total, s.treasure_farm_dictate_total)))
modo(dictate=False)
s = cena([DICTATE], 5, 5)
V.farm_animated_treasures(s)
teste("D2 chave desligada = comportamento da rodada anterior: so' Dictate nao aciona o farm", s.treasures == 5 and s.creature_deaths_total == 0)
modo()
s = cena([DICTATE, MAHADI], 5, 5)
V.farm_animated_treasures(s)
teste("D3 Dictate + Mahadi: sacrifica (de graca, o Mahadi repoe) e o contador 'so' por causa do Dictate' fica em 0", s.treasure_farm_total == 5 and s.treasure_farm_dictate_total == 0 and s.dictate_triggers_total == 5)
s = cena([], 5, 5)
V.farm_animated_treasures(s)
teste("D4 sem Dictate, Mahadi nem Plunderer: nao sacrifica (a regra da rodada anterior continua)", s.treasures == 5 and s.creature_deaths_total == 0)
s = cena([DICTATE], 8, 5)
V.farm_animated_treasures(s)
teste("D5 so' os animados: dos 8 Treasures, 5 animados saem e os 3 criados depois do combate ficam", s.treasures == 3 and s.creature_deaths_total == 5)
# ordem: o Dictate e' conjurado com os terrenos (nao com os animados), depois os animados morrem COM ele em campo
s = V.GameState(hand=[DICTATE], battlefield=["Mountain"] * 5 + [V.COMMANDER], library=["Swamp"] * 30); s.turn = 8; s.commander_in_play = True
s.treasures, s.treasures_animated_alive = 6, 6
V.cast_card(s, DICTATE)
animados_apos_cast = s.treasures_animated_alive
V.farm_animated_treasures(s)
teste("D6 ordem: o Dictate (custo 5) e' pago pelos 5 terrenos (nenhum animado gasto), e os 6 animados depois morrem com ele em campo = 6 gatilhos (pagar com os Treasures, como no T8, perderia esses gatilhos)",
      animados_apos_cast == 6 and s.dictate_triggers_total == 6 and s.treasures == 0, str((animados_apos_cast, s.dictate_triggers_total, s.treasures)))
s = cena([DICTATE, "Zulaport Cutthroat", "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel"], 6, 6)
V.farm_animated_treasures(s)
teste("D7 integracao: Dictate + Zulaport + Sephiroth, 6 animados: 6 gatilhos do Dictate, 6 drains do Zulaport e o Sephiroth vira na 4a morte", s.dictate_triggers_total == 6 and s.life_gained_total >= 6 and s.sephiroth_transformed)
# sequencia real: combat_step anima, main_phase conjura o Dictate, farm, end_step
s = V.GameState(hand=[DICTATE], battlefield=["Mountain"] * 6 + [V.COMMANDER], library=["Swamp"] * 30); s.turn = 8; s.commander_in_play = True; s.treasures = 6
V.combat_step(s)
V.main_phase(s)
V.farm_animated_treasures(s)
V.end_step(s)
teste("D8 sequencia real combat_step -> main_phase (Dictate pago com terrenos) -> farm -> end_step: 6 animados, 6 gatilhos do Dictate, 0 animados vivos no fim",
      DICTATE in s.battlefield and s.dictate_triggers_total >= 6 and s.treasures_animated_alive == 0, str((DICTATE in s.battlefield, s.dictate_triggers_total, s.treasures_animated_alive)))

# ------------------------------------------------------------------ invariantes em partidas reais
import collections
def jogos(n, seed0, modo_jogo):
    fn = V.simulate_one if modo_jogo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    dup = viol_alive = viol_farm = farm_total = farm_dic = 0
    orig_et, orig_farm = V.end_step, V.farm_animated_treasures
    def et(state):
        nonlocal viol_alive
        orig_et(state)
        if state.treasures_animated_alive != 0:
            viol_alive += 1
    def fm(state):
        nonlocal viol_farm
        antes, animados = state.treasure_farm_total, state.treasures_animated_alive
        orig_farm(state)
        if state.treasure_farm_total - antes > animados:
            viol_farm += 1
    V.end_step, V.farm_animated_treasures = et, fm
    for i in range(n):
        s = fn(seed0 + i)
        farm_total += s.treasure_farm_total
        farm_dic += s.treasure_farm_dictate_total
        if s.treasure_farm_dictate_total > s.treasure_farm_total:
            viol_farm += 1
        zonas = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + [c for c, _ in s.impulse_pool] + [c for c, _ in s.impulse_lands])
        if any(zonas[k] > v for k, v in base.items()):
            dup += 1
    V.end_step, V.farm_animated_treasures = orig_et, orig_farm
    return dup, viol_alive, viol_farm, farm_total, farm_dic
for modo_jogo in ("padrao", "resiliencia"):
    dup, va, vf, ft, fd = jogos(1500, 1_000_000, modo_jogo)
    teste(f"I1 ({modo_jogo}, 1.500 jogos) nenhuma carta duplicada, 0 'animados vivos' no fim do turno, o farm nunca acima dos animados", dup == 0 and va == 0 and vf == 0 and ft > 0, str((dup, va, vf, ft)))
    print(f"   info I1 {modo_jogo}: Treasures-criatura sacrificados pelo farm em 1.500 jogos: {ft} (so' por causa do Dictate: {fd})")

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)

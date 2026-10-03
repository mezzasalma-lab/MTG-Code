"""Testes dirigidos da 5a rodada: (1) carta do exilio que expira neste turno e' conjurada antes das da mao (Prosper); (2) com Mahadi/Pitiless
Plunderer, os Treasures-criatura restantes sao sacrificados no fim da 2a main (a linha do T8 da partida manual #1). Cada teste monta um GameState a
mao e chama a funcao real. Uso: python3 testes_dirigidos.py"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

V = F.flags(F.carrega(F.DEPOIS, "vih_ep_testes"))
res = []


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def novo(bf=(), hand=(), lands=12, turn=7):
    s = V.GameState(hand=list(hand), battlefield=list(bf) + ["Mountain"] * lands, library=["Swamp"] * 30)
    s.turn = turn
    s.commander_in_play = True
    s.battlefield.append(V.COMMANDER)
    return s


def modo(first=True, farm=True):
    F.flags(V, first=first, farm=farm)


PROSPER, MAHADI, LOTHO, PLUNDERER = "Prosper, Tome-Bound", "Mahadi, Emporium Master", "Lotho, Corrupt Shirriff", "Pitiless Plunderer"
# ------------------------------------------------------------------ 1. exilio expirando primeiro
s = novo([PROSPER], hand=[MAHADI], lands=3, turn=7); s.impulse_pool = [(LOTHO, 7)]
V.main_phase(s)
teste("E1 mana pra UMA so': a carta do exilio que expira neste turno (Lotho, prazo 7) e' conjurada ANTES da da mao; o Mahadi espera; Pact Boon cria 1 Treasure",
      LOTHO in s.battlefield and MAHADI in s.hand and s.treasures_created_total == 1 and s.impulse_expiring_first_total == 1,
      str((LOTHO in s.battlefield, s.hand, s.treasures_created_total)))
modo(first=False)
s = novo([PROSPER], hand=[MAHADI], lands=3, turn=7); s.impulse_pool = [(LOTHO, 7)]
V.main_phase(s)
teste("E2 chave desligada = comportamento antigo: a da mao (Mahadi) vai primeiro e a do exilio expira sem uso", MAHADI in s.battlefield and LOTHO not in s.battlefield and (LOTHO, 7) in s.impulse_pool)
modo()
s = novo([PROSPER], hand=[MAHADI], lands=3, turn=7); s.impulse_pool = [(LOTHO, 8)]
V.main_phase(s)
teste("E3 carta do exilio que NAO expira neste turno (prazo 8) pode esperar: a da mao vai primeiro, a do exilio continua no pool", MAHADI in s.battlefield and (LOTHO, 8) in s.impulse_pool and s.impulse_expiring_first_total == 0)
s = V.GameState(hand=[MAHADI], battlefield=["Mountain"] * 3 + [PROSPER], library=["Swamp"] * 30); s.turn = 7; s.impulse_pool = [(LOTHO, 7)]
V.main_phase(s)
teste("E4 o comandante continua sendo conjurado antes de tudo (3 mana: ele; nada sobra pro exilio)", V.COMMANDER in s.battlefield and LOTHO not in s.battlefield)
s = novo([PROSPER], hand=[], lands=12, turn=7); s.impulse_pool = [(LOTHO, 7), ("Sol Ring", 7), ("Arcane Signet", 7)]
V.main_phase(s)
teste("E5 varias do exilio expirando: todas as que cabem na mana entram, com 1 Pact Boon por carta (3 Treasures)", all(c in s.battlefield for c in (LOTHO, "Sol Ring", "Arcane Signet")) and s.treasures_created_total == 3, str(s.treasures_created_total))
s = novo([PROSPER], hand=["Sol Ring"], lands=1, turn=7); s.impulse_pool = [("Blood Money", 7)]
V.main_phase(s)
teste("E6 expirando que nao cabe na mana nao bloqueia a da mao (sem mana pro Blood Money: o Sol Ring entra)", "Sol Ring" in s.battlefield and (("Blood Money", 7) in s.impulse_pool))

# ------------------------------------------------------------------ 2. farm de Treasures-criatura com Mahadi / Plunderer
def cena(bf, treasures, animados, hand=()):
    s = novo(bf, hand=hand, lands=0)
    s.treasures, s.treasures_animated_alive = treasures, animados
    return s
s = cena([MAHADI], 5, 5)
V.farm_animated_treasures(s)
c_depois_farm = (s.treasures, s.creature_deaths_total, s.deaths_this_turn, s.treasure_farm_total, s.treasures_animated_alive)
V.end_step(s)
teste("F1 Mahadi em campo, 5 Treasures animados no fim da 2a main: sacrifica os 5 (5 criaturas mortas); no end step o Mahadi devolve 5: custo liquido ZERO",
      c_depois_farm == (0, 5, 5, 5, 0) and s.treasures == 5, str((c_depois_farm, s.treasures)))
s = cena([PLUNDERER], 5, 5)
V.farm_animated_treasures(s)
teste("F2 Pitiless Plunderer (sem Mahadi): cada morte cria 1 Treasure na hora: sacrifica 5 e fica com 5", s.treasures == 5 and s.creature_deaths_total == 5 and s.treasure_farm_total == 5, str((s.treasures, s.creature_deaths_total)))
s = cena([], 5, 5)
V.farm_animated_treasures(s)
teste("F3 sem Mahadi nem Plunderer custaria 1 Treasure por morte: NAO sacrifica", s.treasures == 5 and s.creature_deaths_total == 0 and s.treasure_farm_total == 0)
s = cena([MAHADI], 8, 5)
V.farm_animated_treasures(s)
teste("F4 so' os ANIMADOS (criaturas) sao sacrificados: dos 8 Treasures, 5 animados saem e os 3 criados depois do combate ficam", s.treasures == 3 and s.creature_deaths_total == 5)
s = cena([MAHADI, "Zulaport Cutthroat", "Dictate of Erebos"], 7, 7)
V.farm_animated_treasures(s)
teste("F5 T8 da partida: com Mahadi + Zulaport + Dictate em campo, 7 animados sacrificados = 7 drains do Zulaport (+7 de vida) e 7 gatilhos do Dictate (proxy de uso)",
      s.drain_damage_total == 7 and s.life_gained_total == 7 and s.dictate_triggers_total == 7, str((s.drain_damage_total, s.life_gained_total, s.dictate_triggers_total)))
modo(farm=False)
s = cena([MAHADI], 5, 5)
V.farm_animated_treasures(s)
teste("F6 chave desligada = comportamento antigo: nada e' sacrificado", s.treasures == 5 and s.creature_deaths_total == 0)
modo()
s = cena(["Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel", MAHADI], 6, 6)
V.farm_animated_treasures(s)
teste("F7 integracao com o Sephiroth: 6 mortes = 6 gatilhos e ele vira na 4a (a regra corrigida na rodada anterior continua valendo)", s.sephiroth_transformed and s.super_nova_emblems == 1 and s.drain_damage_total == 6, str((s.sephiroth_transformed, s.drain_damage_total)))
# turno completo: Vihaan anima, ataque, 2a main, farm, end step
s = V.GameState(hand=[], battlefield=[V.COMMANDER, MAHADI], library=["Swamp"] * 30); s.turn = 7; s.commander_in_play = True; s.treasures = 6
V.combat_step(s)
animados = s.treasures_animated_alive
V.farm_animated_treasures(s)
V.end_step(s)
teste("F8 sequencia real combat_step -> farm -> end_step: o Vihaan anima os 6, o farm os sacrifica, o Mahadi devolve 6; o turno termina com 6 Treasures e 0 animados",
      animados == 6 and s.treasures == 6 and s.treasures_animated_alive == 0 and s.treasure_farm_total == 6, str((animados, s.treasures, s.treasures_animated_alive)))
# a magia paga com animados primeiro (roteamento da 1a rodada continua) e o farm so' leva o que sobrou
s = V.GameState(hand=["Dictate of Erebos"], battlefield=[V.COMMANDER, MAHADI, "Mountain"], library=["Swamp"] * 30); s.turn = 8; s.commander_in_play = True
s.treasures, s.treasures_animated_alive = 7, 7
V.cast_card(s, "Dictate of Erebos")  # custo 5: 1 terreno + 4 Treasures animados
c1 = (s.treasures, s.creature_deaths_total)
V.farm_animated_treasures(s)
teste("F9 Dictate pago com Treasures ja' criaturas (como no T8): os usados no custo e os que sobram contam como mortes: no total os 7 viram 7 criaturas mortas",
      c1 == (3, 4) and s.treasures == 0 and s.creature_deaths_total == 7, str((c1, s.treasures, s.creature_deaths_total)))

# ------------------------------------------------------------------ invariantes em partidas reais
import collections
def jogos(n, seed0, modo_jogo):
    fn = V.simulate_one if modo_jogo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    dup = viol_alive = viol_farm = farm_total = 0
    orig_et = V.end_step
    def et(state):
        nonlocal viol_alive
        orig_et(state)
        if state.treasures_animated_alive != 0:
            viol_alive += 1
    V.end_step = et
    orig_farm = V.farm_animated_treasures
    def fm(state):
        nonlocal viol_farm
        antes = state.treasure_farm_total
        animados = state.treasures_animated_alive
        orig_farm(state)
        if state.treasure_farm_total - antes > animados:
            viol_farm += 1
    V.farm_animated_treasures = fm
    for i in range(n):
        s = fn(seed0 + i)
        farm_total += s.treasure_farm_total
        zonas = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + [c for c, _ in s.impulse_pool] + [c for c, _ in s.impulse_lands])
        if any(zonas[k] > v for k, v in base.items()):
            dup += 1
    V.end_step = orig_et
    V.farm_animated_treasures = orig_farm
    return dup, viol_alive, viol_farm, farm_total
for modo_jogo in ("padrao", "resiliencia"):
    dup, va, vf, ft = jogos(1500, 1_000_000, modo_jogo)
    teste(f"I1 ({modo_jogo}, 1.500 jogos) nenhuma carta duplicada, 0 'animados vivos' no fim do turno, o farm nunca sacrifica mais do que os animados",
          dup == 0 and va == 0 and vf == 0 and ft > 0, str((dup, va, vf, ft)))
    print(f"   info I1 {modo_jogo}: Treasures-criatura sacrificados pelo farm em 1.500 jogos: {ft}")

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)

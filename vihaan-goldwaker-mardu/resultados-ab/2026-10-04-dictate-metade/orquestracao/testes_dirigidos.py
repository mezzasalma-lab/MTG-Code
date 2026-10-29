"""Testes dirigidos da 7a rodada (criterio do usuario: "eu sacrificaria ate' metade dos treasures para eliminar criaturas dos adversarios"): quando SO' o
Dictate of Erebos justifica o sacrificio dos Treasures animados (sem Mahadi/Pitiless Plunderer, que repoem), no maximo METADE do estoque. Cada teste monta um
GameState a mao e chama a funcao real. Uso: python3 testes_dirigidos.py"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

V = F.flags(F.carrega(F.DEPOIS, "vih_7a_testes"))
res = []


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def novo(bf=(), hand=(), lands=0, turn=8):
    s = V.GameState(hand=list(hand), battlefield=list(bf) + ["Mountain"] * lands, library=["Swamp"] * 30)
    s.turn = turn
    s.commander_in_play = True
    s.battlefield.append(V.COMMANDER)
    return s


def cena(bf, treasures, animados):
    s = novo(bf)
    s.treasures, s.treasures_animated_alive = treasures, animados
    return s


def modo(half=True, dictate=True):
    F.flags(V, half=half, dictate=dictate)


DICTATE, MAHADI, PLUNDERER = "Dictate of Erebos", "Mahadi, Emporium Master", "Pitiless Plunderer"
s = cena([DICTATE], 10, 10)
V.farm_animated_treasures(s)
teste("H1 so' o Dictate, 10 Treasures todos animados: sacrifica no maximo METADE (5): 5 mortes, 5 gatilhos do Dictate (= 15 criaturas de oponente no proxy x3), 5 Treasures de reserva",
      s.treasures == 5 and s.creature_deaths_total == 5 and s.dictate_triggers_total == 5 and s.treasure_farm_dictate_total == 5 and s.dictate_triggers_total * V.NUM_OPPONENTS == 15,
      str((s.treasures, s.creature_deaths_total, s.dictate_triggers_total)))
s = cena([DICTATE], 7, 7)
V.farm_animated_treasures(s)
teste("H2 estoque impar (7): 'ate' metade' = 3 (arredonda pra baixo, nunca mais que a metade)", s.treasures == 4 and s.creature_deaths_total == 3, str((s.treasures, s.creature_deaths_total)))
s = cena([DICTATE], 10, 3)
V.farm_animated_treasures(s)
teste("H3 poucos animados (3 de 10): o limite e' o numero de animados, nao a metade (so' criatura conta como morte)", s.treasures == 7 and s.creature_deaths_total == 3)
s = cena([DICTATE], 1, 1)
V.farm_animated_treasures(s)
teste("H4 estoque 1: metade = 0, nao sacrifica o unico Treasure", s.treasures == 1 and s.creature_deaths_total == 0)
s = cena([DICTATE], 12, 7)
V.farm_animated_treasures(s)
teste("H5 estoque 12 com 7 animados: metade = 6 < 7: sacrifica 6 (a metade conta o estoque todo, nao so' os animados)", s.creature_deaths_total == 6 and s.treasures == 6, str((s.creature_deaths_total, s.treasures)))
s = cena([DICTATE], 12, 12)
V.farm_animated_treasures(s)
teste("H6 escala do T8 da partida (12 Treasures animados): sacrifica 6 (o usuario fez 7)", s.creature_deaths_total == 6 and s.dictate_triggers_total == 6)
modo(half=False)
s = cena([DICTATE], 10, 10)
V.farm_animated_treasures(s)
teste("H7 chave desligada = comportamento da rodada anterior: so' o Dictate sacrifica TODOS os animados", s.treasures == 0 and s.creature_deaths_total == 10)
modo()
s = cena([DICTATE, MAHADI], 10, 10)
V.farm_animated_treasures(s)
teste("H8 Dictate + Mahadi: o sacrificio e' de graca (o Mahadi repoe) e continua sendo de TODOS os animados (a metade so' vale quando so' o Dictate justifica); contador 'so' Dictate' = 0",
      s.creature_deaths_total == 10 and s.treasure_farm_dictate_total == 0 and s.dictate_triggers_total == 10)
s = cena([DICTATE, PLUNDERER], 10, 10)
V.farm_animated_treasures(s)
teste("H9 Dictate + Pitiless Plunderer: idem, todos", s.creature_deaths_total == 10 and s.treasure_farm_dictate_total == 0)
s = cena([MAHADI], 10, 10)
V.farm_animated_treasures(s)
teste("H10 so' Mahadi (sem Dictate): todos, como na 5a rodada", s.creature_deaths_total == 10)
modo(dictate=False)
s = cena([DICTATE], 10, 10)
V.farm_animated_treasures(s)
teste("H11 farm com Dictate desligado: nada (regra anterior a 6a rodada)", s.treasures == 10 and s.creature_deaths_total == 0)
modo()
s = cena([], 10, 10)
V.farm_animated_treasures(s)
teste("H12 sem Dictate, Mahadi nem Plunderer: nao sacrifica", s.treasures == 10 and s.creature_deaths_total == 0)
# ordem: o Dictate e' pago com os terrenos; so' depois os animados morrem com ele em campo, ate' a metade
s = V.GameState(hand=[DICTATE], battlefield=["Mountain"] * 5 + [V.COMMANDER], library=["Swamp"] * 30); s.turn = 8; s.commander_in_play = True
s.treasures, s.treasures_animated_alive = 8, 8
V.cast_card(s, DICTATE)
apos_cast = (s.treasures, s.treasures_animated_alive)
V.farm_animated_treasures(s)
teste("H13 ordem: Dictate pago pelos 5 terrenos (os 8 Treasures intactos) e depois 4 animados (metade de 8) morrem com ele em campo = 4 gatilhos", apos_cast == (8, 8) and s.dictate_triggers_total == 4 and s.treasures == 4, str((apos_cast, s.dictate_triggers_total, s.treasures)))
s = V.GameState(hand=[DICTATE], battlefield=["Mountain"] * 6 + [V.COMMANDER], library=["Swamp"] * 30); s.turn = 8; s.commander_in_play = True; s.treasures = 8
V.combat_step(s); V.main_phase(s); V.farm_animated_treasures(s); V.end_step(s)
teste("H14 sequencia real combat_step -> main_phase -> farm -> end_step: 8 animados, Dictate conjurado, 4 sacrificados (metade) e 0 animados vivos no fim", DICTATE in s.battlefield and s.dictate_triggers_total >= 4 and s.treasures_animated_alive == 0, str((DICTATE in s.battlefield, s.dictate_triggers_total)))
s = cena([DICTATE, "Zulaport Cutthroat", "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel"], 12, 12)
V.farm_animated_treasures(s)
teste("H15 integracao: Dictate + Zulaport + Sephiroth, 12 Treasures: 6 sacrificados = 6 gatilhos do Dictate, 6 drains do Zulaport, o Sephiroth vira na 4a morte", s.dictate_triggers_total == 6 and s.life_gained_total >= 6 and s.sephiroth_transformed)

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
        antes, animados, estoque = state.treasure_farm_total, state.treasures_animated_alive, state.treasures
        com_rep = MAHADI in state.battlefield or PLUNDERER in state.battlefield
        antes_dic = state.treasure_farm_dictate_total
        orig_farm(state)
        feito = state.treasure_farm_total - antes
        if feito > animados or (not com_rep and feito > estoque // 2):
            viol_farm += 1
    V.end_step, V.farm_animated_treasures = et, fm
    for i in range(n):
        s = fn(seed0 + i)
        farm_total += s.treasure_farm_total
        farm_dic += s.treasure_farm_dictate_total
        zonas = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + [c for c, _ in s.impulse_pool] + [c for c, _ in s.impulse_lands])
        if any(zonas[k] > v for k, v in base.items()):
            dup += 1
    V.end_step, V.farm_animated_treasures = orig_et, orig_farm
    return dup, viol_alive, viol_farm, farm_total, farm_dic
for modo_jogo in ("padrao", "resiliencia"):
    dup, va, vf, ft, fd = jogos(1500, 1_000_000, modo_jogo)
    teste(f"I1 ({modo_jogo}, 1.500 jogos) nenhuma carta duplicada, 0 'animados vivos' no fim do turno, o farm nunca acima dos animados nem (so' Dictate) acima da metade do estoque", dup == 0 and va == 0 and vf == 0 and ft > 0, str((dup, va, vf, ft)))
    print(f"   info I1 {modo_jogo}: Treasures-criatura sacrificados pelo farm em 1.500 jogos: {ft} (so' por causa do Dictate: {fd})")

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)

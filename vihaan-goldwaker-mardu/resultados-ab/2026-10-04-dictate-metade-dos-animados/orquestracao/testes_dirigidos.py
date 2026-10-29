"""Testes dirigidos da 8a rodada (correcao do usuario: "metade dos tesouros animados, tesouros inanimados nao trigam o Dictate"): quando SO' o Dictate of
Erebos justifica o sacrificio dos Treasures animados (sem Mahadi/Pitiless Plunderer, que repoem), o teto e' METADE DOS ANIMADOS vivos (`animados // 2`), nao metade
do estoque: Treasure inanimado nao e' criatura, nao morre como criatura e nao dispara o Dictate. Cada teste monta um GameState a mao e chama a funcao real.
Uso: python3 testes_dirigidos.py"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

V = F.flags(F.carrega(F.DEPOIS, "vih_8a_testes"))
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


def modo(half=True, animados=True, dictate=True):
    F.flags(V, half=half, animados=animados, dictate=dictate)


DICTATE, MAHADI, PLUNDERER = "Dictate of Erebos", "Mahadi, Emporium Master", "Pitiless Plunderer"
s = cena([DICTATE], 10, 10)
V.farm_animated_treasures(s)
teste("A1 so' o Dictate, 10 Treasures todos animados: sacrifica METADE (5): 5 mortes, 5 gatilhos do Dictate (= 15 criaturas de oponente no proxy x3), 5 de reserva",
      s.treasures == 5 and s.creature_deaths_total == 5 and s.dictate_triggers_total == 5 and s.treasure_farm_dictate_total == 5 and s.dictate_triggers_total * V.NUM_OPPONENTS == 15,
      str((s.treasures, s.creature_deaths_total, s.dictate_triggers_total)))
s = cena([DICTATE], 12, 7)
V.farm_animated_treasures(s)
teste("A2 (o caso da correcao) 12 Treasures, 7 animados + 5 inanimados: a metade e' dos ANIMADOS = 3 (nao 6 = metade do estoque); os 5 inanimados ficam intactos e nao disparam nada",
      s.creature_deaths_total == 3 and s.dictate_triggers_total == 3 and s.treasures == 9 and s.treasures_animated_alive == 4 and (s.treasures - s.treasures_animated_alive) == 5,
      str((s.creature_deaths_total, s.dictate_triggers_total, s.treasures, s.treasures_animated_alive)))
s = cena([DICTATE], 12, 4)
V.farm_animated_treasures(s)
teste("A3 12 Treasures, 4 animados: 2 sacrificados (metade de 4), 2 animados e 8 inanimados sobram como reserva", s.creature_deaths_total == 2 and s.treasures == 10 and s.treasures_animated_alive == 2)
s = cena([DICTATE], 9, 7)
V.farm_animated_treasures(s)
teste("A4 animados impar (7): 'ate' metade' = 3 (arredonda pra baixo, nunca mais que a metade)", s.creature_deaths_total == 3 and s.treasures == 6, str((s.creature_deaths_total, s.treasures)))
s = cena([DICTATE], 9, 1)
V.farm_animated_treasures(s)
teste("A5 1 animado entre 9 Treasures: metade = 0, nao sacrifica o unico animado", s.creature_deaths_total == 0 and s.treasures == 9)
s = cena([DICTATE], 12, 12)
V.farm_animated_treasures(s)
teste("A6 escala do T8 da partida (12 Treasures animados): sacrifica 6 (o usuario fez 7 pagando o Dictate, outra coisa)", s.creature_deaths_total == 6 and s.dictate_triggers_total == 6)
modo(animados=False)
s = cena([DICTATE], 12, 7)
V.farm_animated_treasures(s)
teste("A7 chave desta rodada desligada = comportamento da 7a rodada: base = estoque (min(7 animados, 12 // 2 = 6) = 6)", s.creature_deaths_total == 6 and s.treasures == 6, str((s.creature_deaths_total, s.treasures)))
modo(half=False, animados=False)
s = cena([DICTATE], 10, 10)
V.farm_animated_treasures(s)
teste("A8 chaves da 7a e 8a desligadas = comportamento da 6a rodada: so' o Dictate sacrifica TODOS os animados", s.treasures == 0 and s.creature_deaths_total == 10)
modo()
s = cena([DICTATE, MAHADI], 12, 7)
V.farm_animated_treasures(s)
teste("A9 Dictate + Mahadi: o sacrificio e' de graca (o Mahadi repoe) e continua sendo de TODOS os animados (7); contador 'so' Dictate' = 0",
      s.creature_deaths_total == 7 and s.treasure_farm_dictate_total == 0 and s.dictate_triggers_total == 7)
s = cena([DICTATE, PLUNDERER], 12, 7)
V.farm_animated_treasures(s)
teste("A10 Dictate + Pitiless Plunderer: idem, todos os animados", s.creature_deaths_total == 7 and s.treasure_farm_dictate_total == 0)
s = cena([MAHADI], 12, 7)
V.farm_animated_treasures(s)
teste("A11 so' Mahadi (sem Dictate): todos os animados, como na 5a rodada", s.creature_deaths_total == 7)
modo(dictate=False)
s = cena([DICTATE], 10, 10)
V.farm_animated_treasures(s)
teste("A12 farm com Dictate desligado: nada (regra anterior a 6a rodada)", s.treasures == 10 and s.creature_deaths_total == 0)
modo()
s = cena([], 10, 10)
V.farm_animated_treasures(s)
teste("A13 sem Dictate, Mahadi nem Plunderer: nao sacrifica", s.treasures == 10 and s.creature_deaths_total == 0)
# ordem: o Dictate e' pago com os terrenos; so' depois os animados morrem com ele em campo, ate' a metade dos animados
s = V.GameState(hand=[DICTATE], battlefield=["Mountain"] * 5 + [V.COMMANDER], library=["Swamp"] * 30); s.turn = 8; s.commander_in_play = True
s.treasures, s.treasures_animated_alive = 8, 8
V.cast_card(s, DICTATE)
apos_cast = (s.treasures, s.treasures_animated_alive)
V.farm_animated_treasures(s)
teste("A14 ordem: Dictate pago pelos 5 terrenos (os 8 Treasures intactos) e depois 4 animados (metade de 8) morrem com ele em campo = 4 gatilhos", apos_cast == (8, 8) and s.dictate_triggers_total == 4 and s.treasures == 4, str((apos_cast, s.dictate_triggers_total, s.treasures)))
# CR 611.2c: Treasure criado DEPOIS do inicio do combate nao e' animado e nao entra na base da metade
s = novo([DICTATE], lands=0)
s.battlefield.append(DICTATE) if DICTATE not in s.battlefield else None
s.treasures = 8
V.combat_step(s)
animados_no_combate = s.treasures_animated_alive
V.create_treasures(s, 6, "teste_pos_combate")
animados_apos, estoque_apos = s.treasures_animated_alive, s.treasures
V.farm_animated_treasures(s)
teste("A15 8 Treasures animados no combate + 6 criados depois (inanimados): estoque 14, animados 8; sacrifica 4 (metade dos animados), nao 7 (metade do estoque)",
      animados_apos == animados_no_combate == 8 and estoque_apos >= 14 and s.creature_deaths_total == 4 and s.dictate_triggers_total == 4,
      str((animados_no_combate, animados_apos, estoque_apos, s.creature_deaths_total)))
s = V.GameState(hand=[DICTATE], battlefield=["Mountain"] * 6 + [V.COMMANDER], library=["Swamp"] * 30); s.turn = 8; s.commander_in_play = True; s.treasures = 8
V.combat_step(s); V.main_phase(s); V.farm_animated_treasures(s); V.end_step(s)
teste("A16 sequencia real combat_step -> main_phase -> farm -> end_step: 8 animados, Dictate conjurado, 4 sacrificados (metade) e 0 animados vivos no fim", DICTATE in s.battlefield and s.dictate_triggers_total >= 4 and s.treasures_animated_alive == 0, str((DICTATE in s.battlefield, s.dictate_triggers_total)))
s = cena([DICTATE, "Zulaport Cutthroat", "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel"], 14, 12)
V.farm_animated_treasures(s)
teste("A17 integracao: Dictate + Zulaport + Sephiroth, 14 Treasures com 12 animados: 6 sacrificados = 6 gatilhos do Dictate, 6 drains do Zulaport, o Sephiroth vira na 4a morte", s.dictate_triggers_total == 6 and s.life_gained_total >= 6 and s.sephiroth_transformed)

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
        if feito > animados or (not com_rep and feito > animados // 2):
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
    teste(f"I1 ({modo_jogo}, 1.500 jogos) nenhuma carta duplicada, 0 'animados vivos' no fim do turno, o farm nunca acima dos animados nem (so' Dictate) acima da metade dos animados", dup == 0 and va == 0 and vf == 0 and ft > 0, str((dup, va, vf, ft)))
    print(f"   info I1 {modo_jogo}: Treasures-criatura sacrificados pelo farm em 1.500 jogos: {ft} (so' por causa do Dictate: {fd})")

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)

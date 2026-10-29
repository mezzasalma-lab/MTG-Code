"""Testes dirigidos da 9a rodada (wipes proprios: Blood Money / Blasphemous Act), depois da resposta do usuario sobre a Blood Money do T8 que ficou no
exilio ("sem Vihaan e Mahadi em campo acho que seria pior"). Oraculo e rulings lidos ao vivo em 2026-10-04 (`dados/oraculo_rulings_ao_vivo_9a_rodada.json`):
Blood Money = "Destroy all creatures. For each nontoken creature destroyed this way, you create a tapped Treasure token."; Blasphemous Act = "costs {1}
less to cast for each creature on the battlefield. Deals 13 damage to each creature."; Mayhem Devil so' reage a SACRIFICIO; Pitiless Plunderer dispara
pelas outras criaturas que morrem junto (ruling 2018-01-19). Cada teste monta um GameState a mao e chama a funcao real. Uso: python3 testes_dirigidos.py"""
import collections, itertools, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

V = F.flags(F.carrega(F.DEPOIS, "vih_9a_testes"))
res = []
BM, ACT = "Blood Money", "Blasphemous Act"
ZUL, LOTHO, PLUND, MAHADI, MAYHEM = "Zulaport Cutthroat", "Lotho, Corrupt Shirriff", "Pitiless Plunderer", "Mahadi, Emporium Master", "Mayhem Devil"
SEPH = V.SEPHIROTH
OUTROS = ["Olivia, Opulent Outlaw", "Prosper, Tome-Bound", "Magda, the Hoardmaster", "Kambal, Profiteering Mayor"]


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def modo(destroy=True, tapped=True, cost=True, hold=True, tax=True):
    F.flags(V, destroy=destroy, tapped=tapped, cost=cost, hold=hold, tax=tax)


def novo(bf=(), hand=(), lands=0, turn=8, commander=True):
    bf = [n for n in bf if n != V.COMMANDER]
    s = V.GameState(hand=list(hand), battlefield=list(bf) + ["Mountain"] * lands, library=["Swamp"] * 30)
    s.turn = turn
    if commander:
        s.commander_in_play = True
        s.battlefield.append(V.COMMANDER)
    return s


def verifica_criaturas():
    for n in [ZUL, LOTHO, PLUND, MAHADI, MAYHEM, SEPH] + OUTROS + [V.COMMANDER]:
        assert V.is_creature_card(n), n


verifica_criaturas()

# ---------------------------------------------------------------- destruicao de verdade (OWN_WIPE_DESTROY_ORACLE_ENABLED)
modo()
s = novo([ZUL, LOTHO])
V.resolve_instant_sorcery(s, BM)
teste("W1 Blood Money destroi o COMANDANTE tambem (Vihaan e' Legendary Creature): sai do campo, vai a zona de comando (nao fica no cemiterio), 3 mortes",
      V.COMMANDER not in s.battlefield and not s.commander_in_play and V.COMMANDER not in s.graveyard and s.own_wipe_commander_destroyed_total == 1
      and s.creature_deaths_total == 3 and ZUL in s.graveyard and LOTHO in s.graveyard, str((s.battlefield, s.creature_deaths_total)))
teste("W1b 'for each nontoken creature destroyed': 3 nao-fichas (Zulaport, Lotho e o Vihaan) = 3 Treasures, todos VIRADOS",
      s.treasures == 3 and s.treasures_tapped == 3, str((s.treasures, s.treasures_tapped)))
modo(destroy=False, tapped=False)
s = novo([ZUL, LOTHO])
V.resolve_instant_sorcery(s, BM)
teste("W1c chave desligada = codigo antigo: o comandante SOBREVIVE ao 'destroy all creatures' e so' 2 Treasures, desvirados", V.COMMANDER in s.battlefield and s.commander_in_play and s.treasures == 2 and s.treasures_tapped == 0)

modo()
s = novo(["Olivia, Opulent Outlaw", "Prosper, Tome-Bound", MAYHEM])
V.resolve_instant_sorcery(s, BM)
d_novo = s.drain_damage_total
modo(destroy=False)
s = novo(["Olivia, Opulent Outlaw", "Prosper, Tome-Bound", MAYHEM])
V.resolve_instant_sorcery(s, BM)
teste("W2 destroy != sacrifice: Mayhem Devil ('whenever a player SACRIFICES a permanent') NAO reage a Blood Money (0 de dano); o codigo antigo o disparava",
      d_novo == 0 and s.drain_damage_total > 0, str((d_novo, s.drain_damage_total)))
modo()
s = novo(["Olivia, Opulent Outlaw", MAYHEM])
V.resolve_instant_sorcery(s, ACT)
teste("W2b idem na Blasphemous Act (13 de dano, nao e' sacrificio): 0 de dano do Mayhem Devil", s.drain_damage_total == 0, str(s.drain_damage_total))

modo()
s = novo([PLUND])
s.treasures, s.treasures_animated_alive = 10, 6
s.battlefield.append("Dictate of Erebos")
V.resolve_instant_sorcery(s, BM)
teste("W3 Blood Money destroi os Treasures ANIMADOS vivos (sao criaturas ate' o fim do turno, ficha = sem Treasure por eles) e nao os conta como sacrificados: 6 destruidos + Plunderer e Vihaan",
      s.treasures_animated_alive == 0 and s.dictate_triggers_total == 8 and s.treasures_sacrificed_total == 0 and s.creature_deaths_total == 8,
      str((s.treasures_animated_alive, s.dictate_triggers_total, s.treasures_sacrificed_total, s.creature_deaths_total, s.treasures)))
# 10 Treasures - 6 animados = 4; o Plunderer dispara por cada OUTRA criatura que morre junto (o Vihaan e os 6 Treasures animados, que sao criaturas) = +7;
# a Blood Money cria 1 virado por nao-ficha destruida (Plunderer e Vihaan) = +2  ->  13, dos quais 2 virados
teste("W3b contas dos Treasures: 10 - 6 destruidos = 4, + 7 do Plunderer (Vihaan e os 6 animados morrem junto; nunca pela propria morte) + 2 virados da Blood Money (Plunderer, Vihaan) = 13, dos quais 2 virados",
      s.treasures == 13 and s.treasures_tapped == 2, str((s.treasures, s.treasures_tapped)))

# mortes simultaneas: o resultado nao pode depender da ordem das pecas no campo
modo()
vidas, tesouros = set(), set()
for perm in itertools.permutations([ZUL, LOTHO, "Olivia, Opulent Outlaw"]):
    s = novo(list(perm))
    V.resolve_instant_sorcery(s, BM)
    vidas.add((s.life_gained_total, s.drain_damage_total))
for perm in itertools.permutations([PLUND, LOTHO, "Olivia, Opulent Outlaw"]):
    s = novo(list(perm))
    V.resolve_instant_sorcery(s, BM)
    tesouros.add(s.treasures_created_total)
teste("W4 morte simultanea: o Zulaport dispara pela propria morte e pelas outras (4 mortes = 4 de vida e 4 de dreno) em QUALQUER ordem do campo", vidas == {(4, 4)}, str(vidas))
teste("W4b o Plunderer dispara pelas OUTRAS que morrem junto (3: Lotho, Olivia, Vihaan), nunca por si, em qualquer ordem; + 4 virados da Blood Money = 7 Treasures criados", tesouros == {7}, str(tesouros))
modo(destroy=False)
vidas_antigo = set()
for perm in itertools.permutations([ZUL, LOTHO, "Olivia, Opulent Outlaw"]):
    s = novo(list(perm))
    V.resolve_instant_sorcery(s, BM)
    vidas_antigo.add(s.life_gained_total)
teste("W4c o codigo antigo (chave desligada) dependia da ordem: o numero de gatilhos do Zulaport variava com a posicao dele no campo", len(vidas_antigo) > 1, str(vidas_antigo))
modo()
s = novo([PLUND])
V.on_creature_dies(s, 1, False, dying=PLUND)
teste("W5 'another creature': o Plunderer (ainda em campo durante a propria morte simultanea) nao cria Treasure pela propria morte", s.treasures == 0)

# Sephiroth continua certo dentro do wipe novo (mortes simultaneas, ruling 2025-06-06)
modo()
s = novo([SEPH] + OUTROS)
V.resolve_instant_sorcery(s, BM)
teste("W6 Sephiroth + 4 criaturas + Vihaan num wipe: ele morre junto, entao NAO vira (sem emblema); o gatilho da frente dispara pelas outras 5 e nunca pela propria morte",
      not s.sephiroth_transformed and s.super_nova_emblems == 0 and s.life_gained_total == 5 and s.drain_damage_total == 5, str((s.sephiroth_transformed, s.super_nova_emblems, s.life_gained_total, s.drain_damage_total)))

modo()
s = novo([MAHADI, LOTHO, "Olivia, Opulent Outlaw"])
V.resolve_instant_sorcery(s, BM)
antes_end = s.treasures_created_total
V.end_step(s)
teste("W7 o Mahadi morre no wipe: no end step ele nao cria Treasure por morte nenhuma", s.treasures_created_total == antes_end and MAHADI not in s.battlefield, str((antes_end, s.treasures_created_total)))

# ---------------------------------------------------------------- Treasure virado (BLOOD_MONEY_TAPPED_TREASURE_ENABLED)
modo()
s = novo([LOTHO, "Olivia, Opulent Outlaw"])
V.resolve_instant_sorcery(s, BM)
total_virado = V.total_mana(s)
modo(tapped=False)
s2 = novo([LOTHO, "Olivia, Opulent Outlaw"])
V.resolve_instant_sorcery(s2, BM)
teste("W8 Treasure virado nao paga mana no turno: 3 virados = 0 de mana (com a chave desligada pagariam 3)", total_virado == 0 and V.total_mana(s2) == 3, str((total_virado, V.total_mana(s2))))
modo()
s = novo([DICT := "Dictate of Erebos"])
s.treasures, s.treasures_tapped, s.treasures_animated_alive = 6, 5, 6
V.farm_animated_treasures(s)
teste("W8b o farm usa a habilidade de mana ({T}, Sacrifice): so' desvirado (6 animados, 5 virados -> 1 sacrificado)", s.creature_deaths_total == 1 and s.treasures == 5 and s.treasures_tapped == 5, str((s.creature_deaths_total, s.treasures, s.treasures_tapped)))
s = novo()
s.treasures, s.treasures_tapped = 5, 3
V.sacrifice_treasures(s, 2)
a = (s.treasures, s.treasures_tapped)
V.sacrifice_treasures(s, 2, for_mana=True)
teste("W8c sacrificio fora da mana leva os virados primeiro (5/3 -> 3/1); pra mana, so' os desvirados (3/1 -> 1/1)", a == (3, 1) and (s.treasures, s.treasures_tapped) == (1, 1), str((a, s.treasures, s.treasures_tapped)))
s = novo([LOTHO])
s.treasures, s.treasures_tapped = 4, 4
s.turn = 4
s.library = ["Swamp"] * 40
V.play_turn(s, False, True)
teste("W8d untap: os Treasures virados desviram no meu proximo turno (tapped = 0 no inicio)", s.treasures_tapped == 0)
modo()
s = novo()
s.treasures, s.treasures_tapped = 5, 5
V.combat_step(s)
a = s.combat_attacks_total
s = novo()
s.treasures, s.treasures_tapped = 5, 2
V.combat_step(s)
teste("W8e Treasure animado virado nao ataca: 5 animados todos virados = sem ataque; com 2 virados atacam 3 (9 de dano no proxy)", a == 0 and s.combat_attacks_total == 1 and s.combat_damage_proxy_total >= 9, str((a, s.combat_attacks_total, s.combat_damage_proxy_total)))

# ---------------------------------------------------------------- custo da Blasphemous Act (BLASPHEMOUS_ACT_COST_REDUCTION_ENABLED)
modo()
s = novo(commander=False)
c0 = V.spell_cost(s, ACT)
s = novo([ZUL, LOTHO, "Olivia, Opulent Outlaw"])
c4 = V.spell_cost(s, ACT)
s = novo([ZUL, LOTHO, "Olivia, Opulent Outlaw"])
s.constructs, s.other_tokens, s.dragons, s.treasures_animated_alive = 2, 3, 1, 4
c_tokens = V.spell_cost(s, ACT)
modo(cost=False)
c_off = V.spell_cost(s, ACT)
modo()
teste("W9 Blasphemous Act: {1} a menos por criatura minha em campo: 0 criaturas = 9; 4 (3 + Vihaan) = 5; 14 (com Constructs, fichas, Dragao e Treasures animados) = piso {R} = 1; desligada = 9",
      (c0, c4, c_tokens, c_off) == (9, 5, 1, 9), str((c0, c4, c_tokens, c_off)))
s = novo([ZUL, LOTHO, "Olivia, Opulent Outlaw"], lands=5)
teste("W9b custo 5 com 5 terrenos: conjuravel; com 4 terrenos nao", V.can_cast(s, ACT) and not V.can_cast(novo([ZUL, LOTHO, "Olivia, Opulent Outlaw"], lands=4), ACT))
modo(hold=False)
s = novo([ZUL, LOTHO, "Olivia, Opulent Outlaw"], hand=[ACT], lands=5)
V.cast_card(s, ACT)
teste("W9c o cast cobra o custo reduzido (5 de 5 terrenos) e a Blasphemous Act sai da mao e destroi tudo, comandante inclusive, SEM criar Treasure", s.mana_spent_this_turn == 5 and ACT in s.graveyard and not s.commander_in_play and s.treasures == 0 and s.creature_deaths_total == 4, str((s.mana_spent_this_turn, s.commander_in_play, s.treasures, s.creature_deaths_total)))
modo()

# ---------------------------------------------------------------- linha do usuario (OWN_WIPE_HOLD_ENGINE_ENABLED)
def sem_comandante(cast_count=10):
    s = novo([LOTHO], hand=[BM], lands=8, commander=False)
    s.commander_cast_count = cast_count  # imposto do comandante enorme: nunca e' recastado nesta cena
    return s


modo()
s = novo([LOTHO], hand=[BM], lands=8)
V.main_phase(s)
teste("H1 Vihaan em campo: a Blood Money (7 de mana disponiveis) fica na mao; 1 retencao registrada", BM in s.hand and s.blood_money_cast_total == 0 and s.own_wipe_held_total == 1, str((s.hand, s.own_wipe_held_total)))
s = sem_comandante()
s.battlefield.append(MAHADI)
V.main_phase(s)
teste("H2 so' o Mahadi em campo (comandante na zona de comando): tambem segura", BM in s.hand and s.blood_money_cast_total == 0)
s = sem_comandante()
V.main_phase(s)
teste("H3 sem Vihaan nem Mahadi em campo: conjura (nao ha' motor a perder)", BM in s.graveyard and s.blood_money_cast_total == 1, str((s.hand, s.graveyard)))
s = novo([LOTHO], hand=[ACT], lands=8)
V.main_phase(s)
teste("H4 a mesma retencao vale pra Blasphemous Act (extensao minha da razao do usuario: destruiria os mesmos motores)", ACT in s.hand and s.own_wipes_cast_total == 0)
modo(hold=False)
s = novo([LOTHO], hand=[BM], lands=8)
V.main_phase(s)
teste("H5 chave desligada = comportamento anterior: conjura a Blood Money mesmo com Vihaan em campo (e agora o destroi)", s.blood_money_cast_total == 1 and not s.commander_in_play)
modo()
s = novo([LOTHO], lands=8)
s.impulse_pool.append((BM, s.turn))
ok1 = V.play_from_impulse(s)
s2 = sem_comandante()
s2.hand = []
s2.impulse_pool.append((BM, s2.turn))
ok2 = V.play_from_impulse(s2)
teste("H6 Blood Money exilada (o caso do T8): com Vihaan em campo NAO e' conjurada e fica no pool ate' expirar; sem os motores e' conjurada", (not ok1) and (BM, s.turn) in s.impulse_pool and ok2 and s2.blood_money_cast_total == 1, str((ok1, ok2)))

# ---------------------------------------------------------------- imposto do comandante (COMMANDER_TAX_ENABLED, CR 903.8)
modo()
s = novo(commander=False, lands=4)
s.commander_cast_count = 1
a = V.can_cast(s, V.COMMANDER)  # custo 3 + 2 = 5 com 4 de mana: nao pode
s = novo(commander=False, lands=5)
s.commander_cast_count = 1
b = V.can_cast(s, V.COMMANDER)
modo(tax=False)
s = novo(commander=False, lands=4)
s.commander_cast_count = 1
c = V.can_cast(s, V.COMMANDER)
modo()
teste("X1 imposto do comandante: com 1 cast anterior ele custa 5; com 4 de mana nao e' conjuravel, com 5 e'; a chave desligada (codigo antigo) o deixava conjurar com 3", (a, b, c) == (False, True, True), str((a, b, c)))
s = novo(commander=False, lands=3)
V.main_phase(s)
teste("X1b primeira conjuracao: 3 de mana bastam (imposto 0) e a contagem vai a 1 no cast", s.commander_in_play and s.commander_cast_count == 1, str((s.commander_in_play, s.commander_cast_count)))
s = novo(commander=False, hand=[], lands=6)
orig = V.try_smart_opponent_counter
V.try_smart_opponent_counter = lambda st: True
V.cast_card(s, V.COMMANDER)
V.try_smart_opponent_counter = orig
modo(tax=False)
s2 = novo(commander=False, hand=[], lands=6)
V.try_smart_opponent_counter = lambda st: True
V.cast_card(s2, V.COMMANDER)
V.try_smart_opponent_counter = orig
modo()
teste("X2 CR 903.8: um cast ANULADO tambem soma o imposto (contagem 1, comandante fora de campo); o codigo antigo so' contava quando entrava (contagem 0)",
      s.commander_cast_count == 1 and not s.commander_in_play and s2.commander_cast_count == 0 and not s2.commander_in_play, str((s.commander_cast_count, s2.commander_cast_count)))

# ---------------------------------------------------------------- invariantes em partidas reais
def jogos(n, seed0, modo_jogo, hold):
    F.flags(V, hold=hold)
    fn = V.simulate_one if modo_jogo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    dup = viol_hold = viol_tap = casts = com_motor = 0
    orig_res, orig_et = V.resolve_instant_sorcery, V.end_step
    def res_espia(state, name):
        nonlocal viol_hold, casts, com_motor
        if name in V.OWN_WIPES:
            casts += 1
            if state.commander_in_play or MAHADI in state.battlefield:
                com_motor += 1
                if hold:
                    viol_hold += 1
        return orig_res(state, name)
    def et(state):
        nonlocal viol_tap
        if not (0 <= state.treasures_tapped <= state.treasures):
            viol_tap += 1
        orig_et(state)
    V.resolve_instant_sorcery, V.end_step = res_espia, et
    try:
        for i in range(n):
            s = fn(seed0 + i)
            zonas = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + [c for c, _ in s.impulse_pool] + [c for c, _ in s.impulse_lands])
            if any(zonas[k] > v for k, v in base.items()):
                dup += 1
            if not (0 <= s.treasures_tapped <= s.treasures) or s.treasures < 0:
                viol_tap += 1
    finally:
        V.resolve_instant_sorcery, V.end_step = orig_res, orig_et
    return dup, viol_hold, viol_tap, casts, com_motor
for modo_jogo in ("padrao", "resiliencia"):
    dup, vh, vt, casts, cm = jogos(2000, 1_000_000, modo_jogo, True)
    teste(f"I1 ({modo_jogo}, 2.000 jogos, retencao ligada) nenhuma carta duplicada, tapped sempre entre 0 e o estoque, e NENHUM wipe proprio conjurado com Vihaan/Mahadi em campo", dup == 0 and vt == 0 and vh == 0, str((dup, vh, vt)))
    print(f"   info I1 {modo_jogo}: wipes proprios conjurados com a retencao ligada em 2.000 jogos: {casts}")
    dup, vh, vt, casts2, cm2 = jogos(2000, 1_000_000, modo_jogo, False)
    teste(f"I2 ({modo_jogo}, 2.000 jogos, retencao DESLIGADA) o invariante e' significativo: ha' wipe conjurado com Vihaan/Mahadi em campo, e tapped continua valido", cm2 > 0 and vt == 0 and dup == 0, str((cm2, vt, dup)))
    print(f"   info I2 {modo_jogo}: wipes proprios conjurados sem retencao em 2.000 jogos: {casts2} (com Vihaan/Mahadi em campo: {cm2})")
F.flags(V)

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)

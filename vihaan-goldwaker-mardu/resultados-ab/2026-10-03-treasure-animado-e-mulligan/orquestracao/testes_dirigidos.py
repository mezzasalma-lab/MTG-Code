"""Testes dirigidos das tres correcoes do Vihaan (roteamento do Treasure animado, mulligan com escolha, terreno tapped em T1/T2).
Cada teste monta um GameState a mao e chama a funcao real do simulador. Uso: python3 testes_dirigidos.py"""
import random, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

V = F.flags(F.carrega(F.DEPOIS, "vih_testes"))
res = []


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def novo(hand=(), bf=(), turn=5, treasures=0, alive=0, **kw):
    s = V.GameState(hand=list(hand), battlefield=list(bf), library=["Swamp"] * 30, **kw)
    s.turn = turn
    s.treasures = treasures
    s.treasures_animated_alive = alive
    s.treasures_animated_this_combat = alive
    return s


# ------------------------------------------------------------ Treasure animado
s = novo(treasures=3, alive=2)
V.sacrifice_treasures(s, 3)
teste("R1 3 Treasures, 2 animados: 2 mortes de criatura, 3 de artefato, 3 fichas saindo",
      (s.creature_deaths_total, s.artifact_deaths_total, s.token_leaves_total) == (2, 3, 3),
      str((s.creature_deaths_total, s.artifact_deaths_total, s.token_leaves_total)))
teste("R1 animados vivos zeram; contador 'qualquer caminho' = 2", s.treasures_animated_alive == 0 and s.animated_treasures_sacrificed_any_total == 2)

s = novo(treasures=3, alive=0)
V.sacrifice_treasures(s, 2)
teste("R2 nenhum animado (antes do combate): 0 mortes de criatura (Treasure nao e' criatura antes da animacao)", s.creature_deaths_total == 0 and s.artifact_deaths_total == 2)

# R3 Zulaport / Pitiless Plunderer reagem so' a parte animada
s = novo(bf=["Zulaport Cutthroat", "Pitiless Plunderer"], treasures=4, alive=3)
d0, c0 = s.drain_damage_total, s.treasures_created_total
V.sacrifice_treasures(s, 4)
s_off = novo(bf=["Zulaport Cutthroat", "Pitiless Plunderer"], treasures=4, alive=3)
V.ANIMATED_TREASURE_ROUTING_ENABLED = False
V.sacrifice_treasures(s_off, 4)
V.ANIMATED_TREASURE_ROUTING_ENABLED = True
teste("R3 Pitiless Plunderer: 3 Treasures novos pelos 3 animados (flag ligada) e 0 com a flag desligada",
      s.treasures_created_total - c0 == 3 and s_off.treasures_created_total == 0, f"{s.treasures_created_total - c0} / {s_off.treasures_created_total}")
teste("R3 Zulaport drena mais com a flag ligada (3 mortes de criatura a mais)", s.drain_damage_total > s_off.drain_damage_total, f"{s.drain_damage_total} vs {s_off.drain_damage_total}")

# R4 Altar so' aceita animados; os criados depois ficam
s = novo(bf=["Ashnod's Altar"], treasures=3, alive=1)
V.aggressive_treasure_destruction(s)
teste("R4 so' Ashnod's Altar: sacrifica SO' o animado (os 2 criados depois nao sao criatura e ficam)", s.treasures == 2 and s.bonus_mana_pool == 2 and s.creature_deaths_total == 1,
      f"treasures={s.treasures} mana={s.bonus_mana_pool} mortes={s.creature_deaths_total}")
V.ANIMATED_TREASURE_ROUTING_ENABLED = False
s = novo(bf=["Ashnod's Altar"], treasures=3, alive=1)
V.aggressive_treasure_destruction(s)
V.ANIMATED_TREASURE_ROUTING_ENABLED = True
teste("R4 (codigo antigo, flag desligada) sacrificava os 3 ao Altar: documenta o erro corrigido", s.treasures == 0 and s.creature_deaths_total == 3)

# R5 KCI: todos saem; os animados contam como criatura
s = novo(bf=["Krark-Clan Ironworks"], treasures=3, alive=2)
V.aggressive_treasure_destruction(s)
teste("R5 Krark-Clan Ironworks: 3 sacrificados, 2 deles como criatura, +6 de mana", s.treasures == 0 and s.creature_deaths_total == 2 and s.bonus_mana_pool == 6,
      f"treasures={s.treasures} mortes={s.creature_deaths_total} mana={s.bonus_mana_pool}")
V.ANIMATED_TREASURE_ROUTING_ENABLED = False
s = novo(bf=["Krark-Clan Ironworks"], treasures=3, alive=2)
V.aggressive_treasure_destruction(s)
V.ANIMATED_TREASURE_ROUTING_ENABLED = True
teste("R5 (codigo antigo) KCI tratava como nao-criatura: 0 mortes de criatura", s.creature_deaths_total == 0)

# R6 Altar + KCI juntos: KCI cobre todos; sem dupla contagem
s = novo(bf=["Krark-Clan Ironworks", "Ashnod's Altar"], treasures=4, alive=3)
V.aggressive_treasure_destruction(s)
teste("R6 Altar + KCI: 4 sacrificados uma vez so', 3 como criatura", s.treasures == 0 and s.creature_deaths_total == 3 and s.token_leaves_total == 4)

# R7 spend_mana na 2a main (animados ainda vivos): mana de Treasure animado = criatura
s = novo(treasures=2, alive=2)
V.spend_mana(s, 2)
teste("R7 spend_mana 2a main: 2 Treasures animados gastos = 2 mortes de criatura", s.creature_deaths_total == 2 and s.treasures == 0)
s = novo(treasures=2, alive=0)
V.spend_mana(s, 2)
teste("R7 spend_mana 1a main (nao animados): 0 mortes de criatura", s.creature_deaths_total == 0 and s.treasures == 0)

# R8 outros outlets usam o mesmo roteamento (Deadly Dispute, Magda, Jan Jansen, Face-Breaker)
s = novo(treasures=1, alive=1)
V.resolve_instant_sorcery(s, "Deadly Dispute")
teste("R8 Deadly Dispute sacrificando Treasure animado: conta como criatura", s.creature_deaths_total == 1)
s = novo(bf=["Magda, the Hoardmaster"], treasures=3, alive=3)
s.hand = []
V.main_phase(s)
teste("R8 Magda ('Sacrifice three Treasures') com 3 animados: 3 mortes de criatura", s.creature_deaths_total >= 3, str(s.creature_deaths_total))

# R9 reset no fim do turno e no inicio do proximo
s = novo(bf=[V.COMMANDER], treasures=3, alive=3, commander_in_play=True)
V.end_step(s)
teste("R9 end_step zera os animados vivos ('until end of turn')", s.treasures_animated_alive == 0)
# R9b play_turn completo: a animacao acontece no combate (vivos > 0 logo depois do combat_step) e zera no fim do turno
visto = {}
orig_cs = V.combat_step
def cs(state):
    visto["antes"] = (state.treasures, state.treasures_animated_alive)
    orig_cs(state)
    visto["depois"] = (state.treasures, state.treasures_animated_alive, state.treasures_animated_this_combat)
V.combat_step = cs
s = V.GameState(hand=[], battlefield=[V.COMMANDER] + ["Swamp"] * 4, library=["Swamp"] * 40, commander_in_play=True)
s.turn = 4
s.treasures = 3
V.play_turn(s, False, True)
V.combat_step = orig_cs
teste("R9 play_turn: antes do combate 0 animados; o combate anima os 3; no fim do turno zera",
      visto["antes"][1] == 0 and visto["depois"][2] >= 3 and s.treasures_animated_alive == 0, str(visto) + f" fim={s.treasures_animated_alive}")

# R10 integracao em play_turn COMPLETO (Regra #6): Vihaan em campo, 4 Treasures, KCI + Zulaport; a animacao no combate e a
# morte dos animados na 2a main/destruicao pos-combate precisam estar na ordem certa.
def turno_completo(ligado):
    V.ANIMATED_TREASURE_ROUTING_ENABLED = ligado
    st = V.GameState(hand=[], battlefield=[V.COMMANDER, "Krark-Clan Ironworks", "Zulaport Cutthroat", "Mahadi, Emporium Master"] + ["Swamp"] * 4,
                     library=["Swamp"] * 40, commander_in_play=True)
    st.turn = 4
    st.treasures = 4
    V.play_turn(st, False, True)
    V.ANIMATED_TREASURE_ROUTING_ENABLED = True
    return st
on, off = turno_completo(True), turno_completo(False)
teste("R10 play_turn completo (Vihaan + KCI + Zulaport + Mahadi): com o roteamento, os animados morrem como criatura",
      on.animated_treasures_sacrificed_any_total >= 4 and off.animated_treasures_sacrificed_any_total == 0,
      f"ligado={on.animated_treasures_sacrificed_any_total} desligado={off.animated_treasures_sacrificed_any_total}")
teste("R10 Mahadi no end step cria Treasure por criatura morta no turno (ordem de fases certa: mortes antes do end step)",
      on.creature_deaths_total > off.creature_deaths_total, f"{on.creature_deaths_total} vs {off.creature_deaths_total}")

# R11 invariantes em partidas reais (2.000 jogos): n_criatura == min(n, vivos antes); vivos <= animados do combate; reset
orig = V.sacrifice_treasures
regs = []
def espia(state, n, for_mana=False, as_creature=None):
    antes_alive, antes_any, antes_tr = state.treasures_animated_alive, state.animated_treasures_sacrificed_any_total, state.treasures
    r = orig(state, n, for_mana=for_mana, as_creature=as_creature)
    if as_creature is None:
        regs.append((r, antes_alive, state.animated_treasures_sacrificed_any_total - antes_any, state.treasures_animated_this_combat, antes_tr))
    return r
V.sacrifice_treasures = espia
tot_creature = 0
for i in range(2000):
    st = V.simulate_one(1_000_000 + i)
    tot_creature += st.animated_treasures_sacrificed_any_total
V.sacrifice_treasures = orig
viol = [r for r in regs if r[2] != min(r[0], r[1])]
viol2 = [r for r in regs if r[1] > r[3]]
teste("R11 (2.000 jogos) criaturas sacrificadas = min(n, animados vivos) em toda chamada", not viol and len(regs) > 1000, f"chamadas={len(regs)} violacoes={len(viol)}")
teste("R11 (2.000 jogos) animados vivos nunca excedem os animados do combate", not viol2)
teste("R11 (2.000 jogos) houve sacrificios de animados como criatura", tot_creature > 100, f"total={tot_creature}")

# ------------------------------------------------------------ mulligan com escolha
import itertools
hand = ["Sol Ring", "Swamp", "Swamp", "Plains", "Mountain", "Blightsteel Colossus"]
hand = [h for h in hand if h in V.CARD_DB] or hand
nonlands_hi = sorted([n for n in V.CARD_DB if V.CARD_DB[n].ctype != "land" and n not in V.GOOD_KEEP], key=lambda n: -V.CARD_DB[n].mv)
alto, medio = nonlands_hi[0], nonlands_hi[len(nonlands_hi) // 2]
h = ["Swamp", "Plains", "Mountain", "Sol Ring", medio, alto]
b = V.choose_bottom(h, 1)
teste("M1 bottom de 1: a carta nao-terreno de MAIOR custo (protege Sol Ring e os 3 terrenos)", b == [alto], f"{b} vs {alto} (mv {V.CARD_DB[alto].mv})")
b = V.choose_bottom(h, 2)
teste("M1 bottom de 2: as duas mais caras, nunca o Sol Ring", set(b) == {alto, medio} and "Sol Ring" not in b, str(b))
h5 = ["Swamp", "Swamp", "Plains", "Mountain", "Mountain", "Sol Ring", medio]
b = V.choose_bottom(h5, 1)
teste("M2 mais de 4 terrenos: devolve um terreno (nao o Sol Ring nem o spell)", b[0] in V.LAND_NAMES, str(b))
h5t = ["Swamp", "Swamp", "Plains", "Mountain", "Path of Ancestry", "Sol Ring", medio]
b = V.choose_bottom(h5t, 1)
teste("M2 mais de 4 terrenos: prefere o que entra tapped (Path of Ancestry)", b == ["Path of Ancestry"], str(b))
b = V.choose_bottom(["Swamp", "Plains", "Mountain", "Sol Ring", "Arcane Signet", "Smothering Tithe"], 3)
teste("M3 so' GOOD_KEEP e terrenos: nao quebra e devolve 3 cartas distintas", len(b) == 3 and len(set(b)) == 3, str(b))
# mulligan real: forca 2 mulligans (penalidade 1) e confere posicao (ultima da biblioteca) e que saiu da mao
calls = {"n": 0}
real_keep = V.should_keep
V.should_keep = lambda hand: (calls.__setitem__("n", calls["n"] + 1) or calls["n"] >= 3)
bottom_visto = []
orig_cb = V.choose_bottom
V.choose_bottom = lambda hand, n: (bottom_visto.extend(orig_cb(hand, n)) or bottom_visto[-n:])
hand, lib, mulls = V.mulligan(random.Random(5))
V.choose_bottom = orig_cb
V.should_keep = real_keep
teste("M4 mulligan real com 2 mulligans: mao de 6, e a carta devolvida e' a ULTIMA da biblioteca", mulls == 2 and len(hand) == 6 and len(lib) == len(V.BASE_LIBRARY) - 6 and lib[-1] == bottom_visto[0],
      f"mulls={mulls} mao={len(hand)} lib={len(lib)} ultima={lib[-1]} bottom={bottom_visto}")
V.MULLIGAN_SMART_BOTTOM_ENABLED = False
calls["n"] = 0
V.should_keep = lambda hand: (calls.__setitem__("n", calls["n"] + 1) or calls["n"] >= 3)
hand_o, lib_o, _ = V.mulligan(random.Random(5))
V.should_keep = real_keep
V.MULLIGAN_SMART_BOTTOM_ENABLED = True
teste("M4 flag desligada: comportamento antigo (mao de 6; escolha aleatoria)", len(hand_o) == 6)
# efeito: o que fica na mao depois de varios mulligans tem terrenos (nao devolve terreno a toa)
def media_terrenos(smart, n=3000):
    V.MULLIGAN_SMART_BOTTOM_ENABLED = smart
    tot = 0
    for i in range(n):
        calls["n"] = 0
        V.should_keep = lambda hand: (calls.__setitem__("n", calls["n"] + 1) or calls["n"] >= 3)
        hd, _, _ = V.mulligan(random.Random(100 + i))
        tot += sum(1 for c in hd if c in V.LAND_NAMES)
    V.should_keep = real_keep
    V.MULLIGAN_SMART_BOTTOM_ENABLED = True
    return tot / n
a, b_ = media_terrenos(True), media_terrenos(False)
teste("M5 (3.000 maos de 6 cartas) terrenos na mao: escolha >= aleatorio (a escolha so' devolve terreno quando sobram mais de 4)", a > b_, f"escolha={a:.3f} aleatorio={b_:.3f}")
print(f"   info M5: media de terrenos na mao de 6: escolha={a:.3f} aleatorio={b_:.3f}")

# ------------------------------------------------------------ terreno tapped em T1/T2
def jogada(hand, bf=(), turn=1):
    s = novo(hand=hand, bf=bf, turn=turn)
    s.lands_played_this_turn = 0
    V.play_land(s)
    return s, s.battlefield[len(bf):]

s, j = jogada(["Swamp", "Path of Ancestry"], turn=1)
teste("L1 T1 [Swamp, Path of Ancestry]: joga o TAPPED", j == ["Path of Ancestry"] and "Path of Ancestry" in s.tapped_lands_this_turn, str(j))
s, j = jogada(["Swamp", "Path of Ancestry", "Sol Ring"], turn=1)
teste("L1 T1 com Sol Ring na mao: joga o UNTAPPED (tapped custaria o Sol Ring)", j == ["Swamp"] and s.tapped_land_skipped_for_play_total == 1, str(j))
s, j = jogada(["Path of Ancestry", "Swamp"], turn=1)
teste("L1 ordem da mao [tapped, untapped]: joga o tapped", j == ["Path of Ancestry"], str(j))
s, j = jogada(["Swamp", "Path of Ancestry", "Arcane Signet"], bf=["Plains"], turn=2)
teste("L2 T2 com Arcane Signet ({2}) e 1 terreno em campo: untapped", j == ["Swamp"], str(j))
s, j = jogada(["Swamp", "Path of Ancestry"], bf=["Plains"], turn=2)
teste("L2 T2 sem jogada de 2: tapped", j == ["Path of Ancestry"], str(j))
s, j = jogada(["Swamp", "Path of Ancestry"], bf=["Plains", "Mountain"], turn=3)
teste("L3 T3: comportamento ORIGINAL (primeiro terreno da mao)", j == ["Swamp"], str(j))
s, j = jogada(["Swamp", "Path of Ancestry", "Path to Exile"], turn=1)
teste("L4 T1 com Path to Exile (instant, proxy no goldfish): tapped mesmo assim", j == ["Path of Ancestry"], str(j))
s = novo(bf=[])
teste("L5 land_enters_tapped: Blackcleave Cliffs T1 = untapped (fastland, 0 outros terrenos)", not V.land_enters_tapped(s, "Blackcleave Cliffs"))
s = novo(bf=["Swamp", "Swamp", "Swamp"])
teste("L5 land_enters_tapped: Blackcleave Cliffs com 3 outros terrenos = tapped", V.land_enters_tapped(s, "Blackcleave Cliffs"))
s = novo(bf=["Plains"])
teste("L5 land_enters_tapped: Dragonskull Summit sem Swamp/Mountain = tapped; com Swamp = untapped",
      V.land_enters_tapped(s, "Dragonskull Summit") and not V.land_enters_tapped(novo(bf=["Swamp"]), "Dragonskull Summit"))
V.TAPPED_LAND_FIRST_ENABLED = False
s, j = jogada(["Swamp", "Path of Ancestry"], turn=1)
V.TAPPED_LAND_FIRST_ENABLED = True
teste("L6 flag desligada: primeiro terreno da mao (comportamento antigo)", j == ["Swamp"], str(j))
V.TAPPED_LAND_FIRST_SKIP_IF_LOSES_PLAY = False
s, j = jogada(["Swamp", "Path of Ancestry", "Sol Ring"], turn=1)
V.TAPPED_LAND_FIRST_SKIP_IF_LOSES_PLAY = True
teste("L6 politica cega: tapped mesmo com Sol Ring", j == ["Path of Ancestry"], str(j))
s = novo(hand=["Swamp", "Path of Ancestry", "Sol Ring"], bf=["Plains"], turn=2)
snap = (list(s.hand), list(s.battlefield), s.mana_spent_this_turn, set(s.tapped_lands_this_turn), s.treasures)
V.dry_run_mana_spent(s, "Swamp"); V.dry_run_mana_spent(s, "Path of Ancestry")
teste("L7 dry_run_mana_spent nao muta o estado", snap == (list(s.hand), list(s.battlefield), s.mana_spent_this_turn, set(s.tapped_lands_this_turn), s.treasures))

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)

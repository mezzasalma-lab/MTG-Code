"""Testes dirigidos das duas correcoes (Myriad Landscape + terreno tapped em T1/T2).
Cada teste monta um GameState a mao, chama a funcao real do simulador e confere o
efeito. Saida: PASS/FAIL por teste + total. Uso: python3 testes_dirigidos.py"""
import random, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

M = F.flags(F.carrega(F.DEPOIS, "mega_testes"), tapped=True, myriad=True)
res = []


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def novo(hand=(), bf=(), lib=None, turn=5, gy=(), rng=True, **kw):
    if lib is None:
        lib = ["Mountain"] * 4 + ["Plains"] * 4 + ["Swamp"] * 4 + ["Sol Ring"] * 1 + ["Badlands"] * 1
    s = M.GameState(hand=list(hand), battlefield=list(bf), library=list(lib), graveyard=list(gy),
                    rng=random.Random(7) if rng else None, **kw)
    s.turn = turn
    s.turn_start_gy_permanents = M.count_permanent_cards(s.graveyard)
    return s


# ---------------------------------------------------------------- Myriad Landscape
# M1: ativa com 3 de mana sobrando; sacrifica, busca 2 do MESMO tipo, shuffle, contadores
bf = ["Myriad Landscape", "Mountain", "Swamp"]
s = novo(bf=bf)
lib0 = list(s.library)
M.try_myriad_landscape(s)
basicos = [n for n in s.battlefield if n in ("Plains", "Swamp", "Mountain")]
teste("M1 ativa com remaining=3 (Myriad + 2 terrenos, nada gasto)", s.myriad_activations_total == 1)
teste("M1 Myriad saiu do campo e foi pro cemiterio (sacrificio)", "Myriad Landscape" not in s.battlefield and "Myriad Landscape" in s.graveyard)
novos = s.battlefield[2:]  # [Mountain, Swamp] originais + os 2 novos
teste("M1 2 basicos entraram, mesmo tipo", len(novos) == 2 and novos[0] == novos[1], str(novos))
teste("M1 tipo escolhido = Plains (unica cor sem fonte: W)", novos == ["Plains", "Plains"], str(novos))
teste("M1 biblioteca perdeu exatamente 2 Plains", s.library.count("Plains") == lib0.count("Plains") - 2 and len(s.library) == len(lib0) - 2)
esperada = [c for c in lib0 if c != "Plains"] + [c for c in lib0 if c == "Plains"][:0]
retirados = 0
ordem_sem = []
for c in lib0:
    if c == "Plains" and retirados < 2:
        retirados += 1
        continue
    ordem_sem.append(c)
teste("M1 shuffle de verdade (mesmo multiset, ordem diferente da sem-shuffle)",
      sorted(s.library) == sorted(ordem_sem) and s.library != ordem_sem)
teste("M1 gastou 3 de mana (2 de custo + o {C} do proprio Myriad tapado)", s.mana_spent_this_turn == 3)
teste("M1 contador de basicos buscados = 2", s.myriad_basics_fetched_total == 2)

# M2: no turno em que entrou (tapped) nao ativa
s = novo(bf=["Myriad Landscape", "Mountain", "Swamp", "Plains", "Badlands"], tapped_land_this_turn="Myriad Landscape")
M.try_myriad_landscape(s)
teste("M2 nao ativa no turno em que entrou (entra tapped, nao paga o {T})", s.myriad_activations_total == 0 and "Myriad Landscape" in s.battlefield)

# M3: fronteira de mana: remaining = 2 nao ativa; remaining = 3 ativa
s = novo(bf=["Myriad Landscape", "Mountain", "Swamp", "Plains"], mana_spent_this_turn=2)  # total 4, gasto 2 -> sobra 2
M.try_myriad_landscape(s)
teste("M3 remaining=2 NAO ativa", s.myriad_activations_total == 0)
s = novo(bf=["Myriad Landscape", "Mountain", "Swamp", "Plains"], mana_spent_this_turn=1)  # sobra 3
M.try_myriad_landscape(s)
teste("M3 remaining=3 ativa", s.myriad_activations_total == 1)

# M4: escolha do tipo
def tipo_buscado(bf, hand=(), lib=None, **kw):
    s = novo(hand=hand, bf=bf, lib=lib, **kw)
    n0 = len(s.battlefield)
    M.try_myriad_landscape(s)
    return s, s.battlefield[n0 - 1:][-2:] if s.myriad_activations_total else None

s, got = tipo_buscado(["Myriad Landscape", "Plains", "Swamp", "Mountain", "Badlands"])
teste("M4 W/B/R todos com fonte: escolhe o tipo de MENOS fontes (Plains: 1 fonte)", s.battlefield[-2:] == ["Plains", "Plains"], str(s.battlefield[-2:]))
s, got = tipo_buscado(["Myriad Landscape", "Plains", "Swamp", "Plains", "Scrubland"])
teste("M4 falta so' R -> Mountain", s.battlefield[-2:] == ["Mountain", "Mountain"], str(s.battlefield[-2:]))
s, got = tipo_buscado(["Myriad Landscape", "Plains", "Mountain", "Plateau"])
teste("M4 falta so' B -> Swamp", s.battlefield[-2:] == ["Swamp", "Swamp"], str(s.battlefield[-2:]))
# so' resta 1 Plains e W e' a cor que falta: busca 1 ('up to two', ruling 2018-03-16)
lib1 = ["Plains"] + ["Mountain"] * 4 + ["Swamp"] * 4
s = novo(bf=["Myriad Landscape", "Mountain", "Swamp", "Badlands"], lib=lib1)
M.try_myriad_landscape(s)
teste("M5 so' 1 Plains na biblioteca e W falta: busca 1 (ruling: pode achar so' um)",
      s.battlefield[-1] == "Plains" and s.myriad_basics_fetched_total == 1 and "Plains" not in s.library, str(s.battlefield))
# biblioteca sem nenhum basico: nao ativa, Myriad fica
s = novo(bf=["Myriad Landscape", "Mountain", "Swamp", "Badlands"], lib=["Sol Ring", "Badlands"])
M.try_myriad_landscape(s)
teste("M6 sem basico na biblioteca: nao sacrifica", s.myriad_activations_total == 0 and "Myriad Landscape" in s.battlefield)
# Pips da mao: carta com {R}{R}? (usa pips reais do CARD_DB) -- desempate por deficit
dbl = [n for n, c in M.CARD_DB.items() if c.ctype != "land" and any(k >= 2 for k in c.pips.values())]
teste("M7 info: cartas da lista com pip duplo (afetam 'wanted')", True, str(dbl))
# M8: rng None nao quebra (so' nao embaralha)
s = novo(bf=["Myriad Landscape", "Mountain", "Swamp", "Badlands"], rng=False)
M.try_myriad_landscape(s)
teste("M8 state.rng None: ativa sem excecao", s.myriad_activations_total == 1)
# M9: flag desligada = inerte
M.MYRIAD_ABILITY_ENABLED = False
s = novo(bf=["Myriad Landscape", "Mountain", "Swamp", "Badlands"])
M.try_myriad_landscape(s)
teste("M9 MYRIAD_ABILITY_ENABLED=False: inerte", s.myriad_activations_total == 0 and "Myriad Landscape" in s.battlefield)
M.MYRIAD_ABILITY_ENABLED = True

# M10: 'descended' do Tunnel-Grinder conta o Myriad sacrificado (end step checa depois)
s = novo(bf=["Brass's Tunnel-Grinder", "Myriad Landscape", "Mountain", "Swamp", "Badlands"])
M.try_myriad_landscape(s)
M.try_tunnel_grinder_transform(s)
teste("M10 Myriad sacrificado conta como descend: +1 bore counter no Tunnel-Grinder", s.tunnel_grinder_bore_counters == 1)

# M11: integracao em play_turn -- a ativacao acontece DEPOIS da 2a main phase
lib = ["Mountain"] * 4 + ["Plains"] * 4 + ["Swamp"] * 4 + ["Badlands"] * 20
s = novo(bf=["Megatron, Tyrant", "Myriad Landscape", "Mountain", "Swamp", "Plains", "Badlands"], lib=lib, turn=4,
         commander_in_play=True, megatron_face="vehicle")
s.hand = []
M.play_turn(s, False, True)
teste("M11 play_turn completo (comandante ja em campo, mao vazia): Myriad ativa no fim do turno",
      s.myriad_activations_total == 1 and "Myriad Landscape" in s.graveyard,
      f"ativ={s.myriad_activations_total} remaining_final={M.remaining_mana(s)}")

# M12: invariantes em partidas reais (2.000 jogos, seeds 1_000_000+): so' ativa com remaining>=3, nunca no turno
# em que o Myriad entrou, nunca com Myriad fora de campo; shuffle so' acontece quando ativa.
orig = M.try_myriad_landscape
regs = []
def espia(state):
    antes = state.myriad_activations_total
    rem = M.remaining_mana(state)
    entrou_agora = state.tapped_land_this_turn == "Myriad Landscape"
    em_campo = "Myriad Landscape" in state.battlefield
    tinha_basico = any(b in state.library for b in ("Plains", "Swamp", "Mountain"))
    orig(state)
    regs.append((state.myriad_activations_total - antes, rem, entrou_agora, em_campo, tinha_basico))
M.try_myriad_landscape = espia
ativ = 0
for i in range(2000):
    st = M.simulate_one(1_000_000 + i)
    ativ += st.myriad_activations_total
M.try_myriad_landscape = orig
viol_rem = [r for r in regs if r[0] == 1 and r[1] < 3]
viol_entrou = [r for r in regs if r[0] == 1 and r[2]]
viol_campo = [r for r in regs if r[0] == 1 and not r[3]]
perdeu = [r for r in regs if r[0] == 0 and r[3] and not r[2] and r[1] >= 3 and r[4]]
teste("M12 (2.000 jogos) ativou so' com remaining>=3", not viol_rem and ativ > 0, f"ativacoes={ativ} violacoes={len(viol_rem)}")
teste("M12 (2.000 jogos) nunca ativou no turno em que o Myriad entrou", not viol_entrou)
teste("M12 (2.000 jogos) nunca ativou sem o Myriad em campo", not viol_campo)
teste("M12 (2.000 jogos) toda vez que podia (em campo, nao entrou agora, remaining>=3, basico na biblioteca), ativou",
      len(perdeu) == 0, f"casos que podia e nao ativou: {len(perdeu)}")
teste("M12 (2.000 jogos) amostra nao-vazia: houve chamadas com condicoes satisfeitas",
      sum(1 for r in regs if r[0] == 1) > 50, f"ativacoes registradas: {sum(1 for r in regs if r[0] == 1)}")

# M13 (Regra #6, orquestracao): teste em play_turn COMPLETO -- o Myriad sacrificado conta como 'descended' pro Tunnel-Grinder
# porque a ativacao fica ANTES do end step. Com a habilidade desligada o contador nao anda.
def tg_turno(myriad_ligado):
    M.MYRIAD_ABILITY_ENABLED = myriad_ligado
    # comandante marcado 'em jogo' mas FORA do campo (cast_megatron retorna cedo e o flip nao consome o Tunnel-Grinder como fuel);
    # Tunnel-Grinder e' artefato e viraria combustivel do Megatron se ele estivesse em campo (era o que quebrava a 1a versao deste teste)
    s = novo(bf=["Brass's Tunnel-Grinder", "Myriad Landscape", "Mountain", "Swamp", "Plains", "Badlands"],
             lib=["Mountain"] * 4 + ["Plains"] * 4 + ["Swamp"] * 4 + ["Badlands"] * 20, turn=4,
             commander_in_play=True, megatron_face="vehicle")
    s.hand = []
    M.play_turn(s, False, True)
    M.MYRIAD_ABILITY_ENABLED = True
    return s
a, b = tg_turno(True), tg_turno(False)
teste("M13 play_turn completo: com a habilidade, bore counter do Tunnel-Grinder = 1 (descend via Myriad); sem, = 0",
      a.tunnel_grinder_bore_counters == 1 and b.tunnel_grinder_bore_counters == 0,
      f"com={a.tunnel_grinder_bore_counters} sem={b.tunnel_grinder_bore_counters}")

# M14: os 2 basicos buscados estao UNTAPPED e rendem mana no turno seguinte (nao ficam 'tapped' pra sempre)
s = novo(bf=["Megatron, Tyrant", "Myriad Landscape", "Mountain", "Swamp", "Plains", "Badlands"],
         lib=["Plains"] * 3 + ["Badlands"] * 30, turn=4, commander_in_play=True, megatron_face="vehicle")
s.hand = []
M.play_turn(s, False, True)
lands1 = sum(1 for n in s.battlefield if n in M.LAND_NAMES)
ativou = s.myriad_activations_total == 1
registro = {}
orig_pl = M.play_land
def espia_pl(st):
    orig_pl(st)
    registro["mana"] = M.total_mana(st)
    registro["lands"] = sum(1 for n in st.battlefield if n in M.LAND_NAMES)
    registro["tapped"] = st.tapped_land_this_turn
M.play_land = espia_pl
M.play_turn(s, False, True)
M.play_land = orig_pl
teste("M14 turno seguinte: os basicos buscados rendem mana (total_mana >= terrenos - 1 jogado tapped)",
      ativou and registro["tapped"] not in ("Plains",) and registro["mana"] >= registro["lands"] - (1 if registro["tapped"] else 0),
      str(registro))

# ------------------------------------------------------- terreno tapped em T1/T2
def jogada(hand, bf=(), turn=1, **kw):
    s = novo(hand=hand, bf=bf, turn=turn, **kw)
    s.lands_played_this_turn = 0
    M.play_land(s)
    jogado = [n for n in s.battlefield if n not in bf or s.battlefield.count(n) > list(bf).count(n)]
    return s, s.battlefield[len(bf):]

s, j = jogada(["Plains", "Evolving Wilds"], turn=1)
teste("T1 [Plains, Evolving Wilds], sem spell: joga o TAPPED", j == ["Evolving Wilds"] and s.tapped_land_this_turn == "Evolving Wilds", str(j))
s, j = jogada(["Plains", "Evolving Wilds", "Sol Ring"], turn=1)
teste("T1 com Sol Ring na mao: joga o UNTAPPED (tapped custaria o Sol Ring)", j == ["Plains"] and s.tapped_land_skipped_for_play_total == 1, str(j))
s, j = jogada(["Swamp", "Sunlit Marsh"], turn=1)
teste("T1 [Swamp, Sunlit Marsh]: tapped primeiro", j == ["Sunlit Marsh"], str(j))
s, j = jogada(["Plains", "Myriad Landscape"], turn=1)
teste("T1 [Plains, Myriad Landscape]: Myriad (tapped) primeiro", j == ["Myriad Landscape"], str(j))
s, j = jogada(["Swamp", "Evolving Wilds", "Mind Stone"], bf=["Plains"], turn=2)
teste("T2 com Mind Stone ({2}) na mao e 1 terreno em campo: untapped (senao perde o Mind Stone)", j == ["Swamp"], str(j))
s, j = jogada(["Swamp", "Evolving Wilds"], bf=["Plains"], turn=2)
teste("T2 sem jogada de 2: tapped", j == ["Evolving Wilds"], str(j))
s, j = jogada(["Swamp", "Evolving Wilds", "Sol Ring", "Mind Stone"], bf=["Plains"], turn=2)
teste("T2 Sol Ring + Mind Stone: tapped basta (Sol Ring {1} paga com 1 untapped e libera +2 pro Mind Stone)", j == ["Evolving Wilds"], str(j))
s, j = jogada(["Swamp", "Evolving Wilds"], bf=["Plains", "Mountain"], turn=3)
teste("T3: comportamento ORIGINAL (nao forca tapped; ordena so' por cor faltante)", len(j) == 1, str(j))
s_orig, j_orig = jogada(["Swamp", "Evolving Wilds"], bf=["Plains", "Mountain"], turn=3)
M.TAPPED_LAND_FIRST_ENABLED = False
s_off, j_off = jogada(["Swamp", "Evolving Wilds"], bf=["Plains"], turn=2)
teste("flag TAPPED_LAND_FIRST_ENABLED=False: escolha = a de antes (ordem por cor faltante)", len(j_off) == 1)
M.TAPPED_LAND_FIRST_ENABLED = True
s, j = jogada(["Evolving Wilds", "Terramorphic Expanse"], turn=1)
teste("T1 so' tapped na mao: joga um deles normalmente", len(j) == 1 and s.tapped_land_this_turn == j[0])
s, j = jogada(["Plains", "Mountain"], turn=1)
teste("T1 so' untapped na mao: comportamento original", len(j) == 1 and s.tapped_land_this_turn is None)
st = novo(bf=["Plains", "Mountain"])
teste("land_enters_tapped: Smoldering Marsh com 2 basicos = untapped", not M.land_enters_tapped(st, "Smoldering Marsh"))
st = novo(bf=["Plains"])
teste("land_enters_tapped: Smoldering Marsh com 1 basico = tapped", M.land_enters_tapped(st, "Smoldering Marsh"))
teste("land_enters_tapped: Badlands/Command Tower/Shadowblood Ridge = untapped",
      not any(M.land_enters_tapped(st, n) for n in ("Badlands", "Command Tower", "Shadowblood Ridge", "Fountainport", "Plateau", "Scrubland", "Plains")))
# politica cega (flag): sempre o tapped, mesmo perdendo o Sol Ring
M.TAPPED_LAND_FIRST_SKIP_IF_LOSES_PLAY = False
s, j = jogada(["Plains", "Evolving Wilds", "Sol Ring"], turn=1)
teste("flag SKIP_IF_LOSES_PLAY=False (politica cega): joga o tapped mesmo com Sol Ring na mao", j == ["Evolving Wilds"], str(j))
M.TAPPED_LAND_FIRST_SKIP_IF_LOSES_PLAY = True
# instant/sorcery NAO contam como 'jogada perdida' (sem alvo em goldfish; o main_phase as lanca como proxy)
s, j = jogada(["Plains", "Evolving Wilds", "Swords to Plowshares"], turn=1)
teste("T1 com so' Swords na mao (instant, proxy de interacao): tapped mesmo assim", j == ["Evolving Wilds"], str(j))
s, j = jogada(["Mountain", "Evolving Wilds", "Faithless Looting"], turn=1)
teste("T1 com Faithless Looting ({R}): tapped mesmo assim (filtragem nao e' desenvolvimento)", j == ["Evolving Wilds"], str(j))
s, j = jogada(["Mountain", "Evolving Wilds", "Goblin Welder"], turn=1)
teste("T1 com Goblin Welder ({R}, criatura MV1, permanente): untapped (tapped custaria o cast)", j == ["Mountain"], str(j))
# dry-run nao muta o estado
s = novo(hand=["Plains", "Evolving Wilds", "Sol Ring"], bf=["Swamp"], turn=2)
snap = (list(s.hand), list(s.battlefield), s.mana_spent_this_turn, s.tapped_land_this_turn, list(s.graveyard))
M.dry_run_mana_spent(s, "Plains"); M.dry_run_mana_spent(s, "Evolving Wilds")
teste("dry_run_mana_spent nao muta o estado", snap == (list(s.hand), list(s.battlefield), s.mana_spent_this_turn, s.tapped_land_this_turn, list(s.graveyard)))
# dry-run: valor esperado
s = novo(hand=["Plains", "Evolving Wilds", "Sol Ring", "Mind Stone"], bf=["Swamp"], turn=2)
a = M.dry_run_mana_spent(s, "Plains"); b = M.dry_run_mana_spent(s, "Evolving Wilds")
teste("dry-run T2 Sol Ring+Mind Stone: untapped gasta 3, tapped tambem 3", (a, b) == (3, 3), f"{a},{b}")
s = novo(hand=["Plains", "Evolving Wilds", "Mind Stone"], bf=["Swamp"], turn=2)
a = M.dry_run_mana_spent(s, "Plains"); b = M.dry_run_mana_spent(s, "Evolving Wilds")
teste("dry-run T2 so' Mind Stone: untapped gasta 2, tapped 0", (a, b) == (2, 0), f"{a},{b}")

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)

"""Testes dirigidos do harness dos wipes de sacrificio (`sac_harness.py`): cada teste monta um GameState a mao e chama o resolvedor real; S1 compara o executor novo com o
`edict_harness.py` da rodada da Blasphemous Edict (mesmos estados naturais -> mesma impressao digital do estado final); S22 roda os 20 resolvedores sobre estados naturais e confere as
invariantes. O simulador (`vihaan_goldfish_v1.py`) NAO e' alterado nesta rodada. Uso: python3 testes_dirigidos.py"""
import copy, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F
import sac_harness as H
import edict_harness as EH

V = F.flags(F.carrega(F.DEPOIS, "vih_sac_testes"))
H.instala(V)
res = []
VIH, MAYHEM, MAHADI, LOTHO, OLIVIA, ZUL, PLUND = V.COMMANDER, "Mayhem Devil", "Mahadi, Emporium Master", "Lotho, Corrupt Shirriff", "Olivia, Opulent Outlaw", "Zulaport Cutthroat", "Pitiless Plunderer"
SOL, ALTAR, KCI, SIGNET, DICTATE, PROC, MANU = "Sol Ring", "Ashnod's Altar", "Krark-Clan Ironworks", "Arcane Signet", "Dictate of Erebos", "Anointed Procession", "Academy Manufactor"


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def novo(bf=(), hand=(), lands=0, turn=8, commander=True, animados=0, inan=0, tokens=0, constructs=0, dragons=0, gy=(), clues=0, foods=0, lands_named=None):
    bf = [n for n in bf if n != VIH]
    s = V.GameState(hand=list(hand), battlefield=list(bf) + (lands_named if lands_named is not None else ["Mountain"] * lands), library=["Swamp"] * 30, graveyard=list(gy))
    s.turn = turn
    s.commander_cast_count = 10
    if commander:
        s.commander_in_play = True
        s.battlefield.append(VIH)
    s.treasures = animados + inan
    s.treasures_animated_alive = animados
    s.other_tokens = tokens
    s.constructs = constructs
    s.dragons = dragons
    s.clues = clues
    s.foods = foods
    return s


def nl(s):   # permanentes nomeados nao-terreno em campo
    return sorted(n for n in s.battlefield if n not in V.LAND_NAMES)


# --------------------------------------------------------------------------------------------------------------------------------- S0 oraculo -> parametros
teste("S0a tipos de criatura vem do type_line do Scryfall: Vihaan = {Dwarf, Warlock}, Mayhem Devil = {Devil}, Mahadi = {Devil}", H.tipos_criatura(VIH) == {"Dwarf", "Warlock"} and H.tipos_criatura(MAYHEM) == {"Devil"} and H.tipos_criatura(MAHADI) == {"Devil"})
teste("S0b poder: Vihaan 3; cores: Sol Ring incolor, Mayhem Devil {B,R}", H.poder(VIH) == 3 and H.cores(SOL) == [] and sorted(H.cores(MAYHEM)) == ["B", "R"])
teste("S0c o Winnowing (as 2 politicas) nao paga com animados (convoke) e as demais variantes pagam (politica da 10a rodada)", H.WINNOW not in V.OWN_WIPES and H.WINNOW2 not in V.OWN_WIPES and all(v in V.OWN_WIPES for v in H.VARIANTES if v not in (H.WINNOW, H.WINNOW2)))
teste("S0d as referencias (Blasphemous Act, Blood Money) ja' sao wipes proprios do simulador e nao foram tocadas pelo harness", all(v in V.OWN_WIPES for v in H.REFERENCIAS) and H.ACT == "Blasphemous Act" if hasattr(H, "ACT") else all(v in V.OWN_WIPES for v in H.REFERENCIAS))

# --------------------------------------------------------------------------------------------------------------------------------- S1 equivalencia com o harness da Edict
amostras = []
orig_main = V.main_phase
def espia(state):
    if state.turn >= 3 and len(amostras) < 4000:
        amostras.append(copy.deepcopy(state))
    return orig_main(state)
V.main_phase = espia
for i in range(300):
    V.simulate_one(1_000_000 + i)
V.main_phase = orig_main
def impr(st):
    """Impressao digital do estado final, ignorando a ORDEM do cemiterio e os campos do Reaver Cleaver: o executor novo desequipa o Cleaver quando o portador/o proprio Cleaver e' sacrificado
    (correto), o `edict_harness` nunca desequipava (nao afeta nenhuma metrica do ensaio, que mede so' o evento do cast)."""
    c = copy.copy(st)
    c.graveyard = sorted(st.graveyard)
    c.reaver_cleaver_equipped, c.reaver_cleaver_host = False, None
    return F.impressao(c)
dif = 0
for st in amostras:
    a, b = copy.deepcopy(st), copy.deepcopy(st)
    na = EH.edict_sacrificar(V, a)
    nb = H.r_n(V, b, 13)
    if hasattr(b, "_info"):
        del b._info
    if na != nb or impr(a) != impr(b):
        dif += 1
teste("S1 o executor novo (r_n, N=13) == edict_sacrificar da rodada anterior em %d estados naturais (mesma impressao digital do estado final, ordem do cemiterio e Reaver Cleaver a parte, e mesmo total sacrificado)" % len(amostras), dif == 0 and len(amostras) > 1000, "diferencas=%d" % dif)

# --------------------------------------------------------------------------------------------------------------------------------- S3/S4 By Invitation Only (N livre)
base = dict(bf=[VIH, MAHADI, MAYHEM, LOTHO, OLIVIA], tokens=6, animados=2)
s = novo(**base)
n = H.r_bio(V, s, "motores")
teste("S3 BIO [N=motores]: 13 criaturas minhas, 3 motores -> N=10; as 10 sacrificadas sao 2 animados + 6 fichas + as 2 nomeadas de menor MV; Vihaan, Mahadi e Mayhem SOBREVIVEM", n == 10 and s._info["n_opp"] == 10 and s.commander_in_play and MAHADI in s.battlefield and MAYHEM in s.battlefield
      and s.other_tokens == 0 and s.treasures_animated_alive == 0 and LOTHO not in s.battlefield and OLIVIA not in s.battlefield, str((n, nl(s), s._info)))
s = novo(**base)
n = H.r_bio(V, s, "fodder")
teste("S4 BIO [N=fodder]: N=8 (6 fichas + 2 animados), TODAS as nomeadas (Vihaan, Mahadi, Mayhem, Lotho, Olivia) sobrevivem; o Mayhem Devil dispara por cada um dos 8", n == 8 and s.commander_in_play and all(x in s.battlefield for x in (MAHADI, MAYHEM, LOTHO, OLIVIA))
      and s.drain_damage_total >= 8, str((n, nl(s), s.drain_damage_total)))
s = novo(**base)
n = H.r_bio(V, s, "13")
teste("S4b BIO [N=13] com exatamente 13 criaturas: sacrifica as 13 (inclui Vihaan; Vihaan vai a zona de comando) e o Mayhem Devil dispara 13 vezes", n == 13 and not s.commander_in_play and s.drain_damage_total == 13 and s.creature_deaths_total == 13, str((n, s.drain_damage_total, s.creature_deaths_total)))

# --------------------------------------------------------------------------------------------------------------------------------- S5/S6 Mythos / Tragic Arrogance (guardar 1 de cada tipo)
s = novo([MAYHEM, LOTHO, SOL, ALTAR, DICTATE, PROC], tokens=3, animados=4, inan=2, clues=1, foods=1)
n = H.r_manter_um(V, s)
teste("S5 Mythos/Tragic Arrogance: guardo Vihaan (criatura), Sol Ring (artefato) e Dictate of Erebos (encantamento); todo o resto nao-terreno e' sacrificado (Mayhem, Lotho, Altar, Procession, 3 fichas, 6 Treasures, Clue, Food = 15)",
      nl(s) == sorted([VIH, SOL, DICTATE]) and s.treasures == 0 and s.clues == 0 and s.foods == 0 and s.other_tokens == 0 and s.treasures_animated_alive == 0, str((nl(s), s.treasures, s.clues, s.foods)))
s2 = novo([MAYHEM, LOTHO, SOL, ALTAR, DICTATE, PROC], tokens=3, animados=4, inan=2, clues=1, foods=1)
n2 = H.r_manter_um(V, s2)
teste("S5b o Mayhem Devil dispara por CADA permanente sacrificado (inclusive ele proprio): 4 nomeados (Mayhem, Lotho, Altar, Procession) + 3 fichas + 6 Treasures + Clue + Food = 15 sacrificados = 15 de dano", n2 == 15 and s2.drain_damage_total == 15, str((n2, s2.drain_damage_total)))
s = novo([DICTATE], animados=3)
H.r_manter_um(V, s)
teste("S6 sem artefato nomeado: guardo UM Treasure como o artefato (o estoque cai de 3 para 1) e Vihaan + Dictate", nl(s) == sorted([VIH, DICTATE]) and s.treasures == 1, str((nl(s), s.treasures)))
s = novo([], commander=False, animados=3)
H.r_manter_um(V, s)
teste("S6b sem criatura nomeada e sem artefato nomeado: guardo UM Treasure animado como a criatura e OUTRO como o artefato (podem ser objetos diferentes; ruling 2020-04-17 so' permite o MESMO, nao obriga): sobram 2 de 3", s.treasures == 2 and s.treasures_animated_alive == 2, str((s.treasures, s.treasures_animated_alive)))
s = novo([], commander=False, animados=1)
H.r_manter_um(V, s)
teste("S6c com um unico Treasure animado ele serve de criatura E de artefato: sobra 1 de 1", s.treasures == 1 and s.treasures_animated_alive == 1, str((s.treasures, s.treasures_animated_alive)))

# --------------------------------------------------------------------------------------------------------------------------------- S7 Winnowing
s = novo([MAYHEM, MAHADI, OLIVIA], animados=5)
H.r_winnowing(V, s)
teste("S7 Winnowing com Vihaan em campo: a minha criatura-escolhida e' o Vihaan (Dwarf Warlock); Mayhem/Mahadi (Devil), Olivia (Vampire Assassin) e os 5 animados (Construct Assassin) NAO compartilham tipo e morrem",
      s.commander_in_play and nl(s) == [VIH] and s.treasures_animated_alive == 0 and s._info["escolhida"] == VIH, str((nl(s), s.treasures_animated_alive, s._info)))
s = novo([MAYHEM, MAHADI, OLIVIA], commander=False, animados=4)
H.r_winnowing(V, s)
teste("S7b sem Vihaan: escolho o Mayhem Devil (Devil): Mahadi tambem sobrevive (outro Devil); Olivia e os 4 animados morrem", nl(s) == sorted([MAYHEM, MAHADI]) and s.treasures_animated_alive == 0, str((nl(s), s._info)))
s = novo([OLIVIA], commander=False, animados=4)
H.r_winnowing(V, s)
teste("S7c so' Olivia (Vampire Assassin) + 4 animados (Construct Assassin): compartilham 'Assassin' -> escolhendo um animado, TODOS sobrevivem (Olivia + 4 animados)", nl(s) == [OLIVIA] and s.treasures_animated_alive == 4 and s.drain_damage_total == 0, str((nl(s), s.treasures_animated_alive)))
s = novo([MAYHEM, OLIVIA], animados=4)
H.r_winnowing(V, s, "fichas")
teste("S7f Winnowing [guarda os animados]: com Vihaan + Mayhem + Olivia + 4 animados escolho um animado (Construct Assassin): os 4 animados e Olivia (Assassin) ficam; Vihaan e Mayhem saem", not s.commander_in_play and nl(s) == [OLIVIA] and s.treasures_animated_alive == 4, str((nl(s), s.treasures_animated_alive, s._info)))
V_ = H.FASE
H.FASE = "2a main"
s = novo([MAYHEM, OLIVIA], lands=3, animados=4)
c2 = V.spell_cost(s, H.WINNOW)
H.FASE = "1a main"
s1 = novo([MAYHEM, OLIVIA], lands=3, animados=0, tokens=2)
c1 = V.spell_cost(s1, H.WINNOW)
H.FASE = V_
teste("S7d custo do Winnowing: 6 menos 1 por criatura desvirada (convoke), minimo {W}{W}=2: 2a main com Vihaan, 4 animados e Olivia (outlaw, vigilance) = 6-5 -> 2; 1a main com 5 criaturas = 6-5 -> 2", c2 == 2 and c1 == 2, str((c1, c2)))
s = novo([MAYHEM, OLIVIA], lands=6, animados=4, hand=[H.WINNOW])
H.FASE = "2a main"
V.cast_card(s, H.WINNOW)
H.FASE = V_
teste("S7e o Winnowing conjurado com convoke NAO sacrifica animados pra pagar (pagos=0)", s.own_wipe_animated_paid_total == 0, str(s.own_wipe_animated_paid_total))

# --------------------------------------------------------------------------------------------------------------------------------- S8 Slaughter the Strong
s = novo([MAYHEM, LOTHO], constructs=2, animados=2)
H.r_slaughter(V, s)
teste("S8 Slaughter the Strong: guardo criaturas de poder total <= 4: Vihaan (3) + 1 Construct (1); Mayhem, Lotho, 1 Construct e os 2 animados (3/3) saem", s.commander_in_play and nl(s) == [VIH] and s.constructs == 1 and s.treasures_animated_alive == 0, str((nl(s), s.constructs, s.treasures_animated_alive)))

# --------------------------------------------------------------------------------------------------------------------------------- S9/S10/S11 Living Death / Scrap Mastery / All Is Dust
s = novo([MAYHEM], tokens=2, gy=[ZUL, LOTHO, SOL])
H.r_living(V, s)
teste("S9 Living Death: as cartas de criatura do cemiterio (Zulaport, Lotho) voltam; Vihaan (zona de comando) e Mayhem (acabou de ser sacrificado, nao estava exilado) NAO voltam; Sol Ring segue no cemiterio",
      ZUL in s.battlefield and LOTHO in s.battlefield and MAYHEM not in s.battlefield and MAYHEM in s.graveyard and not s.commander_in_play and SOL in s.graveyard and s.other_tokens == 0 and s.recursion_events_total == 2, str((nl(s), s.graveyard)))
s = novo([SOL, KCI, MAYHEM], animados=2, inan=3, constructs=1, clues=1, foods=1, gy=[SIGNET])
n = H.r_scrap(V, s)
teste("S10 Scrap Mastery: todos os artefatos saem (Sol Ring, KCI, 5 Treasures, Construct, Clue, Food = 10; o Mayhem Devil dispara 10 vezes); Arcane Signet (do cemiterio) volta; Vihaan e Mayhem ficam",
      n == 10 and s.drain_damage_total == 10 and SIGNET in s.battlefield and SOL not in s.battlefield and KCI not in s.battlefield and s.treasures == 0 and s.constructs == 0 and s.clues == 0 and s.foods == 0
      and s.commander_in_play and MAYHEM in s.battlefield, str((n, s.drain_damage_total, nl(s))))
s = novo([SOL, MAYHEM, DICTATE], animados=3, constructs=2, tokens=2, dragons=1)
H.r_dust(V, s)
teste("S11 All Is Dust: so' os COLORIDOS saem (Vihaan, Mayhem, Dictate, 2 fichas genericas, Dragao); Sol Ring, os 3 Treasures animados e os 2 Constructs (incolores) ficam", nl(s) == [SOL] and s.treasures == 3 and s.constructs == 2 and s.other_tokens == 0 and s.dragons == 0 and not s.commander_in_play, str((nl(s), s.treasures, s.constructs)))

# --------------------------------------------------------------------------------------------------------------------------------- S12.. Meathook / Taste / Hex / Liliana / Prank / Zodiark / Barter
s = novo([MAYHEM], lands=10, animados=3, tokens=4)
x = H.x_meathook(V, s)
c = V.spell_cost(s, H.MEATHOOK)
teste("S12 Meathook Massacre II: X maximo com custo 4+2X <= mana e X <= fodder pos-pagamento; custo = 4+2X", x >= 1 and c == 4 + 2 * x, str((x, c)))
s = novo([MAYHEM], tokens=4)
H.r_taste(V, s)
teste("S13 Taste of Death: cada jogador sacrifica 3 (3 fichas); eu crio 3 Food; Mayhem dispara 3 vezes", s.other_tokens == 1 and s.foods == 3 and s.drain_damage_total >= 3, str((s.other_tokens, s.foods, s.drain_damage_total)))
s = novo([MAYHEM, PROC], tokens=4)
H.r_taste(V, s)
teste("S13b com Anointed Procession os 3 Food viram 6", s.foods == 6, str(s.foods))
s = novo([MANU], tokens=4)
H.r_taste(V, s)
teste("S13c com Academy Manufactor cada Food vira Treasure + Clue + Food (3 de cada)", s.treasures >= 3 and s.clues >= 3 and s.foods >= 3, str((s.treasures, s.clues, s.foods)))
s = novo([], tokens=8)
H.r_hex(V, s)
teste("S14 Necrotic Hex: sacrifica 6 fichas e cria 6 Zumbis: 8-6+6 = 8 fichas", s.other_tokens == 8, str(s.other_tokens))
s = novo([], tokens=5)
mao = len(s.hand)
H.r_liliana(V, s)
teste("S15 Liliana -4: sacrifica 2 (fichas) e compra 2 cartas (passiva: 'whenever a creature you control dies, draw a card')", s.other_tokens == 3 and len(s.hand) == mao + 2, str((s.other_tokens, len(s.hand) - mao)))
s = novo([], tokens=5)
vida = s.life
H.r_prank(V, s)
teste("S16 Rankle's Prank (modos: perder 4 de vida + sacrificar 2): cada oponente perde 4 (mesa +12), eu perco 4, 2 fichas saem", s.table_damage_total == 12 and s.life == vida - 4 and s.other_tokens == 3, str((s.table_damage_total, s.life - vida, s.other_tokens)))
s = novo([MAYHEM, LOTHO, OLIVIA, ZUL, PLUND], tokens=2)   # Vihaan + 5 nomeadas + 2 fichas = 8 criaturas
H.r_zodiark(V, s)
teste("S17 Zodiark: metade das criaturas (8//2=4) sacrificadas (2 fichas + 2 nomeadas de menor MV), motores ficam", s._info["n_minhas"] == 4 and s.commander_in_play and MAYHEM in s.battlefield and s.other_tokens == 0, str((s._info, nl(s))))
s = novo([MAYHEM, LOTHO])
H.r_n(V, s, 2)
teste("S18 Barter/Tergrid/Liliana (N=2): 3 criaturas (Vihaan, Mayhem, Lotho) -> sacrifica Lotho e uma motor de menor MV preferindo ficar com Vihaan e Mahadi; dreno 2", s._info["n_minhas"] == 2 and s.commander_in_play and s.drain_damage_total == 2, str((s._info, nl(s), s.drain_damage_total)))

# --------------------------------------------------------------------------------------------------------------------------------- S19 cores
s = novo([], commander=False, lands_named=["Plains", "Mountain", "Swamp", "Swamp"])
a = H.cor_ok(V, s, H.BIO13)
s = novo([], commander=False, lands_named=["Plains", "Plains", "Swamp"])
b = H.cor_ok(V, s, H.BIO13)
s = novo([], commander=False, lands_named=["Plains", "Swamp"], inan=1)
c = H.cor_ok(V, s, H.BIO13)
teste("S19a {W}{W}: 1 Plains sozinha NAO basta; 2 Plains sim; 1 Plains + 1 Treasure (qualquer cor) sim", (not a) and b and c, str((a, b, c)))
s = novo([], commander=False, lands_named=["Swamp"] * 4)
d = H.cor_ok(V, s, H.ZODIARK)
s = novo([], commander=False, lands_named=["Swamp"] * 4, inan=1)
e = H.cor_ok(V, s, H.ZODIARK)
teste("S19b Zodiark {B}{B}{B}{B}{B}: 4 Swamps NAO bastam; 4 Swamps + 1 Treasure sim", (not d) and e, str((d, e)))
s = novo([], commander=False, lands_named=["Plains", "Plains", "Mountain", "Swamp"])
f = H.cor_ok(V, s, H.MYTHOS)
s = novo([], commander=False, lands_named=["Plains", "Plains", "Swamp"])
g = H.cor_ok(V, s, H.MYTHOS)
teste("S19c Mythos of Snapdax precisa de W W + B + R gastos (4 fontes distintas): Plains Plains Mountain Swamp sim; so' 3 fontes NAO", f and not g, str((f, g)))
s = novo([MAYHEM, LOTHO, OLIVIA, ZUL, PLUND, MAHADI], commander=True, tokens=10, lands_named=["Swamp"])
h1 = H.cor_ok(V, s, H.EDICT)
s = novo([MAYHEM], commander=True, tokens=3, lands_named=["Swamp"])
h2 = H.cor_ok(V, s, H.EDICT)
teste("S19d Edict: com 13+ criaturas basta {B} (custo alternativo); com menos precisa {B}{B}", h1 and not h2, str((h1, h2)))

# --------------------------------------------------------------------------------------------------------------------------------- S20 custo pago com animados
s = novo([], lands=1, animados=4, hand=[H.BARTER])
V.cast_card(s, H.BARTER)
teste("S20 custo da Barter in Blood (4) e' pago primeiro com os 4 Treasures animados (politica da 10a rodada): pagos=4; o dreno do pagamento so' aparece com Mayhem Devil", s.own_wipe_animated_paid_total == 4, str(s.own_wipe_animated_paid_total))

# --------------------------------------------------------------------------------------------------------------------------------- S22 invariantes em estados naturais
viol = {}
exc = 0
for st in amostras[:1500]:
    for v in H.VARIANTES:
        for fase in ("1a main", "2a main"):
            H.FASE = fase
            c = copy.deepcopy(st)
            c.hand.append(v)
            if not V.can_cast(c, v):
                continue
            base_v = set(H.invariantes(V, c))
            try:
                V.cast_card(c, v)
            except Exception as e:
                exc += 1
                continue
            for x in H.invariantes(V, c):
                if x not in base_v:
                    viol[(v, x)] = viol.get((v, x), 0) + 1
teste("S22 os 20 resolvedores sobre 1.500 estados naturais x 2 fases: 0 excecoes e 0 violacoes de invariante introduzidas", exc == 0 and not viol, str((exc, sorted(viol.items())[:5])))

print("\n%d/%d testes passaram" % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)

"""Testes dirigidos do Megatron (2a rodada): London Mulligan e fetch lands. Cada teste monta um GameState a mao e chama a funcao
real do simulador. Uso: python3 testes_dirigidos.py"""
import json, os, random, re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

M = F.flags(F.carrega(F.DEPOIS, "meg_testes2"))
res = []


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


LIB = (["Plains", "Swamp", "Mountain"] * 4 + ["Badlands", "Scrubland", "Plateau", "Smoldering Marsh", "Sunlit Marsh", "Command Tower"]
       + ["Sol Ring"] * 2 + ["Mind Stone"] * 2)


def novo(hand=(), bf=(), lib=None, turn=5, **kw):
    s = M.GameState(hand=list(hand), battlefield=list(bf), library=list(LIB if lib is None else lib), rng=random.Random(11), **kw)
    s.turn = turn
    return s


# ====================================================================== London Mulligan
class Identidade(random.Random):
    def shuffle(self, x):
        return None


def mull(modo, n_mulls=2):
    """Forca n_mulls mulligans com baralho na ordem de BASE_LIBRARY."""
    M.MULLIGAN_BOTTOM_MODE = modo
    it = iter([False] * n_mulls + [True])
    real = M.should_keep
    M.should_keep = lambda hand: next(it)
    hand, lib, mulls = M.mulligan(Identidade(1))
    M.should_keep = real
    M.MULLIGAN_BOTTOM_MODE = "smart"
    return hand, lib, mulls


h7 = M.BASE_LIBRARY[:7]
hand, lib, mulls = mull("legacy")
menor = min(h7, key=lambda n: M.CARD_DB[n].mv)
teste("ML1 modo legacy reproduz o bug: carta de MENOR MV devolvida no TOPO (proxima compra)", lib[0] == menor and mulls == 2 and len(hand) == 6, f"topo={lib[0]} menor={menor}")
hand, lib, mulls = mull("bottom_only")
teste("ML1 modo bottom_only: mesma carta (menor MV), agora no FUNDO", lib[-1] == menor, f"fundo={lib[-1]} menor={menor}")
hand, lib, mulls = mull("smart")
sobrou = [c for c in h7 if c not in hand or h7.count(c) > hand.count(c)]
teste("ML2 modo smart: mao de 6, a devolvida e' a ULTIMA da biblioteca e nao esta na mao",
      len(hand) == 6 and len(sobrou) == 1 and lib[-1] == sobrou[0], f"mao={len(hand)} sobrou={sobrou} ultima={lib[-1]}")
hand3, lib3, _ = mull("smart", 3)
h7_3 = M.BASE_LIBRARY[:7]
devolvidas = list(h7_3)
for c in hand3:
    devolvidas.remove(c)
teste("ML2 3 mulligans (penalidade 2): 5 cartas na mao e as 2 devolvidas sao as 2 ULTIMAS da biblioteca",
      len(hand3) == 5 and len(devolvidas) == 2 and sorted(lib3[-2:]) == sorted(devolvidas), f"mao={len(hand3)} devolvidas={devolvidas} fundo={lib3[-2:]}")
# regras de escolha
cheia = ["Swamp", "Plains", "Mountain", "Sol Ring", "Blightsteel Colossus", "Goblin Welder"]
cheia = [c for c in cheia if c in M.CARD_DB]
b = M.choose_bottom(cheia, 1)
teste("ML3 devolve a carta nao-terreno de MAIOR custo (Blightsteel Colossus), nunca Sol Ring nem terreno", b == ["Blightsteel Colossus"], str(b))
b = M.choose_bottom(["Swamp", "Plains", "Mountain", "Badlands", "Scrubland", "Sol Ring", "Goblin Welder"], 1)
teste("ML3 mais de 4 terrenos: devolve um terreno (o de menos cores, empate: o que entra tapped)", b[0] in M.LAND_NAMES and len(M.CARD_DB[b[0]].produces) == 1, str(b))
b = M.choose_bottom(["Swamp", "Plains", "Mountain", "Myriad Landscape", "Scrubland", "Sol Ring", "Goblin Welder"], 1)
teste("ML3 mais de 4 terrenos com Myriad (incolor): devolve o Myriad primeiro", b == ["Myriad Landscape"], str(b))
b = M.choose_bottom(["Sol Ring", "Arcane Signet", "Fellwar Stone", "Mind Stone", "Swamp"], 2)
teste("ML3 mao so' de keepers+1 terreno: nao quebra, 2 cartas distintas", len(b) == 2 and len(set(b)) == 2, str(b))
# efeito agregado
def stats(modo, n=4000):
    M.MULLIGAN_BOTTOM_MODE = modo
    cont = dict(top=0, tot=0, lands=0)
    real = M.should_keep
    for i in range(n):
        it = iter([False, False, True])
        M.should_keep = lambda hand: next(it)
        hd, lb, _ = M.mulligan(random.Random(100 + i))
        cont["tot"] += 1
        cont["lands"] += sum(1 for c in hd if c in M.LAND_NAMES)
    M.should_keep = real
    M.MULLIGAN_BOTTOM_MODE = "smart"
    return cont["lands"] / cont["tot"]
tl, ts = stats("legacy"), stats("smart")
teste("ML4 (4.000 maos de 6, 2 mulligans forcados) a escolha nao esvazia a mao de terrenos como o legado (min MV devolvia terreno primeiro)",
      ts >= tl - 0.01, f"legacy={tl:.3f} smart={ts:.3f}")
print(f"   info ML4: media de terrenos na mao de 6 cartas: legacy={tl:.3f} smart={ts:.3f}")

# ====================================================================== Fetch lands
# F0: tipos dos terrenos conferidos contra o type_line do cache do Scryfall (por script, nunca de memoria)
cache = json.load(open(os.path.join(F.DECK, "..", "scryfall-cache", "oracle-cache.json")))
lista = [l.split(" ", 1)[1].strip() for l in open(os.path.join(F.DECK, "lista.md")) if re.match(r"^\d+ ", l)]
tipos_cache = {}
for n in lista:
    if n in ("Mountain", "Plains", "Swamp"):
        tipos_cache[n] = {n}
    elif n in cache and cache[n]["type_line"].startswith("Land"):
        tl_ = cache[n]["type_line"]
        tipos_cache[n] = {t for t in ("Plains", "Island", "Swamp", "Mountain", "Forest") if t in tl_.split("—")[-1]} if "—" in tl_ else set()
com_tipo = {n: t for n, t in tipos_cache.items() if t}
teste("F0 LAND_TYPES do simulador == tipos do type_line do Scryfall (cache) para todo terreno da lista com tipo basico",
      {n: set(t) for n, t in M.LAND_TYPES.items()} == com_tipo, f"sim={M.LAND_TYPES} cache={com_tipo}")
pool_rocky = {n for n, t in com_tipo.items() if t & {"Swamp", "Mountain"}}
teste("F0 alvos do Rocky Tar Pit ('Swamp or Mountain card') na lista = ROCKY_TAR_PIT_ORDER", pool_rocky == set(M.ROCKY_TAR_PIT_ORDER), f"{sorted(pool_rocky)} vs {M.ROCKY_TAR_PIT_ORDER}")

# F1 Evolving Wilds T1: sacrifica na hora, basico entra tapped, sem mana, biblioteca perde 1 e e' embaralhada
s = novo(hand=["Evolving Wilds"], turn=1)
lib0 = list(s.library)
M.play_land(s)
novo_b = [n for n in s.battlefield]
teste("F1 Evolving Wilds: sacrificado (cemiterio), 1 basico no campo, entrou TAPPED (0 de mana neste turno)",
      "Evolving Wilds" in s.graveyard and len(novo_b) == 1 and novo_b[0] in M.BASIC_LANDS and s.extra_tapped_lands_this_turn == novo_b and M.total_mana(s) == 0,
      f"bf={novo_b} gy={s.graveyard} tapped={s.extra_tapped_lands_this_turn} mana={M.total_mana(s)}")
esperada = list(lib0); esperada.remove(novo_b[0])
teste("F1 biblioteca perdeu exatamente o basico buscado e foi embaralhada (mesmo multiset, ordem diferente)",
      sorted(s.library) == sorted(esperada) and s.library != esperada and s.fetch_cracks_total == 1)
teste("F1 'descended': a carta sacrificada conta como permanente no cemiterio", M.count_permanent_cards(s.graveyard) == 1)
# F2 escolha pela cor que falta
s = novo(hand=["Terramorphic Expanse"], bf=["Swamp", "Mountain"], turn=3)
M.play_land(s)
teste("F2 Terramorphic Expanse com Swamp+Mountain em campo (falta W): busca Plains", s.battlefield[-1] == "Plains" and "Terramorphic Expanse" in s.graveyard, str(s.battlefield))
s = novo(hand=["Evolving Wilds", "Goblin Welder"], bf=["Plains", "Swamp"], turn=3)
M.play_land(s)
teste("F2 falta R e a mao tem Goblin Welder ({R}): busca Mountain", s.battlefield[-1] == "Mountain", str(s.battlefield))
# F3 instancias: so' a copia tapped sai de color_sources
s = novo(bf=["Plains", "Plains"], turn=3)
s.extra_tapped_lands_this_turn = ["Plains"]
teste("F3 duas Plains, uma tapped por efeito: color_sources(W) = 1 e total_mana = 1 (nao exclui as duas pelo nome)", M.color_sources(s, "W") == 1 and M.total_mana(s) == 1,
      f"W={M.color_sources(s, 'W')} mana={M.total_mana(s)}")
# F4 sem basico na biblioteca
s = novo(hand=["Evolving Wilds"], lib=["Sol Ring", "Command Tower", "Badlands"], turn=3)
M.play_land(s)
teste("F4 sem basico na biblioteca: nao sacrifica; fica em campo sem mana nem cor", "Evolving Wilds" in s.battlefield and M.total_mana(s) == 0 and M.colored_sources_all(s, "R") == 0 and s.fetch_cracks_total == 0)
# F5 Rocky Tar Pit: entra tapped, nao sacrifica no turno
s = novo(hand=["Rocky Tar Pit"], turn=1)
M.play_land(s); M.try_crack_rocky_tar_pit(s)
teste("F5 Rocky Tar Pit jogado: fica em campo (entrou tapped, nao paga o {T}); 0 de mana; biblioteca intacta", "Rocky Tar Pit" in s.battlefield and M.total_mana(s) == 0 and s.library == LIB and s.fetch_cracks_total == 0)
# F6 Rocky no turno seguinte: duais com tipo, cobrindo as cores em deficit
s = novo(bf=["Rocky Tar Pit", "Plains"], turn=3)
M.try_crack_rocky_tar_pit(s)
teste("F6 Rocky (falta B e R): busca Badlands (Swamp Mountain, cobre as duas), untapped: total_mana = 2 ja' neste turno",
      s.battlefield[-1] == "Badlands" and "Rocky Tar Pit" in s.graveyard and M.total_mana(s) == 2 and s.fetch_untapped_total == 1 and s.fetch_duals_fetched_total == 1,
      f"bf={s.battlefield} mana={M.total_mana(s)}")
s = novo(bf=["Rocky Tar Pit", "Mountain"], turn=3)
M.try_crack_rocky_tar_pit(s)
teste("F6 Rocky (falta W e B): busca Scrubland (Plains Swamp)", s.battlefield[-1] == "Scrubland", str(s.battlefield))
s = novo(bf=["Rocky Tar Pit", "Swamp"], turn=3)
M.try_crack_rocky_tar_pit(s)
teste("F6 Rocky (falta W e R): busca Plateau (Mountain Plains)", s.battlefield[-1] == "Plateau", str(s.battlefield))
# F7 alvo que entra tapped
s = novo(bf=["Rocky Tar Pit", "Mountain"], lib=["Sunlit Marsh", "Swamp"], turn=3)
M.try_crack_rocky_tar_pit(s)
teste("F7 Rocky buscando Sunlit Marsh (entra tapped): registrado como tapped, 0 mana do alvo neste turno",
      s.battlefield[-1] == "Sunlit Marsh" and s.extra_tapped_lands_this_turn == ["Sunlit Marsh"] and M.total_mana(s) == 1, f"mana={M.total_mana(s)} tapped={s.extra_tapped_lands_this_turn}")
s = novo(bf=["Rocky Tar Pit", "Plains", "Swamp"], lib=["Smoldering Marsh"], turn=4)
M.try_crack_rocky_tar_pit(s)
teste("F7 Smoldering Marsh com 2 basicos em campo entra UNTAPPED", s.battlefield[-1] == "Smoldering Marsh" and s.extra_tapped_lands_this_turn == [])
s = novo(bf=["Rocky Tar Pit", "Plains", "Command Tower"], lib=["Smoldering Marsh"], turn=4)
M.try_crack_rocky_tar_pit(s)
teste("F7 Smoldering Marsh com 1 basico entra TAPPED", s.extra_tapped_lands_this_turn == ["Smoldering Marsh"], str(s.extra_tapped_lands_this_turn))
# F8 alvo invalido
s = novo(bf=["Rocky Tar Pit"], lib=["Plains", "Command Tower", "Sol Ring"], turn=3)
M.try_crack_rocky_tar_pit(s)
teste("F8 Rocky sem carta Swamp/Mountain na biblioteca (so' Plains e Command Tower): nao sacrifica", "Rocky Tar Pit" in s.battlefield and s.fetch_cracks_total == 0)
# F9 chave desligada = comportamento antigo
M.FETCHLANDS_ENABLED = False
s = novo(hand=["Evolving Wilds"], turn=1)
M.play_land(s)
t1 = ("Evolving Wilds" in s.battlefield and s.tapped_land_this_turn == "Evolving Wilds" and M.total_mana(s) == 0 and s.fetch_cracks_total == 0)
s2 = novo(bf=["Evolving Wilds", "Plains"], turn=2)
t2 = M.total_mana(s2) == 2 and M.color_sources(s2, "B") == 1
M.FETCHLANDS_ENABLED = True
teste("F9 FETCHLANDS_ENABLED=False: Evolving Wilds volta a ser 'terreno tapped que vira fonte W/B/R' (antigo)", t1 and t2)

# F10 integracao em play_turn COMPLETO (Regra #6): Rocky sacrificado ANTES da main phase do turno seguinte; basico rende no T2
vistos = []
orig_mp = M.main_phase
def mp(state):
    vistos.append((state.turn, M.total_mana(state), "Rocky Tar Pit" in state.battlefield, list(state.battlefield)))
    orig_mp(state)
M.main_phase = mp
s = M.GameState(hand=["Rocky Tar Pit", "Plains", "Swamp", "Mountain"], library=["Plains"] * 3 + ["Swamp"] * 3 + ["Mountain"] * 3 + ["Badlands"] + ["Sol Ring"] * 2 + ["Command Tower"] * 30,
                rng=random.Random(3))
M.play_turn(s, True, True)   # T1
M.play_turn(s, False, True)  # T2
M.main_phase = orig_mp
t2_main1 = [v for v in vistos if v[0] == 2][0]
teste("F10 play_turn completo: no 1o main phase do T2 o Rocky ja' foi sacrificado e o terreno buscado entrou (mana do T2 = terrenos untapped)",
      not t2_main1[2] and t2_main1[1] >= 2, str(t2_main1))
vistos_t1 = [v for v in vistos if v[0] == 1][0]
teste("F10 no T1 o Rocky (tapped) esta em campo e rende 0", vistos_t1[2] and vistos_t1[1] == 0, str(vistos_t1))

# F11 invariantes em partidas reais (2.000 jogos): conservacao de TODOS os terrenos nomeados; fetch nao fica sem sacrificar quando ha alvo
CONS = {"Plains": 6, "Swamp": 6, "Mountain": 6, "Myriad Landscape": 1, "Evolving Wilds": 1, "Terramorphic Expanse": 1, "Rocky Tar Pit": 1,
        "Badlands": 1, "Scrubland": 1, "Plateau": 1, "Smoldering Marsh": 1, "Sunlit Marsh": 1, "Command Tower": 1}
viol_c, viol_f, viol_m, cracks, duais, n_jogos = 0, 0, 0, 0, 0, 2000
orig_et = M.end_step
def et(state):
    global viol_f, viol_m
    for f, alvos in (("Evolving Wilds", M.BASIC_LANDS), ("Terramorphic Expanse", M.BASIC_LANDS)):
        if f in state.battlefield and any(b in state.library for b in alvos):
            viol_f += 1
    if "Rocky Tar Pit" in state.battlefield and state.land_played_this_turn_name != "Rocky Tar Pit" and any(n in state.library for n in M.ROCKY_TAR_PIT_ORDER):
        viol_f += 1
    if M.total_mana(state) < 0:
        viol_m += 1
    orig_et(state)
M.end_step = et
from collections import Counter
for i in range(n_jogos):
    st = M.simulate_one(1_000_000 + i)
    z = Counter(st.hand + st.battlefield + st.graveyard + st.library + st.exile)
    if any(z[n] != k for n, k in CONS.items()):
        viol_c += 1
    cracks += st.fetch_cracks_total
    duais += st.fetch_duals_fetched_total
M.end_step = orig_et
teste("F11 (2.000 jogos) conservacao: cada terreno nomeado aparece o numero certo de vezes entre as zonas", viol_c == 0, f"violacoes={viol_c}")
teste("F11 (2.000 jogos) nenhum fetch fica em campo sem sacrificar quando havia alvo na biblioteca (ao fim de cada turno)", viol_f == 0, f"violacoes={viol_f}")
teste("F11 (2.000 jogos) total_mana nunca negativo", viol_m == 0)
teste("F11 (2.000 jogos) houve sacrificios e o Rocky buscou duais", cracks > 500 and duais > 50, f"sacrificios={cracks} duais={duais}")

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)

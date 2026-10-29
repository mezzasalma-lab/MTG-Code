"""Testes dirigidos da correcao 'terreno virado primeiro em T1/T2' (2026-10-05). Cada teste confere o COMPORTAMENTO que a correcao promete (nao so' que o codigo roda):
  TL1  mao [virado, desvirado, magica que so' o desvirado paga] em T1 -> joga o DESVIRADO (nao perde a jogada) e conta `tapped_land_skipped_for_play_total`
  TL2  mao [virado, desvirado] sem nada pra conjurar em T1 -> joga o VIRADO (a mana de um turno sem jogada seria desperdicada) e conta `tapped_land_first_plays_total`
  TL3  chave desligada -> volta ao primeiro da ordem propria do deck (caminho antigo)
  TL4  T3 em diante -> ordem propria do deck, a correcao nao se aplica
  TL5  so' virados ou so' desvirados na mao -> ordem propria do deck
  TL6  o ensaio a seco NAO muta o estado nem o RNG nem `random` global, e solta a trava (_TL_FORCED/_TL_BUSY)
  TL8  modo GHOST (so' validacao): roda o ensaio e joga o padrao, sem contar
  TL7  integracao: `play_land` de fato poe o terreno escolhido em campo, uma vez so', e o virado NAO produz mana no turno em que entrou
Uso: python3 testes_dirigidos_terreno.py config.json"""
import collections, dataclasses, json, os, random, sys, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
M = A.carrega(os.path.join(DECK, cfg["sim"]), "td_tl", DECK)
resultados = []


def teste(nome):
    def deco(f):
        try:
            f()
            resultados.append((nome, True, ""))
        except Exception:
            resultados.append((nome, False, traceback.format_exc(limit=4)))
        return f
    return deco


def novo_estado(turno=1, mao=()):
    campos = {f.name for f in dataclasses.fields(M.GameState)}
    kw = {}
    if "rng" in campos:
        kw["rng"] = random.Random(7)
    lib = list(getattr(M, "BASE_LIBRARY", []) or [])
    if not lib and hasattr(M, "parse_decklist"):
        lib = list(M.parse_decklist(M.DECKLIST_TEXT))
    if "library" in campos:
        kw["library"] = [c for c in lib if c in M.CARD_DB][:70]
    s = M.GameState(**kw)
    s.turn = turno
    s.hand = list(mao)
    return s


def nomes_campo(s):
    out = []
    for p in s.battlefield:
        card = getattr(p, "card", p)
        out.append(card if isinstance(card, str) else getattr(card, "name", str(card)))
    return out


def eh_terreno(n):
    return (n in M.LAND_NAMES) if hasattr(M, "LAND_NAMES") else bool(M.is_land(n))


def tipos(c):
    t = getattr(c, "types", None)
    if t:
        return {x.lower() for x in t}
    return {str(getattr(c, "ctype", getattr(c, "type", ""))).lower()}


def nao_terreno_barato():
    return sorted((n for n, c in M.CARD_DB.items() if not eh_terreno(n) and 1 <= c.mv <= 2 and not ({"instant", "sorcery", "token"} & tipos(c))
                   and "Token" not in n and "//" not in n and n != getattr(M, "COMMANDER", None)), key=lambda n: (M.CARD_DB[n].mv, n))


# --- procura, por forca bruta, um cenario real: (virado, desvirado, magica) em que o desvirado paga a magica e o virado nao
s0 = novo_estado()
TODOS = sorted(n for n in M.CARD_DB if eh_terreno(n))
VIRADOS = [n for n in TODOS if M._tl_is_tapped(s0, n)]
DESVIRADOS = [n for n in TODOS if not M._tl_is_tapped(s0, n) and n not in getattr(M, "MDFC_LAND_SPELLS", ()) and n not in getattr(M, "MDFC_LAND_FACES", ()) and "//" not in n]
VIRADOS = [n for n in VIRADOS if n not in getattr(M, "MDFC_LAND_SPELLS", ()) and n not in getattr(M, "MDFC_LAND_FACES", ()) and "//" not in n
           and not any("bounce" in str(t).lower() for t in getattr(M.CARD_DB[n], "tags", ()))]   # bounceland: devolve terreno, nao e' o dilema virado x desvirado
CENARIO = None
if VIRADOS and DESVIRADOS:
    for t in VIRADOS[:3]:
        for u in DESVIRADOS:
            for c in nao_terreno_barato():
                try:
                    st = novo_estado(1, [t, u, c])
                    mt, mu = M._tl_dry_run_mv(st, t), M._tl_dry_run_mv(st, u)
                except Exception:
                    continue
                if mu > 0 and mt == 0:
                    CENARIO = (t, u, c)
                    break
            if CENARIO:
                break
        if CENARIO:
            break
print("cenario (virado, desvirado, magica):", CENARIO)


@teste("TL1 com uma magica que so' o desvirado paga, T1 joga o desvirado e conta o skip")
def _():
    assert CENARIO, "nao achei cenario (virado, desvirado, magica)"
    t, u, c = CENARIO
    s = novo_estado(1, [t, u, c])
    assert M.tapped_first_pick(s, [t, u]) == u
    assert s.tapped_land_skipped_for_play_total == 1 and s.tapped_land_first_plays_total == 0


@teste("TL2 sem nada pra conjurar, T1 joga o virado e conta o first-play")
def _():
    assert VIRADOS and DESVIRADOS
    t, u = VIRADOS[0], DESVIRADOS[0]
    s = novo_estado(1, [t, u])
    assert M.tapped_first_pick(s, [t, u]) == t
    assert s.tapped_land_first_plays_total == 1 and s.tapped_land_skipped_for_play_total == 0


@teste("TL3 chave desligada: primeiro da ordem propria do deck, sem contar nada")
def _():
    assert CENARIO
    t, u, c = CENARIO
    M.TAPPED_LAND_FIRST_ENABLED = False
    try:
        s = novo_estado(1, [t, u])
        assert M.tapped_first_pick(s, [u, t]) == u and M.tapped_first_pick(s, [t, u]) == t
        assert s.tapped_land_first_plays_total == 0 and s.tapped_land_skipped_for_play_total == 0
    finally:
        M.TAPPED_LAND_FIRST_ENABLED = True


@teste("TL4 em T3 a correcao nao se aplica (ordem propria do deck)")
def _():
    t, u = VIRADOS[0], DESVIRADOS[0]
    s = novo_estado(M.TAPPED_LAND_FIRST_MAX_TURN + 1, [t, u])
    assert M.tapped_first_pick(s, [u, t]) == u and M.tapped_first_pick(s, [t, u]) == t
    assert s.tapped_land_first_plays_total == 0


@teste("TL5 so' viradas ou so' desviradas na mao: ordem propria do deck")
def _():
    s = novo_estado(1, [])
    if len(VIRADOS) >= 2:
        assert M.tapped_first_pick(s, VIRADOS[:2]) == VIRADOS[0]
    if len(DESVIRADOS) >= 2:
        assert M.tapped_first_pick(s, DESVIRADOS[:2]) == DESVIRADOS[0]
    assert s.tapped_land_first_plays_total == 0 and s.tapped_land_skipped_for_play_total == 0


@teste("TL6 o ensaio nao muta estado/RNG/random global e solta a trava")
def _():
    assert CENARIO
    t, u, c = CENARIO
    s = novo_estado(1, [t, u, c])
    antes = A.impressao(s)
    rng_antes = s.rng.getstate() if hasattr(s, "rng") else None
    g_antes = random.getstate()
    M._tl_dry_run_mv(s, t)
    M._tl_dry_run_mv(s, u)
    assert A.impressao(s) == antes, "o ensaio mexeu no estado"
    if rng_antes is not None:
        assert s.rng.getstate() == rng_antes, "o ensaio consumiu o RNG do estado"
    assert random.getstate() == g_antes, "o ensaio consumiu o random global"
    assert M._TL_FORCED is None and M._TL_BUSY is False


@teste("TL8 modo GHOST: roda o ensaio mas joga o padrao e nao conta nada")
def _():
    t, u = VIRADOS[0], DESVIRADOS[0]
    s = novo_estado(1, [t, u])
    M.TAPPED_LAND_FIRST_GHOST = True
    try:
        assert M.tapped_first_pick(s, [u, t]) == u and M.tapped_first_pick(s, [t, u]) == t
        assert s.tapped_land_first_plays_total == 0 and s.tapped_land_skipped_for_play_total == 0
    finally:
        M.TAPPED_LAND_FIRST_GHOST = False


@teste("TL7 play_land joga so' o terreno escolhido (1 por turno) e o virado nao da mana no turno")
def _():
    assert VIRADOS and DESVIRADOS
    t, u = VIRADOS[0], DESVIRADOS[0]
    s = novo_estado(1, [t, u])
    def mana(st):
        try:
            return M.total_mana(st)
        except Exception:
            return None
    mana0 = mana(s)
    try:
        M.play_land(s, [])
    except TypeError:
        M.play_land(s)
    nomes = nomes_campo(s)
    assert nomes.count(t) == 1 and u not in nomes, nomes
    assert u in s.hand and t not in s.hand
    if mana0 is not None and mana(s) is not None:
        assert mana(s) == mana0, ("o terreno virado nao pode somar mana no proprio turno", mana0, mana(s))


if hasattr(M, "BOUNCELAND_ENTRY_ENABLED"):
    def _bounce_nome():
        return next(n for n in M.CARD_DB if n in M.LAND_NAMES and any("bounceland" in str(t) for t in M.CARD_DB[n].tags))

    @teste("TL9 bounceland (Izzet Boilerworks): entra VIRADO (sem mana no turno) e, com outro terreno em campo, devolve esse terreno")
    def _():
        b = _bounce_nome()
        outro = DESVIRADOS[0]
        s = novo_estado(2, [b])
        M.mk = None
        poe = M.enter_battlefield(s, outro, [], tapped=False)
        antes = M.total_mana(s)
        M.play_land(s, [])
        nomes = nomes_campo(s)
        assert b in nomes and outro not in nomes and outro in s.hand, (nomes, s.hand)
        assert M.total_mana(s) == 0, ("o bounceland entrou virado e o terreno devolvido saiu: sem mana", M.total_mana(s))

    @teste("TL10 bounceland sem outro terreno em campo devolve a si mesmo (nao fica em campo produzindo mana)")
    def _():
        b = _bounce_nome()
        s = novo_estado(1, [b])
        M.play_land(s, [])
        assert b not in nomes_campo(s) and b in s.hand and s.lands_played_this_turn == 1
        assert M.total_mana(s) == 0

    @teste("TL11 chave BOUNCELAND_ENTRY_ENABLED desligada: comportamento antigo (entra desvirado, sem devolver a si mesmo)")
    def _():
        b = _bounce_nome()
        M.BOUNCELAND_ENTRY_ENABLED = False
        try:
            s = novo_estado(1, [b])
            M.play_land(s, [])
            assert b in nomes_campo(s) and M.total_mana(s) > 0
        finally:
            M.BOUNCELAND_ENTRY_ENABLED = True

for nome, ok, tb in resultados:
    print(("PASS " if ok else "FAIL ") + nome)
    if not ok:
        print("     " + tb.strip().replace("\n", "\n     "))
print()
print(f"{sum(1 for _, ok, _ in resultados if ok)}/{len(resultados)} testes passaram")
sys.exit(0 if all(ok for _, ok, _ in resultados) else 1)

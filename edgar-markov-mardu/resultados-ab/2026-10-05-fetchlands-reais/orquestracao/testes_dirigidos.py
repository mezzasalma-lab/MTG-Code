"""Testes dirigidos da correcao 'fetchlands reais' (2026-10-05). Cada teste confere o COMPORTAMENTO que a correcao promete (nao so' que o codigo roda):
  FT1  jogar a fetch: ela vai pro cemiterio (sai do campo), a biblioteca perde exatamente 1 carta, 1 terreno entra em campo e `fetches_cracked_total` = 1
  FT2  o terreno buscado tem subtipo de terreno compativel com a fetch (oraculo: "a Mountain or Plains card"), por SUBTIPO e nao por nome
  FT3  vida: a fetch custa exatamente 1 de vida (o terreno buscado nao e' choque quando ha alternativa; nao paga 2)
  FT4  sem alvo na biblioteca: a fetch fica em campo (comportamento antigo) e `fetch_no_target_total` = 1
  FT5  politica de escolha: entre um terreno que entra virado e um que entra desvirado, busca o desvirado
  FT6  thinning: a carta buscada SAI da biblioteca (a copia buscada nao continua la')
  FT7  chave desligada (FETCH_LANDS_ENABLED=False): a fetch fica em campo, biblioteca/cemiterio intactos, contador 0 (caminho antigo)
  FT9  (so' Edgar) Sevinne's Reclamation devolve uma fetch do cemiterio ao campo e ela busca de novo
  FT8  integracao: 300 partidas completas (padrao e resiliencia) com a chave ligada: sem excecao, a fetch quebra de fato, e sobra fetch em campo so' se foi contada sem alvo
Uso: python3 testes_dirigidos_fetch.py config.json"""
import dataclasses, json, os, random, sys, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
M = A.carrega(os.path.join(DECK, cfg["sim"]), "td_ft", DECK)
NOME = os.path.basename(DECK)
EDGAR = NOME.startswith("edgar")
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


def novo_estado(turno=3):
    campos = {f.name for f in dataclasses.fields(M.GameState)}
    kw = {}
    if "rng" in campos:
        kw["rng"] = random.Random(7)
    if "library" in campos:
        kw["library"] = []   # Edgar: `library` e' argumento obrigatorio; cada teste poe a sua depois
    s = M.GameState(**kw)
    s.turn = turno
    return s


def joga(s, fetch):
    """Poe so' a fetch na mao e roda o `play_land` real do deck."""
    s.hand = [fetch]
    if hasattr(s, "lands_played_this_turn"):
        s.lands_played_this_turn = 0
    if hasattr(s, "land_played"):
        s.land_played = False
    if EDGAR:
        M.play_land(s, [])
    else:
        M.play_land(s)


def tipos_de(n):
    return set(M.LAND_BASIC_TYPES.get(n, ()))


def tapped(s, n):
    return M._tl_is_tapped(s, n)


FETCHES = sorted(M.FETCH_TYPES)
F = FETCHES[0]
TIPOS_F = set(M.FETCH_TYPES[F])
ELEG = sorted(n for n in M.LAND_BASIC_TYPES if tipos_de(n) & TIPOS_F and n in M.CARD_DB)
NAO_ELEG = sorted(n for n in M.CARD_DB if n not in M.FETCH_TYPES and n not in M.LAND_BASIC_TYPES and M.CARD_DB[n].mv >= 1 and "//" not in n)[:5]
print("fetch de teste:", F, "-> tipos", sorted(TIPOS_F), "| elegiveis:", ELEG[:6], "...")


def com_biblioteca(lib, turno=3):
    s = novo_estado(turno)
    s.library = list(lib)
    s.life = 40
    return s


@teste("FT1 a fetch vai pro cemiterio, 1 carta sai da biblioteca, 1 terreno entra e o contador sobe")
def _():
    s = com_biblioteca(ELEG[:3] + NAO_ELEG)
    n0 = len(s.library)
    joga(s, F)
    assert F not in s.battlefield and F in s.graveyard, (s.battlefield, s.graveyard)
    assert len(s.library) == n0 - 1, (n0, len(s.library))
    novos = [n for n in s.battlefield if n in M.LAND_BASIC_TYPES]
    assert len(novos) == 1, s.battlefield
    assert s.fetches_cracked_total == 1 and s.fetch_no_target_total == 0


@teste("FT2 o buscado tem subtipo compativel (varre TODAS as fetches do deck)")
def _():
    for fe in FETCHES:
        alvos = sorted(n for n in M.LAND_BASIC_TYPES if n in M.CARD_DB and tipos_de(n) & set(M.FETCH_TYPES[fe]))
        outros = sorted(n for n in M.LAND_BASIC_TYPES if n in M.CARD_DB and not (tipos_de(n) & set(M.FETCH_TYPES[fe])))
        s = com_biblioteca(outros + alvos)   # os incompativeis vem PRIMEIRO na biblioteca: a busca nao pode pegar um deles
        joga(s, fe)
        novos = [n for n in s.battlefield if n in M.LAND_BASIC_TYPES]
        assert len(novos) == 1 and tipos_de(novos[0]) & set(M.FETCH_TYPES[fe]), (fe, novos)


@teste("FT3 a fetch custa exatamente 1 de vida")
def _():
    s = com_biblioteca(ELEG[:3] + NAO_ELEG)
    joga(s, F)
    assert s.life == 39, s.life


@teste("FT4 sem alvo na biblioteca: a fetch fica em campo e conta sem-alvo")
def _():
    sem = sorted(n for n in M.LAND_BASIC_TYPES if n in M.CARD_DB and not (tipos_de(n) & TIPOS_F)) + NAO_ELEG
    s = com_biblioteca(sem)
    n0 = len(s.library)
    joga(s, F)
    assert F in s.battlefield and F not in s.graveyard
    assert len(s.library) == n0 and s.fetches_cracked_total == 0 and s.fetch_no_target_total == 1


CEN5 = None
s0 = novo_estado()
for fe in FETCHES:
    alvos = [n for n in M.LAND_BASIC_TYPES if tipos_de(n) & set(M.FETCH_TYPES[fe]) and n in M.CARD_DB]
    vir = [n for n in sorted(alvos) if tapped(s0, n)]
    des = [n for n in sorted(alvos) if not tapped(s0, n)]
    if vir and des:
        CEN5 = (fe, vir[0], des[0])
        break
print("cenario FT5 (fetch, virado, desvirado):", CEN5)


@teste("FT5 entre terreno virado e desvirado, busca o desvirado (o virado esta ANTES na biblioteca)")
def _():
    assert CEN5, "nao achei cenario"
    fe, v, d = CEN5
    s = com_biblioteca([v, d] + NAO_ELEG)
    joga(s, fe)
    assert d in s.battlefield and v not in s.battlefield and v in s.library, (s.battlefield, v, d)


@teste("FT6 thinning: a copia buscada sai da biblioteca")
def _():
    alvo = ELEG[0]
    s = com_biblioteca([alvo] + NAO_ELEG)
    joga(s, F)
    assert alvo not in s.library and alvo in s.battlefield, (s.library, s.battlefield)


@teste("FT7 chave desligada: a fetch fica em campo, nada muda na biblioteca/cemiterio, contador 0")
def _():
    M.FETCH_LANDS_ENABLED = False
    try:
        s = com_biblioteca(ELEG[:3] + NAO_ELEG)
        n0, g0 = len(s.library), list(s.graveyard)
        joga(s, F)
        assert F in s.battlefield and len(s.library) == n0 and s.graveyard == g0 and s.fetches_cracked_total == 0 and s.fetch_no_target_total == 0
    finally:
        M.FETCH_LANDS_ENABLED = True


if EDGAR:
    @teste("FT9 (Edgar) Sevinne's Reclamation devolve a fetch do cemiterio ao campo e ela tambem busca (permanente MV<=3)")
    def _():
        s = novo_estado(5)
        s.library = ["Plains", "Swamp", "Blood Crypt", "Sol Ring"]
        s.battlefield = ["Plains", "Plains", "Swamp", "Swamp", "Swamp", "Plains"]
        s.hand = ["Sevinne's Reclamation"]
        s.graveyard = ["Arid Mesa"]
        s.life = 40
        M.cast_available_spells(s, [])
        assert "Arid Mesa" in s.graveyard and "Arid Mesa" not in s.battlefield, (s.battlefield, s.graveyard)
        assert s.fetches_cracked_total == 1 and len(s.library) == 3 and s.life == 39, (s.fetches_cracked_total, s.library, s.life)


def valor(r, k, padrao=0):
    return r.get(k, padrao) if isinstance(r, dict) else getattr(r, k, padrao)


@teste("FT8 integracao: 300 partidas completas por modo, sem excecao, a fetch quebra e sobra em campo so' se contada sem alvo")
def _():
    for modo in ("padrao", "resiliencia"):
        quebradas, ok = 0, 0
        for sd in range(5_000_000, 5_000_300):
            r = A.chama(M, modo, sd, cfg.get("turns", 8), tuple(cfg["extra"]) if cfg.get("extra") is not None else None)
            quebradas += valor(r, "fetches_cracked_total")
            ok += 1
            if not isinstance(r, dict):
                restantes = sum(1 for n in r.battlefield if n in M.FETCH_TYPES)
                assert restantes <= valor(r, "fetch_no_target_total"), (modo, sd, restantes)
        assert ok == 300 and quebradas > 0, (modo, ok, quebradas)
        print(f"   {modo}: {quebradas} fetches quebradas em 300 partidas")


falhas = [(n, tb) for n, ok, tb in resultados if not ok]
for n, ok, tb in resultados:
    print(("PASS " if ok else "FAIL ") + n)
    if tb:
        print(tb)
print(f"\n{len(resultados) - len(falhas)}/{len(resultados)} testes passaram")
sys.exit(1 if falhas else 0)

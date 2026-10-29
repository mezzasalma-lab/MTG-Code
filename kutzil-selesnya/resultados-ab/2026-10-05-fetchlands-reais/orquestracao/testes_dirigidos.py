"""Testes dirigidos da correcao 'Windswept Heath real + Field of the Dead em todo terreno que entra' (Kutzil, 2026-10-05). Cada teste confere o COMPORTAMENTO prometido:
  KF1  a Heath quebra: sai do campo, vai pro cemiterio, a biblioteca perde 1 carta, 1 terreno entra, vida -1, contador +1
  KF2  busca por SUBTIPO: com SO' o Temple Garden (Forest Plains) na biblioteca, a Heath o busca (o codigo antigo, so' basicos, nao buscava nada)
  KF3  os terrenos sem subtipo Forest/Plains (que vem ANTES na biblioteca) nao sao buscados
  KF4  sem alvo: a Heath fica em campo e conta `fetch_no_target_total`
  KF5  politica: com um basico e o Temple Garden na biblioteca e falta de cor, busca o que cobre a cor que falta
  KF6  Field of the Dead dispara no terreno buscado pela Heath (7 nomes distintos -> Zombie 2/2); com a chave desligada nao dispara (comportamento antigo)
  KF7  Field of the Dead dispara no terreno da Summon: Fenrir (capitulo I); desligada nao dispara
  KF8  chave FETCH_LANDS_ENABLED desligada: busca so' basico, sem vida, sem cemiterio (caminho antigo)
  KF9  integracao: 300 partidas completas por modo, sem excecao, a Heath quebra de fato
Uso: python3 testes_dirigidos_fetch_kutzil.py config.json"""
import dataclasses, json, os, random, sys, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
M = A.carrega(os.path.join(DECK, cfg["sim"]), "td_kf", DECK)
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


def novo_estado(turno=4):
    campos = {f.name for f in dataclasses.fields(M.GameState)}
    kw = {"rng": random.Random(7)} if "rng" in campos else {}
    if "library" in campos and not any(f.name == "library" and (f.default is not dataclasses.MISSING or f.default_factory is not dataclasses.MISSING) for f in dataclasses.fields(M.GameState)):
        kw["library"] = []
    s = M.GameState(**kw)
    s.turn = turno
    s.life_total = 40
    return s


def com_heath(lib, extra_campo=()):
    s = novo_estado()
    s.library = list(lib)
    for n in extra_campo:
        s.battlefield.append(M.mk_perm(s, n))
    s.battlefield.append(M.mk_perm(s, "Windswept Heath"))
    return s


def nomes(s):
    return [p.card.name for p in s.battlefield]


def heath(s):
    M.try_windswept_heath(s, [])


def zumbis(s):
    return sum(1 for p in s.battlefield if p.card.name == "Zombie Token")


FILLER = ["Command Tower"] if "Command Tower" in M.CARD_DB else [n for n in M.CARD_DB if M.is_land_card(n) and n not in M.LAND_BASIC_TYPES and n not in ("Windswept Heath",)][:1]
NAO_FP = [n for n in sorted(M.CARD_DB) if M.is_land_card(n) and n not in M.LAND_BASIC_TYPES and n not in ("Windswept Heath", "Field of the Dead") and "//" not in n][:8]


@teste("KF1 a Heath quebra: cemiterio, biblioteca -1, terreno em campo, vida -1, contador +1")
def _():
    s = com_heath(["Forest", "Plains", "Temple Garden"] + FILLER)
    n0 = len(s.library)
    heath(s)
    assert "Windswept Heath" not in nomes(s) and "Windswept Heath" in s.graveyard, (nomes(s), s.graveyard)
    assert len(s.library) == n0 - 1 and s.life_total == 39 and s.fetches_cracked_total == 1
    assert sum(1 for n in nomes(s) if n in M.LAND_BASIC_TYPES) == 1


@teste("KF2 busca por subtipo: so' o Temple Garden (Forest Plains) na biblioteca, a Heath o busca")
def _():
    s = com_heath(["Temple Garden"] + FILLER)
    heath(s)
    assert "Temple Garden" in nomes(s) and "Temple Garden" not in s.library, nomes(s)


@teste("KF3 terrenos sem subtipo Forest/Plains, antes na biblioteca, nao sao buscados")
def _():
    s = com_heath(NAO_FP + ["Plains"])
    heath(s)
    assert "Plains" in nomes(s) and not any(n in nomes(s) for n in NAO_FP), nomes(s)


@teste("KF4 sem alvo: a Heath fica em campo e conta sem-alvo")
def _():
    s = com_heath(NAO_FP)
    n0 = len(s.library)
    heath(s)
    assert "Windswept Heath" in nomes(s) and len(s.library) == n0 and s.life_total == 40
    assert s.fetch_no_target_total == 1 and s.fetches_cracked_total == 0


@teste("KF5 politica: faltando a cor W, busca o que a cobre (Plains/Temple Garden), nao o Forest")
def _():
    s = com_heath(["Forest", "Plains"], extra_campo=["Forest", "Forest"])   # 2 fontes G, 0 de W
    heath(s)
    assert nomes(s).count("Plains") == 1 and nomes(s).count("Forest") == 2, nomes(s)


def monta_fotd(s):
    """Field of the Dead + 5 terrenos de nomes distintos (sem Forest/Temple Garden) no campo: o buscado/da Fenrir e' o 7o nome distinto."""
    for n in ["Field of the Dead"] + [x for x in NAO_FP if x not in ("Field of the Dead",)][:5]:
        s.battlefield.append(M.mk_perm(s, n))
    assert len({p.card.name for p in s.battlefield if M.is_land_card(p.card.name)}) == 6, [p.card.name for p in s.battlefield]


@teste("KF6 Field of the Dead dispara no terreno buscado pela Heath (e nao dispara com a chave desligada)")
def _():
    for flag, esperado in ((True, 1), (False, 0)):
        M.LAND_ENTER_TRIGGERS_ALL_ENABLED = flag
        try:
            s = novo_estado()
            s.library = ["Forest", "Plains"]
            monta_fotd(s)
            s.battlefield.append(M.mk_perm(s, "Windswept Heath"))   # 7 nomes com a Heath; ao quebrar, a Heath sai e o Forest entra: 7 de novo
            heath(s)
            assert zumbis(s) == esperado, (flag, zumbis(s), nomes(s))
        finally:
            M.LAND_ENTER_TRIGGERS_ALL_ENABLED = True


@teste("KF7 Field of the Dead dispara no terreno da Summon: Fenrir cap. I (e nao com a chave desligada)")
def _():
    for flag, esperado in ((True, 1), (False, 0)):
        M.LAND_ENTER_TRIGGERS_ALL_ENABLED = flag
        try:
            s = novo_estado()
            s.library = ["Forest"] + FILLER
            monta_fotd(s)
            fen = M.mk_perm(s, "Summon: Fenrir")
            fen.saga_chapter = 1
            s.battlefield.append(fen)
            M.do_saga_fenrir_chapter(s, fen, [])
            assert zumbis(s) == esperado, (flag, zumbis(s), nomes(s))
        finally:
            M.LAND_ENTER_TRIGGERS_ALL_ENABLED = True


@teste("KF8 FETCH_LANDS_ENABLED desligada: so' basico, sem vida, sem cemiterio (caminho antigo)")
def _():
    M.FETCH_LANDS_ENABLED = False
    try:
        s = com_heath(["Temple Garden", "Forest"] + FILLER)
        heath(s)
        assert "Forest" in nomes(s) and "Temple Garden" in s.library, nomes(s)
        assert s.life_total == 40 and "Windswept Heath" not in s.graveyard and s.fetches_cracked_total == 0
    finally:
        M.FETCH_LANDS_ENABLED = True


@teste("KF9 integracao: 300 partidas por modo, sem excecao, a Heath quebra de fato")
def _():
    extra = tuple(cfg["extra"]) if cfg.get("extra") is not None else None
    for modo in ("padrao", "resiliencia"):
        quebradas = 0
        for sd in range(5_000_000, 5_000_300):
            r = A.chama(M, modo, sd, cfg.get("turns", 8), extra)
            o = r[0] if isinstance(r, tuple) and r and hasattr(r[0], "__dict__") else r
            quebradas += o["fetches_cracked_total"] if isinstance(o, dict) else o.fetches_cracked_total
        assert quebradas > 0, (modo, quebradas)
        print(f"   {modo}: {quebradas} Heaths quebradas em 300 partidas")


falhas = [(n, tb) for n, ok, tb in resultados if not ok]
for n, ok, tb in resultados:
    print(("PASS " if ok else "FAIL ") + n)
    if tb:
        print(tb)
print(f"\n{len(resultados) - len(falhas)}/{len(resultados)} testes passaram")
sys.exit(1 if falhas else 0)

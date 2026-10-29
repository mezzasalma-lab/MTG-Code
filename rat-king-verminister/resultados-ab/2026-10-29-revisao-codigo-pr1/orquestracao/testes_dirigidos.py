"""Testes dirigidos da Rodada 6 do Rat King (2026-10-29), achados pela revisao de codigo do PR #1. Cada teste confere o COMPORTAMENTO prometido com a chave ligada E com ela desligada.
  R6-1  apply_own_wipe dispara o gatilho do Thornbite Staff: o holder que SOBREVIVE ao wipe desvira (carta e ficha de Mercenary); o holder que morre junto nao quebra nada; chave desligada = fica virado
  R6-2  choose_bottom nao devolve a MDFC (Fell the Profane // Fell Mire) quando ela e' o 3o terreno que should_keep contou; com 3 terrenos reais ela volta a ser a carta de maior MV; chave desligada = a devolve
  R6-3  ensaio do terreno virado: Dark Ritual + Rat Colony no T1 (semente 1000008) e Dark Ritual + Ripples of Undeath (semente 1000307) saem com o terreno desvirado; chave desligada joga o virado
  R6-4  a guarda de importacao: tirar uma criatura de CREATURE_TYPES (ou de CREATURE_TOUGHNESS) faz o simulador NAO importar
  R6-5  partidas inteiras (20.000): 0 excecoes; chave desligada: contador 0; o desvirar do Staff apos wipe meu e' LATENTE (0 disparos medidos em partidas inteiras)
Uso: python3 testes_dirigidos.py config.json"""
import contextlib, json, os, sys, traceback, tempfile, re
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
M = A.carrega(os.path.join(DECK, cfg["sim"]), "td_r6", DECK)
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


@contextlib.contextmanager
def chaves(**kw):
    antigo = {k: getattr(M, k) for k in kw}
    for k, v in kw.items():
        setattr(M, k, v)
    try:
        yield
    finally:
        for k, v in antigo.items():
            setattr(M, k, v)


def novo(turno=5, campo=(), mao=(), swamps=0, rats=0, squirrels=0, mercs=0, vida=40):
    s = M.GameState()
    s.turn = turno
    s.battlefield = list(campo) + ["Swamp"] * swamps
    s.hand = list(mao)
    s.rat_tokens, s.squirrel_tokens, s.mercenary_tokens = rats, squirrels, mercs
    s.life = vida
    s.library = ["Swamp"] * 30
    for n in s.battlefield:
        if M.is_creature_card(n):
            s.creature_cast_turn[n] = 1
    s.commander_in_play = M.COMMANDER in s.battlefield
    if s.commander_in_play:
        s.commander_cast_count = 1
    return s


SW = dict(WIPE_EFFECT_SWARMYARD=True, WIPE_EFFECT_DAMNATION=True, WIPE_EFFECT_KINDRED=True)


@teste("R6-1 Staff apos wipe meu: Swarmyard mata o Zulaport e poupa o Rat Colony (Rat = protegido) -> o holder virado desvira; chave desligada: continua virado; contador de desvirar = 1 / 0")
def _():
    for ligada in (True, False):
        with chaves(WIPE_UNTAPS_STAFF=ligada, **SW):
            s = novo(campo=["Thornbite Staff", "Rat Colony", "Zulaport Cutthroat"], swamps=5)
            s.staff_holder = "Rat Colony"
            s.tapped_creatures_this_turn.add("Rat Colony")
            plano = M.wipe_plan(s, "Swarmyard Massacre")
            assert plano["named"] == ["Zulaport Cutthroat"], plano
            M.apply_own_wipe(s, "Swarmyard Massacre")
            assert "Zulaport Cutthroat" not in s.battlefield and "Rat Colony" in s.battlefield
            virado = "Rat Colony" in s.tapped_creatures_this_turn
            assert virado == (not ligada), f"ligada={ligada}: holder virado={virado}"
            assert s.wipe_staff_untaps_total == (1 if ligada else 0), s.wipe_staff_untaps_total


@teste("R6-1b holder = ficha de Mercenary (changeling, protegida no Swarmyard): staff_tapped True -> False apos o wipe que mata o Zulaport")
def _():
    for ligada in (True, False):
        with chaves(WIPE_UNTAPS_STAFF=ligada, **SW):
            s = novo(campo=["Thornbite Staff", "Zulaport Cutthroat"], swamps=5, mercs=1)
            s.staff_holder, s.staff_tapped = "__mercenary__", True
            M.apply_own_wipe(s, "Swarmyard Massacre")
            assert s.mercenary_tokens == 1 and "Zulaport Cutthroat" not in s.battlefield
            assert s.staff_tapped == (not ligada), f"ligada={ligada}: staff_tapped={s.staff_tapped}"


@teste("R6-1c holder que MORRE no mesmo wipe (Damnation): sem excecao, holder descartado, nenhum desvirar contado; wipe que nao mata nada: nada muda")
def _():
    with chaves(WIPE_UNTAPS_STAFF=True, **SW):
        s = novo(campo=["Thornbite Staff", "Rat Colony"], swamps=5)
        s.staff_holder = "Rat Colony"; s.tapped_creatures_this_turn.add("Rat Colony")
        M.apply_own_wipe(s, "Damnation")
        assert "Rat Colony" not in s.battlefield and s.staff_holder is None and s.wipe_staff_untaps_total == 0
        s = novo(campo=["Thornbite Staff", "Rat Colony"], swamps=5)
        s.staff_holder = "Rat Colony"; s.tapped_creatures_this_turn.add("Rat Colony")
        M.apply_own_wipe(s, "Damnation") if False else None
        antes = (list(s.battlefield), set(s.tapped_creatures_this_turn))
        M.apply_own_wipe(s, "Kindred Dominance")           # so' Rats no campo: nada morre
        assert (list(s.battlefield), set(s.tapped_creatures_this_turn)) == antes and s.wipe_staff_untaps_total == 0


FELL = M.FELL_CARD


@teste("R6-2 choose_bottom: 2 terrenos + MDFC (3 'terrenos' para should_keep): a MDFC NAO e' devolvida (chave ligada); desligada: e' a carta de maior MV e vai; a mao devolvida continua passando should_keep")
def _():
    mao = ["Swamp", "Swamp", FELL, "Piper of the Swarm", "Zulaport Cutthroat", "Rat Colony", "Dark Ritual"]
    assert M.CARD_DB[FELL].mv > M.CARD_DB["Piper of the Swarm"].mv and M.should_keep(mao)
    with chaves(FELL_MIRE_PROTECTED_IN_BOTTOM=False):
        assert M.choose_bottom(mao, 1) == [FELL], M.choose_bottom(mao, 1)
    with chaves(FELL_MIRE_PROTECTED_IN_BOTTOM=True):
        fundo = M.choose_bottom(mao, 1)
        assert fundo and fundo[0] != FELL, fundo
        resto = list(mao); resto.remove(fundo[0])
        assert M.should_keep(resto), "a mao que sobra ainda tem os 3 'terrenos'"


@teste("R6-2b com 3 terrenos reais a MDFC e' so' uma magia de MV 4: pode ser devolvida (chave ligada = desligada); sem a contagem na mao (FELL_MIRE_COUNTS_FOR_KEEP desligado) a protecao nao age")
def _():
    mao = ["Swamp", "Swamp", "Swamp", FELL, "Piper of the Swarm", "Zulaport Cutthroat", "Dark Ritual"]
    with chaves(FELL_MIRE_PROTECTED_IN_BOTTOM=True):
        assert M.choose_bottom(mao, 1) == [FELL]
    mao2 = ["Swamp", "Swamp", FELL, "Piper of the Swarm", "Zulaport Cutthroat", "Rat Colony", "Dark Ritual"]
    with chaves(FELL_MIRE_PROTECTED_IN_BOTTOM=True, FELL_MIRE_COUNTS_FOR_KEEP=False):
        assert M.choose_bottom(mao2, 1) == [FELL]


@teste("R6-3 ensaio do terreno virado: semente 1000008 (Bojuka Bog x Swamp; Dark Ritual + Rat Colony) e 1000307 (Castle Locthwain x Swamp; Dark Ritual + Ripples of Undeath): com a chave o T1 joga o Swamp e a magia sai; sem ela joga o virado")
def _():
    for sd, carta, virado in ((1000008, "Rat Colony", "Bojuka Bog"), (1000307, "Ripples of Undeath", "Castle Locthwain")):
        for ligada in (True, False):
            with chaves(TAPPED_FIRST_TIEBREAK_DEV=ligada):
                s = M.simulate_one(sd, turns=1)
                saiu = carta in s.battlefield or carta in s.graveyard
                assert saiu == ligada, f"semente {sd} chave={ligada}: {carta} em campo/cemiterio={saiu}; campo={s.battlefield}"
                assert (virado in s.battlefield) == (not ligada), f"semente {sd} chave={ligada}: {virado} em campo={virado in s.battlefield}"


@teste("R6-4 guarda de importacao: sem uma criatura em CREATURE_TYPES (ou em CREATURE_TOUGHNESS) o simulador nao importa (AssertionError); o arquivo vivo importa")
def _():
    fonte = open(os.path.join(DECK, cfg["sim"]), encoding="utf-8").read()
    for tabela in ("CREATURE_TYPES", "CREATURE_TOUGHNESS"):
        ini = fonte.index(f"{tabela} = {{")
        fim = fonte.index("\n}", ini)
        bloco = fonte[ini:fim]
        linha = [l for l in bloco.split("\n") if "'Pitiless Plunderer'" in l][0]
        cortado = fonte.replace(linha + "\n", "", 1)
        assert cortado != fonte
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "sim_cortado.py")
            open(p, "w", encoding="utf-8").write(cortado)
            try:
                A.carrega(p, "sim_cortado_" + tabela, DECK)
            except AssertionError as e:
                assert "Pitiless Plunderer" in str(e), str(e)
            else:
                raise AssertionError(f"importou sem 'Pitiless Plunderer' em {tabela}")


@teste("R6-5 partidas inteiras (20.000, sementes 5_000_000+i, limite 0 e limite None): 0 excecoes; chave desligada: contador 0; o desvirar do Staff apos wipe meu e' LATENTE (0 disparos medidos: o holder nunca esta virado quando o wipe resolve, ver resumos/staff_apos_wipe_20000.txt)")
def _():
    total = {}
    for rotulo, lim, ligada in (("atual_ligada", 0, True), ("atual_desligada", 0, False), ("sempre_ligada", None, True), ("sempre_desligada", None, False)):
        with chaves(WIPE_UNTAPS_STAFF=ligada, WIPE_CAST_MAX_OWN_LOSS=lim):
            soma, exc = 0, 0
            for sd in range(5_000_000, 5_020_000):
                try:
                    soma += M.simulate_one(sd, turns=8).wipe_staff_untaps_total
                except Exception:
                    exc += 1
            assert exc == 0, f"{rotulo}: excecoes={exc}"
            total[rotulo] = soma
    print("R6-5: desvirares do Staff apos wipe meu em 20.000 partidas:", total)
    assert total["atual_desligada"] == 0 and total["sempre_desligada"] == 0, total


ok = sum(1 for _, v, _ in resultados if v)
for nome, v, tb in resultados:
    print(("OK     " if v else "FALHOU ") + nome)
    if not v:
        print(tb)
print(f"{ok} passaram, {len(resultados) - ok} falharam, {len(resultados)} testes")
sys.exit(0 if ok == len(resultados) else 1)

"""Testes dirigidos da correcao 'terreno que volta ao campo dispara landfall' (Prismatic Bridge, 2026-10-05):
  PF1  Evolution Sage em campo + um planeswalker: `_return_to_battlefield` com um terreno proliferate (+1 de lealdade) e conta `returned_land_landfall_total`
  PF2  chave LAND_ENTER_TRIGGERS_ALL_ENABLED desligada: nada acontece (caminho antigo)
  PF3  sem Evolution Sage em campo: o landfall dispara mas nao muda a lealdade (conta o retorno do terreno, 0 proliferate)
  PF4  uma criatura que volta NAO dispara landfall
  PF5  integracao: 300 partidas por modo, sem excecao
Uso: python3 testes_dirigidos_landfall_pb.py config.json"""
import dataclasses, json, os, random, sys, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
M = A.carrega(os.path.join(DECK, cfg["sim"]), "td_pf", DECK)
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


def novo_estado(turno=5):
    campos = {f.name for f in dataclasses.fields(M.GameState)}
    kw = {}
    if "rng" in campos:
        kw["rng"] = random.Random(7)
    if "library" in campos:
        kw["library"] = []
    s = M.GameState(**kw)
    s.turn = turno
    return s


PW = "Teferi, Hero of Dominaria"
TERRENO = next(n for n in sorted(M.CARD_DB) if M.is_land(n) and "//" not in n and n not in ("Fabled Passage",))   # PB nao tem basicos: qualquer terreno nao-fetch do deck


def cenario(com_sage=True):
    s = novo_estado()
    s.battlefield = [PW] + (["Evolution Sage"] if com_sage else [])
    s.loyalty[PW] = 4
    return s


@teste("PF1 terreno devolvido + Evolution Sage: proliferate (+1 de lealdade) e contador")
def _():
    s = cenario()
    l0 = s.loyalty[PW]
    M._return_to_battlefield(s, TERRENO, [])
    assert s.loyalty[PW] > l0 and s.evolution_sage_proliferates == 1 and s.returned_land_landfall_total == 1, (s.loyalty[PW], s.evolution_sage_proliferates)


@teste("PF2 chave desligada: sem landfall no terreno devolvido")
def _():
    M.LAND_ENTER_TRIGGERS_ALL_ENABLED = False
    try:
        s = cenario()
        l0 = s.loyalty[PW]
        M._return_to_battlefield(s, TERRENO, [])
        assert s.loyalty[PW] == l0 and s.evolution_sage_proliferates == 0 and s.returned_land_landfall_total == 0
    finally:
        M.LAND_ENTER_TRIGGERS_ALL_ENABLED = True


@teste("PF3 sem Evolution Sage: conta o retorno mas nao proliferate")
def _():
    s = cenario(com_sage=False)
    l0 = s.loyalty[PW]
    M._return_to_battlefield(s, TERRENO, [])
    assert s.loyalty[PW] == l0 and s.evolution_sage_proliferates == 0 and s.returned_land_landfall_total == 1


@teste("PF4 criatura devolvida nao dispara landfall")
def _():
    s = cenario()
    M._return_to_battlefield(s, "Evolution Sage", [])
    assert s.returned_land_landfall_total == 0 and s.evolution_sage_proliferates == 0


@teste("PF5 integracao: 300 partidas por modo, sem excecao")
def _():
    extra = tuple(cfg["extra"]) if cfg.get("extra") is not None else None
    total = 0
    for modo in ("padrao", "resiliencia"):
        for sd in range(5_000_000, 5_000_300):
            r = A.chama(M, modo, sd, cfg.get("turns", 8), extra)
            o = r[0] if isinstance(r, tuple) and r and hasattr(r[0], "__dict__") else r
            total += o["returned_land_landfall_total"] if isinstance(o, dict) else o.returned_land_landfall_total
        print(f"   {modo}: ok")
    print(f"   terrenos devolvidos que dispararam landfall em 600 partidas: {total}")


falhas = [(n, tb) for n, ok, tb in resultados if not ok]
for n, ok, tb in resultados:
    print(("PASS " if ok else "FAIL ") + n)
    if tb:
        print(tb)
print(f"\n{len(resultados) - len(falhas)}/{len(resultados)} testes passaram")
sys.exit(1 if falhas else 0)

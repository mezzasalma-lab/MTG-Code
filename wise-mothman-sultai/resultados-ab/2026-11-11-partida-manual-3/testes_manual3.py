"""Testes dirigidos da partida manual #3 do Wise Mothman: cada afirmacao do LEIAME/goldfish-log que depende do log bruto e' conferida contra `dados/partida.json.xz`; as que dependem de oraculo,
ruling ou regra, contra o cache do repositorio e os arquivos arquivados em `resumos/`. Cada teste tem um CONTROLE DE CORTE (a afirmacao tem de FALHAR no dado alterado), para nao passar no vazio.
Uso: python3 -I testes_manual3.py   (uma linha por teste; sai com 1 se algum falhar)
NAO prova: a intencao do usuario (ver as respostas de 2026-11-05 no LEIAME), mill de oponente, o que o log nao registra (fichas que somem)."""
import copy, json, lzma, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
T = json.load(lzma.open(os.path.join(aqui, "dados", "partida.json.xz")))
RUL = json.load(open(os.path.join(aqui, "resumos", "rulings_scryfall.json")))
CR = open(os.path.join(aqui, "resumos", "cr_trechos.txt"), encoding="utf-8").read()
ORC = json.load(open(os.path.join(aqui, "..", "..", "..", "scryfall-cache", "oracle-cache.json")))
LISTA = open(os.path.join(aqui, "..", "..", "lista.md"), encoding="utf-8").read()
res = []
def teste(nome, fn, controle=None):
    try:
        ok = bool(fn(T))
    except Exception as e:
        ok, nome = False, f"{nome} (erro: {e!r})"
    ctrl = "sem controle"
    if controle is not None:
        try:
            falha = not bool(controle())
        except Exception:
            falha = True
        ctrl = "controle de corte falha como deve" if falha else "CONTROLE NAO FALHOU (teste vacuo)"
        ok = ok and falha
    res.append(ok); print(f"{'PASSA' if ok else 'FALHA'} | {nome} | {ctrl}")
def idx(ti, pred, d=None):
    return [j for j, r in enumerate((d or T)[ti - 1]) if pred(r)]
def sem(d, ti, a, b):
    d = copy.deepcopy(d); d[ti - 1] = [r for j, r in enumerate(d[ti - 1]) if not (a <= j <= b)]; return d
FOTO = ["Breeding Pool", "Forest", "Plaza of Heroes", "Forest", "An Offer You Can't Refuse", "Tropical Island", "Forest"]
# 1. a mao da foto = as 7 primeiras compras do T1, na ordem; a 8a e' a compra do turno (Altar); sem mulligan
def t1(d):
    c = [r["name"] for r in d[0] if r["fromZone"] == "library" and r["toZone"] == "hand"]
    return c[:7] == FOTO and c[7] == "Altar of the Brood" and len(c) == 8
def c1():
    d = copy.deepcopy(T); d[0][0], d[0][1] = d[0][1], d[0][0]; return t1(d)
teste("T1: as 7 primeiras compras = mao da foto (ordem), a 8a = Altar of the Brood", t1, c1)
# 2. T4: Mothman sai do comando com 4 terrenos virados que so' dao G/U; a Plaza estava na mao (descartada pela Dark Deal)
def cores(n):
    t = ORC[n].get("oracle_text") or ""; tl = ORC[n]["type_line"]
    s = {c for c, nome in (("G", "Forest"), ("U", "Island"), ("B", "Swamp"), ("R", "Mountain"), ("W", "Plains")) if nome in tl}
    return s
def t2(d):
    cast = idx(4, lambda r: r["name"] == "The Wise Mothman" and r["fromZone"] == "commandZone", d)
    viradas = [r["name"] for r in d[3] if r["tapped"] and r["zone"] == "battlefield" and r["toZone"] is None and "Land" in ORC[r["name"]]["type_line"]]
    cs = set().union(*(cores(n) for n in viradas))
    plaza = idx(4, lambda r: r["name"] == "Plaza of Heroes" and r["fromZone"] == "hand" and r["toZone"] == "graveyard", d)
    return len(cast) == 1 and len(viradas) == 4 and "B" not in cs and cs == {"G", "U"} and plaza and "{B}" in ORC["The Wise Mothman"]["mana_cost"]
def c2():
    d = copy.deepcopy(T)
    for r in d[3]:
        if r["name"] == "Forest" and r["tapped"] and r["toZone"] is None:
            r["name"] = "Overgrown Tomb"      # com um terreno que da B a afirmacao tem de cair
            break
    return t2(d)
teste("T4: Mothman ({1}{B}{G}{U}) com 4 terrenos virados que so' dao G e U; Plaza na mao", t2, c2)
# 3. T4: Dark Deal: 6 descartadas, 4 compradas (esperado 5)
def t3(d):
    dd = idx(4, lambda r: r["name"] == "Dark Deal", d)[0]
    desc = [r for j, r in enumerate(d[3]) if j > dd and r["fromZone"] == "hand" and r["toZone"] == "graveyard"]
    comp = [r for j, r in enumerate(d[3]) if j > dd and r["fromZone"] == "library" and r["toZone"] == "hand"]
    return len(desc) == 6 and len(comp) == 4 and "minus one" in ORC["Dark Deal"]["oracle_text"]
def c3():
    d = copy.deepcopy(T); extra = copy.deepcopy(d[3][-1]); extra["id"] += "x"; d[3].append(extra); return t3(d)
teste("T4: Dark Deal: 6 cartas descartadas e 4 compradas (o texto manda 6 - 1 = 5)", t3, c3)
# 4. T5: 1 mill proprio (Gyre Sage), T6: nenhum (rad do T5 esquecido no T6)
def t4(d):
    mills = [[r["name"] for r in t if r["fromZone"] == "library" and r["toZone"] == "graveyard"] for t in d]
    return mills == [[], [], [], [], ["Gyre Sage"], []]
teste("mill proprio por turno: so' a Gyre Sage no T5; nenhum no T6", t4, lambda: t4(sem(T, 5, 5, 5)))
# 5. T5: 7 cliques seguidos de +1 no Mothman DEPOIS da Six, nenhum na Six; fim do T5 = 8
def t5(d):
    six = idx(5, lambda r: r["name"] == "Six" and r["toZone"] == "battlefield", d)[0]
    cl = [r["counters"]["+1 / +1"]["count"] for j, r in enumerate(d[4]) if j > six and r["name"] == "The Wise Mothman" and "+1 / +1" in r["counters"]]
    sem_six = not any(r["name"] == "Six" and "+1 / +1" in r["counters"] for r in d[4])
    return cl[:7] == [2, 3, 4, 5, 6, 7, 8] and sem_six
teste("T5: depois da Six, +1 no Mothman 2..8 (7 cliques) e nenhum contador na Six", t5, lambda: t5(sem(T, 5, 15, 15)))
# 6. T6: Springs do cemiterio direto para o campo; Gyre Sage cemiterio->campo e depois ->mao
def t6(d):
    s = idx(6, lambda r: r["name"] == "Rejuvenating Springs" and r["fromZone"] == "graveyard" and r["toZone"] == "battlefield", d)
    g1 = idx(6, lambda r: r["name"] == "Gyre Sage" and r["fromZone"] == "graveyard" and r["toZone"] == "battlefield", d)
    g2 = idx(6, lambda r: r["name"] == "Gyre Sage" and r["fromZone"] == "graveyard" and r["toZone"] == "hand", d)
    ult = {}
    for r in d[5]: ult[r["name"]] = r
    return len(s) == 1 and g1 and g2 and g1[0] < g2[0] and ult["Rejuvenating Springs"]["zone"] == "battlefield" and ult["Gyre Sage"]["zone"] == "hand"
teste("T6: Springs vai do cemiterio ao campo e termina em campo; Gyre Sage campo -> mao", t6, lambda: t6(sem(T, 6, 13, 13)))
# 7. T6: 2 Instants devolvidos a mao (Didn't Say Please e An Offer You Can't Refuse)
def t7(d):
    voltou = [r["name"] for r in d[5] if r["fromZone"] == "graveyard" and r["toZone"] == "hand"]
    inst = [n for n in voltou if "Instant" in ORC[n]["type_line"]]
    return sorted(inst) == ["An Offer You Can't Refuse", "Didn't Say Please"] and "permanent card" in ORC["Evolution Witness"]["oracle_text"]
teste("T6: a Witness devolve 'permanent card' e o log leva 2 Instants a mao", t7, lambda: t7(sem(T, 6, 15, 15)))
# 8. T6: 6 cartas distintas saem do cemiterio para 5 eventos de contador na Witness
def t8(d):
    saiu = {r["name"] for r in d[5] if r["fromZone"] == "graveyard" and r["toZone"] in ("hand", "battlefield")}
    ev = [r["counters"]["+1 / +1"]["count"] for r in d[5] if r["name"] == "Evolution Witness" and "+1 / +1" in r["counters"]]
    return len(saiu) == 6 and ev == [2, 4, 5]
teste("T6: 6 cartas saem do cemiterio; a Witness chega a 5 contadores (registros 2, 4, 5)", t8, lambda: t8(sem(T, 6, 27, 27)))
# 9. dois terrenos no T6 (Overgrown Tomb da mao + Springs do cemiterio); 1 por turno de T1 a T5
def t9(d):
    for ti in range(1, 6):
        n = {r["id"] for r in d[ti - 1] if r["fromZone"] == "hand" and r["toZone"] == "battlefield" and "Land" in ORC[r["name"]]["type_line"]}
        if len(n) != 1:
            return False
    mao6 = {r["id"] for r in d[5] if r["fromZone"] == "hand" and r["toZone"] == "battlefield" and "Land" in ORC[r["name"]]["type_line"]}
    cem6 = {r["id"] for r in d[5] if r["fromZone"] == "graveyard" and r["toZone"] == "battlefield" and "Land" in ORC[r["name"]]["type_line"]}
    return len(mao6) == 1 and len(cem6) == 1
teste("terrenos: 1 por turno de T1 a T5; T6 tem Tomb (mao) + Springs (cemiterio)", t9, lambda: t9(sem(T, 6, 13, 13)))
# 10. interacao simulada: so' a Dark Deal, no T4
def t10(d):
    return [[r["name"] for r in t if r["zone"] == "opponentsCards"] for t in d] == [[], [], [], ["Dark Deal"], [], []]
teste("simulador de interacao: so' a Dark Deal (T4)", t10, lambda: t10(sem(T, 4, 8, 8)))
# 11. mana: T5 3 viradas para a Six; T6 5 viradas (Witness 3 + Nature's Lore 2)
def t11(d):
    def virados(ti):
        ult = {}
        for r in d[ti - 1]: ult[r["id"]] = r
        return [r["name"] for r in ult.values() if r["zone"] == "battlefield" and r["tapped"] and "Land" in ORC[r["name"]]["type_line"] and not (r["fromZone"] and r["toZone"] == "battlefield")]
    return len(virados(5)) == 3 and len(virados(6)) == 5
teste("mana: T5 3 terrenos virados (Six {2}{G}); T6 5 (Witness 3 + Nature's Lore 2)", t11, lambda: t11(sem(T, 6, 17, 18)))
# 12. todas as cartas do log (exceto a Dark Deal) estao na lista atual
def t12(_):
    nomes = {r["name"] for t in T for r in t if not r["token"]}
    return all(n in LISTA for n in nomes - {"Dark Deal"}) and "Dark Deal" not in LISTA
teste("todas as cartas do log estao na lista.md (a Dark Deal e' do oponente simulado)", t12, lambda: "Dark Deal" in LISTA)
# 13. rulings arquivadas do Mothman e CR
def t13(rul):
    mm = " ".join(c for _, c in rul["The Wise Mothman"]["rulings"])
    return ("trigger just once" in mm or "will trigger just once" in mm) and "exactly once" in mm and "all at once" in mm and "728.1" in CR and "702.81a" in CR and "305.2" in CR
def c13():
    r = copy.deepcopy(RUL); r["The Wise Mothman"]["rulings"] = []; return t13(r)
teste("rulings do Mothman (gatilho 1x por mill simultaneo) e CR 728.1, 702.81a, 305.2 arquivadas", lambda _: t13(RUL), c13)
print(f"\n{sum(res)}/{len(res)} testes passam")
sys.exit(0 if all(res) else 1)

"""Ensaio a seco (dry-run) dos wipes/efeitos de sacrificio em massa (todas as variantes de `sac_harness.VARIANTES`) x Blasphemous Act, sobre estados NATURAIS do goldfish. A cada fase principal
(turno >= 3) de partidas do modo padrao, copia o estado (deepcopy) e, em copias separadas, conjura cada variante pelo caminho real do simulador (`cast_card`: custo, pagamento primeiro com
Treasures animados, gatilhos), sem a retencao (so' pra medir), registrando o que cada uma causa so' no MEU lado. Estratos: com/sem Mayhem Devil, 1a main x 2a main (apos o combate, com animados),
4+ animados. Tambem registra a castabilidade por COR (o simulador so' conta mana: aqui cada ensaio ve' se as fontes em campo cobrem os simbolos de cor da carta; otimista).
NAO mede o efeito nas criaturas/permanentes do oponente (📊): e' o piso de cada variante, nao o valor dela.
Uso: python3 sac_dry_run.py [N] [semente0] [--bruto arquivo.json.xz]   (--bruto salva as amostras cruas, em colunas)
     FX_MODO=resiliencia python3 sac_dry_run.py ...                      (estados sob pressao de interacao de oponente)
     python3 sac_dry_run.py --sum --bruto arquivo.json.xz                (refaz as tabelas so' do bruto)"""
import copy, json, lzma, math, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
import sac_harness as H

SUM = "--sum" in sys.argv   # refaz as tabelas SO' a partir do bruto arquivado (--bruto arquivo), sem simular nada
BRUTO = sys.argv[sys.argv.index("--bruto") + 1] if "--bruto" in sys.argv else None
args = [a for a in sys.argv[1:] if not a.startswith("--") and a != BRUTO]
if BRUTO:
    BRUTO = os.path.abspath(BRUTO)   # o carregador do simulador faz chdir pro deck: caminho relativo quebraria depois
N = int(args[0]) if len(args) > 0 else 3000
S0 = int(args[1]) if len(args) > 1 else 3_000_000
MODO = os.environ.get("FX_MODO", "padrao")   # "padrao" | "resiliencia" (estados sob pressao de interacao de oponente)
V = F.flags(F.carrega(F.DEPOIS, "vih_dryrun"))
H.instala(V)
V.OWN_WIPE_HOLD_ALWAYS_ENABLED = False   # so' pra medir: a retencao da 10a rodada impediria o cast
V.OWN_WIPE_HOLD_ENGINE_ENABLED = False
ACT = "Blasphemous Act"
TODAS = H.REFERENCIAS + H.VARIANTES
amostras = []
contador = {}
violacoes = {}     # nome da violacao -> contagem (so' as introduzidas pelo ensaio)
excecoes = []


def metricas(s):
    nome = [n for n in s.battlefield if n not in V.LAND_NAMES]
    anim = min(s.treasures_animated_alive, s.treasures)
    return {"dreno": s.drain_damage_total, "mesa": s.table_damage_total, "mortes": s.creature_deaths_total,
            "nomeadas": sum(1 for n in nome if V.is_creature_card(n)), "fichas": s.constructs + s.other_tokens + s.dragons + anim,
            "outros": sum(1 for n in nome if not V.is_creature_card(n)), "estoque": s.treasures,
            "perm": len(nome) + s.constructs + s.other_tokens + s.dragons + s.treasures + s.clues + s.foods, "vihaan": 1 if s.commander_in_play else 0,
            "mahadi": 1 if "Mahadi, Emporium Master" in s.battlefield else 0, "mayhem": 1 if "Mayhem Devil" in s.battlefield else 0,
            "criados": s.treasures_created_total, "cartas": s.cards_drawn_extra, "mana_resta": V.remaining_mana(s), "pagos": s.own_wipe_animated_paid_total,
            "vida": s.life_gained_total}


def ensaio(state, carta):
    cor = H.cor_ok(V, state, carta)
    c = copy.deepcopy(state)
    c.hand.append(carta)
    custo = V.spell_cost(c, carta)
    if not V.can_cast(c, carta):
        return {"cast": False, "cor": cor, "custo": custo}
    antes = metricas(c)
    c._info = {}
    base_v = set(H.invariantes(V, c))
    try:
        V.cast_card(c, carta)
    except Exception as e:   # nunca deve ocorrer; contado e impresso
        excecoes.append((carta, repr(e)))
        return {"cast": False, "cor": cor, "custo": custo}
    for x in H.invariantes(V, c):
        if x not in base_v:
            violacoes[(carta, x)] = violacoes.get((carta, x), 0) + 1
    depois = metricas(c)
    d = {k: depois[k] - antes[k] for k in antes}
    info = getattr(c, "_info", {}) or {}
    d.update({"cast": True, "cor": cor, "custo": custo, "n_opp": info.get("n_opp"), "minhas_sac": info.get("n_minhas"), "reviveram": info.get("reviveram", 0),
              "perdidas": (antes["nomeadas"] + antes["fichas"]) - (depois["nomeadas"] + depois["fichas"]),
              "vihaan_morre": antes["vihaan"] - depois["vihaan"], "mayhem_morre": antes["mayhem"] - depois["mayhem"], "mahadi_morre": antes["mahadi"] - depois["mahadi"],
              "mana_resta": depois["mana_resta"]})
    return d


orig_main = V.main_phase


def main_espia(state):
    if state.turn >= 3:
        k = contador.get(id(state), (None, 0))
        n = k[1] + 1 if k[0] == state.turn else 1
        contador[id(state)] = (state.turn, n)
        fase = "2a main (pos-combate)" if n >= 2 else "1a main"
        H.FASE = "2a main" if n >= 2 else "1a main"
        inv = H.inventario(V, state)
        gy_cre = sum(1 for x in state.graveyard if V.is_creature_card(x))
        amostras.append({"fase": fase, "mayhem": "Mayhem Devil" in state.battlefield, "bats": "Mirkwood Bats" in state.battlefield, "vihaan": state.commander_in_play,
                         "criaturas": H.total_criaturas(inv), "animados": inv["anim"], "estoque": state.treasures, "gy_cre": gy_cre, "turno": state.turn,
                         "dictate": "Dictate of Erebos" in state.battlefield, "plund": "Pitiless Plunderer" in state.battlefield, "mahadi": "Mahadi, Emporium Master" in state.battlefield,
                         "r": {v: ensaio(state, v) for v in TODAS}})
    return orig_main(state)


CAMPOS_AMOSTRA = ["fase", "mayhem", "bats", "vihaan", "criaturas", "animados", "estoque", "gy_cre", "turno", "dictate", "plund", "mahadi"]
CAMPOS_R = ["cast", "cor", "custo", "n_opp", "minhas_sac", "perdidas", "perm", "outros", "estoque", "dreno", "mesa", "vihaan_morre", "mayhem_morre", "mahadi_morre", "mana_resta", "reviveram", "cartas", "criados", "pagos"]


def salva_bruto(caminho):
    cols = {c: [a[c] for a in amostras] for c in CAMPOS_AMOSTRA}
    res = {v: {c: [a["r"][v].get(c) for a in amostras] for c in CAMPOS_R} for v in TODAS}
    for v in res.values():
        for c in ("cast", "cor"):
            v[c] = [int(x) for x in v[c]]
    for c in ("mayhem", "bats", "vihaan", "dictate", "plund", "mahadi"):
        cols[c] = [int(x) for x in cols[c]]
    with lzma.open(caminho, "wt", preset=9) as f:
        json.dump({"formato": "amostras-colunas-v1", "modo": MODO, "N": N, "S0": S0, "variantes": TODAS, "campos_amostra": CAMPOS_AMOSTRA, "campos_r": CAMPOS_R, "amostras": cols, "resultados": res,
                   "violacoes": sorted([list(k) + [v] for k, v in violacoes.items()]), "excecoes": excecoes[:20], "n_excecoes": len(excecoes)}, f, ensure_ascii=False)


def carrega_bruto(caminho):
    d = json.load(lzma.open(caminho, "rt"))
    n = len(d["amostras"]["turno"])
    out = []
    for i in range(n):
        a = {c: d["amostras"][c][i] for c in d["campos_amostra"]}
        for c in ("mayhem", "bats", "vihaan", "dictate", "plund", "mahadi"):
            a[c] = bool(a[c])
        a["r"] = {}
        for v in d["variantes"]:
            r = {c: d["resultados"][v][c][i] for c in d["campos_r"]}
            r["cast"], r["cor"] = bool(r["cast"]), bool(r["cor"])
            a["r"][v] = r
        out.append(a)
    return d, out


if SUM:
    d, amostras = carrega_bruto(BRUTO)
    N, S0, MODO = d["N"], d["S0"], d["modo"]
    violacoes = {(x[0], x[1]): x[2] for x in d["violacoes"]}
    excecoes = d["excecoes"] + [None] * (d["n_excecoes"] - len(d["excecoes"]))
else:
    V.main_phase = main_espia
    fn = V.simulate_one if MODO == "padrao" else V.simulate_one_with_interaction
    for i in range(N):
        contador.clear()
        fn(S0 + i)
    if BRUTO:
        salva_bruto(BRUTO)


def media(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return (float("nan"), 0.0)
    return (st.mean(xs), 1.96 * st.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 and len(set(xs)) > 1 else 0.0)


def ok(a, v):
    r = a["r"][v]
    return r["cast"] and r["cor"]


def tabela(rotulo, sel):
    amo = [a for a in amostras if sel(a)]
    print(f"\n### {rotulo}: {len(amo)} estados")
    if not amo:
        return
    print("%-47s %6s %7s %5s %5s %7s %6s %9s %8s %9s %7s %7s %7s" % ("variante (media por estado onde conjuravel por mana E cor; so' meu lado)", "%mana", "%mana+cor", "custo", "N/opp", "perdidas",
                                                                      "perm-", "estoqueΔ", "dreno", "dreno-Act", "Vihaan†", "Mayhem†", "mana+"))
    base = {id(a): a["r"][ACT] for a in amo}
    for v in TODAS:
        pm = sum(1 for a in amo if a["r"][v]["cast"])
        pc = sum(1 for a in amo if ok(a, v))
        com = [a for a in amo if ok(a, v)]
        if not com:
            print("%-47s %5.1f%% %8.1f%%   (nunca conjuravel por mana+cor)" % (v[:47], 100.0 * pm / len(amo), 100.0 * pc / len(amo)))
            continue
        rs = [a["r"][v] for a in com]
        par = [a for a in com if ok(a, ACT)]
        dif = [a["r"][v]["dreno"] - a["r"][ACT]["dreno"] for a in par]
        nopp = [r["n_opp"] for r in rs if r.get("n_opp") is not None]
        print("%-47s %5.1f%% %8.1f%% %5.1f %5s %7.2f %6.2f %+9.2f %8.2f %+6.2f±%-4.2f %6.1f%% %6.1f%% %7.2f" % (
            v[:47], 100.0 * pm / len(amo), 100.0 * pc / len(amo), media([r["custo"] for r in rs])[0], ("%.1f" % media(nopp)[0]) if nopp else "-",
            media([r["perdidas"] for r in rs])[0], -media([r["perm"] for r in rs])[0], media([r["estoque"] for r in rs])[0], media([r["dreno"] for r in rs])[0],
            media(dif)[0] if dif else float("nan"), media(dif)[1] if dif else 0.0, 100.0 * media([r["vihaan_morre"] for r in rs])[0], 100.0 * media([r["mayhem_morre"] for r in rs])[0],
            media([r["mana_resta"] for r in rs])[0]))


print(f"N={N} partidas (modo {MODO}, sementes {S0}..{S0 + N - 1}); {len(amostras)} estados amostrados (turno >= 3, 1a e 2a main).")
print("Colunas: %mana = conjuravel so' por quantidade de mana (o que o simulador ve'); %mana+cor = tambem cobre os simbolos de cor (otimista); custo = mana pago; N/opp = quantas criaturas CADA")
print("oponente sacrificaria (so' as de numero fixo/livre; as demais ficam '-'); perdidas = minhas criaturas+fichas+animados que saem (sem contar o que paga o custo); perm- = TODOS os meus permanentes")
print("nao-terreno que saem (criaturas, fichas, Treasures, Clues, Foods, artefatos e encantamentos; inclui o que paga o custo; negativo = ganhei mais do que perdi); estoqueΔ = variacao liquida do estoque de")
print("Treasures (inclui os gastos no custo); dreno = proxy de dano/dreno do meu lado (Mayhem/Zulaport/Bats/...; NAO inclui o que o lado do oponente geraria); dreno-Act = diferenca pareada vs Blasphemous Act")
print("nos estados em que as DUAS sao conjuraveis; Vihaan†/Mayhem† = % dos casos em que morre (entre os conjuraveis); mana+ = mana que sobra.")
tabela("TODOS os estados", lambda a: True)
tabela("com Mayhem Devil em campo", lambda a: a["mayhem"])
tabela("sem Mayhem Devil em campo", lambda a: not a["mayhem"])
tabela("2a main (apos o combate)", lambda a: a["fase"].startswith("2a"))
tabela("com Mayhem Devil, 2a main", lambda a: a["mayhem"] and a["fase"].startswith("2a"))
tabela("2a main, 4 ou mais animados (com ou sem Mayhem Devil)", lambda a: a["fase"].startswith("2a") and a["animados"] >= 4)
tabela("com Mayhem Devil, 2a main, 4 ou mais animados", lambda a: a["mayhem"] and a["fase"].startswith("2a") and a["animados"] >= 4)
tabela("turno >= 6 (partida mais avancada)", lambda a: a["turno"] >= 6)
tabela("minhas criaturas >= 6 (um wipe e' plausivel)", lambda a: a["criaturas"] >= 6)
tabela("com 3 ou mais cartas de criatura no cemiterio (Living Death)", lambda a: a["gy_cre"] >= 3)

print("\n### Distribuicao dos estados amostrados (turno >= 3, 1a e 2a main)")
tot = len(amostras)


def pct(x):
    return "%.1f%% (%d de %d)" % (100.0 * x / tot, x, tot)


print("  Mayhem Devil em campo:", pct(sum(1 for a in amostras if a["mayhem"])))
print("  Mirkwood Bats em campo:", pct(sum(1 for a in amostras if a["bats"])))
for lim in (2, 4, 8, 13, 14):
    print(f"  minhas criaturas (nomeadas + fichas + animados) >= {lim}:", pct(sum(1 for a in amostras if a["criaturas"] >= lim)))
print("  criaturas minhas: media %.2f | animados: media %.2f | estoque de Treasures: media %.2f | cartas de criatura no cemiterio: media %.2f" % (
    st.mean(a["criaturas"] for a in amostras), st.mean(a["animados"] for a in amostras), st.mean(a["estoque"] for a in amostras), st.mean(a["gy_cre"] for a in amostras)))
print("  Vihaan em campo:", pct(sum(1 for a in amostras if a["vihaan"])))
print("  Dictate of Erebos em campo:", pct(sum(1 for a in amostras if a["dictate"])), "| Pitiless Plunderer:", pct(sum(1 for a in amostras if a["plund"])), "| Mahadi:", pct(sum(1 for a in amostras if a["mahadi"])))
print("\n### Invariantes (violacoes introduzidas pelo ensaio) e excecoes:", "NENHUMA violacao" if not violacoes else sorted(violacoes.items()), "| excecoes:", len(excecoes), excecoes[:3])

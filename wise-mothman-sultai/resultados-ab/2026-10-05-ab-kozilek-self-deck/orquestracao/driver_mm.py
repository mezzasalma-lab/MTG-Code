"""Driver do A/B do simulador do Mothman (2026-10-05). Le `config.json` e roda:
  smoke -> biblioteca (99 cartas, 0 desconhecidas, 0 duplicadas nao-basicas) para cada variante + 200 partidas por modo (excecoes);
  reg   -> regressao (sementes 5_000_000+i, N por config): excecoes + invariantes genericas, nas variantes de `regressao`, dois modos;
  ab    -> lotes 2000 (sementes 1_000_000+i, todas as variantes) e 10000 (sementes 3_000_000+i, so' `variantes_10000`), modos padrao e resiliencia: tabela pareada
           (variante - base) com IC95% e brutos em colunas-v1 (.json.xz);
  sum   -> refaz as tabelas SO' dos brutos arquivados.
Uso: python3 driver_mm.py config.json [smoke|reg|ab|sum|tudo] [N_reg]"""
import json, os, sys, collections
if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A

cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
ETAPA = sys.argv[2] if len(sys.argv) > 2 else "tudo"
NREG = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
OUTDIR = os.path.abspath(os.environ.get("DRIVER_OUT") or ARQ)
DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
SIM = os.path.join(DECK, cfg["sim"])
TURNS = cfg["turns"]
MODOS = ("padrao", "resiliencia")
DEST = cfg["destaque"]
VAR = cfg["variantes"]
os.makedirs(os.path.join(OUTDIR, "resumos"), exist_ok=True)
os.makedirs(os.path.join(OUTDIR, "dados"), exist_ok=True)


def out(nome, txt):
    open(os.path.join(OUTDIR, "resumos", nome), "w").write(txt if txt.endswith("\n") else txt + "\n")
    print(txt)


def smoke():
    linhas = []
    for nome, fl in VAR.items():
        m = A.carrega(SIM, "smoke_" + nome[:12], DECK)
        for k, v in fl.items():
            setattr(m, k, v)
        bl = m.current_library()
        cnt = collections.Counter(bl)
        desc = [n for n in set(bl) if n not in m.CARD_DB]
        dup = sorted(n for n, k in cnt.items() if k > 1 and n not in ("Forest", "Island", "Swamp"))
        exc = {}
        for modo in MODOS:
            e = 0
            for sd in range(1_000_000, 1_000_200):
                try:
                    A.chama(m, modo, sd, TURNS)
                except Exception:
                    e += 1
            exc[modo] = e
        linhas.append(f"{nome:34s} cartas={len(bl)} distintas={len(cnt)} desconhecidas={desc} duplicadas_nao_basicas={dup} excecoes_200: {exc}")
    out("smoke.txt", "\n".join(linhas))


def reg():
    linhas = [f"Regressao: N={NREG} por variante/modo, sementes 5_000_000+i; excecoes + invariantes genericas (carta acima do baralho em alguma zona; contadores negativos)"]
    for nome in cfg["regressao"]:
        for modo in MODOS:
            r = A.regressao(SIM, f"reg_{nome[:8]}_{modo}", DECK, VAR[nome], modo, NREG, 5_000_000, TURNS)
            linhas.append(f"{nome:34s} {modo:12s} partidas ok={r['partidas_ok']} | excecoes={sum(r['excecoes'].values())} {r['excecoes'] or ''} | carta acima do baralho={r['carta_acima_do_baralho']} | campos negativos={r['campos_negativos']}")
    out("regressao_%d.txt" % NREG, "\n".join(linhas))


LOTES = [l for l in ((2000, 1_000_000), (10000, 3_000_000)) if str(l[0]) in os.environ.get("LOTES", "2000,10000").split(",")]   # env LOTES=2000: so' o lote pequeno (re-execucao rapida)


def tabelas(res, N, seed0, modo):
    partes = [f"LOTE N={N} sementes {seed0}..{seed0 + N - 1}, {TURNS} turnos, modo {modo}"]
    for nome in res:
        if nome == "base":
            continue
        partes.append(A.tabela_pareada(res["base"], res[nome], DEST, rotulo=f"[{nome} - base]"))
    return "\n\n".join(partes)


def ab():
    for N, seed0 in LOTES:
        nomes = list(VAR) if N == 2000 else cfg["variantes_10000"]
        for modo in MODOS:
            seeds = range(seed0, seed0 + N)
            res = {}
            for nome in nomes:
                res[nome] = A.serie_paralela(SIM, f"ab_{nome[:10]}_{modo}_{N}", DECK, VAR[nome], modo, seeds, TURNS)
                print("feito", N, modo, nome, flush=True)
            suf = "" if modo == "padrao" else "_resiliencia"
            A.salvar_raw(os.path.join(OUTDIR, "dados", f"raw_ab_{N}{suf}"), res)
            out(f"ab_{N}{suf}.txt", tabelas(res, N, seed0, modo))


def soma():
    for N, seed0 in LOTES:
        for modo in MODOS:
            suf = "" if modo == "padrao" else "_resiliencia"
            res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_ab_{N}{suf}"))
            out(f"ab_{N}{suf}.txt", tabelas(res, N, seed0, modo))


COMPACTO = ["cleared_T7", "cleared_T8", "cleared_T9", "cleared_T10", "first_elim_T6", "first_elim_T8", "self_lost", "decked", "opps_eliminated_total", "mothman_triggers_total", "counters_placed_total", "library_min", "kozilek_shuffles_total"]


def compacto():
    """Uma linha por variante (media na variante e diferenca pareada vs base com IC95%) para as metricas centrais: refeito SO' dos brutos arquivados."""
    import statistics as st
    for N, seed0 in LOTES:
        for modo in MODOS:
            suf = "" if modo == "padrao" else "_resiliencia"
            res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_ab_{N}{suf}"))
            base = res["base"]
            linhas = [f"COMPACTO N={N} modo {modo}: media da base e, por variante, diferenca pareada (variante - base) +- IC95%. '*' = |dif| > IC."]
            linhas.append("%-52s " % "variante" + " ".join("%22s" % c for c in COMPACTO))
            medias = {c: st.mean(x[1].get(c, 0.0) for x in base) for c in COMPACTO}
            linhas.append("%-52s " % "base (media)" + " ".join("%22.4f" % medias[c] for c in COMPACTO))
            for nome, rs in res.items():
                if nome == "base":
                    continue
                cel = []
                for c in COMPACTO:
                    m, h = A.ic([x[1].get(c, 0.0) for x in base], [x[1].get(c, 0.0) for x in rs])
                    cel.append("%+10.4f±%-8.4f%s" % (m, h, "*" if abs(m) > h else " "))
                linhas.append("%-52s " % nome + " ".join("%22s" % c for c in cel))
            out(f"compacto_{N}{suf}.txt", "\n".join(linhas))


if ETAPA in ("smoke", "tudo"):
    smoke()
if ETAPA in ("reg", "tudo"):
    reg()
if ETAPA in ("ab", "tudo"):
    ab()
    compacto()
if ETAPA == "sum":
    soma()
    compacto()
if ETAPA == "compacto":
    compacto()

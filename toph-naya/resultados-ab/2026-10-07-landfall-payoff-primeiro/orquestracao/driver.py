"""Driver generico de validacao de uma correcao de simulador (2026-10-05). Le um `config.json` (na pasta do arquivo `resultados-ab/<data>-<tema>/orquestracao/`) e roda as etapas:
  smoke  -> importa o simulador vivo e o snapshot, confere biblioteca (99 cartas, 0 desconhecidas) e roda 200 partidas por modo;
  bitid  -> N partidas (padrao e resiliencia) com as chaves da correcao DESLIGADAS == snapshot (impressao digital do resultado inteiro);
  ab     -> lotes 2000 (sementes 1_000_000+i) e 10000 (3_000_000+i), modos padrao e resiliencia: variantes `antes` (snapshot), `depois` (o que fica no repositorio) e as de
            sensibilidade do config; tabela pareada com IC95% e brutos em colunas-v1 (.json.xz);
  reg    -> regressao (sementes 5_000_000+i): excecoes + invariantes genericas, configuracoes `depois` e `chave_desligada`, dois modos.
Uso: python3 driver.py config.json [smoke|bitid|ghost|ab|reg|sum|tudo] [N_bitid] [N_reg]   (sum = refaz as tabelas do A/B so' dos brutos)"""
import json, os, sys, time
# Reprodutibilidade entre processos: a ordem de iteracao de set/frozenset de str muda com PYTHONHASHSEED. Fixa 0 re-executando a si mesmo (os workers do Pool herdam).
if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A

cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "config.json")))
ETAPA = sys.argv[2] if len(sys.argv) > 2 else "tudo"
NBIT = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
NREG = int(sys.argv[4]) if len(sys.argv) > 4 else 20000
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
OUTDIR = os.path.abspath(os.environ.get("DRIVER_OUT") or ARQ)   # DRIVER_OUT: re-execucao sem sobrescrever o arquivo
DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
SIM = os.path.join(DECK, cfg["sim"])
SNAP = os.path.join(ARQ, cfg["snapshot"])
TURNS = cfg.get("turns", 8)
EXTRA = tuple(cfg["extra"]) if cfg.get("extra") is not None else None
IGNORA = tuple(cfg.get("ignora_campos", []))
OFF = cfg["flags_off"]
MODOS = ("padrao", "resiliencia")
DEST = cfg.get("destaque", [])
os.makedirs(os.path.join(OUTDIR, "resumos"), exist_ok=True)
os.makedirs(os.path.join(OUTDIR, "dados"), exist_ok=True)


LOTES = [l for l in ((2000, 1_000_000), (10000, 3_000_000)) if str(l[0]) in os.environ.get("LOTES", "2000,10000").split(",")]   # env LOTES=2000: so' o lote pequeno (re-execucao rapida na verificacao)


def out(nome, txt):
    open(os.path.join(OUTDIR, "resumos", nome), "w").write(txt if txt.endswith("\n") else txt + "\n")
    print(txt)


def smoke():
    import collections
    linhas = []
    for rot, caminho, flags in (("DEPOIS (arquivo vivo)", SIM, {}), ("ANTES (snapshot)", SNAP, None)):
        m = A.carrega(caminho, "smoke_" + rot[:3], DECK)
        bl = list(getattr(m, "BASE_LIBRARY", []) or [])
        desc = [n for n in set(bl) if n not in m.CARD_DB]
        cnt = collections.Counter(bl)
        dup = sorted(n for n, k in cnt.items() if k > 1 and n not in ("Forest", "Island", "Swamp", "Mountain", "Plains", "Snow-Covered Forest", "Snow-Covered Plains", "Snow-Covered Island", "Snow-Covered Swamp", "Snow-Covered Mountain", "Wastes"))
        linhas.append(f"{rot}: cartas na biblioteca={len(bl)} | distintas={len(cnt)} | desconhecidas (fora do CARD_DB)={desc} | duplicadas nao-basicas={dup}")
        for modo in MODOS:
            exc = 0
            for sd in range(1_000_000, 1_000_200):
                try:
                    A.chama(m, modo, sd, TURNS, EXTRA)
                except Exception:
                    exc += 1
            linhas.append(f"   200 partidas modo {modo}: excecoes={exc}")
    m = A.carrega(SIM, "smoke_flags", DECK)
    linhas.append("chaves da correcao no arquivo vivo: " + ", ".join(f"{k}={getattr(m, k, 'AUSENTE')}" for k in OFF))
    out("smoke.txt", "\n".join(linhas))


def bitid():
    linhas = [f"Bit-identidade: arquivo vivo com as chaves {OFF} == snapshot {cfg['snapshot']}; N={NBIT} por modo, sementes 5_000_000+i; impressao digital do resultado INTEIRO (campos novos ignorados: {list(IGNORA)})"]
    seeds = range(5_000_000, 5_000_000 + NBIT)
    for modo in MODOS:
        a = A.serie_paralela(SNAP, "bi_antes_" + modo, DECK, {}, modo, seeds, TURNS, EXTRA, IGNORA)
        d = A.serie_paralela(SIM, "bi_depois_" + modo, DECK, OFF, modo, seeds, TURNS, EXTRA, IGNORA)
        dif = sum(1 for x, y in zip(a, d) if x[0] != y[0])
        linhas.append(f"{modo}: N={NBIT} partidas diferentes={dif} -> {'BIT-IDENTICO' if dif == 0 else 'DIVERGE'}")
    out("bitident_%d.txt" % NBIT, "\n".join(linhas))


def ghost():
    """Valida que o ENSAIO A SECO nao tem efeito colateral: chave da correcao ligada + modo GHOST (roda o ensaio e ignora o resultado) deve ser bit-identica a tudo desligado."""
    g = cfg.get("ghost")
    if not g:
        return
    linhas = [f"Ghost: arquivo vivo com {g} (o ensaio roda, o resultado e' ignorado) == arquivo vivo com as chaves {OFF}; N={NBIT} por modo, sementes 5_000_000+i; impressao digital do resultado INTEIRO (campos novos ignorados: {list(IGNORA)})"]
    seeds = range(5_000_000, 5_000_000 + NBIT)
    for modo in MODOS:
        a = A.serie_paralela(SIM, "gh_off_" + modo, DECK, OFF, modo, seeds, TURNS, EXTRA, IGNORA)
        b = A.serie_paralela(SIM, "gh_on_" + modo, DECK, dict(OFF, **g), modo, seeds, TURNS, EXTRA, IGNORA)
        dif = sum(1 for x, y in zip(a, b) if x[0] != y[0])
        linhas.append(f"{modo}: N={NBIT} partidas diferentes={dif} -> {'IDENTICO (o ensaio nao tem efeito colateral)' if dif == 0 else 'DIVERGE'}")
    out("ghost_%d.txt" % NBIT, "\n".join(linhas))


def ab():
    variantes = {"antes": (SNAP, {}), "depois": (SIM, cfg.get("flags_depois", {}))}   # flags_depois: isola uma correcao quando o arquivo vivo tem mais de uma
    for nome, fl in cfg.get("sensibilidade", {}).items():
        variantes[nome] = (SIM, fl)
    for N, seed0 in LOTES:
        for modo in MODOS:
            seeds = range(seed0, seed0 + N)
            res = {}
            for nome, (caminho, fl) in variantes.items():
                res[nome] = A.serie_paralela(caminho, f"ab_{nome}_{modo}_{N}", DECK, fl, modo, seeds, TURNS, EXTRA, IGNORA)
            sufixo = "" if modo == "padrao" else "_resiliencia"
            A.salvar_raw(os.path.join(OUTDIR, "dados", f"raw_ab_{N}{sufixo}"), res)
            partes = [f"LOTE N={N} sementes {seed0}..{seed0 + N - 1}, {TURNS} turnos, modo {modo}"]
            for nome in variantes:
                if nome == "antes":
                    continue
                partes.append(A.tabela_pareada(res["antes"], res[nome], DEST, rotulo=f"[{nome} - antes]"))
            out(f"ab_{N}{sufixo}.txt", "\n\n".join(partes))


def soma():
    """Refaz as tabelas do A/B SO' a partir dos brutos arquivados (.json.xz)."""
    for N, seed0 in LOTES:
        for modo in MODOS:
            sufixo = "" if modo == "padrao" else "_resiliencia"
            res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_ab_{N}{sufixo}"))
            partes = [f"LOTE N={N} sementes {seed0}..{seed0 + N - 1}, {TURNS} turnos, modo {modo}"]
            for nome in res:
                if nome == "antes":
                    continue
                partes.append(A.tabela_pareada(res["antes"], res[nome], DEST, rotulo=f"[{nome} - antes]"))
            out(f"ab_{N}{sufixo}.txt", "\n\n".join(partes))


def reg():
    linhas = [f"Regressao: N={NREG} por configuracao/modo, sementes 5_000_000+i; excecoes + invariantes genericas (carta acima do baralho em alguma zona; contadores negativos)"]
    for rot, fl in (("depois (repositorio)", {}), ("chave_desligada", OFF)):
        for modo in MODOS:
            r = A.regressao(SIM, f"reg_{rot[:4]}_{modo}", DECK, fl, modo, NREG, 5_000_000, TURNS, EXTRA)
            linhas.append(f"{rot:22s} {modo:12s} partidas ok={r['partidas_ok']} | excecoes={sum(r['excecoes'].values())} {r['excecoes'] or ''} | carta acima do baralho={r['carta_acima_do_baralho']} | campos negativos={r['campos_negativos']}")
    out("regressao_%d.txt" % NREG, "\n".join(linhas))


if ETAPA in ("smoke", "tudo"):
    smoke()
if ETAPA in ("bitid", "tudo"):
    bitid()
if ETAPA in ("ghost", "tudo"):
    ghost()
if ETAPA in ("ab", "tudo"):
    ab()
if ETAPA in ("reg", "tudo"):
    reg()
if ETAPA == "sum":
    soma()

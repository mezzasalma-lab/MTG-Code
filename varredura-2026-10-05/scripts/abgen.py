"""Harness GENERICO de validacao dos simuladores de goldfish (A/B pareado, bit-identidade, regressao), usado nas correcoes de 2026-10-05 (varredura das classes de erro
achadas nas rodadas do Vihaan/Megatron em todos os outros decks). Funciona com qualquer simulador do repositorio: `simulate_one(seed, turns)` pode devolver um GameState, um dict
(Beorn, Edgar, Thranduil, Prismatic Bridge) ou uma tupla (Toph: estado + log); o modo de resiliencia e' `simulate_one_with_interaction`.

Pareamento: a MESMA semente nas duas variantes; IC95% = 1,96 * dp(diferenca pareada) / raiz(N). As metricas sao TODOS os campos numericos do resultado (int/float/bool; listas, conjuntos
e dicts viram o tamanho), entao a tabela mostra tudo o que a correcao moveu, sem escolher o que olhar. Bit-identidade: impressao digital do resultado INTEIRO (campo a campo, conjuntos
ordenados), partida a partida. Uso como biblioteca (ver `driver_*.py`)."""
import collections, copy, dataclasses, hashlib, importlib.util, math, os, random, statistics as st, sys, traceback, json, lzma
from multiprocessing import Pool

IGNORA = {"rng", "interaction_rng", "log", "game_log"}


def _eh_cache(k):
    """Campo interno de memoizacao (`_mana_cache` do Tom): o conteudo depende da ordem de iteracao de set, nao do jogo. Fora da impressao digital."""
    return isinstance(k, str) and k.startswith("_") and "cache" in k


def carrega(caminho, nome, cwd):
    """Importa o simulador como modulo isolado. Os simuladores leem `lista.md` do diretorio de trabalho no import: faz chdir pro deck."""
    os.chdir(cwd)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def _norm(o, vistos=None, prof=0):
    if vistos is None:
        vistos = set()
    if o is None or isinstance(o, (bool, int, float, str, bytes)):
        return o
    if isinstance(o, random.Random):
        return "RNG:" + hashlib.sha1(repr(o.getstate()).encode()).hexdigest()[:10]
    i = id(o)
    if i in vistos or prof > 40:
        return "<ciclo>"
    vistos = vistos | {i}
    if isinstance(o, (set, frozenset)):
        return ("set", sorted((repr(_norm(x, vistos, prof + 1)) for x in o)))
    if isinstance(o, dict):
        return ("dict", sorted(((repr(_norm(k, vistos, prof + 1)), _norm(v, vistos, prof + 1)) for k, v in o.items() if k not in IGNORA and not _eh_cache(k)), key=lambda kv: kv[0]))
    if isinstance(o, (list, tuple, collections.deque)):
        return [_norm(x, vistos, prof + 1) for x in o]
    if hasattr(o, "__dict__"):
        return (type(o).__name__, sorted(((k, _norm(v, vistos, prof + 1)) for k, v in vars(o).items() if k not in IGNORA and not _eh_cache(k)), key=lambda kv: kv[0]))
    if dataclasses.is_dataclass(o):
        return (type(o).__name__, [(f.name, _norm(getattr(o, f.name), vistos, prof + 1)) for f in dataclasses.fields(o) if f.name not in IGNORA])
    return repr(o)


def impressao(o, ignora_campos=()):
    """sha1 do resultado inteiro. `ignora_campos`: campos NOVOS (que o snapshot antigo nao tem) a desconsiderar."""
    if isinstance(o, tuple) and o and hasattr(o[0], "__dict__"):
        o = o[0]   # Toph devolve (estado, log)
    if ignora_campos and hasattr(o, "__dict__"):
        d = {k: v for k, v in vars(o).items() if k not in ignora_campos}
        n = _norm(d)
    elif ignora_campos and isinstance(o, dict):
        n = _norm({k: v for k, v in o.items() if k not in ignora_campos})
    else:
        n = _norm(o)
    return hashlib.sha1(repr(n).encode()).hexdigest()


def numericos(o):
    """Todos os campos numericos do resultado (listas/conjuntos/dicts -> tamanho)."""
    if isinstance(o, tuple) and o and hasattr(o[0], "__dict__"):
        o = o[0]
    campos = vars(o) if hasattr(o, "__dict__") else (o if isinstance(o, dict) else {})
    out = {}
    for k, v in campos.items():
        if k in IGNORA:
            continue
        if k.endswith("_turn") and "this_turn" not in k and k != "turn" and (v is None or (isinstance(v, int) and not isinstance(v, bool))):
            # campo "turno em que X aconteceu" (None = nunca): vira indicadores, em vez de zerar o None
            out[k + "__nunca"] = 1.0 if v is None else 0.0
            for T in (3, 4, 5, 6):
                out[f"{k}__ate_T{T}"] = 1.0 if (v is not None and v <= T) else 0.0
            continue
        if isinstance(v, bool):
            out[k] = float(v)
        elif isinstance(v, (int, float)):
            out[k] = float(v)
        elif isinstance(v, (list, set, frozenset, dict, tuple)):
            out["len_" + k] = float(len(v))
    return out


def chama(m, modo, seed, turns, extra=None):
    fn = m.simulate_one if modo == "padrao" else m.simulate_one_with_interaction
    if extra:
        return fn(seed, turns, *extra)
    return fn(seed, turns)


def serie(m, modo, seeds, turns, extra=None, ignora=()):
    """Roda `seeds` e devolve [(impressao, numericos)] na ordem."""
    out = []
    for sd in seeds:
        r = chama(m, modo, sd, turns, extra)
        out.append((impressao(r, ignora), numericos(r)))
    return out


def ic(a, b):
    d = [y - x for x, y in zip(a, b)]
    if len(d) < 2 or len(set(d)) == 1:
        return (st.mean(d) if d else 0.0), 0.0
    return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d))


def tabela_pareada(base, var, destaque=(), limite=14, rotulo=""):
    """Diferenca pareada (var - base) de cada campo numerico: mostra os `destaque` e os campos mais movidos (|dif|/IC alto). Devolve o texto."""
    campos = sorted(set(base[0][1]) & set(var[0][1]))
    linhas = []
    for c in campos:
        a = [x[1].get(c, 0.0) for x in base]
        b = [x[1].get(c, 0.0) for x in var]
        m, h = ic(a, b)
        if m == 0.0 and h == 0.0:
            continue
        z = abs(m) / h if h > 0 else (999 if m != 0 else 0)
        linhas.append((c, st.mean(a), st.mean(b), m, h, z))
    iguais = sum(1 for x, y in zip(base, var) if x[0] == y[0])
    n = len(base)
    txt = [f"{rotulo} N={n} | partidas com resultado IDENTICO ao da base: {iguais} ({100 * iguais / n:.1f}%)"]
    pick = {l[0]: l for l in linhas}
    mostrados = [pick[c] for c in destaque if c in pick]
    resto = sorted((l for l in linhas if l[0] not in destaque), key=lambda l: -l[5])[:limite]
    txt.append("   %-38s %12s %12s %20s" % ("campo", "base", "variante", "dif. pareada (IC95%)"))
    for c, ma, mb, m, h, z in mostrados + resto:
        marca = "*" if z > 1 else " "
        txt.append("  %s%-38s %12.4f %12.4f %+12.4f ±%-8.4f" % (marca, c, ma, mb, m, h))
    return "\n".join(txt)


def _job_serie(args):
    caminho, nome, cwd, flags, modo, seeds, turns, extra, ignora = args
    m = carrega(caminho, nome, cwd)
    for k, v in flags.items():
        if hasattr(m, k):
            setattr(m, k, v)
        else:
            raise AttributeError(f"{k} nao existe em {caminho}")
    return serie(m, modo, seeds, turns, extra, ignora)


def serie_paralela(caminho, nome, cwd, flags, modo, seeds, turns, extra=None, ignora=(), proc=4):
    """Divide as sementes em blocos e roda em `proc` processos."""
    seeds = list(seeds)
    k = max(1, len(seeds) // (proc * 4))
    blocos = [seeds[i:i + k] for i in range(0, len(seeds), k)]
    args = [(caminho, f"{nome}_{i}", cwd, flags, modo, b, turns, extra, ignora) for i, b in enumerate(blocos)]
    with Pool(proc) as p:
        partes = p.map(_job_serie, args)
    return [x for parte in partes for x in parte]


def salvar_raw(caminho_sem_ext, variantes):
    """Formato colunas-v1: {variante: [(fp, {campo: valor})]} -> .json.xz"""
    out = {"formato": "colunas-v1", "variantes": {}}
    for nome, rs in variantes.items():
        campos = sorted({c for _, d in rs for c in d})
        out["variantes"][nome] = {"n": len(rs), "fp": [fp[:12] for fp, _ in rs], "campos": {c: [d.get(c, 0.0) for _, d in rs] for c in campos}}
    with lzma.open(caminho_sem_ext + ".json.xz", "wt", preset=9) as f:
        f.write(json.dumps(out, separators=(",", ":")))


def carregar_raw(caminho_sem_ext):
    with lzma.open(caminho_sem_ext + ".json.xz", "rt") as f:
        d = json.load(f)
    res = {}
    for nome, v in d["variantes"].items():
        ks = list(v["campos"])
        res[nome] = [(v["fp"][i], {k: v["campos"][k][i] for k in ks}) for i in range(v["n"])]
    return res


# ----------------------------------------------------------------------------------------------------------------------------- regressao
def _nome(x):
    x = getattr(x, "card", x)
    return getattr(x, "name", x) if not isinstance(x, str) else x


def _zonas(estado):
    zs = []
    for k in ("hand", "library", "battlefield", "graveyard", "exile", "exiled", "command_zone"):
        v = getattr(estado, k, None)
        if isinstance(v, (list, tuple)):
            zs += [_nome(x) for x in v]
    return collections.Counter(n for n in zs if isinstance(n, str))


def _job_regressao(args):
    caminho, nome, cwd, flags, modo, seeds, turns, extra = args
    m = carrega(caminho, nome, cwd)
    for k, v in flags.items():
        setattr(m, k, v)
    base = collections.Counter(getattr(m, "BASE_LIBRARY", []) or [])
    exc = collections.Counter(); ex = {}
    dup = neg = n = 0
    suspeitos = collections.Counter()
    for sd in seeds:
        try:
            r = chama(m, modo, sd, turns, extra)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]
            k = f"{type(e).__name__}: {str(e)[:60]} @ {os.path.basename(tb.filename)}:{tb.lineno} {tb.name}"
            exc[k] += 1; ex.setdefault(k, sd)
            continue
        n += 1
        est = r[0] if isinstance(r, tuple) else r
        if hasattr(est, "__dict__") and base:
            z = _zonas(est)
            if any(c > base[nm] for nm, c in z.items() if nm in base and base[nm] >= 1 and nm not in ("Forest", "Island", "Swamp", "Mountain", "Plains") and c > base[nm]):
                dup += 1
        if hasattr(est, "__dict__"):
            for k, v in vars(est).items():
                if isinstance(v, (int, float)) and not isinstance(v, bool) and v < 0 and any(t in k for t in ("count", "total", "tokens", "treasures", "lands", "mana", "mulligans")):
                    suspeitos[k] += 1
    return dict(exc), ex, dup, dict(suspeitos), n


def regressao(caminho, nome, cwd, flags, modo, n, seed0, turns, extra=None, proc=4):
    seeds = list(range(seed0, seed0 + n))
    k = max(1, len(seeds) // (proc * 3))
    blocos = [seeds[i:i + k] for i in range(0, len(seeds), k)]
    args = [(caminho, f"{nome}_{i}", cwd, flags, modo, b, turns, extra) for i, b in enumerate(blocos)]
    with Pool(proc) as p:
        partes = p.map(_job_regressao, args)
    exc = collections.Counter(); ex = {}; dup = 0; sus = collections.Counter(); tot = 0
    for e, x, d, s, c in partes:
        exc.update(e); ex.update({k: v for k, v in x.items() if k not in ex}); dup += d; sus.update(s); tot += c
    return {"partidas_ok": tot, "excecoes": dict(exc), "exemplos": ex, "carta_acima_do_baralho": dup, "campos_negativos": dict(sus)}

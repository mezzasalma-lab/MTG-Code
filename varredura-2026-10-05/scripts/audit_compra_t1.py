"""audit_compra_t1.py (2026-10-20) — o simulador compra a carta do turno 1? (Commander e' multijogador: ninguem pula a compra do T1; so' o 1o jogador no 1x1, CR 103.8a).
Metodo em RUNTIME, nao por grep: para as MESMAS sementes, roda `simulate_one(seed, 0)` (so' a abertura: mulligan, sem turno) e `simulate_one(seed, 1)` (abertura + 1 turno) e compara o
tamanho da biblioteca. Com a compra do T1 a biblioteca cai >= 1 em TODA partida (a compra; fetch/Rampant Growth/etc. so' aumentam a queda). Se pula, ha' partidas com queda 0.
Simuladores baseados em dict (Beorn, Edgar, Prismatic Bridge, Thranduil) so' retornam o estado no modo `simulate_one_with_interaction` (retorna tupla/dict): o script tenta os dois.
Veredito por deck: COMPRA (n > 0 e queda minima >= 1) | PULA (alguma partida com queda 0) | VACUO (n == 0: nada foi medido; nunca conta como "ok", Regra #10 item 4).
Uso: python3 audit_compra_t1.py [ROOT] [N_SEMENTES]     (ROOT padrao = raiz do repositorio; sementes 1_000_000..)"""
import sys, os, glob, collections
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(os.path.join(AQUI, "..", ".."))
N = int(sys.argv[2]) if len(sys.argv) > 2 else 80


def estado(r):
    if isinstance(r, tuple):
        r = r[0]
    if isinstance(r, dict):
        return r.get("library")
    return getattr(r, "library", None)


def mede(m, fn_nome, seeds):
    fn = getattr(m, fn_nome, None)
    if fn is None:
        return None
    dif = collections.Counter(); sem = 0
    for sd in seeds:
        try:
            l0 = estado(fn(sd, 0)); l1 = estado(fn(sd, 1))
        except Exception:
            sem += 1; continue
        if l0 is None or l1 is None:
            sem += 1; continue
        dif[len(l0) - len(l1)] += 1
    return dif, sem


linhas = [f"audit_compra_t1: ROOT={ROOT} N={N} sementes {1_000_000}..{1_000_000 + N - 1}; queda da biblioteca entre turns=0 e turns=1 (contagem de partidas por queda)"]
resumo = collections.Counter()
for f in sorted(glob.glob(os.path.join(ROOT, "*", "*_goldfish_v1.py"))):
    deck = os.path.dirname(f); nome = os.path.basename(deck)
    try:
        m = A.carrega(f, "t1_" + nome.replace("-", "_"), deck)
    except Exception as e:
        linhas.append(f"{nome:28s} ERRO import {type(e).__name__}: {str(e)[:60]}"); resumo["ERRO"] += 1; continue
    seeds = range(1_000_000, 1_000_000 + N)
    usado = None
    for fn_nome in ("simulate_one", "simulate_one_with_interaction"):
        r = mede(m, fn_nome, seeds)
        if r and sum(r[0].values()) > 0:
            usado = (fn_nome, r); break
    if usado is None:
        linhas.append(f"{nome:28s} VACUO (nenhuma partida medida)"); resumo["VACUO"] += 1; continue
    fn_nome, (dif, sem) = usado
    n = sum(dif.values())
    veredito = "COMPRA" if min(dif) >= 1 else "PULA"
    resumo[veredito] += 1
    chave = getattr(m, "FIRST_TURN_SKIPS_DRAW", "(sem chave)")
    linhas.append(f"{nome:28s} {veredito:7s} n={n:3d} sem_medida={sem} via {fn_nome:30s} queda={dict(sorted(dif.items()))} FIRST_TURN_SKIPS_DRAW={chave}")
linhas.append("resumo: " + ", ".join(f"{k}={v}" for k, v in sorted(resumo.items())))
print("\n".join(linhas))

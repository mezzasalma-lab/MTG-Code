"""Regressao do Vihaan (Sephiroth): 20.000 partidas por configuracao/modo -> 0 excecoes; invariantes: (1) cartas nomeadas nunca duplicam
(mao+campo+cemiterio+biblioteca+impulso <= BASE_LIBRARY), (2) Treasures >= 0 e 'animados vivos' == 0 no fim do turno, (3) Sephiroth:
has_super_nova_emblem == (emblemas > 0), emblemas >= 0, virou => emblemas >= 1, nenhum lote de mortes ativo no fim do turno,
contador 'este turno' >= 0. Uso: python3 fx_regressao.py [N]"""
import collections, os, sys, traceback
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED0 = 5_000_000


def job(args):
    config, modo = args
    V = F.carrega(F.DEPOIS, "vih_reg_%d_%s_%s" % (os.getpid(), config, modo))
    F.flags(V, emblema=config in ("todas", "so_emblema"), simultaneas=config in ("todas", "so_simultaneas"), fronteira=config in ("todas", "so_fronteira"))
    fn = V.simulate_one if modo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    excecoes, viol_cons, viol_alive, viol_neg, viol_seph, viol_lote, extra, flips = 0, 0, 0, 0, 0, 0, 0, 0
    falhas = []
    orig_et = V.end_step
    def espia_end(state):
        nonlocal viol_alive, viol_neg, viol_lote
        if state.seph_batch_active:
            viol_lote += 1
        orig_et(state)
        if state.treasures_animated_alive != 0:
            viol_alive += 1
        if state.treasures < 0:
            viol_neg += 1
    V.end_step = espia_end
    for i in range(N):
        try:
            s = fn(SEED0 + i)
        except Exception:
            excecoes += 1
            if len(falhas) < 3:
                falhas.append((SEED0 + i, traceback.format_exc(limit=3)))
            continue
        zonas = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + [c for c, _ in s.impulse_pool])
        if any(zonas[n] > k for n, k in base.items()):
            viol_cons += 1
        if (s.has_super_nova_emblem != (s.super_nova_emblems > 0)) or s.super_nova_emblems < 0 \
                or (s.sephiroth_transformed and s.super_nova_emblems < 1) or s.sephiroth_deaths_this_turn < 0 or s.seph_batch_active:
            viol_seph += 1
        extra += s.sephiroth_extra_triggers_total
        flips += 1 if s.has_super_nova_emblem else 0
    return config, modo, excecoes, viol_cons, viol_alive, viol_neg, viol_seph, viol_lote, extra, flips, falhas


if __name__ == "__main__":
    jobs = [("todas", "padrao"), ("todas", "resiliencia"), ("so_emblema", "resiliencia"), ("so_simultaneas", "resiliencia"),
            ("so_fronteira", "resiliencia"), ("nenhuma", "padrao"), ("nenhuma", "resiliencia")]
    with Pool(4) as p:
        for config, modo, exc, vc, va, vn, vs, vl, ex, fl, falhas in p.map(job, jobs):
            print("%-14s %-12s N=%d sementes %d..%d: excecoes=%d | cartas duplicadas=%d | animados vivos != 0 no fim do turno=%d | Treasures<0=%d | "
                  "invariante Sephiroth violado=%d | lote de mortes ativo no fim do turno=%d | jogos com emblema=%d | gatilhos extras do emblema=%d" % (
                config, modo, N, SEED0, SEED0 + N - 1, exc, vc, va, vn, vs, vl, fl, ex))
            for sd, tb in falhas:
                print("   semente", sd, tb)

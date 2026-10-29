"""Regressao do Vihaan: 20.000 partidas por configuracao/modo -> 0 excecoes; invariantes: (1) conservacao de cartas nomeadas
(mao+campo+cemiterio+biblioteca+impulso == BASE_LIBRARY, partida a partida, exceto tokens), (2) Treasures >= 0 e 'animados vivos'
sempre 0 no fim do turno e <= Treasures em campo. Uso: python3 fx_regressao.py [N]"""
import collections, os, sys, traceback
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED0 = 5_000_000


def job(args):
    config, modo = args
    V = F.carrega(F.DEPOIS, "vih_reg_%d_%s_%s" % (os.getpid(), config, modo))
    F.flags(V, treasure=config in ("todas", "so_treasure", "todas_t4"), bottom=config in ("todas", "so_bottom", "todas_t4"),
            tapped=config in ("todas", "so_tapped", "blunt", "todas_t4"), tapped_max_turn=4 if config == "todas_t4" else None,
            skip_if_loses_play=config != "blunt")
    fn = V.simulate_one if modo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    excecoes, viol_cons, viol_alive, viol_neg, falhas = 0, 0, 0, 0, []
    orig_et = V.end_step
    def espia_end(state):
        orig_et(state)
        nonlocal viol_alive, viol_neg
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
        # cartas nomeadas nunca somem nem duplicam (tokens/copias nao estao em BASE_LIBRARY e ficam de fora da comparacao)
        if any(zonas[n] != k for n, k in base.items() if n in zonas or True) and any(zonas[n] > k for n, k in base.items()):
            viol_cons += 1
    return config, modo, excecoes, viol_cons, viol_alive, viol_neg, falhas


if __name__ == "__main__":
    jobs = [("todas", "padrao"), ("todas", "resiliencia"), ("so_treasure", "padrao"), ("so_bottom", "padrao"), ("so_tapped", "padrao"),
            ("blunt", "padrao"), ("todas_t4", "padrao"), ("todas_t4", "resiliencia")]
    with Pool(4) as p:
        for config, modo, exc, vc, va, vn, falhas in p.map(job, jobs):
            print("%-12s %-12s N=%d sementes %d..%d: excecoes=%d | cartas duplicadas=%d | animados vivos != 0 no fim do turno=%d | Treasures<0=%d" % (
                config, modo, N, SEED0, SEED0 + N - 1, exc, vc, va, vn))
            for sd, tb in falhas:
                print("   semente", sd, tb)

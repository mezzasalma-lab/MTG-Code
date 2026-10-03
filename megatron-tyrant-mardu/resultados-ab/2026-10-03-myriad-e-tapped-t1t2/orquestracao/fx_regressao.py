"""Regressao: 20.000 partidas por modo (padrao e resiliencia) com as DUAS correcoes ligadas (config final do repositorio) -> 0 excecoes;
mais invariantes de conservacao de cartas (basicos + Myriad nunca somem nem duplicam entre as zonas), e as demais variantes no modo padrao.
Uso: python3 fx_regressao.py [N]"""
import collections, os, sys, traceback
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED0 = 5_000_000


def job(args):
    config, modo = args
    m = F.carrega(F.DEPOIS, "mega_reg_%d_%s_%s" % (os.getpid(), config, modo))
    F.flags(m, tapped=config != "so_myriad", myriad=config != "so_tapped", tapped_max_turn=4 if config == "ambas_t4" else None,
            skip_if_loses_play=config != "blunt")
    fn = m.simulate_one if modo == "padrao" else m.simulate_one_with_interaction
    excecoes, viol_conserv, ativ, falhas = 0, 0, 0, []
    CONS = {"Plains": 6, "Swamp": 6, "Mountain": 6, "Myriad Landscape": 1}
    for i in range(N):
        try:
            s = fn(SEED0 + i)
        except Exception:
            excecoes += 1
            if len(falhas) < 3:
                falhas.append((SEED0 + i, traceback.format_exc(limit=3)))
            continue
        zonas = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + s.exile)
        for nome, k in CONS.items():
            if zonas[nome] != k:
                viol_conserv += 1
                break
        ativ += s.myriad_activations_total
    return config, modo, excecoes, viol_conserv, ativ, falhas


if __name__ == "__main__":
    jobs = [("ambas", "padrao"), ("ambas", "resiliencia"), ("so_tapped", "padrao"), ("so_myriad", "padrao"), ("blunt", "padrao"),
            ("ambas_t4", "padrao"), ("ambas_t4", "resiliencia")]
    with Pool(4) as p:
        for config, modo, exc, viol, ativ, falhas in p.map(job, jobs):
            print("%-10s %-12s N=%d sementes %d..%d: excecoes=%d | violacoes de conservacao (Plains/Swamp/Mountain/Myriad) = %d | ativacoes do Myriad=%d" % (
                config, modo, N, SEED0, SEED0 + N - 1, exc, viol, ativ))
            for sd, tb in falhas:
                print("   semente", sd, tb)

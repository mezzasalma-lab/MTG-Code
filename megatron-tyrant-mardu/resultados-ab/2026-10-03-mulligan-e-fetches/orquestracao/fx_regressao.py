"""Regressao do Megatron (2a rodada): 20.000 partidas por configuracao/modo -> 0 excecoes; invariantes: conservacao de todos os terrenos
nomeados entre as zonas, total_mana nunca negativo, fetch nunca sobra em campo ao fim do turno quando havia alvo. Uso: python3 fx_regressao.py [N]"""
import collections, os, sys, traceback
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED0 = 5_000_000
CONS = {"Plains": 6, "Swamp": 6, "Mountain": 6, "Myriad Landscape": 1, "Evolving Wilds": 1, "Terramorphic Expanse": 1, "Rocky Tar Pit": 1,
        "Badlands": 1, "Scrubland": 1, "Plateau": 1, "Smoldering Marsh": 1, "Sunlit Marsh": 1, "Command Tower": 1}


def job(args):
    config, modo = args
    M = F.carrega(F.DEPOIS, "meg_reg2_%d_%s_%s" % (os.getpid(), config, modo))
    F.flags(M, mulligan={"ambas": "smart", "so_mull": "smart", "so_fetch": "legacy", "mull_posicao": "bottom_only", "antigo": "legacy"}[config],
            fetch=config in ("ambas", "so_fetch"))
    fn = M.simulate_one if modo == "padrao" else M.simulate_one_with_interaction
    exc, viol_c, viol_f, viol_m, falhas = 0, 0, 0, 0, []
    orig_et = M.end_step
    def et(state):
        nonlocal viol_f, viol_m
        if M.FETCHLANDS_ENABLED:
            for f in ("Evolving Wilds", "Terramorphic Expanse"):
                if f in state.battlefield and any(b in state.library for b in M.BASIC_LANDS):
                    viol_f += 1
            if "Rocky Tar Pit" in state.battlefield and state.land_played_this_turn_name != "Rocky Tar Pit" \
                    and any(n in state.library for n in M.ROCKY_TAR_PIT_ORDER):
                viol_f += 1
        if M.total_mana(state) < 0:
            viol_m += 1
        orig_et(state)
    M.end_step = et
    for i in range(N):
        try:
            s = fn(SEED0 + i)
        except Exception:
            exc += 1
            if len(falhas) < 3:
                falhas.append((SEED0 + i, traceback.format_exc(limit=3)))
            continue
        z = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + s.exile)
        if any(z[n] != k for n, k in CONS.items()):
            viol_c += 1
    return config, modo, exc, viol_c, viol_f, viol_m, falhas


if __name__ == "__main__":
    jobs = [("ambas", "padrao"), ("ambas", "resiliencia"), ("so_mull", "padrao"), ("so_fetch", "padrao"), ("mull_posicao", "padrao"),
            ("antigo", "padrao"), ("antigo", "resiliencia")]
    with Pool(4) as p:
        for config, modo, exc, vc, vf, vm, falhas in p.map(job, jobs):
            print("%-13s %-12s N=%d sementes %d..%d: excecoes=%d | violacoes de conservacao (13 terrenos nomeados)=%d | fetch sobrando em campo=%d | total_mana<0=%d" % (
                config, modo, N, SEED0, SEED0 + N - 1, exc, vc, vf, vm))
            for sd, tb in falhas:
                print("   semente", sd, tb)

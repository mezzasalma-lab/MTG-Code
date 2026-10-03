"""Regressao do Vihaan ('fora da mao'): 20.000 partidas por configuracao/modo -> 0 excecoes; invariantes: (1) nenhuma carta nomeada duplicada
(mao+campo+cemiterio+biblioteca+pool+terrenos exilados <= BASE_LIBRARY), (2) Treasures >= 0 e 'animados vivos' == 0 no fim do turno,
(3) no maximo 1 jogada de terreno por turno (terreno do exilio e da mao nunca os dois), (4) nenhuma instantanea/feitico parado no campo no fim
(esperado 0 so' com 'todas'), (5) invariante do emblema do Sephiroth. Uso: python3 fx_regressao.py [N]"""
import collections, os, sys, traceback
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED0 = 5_000_000


def job(args):
    config, modo = args
    V = F.carrega(F.DEPOIS, "vih_reg_%d_%s_%s" % (os.getpid(), config, modo))
    t = config == "todas"
    F.flags(V, land=t or config == "so_land", cast=t or config == "so_cast", count=t or config == "so_count", storm=t or config == "so_storm",
            sevinne=t or config == "so_sevinne")
    fn = V.simulate_one if modo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    excecoes = viol_cons = viol_alive = viol_neg = viol_terreno = viol_magia = viol_seph = 0
    pact_lands = lotho = pump = sev_np = 0
    falhas = []
    orig_et = V.end_step
    def espia_end(state):
        nonlocal viol_alive, viol_neg, viol_terreno
        if state.lands_played_this_turn > 1:
            viol_terreno += 1
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
        zonas = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + [c for c, _ in s.impulse_pool] + [c for c, _ in s.impulse_lands])
        if any(zonas[n] > k for n, k in base.items()):
            viol_cons += 1
        if any(V.CARD_DB[c].ctype in ("instant", "sorcery") for c in s.battlefield):
            viol_magia += 1
        if s.has_super_nova_emblem != (s.super_nova_emblems > 0):
            viol_seph += 1
        pact_lands += s.impulse_lands_played_total
        lotho += s.lotho_triggers_total
        pump += s.storm_pump_total
        sev_np += s.sevinne_nonpermanent_returns_total
    return config, modo, excecoes, viol_cons, viol_alive, viol_neg, viol_terreno, viol_magia, viol_seph, pact_lands, lotho, pump, sev_np, falhas


if __name__ == "__main__":
    jobs = [("todas", "padrao"), ("todas", "resiliencia"), ("nenhuma", "padrao"), ("nenhuma", "resiliencia"),
            ("so_land", "padrao"), ("so_cast", "padrao"), ("so_count", "padrao"), ("so_storm", "padrao"), ("so_sevinne", "padrao")]
    with Pool(4) as p:
        for r in p.map(job, jobs):
            config, modo, exc, vc, va, vn, vt, vm, vs, pl, lo, pu, sn, falhas = r
            print("%-11s %-12s N=%d sementes %d..%d: excecoes=%d | cartas duplicadas=%d | animados vivos != 0 no fim do turno=%d | Treasures<0=%d | "
                  ">1 jogada de terreno no turno=%d | jogos com instantanea/feitico parado no campo=%d | emblema Sephiroth inconsistente=%d | "
                  "terrenos do exilio jogados=%d | gatilhos do Lotho=%d | bonus Storm somado=%d | Sevinne's devolveu nao-permanente=%d" % (
                config, modo, N, SEED0, SEED0 + N - 1, exc, vc, va, vn, vt, vm, vs, pl, lo, pu, sn))
            for sd, tb in falhas:
                print("   semente", sd, tb)

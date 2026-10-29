"""Regressao do Vihaan (7a rodada): 20.000 partidas por configuracao/modo -> 0 excecoes; invariantes: (1) nenhuma carta nomeada duplicada
(mao+campo+cemiterio+biblioteca+pool+terrenos exilados <= BASE_LIBRARY), (2) Treasures >= 0 e 'animados vivos' == 0 no fim do turno, (3) no maximo 1
jogada de terreno por turno, (4) nenhuma instantanea/feitico parado no campo no fim, (5) o farm nunca sacrifica mais do que os animados, so' com o Dictate nunca mais do que METADE do estoque, nem roda sem
Mahadi/Pitiless Plunderer (ou Dictate, quando a chave dele esta ligada) em campo, (6) invariante do emblema do Sephiroth. Uso: python3 fx_regressao.py [N]"""
import collections, os, sys, traceback
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED0 = 5_000_000


F_DICTATE = False
HALF_ON = True


def job(args):
    global F_DICTATE, HALF_ON
    config, modo = args
    V = F.carrega(F.DEPOIS, "vih_reg_%d_%s_%s" % (os.getpid(), config, modo))
    F.flags(V, half=(config != "tudo"), dictate=(config != "sem"))
    F_DICTATE = config != "sem"
    HALF_ON = config != "tudo"
    fn = V.simulate_one if modo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    excecoes = viol_cons = viol_alive = viol_neg = viol_terreno = viol_magia = viol_farm = viol_seph = 0
    farm = first = dictate = 0
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
    orig_farm = V.farm_animated_treasures
    def espia_farm(state):
        nonlocal viol_farm
        antes, animados, estoque = state.treasure_farm_total, state.treasures_animated_alive, state.treasures
        tinha_motor = ("Mahadi, Emporium Master" in state.battlefield or "Pitiless Plunderer" in state.battlefield
                       or (F_DICTATE and "Dictate of Erebos" in state.battlefield))
        orig_farm(state)
        feito = state.treasure_farm_total - antes
        com_reposicao = "Mahadi, Emporium Master" in state.battlefield or "Pitiless Plunderer" in state.battlefield
        if feito > animados or (feito > 0 and not tinha_motor) or (HALF_ON and not com_reposicao and feito > estoque // 2):
            viol_farm += 1
    V.farm_animated_treasures = espia_farm
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
        farm += s.treasure_farm_total
        first += s.impulse_all_first_total
        dictate += s.dictate_triggers_total
    return config, modo, excecoes, viol_cons, viol_alive, viol_neg, viol_terreno, viol_magia, viol_farm, viol_seph, farm, first, dictate, falhas


if __name__ == "__main__":
    jobs = [("metade", "padrao"), ("metade", "resiliencia"), ("tudo", "padrao"), ("tudo", "resiliencia"), ("sem", "padrao"), ("sem", "resiliencia")]
    with Pool(4) as p:
        for r in p.map(job, jobs):
            config, modo, exc, vc, va, vn, vt, vm, vf, vs, fa, fi, di, falhas = r
            print("%-9s %-12s N=%d sementes %d..%d: excecoes=%d | cartas duplicadas=%d | animados vivos != 0 no fim do turno=%d | Treasures<0=%d | "
                  ">1 jogada de terreno no turno=%d | jogos com instantanea/feitico parado no campo=%d | farm invalido=%d | emblema Sephiroth inconsistente=%d | "
                  "Treasures-criatura sacrificados pelo farm=%d | cartas do exilio jogadas antes das da mao (so' pela chave 'sempre')=%d | gatilhos do Dictate (proxy)=%d" % (
                config, modo, N, SEED0, SEED0 + N - 1, exc, vc, va, vn, vt, vm, vf, vs, fa, fi, di))
            for sd, tb in falhas:
                print("   semente", sd, tb)

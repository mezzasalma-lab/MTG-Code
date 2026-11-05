"""Regressao do Vihaan (10a rodada): 20.000 partidas por configuracao/modo -> 0 excecoes; invariantes: (1) nenhuma carta nomeada duplicada
(mao+campo+cemiterio+biblioteca+pool+terrenos exilados <= BASE_LIBRARY), (2) Treasures >= 0 e 'animados vivos' == 0 no fim do turno, (3) no maximo 1
jogada de terreno por turno, (4) nenhuma instantanea/feitico parado no campo no fim, (5) o farm nunca sacrifica mais do que os animados desvirados, so' com o
Dictate nunca mais do que METADE dos animados, nem roda sem Mahadi/Pitiless Plunderer/Dictate em campo, (6) invariante do emblema do Sephiroth,
(7) Treasures virados sempre entre 0 e o estoque, (8) retencao: `sempre` nunca conjura wipe proprio; `liberar` so' na circunstancia mitigada (Mayhem Devil +
animados pagam o custo inteiro + dano do pagamento > criaturas minhas); `antes` (9a rodada) nunca com Vihaan/Mahadi em campo, (9) depois de um wipe proprio nao sobra
criatura nenhuma, (10) o comandante so' e' conjurado com mana pro imposto, (11) o pagamento do wipe com animados nunca passa dos animados vivos e, quando a
chave esta ligada e ha' animado, e' o que paga primeiro. Configuracoes: `liberar` (o que fica no repositorio), `sempre` (sem a excecao), `sem_hold` (nenhuma retencao,
sem pagar com animados) e `antes` (as 3 chaves da 10a desligadas = 47ec126). Uso: python3 fx_regressao.py [N]"""
import collections, os, sys, traceback
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED0 = 5_000_000
CONF = {"liberar": dict(hold_always=True, pay=True, release=True, engine=True),
        "sempre": dict(hold_always=True, pay=True, release=False, engine=True),
        "sem_hold": dict(hold_always=False, pay=False, release=False, engine=False),
        "antes": dict(hold_always=False, pay=False, release=False, engine=True)}
MAHADI = "Mahadi, Emporium Master"


def job(args):
    config, modo = args
    V = F.carrega(F.DEPOIS, "vih_reg_%d_%s_%s" % (os.getpid(), config, modo))
    F.flags(V, **CONF[config])
    cf = CONF[config]
    fn = V.simulate_one if modo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    excecoes = viol_cons = viol_alive = viol_neg = viol_terreno = viol_magia = viol_farm = viol_seph = 0
    viol_tap = viol_hold = viol_wipe = viol_tax = viol_pay = 0
    mit = pagos_tot = 0
    farm = first = dictate = wipes = cmd_dest = 0
    falhas = []
    orig_et = V.end_step
    def espia_end(state):
        nonlocal viol_alive, viol_neg, viol_terreno, viol_tap
        if state.lands_played_this_turn > 1:
            viol_terreno += 1
        if not (0 <= state.treasures_tapped <= state.treasures):
            viol_tap += 1
        orig_et(state)
        if state.treasures_animated_alive != 0:
            viol_alive += 1
        if state.treasures < 0:
            viol_neg += 1
    V.end_step = espia_end
    orig_farm = V.farm_animated_treasures
    def espia_farm(state):
        nonlocal viol_farm
        antes, animados, estoque, virados = state.treasure_farm_total, state.treasures_animated_alive, state.treasures, state.treasures_tapped
        tinha_motor = ("Mahadi, Emporium Master" in state.battlefield or "Pitiless Plunderer" in state.battlefield or "Dictate of Erebos" in state.battlefield)
        orig_farm(state)
        feito = state.treasure_farm_total - antes
        com_reposicao = "Mahadi, Emporium Master" in state.battlefield or "Pitiless Plunderer" in state.battlefield
        if (feito > animados or feito > estoque - virados or (feito > 0 and not tinha_motor)
                or (not com_reposicao and feito > animados // 2)):
            viol_farm += 1
    V.farm_animated_treasures = espia_farm
    orig_res = V.resolve_instant_sorcery
    def espia_res(state, name):
        nonlocal viol_wipe, wipes, cmd_dest
        if name in V.OWN_WIPES:
            wipes += 1
            tinha = state.commander_in_play
            orig_res(state, name)
            if tinha and not state.commander_in_play:
                cmd_dest += 1
            if any(V.is_creature_card(n) for n in state.battlefield) or state.treasures_animated_alive or state.constructs or state.other_tokens or state.dragons or state.commander_in_play:
                viol_wipe += 1
            return
        return orig_res(state, name)
    V.resolve_instant_sorcery = espia_res
    orig_cast = V.cast_card
    def espia_cast(state, name, from_zone="hand"):
        nonlocal viol_tax, viol_hold, viol_pay, mit, pagos_tot
        if name == V.COMMANDER and V.remaining_mana(state) < V.CARD_DB[name].mv + 2 * state.commander_cast_count:
            viol_tax += 1
        if name in V.OWN_WIPES:
            m = V.wipe_mitigated(state, name)
            if cf["hold_always"]:
                if not (cf["release"] and m):
                    viol_hold += 1
            elif cf["engine"] and (state.commander_in_play or MAHADI in state.battlefield):
                viol_hold += 1
            if m:
                mit += 1
            disp = min(state.treasures_animated_alive, state.treasures - state.treasures_tapped)
            antes_pag = state.own_wipe_animated_paid_total
            r = orig_cast(state, name, from_zone)
            pagos = state.own_wipe_animated_paid_total - antes_pag
            pagos_tot += pagos
            if pagos > disp or (cf["pay"] and disp > 0 and pagos == 0) or (not cf["pay"] and pagos != 0):
                viol_pay += 1
            return r
        return orig_cast(state, name, from_zone)
    V.cast_card = espia_cast
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
        if not (0 <= s.treasures_tapped <= s.treasures):
            viol_tap += 1
        farm += s.treasure_farm_total
        first += s.impulse_all_first_total
        dictate += s.dictate_triggers_total
    return (config, modo, excecoes, viol_cons, viol_alive, viol_neg, viol_terreno, viol_magia, viol_farm, viol_seph, viol_tap, viol_hold, viol_wipe, viol_tax, viol_pay,
            farm, dictate, wipes, cmd_dest, mit, pagos_tot, falhas)


if __name__ == "__main__":
    jobs = [(c, m) for c in ("liberar", "sempre", "sem_hold", "antes") for m in ("padrao", "resiliencia")]
    with Pool(4) as p:
        for r in p.map(job, jobs):
            config, modo, exc, vc, va, vn, vt, vm, vf, vs, vtap, vh, vw, vx, vp, fa, di, wp, cd, mi, pg, falhas = r
            print("%-9s %-12s N=%d sementes %d..%d: excecoes=%d | cartas duplicadas=%d | animados vivos != 0 no fim do turno=%d | Treasures<0=%d | "
                  ">1 jogada de terreno no turno=%d | jogos com instantanea/feitico parado no campo=%d | farm invalido=%d | emblema Sephiroth inconsistente=%d | "
                  "Treasures virados fora de [0, estoque]=%d | wipe proprio conjurado contra a retencao da config=%d | sobrou criatura depois do wipe=%d | "
                  "comandante conjurado sem mana pro imposto=%d | pagamento do wipe com animados invalido=%d | Treasures-criatura sacrificados pelo farm=%d | "
                  "gatilhos do Dictate (proxy)=%d | wipes proprios conjurados=%d | Vihaan destruido por wipe proprio=%d | wipes na circunstancia mitigada=%d | "
                  "animados sacrificados pra pagar wipe=%d" % (
                config, modo, N, SEED0, SEED0 + N - 1, exc, vc, va, vn, vt, vm, vf, vs, vtap, vh, vw, vx, vp, fa, di, wp, cd, mi, pg))
            for sd, tb in falhas:
                print("   semente", sd, tb)

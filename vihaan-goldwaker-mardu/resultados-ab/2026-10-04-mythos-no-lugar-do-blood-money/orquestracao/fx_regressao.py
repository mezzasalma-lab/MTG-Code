"""Regressao do Vihaan (12a rodada): 20.000 partidas por configuracao/modo -> 0 excecoes; invariantes: (1) nenhuma carta nomeada duplicada (mao+campo+cemiterio+biblioteca+pool+terrenos
exilados <= BASE_LIBRARY), (2) Treasures >= 0 e 'animados vivos' == 0 no fim do turno, (3) no maximo 1 jogada de terreno por turno, (4) nenhuma instantanea/feitico parado no campo no fim,
(5) o farm nunca sacrifica mais do que os animados desvirados, so' com o Dictate nunca mais do que METADE dos animados, nem roda sem Mahadi/Pitiless Plunderer/Dictate em campo,
(6) invariante do emblema do Sephiroth, (7) Treasures virados entre 0 e o estoque, (8) todo wipe proprio conjurado esta na circunstancia mitigada (retencao universal da 10a rodada;
so' nas configuracoes COM retencao), (9) depois de Blood Money/Blasphemous Act nao sobra criatura, (10) o comandante so' e' conjurado com mana pro imposto, (11) o pagamento do wipe com
animados nunca passa dos animados vivos, (12) a saida de ficha por DESTRUICAO nunca causa dreno quando so' o Mirkwood Bats esta em campo (11a rodada),
NOVOS DA 12a RODADA (Mythos of Snapdax), checados em cada conjuracao/resolucao: (13) a Mythos so' e' conjurada com `{W}{W}` entre as fontes (config com a cor ligada), (14) o contador de
`{B}{R}` possivel sobe se e so' se Mythos resolveu e as fontes cobriam W,W,B,R distintos, (15) os SOBREVIVENTES da selecao (= permanentes nao-terreno antes - sacrificadas, medidos ao redor de
`_mass_sacrifice`, sem o ruido dos gatilhos de morte que criam Treasure/Clue/Food depois) formam uma ESCOLHA LEGAL (`fx_common.escolha_legal`: da' pra atribuir cada sobrevivente a um slot
distinto artefato/criatura/encantamento do tipo dele; nao ha' planeswalker na lista; um artefato-criatura escolhido como "o artefato" fica em campo ao lado de "a criatura"), (16) o contador `mythos_perm_lost_total` e o retorno de `_mass_sacrifice` batem com antes - sobreviventes, (17) o Vihaan, se estava em
campo, sobrevive (e, sem ele, o Mahadi / Mayhem Devil, nessa ordem), (18) com a chave ligada a biblioteca nao tem Blood Money e tem 1 Mythos; desligada, o contrario,
(19) com a retencao ligada e o cascade corrigido, NENHUM wipe proprio e' resolvido dentro de um cascade (o acerto segurado vai pro fundo).
(Historico: a 1a versao de (15)/(16) olhava o ESTADO FINAL e dava 166/57 falsos positivos em 2.273 resolucoes, porque Pitiless Plunderer/Mahadi/Academy Manufactor criam Treasure/Clue/Food
nos gatilhos de morte da propria resolucao; a 2a ("no maximo 1 criatura, 1 artefato, 1 encantamento") ainda dava 8+2 falsos positivos em ~280 resolucoes, todos com a Academy Manufactor
(artefato-criatura) como "o artefato" ao lado do Vihaan como "a criatura": legal pelas regras. Diagnosticos em resumos/diagnostico_resto.txt.)
Configuracoes: `mythos` (o que fica no repositorio), `antes` (chave da 12a rodada desligada = a17049f) e `mythos_sem_hold` (chave ligada, SEM a retencao dos wipes proprios: e' ela que faz
a Mythos ser conjurada de verdade, pra os invariantes 13-17 terem material). Uso: python3 fx_regressao.py [N]"""
import collections, os, sys, traceback
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED0 = 5_000_000
CONF = {"mythos": dict(mythos=True), "antes": dict(mythos=False), "mythos_sem_hold": dict(mythos=True, hold=False)}   # `antes`: mythos=False tambem desliga a correcao do cascade (= a17049f)
CF = {"mythos": dict(hold_always=True, pay=True, release=True, engine=True), "antes": dict(hold_always=True, pay=True, release=True, engine=True),
      "mythos_sem_hold": dict(hold_always=False, pay=True, release=True, engine=False)}
MAHADI = "Mahadi, Emporium Master"
MYTHOS, ENGINES = "Mythos of Snapdax", ("Vihaan, Goldwaker", "Mahadi, Emporium Master", "Mayhem Devil")


def job(args):
    config, modo = args
    cf = CF[config]
    V = F.carrega(F.DEPOIS, "vih_reg_%d_%s_%s" % (os.getpid(), config, modo))
    F.flags(V, **CONF[config])
    fn = V.simulate_one if modo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    viol_lista = 0 if (base["Blood Money"] == (0 if config != "antes" else 1) and base[MYTHOS] == (1 if config != "antes" else 0)) else 1
    excecoes = viol_cons = viol_alive = viol_neg = viol_terreno = viol_magia = viol_farm = viol_seph = 0
    viol_tap = viol_hold = viol_wipe = viol_tax = viol_pay = viol_bats = exerc_bats = 0
    viol_cor = viol_br = viol_resto = viol_conta = viol_motor = viol_casc = 0
    casc = {"dentro": False, "wipes": 0, "recusados": 0}
    ultimo = [0]
    mit = pagos_tot = myt = myt_br = myt_perm = myt_cre = 0
    farm = first = dictate = wipes = cmd_dest = 0
    falhas = []

    def nomeadas(state):    # permanentes nomeadas nao-terreno (a magia em voo do cascade fica no campo temporariamente: nao e' permanente)
        return [n for n in state.battlefield if n not in V.LAND_NAMES and V.CARD_DB[n].ctype not in ("instant", "sorcery")]

    orig_ms = V._mass_sacrifice
    def espia_ms(state, sel):
        nonlocal viol_resto, viol_conta, viol_motor, myt_cre
        pre_nom = nomeadas(state)
        pre_tok = {"con": state.constructs, "oth": state.other_tokens, "dra": state.dragons, "anim": min(state.treasures_animated_alive, state.treasures),
                   "inan": state.treasures - min(state.treasures_animated_alive, state.treasures), "clues": state.clues, "foods": state.foods}
        pre_n = len(pre_nom) + sum(pre_tok.values())
        pre_cre = sum(1 for n in pre_nom if V.is_creature_card(n)) + pre_tok["con"] + pre_tok["oth"] + pre_tok["dra"] + pre_tok["anim"]
        motor = next((e for e in ENGINES if e in pre_nom), None)
        r = orig_ms(state, sel)
        ultimo[0] = r
        sac = collections.Counter(sel["cre"] + sel["outros"])
        vivos = list((collections.Counter(pre_nom) - sac).elements())
        tok = {k: pre_tok[k] - sel[k] for k in pre_tok}
        cre = sum(1 for n in vivos if V.is_creature_card(n)) + tok["con"] + tok["oth"] + tok["dra"] + tok["anim"]
        myt_cre += pre_cre - cre
        resto = len(vivos) + sum(tok.values())
        if (sum(sac.values()) != len(sel["cre"]) + len(sel["outros"]) or any(sac[n] > 1 and n not in V.LAND_NAMES for n in sac)
                or not F.escolha_legal(V, vivos, tok)):
            viol_resto += 1
        if r != pre_n - resto:
            viol_conta += 1
        if motor is not None and motor not in vivos:
            viol_motor += 1
        return r
    V._mass_sacrifice = espia_ms
    orig_dc = V.do_cascade
    def espia_dc(state, cutoff):
        casc["dentro"] = True
        try:
            return orig_dc(state, cutoff)
        finally:
            casc["dentro"] = False
    V.do_cascade = espia_dc
    orig_cd = V.cascade_declines
    def espia_cd(state, name):
        r = orig_cd(state, name)
        casc["recusados"] += int(r)
        return r
    V.cascade_declines = espia_cd
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
        nonlocal viol_wipe, wipes, cmd_dest, viol_resto, viol_conta, viol_motor, myt, myt_perm, myt_cre, viol_casc
        if name in V.OWN_WIPES and casc["dentro"]:
            casc["wipes"] += 1
            if V.CASCADE_DECLINE_HELD_WIPES_ENABLED and cf["hold_always"]:
                viol_casc += 1
        if name == MYTHOS:
            wipes += 1
            tinha = state.commander_in_play
            antes_perm = state.mythos_perm_lost_total
            ultimo[0] = -1
            orig_res(state, name)
            if state.mythos_perm_lost_total - antes_perm != ultimo[0]:
                viol_conta += 1   # o contador tem que somar exatamente o retorno de `_mass_sacrifice`
            if tinha and not state.commander_in_play:
                cmd_dest += 1
            myt += 1
            myt_perm += ultimo[0]
            return
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
        nonlocal viol_tax, viol_hold, viol_pay, mit, pagos_tot, viol_cor, viol_br, myt_br
        if name == V.COMMANDER and V.remaining_mana(state) < V.CARD_DB[name].mv + 2 * state.commander_cast_count:
            viol_tax += 1
        if name == MYTHOS:
            if V.MYTHOS_COLOR_CHECK_ENABLED and not V.pips_ok(V.color_sources(state), ["W", "W"]):
                viol_cor += 1
            esperado = V.pips_ok(V.color_sources(state), ["W", "W", "B", "R"])
            c0, b0 = state.mythos_cast_total, state.mythos_br_spent_total
            r = orig_cast(state, name, from_zone)
            if state.mythos_cast_total - c0 == 1:
                myt_br += state.mythos_br_spent_total - b0
                if (state.mythos_br_spent_total - b0) != int(esperado):
                    viol_br += 1
            elif state.mythos_br_spent_total != b0:
                viol_br += 1
            return r
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
    orig_tl = V.on_token_leaves
    def espia_tl(state, n, *a, **kw):
        nonlocal viol_bats, exerc_bats
        if kw.get("sacrificed", True) is False and "Mirkwood Bats" in state.battlefield and "Nadier's Nightblade" not in state.battlefield and n > 0:
            antes = state.drain_damage_total
            orig_tl(state, n, *a, **kw)
            exerc_bats += 1
            if state.drain_damage_total != antes:
                viol_bats += 1
            return
        return orig_tl(state, n, *a, **kw)
    V.on_token_leaves = espia_tl
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
    return (config, modo, excecoes, viol_cons, viol_alive, viol_neg, viol_terreno, viol_magia, viol_farm, viol_seph, viol_tap, viol_hold, viol_wipe, viol_tax, viol_pay, viol_bats, exerc_bats,
            viol_cor, viol_br, viol_resto, viol_conta, viol_motor, viol_lista, viol_casc, myt, myt_br, myt_perm, myt_cre, casc["wipes"], casc["recusados"],
            farm, dictate, wipes, cmd_dest, mit, pagos_tot, falhas)


if __name__ == "__main__":
    jobs = [(c, m) for c in ("mythos", "antes", "mythos_sem_hold") for m in ("padrao", "resiliencia")]
    with Pool(4) as p:
        for r in p.map(job, jobs):
            (config, modo, exc, vc, va, vn, vt, vm, vf, vs, vtap, vh, vw, vx, vp, vb, eb, vcor, vbr, vres, vcon, vmot, vlis, vcasc, my, mybr, myperm, mycre, cw, cr,
             fa, di, wp, cd, mi, pg, falhas) = r
            print("%-16s %-12s N=%d sementes %d..%d: excecoes=%d | cartas duplicadas=%d | animados vivos != 0 no fim do turno=%d | Treasures<0=%d | "
                  ">1 jogada de terreno no turno=%d | jogos com instantanea/feitico parado no campo=%d | farm invalido=%d | emblema Sephiroth inconsistente=%d | "
                  "Treasures virados fora de [0, estoque]=%d | wipe proprio conjurado contra a retencao da config=%d | sobrou criatura depois de Blood Money/Act=%d | "
                  "comandante conjurado sem mana pro imposto=%d | pagamento do wipe com animados invalido=%d | ficha destruida drenou so' com o Bats em campo=%d (exercitado em %d saidas de ficha por destruicao) | "
                  "MYTHOS: conjurada sem {W}{W}=%d | contador {B}{R} errado=%d | sobrou > 1 criatura/artefato/encantamento ou > 3 permanentes=%d | contador de permanentes perdidas errado=%d | "
                  "motor guardado nao sobreviveu=%d | lista da config errada=%d | wipe resolvido no cascade contra a retencao=%d | Mythos resolvidas=%d (com {B}{R} possivel=%d; permanentes minhas sacrificadas=%d, criaturas=%d) | "
                  "wipes proprios resolvidos DENTRO de cascade=%d, acertos de wipe que o cascade recusou=%d | "
                  "Treasures-criatura sacrificados pelo farm=%d | gatilhos do Dictate (proxy)=%d | wipes proprios conjurados=%d | Vihaan destruido por wipe proprio=%d | "
                  "wipes na circunstancia mitigada=%d | animados sacrificados pra pagar wipe=%d" % (
                config, modo, N, SEED0, SEED0 + N - 1, exc, vc, va, vn, vt, vm, vf, vs, vtap, vh, vw, vx, vp, vb, eb, vcor, vbr, vres, vcon, vmot, vlis, vcasc, my, mybr, myperm, mycre, cw, cr,
                fa, di, wp, cd, mi, pg))
            for sd, tb in falhas:
                print("   semente", sd, tb)

"""A/B pareado da troca Blood Money -> Mythos of Snapdax (12a rodada) no simulador do Vihaan. Variantes (mesma semente = pareado; a troca e' feita NA MESMA POSICAO da biblioteca via `swap`,
com a chave `mythos` desligada pra o resto da biblioteca ficar identico ao de ANTES; ver LEIAME):
  antes             = snapshot a17049f (lista com Blood Money), politica de retencao dos wipes proprios como no repositorio
  mythos_par        = Mythos no lugar do Blood Money (swap), `{W}{W}` conferido, mesma retencao, cascade como em a17049f (conjura wipe a forca)  [isola a troca]
  antes_cascata     = ANTES + o cascade recusa o wipe proprio segurado (a correcao achada na validacao; sem troca de carta)                   [isola a correcao do cascade]
  mythos_cascata    = Mythos no lugar do Blood Money (swap) + cascade recusando wipe segurado                                                  [o que o repositorio roda, pareado]
  mythos_sem_cor    = idem mythos_cascata, SEM conferir o `{W}{W}` (teto: mede o que a cor custa)
  antes_sem_hold    = snapshot, SEM retencao dos wipes proprios (todo wipe conjurado quando pode: sensibilidade "o que o wipe faz se eu o conjurar")
  mythos_sem_hold   = Mythos no lugar do Blood Money, SEM retencao
  mythos_sem_hold_sem_cor = idem, SEM retencao e SEM conferir o `{W}{W}` (a diferenca pra `mythos_sem_hold` e' o que a cor custa quando a carta e' de fato conjurada)
  mythos_repo       = o que o repositorio roda de verdade (chave ligada: a Mythos entra na posicao da lista.md, nao na do Blood Money) -> NAO pareado com `antes`
Uso: [FX_MODO=resiliencia] python3 fx_ab.py LOTE [--sum]   LOTE = 2000 (sementes 1_000_000+i) | 10000 (sementes 3_000_000+i)"""
import math, os, statistics as st, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
from raw_io import salvar_raw, carregar_raw

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
LOTE = int(ARGS[0]) if ARGS else 2000
SEED0 = {2000: 1_000_000, 10000: 3_000_000}.get(LOTE, 3_000_000)
SEEDS = list(range(SEED0, SEED0 + LOTE))
MODO = os.environ.get("FX_MODO", "padrao")
RAW = os.environ.get("FX_RAW") or os.path.join(F.HERE, "dados", "raw_ab_%d%s" % (LOTE, "" if MODO == "padrao" else "_" + MODO))   # FX_RAW: re-execucao sem sobrescrever o arquivo
VARIANTES = ["antes", "mythos_par", "antes_cascata", "mythos_cascata", "mythos_sem_cor", "antes_sem_hold", "mythos_sem_hold", "mythos_sem_hold_sem_cor", "mythos_repo"]
PARES = [("mythos_par", "antes"), ("antes_cascata", "antes"), ("mythos_cascata", "antes_cascata"), ("mythos_sem_cor", "antes_cascata"), ("mythos_sem_hold", "antes_sem_hold"), ("mythos_sem_hold_sem_cor", "antes_sem_hold"), ("mythos_sem_hold_sem_cor", "mythos_sem_hold"), ("antes_sem_hold", "antes")]
NAO_PAREADO = ("mythos_repo", "antes_cascata")
TURNS = 8
SWAP = ("Blood Money", "Mythos of Snapdax")
MYTHOS, BM, ACT = "Mythos of Snapdax", "Blood Money", "Blasphemous Act"


def modulo(nome):
    pid = os.getpid()
    if nome in ("antes", "antes_sem_hold"):
        return F.flags(F.carrega(F.ANTES, "vih_antes_%d_%s" % (pid, nome)), hold=(nome != "antes_sem_hold"))
    M = F.carrega(F.DEPOIS, "vih_depois_%d_%s" % (pid, nome))
    if nome == "mythos_repo":
        return F.flags(M, mythos=True)
    cascata = nome in ("antes_cascata", "mythos_cascata", "mythos_sem_cor")
    return F.flags(M, mythos=False, cor=(nome not in ("mythos_sem_cor", "mythos_sem_hold_sem_cor")), hold=(nome not in ("mythos_sem_hold", "mythos_sem_hold_sem_cor")), cascata=cascata)


def run_variant(nome):
    V = modulo(nome)
    swap = SWAP if nome.startswith("mythos") and nome != "mythos_repo" else None   # antes_cascata: sem troca (so' a correcao do cascade)
    rec = {}
    orig_pl = V.play_land
    def pl(state):
        orig_pl(state)
        if state.turn in (5, 6):
            rec[state.turn] = V.total_mana(state)
    V.play_land = pl
    chamadas, qtd = {}, {}
    orig_ct = V.create_treasures
    def ct(state, n, source="", **kw):
        chamadas[source] = chamadas.get(source, 0) + 1
        qtd[source] = qtd.get(source, 0) + n
        orig_ct(state, n, source, **kw)
    V.create_treasures = ct
    CARTAS = {BM: "bm", ACT: "act", MYTHOS: "myt"}
    wip = {"eng": 0, "cmd_dest": 0}
    for k in CARTAS.values():
        wip.update({k: 0, k + "_cre": 0, k + "_perm": 0})   # resolucoes; criaturas minhas perdidas; permanentes minhas perdidas (nao-terreno, nomeadas + fichas, liquido do que a propria resolucao cria)
    orig_res = V.resolve_instant_sorcery
    def conta(state):   # (criaturas, permanentes nao-terreno), nomeadas + fichas; a magia em voo do cascade (instantanea/feitico no campo) nao e' permanente
        nom = [n for n in state.battlefield if n not in V.LAND_NAMES and V.CARD_DB[n].ctype not in ("instant", "sorcery")]
        cre = sum(1 for n in nom if V.is_creature_card(n)) + state.constructs + state.other_tokens + state.dragons + min(state.treasures_animated_alive, state.treasures)
        return cre, len(nom) + state.constructs + state.other_tokens + state.dragons + state.treasures + state.clues + state.foods
    def res(state, name):
        if name in CARTAS:  # contagem por nome: igual em ANTES e DEPOIS (o snapshot antigo nao tem os contadores novos)
            k = CARTAS[name]
            wip[k] += 1
            casc["resolvidos"] += int(casc["dentro"])
            if state.commander_in_play or "Mahadi, Emporium Master" in state.battlefield:
                wip["eng"] += 1
            tinha = state.commander_in_play
            c0, p0 = conta(state)
            orig_res(state, name)
            c1, p1 = conta(state)
            wip[k + "_cre"] += c0 - c1
            wip[k + "_perm"] += p0 - p1
            if tinha and not state.commander_in_play:
                wip["cmd_dest"] += 1
            return
        return orig_res(state, name)
    V.resolve_instant_sorcery = res
    casc = {"dentro": False, "resolvidos": 0, "recusados": 0}   # wipes proprios resolvidos DENTRO do cascade / acertos de wipe que o cascade recusou
    orig_dc = V.do_cascade
    def dc(state, cutoff):
        casc["dentro"] = True
        try:
            return orig_dc(state, cutoff)
        finally:
            casc["dentro"] = False
    V.do_cascade = dc
    if hasattr(V, "cascade_declines"):
        orig_cd = V.cascade_declines
        def cd(state, name):
            r = orig_cd(state, name)
            casc["recusados"] += int(r)
            return r
        V.cascade_declines = cd
    bloq = set()   # turnos em que a Mythos estava na mao, o custo cabia e a COR travou
    if hasattr(V, "pips_ok"):
        orig_cc = V.can_cast
        def cc(state, name):
            r = orig_cc(state, name)
            if name == MYTHOS and not r and V.remaining_mana(state) >= V.spell_cost(state, name):
                bloq.add(state.turn)
            return r
        V.can_cast = cc
    fn = V.simulate_one if MODO == "padrao" else V.simulate_one_with_interaction
    out = []
    for sd in SEEDS:
        rec.clear(); chamadas.clear(); qtd.clear(); bloq.clear(); casc.update(dentro=False, resolvidos=0, recusados=0)
        wip.update({k: 0 for k in wip})
        s = fn(sd, TURNS, swap)
        out.append({"win_turn": s.win_turn, "revel_turn": s.revel_condition_met_turn, "treasures": s.treasures_created_total,
                    "table_dmg": s.table_damage_total, "drain": s.drain_damage_total, "combat": s.combat_damage_proxy_total,
                    "creature_deaths": s.creature_deaths_total, "bonus_mana": s.bonus_mana_generated_total, "life_gained": s.life_gained_total,
                    "recursion": s.recursion_events_total, "cards_extra": s.cards_drawn_extra,
                    "mahadi": chamadas.get("Mahadi (fim do turno)", 0), "plund_n": qtd.get("Pitiless Plunderer", 0),
                    "farm": getattr(s, "treasure_farm_total", 0), "dictate": getattr(s, "dictate_triggers_total", -1), "tend": s.treasures,
                    "bm": wip["bm"], "act": wip["act"], "myt": wip["myt"], "eng": wip["eng"], "cmd_dest": wip["cmd_dest"],
                    "bm_cre": wip["bm_cre"], "bm_perm": wip["bm_perm"], "act_cre": wip["act_cre"], "act_perm": wip["act_perm"], "myt_cre": wip["myt_cre"], "myt_perm_l": wip["myt_perm"],
                    "casc_wipe": casc["resolvidos"], "casc_recusa": casc["recusados"],
                    "myt_br": getattr(s, "mythos_br_spent_total", 0), "myt_perm": getattr(s, "mythos_perm_lost_total", 0),
                    "myt_cor_bloq": len(bloq), "myt_mao": int(MYTHOS in s.hand or wip["myt"] > 0),
                    "mana_t5": rec.get(5, 0), "mana_t6": rec.get(6, 0), "fp": F.impressao(s, norm=True)[:12]})
    return nome, out


def vec(rs):
    f = lambda k: [float(r[k]) for r in rs]
    return {"win8": [1.0 if (r["win_turn"] and r["win_turn"] <= TURNS) else 0.0 for r in rs], "treas": f("treasures"), "table": f("table_dmg"),
            "drain": f("drain"), "combat": f("combat"), "deaths": f("creature_deaths"), "bmana": f("bonus_mana"), "rec": f("recursion"),
            "m5": f("mana_t5"), "m6": f("mana_t6"), "tend": f("tend")}


def ci(a, b, pareado=True):
    if pareado:
        d = [y - x for x, y in zip(a, b)]
        return st.mean(d), (1.96 * st.stdev(d) / math.sqrt(len(d)) if len(set(d)) > 1 else 0.0)
    return st.mean(b) - st.mean(a), 1.96 * math.sqrt(st.variance(a) / len(a) + st.variance(b) / len(b))


def tabela(bruto):
    res = {k: vec(v) for k, v in bruto.items()}
    n = len(bruto["antes"])
    print("LOTE N=%d sementes %d..%d, %d turnos, %s" % (n, SEED0, SEED0 + n - 1, TURNS,
          "modo padrao (goldfish)" if MODO == "padrao" else "modo resiliencia (oponente esperto, simulate_one_with_interaction)"))
    for nome in ("antes", "antes_sem_hold"):
        b = res[nome]
        print("%-15s win<=T8 %.1f%% | Treasures criados %.2f (estoque no fim %.2f) | dano mesa %.2f combate %.2f drain %.2f | mortes de criatura %.2f | mana bonus %.2f | recursoes %.2f | mana T5 %.3f T6 %.3f" % (
            nome + ":", 100 * st.mean(b["win8"]), st.mean(b["treas"]), st.mean(b["tend"]), st.mean(b["table"]), st.mean(b["combat"]), st.mean(b["drain"]),
            st.mean(b["deaths"]), st.mean(b["bmana"]), st.mean(b["rec"]), st.mean(b["m5"]), st.mean(b["m6"])))
    cols = ("win8", "treas", "tend", "table", "combat", "drain", "deaths", "bmana", "m5", "m6")
    cab = ("win<=8 pp", "Treasures criados", "estoque no fim", "dano mesa", "combate", "drain", "mortes cria.", "mana bonus", "mana T5", "mana T6")
    print("\nDiferenca (variante - base), pareada por semente, IC95%:")
    print("%-34s " % "variante (base)" + " ".join("%-14s" % c for c in cab))
    for nome, base in PARES + [NAO_PAREADO]:
        pareado = (nome, base) != NAO_PAREADO
        linha = []
        for c in cols:
            m, h = ci(res[base][c], res[nome][c], pareado)
            fat = 100 if c == "win8" else 1
            linha.append("%+7.3f±%-6.3f" % (fat * m, fat * h))
        print("%-34s " % ("%s (%s)%s" % (nome, base, "" if pareado else " NAO pareado")) + " ".join("%-14s" % x for x in linha))
    print()
    print("(jogos iguais = impressao digital do estado final identica, com 'Mythos of Snapdax' lido como 'Blood Money'; so' mede em quantas partidas a troca/correcao mudou ALGUMA coisa)")
    print("%-24s %-12s %-12s %-10s %-10s %-24s %-18s %-20s %-16s %-16s" % ("variante", "jogos iguais", "Blood Money", "Act", "Mythos", "Mythos c/ {B}{R} poss.", "Vihaan destruido", "turnos c/ cor travada", "wipe via cascade", "cascade recusou"))
    for nome in VARIANTES:
        rs, ra = bruto[nome], bruto["antes"]
        iguais = sum(1 for x, y in zip(ra, rs) if x["fp"] == y["fp"])
        m = lambda k: st.mean([r[k] for r in rs])
        print("%-24s %5.1f%%       %-12.4f %-10.4f %-10.4f %-24.4f %-18.4f %-20.4f %-16.4f %-16.4f" % (
            nome, 100 * iguais / n, m("bm"), m("act"), m("myt"), m("myt_br"), m("cmd_dest"), m("myt_cor_bloq"), m("casc_wipe"), m("casc_recusa")))
    print("\nPor resolucao, POR CARTA (soma sobre as partidas; so' o MEU lado; criaturas = nomeadas + fichas + Treasures animados; permanentes = nao-terreno, nomeadas + fichas, liquido do que a propria")
    print("resolucao cria: o Blood Money cria 1 Treasure por criatura nao-ficha destruida, a Mythos so' sacrifica):")
    print("  %-24s %-16s %-11s %-18s %-22s" % ("variante", "carta", "resolucoes", "criaturas perdidas", "permanentes perdidos"))
    for nome in VARIANTES:
        rs = bruto[nome]
        for rotulo, k in (("Blood Money", "bm"), ("Blasphemous Act", "act"), ("Mythos of Snapdax", "myt")):
            tot = sum(r[k] for r in rs)
            if tot:
                cre = sum(r[k + "_cre"] for r in rs)
                perm = sum(r["myt_perm_l" if k == "myt" else k + "_perm"] for r in rs)
                print("  %-24s %-16s %-11d %-18.2f %-22.2f" % (nome, rotulo, tot, cre / tot, perm / tot))


if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        with Pool(4) as p:
            bruto = dict(p.map(run_variant, VARIANTES))
        salvar_raw(RAW, bruto)
    tabela(bruto)

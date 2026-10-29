"""A/B pareado da correcao da 11a rodada no simulador do Vihaan (Mirkwood Bats so' dispara em SACRIFICIO de ficha). Variantes (mesma semente = pareado; ANTES = commit b30ef1f,
em que o Bats disparava tambem em ficha DESTRUIDA por wipe proprio ou do oponente): `antes` = snapshot; `bats` = o que fica no repositorio.
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
RAW = os.path.join(F.HERE, "dados", "raw_ab_%d%s" % (LOTE, "" if MODO == "padrao" else "_" + MODO))
VARIANTES = ["antes", "bats"]
TURNS = 8


def modulo(nome):
    pid = os.getpid()
    if nome == "antes":
        return F.carrega(F.ANTES, "vih_antes_%d" % pid)
    return F.flags(F.carrega(F.DEPOIS, "vih_depois_%d_%s" % (pid, nome)), bats=True)


def run_variant(nome):
    V = modulo(nome)
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
        chamadas[source] = chamadas.get(source, 0) + 1  # chamadas (gatilhos), antes de Xorn/Procession: comparavel entre ANTES e DEPOIS
        qtd[source] = qtd.get(source, 0) + n            # quantidade pedida (Mahadi: 1 por criatura morta)
        orig_ct(state, n, source, **kw)
    V.create_treasures = ct
    bats = {"dreno": 0, "chamadas": 0}
    orig_tl = V.on_token_leaves
    def tl(state, n, *a, **kw):
        if "Mirkwood Bats" in state.battlefield and "Nadier's Nightblade" not in state.battlefield and n > 0:
            antes = state.drain_damage_total
            orig_tl(state, n, *a, **kw)
            bats["dreno"] += state.drain_damage_total - antes
            bats["chamadas"] += 1
            return
        return orig_tl(state, n, *a, **kw)
    V.on_token_leaves = tl
    wip = {"bm": 0, "act": 0, "eng": 0, "cmd_dest": 0}
    orig_res = V.resolve_instant_sorcery
    def res(state, name):
        if name in ("Blood Money", "Blasphemous Act"):  # contagem identica em ANTES e DEPOIS (o snapshot antigo nao tem os contadores novos)
            wip["bm" if name == "Blood Money" else "act"] += 1
            if state.commander_in_play or "Mahadi, Emporium Master" in state.battlefield:
                wip["eng"] += 1
            tinha = state.commander_in_play
            orig_res(state, name)
            if tinha and not state.commander_in_play:
                wip["cmd_dest"] += 1
            return
        return orig_res(state, name)
    V.resolve_instant_sorcery = res
    fn = V.simulate_one if MODO == "padrao" else V.simulate_one_with_interaction
    out = []
    for sd in SEEDS:
        rec.clear(); chamadas.clear(); qtd.clear(); wip.update(bm=0, act=0, eng=0, cmd_dest=0); bats.update(dreno=0, chamadas=0)
        s = fn(sd, TURNS)
        expiradas = sum(1 for c, d in s.impulse_pool if d < s.turn and V.CARD_DB[c].ctype != "land")
        out.append({"win_turn": s.win_turn, "revel_turn": s.revel_condition_met_turn, "treasures": s.treasures_created_total,
                    "table_dmg": s.table_damage_total, "drain": s.drain_damage_total, "combat": s.combat_damage_proxy_total,
                    "creature_deaths": s.creature_deaths_total, "bonus_mana": s.bonus_mana_generated_total, "life_gained": s.life_gained_total,
                    "recursion": s.recursion_events_total, "cards_extra": s.cards_drawn_extra,
                    "imp_lands": getattr(s, "impulse_lands_played_total", 0), "imp_spells": getattr(s, "impulse_spells_cast_total", 0),
                    "mahadi": chamadas.get("Mahadi (fim do turno)", 0), "mahadi_n": qtd.get("Mahadi (fim do turno)", 0), "plund_n": qtd.get("Pitiless Plunderer", 0),
                    "pact": chamadas.get("Prosper Pact Boon", 0), "first": getattr(s, "impulse_all_first_total", 0), "farm_dic": getattr(s, "treasure_farm_dictate_total", 0),
                    "farm": getattr(s, "treasure_farm_total", 0), "dictate": getattr(s, "dictate_triggers_total", -1), "tend": s.treasures,
                    "pool_expirado": expiradas, "bm": wip["bm"], "act": wip["act"], "eng": wip["eng"], "cmd_dest": wip["cmd_dest"],
                    "bats_dreno": bats["dreno"], "bats_chamadas": bats["chamadas"],
                    "mana_t5": rec.get(5, 0), "mana_t6": rec.get(6, 0), "fp": F.impressao(s)[:12]})
    return nome, out


def vec(rs):
    f = lambda k: [float(r[k]) for r in rs]
    return {"win8": [1.0 if (r["win_turn"] and r["win_turn"] <= TURNS) else 0.0 for r in rs], "treas": f("treasures"), "table": f("table_dmg"),
            "drain": f("drain"), "combat": f("combat"), "deaths": f("creature_deaths"), "bmana": f("bonus_mana"), "rec": f("recursion"),
            "m5": f("mana_t5"), "m6": f("mana_t6"), "tend": f("tend")}


def ci(a, b):
    d = [y - x for x, y in zip(a, b)]
    return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d)) if len(set(d)) > 1 else 0.0


def tabela(bruto):
    res = {k: vec(v) for k, v in bruto.items()}
    base = res["antes"]
    n = len(bruto["antes"])
    print("LOTE N=%d sementes %d..%d, %d turnos, %s" % (n, SEED0, SEED0 + n - 1, TURNS,
          "modo padrao (goldfish)" if MODO == "padrao" else "modo resiliencia (oponente esperto, simulate_one_with_interaction)"))
    print("ANTES: win<=T8 %.1f%% | Treasures criados %.2f (estoque no fim %.2f) | dano mesa %.2f combate %.2f drain %.2f | mortes de criatura %.2f | mana bonus %.2f | recursoes %.2f | mana T5 %.3f T6 %.3f" % (
        100 * st.mean(base["win8"]), st.mean(base["treas"]), st.mean(base["tend"]), st.mean(base["table"]), st.mean(base["combat"]), st.mean(base["drain"]),
        st.mean(base["deaths"]), st.mean(base["bmana"]), st.mean(base["rec"]), st.mean(base["m5"]), st.mean(base["m6"])))
    cols = ("win8", "treas", "tend", "table", "combat", "drain", "deaths", "bmana", "m5", "m6")
    cab = ("win<=8 pp", "Treasures criados", "estoque no fim", "dano mesa", "combate", "drain", "mortes cria.", "mana bonus", "mana T5", "mana T6")
    print("%-9s " % "variante" + " ".join("%-14s" % c for c in cab))
    for nome in VARIANTES[1:]:
        r = res[nome]
        linha = []
        for c in cols:
            m, h = ci(base[c], r[c])
            fat = 100 if c == "win8" else 1
            linha.append("%+7.3f±%-6.3f" % (fat * m, fat * h))
        print("%-9s " % nome + " ".join("%-14s" % x for x in linha))
    print()
    print("%-9s %-12s %-30s %-34s %-18s %-18s %-14s" % ("variante", "jogos iguais", "dreno atribuivel ao Bats", "saidas de ficha c/ Bats (sem Nadier)", "Blood Money", "Blasphemous Act", "pool expirado"))
    for nome in VARIANTES:
        rs, ra = bruto[nome], bruto["antes"]
        iguais = sum(1 for x, y in zip(ra, rs) if x["fp"] == y["fp"])
        m = lambda k: st.mean([r[k] for r in rs])
        print("%-9s %5.1f%%       %-30.4f %-34.4f %-18.4f %-18.4f %-14.4f" % (nome, 100 * iguais / n, m("bats_dreno"), m("bats_chamadas"), m("bm"), m("act"), m("pool_expirado")))


if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        with Pool(4) as p:
            bruto = dict(p.map(run_variant, VARIANTES))
        salvar_raw(RAW, bruto)
    tabela(bruto)

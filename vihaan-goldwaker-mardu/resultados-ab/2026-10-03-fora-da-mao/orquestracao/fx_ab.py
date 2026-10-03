"""A/B pareado das 5 correcoes de 'fora da mao' no simulador do Vihaan. Variantes (mesma semente em todas = pareado; ANTES = commit c04840d):
  antes     simulador ANTES (codigo/vihaan_goldfish_v1_ANTES_c04840d.py)
  land      DEPOIS, so' o terreno do exilio (Prosper/Inspired Tinkering/Face-Breaker) jogado + Pact Boon
  cast      DEPOIS, so' a magia do exilio pela esteira de cast (resolve, cemiterio, conta, Pact Boon)
  count     DEPOIS, so' a contagem de "spell cast" (flashback/Cascade contam; Lotho nao dispara contra si)
  storm     DEPOIS, so' o +1/+0 da Storm por Treasure sacrificado
  sevinne   DEPOIS, so' o alvo "permanent card" da Sevinne's Reclamation
  todas     DEPOIS, as cinco (e' o simulador que fica no repositorio)
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
VARIANTES = ["antes", "land", "cast", "count", "storm", "sevinne", "todas"]
TURNS = 8


def modulo(nome):
    pid = os.getpid()
    if nome == "antes":
        return F.carrega(F.ANTES, "vih_antes_%d" % pid)
    m = F.carrega(F.DEPOIS, "vih_depois_%d_%s" % (pid, nome))
    t = nome == "todas"
    return F.flags(m, land=t or nome == "land", cast=t or nome == "cast", count=t or nome == "count", storm=t or nome == "storm", sevinne=t or nome == "sevinne")


def run_variant(nome):
    V = modulo(nome)
    rec = {}
    orig_pl = V.play_land
    def pl(state):
        orig_pl(state)
        if state.turn in (5, 6):
            rec[state.turn] = V.total_mana(state)
    V.play_land = pl
    chamadas = {}
    orig_ct = V.create_treasures
    def ct(state, n, source=""):
        chamadas[source] = chamadas.get(source, 0) + 1  # chamadas (gatilhos), antes de Xorn/Procession: comparavel entre ANTES e DEPOIS
        orig_ct(state, n, source)
    V.create_treasures = ct
    fn = V.simulate_one if MODO == "padrao" else V.simulate_one_with_interaction
    out = []
    for sd in SEEDS:
        rec.clear(); chamadas.clear()
        s = fn(sd, TURNS)
        expiradas = sum(1 for c, d in s.impulse_pool if d < s.turn and V.CARD_DB[c].ctype != "land")
        out.append({"win_turn": s.win_turn, "revel_turn": s.revel_condition_met_turn, "treasures": s.treasures_created_total,
                    "table_dmg": s.table_damage_total, "drain": s.drain_damage_total, "combat": s.combat_damage_proxy_total,
                    "creature_deaths": s.creature_deaths_total, "bonus_mana": s.bonus_mana_generated_total, "life_gained": s.life_gained_total,
                    "recursion": s.recursion_events_total, "cards_extra": s.cards_drawn_extra,
                    "imp_lands": getattr(s, "impulse_lands_played_total", 0), "imp_spells": getattr(s, "impulse_spells_cast_total", 0),
                    "lotho": chamadas.get("Lotho (2a magica)", 0), "pact": chamadas.get("Prosper Pact Boon", 0), "storm_pump": getattr(s, "storm_pump_total", 0),
                    "stuck": sum(1 for c in s.battlefield if V.CARD_DB[c].ctype in ("instant", "sorcery")), "pool_expirado": expiradas,
                    "mana_t5": rec.get(5, 0), "mana_t6": rec.get(6, 0), "fp": F.impressao(s)[:12]})
    return nome, out


def vec(rs):
    f = lambda k: [float(r[k]) for r in rs]
    return {"win8": [1.0 if (r["win_turn"] and r["win_turn"] <= TURNS) else 0.0 for r in rs], "treas": f("treasures"), "table": f("table_dmg"),
            "drain": f("drain"), "combat": f("combat"), "deaths": f("creature_deaths"), "bmana": f("bonus_mana"), "rec": f("recursion"),
            "m5": f("mana_t5"), "m6": f("mana_t6")}


def ci(a, b):
    d = [y - x for x, y in zip(a, b)]
    return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d)) if len(set(d)) > 1 else 0.0


def tabela(bruto):
    res = {k: vec(v) for k, v in bruto.items()}
    base = res["antes"]
    n = len(bruto["antes"])
    print("LOTE N=%d sementes %d..%d, %d turnos, %s" % (n, SEED0, SEED0 + n - 1, TURNS,
          "modo padrao (goldfish)" if MODO == "padrao" else "modo resiliencia (oponente esperto, simulate_one_with_interaction)"))
    print("ANTES: win<=T8 %.1f%% | Treasures criados %.2f | dano mesa %.2f combate %.2f drain %.2f | mortes de criatura %.2f | mana bonus %.2f | recursoes %.2f | mana T5 %.3f T6 %.3f" % (
        100 * st.mean(base["win8"]), st.mean(base["treas"]), st.mean(base["table"]), st.mean(base["combat"]), st.mean(base["drain"]),
        st.mean(base["deaths"]), st.mean(base["bmana"]), st.mean(base["rec"]), st.mean(base["m5"]), st.mean(base["m6"])))
    cols = ("win8", "treas", "table", "combat", "drain", "deaths", "bmana", "rec", "m5", "m6")
    cab = ("win<=8 pp", "Treasures", "dano mesa", "combate", "drain", "mortes cria.", "mana bonus", "recursoes", "mana T5", "mana T6")
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
    print("%-9s %-12s %-18s %-17s %-16s %-16s %-14s %-24s %-14s" % ("variante", "jogos iguais", "terrenos do exilio", "magias do exilio", "Lotho (chamadas)", "Pact Boon (cham.)", "bonus da Storm", "magias paradas no campo", "pool expirado"))
    for nome in VARIANTES:
        rs, ra = bruto[nome], bruto["antes"]
        iguais = sum(1 for x, y in zip(ra, rs) if x["fp"] == y["fp"])
        m = lambda k: st.mean([r[k] for r in rs])
        print("%-9s %5.1f%%       %-18.4f %-17.4f %-16.4f %-16.4f %-14.4f %-24.4f %-14.4f" % (nome, 100 * iguais / n, m("imp_lands"), m("imp_spells"), m("lotho"), m("pact"), m("storm_pump"), m("stuck"), m("pool_expirado")))


if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        with Pool(4) as p:
            bruto = dict(p.map(run_variant, VARIANTES))
        salvar_raw(RAW, bruto)
    tabela(bruto)

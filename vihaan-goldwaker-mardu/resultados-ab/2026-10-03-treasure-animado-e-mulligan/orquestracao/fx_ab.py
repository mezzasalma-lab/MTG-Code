"""A/B pareado das correcoes do simulador do Vihaan (roteamento do Treasure animado, mulligan com escolha, terreno tapped em T1/T2).
Variantes (mesma semente em todas = pareado):
  antes      simulador ANTES (commit 6e623d3, codigo/vihaan_goldfish_v1_ANTES_6e623d3.py)
  treasure   DEPOIS, so' o roteamento do Treasure animado
  bottom     DEPOIS, so' o mulligan com escolha das cartas do fundo
  tapped     DEPOIS, so' o terreno tapped em T1/T2 (com teste de jogada perdida)
  blunt      DEPOIS, terreno tapped CEGO (sempre o tapped em T1/T2), so' sensibilidade
  todas      DEPOIS, as tres correcoes (e' o simulador que fica no repositorio)
  todas_t4   sensibilidade: politica de tapped vale ate' o T4
Uso: [FX_MODO=resiliencia] python3 fx_ab.py LOTE [--sum]   LOTE = 2000 (sementes 1_000_000+i) | 10000 (sementes 3_000_000+i, as do Kingpin)"""
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
VARIANTES = ["antes", "treasure", "bottom", "tapped", "blunt", "todas", "todas_t4"]
TURNS = 8


def modulo(nome):
    pid = os.getpid()
    if nome == "antes":
        return F.carrega(F.ANTES, "vih_antes_%d" % pid)
    m = F.carrega(F.DEPOIS, "vih_depois_%d_%s" % (pid, nome))
    return F.flags(m, treasure=nome in ("treasure", "todas", "todas_t4"), bottom=nome in ("bottom", "todas", "todas_t4"),
                   tapped=nome in ("tapped", "blunt", "todas", "todas_t4"), tapped_max_turn=4 if nome == "todas_t4" else None,
                   skip_if_loses_play=nome != "blunt")


def run_variant(nome):
    V = modulo(nome)
    rec = {}
    orig_pl = V.play_land
    def pl(state):
        orig_pl(state)
        if state.turn <= 6:
            rec[state.turn] = V.total_mana(state)
    V.play_land = pl
    fn = V.simulate_one if MODO == "padrao" else V.simulate_one_with_interaction
    out = []
    for sd in SEEDS:
        rec.clear()
        s = fn(sd, TURNS)
        r = {"win_turn": s.win_turn, "revel_turn": s.revel_condition_met_turn, "cmd_turn": s.commander_cast_turn,
             "treasures": s.treasures_created_total, "treasures_sacrificed": s.treasures_sacrificed_total, "treasures_end": s.treasures,
             "drain": s.drain_damage_total, "table_dmg": s.table_damage_total, "combat": s.combat_damage_proxy_total,
             "creature_deaths": s.creature_deaths_total, "artifact_deaths": s.artifact_deaths_total, "bonus_mana": s.bonus_mana_generated_total,
             "life_gained": s.life_gained_total, "cards_extra": s.cards_drawn_extra, "magda_dragons": s.magda_dragons_created_total,
             "mulligans": s.mulligans, "animated_any": getattr(s, "animated_treasures_sacrificed_any_total", 0),
             "animated_altar": s.animated_treasures_sacrificed_total,
             "tapped_first": getattr(s, "tapped_land_first_plays_total", 0), "tapped_skipped": getattr(s, "tapped_land_skipped_for_play_total", 0),
             "fp": F.impressao(s)[:12]}
        for t in range(1, 7):
            r["mana_t%d" % t] = rec.get(t, 0)
        out.append(r)
    return nome, out


def vec(rs):
    c = lambda r: r["cmd_turn"] if r["cmd_turn"] else 99
    v = {"win8": [1.0 if (r["win_turn"] and r["win_turn"] <= TURNS) else 0.0 for r in rs],
         "revel8": [1.0 if (r["revel_turn"] and r["revel_turn"] <= TURNS) else 0.0 for r in rs],
         "cmd3": [1.0 if c(r) <= 3 else 0.0 for r in rs], "cmd4": [1.0 if c(r) <= 4 else 0.0 for r in rs],
         "treas": [float(r["treasures"]) for r in rs], "tend": [float(r["treasures_end"]) for r in rs],
         "table": [float(r["table_dmg"]) for r in rs], "combat": [float(r["combat"]) for r in rs], "drain": [float(r["drain"]) for r in rs],
         "deaths": [float(r["creature_deaths"]) for r in rs], "bmana": [float(r["bonus_mana"]) for r in rs]}
    for t in (2, 3, 4):
        v["m%d" % t] = [float(r["mana_t%d" % t]) for r in rs]
    return v


def ci(a, b):
    d = [y - x for x, y in zip(a, b)]
    return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d)) if len(set(d)) > 1 else 0.0


def tabela(bruto):
    res = {k: vec(v) for k, v in bruto.items()}
    base = res["antes"]
    n = len(bruto["antes"])
    print("LOTE N=%d sementes %d..%d, %d turnos, %s" % (n, SEED0, SEED0 + n - 1, TURNS,
          "modo padrao (goldfish)" if MODO == "padrao" else "modo resiliencia (oponente esperto, simulate_one_with_interaction)"))
    print("ANTES: win<=T8 %.1f%% revel<=T8 %.2f%% cmd<=3 %.1f%% cmd<=4 %.1f%% Treasures criados %.2f (fim %.2f) dano mesa %.2f combate %.2f drain %.2f mortes de criatura %.2f mana bonus %.2f | mana T2 %.3f T3 %.3f T4 %.3f" % (
        100 * st.mean(base["win8"]), 100 * st.mean(base["revel8"]), 100 * st.mean(base["cmd3"]), 100 * st.mean(base["cmd4"]), st.mean(base["treas"]), st.mean(base["tend"]),
        st.mean(base["table"]), st.mean(base["combat"]), st.mean(base["drain"]), st.mean(base["deaths"]), st.mean(base["bmana"]),
        st.mean(base["m2"]), st.mean(base["m3"]), st.mean(base["m4"])))
    cols = ("win8", "revel8", "cmd3", "cmd4", "treas", "table", "combat", "drain", "deaths", "bmana", "m2", "m3", "m4")
    cab = ("win<=8 pp", "revel<=8 pp", "cmd<=3 pp", "cmd<=4 pp", "Treasures", "dano mesa", "combate", "drain", "mortes cria.", "mana bonus", "mana T2", "mana T3", "mana T4")
    print("%-9s " % "variante" + " ".join("%-13s" % c for c in cab))
    for nome in VARIANTES[1:]:
        r = res[nome]
        linha = []
        for c in cols:
            m, h = ci(base[c], r[c])
            f = 100 if c in ("win8", "revel8", "cmd3", "cmd4") else 1
            linha.append("%+6.2f±%-5.2f" % (f * m, f * h))
        print("%-9s " % nome + " ".join("%-13s" % x for x in linha))
    print()
    print("%-9s %-13s %-14s %-14s %-12s %-18s" % ("variante", "jogos iguais", "animados/jogo", "(so' Altar)", "tapped 1o", "untapped p/jogada"))
    for nome in VARIANTES[1:]:
        rs, ra = bruto[nome], bruto["antes"]
        iguais = sum(1 for x, y in zip(ra, rs) if x["fp"] == y["fp"])
        print("%-9s %5.1f%%        %-14.3f %-14.3f %-12.3f %-18.3f" % (nome, 100 * iguais / n, st.mean([r["animated_any"] for r in rs]),
              st.mean([r["animated_altar"] for r in rs]), st.mean([r["tapped_first"] for r in rs]), st.mean([r["tapped_skipped"] for r in rs])))


if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        with Pool(4) as p:
            bruto = dict(p.map(run_variant, VARIANTES))
        salvar_raw(RAW, bruto)
    tabela(bruto)

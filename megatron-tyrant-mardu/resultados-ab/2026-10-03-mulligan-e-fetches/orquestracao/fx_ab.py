"""A/B pareado das correcoes de 2026-10-03 (2a rodada) no simulador do Megatron: London Mulligan e fetch lands.
Variantes (mesma semente em todas = pareado):
  antes         simulador ANTES (commit 3dae6ba, codigo/megatron_goldfish_v1_ANTES_3dae6ba.py)
  mull_posicao  DEPOIS, mulligan so' com a posicao corrigida (menor MV, mas no FUNDO) -- isola o efeito da posicao
  mull_smart    DEPOIS, mulligan com escolha das cartas do fundo (fetches desligadas)
  fetch         DEPOIS, fetch lands com a habilidade real (mulligan antigo)
  ambas         DEPOIS, as duas (e' o simulador que fica no repositorio)
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
MODO = os.environ.get("FX_MODO", "padrao")   # padrao = goldfish puro | resiliencia = simulate_one_with_interaction
RAW = os.path.join(F.HERE, "dados", "raw_ab_%d%s" % (LOTE, "" if MODO == "padrao" else "_" + MODO))
VARIANTES = ["antes", "mull_posicao", "mull_smart", "fetch", "ambas"]


def modulo(nome):
    pid = os.getpid()
    if nome == "antes":
        return F.carrega(F.ANTES, "meg_antes_%d" % pid)
    m = F.carrega(F.DEPOIS, "meg_depois_%d_%s" % (pid, nome))
    mull = {"mull_posicao": "bottom_only", "mull_smart": "smart", "fetch": "legacy", "ambas": "smart"}[nome]
    return F.flags(m, mulligan=mull, fetch=nome in ("fetch", "ambas"))


def run_variant(nome):
    M = modulo(nome)
    rec = {}
    # mana disponivel NO 1o main phase de cada turno (depois de jogar o terreno E de sacrificar o Rocky Tar Pit, que so' e'
    # sacrificado entre o play_land e o main phase: medir logo depois de play_land subestimaria o Rocky)
    orig_mp = M.main_phase
    def mp(state):
        if state.turn <= 6 and state.turn not in rec:
            rec[state.turn] = M.total_mana(state)
        orig_mp(state)
    M.main_phase = mp
    out = []
    for sd in SEEDS:
        rec.clear()
        s = (M.simulate_one if MODO == "padrao" else M.simulate_one_with_interaction)(sd, 8)
        r = {"cmd_turn": s.commander_cast_turn, "proxy_dmg": s.proxy_damage_total, "mana_convert": s.megatron_mana_generated_total,
             "conversions": s.megatron_conversions_total, "weld": s.weld_activations_total, "recursion": s.recursion_events_total,
             "cards_extra": s.cards_drawn_extra, "poison_win": 1 if s.blightsteel_poison_win else 0,
             "cmd_dmg_win": 1 if s.commander_damage_win else 0, "lands_end": sum(1 for n in s.battlefield if n in M.LAND_NAMES),
             "hand": len(s.hand), "ramp": s.ramp_pieces_cast_total, "mulligans": s.mulligans,
             "myriad_acts": getattr(s, "myriad_activations_total", 0), "fetch_cracks": getattr(s, "fetch_cracks_total", 0),
             "fetch_duals": getattr(s, "fetch_duals_fetched_total", 0), "fetch_untapped": getattr(s, "fetch_untapped_total", 0),
             "fp": F.impressao(s)[:12]}
        for t in range(1, 7):
            r["mana_t%d" % t] = rec.get(t, 0)
        out.append(r)
    return nome, out


def vec(rs):
    c = lambda r: r["cmd_turn"] if r["cmd_turn"] else 99
    v = {"cmd3": [1.0 if c(r) <= 3 else 0.0 for r in rs], "cmd4": [1.0 if c(r) <= 4 else 0.0 for r in rs],
         "cmd5": [1.0 if c(r) <= 5 else 0.0 for r in rs], "never": [1.0 if c(r) == 99 else 0.0 for r in rs],
         "win": [1.0 if (r["poison_win"] or r["cmd_dmg_win"]) else 0.0 for r in rs],
         "dmg": [float(r["proxy_dmg"]) for r in rs], "mana": [float(r["mana_convert"]) for r in rs],
         "weld": [float(r["weld"]) for r in rs], "lands": [float(r["lands_end"]) for r in rs],
         "extra": [float(r["cards_extra"]) for r in rs], "ramp": [float(r["ramp"]) for r in rs]}
    for t in (2, 3, 4, 5):
        v["m%d" % t] = [float(r["mana_t%d" % t]) for r in rs]
    return v


def ci(a, b):
    d = [y - x for x, y in zip(a, b)]
    return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d))


def tabela(bruto):
    res = {k: vec(v) for k, v in bruto.items()}
    base = res["antes"]
    n = len(bruto["antes"])
    print("LOTE N=%d sementes %d..%d, 8 turnos, %s" % (n, SEED0, SEED0 + n - 1,
          "modo padrao (goldfish)" if MODO == "padrao" else "modo resiliencia (oponente esperto, simulate_one_with_interaction)"))
    print("ANTES: cmd<=3 %.1f%% cmd<=4 %.1f%% cmd<=5 %.1f%% nunca(T8) %.1f%% win %.1f%% dano %.2f mana_conv %.2f weld %.3f | mana no main phase T2 %.3f T3 %.3f T4 %.3f T5 %.3f" % (
        100*st.mean(base["cmd3"]), 100*st.mean(base["cmd4"]), 100*st.mean(base["cmd5"]), 100*st.mean(base["never"]), 100*st.mean(base["win"]),
        st.mean(base["dmg"]), st.mean(base["mana"]), st.mean(base["weld"]), st.mean(base["m2"]), st.mean(base["m3"]), st.mean(base["m4"]), st.mean(base["m5"])))
    cols = ("cmd3", "cmd4", "cmd5", "never", "win", "dmg", "mana", "weld", "m2", "m3", "m4", "m5", "lands", "extra")
    cab = ("cmd<=3 pp", "cmd<=4 pp", "cmd<=5 pp", "nunca pp", "win pp", "dano", "mana conv", "weld", "mana T2", "mana T3", "mana T4", "mana T5", "terrenos", "cartas extra")
    print("%-13s " % "variante" + " ".join("%-13s" % c for c in cab))
    for nome in VARIANTES[1:]:
        r = res[nome]
        linha = []
        for c in cols:
            m, h = ci(base[c], r[c])
            f = 100 if c in ("cmd3", "cmd4", "cmd5", "never", "win") else 1
            linha.append("%+6.2f±%-5.2f" % (f * m, f * h))
        print("%-13s " % nome + " ".join("%-13s" % x for x in linha))
    print()
    print("%-13s %-13s %-16s %-16s %-16s" % ("variante", "jogos iguais", "fetch: sacrif.", "Rocky: duais", "Rocky: untapped"))
    for nome in VARIANTES[1:]:
        rs, ra = bruto[nome], bruto["antes"]
        iguais = sum(1 for x, y in zip(ra, rs) if x["fp"] == y["fp"])
        print("%-13s %5.1f%%        %-16.3f %-16.3f %-16.3f" % (nome, 100 * iguais / n, st.mean([r["fetch_cracks"] for r in rs]),
              st.mean([r["fetch_duals"] for r in rs]), st.mean([r["fetch_untapped"] for r in rs])))


if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        with Pool(4) as p:
            bruto = dict(p.map(run_variant, VARIANTES))
        salvar_raw(RAW, bruto)
    tabela(bruto)

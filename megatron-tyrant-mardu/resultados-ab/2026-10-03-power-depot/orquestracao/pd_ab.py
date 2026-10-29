"""A/B pareado: Power Depot entra no lugar de X (mesma posição), Megatron, 8 turnos, N sementes 3_000_000+i.
X = cada terreno distinto da lista (+ 2 rocks como comparação terreno-vs-rock). A política de jogada vem de PD_POLICY (core|early|early_all|fodder7|early_all_fodder7).
Uso: PD_POLICY=core PD_COLOR=sim|strict python3 pd_ab.py [N] [--sum]   (--sum refaz a tabela a partir do bruto arquivado)"""
import json, math, sys, statistics as st
from multiprocessing import Pool
sys.path.insert(0, '.')
import pd_harness as H
from raw_io import salvar_raw, carregar_raw
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
N = int(ARGS[0]) if ARGS else 10000
SEEDS = list(range(3_000_000, 3_000_000 + N))
POL = H.POLICY["mode"]
RAW = H.DADOS + "/raw_ab_powerdepot_%d_%s%s" % (N, POL, "" if H.COLOR == "sim" else "_" + H.COLOR)
LANDS = ["Plains", "Swamp", "Mountain", "Fountainport", "Myriad Landscape", "Susur Secundi, Void Altar", "Evolving Wilds", "Terramorphic Expanse",
         "Rocky Tar Pit", "Sunlit Marsh", "Nomad Outpost", "Smoldering Marsh", "Shadowblood Ridge", "Exotic Orchard", "Forbidden Orchard",
         "Scrubland", "Plateau", "Badlands", "Command Tower"]
ROCKS = ["Arcane Signet", "Fellwar Stone"]
def vec(rs):
    c = lambda r: r["cmd_turn"] if r["cmd_turn"] else 99
    return {"cmd3": [1.0 if c(r) <= 3 else 0.0 for r in rs], "cmd4": [1.0 if c(r) <= 4 else 0.0 for r in rs], "cmd5": [1.0 if c(r) <= 5 else 0.0 for r in rs],
            "never": [1.0 if c(r) == 99 else 0.0 for r in rs], "win": [1.0 if (r["poison_win"] or r["cmd_dmg_win"]) else 0.0 for r in rs],
            "dmg": [float(r["proxy_dmg"]) for r in rs], "mana": [float(r["mana_convert"]) for r in rs], "weld": [float(r["weld"]) for r in rs],
            "lands": [float(r["lands_end"]) for r in rs], "depot": [1.0 if r["depot_turn"] else 0.0 for r in rs],
            "fixcmd": [1.0 if r["depot_fixed_cmd_turn"] else 0.0 for r in rs],
            "fixdec": [1.0 if (r["depot_fixed_cmd_turn"] and r["cmd_turn"] and r["depot_fixed_cmd_turn"] == r["cmd_turn"]) else 0.0 for r in rs]}
def job(x):
    return ("__base__" if x is None else x), H.run_variant(([] if x is None else [(x, H.DEPOT)], SEEDS, 8))
def ci(a, b):
    d = [y - x for x, y in zip(a, b)]; return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d))
def tabela(bruto):
    res = {k: vec(v) for k, v in bruto.items()}
    base = res["__base__"]
    print("política=%s cor=%s N=%d base: cmd<=3 %.1f%% cmd<=4 %.1f%% cmd<=5 %.1f%% nunca(T8) %.1f%% win %.1f%% dano %.2f mana_conv %.2f weld %.3f terrenos(fim) %.2f" % (
        POL, H.COLOR, N, 100*st.mean(base["cmd3"]), 100*st.mean(base["cmd4"]), 100*st.mean(base["cmd5"]), 100*st.mean(base["never"]), 100*st.mean(base["win"]),
        st.mean(base["dmg"]), st.mean(base["mana"]), st.mean(base["weld"]), st.mean(base["lands"])))
    print("%-27s %-13s %-13s %-13s %-13s %-13s %-12s %-12s %6s %6s %6s" % ("Depot no lugar de", "cmd<=3 (pp)", "cmd<=4 (pp)", "cmd<=5 (pp)", "nunca T8 (pp)", "win (pp)", "dano", "mana conv.", "Depot", "fixa", "decis."))
    for x in LANDS + ROCKS:
        r = res[x]; row = {k: ci(base[k], r[k]) for k in ("cmd3", "cmd4", "cmd5", "never", "win", "dmg", "mana")}
        print("%-27s %+5.2f±%-6.2f %+5.2f±%-6.2f %+5.2f±%-6.2f %+5.2f±%-6.2f %+5.2f±%-6.2f %+5.2f±%-5.2f %+5.2f±%-5.2f %5.1f%% %5.1f%% %5.1f%%" % (
            x[:27], 100*row["cmd3"][0], 100*row["cmd3"][1], 100*row["cmd4"][0], 100*row["cmd4"][1], 100*row["cmd5"][0], 100*row["cmd5"][1], 100*row["never"][0], 100*row["never"][1],
            100*row["win"][0], 100*row["win"][1], row["dmg"][0], row["dmg"][1], row["mana"][0], row["mana"][1], 100*st.mean(r["depot"]), 100*st.mean(r["fixcmd"]), 100*st.mean(r["fixdec"])))
if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        with Pool(4) as p:
            bruto = dict(p.map(job, [None] + LANDS + ROCKS))
        salvar_raw(RAW, bruto)
    tabela(bruto)

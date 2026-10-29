"""A/B pareado: Inevitable Defeat entra no lugar de X (mesma posição), Vihaan, 8 turnos, N sementes 3_000_000+i.
Controles: Arcane Signet (deve doer), Sol Ring (deve doer muito), Blank Card (carta morta no mesmo slot)."""
import json, math, sys, statistics as st
from multiprocessing import Pool
sys.path.insert(0, '.')
import vih_harness as H
from raw_io import salvar_raw, carregar_raw
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
SEEDS = list(range(3_000_000, 3_000_000 + N))
CUTS = ["Monologue Tax", "Academy Manufactor", "Back in Town", "Teferi's Protection", "Smothering Tithe", "Council's Judgment",
        "Shoot the Sheriff", "Boros Charm", "Path to Exile", "Deadly Derision", "Requisition Raid", "Blasphemous Act", "Life Insurance",
        "Mari, the Killing Quill", "The Reaver Cleaver", "Laughing Jasper Flint", "Urabrask's Forge", "Lotho, Corrupt Shirriff", "Orochi Soul-Reaver"]
CTRL = ["Arcane Signet", "Sol Ring"]
def vec(rs):
    return {"win8": [1.0 if (r["win_turn"] and r["win_turn"] <= 8) else 0.0 for r in rs],
            "cmd3": [1.0 if (r["cmd_turn"] and r["cmd_turn"] <= 3) else 0.0 for r in rs],
            "table": [float(r["table_dmg"]) for r in rs], "combat": [float(r["combat"]) for r in rs],
            "treasures": [float(r["treasures"]) for r in rs], "removal": [float(r["removal"]) for r in rs],
            "life": [float(r["life_gained"]) for r in rs], "recursion": [float(r["recursion"]) for r in rs], "magda": [float(r["defeat_magda"]) for r in rs], "witch": [float(r["defeat_witch"]) for r in rs], "defeat_cast": [1.0 if r["defeat_turn"] else 0.0 for r in rs]}
RAW = H.DADOS + "/raw_ab_vihaan_%d_cor-%s" % (N, H.COLOR_MODE)
def job(v):
    kind, x = v
    if kind == "base": pairs = []
    elif kind == "defeat": pairs = [(x, H.DEFEAT)]
    else: pairs = [(x, H.BLANK)]
    return v, H.run_variant((pairs, SEEDS, 8))
def chave(v): return "%s|%s" % (v[0], v[1])
def ci(a, b):
    d = [y - x for x, y in zip(a, b)]; m = st.mean(d); se = st.stdev(d) / math.sqrt(len(d)); return m, 1.96 * se
if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        jobs = [("base", None)] + [("defeat", c) for c in CUTS + CTRL] + [("blank", c) for c in CUTS[:3]]
        with Pool(4) as p:
            bruto = {chave(k): v for k, v in p.map(job, jobs)}
        salvar_raw(RAW, bruto)
    res = {tuple((k.split("|")[0], None if k.split("|")[1] == "None" else k.split("|")[1])): vec(v) for k, v in bruto.items()}
    base = res[("base", None)]
    out = {"N": N, "base_mean": {k: st.mean(v) for k, v in base.items()}, "defeat": {}}
    print("N=%d base: win<=8=%.3f cmd<=3=%.3f table=%.2f combat=%.2f removal=%.2f life=%.2f" % (N, st.mean(base["win8"]), st.mean(base["cmd3"]), st.mean(base["table"]), st.mean(base["combat"]), st.mean(base["removal"]), st.mean(base["life"])))
    print("%-26s %-17s %-17s %-17s %-15s %-8s" % ("Defeat entra no lugar de", "win<=8 (pp)", "cmd<=3 (pp)", "table dmg", "treasures", "cast%  Magda/Witch em campo (% jogos)"))
    for kind, label in (("defeat", "D"), ("blank", "B")):
        for c in (CUTS + CTRL if kind == "defeat" else CUTS[:3]):
            r = res[(kind, c)]; row = {}
            for k in ("win8", "cmd3", "table", "treasures", "combat", "removal", "life", "recursion"):
                row[k] = ci(base[k], r[k])
            row["cast"] = st.mean(r["defeat_cast"]); row["magda_rate"] = st.mean(r["magda"]); row["witch_rate"] = st.mean(r["witch"])
            out.setdefault(kind, {})[c] = row
            tag = ("%s<-%s" % ("Defeat", c)) if kind == "defeat" else ("Blank<-%s" % c)
            print("%-26s %+6.2f±%-8.2f %+6.2f±%-8.2f %+6.2f±%-8.2f %+5.2f±%-7.2f %6.1f%%  %4.1f / %4.1f  recursao %+5.3f±%.3f" % (tag[:26], 100*row["win8"][0], 100*row["win8"][1], 100*row["cmd3"][0], 100*row["cmd3"][1], row["table"][0], row["table"][1], row["treasures"][0], row["treasures"][1], 100*row["cast"], 100*row["magda_rate"], 100*row["witch_rate"], row["recursion"][0], row["recursion"][1]))

"""A/B pareado: Inevitable Defeat entra no lugar de X (mesma posição), Megatron, 8 turnos, N sementes 3_000_000+i.
Controles (devem doer): Arcane Signet, Fellwar Stone. Blank<-X mostra o viés de 'carta morta' do simulador (descarte grátis)."""
import json, math, sys, statistics as st
from multiprocessing import Pool
sys.path.insert(0, '.')
import meg_harness as H
from raw_io import salvar_raw, carregar_raw
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
SEEDS = list(range(3_000_000, 3_000_000 + N))
CUTS = ["Chaos Warp", "Generous Gift", "Path to Exile", "Swords to Plowshares", "Vandalblast", "Heartless Conscription", "Decree of Pain",
        "Blasphemous Act", "Tarrian's Journal", "Scarecrone", "Black Market Connections", "Clever Concealment", "Pia's Revolution"]
CTRL = ["Arcane Signet", "Fellwar Stone"]
def vec(rs):
    return {"win": [1.0 if (r["poison_win"] or r["cmd_dmg_win"]) else 0.0 for r in rs],
            "cmd5": [1.0 if (r["cmd_turn"] and r["cmd_turn"] <= 5) else 0.0 for r in rs],
            "dmg": [float(r["proxy_dmg"]) for r in rs], "dmg120": [1.0 if r["proxy_dmg"] >= 120 else 0.0 for r in rs],
            "mana": [float(r["mana_convert"]) for r in rs], "interaction": [float(r["interaction"]) for r in rs],
            "life": [float(r["lifegain"]) for r in rs], "weld": [float(r["weld"]) for r in rs],
            "cast": [1.0 if r["defeat_turn"] else 0.0 for r in rs], "tyrant": [float(r["defeat_tyrant_face"]) for r in rs],
            "cmdin": [float(r["defeat_with_megatron"]) for r in rs]}
RAW = H.DADOS + "/raw_ab_megatron_%d" % N
def job(v):
    kind, x = v
    pairs = [] if kind == "base" else [(x, H.DEFEAT if kind == "defeat" else H.BLANK)]
    return v, H.run_variant((pairs, SEEDS, 8))
def chave(v): return "%s|%s" % (v[0], v[1])
def ci(a, b):
    d = [y - x for x, y in zip(a, b)]; return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d))
if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        jobs = [("base", None)] + [("defeat", c) for c in CUTS + CTRL] + [("blank", c) for c in CUTS[:4]]
        with Pool(4) as p:
            bruto = {chave(k): v for k, v in p.map(job, jobs)}
        salvar_raw(RAW, bruto)
    res = {tuple((k.split("|")[0], None if k.split("|")[1] == "None" else k.split("|")[1])): vec(v) for k, v in bruto.items()}
    base = res[("base", None)]
    out = {"N": N, "base_mean": {k: st.mean(v) for k, v in base.items()}}
    print("N=%d base: win=%.3f cmd<=5=%.3f dmg=%.2f dmg>=120=%.3f mana_conv=%.2f interaction=%.2f lifegain=%.2f" % (N, st.mean(base["win"]), st.mean(base["cmd5"]), st.mean(base["dmg"]), st.mean(base["dmg120"]), st.mean(base["mana"]), st.mean(base["interaction"]), st.mean(base["life"])))
    print("%-27s %-15s %-15s %-15s %-15s %-14s %6s %8s %8s" % ("variante", "win (pp)", "cmd<=5 (pp)", "dmg", "mana convertida", "interacao", "cast%", "c/Tyrant", "c/Megat"))
    for kind in ("defeat", "blank"):
        for c in (CUTS + CTRL if kind == "defeat" else CUTS[:4]):
            r = res[(kind, c)]; row = {k: ci(base[k], r[k]) for k in ("win", "cmd5", "dmg", "dmg120", "mana", "interaction", "life", "weld")}
            row["cast"] = st.mean(r["cast"]); row["tyrant"] = st.mean(r["tyrant"]); row["cmdin"] = st.mean(r["cmdin"])
            out.setdefault(kind, {})[c] = row
            tag = ("Defeat<-%s" if kind == "defeat" else "Blank<-%s") % c
            print("%-27s %+5.2f±%-7.2f %+5.2f±%-7.2f %+5.2f±%-7.2f %+5.2f±%-7.2f %+5.2f±%-6.2f %5.1f%% %7.1f%% %7.1f%%" % (tag[:27], 100*row["win"][0], 100*row["win"][1], 100*row["cmd5"][0], 100*row["cmd5"][1], row["dmg"][0], row["dmg"][1], row["mana"][0], row["mana"][1], row["interaction"][0], row["interaction"][1], 100*row["cast"], 100*row["tyrant"], 100*row["cmdin"]))

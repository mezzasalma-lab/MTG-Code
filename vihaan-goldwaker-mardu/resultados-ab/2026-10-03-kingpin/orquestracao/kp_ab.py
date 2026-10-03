"""A/B pareado: Kingpin entra no lugar de X (mesma posição), Vihaan, 8 turnos, N sementes 3_000_000+i. X = TODA carta não-terreno da lista (exceto o
comandante): inclui Sol Ring e Arcane Signet como controles que devem doer. + 3 linhas 'Blank<-X' (carta inconjurável, viés de carta morta).
A política vem de KP_POLICY (sim|anim|delib). Uso: KP_POLICY=anim [KP_TURNS=12 KP_SLOTS='A|B|C' KP_BLANKS='A|B'] python3 kp_ab.py [N] [--sum]   (--sum refaz a tabela a partir do bruto arquivado)"""
import json, math, os, sys, statistics as st
from multiprocessing import Pool
sys.path.insert(0, '.')
import kp_harness as H
from raw_io import salvar_raw, carregar_raw
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
N = int(ARGS[0]) if ARGS else 6000
SEEDS = list(range(3_000_000, 3_000_000 + N))
POL = H.POLICY["mode"]
TURNS = int(os.environ.get("KP_TURNS", "8"))            # horizonte; 12 = rodada longa (o motor de Treasure rende mais turnos depois da conjuração)
SLOTS = [x for x in os.environ.get("KP_SLOTS", "").split("|") if x]   # subconjunto de cortes (rodada longa)
BLK = [x for x in os.environ.get("KP_BLANKS", "").split("|") if x]     # Blank<-X extras na rodada longa (a Blank não depende da política)
RAW = H.DADOS + "/raw_ab_kingpin_%d_%s%s%s%s" % (N, POL, "" if TURNS == 8 else "_t%d" % TURNS, "_slots" if SLOTS else "", "_blk" if BLK else "")
CUTS = SLOTS or sorted({n for n in H.ORIG_LIBRARY if H.V.CARD_DB[n].ctype != "land" and n != H.V.COMMANDER})
BLANKS = ["Monologue Tax", "Academy Manufactor", "Back in Town"]
def vec(rs):
    return {"win8": [1.0 if (r["win_turn"] and r["win_turn"] <= TURNS) else 0.0 for r in rs],
            "revel8": [1.0 if (r["revel_turn"] and r["revel_turn"] <= TURNS) else 0.0 for r in rs],
            "cmd3": [1.0 if (r["cmd_turn"] and r["cmd_turn"] <= 3) else 0.0 for r in rs],
            "treas": [float(r["treasures"]) for r in rs], "tend": [float(r["treasures_end"]) for r in rs],
            "table": [float(r["table_dmg"]) for r in rs], "combat": [float(r["combat"]) for r in rs],
            "drain": [float(r["drain"]) for r in rs], "dragons": [float(r["magda_dragons"]) for r in rs],
            "cast": [1.0 if r["kp_cast_turn"] else 0.0 for r in rs], "trig": [float(r["kp_triggers"]) for r in rs],
            "ktre": [float(r["kp_treasures"]) for r in rs]}
def job(v):
    kind, x = v
    pairs = [] if kind == "base" else [(x, H.KINGPIN if kind == "kp" else H.BLANK)]
    return "%s|%s" % (kind, x), H.run_variant((pairs, SEEDS, TURNS))
def ci(a, b):
    d = [y - x for x, y in zip(a, b)]; return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d))
def tabela(bruto):
    res = {k: vec(v) for k, v in bruto.items()}
    base = res["base|None"]
    print("política=%s turnos=%d N=%d base: win<=T %.1f%% revel<=T %.2f%% cmd<=3 %.1f%% Treasures criados %.2f (fim %.2f) dano mesa %.2f combate %.2f dragões Magda %.3f" % (
        POL, TURNS, N, 100*st.mean(base["win8"]), 100*st.mean(base["revel8"]), 100*st.mean(base["cmd3"]), st.mean(base["treas"]), st.mean(base["tend"]),
        st.mean(base["table"]), st.mean(base["combat"]), st.mean(base["dragons"])))
    rows = []
    for k, r in res.items():
        kind, x = k.split("|", 1)
        if kind == "base": continue
        row = {m: ci(base[m], r[m]) for m in ("win8", "revel8", "cmd3", "treas", "table", "combat", "drain")}
        cast = st.mean(r["cast"]); ct = [i for i, c in enumerate(r["cast"]) if c]
        row["cast"] = cast; row["trig"] = (st.mean(r["trig"][i] for i in ct) if ct else 0.0); row["ktre"] = (st.mean(r["ktre"][i] for i in ct) if ct else 0.0)
        rows.append((kind, x, row))
    rows.sort(key=lambda t: (t[0] != "kp", -t[2]["win8"][0] - t[2]["treas"][0] / 50))
    print("%-30s %-14s %-13s %-13s %-12s %-12s %-12s %6s %9s %7s" % ("Kingpin entra no lugar de", "win<=T (pp)", "revel<=T (pp)", "cmd<=3 (pp)", "Treasures", "dano mesa", "combate", "cast%", "disp/jogo", "T/jogo"))
    for kind, x, r in rows:
        tag = ("Kingpin<-%s" % x) if kind == "kp" else ("Blank<-%s" % x)
        print("%-30s %+5.2f±%-6.2f %+5.2f±%-6.2f %+5.2f±%-5.2f %+5.2f±%-5.2f %+5.2f±%-5.2f %+5.2f±%-5.2f %5.1f%% %9.2f %7.2f" % (
            tag[:30], 100*r["win8"][0], 100*r["win8"][1], 100*r["revel8"][0], 100*r["revel8"][1], 100*r["cmd3"][0], 100*r["cmd3"][1],
            r["treas"][0], r["treas"][1], r["table"][0], r["table"][1], r["combat"][0], r["combat"][1], 100*r["cast"], r["trig"], r["ktre"]))
if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        jobs = [("base", None)] + [("kp", c) for c in CUTS] + [("blank", c) for c in (BLK or ([] if SLOTS else BLANKS))]
        with Pool(4) as p:
            bruto = dict(p.map(job, jobs))
        salvar_raw(RAW, bruto)
    tabela(bruto)

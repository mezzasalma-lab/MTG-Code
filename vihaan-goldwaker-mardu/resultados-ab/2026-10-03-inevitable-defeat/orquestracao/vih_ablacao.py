"""Ablação do Vihaan: custo de cortar cada carta não-terreno (trocada por inconjurável 'Blank Card'), N pareado, 8 turnos.
Uso: python3 vih_ablacao.py [--sum]   (--sum refaz a tabela a partir do bruto arquivado)"""
import json, sys, statistics as st
from multiprocessing import Pool
sys.path.insert(0, '.')
import vih_harness as H
from raw_io import salvar_raw, carregar_raw
N = 5000; SEEDS = list(range(3_000_000, 3_000_000 + N))
RAW = H.DADOS + "/raw_ablacao_vihaan"
def metr(rs):
    w = [r["win_turn"] if r["win_turn"] else 99 for r in rs]; c = [r["cmd_turn"] if r["cmd_turn"] else 99 for r in rs]
    return {"win<=8": sum(1 for x in w if x <= 8) / len(rs), "win<=6": sum(1 for x in w if x <= 6) / len(rs), "cmd<=3": sum(1 for x in c if x <= 3) / len(rs),
            "treasures": st.mean(r["treasures"] for r in rs), "table": st.mean(r["table_dmg"] for r in rs), "combat": st.mean(r["combat"] for r in rs), "removal": st.mean(r["removal"] for r in rs)}
def job(card):
    pairs = [] if card is None else [(card, H.BLANK)]
    return ("__base__" if card is None else card), H.run_variant((pairs, SEEDS, 8))
def tabela(raw):
    out = {(None if k == "__base__" else k): metr(v) for k, v in raw.items()}
    cands = [c for c in out if c is not None]
    base = out[None]
    rows = sorted(((c, {k: out[c][k] - base[k] for k in base}) for c in cands), key=lambda r: r[1]["win<=8"] * 100 + r[1]["cmd<=3"] * 100 + r[1]["table"] / 5)
    print("base:", {k: round(v, 3) for k, v in base.items()})
    print("%-34s %8s %8s %8s %9s %8s %8s" % ("sai (maior perda primeiro)", "win<=8", "win<=6", "cmd<=3", "treasures", "table", "combat"))
    for c, d in rows:
        print("%-34s %+7.1fpp %+7.1fpp %+7.1fpp %+9.2f %+8.1f %+8.1f" % (c[:34], 100*d["win<=8"], 100*d["win<=6"], 100*d["cmd<=3"], d["treasures"], d["table"], d["combat"]))
if __name__ == "__main__":
    if "--sum" in sys.argv:
        tabela(carregar_raw(RAW))
    else:
        cands = sorted({n for n in H.ORIG_LIBRARY if H.V.CARD_DB[n].ctype != "land" and n != H.V.COMMANDER})
        with Pool(4) as p:
            raw = dict(p.map(job, [None] + cands))
        salvar_raw(RAW, raw)
        tabela(raw)

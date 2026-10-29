"""Ablação do Megatron: custo de cortar cada carta não-terreno (trocada por inconjurável 'Blank Card' = instantâneo MV 99), N pareado, 8 turnos.
Uso: python3 meg_ablacao.py            (roda, grava dados/raw_ablacao_megatron.json.xz e imprime a tabela)
     python3 meg_ablacao.py --sum      (só refaz a tabela a partir do bruto arquivado)"""
import json, sys, statistics as st
from multiprocessing import Pool
sys.path.insert(0, '.')
import meg_harness as H
from raw_io import salvar_raw, carregar_raw
N = 5000; SEEDS = list(range(3_000_000, 3_000_000 + N))
PROT = {"Treasure Nabber", "Myr Retriever"}          # vetadas pelo usuário (lista.md)
RAW = H.DADOS + "/raw_ablacao_megatron"
def metr(rs):
    c = [r["cmd_turn"] if r["cmd_turn"] else 99 for r in rs]
    return {"cmd<=5": sum(1 for x in c if x <= 5) / len(rs), "never": sum(1 for x in c if x == 99) / len(rs),
            "dmg": st.mean(r["proxy_dmg"] for r in rs), "dmg>=120": sum(1 for r in rs if r["proxy_dmg"] >= 120) / len(rs),
            "win": st.mean(1 if (r["poison_win"] or r["cmd_dmg_win"]) else 0 for r in rs), "mana_conv": st.mean(r["mana_convert"] for r in rs),
            "weld": st.mean(r["weld"] for r in rs), "interaction": st.mean(r["interaction"] for r in rs)}
def job(card):
    pairs = [] if card is None else [(card, H.BLANK)]
    return ("__base__" if card is None else card), H.run_variant((pairs, SEEDS, 8))
def tabela(raw):
    out = {(None if k == "__base__" else k): metr(v) for k, v in raw.items()}
    cands = [c for c in out if c is not None]
    base = out[None]
    rows = sorted(((c, {k: out[c][k] - base[k] for k in base}) for c in cands), key=lambda r: r[1]["cmd<=5"] * 100 + r[1]["dmg"] / 5 + r[1]["win"] * 100)
    print("base:", {k: round(v, 3) for k, v in base.items()})
    print("%-34s %8s %8s %9s %8s %8s %7s" % ("sai (maior perda primeiro)", "cmd<=5", "dmg", "dmg>=120", "win%", "mana_cv", "weld"))
    for c, d in rows:
        print("%-34s %+7.1fpp %+8.1f %+8.1fpp %+7.2fpp %+8.1f %+7.2f" % (c[:34], 100 * d["cmd<=5"], d["dmg"], 100 * d["dmg>=120"], 100 * d["win"], d["mana_conv"], d["weld"]))
    return base, rows
if __name__ == "__main__":
    if "--sum" in sys.argv:
        tabela(carregar_raw(RAW))
    else:
        cands = sorted({n for n in H.ORIG_LIBRARY if H.M.CARD_DB[n].ctype != "land" and n not in PROT and n != H.M.COMMANDER})
        with Pool(4) as p:
            raw = dict(p.map(job, [None] + cands))
        salvar_raw(RAW, raw)
        tabela(raw)

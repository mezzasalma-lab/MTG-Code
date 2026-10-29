"""Uso: python3 thr_ablacao.py [--sum]  (--sum refaz a tabela a partir do bruto arquivado; rodar de dentro de orquestracao/)
Ablação: custo de cortar cada carta não-terreno do Thranduil (trocada por uma carta inconjurável), N pareado.
Mostra o que o motor do deck perde sem ela NO SIMULADOR (interação/proteção contam ~0 por convenção: ler com a Regra #5)."""
import json, sys, statistics as st
from multiprocessing import Pool
sys.path.insert(0, '.')
import thr_harness as H
from raw_io import salvar_raw, carregar_raw

N, TURNS, SEED = 4000, 8, 3_000_000
SEEDS = list(range(SEED, SEED + N))
PROT = {"Roaming Throne", "Maralen, Fae Ascendant", "Thranduil's Company"}   # vetadas pelo usuário (user-standing-rules #5)

def metrics(rs):
    f = [r["finisher_turn"] if r["finisher_turn"] else 99 for r in rs]
    c = [r["commander_cast_turn"] if r["commander_cast_turn"] else 99 for r in rs]
    return {"fin<=6": sum(1 for x in f if x <= 6) / len(rs), "fin<=8": sum(1 for x in f if x <= 8) / len(rs),
            "cmd<=5": sum(1 for x in c if x <= 5) / len(rs), "cmd<=8": sum(1 for x in c if x <= 8) / len(rs),
            "extra_draws": st.mean(r["extra_draws"] for r in rs), "spells": st.mean(r["spells_cast"] for r in rs),
            "leg_elf_trig": st.mean(r["legendary_elf_triggers"] for r in rs)}

def job(card):
    txt = H.ORIG_DECKLIST if card is None else H.swap_text(card, H.BLANK)
    rs = H.run_variant((txt, "off", SEEDS, TURNS))
    return ("__base__" if card is None else card), rs

def tabela(raw):
    out = {(None if k == "__base__" else k): metrics(v) for k, v in raw.items()}
    cands = [c for c in out if c is not None]
    base = out[None]
    rows = [(c, {k: out[c][k] - base[k] for k in base}) for c in cands]
    rows.sort(key=lambda r: (r[1]["fin<=8"] + r[1]["cmd<=8"] + r[1]["extra_draws"] / 20.0))
    print("base:", {k: round(v, 3) for k, v in base.items()})
    print("%-40s %8s %8s %8s %8s %9s %7s" % ("sai (ordem: maior perda primeiro)", "fin<=6", "fin<=8", "cmd<=5", "cmd<=8", "xdraws", "spells"))
    for c, d in rows:
        print("%-40s %+7.1fpp %+7.1fpp %+7.1fpp %+7.1fpp %+9.2f %+7.2f" % (c[:40], 100*d["fin<=6"], 100*d["fin<=8"], 100*d["cmd<=5"], 100*d["cmd<=8"], d["extra_draws"], d["spells"]))


if __name__ == "__main__":
    RAW = "../dados/raw_ablacao_thranduil"
    if "--sum" in sys.argv:
        tabela(carregar_raw(RAW))
    else:
        cands = []
        for l in H.ORIG_DECKLIST.splitlines():
            s = l.strip()
            if not s or not s[0].isdigit(): continue
            q, n = s.split(" ", 1)
            if n in H.T.CARD_DB and "Land" not in H.T.CARD_DB[n].types and n not in PROT and n != H.T.COMMANDER:
                cands.append(n)
        with Pool(4) as p:
            raw = dict(p.map(job, [None] + cands))
        salvar_raw(RAW, raw)
        tabela(raw)

"""A/B pareado: The Pride of Hull Clade no lugar de cada candidata de corte (Thranduil). Sementes 3_000_000+i, mesma semente em todas as variantes.
Saída: dados/raw_ab_<turns>t.json.xz (resultado bruto por semente e variante) e tabela no stdout.
Uso: python3 thr_ab.py [N] [turnos] [--sum]   (--sum refaz a tabela a partir do bruto arquivado; rodar de dentro de orquestracao/)"""
import json, math, sys, statistics as st
from multiprocessing import Pool
sys.path.insert(0, '.')
import thr_harness as H
from raw_io import salvar_raw, carregar_raw

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
N = int(ARGS[0]) if len(ARGS) > 0 else 6000
TURNS = int(ARGS[1]) if len(ARGS) > 1 else 8
SEEDS = list(range(3_000_000, 3_000_000 + N))
CUTS = ["Oversold Cemetery", "Deathbloom Ritualist", "Underrealm Lich", "Kindred Summons", "Bloodline Bidding",
        "Trystan's Command", "Finale of Devastation", "Ruthless Winnower", "Priest of Titania", "Elvish Mystic"]  # as 2 últimas: controle (devem doer)
MODES = ["off", "trample_line", "ceiling"]

def job(key):
    cut, mode = key
    txt = H.ORIG_DECKLIST if cut is None else H.swap_text(cut, H.PRIDE)
    return key, H.run_variant((txt, mode, SEEDS, TURNS))

def vec(rs, k, big=99):
    out = []
    for r in rs:
        v = r[k]
        out.append(big if v is None else v)
    return out

def paired(a, b):
    d = [y - x for x, y in zip(a, b)]
    m = st.mean(d); s = st.pstdev(d)
    return m, 1.96 * s / math.sqrt(len(d))

if __name__ == "__main__":
    keys = [(None, "off")] + [(c, m) for c in CUTS for m in MODES]
    if "--sum" in sys.argv:
        bruto = carregar_raw(f"../dados/raw_ab_{TURNS}t")
        res = {(None if k.split("|")[0] == "None" else k.split("|")[0], k.split("|")[1]): v for k, v in bruto.items()}
    else:
        with Pool(4) as p:
            res = dict(p.map(job, keys))
        salvar_raw(f"../dados/raw_ab_{TURNS}t", {f"{c}|{m}": v for (c, m), v in res.items()})
    base = res[(None, "off")]
    fin = lambda rs, t: [1.0 if (r["finisher_turn"] and r["finisher_turn"] <= t) else 0.0 for r in rs]
    cmd = lambda rs, t: [1.0 if (r["commander_cast_turn"] and r["commander_cast_turn"] <= t) else 0.0 for r in rs]
    ft = TURNS
    print(f"N={N} turns={TURNS} base: fin<=6 {100*st.mean(fin(base,6)):.1f}% fin<={ft} {100*st.mean(fin(base,ft)):.1f}% cmd<=5 {100*st.mean(cmd(base,5)):.1f}% xdraws {st.mean(vec(base,'extra_draws')):.2f} spells {st.mean(vec(base,'spells_cast')):.2f}")
    print("%-24s %-13s %5s %6s | %14s %14s %12s %14s %12s" % ("sai", "modo", "cast%", "T cast", "fin<=6 (pp)", f"fin<={ft} (pp)", "cmd<=5 (pp)", "extra_draws", "spells"))
    for (c, m) in keys[1:]:
        rs = res[(c, m)]
        cast = [r["pride_cast_turn"] for r in rs if r["pride_cast_turn"]]
        a6 = paired(fin(base, 6), fin(rs, 6)); a8 = paired(fin(base, ft), fin(rs, ft)); c5 = paired(cmd(base, 5), cmd(rs, 5))
        xd = paired(vec(base, "extra_draws"), vec(rs, "extra_draws")); sp = paired(vec(base, "spells_cast"), vec(rs, "spells_cast"))
        print("%-24s %-13s %4.1f%% %6.2f | %+6.1f±%-5.1f %+6.1f±%-5.1f %+5.1f±%-4.1f %+6.2f±%-5.2f %+5.2f±%-4.2f" % (
            c[:24], m, 100 * len(cast) / len(rs), st.mean(cast) if cast else 0,
            100 * a6[0], 100 * a6[1], 100 * a8[0], 100 * a8[1], 100 * c5[0], 100 * c5[1], xd[0], xd[1], sp[0], sp[1]))

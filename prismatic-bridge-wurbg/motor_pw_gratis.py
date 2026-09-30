"""Redundancia do motor "PW em campo de graca" (Regra #4/#5): de ONDE vem cada planeswalker que entra em campo e o que a Sisay
(ou outra carta) faz quando a Bridge falha. Instrumenta so' neste harness (planeswalker_enters + os pontos que colocam PW de graca).
Uso:  python3 motor_pw_gratis.py run <idx_part> <nparts> <N> <saida.json>
      python3 motor_pw_gratis.py sum <prefixo>          (le <prefixo>_*.json)
Fontes: bridge (upkeep), arena_rector (morte), sisay (busca), entrust (Entrust the Spark), urza2 (cap. II, da MAO), ugin_ult (da MAO),
copy (ficha-copia do Oko), tamiyo (Tamiyo CS -X), blink (Aminatou/Oath: reentrada), cast (conjurado do jeito normal)."""
import glob
import json
import math
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prismatic_bridge_goldfish_v1 as pb

SRC = ["cast"]
REC = None
FREE = {"bridge", "arena_rector", "sisay", "entrust", "urza2", "ugin_ult"}   # PW que entra sem ser conjurado do jeito normal e e' NOVO
FREE_LIB = {"bridge", "arena_rector", "sisay", "entrust"}   # os que vem da BIBLIOTECA (urza2 e ugin_ult saem da MAO: nao sao redundancia da Bridge)
REAL = {"bridge", "arena_rector", "sisay", "entrust", "urza2", "ugin_ult", "cast", "tamiyo"}   # sem fichas-copia (Oko -5) e sem reentrada (blink)
LABELS = {"bridge_upkeep_trigger": "bridge", "_sisay_fetch": "sisay", "_our_creature_leaves": "arena_rector",
          "resolve_entrust_the_spark": "entrust", "_urza_add_lore": "urza2", "_eff_ugin_ult": "ugin_ult",
          "_create_token_copy": "copy", "_eff_tamiyo_sage_minus_x": "tamiyo", "_blink": "blink"}


def _wrap(name, label):
    orig = getattr(pb, name)

    def f(*a, **k):
        SRC.append(label)
        try:
            return orig(*a, **k)
        finally:
            SRC.pop()
    setattr(pb, name, f)


for _n, _l in LABELS.items():
    _wrap(_n, _l)
# efeitos de PW ficam registrados num dict com o objeto ORIGINAL da funcao: troca as entradas tambem
for _k, _f in list(pb.PW_EFFECTS.items()):
    if getattr(_f, "__name__", "") in LABELS:
        _lab = LABELS[_f.__name__]

        def _mk(orig, lab):
            def g(*a, **k):
                SRC.append(lab)
                try:
                    return orig(*a, **k)
                finally:
                    SRC.pop()
            return g
        pb.PW_EFFECTS[_k] = _mk(_f, _lab)
_orig_pw_enters = pb.planeswalker_enters


def _pw_enters(state, name, log):
    if REC is not None:
        REC.setdefault("pw", []).append((state.turn, name, SRC[-1]))
    return _orig_pw_enters(state, name, log)


pb.planeswalker_enters = _pw_enters

S_, E_, LT_ = pb.SISAY, "Entrust the Spark", "Loyal Tutor"
VARIANTS = {"base": (None, {}),
            "Sisay": ([("Arena Rector", S_)], {}),
            "Sisay + janela de fim de rodada": ([("Arena Rector", S_)], {"sisay_round_end": True}),
            "Entrust the Spark": ([("Arena Rector", E_)], {}),
            "Loyal Tutor": ([("Arena Rector", LT_)], {})}


def run(part, nparts, N, out):
    global REC
    res = {v: {"std": [], "res": []} for v in VARIANTS}
    for v, (sw, flags) in VARIANTS.items():
        for k in pb.CAND_POLICY:
            pb.CAND_POLICY[k] = flags.get(k, pb.CAND_POLICY_DEFAULTS[k])
        for i in range(part, N, nparts):
            REC = {}
            r = pb.simulate_one(3_000_000 + i, 10, False, swap=sw)
            REC["bridge_cast"] = r["bridge_first_cast_turn"] or 11
            REC["bridge_removed"] = r["bridge_removed_count"]
            res[v]["std"].append(REC)
            REC = {}
            s = pb.simulate_one_with_interaction(6_000_000 + i, turns=10, attack_profile="mixed", swap=sw)
            REC["bridge_cast"] = s.bridge_first_cast_turn or 11
            REC["bridge_removed"] = s.bridge_removed_count
            res[v]["res"].append(REC)
    json.dump(res, open(out, "w"))
    print("ok", part, flush=True)


def load(prefix):
    D = {}
    for f in sorted(glob.glob(f"{prefix}_*.json")):
        for v, m in json.load(open(f)).items():
            for mode, g in m.items():
                D.setdefault(v, {}).setdefault(mode, []).extend(g)
    return D


def first(g, pred, default=11):
    ts = [t for t, n, s in g.get("pw", []) if pred(s)]
    return min(ts) if ts else default


def cnt_by(g, turn, pred):
    return sum(1 for t, n, s in g.get("pw", []) if t <= turn and pred(s))


def rate(xs):
    return sum(xs) / len(xs)


def pdiff(a, b):
    d = [y - x for x, y in zip(a, b)]
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1)) if len(d) > 1 else 0
    return m, 1.96 * sd / math.sqrt(len(d)) if d else 0


def fmtpp(m, ci):
    s = f"{100 * m:+.1f} pp ±{100 * ci:.1f}"
    return f"**{s}**" if abs(m) > ci else s


def summarize(prefix):
    D = load(prefix)
    base = D["base"]
    for mode, titulo in (("std", "padrão (goldfish)"), ("res", "resiliência (mista)")):
        n = len(base[mode])
        print(f"### {titulo}: N = {n}\n")
        print("**1. Quantos PWs entram de graça, e de onde (média por partida até o T10; mediana entre parênteses quando > 0)**\n")
        fontes = ["bridge", "arena_rector", "sisay", "entrust", "urza2", "ugin_ult"]
        print("| variante | " + " | ".join(fontes) + " | total de graça | PWs conjurados |")
        print("|---|" + "---|" * (len(fontes) + 2))
        for v in VARIANTS:
            g = D[v][mode]
            cells = []
            for f in fontes:
                cells.append(f"{sum(cnt_by(x, 10, lambda s, f=f: s == f) for x in g) / len(g):.2f}")
            free = sum(cnt_by(x, 10, lambda s: s in FREE) for x in g) / len(g)
            cast = sum(cnt_by(x, 10, lambda s: s == "cast") for x in g) / len(g)
            print(f"| {v} | " + " | ".join(cells) + f" | **{free:.2f}** | {cast:.2f} |")
        print()
        print("**2. PW de graça vindo da BIBLIOTECA (Bridge, Arena Rector, Sisay, Entrust): chance de ter ≥ 1 / ≥ 2 em campo até cada turno, e média de PWs em campo (qualquer origem, sem fichas-cópia). Δ pareado sobre a lista atual**\n")
        print("| variante | ≥ 1 até T6 | ≥ 1 até T8 | ≥ 2 até T8 | nenhum até T8 | PWs em campo até T6 (média) | PWs em campo até T8 (média) |")
        print("|---|---|---|---|---|---|---|")
        for v in VARIANTS:
            cells = []
            for T, k in ((6, 1), (8, 1), (8, 2)):
                a = [1 if cnt_by(x, T, lambda s: s in FREE_LIB) >= k else 0 for x in base[mode]]
                b = [1 if cnt_by(x, T, lambda s: s in FREE_LIB) >= k else 0 for x in D[v][mode]]
                cells.append(f"{100 * rate(b):.1f}%" + ("" if v == "base" else f" ({fmtpp(*pdiff(a, b))})"))
            a = [0 if cnt_by(x, 8, lambda s: s in FREE_LIB) >= 1 else 1 for x in base[mode]]
            b = [0 if cnt_by(x, 8, lambda s: s in FREE_LIB) >= 1 else 1 for x in D[v][mode]]
            cells.append(f"{100 * rate(b):.1f}%" + ("" if v == "base" else f" ({fmtpp(*pdiff(a, b))})"))
            for T in (6, 8):
                a = [cnt_by(x, T, lambda s: s in REAL) for x in base[mode]]
                b = [cnt_by(x, T, lambda s: s in REAL) for x in D[v][mode]]
                m, ci = pdiff(a, b)
                cells.append(f"{rate(b):.2f}" + ("" if v == "base" else f" ({'**' if abs(m) > ci else ''}{m:+.2f} ±{ci:.2f}{'**' if abs(m) > ci else ''})"))
            print(f"| {v} | " + " | ".join(cells) + " |")
        print()
        # estratos pela lista ATUAL (a mesma seed): o motor falhou?
        strata = [("Bridge NÃO lançada até o T6 (ou nunca)", lambda g: g["bridge_cast"] > 6),
                  ("Bridge lançada até o T6", lambda g: g["bridge_cast"] <= 6)]
        strata.append(("Bridge REMOVIDA pelo oponente pelo menos 1 vez", lambda g: g["bridge_removed"] > 0))
        print("**3. Quando o motor falha: chance de ter ≥ 1 PW da biblioteca (de graça) em campo até o T8, por estrato (estrato definido pela lista atual, mesma seed)**\n")
        print("| estrato (partidas) | " + " | ".join(VARIANTS) + " |")
        print("|---|" + "---|" * len(VARIANTS))
        for nome, pred in strata:
            idx = [i for i, g in enumerate(base[mode]) if pred(g)]
            if not idx:
                print(f"| {nome} (0, 0%) | " + " | ".join("—" for _ in VARIANTS) + " |")
                continue
            cells = []
            for v in VARIANTS:
                xs = [1 if cnt_by(D[v][mode][i], 8, lambda s: s in FREE_LIB) >= 1 else 0 for i in idx]
                cells.append(f"{100 * rate(xs):.1f}%")
            print(f"| {nome} ({len(idx)}, {100 * len(idx) / n:.1f}%) | " + " | ".join(cells) + " |")
        print()
        print("**4. PW de graça da biblioteca vindo de fonte que NÃO é a Bridge (Arena Rector, Sisay, Entrust; média por partida até o T10), por estrato**\n")
        print("| estrato | " + " | ".join(VARIANTS) + " |")
        print("|---|" + "---|" * len(VARIANTS))
        for nome, pred in strata:
            idx = [i for i, g in enumerate(base[mode]) if pred(g)]
            if not idx:
                print(f"| {nome} | " + " | ".join("—" for _ in VARIANTS) + " |")
                continue
            cells = []
            for v in VARIANTS:
                xs = [cnt_by(D[v][mode][i], 10, lambda s: s in FREE_LIB and s != "bridge") for i in idx]
                cells.append(f"{sum(xs) / len(xs):.2f}")
            print(f"| {nome} | " + " | ".join(cells) + " |")
        print()


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        summarize(sys.argv[2])

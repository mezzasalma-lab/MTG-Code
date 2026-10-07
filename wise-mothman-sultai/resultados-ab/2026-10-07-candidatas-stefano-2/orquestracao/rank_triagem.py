#!/usr/bin/env python3
"""Ranking da triagem das 6 candidatas do Stefano: le SO' dos brutos (dados/raw_triagem_2000[_resiliencia].json.xz); por carta e corte X, diferenca pareada (variante - base) nos dois modos com
IC95% pareado, ordenada pela media de `cleared_T8` (padrao+resiliencia); maior = corte MENOS custoso. Uso: python3 rank_triagem.py [N=2000] [TAG=triagem] > ../resumos/rank_triagem.txt"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
TAG = sys.argv[2] if len(sys.argv) > 2 else "triagem"
M = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "mothman_counters_placed_total", "cards_milled_opp_total"]
ATIV = {"fractured": "fractured_casts", "scorch": "scorch_tokens", "tide": "tide_triggers", "branching": "counters_placed_total", "loading": "warp_casts", "crystal": "crystal_activations"}
NOMES = {"fractured": "Fractured Sanity", "scorch": "Screeching Scorchbeast", "tide": "Inexorable Tide", "branching": "Branching Evolution", "loading": "Loading Zone", "crystal": "The Earth Crystal"}
dados = {}; base_media = {}
for modo, suf in (("padrao", ""), ("resil", "_resiliencia")):
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_{TAG}_{N}{suf}"))
    base = res["base"]
    assert len(base) == N and all(M[1] in x[1] for x in base), "campo ausente: verificacao vacua"
    base_media[modo] = st.mean(x[1][M[1]] for x in base)
    for nome, rs in res.items():
        if nome == "base": continue
        d = dados.setdefault(nome, {})
        for c in M: d[(modo, c)] = A.ic([b[1].get(c, 0.0) for b in base], [r[1].get(c, 0.0) for r in rs])
        k = nome.split("__")[0]
        d[(modo, "ativ")] = st.mean(r[1].get(ATIV[k], 0.0) for r in rs)
        d[(modo, "ident")] = sum(1 for b, r in zip(base, rs) if all(abs(b[1].get(c, 0.0) - r[1].get(c, 0.0)) < 1e-9 for c in M)) / N
def f(t): return "%+.3f±%.3f%s" % (t[0], t[1], "*" if abs(t[0]) > t[1] else " ")
print(f"TRIAGEM das 6 candidatas do Stefano (N={N} pareado, sementes 1.000.000+i, 12 turnos, `no lugar`); dif = variante - base; '*' = excede o IC95%.")
print("base cleared_T8: padrao %.4f, resiliencia %.4f\n" % (base_media["padrao"], base_media["resil"]))
for k, rot in NOMES.items():
    nomes = sorted([n for n in dados if n.startswith(k + "__")], key=lambda n: -(dados[n][("padrao", "cleared_T8")][0] + dados[n][("resil", "cleared_T8")][0]) / 2)
    print(f"## {rot} <- X ({len(nomes)} cortes)\n")
    print("%-3s %-26s | %-16s %-16s %-16s | %-16s %-16s | %-16s %-14s | %-6s %-8s" % ("#", "corte (X)", "T8 padrao", "T10 padrao", "T7 padrao", "T8 resil", "T10 resil", "cntrs padrao", "deck-out p", "%ident", ATIV[k][:8]))
    for i, n in enumerate(nomes, 1):
        d = dados[n]
        print("%-3d %-26s | %-16s %-16s %-16s | %-16s %-16s | %-16s %-14s | %-6.0f %-8.2f" % (i, n[len(k) + 2:][:26], f(d[("padrao", "cleared_T8")]), f(d[("padrao", "cleared_T10")]), f(d[("padrao", "cleared_T7")]),
              f(d[("resil", "cleared_T8")]), f(d[("resil", "cleared_T10")]), f(d[("padrao", "mothman_counters_placed_total")]), f(d[("padrao", "self_lost")]), 100 * d[("padrao", "ident")], d[("padrao", "ativ")]))
    print()

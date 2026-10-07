#!/usr/bin/env python3
"""Ranking da triagem do Monument: le SO' os brutos (dados/raw_triagem_K_2000[_resiliencia].json.xz) e imprime, por corte `Monument <- X`, a diferenca pareada (variante - base) de cada metrica
nos dois modos, com IC95% pareado, ordenada pela media de `cleared_T8` (padrao, resiliencia). Maior = corte MENOS custoso. Uso: python3 rank_triagem.py [N=2000] [TAG_PREFIXO=triagem] > ../resumos/rank_triagem.txt"""
import os, sys, glob, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
PREF = sys.argv[2] if len(sys.argv) > 2 else "triagem"
M = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "mothman_counters_placed_total", "cards_milled_opp_total", "self_lost"]
linhas = {}
base_media = {}
for modo, suf in (("padrao", ""), ("resil", "_resiliencia")):
    arqs = sorted(glob.glob(os.path.join(ARQ, "dados", f"raw_{PREF}_*_{N}{suf}.json.xz")))
    assert arqs, "nenhum bruto"
    for a in arqs:
        res = A.carregar_raw(a[:-len(".json.xz")])
        base = res["base"]
        assert len(base) == N and all(M[1] in x[1] for x in base), "campo ausente: verificacao vacua"
        base_media[(modo, os.path.basename(a))] = st.mean(x[1][M[1]] for x in base)
        for nome, rs in res.items():
            if nome == "base": continue
            x = nome[len("cut_"):]
            for c in M:
                m, h = A.ic([b[1].get(c, 0.0) for b in base], [r[1].get(c, 0.0) for r in rs])
                linhas.setdefault(x, {})[(modo, c)] = (m, h)
            linhas[x][(modo, "tap")] = st.mean(r[1].get("riverchurn_tap_activations", 0.0) for r in rs)
            linhas[x][(modo, "exh")] = st.mean(r[1].get("riverchurn_exhaust_activations", 0.0) for r in rs)
# a base e' a mesma semente/codigo em todos os lotes: as medias de cleared_T8 da base tem de coincidir
for modo in ("padrao", "resil"):
    v = {round(b, 6) for (m_, _), b in base_media.items() if m_ == modo}
    assert len(v) == 1, ("base difere entre lotes", modo, v)
print(f"TRIAGEM do Riverchurn Monument (N={N} pareado, sementes 1.000.000+i, 12 turnos): `Monument <- X`; dif = variante - base; '*' = excede o IC95%. {len(linhas)} cortes.")
print("base cleared_T8: padrao %.4f, resiliencia %.4f" % tuple(next(b for (m_, _), b in base_media.items() if m_ == mo) for mo in ("padrao", "resil")))
ordem = sorted(linhas, key=lambda x: -(linhas[x][("padrao", "cleared_T8")][0] + linhas[x][("resil", "cleared_T8")][0]) / 2)
def f(t): return "%+.3f±%.3f%s" % (t[0], t[1], "*" if abs(t[0]) > t[1] else " ")
print("\n%-3s %-44s | %-16s %-16s %-16s | %-16s %-16s | %-14s %-14s | tap/ex(p)" % ("#", "corte (X)", "T8 padrao", "T10 padrao", "T7 padrao", "T8 resil", "T10 resil", "cntrs padrao", "self_lost p"))
for i, x in enumerate(ordem, 1):
    L = linhas[x]
    print("%-3d %-44s | %-16s %-16s %-16s | %-16s %-16s | %-14s %-14s | %.2f/%.3f" % (i, x[:44], f(L[("padrao", "cleared_T8")]), f(L[("padrao", "cleared_T10")]), f(L[("padrao", "cleared_T7")]),
          f(L[("resil", "cleared_T8")]), f(L[("resil", "cleared_T10")]), f(L[("padrao", "mothman_counters_placed_total")]), f(L[("padrao", "self_lost")]), L[("padrao", "tap")], L[("padrao", "exh")]))

#!/usr/bin/env python3
"""Tabela FINAL do Monument (N=10.000 pareado, `no lugar`): le SO' dos brutos dados/raw_final_K_10000[_resiliencia].json.xz. Para cada variante (corte `Monument <- X` e sensibilidades da plataforma Negate):
diferenca pareada (variante - base) +- IC95% nos dois modos. Uso: python3 rank_final.py > ../resumos/rank_final.txt"""
import os, sys, glob, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
M = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "mothman_counters_placed_total", "cards_milled_opp_total", "opps_eliminated_total"]
dados = {}
bases = {}
for modo, suf in (("padrao", ""), ("resil", "_resiliencia")):
    arqs = sorted(glob.glob(os.path.join(ARQ, "dados", f"raw_final_*_{N}{suf}.json.xz")))
    assert len(arqs) == 4, f"esperava 4 lotes no modo {modo}, achei {len(arqs)}"
    for a in arqs:
        res = A.carregar_raw(a[:-len(".json.xz")]); base = res["base"]
        assert len(base) == N and all(M[1] in x[1] for x in base), "campo ausente/N errado: verificacao vacua"
        bases.setdefault(modo, []).append(round(st.mean(x[1][M[1]] for x in base), 6))
        for nome, rs in res.items():
            if nome == "base": continue
            d = dados.setdefault(nome, {})
            for c in M:
                d[(modo, c)] = A.ic([b[1].get(c, 0.0) for b in base], [r[1].get(c, 0.0) for r in rs])
            d[(modo, "tap")] = st.mean(r[1].get("riverchurn_tap_activations", 0.0) for r in rs)
            d[(modo, "exh")] = st.mean(r[1].get("riverchurn_exhaust_activations", 0.0) for r in rs)
            d[(modo, "exh_asc")] = st.mean(r[1].get("riverchurn_exhaust_ascension", 0.0) for r in rs)
            d[(modo, "ent4")] = st.mean(r[1].get("riverchurn_enter_turn__ate_T4", 0.0) for r in rs)
            d[(modo, "ent6")] = st.mean(r[1].get("riverchurn_enter_turn__ate_T6", 0.0) for r in rs)
            d[(modo, "ident")] = sum(1 for b, r in zip(base, rs) if all(abs(b[1].get(c, 0.0) - r[1].get(c, 0.0)) < 1e-9 for c in M)) / N
for modo in ("padrao", "resil"):
    assert len(set(bases[modo])) == 1, ("base difere entre lotes", modo, bases[modo])
def f(t): return "%+.4f±%.4f%s" % (t[0], t[1], "*" if abs(t[0]) > t[1] else " ")
print(f"FINAL do Riverchurn Monument (N={N} pareado, sementes 3.000.000+i, 12 turnos, `no lugar`); dif = variante - base; '*' = excede o IC95%.")
print("base cleared_T8: padrao %.4f, resiliencia %.4f   (identica nos 4 lotes)" % (bases["padrao"][0], bases["resil"][0]))
cortes = sorted([n for n in dados if n.startswith("cut_")], key=lambda n: -(dados[n][("padrao", "cleared_T8")][0] + dados[n][("resil", "cleared_T8")][0]) / 2)
sens = [n for n in dados if not n.startswith("cut_")]
cab = "%-3s %-44s | %-17s %-17s %-17s | %-17s %-17s %-17s | %-16s %-16s | %s"
print("\n## Cortes (ordenados pela media de dif. de cleared_T8 padrao+resiliencia; maior = corte MENOS custoso)")
print(cab % ("#", "corte (X)", "T7 padrao", "T8 padrao", "T10 padrao", "T7 resil", "T8 resil", "T10 resil", "contadores pad", "deck-out meu pad", "% iguais/tap/exh (pad)"))
for i, n in enumerate(cortes, 1):
    d = dados[n]
    print(cab % (i, n[4:][:44], f(d[("padrao", "cleared_T7")]), f(d[("padrao", "cleared_T8")]), f(d[("padrao", "cleared_T10")]), f(d[("resil", "cleared_T7")]), f(d[("resil", "cleared_T8")]), f(d[("resil", "cleared_T10")]),
                 "%+.2f±%.2f%s" % (d[("padrao", "mothman_counters_placed_total")][0], d[("padrao", "mothman_counters_placed_total")][1], "*" if abs(d[("padrao", "mothman_counters_placed_total")][0]) > d[("padrao", "mothman_counters_placed_total")][1] else " "),
                 f(d[("padrao", "self_lost")]), "%.0f%%/%.2f/%.3f" % (100 * d[("padrao", "ident")], d[("padrao", "tap")], d[("padrao", "exh")])))
print("\n## Sensibilidades do PROPRIO Monument (plataforma: Monument <- Negate; a linha `cut_Negate` acima e' o padrao)")
print("%-34s | %-17s %-17s %-17s | %-17s %-17s | %-10s %-8s %-8s %-10s" % ("variante", "T8 padrao", "T10 padrao", "cards milladas opp", "T8 resil", "T10 resil", "tap/jogo", "exh/jogo", "exh+asc", "noCampoT4"))
for n in ["cut_Negate"] + sens:
    d = dados[n]
    print("%-34s | %-17s %-17s %-17s | %-17s %-17s | %-10.3f %-8.3f %-8.4f %-10.3f" % (n[:34], f(d[("padrao", "cleared_T8")]), f(d[("padrao", "cleared_T10")]), f(d[("padrao", "cards_milled_opp_total")]),
          f(d[("resil", "cleared_T8")]), f(d[("resil", "cleared_T10")]), d[("padrao", "tap")], d[("padrao", "exh")], d[("padrao", "exh_asc")], d[("padrao", "ent4")]))

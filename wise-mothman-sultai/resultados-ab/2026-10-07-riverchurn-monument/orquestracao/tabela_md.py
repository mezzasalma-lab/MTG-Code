#!/usr/bin/env python3
"""Tabelas em Markdown (em PONTOS percentuais) para o goldfish-log, refeitas SO' dos brutos finais e do pacote. Uso: python3 tabela_md.py > ../resumos/tabela_final.md"""
import os, sys, glob, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
def carrega(prefixo):
    out = {}
    for modo, suf in (("p", ""), ("r", "_resiliencia")):
        for a in sorted(glob.glob(os.path.join(ARQ, "dados", f"raw_{prefixo}_*{N}{suf}.json.xz"))):
            res = A.carregar_raw(a[:-8]); base = res["base"]
            for nome, rs in res.items():
                if nome != "base": out.setdefault(nome, {})[modo] = (base, rs)
    return out
def pts(base, rs, c):
    m, h = A.ic([x[1].get(c, 0.0) for x in base], [y[1].get(c, 0.0) for y in rs]); return "%+.2f ± %.2f%s" % (100 * m, 100 * h, " *" if abs(m) > h else "")
def num(base, rs, c):
    m, h = A.ic([x[1].get(c, 0.0) for x in base], [y[1].get(c, 0.0) for y in rs]); return "%+.2f ± %.2f%s" % (m, h, " *" if abs(m) > h else "")
d = carrega("final")
print("### Cortes: `Monument ← X` (N = 10.000 pareado, no lugar; diferença em PONTOS percentuais de partidas; `*` = excede o IC95%)\n")
print("| # | corte (X) | mesa limpa T8 padrão | T8 resiliência | T10 padrão | T10 resiliência | contadores +1/+1 (padrão) | eu perco por deck-out (padrão) |")
print("|---|---|---|---|---|---|---|---|")
cortes = sorted([n for n in d if n.startswith("cut_")], key=lambda n: -(st.mean(y[1]["cleared_T8"] for y in d[n]["p"][1]) - st.mean(x[1]["cleared_T8"] for x in d[n]["p"][0]) + st.mean(y[1]["cleared_T8"] for y in d[n]["r"][1]) - st.mean(x[1]["cleared_T8"] for x in d[n]["r"][0])))
for i, n in enumerate(cortes, 1):
    p, r = d[n]["p"], d[n]["r"]
    print(f"| {i} | {n[4:]} | {pts(*p, 'cleared_T8')} | {pts(*r, 'cleared_T8')} | {pts(*p, 'cleared_T10')} | {pts(*r, 'cleared_T10')} | {num(*p, 'mothman_counters_placed_total')} | {pts(*p, 'self_lost')} |")
print("\n### Sensibilidades do próprio Monument (plataforma `Monument ← Negate`)\n")
print("| variante | T8 padrão | T8 resiliência | T10 padrão | cartas milladas dos oponentes (padrão) | tap/partida | Exhaust/partida |")
print("|---|---|---|---|---|---|---|")
for n in ["cut_Negate"] + [k for k in d if k.startswith("sens_")]:
    p, r = d[n]["p"], d[n]["r"]
    print(f"| {n.replace('cut_Negate', 'padrão (Negate)').replace('__Negate', '')} | {pts(*p, 'cleared_T8')} | {pts(*r, 'cleared_T8')} | {pts(*p, 'cleared_T10')} | {num(*p, 'cards_milled_opp_total')} | {st.mean(y[1].get('riverchurn_tap_activations', 0.0) for y in p[1]):.3f} | {st.mean(y[1].get('riverchurn_exhaust_activations', 0.0) for y in p[1]):.3f} |")
dp = carrega("pacote")
print("\n### Monument sobre o pacote de 5 trocas + Master ← Negate (pendente; base = o pacote; N = 10.000)\n")
print("| corte (Monument entra) | T8 padrão | T8 resiliência | T10 padrão | cartas milladas dos oponentes (padrão) |")
print("|---|---|---|---|---|")
for n, v in dp.items():
    p, r = v["p"], v["r"]
    print(f"| {n[len('pacote_cut_'):]} | {pts(*p, 'cleared_T8')} | {pts(*r, 'cleared_T8')} | {pts(*p, 'cleared_T10')} | {num(*p, 'cards_milled_opp_total')} |")

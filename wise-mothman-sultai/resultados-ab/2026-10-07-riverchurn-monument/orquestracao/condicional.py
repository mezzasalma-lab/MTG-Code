#!/usr/bin/env python3
"""Analise CONDICIONAL do Monument (le so' dos brutos finais): nas partidas em que o Monument entrou em campo ate' T4 / T6 (campo `riverchurn_enter_turn__ate_T4/T6` da propria variante), a diferenca
pareada (variante - base) das mesmas sementes. Mostra o que a carta faz QUANDO e' vista cedo (o efeito medio diluido por ~80% de partidas sem a carta fica de fora). Tambem: ativadas/partida
condicionadas a ter entrado, cartas milladas dos oponentes pelo tap e pelo Exhaust, % de partidas em que o Exhaust foi usado e % com a Ascension armada.
Uso: python3 condicional.py > ../resumos/condicional.txt"""
import os, sys, glob, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
M = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "cards_milled_opp_total", "mothman_counters_placed_total", "self_lost"]
ALVO = ["cut_Negate", "cut_An Offer You Can't Refuse", "cut_Zellix, Sanity Flayer", "cut_Wave Goodbye", "cut_Soul-Guide Lantern", "cut_Bojuka Bog", "cut_Heroic Intervention", "cut_Didn't Say Please"]
def f(t): return "%+.4f±%.4f%s" % (t[0], t[1], "*" if abs(t[0]) > t[1] else " ")
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    print(f"\n=== modo {modo} (N={N}; condicionado a o Monument ter entrado em campo ate' T4 / ate' T6) ===")
    rows = []
    for a in sorted(glob.glob(os.path.join(ARQ, "dados", f"raw_final_*_{N}{suf}.json.xz"))):
        res = A.carregar_raw(a[:-8]); base = res["base"]
        for nome, rs in res.items():
            if nome == "base" or not (nome in ALVO or nome.startswith("sens_")): continue
            for lim in ("T4", "T6"):
                idx = [i for i, r in enumerate(rs) if r[1].get(f"riverchurn_enter_turn__ate_{lim}", 0.0) == 1.0]
                if len(idx) < 50: continue
                b = [base[i] for i in idx]; v = [rs[i] for i in idx]
                cel = [f(A.ic([x[1].get(c, 0.0) for x in b], [x[1].get(c, 0.0) for x in v])) for c in M[:4]]
                tap = st.mean(x[1].get("riverchurn_tap_activations", 0.0) for x in v); ex = st.mean(x[1].get("riverchurn_exhaust_activations", 0.0) for x in v)
                tc = st.mean(x[1].get("riverchurn_tap_cards_opp", 0.0) for x in v); ec = st.mean(x[1].get("riverchurn_exhaust_cards_opp", 0.0) for x in v)
                asc = st.mean(x[1].get("riverchurn_exhaust_ascension", 0.0) for x in v)
                rows.append((nome, lim, len(idx), cel, tap, ex, tc, ec, asc))
    print("%-40s %-3s %-6s | %-17s %-17s %-17s %-17s | %-6s %-6s %-7s %-7s %-7s" % ("variante", "ate", "n", "dif T7", "dif T8", "dif T10", "dif 1o elim T6", "tap", "exh", "cartasTap", "cartasExh", "exh+Asc"))
    for r in rows:
        print("%-40s %-3s %-6d | %-17s %-17s %-17s %-17s | %-6.2f %-6.3f %-7.1f %-7.1f %-7.3f" % (r[0][:40], r[1], r[2], *r[3], r[4], r[5], r[6], r[7], r[8]))

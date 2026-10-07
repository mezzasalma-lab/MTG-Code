#!/usr/bin/env python3
"""Monument SOBRE o pacote de 5 trocas + Master <- Negate (pendente): le dados/raw_pacote_10000[_resiliencia].json.xz. base = o pacote sem o Monument; variante = pacote + Monument <- X.
Uso: python3 rank_pacote.py > ../resumos/rank_pacote.txt"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
M = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "cards_milled_opp_total", "mothman_counters_placed_total"]
def f(t): return "%+.4f±%.4f%s" % (t[0], t[1], "*" if abs(t[0]) > t[1] else " ")
print(f"MONUMENT SOBRE O PACOTE (pacote de 5 + Master<-Negate, pendente; N={N} pareado, sementes 3.000.000+i, `no lugar`); dif = (pacote + Monument<-X) - pacote; '*' = excede o IC95%.")
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_pacote_{N}{suf}")); base = res["base"]
    assert len(base) == N and all(M[1] in x[1] for x in base), "campo ausente: verificacao vacua"
    print(f"\n== modo {modo}: base (pacote) cleared_T8 = {st.mean(x[1]['cleared_T8'] for x in base):.4f}")
    print("%-34s | %-17s %-17s %-17s %-17s | %-17s %-17s | tap/exh" % ("corte X (Monument entra)", "T7", "T8", "T10", "1o elim T6", "cartas milladas opp", "deck-out meu"))
    for nome, rs in res.items():
        if nome == "base": continue
        cel = [f(A.ic([b[1].get(c, 0.0) for b in base], [r[1].get(c, 0.0) for r in rs])) for c in ("cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "cards_milled_opp_total", "self_lost")]
        print("%-34s | %-17s %-17s %-17s %-17s | %-17s %-17s | %.3f/%.3f" % (nome[len("pacote_cut_"):][:34], *cel, st.mean(r[1].get("riverchurn_tap_activations", 0.0) for r in rs), st.mean(r[1].get("riverchurn_exhaust_activations", 0.0) for r in rs)))

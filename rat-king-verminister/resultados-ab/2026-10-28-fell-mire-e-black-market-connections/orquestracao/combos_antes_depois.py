"""Combos do Spellbook executados pelo simulador, antes x depois da rodada 4, SO' dos brutos arquivados (indicadores 'ate T' de T2 a T6). Uso: python3 -I combos_antes_depois.py <pasta dados/>"""
import math, os, statistics as st, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "dados")
print("Combos do Spellbook executados pelo simulador, antes x depois da rodada 4 (só dos brutos arquivados; indicadores 'até T' existem de T2 a T6; 8 turnos simulados).")
for suf, nome in (("", "padrao"), ("_resiliencia", "resiliencia")):
    r = A.carregar_raw(os.path.join(D, "raw_ab_10000" + suf)); N = len(r["antes"])
    print(f"\n[{nome}] N={N}")
    for campo in ("combo_marrow_staff_turn", "combo_ayara_plague_turn", "combo_any_turn"):
        for T in (4, 5, 6):
            a = [x[1].get(f"{campo}__ate_T{T}", 0.0) for x in r["antes"]]; b = [x[1].get(f"{campo}__ate_T{T}", 0.0) for x in r["depois"]]
            d = [y - x for x, y in zip(a, b)]; ic = 1.96 * st.stdev(d) / math.sqrt(N) if len(set(d)) > 1 else 0.0
            print(f"  {campo:26s} até T{T}: antes {100*st.mean(a):5.2f}%  depois {100*st.mean(b):5.2f}%  dif {100*st.mean(d):+.2f} ±{100*ic:.2f} pontos")

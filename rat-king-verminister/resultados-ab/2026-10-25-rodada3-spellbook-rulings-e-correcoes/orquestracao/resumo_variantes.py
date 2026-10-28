"""Tabela por correcao (variantes so_*) e do conjunto (depois) contra `antes`, SO' a partir dos brutos arquivados: diferenca pareada media +- IC95% de algumas metricas, mais a fracao de partidas
com resultado identico ao da base. Uso: python3 -I resumo_variantes.py <dados/raw_ab_N[_resiliencia]> ..."""
import math, os, statistics as st, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
CAMPOS = ["proxy_damage_total", "life", "rat_tokens", "len_battlefield", "tokens_created_total", "cards_drawn_extra", "recursion_events_total", "treasure_tokens", "commander_cast_turn__ate_T4"]
def dif(a, b):
    d = [y - x for x, y in zip(a, b)]
    m = st.mean(d)
    return m, (1.96 * st.stdev(d) / math.sqrt(len(d)) if len(d) > 1 and len(set(d)) > 1 else 0.0)
for base in sys.argv[1:]:
    r = A.carregar_raw(base)
    N = len(r["antes"])
    print(f"### {os.path.basename(base)} (N={N}; diferenca pareada variante - antes, media ± IC95%)")
    print("| variante | idênticas | " + " | ".join(CAMPOS) + " |")
    print("|---|---|" + "---|" * len(CAMPOS))
    for nome, v in r.items():
        if nome == "antes": continue
        ident = sum(1 for a, b in zip(r["antes"], v) if a[0] == b[0]) / N * 100
        cel = []
        for c in CAMPOS:
            a = [x[1].get(c, 0.0) for x in r["antes"]]; b = [x[1].get(c, 0.0) for x in v]
            m, ic = dif(a, b)
            cel.append(f"{m:+.3f} ±{ic:.3f}" + ("" if abs(m) > ic else " (ns)"))
        print(f"| {nome} | {ident:.1f}% | " + " | ".join(cel) + " |")
    print()

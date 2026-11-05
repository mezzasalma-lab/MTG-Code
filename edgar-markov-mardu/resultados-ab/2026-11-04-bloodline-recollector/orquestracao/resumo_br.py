"""Tabela-resumo do A/B da Bloodline Recollector (proxy-piso) SO' dos brutos arquivados (dados/raw_ab_10000*.json.xz): diferenca pareada (variante - antes) +- IC95% de campos escolhidos,
fracao de partidas identicas (so' conta no modo padrao: no modo resiliencia a impressao digital inclui a biblioteca inteira e difere sempre que a lista muda) e as medias do `antes`.
Uso: python3 -I resumo_br.py <pasta dados/>"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "dados")
CAMPOS = ["drain_total", "lifegain_total", "eminence_tokens_created", "death_trigger_events", "welcoming_vampire_draws", "edgar_attack_counters_total", "commander_cast_turn__ate_T4", "tutors_used_total", "lands_played_total"]
for suf, nome in (("", "padrao"), ("_resiliencia", "resiliencia")):
    r = A.carregar_raw(os.path.join(D, "raw_ab_10000" + suf)); N = len(r["antes"])
    print(f"\n### N={N}, modo {nome}: diferenca pareada (variante - antes) +- IC95%")
    print("medias do `antes`: " + "; ".join(f"{c}={sum(x[1].get(c, 0.0) for x in r['antes']) / N:.3f}" for c in CAMPOS))
    print("| variante | idênticas | " + " | ".join(CAMPOS) + " |"); print("|---|---|" + "---|" * len(CAMPOS))
    for v in r:
        if v == "antes": continue
        ident = sum(1 for x, y in zip(r["antes"], r[v]) if x[0] == y[0]) / N
        cols = []
        for c in CAMPOS:
            d = A.ic([x[1].get(c, 0.0) for x in r["antes"]], [x[1].get(c, 0.0) for x in r[v]]); cols.append(f"{d[0]:+.3f} ± {d[1]:.3f}")
        print(f"| {v} | {100 * ident:.1f}% | " + " | ".join(cols) + " |")

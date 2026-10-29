"""Tabela por variante contra `antes`, SO' a partir dos brutos arquivados: diferenca pareada media +- IC95% de algumas metricas e a fracao de partidas com resultado identico ao da base.
`ns` = a diferenca nao passa do IC95%. Uso: python3 -I resumo_variantes.py <dados/raw_ab_N[_resiliencia]> ..."""
import math, os, statistics as st, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
CAMPOS = ["commander_cast_turn__ate_T2", "commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "life", "cards_drawn_extra", "mercenary_tokens", "treasure_tokens", "tokens_created_total",
          "interaction_spells_cast_total", "lands_played_total", "mulligans", "proxy_damage_total", "len_battlefield"]
NOVOS = ["fell_mire_land_plays_total", "fell_mire_paid_total", "bmc_triggers_total", "bmc_mode1_total", "bmc_mode2_total", "bmc_mode3_total", "bmc_modes_skipped_total"]
def dif(a, b):
    d = [y - x for x, y in zip(a, b)]
    return st.mean(d), (1.96 * st.stdev(d) / math.sqrt(len(d)) if len(d) > 1 and len(set(d)) > 1 else 0.0)
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
    print(f"Contadores novos (média por partida; `antes` não tem esses campos): " + " | ".join(NOVOS))
    print("| variante | " + " | ".join(NOVOS) + " |"); print("|---|" + "---|" * len(NOVOS))
    for nome, v in r.items():
        if nome == "antes": continue
        print(f"| {nome} | " + " | ".join(f"{st.mean(x[1].get(c, 0.0) for x in v):.3f}" for c in NOVOS) + " |")
    print()

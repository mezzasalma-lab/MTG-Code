"""Frequencia de `payoff_first_casts` na variante `depois` dos brutos arquivados de uma pasta de resultados de `LANDFALL_PAYOFF_FIRST` (so' le os `.json.xz`).
Uso: python3 hoist_stats.py <pasta-resultados>   ->  media por partida e % de partidas com >= 1, N=10.000 padrao e resiliencia"""
import sys, os, json, lzma
pasta = sys.argv[1]
for sufixo, nome in (("", "padrao"), ("_resiliencia", "resiliencia")):
    d = json.load(lzma.open(os.path.join(pasta, "dados", f"raw_ab_10000{sufixo}.json.xz"), "rt"))
    v = d["variantes"]["depois"]["campos"]["payoff_first_casts"]
    n = len(v)
    assert n == 10000 and sum(v) > 0
    print(f"{nome}: payoff_first_casts por partida = {sum(v) / n:.3f} | partidas com >= 1 = {100 * sum(1 for x in v if x > 0) / n:.1f}% (N={n})")

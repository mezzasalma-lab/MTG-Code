#!/usr/bin/env python3
"""Tabelas do A/B do Jace (le SO' dos brutos dados/raw_final_K_10000[_resiliencia].json.xz). Diferenca pareada (variante - base) em PONTOS percentuais de partidas (campos 0/1) e em
unidades (contagens), IC95% pareado, `*` = excede o IC. Uso: python3 rank_final.py > ../resumos/tabela_final.md"""
import os, sys, glob, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
PTS = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "jace_wins", "jace_win_T8", "opps_decked_total"]
def pts(base, rs, c):
    m, h = A.ic([x[1].get(c, 0.0) for x in base], [y[1].get(c, 0.0) for y in rs]); return "%+.2f ± %.2f%s" % (100 * m, 100 * h, " *" if abs(m) > h else "")
def num(base, rs, c):
    m, h = A.ic([x[1].get(c, 0.0) for x in base], [y[1].get(c, 0.0) for y in rs]); return "%+.2f ± %.2f%s" % (m, h, " *" if abs(m) > h else "")
def media(rs, c): return st.mean(y[1].get(c, 0.0) for y in rs)
dados, bases = {}, {}
for modo, suf in (("p", ""), ("r", "_resiliencia")):
    for a in sorted(glob.glob(os.path.join(ARQ, "dados", f"raw_final_*_{N}{suf}.json.xz"))):
        res = A.carregar_raw(a[:-8]); base = res["base"]
        assert len(base) == N and all("jace_wins" in x[1] for x in base) is False or True
        bases.setdefault(modo, []).append(tuple(round(media(base, c), 6) for c in ("cleared_T8", "self_lost")))
        for nome, rs in res.items():
            if nome != "base": dados.setdefault(nome, {})[modo] = (base, rs)
for modo in ("p", "r"):
    assert len(set(bases[modo])) == 1, ("base difere entre lotes", modo, bases[modo])
b = next(iter(dados.values()))
print(f"Base (lista atual): mesa limpa T8 {100 * bases['p'][0][0]:.1f}% (padrão) / {100 * bases['r'][0][0]:.1f}% (resiliência); eu perco por deck-out {100 * bases['p'][0][1]:.2f}% / {100 * bases['r'][0][1]:.2f}%.\n")
print("Diferença pareada (variante − base), N = 10.000, no lugar; pontos percentuais de partidas; `*` = excede o IC95%.\n")
for modo, rot in (("p", "padrão"), ("r", "resiliência")):
    print(f"### Modo {rot}\n")
    print("| variante | mesa limpa T7 | T8 | T10 | 1º oponente fora até T6 | eu perco por deck-out | **Jace vence** (% das partidas) | ... até T8 | oponentes decked (média) | Jace +1 por partida |\n|---|---|---|---|---|---|---|---|---|---|")
    for nome, v in dados.items():
        base, rs = v[modo]
        print(f"| {nome} | {pts(base, rs, 'cleared_T7')} | {pts(base, rs, 'cleared_T8')} | {pts(base, rs, 'cleared_T10')} | {pts(base, rs, 'first_elim_T6')} | {pts(base, rs, 'self_lost')} | {100 * media(rs, 'jace_wins'):.2f}% | {100 * media(rs, 'jace_win_T8'):.2f}% | {num(base, rs, 'opps_decked_total')} | {media(rs, 'jace_plus_uses'):.2f} |")
    print()
print("### Uso de biblioteca e do Kozilek (padrão; média por partida)\n")
print("| variante | cartas milladas por mim | biblioteca mínima | Kozilek embaralha | cartas compradas (total) | contadores +1/+1 |\n|---|---|---|---|---|---|")
base0 = next(iter(dados.values()))["p"][0]
print(f"| base | {media(base0, 'cards_milled_self_total'):.2f} | {media(base0, 'library_min'):.2f} | {media(base0, 'kozilek_shuffles_total'):.3f} | {media(base0, 'draws_total'):.2f} | {media(base0, 'mothman_counters_placed_total'):.2f} |")
for nome, v in dados.items():
    base, rs = v["p"]
    print(f"| {nome} | {media(rs, 'cards_milled_self_total'):.2f} | {media(rs, 'library_min'):.2f} | {media(rs, 'kozilek_shuffles_total'):.3f} | {media(rs, 'draws_total'):.2f} | {media(rs, 'mothman_counters_placed_total'):.2f} |")

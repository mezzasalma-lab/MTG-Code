#!/usr/bin/env python3
"""Tabela do A/B dos terrenos com proxy (lotes `terrenos3` e `cmd50`): le SO' do bruto dados/raw_<tag>_10000[_resiliencia].json.xz (tag = terrenos | terrenos2). Diferenca pareada (variante - base), N = 10.000, pontos percentuais de partidas (campos 0/1) ou unidades,
IC95% pareado, `*` = excede o IC. Uso: python3 rank_proxy.py terrenos3 > ../resumos/tabela_x.md ; python3 rank_proxy.py cmd50 > ../resumos/tabela_y.md"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
TAG = sys.argv[1]; N = 10000
def ic(base, rs, c, escala=1.0):
    m, h = A.ic([x[1].get(c, 0.0) for x in base], [y[1].get(c, 0.0) for y in rs]); return "%+.2f ± %.2f%s" % (escala * m, escala * h, " *" if abs(m) > h else "")
def media(rs, c): return st.mean(y[1].get(c, 0.0) for y in rs)
dados = {}; bases = {}
MODOS_OK = [(m_, suf_) for m_, suf_ in (("p", ""), ("r", "_resiliencia")) if os.path.exists(os.path.join(ARQ, "dados", f"raw_{TAG}_{N}{suf_}.json.xz"))]
assert MODOS_OK, "nenhum bruto"
for modo, suf in MODOS_OK:
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_{TAG}_{N}{suf}")); base = res["base"]
    assert len(base) == N and "cleared_T8" in base[0][1]
    bases[modo] = base
    for nome, rs in res.items():
        if nome != "base": dados.setdefault(nome, {})[modo] = rs
b = bases
for md in b:
    print(f"Base ({'padrão' if md == 'p' else 'resiliência'}; lista atual): mesa limpa T8 {100 * media(b[md], 'cleared_T8'):.1f}%, T10 {100 * media(b[md], 'cleared_T10'):.1f}%; comandante conjurado até T4 {100 * media(b[md], 'commander_cast_turn__ate_T4'):.1f}%, até T5 {100 * media(b[md], 'commander_cast_turn__ate_T5'):.1f}%; deck-out {100 * media(b[md], 'self_lost'):.2f}%; regenerações usadas {media(b[md], 'regenerations_used'):.4f}; peças removidas {media(b[md], 'smart_removals_total'):.3f}.")
print()
print("Diferença pareada (variante − base), N = 10.000, no lugar; pontos percentuais de partidas; `*` = excede o IC95%.\n")
for modo, rot in [(m_, {"p": "padrão", "r": "resiliência"}[m_]) for m_, _ in MODOS_OK]:
    print(f"### Modo {rot}\n")
    print("| variante | comandante até T3 | até T4 | até T5 | até T6 | mesa limpa T7 | T8 | T10 | 1º oponente fora até T6 | eu perco por deck-out |\n|---|---|---|---|---|---|---|---|---|---|")
    for nome, v in dados.items():
        rs = v[modo]; base = b[modo]
        print(f"| {nome} | " + " | ".join(ic(base, rs, c, 100) for c in ("commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "commander_cast_turn__ate_T6", "cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost")) + " |")
    print()
print("### Atividade e proteção (diferença pareada da média por partida)\n")
CAMPOS = [("regenerations_used", "regenerações usadas"), ("protection_used_total", "proteções usadas"), ("smart_removals_total", "peças do motor removidas"), ("smart_wipes_total", "wipes que pegaram"), ("commander_countered_total", "comandante anulado"), ("fetches_cracked_total", "fetches quebradas"), ("life_min", "vida mínima")]
for md in b:
    rot = {"p": "padrão", "r": "resiliência"}[md]
    print(f"**{rot}**\n\n| variante | " + " | ".join(r for _, r in CAMPOS) + " |\n|---|" + "---|" * len(CAMPOS))
    print("| base (média) | " + " | ".join("%.4f" % media(b[md], c) for c, _ in CAMPOS) + " |")
    for nome, v in dados.items():
        print(f"| {nome} | " + " | ".join(ic(b[md], v[md], c) for c, _ in CAMPOS) + " |")
    print()

#!/usr/bin/env python3
"""Tabela do A/B da base de mana: le SO' do bruto dados/raw_<tag>_10000[_resiliencia].json.xz (tag = terrenos | terrenos2). Diferenca pareada (variante - base), N = 10.000, pontos percentuais de partidas (campos 0/1) ou unidades,
IC95% pareado, `*` = excede o IC. Uso: python3 rank_terrenos.py terrenos > ../resumos/tabela_terrenos.md ; python3 rank_terrenos.py terrenos2 > ../resumos/tabela_terrenos2.md"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
TAG = sys.argv[1]; N = 10000
def ic(base, rs, c, escala=1.0):
    m, h = A.ic([x[1].get(c, 0.0) for x in base], [y[1].get(c, 0.0) for y in rs]); return "%+.2f ± %.2f%s" % (escala * m, escala * h, " *" if abs(m) > h else "")
def media(rs, c): return st.mean(y[1].get(c, 0.0) for y in rs)
dados = {}; bases = {}
for modo, suf in (("p", ""), ("r", "_resiliencia")):
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_{TAG}_{N}{suf}")); base = res["base"]
    assert len(base) == N and "cleared_T8" in base[0][1]
    bases[modo] = base
    for nome, rs in res.items():
        if nome != "base": dados.setdefault(nome, {})[modo] = rs
b = bases
print(f"Base (lista atual): mesa limpa T8 {100 * media(b['p'], 'cleared_T8'):.1f}% (padrão) / {100 * media(b['r'], 'cleared_T8'):.1f}% (resiliência); comandante conjurado até T4 {100 * media(b['p'], 'commander_cast_turn__ate_T4'):.1f}% / {100 * media(b['r'], 'commander_cast_turn__ate_T4'):.1f}%, até T5 {100 * media(b['p'], 'commander_cast_turn__ate_T5'):.1f}% / {100 * media(b['r'], 'commander_cast_turn__ate_T5'):.1f}%; deck-out {100 * media(b['p'], 'self_lost'):.2f}% / {100 * media(b['r'], 'self_lost'):.2f}%.\n")
print("Diferença pareada (variante − base), N = 10.000, no lugar; pontos percentuais de partidas; `*` = excede o IC95%.\n")
for modo, rot in (("p", "padrão"), ("r", "resiliência")):
    print(f"### Modo {rot}\n")
    print("| variante | comandante até T3 | até T4 | até T5 | até T6 | mesa limpa T7 | T8 | T10 | 1º oponente fora até T6 | eu perco por deck-out |\n|---|---|---|---|---|---|---|---|---|---|")
    for nome, v in dados.items():
        rs = v[modo]; base = b[modo]
        print(f"| {nome} | " + " | ".join(ic(base, rs, c, 100) for c in ("commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "commander_cast_turn__ate_T6", "cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost")) + " |")
    print()
print("### Atividade (diferença pareada da média por partida; padrão | resiliência)\n")
CAMPOS = [("atomize_casts", "Atomize"), ("casualties_casts", "Casualties of War"), ("trophy_casts", "Assassin's Trophy"), ("regenerations_used", "regenerações usadas"), ("protection_used_total", "proteções usadas"), ("smart_removals_total", "peças do motor removidas"), ("prox_mana_wasted_total", "mana desperdiçado")]
print("| variante | " + " | ".join(r for _, r in CAMPOS) + " |\n|---|" + "---|" * len(CAMPOS))
print("| **base (média)** | " + " | ".join("%.3f \\| %.3f" % (media(b['p'], c), media(b['r'], c)) for c, _ in CAMPOS) + " |")
for nome, v in dados.items():
    print(f"| {nome} | " + " | ".join("%s \\| %s" % (ic(b['p'], v['p'], c), ic(b['r'], v['r'], c)) for c, _ in CAMPOS) + " |")

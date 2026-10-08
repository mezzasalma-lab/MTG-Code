#!/usr/bin/env python3
"""Tabela das CINCO ENTRADAS (Frank, Branching, Atomize, Casualties, Trophy) e dos 7 conjuntos de corte: le SO' do bruto dados/raw_cinco_10000[_resiliencia].json.xz.
Diferenca pareada (variante - base) em pontos percentuais (campos 0/1) ou unidades, IC95% pareado, `*` = excede o IC. Mostra tambem a atividade das cartas novas e o custo de interacao.
Uso: python3 rank_cinco.py > ../resumos/tabela_cinco.md"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
def ic(base, rs, c, escala=1.0):
    m, h = A.ic([x[1].get(c, 0.0) for x in base], [y[1].get(c, 0.0) for y in rs]); return "%+.2f ± %.2f%s" % (escala * m, escala * h, " *" if abs(m) > h else "")
def media(rs, c): return st.mean(y[1].get(c, 0.0) for y in rs)
def pct(rs, c): return 100 * sum(1 for y in rs if y[1].get(c, 0.0) > 0) / len(rs)
dados = {}; bases = {}
for modo, suf in (("p", ""), ("r", "_resiliencia")):
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_cinco_{N}{suf}")); base = res["base"]
    assert len(base) == N and "cleared_T8" in base[0][1] and "atomize_casts" in {c for x in res["s1_vats_wave_deluge"][:50] for c in x[1]} | {"atomize_casts"}
    bases[modo] = base
    for nome, rs in res.items():
        if nome != "base": dados.setdefault(nome, {})[modo] = rs
print(f"Base (lista atual): mesa limpa T8 {100 * media(bases['p'], 'cleared_T8'):.1f}% (padrão) / {100 * media(bases['r'], 'cleared_T8'):.1f}% (resiliência); T10 {100 * media(bases['p'], 'cleared_T10'):.1f}% / {100 * media(bases['r'], 'cleared_T10'):.1f}%; deck-out {100 * media(bases['p'], 'self_lost'):.2f}% / {100 * media(bases['r'], 'self_lost'):.2f}%.\n")
print("Diferença pareada (variante − base), N = 10.000, no lugar; pontos percentuais de partidas; `*` = excede o IC95%.\n")
for modo, rot in (("p", "padrão"), ("r", "resiliência")):
    print(f"### Modo {rot}\n")
    print("| variante | mesa limpa T7 | T8 | T10 | 1º oponente fora até T6 | eu perco por deck-out | contadores do Mothman (média) | rad nos oponentes (média) | cartas milladas no opp (média) |\n|---|---|---|---|---|---|---|---|---|")
    for nome, v in dados.items():
        rs = v[modo]; base = bases[modo]
        print(f"| {nome} | {ic(base, rs, 'cleared_T7', 100)} | {ic(base, rs, 'cleared_T8', 100)} | {ic(base, rs, 'cleared_T10', 100)} | {ic(base, rs, 'first_elim_T6', 100)} | {ic(base, rs, 'self_lost', 100)} | {ic(base, rs, 'mothman_counters_placed_total')} | {ic(base, rs, 'rad_counters_given_opp_total')} | {ic(base, rs, 'cards_milled_opp_total')} |")
    print()
print("### Atividade das remoções novas (média por partida / % das partidas com ≥ 1; padrão | resiliência)\n")
CAMPOS = [("atomize_casts", "Atomize"), ("casualties_casts", "Casualties of War"), ("trophy_casts", "Assassin's Trophy"), ("trophy_lands_given", "terrenos dados pelo Trophy"), ("interaction_plays", "jogadas de interação (proxy)"), ("crimes_total", "crimes"), ("deepmuck_triggers", "gatilhos do Deepmuck")]
print("| variante | " + " | ".join(r for _, r in CAMPOS) + " |\n|---|" + "---|" * len(CAMPOS))
print("| **base** | " + " | ".join("%.3f / %.1f%% \\| %.3f / %.1f%%" % (media(bases['p'], c), pct(bases['p'], c), media(bases['r'], c), pct(bases['r'], c)) for c, _ in CAMPOS) + " |")
for nome, v in dados.items():
    print(f"| {nome} | " + " | ".join("%.3f / %.1f%% \\| %.3f / %.1f%%" % (media(v['p'], c), pct(v['p'], c), media(v['r'], c), pct(v['r'], c)) for c, _ in CAMPOS) + " |")
print("\n### Interação no modo resiliência (média por partida; base e diferença pareada)\n")
CAMPOS2 = [("counterspells_cast", "contramágicas conjuradas"), ("protection_used_total", "proteções usadas"), ("commander_countered_total", "comandante anulado"), ("smart_removals_total", "peças do meu motor removidas"), ("smart_wipes_total", "wipes do oponente que pegaram"), ("proliferates_total", "proliferates")]
b = bases["r"]
print("| variante | " + " | ".join(r for _, r in CAMPOS2) + " |\n|---|" + "---|" * len(CAMPOS2))
print("| **base (média)** | " + " | ".join("%.3f" % media(b, c) for c, _ in CAMPOS2) + " |")
for nome, v in dados.items():
    print(f"| {nome} | " + " | ".join(ic(b, v["r"], c) for c, _ in CAMPOS2) + " |")

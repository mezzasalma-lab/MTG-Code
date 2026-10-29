#!/usr/bin/env python3
"""Tabela do PACOTE (Horrigan + Branching Evolution) e de qual interacao cortar: le SO' do bruto dados/raw_pacote_10000[_resiliencia].json.xz. Diferenca pareada (variante - base) em pontos percentuais
(campos 0/1) ou unidades, IC95% pareado, `*` = excede o IC. Mostra tambem a media ABSOLUTA da base e as atividades de interacao (contramagicas, protecoes, remocao/wipe dos oponentes sobre o meu motor).
Uso: python3 rank_pacote.py > ../resumos/tabela_pacote.md"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
def ic(base, rs, c, escala=1.0):
    m, h = A.ic([x[1].get(c, 0.0) for x in base], [y[1].get(c, 0.0) for y in rs]); return "%+.2f ± %.2f%s" % (escala * m, escala * h, " *" if abs(m) > h else "")
def media(rs, c): return st.mean(y[1].get(c, 0.0) for y in rs)
dados = {}; bases = {}
for modo, suf in (("p", ""), ("r", "_resiliencia")):
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_pacote_{N}{suf}")); base = res["base"]
    assert len(base) == N and "cleared_T8" in base[0][1] and "protection_used_total" in base[0][1]
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
print("### Interação no modo resiliência (média por partida; base e diferença pareada)\n")
CAMPOS = [("counterspells_cast", "contramágicas conjuradas"), ("protection_used_total", "proteções usadas (contra remoção/wipe)"), ("commander_countered_total", "comandante anulado pelo oponente"),
          ("smart_removals_total", "peças do meu motor removidas"), ("smart_wipes_total", "wipes do oponente que pegaram"), ("proliferates_total", "proliferates")]
print("| variante | " + " | ".join(r for _, r in CAMPOS) + " |\n|---|" + "---|" * len(CAMPOS))
b = bases["r"]
print("| **base (média)** | " + " | ".join("%.3f" % media(b, c) for c, _ in CAMPOS) + " |")
for nome, v in dados.items():
    print(f"| {nome} | " + " | ".join(ic(b, v["r"], c) for c, _ in CAMPOS) + " |")

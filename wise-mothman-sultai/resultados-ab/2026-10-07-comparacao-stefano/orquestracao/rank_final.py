#!/usr/bin/env python3
"""Tabela FINAL de Horrigan e Master (N=10.000 pareado, `no lugar`): le SO' do bruto dados/raw_final_10000[_resiliencia].json.xz. Diferenca pareada (variante - base) em pontos percentuais
de partidas (campos 0/1) ou unidades, IC95% pareado, `*` = excede o IC. Uso: python3 rank_final.py > ../resumos/tabela_final.md"""
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
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_final_{N}{suf}")); base = res["base"]
    assert len(base) == N and "cleared_T8" in base[0][1]
    bases[modo] = base
    for nome, rs in res.items():
        if nome != "base": dados.setdefault(nome, {})[modo] = rs
print(f"Base (lista atual): mesa limpa T8 {100 * media(bases['p'], 'cleared_T8'):.1f}% (padrão) / {100 * media(bases['r'], 'cleared_T8'):.1f}% (resiliência); eu perco por deck-out {100 * media(bases['p'], 'self_lost'):.2f}% / {100 * media(bases['r'], 'self_lost'):.2f}%.\n")
print("Diferença pareada (variante − base), N = 10.000, no lugar; pontos percentuais de partidas; `*` = excede o IC95%.\n")
for modo, rot in (("p", "padrão"), ("r", "resiliência")):
    print(f"### Modo {rot}\n")
    print("| variante | mesa limpa T7 | T8 | T10 | 1º oponente fora até T6 | eu perco por deck-out | contadores +1/+1 (média) | rad nos oponentes (média) | cartas milladas no opp (média) | partidas idênticas à base |\n|---|---|---|---|---|---|---|---|---|---|")
    for nome, v in dados.items():
        rs = v[modo]; base = bases[modo]
        ident = sum(1 for b, r in zip(base, rs) if all(abs(b[1].get(c, 0.0) - r[1].get(c, 0.0)) < 1e-9 for c in ("cleared_T8", "cleared_T10", "self_lost", "cards_milled_opp_total", "mothman_counters_placed_total"))) / N
        print(f"| {nome} | {ic(base, rs, 'cleared_T7', 100)} | {ic(base, rs, 'cleared_T8', 100)} | {ic(base, rs, 'cleared_T10', 100)} | {ic(base, rs, 'first_elim_T6', 100)} | {ic(base, rs, 'self_lost', 100)} | {ic(base, rs, 'mothman_counters_placed_total')} | {ic(base, rs, 'rad_counters_given_opp_total')} | {ic(base, rs, 'cards_milled_opp_total')} | {100 * ident:.0f}% |")
    print()
print("### Atividade das cartas (média por partida, todas as partidas; padrão / resiliência)\n")
print("| variante | Horrigan entra (etb) | ataques do Horrigan | dano médio por ataque | Master ativa | ... em criatura minha | ... em criatura de oponente | ... no turno de oponente | Master: 2 rad ao entrar |\n|---|---|---|---|---|---|---|---|---|")
def par(rs_p, rs_r, c): return "%.3f / %.3f" % (media(rs_p, c), media(rs_r, c))
for nome, v in dados.items():
    p, r = v["p"], v["r"]
    dano = lambda rs: (sum(y[1].get("horrigan_attack_damage", 0.0) for y in rs) / max(1.0, sum(y[1].get("horrigan_attacks", 0.0) for y in rs)))
    print(f"| {nome} | {par(p, r, 'horrigan_etb_prolifs')} | {par(p, r, 'horrigan_attacks')} | {dano(p):.1f} / {dano(r):.1f} | {par(p, r, 'master_activations')} | {par(p, r, 'master_act_mine')} | {par(p, r, 'master_act_opp')} | {par(p, r, 'master_act_on_opp_phase')} | {par(p, r, 'master_etb_rad')} |")

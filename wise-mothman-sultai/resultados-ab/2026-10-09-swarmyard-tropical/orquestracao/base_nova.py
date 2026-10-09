#!/usr/bin/env python3
"""Lido SO' dos brutos arquivados: (1) a NOVA LINHA DE BASE (lista aplicada = variante e1_swarmyard_tropical; o vivo com SWAPS=() e' bit-identico a ela, resumos/bitident_lista_20000.txt) ao lado da anterior; (2) o que a
Swarmyard fazia (regeneracoes usadas, partidas com >= 1, comandante conjurado 2+ vezes) nas premissas do lote W (remocao pontual nunca mira o comandante) e do lote V (COMMANDER_REMOVAL_SHARE = 0,5).
Uso: python3 base_nova.py > ../resumos/base_nova.md"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
def raw(tag, suf): return A.carregar_raw(os.path.join(ARQ, "dados", f"raw_{tag}_10000{suf}"))
def m(rs, c): return st.mean(y[1].get(c, 0.0) for y in rs)
def pct(rs, f): return 100 * st.mean(1.0 if f(y[1]) else 0.0 for y in rs)
print("## Nova linha de base (lista aplicada em 2026-10-09 = e1; N = 10.000, sementes 3.000.000+i, 12 turnos)\n")
print("| métrica | modo padrão | modo resiliência |\n|---|---|---|")
E = {md: raw("swtrop", suf)["e1_swarmyard_tropical"] for md, suf in (("p", ""), ("r", "_resiliencia"))}
B = {md: raw("swtrop", suf)["base"] for md, suf in (("p", ""), ("r", "_resiliencia"))}
LIN = [("comandante conjurado até T4 (%)", lambda r: 100 * m(r, "commander_cast_turn__ate_T4")), ("comandante conjurado até T5 (%)", lambda r: 100 * m(r, "commander_cast_turn__ate_T5")),
       ("mesa limpa até T7 (%)", lambda r: 100 * m(r, "cleared_T7")), ("mesa limpa até T8 (%)", lambda r: 100 * m(r, "cleared_T8")), ("mesa limpa até T10 (%)", lambda r: 100 * m(r, "cleared_T10")),
       ("1º oponente fora até T6 (%)", lambda r: 100 * m(r, "first_elim_T6")), ("eu perco por deck-out (%)", lambda r: 100 * m(r, "self_lost")),
       ("regenerações usadas por partida", lambda r: m(r, "regenerations_used")), ("proteções usadas por partida", lambda r: m(r, "protection_used_total")), ("peças do motor removidas por partida", lambda r: m(r, "smart_removals_total")),
       ("contadores postos pelo gatilho do Mothman por partida (`mothman_counters_placed_total`; NÃO é o campo de 133/91 dos §17–§19)", lambda r: m(r, "mothman_counters_placed_total"))]
for rot, f in LIN:
    print(f"| {rot} (nova) | {f(E['p']):.4f} | {f(E['r']):.4f} |")
    print(f"| {rot} (anterior, lista de antes da troca) | {f(B['p']):.4f} | {f(B['r']):.4f} |")
print("\n## O que a Swarmyard fazia (base com a Swarmyard × e1 sem ela)\n")
print("| premissa | modo | regenerações usadas (com / sem) | partidas com ≥ 1 regeneração (com / sem) | partidas com comandante conjurado 2+ vezes, inclui conjuração anulada (com / sem) |\n|---|---|---|---|---|")
for rot, tag, mds in (("remoção pontual NUNCA mira o comandante (lote W)", "swtrop", (("padrão", ""), ("resiliência", "_resiliencia"))), ("50% das remoções pontuais miram o comandante (lote V)", "swtrop50", (("resiliência", "_resiliencia"),))):
    for md, suf in mds:
        r = raw(tag, suf); b, e = r["base"], r["e1_swarmyard_tropical"]
        print(f"| {rot} | {md} | {m(b, 'regenerations_used'):.4f} / {m(e, 'regenerations_used'):.4f} | {pct(b, lambda x: x.get('regenerations_used', 0) >= 1):.2f}% / {pct(e, lambda x: x.get('regenerations_used', 0) >= 1):.2f}% | {pct(b, lambda x: x.get('commander_cast_count', 0) >= 2):.2f}% / {pct(e, lambda x: x.get('commander_cast_count', 0) >= 2):.2f}% |")

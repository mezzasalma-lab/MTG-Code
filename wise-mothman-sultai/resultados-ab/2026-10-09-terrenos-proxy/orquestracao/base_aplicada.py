#!/usr/bin/env python3
"""Duas tabelas lidas SO' dos brutos arquivados:
 (1) a NOVA LINHA DE BASE (lista aplicada = variante d1_hollow_bayou_passage_vista do lote terrenos4; o simulador vivo com SWAPS=() e' bit-identico a ela, ver resumos/bitident_lista_20000.txt), N = 10.000, sementes 3.000.000+i, 12 turnos, 2 modos;
 (2) o valor da Swarmyard (a3_swarmyard_sea contra a base de cada lote): regeneracoes usadas, partidas com >= 1 regeneracao, comandante conjurado 2+ vezes (volta ao comando por morte OU por conjuração anulada: o campo `commander_cast_count` conta as duas), nas premissas do lote X (spot removal nunca mira o comandante)
     e do lote Y (COMMANDER_REMOVAL_SHARE = 0,5: metade das remocoes pontuais mira o comandante).
Uso: python3 base_aplicada.py > ../resumos/base_aplicada.md"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
def raw(tag, suf): return A.carregar_raw(os.path.join(ARQ, "dados", f"raw_{tag}_10000{suf}"))
def m(rs, c): return st.mean(y[1].get(c, 0.0) for y in rs)
def pct(rs, f): return 100 * st.mean(1.0 if f(y[1]) else 0.0 for y in rs)
print("## Nova linha de base (lista aplicada em 2026-10-09 = d1; N = 10.000, sementes 3.000.000+i, 12 turnos)\n")
print("| métrica | modo padrão | modo resiliência |\n|---|---|---|")
D = {md: raw("terrenos4", suf)["d1_hollow_bayou_passage_vista"] for md, suf in (("p", ""), ("r", "_resiliencia"))}
B = {md: raw("terrenos4", suf)["base"] for md, suf in (("p", ""), ("r", "_resiliencia"))}
LIN = [("comandante conjurado até T4 (%)", lambda r: 100 * m(r, "commander_cast_turn__ate_T4")), ("comandante conjurado até T5 (%)", lambda r: 100 * m(r, "commander_cast_turn__ate_T5")),
       ("mesa limpa até T7 (%)", lambda r: 100 * m(r, "cleared_T7")), ("mesa limpa até T8 (%)", lambda r: 100 * m(r, "cleared_T8")), ("mesa limpa até T10 (%)", lambda r: 100 * m(r, "cleared_T10")),
       ("1º oponente fora até T6 (%)", lambda r: 100 * m(r, "first_elim_T6")), ("eu perco por deck-out (%)", lambda r: 100 * m(r, "self_lost")),
       ("contadores +1/+1 postos por partida", lambda r: m(r, "counters_placed_total")), ("gatilhos do Mothman por partida", lambda r: m(r, "mothman_triggers_total"))]
for rot, f in LIN:
    print(f"| {rot} (nova) | {f(D['p']):.2f} | {f(D['r']):.2f} |")
    print(f"| {rot} (anterior, lista de 2026-10-08) | {f(B['p']):.2f} | {f(B['r']):.2f} |")
print("\n## Swarmyard: o que a regeneração vale (a3_swarmyard_sea − base, pareado; a base tem a Swarmyard)\n")
print("| premissa | modo | regenerações usadas por partida (base) | partidas com ≥ 1 regeneração (base) | com a Swarmyard trocada pelo Underground Sea | partidas com comandante conjurado 2+ vezes, inclui conjuração anulada (base) | (sem a Swarmyard) |\n|---|---|---|---|---|---|---|")
for rot, tag, mds in (("spot removal NUNCA mira o comandante (lote X)", "terrenos3", (("padrão", ""), ("resiliência", "_resiliencia"))), ("50% das remoções pontuais miram o comandante (lote Y)", "cmd50", (("resiliência", "_resiliencia"),))):
    for md, suf in mds:
        r = raw(tag, suf); b, a = r["base"], r["a3_swarmyard_sea"]
        print(f"| {rot} | {md} | {m(b, 'regenerations_used'):.4f} | {pct(b, lambda x: x.get('regenerations_used', 0) >= 1):.2f}% | {m(a, 'regenerations_used'):.4f} / {pct(a, lambda x: x.get('regenerations_used', 0) >= 1):.2f}% | {pct(b, lambda x: x.get('commander_cast_count', 0) >= 2):.2f}% | {pct(a, lambda x: x.get('commander_cast_count', 0) >= 2):.2f}% |")

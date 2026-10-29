"""Espiao do achado lateral 'contadores de fichas doentes': `sacrifice_constructs` / `sacrifice_other_tokens` do simulador nunca decrementam `*_sick`, so' o total; os prontos sao `max(0, total - doentes)`.
Conta, em N partidas, quantos sacrificios de fichas com doentes presentes acontecem ANTES do combate do turno (unico momento em que importa: os doentes zeram no fim do turno) e quantos atacantes
prontos a menos isso causa se o jogador deveria sacrificar os doentes primeiro. Uso: python3 espiao_fichas_doentes.py padrao|resiliencia N"""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
V = F.flags(F.carrega(F.DEPOIS, "vih_sick"))
modo = sys.argv[1]
N = int(sys.argv[2])
cont = collections.Counter()
o_c, o_o = V.sacrifice_constructs, V.sacrifice_other_tokens
o_cs = V.combat_step
def cs(state):
    state._combate = state.turn
    return o_cs(state)
V.combat_step = cs
def pre(state):
    return getattr(state, '_combate', None) != state.turn
def sc(state, n):
    if n > 0 and state.constructs > 0 and state.constructs_sick > 0 and pre(state):
        cont["constructs_sick_gt0"] += 1
        # tokens que ficariam prontos se os sacrificados fossem os doentes primeiro
        pronto_atual = max(0, state.constructs - min(n, state.constructs) - state.constructs_sick)
        pronto_novo = max(0, state.constructs - min(n, state.constructs) - max(0, state.constructs_sick - min(n, state.constructs)))
        if pronto_novo != pronto_atual: cont["constructs_afeta_prontos"] += 1; cont["constructs_prontos_perdidos"] += pronto_novo - pronto_atual
    return o_c(state, n)
def so(state, n):
    if n > 0 and state.other_tokens > 0 and state.other_tokens_sick > 0 and pre(state):
        cont["other_sick_gt0"] += 1
        pronto_atual = max(0, state.other_tokens - min(n, state.other_tokens) - state.other_tokens_sick)
        pronto_novo = max(0, state.other_tokens - min(n, state.other_tokens) - max(0, state.other_tokens_sick - min(n, state.other_tokens)))
        if pronto_novo != pronto_atual: cont["other_afeta_prontos"] += 1; cont["other_prontos_perdidos"] += pronto_novo - pronto_atual
    return o_o(state, n)
V.sacrifice_constructs, V.sacrifice_other_tokens = sc, so
fn = V.simulate_one if modo == "padrao" else V.simulate_one_with_interaction
jogos_afetados = 0
for i in range(N):
    antes = sum(cont.values())
    fn(1_000_000 + i)
    if sum(cont.values()) != antes: jogos_afetados += 1
print(modo, N, dict(cont), "jogos com algum evento:", jogos_afetados)

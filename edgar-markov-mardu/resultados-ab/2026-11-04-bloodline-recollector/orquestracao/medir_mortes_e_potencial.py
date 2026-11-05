"""Apoio (Regra #5: o simulador e' evidencia de APOIO, nao arbitro) para avaliar a Bloodline Recollector no Edgar Markov (2026-11-04).
O gatilho da carta e' "at the beginning of each end step, if three or more creatures died this turn". O simulador (edgar_markov_goldfish_v1.py) NAO consegue medir isso, por construcao:
`sac_loop` sacrifica no maximo 2 TOKENS de Vampiro por turno (cap declarado no proprio codigo) e nunca uma criatura nomeada. Esta medicao mostra os dois lados:
  (a) PISO: em quantos fins de turno o simulador, com a politica dele, chega a >= 2 e >= 3 mortes (>= 2 e' o gatilho do Emeritus of Woe, que o simulador ja' modela);
  (b) POTENCIAL de uma linha DELIBERADA: no inicio do sac_loop, quantas vezes ha' um outlet gratis em campo E >= 3 tokens de Vampiro disponiveis (3 mortes possiveis sem gastar carta nomeada).
Uso: PYTHONHASHSEED=0 python3 -I medir_mortes_e_potencial.py [N]   (padrao 10.000, sementes 3_000_000+i, 8 turnos, modo padrao)"""
import collections, importlib.util, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
os.chdir(DECK)
spec = importlib.util.spec_from_file_location("edgar_sim", os.path.join(DECK, "edgar_markov_goldfish_v1.py")); m = importlib.util.module_from_spec(spec); sys.modules["edgar_sim"] = m; spec.loader.exec_module(m)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
rec = collections.defaultdict(lambda: collections.Counter())   # turno -> contadores
jogo = collections.Counter()
atual = {"seed": None, "d3": False, "d2": False, "pot": False, "emeritus_prep": False}
orig_sac, orig_end = m.sac_loop, m.do_end_step
def sac(state, log):
    out = any(c in m.SAC_OUTLETS for c in state.battlefield)
    pago = state.has("Indulgent Aristocrat")
    rec[state.turn]["sac_loop_chamadas"] += 1
    if out and len(state.tokens) >= 3: rec[state.turn]["potencial_outlet_gratis_e_3_tokens"] += 1; atual["pot"] = True
    if (out or pago) and len(state.tokens) >= 3: rec[state.turn]["potencial_qualquer_outlet_e_3_tokens"] += 1
    if out: rec[state.turn]["outlet_gratis_em_campo"] += 1
    return orig_sac(state, log)
def fim(state, log):
    d = state.creatures_died_this_turn
    rec[state.turn]["fins_de_turno"] += 1
    if d >= 2: rec[state.turn]["mortes>=2"] += 1; atual["d2"] = True
    if d >= 3: rec[state.turn]["mortes>=3"] += 1; atual["d3"] = True
    return orig_end(state, log)
m.sac_loop, m.do_end_step = sac, fim
for i in range(N):
    atual.update(seed=3_000_000 + i, d3=False, d2=False, pot=False)
    r = m.simulate_one(3_000_000 + i, turns=8)
    jogo["partidas"] += 1; jogo["alguma_vez_mortes>=2"] += atual["d2"]; jogo["alguma_vez_mortes>=3"] += atual["d3"]; jogo["alguma_vez_potencial(outlet gratis + 3 tokens)"] += atual["pot"]
    jogo["emeritus_tutors>=1"] += (r.get("emeritus_of_woe_tutors", 0) or 0) >= 1
print(f"{N} partidas, modo padrao, sementes 3_000_000+i, 8 turnos (simulador vivo, politica dele: ate 2 sacrificios de token por turno)")
print("por turno (fraccao dos fins de turno / das chamadas do sac_loop):")
print("turno | fins | mortes>=2 | mortes>=3 | outlet gratis em campo | outlet gratis + >=3 tokens (potencial)")
for t in range(1, 9):
    c = rec[t]; f = max(1, c["fins_de_turno"]); s = max(1, c["sac_loop_chamadas"])
    print(f"  T{t}  | {c['fins_de_turno']:5d} | {100*c['mortes>=2']/f:6.2f}% | {100*c['mortes>=3']/f:6.2f}% | {100*c['outlet_gratis_em_campo']/s:6.2f}% | {100*c['potencial_outlet_gratis_e_3_tokens']/s:6.2f}%")
print("por partida (alguma vez em T1..T8):")
for k in ("alguma_vez_mortes>=2", "alguma_vez_mortes>=3", "alguma_vez_potencial(outlet gratis + 3 tokens)", "emeritus_tutors>=1"):
    print(f"  {k}: {jogo[k]} de {jogo['partidas']} ({100*jogo[k]/jogo['partidas']:.2f}%)")

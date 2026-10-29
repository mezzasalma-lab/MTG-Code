"""Ajuste do perfil `playtester` do oponente: mede, no simulador, as MESMAS grandezas que `taxas_observadas.py` mediu nos 5 goldfish manuais do usuario, com e sem o perfil.
Grandezas por partida (modo de resiliencia, 12 turnos): (a) criaturas de oponente em campo (soma dos 3) no fim dos turnos 5, 8 e 10; (b) eventos de interacao: remocao pontual, anulacao, efeito em massa (wipe de criatura /
artefato / encantamento / cemiterio) e descarte. Observado (5 logs, T4 em diante, 31 turnos de usuario): criaturas 11 eventos; remocao 5, anulacao 2, efeito em massa 5 (+1 aura): 13 nao-criatura.
Uso: TAM_SIM=<caminho do tam_goldfish_v1.py> python3 ajuste_perfil.py <N> <perfil: default|playtester>    (sementes 1_000_000+i)"""
import os, sys, importlib.util, collections, math, statistics
sim = os.environ.get("TAM_SIM", "/home/user/MTG-Code/tam-the-possibility-wubrg/tam_goldfish_v1.py")
spec = importlib.util.spec_from_file_location("tam_aj", sim)
T = importlib.util.module_from_spec(spec); sys.modules["tam_aj"] = T; spec.loader.exec_module(T)
N = int(sys.argv[1]); perfil = sys.argv[2] if len(sys.argv) > 2 else "default"
if perfil == "playtester":
    T.aplica_perfil("playtester")
board = collections.defaultdict(list)
cont = collections.defaultdict(list)
for i in range(N):
    sd = 1_000_000 + i
    st = T.new_state(sd); T.setup_resilience(st, sd)
    for t in range(1, 13):
        T.play_turn(st)
        if st.game_over: break
        for o in list(st.opps):
            if not o.eliminated: T.opponent_turn(st, o)
        if t in (5, 8, 10): board[t].append(sum(len(o.board) for o in st.opps))
    m = st.m
    cont["remocao_pontual"].append(m.get("smart_removals", 0))
    cont["anulacao"].append(m.get("smart_counters", 0))
    cont["efeito_em_massa"].append(m.get("smart_wipes", 0) + m.get("smart_artifact_wipes", 0) + m.get("smart_enchantment_wipes", 0) + m.get("graveyard_wipe_used", 0))
    cont["descarte"].append(m.get("smart_discards", 0))
def ic(v):
    mu = statistics.mean(v); sd = statistics.pstdev(v) if len(v) > 1 else 0; h = 1.96 * sd / math.sqrt(len(v)); return mu, mu - h, mu + h
print(f"perfil={perfil} N={N} modo resiliencia, 12 turnos (sim: {os.path.basename(os.path.dirname(sim))})")
print("criaturas de oponente em campo (soma dos 3, fim do turno): observado nos logs (cartas de criatura vistas, cumulativo, sem mortes): T5 1.0 | T8 2.1 | T10 2.4")
for t in (5, 8, 10):
    mu, lo, hi = ic(board[t]); print(f"   T{t:2d}: {mu:5.2f} (IC95% {lo:5.2f}-{hi:5.2f})")
obs = {"remocao_pontual": 1.45, "anulacao": 0.58, "efeito_em_massa": 1.45, "descarte": 0.29}
obs_ic = {"remocao_pontual": (0.47, 3.39), "anulacao": (0.07, 2.10), "efeito_em_massa": (0.47, 3.39), "descarte": (0.0, 1.6)}
print("eventos de interacao por partida (sim: T3-T12; observado: 9 turnos T4-T12 dos 5 logs, IC95% de Poisson; o descarte observado e' o Junji: 1 evento INFERIDO, IC nao informativo)")
for k in obs:
    mu, lo, hi = ic(cont[k]); a, b = obs_ic[k]
    print(f"   {k:16s} sim {mu:5.2f} ({lo:5.2f}-{hi:5.2f}) | observado {obs[k]:4.2f} ({a:.2f}-{b:.2f}) | sim dentro do IC observado: {'sim' if a <= mu <= b else 'NAO'}")
tot = [sum(cont[k][i] for k in obs) for i in range(N)]
mu, lo, hi = ic(tot); print(f"   {'total nao-criatura':16s} sim {mu:5.2f} ({lo:5.2f}-{hi:5.2f}) | observado 3.77 (2.00-6.42)")

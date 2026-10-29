"""Validacao do perfil `playtester`: repete os replays dos goldfish manuais #3, #4 e #5 (a MESMA mao e as MESMAS compras do usuario, resto do baralho em N ordens) nos 3 oponentes -- padrao, resiliencia de sempre e resiliencia
com o perfil do playtester -- e compara os planeswalkers em campo no fim de cada turno com o jogo REAL do usuario (do log). Nao e' validacao independente: o perfil foi ajustado nas taxas de eventos de oponente dos 5 logs (que incluem
estes 3); a comparacao mostra se o perfil aproxima o RESULTADO do usuario (planeswalkers), nao so' as taxas.
Uso: python3 replay_perfil.py <N> <jogo: 3|4|5> <modo: padrao|resiliencia> <perfil: default|playtester>"""
import os, sys, importlib.util, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.abspath(os.path.join(AQUI, "..", ".."))
N = int(sys.argv[1]); JOGO = sys.argv[2]; MODO = sys.argv[3]; PERFIL = sys.argv[4]
PASTAS = {"3": "2026-10-21-goldfish-manual-3", "4": "2026-10-21-goldfish-manual-4", "5": "2026-10-21-goldfish-manual-5"}
# planeswalkers em campo no FIM de cada turno, no jogo do usuario (fichas de Jace contam): dos LEIAME de cada pasta / do log
USUARIO = {"3": {1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 3, 7: 4},
           "4": {1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 3, 8: 3, 9: 4},
           "5": {1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 2, 7: 2, 8: 4, 9: 5, 10: 7}}
TURNOS = {"3": 7, "4": 9, "5": 10}
orq = os.path.join(ARQ, PASTAS[JOGO], "orquestracao")
sys.path.insert(0, orq)
spec = importlib.util.spec_from_file_location(f"replay_manual_{JOGO}", os.path.join(orq, f"replay_manual_{JOGO}.py"))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
T = R.T
if PERFIL == "playtester":
    T.aplica_perfil("playtester")
usu = USUARIO[JOGO]
res = []
tam = []
for i in range(N):
    s = R.estado(1_000_000 + i, resiliencia=(MODO == "resiliencia"))
    linha = {}
    for t in range(1, TURNOS[JOGO] + 1):
        T.play_turn(s)
        for o in list(s.opps):
            if not o.eliminated:
                T.opponent_turn(s, o)
        linha[t] = len(T.pws(s))
        if s.game_over:
            for u in range(t + 1, TURNOS[JOGO] + 1):
                linha[u] = linha[t]
            break
    res.append(linha)
    tam.append(s.commander_cast_turn)
q = lambda x, f: x[int(f * (len(x) - 1))]
print(f"Replay do goldfish manual #{JOGO} | modo {MODO} | perfil {PERFIL} | N={N} ordens do resto do baralho")
print("turno | planeswalkers: mediana [Q1-Q3] | usuario | P(sim >= usuario)")
for t in range(1, TURNOS[JOGO] + 1):
    a = sorted(r[t] for r in res)
    pge = sum(1 for x in a if x >= usu[t]) / N
    print(f"  T{t:2d} | {st.median(a):4.1f} [{q(a, .25)}-{q(a, .75)}] | {usu[t]} | {100 * pge:5.1f}%")
t_ = [x for x in tam if x is not None]
print(f"Tam conjurada: mediana T{st.median(t_) if t_ else '-'} ({len(t_)}/{N} partidas)")

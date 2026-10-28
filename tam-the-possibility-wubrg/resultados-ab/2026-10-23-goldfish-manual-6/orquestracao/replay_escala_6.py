"""Replay do goldfish manual #6 em N ordens do resto do baralho (mesma mao, mesmas compras do usuario), nos 3 oponentes: padrao, resiliencia de sempre e resiliencia com o perfil `playtester`; compara os planeswalkers em campo
no fim de cada turno com o jogo REAL (de `pws_por_turno.py`: leitura do log; e a variante com a premissa da Fracture). Nao e' validacao: o perfil playtester foi ajustado nos logs #1-#5, nao neste.
Uso: python3 replay_escala_6.py <N> <modo: padrao|resiliencia> <perfil: default|playtester>"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import replay_manual_6 as R
import pws_por_turno as P
T = R.T
N = int(sys.argv[1]); MODO = sys.argv[2]; PERFIL = sys.argv[3]
if PERFIL == "playtester":
    T.aplica_perfil("playtester")
usu = {t: len(n) for t, n in P.contagem().items()}
P.PREMISSA = True
usu_f = {t: len(n) for t, n in P.contagem().items()}
TURNOS = 11
res, tam = [], []
for i in range(N):
    s = R.estado(1_000_000 + i, resiliencia=(MODO == "resiliencia"))
    linha = {}
    for t in range(1, TURNOS + 1):
        T.play_turn(s)
        for o in list(s.opps):
            if not o.eliminated:
                T.opponent_turn(s, o)
        linha[t] = len(T.pws(s))
        if s.game_over:
            for u in range(t + 1, TURNOS + 1):
                linha[u] = linha[t]
            break
    res.append(linha)
    tam.append(s.commander_cast_turn)
q = lambda x, f: x[int(f * (len(x) - 1))]
print(f"Replay do goldfish manual #6 | modo {MODO} | perfil {PERFIL} | N={N} ordens do resto do baralho")
print("turno | planeswalkers: mediana [Q1-Q3] | usuario (log) | usuario (premissa Fracture no T4) | P(sim >= usuario)")
for t in range(1, TURNOS + 1):
    a = sorted(r[t] for r in res)
    pge = sum(1 for x in a if x >= usu[t]) / N
    print(f"  T{t:2d} | {st.median(a):4.1f} [{q(a, .25)}-{q(a, .75)}] | {usu[t]} | {usu_f[t]} | {100 * pge:5.1f}%")
t_ = [x for x in tam if x is not None]
print(f"Tam conjurada: mediana T{st.median(t_) if t_ else '-'} ({len(t_)}/{N} partidas); o usuario: T3")

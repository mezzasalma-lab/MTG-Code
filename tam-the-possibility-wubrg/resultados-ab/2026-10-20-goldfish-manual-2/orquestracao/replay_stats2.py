"""Replay do goldfish manual #2 em N ordens do RESTO do baralho (a mesma mao e as mesmas 12 compras do usuario, na mesma ordem): mediana e quartis, por turno (1 a 8, o jogo dele acabou no T8), de planeswalkers
em campo, lealdade total e mana no inicio do turno; turno em que a Tam entra; 1a ultimate. Compara com o jogo do usuario JA' CORRIGIDO por ele (T4: a Saheeli foi undo; T7: o Teferi morreu pro Swift End).
Uso: python3 replay_stats2.py [N] [modo: padrao|resiliencia]"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import replay_manual_2 as R
T = R.T

# jogo do usuario, do log com as correcoes dele (resultados-ab/2026-10-20-goldfish-manual-2/LEIAME.md): planeswalkers em campo no FIM de cada turno (a ficha de Jace conta)
USUARIO_PW = {1: 0, 2: 0, 3: 0, 4: 1, 5: 3, 6: 4, 7: 6, 8: 6}
USUARIO_TAM_T = 3


def um(seed, modo):
    s = R.estado(seed, resiliencia=(modo == "resiliencia"))
    rows = {}
    for t in range(1, 9):
        T.play_turn(s)
        for o in list(s.opps):
            if not o.eliminated:
                T.opponent_turn(s, o)
        rows[t] = (len(T.pws(s)), sum(T.loyalty(p) for p in T.pws(s)), s.by_turn.get(t, {}).get("mana", 0))
        if s.game_over:
            for u in range(t + 1, 9):
                rows[u] = rows[t]
            break
    return rows, s.commander_cast_turn, s.first_turn.get("first_ultimate"), s.m.get("saheeli_mana_copies", 0)


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    modo = sys.argv[2] if len(sys.argv) > 2 else "padrao"
    res = [um(1_000_000 + i, modo) for i in range(N)]
    print(f"Replay do goldfish manual #2, modo {modo}, N={N} ordens do resto do baralho (mesmas 20 cartas iniciais do usuario)")
    print("turno | PWs mediana [Q1-Q3] | usuario | lealdade total mediana | mana no inicio mediana")
    for t in range(1, 9):
        a = sorted(r[0][t][0] for r in res); b = sorted(r[0][t][1] for r in res); c = sorted(r[0][t][2] for r in res)
        q = lambda x, f: x[int(f * (len(x) - 1))]
        print(f"  T{t:2d} | {st.median(a):4.1f} [{q(a, .25)}-{q(a, .75)}] | {USUARIO_PW[t]} | {st.median(b):5.1f} | {st.median(c):4.1f}")
    tam = [r[1] for r in res if r[1] is not None]
    ult = [r[2] for r in res if r[2] is not None]
    cp = sum(1 for r in res if r[3] > 0)
    print(f"Tam conjurada: mediana T{st.median(tam)} (usuario: T{USUARIO_TAM_T}); 1a ultimate: em {len(ult)}/{N} partidas, mediana T{st.median(ult) if ult else '-'} (usuario: nenhuma); partidas com copia de mana da Saheeli: {cp}/{N}")

"""Replay do goldfish manual #1 em N ordens do RESTO do baralho (a mesma mao e as mesmas 10 compras do usuario, na mesma ordem): mediana e quartis, por turno, de planeswalkers em campo,
lealdade total e mana disponivel no inicio do turno; turno em que a Tam entra; turno da 1a ultimate. Compara com o jogo do usuario (tabela fixa abaixo, tirada do log).
Uso: python3 replay_stats.py [N] [modo: padrao|resiliencia]"""
import os, sys, statistics as st, collections
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import replay_manual_1 as R
T = R.T

# jogo do usuario, contado do log (resultados-ab/2026-10-19-goldfish-manual-1/LEIAME.md, tabela "O jogo do usuario"): planeswalkers em campo no FIM de cada turno (a ficha de Jace conta) e Tam em campo
USUARIO_PW = {1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3}
USUARIO_TAM_T = 4


def um(seed, modo):
    s = R.estado(seed, resiliencia=(modo == "resiliencia"))
    rows = {}
    for t in range(1, 11):
        T.play_turn(s)
        for o in list(s.opps):
            if not o.eliminated:
                T.opponent_turn(s, o)
        rows[t] = (len(T.pws(s)), sum(T.loyalty(p) for p in T.pws(s)), s.by_turn.get(t, {}).get("mana", 0))
        if s.game_over:
            for u in range(t + 1, 11):
                rows[u] = rows[t]
            break
    return rows, s.commander_cast_turn, s.first_turn.get("first_ultimate")


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    modo = sys.argv[2] if len(sys.argv) > 2 else "padrao"
    res = [um(1_000_000 + i, modo) for i in range(N)]
    print(f"Replay do goldfish manual #1, modo {modo}, N={N} ordens do resto do baralho (mesmas 18 cartas iniciais do usuario)")
    print("turno | PWs mediana [Q1-Q3] | usuario | lealdade total mediana | mana no inicio mediana")
    for t in range(1, 11):
        a = sorted(r[0][t][0] for r in res); b = sorted(r[0][t][1] for r in res); c = sorted(r[0][t][2] for r in res)
        q = lambda x, f: x[int(f * (len(x) - 1))]
        print(f"  T{t:2d} | {st.median(a):4.1f} [{q(a, .25)}-{q(a, .75)}] | {USUARIO_PW[t]} | {st.median(b):5.1f} | {st.median(c):4.1f}")
    tam = [r[1] for r in res if r[1] is not None]
    ult = [r[2] for r in res if r[2] is not None]
    print(f"Tam conjurada: mediana T{st.median(tam)} (usuario: T{USUARIO_TAM_T}); 1a ultimate: em {len(ult)}/{N} partidas, mediana T{st.median(ult) if ult else '-'} (usuario: T9, Vronos -7)")

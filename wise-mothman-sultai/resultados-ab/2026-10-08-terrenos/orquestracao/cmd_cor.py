"""Por que o comandante (The Wise Mothman, {1}{B}{G}{U}) ainda nao foi conjurado no fim do turno T (4, 5, 6)? Classifica, entre as partidas em que ele NAO foi conjurado ate' o fim de T: (a) menos de 4 terrenos em campo (mana);
(b) >= 4 terrenos mas falta alguma das cores B / G / U (terrenos em campo, desvirados ou nao; fetch ainda nao usado nao conta; Sol Ring e pedras nao entram: piso); (c) >= 4 terrenos e as tres cores: nao conjurou por outro motivo
(prioridade, mana gasto na mesma fase). Simulador CONGELADO da lista atual, N sementes 3.000.000+i, modo padrao. Uso: python3 cmd_cor.py N saida.json.xz"""
import json, lzma, os, sys
os.environ["PYTHONHASHSEED"] = os.environ.get("PYTHONHASHSEED", "0")
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SIM = os.path.join(DECK, "resultados-ab/2026-10-08-terrenos/codigo/mothman_goldfish_v1_lista_atual.py")
N, saida = int(sys.argv[1]), os.path.abspath(sys.argv[2])
m = A.carrega(SIM, "cor_sim", DECK)
orig = m.play_turn; REC = []
def w(st):
    r = orig(st)
    ls = m.lands_in_play(st)
    cores = set()
    for l in ls: cores |= (m.eff_card(l).produces & set("BGU"))
    REC.append([st.turn, len(ls), "".join(sorted(cores)), 1 if st.commander_cast_turn is not None else 0])
    return r
m.play_turn = w
J = []
for i in range(N):
    REC.clear(); A.chama(m, "padrao", 3_000_000 + i, 12); J.append([list(x) for x in REC])
with lzma.open(saida, "wt", preset=9) as f:
    json.dump({"formato": "cor-v1: por partida, lista de [turno, terrenos em campo, cores B/G/U disponiveis nos terrenos, comandante ja' conjurado]", "n": N, "modo": "padrao", "sementes": "3000000+i", "jogos": J}, f)
print("ok", N)

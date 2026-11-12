"""Tamanho do cemiterio de CADA oponente no fim de cada turno meu (Drown in the Loch: 'mana value <= numero de cartas no cemiterio do CONTROLADOR do alvo', ou seja, o do oponente).
Simulador CONGELADO (mesmo do A/B). Mede so' o que o mill do MEU deck poe la: os oponentes do simulador sao passivos (sem magias proprias, sem criaturas mortas), entao e' PISO do cemiterio real.
Uso: python3 gy_opp.py <N> <padrao|resiliencia> <saida.json.xz>   (sementes 3.000.000+i)"""
import json, lzma, os, sys
os.environ["PYTHONHASHSEED"] = os.environ.get("PYTHONHASHSEED", "0")
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SIM = os.path.join(DECK, "resultados-ab/2026-10-08-pacote-e-interacao/codigo/mothman_goldfish_v1_estado_2026-10-08.py")
N, modo, saida = int(sys.argv[1]), sys.argv[2], os.path.abspath(sys.argv[3])      # absoluto ANTES de A.carrega (que faz chdir pro deck)
m = A.carrega(SIM, "gy_sim", DECK)
orig = m.play_turn
LOG = []
def wrapped(state):
    r = orig(state)
    LOG.append([state.turn, [[len(o.graveyard), 1 if o.eliminated else 0] for o in state.opps]])
    return r
m.play_turn = wrapped
jogos = []
for i in range(N):
    LOG.clear()
    A.chama(m, modo, 3_000_000 + i, 12)
    jogos.append([list(x) for x in LOG])
with lzma.open(saida, "wt", preset=9) as f:
    json.dump({"formato": "gy-v1: por partida, lista de [turno, [[cartas_no_cemiterio, eliminado]*3 oponentes]] no fim do MEU turno", "n": N, "modo": modo, "sementes": "3000000+i", "jogos": jogos}, f)
print("ok", N, modo, len(jogos), "jogos;", sum(len(j) for j in jogos), "turnos registrados")

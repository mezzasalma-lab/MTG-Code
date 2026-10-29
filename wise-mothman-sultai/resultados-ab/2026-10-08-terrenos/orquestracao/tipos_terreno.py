"""Quando um terreno 'check' (entra desvirado se voce controla um tipo) entraria desvirado? Em cada fim de turno T (1..5), a fracao das partidas em que ja' ha' em campo um terreno do tipo Swamp ou Forest (Woodland Cemetery), Island ou Swamp
(Drowned Catacomb), Forest ou Island (Hinterland Harbor). Os tipos vem do `land_types` do CARD_DB do simulador (basicos + Breeding Pool / Overgrown Tomb / Watery Grave / Zagoth Triome; um terreno buscado conta). Simulador CONGELADO da lista
atual, modo padrao, N sementes 3.000.000+i. Uso: python3 tipos_terreno.py N saida.json.xz"""
import json, lzma, os, sys
os.environ["PYTHONHASHSEED"] = os.environ.get("PYTHONHASHSEED", "0")
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SIM = os.path.join(DECK, "resultados-ab/2026-10-08-terrenos/codigo/mothman_goldfish_v1_lista_atual.py")
N, saida = int(sys.argv[1]), os.path.abspath(sys.argv[2])
m = A.carrega(SIM, "tipos_sim", DECK)
orig = m.play_turn; REC = []
def w(st):
    r = orig(st)
    ts = set()
    for l in m.lands_in_play(st): ts |= set(m.eff_card(l).land_types)
    REC.append([st.turn, len(m.lands_in_play(st)), sorted(ts)])
    return r
m.play_turn = w
J = []
for i in range(N):
    REC.clear(); A.chama(m, "padrao", 3_000_000 + i, 12); J.append([list(x) for x in REC])
with lzma.open(saida, "wt", preset=9) as f:
    json.dump({"formato": "tipos-v1: por partida, lista de [turno, terrenos em campo, tipos de terreno presentes]", "n": N, "modo": "padrao", "sementes": "3000000+i", "jogos": J}, f)
print("ok", N)

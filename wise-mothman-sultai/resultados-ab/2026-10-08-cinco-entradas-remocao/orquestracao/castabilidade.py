"""Quando as tres remocoes novas aparecem e quando sao conjuradas, e se o mana do deck sustenta BBGG (Casualties of War) e BG: variante s4 (Offer, Negate, V.A.T.S., Wave Goodbye, Didn't Say Please saem; as cinco entram),
simulador CONGELADO, N sementes 3.000.000+i, dois modos. Por partida: turno em que a carta foi vista pela 1a vez (mao / cemiterio no inicio ou fim de um turno meu), turno em que foi conjurada, e a cada fim de turno
quantos terrenos em campo produzem B / G e quantos terrenos ha' (o mana de pedras nao entra: piso). Uso: python3 castabilidade.py N padrao|resiliencia saida.json.xz"""
import json, lzma, os, sys
os.environ["PYTHONHASHSEED"] = os.environ.get("PYTHONHASHSEED", "0")
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SIM = os.path.join(DECK, "resultados-ab/2026-10-08-cinco-entradas-remocao/codigo/mothman_goldfish_v1_DEPOIS.py")
N, modo, saida = int(sys.argv[1]), sys.argv[2], os.path.abspath(sys.argv[3])
m = A.carrega(SIM, "cast_sim", DECK)
m.SWAPS = (("An Offer You Can't Refuse", "Agent Frank Horrigan"), ("Negate", "Branching Evolution"), ("V.A.T.S.", "Atomize"), ("Wave Goodbye", "Casualties of War"), ("Didn't Say Please", "Assassin's Trophy")); m.SWAP_IN_PLACE = True
NOVAS = ("Atomize", "Casualties of War", "Assassin's Trophy")
orig = m.play_turn
REC = []
def w(st):
    antes = {c: (c in st.hand or c in st.graveyard) for c in NOVAS}
    c0 = {c: st.casts_by_card.get(c, 0) for c in NOVAS}
    r = orig(st)
    lands = m.lands_in_play(st)
    b = sum(1 for l in lands if "B" in m.eff_card(l).produces); g = sum(1 for l in lands if "G" in m.eff_card(l).produces)
    vis = {c: (antes[c] or c in st.hand or c in st.graveyard) for c in NOVAS}
    REC.append([st.turn, len(lands), b, g, [int(vis[c]) for c in NOVAS], [st.casts_by_card.get(c, 0) - c0[c] for c in NOVAS]])
    return r
m.play_turn = w
jogos = []
for i in range(N):
    REC.clear()
    A.chama(m, modo, 3_000_000 + i, 12)
    jogos.append([list(x) for x in REC])
with lzma.open(saida, "wt", preset=9) as f:
    json.dump({"formato": "cast-v1: por partida, lista de [turno, terrenos, terrenos_B, terrenos_G, [visto Atomize, Casualties, Trophy], [casts neste turno]]", "n": N, "modo": modo, "variante": "s4 (cinco entradas; saem Offer, Negate, V.A.T.S., Wave Goodbye, Didn't Say Please)", "jogos": jogos}, f)
print("ok", N, modo)

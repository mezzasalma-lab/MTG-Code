"""Convencao (decidida pelo usuario em 2026-10-21): as cores dos terrenos dos 3 oponentes sao ALEATORIAS (sorteadas por semente: identidade de 2 cores por oponente; cada terreno produz uma delas).
Mede o que isso significa para a Exotic Orchard / Fellwar Stone (`a land an opponent controls could produce`): no inicio de cada turno meu, quais cores algum terreno de oponente produz.
Uso: python3 cores_disponiveis.py [N] (sementes 1_000_000+i; modo padrao; `simulate_one(seed, k)` roda k turnos meus, cada um seguido dos turnos dos oponentes)."""
import os, sys, collections, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, DECK)
import tam_goldfish_v1 as T
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
print(f"Cores que algum terreno de oponente produz no INICIO do meu turno k+1 (N = {N} sementes, 3 oponentes, identidade de 2 cores sorteada por oponente e cor sorteada por terreno)\n")
print("| início do turno | oponentes com >= 1 terreno | n.º médio de cores | P(>= 1 cor) | P(W) | P(U) | P(B) | P(R) | P(G) | P(as 5 cores) |")
print("|---|---|---|---|---|---|---|---|---|---|")
for k in (1, 2, 3, 4):
    ncor, com, anyc = [], [], 0
    pc = collections.Counter(); todas = 0
    for i in range(N):
        s = T.simulate_one(1_000_000 + i, k)
        cs = set(T.opp_land_colors(s))
        ncor.append(len(cs)); com.append(sum(1 for o in s.opps if o.land_colors))
        anyc += bool(cs); todas += (len(cs) == 5)
        for c in cs: pc[c] += 1
    print(f"| T{k + 1} | {st.mean(com):.2f} | {st.mean(ncor):.2f} | {100 * anyc / N:.1f}% | " + " | ".join(f"{100 * pc[c] / N:.1f}%" for c in "WUBRG") + f" | {100 * todas / N:.1f}% |")

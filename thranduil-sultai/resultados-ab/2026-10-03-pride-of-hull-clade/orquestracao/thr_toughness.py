"""Toughness total, fontes de U e mana por turno nas partidas-base do Thranduil (sem Pride). Mostra QUANDO a Pride custaria {G}
e quando a ativação {2}{U}{U} é paga. Sementes 3_000_000+i, N=6000."""
import json, sys, statistics as st
sys.path.insert(0, '.')
import thr_harness as H
T = H.T
# Fixa o simulador no comportamento de 2026-10-03: as chaves da varredura de 2026-10-05 (terreno virado primeiro, ordem deterministica) nao existiam quando esta tabela foi gerada.
for _k in ("TAPPED_LAND_FIRST_ENABLED", "DETERMINISTIC_SET_ORDER_ENABLED"):
    if hasattr(T, _k):
        setattr(T, _k, False)
N = 6000
rows = {t: [] for t in range(1, 9)}
for i in range(N):
    sd = 3_000_000 + i
    T.DECKLIST_TEXT = H.ORIG_DECKLIST
    import random
    rng = random.Random(sd)
    deck = T.parse_decklist(T.DECKLIST_TEXT); rng.shuffle(deck)
    state = T.GameState(rng=rng, library=deck)
    mull = 0
    while True:
        state.hand = []; state.draw(7, source="normal")
        if T.should_keep(state.hand) or mull >= 2: break
        mull += 1; state.library.extend(state.hand); state.hand = []; rng.shuffle(state.library)
    pen = max(0, mull - 1)
    if pen:
        for c in T.choose_bottom(state.hand, pen): state.hand.remove(c); state.library.append(c)
    gl = [[{}]]
    for t in range(1, 9):
        T.play_turn(state, t, gl)
        rows[t].append((H.total_toughness(state), T.color_sources(state, "U"), T.total_mana(state)))
out = {}
print("turno | toughness médio | P(>=10: Pride custa {G}) | P(>=7: custa <=4) | P(>=2 fontes de U) | mana total médio | P(mana>=4+1 e UU)")
for t in range(3, 9):
    r = rows[t]
    tt = [x[0] for x in r]; u2 = [x[1] >= 2 for x in r]
    p10 = sum(1 for x in tt if x >= 10) / N; p7 = sum(1 for x in tt if x >= 7) / N
    mana = [x[2] for x in r]
    pact = sum(1 for x in r if x[1] >= 2 and x[2] >= 5) / N
    print(f"T{t}   | {st.mean(tt):5.1f} | {100*p10:5.1f}% | {100*p7:5.1f}% | {100*st.mean(u2):5.1f}% | {st.mean(mana):5.1f} | {100*pact:5.1f}%")
    out[t] = {"tough_mean": st.mean(tt), "p_tough_ge10": p10, "p_tough_ge7": p7, "p_u2": st.mean(u2), "mana_mean": st.mean(mana), "p_u2_mana5": pact}

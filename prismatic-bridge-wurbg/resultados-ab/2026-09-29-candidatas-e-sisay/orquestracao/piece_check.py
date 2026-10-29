import sys, statistics as st
sys.path.insert(0, "/home/user/MTG-Code/prismatic-bridge-wurbg")
import prismatic_bridge_goldfish_v1 as pb

PAIR2 = {
    "Vraska+Vorinclex": ["Vraska, Betrayal's Sting", "Vorinclex, Monstrous Raider"],
    "Vraska+Innkeeper": ["Vraska, Betrayal's Sting", "Innkeeper's Talent"],
    "TTA+Chain Veil": ["Teferi, Temporal Archmage", "The Chain Veil"],
    "TWSS+Chain Veil": ["Teferi, Who Slows the Sunset", "The Chain Veil"],
    "TWSS+Dynamo": ["Teferi, Who Slows the Sunset", "The Peregrine Dynamo"],
}
first = {}
orig = pb.play_turn


def wrapped(state, turn, game_log, skip_legacy_removal=False):
    orig(state, turn, game_log, skip_legacy_removal=skip_legacy_removal)
    if turn == 1:
        first.clear()
    bf = set(state.battlefield)
    for c in ("Vorinclex, Monstrous Raider", "Vraska, Betrayal's Sting"):
        if c in bf and c not in first:
            first[c] = turn
    for k, pcs in PAIR2.items():
        if k not in first and all(p in bf for p in pcs):
            first[k] = turn


pb.play_turn = wrapped
N = 1500
a = b = both = 0
trig = []
hitspw = []
hitscr = []
union = {6: 0, 8: 0, 10: 0}
by_triggers = {"<=5": [0, 0], "6-10": [0, 0], ">10": [0, 0]}
for i in range(N):
    first.clear()
    r = pb.simulate_one(3_000_000 + i, 10, False)
    x = "Vorinclex, Monstrous Raider" in first
    y = "Vraska, Betrayal's Sting" in first
    a += x
    b += y
    both += x and y
    trig.append(r["bridge_triggers"])
    hitspw.append(r["bridge_hits_planeswalker"])
    hitscr.append(r["bridge_hits_creature"])
    ts = [first[k] for k in PAIR2 if k in first]
    for T in union:
        if ts and min(ts) <= T:
            union[T] += 1
    key = "<=5" if r["bridge_triggers"] <= 5 else ("6-10" if r["bridge_triggers"] <= 10 else ">10")
    by_triggers[key][0] += 1
    by_triggers[key][1] += ("Vraska+Vorinclex" in first)
print(f"P(Vorinclex em campo ate T10) {100*a/N:.1f}% | P(Vraska) {100*b/N:.1f}% | ambas {100*both/N:.1f}% | "
      f"independente seria {100*(a/N)*(b/N):.1f}%")
print(f"gatilhos da Bridge: media {st.mean(trig):.2f} mediana {st.median(trig)} p90 {sorted(trig)[int(.9*N)]} max {max(trig)} | "
      f"acertos PW {st.mean(hitspw):.2f} criatura {st.mean(hitscr):.2f}")
print("Vraska+Vorinclex por faixa de gatilhos da Bridge:", {k: (v[0], f'{100*v[1]/max(1,v[0]):.1f}%') for k, v in by_triggers.items()})
print("UNIAO dos 5 combos de 2 pecas (pecas juntas em campo):", {f"T{T}": f"{100*v/N:.1f}%" for T, v in union.items()})

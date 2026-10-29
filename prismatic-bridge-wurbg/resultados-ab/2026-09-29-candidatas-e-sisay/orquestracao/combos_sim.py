import sys, json, math
sys.path.insert(0, "/home/user/MTG-Code/prismatic-bridge-wurbg")
import prismatic_bridge_goldfish_v1 as pb
COMBOS = {
 "Vraska+Vorinclex (oponente perde)": ["Vraska, Betrayal's Sting", "Vorinclex, Monstrous Raider"],
 "Vraska+Innkeeper's Talent (oponente perde)": ["Vraska, Betrayal's Sting", "Innkeeper's Talent"],
 "TTA+Chain Veil (infinito)": ["Teferi, Temporal Archmage", "The Chain Veil"],
 "TWSS+Chain Veil (infinito)": ["Teferi, Who Slows the Sunset", "The Chain Veil"],
 "TWSS+Peregrine Dynamo (infinito)": ["Teferi, Who Slows the Sunset", "The Peregrine Dynamo"],
 "TTA+Chain Veil+Carth": ["Teferi, Temporal Archmage", "The Chain Veil", "Carth the Lion"],
 "Aminatou+Bolas+Oath of Teferi": ["Aminatou, the Fateshifter", "Nicol Bolas, Dragon-God", "Oath of Teferi"],
 "Aminatou+Bolas+Chain Veil": ["Aminatou, the Fateshifter", "Nicol Bolas, Dragon-God", "The Chain Veil"],
}
first = {}
orig = pb.play_turn
def wrapped(state, turn, game_log, skip_legacy_removal=False):
    orig(state, turn, game_log, skip_legacy_removal=skip_legacy_removal)
    if turn == 1:
        first.clear()
    bf = set(state.battlefield)
    for k, pcs in COMBOS.items():
        if k not in first and all(p in bf for p in pcs):
            first[k] = turn
pb.play_turn = wrapped
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
cum = {k: {6: 0, 8: 0, 10: 0} for k in COMBOS}
elim = 0
for i in range(N):
    first.clear()
    r = pb.simulate_one(3_000_000 + i, 10, False)
    for k, t in first.items():
        for T in (6, 8, 10):
            if t <= T: cum[k][T] += 1
    if r["opp_eliminated_total"] > 0: elim += 1
print(f"N={N}  (turnos: T e' o turno em que AS PECAS JA' ESTAO JUNTAS EM CAMPO; nao mede se o loop executa)")
def hyp(k, n): return k * (k - 1) / (99 * 98) if k == 2 else None
for k, pcs in COMBOS.items():
    row = " ".join(f"T{T}: {100*cum[k][T]/N:5.2f}%" for T in (6, 8, 10))
    h = ""
    if len(pcs) == 2:
        h = " | hipergeometrica so' por compra (7+T cartas): " + " ".join(f"T{T}: {100*(7+T)*(6+T)/(99*98):.2f}%" for T in (6, 8, 10))
    print(f"{k:46s} {row}{h}")
print(f"partidas em que algum oponente foi eliminado por veneno ate' T10 (Vraska -9): {100*elim/N:.2f}%")

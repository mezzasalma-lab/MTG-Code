"""Quando as pecas dos combos do Commander Spellbook estao JUNTAS em campo (Regra 7 de user-standing-rules.md).
Uso: python3 combos_probabilidade.py [N]
Mede no goldfish padrao (10 turnos), por turno, o 1o turno em que todas as pecas do combo estao em campo. NAO mede
se o loop executa (so' o Vraska -9 com Vorinclex/Innkeeper e' executado pelo simulador). Compara com a
hipergeometrica "so' por compra" ((7+T)(6+T)/(99*98) pra 2 pecas): a Bridge poe pecas em campo sem comprar,
entao o numero real e' maior, e a cauda (partidas com dezenas de gatilhos) pesa."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prismatic_bridge_goldfish_v1 as pb

PAIRS = {
    "Vraska + Vorinclex": ["Vraska, Betrayal's Sting", "Vorinclex, Monstrous Raider"],
    "Vraska + Innkeeper's Talent": ["Vraska, Betrayal's Sting", "Innkeeper's Talent"],
    "TTA + Chain Veil": ["Teferi, Temporal Archmage", "The Chain Veil"],
    "TWSS + Chain Veil": ["Teferi, Who Slows the Sunset", "The Chain Veil"],
    "TWSS + Peregrine Dynamo": ["Teferi, Who Slows the Sunset", "The Peregrine Dynamo"],
}
first = {}
_orig = pb.play_turn


def _wrapped(state, turn, game_log, skip_legacy_removal=False):
    _orig(state, turn, game_log, skip_legacy_removal=skip_legacy_removal)
    if turn == 1:
        first.clear()
    bf = set(state.battlefield)
    for k, pcs in PAIRS.items():
        if k not in first and all(p in bf for p in pcs):
            first[k] = turn


pb.play_turn = _wrapped
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
cum = {k: {6: 0, 8: 0, 10: 0} for k in PAIRS}
union = {6: 0, 8: 0, 10: 0}
elim = 0
for i in range(N):
    first.clear()
    r = pb.simulate_one(3_000_000 + i, 10, False)
    for k, t in first.items():
        for T in cum[k]:
            cum[k][T] += t <= T
    if first:
        for T in union:
            union[T] += min(first.values()) <= T
    elim += r["opp_eliminated_total"] > 0
print(f"N={N} partidas; % com as pecas juntas em campo ate' o turno T")
for k in PAIRS:
    print(f"{k:30s} " + " ".join(f"T{T}: {100 * cum[k][T] / N:5.2f}%" for T in (6, 8, 10)))
print(f"{'UNIAO dos 5 pares':30s} " + " ".join(f"T{T}: {100 * union[T] / N:5.2f}%" for T in (6, 8, 10)))
print("hipergeometrica so' por compra (2 pecas): " + " ".join(f"T{T}: {100 * (7 + T) * (6 + T) / (99 * 98):.2f}%" for T in (6, 8, 10)))
print(f"algum oponente eliminado por veneno ate' o T10: {100 * elim / N:.2f}%")

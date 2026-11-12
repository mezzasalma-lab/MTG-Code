"""Smoke test do simulador DEPOIS (Megatron, 2a rodada). Uso: python3 smoke.py"""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
M = F.carrega(F.DEPOIS, "meg_smoke2")
cnt = Counter(M.BASE_LIBRARY)
print("cartas na biblioteca:", len(M.BASE_LIBRARY), "| distintas:", len(cnt))
print("desconhecidas (fora do CARD_DB):", [n for n in cnt if n not in M.CARD_DB])
print("duplicadas nao-basicas:", [n for n, k in cnt.items() if k > 1 and n not in ("Mountain", "Plains", "Swamp")])
print("terrenos:", sum(k for n, k in cnt.items() if n in M.LAND_NAMES), "| fetch lands na lista:", sorted(n for n in M.FETCH_LANDS if n in cnt))
print("flags:", M.MULLIGAN_BOTTOM_MODE, M.FETCHLANDS_ENABLED, M.TAPPED_LAND_FIRST_ENABLED, M.MYRIAD_ABILITY_ENABLED)
s = [M.simulate_one(1_000_000 + i) for i in range(200)]
print("200 partidas sem excecao | com fetch sacrificado: %d | com Myriad ativado: %d" % (
    sum(1 for x in s if x.fetch_cracks_total), sum(1 for x in s if x.myriad_activations_total)))

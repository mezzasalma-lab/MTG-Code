"""Smoke test do simulador DEPOIS (Vihaan): contagem de cartas, desconhecidas, duplicadas, terrenos + 200 partidas. Uso: python3 smoke.py"""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
V = F.carrega(F.DEPOIS, "vih_smoke")
cnt = Counter(V.BASE_LIBRARY)
print("cartas na biblioteca:", len(V.BASE_LIBRARY), "| distintas:", len(cnt))
print("desconhecidas (fora do CARD_DB):", [n for n in cnt if n not in V.CARD_DB])
basicos = ("Mountain", "Plains", "Swamp")
print("duplicadas nao-basicas:", [n for n, k in cnt.items() if k > 1 and n not in basicos])
print("terrenos:", sum(k for n, k in cnt.items() if n in V.LAND_NAMES), "| basicos:", {n: cnt[n] for n in basicos})
print("flags:", V.ANIMATED_TREASURE_ROUTING_ENABLED, V.MULLIGAN_SMART_BOTTOM_ENABLED, V.TAPPED_LAND_FIRST_ENABLED, V.TAPPED_LAND_FIRST_MAX_TURN, V.TAPPED_LAND_FIRST_SKIP_IF_LOSES_PLAY)
s = [V.simulate_one(1_000_000 + i) for i in range(200)]
print("200 partidas sem excecao | partidas com animados sacrificados como criatura: %d" % sum(1 for x in s if x.animated_treasures_sacrificed_any_total))

"""Confere `LAND_COLORS` do simulador (cores W/B/R que cada terreno produz, usadas SO' pela Mythos) contra o `produced_mana` ao vivo do Scryfall (cache cru da rodada dos wipes de sacrificio:
../../2026-10-04-wipes-de-sacrificio/dados/oraculo_lista_ao_vivo.json.xz; faces somadas) para os 29 terrenos distintos da biblioteca, e conta as fontes de W, B e R (copias). Uso: python3 confere_cores.py"""
import collections, json, lzma, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
V = F.flags(F.carrega(F.DEPOIS, "vih_cores"))
c = json.load(lzma.open(os.path.join(F.DECK, "resultados-ab", "2026-10-04-wipes-de-sacrificio", "dados", "oraculo_lista_ao_vivo.json.xz"), "rt"))
cnt = collections.Counter(V.BASE_LIBRARY)
lands = sorted(n for n in cnt if n in V.LAND_NAMES)
print("terrenos distintos na biblioteca:", len(lands), "| copias:", sum(cnt[n] for n in lands), "| fora do LAND_COLORS:", [n for n in lands if n not in V.LAND_COLORS])
bad = []
for n in lands:
    prod = set(c[n].get("produced_mana") or [])
    for f in c[n].get("card_faces", []):
        prod |= set(f.get("produced_mana") or [])
    esperado = "".join(x for x in "WBR" if x in prod)
    if set(V.LAND_COLORS[n]) != set(esperado):
        bad.append((n, V.LAND_COLORS[n], esperado))
print("divergencias LAND_COLORS x produced_mana ao vivo:", bad)
for cor in "WBR":
    ns = [n for n in lands if cor in V.LAND_COLORS[n]]
    print(f"fontes de {cor} entre os terrenos: {sum(cnt[n] for n in ns)} copias em {len(ns)} nomes (+ Arcane Signet e Treasures, qualquer cor)")

#!/usr/bin/env python3
"""Fontes de mana por cor (B / G / U) da lista atual e de cada troca 'terreno X -> Underground Sea', lidas do CARD_DB do simulador CONGELADO `codigo/mothman_goldfish_v1_ANTES.py` (a lista e' o DECKLIST_TEXT dele). Diretas = terrenos
que produzem a cor; efetivas = diretas + cada fetch contada nas cores dos tipos que ela busca (Misty: G e U; Polluted Delta: U e B; Verdant: B e G) + Prismatic Vista (uma fonte de cada cor, ha' basicos das tres) -- o mesmo criterio
de `../../2026-10-08-terrenos/orquestracao/analise_terrenos.py`. Plaza of Heroes (cor so' para magia lendaria) nao conta. Uso: python3 fontes_por_cor.py > ../resumos/fontes_por_cor.md"""
import collections, importlib.util, json, os
AQUI = os.path.dirname(os.path.abspath(__file__)); ARQ = os.path.abspath(os.path.join(AQUI, "..")); DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
os.chdir(DECK)
sp = importlib.util.spec_from_file_location("mm", os.path.join(ARQ, "codigo", "mothman_goldfish_v1_ANTES.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
CD = m.CARD_DB; cfg = json.load(open(os.path.join(AQUI, "config_u.json")))
FETCH = {"Misty Rainforest": "GU", "Polluted Delta": "UB", "Verdant Catacombs": "BG"}
def fontes(lib):
    c = collections.Counter(lib); direto = collections.Counter(); ef = collections.Counter()
    for n, q in c.items():
        if "land" not in CD[n].types: continue
        for col in CD[n].produces & set("BGU"): direto[col] += q
    ef.update(direto)
    for f, cols in FETCH.items():
        if f in c:
            for col in cols: ef[col] += c[f]
    if "Prismatic Vista" in c:
        for col in "BGU": ef[col] += 1
    nland = sum(q for n, q in c.items() if "land" in CD[n].types)
    return direto, ef, nland
print("| troca (sai → Underground Sea) | terrenos | fontes diretas B / G / U | fontes efetivas B / G / U |\n|---|---|---|---|")
for nome, v in cfg["variantes"].items():
    m.SWAPS = tuple(tuple(p) for p in v.get("SWAPS", [])); m.SWAP_IN_PLACE = bool(v.get("SWAP_IN_PLACE", False))
    d, e, nl = fontes(m.current_library())
    rot = "(lista atual)" if nome == "base" else v["SWAPS"][0][0]
    print(f"| {rot} | {nl} | {d['B']} / {d['G']} / {d['U']} | {e['B']} / {e['G']} / {e['U']} |")
m.SWAPS = (("Urza's Saga", "Underground Sea"),); m.SWAP_IN_PLACE = True
d, e, nl = fontes(m.current_library()); print(f"| Urza's Saga | {nl} | {d['B']} / {d['G']} / {d['U']} | {e['B']} / {e['G']} / {e['U']} |")

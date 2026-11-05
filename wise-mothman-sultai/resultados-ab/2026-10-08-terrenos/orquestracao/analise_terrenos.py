#!/usr/bin/env python3
"""Analise ESTATICA da base de mana do Mothman (lista aplicada em 2026-10-08), so' a partir do CARD_DB do simulador e do cache do Scryfall: (a) terrenos e fontes por cor (fetch contado nas cores que alcanca com os alvos
que ESTAO na lista); (b) exigencia de pips por cor das 63 nao-terrenos; (c) hipergeometrica: P(>= k fontes da cor entre as cartas vistas ate' o turno T, na compra, sem mulligan). Uso: python3 analise_terrenos.py > ../resumos/analise_terrenos.md"""
import importlib.util, os, collections, math, json
DECK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
os.chdir(DECK)
sp = importlib.util.spec_from_file_location("mm", "mothman_goldfish_v1.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
lib = collections.Counter(m.current_library()); CD = m.CARD_DB
lands = {n: q for n, q in lib.items() if "land" in CD[n].types}
nl = sum(lands.values()); total = sum(lib.values())
# --- fontes por cor
direto = collections.Counter(); 
for n, q in lands.items():
    for c in CD[n].produces:
        if c in "BGU": direto[c] += q
# tipos de terreno alcancaveis por fetch (alvos que estao na lista)
tipo = {"Forest": {"Forest": 5, "Breeding Pool": 1, "Overgrown Tomb": 1, "Zagoth Triome": 1},
        "Island": {"Island": 4, "Breeding Pool": 1, "Watery Grave": 1, "Zagoth Triome": 1},
        "Swamp": {"Swamp": 3, "Overgrown Tomb": 1, "Watery Grave": 1, "Zagoth Triome": 1}}
for t, d in tipo.items():
    for nome in d: assert nome in lands, nome
fetch = {"Misty Rainforest": ("Forest", "Island"), "Polluted Delta": ("Island", "Swamp"), "Verdant Catacombs": ("Swamp", "Forest")}
cor_de = {"Forest": "G", "Island": "U", "Swamp": "B"}
efetivo = collections.Counter(direto)
for f, ts in fetch.items():
    for t in ts: efetivo[cor_de[t]] += 1
for c in "BGU": efetivo[c] += 1           # Fabled Passage: qualquer basico (tapped)
print(f"## Terrenos ({nl} no baralho de {total}; Sol Ring a parte)\n")
print("| fontes por cor | B | G | U |\n|---|---|---|---|")
print(f"| diretas (terrenos que produzem a cor) | {direto['B']} | {direto['G']} | {direto['U']} |")
print(f"| efetivas (+ 3 fetches pelos tipos que alcancam + Fabled Passage) | {efetivo['B']} | {efetivo['G']} | {efetivo['U']} |")
inc = [n for n in lands if not CD[n].produces and "fetch" not in CD[n].tags and "saga" not in CD[n].tags]
print(f"\nTerrenos que NAO produzem cor: {[ (n, sorted(CD[n].produces)) for n, q in lands.items() if not (CD[n].produces & set('BGU')) and 'fetch' not in CD[n].tags]}")
print("\nEntram virados (ou condicionais): Zagoth Triome (sempre), Bojuka Bog (sempre), Fabled Passage (o terreno buscado), Morphic Pool / Rejuvenating Springs / Undergrowth Stadium (virados salvo 2+ oponentes: aqui 3 oponentes, entram desvirados), Shifting Woodland (salvo Forest), shocks (2 de vida ou virado), Agadeem (3 de vida ou virado).\n")
# --- pips por cor
exig = {c: collections.Counter() for c in "BGU"}; cartas_cor = {c: [] for c in "BGU"}
for n, q in lib.items():
    c = CD[n]
    if "land" in c.types: continue
    pips = [set(p) for p in c.pips]
    for col in "BGU":
        so = sum(1 for p in pips if p == {col})                  # pips que EXIGEM a cor (nao hibridos)
        if so: exig[col][min(so, 4)] += 1; cartas_cor[col].append((n, so, c.mv))
print("## Exigencia de cor das nao-terrenos (pips que exigem a cor; hibridos G/U nao contam)\n")
print("| cor | cartas com ≥1 pip | com ≥2 pips | com ≥3 pips |\n|---|---|---|---|")
for col in "BGU":
    n1 = sum(exig[col].values()); n2 = sum(v for k, v in exig[col].items() if k >= 2); n3 = sum(v for k, v in exig[col].items() if k >= 3)
    print(f"| {col} | {n1} | {n2} | {n3} |")
print("\nCartas com 2+ pips da mesma cor:")
for col in "BGU":
    print(f"- {col}: " + ", ".join(f"{n} ({s}×{col}, MV {mv})" for n, s, mv in sorted(cartas_cor[col], key=lambda x: (-x[1], x[2])) if s >= 2))
print(f"\nComandante The Wise Mothman: {{1}}{{B}}{{G}}{{U}} (precisa das TRES cores no T4). Casualties of War {{2}}{{B}}{{B}}{{G}}{{G}}; Nuclear Fallout {{X}}{{B}}{{B}}; Agadeem's Awakening {{X}}{{B}}{{B}}{{B}}; Agent Frank Horrigan {{5}}{{B}}{{G}}.\n")
# --- hipergeometrica
def hyp_ge(N, K, n, k):
    return sum(math.comb(K, i) * math.comb(N - K, n - i) for i in range(k, min(K, n) + 1)) / math.comb(N, n)
print("## Hipergeométrica: P(≥ k fontes da cor entre as cartas vistas até o turno T) — baralho de 99, 7 cartas + 1 compra por turno a partir do T2 (sem mulligan); 'efetivas' = fetch conta nas cores que alcança\n")
print("| fontes S | ≥1 até T2 | ≥1 até T3 | ≥1 até T4 | ≥2 até T5 | ≥2 até T6 | ≥2 até T7 | ≥2 até T8 |\n|---|---|---|---|---|---|---|---|")
for S in (13, 14, 15, 16, 17, 18, 19, 20):
    row = []
    for k, T in ((1, 2), (1, 3), (1, 4), (2, 5), (2, 6), (2, 7), (2, 8)):
        row.append(f"{100 * hyp_ge(99, S, 7 + T - 1, k):.0f}%")
    mark = " ← B / U efetivas" if S == efetivo["B"] else (" ← G efetivas" if S == efetivo["G"] else "")
    print(f"| {S}{mark} | " + " | ".join(row) + " |")
print("\n(Aproximação: ignora fetch afinando o baralho, Nature's Lore / Three Visits / Gyre Sage / Kami e Sol Ring; é piso para a cor, não modelo do jogo. O modelo do jogo está na medição do simulador.)")

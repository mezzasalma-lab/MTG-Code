#!/usr/bin/env python3
"""Inclusao de cada carta nos decks do Moxfield (bracket 3; bracket 3 com 22+ planeswalkers; todos), SEM o proprio deck do usuario, e onde cada carta esta no nosso registro (deck / sideboard / fora). Le so' dos dados arquivados.
Uso: python3 inclusao_cartas.py > ../resumos/inclusao_cartas.md"""
import json, lzma, os, re, collections
AQUI = os.path.dirname(os.path.abspath(__file__)); ARQ = os.path.abspath(os.path.join(AQUI, "..")); DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
O = json.load(lzma.open(os.path.join(ARQ, "dados", "oraculos_referencia.json.xz"), "rt")); cache = json.load(open(os.path.join(DECK, "..", "scryfall-cache", "oracle-cache.json"), encoding="utf-8"))
decks = [json.loads(l) for l in lzma.open(os.path.join(ARQ, "dados", "decks_edhrec.jsonl.xz"), "rt", encoding="utf-8")]
L = open(os.path.join(DECK, "lista.md"), encoding="utf-8").read(); main = set(re.findall(r"^1 (.+)$", L.split("## Sideboard")[0], re.M)); side = set(re.findall(r"^1 (.+)$", L.split("## Sideboard")[1], re.M)); nosso = main | {"Tam, the Possibility"}
def S(r): return {n for t, l in r["cards"].items() for n, q in l}
FRENTE = {k.split(" // ")[0]: k for k in list(O) + list(cache) if " // " in k}
def info(n): return O.get(n) or cache.get(n) or O.get(FRENTE.get(n, "")) or cache.get(FRENTE.get(n, ""))
def nl(r): return {n for n in S(r) if n != "Tam, the Possibility" and "Land" not in info(n)["type_line"].split("—")[0]}
NOSSO_NL = {n for n in main if n != "Tam, the Possibility" and "Land" not in info(n)["type_line"].split("—")[0]}
mox = [r for r in decks if "moxfield" in (r.get("url") or "") and nl(r) != NOSSO_NL]      # fora: o proprio deck do usuario, ja' publicado (mesmas 63 cartas nao-terreno)
b3 = [r for r in mox if r["bracket"] == 3]; b3pw = [r for r in b3 if (r["tipos"]["planeswalker"] or 0) >= 22]
def incl(D):
    c = collections.Counter()
    for r in D: c.update(S(r))
    return {k: v / len(D) for k, v in c.items()}
iB3, iPW, iAll = incl(b3), incl(b3pw), incl(mox)
BAS = {"Plains", "Island", "Swamp", "Mountain", "Forest"}
print("# Inclusão das cartas nos decks do Moxfield (sem o nosso)\n")
print(f"Decks: todos {len(mox)}, bracket 3: {len(b3)}, bracket 3 com 22+ planeswalkers: {len(b3pw)}.\n")
print("## Cartas que os decks do Moxfield (bracket 3) jogam em ≥ 30% e que NÃO estão no nosso deck\n\n| carta | B3 | B3 e 22+ PW | todos | tipo | MV | Game Changer | onde está no nosso registro |\n|---|---|---|---|---|---|---|---|")
for n in sorted(iB3, key=lambda n: (-iB3[n], n)):
    if iB3[n] < 0.30: break
    if n in main or n == "Tam, the Possibility" or n in BAS: continue
    c = info(n); print(f"| {n} | {100 * iB3[n]:.0f}% | {100 * iPW.get(n, 0):.0f}% | {100 * iAll[n]:.0f}% | {c['type_line'].split('—')[0].strip()} | {int(c['cmc'])} | {'**SIM**' if (O.get(n) or {}).get('game_changer') else 'não'} | {'sideboard' if n in side else 'fora'} |")
print("\n## Cartas do nosso deck com baixa inclusão (< 15% nos decks B3 do Moxfield), não-terrenos e terrenos\n\n| carta | B3 | B3 e 22+ PW | tipo |\n|---|---|---|---|")
for n in sorted(main, key=lambda n: (iB3.get(n, 0), n)):
    if n in BAS: continue
    if iB3.get(n, 0) >= 0.15: break
    print(f"| {n} | {100 * iB3.get(n, 0):.0f}% | {100 * iPW.get(n, 0):.0f}% | {info(n)['type_line'].split('—')[0].strip()} |")
print("\n## Cartas do nosso deck com alta inclusão (≥ 50% no B3)\n")
print(", ".join(f"{n} ({100 * iB3[n]:.0f}%)" for n in sorted(main, key=lambda n: (-iB3.get(n, 0), n)) if iB3.get(n, 0) >= 0.50))
print("\n\nInclusão (B3 / B3 e 22+ PW) das cartas das trocas propostas:\n\n| carta | B3 | B3 e 22+ PW |\n|---|---|---|")
for n in ("Swords to Plowshares", "Oath of Ajani", "Doubling Season", "Commodore Guff", "Karn's Bastion", "Mutational Advantage", "Leyline Immersion", "Staff of Compleation", "Domri, Chaos Bringer", "Teferi's Talent", "Baxter Building", "Liliana's Talent", "Carth the Lion", "Nicol Bolas, Dragon-God", "Countersculpt", "Jace's Machinations", "Loyal Tutor", "Path to Exile", "Teferi, Master of Time"):
    print(f"| {n} | {100 * iB3.get(n, 0):.0f}% | {100 * iPW.get(n, 0):.0f}% |")

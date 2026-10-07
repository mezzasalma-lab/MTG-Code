#!/usr/bin/env python3
"""Regra #4 item 4: enumera POR SCRIPT (oraculo do cache, lista.md) as cartas que satisfazem cada condicao que o Jace, Wielder of Mysteries toca: compras (vitoria com biblioteca vazia), auto-mill,
cartas que DEVOLVEM cartas a biblioteca (anti-sinergia com a vitoria por biblioteca vazia: Kozilek), planeswalkers, e as fontes de {U} (o Jace custa {1}{U}{U}{U}). Uso: python3 enumera_condicoes_jace.py > ../resumos/enumeracao_condicoes.txt"""
import json, os, re, sys, collections
A = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(A, "..", "..", "..", ".."))
sys.path.insert(0, A); import gera_config as G
c = json.load(open(os.path.join(ROOT, "scryfall-cache", "oracle-cache.json")))
copias = collections.Counter()                       # G.lista() ignora a coluna de quantidade (basicos): conto direto da lista.md
_sec = None
for _l in open(os.path.join(ROOT, "wise-mothman-sultai", "lista.md"), encoding="utf-8"):
    _l = _l.rstrip("\n")
    if _l.startswith("## "): _sec = _l[3:].strip(); continue
    _m = re.match(r"^(\d+) (.+)$", _l.strip())
    if _m and _sec == "Deck": copias[_m.group(2).strip()] += int(_m.group(1))
nomes = list(copias)
T = lambda n: c[n].get("oracle_text") or ""; TL = lambda n: c[n].get("type_line") or ""
print(f"cartas distintas lidas: {len(nomes)} ({sum(copias.values())} copias; 99 + comandante), sem oraculo no cache: {[n for n in nomes if n not in c]}")
def lista(titulo, f):
    hit = [n for n in nomes if f(n)]
    print(f"\n## {titulo} [{len(hit)}]"); [print("  -", n, "|", TL(n)) for n in hit]
lista("COMPRA (cada compra com a biblioteca vazia e o Jace em campo vira vitoria)", lambda n: re.search(r"\bdraws?\b (a|an additional|two|three|four|that many|cards)|you may draw|draw (a|two|three|four|seven) cards?", T(n), re.I) is not None and "Land" not in TL(n).split("—")[0])
lista("AUTO-MILL possivel ('you mill', 'target player mills', 'each player mills', X cartas, mill do rad)", lambda n: re.search(r"mill (a|two|three|four|five|seven|X|\d+) cards?|target player mills|each player mills|you mill|mills? (that many|cards equal)|rad counter", T(n), re.I) is not None)
lista("DEVOLVE cartas a BIBLIOTECA / embaralha o cemiterio (ANTI-sinergia com esvaziar a biblioteca)", lambda n: re.search(r"(into|on top of|on the bottom of) (its owner's|your|their) library|shuffle[s]? (your|their|its owner's) graveyard|shuffles? .* graveyard into", T(n), re.I) is not None)
lista("PLANESWALKERS", lambda n: "Planeswalker" in TL(n))
def fonte_u(n):
    t = TL(n)
    if "Land" not in t: return False
    if re.search(r"search your library for a[^.]*\b(Island|basic land)", T(n), re.I): return True        # fetch que pode buscar Island
    return "Island" in t or re.search(r"add (one mana of any color|\{U\}|[^.]*\{U\})|any color|any type", T(n), re.I) is not None
print("\n## FONTES DE {U} entre os terrenos (por script; copias contadas)")
tot = 0
for n in nomes:
    if fonte_u(n):
        tot += copias[n]; print(f"  - {n} x{copias[n]} | {TL(n)}")
print(f"  total de copias de terreno que produzem {{U}}: {tot} de {sum(copias[n] for n in nomes if 'Land' in TL(n))} terrenos (o MDFC Agadeem conta como terreno so' pelo lado terreno)")

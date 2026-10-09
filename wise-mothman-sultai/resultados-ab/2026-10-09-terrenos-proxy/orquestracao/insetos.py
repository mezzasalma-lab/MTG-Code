import re, json, urllib.request, urllib.parse, sys
"""Enumera POR SCRIPT, no Scryfall ao vivo, as cartas da lista com tipo Insect / Rat / Spider / Squirrel (os alvos da Swarmyard), Changeling / Kindred / "every creature type" e textos que criam ficha ou mudam tipo desses (Regra #4, adendo item 4).
Cartas de 2 faces / aventura que o /cards/collection nao acha pelo nome composto sao buscadas por /cards/named?fuzzy. Uso (de dentro de wise-mothman-sultai/): python3 resultados-ab/2026-10-09-terrenos-proxy/orquestracao/insetos.py <saida.json>"""
import os
OUT = sys.argv[1]
lista = open("lista.md", encoding="utf-8").read().splitlines()
nomes = []
for l in lista:
    m = re.match(r"^(\d+)x?\s+(.+?)\s*$", l.strip())
    if m: nomes.append((int(m.group(1)), m.group(2)))
nm = [n for _, n in nomes]
print("linhas:", len(nm), "cartas (com basicos):", sum(q for q, _ in nomes))
def post(ids):
    req = urllib.request.Request("https://api.scryfall.com/cards/collection", data=json.dumps({"identifiers": [{"name": n} for n in ids]}).encode(), headers={"Content-Type": "application/json", "User-Agent": "mtg-code/1.0", "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req))
cards = {}; nf = []
for i in range(0, len(nm), 70):
    r = post(nm[i:i+70]); nf += r.get("not_found", [])
    for c in r["data"]: cards[c["name"]] = c
print("encontradas no lote:", len(cards), "| nao encontradas no lote (buscadas por fuzzy):", [x["name"] for x in nf])
for x in nf:
    d = json.load(urllib.request.urlopen(urllib.request.Request("https://api.scryfall.com/cards/named?fuzzy=" + urllib.parse.quote(x["name"].split(" // ")[0]), headers={"User-Agent": "mtg-code/1.0", "Accept": "application/json"})))
    cards[d["name"]] = d
print("total resolvido:", len(cards), "de", len(nm), "nomes distintos (0 = vacuo)")
assert len(cards) == len(nm), (len(cards), len(nm))
json.dump(cards, open(OUT, "w"), ensure_ascii=False, indent=0, sort_keys=True)
TIPOS = ["Insect", "Rat", "Spider", "Squirrel"]
def faces(c):
    return c.get("card_faces") or [c]
print()
for t in TIPOS:
    print("=== tipo", t, "(type_line, qualquer face)")
    for n, c in sorted(cards.items()):
        for f in faces(c):
            tl = f.get("type_line", c.get("type_line", ""))
            if re.search(r"\b" + t + r"\b", tl): print(" -", n, "|", tl, "|", f.get("power"), "/", f.get("toughness"), "| MV", c.get("cmc")); break
print("\n=== Changeling / 'every creature type' / Kindred (conta em toda zona)")
for n, c in sorted(cards.items()):
    for f in faces(c):
        ot = f.get("oracle_text", ""); kw = c.get("keywords", [])
        if "Changeling" in kw or "every creature type" in ot or "Kindred" in f.get("type_line", ""):
            print(" -", n, "|", f.get("type_line"), "|", ot.replace("\n", " / ")[:160]); break
print("\n=== cria ficha Insect/Rat/Spider/Squirrel ou muda tipo (texto do oraculo)")
for n, c in sorted(cards.items()):
    for f in faces(c):
        ot = f.get("oracle_text", "")
        if re.search(r"(Insect|Rat|Spider|Squirrel|Hornet|Wasp|Bee\b|Beetle|Ant\b)", ot) and ("token" in ot or "becomes" in ot or "is a" in ot or "in addition" in ot):
            print(" -", n, "|", ot.replace("\n", " / ")[:220]); break
print("\n=== quem 'cuida' de Inseto no texto (Insect em oraculo, nao so type_line)")
for n, c in sorted(cards.items()):
    for f in faces(c):
        ot = f.get("oracle_text", "")
        if re.search(r"\bInsects?\b", ot): print(" -", n, "|", ot.replace("\n", " / ")[:220]); break

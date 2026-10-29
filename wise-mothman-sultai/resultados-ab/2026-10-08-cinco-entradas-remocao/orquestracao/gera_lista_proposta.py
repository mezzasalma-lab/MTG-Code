"""Gera a lista PROPOSTA (conjunto s4: saem Offer, Negate, V.A.T.S., Wave Goodbye, Didn't Say Please; entram Agent Frank Horrigan, Branching Evolution, Atomize, Casualties of War, Assassin's Trophy) a partir de
`lista.md` SEM alterar `lista.md`. Confere: 99 cartas no deck, cada saida existia, cada entrada nao existia, legalidade em Commander e identidade de cor dentro de B/G/U (scryfall-cache). Uso: python3 gera_lista_proposta.py"""
import json, os, re, collections
AQUI = os.path.dirname(os.path.abspath(__file__)); DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SAEM = ["An Offer You Can't Refuse", "Negate", "V.A.T.S.", "Wave Goodbye", "Didn't Say Please"]
ENTRAM = ["Agent Frank Horrigan", "Branching Evolution", "Atomize", "Casualties of War", "Assassin's Trophy"]
cache = json.load(open(os.path.join(DECK, "..", "scryfall-cache", "oracle-cache.json")))
linhas = open(os.path.join(DECK, "lista.md"), encoding="utf-8").read().split("\n")
sec = None; deck = collections.Counter(); cab = []; cmd = []
for l in linhas:
    if l.startswith("## "): sec = l[3:].strip().lower()
    m = re.match(r"^(\d+)\s+(.+)$", l)
    if m and sec == "deck": deck[m.group(2).strip()] += int(m.group(1))
    elif m and sec == "comandante": cmd.append(m.group(2).strip())
assert sum(deck.values()) == 99 and cmd == ["The Wise Mothman"], (sum(deck.values()), cmd)
for c in SAEM: assert deck[c] == 1, c
for c in ENTRAM: assert deck[c] == 0, c
for c in SAEM: del deck[c]
for c in ENTRAM:
    deck[c] += 1; d = cache[c]
    assert d["legalities"]["commander"] == "legal" and set(d["color_identity"]) <= {"B", "G", "U"}, (c, d["legalities"]["commander"], d["color_identity"])
assert sum(deck.values()) == 99
i0 = next(i for i, l in enumerate(linhas) if l.strip() == "## Deck")
cab = linhas[:i0 + 2]
corpo = [f"{q} {n}" for n, q in sorted(deck.items(), key=lambda kv: kv[0].lower())]
txt = "\n".join(cab + corpo) + "\n"
txt = txt.replace("> Lista informada pelo usuário em 2026-10-05", "> **PROPOSTA de 2026-10-08, NAO aplicada: `lista.md` continua a lista do usuario.** Conjunto s4 do A/B (resultados-ab/2026-10-08-cinco-entradas-remocao).\n> Lista informada pelo usuário em 2026-10-05", 1)
open(os.path.join(AQUI, "..", "lista_proposta_s4.md"), "w", encoding="utf-8").write(txt)
print("ok: 99 cartas no deck; saem", SAEM, "entram", ENTRAM)

"""Enumera POR SCRIPT, lendo type_line/mana_cost/oracle_text AO VIVO (dados/scryfall_oraculo_rulings_2026-10-25.json), quais cartas e quais FICHAS da lista
satisfazem cada condicao de tipo/cor que outra carta da lista le (Regra #3 item 2, Regra #4 adendo item 4). Nada de memoria.
Fichas: lidas do proprio oraculo ("create ... token"), com cor/tipo/habilidade declarados no texto.
Uso: python3 -I enumera_condicoes.py <scryfall_oraculo_rulings.json>"""
import json, re, sys
d = json.load(open(sys.argv[1]))
def txt(v): return " ".join((f.get("oracle_text") or "") for f in v["faces"])
def tl(v): return v["type_line"]
def is_creature(v): return "Creature" in tl(v).split(" // ")[0]
def black(v): return "{B}" in (v["mana_cost"] or "").split(" // ")[0]
# --- fichas criadas pela lista, extraidas do oraculo ---
fichas = {}
for n, v in d.items():
    for m in re.finditer(r"[Cc]reate (?:a|an|two|X|[^.]*?)\s*((?:\d/\d )?[^.]*?token[^.]*)", txt(v)):
        fichas.setdefault(m.group(1).strip()[:110], []).append(n)
print("== FICHAS que a lista cria (frase literal do oraculo -> cartas)")
for f, cs in sorted(fichas.items()): print(f"  '{f}'  <-  {', '.join(sorted(set(cs)))}")
tokens = {  # propriedades lidas das frases acima (cor/tipo/changeling) -- conferidas contra o texto impresso logo abaixo
    "Rat (1/1 preta)": {"Rat"}, "Squirrel (1/1 verde)": {"Squirrel"}, "Mercenary (3/2 incolor, Shapeshifter, changeling = todo tipo)": {"ALL"}}
print()
# --- condicoes ---
conds = {
  "Rat": r"\bRats?\b", "Squirrel": r"\bSquirrels?\b", "Shaman": r"\bShaman\b", "Bat": r"\bBats?\b", "Lizard": r"\bLizards?\b",
  "Insect": r"\bInsects?\b", "Spider": r"\bSpiders?\b", "black creature": r"black creature", "artifact": r"\bartifact", "Treasure": r"\bTreasure",
  "legendary creature": r"legendary creature", "Swamp": r"\bSwamps?\b", "creature type (escolhido)": r"choose a creature type",
}
for c, rx in conds.items():
    leitores = [n for n, v in d.items() if re.search(rx, txt(v)) and not (c == "Rat" and n == "Rat Colony" and False)]
    if c in ("Rat", "Squirrel", "Shaman", "Bat", "Lizard", "Insect", "Spider"):
        sat_cartas = [n for n, v in d.items() if re.search(rf"\b{c}\b", tl(v).split(" // ")[0].split("—")[-1])]
        chang = [n for n, v in d.items() if "Changeling" in (v["keywords"] or []) or "every creature type" in txt(v)]
        print(f"[{c}]  tipo impresso (type_line): {sat_cartas or '-'} | changeling impresso em carta: {chang or '-'} | fichas que contam: "
              f"{[k for k,t in tokens.items() if c in t or 'ALL' in t]}")
    elif c == "black creature":
        sat = [n for n, v in d.items() if is_creature(v) and black(v)]
        print(f"[{c}]  criaturas pretas por mana_cost ({len(sat)}): {sat} | fichas pretas: Rat | NAO pretas: Squirrel (verde), Mercenary (incolor)")
    elif c == "legendary creature":
        sat = [n for n, v in d.items() if is_creature(v) and "Legendary" in tl(v)]
        print(f"[{c}]  {len(sat)}: {sat}")
    elif c == "artifact":
        sat = [n for n, v in d.items() if "Artifact" in tl(v).split(" // ")[0]]
        print(f"[{c}]  cartas ({len(sat)}): {sat} | fichas: Treasure")
    else:
        print(f"[{c}]  ", end="")
        print("")
    print(f"      LEEM a condicao ({len(leitores)}): {leitores}")
    print()
# --- Shaman: quem seria Shaman de verdade na lista (carta ou ficha)? ---
sh = [n for n, v in d.items() if "Shaman" in tl(v)]
print("Cartas com 'Shaman' no type_line:", sh, "(Thornbite Staff e' Kindred: tem o tipo, nao e' criatura)")
print("Fichas Shaman: so' o Mercenary (changeling = todo tipo de criatura, inclusive Shaman) -> Thornbite Staff: 'Whenever a Shaman creature enters, you may attach' DISPARA nele.")

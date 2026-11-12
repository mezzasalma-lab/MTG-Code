#!/usr/bin/env python3
"""Compara a ESTRUTURA do nosso deck com a dos decks do Moxfield (662 = 663 menos o proprio deck do usuario; subconjuntos: bracket 3, e os com 22+ planeswalkers) por categorias lidas do ORACULO (regex sobre `oracle_text` sem o texto de lembrete), carta por carta, sobre dados/oraculos_referencia.json.xz
e dados/decks_edhrec.jsonl. Uso: python3 comparacao_estrutural.py > ../resumos/comparacao_estrutural.md"""
import json, lzma, os, re, statistics as st, collections
AQUI = os.path.dirname(os.path.abspath(__file__)); ARQ = os.path.abspath(os.path.join(AQUI, ".."))
O = json.load(lzma.open(os.path.join(ARQ, "dados", "oraculos_referencia.json.xz"), "rt"))
decks = [json.loads(l) for l in lzma.open(os.path.join(ARQ, "dados", "decks_edhrec.jsonl.xz"), "rt", encoding="utf-8")]
DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
L = open(os.path.join(DECK, "lista.md"), encoding="utf-8").read(); nosso = set(re.findall(r"^1 (.+)$", L.split("## Sideboard")[0], re.M)) | {"Tam, the Possibility"}
cache = json.load(open(os.path.join(DECK, "..", "scryfall-cache", "oracle-cache.json"), encoding="utf-8"))
FRENTE = {k.split(" // ")[0]: k for k in list(O) + list(cache) if " // " in k}      # carta de 2 faces: o deck lista so' a frente
def info(n):
    return O.get(n) or cache.get(n) or O.get(FRENTE.get(n, "")) or cache.get(FRENTE.get(n, ""))
def nao_terrenos(r): return {n for t, l in r["cards"].items() for n, q in l if n != "Tam, the Possibility" and "Land" not in info(n)["type_line"].split("—")[0]}
NOSSO_NL = {n for n in nosso if n != "Tam, the Possibility" and "Land" not in info(n)["type_line"].split("—")[0]}
def e_o_nosso(r): return nao_terrenos(r) == NOSSO_NL      # o proprio deck do usuario, ja' publicado no Moxfield (mesmas 63 cartas nao-terreno): fora das referencias
mox = [r for r in decks if "moxfield" in (r.get("url") or "") and not e_o_nosso(r)]
def sem_lembrete(t): return re.sub(r"\([^)]*\)", "", t or "")
def eh_terreno(c): return "Land" in c["type_line"].split("—")[0]
def eh_pw(c): return "Planeswalker" in c["type_line"].split("—")[0]
CAT = {
 "mana de não-terreno (rocha/criatura/aura; sem PW)": lambda c, t: (not eh_terreno(c)) and (not eh_pw(c)) and bool(re.search(r"\{T\}[^.]*: Add|Add \{[WUBRGC]|Add one mana|Add (two|three|four|five)", t)) and "Creature" in c["type_line"] or ((not eh_terreno(c)) and (not eh_pw(c)) and ("Artifact" in c["type_line"].split("—")[0]) and bool(re.search(r"\{T\}[^.]*: Add", t))),
 "ramp que busca terreno (feitiço/instantâneo)": lambda c, t: (not eh_terreno(c)) and bool(re.search(r"Search your library for [^.]*(basic )?land card[^.]*battlefield|Search your library for [^.]*(Forest|Island|Plains|Swamp|Mountain) card", t)),
 "planeswalker que produz mana": lambda c, t: eh_pw(c) and bool(re.search(r"[+−-]\d+: Add|\+\d+: Untap|Add \{", t)),
 "contramágica": lambda c, t: (not eh_terreno(c)) and bool(re.search(r"Counter target", t)),
 "instantâneo (qualquer)": lambda c, t: (not eh_terreno(c)) and "Instant" in c["type_line"].split("—")[0],
 "remoção pontual em instantâneo/flash": lambda c, t: ("Instant" in c["type_line"].split("—")[0]) and bool(re.search(r"(Destroy|Exile|Return|deals? \d+ damage to) target|gets -\d+/-\d+", t)),
 "remoção em massa de criaturas": lambda c, t: (not eh_terreno(c)) and bool(re.search(r"(destroy|exile) all (creatures|nonland|artifacts)|damage to each creature|each player sacrifices|sacrifices all creatures|destroy all creatures", t, re.I)),
 "tutor (busca não-terreno)": lambda c, t: (not eh_terreno(c)) and bool(re.search(r"Search your library", t)) and not re.search(r"Search your library for [^.]*(basic land|land card|Forest|Island|Plains|Swamp|Mountain)", t),
 "compra de cartas (heurística)": lambda c, t: (not eh_terreno(c)) and bool(re.search(r"[Dd]raws? (a|an additional|two|three|four|X|that many|half) cards?|You draw|draw a card for each|draw cards equal", t)),
 "proliferate ou dobra contadores": lambda c, t: bool(re.search(r"[Pp]roliferate|[Dd]ouble the number of|twice that many|[Pp]ut an additional (counter|loyalty counter)|put (twice|that many plus)", t)),
 "proteção de planeswalker / fase / indestrutível": lambda c, t: (not eh_terreno(c)) and bool(re.search(r"phase out|hexproof|indestructible|can't attack planeswalkers|Creatures can't attack planeswalker|prevent all damage|can't be countered", t)),
 "ficha de Jace / cria planeswalker": lambda c, t: bool(re.search(r"[Ee]mpower Jace|create [^.]*planeswalker", t)),
 "terreno que entra virado (incondicional)": lambda c, t: eh_terreno(c) and bool(re.search(r"enters tapped\.?($|\s)", t)) and "unless" not in t and "you may pay" not in t,
 "terreno com fetch": lambda c, t: eh_terreno(c) and bool(re.search(r"Sacrifice [^.]*: Search your library", t)),
}
def conta(cartas):
    out = collections.Counter(); sem = 0
    for n, q in cartas:
        c = info(n)
        if not c: sem += 1; continue
        t = sem_lembrete(c.get("oracle_text"))
        for k, f in CAT.items():
            if f(c, t): out[k] += q
    return out, sem
def cartas_do_deck(r): return [(n, q) for tipo, l in r["cards"].items() for n, q in l]
def media(S):
    tot = collections.Counter(); n = 0
    for r in S:
        c, sem = conta(cartas_do_deck(r)); tot.update(c); n += 1
    return {k: tot[k] / n for k in CAT}
b3 = [r for r in mox if r["bracket"] == 3]; pw22 = [r for r in mox if (r["tipos"]["planeswalker"] or 0) >= 22]; b3pw = [r for r in b3 if (r["tipos"]["planeswalker"] or 0) >= 22]
c_nosso, sem_n = conta([(n, 1) for n in nosso]); assert sem_n == 0, sem_n
TROCAS = [("Leyline Immersion", "Swords to Plowshares"), ("Staff of Compleation", "Oath of Ajani"), ("Domri, Chaos Bringer", "Doubling Season"), ("Teferi's Talent", "Commodore Guff"), ("Baxter Building", "Karn's Bastion"), ("Liliana's Talent", "Mutational Advantage")]
depois = set(nosso)
for x, y in TROCAS: assert x in depois and y not in depois; depois.remove(x); depois.add(y)
c_depois, sem_d = conta([(n, 1) for n in depois]); assert sem_d == 0, sem_d
M = {"todos Moxfield": media(mox), "Moxfield B3": media(b3), "Moxfield 22+ PW": media(pw22), "Moxfield B3 e 22+ PW": media(b3pw)}
print("# Estrutura: nosso deck x decks do Moxfield (categorias lidas do oráculo, heurística por regex)\n")
print(f"Decks de referência (Moxfield, via EDHREC): {len(mox)}; bracket 3: {len(b3)}; 22+ planeswalkers: {len(pw22)}; bracket 3 e 22+ planeswalkers: {len(b3pw)}. Média por deck (nosso = contagem exata). Regex sobre `oracle_text` sem o texto de lembrete: **são heurísticas, comparam o mesmo critério nos dois lados, e não são lista exaustiva de efeitos**.\n")
print("| categoria | nosso | nosso com o pacote de 6 trocas (proposta) | " + " | ".join(M) + " |\n|---|---|---|" + "---|" * len(M))
for k in CAT: print(f"| {k} | {c_nosso[k]} | {c_depois[k]} | " + " | ".join(f"{M[m][k]:.1f}" for m in M) + " |")
tipos = {"planeswalker": 25, "creature": 12, "instant": 1, "sorcery": 4, "artifact": 8, "enchantment": 14, "land": 36}
print("\n| tipo (campo do EDHREC) | nosso | " + " | ".join(M) + " |\n|---|---|---|---|---|---|")
for k, v in tipos.items():
    row = []
    for S in (mox, b3, pw22, b3pw): row.append(f"{st.mean((r['tipos'][k] or 0) for r in S):.1f}")
    print(f"| {k} | {v} | " + " | ".join(row) + " |")

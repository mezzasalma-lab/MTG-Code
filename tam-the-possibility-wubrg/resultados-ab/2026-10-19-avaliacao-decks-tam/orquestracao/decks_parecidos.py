#!/usr/bin/env python3
"""Os decks do Moxfield MAIS PARECIDOS com o nosso (Jaccard sobre as cartas nao-terreno do deck, sem o comandante) e o que cada um tem a mais / a menos. Le so' dos dados arquivados. Uso: python3 decks_parecidos.py > ../resumos/decks_parecidos.md"""
import json, lzma, os, re, collections
AQUI = os.path.dirname(os.path.abspath(__file__)); ARQ = os.path.abspath(os.path.join(AQUI, "..")); DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
O = json.load(lzma.open(os.path.join(ARQ, "dados", "oraculos_referencia.json.xz"), "rt"))
cache = json.load(open(os.path.join(DECK, "..", "scryfall-cache", "oracle-cache.json"), encoding="utf-8"))
decks = [json.loads(l) for l in lzma.open(os.path.join(ARQ, "dados", "decks_edhrec.jsonl.xz"), "rt", encoding="utf-8")]
L = open(os.path.join(DECK, "lista.md"), encoding="utf-8").read(); nosso = set(re.findall(r"^1 (.+)$", L.split("## Sideboard")[0], re.M)) - {"Tam, the Possibility"}
todos_mox = [r for r in decks if "moxfield" in (r.get("url") or "")]
FRENTE = {k.split(" // ")[0]: k for k in list(O) + list(cache) if " // " in k}
def info(n): return O.get(n) or cache.get(n) or O.get(FRENTE.get(n, "")) or cache.get(FRENTE.get(n, ""))
def terreno(n): c = info(n); return c and "Land" in c["type_line"].split("—")[0]
def cartas(r): return {n for t, l in r["cards"].items() for n, q in l if n != "Tam, the Possibility" and not terreno(n)}
nosso_nl = {n for n in nosso if not terreno(n)}
proprio = [r for r in todos_mox if cartas(r) == nosso_nl]
mox = [r for r in todos_mox if r not in proprio]
res = []
for r in mox:
    s = cartas(r); j = len(s & nosso_nl) / len(s | nosso_nl); res.append((j, r, s))
res.sort(key=lambda x: (-x[0], x[1]["url"]))
print("# Os 8 decks do Moxfield mais parecidos com o nosso (Jaccard sobre as cartas não-terreno)\n")
print(f"Comparados {len(mox)} decks do Moxfield (via EDHREC, 2026-10-19). Nosso deck: {len(nosso_nl)} cartas não-terreno (sem o comandante). **Fora da comparação: {len(proprio)} deck(s) com a MESMA lista do nosso ({', '.join(r['url'] for r in proprio) or 'nenhum'}): é o próprio deck do usuário, já publicado no Moxfield.**\n")
print("| # | deck (Moxfield) | similaridade | bracket | preço (US$) | PWs | cartas em comum |\n|---|---|---|---|---|---|---|")
for i, (j, r, s) in enumerate(res[:8], 1): print(f"| {i} | {r['url']} | {j:.2f} | {r['bracket'] or '—'} | {r['price']:.0f} | {r['tipos']['planeswalker']} | {len(s & nosso_nl)} |")
print("\nPara cada um: cartas que ele TEM e nós não, e cartas NOSSAS que ele não tem (só não-terrenos).\n")
for i, (j, r, s) in enumerate(res[:8], 1):
    print(f"**{i}. {r['url']}** (bracket {r['bracket'] or '—'}, {r['tipos']['planeswalker']} planeswalkers, instantâneos {r['tipos']['instant']}):")
    print("- ele tem e nós não: " + ", ".join(sorted(s - nosso_nl)))
    print("- nós temos e ele não: " + ", ".join(sorted(nosso_nl - s)) + "\n")

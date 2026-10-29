"""Confere `lista-fisica.md` (bloco 'Lista física atual') contra `lista.md` menos as 6 cartas que o usuário disse que faltam (2026-10-23).
Uso (de dentro desta pasta): python3 confere.py     -> imprime OK ou a diferença"""
import json, re, os
AQUI = os.path.dirname(os.path.abspath(__file__)); DECK = os.path.abspath(os.path.join(AQUI, "..", ".."))
FALTAM = ["Beast Whisperer", "Devoted Druid", "Maralen, Fae Ascendant", "Buried Alive", "Deadly Rollick", "Awaken the Honored Dead"]
def linhas_de_cartas(txt):
    out = []
    for l in txt.split("\n"):
        m = re.match(r"^(\d+)\s+(.+)$", l.strip())
        if m: out.append((int(m.group(1)), m.group(2).strip()))
    return out
lista = open(os.path.join(DECK, "lista.md"), encoding="utf-8").read()
esperado = [(q, n) for q, n in linhas_de_cartas(lista) if n not in FALTAM]
fis = open(os.path.join(DECK, "lista-fisica.md"), encoding="utf-8").read()
bloco = fis.split("### Lista física atual", 1)[1].split("```", 2)[1]
obtido = linhas_de_cartas(bloco)
sj = json.load(open(os.path.join(AQUI, "scryfall_faltantes.json"), encoding="utf-8"))
assert sorted(sj) == sorted(FALTAM), sorted(sj)
print("lista.md:", sum(q for q, _ in linhas_de_cartas(lista)), "cartas | fisicas esperadas:", sum(q for q, _ in esperado), "| no arquivo:", sum(q for q, _ in obtido))
print("OK" if esperado == obtido else ("DIFERE: " + str(set(esperado) ^ set(obtido))))
print("faltantes com preco USD:", {n: v["usd"] for n, v in sj.items()}, "| soma:", round(sum(float(v["usd"]) for v in sj.values()), 2))

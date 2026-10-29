"""Enumera POR SCRIPT (Regra #4, adendo 4) quais cartas da lista do Mothman satisfazem a condicao da Tergrid ('an opponent sacrifices a nontoken permanent or discards a permanent card')
e quais gatilhos/estaticos do deck leem 'sacrifice'/'discard'; le oraculo ao vivo (cache do repositorio, nao memoria) e a marca Game Changer do bruto do Scryfall.
Uso: python3 enumera_tergrid.py > ../resumos/enumera_tergrid.txt"""
import json, lzma, re, os
ROOT = "/home/user/MTG-Code"
DECK = f"{ROOT}/wise-mothman-sultai"
cache = json.load(open(f"{ROOT}/scryfall-cache/oracle-cache.json"))
bruto = json.load(lzma.open(f"{DECK}/resultados-ab/2026-10-05-candidatas-pos-eoe/dados/lista_bruto.json.xz", "rt"))
nomes = {}
for it in bruto:
    c = it["carta"]
    nomes[c["name"]] = c
def texto(n):
    c = nomes.get(n) or cache.get(n)
    if c.get("oracle_text"):
        return c["oracle_text"]
    return " // ".join(f.get("oracle_text", "") for f in c.get("card_faces", []))
print(f"cartas distintas lidas: {len(nomes)} (> 0)")
pats = [("oponente/jogador-alvo SACRIFICA", r"(opponent|defending player|target player|each player|that player)[^.\n]{0,60}sacrifice"),
        ("oponente DESCARTA", r"(opponent|defending player|target player|each player|that player)[^.\n]{0,60}discard"),
        ("annihilator", r"annihilator"),
        ("'discard' em qualquer lugar", r"discard"),
        ("'sacrifice' em qualquer lugar", r"sacrifice")]
for rot, pat in pats:
    hits = [(n, [l.strip() for l in texto(n).splitlines() if re.search(pat, l, re.I)]) for n in sorted(nomes)]
    hits = [(n, ls) for n, ls in hits if ls]
    print(f"\n== {rot}: {len(hits)} cartas")
    for n, ls in hits:
        print(f"  - {n}: {ls[0][:150]}")
gc = sorted(n for n, c in nomes.items() if c.get("game_changer"))
print(f"\n== Game Changers na lista atual (campo `game_changer` do Scryfall): {len(gc)}: {gc}")
print("Tergrid game_changer:", json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dados", "tergrid_carta.json"))).get("game_changer"))

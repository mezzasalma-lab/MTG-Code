"""Linha do tempo do goldfish manual #5, gerada SO' de dados/goldfish_manual_5_bruto.json (blocos = turnos; mao inicial = 7 cartas + a compra do T1 (no log, 8 cartas library->hand no bloco 1; foto da mao inicial em dados/mao_inicial_foto.png)).
Por turno: compras (library->hand), terrenos jogados, magias conjuradas (hand->battlefield / commandZone->battlefield), buscas (library->battlefield), saidas do campo, cartas de oponente e a ULTIMA lealdade vista de cada
planeswalker no bloco. Nao interpreta: o que e' interpretacao fica no LEIAME.md."""
import json, os, sys, collections
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, DECK)
import tam_goldfish_v1 as T

data = json.load(open(os.path.join(AQUI, "..", "dados", "goldfish_manual_5_bruto.json")))
is_land = lambda n: n in T.CARD_DB and "land" in T.CARD_DB[n].types
print("| turno | compras (biblioteca -> mão) | terreno jogado | conjurou | buscou (biblioteca -> campo) | saiu do campo | oponente | lealdade no fim do bloco |")
print("|---|---|---|---|---|---|---|---|")
for i, blk in enumerate(data, 1):
    comp, terr, cast, busca, sai, opp = [], [], [], [], [], []
    loy = collections.OrderedDict()
    for e in blk:
        n, fz, tz = e.get("name"), e.get("fromZone"), e.get("toZone")
        if fz == "library" and tz == "hand":
            comp.append(n)
        elif fz == "hand" and tz == "battlefield":
            (terr if is_land(n) else cast).append(n)
        elif fz == "commandZone" and tz == "battlefield":
            cast.append(n + (" (imposto %d)" % e["commandTax"] if e.get("commandTax") else ""))
        elif fz == "library" and tz == "battlefield":
            busca.append(n)
        elif fz == "battlefield" and tz in ("graveyard", "exile"):
            sai.append(f"{n} → {tz}")
        elif tz == "opponentsCards":
            opp.append(n)
        l = (e.get("counters") or {}).get("Loyalty")
        if l is not None:
            loy[n] = l["count"]
    cast = [c for c in cast]
    print(f"| T{i} | {', '.join(comp) or '—'} | {', '.join(terr) or '—'} | {', '.join(cast) or '—'} | {', '.join(busca) or '—'} | {', '.join(sai) or '—'} | {', '.join(opp) or '—'} | {', '.join(f'{k.split(chr(44))[0]} {v}' for k, v in loy.items()) or '—'} |")

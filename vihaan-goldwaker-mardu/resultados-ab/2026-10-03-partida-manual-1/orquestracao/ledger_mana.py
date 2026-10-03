"""Conta de mana por turno da partida manual. Fontes liquidas (cada permanente desvirado conta 1 vez por turno; Sol Ring 2; Rakdos Signet
e Desolate Mire +1 liquido porque gastam 1 pra gerar 2) contra o custo das magias que entraram em campo (de mao, exilio, comando,
cemiterio-flashback). Treasures: 'tapped' que continua existindo no turno seguinte = atacante marcado; que some = sacrificado/morto.
Uso: python3 ledger_mana.py ../dados/partida.json.xz ../dados/oraculo_rulings_ao_vivo.json"""
import json, lzma, re, sys
d = json.load(lzma.open(sys.argv[1], "rt"))
orc = json.load(open(sys.argv[2]))
LANDS = {"Mountain", "Swamp", "Plains", "Dragonskull Summit", "Tainted Peak", "Path of Ancestry", "Battlefield Forge", "Desolate Mire"}
PESO = {"Sol Ring": 2}  # os demais pesam 1 (Signet Rakdos e Mire: +1 liquido)
CUSTO_ESPECIAL = {"Sevinne's Reclamation": {8: 5}}  # turno -> custo real (flashback {4}{W})


def mv(nome):
    mc = (orc.get(nome) or {}).get("mana_cost") or ""
    return sum(int(x) if x.isdigit() else 1 for x in re.findall(r"\{([^}]+)\}", mc) if x not in ("X",))

ids_por_turno = [{r["id"] for r in t} for t in d]
print("turno | fontes liquidas (exceto Treasure) | magias (custo) | sobra | Treasures tapped: sobrevivem (atacante) / somem (sacrificado ou morto)")
for n, t in enumerate(d, 1):
    tapped_unicos = {}
    for r in t:
        if r["tapped"] and not r["token"] and r["fromZone"] is None and r["toZone"] is None and r["name"] != "Vihaan, Goldwaker" and r["name"] != "Captain Lannery Storm":
            tapped_unicos[r["id"]] = r["name"]
    fontes = sum(PESO.get(nm, 1) for nm in tapped_unicos.values())
    magias = []
    for r in t:
        if r["token"] or r["name"] in LANDS or r["toZone"] != "battlefield" and r["fromZone"] != "commandZone":
            continue
        if r["fromZone"] in ("hand", "exile", "commandZone", "graveyard") and r["toZone"] == "battlefield":
            custo = CUSTO_ESPECIAL.get(r["name"], {}).get(n, mv(r["name"]))
            if r["fromZone"] == "graveyard" and r["name"] not in CUSTO_ESPECIAL:
                continue  # alvo reanimado, nao e' magia
            if n == 6 and r["name"] == "Mahadi, Emporium Master" or n == 8 and r["name"] == "Zulaport Cutthroat":
                continue
            magias.append((r["name"], custo))
    # Sevinne's aparece 2x (exilio->campo e campo->cemiterio): conta so' a entrada
    custo_total = sum(c for _, c in magias)
    sobrevive, some = 0, 0
    for r in t:
        if r["token"] and r["tapped"] and r["fromZone"] is None and r["toZone"] is None:
            seguinte = ids_por_turno[n] if n < len(d) else None
            if seguinte is None:
                continue
            if r["id"] in seguinte:
                sobrevive += 1
            else:
                some += 1
    final = " (ultimo turno: sem turno seguinte pra decidir)" if n == len(d) else ""
    print("T%d | %d (%s) | %s = %d | %+d | %d sobrevivem / %d somem%s" % (n, fontes, ", ".join(sorted(tapped_unicos.values())), "; ".join("%s %d" % m for m in magias) or "-", custo_total, fontes - custo_total, sobrevive, some, final))

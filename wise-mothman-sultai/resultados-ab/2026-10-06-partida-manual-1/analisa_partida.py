"""Trace de uma partida manual do Archidekt playtester (The Wise Mothman). Uso: python3 analisa_partida.py [dados/partida.json.xz]  (Markdown no stdout)
Cada elemento do JSON e' um turno (rodada); cada registro e' o estado de um objeto quando mudou (zona, virada, marcadores).
`opponentsCards` = interacao que o usuario poe contra si (simulador de interacao 'On'). Registros sem fromZone/toZone sao so' mudanca de estado (virar/desvirar/marcador).
O trace NAO prova custo de mana nem ordem da pilha; o que prova (so' pelo log): terrenos jogados da mao e do cemiterio por turno, compras (library->hand), mills (library->graveyard),
mana de fontes viradas (contagem), marcadores. O mill de OPONENTE nao aparece no log (limite declarado pelo usuario)."""
import json, lzma, os, sys
from collections import defaultdict
aqui = os.path.dirname(os.path.abspath(__file__))
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, "dados", "partida.json.xz")
T = json.load(lzma.open(caminho) if caminho.endswith(".xz") else open(caminho))
ORC = json.load(open(os.path.join(aqui, "..", "..", "..", "scryfall-cache", "oracle-cache.json")))
def tipo(n):
    e = ORC.get(n) or ORC.get(n.split(" // ")[0]) or {}
    tl = e.get("type_line") or ""
    return tl.split(" // ")[0]
def is_land(n): return "Land" in tipo(n) and n != "Agadeem's Awakening // Agadeem, the Undercrypt"
def ctr(e): return ",".join(f"{k}x{v['count']}" for k, v in sorted((e.get("counters") or {}).items())) or "-"
estado = {}
print("# Trace da partida manual do Mothman (2026-10-06)\n")
for i, t in enumerate(T, 1):
    print(f"## T{i} ({len(t)} registros)")
    resumo = defaultdict(list)
    for e in t:
        n, fz, tz = e["name"], e.get("fromZone"), e.get("toZone")
        ant = estado.get(e["id"])
        linha = None
        if fz or tz:
            linha = f"{fz or '?'} -> {tz or '?'}"
            if fz == "library" and tz == "hand": resumo["compra/tutor (library->hand)"].append(n)
            elif fz == "library" and tz == "graveyard": resumo["MILL meu (library->graveyard)"].append(n)
            elif fz == "hand" and tz == "battlefield": resumo["terreno da mao" if is_land(n) else "conjurada/jogada da mao (->campo)"].append(n)
            elif fz == "graveyard" and tz == "battlefield": resumo["terreno do CEMITERIO (Icetill)" if is_land(n) else "reanimada/retrace (cemiterio->campo)"].append(n)
            elif fz == "graveyard" and tz == "hand": resumo["cemiterio->mao"].append(n)
            elif fz == "hand" and tz == "graveyard": resumo["mao->cemiterio (descarte/instante/sacrificio)"].append(n)
            elif fz == "battlefield" and tz == "graveyard": resumo["campo->cemiterio"].append(n)
            elif fz == "battlefield" and tz == "hand": resumo["campo->mao (bounce)"].append(n)
            elif fz == "commandZone": resumo["zona de comando->campo"].append(n)
            elif tz == "opponentsCards": resumo["INTERACAO do oponente simulado"].append(n)
            else: resumo[f"outra {fz}->{tz}"].append(n)
        elif ant is not None:
            mud = []
            if ant["tapped"] != e["tapped"]: mud.append("virou" if e["tapped"] else "desvirou")
            if ctr(ant) != ctr(e): mud.append(f"marcadores {ctr(ant)} -> {ctr(e)}")
            if mud:
                linha = "; ".join(mud)
                if "virou" in mud and (is_land(n) or n in ("Sol Ring",)): resumo["fonte de mana virada"].append(n)
                if any(m.startswith("marc") for m in mud): resumo["marcadores mudaram"].append(f"{n} ({ctr(ant)} -> {ctr(e)})")
        if linha:
            print(f"- {n} [{e['id'][:4]}]: {linha}" + (f" | marcadores {ctr(e)}" if ctr(e) != "-" else "") + (" | VIRADA" if e["tapped"] else ""))
        estado[e["id"]] = e
    print("\n  Resumo do turno:")
    for k, v in resumo.items(): print(f"  - {k} ({len(v)}): {', '.join(v)}")
    print()

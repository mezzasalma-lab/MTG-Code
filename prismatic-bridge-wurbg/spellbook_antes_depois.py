"""Commander Spellbook antes/depois de cada carta candidata (Regra #4, adendo 2026-09-28).
Uso: python3 spellbook_antes_depois.py
Consulta `find-my-combos` com o comandante + as 99 cartas (lista atual e cada troca), lista combos e quase-combos
novos/removidos, e roda um CONTROLE POSITIVO (tira a The Chain Veil, que esta em 4 combos: a resposta tem que mudar).
Resposta identica em todos os cenarios sem controle positivo nao prova nada."""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prismatic_bridge_goldfish_v1 as pb

os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
CMD = "Esika, God of the Tree // The Prismatic Bridge"


def query(deck):
    body = {"commanders": [{"card": CMD}], "main": [{"card": c, "quantity": 1} for c in deck]}
    req = urllib.request.Request("https://backend.commanderspellbook.com/find-my-combos", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=120))["results"]


def summarize(r):
    inc = {tuple(sorted(u["card"]["name"] for u in c["uses"])) for c in r["included"]}
    alm = {tuple(sorted(u["card"]["name"] for u in c["uses"])) for c in r["almostIncluded"]}
    return inc, alm


def deck_with(swaps):
    text = pb.apply_swaps(pb.build_decklist(False), swaps) if swaps else pb.build_decklist(False)
    return pb.parse_decklist(text)


if __name__ == "__main__":
    D, G, V, S = pb.CANDIDATE_PWS
    scen = {"base": deck_with(None),
            "Dihada": deck_with([("Arena Rector", D)]), "Guff": deck_with([("Arena Rector", G)]),
            "Vronos": deck_with([("Arena Rector", V)]), "Sarkhan": deck_with([("Arena Rector", S)]),
            "as 4 juntas": deck_with([("Arena Rector", D), ("Swan Song", G), ("Veil of Summer", V), ("Oath of Nissa", S)]),
            "CONTROLE positivo: sem The Chain Veil": [c for c in deck_with(None) if c != "The Chain Veil"]}
    base_inc = base_alm = None
    for name, deck in scen.items():
        inc, alm = summarize(query(deck))
        print(f"{name:40s} cartas={len(deck)} combos={len(inc)} quase-combos={len(alm)}")
        if base_inc is None:
            base_inc, base_alm = inc, alm
            continue
        print("   combos novos:", sorted(inc - base_inc), "| removidos:", sorted(base_inc - inc))
        print("   quase-combos novos:", len(alm - base_alm), "| removidos:", len(base_alm - alm))

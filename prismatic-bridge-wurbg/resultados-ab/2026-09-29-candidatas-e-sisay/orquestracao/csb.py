import json, os, sys, urllib.request
sys.path.insert(0, "/home/user/MTG-Code/prismatic-bridge-wurbg")
import prismatic_bridge_goldfish_v1 as pb
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
CMD = "Esika, God of the Tree // The Prismatic Bridge"

def query(deck):
    body = {"commanders": [{"card": CMD}], "main": [{"card": c, "quantity": 1} for c in deck]}
    req = urllib.request.Request("https://backend.commanderspellbook.com/find-my-combos",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=120))["results"]

def summarize(r):
    inc = {tuple(sorted(u["card"]["name"] for u in c["uses"])) for c in r["included"]}
    alm = {tuple(sorted(u["card"]["name"] for u in c["uses"])) for c in r["almostIncluded"]}
    return inc, alm

def deck_with(swaps):
    text = pb.apply_swaps(pb.build_decklist(False), swaps) if swaps else pb.build_decklist(False)
    return pb.parse_decklist(text)

if __name__ == "__main__":
    scen = {"base": None,
            "Dihada": [("Arena Rector", pb.CANDIDATE_PWS[0])],
            "Guff": [("Arena Rector", pb.CANDIDATE_PWS[1])],
            "Vronos": [("Arena Rector", pb.CANDIDATE_PWS[2])],
            "Sarkhan": [("Arena Rector", pb.CANDIDATE_PWS[3])],
            "todas": [("Arena Rector", pb.CANDIDATE_PWS[0]), ("Swan Song", pb.CANDIDATE_PWS[1]),
                      ("Veil of Summer", pb.CANDIDATE_PWS[2]), ("Oath of Nissa", pb.CANDIDATE_PWS[3])],
            # controle positivo: uma carta que ESTA em combos da lista (prova que o pipeline reage a mudanca de lista)
            "controle_sem_Chain_Veil": [("The Chain Veil", "Arena Rector")] if False else None}
    out = {}
    base_inc = base_alm = None
    for name, sw in scen.items():
        if name.startswith("controle"):
            deck = [c for c in deck_with(None) if c != "The Chain Veil"] + ["Farseek"] if "Farseek" not in deck_with(None) else [c for c in deck_with(None) if c != "The Chain Veil"]
        else:
            deck = deck_with(sw)
        r = query(deck)
        inc, alm = summarize(r)
        out[name] = (len(deck), len(inc), len(alm), r.get("identity"))
        if name == "base":
            base_inc, base_alm = inc, alm
        print(f"{name:26s} cartas={len(deck)} incluidos={len(inc)} quase={len(alm)} identidade={r.get('identity')}")
        if name != "base":
            print("   combos novos:", sorted(inc - base_inc), "| que sumiram:", sorted(base_inc - inc))
            print("   quase-combos novos:", len(alm - base_alm), "| que sumiram:", len(base_alm - alm))
            for k in sorted(alm - base_alm)[:8]: print("      +", k)
            for k in sorted(base_alm - alm)[:8]: print("      -", k)

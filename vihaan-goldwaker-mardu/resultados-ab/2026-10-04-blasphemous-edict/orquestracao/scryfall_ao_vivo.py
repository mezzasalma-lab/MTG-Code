"""Oráculo, tipo, custo e RULINGS ao vivo (Scryfall) das cartas da avaliação Blasphemous Act x Blasphemous Edict. Guarda a resposta crua em ../dados/oraculo_rulings_ao_vivo.json.
Uso (da raiz do repositório): SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-04-blasphemous-edict/orquestracao/scryfall_ao_vivo.py"""
import json, os, subprocess, sys, time, urllib.parse
AQUI = os.path.dirname(os.path.abspath(__file__))
NOMES = ["Blasphemous Edict", "Blasphemous Act", "Mayhem Devil", "Mirkwood Bats", "Nadier's Nightblade", "Zulaport Cutthroat", "Pitiless Plunderer", "Mahadi, Emporium Master",
         "Dictate of Erebos", "Rain of Riches", "Blood Money", "Marionette Master", "Agent of the Iron Throne", "Life Insurance", "Captain Lannery Storm",
         "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel", "Vihaan, Goldwaker", "Anointed Procession", "Kambal, Profiteering Mayor"]

def get(url):
    r = subprocess.run(["curl", "-sS", "--max-time", "40", url], capture_output=True, text=True)
    return json.loads(r.stdout)

saida = {}
for n in NOMES:
    c = get("https://api.scryfall.com/cards/named?exact=" + urllib.parse.quote(n)); time.sleep(0.12)
    r = get(c["rulings_uri"]); time.sleep(0.12)
    saida[n] = {"name": c.get("name"), "oracle_id": c.get("oracle_id"), "type_line": c.get("type_line"), "mana_cost": c.get("mana_cost"), "cmc": c.get("cmc"), "oracle_text": c.get("oracle_text"),
                "power": c.get("power"), "toughness": c.get("toughness"), "color_identity": c.get("color_identity"), "legal_commander": c.get("legalities", {}).get("commander"),
                "rulings": [(x["published_at"], x["comment"]) for x in r.get("data", [])]}
json.dump(saida, open(os.path.join(AQUI, "..", "dados", "oraculo_rulings_ao_vivo.json"), "w"), ensure_ascii=False, indent=1)
for n, v in saida.items():
    print("=====", n, "|", v["type_line"], "|", v["mana_cost"], "| commander:", v["legal_commander"], "| id:", v["color_identity"])
    print(v["oracle_text"])
    for d, t in v["rulings"]:
        print(" -", d, t)

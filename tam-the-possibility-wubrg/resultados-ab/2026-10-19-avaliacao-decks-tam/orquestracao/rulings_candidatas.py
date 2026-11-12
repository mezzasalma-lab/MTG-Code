"""Rulings (Scryfall, ao vivo) das candidatas e das cartas do deck que elas tocam, LIDAS ANTES de avaliar (Regra #3 de CLAUDE.md). Uso: python3 rulings_candidatas.py <saida.json>"""
import json, os, sys, time, urllib.request, urllib.parse
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
NOMES = ["Tam, the Possibility", "Carth the Lion", "Nicol Bolas, Dragon-God", "Doubling Season", "Teferi, Master of Time", "Oath of Ajani", "Deepglow Skate", "Commodore Guff", "Spark Double", "The Chain Veil", "Oath of Teferi",
         "Teferi, Temporal Archmage", "Aminatou, the Fateshifter", "Way of the Paradox", "Sanctum Lurker", "Overwrite the Multiverse", "Displacer Kitten", "Teferi, Time Raveler", "Leyline Immersion", "Ichormoon Gauntlet", "Loyal Tutor",
         "The Theorist, Jace Beleren", "Karn's Bastion", "Interplanar Beacon", "Swords to Plowshares", "Path to Exile", "Vraska, Betrayal's Sting", "Vorinclex, Monstrous Raider", "Tekuthal, Inquiry Dominus", "Lae'zel, Vlaakith's Champion"]
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "MTG-Code-audit/1.0", "Accept": "application/json"}), timeout=60))
out = {}
for n in NOMES:
    d = get("https://api.scryfall.com/cards/named?exact=" + urllib.parse.quote(n)); r = get(d["rulings_uri"])["data"]
    out[n] = {"oracle_id": d["oracle_id"], "oracle_text": d.get("oracle_text", ""), "game_changer": d.get("game_changer"), "rulings": [[x["published_at"], x["comment"]] for x in r]}
    time.sleep(0.12)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
for n, v in out.items(): print(f"## {n} | {len(v['rulings'])} rulings | GC={v['game_changer']}")

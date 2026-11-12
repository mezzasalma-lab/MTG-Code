"""Baixa ao vivo (Scryfall) o oraculo e as rulings das cartas desta partida (Regra #3: ler as rulings ANTES de concluir) e acrescenta ao scryfall-cache/oracle-cache.json
as cartas que faltarem. Uso: python3 baixar_rulings.py <saida_rulings.json>"""
import json, sys, time, urllib.request, urllib.parse
CACHE = "/home/user/MTG-Code/scryfall-cache/oracle-cache.json"
NOMES = ["Winding Constrictor", "Ouroboroid", "Basking Broodscale", "Gyre Sage", "The Great Henge", "Kami of Whispered Hopes", "The Wise Mothman", "Freestrider Lookout", "Undergrowth Stadium",
         "Soul-Guide Lantern", "Cankerbloom", "Takenuma, Abandoned Mire", "Swarmyard", "Zagoth Triome", "Fierce Guardianship", "Mindcrank"]
def g(url):
    for t in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "MTG-Code-audit/1.0", "Accept": "application/json"}), timeout=60))
        except Exception as e:
            time.sleep(2 * (t + 1))
    raise RuntimeError(url)
cache = json.load(open(CACHE))
out = {}
novas = []
for n in NOMES:
    c = g("https://api.scryfall.com/cards/named?" + urllib.parse.urlencode({"exact": n.split(" // ")[0]}))
    r = g(c["rulings_uri"])["data"]
    out[n] = {"scryfall_name": c["name"], "oracle_id": c["oracle_id"], "flavor_name": c.get("flavor_name"), "rulings": [(x["published_at"], x["comment"]) for x in r]}
    if c["name"] not in cache and n not in cache:
        faces = c.get("card_faces")
        e = {k: c.get(k) for k in ("cmc", "collector_number", "color_identity", "colors", "keywords", "legalities", "loyalty", "mana_cost", "name", "oracle_text", "power", "prices", "released_at", "scryfall_uri", "set", "toughness", "type_line")}
        e["legalities"] = dict(sorted((e["legalities"] or {}).items()))   # o cache existente guarda as chaves em ordem alfabetica
        e["prices"] = dict(sorted((e["prices"] or {}).items()))
        cache[c["name"]] = e
        if faces:
            cache[c["name"]]["card_faces"] = [{k: f.get(k) for k in ("name", "mana_cost", "type_line", "oracle_text", "power", "toughness")} for f in faces]
        novas.append(c["name"])
    time.sleep(0.12)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
if novas:
    open(CACHE, "w").write(json.dumps(cache, indent=2, ensure_ascii=False) + "\n")   # mesmo formato do arquivo existente (diff so' das cartas novas)
print("rulings baixadas:", {k: len(v["rulings"]) for k, v in out.items()})
print("acrescentadas ao cache:", novas)

"""Oraculo COMPLETO (todas as faces), tipo, custo, cor, legalidade e RULINGS ao vivo (Scryfall) dos wipes/efeitos de sacrificio em massa achados por busca_ampla.py + das cartas do deck
que decidem a avaliacao (Mayhem Devil, Dictate, Teferi's Protection, Boros Charm, Vihaan, Act, Edict...). Regra #3: ler as rulings ANTES de modelar. Guarda a resposta crua em
../dados/oraculo_candidatas_rulings.json. Nome exato (`/cards/named?exact=`); cai no `fuzzy` se falhar (Regra #2: flavor_name e faces).
Uso (da raiz do repositorio): SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-04-wipes-de-sacrificio/orquestracao/oraculo_candidatas.py"""
import json, os, subprocess, time, urllib.parse
AQUI = os.path.dirname(os.path.abspath(__file__))
CANDIDATAS = [
    # grupo A: "cada jogador sacrifica N criaturas"
    "Blasphemous Edict", "By Invitation Only", "Barter in Blood", "Tergrid's Shadow", "Rankle's Prank", "Taste of Death", "Necrotic Hex", "Abyssal Gorestalker",
    "Meathook Massacre II", "Liliana, Dreadhorde General", "Zodiark, Umbral God",
    # grupo B: "mantem so' alguns, sacrifica o resto"
    "Tragic Arrogance", "Mythos of Snapdax", "Winnowing", "Slaughter the Strong", "Destined Confrontation", "Rite of Ruin",
    # grupo C: com reanimacao
    "Living Death", "Living End", "Bringer of the Last Gift",
    # grupo D: por tipo
    "Scrap Mastery", "All Is Dust",
    # grupo E: so' os oponentes sacrificam (ou escolha minha)
    "Extus, Oriq Overlord // Awaken the Blood Avatar", "Vona's Hunger", "Make an Example", "Syphon Flesh", "Perilous Predicament", "Crackling Doom", "Rush of Dread",
    "Skull Storm", "Choice of Damnations", "Portal to Phyrexia", "Urborg Justice", "Martyr's Bond", "Butcher of Malakir", "Dusk Mangler", "Malfegor", "Gix's Command",
    "Legate Lanius, Caesar's Ace", "Din of the Fireherd", "Dead Drop", "Curse of the Cabal",
    # mistos (vida/descarte/metade)
    "Fraying Omnipotence", "Pox", "Pox Plague", "Death Cloud",
    # o deck: o que decide a avaliacao
    "Blasphemous Act", "Blood Money", "Mayhem Devil", "Dictate of Erebos", "Teferi's Protection", "Boros Charm", "Vihaan, Goldwaker", "Mirkwood Bats", "Pitiless Plunderer",
    "Zulaport Cutthroat", "Mahadi, Emporium Master", "Krark-Clan Ironworks", "Ashnod's Altar", "Deadly Dispute", "Sevinne's Reclamation", "Life Insurance", "Revel in Riches",
]


def get(url):
    for t in range(4):
        r = subprocess.run(["curl", "-sS", "--max-time", "40", url], capture_output=True, text=True)
        time.sleep(0.12)
        try:
            return json.loads(r.stdout)
        except Exception:
            time.sleep(1 + t)
    raise RuntimeError(url)


saida = {}
for n in CANDIDATAS:
    c = get("https://api.scryfall.com/cards/named?exact=" + urllib.parse.quote(n))
    if c.get("object") == "error":
        c = get("https://api.scryfall.com/cards/named?fuzzy=" + urllib.parse.quote(n))
    if c.get("object") == "error":
        saida[n] = {"erro": c.get("details")}
        print("ERRO", n, c.get("details"))
        continue
    r = get(c["rulings_uri"])
    faces = c.get("card_faces") or [c]
    saida[n] = {"name": c["name"], "oracle_id": c["oracle_id"], "type_line": c["type_line"], "mana_cost": c.get("mana_cost") or " // ".join(f.get("mana_cost", "") for f in faces), "cmc": c["cmc"],
                "oracle_text": c.get("oracle_text") or "\n//\n".join(f.get("oracle_text", "") for f in faces), "faces": [{"name": f.get("name"), "mana_cost": f.get("mana_cost"), "type_line": f.get("type_line"), "power": f.get("power"),
                "toughness": f.get("toughness"), "oracle_text": f.get("oracle_text")} for f in faces], "power": c.get("power"), "toughness": c.get("toughness"), "color_identity": c["color_identity"],
                "legal_commander": c["legalities"]["commander"], "game_changer": c.get("game_changer"), "set": c.get("set"), "released_at": c.get("released_at"), "prices_usd": c.get("prices", {}).get("usd"),
                "rulings": [(x["published_at"], x["comment"]) for x in r.get("data", [])]}
json.dump(saida, open(os.path.join(AQUI, "..", "dados", "oraculo_candidatas_rulings.json"), "w"), ensure_ascii=False, indent=1)
for n, v in saida.items():
    if "erro" in v:
        continue
    print("=====", v["name"], "|", v["type_line"], "|", v["mana_cost"], "| commander:", v["legal_commander"], "| GC:", v["game_changer"], "| id:", v["color_identity"], "| US$", v["prices_usd"])
    print(v["oracle_text"])
    for d, t in v["rulings"]:
        print(" -", d, t)

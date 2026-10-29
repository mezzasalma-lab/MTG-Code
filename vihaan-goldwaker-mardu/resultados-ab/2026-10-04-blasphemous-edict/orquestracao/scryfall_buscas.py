"""Buscas ao vivo no Scryfall pra avaliacao Act x Edict: (1) Blasphemous Edict e' Game Changer? (2) outras magias de 'cada jogador sacrifica' / wipe por sacrificio na identidade
R/W/B legais em Commander (so' listadas, NAO avaliadas). Guarda as respostas cruas em ../dados/scryfall_buscas.json.
Uso (da raiz do repositorio): SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-04-blasphemous-edict/orquestracao/scryfall_buscas.py"""
import json, os, subprocess, time, urllib.parse
AQUI = os.path.dirname(os.path.abspath(__file__))
def get(q):
    r = subprocess.run(["curl", "-sS", "--max-time", "40", "https://api.scryfall.com/cards/search?order=cmc&q=" + urllib.parse.quote(q)], capture_output=True, text=True)
    time.sleep(0.15)
    return json.loads(r.stdout)
buscas = {
    "game_changer": 'is:gamechanger name:"Blasphemous Edict"',
    "edict_sorcery_rwb": 'f:commander id<=rwb t:sorcery o:"each player sacrifices" -o:"sacrifices a creature of their choice, then"',
    "wipe_sacrificio_rwb": 'f:commander id<=rwb (t:sorcery OR t:instant) (o:"sacrifices all" OR o:"sacrifices thirteen" OR o:"sacrifices each" OR (o:"each player sacrifices" o:creatures))',
}
saida = {k: get(q) for k, q in buscas.items()}
json.dump(saida, open(os.path.join(AQUI, "..", "dados", "scryfall_buscas.json"), "w"), ensure_ascii=False, indent=1)
gc = saida["game_changer"]
print("1) Blasphemous Edict e' Game Changer?", "SIM" if gc.get("total_cards") else "NAO (busca is:gamechanger sem resultado: %s)" % gc.get("details", gc.get("object")))
for k in ("edict_sorcery_rwb", "wipe_sacrificio_rwb"):
    r = saida[k]
    print(f"\n2) {k}: {r.get('total_cards', 0)} cartas")
    for c in r.get("data", [])[:25]:
        print("   -", c["name"], "|", c.get("mana_cost"), "|", c["type_line"], "|", (c.get("oracle_text") or "").replace("\n", " ")[:200])

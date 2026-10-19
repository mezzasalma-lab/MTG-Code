"""Completa o `scryfall-cache/oracle-cache.json` com o oraculo de TODA carta vista na sessao de 2026-10-19 (Regras 14 e 15): os 1.219 decks do EDHREC (Moxfield + Archidekt), a pagina do Tam no EDHREC, as cartas citadas nas respostas do Commander Spellbook
(combos, "quase", variantes), as cartas dos reports do Mothman, e as colunas extras pedidas na linha de comando. Busca por NOME (`POST /cards/collection`, face da frente para carta de 2 faces), grava o bruto em dados/oraculos_vistos.json.xz,
acrescenta ao cache o que faltar e completa `card_faces`/`layout` das entradas de 2 faces que nao tinham (Regra 14: nunca `oracle_text` nulo).
Uso: python3 completa_cache.py <saida_bruto.json.xz> [nome extra ...]"""
import glob, json, lzma, os, re, sys, time, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
CACHE = os.path.join(R, "scryfall-cache", "oracle-cache.json")
TAM = os.path.join(R, "tam-the-possibility-wubrg", "resultados-ab")
CAMPOS = ['cmc', 'collector_number', 'color_identity', 'colors', 'keywords', 'legalities', 'loyalty', 'mana_cost', 'name', 'oracle_text', 'power', 'prices', 'released_at', 'scryfall_uri', 'set', 'toughness', 'type_line']
def post(ids):
    rq = urllib.request.Request("https://api.scryfall.com/cards/collection", data=json.dumps({"identifiers": ids}).encode(), headers={"Content-Type": "application/json", "User-Agent": "MTG-Code-audit/1.0", "Accept": "application/json"})
    for t in range(5):
        try: return json.load(urllib.request.urlopen(rq, timeout=90))
        except Exception: time.sleep(2 * (t + 1))
    raise RuntimeError("scryfall")
def nomes_do_spellbook(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and " + " in k: acc.update(x.strip() for x in k.split(" + "))
            nomes_do_spellbook(v, acc)
    elif isinstance(o, list):
        for v in o:
            if isinstance(v, str) and " + " in v: acc.update(x.strip() for x in v.split(" + "))
            else: nomes_do_spellbook(v, acc)
def coleta():
    nomes = set()
    for f in glob.glob(os.path.join(TAM, "*", "dados", "decks_edhrec.jsonl.xz")):
        for l in lzma.open(f, "rt", encoding="utf-8"):
            for t, lst in json.loads(l)["cards"].items(): nomes.update(n for n, q in lst)
    for f in glob.glob(os.path.join(TAM, "*", "dados", "spellbook_*.json")): nomes_do_spellbook(json.load(open(f)), nomes)
    for f in glob.glob(os.path.join(TAM, "*", "dados", "edhrec_tam.json.xz")):
        def walk(o):
            if isinstance(o, dict):
                if isinstance(o.get("name"), str) and ("sanitized" in o or "synergy" in o or "inclusion" in o): nomes.add(o["name"])
                for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(json.load(lzma.open(f, "rt", encoding="utf-8")))
    return nomes
if __name__ == "__main__":
    saida, extras = sys.argv[1], sys.argv[2:]
    cache = json.load(open(CACHE, encoding="utf-8")); tem = set(cache); frente = {k.split(" // ")[0] for k in tem if " // " in k}
    pedir = sorted(n for n in (coleta() | set(extras)) if n not in tem and n not in frente)
    print("nomes vistos que faltam no cache:", len(pedir), flush=True)
    bruto = {}; nf = []
    for i in range(0, len(pedir), 70):
        r = post([{"name": n.split(" // ")[0]} for n in pedir[i:i + 70]])
        for c in r["data"]:
            if c.get("layout") in ("token", "emblem", "double_faced_token", "art_series"): continue
            bruto[c["name"]] = c
        nf += [x.get("name") for x in r.get("not_found", [])]; time.sleep(0.12)
    print("resolvidas:", len(bruto), "| nao encontradas:", nf, flush=True)
    # entradas de 2 faces ja' no cache sem card_faces: refaz
    sem_faces = sorted(k for k, v in cache.items() if " // " in k and not v.get("card_faces"))
    print("entradas de 2 faces sem card_faces no cache:", len(sem_faces), flush=True)
    for i in range(0, len(sem_faces), 70):
        r = post([{"name": n.split(" // ")[0]} for n in sem_faces[i:i + 70]])
        for c in r["data"]: bruto[c["name"]] = c
        time.sleep(0.12)
    json.dump(bruto, lzma.open(saida, "wt", preset=9), ensure_ascii=False)
    add = 0; fix = 0
    for n, c in bruto.items():
        faces = c.get("card_faces") or []
        txt = c.get("oracle_text") or " // ".join(f.get("oracle_text", "") for f in faces)
        if n not in cache:
            if not txt and "Land" not in (c.get("type_line") or ""): print("SEM ORACULO:", n); continue
            cache[n] = {f: c.get(f) for f in CAMPOS}; cache[n]["oracle_text"] = txt; add += 1
        e = cache[n]
        if faces and not e.get("card_faces"):
            e["card_faces"] = [{"name": f.get("name"), "mana_cost": f.get("mana_cost"), "type_line": f.get("type_line"), "oracle_text": f.get("oracle_text"), "power": f.get("power"), "toughness": f.get("toughness"), "loyalty": f.get("loyalty")} for f in faces]
            if not e.get("oracle_text"): e["oracle_text"] = txt
            fix += 1
        if c.get("layout") and not e.get("layout"): e["layout"] = c["layout"]
        if c.get("game_changer") is not None and e.get("game_changer") is None: e["game_changer"] = c["game_changer"]
    open(CACHE, "w", encoding="utf-8").write(json.dumps(cache, indent=2, ensure_ascii=False) + "\n")
    vazios = [k for k, v in cache.items() if not v.get("oracle_text") and "Land" not in (v.get("type_line") or "")]
    print("acrescentadas:", add, "| faces completadas:", fix, "| cache:", len(cache), "| sem oraculo (nao terreno):", len(vazios), vazios[:10], flush=True)

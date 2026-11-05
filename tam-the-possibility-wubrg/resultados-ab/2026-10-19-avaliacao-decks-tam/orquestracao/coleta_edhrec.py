"""Coleta as listas de decks do Tam, the Possibility publicadas (EDHREC guarda as listas enviadas pelos usuarios; o Moxfield bloqueia acesso automatizado: HTTP 403 do Cloudflare, nao contornado).
1) baixa a tabela de decks (`json.edhrec.com/pages/decks/tam-the-possibility.json`, 6.931 decks em 2026-10-19);
2) escolhe os decks com bracket declarado 3 ou 4 + uma amostra aleatoria (semente fixa) dos sem bracket;
3) baixa `edhrec.com/api/deckpreview/<urlhash>` de cada um e grava so' os campos uteis (url de origem, bracket, preco, salt, comandantes, cartas por tipo, tags).
Uso: python3 coleta_edhrec.py <saida.jsonl> [n_amostra_sem_bracket]"""
import json, os, random, sys, time, urllib.request, concurrent.futures as cf
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
UA = {"User-Agent": "MTG-Code-audit/1.0"}
def get(u, tries=4):
    for t in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
        except Exception as e:
            if "429" in str(e): time.sleep(20)
            time.sleep(1.5 * (t + 1))
    return None
out, n_amostra = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 500
tabela = get("https://json.edhrec.com/pages/decks/tam-the-possibility.json")["table"]
com_b = [t for t in tabela if t["bracket"] in (3, 4)]; sem_b = [t for t in tabela if t["bracket"] is None]
random.Random(20261019).shuffle(sem_b); escolha = com_b + sem_b[:n_amostra]
print("tabela:", len(tabela), "| bracket 3/4:", len(com_b), "| amostra sem bracket:", min(n_amostra, len(sem_b)), "| a baixar:", len(escolha), flush=True)
def um(t):
    time.sleep(0.12); r = get("https://edhrec.com/api/deckpreview/" + t["urlhash"])
    if not r: return {"urlhash": t["urlhash"], "erro": True, "tabela": t}
    return {"urlhash": t["urlhash"], "url": r.get("url"), "bracket": t["bracket"], "price": r.get("price"), "salt": r.get("salt"), "savedate": r.get("savedate"), "tags": r.get("tags"), "commanders": r.get("commanders"),
            "tipos": {k: r.get(k) for k in ("creature", "instant", "sorcery", "artifact", "enchantment", "planeswalker", "land", "basic")}, "cards": r["deck"]["cards"], "commander_v2": r["deck"].get("commander_v2")}
n = 0
with open(out, "w", encoding="utf-8") as f, cf.ThreadPoolExecutor(4) as ex:
    for r in ex.map(um, escolha):
        f.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
        if n % 100 == 0: print(n, "/", len(escolha), flush=True)
print("fim", n, flush=True)

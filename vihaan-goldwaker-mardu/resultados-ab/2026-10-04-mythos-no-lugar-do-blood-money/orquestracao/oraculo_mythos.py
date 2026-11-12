"""Oraculo e rulings AO VIVO (Scryfall) da Mythos of Snapdax e do Blood Money (Regra #1/#2: nunca de memoria), checagem de legalidade e identidade de cor, e o CMC medio dos nao-terrenos
ANTES e DEPOIS da troca (conta por script, cmc lido do cache ao vivo da rodada dos wipes de sacrificio: ../../2026-10-04-wipes-de-sacrificio/dados/oraculo_lista_ao_vivo.json.xz).
Uso (de dentro de orquestracao/): SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 oraculo_mythos.py          -> consulta a API e grava ../dados/oraculo_rulings_ao_vivo.json
                                  python3 oraculo_mythos.py --sum                                       -> refaz so' o texto a partir do bruto arquivado"""
import collections, json, lzma, os, re, sys, time, urllib.parse, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(AQUI, "..", "..", "..")
ARQ = os.path.join(AQUI, "..", "dados", "oraculo_rulings_ao_vivo.json")
CARTAS = ["Mythos of Snapdax", "Blood Money"]


def get(url):
    for t in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MTG-Code-audit/1.0", "Accept": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            print("   retry", t, repr(e)[:80], file=sys.stderr); time.sleep(2 + 2 * t)
    raise RuntimeError(url)


if "--sum" in sys.argv:
    dados = json.load(open(ARQ))
else:
    dados = {}
    for n in CARTAS:
        c = get("https://api.scryfall.com/cards/named?exact=" + urllib.parse.quote(n))
        time.sleep(0.2)
        r = get(c["rulings_uri"])["data"]
        dados[n] = {"card": c, "rulings": r}
    json.dump(dados, open(ARQ, "w"), ensure_ascii=False, indent=1)
for n in CARTAS:
    c, r = dados[n]["card"], dados[n]["rulings"]
    print(f"=== {c['name']} | {c['mana_cost']} (cmc {c['cmc']}) | {c['type_line']} | cores {c['colors']} | identidade {c['color_identity']} | commander: {c['legalities']['commander']} | flavor_name: {c.get('flavor_name')}")
    print("   oraculo:", c["oracle_text"].replace("\n", " / "))
    for x in r:
        print(f"   ruling {x['published_at']}: {x['comment']}")


def parse(path):
    out, sec = [], None
    for l in open(path):
        l = l.rstrip("\n")
        if l.startswith("#"):
            sec = l.lstrip("# ").strip().lower(); continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if m and sec and not sec.startswith("comandante"):
            out += [m.group(2).strip()] * int(m.group(1))
    return out


cache = json.load(lzma.open(os.path.join(DECK, "resultados-ab", "2026-10-04-wipes-de-sacrificio", "dados", "oraculo_lista_ao_vivo.json.xz"), "rt"))
cache["Mythos of Snapdax"] = dados["Mythos of Snapdax"]["card"]
antes = parse(os.path.join(DECK, "resultados-ab", "_lista_legada", "lista.md"))
depois = parse(os.path.join(DECK, "lista.md"))


def nao_terrenos(lista):
    return [n for n in lista if "Land" not in cache[n]["type_line"].split(" // ")[0]]


for nome, lista in (("ANTES (Blood Money)", antes), ("DEPOIS (Mythos)", depois)):
    nt = nao_terrenos(lista)
    print(f"\n{nome}: cartas={len(lista)} | terrenos={len(lista) - len(nt)} | nao-terrenos={len(nt)} | CMC medio dos nao-terrenos = {sum(cache[n]['cmc'] for n in nt) / len(nt):.4f} (soma {sum(cache[n]['cmc'] for n in nt):.0f})")
tre = lambda l: sorted({n for n in l if re.search(r"create[^.]*Treasure|Treasure token", cache[n].get("oracle_text") or "", re.I) and "Land" not in cache[n]["type_line"].split(" // ")[0]})
print("\nCartas da lista cujo oraculo cria Treasure (varredura literal por 'Treasure' em create/token): ANTES %d | DEPOIS %d | saiu: %s | entrou: %s" % (
    len(tre(antes)), len(tre(depois)), sorted(set(tre(antes)) - set(tre(depois))), sorted(set(tre(depois)) - set(tre(antes)))))

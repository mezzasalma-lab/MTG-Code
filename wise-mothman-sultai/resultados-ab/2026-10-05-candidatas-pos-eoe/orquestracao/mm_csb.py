"""Commander Spellbook para a lista do Mothman: base e cenarios (sai/entra). Uso: python3 mm_csb.py <lista.md> <cenarios.json> <saida.json>
cenarios.json: {"nome_do_cenario": {"sai": [...], "entra": [...]}, ...}. O cenario 'base' e' sempre rodado. Controle positivo: ver cenarios_controle.json."""
import json, os, re, sys, time, urllib.request, collections
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
CMD = "The Wise Mothman"
def parse(path):
    cards = []; sec = None
    for l in open(path):
        l = l.rstrip("\n")
        if l.startswith("#"):
            sec = l.lstrip("# ").strip().lower(); continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if m and sec and not sec.startswith("comandante"):
            cards += [m.group(2).strip()] * int(m.group(1))
    return cards
def query(deck):
    cnt = collections.Counter(deck)
    body = {"commanders": [{"card": CMD}], "main": [{"card": c, "quantity": q} for c, q in cnt.items()]}
    req = urllib.request.Request("https://backend.commanderspellbook.com/find-my-combos", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "MTG-Code-audit/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=240))["results"]
def key(c): return " + ".join(sorted(u["card"]["name"] for u in c["uses"]))
def resumo(r):
    inc = {key(c): {"produz": [p["feature"]["name"] if "feature" in p else p.get("name", str(p)) for p in c.get("produces", [])][:4],
                    "id": c.get("id"), "bracket": c.get("bracketTag"), "popularidade": c.get("popularity")} for c in r["included"]}
    alm = sorted(key(c) for c in r["almostIncluded"])
    return inc, alm
if __name__ == "__main__":
    lista, cen, out = sys.argv[1], sys.argv[2], sys.argv[3]
    base = parse(lista)
    cenarios = {"base": {"sai": [], "entra": []}}
    cenarios.update(json.load(open(cen)) if os.path.exists(cen) and os.path.getsize(cen) else {})
    res = {}
    for nome, c in cenarios.items():
        deck = list(base)
        for x in c.get("sai", []):
            deck.remove(x)
        deck += c.get("entra", [])
        r = query(deck); inc, alm = resumo(r)
        res[nome] = {"n_cartas_main": len(deck), "sai": c.get("sai", []), "entra": c.get("entra", []), "incluidos": inc, "quase_incluidos": alm, "identidade": r.get("identity")}
        print(f"{nome:44s} main={len(deck):3d} incluidos={len(inc):3d} quase={len(alm):4d} id={r.get('identity')}")
        time.sleep(0.5)
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)

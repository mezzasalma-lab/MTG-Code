"""Commander Spellbook antes/depois para uma lista do repositório. Uso: python3 csb_generic.py <deck_dir> "<commander>" <saida.json> [sai1,sai2,...] <entra>
Lê <deck_dir>/lista.md (linhas 'N Nome'), remove 'sai' e adiciona 'entra'; consulta POST /find-my-combos."""
import json, os, re, sys, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")

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

def query(cmd, deck):
    body = {"commanders": [{"card": cmd}], "main": [{"card": c, "quantity": 1} for c in sorted(set(deck))]}
    # básicas: quantidade
    from collections import Counter
    cnt = Counter(deck)
    body["main"] = [{"card": c, "quantity": q} for c, q in cnt.items()]
    req = urllib.request.Request("https://backend.commanderspellbook.com/find-my-combos", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "MTG-Code-audit/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=180))["results"]

def summarize(r):
    def key(c): return tuple(sorted(u["card"]["name"] for u in c["uses"]))
    return ({key(c): [p["name"] if isinstance(p, dict) and "name" in p else str(p) for p in c.get("produces", [])][:3] for c in r["included"]},
            {key(c) for c in r["almostIncluded"]})

if __name__ == "__main__":
    d, cmd, out = sys.argv[1], sys.argv[2], sys.argv[3]
    cuts = [x for x in sys.argv[4].split("|") if x]; entra = sys.argv[5] if len(sys.argv) > 5 else None
    base = parse(os.path.join(d, "lista.md"))
    print("cartas na lista:", len(base))
    res = {}
    def run(name, deck):
        r = query(cmd, deck); inc, alm = summarize(r)
        res[name] = {"n": len(deck), "incluidos": {" + ".join(k): v for k, v in inc.items()}, "quase": sorted(" + ".join(k) for k in alm), "identidade": r.get("identity")}
        print(f"{name:34s} n={len(deck)} incluidos={len(inc)} quase={len(alm)} id={r.get('identity')}")
        return inc, alm
    binc, balm = run("base", base)
    if entra:
        inc, alm = run(f"+{entra} (sem cortar)", base + [entra])
        print("   novos incluidos:", sorted(set(inc) - set(binc)), "| novos quase:", len(alm - balm))
        for k in sorted(alm - balm)[:15]: print("      quase +", k)
        for c in cuts:
            deck = list(base); deck.remove(c); deck.append(entra)
            inc, alm = run(f"-{c} +{entra}", deck)
            print("   incluidos que SUMIRAM:", sorted(set(binc) - set(inc)), "| NOVOS:", sorted(set(inc) - set(binc)))
            print("   quase sumiram:", len(balm - alm), "| quase novos:", len(alm - balm))
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)

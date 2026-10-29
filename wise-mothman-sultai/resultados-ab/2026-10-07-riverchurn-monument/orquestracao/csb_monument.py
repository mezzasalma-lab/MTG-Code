"""Commander Spellbook ANTES/DEPOIS para Riverchurn Monument no Mothman (Regra #4 adendo 2026-09-28 + achado de 2026-10-05).
1) resolve cada nome via GET /cards/?q= e REGISTRA se o Spellbook reconhece (a API ignora nome desconhecido, sem erro);
2) roda a lista base; 3) roda `Monument <- X` para CADA carta nao-basica da lista (X != comandante); 4) controle positivo (combo conhecido tem de aparecer)
e controle de corte (cortar peca de combo da lista tem de fazer o combo sumir).
Uso: python3 csb_monument.py <lista.md> <saida.json> [workers]"""
import json, os, re, sys, time, urllib.request, urllib.parse, collections, concurrent.futures as cf
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
CMD = "The Wise Mothman"
MON = "Riverchurn Monument"
BASICOS = {"Forest", "Island", "Swamp"}
def parse(path):
    cards = []; sec = None
    for l in open(path, encoding="utf-8"):
        l = l.rstrip("\n")
        if l.startswith("#"):
            sec = l.lstrip("# ").strip().lower(); continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if m and sec and not sec.startswith("comandante"):
            cards += [m.group(2).strip()] * int(m.group(1))
    return cards
def http(url, data=None, tries=4):
    for t in range(tries):
        try:
            rq = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "MTG-Code-audit/1.0"})
            return json.load(urllib.request.urlopen(rq, timeout=240))
        except Exception:
            time.sleep(2 * (t + 1))
    raise RuntimeError(url)
def query(deck):
    cnt = collections.Counter(deck)
    body = {"commanders": [{"card": CMD}], "main": [{"card": c, "quantity": q} for c, q in cnt.items()]}
    return http("https://backend.commanderspellbook.com/find-my-combos", json.dumps(body).encode())["results"]
def key(c): return " + ".join(sorted(u["card"]["name"] for u in c["uses"]))
def resumo(r):
    inc = {key(c): {"produz": [p["feature"]["name"] if "feature" in p else p.get("name", str(p)) for p in c.get("produces", [])][:4],
                    "id": c.get("id"), "bracket": c.get("bracketTag"), "popularidade": c.get("popularity")} for c in r["included"]}
    alm = sorted(key(c) for c in r["almostIncluded"])
    return inc, alm
def resolve(n):
    d = http("https://backend.commanderspellbook.com/cards/?" + urllib.parse.urlencode({"q": n, "limit": 10}))
    nomes = [x["name"] for x in d["results"]]
    for x in nomes:
        if x.lower() == n.lower(): return x
    for x in nomes:
        if x.split(" // ")[0].lower() == n.split(" // ")[0].lower(): return x
    return None
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    base = parse(lista)
    distintas = sorted({c for c in base if c not in BASICOS})
    # 1) reconhecimento de nomes (todas as cartas da lista + Monument + comandante + controle positivo)
    extras = [MON, CMD, "Thassa's Oracle", "Demonic Consultation"]
    nomes = distintas + extras
    reconhece = {}
    with cf.ThreadPoolExecutor(W) as ex:
        for n, r in zip(nomes, ex.map(resolve, nomes)):
            reconhece[n] = r
    nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos pelo Spellbook:", nao, flush=True)
    base_res = query(base); binc, balm = resumo(base_res)
    print("base: main", len(base), "incluidos", len(binc), "quase", len(balm), flush=True)
    def cen(sai, entra):
        deck = list(base)
        for x in sai: deck.remove(x)
        deck += entra
        r = query(deck); inc, alm = resumo(r)
        return {"n_main": len(deck), "sai": sai, "entra": entra, "incluidos": inc, "quase": alm}
    res = {}
    def um(x):
        c = cen([x], [MON])
        c["novos"] = {k: v for k, v in c["incluidos"].items() if k not in binc}
        c["sumiram"] = [k for k in binc if k not in c["incluidos"]]
        c["quase_novos"] = sorted(set(c["quase"]) - set(balm))
        c["quase_novos_com_monument"] = [k for k in c["quase_novos"] if MON in k]
        c["quase_sumiram"] = sorted(set(balm) - set(c["quase"]))
        del c["incluidos"], c["quase"]
        return x, c
    with cf.ThreadPoolExecutor(W) as ex:
        for i, (x, c) in enumerate(ex.map(um, distintas), 1):
            res[x] = c
            if i % 10 == 0: print(i, "/", len(distintas), flush=True)
    # Monument sozinho (lista com 100 nao-comandante: so' pra ver se a PECA entra em algum combo)
    so = cen([], [MON]); so["novos"] = {k: v for k, v in so["incluidos"].items() if k not in binc}
    so["quase_com_monument"] = [k for k in so["quase"] if MON in k]; del so["incluidos"], so["quase"]
    # controles
    pos = cen(["Negate", "Swiftfoot Boots"], ["Thassa's Oracle", "Demonic Consultation"])
    pos["achou_thassa_consultation"] = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in pos["incluidos"])
    corte = cen(["Mindcrank"], ["Evolution Sage"])
    corte["combo_ascension_mindcrank_sumiu"] = not any("Bloodchief Ascension" in k and "Mindcrank" in k for k in corte["incluidos"])
    corte["base_tem_ascension_mindcrank"] = any("Bloodchief Ascension" in k and "Mindcrank" in k for k in binc)
    for c in (pos, corte): del c["incluidos"], c["quase"]
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "base": {"incluidos": binc, "quase_n": len(balm)}, "monument_por_corte": res,
               "monument_sem_cortar": so, "controle_positivo": pos, "controle_corte": corte}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo (Thassa+Consultation apareceu):", pos["achou_thassa_consultation"])
    print("controle de corte (base tem Ascension+Mindcrank; sumiu ao cortar Mindcrank):", corte["base_tem_ascension_mindcrank"], corte["combo_ascension_mindcrank_sumiu"])

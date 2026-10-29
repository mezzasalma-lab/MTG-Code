"""Commander Spellbook para o deck Beorn, ANTES (com Ram Through) e DEPOIS (com Herd Heirloom) da troca pedida pelo usuario em 2026-10-23 (Regra #4 + adendo, item 2).
1) resolve cada nome via GET /cards/?q= e REGISTRA se o Spellbook reconhece (a API ignora nome desconhecido, sem erro: achado de 2026-10-05);
2) combos do deck ANTES e DEPOIS (comandante + 99), e o que o Spellbook diz estar a UMA carta de distancia ("quase");
3) controle positivo (trocar duas cartas por Basalt Monolith + Rings of Brighthearth, os dois incolores: o combo deles tem de aparecer) e controle de corte (so' o Basalt Monolith: o combo tem de SUMIR).
Uso: python3 csb_beorn.py <lista.md ANTES> <saida.json>   (a lista DEPOIS e' a mesma com Ram Through -> Herd Heirloom)"""
import json, os, re, sys, time, urllib.request, urllib.parse, collections, concurrent.futures as cf
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
CMD = "Beorn the Fierce"
def parse(path):
    main = []; sec = None
    for l in open(path, encoding="utf-8"):
        l = l.rstrip("\n")
        if l.startswith("#"):
            sec = l.lstrip("# ").strip().lower(); continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if not m or not sec or sec.startswith("comandante"): continue
        main += [m.group(2).strip()] * int(m.group(1))
    return main
def http(url, data=None, tries=4):
    for t in range(tries):
        try:
            rq = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "MTG-Code-audit/1.0"})
            return json.load(urllib.request.urlopen(rq, timeout=240))
        except Exception:
            time.sleep(2 * (t + 1))
    raise RuntimeError(url)
def query(deck, cmd=CMD):
    cnt = collections.Counter(deck)
    body = {"commanders": [{"card": cmd}], "main": [{"card": c, "quantity": q} for c, q in cnt.items()]}
    return http("https://backend.commanderspellbook.com/find-my-combos", json.dumps(body).encode())["results"]
def key(c): return " + ".join(sorted(u["card"]["name"] for u in c["uses"]))
def resumo(r):
    pn = lambda c: [p["feature"]["name"] if "feature" in p else p.get("name", str(p)) for p in c.get("produces", [])]
    inc = {key(c): {"produz": pn(c)[:4], "id": c.get("id"), "bracket": c.get("bracketTag"), "descricao": (c.get("description") or "")[:400]} for c in r["included"]}
    alm = {key(c): {"produz": pn(c)[:3], "id": c.get("id"), "bracket": c.get("bracketTag")} for c in r["almostIncluded"]}
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
    antes = parse(lista); assert len(antes) == 99 and "Ram Through" in antes, (len(antes))
    depois = [("Herd Heirloom" if c == "Ram Through" else c) for c in antes]; assert len(depois) == 99 and len(set(depois)) == len(set(antes))
    nomes = sorted(set(antes) | set(depois) | {CMD, "Basalt Monolith", "Rings of Brighthearth", "Mind Stone"})
    with cf.ThreadPoolExecutor(3) as ex: reconhece = dict(zip(nomes, ex.map(resolve, nomes)))
    nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos pelo Spellbook:", nao, flush=True)
    res = {}
    for rotulo, deck in (("antes_ram_through", antes), ("depois_herd_heirloom", depois)):
        inc, alm = resumo(query(deck)); res[rotulo] = {"incluidos": inc, "quase": alm}
        print(rotulo, ": combos incluidos", len(inc), "| quase (1 carta de distancia)", len(alm), flush=True)
        for k, v in inc.items(): print("  COMBO:", k, "|", v["produz"], "| bracket", v["bracket"], flush=True)
    pos = list(depois); pos.remove("Sol Ring"); pos.remove("Thought Vessel"); pos += ["Basalt Monolith", "Rings of Brighthearth"]; assert len(pos) == 99
    pinc, _ = resumo(query(pos)); achou = any("Basalt Monolith" in k and "Rings of Brighthearth" in k for k in pinc)
    cor = list(depois); cor.remove("Sol Ring"); cor.remove("Thought Vessel"); cor += ["Basalt Monolith", "Mind Stone"]; assert len(cor) == 99      # igual ao positivo, com o Rings trocado por uma pedra neutra
    cinc, _ = resumo(query(cor)); sumiu = not any("Basalt Monolith" in k and "Rings of Brighthearth" in k for k in cinc)
    dif_inc = sorted(set(res["antes_ram_through"]["incluidos"]) ^ set(res["depois_herd_heirloom"]["incluidos"]))
    dif_alm = sorted(set(res["antes_ram_through"]["quase"]) ^ set(res["depois_herd_heirloom"]["quase"]))
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, **res, "diferenca_combos_incluidos": dif_inc, "diferenca_quase": dif_alm,
               "controle_positivo_basalt_rings": achou, "controle_de_corte_combo_sumiu_sem_o_rings": sumiu, "controle_positivo_n_combos": len(pinc)}, open(out, "w"), ensure_ascii=False, indent=1)
    print("diferenca nos combos incluidos (antes x depois):", dif_inc, "| nos 'quase':", dif_alm)
    print("controle positivo (Basalt Monolith + Rings aparece):", achou, "| controle de corte (sem o Rings some):", sumiu)

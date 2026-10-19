"""Commander Spellbook para o deck Tam, the Possibility (Regra #4 + adendo; registro de 2026-10-19).
1) resolve cada nome (comandante + 99 do deck + 13 do sideboard) via GET /cards/?q= e REGISTRA se o Spellbook reconhece (a API ignora nome desconhecido, sem erro: achado de 2026-10-05);
2) combos do deck exato (comandante + 99; o sideboard NAO entra);
3) controle positivo (trocar duas cartas por Thassa's Oracle + Demonic Consultation: o combo deles tem de aparecer) e controle de corte (so' o Thassa's Oracle: o combo tem de SUMIR);
4) o que o Spellbook diz estar a UMA carta de distancia ("quase").
Uso: python3 csb_tam.py <lista.md> <saida.json>"""
import json, os, re, sys, time, urllib.request, urllib.parse, collections, concurrent.futures as cf
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
CMD = "Tam, the Possibility"
def parse(path):
    main, side = [], []; sec = None
    for l in open(path, encoding="utf-8"):
        l = l.rstrip("\n")
        if l.startswith("#"):
            sec = l.lstrip("# ").strip().lower(); continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if not m or not sec: continue
        alvo = side if sec.startswith("sideboard") else (None if sec.startswith("comandante") else main)
        if alvo is not None: alvo += [m.group(2).strip()] * int(m.group(1))
    return main, side
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
    inc = {key(c): {"produz": [p["feature"]["name"] if "feature" in p else p.get("name", str(p)) for p in c.get("produces", [])][:4], "id": c.get("id"), "bracket": c.get("bracketTag"), "popularidade": c.get("popularity"),
                    "descricao": (c.get("description") or "")[:400]} for c in r["included"]}
    alm = {key(c): {"produz": [p["feature"]["name"] if "feature" in p else p.get("name", str(p)) for p in c.get("produces", [])][:3], "id": c.get("id"), "bracket": c.get("bracketTag")} for c in r["almostIncluded"]}
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
    main, side = parse(lista); assert len(main) == 99 and len(side) == 13, (len(main), len(side))
    nomes = sorted(set(main) | set(side) | {CMD, "Thassa's Oracle", "Demonic Consultation", "Mind Stone"})
    with cf.ThreadPoolExecutor(3) as ex: reconhece = dict(zip(nomes, ex.map(resolve, nomes)))
    nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos pelo Spellbook:", nao, flush=True)
    inc, alm = resumo(query(main)); print("deck exato: combos incluidos", len(inc), "| quase (1 carta de distancia)", len(alm), flush=True)
    for k, v in inc.items(): print("  COMBO:", k, "|", v["produz"], "| bracket", v["bracket"], flush=True)
    pos = list(main); pos.remove("Sol Ring"); pos.remove("Arcane Signet"); pos += ["Thassa's Oracle", "Demonic Consultation"]; assert len(pos) == 99
    pinc, _ = resumo(query(pos)); achou = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in pinc)
    cor = list(main); cor.remove("Sol Ring"); cor.remove("Arcane Signet"); cor += ["Thassa's Oracle", "Mind Stone"]; assert len(cor) == 99      # igual ao positivo, com a Consultation trocada por uma pedra neutra
    cinc, _ = resumo(query(cor)); sumiu = not any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in cinc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "deck": {"incluidos": inc, "quase": alm}, "controle_positivo_thassa_consultation": achou, "controle_de_corte_combo_sumiu_sem_a_consultation": sumiu,
               "controle_positivo_n_combos": len(pinc)}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo (Thassa+Consultation aparece):", achou, "| controle de corte (sem a Consultation some):", sumiu)

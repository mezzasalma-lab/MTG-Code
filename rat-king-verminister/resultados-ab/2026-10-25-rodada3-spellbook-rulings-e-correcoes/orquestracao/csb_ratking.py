"""Commander Spellbook para o deck Rat King, Verminister (Regra #4 + adendo, item 2), lista ATUAL de lista.md (sem troca).
1) resolve cada nome via GET /cards/?q= e REGISTRA se o Spellbook reconhece (a API ignora nome desconhecido, sem erro: achado de 2026-10-05);
2) combos do deck (comandante + 99) e o que o Spellbook diz estar a UMA carta de distancia ("quase");
3) estimate-bracket (bracketTag do deck + combos classificados) com controle positivo (Necropotence = Game Changer);
4) controle positivo (trocar Sol Ring + Jet Medallion por Basalt Monolith + Rings of Brighthearth: o combo deles tem de aparecer) e controle de corte (so' o Basalt Monolith + Mind Stone: o combo tem de SUMIR).
Uso: python3 -I csb_ratking.py <lista.md> <saida.json>"""
import json, os, re, sys, time, urllib.request, urllib.parse, collections, concurrent.futures as cf
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
CMD = "Rat King, Verminister"
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
def estimate(deck, cmd=CMD):
    """POST /estimate-bracket: bracketTag estimado do deck + combos classificados (speed, definitelyTwoCard, relevant...)."""
    cnt = collections.Counter(deck)
    body = {"commanders": [{"card": cmd}], "main": [{"card": c, "quantity": q} for c, q in cnt.items()]}
    return http("https://backend.commanderspellbook.com/estimate-bracket", json.dumps(body).encode())
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
    deck = parse(lista); assert len(deck) == 99, len(deck)
    nomes = sorted(set(deck) | {CMD, "Basalt Monolith", "Rings of Brighthearth", "Mind Stone"})
    with cf.ThreadPoolExecutor(3) as ex: reconhece = dict(zip(nomes, ex.map(resolve, nomes)))
    nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos pelo Spellbook:", nao, flush=True)
    inc, alm = resumo(query(deck))
    print("combos incluidos:", len(inc), "| quase (1 carta de distancia):", len(alm), flush=True)
    for k, v in inc.items(): print("  COMBO:", k, "|", v["produz"], "| bracket", v["bracket"], flush=True)
    pos = list(deck); pos.remove("Sol Ring"); pos.remove("Jet Medallion"); pos += ["Basalt Monolith", "Rings of Brighthearth"]; assert len(pos) == 99
    pinc, _ = resumo(query(pos)); achou = any("Basalt Monolith" in k and "Rings of Brighthearth" in k for k in pinc)
    cor = list(deck); cor.remove("Sol Ring"); cor.remove("Jet Medallion"); cor += ["Basalt Monolith", "Mind Stone"]; assert len(cor) == 99
    cinc, _ = resumo(query(cor)); sumiu = not any("Basalt Monolith" in k and "Rings of Brighthearth" in k for k in cinc)
    est = estimate(deck)
    est_resumo = {"bracketTag": est["bracketTag"], "game_changers_na_lista": [c["card"]["name"] for c in est["cards"] if c["gameChanger"]],
                  "banidas": [c["card"]["name"] for c in est["cards"] if c["banned"]], "mass_land_denial": [c["card"]["name"] for c in est["cards"] if c["massLandDenial"]],
                  "extra_turn": [c["card"]["name"] for c in est["cards"] if c["extraTurn"]],
                  "combos_classificados": [{"combo": key(c["combo"]), "relevant": c["relevant"], "borderlineRelevant": c["borderlineRelevant"], "definitelyTwoCard": c["definitelyTwoCard"],
                                            "arguablyTwoCard": c["arguablyTwoCard"], "speed": c["speed"], "lock": c["lock"], "bracketTag_do_combo": c["combo"].get("bracketTag")} for c in est["combos"]]}
    print("estimate-bracket:", json.dumps(est_resumo, ensure_ascii=False))
    ctl = list(deck); ctl.remove("Sol Ring"); ctl.append("Necropotence")
    est_ctl = estimate(ctl); gc_ctl = [c["card"]["name"] for c in est_ctl["cards"] if c["gameChanger"]]
    print("controle positivo do estimate-bracket (trocar Sol Ring por Necropotence, Game Changer conhecida):", gc_ctl, "->", est_ctl["bracketTag"])
    json.dump({"estimate_bracket": est_resumo, "estimate_bracket_controle_positivo": {"game_changers": gc_ctl, "bracketTag": est_ctl["bracketTag"]}, "reconhece": reconhece, "nao_reconhecidos": nao, "incluidos": inc, "quase": alm,
               "controle_positivo_basalt_rings": achou, "controle_de_corte_combo_sumiu_sem_o_rings": sumiu, "controle_positivo_n_combos": len(pinc), "controle_corte_n_combos": len(cinc)},
              open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo (Basalt Monolith + Rings aparece):", achou, "| controle de corte (sem o Rings some):", sumiu)

"""Commander Spellbook para TODOS os decks do repositorio (pedido do usuario em 2026-10-28: "Quero todos os Spellbooks sim, e salvos no repositorio").
Para cada `<deck>/lista.md`: le o comandante (um por opcao, nos precons de 2+ comandantes os outros entram na lista) e as demais secoes (menos as de notas/mudancas), RESOLVE cada nome no Spellbook
(a API ignora, sem erro, nome que nao reconhece: achado de 2026-10-05), roda `find-my-combos` e `estimate-bracket`, e os controles (positivo: lista + Basalt Monolith + Rings of Brighthearth tem de mostrar o combo
deles; de corte: lista + Basalt Monolith + Mind Stone NAO pode). Grava por deck em `<deck>/resultados-ab/2026-10-28-spellbook/dados/` e um resumo central.
Uso: python3 -I csb_todos.py <raiz do repositorio> [deck ...]     (sem decks = todos; o rat-king-verminister ja' tem a rodada propria de 2026-10-25)"""
import collections, concurrent.futures as cf, glob, hashlib, json, os, re, sys, time, urllib.parse, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
RAIZ = os.path.abspath(sys.argv[1]); SO = sys.argv[2:]
DATA = "2026-10-28"
EXCL = re.compile(r"mudan|altera|game changers|links|notas|trocas|sugest|fora do|maybe|considera|sideboard|cortad|removid", re.I)
BASE = "https://backend.commanderspellbook.com"
def http(url, data=None, tries=8):
    for t in range(tries):
        try:
            rq = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "MTG-Code-audit/1.0"})
            return json.load(urllib.request.urlopen(rq, timeout=240))
        except Exception as e:
            time.sleep(2 * (t + 1) ** 1.5)
    raise RuntimeError(url)
def parse(path):
    """So' o que vem depois do 1o '## Comandante' (a prosa numerada do cabecalho, ex. Megatron, nao e' carta)."""
    txt = open(path, encoding="utf-8").read()
    i = txt.lower().find("## comandante")
    cmd, main = [], []; sec = None; skip = False
    for l in txt[i:].split("\n"):
        if l.startswith("#"):
            sec = l.lstrip("# ").strip(); skip = bool(EXCL.search(sec)); continue
        m = re.match(r"^\s*(\d+)\s*x?\s+(.+?)\s*$", l)
        if not m or skip: continue
        n, name = int(m.group(1)), m.group(2).strip()
        (cmd if sec.lower().startswith("comandante") else main).append((name, n))
    return cmd, main
def resolve(n):
    try:
        d = http(BASE + "/cards/?" + urllib.parse.urlencode({"q": n, "limit": 10}))
    except RuntimeError:
        return "ERRO"
    nomes = [x["name"] for x in d["results"]]
    for x in nomes:
        if x.lower() == n.lower(): return x
    for x in nomes:
        if x.split(" // ")[0].lower() == n.split(" // ")[0].lower(): return x
    return None
def key(c): return " + ".join(sorted(u["card"]["name"] for u in c["uses"]))
def comp(deck_main, commander):
    cnt = collections.Counter()
    for name, n in deck_main: cnt[name] += n
    return {"commanders": [{"card": commander}], "main": [{"card": c, "quantity": q} for c, q in cnt.items()]}
def pn(c): return [p["feature"]["name"] if "feature" in p else p.get("name", str(p)) for p in c.get("produces", [])]
RAW = {}   # respostas CRUAS da API desta execucao, gravadas por deck em dados/spellbook_raw_<deck>_<data>.json.xz (Regra #8)
def find(body, rot=None):
    bruto = http(BASE + "/find-my-combos", json.dumps(body).encode())
    if rot is not None: RAW[rot] = {"entrada": body, "resposta": bruto}
    r = bruto["results"]
    inc = {key(c): {"id": c.get("id"), "bracketTag": c.get("bracketTag"), "produz": pn(c)[:4], "usa": [u["card"]["name"] for u in c["uses"]], "prerequisitos": c.get("easyPrerequisites")} for c in r["included"]}
    alm = {key(c): {"id": c.get("id"), "bracketTag": c.get("bracketTag"), "produz": pn(c)[:3]} for c in r["almostIncluded"]}
    return inc, alm
def est(body, rot=None):
    e = http(BASE + "/estimate-bracket", json.dumps(body).encode())
    if rot is not None: RAW[rot] = {"entrada": body, "resposta": e}
    return {"bracketTag": e["bracketTag"], "game_changers": [c["card"]["name"] for c in e["cards"] if c["gameChanger"]], "banidas": [c["card"]["name"] for c in e["cards"] if c["banned"]],
            "mass_land_denial": [c["card"]["name"] for c in e["cards"] if c["massLandDenial"]], "extra_turn": [c["card"]["name"] for c in e["cards"] if c["extraTurn"]],
            "combos": [{"combo": key(c["combo"]), "relevant": c["relevant"], "borderlineRelevant": c["borderlineRelevant"], "definitelyTwoCard": c["definitelyTwoCard"], "arguablyTwoCard": c["arguablyTwoCard"],
                        "speed": c["speed"], "lock": c["lock"], "tag": c["combo"].get("bracketTag")} for c in e["combos"]]}
if __name__ == "__main__":
    decks = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(RAIZ, "*", "lista.md")))
    decks = [d for d in decks if (not SO and d != "rat-king-verminister") or d in SO]
    listas = {d: parse(os.path.join(RAIZ, d, "lista.md")) for d in decks}
    unicos = sorted({n for cmd, main in listas.values() for n, _ in cmd + main} | {"Basalt Monolith", "Rings of Brighthearth", "Mind Stone"})
    print(f"decks: {len(decks)} | nomes unicos a resolver: {len(unicos)}", flush=True)
    res = {}
    parcial = os.path.join(RAIZ, "spellbook-todos-os-decks-2026-10-28", "dados", "nomes_resolvidos_parcial.json")
    if os.path.exists(parcial): res = {k: v for k, v in json.load(open(parcial, encoding="utf-8")).items() if v != "ERRO"}   # retoma: so' o que ja' resolveu sem erro de rede
    for rodada in range(4):
        falta = [n for n in unicos if n not in res]
        if not falta: break
        print(f"  rodada de resolucao {rodada + 1}: {len(falta)} nomes", flush=True)
        with cf.ThreadPoolExecutor(3) as ex:
            for i, (n, r) in enumerate(zip(falta, ex.map(resolve, falta))):
                if r != "ERRO": res[n] = r
                if i % 400 == 0:
                    print("  resolvidos", i, flush=True); json.dump(res, open(parcial, "w", encoding="utf-8"), ensure_ascii=False)
        json.dump(res, open(parcial, "w", encoding="utf-8"), ensure_ascii=False)
    sem_resposta = [n for n in unicos if n not in res]
    assert not sem_resposta, f"{len(sem_resposta)} nomes sem resposta da API apos 4 rodadas (rede): {sem_resposta[:10]}"
    nao = sorted(n for n, r in res.items() if r is None)
    print("nomes NAO reconhecidos pelo Spellbook (total):", len(nao), nao, flush=True)
    json.dump({"data": DATA, "reconhece": res}, open(os.path.join(RAIZ, "spellbook-todos-os-decks-2026-10-28", "dados", "nomes_resolvidos.json"), "w"), ensure_ascii=False, indent=1)
    resumo = []

    def resumir(out):
        opcoes = out["opcoes_de_comandante"]
        return {"deck": out["deck"], "total": out["total_cartas_parseadas"], "comandantes": [o["comandante"] for o in opcoes], "n_combos": [len(o["incluidos"]) for o in opcoes], "n_quase": [len(o["quase"]) for o in opcoes],
                "bracket_estimado": [o["estimate_bracket"]["bracketTag"] for o in opcoes], "game_changers": sorted({g for o in opcoes for g in o["estimate_bracket"]["game_changers"]}),
                "combos": sorted({k for o in opcoes for k in o["incluidos"]}), "combos_2_cartas": sorted({k for o in opcoes for k, v in o["incluidos"].items() if len(v["usa"]) == 2}),
                "nao_reconhecidos": out["nomes_nao_reconhecidos"], "bracket_mencionado": out["bracket_mencionado_em_lista_ou_auditoria_(grep)"],
                "controles": [out["controle_positivo_basalt_rings_apareceu"], out["controle_de_corte_sumiu"]]}

    for d in decks:
        pasta = os.path.join(RAIZ, d, "resultados-ab", f"{DATA}-spellbook", "dados"); os.makedirs(pasta, exist_ok=True)
        arq = os.path.join(pasta, f"spellbook_{d}_{DATA}.json")
        if os.path.exists(arq) and not SO and not os.environ.get("REFAZER"):                         # retomada: deck ja' feito nesta data (a rodada e' de UM dia; apague o arquivo pra refazer)
            out = json.load(open(arq, encoding="utf-8")); resumo.append(resumir(out)); print(f"{d:42s} (ja' feito, lido do arquivo)", flush=True); continue
        cmd, main = listas[d]; total = sum(n for _, n in cmd) + sum(n for _, n in main)
        opcoes = []
        for i, (c, _) in enumerate(cmd):
            outros = [(x, 1) for j, (x, _) in enumerate(cmd) if j != i]            # precons: o(s) outro(s) comandante(s) entram na lista
            body = comp(main + outros, c)
            inc, alm = find(body, f"find_opcao{i}"); e = est(body, f"estimate_opcao{i}")
            opcoes.append({"comandante": c, "incluidos": inc, "quase": alm, "estimate_bracket": e})
        mc = main + [(x, 1) for x, _ in cmd[1:]]
        pos = comp(mc + [("Basalt Monolith", 1), ("Rings of Brighthearth", 1)], cmd[0][0]); cor = comp(mc + [("Basalt Monolith", 1), ("Mind Stone", 1)], cmd[0][0])
        pinc, _ = find(pos, "find_controle_positivo"); cinc, _ = find(cor, "find_controle_de_corte")
        achou = any("Basalt Monolith" in k and "Rings of Brighthearth" in k for k in pinc); sumiu = not any("Basalt Monolith" in k and "Rings of Brighthearth" in k for k in cinc)
        nr = sorted({n for n, _ in cmd + main if res.get(n) is None})
        brk = sorted({m for f in ("lista.md", "auditoria.md") if os.path.exists(os.path.join(RAIZ, d, f)) for m in re.findall(r"Bracket\s*(\d)", open(os.path.join(RAIZ, d, f), encoding="utf-8").read())})
        out = {"deck": d, "data": DATA, "total_cartas_parseadas": total, "nomes_nao_reconhecidos": nr, "opcoes_de_comandante": opcoes, "bracket_mencionado_em_lista_ou_auditoria_(grep)": brk,
               "controle_positivo_basalt_rings_apareceu": achou, "controle_de_corte_sumiu": sumiu}
        json.dump(out, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        import lzma
        with lzma.open(os.path.join(pasta, f"spellbook_raw_{d}_{DATA}.json.xz"), "wt", preset=9) as fz:
            json.dump(dict(RAW), fz, ensure_ascii=False)
        RAW.clear()
        resumo.append(resumir(out))
        print(f"{d:42s} total={total:3d} combos={[len(o['incluidos']) for o in opcoes]} est={[o['estimate_bracket']['bracketTag'] for o in opcoes]} nao_reconhecidos={len(nr)} controles={achou},{sumiu}", flush=True)
    json.dump(resumo, open(os.path.join(RAIZ, "spellbook-todos-os-decks-2026-10-28", "dados", "resumo_todos.json"), "w"), ensure_ascii=False, indent=1)
    print("FIM", flush=True)

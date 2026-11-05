"""Commander Spellbook ANTES/DEPOIS da entrada da Bloodline Recollector // Ancestral Craving (Reality Fracture) no Edgar Markov (pedido do usuario em 2026-11-04).
Regra #4 (adendo, item 2): resolve cada nome (a API ignora, sem erro, nome que nao reconhece), roda controle positivo (Basalt Monolith + Rings of Brighthearth) e de corte (com Mind Stone o combo some),
e testa: ANTES (lista atual), +BR (101 cartas), e, para CADA carta X da lista (menos o comandante): -X +BR (100 cartas). Grava as respostas cruas (.json.xz) e o resumo.
Uso: python3 -I spellbook_br.py <raiz do repo> <pasta de saida>"""
import collections, concurrent.futures as cf, json, lzma, os, re, sys, time, urllib.parse, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
RAIZ, SAIDA = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
BASE = "https://backend.commanderspellbook.com"
BR = "Bloodline Recollector // Ancestral Craving"
def http(url, data=None, tries=8):
    for t in range(tries):
        try:
            rq = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "MTG-Code-audit/1.0"})
            return json.load(urllib.request.urlopen(rq, timeout=240))
        except Exception:
            time.sleep(2 * (t + 1) ** 1.5)
    raise RuntimeError(url)
def parse(path):
    txt = open(path, encoding="utf-8").read(); i = txt.lower().find("## comandante"); cmd, main = [], []; sec = None
    for l in txt[i:].split("\n"):
        if l.startswith("#"): sec = l.lstrip("# ").strip(); continue
        m = re.match(r"^\s*(\d+)\s*x?\s+(.+?)\s*$", l)
        if m: (cmd if sec.lower().startswith("comandante") else main).append((m.group(2).strip(), int(m.group(1))))
    return cmd, main
def resolve(n):
    d = http(BASE + "/cards/?" + urllib.parse.urlencode({"q": n, "limit": 10}))
    nomes = [x["name"] for x in d["results"]]
    for x in nomes:
        if x.lower() == n.lower(): return x
    for x in nomes:
        if x.split(" // ")[0].lower() == n.split(" // ")[0].lower(): return x
    return None
def key(c): return " + ".join(sorted(u["card"]["name"] for u in c["uses"]))
def comp(main, cmdr):
    cnt = collections.Counter()
    for n, q in main: cnt[n] += q
    return {"commanders": [{"card": cmdr}], "main": [{"card": c, "quantity": q} for c, q in cnt.items()]}
RAW = {}
def find(body, rot):
    r = http(BASE + "/find-my-combos", json.dumps(body).encode()); RAW[rot] = {"entrada": body, "resposta": r}
    inc = {key(c): {"id": c.get("id"), "tag": c.get("bracketTag"), "usa": [u["card"]["name"] for u in c["uses"]]} for c in r["results"]["included"]}
    alm = {key(c): {"id": c.get("id"), "tag": c.get("bracketTag"), "usa": [u["card"]["name"] for u in c["uses"]]} for c in r["results"]["almostIncluded"]}
    return inc, alm
def est(body, rot):
    e = http(BASE + "/estimate-bracket", json.dumps(body).encode()); RAW[rot] = {"entrada": body, "resposta": e}
    return {"bracketTag": e["bracketTag"], "game_changers": sorted(c["card"]["name"] for c in e["cards"] if c["gameChanger"])}
if __name__ == "__main__":
    (cmdr, _), = parse(os.path.join(RAIZ, "edgar-markov-mardu", "lista.md"))[0]
    cmd, main = parse(os.path.join(RAIZ, "edgar-markov-mardu", "lista.md")); cmdr = cmd[0][0]
    nomes = sorted({n for n, _ in cmd + main} | {BR, "Basalt Monolith", "Rings of Brighthearth", "Mind Stone"})
    with cf.ThreadPoolExecutor(3) as ex: res = dict(zip(nomes, ex.map(resolve, nomes)))
    nao = sorted(n for n, r in res.items() if r is None)
    print("nomes:", len(nomes), "| NAO reconhecidos:", nao, "| BR reconhecida como:", res[BR], flush=True)
    assert res[BR], "o Spellbook nao reconhece a Bloodline Recollector: qualquer 'nenhum combo novo' seria vacuo"
    pos = comp(main + [("Basalt Monolith", 1), ("Rings of Brighthearth", 1)], cmdr); cor = comp(main + [("Basalt Monolith", 1), ("Mind Stone", 1)], cmdr)
    pinc, _ = find(pos, "controle_positivo"); cinc, _ = find(cor, "controle_de_corte")
    achou = any("Basalt Monolith" in k and "Rings of Brighthearth" in k for k in pinc); sumiu = not any("Basalt Monolith" in k and "Rings of Brighthearth" in k for k in cinc)
    print("controle positivo:", achou, "| controle de corte (combo some sem Rings):", sumiu, flush=True)
    antes_body = comp(main, cmdr); a_inc, a_alm = find(antes_body, "ANTES"); a_est = est(antes_body, "ANTES_bracket")
    br_body = comp(main + [(BR, 1)], cmdr); b_inc, b_alm = find(br_body, "+BR"); b_est = est(br_body, "+BR_bracket")
    print(f"ANTES: {len(a_inc)} combos, {len(a_alm)} quase, bracket {a_est} | +BR: {len(b_inc)} combos, {len(b_alm)} quase, bracket {b_est}", flush=True)
    novos = {k: v for k, v in b_inc.items() if k not in a_inc}; quase_br = {k: v for k, v in b_alm.items() if BR in v["usa"] or any("Bloodline Recollector" in u for u in v["usa"])}
    print("combos NOVOS com a BR:", list(novos), "| 'quase' que citam a BR:", len(quase_br), flush=True)
    def troca(x):
        body = comp([(n, q) for n, q in main if n != x] + [(BR, 1)], cmdr)
        inc, _ = find(body, f"troca_sai_{x}")
        return x, sorted(k for k in a_inc if k not in inc), sorted(k for k in inc if k not in a_inc)
    cartas = [n for n, _ in main]
    with cf.ThreadPoolExecutor(3) as ex: trocas = list(ex.map(troca, cartas))
    perde = {x: p for x, p, g in trocas if p}; ganha = {x: g for x, p, g in trocas if g}
    print("trocas testadas (sai X, entra BR):", len(trocas), "| trocas que PERDEM combo:", {k: len(v) for k, v in perde.items()}, "| que GANHAM combo:", ganha, flush=True)
    out = {"data": "2026-11-04", "reconhece": res, "nao_reconhecidos": nao, "controle_positivo": achou, "controle_de_corte": sumiu,
           "antes": {"combos": a_inc, "n_quase": len(a_alm), "bracket": a_est}, "mais_br": {"combos": b_inc, "n_quase": len(b_alm), "bracket": b_est, "novos": novos, "quase_que_citam_br": quase_br},
           "trocas": {x: {"perde": p, "ganha": g} for x, p, g in trocas}}
    os.makedirs(os.path.join(SAIDA, "dados"), exist_ok=True)
    json.dump(out, open(os.path.join(SAIDA, "dados", "spellbook_br_2026-11-04.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with lzma.open(os.path.join(SAIDA, "dados", "spellbook_br_raw_2026-11-04.json.xz"), "wt", preset=9) as fz: json.dump(RAW, fz, ensure_ascii=False)
    print("FIM", flush=True)

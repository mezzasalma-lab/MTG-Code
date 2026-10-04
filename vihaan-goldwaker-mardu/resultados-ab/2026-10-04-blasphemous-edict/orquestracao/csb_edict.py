"""Commander Spellbook antes/depois da troca Blasphemous Act -> Blasphemous Edict no Vihaan, com controles positivos. Guarda a resposta CRUA de cada consulta
(../dados/spellbook_cru.json.xz) e o resumo (../dados/spellbook_resumo.json). Uso (da raiz do repositorio):
SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-04-blasphemous-edict/orquestracao/csb_edict.py"""
import collections, json, lzma, os, re, sys, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
AQUI = os.path.dirname(os.path.abspath(__file__))
LISTA = os.path.join(AQUI, "..", "..", "..", "resultados-ab", "_lista_legada", "lista.md")   # 12a rodada: a lista de a17049f (com Blood Money); a viva tem a Mythos
CMD = "Vihaan, Goldwaker"

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

def chave(c):
    return " + ".join(sorted(u["card"]["name"] for u in c["uses"]))

def resumo(r):
    inc = {chave(c): [p["feature"]["name"] if isinstance(p, dict) and "feature" in p else (p.get("name") if isinstance(p, dict) else str(p)) for p in c.get("produces", [])][:3] for c in r["included"]}
    alm = sorted(chave(c) for c in r["almostIncluded"])
    return inc, alm

base = parse(LISTA)
assert "Blasphemous Act" in base and "Blasphemous Edict" not in base, "lista inesperada"
def troca(sai=None, entra=None):
    d = list(base)
    if sai: d.remove(sai)
    if entra: d.append(entra)
    return d
CENARIOS = {
    "base (lista atual, com Blasphemous Act)": base,
    "+Blasphemous Edict (sem cortar nada)": troca(entra="Blasphemous Edict"),
    "-Blasphemous Act (sem entrar nada)": troca(sai="Blasphemous Act"),
    "-Blasphemous Act +Blasphemous Edict (a troca)": troca("Blasphemous Act", "Blasphemous Edict"),
    "CONTROLE -Smothering Tithe": troca(sai="Smothering Tithe"),
    "CONTROLE -Ashnod's Altar": troca(sai="Ashnod's Altar"),
    "CONTROLE -Mayhem Devil": troca(sai="Mayhem Devil"),
}
crus, res = {}, {}
for nome, deck in CENARIOS.items():
    r = query(deck); crus[nome] = r
    inc, alm = resumo(r)
    res[nome] = {"n": len(deck), "incluidos": inc, "quase": alm, "identidade": r.get("identity")}
    print(f"{nome:50s} n={len(deck)} incluidos={len(inc)} quase={len(alm)} id={r.get('identity')}")
b_inc, b_alm = set(res["base (lista atual, com Blasphemous Act)"]["incluidos"]), set(res["base (lista atual, com Blasphemous Act)"]["quase"])
for nome, v in res.items():
    if nome.startswith("base"): continue
    inc, alm = set(v["incluidos"]), set(v["quase"])
    print(f"\n[{nome}] combos que SUMIRAM: {sorted(b_inc - inc)} | NOVOS: {sorted(inc - b_inc)}")
    print(f"   'quase' que sumiram: {len(b_alm - alm)} | 'quase' novos: {len(alm - b_alm)}")
    for k in sorted(alm - b_alm)[:12]:
        print("      quase novo +", k)
json.dump(res, open(os.path.join(AQUI, "..", "dados", "spellbook_resumo.json"), "w"), ensure_ascii=False, indent=1)
with lzma.open(os.path.join(AQUI, "..", "dados", "spellbook_cru.json.xz"), "wt", preset=9) as f:
    json.dump(crus, f, ensure_ascii=False)

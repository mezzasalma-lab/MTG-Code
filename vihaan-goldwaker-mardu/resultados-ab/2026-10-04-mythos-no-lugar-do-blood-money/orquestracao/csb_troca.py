"""Commander Spellbook ANTES/DEPOIS da troca Blood Money -> Mythos of Snapdax (12a rodada), com controles positivos (Regra #4, adendo 2026-09-28): ANTES = `resultados-ab/_lista_legada/lista.md`
(a lista de a17049f, com Blood Money), DEPOIS = a `lista.md` do repositorio; controles = DEPOIS sem Smothering Tithe e sem Ashnod's Altar (tem que SUMIR combo, senao a consulta nao serve).
Guarda a resposta CRUA (../dados/spellbook_cru.json.xz) e o resumo (../dados/spellbook_resumo.json).
Uso (de dentro de orquestracao/): python3 csb_troca.py        -> consulta a API e grava os dados
                                  python3 csb_troca.py --sum  -> refaz so' o texto a partir do bruto arquivado"""
import collections, json, lzma, os, re, sys, time, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(AQUI, "..", "..", "..")
CMD = "Vihaan, Goldwaker"
SUM = "--sum" in sys.argv


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
    for t in range(4):
        try:
            req = urllib.request.Request("https://backend.commanderspellbook.com/find-my-combos", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json", "User-Agent": "MTG-Code-audit/1.0"})
            return json.load(urllib.request.urlopen(req, timeout=240))["results"]
        except Exception as e:
            print("   retry", t, repr(e)[:80], file=sys.stderr); time.sleep(3 + 3 * t)
    raise RuntimeError("Spellbook indisponivel")


def chave(c):
    return " + ".join(sorted(u["card"]["name"] for u in c["uses"]))


def resumo(r):
    inc = {chave(c): [p["feature"]["name"] if isinstance(p, dict) and "feature" in p else (p.get("name") if isinstance(p, dict) else str(p)) for p in c.get("produces", [])][:3] for c in r["included"]}
    return inc, sorted(chave(c) for c in r["almostIncluded"])


antes = parse(os.path.join(DECK, "resultados-ab", "_lista_legada", "lista.md"))
depois = parse(os.path.join(DECK, "lista.md"))
assert len(antes) == len(depois) == 99 and "Blood Money" in antes and "Mythos of Snapdax" not in antes
assert sorted(depois) == sorted([c for c in antes if c != "Blood Money"] + ["Mythos of Snapdax"]), "DEPOIS nao e' ANTES - Blood Money + Mythos"


def sem(deck, c):
    d = list(deck); d.remove(c); return d


CEN = {"ANTES (Blood Money)": antes, "DEPOIS (Mythos no lugar)": depois, "CONTROLE DEPOIS -Smothering Tithe": sem(depois, "Smothering Tithe"),
       "CONTROLE DEPOIS -Ashnod's Altar": sem(depois, "Ashnod's Altar")}
ARQ_CRU, ARQ_RES = os.path.join(AQUI, "..", "dados", "spellbook_cru.json.xz"), os.path.join(AQUI, "..", "dados", "spellbook_resumo.json")
crus = json.load(lzma.open(ARQ_CRU, "rt")) if SUM else {n: query(d) for n, d in CEN.items()}
res = {}
for nome, r in crus.items():
    inc, alm = resumo(r)
    res[nome] = {"n": len(CEN[nome]), "incluidos": inc, "quase": alm, "identidade": r.get("identity")}
    print(f"{nome:40s} n={len(CEN[nome])} incluidos={len(inc)} quase={len(alm)} id={r.get('identity')}")
b = res["ANTES (Blood Money)"]; b_inc, b_alm = set(b["incluidos"]), set(b["quase"])
print("\nCombos INCLUIDOS em ANTES (%d):" % len(b_inc))
for k in sorted(b_inc):
    print("  -", k, "->", b["incluidos"][k])
for nome, v in res.items():
    if nome.startswith("ANTES"):
        continue
    inc, alm = set(v["incluidos"]), set(v["quase"])
    print(f"\n[{nome}] combos que SUMIRAM: {sorted(b_inc - inc)} | NOVOS: {sorted(inc - b_inc)}")
    print(f"   'quase' que sumiram: {len(b_alm - alm)} {sorted(b_alm - alm)} | 'quase' novos: {len(alm - b_alm)}")
    for k in sorted(alm - b_alm)[:10]:
        print("      quase novo +", k)
if not SUM:
    json.dump(res, open(ARQ_RES, "w"), ensure_ascii=False, indent=1)
    with lzma.open(ARQ_CRU, "wt", preset=9) as f:
        json.dump(crus, f, ensure_ascii=False)

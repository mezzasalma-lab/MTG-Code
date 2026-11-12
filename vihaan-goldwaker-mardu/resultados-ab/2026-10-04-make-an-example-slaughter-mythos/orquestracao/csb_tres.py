"""Commander Spellbook antes/depois para as 3 cartas que o usuario escolheu (Make an Example, Slaughter the Strong, Mythos of Snapdax), com os DOIS cortes possiveis (Blasphemous Act e
Blood Money) e controles positivos (Regra #4, adendo 2026-09-28). Guarda a resposta CRUA (../dados/spellbook_cru.json.xz) e o resumo (../dados/spellbook_resumo.json).
Uso (de dentro de orquestracao/): SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 csb_tres.py          -> consulta a API e grava os dados
                                  python3 csb_tres.py --sum                                         -> refaz so' o texto a partir do bruto arquivado"""
import collections, json, lzma, os, re, sys, time, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
AQUI = os.path.dirname(os.path.abspath(__file__))
LISTA = os.path.join(AQUI, "..", "..", "..", "resultados-ab", "_lista_legada", "lista.md")   # 12a rodada: a lista de a17049f (com Blood Money); a viva tem a Mythos
CMD = "Vihaan, Goldwaker"
ACT, BM = "Blasphemous Act", "Blood Money"
CANDS = ["Make an Example", "Slaughter the Strong", "Mythos of Snapdax"]
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


base = parse(LISTA)
assert ACT in base and BM in base and all(c not in base for c in CANDS), "lista inesperada"


def troca(sai=None, entra=None):
    d = list(base)
    if sai: d.remove(sai)
    if entra: d.append(entra)
    return d


CEN = {"base (lista atual)": base, f"-{ACT} (sem entrar nada)": troca(sai=ACT), f"-{BM} (sem entrar nada)": troca(sai=BM),
       "CONTROLE -Smothering Tithe": troca(sai="Smothering Tithe"), "CONTROLE -Ashnod's Altar": troca(sai="Ashnod's Altar")}
for x in CANDS:
    CEN[f"+{x} (sem cortar)"] = troca(entra=x)
    CEN[f"-{ACT} +{x}"] = troca(ACT, x)
    CEN[f"-{BM} +{x}"] = troca(BM, x)
ARQ_CRU, ARQ_RES = os.path.join(AQUI, "..", "dados", "spellbook_cru.json.xz"), os.path.join(AQUI, "..", "dados", "spellbook_resumo.json")
if SUM:
    crus = json.load(lzma.open(ARQ_CRU, "rt"))
else:
    crus = {n: query(d) for n, d in CEN.items()}
res = {}
for nome, r in crus.items():
    inc, alm = resumo(r)
    res[nome] = {"n": len(CEN[nome]), "incluidos": inc, "quase": alm, "identidade": r.get("identity")}
    print(f"{nome:52s} n={len(CEN[nome])} incluidos={len(inc)} quase={len(alm)} id={r.get('identity')}")
b = res["base (lista atual)"]; b_inc, b_alm = set(b["incluidos"]), set(b["quase"])
print("\nCombos INCLUIDOS na base (%d):" % len(b_inc))
for k in sorted(b_inc):
    print("  -", k, "->", b["incluidos"][k])
for nome, v in res.items():
    if nome.startswith("base"):
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

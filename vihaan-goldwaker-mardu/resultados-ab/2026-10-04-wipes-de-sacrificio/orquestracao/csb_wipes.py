"""Commander Spellbook antes/depois para CADA wipe/efeito de sacrificio candidato no Vihaan, com controles positivos (Regra #4, adendo de 2026-09-28: rodar o Spellbook ANTES e DEPOIS de cada troca).
Para cada candidata X: '+X (sem cortar)' e '-Blasphemous Act +X (a troca)'; mais a base, '-Blasphemous Act' (sem entrar nada) e 3 controles positivos (cortar Smothering Tithe, Ashnod's Altar e
Mayhem Devil: tem que SUMIR combo, senao o metodo nao enxerga nada). Guarda a resposta CRUA de cada consulta (../dados/spellbook_cru.json.xz) e o resumo (../dados/spellbook_resumo.json).
Uso (da raiz do repositorio): SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-04-wipes-de-sacrificio/orquestracao/csb_wipes.py"""
import collections, json, lzma, os, re, sys, time, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
AQUI = os.path.dirname(os.path.abspath(__file__))
LISTA = os.path.join(AQUI, "..", "..", "..", "resultados-ab", "_lista_legada", "lista.md")   # 12a rodada: a lista de a17049f (com Blood Money); a viva tem a Mythos
CMD = "Vihaan, Goldwaker"
CANDIDATAS = ["Blasphemous Edict", "By Invitation Only", "Barter in Blood", "Tergrid's Shadow", "Rankle's Prank", "Taste of Death", "Necrotic Hex", "Liliana, Dreadhorde General",
              "Zodiark, Umbral God", "Meathook Massacre II", "Mythos of Snapdax", "Tragic Arrogance", "Winnowing", "Slaughter the Strong", "Living Death", "Scrap Mastery", "All Is Dust"]


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
            print("   retry", t, repr(e)[:80], file=sys.stderr)
            time.sleep(3 + 3 * t)
    raise RuntimeError("Spellbook indisponivel")


def chave(c):
    return " + ".join(sorted(u["card"]["name"] for u in c["uses"]))


def resumo(r):
    inc = {chave(c): [p["feature"]["name"] if isinstance(p, dict) and "feature" in p else (p.get("name") if isinstance(p, dict) else str(p)) for p in c.get("produces", [])][:3] for c in r["included"]}
    alm = sorted(chave(c) for c in r["almostIncluded"])
    return inc, alm


base = parse(LISTA)
ACT = "Blasphemous Act"
assert ACT in base and all(c not in base for c in CANDIDATAS), "lista inesperada"


def troca(sai=None, entra=None):
    d = list(base)
    if sai:
        d.remove(sai)
    if entra:
        d.append(entra)
    return d


CENARIOS = {"base (lista atual, com Blasphemous Act)": base, "-Blasphemous Act (sem entrar nada)": troca(sai=ACT),
            "CONTROLE -Smothering Tithe": troca(sai="Smothering Tithe"), "CONTROLE -Ashnod's Altar": troca(sai="Ashnod's Altar"), "CONTROLE -Mayhem Devil": troca(sai="Mayhem Devil")}
for x in CANDIDATAS:
    CENARIOS[f"+{x} (sem cortar)"] = troca(entra=x)
    CENARIOS[f"-{ACT} +{x} (a troca)"] = troca(ACT, x)
crus, res = {}, {}
for nome, deck in CENARIOS.items():
    r = query(deck); crus[nome] = r
    inc, alm = resumo(r)
    res[nome] = {"n": len(deck), "incluidos": inc, "quase": alm, "identidade": r.get("identity")}
    print(f"{nome:62s} n={len(deck)} incluidos={len(inc)} quase={len(alm)} id={r.get('identity')}", flush=True)
b = res["base (lista atual, com Blasphemous Act)"]
b_inc, b_alm = set(b["incluidos"]), set(b["quase"])
print("\nCombos INCLUIDOS na base (%d):" % len(b_inc))
for k in sorted(b_inc):
    print("  -", k, "->", b["incluidos"][k])
for nome, v in res.items():
    if nome.startswith("base"):
        continue
    inc, alm = set(v["incluidos"]), set(v["quase"])
    print(f"\n[{nome}] combos que SUMIRAM: {sorted(b_inc - inc)} | NOVOS: {sorted(inc - b_inc)}")
    print(f"   'quase' que sumiram: {len(b_alm - alm)} | 'quase' novos: {len(alm - b_alm)}")
    for k in sorted(alm - b_alm)[:10]:
        print("      quase novo +", k)
json.dump(res, open(os.path.join(AQUI, "..", "dados", "spellbook_resumo.json"), "w"), ensure_ascii=False, indent=1)
with lzma.open(os.path.join(AQUI, "..", "dados", "spellbook_cru.json.xz"), "wt", preset=9) as f:
    json.dump(crus, f, ensure_ascii=False)

"""Enumeracao POR SCRIPT (oraculo ao vivo, Scryfall /cards/collection; fallback por flavor_name, Regra #2) das cartas da lista do Vihaan que satisfazem cada condicao
relevante pra comparar Blasphemous Act (destroy-like: 13 de dano) x Blasphemous Edict (sacrificio). Guarda o oraculo cru em ../dados/oraculo_lista_ao_vivo.json.xz.
Uso (da raiz do repositorio): SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-04-blasphemous-edict/orquestracao/enumeracao.py"""
import json, lzma, os, re, subprocess, sys, time, urllib.parse
AQUI = os.path.dirname(os.path.abspath(__file__))
LISTA = os.path.join(AQUI, "..", "..", "..", "lista.md")

def nomes(path):
    out = []; sec = None
    for l in open(path):
        l = l.rstrip("\n")
        if l.startswith("#"):
            sec = l.lstrip("# ").strip().lower(); continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if m and sec:
            out.append(m.group(2).strip())
    return list(dict.fromkeys(out))

def curl(url, body=None):
    cmd = ["curl", "-sS", "--max-time", "60", url]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    return json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)

def texto(c):
    if "card_faces" in c and c.get("oracle_text") is None:
        return "\n//\n".join(f.get("oracle_text") or "" for f in c["card_faces"])
    return c.get("oracle_text") or ""

def tipo(c):
    return c.get("type_line") or ""

lst = nomes(LISTA)
alvo = lst + ["Blasphemous Edict"]
cartas, faltam = {}, []
for i in range(0, len(alvo), 75):
    lote = alvo[i:i + 75]
    r = curl("https://api.scryfall.com/cards/collection", {"identifiers": [{"name": n} for n in lote]}); time.sleep(0.15)
    for c in r.get("data", []):
        cartas[c["name"]] = c
    faltam += [x["name"] for x in r.get("not_found", [])]
resolvidos = {}
for n in faltam:  # Regra #2: nome de capa Universes Beyond (flavor_name)
    r = curl("https://api.scryfall.com/cards/search?q=" + urllib.parse.quote('"%s"' % n)); time.sleep(0.15)
    achou = [c for c in r.get("data", []) if (c.get("flavor_name") or "").lower() == n.lower() or c.get("name", "").lower() == n.lower()]
    if achou:
        cartas[achou[0]["name"]] = achou[0]; resolvidos[n] = achou[0]["name"]
nao_res = [n for n in faltam if n not in resolvidos]
print("cartas distintas na lista:", len(lst), "| resolvidas:", len(cartas) - 1, "| por flavor_name:", resolvidos, "| NAO resolvidas:", nao_res)
json.dump(cartas, lzma.open(os.path.join(AQUI, "..", "dados", "oraculo_lista_ao_vivo.json.xz"), "wt", preset=9), ensure_ascii=False)

lista_cartas = {n: c for n, c in cartas.items() if n != "Blasphemous Edict" and n != "Vihaan, Goldwaker"}
print("\n== 1. criaturas (type_line) na lista:", sum(1 for c in lista_cartas.values() if "Creature" in tipo(c)))
print("   ", sorted(n for n, c in lista_cartas.items() if "Creature" in tipo(c)))

def varre(rotulo, pred):
    r = sorted(n for n, c in lista_cartas.items() if pred(texto(c), tipo(c)))
    print(f"\n== {rotulo}: {len(r)}")
    for n in r:
        linhas = [l for l in texto(lista_cartas[n]).split("\n") if re.search(r"sacrific", l, re.I)] if "SACRIF" in rotulo.upper() else []
        print("   -", n, ("| " + " / ".join(l.strip()[:150] for l in linhas)) if linhas else "")
    return r

sac = varre("2. SACRIFICIO no texto (qualquer 'sacrific')", lambda t, ty: re.search(r"sacrific", t, re.I) is not None)
reativo_sac = varre("2a. REAGEM a sacrificio ('whenever you sacrifice' / 'a player sacrifices' / 'create or sacrifice')", lambda t, ty: re.search(r"whenever (you|a player|an opponent|a creature|another creature)[^.\n]*sacrific", t, re.I) is not None or re.search(r"create or sacrifice", t, re.I) is not None)
morte = varre("3. REAGEM a morte / ao cemiterio / saida do campo ('dies', 'put into a graveyard from the battlefield', 'leaves the battlefield')", lambda t, ty: re.search(r"\bdies\b|put into a graveyard from the battlefield|leaves the battlefield", t, re.I) is not None)
varre("4. SO' 'destroy' sem sacrifice (Act/Blood Money destroem; efeitos de 'destroy' no texto)", lambda t, ty: re.search(r"\bdestroy", t, re.I) is not None)
varre("5. indestrutivel / regenera / protecao (sobrevivem a Act mas nao a Edict, ou o contrario)", lambda t, ty: re.search(r"indestructible|regenerat|protection from|hexproof|phase", t, re.I) is not None)
varre("6. tokens de criatura criados (contam como criatura sacrificada/destruida)", lambda t, ty: re.search(r"create[^.\n]*(creature token|Servo|Construct|Dragon token|Treasure)|creature token", t, re.I) is not None)
varre("7. 'each player sacrifices' / 'each opponent sacrifices' / 'sacrifices a creature' (edicts ja' na lista)", lambda t, ty: re.search(r"(each|target) (player|opponent)s? sacrifices?|sacrifices? (a|an|\w+) (creature|permanent)", t, re.I) is not None)
varre("8. 'damage to each creature' / 'each creature' / 'all creatures' (outros wipes na lista)", lambda t, ty: re.search(r"each creature|all creatures|each other creature", t, re.I) is not None)
varre("9. 'Treasure' + 'sacrifice' (sacrificar Treasure: Storm, Altar, etc.)", lambda t, ty: re.search(r"sacrifice (a|an|one|two|three|X|any number of)?[^.\n]*Treasure|Treasure[^.\n]*sacrific", t, re.I) is not None)
print("\n== Blasphemous Edict (oraculo ao vivo):", texto(cartas["Blasphemous Edict"]).replace("\n", " | "), "|", tipo(cartas["Blasphemous Edict"]), cartas["Blasphemous Edict"]["mana_cost"], "color_identity", cartas["Blasphemous Edict"]["color_identity"])
print("== identidade de cor da Edict ⊆ {R,W,B}:", set(cartas["Blasphemous Edict"]["color_identity"]) <= {"R", "W", "B"})

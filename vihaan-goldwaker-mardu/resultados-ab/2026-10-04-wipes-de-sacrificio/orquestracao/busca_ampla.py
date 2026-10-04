"""Busca AMPLA e ao vivo no Scryfall de TODA carta legal em Commander e na identidade do Vihaan (R/W/B) cujo oraculo faz jogadores SACRIFICAREM varias permanentes
(wipe/edict em massa). Substitui a lista curta da rodada da Blasphemous Edict (que so' procurava `t:sorcery` e 3 frases fixas e portanto perdia instantaneos, criaturas,
planeswalkers e variantes "all but"). Guarda a resposta CRUA de cada busca em ../dados/busca_ampla_cru.json.xz e o resultado da classificacao em ../dados/busca_ampla_classificada.json.
Classificacao por script (nada de memoria): le `oracle_text` e marca (a) quem sacrifica ("each player", "each opponent", "target player/opponent", "you"), (b) quanto
(numero fixo, X/livre, "all", "all but", "half/third", "that many"), (c) o que (creature, permanent, artifact, land, nonland). Quem so' faz um sacrificio de UMA criatura
(edict simples) e' separado como 'edict de 1' (nao e' wipe, mas fica listado), e quem so' tem terreno e' separado como 'terreno'.
Uso (da raiz do repositorio): SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-04-wipes-de-sacrificio/orquestracao/busca_ampla.py"""
import json, lzma, os, re, subprocess, sys, time, urllib.parse
AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = 'f:commander id<=rwb '


def get(url):
    for t in range(4):
        r = subprocess.run(["curl", "-sS", "--max-time", "60", url], capture_output=True, text=True)
        time.sleep(0.12)
        try:
            return json.loads(r.stdout)
        except Exception:
            time.sleep(1 + t)
    raise RuntimeError("falha ao buscar " + url)


def busca(q):
    """Todas as paginas de uma busca; devolve a lista de cartas (resposta crua do Scryfall)."""
    url = "https://api.scryfall.com/cards/search?unique=cards&order=name&q=" + urllib.parse.quote(q)
    cartas = []
    while url:
        d = get(url)
        if d.get("object") == "error":
            return {"erro": d.get("details"), "cartas": cartas}
        cartas += d["data"]
        url = d.get("next_page")
    return {"cartas": cartas}


# varias formulacoes: cada uma pega uma familia de oraculos; a uniao e' deduplicada por oracle_id
BUSCAS = {
    "each_player_sacrifices": BASE + 'o:"each player sacrifices"',
    "each_opponent_sacrifices": BASE + 'o:"each opponent sacrifices"',
    "each_other_player_sacrifices": BASE + 'o:"each other player sacrifices"',
    "sacrifices_all": BASE + '(o:"sacrifices all" or o:"sacrifice all" or o:"sacrifices each" or o:"sacrifices every")',
    "sacrifices_numero": BASE + 'o:/sacrifices? (two|three|four|five|six|seven|eight|nine|ten|thirteen|x|half|a third|that many|all but)/',
    "player_sacrifices_regex": BASE + 'o:/(each|every|target|that|defending) (other )?(player|opponent)s? (also )?sacrifices?/',
    "sacrifice_all_but": BASE + '(o:"all but" o:sacrifice)',
    "for_each_player_choose": BASE + '(o:"for each player" o:sacrifice)',
    "sacrifices_half_third": BASE + '(o:"half of the" or o:"a third of") o:sacrifices',
    "all_other_nonland": BASE + 'o:"sacrifices all other"',
}
cru = {}
for k, q in BUSCAS.items():
    cru[k] = {"q": q, **busca(q)}
    print(f"{k:32s} {len(cru[k]['cartas']):4d} cartas  {cru[k].get('erro', '')}", file=sys.stderr)

por_id = {}
achada_em = {}
for k, r in cru.items():
    for c in r["cartas"]:
        por_id[c["oracle_id"]] = c
        achada_em.setdefault(c["oracle_id"], []).append(k)

NUM = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "thirteen": 13}


def texto(c):
    if c.get("oracle_text"):
        return c["oracle_text"]
    return "\n//\n".join(f.get("oracle_text", "") for f in c.get("card_faces", []))


def classifica(c):
    t = texto(c)
    tl = " ".join(f.get("type_line", "") for f in c.get("card_faces", [])) if "card_faces" in c else c["type_line"]
    low = t.lower()
    quem = []
    for rot, pad in (("each player", r"each player sacrifices"), ("each opponent", r"each opponent sacrifices"), ("each other player", r"each other player sacrifices"),
                     ("target player/opponent", r"target (player|opponent) sacrifices"), ("player (todos)", r"(?<!target )(?<!each )players? (also )?sacrifices"),
                     ("for each player", r"for each player"), ("defending player", r"defending player sacrifices")):
        if re.search(pad, low):
            quem.append(rot)
    alvo = []
    for rot, pad in (("criatura", r"sacrifices?[^.]*creature"), ("permanente", r"sacrifices?[^.]*permanent"), ("artefato", r"sacrifices?[^.]*artifact"),
                     ("terreno", r"sacrifices?[^.]*land"), ("encantamento", r"sacrifices?[^.]*enchantment")):
        if re.search(pad, low):
            alvo.append(rot)
    qtd = []
    if re.search(r"sacrifices? all|sacrifices? each|sacrifices? every", low): qtd.append("tudo")
    if "all other" in low and "sacrifice" in low: qtd.append("all other")
    if re.search(r"all but", low): qtd.append("all but")
    if re.search(r"half|a third", low): qtd.append("metade/terco")
    if re.search(r"sacrifices? that many|sacrifices? x |sacrifices? x$|any number", low): qtd.append("X/livre")
    if re.search(r"sacrifices? (two|three|four|five|six|seven|thirteen)", low): qtd.append("N fixo>=2")
    if re.search(r"choose a number", low): qtd.append("N livre")
    if not qtd and re.search(r"sacrifices? (a|one) ", low): qtd.append("1")
    return {"name": c["name"], "mana_cost": c.get("mana_cost") or " // ".join(f.get("mana_cost", "") for f in c.get("card_faces", [])), "cmc": c.get("cmc"), "type_line": tl,
            "color_identity": c["color_identity"], "legal_commander": c["legalities"]["commander"], "oracle": t, "quem": quem, "alvo": alvo, "qtd": qtd,
            "achada_em": achada_em[c["oracle_id"]], "oracle_id": c["oracle_id"], "rulings_uri": c.get("rulings_uri"), "set": c.get("set"), "released_at": c.get("released_at")}


todas = sorted((classifica(c) for c in por_id.values()), key=lambda x: (x["cmc"] or 0, x["name"]))
# 'wipe' = faz o jogador sacrificar mais de 1 permanente de criatura/artefato/permanente de uma vez (N>=2, tudo, all but, livre, metade)
def tipo(x):
    q = set(x["qtd"])
    if q & {"tudo", "all other", "all but", "metade/terco", "X/livre", "N fixo>=2", "N livre"}:
        base = "terreno" if x["alvo"] == ["terreno"] else "mass"
        return base
    return "edict de 1" if "1" in q else "outro"
for x in todas:
    x["tipo"] = tipo(x)
json.dump(todas, open(os.path.join(AQUI, "..", "dados", "busca_ampla_classificada.json"), "w"), ensure_ascii=False, indent=1)
with lzma.open(os.path.join(AQUI, "..", "dados", "busca_ampla_cru.json.xz"), "wt", preset=9) as f:
    json.dump(cru, f, ensure_ascii=False)

print(f"Uniao deduplicada por oracle_id: {len(todas)} cartas (R/W/B, legais em Commander)")
for tp in ("mass", "terreno", "edict de 1", "outro"):
    sel = [x for x in todas if x["tipo"] == tp]
    print(f"\n=== {tp.upper()}: {len(sel)} cartas")
    for x in sel:
        print(f"- {x['name']} | {x['mana_cost']} | {x['type_line']} | legal={x['legal_commander']} | quem={x['quem']} alvo={x['alvo']} qtd={x['qtd']}")
        print("    ", x["oracle"].replace("\n", " ")[:330])

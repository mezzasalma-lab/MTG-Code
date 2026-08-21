"""
Matriz de sinergia - Thranduil, the Elvenking

Motivo de existir: numa conversa anterior, avaliei cartas pra corte usando uma
lente por vez (EDHREC, depois GY-ability, depois tag de funcao) e errei
repetidamente porque nao cruzava tudo simultaneamente antes de falar. Esse
script existe pra isso NAO acontecer de novo - toda avaliacao de corte/adicao
deve rodar por aqui primeiro, nao sair de julgamento ad-hoc.

Fontes, sem inventar nada:
- CARD_DB do thranduil_goldfish_v1.py (tags de funcao ja derivadas de oracle_text real)
- /tmp/scryfall_cache/thranduil_full.json (oracle_text bruto, pra deteccao mecanica)
- /tmp/scryfall_cache/thranduil_edhrec.json (inclusao real, 5314 decks)

O que este script calcula pra CADA carta da lista, tudo junto:
1. Todas as tags de funcao do CARD_DB (ramp/draw/removal/protecao/tutor/finisher/etc)
2. % de inclusao no EDHREC (categoria de maior % entre todas)
3. Se tem habilidade ATIVADA (formato "custo: efeito") - unica coisa que o
   Thranduil herda de Elfos no cemiterio (CR: nomes proprios em habilidades
   concedidas passam a se referir a quem recebeu a habilidade)
4. Se e um "combustivel de GY" - mill de cartas, relevante pro motor do
   Thranduil mesmo sem habilidade ativada propria (ex: Trystan/Lluwen enchem
   o cemiterio de Elfos pros OUTROS cartoes ativados funcionarem)
5. Cluster de redundancia - outras cartas que cobrem a mesma funcao primaria
6. "protegida" = tem pelo meno uma funcao que ja identificamos como escassa
   nesta sessao (removal, draw engine validado, ramp, protecao, finisher,
   tutor, GY-fuel) - NUNCA sugerir corte de carta protegida sem dizer
   explicitamente por que a perda e aceitavel apesar disso.
"""

import json, re, sys
sys.path.insert(0, '.')
import thranduil_goldfish_v1 as sim

ORACLE_CACHE = "/tmp/scryfall_cache/thranduil_full.json"
EDHREC_CACHE = "/tmp/scryfall_cache/thranduil_edhrec.json"

PROTECTED_TAGS = {
    "draw_engine", "creature_draw_engine", "combat_damage_draw",
    "removal", "removal_repeatable", "removal_combat", "removal_artifact",
    "removal_enchantment", "removal_exile", "ramp",
    "finisher_repeatable", "finisher_drain", "finisher_burst",
    "protection", "protection_counterspell", "tutor", "tutor_gy", "tutor_passive",
    "wipe_asymmetric", "bounce_asymmetric", "gy_fuel",
}

def load_oracle():
    return json.load(open(ORACLE_CACHE))

def load_edhrec():
    d = json.load(open(EDHREC_CACHE))
    cardlists = d["container"]["json_dict"]["cardlists"]
    edhrec = {}
    for cl in cardlists:
        if cl.get("tag") == "lands":
            continue
        for c in cl["cardviews"]:
            name = c["name"]
            nd, pd = c.get("num_decks", 0), c.get("potential_decks", 1)
            pct = nd / pd * 100 if pd else 0
            if name not in edhrec or pct > edhrec[name][0]:
                edhrec[name] = (pct, cl.get("tag"))
    return edhrec

def has_activated_ability(oracle_text: str) -> list:
    """Deteccao mecanica de habilidade ativada: linha no formato 'custo: efeito'.
    Nao pega gatilhos ('Whenever...') nem estaticas sem dois-pontos."""
    if not oracle_text:
        return []
    found = []
    for line in oracle_text.split("\n"):
        line = line.strip()
        if line.startswith("("):
            continue
        m = re.match(r"^([^.]{0,60}?):\s*(.+)$", line)
        if m:
            found.append(line)
    return found

def is_elf_type(type_line: str) -> bool:
    return "Elf" in (type_line or "")

def mills_cards(oracle_text: str) -> bool:
    """'Combustivel de GY' = qualquer efeito que bote cartas SUAS no cemiterio:
    mill classico OU descartar carta(s) da propria mao. Ficou faltando o caso
    de descarte na primeira versao (Formidable Speaker discarta, nao 'mill',
    e passou batido)."""
    if not oracle_text:
        return False
    t = oracle_text.lower()
    return "mill" in t or "discard a card" in t or "discard up to" in t

def build_matrix(deck_names, oracle_cache, edhrec):
    rows = []
    for name in deck_names:
        card_db = sim.CARD_DB.get(name)
        if not card_db or "Land" in card_db.types:
            continue

        oracle = oracle_cache.get(name) or oracle_cache.get(name.split(" // ")[0])
        text = ""
        type_line = ""
        if oracle:
            text = oracle.get("oracle_text") or ""
            type_line = oracle.get("type_line") or ""
            if not text and "card_faces" in oracle:
                text = "\n".join((f.get("oracle_text") or "") for f in oracle["card_faces"])
                type_line = oracle["card_faces"][0].get("type_line", "")

        tags = set(card_db.tags)
        activated = has_activated_ability(text) if is_elf_type(type_line) else []
        gy_inheritable = bool(activated)
        gy_fuel = mills_cards(text) or card_db.mill_amount > 0

        edh_name = name.split(" // ")[0]
        edh_pct, edh_cat = edhrec.get(edh_name, (None, None))

        protected = tags & PROTECTED_TAGS
        if gy_inheritable:
            protected.add("gy_inheritable_ability")
        if gy_fuel:
            protected.add("gy_fuel")

        rows.append({
            "name": name,
            "tags": sorted(tags),
            "edhrec_pct": edh_pct,
            "edhrec_cat": edh_cat,
            "gy_inheritable_ability": gy_inheritable,
            "gy_inheritable_detail": activated,
            "gy_fuel": gy_fuel,
            "protected": sorted(protected),
            "is_protected": len(protected) > 0,
        })
    return rows

def cluster_redundancy(rows):
    """Agrupa por cada tag de funcao (exceto 'elf' generico) pra mostrar quem mais cobre o mesmo papel."""
    clusters = {}
    for r in rows:
        for t in r["tags"]:
            if t == "elf":
                continue
            clusters.setdefault(t, []).append(r["name"])
    return clusters

def parse_decklist_names():
    names = []
    for line in open("lista.md"):
        line = line.strip()
        m = re.match(r"^\d+\s+(.+)$", line)
        if m and m.group(1) != sim.COMMANDER:
            names.append(m.group(1))
    return names

# Candidatas a ADICAO em consideracao - precisam passar pelo MESMO crivo que
# as cartas ja no deck, senao a avaliacao fica incompleta de novo (ja
# aconteceu: avaliei o deck todo mas nunca rodei as candidatas por aqui).
CANDIDATE_ADDITIONS = [
    "Deadly Rollick", "Putrefy", "Feed the Swarm",
    "Devoted Druid", "Imperious Perfect", "Formidable Speaker",
]

def main():
    oracle_cache = load_oracle()
    edhrec = load_edhrec()
    names = parse_decklist_names()

    include_candidates = "--with-candidates" in sys.argv
    if include_candidates:
        for n in CANDIDATE_ADDITIONS:
            if n not in sim.CARD_DB:
                print(f"AVISO: {n} nao esta no CARD_DB do simulador, pulando (adicione antes de avaliar).")
                continue
        names = names + [n for n in CANDIDATE_ADDITIONS if n in sim.CARD_DB]

    rows = build_matrix(names, oracle_cache, edhrec)
    clusters = cluster_redundancy(rows)

    # Ordena: nao-protegidas primeiro, depois por EDHREC crescente (mais fraca primeiro)
    def sort_key(r):
        return (r["is_protected"], r["edhrec_pct"] if r["edhrec_pct"] is not None else -1)
    rows.sort(key=sort_key)

    print(f"{'Carta':38} | {'EDHREC':9} | {'Protegida?':10} | {'GY-herdavel?':13} | {'GY-fuel?':9} | Funcoes")
    print("-" * 140)
    for r in rows:
        pct = f"{r['edhrec_pct']:.1f}%" if r["edhrec_pct"] is not None else "n/a"
        prot = "SIM" if r["is_protected"] else "nao"
        gyh = "SIM" if r["gy_inheritable_ability"] else "nao"
        gyf = "SIM" if r["gy_fuel"] else "nao"
        funcs = ",".join(r["protected"]) if r["protected"] else ",".join(r["tags"]) or "(nenhuma)"
        print(f"{r['name']:38} | {pct:9} | {prot:10} | {gyh:13} | {gyf:9} | {funcs}")

    print("\n=== Candidatos reais a corte (sem NENHUMA protecao em nenhuma dimensao) ===")
    real_candidates = [r for r in rows if not r["is_protected"]]
    for r in real_candidates:
        pct = f"{r['edhrec_pct']:.1f}%" if r["edhrec_pct"] is not None else "n/a"
        print(f"  {r['name']:38} EDHREC={pct}  tags={r['tags']}")

    if not real_candidates:
        print("  NENHUM - toda carta da lista tem pelo menos uma funcao protegida.")

    with open("thranduil_synergy_matrix.json", "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "clusters": clusters}, f, ensure_ascii=False, indent=1)
    print("\nMatriz completa salva em thranduil_synergy_matrix.json")

if __name__ == "__main__":
    main()

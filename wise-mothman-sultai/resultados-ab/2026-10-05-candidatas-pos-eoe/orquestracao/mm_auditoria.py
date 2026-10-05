"""Auditoria mecanica do deck Mothman a partir de lista.md + cache de oraculo. Uso: python3 mm_auditoria.py <lista.md> <saida.txt>"""
import json, re, sys, collections
lista, saida = sys.argv[1], sys.argv[2]
cache = json.load(open("/home/user/MTG-Code/scryfall-cache/oracle-cache.json"))
sec = None; deck = []
for l in open(lista):
    l = l.rstrip("\n")
    m = re.match(r"^(\d+)\s+(.+)$", l)
    if l.startswith("## "): sec = l[3:].strip().lower()
    if m: deck.append((int(m.group(1)), m.group(2).strip(), sec))
out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s)
def card(n): return cache[n]
def tl(n): return card(n)["type_line"] or ""
def is_land(n): return "Land" in tl(n).split("//")[-1] if "//" in tl(n) and "Land" in tl(n).split("//")[-1] and "Land" not in tl(n).split("//")[0] else "Land" in tl(n)
BASICS = {"Forest", "Island", "Swamp"}
P("## 1. Identidade de cor e legalidade")
bad = []
tot = 0
for n, nome, s in deck:
    c = card(nome); tot += n
    if not set(c["color_identity"]) <= set("BGU"): bad.append((nome, c["color_identity"]))
    if c["legalities"]["commander"] != "legal": bad.append((nome, c["legalities"]["commander"]))
P(f"total {tot} cartas (comandante + deck); fora da identidade BGU ou nao-legal: {bad or 'nenhuma'}")
dup = [nome for n, nome, s in deck if n > 1 and nome not in BASICS]
P("duplicadas nao-basicas:", dup or "nenhuma")
# terrenos
P("\n## 2. Terrenos")
lands = [(n, nome) for n, nome, s in deck if s == "deck" and "Land" in (card(nome)["type_line"] or "") and "Creature" not in (card(nome)["type_line"] or "")]
mdfc = [nome for n, nome, s in deck if "//" in nome and "Land" in card(nome)["type_line"].split("//")[-1] and "Land" not in card(nome)["type_line"].split("//")[0]]
nl = sum(n for n, _ in lands)
P(f"terrenos contados por type_line (INCLUI o MDFC {mdfc}, que tem a face Land): {nl} = {nl - 1} de face unica + 1 MDFC (basicos {sum(n for n,x in lands if x in BASICS)}, nao-basicos incl. MDFC {sum(n for n,x in lands if x not in BASICS)})")
P("lista:", ", ".join(f"{n}x {x}" for n, x in sorted(lands, key=lambda t: t[1])))
# fontes de cor
TYPES = lambda nome: set(re.findall(r"(Plains|Island|Swamp|Mountain|Forest)", (card(nome)["type_line"] or "").split("//")[0]))
def prod(nome):
    t = card(nome)["oracle_text"] or ""
    s = set()
    for m in re.finditer(r"\{T\}[^.\n]*?: Add ([^.\n]+)", t):
        s |= set(re.findall(r"\{([WUBRG])\}", m.group(1)))
        if "any color" in m.group(1) or "any one color" in m.group(1): s |= {"ANY"}
    for t_ in TYPES(nome):
        s.add({"Island": "U", "Swamp": "B", "Forest": "G", "Plains": "W", "Mountain": "R"}[t_])
    return s
fetch_types = {"Misty Rainforest": {"Forest", "Island"}, "Polluted Delta": {"Island", "Swamp"}, "Verdant Catacombs": {"Swamp", "Forest"}}
col = {}
lib_lands = [x for n, x in lands for _ in range(n)]
TCOL = {"Island": "U", "Swamp": "B", "Forest": "G"}
dir_, fetch_, cond_ = collections.Counter(), collections.Counter(), collections.Counter()
detalhe = []
for n, nome in lands:
    p = prod(nome)
    if nome == "Command Tower": p = {"U", "B", "G"}
    if nome in fetch_types:
        alvo = set()
        for x in lib_lands:
            if TYPES(x) & fetch_types[nome]: alvo |= {TCOL[t] for t in TYPES(x) if t in TCOL}
        for c in alvo: fetch_[c] += n
        detalhe.append((nome, "fetch->" + "".join(sorted(alvo))))
        continue
    if nome == "Fabled Passage":
        for c in "UBG": fetch_[c] += n
        detalhe.append((nome, "fetch basico->UBG (precisa de basico de cada cor na biblioteca)")); continue
    if nome == "Plaza of Heroes":
        for c in "UBG": cond_[c] += n
        detalhe.append((nome, "condicional: so' magia lendaria / cor entre permanentes lendarios")); continue
    pp = p & set("UBG")
    for c in pp: dir_[c] += n
    detalhe.append((nome, "".join(sorted(pp)) or "C" + ("(tapped)" if re.search(r"enters tapped", card(nome)["oracle_text"] or "") else "")))
P("producao por terreno:", "; ".join(f"{a}={b}" for a, b in detalhe))
P(f"fontes DIRETAS: U={dir_['U']} B={dir_['B']} G={dir_['G']}")
P(f"fontes por BUSCA (fetch/Passage), contadas como a uniao dos tipos alcancaveis na lista: U={fetch_['U']} B={fetch_['B']} G={fetch_['G']}")
P(f"condicional (Plaza of Heroes, so' pra lendarias): U={cond_['U']} B={cond_['B']} G={cond_['G']}")
for c in "UBG": P(f"  total incondicional {c}: {dir_[c] + fetch_[c]}")
# (entra virado: conferido a mao no oraculo; o regex dava falso positivo nos choques, ver auditoria.md)
# nao-terrenos
P("\n## 3. Curva de mana (nao-terrenos, comandante fora)")
nonland = [(n, nome) for n, nome, s in deck if s == "deck" and (n, nome) not in lands]
curve = collections.Counter()
for n, nome in nonland:
    c = card(nome); cm = int(c["cmc"] or 0) if "//" not in nome else int(c["cmc"] or 0)
    curve[cm] += n
P("cmc:", dict(sorted(curve.items())), "| total nao-terrenos:", sum(curve.values()), "| cmc medio:", round(sum(k * v for k, v in curve.items()) / sum(curve.values()), 2))
P("(X-spells contam cmc com X=0: Walking Ballista, Nuclear Fallout, Repulsive Mutation, Agadeem's Awakening)")
P("\n## 3b. Pips de cor (TRIAGEM agregada — nao e' necessidade turno-a-turno, Regra 8; so' sinaliza desequilibrio grosseiro)")
pip = collections.Counter(); early = collections.Counter(); ncards = collections.Counter()
for n, nome in nonland:
    mc = card(nome)["mana_cost"] or ""
    if "//" in mc: mc = mc.split("//")[0]
    cores = set()
    for sym in re.findall(r"\{([^}]+)\}", mc):
        if re.fullmatch(r"[WUBRG]", sym):
            pip[sym] += n; cores.add(sym)
        elif re.fullmatch(r"[WUBRG]/[WUBRG]", sym):
            a, b = sym.split("/"); pip[a + "/" + b] += n; cores |= {a, b}
    for c in cores & set("UBG"):
        ncards[c] += 1
        if int(card(nome)["cmc"] or 0) <= 2: early[c] += 1
P("pips mono:", {c: pip[c] for c in "UBG"}, "| hibridos:", {k: v for k, v in pip.items() if "/" in k})
P("cartas nao-terreno que exigem a cor (hibrido conta nas duas):", dict(ncards), "| dessas, com cmc<=2:", dict(early))

# categorias (heuristica por texto; revisao manual abaixo)
P("\n## 4. Categorias por oraculo (heuristica por regex; lista completa para conferencia)")
CAT = {
 "ramp": r"search your library for a (basic land|Forest)|Add \{C\}\{C\}|\{T\}: Add (\{[WUBRGC]\}|X mana|one mana)|Eldrazi Spawn|Treasure|put a land card from among them onto the battlefield|put (up to two )?land cards? .*onto the battlefield",
 "compra": r"draw (a|two|three|four|that many|X) cards?|you may draw|draw a card",
 "remocao_pontual": r"Destroy target|Exile target|exile target|-X/-X|deals? \d+ damage to any target|damage to any target|Return target .* to its owner's hand|Remove a \+1/\+1 counter .* deals 1 damage",
 "board_wipe": r"All creatures get|Each creature gets|Return each creature|Destroy all|Wave Goodbye",
 "contramagica": r"Counter target",
 "protecao": r"hexproof|indestructible|Regenerate|protection from",
 "recursao": r"return .* from your graveyard|from your graveyard|put .* from (a|your) graveyard onto the battlefield|retrace|Muldrotha",
}
cats = collections.defaultdict(list)
for n, nome in nonland + [(1, m) for m in mdfc]:
    t = (card(nome)["oracle_text"] or "")
    for k, rx in CAT.items():
        if re.search(rx, t, re.I): cats[k].append(nome)
for k, v in cats.items(): P(f"- {k} ({len(v)}): {', '.join(sorted(set(v)))}")
open(saida, "w").write("\n".join(out) + "\n")

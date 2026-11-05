#!/usr/bin/env python3
"""Auditoria ESTATICA do deck Tam, the Possibility (registro de 2026-10-19; sem simulador): composicao, curva, planeswalkers e tipos, base de mana, EDHREC e probabilidade dos combos achados no Spellbook (Regra 7 de user-standing-rules).
Le SO' dos dados arquivados: dados/resolvido.json.xz (Scryfall, set + nº de colecionador), dados/edhrec_tam.json.xz, dados/spellbook_tam.json. Uso: python3 analise_estatica.py > ../resumos/analise_estatica.md"""
import collections, json, lzma, math, os, re
AQUI = os.path.dirname(os.path.abspath(__file__)); ARQ = os.path.abspath(os.path.join(AQUI, ".."))
rows = json.load(lzma.open(os.path.join(ARQ, "dados", "resolvido.json.xz"), "rt")); edh = json.load(lzma.open(os.path.join(ARQ, "dados", "edhrec_tam.json.xz"), "rt")); sb = json.load(open(os.path.join(ARQ, "dados", "spellbook_tam.json")))
CMD = [x for x in rows if x["cat"].startswith("Commander")][0]["card"]
main = [x for x in rows if x["cat"] not in ("Sideboard",) and not x["cat"].startswith("Commander")]; side = [x for x in rows if x["cat"] == "Sideboard"]
assert len(main) == 99 and len(side) == 13
def txt(c): return c.get("oracle_text") or ""
def tl(c): return c["type_line"]
def is_land(c): return "Land" in tl(c).split("—")[0]
def is_pw(c): return "Planeswalker" in tl(c).split("—")[0]
print("# Auditoria estática — Tam, the Possibility (WUBRG) — 2026-10-19\n")
print(f"Comandante: **{CMD['name']}** ({CMD['mana_cost']}, {tl(CMD)}), identidade de cor {''.join(sorted(CMD['color_identity'], key='WUBRG'.index))}. Deck: {len(main)} + comandante; sideboard: {len(side)}. Gerado de `dados/resolvido.json.xz`, `edhrec_tam.json.xz` e `spellbook_tam.json`.\n")
# ---------- 1. composicao
print("## 1. Composição\n")
cat = collections.Counter(x["cat"] for x in main)
print("| categoria do usuário | cartas |\n|---|---|")
for k, v in cat.most_common(): print(f"| {k} | {v} |")
tipos = collections.Counter()
for x in main:
    p = tl(x["card"]).split("—")[0]
    for k in ("Land", "Creature", "Planeswalker", "Artifact", "Enchantment", "Instant", "Sorcery"):
        if k in p: tipos[k] += 1
print(f"\nTipos no deck (uma carta pode contar em vários; as 8 \"Way of the…\" e o Oath of Nissa/Teferi são encantamentos lendários): " + ", ".join(f"{k} {v}" for k, v in tipos.most_common()) + ".")
print(f"\nEDHREC (média de {edh['container']['json_dict']['card'].get('num_decks', '?')} decks do Tam): criaturas {edh['creature']}, instantâneos {edh['instant']}, feitiços {edh['sorcery']}, artefatos {edh['artifact']}, encantamentos {edh['enchantment']}, planeswalkers {edh['planeswalker']}, terrenos {edh['land']} (básicos {edh['basic']}). Este deck: criaturas {tipos['Creature']}, instantâneos {tipos['Instant']}, feitiços {tipos['Sorcery']}, artefatos {tipos['Artifact']}, encantamentos {tipos['Enchantment']}, **planeswalkers {tipos['Planeswalker']}**, terrenos {tipos['Land']} (**0 básicos**).\n")
# ---------- 2. curva
print("## 2. Curva (não-terrenos do deck, sem o comandante)\n")
nl = [x["card"] for x in main if not is_land(x["card"])]
mv = collections.Counter(int(c["cmc"]) for c in nl)
print("| MV | " + " | ".join(str(i) for i in range(0, 10)) + " |\n|---|" + "---|" * 10)
print("| cartas | " + " | ".join(str(mv.get(i, 0)) for i in range(0, 10)) + " |")
print(f"\nNão-terrenos: {len(nl)}; MV médio **{sum(c['cmc'] for c in nl) / len(nl):.2f}**; mediana {sorted(c['cmc'] for c in nl)[len(nl) // 2]:.0f}. Sem o desconto da Tam. EDHREC (curva média): " + ", ".join(f"MV{k}: {v}" for k, v in edh["panels"]["mana_curve"].items()) + ".")
pws = [c for c in nl if is_pw(c)]
def generico(c):
    m = re.match(r"^(?:\{(\d+)\})?", c.get("mana_cost") or ""); return int(m.group(1)) if m and m.group(1) else 0
com = collections.Counter(int(c["cmc"]) - (1 if generico(c) >= 1 else 0) for c in pws); sem = collections.Counter(int(c["cmc"]) for c in pws)
print(f"\n**Planeswalkers: {len(pws)}.** Custo de conjuração, sem a Tam / com a Tam em campo (\"{{1}} a menos\" só reduz o genérico; PW sem genérico no custo não desconta): " + "; ".join(f"MV{k}: {sem.get(k, 0)}→{com.get(k, 0)}" for k in range(1, 8)) + f". Média {sum(sem.elements()) / len(pws) if False else sum(k * v for k, v in sem.items()) / len(pws):.2f} → {sum(k * v for k, v in com.items()) / len(pws):.2f}.\n")
# ---------- 3. planeswalkers e tipos
print("## 3. Planeswalkers e tipos de planeswalker (o X da Tam)\n")
def tipos_pw(c):
    t = tl(c).split("—")
    return [s for s in t[1].split()] if len(t) > 1 else []
print("| planeswalker | MV | lealdade | tipo(s) |\n|---|---|---|---|")
for c in sorted(pws, key=lambda c: (c["cmc"], c["name"])): print(f"| {c['name']} | {int(c['cmc'])} | {c['loyalty']} | {' '.join(tipos_pw(c)) or '(nenhum)'} |")
dist = sorted({t for c in pws for t in tipos_pw(c)})
sem_tipo = [c["name"] for c in pws if not tipos_pw(c)]
print(f"\n**{len(dist)} tipos de planeswalker distintos entre os {len(pws)} planeswalkers do deck**: {', '.join(dist)}. Sem subtipo (não contam para o X da Tam): {sem_tipo or 'nenhum'}.")
jace = [c["name"] for c in nl if "empower jace" in txt(c).lower()]
print(f"\nAs {len(jace)} cartas \"empower Jace\" ({', '.join(jace)}) criam (ou reforçam) uma **ficha de Jace** (planeswalker azul): conta como o tipo **Jace** (Tam: \"planeswalker types among planeswalkers you control\"). Cada ativação da Tam faz X proliferates; X máximo sem ficha de Jace = {len(dist)}, com = {len(set(dist) | {'Jace'})} (se todos os planeswalkers estivessem em campo ao mesmo tempo; na prática é o que estiver em jogo).\n")
# ---------- 4. mana
print("## 4. Base de mana (Regra 6: fixers flexíveis contam como fontes reais; sem simulação)\n")
lands = [x["card"] for x in main if is_land(x["card"])]
def entrada(c):
    t = txt(c)
    if "enters tapped unless you have two or more opponents" in t: return "lenta (desvira com 2+ oponentes: sempre desvirada numa mesa de 4)"
    if "you may pay 2 life. If you don't, it enters tapped" in t: return "choque (2 de vida ou entra virada)"
    if "unless it's your first, second, or third turn" in t: return "virada a partir do 4º turno"
    if re.search(r"This land enters tapped\.", t): return "sempre virada"
    if "Sacrifice this land: Search" in t: return "fetch"
    return "sempre desvirada"
def fetch_tipos(c):
    m = re.search(r"Search your library for an? (\w+) or (\w+) card", txt(c)); return set(m.groups()) if m else None
COR = {"Plains": "W", "Island": "U", "Swamp": "B", "Mountain": "R", "Forest": "G"}
def cores(c):
    n = c["name"]; t = txt(c); out = set()
    for sub in tl(c).split("—")[-1].split() if "—" in tl(c) else []:
        if sub in COR: out.add(COR[sub])
    if n in ("Command Tower", "City of Brass"): out = set("WUBRG")
    if n == "Starting Town": out = set("WUBRG")            # {T}, pay 1 life: any color
    if n == "Yavimaya, Cradle of Growth": out = {"G"}      # cada terreno e' Forest
    if n == "The World Tree": out = {"G"}                  # + qualquer cor com 6+ terrenos
    for m in re.finditer(r"Add ([^.\n(]+)", re.sub(r"\([^)]*\)", "", t)):
        out |= set(re.findall(r"\{([WUBRG])\}", m.group(1)))
    return out
tab = []
for c in sorted(lands, key=lambda c: c["name"]):
    tab.append((c["name"], entrada(c), cores(c) if not fetch_tipos(c) else set(), fetch_tipos(c)))
print("| terreno | entrada | cores que produz | observação |\n|---|---|---|---|")
OBS = {"Baxter Building": "`{C}`; `{4},{T}`: 4 mana de qualquer combinação", "City of Brass": "1 de dano toda vez que fica virada", "Command Tower": "qualquer cor da identidade do comandante (as 5)", "Exotic Orchard": "só cores que um terreno de OPONENTE produz (condicional)",
       "Fire-Lit Thicket": "filtro: precisa de `{R/G}` para sair `{R}{R}`/`{R}{G}`/`{G}{G}`", "Flooded Grove": "filtro: precisa de `{G/U}`", "Twilight Mire": "filtro: precisa de `{B/G}`", "Wooded Bastion": "filtro: precisa de `{G/W}`",
       "Mossfire Valley": "`{1},{T}`: `{R}{G}` (precisa de 1 mana de entrada)", "Overflowing Basin": "`{1},{T}`: `{G}{U}` (precisa de 1 mana de entrada)", "Great Hall of the Citadel": "`{C}`; `{1},{T}`: 2 mana de qualquer cor, SÓ para magias lendárias",
       "Plaza of Heroes": "`{C}`; qualquer cor SÓ para magia lendária (todo planeswalker e as 8 \"Way of…\" são lendários)", "Starting Town": "`{C}`, ou qualquer cor pagando 1 de vida; entra virado depois do 3º turno", "The World Tree": "sempre virado; com 6+ terrenos todos os terrenos tocam de qualquer cor; `{G}`",
       "Yavimaya, Cradle of Growth": "**todo terreno é Forest**: todo terreno toca `{G}` e toda fetch com Forest acha qualquer terreno", "Boseiju, Who Endures": "canal `{1}{G}`: destrói artefato / encantamento / terreno não básico de oponente"}
for n, e, co, ft in tab:
    o = OBS.get(n, "")
    if ft: o = f"busca {'/'.join(sorted(ft))}"
    print(f"| {n} | {e} | {''.join(sorted(co, key='WUBRG'.index)) or '—'} | {o} |")
ent = collections.Counter(e for _, e, _, _ in tab)
print(f"\nEntrada: " + "; ".join(f"{k}: {v}" for k, v in ent.most_common()) + ". **Nenhum terreno básico na lista**: as fetches só acham terrenos com tipo de terreno (choques, triomes, e qualquer terreno com a Yavimaya em campo).\n")
tipos_terreno = {c["name"]: {s for s in (tl(c).split("—")[1].split() if "—" in tl(c) else [])} for c in lands}
fetchs = {c["name"]: fetch_tipos(c) for c in lands if fetch_tipos(c)}
alvo = {f: sorted(n for n, t in tipos_terreno.items() if t & ft) for f, ft in fetchs.items()}
print("**Alvos de cada fetch (terrenos da lista com o tipo de terreno pedido; com a Yavimaya em campo, qualquer terreno):**\n")
for f, a in alvo.items(): print(f"- {f}: {len(a)} alvos ({', '.join(a)})")
def cor_fetch(f): return set().union(*[cores(next(c for c in lands if c["name"] == n)) for n in alvo[f]])
dirt = {k: 0 for k in "WUBRG"}; efet = {k: 0 for k in "WUBRG"}
filt_ = {"Fire-Lit Thicket", "Flooded Grove", "Twilight Mire", "Wooded Bastion", "Mossfire Valley", "Overflowing Basin"}
for n, e, co, ft in tab:
    if ft: continue
    for k in co:
        if k in "WUBRG": dirt[k] += 1
        if n not in ("Exotic Orchard",): efet[k] += 1
for f in fetchs:
    for k in cor_fetch(f): efet[k] += 1
print("\n| fonte de cor | W | U | B | R | G |\n|---|---|---|---|---|---|")
print("| terrenos que produzem a cor (diretas, inclui filtros e `Command Tower` / `City of Brass` / `Starting Town`) | " + " | ".join(str(dirt[k]) for k in "WUBRG") + " |")
print("| + 4 fetches (pelas cores dos alvos) | " + " | ".join(str(efet[k]) for k in "WUBRG") + " |")
rochas = {"Arcane Signet": set("WUBRG"), "Birds of Paradise": set("WUBRG"), "Noble Hierarch": set("GWU"), "Ignoble Hierarch": set("BRG")}
rc = {k: sum(1 for v in rochas.values() if k in v) for k in "WUBRG"}
print("| + 4 fixers de mana não-terreno sem condição (Arcane Signet, Birds of Paradise, Noble Hierarch, Ignoble Hierarch) | " + " | ".join(str(efet[k] + rc[k]) for k in "WUBRG") + " |")
print("\nNão contados acima (dependem de condição): Plaza of Heroes e Great Hall of the Citadel (só magias lendárias), Exotic Orchard e Fellwar Stone (cores de terrenos de oponente), Bloom Tender e Faeburrow Elder (cores entre os permanentes que você controla), Chromatic Orrery (gasta mana como qualquer cor), Wrenn and Realmbreaker (terrenos tocam de qualquer cor), The World Tree (6+ terrenos).")
# hipergeometrica: fontes efetivas por cor
def hyp_ge(N, K, n, k): return sum(math.comb(K, i) * math.comb(N - K, n - i) for i in range(k, min(K, n) + 1)) / math.comb(N, n)
print("\n**Hipergeométrica por cor** (baralho de 99, 7 cartas + 1 compra por turno a partir do T2, sem mulligan; fontes = linha \"+ 4 fixers\" acima; uma cor por vez, NÃO é a probabilidade conjunta das cinco):\n")
print("| cor (fontes) | ≥1 até T2 | ≥1 até T3 | ≥1 até T4 | ≥2 até T6 | ≥2 até T8 |\n|---|---|---|---|---|---|")
for k in "WUBRG":
    S = efet[k] + rc[k]; n = lambda T: 7 + (T - 1)
    print(f"| {k} ({S}) | {100 * hyp_ge(99, S, n(2), 1):.1f}% | {100 * hyp_ge(99, S, n(3), 1):.1f}% | {100 * hyp_ge(99, S, n(4), 1):.1f}% | {100 * hyp_ge(99, S, n(6), 2):.1f}% | {100 * hyp_ge(99, S, n(8), 2):.1f}% |")
pips = {k: [0, 0, 0] for k in "WUBRG"}
for c in nl:
    for k in "WUBRG":
        q = len(re.findall(r"\{" + k + r"\}", c.get("mana_cost") or ""))
        if q: pips[k][0] += 1
        if q >= 2: pips[k][1] += 1
        if q >= 3: pips[k][2] += 1
print("\nExigência de cor dos não-terrenos (pips `{X}` no custo; sem híbridos): " + "; ".join(f"{k}: {v[0]} cartas ({v[1]} com 2+, {v[2]} com 3+)" for k, v in pips.items()) + ". O comandante custa `{1}{G}{U}` e a ativação dele pede `{W}{U}{B}{R}{G}` + `{T}`.\n")
# ---------- 5. EDHREC
print("## 5. EDHREC (snapshot de 2026-10-19)\n")
cl = {x["header"]: x["cardviews"] for x in edh["container"]["json_dict"]["cardlists"]}
nome_main = {x["card"]["name"] for x in main}; nome_side = {x["card"]["name"] for x in side}
pot = edh["container"]["json_dict"]["card"].get("num_decks")
print(f"Decks do Tam no EDHREC: **{pot}** (bracket declarado em {sum(edh['bracket_counts'].values())}: " + ", ".join(f"B{k} {v}" for k, v in sorted(edh['bracket_counts'].items())) + "). Temas: " + ", ".join(f"{t['value']} {t['count']}" for t in edh["tag_counts"][:8]) + ".\n")
todas = {}
for h, cv in cl.items():
    for x in cv: todas[x["name"]] = x
incl = sorted(todas.values(), key=lambda x: -x["num_decks"] / max(1, x["potential_decks"]))
print("**Cartas de maior inclusão no EDHREC e onde estão neste registro** (inclusão = decks com a carta / decks do Tam; só cartas que o EDHREC lista; as 50 maiores):\n")
print("| carta | inclusão | sinergia | neste deck? |\n|---|---|---|---|")
for x in incl[:50]:
    st = "deck" if x["name"] in nome_main else ("**sideboard**" if x["name"] in nome_side else ("comandante" if x["name"] == CMD["name"] else "não está"))
    print(f"| {x['name']} | {100 * x['num_decks'] / x['potential_decks']:.0f}% | {x['synergy']:+.2f} | {st} |")
BASICOS = {"Plains", "Island", "Swamp", "Mountain", "Forest"}
fora = [x for x in incl if x["name"] not in nome_main and x["name"] not in nome_side and x["name"] != CMD["name"] and x["name"] not in BASICOS and x["num_decks"] / x["potential_decks"] >= 0.30]
print(f"\nCartas com ≥ 30% de inclusão no EDHREC que **não estão** nem no deck nem no sideboard, fora os 5 terrenos básicos ({len(fora)}): " + ", ".join(f"{x['name']} ({100 * x['num_decks'] / x['potential_decks']:.0f}%)" for x in fora) + ".")
bx = [x for x in main if x["card"]["name"] not in todas]
print(f"\nCartas do deck que o EDHREC **não lista** nas listas deste comandante (inclusão baixa demais para aparecer, ou carta nova): {len(bx)}: " + ", ".join(x["card"]["name"] for x in bx) + ".\n")
# ---------- 6. combos
print("## 6. Combos (Commander Spellbook) e probabilidade real (Regra 7)\n")
print(f"{len(sb['reconhece'])} nomes resolvidos no Spellbook, **{len(sb['nao_reconhecidos'])} não reconhecidos** (inclui o comandante, lançado em 2026-10-02); controle positivo (Thassa's Oracle + Demonic Consultation aparece): {sb['controle_positivo_thassa_consultation']}; controle de corte (sem a Consultation o combo some): {sb['controle_de_corte_combo_sumiu_sem_a_consultation']}. Combos no deck exato: **{len(sb['deck']['incluidos'])}**; \"quase\" (a uma carta de distância): {len(sb['deck']['quase'])}.\n")
N = 99
def p_todas(k, n): return math.comb(N - k, n - k) / math.comb(N, n)
def p_uniao(n):
    A = p_todas(2, n); B = p_todas(3, n); AB = p_todas(4, n); return A + B - AB
print("| combo | peças | mana mínimo das peças (com a Tam em campo para o planeswalker) |\n|---|---|---|\n| Teferi, Temporal Archmage + The Chain Veil | 2 | Teferi 6 (5 com a Tam) + Veil 4 + ativação `{4}` |\n| Chromatic Orrery + Tezzeret the Seeker + The Chain Veil | 3 | Orrery 7 + Veil 4 + Tezzeret 5 (4 com a Tam); o Orrery já dá `{C}`×5 para pagar a ativação do Veil |")
print("\nProbabilidade de ter **todas as peças já vistas** (7 cartas + 1 compra por turno a partir do T2, sem mulligan, sem tutor), deck de 99:\n")
print("| até o turno | cartas vistas | Teferi TA + Chain Veil | Orrery + Tezzeret + Chain Veil | qualquer dos dois |\n|---|---|---|---|---|")
for T in (5, 6, 8, 10, 12):
    n = 7 + T - 1; print(f"| T{T} | {n} | {100 * p_todas(2, n):.2f}% | {100 * p_todas(3, n):.3f}% | {100 * p_uniao(n):.2f}% |")
print("\n**Tutores que mudam a conta:** `Tezzeret the Seeker` (−X: busca artefato de MV ≤ X e põe em campo: pode buscar o The Chain Veil com X = 4, mas entra com 4 de lealdade e fica em 0) e `Entrust the Spark` (sacrifica um planeswalker e busca um planeswalker: acha Tezzeret ou Teferi). O Spellbook **não** conta isso.")
d1 = json.load(open(os.path.join(ARQ, "dados", "spellbook_combos_detalhe.json")))["787-1124"]
print("\n**Atenção ao combo Teferi + Chain Veil neste deck:** o passo-a-passo do próprio Spellbook (variante `787-1124`, `dados/spellbook_combos_detalhe.json`) inclui *\"Cast Teferi from your command zone\"* e o pré-requisito *\"You have enough mana to recast Teferi from your command zone minus four\"*: o laço infinito **recasta o Teferi da zona de comando** depois que ele morre por lealdade 0. **Aqui o comandante é a Tam**, o Teferi está nos 99 e não volta ao comando. O Spellbook o lista como incluído porque as duas cartas estão no deck, mas sem o recast o laço do Veil gasta 1 de lealdade por volta e **termina** quando o Teferi chega a 0 (leitura do texto do Spellbook, não simulada; **este deck tem várias fontes de lealdade (proliferate da própria Tam, Ichormoon Gauntlet, Flux Channeler, Vraska, Teferi's Talent...) que podem repor a lealdade do Teferi, mas isso NÃO foi verificado**: nem o Spellbook o lista, nem há simulador). O combo Orrery + Tezzeret + Veil não tem esse requisito (`+1` do Tezzeret desvira Orrery e Veil: rende `{C}`×5 − `{4}` por volta).\n")
side_q = [(k, v) for k, v in sb["deck"]["quase"].items() if len([p for p in k.split(" + ") if p not in nome_main and p != CMD["name"]]) == 1 and [p for p in k.split(" + ") if p not in nome_main and p != CMD["name"]][0] in nome_side]
print(f"**\"Quase\" cuja peça que falta está no SIDEBOARD** ({len(side_q)}): " + "; ".join(f"{k} → {', '.join(v['produz'])} (bracket {v['bracket']})" for k, v in side_q) + ". Trazer essa carta para o deck criaria um combo de 2 cartas: pesa no Bracket.\n")

# ---------- 7. varreduras de oraculo
print("## 7. Varreduras de oráculo (regex sobre `oracle_text` sem o texto de lembrete; só o deck de 99 + comandante; varredura heurística, NÃO é lista exaustiva de efeitos; lista os nomes para conferência)\n")
alvo = [x["card"] for x in main if not is_land(x["card"])] + [CMD]
def varre(rotulo, rx, so_nao_terreno=True):
    pool = alvo if so_nao_terreno else [x["card"] for x in main] + [CMD]
    nom = sorted({c["name"] for c in pool if re.search(rx, re.sub(r"\([^)]*\)", "", txt(c)), re.I)})      # sem o texto de lembrete entre parenteses (o do Jace traz "Draw a card")
    print(f"- **{rotulo}** ({len(nom)}): " + (", ".join(nom) if nom else "nenhuma"))
varre("contramágica (\"counter target\")", r"counter target")
varre("tutor / busca na biblioteca (não-terreno)", r"search your library")
varre("turno extra", r"extra turn")
varre("destruição em massa de terrenos", r"destroy all lands|each player sacrifices .* land")
varre("remoção em massa de criaturas", r"(destroys? all creatures|exile all creatures|damage to each creature|destroy all creatures with|each player sacrifices a creature|sacrifices all creatures|deals 13 damage to each creature|4 damage to each creature)")
varre("proliferate", r"proliferate")
varre("compra de cartas", r"draw (a|two|three|x|that many) cards?|draws? two cards|you draw a card", True)
varre("cria ficha de Jace (empower Jace)", r"empower jace")
varre("dano direto / perda de vida a oponentes", r"deals? (x|\d+) damage to (each opponent|any target|target player|target opponent)|each opponent loses|target opponent loses|deals that much damage to target opponent")
side_names = {x["card"]["name"] for x in side}
print(f"\nSideboard (13, fora do deck): " + ", ".join(sorted(side_names)) + ". Tipos: " + ", ".join(f"{k} {v}" for k, v in collections.Counter(('Planeswalker' if is_pw(x['card']) else 'Criatura') for x in side).items()) + ".")

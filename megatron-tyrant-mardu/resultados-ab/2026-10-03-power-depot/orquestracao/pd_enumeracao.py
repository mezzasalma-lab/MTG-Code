"""Enumeração por script (Regra #4.4): o que o Power Depot toca na lista do Megatron, lendo type_line/oracle_text/mana_cost do cache do Scryfall
(scryfall-cache/oracle-cache.json; DFC procurado por 'Frente // Verso'). Power Depot: mana de qualquer cor SÓ para magias-artefato e habilidades de artefatos;
Artifact Land; entra tapped; Modular 1. Uso: python3 pd_enumeracao.py"""
import json, re
REPO = "/home/user/MTG-Code"
c = json.load(open(f"{REPO}/scryfall-cache/oracle-cache.json"))
names, sec, qty = [], None, {}
for l in open(f"{REPO}/megatron-tyrant-mardu/lista.md"):
    l = l.rstrip("\n")
    if l.startswith("## "): sec = l[3:].strip().lower(); continue
    m = re.match(r"^(\d+)\s+(.+)$", l)
    if m and sec in ("comandante", "deck", "terrenos"):
        names.append(m.group(2).strip()); qty[m.group(2).strip()] = int(m.group(1))
def get(n):
    k = n if n in c else next((x for x in c if x.startswith(n + " //")), None)
    e = c[k]; tl = e.get("type_line") or ""; ot = e.get("oracle_text") or ""; mc = e.get("mana_cost") or ""
    if e.get("card_faces"):
        if not ot: ot = " // ".join(f.get("oracle_text", "") for f in e["card_faces"])
        if not mc: mc = e["card_faces"][0].get("mana_cost", "")
        if not tl: tl = " // ".join(f.get("type_line", "") for f in e["card_faces"])
    return tl, ot, mc
info = {n: get(n) for n in names}
lands = [n for n in names if "Land" in info[n][0].split(" // ")[0].split(" — ")[0]]
spells = [n for n in names if n not in lands]
def pips(mc): return re.findall(r"\{([WUBRG])\}", mc)
print("nomes distintos lidos de lista.md:", len(names), "| terrenos distintos:", len(lands), "(%d cópias)" % sum(qty[n] for n in lands), "| não-terrenos:", len(spells))
print("\n## 1) MAGIAS-ARTEFATO com pips coloridos no custo (o mana de qualquer cor do Power Depot paga):")
art = [n for n in spells if "Artifact" in info[n][0]]
for n in art:
    p = pips(info[n][2])
    print("  - %-34s %-14s [%s]%s" % (n, info[n][2] or "(sem custo na face frontal)", info[n][0].split(" — ")[0], "  <- colorido" if p else ""))
print("  total de artefatos não-terreno: %d | com pips coloridos: %d" % (len(art), sum(1 for n in art if pips(info[n][2]))))
print("  Comandante: Megatron, Tyrant {3}{R}{W}{B} (Legendary Artifact Creature); More Than Meets the Eye {1}{R}{W}{B} lança a face Vehicle (Legendary Artifact): as duas são magias-artefato.")
print("\n## 2) MAGIAS NÃO-artefato com pips coloridos (o Depot NÃO fixa; só rende {C}):")
for n in spells:
    if n not in art and pips(info[n][2]): print("  - %-34s %-14s [%s]" % (n, info[n][2], info[n][0].split(" — ")[0]))
print("\n## 3) Cartas da lista que LEEM 'artifact' no texto (o Depot é artefato permanente enquanto está em campo/ao entrar/ao ir ao cemitério):")
pat = {
 "affinity/improvise/convoke de artefato": r"affinity for artifacts|improvise",
 "sacrifica artefato (custo ou efeito)": r"sacrifice (an|another|two|three|one or more) artifacts?|sacrifice an artifact",
 "artifact card no cemitério (alvo de reanimar/devolver)": r"artifact card",
 "'nontoken artifact ... enters' (Ultron)": r"nontoken artifact you control enters|another nontoken artifact",
 "'artifact ... put into (your) graveyard from the battlefield'": r"artifact.*put into (a|your) graveyard from the battlefield|artifact you control is put into a graveyard",
 "valor/contagem de artefatos em campo": r"total mana value of noncreature artifacts|greatest mana value among artifacts|for each artifact|number of artifacts",
}
for k, p in pat.items():
    print("  ## %s" % k)
    for n in spells:
        if re.search(p, info[n][1], re.I): print("     - %s [%s]: %s" % (n, info[n][0].split(" — ")[0], re.sub(r"\s+", " ", info[n][1])[:200]))
print("\n## 4) ARTEFATOS-CRIATURA da lista (alvos possíveis do Modular 1: +1/+1 ao Depot ir pro cemitério):")
for n in spells:
    if re.search(r"Artifact Creature", info[n][0]): print("  - %s (%s)" % (n, info[n][0].split(" — ")[0]))
print("\n## 5) TERRENOS da lista e o que cada um dá (cópias):")
for n in lands:
    tl, ot, mc = info[n]
    if re.search(r"put it onto the battlefield tapped|put (them|those) onto the battlefield tapped", ot, re.I):
        tap = "fetch: o terreno buscado entra tapped"
    elif re.search(r"enters tapped unless|enters tapped if|may pay 2 life", ot, re.I):
        tap = "tapped condicional"
    elif re.search(r"enters tapped|enters the battlefield tapped", ot, re.I):
        tap = "entra TAPPED"
    else:
        tap = "untapped"
    print("  - %-30s x%d  [%s]  %s | %s" % (n, qty[n], tl.split(" — ")[0] if tl.split(" — ")[0] != "Land" else "Land", tap, re.sub(r"\s+", " ", ot)[:120]))
print("\n## 6) HABILIDADES ATIVADAS de cartas-artefato da lista cujo CUSTO tem mana colorido (o mana de qualquer cor do Depot também paga habilidades de artefatos):")
achou = False
for n in art:
    ot = info[n][1]
    for ln in re.split(r"\n| // ", ot):
        if ":" in ln:
            custo = ln.split(":")[0]
            if re.search(r"\{[WUBRG]\}", custo) and "(" not in custo and not custo.strip().startswith(("When", "Whenever", "At the beginning")):   # "(" = custo de CONJURAR de uma face de DFC/MDFC, não habilidade ativada
                achou = True
                print("  - %s: %s" % (n, re.sub(r"\s+", " ", ln)[:200]))
if not achou:
    print("  (nenhuma)")
print("\n## 7) Contagem: artefatos não-terreno %d; magias-artefato com pip colorido %d; não-artefatos com pip colorido %d; terrenos distintos %d (%d cópias)" % (
    len(art), sum(1 for n in art if pips(info[n][2])), sum(1 for n in spells if n not in art and pips(info[n][2])), len(lands), sum(qty[n] for n in lands)))

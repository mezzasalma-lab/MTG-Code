"""Enumera por script, no oraculo das cartas da lista, as condicoes de que dependem as candidatas principais (Regra #4, item 4).
Uso: python3 mm_condicoes.py <lista.md> <saida.txt>"""
import json, re, sys
lista, saida = sys.argv[1], sys.argv[2]
cache = json.load(open("/home/user/MTG-Code/scryfall-cache/oracle-cache.json"))
deck = []
for l in open(lista):
    m = re.match(r"^(\d+)\s+(.+)$", l.rstrip("\n"))
    if m: deck.append(m.group(2).strip())
nb = [d for d in dict.fromkeys(deck) if d not in ("Forest", "Island", "Swamp")]
T = lambda n: cache[n]["oracle_text"] or ""
TL = lambda n: cache[n]["type_line"] or ""
out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s)
def L(titulo, itens, nota=""):
    P(f"- **{titulo}** ({len(itens)}): " + ", ".join(itens) + (f"  _{nota}_" if nota else ""))
P("## Condicoes enumeradas no oraculo da lista (script mm_condicoes.py)\n")
# Evolution Sage / proliferate
cont_p1 = [n for n in nb if re.search(r"\+1/\+1 counter", T(n))]
L("Cartas que colocam/recebem contador +1/+1 (alvos do proliferate; tambem Terrasymbiosis/Corpsejack/Hardened)", cont_p1)
outros_cont = [n for n in nb if re.search(r"quest counter|lore counter|influence counter|loyalty|charge counter|rad counter", T(n)) or "Saga" in TL(n) or "Planeswalker" in TL(n)]
L("Cartas com OUTROS tipos de contador (proliferate tambem os cresce)", outros_cont, "Bloodchief Ascension (quest, precisa de 3), Urza's Saga (lore), Palantir (influence = X do mill), Ashiok (lealdade), rad counters")
# Bruvac
mo = [n for n in nb if re.search(r"each opponent mills|target player mills|that player mills|each player mills|mills? (that many|three|two|a card|cards equal)|its controller mills", T(n), re.I) and n not in ("Icetill Explorer", "Six", "Smuggler's Surprise", "Palantír of Orthanc", "Hedge Shredder", "Takenuma, Abandoned Mire", "Bramble Familiar // Fetch Quest")]
mo += ["Mesmeric Orb"]  # 'that permanent's controller mills' (simetrico)
L("Fontes de mill que atingem OPONENTE (Bruvac dobra: 'If an opponent would mill')", sorted(set(mo)), "alem dos rad counters (Mothman, Mirelurk Queen, Nuclear Fallout) e Palantir (se o oponente nao deixar comprar)")
# Master of Lake-town
perda = [n for n in nb if re.search(r"loses? (\d+ )?life|lose life|each opponent loses|deals? (\d+|X) damage|damage to (each opponent|any target)|Pay \d+ life|pay \d+ life|Pay 1 life|loses 1 life", T(n)) or re.search(r"Pay 1 life", T(n))]
L("Fontes de PERDA DE VIDA (cada uma e' uma mill extra com The Master of Lake-town; inclui as que cobram vida de VOCE)", perda)
# Garruk's Uprising
pw4 = []
for n in nb:
    if "Creature" in TL(n).split("//")[0] and cache[n]["power"] not in (None, "*"):
        try:
            if int(cache[n]["power"]) >= 4: pw4.append(f"{n} ({cache[n]['power']})")
        except ValueError: pass
L("Criaturas com poder IMPRESSO >= 4 (Garruk's Uprising: compra ao entrar; contadores aumentam)", pw4)
# Lo and Li
adv = [n for n in nb if re.search(r"\bAdvisor\b", TL(n).split("//")[0])]
L("Advisors (Lo and Li poe contador em cada um quando oponente descarta/mill)", adv)
# Crime (Deepmuck Desperado / Freestrider Lookout) - o que e' crime: mirar oponente / algo dele / cemiterio dele
crime = [n for n in nb if re.search(r"target (player|opponent|creature|artifact|enchantment|nonland permanent|land|spell|card from a graveyard|noncreature spell|nonbasic land)|Counter target|deals 1 damage|exile target|Destroy target", T(n)) and n not in ("Deepmuck Desperado", "Freestrider Lookout")]
L("Fontes de CRIME (gatilho de Deepmuck Desperado / Freestrider Lookout) - todo alvo no oponente, inclui contramagicas e o gatilho do Mothman se mirar criatura dele", crime)
# creature count for Mothman X cap
cre = [n for n in nb if "Creature" in TL(n).split("//")[0]]
L("Criaturas na lista (cada gatilho do Mothman poe no maximo 1 contador por criatura-alvo; X>numero de corpos e' desperdicado)", cre)
# land to graveyard / dredge
cic = [n for n in nb if re.search(r"Cycling|Dredge|Channel|sacrifice (this land|a land)|Sacrifice this land", T(n))]
L("Terrenos/cartas que mandam TERRENO pro cemiterio de proposito (Gitrog compra; Icetill/Muldrotha/Agatha/Hedge Shredder aproveitam)", cic)
open(saida, "w").write("\n".join(out) + "\n")

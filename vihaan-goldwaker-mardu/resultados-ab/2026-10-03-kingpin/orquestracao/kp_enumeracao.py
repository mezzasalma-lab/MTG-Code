"""Enumeração por script (Regra #4.4): o que o Kingpin ("Whenever you sacrifice Kingpin or another creature, create two Treasure tokens; 1x/turno") toca na
lista do Vihaan, lendo type_line/oracle_text do cache do Scryfall (scryfall-cache/oracle-cache.json; DFC procurado por 'Frente // Verso').
Uso: python3 kp_enumeracao.py"""
import json, re
REPO = "/home/user/MTG-Code"
c = json.load(open(f"{REPO}/scryfall-cache/oracle-cache.json"))
names = [l.strip()[l.strip().index(" ") + 1:] for l in open(f"{REPO}/vihaan-goldwaker-mardu/resultados-ab/_lista_legada/lista.md") if l.strip() and l.strip()[0].isdigit()]
names.append("Vihaan, Goldwaker")
def get(n):
    k = n if n in c else next((x for x in c if x.startswith(n + " //")), None)
    e = c[k]; tl = e.get("type_line") or ""; ot = e.get("oracle_text") or ""
    if not ot and e.get("card_faces"):
        ot = " // ".join(f.get("oracle_text", "") for f in e["card_faces"]); tl = " // ".join(f.get("type_line", "") for f in e["card_faces"])
    return tl, ot
info = {n: get(n) for n in sorted(set(names))}
def show(n, lim=210): return "  - %s [%s]: %s" % (n, info[n][0].split(" — ")[0], re.sub(r"\s+", " ", info[n][1])[:lim])
print("nomes distintos lidos de lista.md (comandante + 99 cartas, básicas contadas uma vez):", len(info))
secoes = [
 ("1) SAÍDAS que sacrificam CRIATURA (custo ou efeito; o Kingpin dispara ao sacrificar, 1x/turno)",
  lambda n, tl, ot: re.search(r"sacrifice (a|an|another|any number of|two|three|up to|one or more|target)?\s*(creature|permanent|artifact or creature|artifact, enchantment|artifact)", ot, re.I) and "Land" not in tl.split(" — ")[0] or (re.search(r"sacrifice", ot, re.I) and "Land" in tl and re.search(r"Sacrifice a creature", ot))),
 ("2) Geradores de TREASURE e substituições de criação (o Kingpin cria 2; Xorn +1, Procession ×2, Academy Manufactor)",
  lambda n, tl, ot: re.search(r"Treasure|would create one or more|instead create", ot) and "Land" not in tl.split(" — ")[0]),
 ("3) Pagadores de 'token criado / token entra / token sai' (cada disparo do Kingpin cria 2+ fichas)",
  lambda n, tl, ot: re.search(r"create or sacrifice a token|tokens? you control (enter|leave)|token you control leaves|whenever you create", ot, re.I)),
 ("4) Pagadores de morte/sacrifício de criatura (o Kingpin sacrificado/saída também dispara estes)",
  lambda n, tl, ot: re.search(r"(creature|nontoken creature)( you control)? dies|whenever you sacrifice|another creature dies|creature (you control )?dies", ot, re.I)),
 ("5) Cartas que LEEM no TEXTO o tipo Human/Villain (o Kingpin é Human Villain, NÃO é outlaw: sem vigilância/haste do Vihaan)",
  lambda n, tl, ot: re.search(r"Villain|Human", ot)),
 ("6) Cartas que fazem Treasure virar CRIATURA (sacrificá-lo vira sacrificar criatura)",
  lambda n, tl, ot: re.search(r"Treasures? you control become|Treasure.*become.*creature|becomes? a .*creature", ot)),
]
for titulo, f in secoes:
    print("\n## " + titulo)
    k = 0
    for n, (tl, ot) in info.items():
        if f(n, tl, ot):
            print(show(n)); k += 1
    print("  (%d cartas)" % k)
cre = [n for n, (tl, ot) in info.items() if "Creature" in tl.split(" // ")[0] and "Land" not in tl.split(" — ")[0]]
outl = [n for n in cre if re.search(r"Assassin|Mercenary|Pirate|Rogue|Warlock", info[n][0])]
print("\n## 7) Contagem: criaturas na lista (com o comandante) = %d | outlaws = %d | não-outlaws = %d" % (len(cre), len(outl), len(cre) - len(outl)))

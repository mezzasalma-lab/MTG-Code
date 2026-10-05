"""Rulings do Scryfall das cartas centrais (deck + candidatas principais), em markdown, a partir SO' dos .json brutos. Uso: python3 resumo_rulings.py <dados_dir>"""
import json, os, sys
d = sys.argv[1]
lista = json.load(open(os.path.join(d, "lista_bruto.json")))
rs = json.load(open(os.path.join(d, "rulings_shortlist.json")))
print("# Rulings lidas (Scryfall `rulings_uri`) — cartas centrais\n")
print("## Cartas do deck\n")
CENTRAIS = ["The Wise Mothman", "Mirelurk Queen", "Kodama of the West Tree", "Winding Constrictor", "Hardened Scales", "Kami of Whispered Hopes", "Bloodchief Ascension", "Mindcrank", "Palantír of Orthanc", "Hollowmurk Siege", "Danny Pink", "Glen Elendra Archmage", "Undead Alchemist", "Mesmeric Orb"]
vistos = set()
for o in lista:
    n = o["carta"]["name"]
    if n in CENTRAIS and n not in vistos:
        vistos.add(n)
        print(f"### {n} ({len(o['rulings'])})")
        if n in ("Mirelurk Queen",):
            print("(mesmas rulings de rad counters do Mothman)\n"); continue
        for r in o["rulings"]: print(f"- {r['published_at']}: {r['comment']}")
        print()
print("## Candidatas principais\n")
PRINC = ["Evolution Sage", "Tekuthal, Inquiry Dominus", "Bruvac the Grandiloquent", "The Master of Lake-town", "Garruk's Uprising", "Mutational Advantage", "Corpsejack Menace", "Lo and Li, Royal Advisors", "Terrasymbiosis", "Oko, Lorwyn Liege // Oko, Shadowmoor Scion", "Grist, the Hunger Tide", "Vraska, Betrayal's Sting", "Innkeeper's Talent", "Contentious Plan", "Karn's Bastion", "Rancor"]
for n in PRINC:
    v = rs.get(n)
    print(f"### {n} ({len(v) if isinstance(v, list) else v})")
    if isinstance(v, list):
        for r in v: print(f"- {r['published_at']}: {r['comment']}")
    print()

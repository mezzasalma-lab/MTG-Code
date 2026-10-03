"""Enumeração por script (Regra #4.4): quais cartas da lista do Vihaan satisfazem cada condição de que a Inevitable Defeat depende
(crime, alvo de oponente, ganho de vida, perda de vida de oponente, exile, gatilho de spell), lendo type_line/oracle_text do cache do Scryfall.
Uso: python3 vih_enumeracao.py"""
import json, re
REPO = "/home/user/MTG-Code"
c = json.load(open(f"{REPO}/scryfall-cache/oracle-cache.json"))
names = [l.strip()[l.strip().index(" ") + 1:] for l in open(f"{REPO}/vihaan-goldwaker-mardu/lista.md") if l.strip() and l.strip()[0].isdigit()]
names.append("Vihaan, Goldwaker")
def text(n):
    k = n if n in c else next((x for x in c if x.startswith(n + " //")), None)
    if k is None: return None, None
    e = c[k]; tl = e.get("type_line") or ""; ot = e.get("oracle_text") or ""
    if not ot and e.get("card_faces"):
        ot = " // ".join(f.get("oracle_text", "") for f in e["card_faces"]); tl = " // ".join(f.get("type_line", "") for f in e["card_faces"])
    return tl, ot
print("nomes distintos lidos de lista.md (comandante + 99 cartas, básicas contadas uma vez):", len(names), "| sem entrada no cache:", [n for n in names if text(n)[0] is None])
pats = {
 "CRIME (commit a crime)": r"commit a crime|committed a crime",
 "ALVO OPONENTE/PERMANENTE DELE (conta como crime ao ser alvo)": r"target (opponent|player|creature an opponent|nonland permanent|permanent an opponent)",
 "GANHA VIDA (você)": r"you gain|gain (\d+|x) life|whenever you gain life",
 "PERDA DE VIDA DE OPONENTE (gatilho)": r"(opponent|each opponent|target opponent|that player) loses?|loses? (\d+|x) life|whenever an opponent loses life",
 "EXILE (spell/habilidade exila permanente)": r"exile target|exile (another )?target|exiles",
 "GATILHO 'whenever you cast ... instant/noncreature/spell'": r"whenever you cast (a|an|your)? ?(instant|noncreature|spell)",
}
for k, p in pats.items():
    print("\n##", k)
    for n in sorted(names):
        tl, ot = text(n)
        if ot and re.search(p, ot, re.I): print("  - %s [%s]: %s" % (n, tl.split(" — ")[0], re.sub(r"\s+", " ", ot)[:210]))

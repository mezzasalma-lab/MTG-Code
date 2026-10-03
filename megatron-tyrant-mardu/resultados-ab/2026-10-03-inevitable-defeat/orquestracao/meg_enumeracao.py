"""Enumeração por script (Regra #4.4): quais cartas da lista do Megatron satisfazem cada condição de que a Inevitable Defeat depende,
lendo type_line/oracle_text do cache do Scryfall (scryfall-cache/oracle-cache.json; DFC procurado por 'Frente // Verso'). Uso: python3 meg_enumeracao.py"""
import json, re
REPO = "/home/user/MTG-Code"
c = json.load(open(f"{REPO}/scryfall-cache/oracle-cache.json"))
names, sec = [], None
for l in open(f"{REPO}/megatron-tyrant-mardu/lista.md"):
    l = l.rstrip("\n")
    if l.startswith("## "): sec = l[3:].strip().lower(); continue
    m = re.match(r"^(\d+)\s+(.+)$", l)
    if m and sec in ("comandante", "deck", "terrenos"): names.append(m.group(2).strip())
def get(n):
    k = n if n in c else next((x for x in c if x.startswith(n + " //")), None)
    if k is None: return None, None
    e = c[k]; tl = e.get("type_line") or ""; ot = e.get("oracle_text") or ""
    if not ot and e.get("card_faces"):
        ot = " // ".join(f.get("oracle_text", "") for f in e["card_faces"]); tl = " // ".join(f.get("type_line", "") for f in e["card_faces"])
    return tl, ot
print("nomes distintos lidos de lista.md (comandante + 99 cartas, básicas contadas uma vez):", len(names), "| sem entrada no cache:", [n for n in names if get(n)[0] is None])
pats = {
 "REMOÇÃO/INTERAÇÃO (exile|destroy|damage|shuffle ... target/all)": r"(exile|destroy|shuffles?) (target|all|each|up to)|deals? (\d+|x) damage to (target|each)|phase out",
 "PERDA DE VIDA DE OPONENTE (alimenta o 2º flip do Megatron)": r"loses? (\d+|x) life|opponents? (have )?lost|each opponent loses|deals? .* damage to (each )?opponent|damage to (that|target|each) (player|opponent)",
 "GANHO/PAGAMENTO DE VIDA (vida como recurso)": r"gain (\d+|x|that much) life|you gain|pay (\d+|x) life|lose (\d+|x) life",
 "EXILE (cartas que exilam / usam exílio)": r"exiled|exile",
}
for k, p in pats.items():
    print("\n##", k)
    for n in names:
        tl, ot = get(n)
        if ot and re.search(p, ot, re.I) and "Land" not in tl.split(" — ")[0]:
            print("  - %s [%s] %s" % (n, tl.split(" — ")[0], re.sub(r"\s+", " ", ot)[:230]))

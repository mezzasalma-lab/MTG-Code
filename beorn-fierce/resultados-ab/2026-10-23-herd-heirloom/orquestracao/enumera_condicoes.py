"""Regra #4 adendo, item 4: enumera POR SCRIPT, lendo type_line/oracle_text/power do cache do Scryfall, quais cartas da lista do Beorn satisfazem cada condicao que o Herd Heirloom usa ou alimenta. Nada de memoria.
Condicoes: (a) criatura com poder >= 4 (alvo da habilidade 2); (b) criatura Bear (Roaming Throne dobra o gatilho concedido); (c) 'creature spell' (so' elas usam o mana da habilidade 1);
(d) cartas que perguntam por trample / dano de combate a jogador / compra por dano de combate; (e) cartas que perguntam por artefato; (f) Ram Through: o que a carta fazia no deck.
Uso: python3 enumera_condicoes.py <lista.md> <cache.json>   (saida em stdout)"""
import json, re, sys
lista, cache = sys.argv[1], sys.argv[2]
oc = json.load(open(cache, encoding="utf-8"))
nomes, sec = [], None
for l in open(lista, encoding="utf-8"):
    if l.startswith("#"): sec = l.lstrip("# ").strip().lower(); continue
    m = re.match(r"^(\d+)\s+(.+)$", l.rstrip("\n"))
    if m and sec: nomes += [m.group(2).strip()] * int(m.group(1))
nomes = sorted(set(nomes))
def carta(n):
    for k in (n, n.split(" // ")[0]):
        if k in oc: return oc[k]
    return None
falta = [n for n in nomes if carta(n) is None]
print(f"cartas na lista (distintas): {len(nomes)} | sem oraculo no cache: {falta}")
def txt(c): return (c.get("oracle_text") or "") + " " + " ".join(f.get("oracle_text", "") for f in c.get("card_faces", []))
def tl(c): return (c.get("type_line") or "")
rows = {n: carta(n) for n in nomes if carta(n)}
pw = {}
for n, c in rows.items():
    if "Creature" in tl(c) or c.get("power") not in (None, ""):
        pw[n] = c.get("power")
print("\n(a) criaturas e PODER impresso (campo power do cache):")
for n, p in sorted(pw.items(), key=lambda kv: (-(int(kv[1]) if str(kv[1]).lstrip('-').isdigit() else -1), kv[0])):
    print(f"   {n:45s} power={p!s:3s} {tl(rows[n])}")
print("   -> power >= 4 (numerico):", [n for n, p in pw.items() if str(p).isdigit() and int(p) >= 4])
print("   -> power nao-numerico (CDA, conferir a mao):", [n for n, p in pw.items() if not str(p).isdigit()])
print("\n(b) Bear no type_line OU Changeling OU 'every creature type' (Maskwood Nexus afeta todas as suas criaturas):")
print("   ", [n for n, c in rows.items() if re.search(r"\bBear\b", tl(c)) or "Changeling" in (c.get("keywords") or []) or "Changeling" in txt(c) or "every creature type" in txt(c)])
print("\n(c) magias de criatura (as unicas que o mana da habilidade 1 paga):", sum(1 for c in rows.values() if "Creature" in tl(c) and "Land" not in tl(c)))
print("    nao-criatura e nao-terreno (nunca usam o mana restrito):", sum(1 for c in rows.values() if "Creature" not in tl(c) and "Land" not in tl(c)))
print("\n(d) oraculo cita trample / 'combat damage to a player' / 'deals combat damage':")
for n, c in rows.items():
    t = txt(c)
    if re.search(r"trample|combat damage to a player|deals combat damage", t, re.I):
        print(f"   {n:45s} | {re.sub(chr(10), ' / ', t)[:170]}")
print("\n(e) oraculo cita 'artifact' (alem de ser artefato):")
for n, c in rows.items():
    t = txt(c)
    if re.search(r"artifact", t, re.I) and n not in ("Herd Heirloom",):
        print(f"   {n:45s} [{tl(c)}] | {re.sub(chr(10), ' / ', t)[:170]}")
print("\n(f) artefatos na lista:", [n for n, c in rows.items() if "Artifact" in tl(c)])

"""audit_inicio_de_combate.py (2026-10-23) — classe achada no Beorn: o gatilho "At the beginning of combat on your turn" estava preso a `can_attack(Beorn)` (lido como "whenever it attacks"),
o que o impedia de disparar com a criatura doente de invocacao ou sem atacar. Esta varredura LISTA, para cada deck do repositorio, as cartas da `lista.md` cujo oraculo (cache do Scryfall, qualquer face)
tem "beginning of combat" e mostra onde o simulador do deck cita a carta, marcando as linhas proximas que contem `can_attack` / `summoning` / `attack`. So' lista candidatos: a leitura de cada um e' a mao.
Uso: python3 audit_inicio_de_combate.py [ROOT]"""
import glob, json, os, re, sys
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
oc = json.load(open(os.path.join(ROOT, "scryfall-cache", "oracle-cache.json"), encoding="utf-8"))
def carta(n):
    for k in (n, n.split(" // ")[0]):
        if k in oc: return oc[k]
def texto(c): return (c.get("oracle_text") or "") + " " + " ".join(f.get("oracle_text", "") for f in c.get("card_faces", []))
total = 0
for sim in sorted(glob.glob(os.path.join(ROOT, "*", "*_goldfish_v1.py"))):
    deck = os.path.dirname(sim); nome = os.path.basename(deck)
    lista = os.path.join(deck, "lista.md")
    if not os.path.exists(lista): continue
    nomes = []
    for l in open(lista, encoding="utf-8"):
        m = re.match(r"^(\d+)\s+(.+)$", l.strip())
        if m: nomes.append(m.group(2).strip())
    cands = []
    for n in sorted(set(nomes)):
        c = carta(n)
        if c and re.search(r"beginning of (?:your )?combat", texto(c), re.I): cands.append((n, texto(c)))
    if not cands: continue
    src = open(sim, encoding="utf-8").read().split("\n")
    print(f"\n== {nome}: {len(cands)} carta(s) com gatilho de inicio de combate")
    for n, t in cands:
        total += 1
        trecho = re.search(r"[^.\n]*beginning of (?:your )?combat[^.\n]*\.?", t, re.I)
        print(f"  * {n} | {trecho.group(0).strip()[:150] if trecho else ''}")
        curto = n.split(",")[0].split(" // ")[0]
        hits = [i for i, l in enumerate(src) if curto in l and not l.strip().startswith("#") and '"""' not in l]
        sus = []
        for i in hits:
            janela = src[max(0, i - 3): i + 4]
            if any(re.search(r"can_attack|summoning|doenca|attackers|attacks", w) for w in janela): sus.append(i + 1)
        print(f"      citada em {len(hits)} linhas do simulador; linhas com can_attack/doenca/attack por perto (ler a mao): {sus[:12]}")
print(f"\ntotal de cartas candidatas: {total}")

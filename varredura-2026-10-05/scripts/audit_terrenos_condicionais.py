"""Inventario estatico (Regra #10; pedido do usuario em 2026-11-11: "revisar e corrigir o Plaza e demais terrenos em todos os simuladores"):
para cada deck com `lista.md`, lista os TERRENOS cujo mana e' restrito ou condicional (oraculo do `scryfall-cache`: 'Spend this mana only', 'color identity', 'that a land ... could produce',
'among ...', 'for each', 'any color/type'; fetchlands fora), e diz se o deck tem simulador (`*_goldfish_v1.py`) e quantas vezes o nome do terreno aparece no arquivo dele (0 = nao modelado).
So' triagem: ler a modelagem de cada terreno a' mao. Uso: python3 -I audit_terrenos_condicionais.py   (da raiz do repositorio ou de qualquer pasta)"""
import glob, json, os, re
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
C = json.load(open(os.path.join(R, "scryfall-cache", "oracle-cache.json")))
PAD = [r"Spend this mana only", r"commander's color identity", r"that a land you control could produce", r"that a land an opponent controls could produce", r"among (legendary|creatures|lands|permanents)",
       r"for each ", r"of any type that a land", r"any color", r"any type", r"Add \{C\} for each", r"depending on"]
def cartas(lista):
    out, ativo = [], True
    for ln in open(lista, encoding="utf-8"):
        s = ln.strip()
        if s.startswith("#"):
            ativo = not re.search(r"sideboard|maybe|fora do deck|lista anterior", s, re.I)
            continue
        if s.startswith(">") or not ativo:
            continue
        m = re.match(r"^(\d+)x?\s+(.+?)\s*(\(.*)?$", s)
        if m:
            out.append(m.group(2).strip())
    return out
linhas = []
for lista in sorted(glob.glob(os.path.join(R, "*", "lista.md"))):
    deck = os.path.basename(os.path.dirname(lista))
    sims = [p for p in glob.glob(os.path.join(R, deck, "*goldfish*.py")) if "original" not in p and "/test" not in p and "physical" not in p]
    src = open(sims[0], encoding="utf-8").read() if sims else ""
    achados = []
    for n in sorted(set(cartas(lista))):
        e = C.get(n) or C.get(n.split(" // ")[0])
        if not e or "Land" not in (e.get("type_line") or ""):
            continue
        t = e.get("oracle_text") or ""
        if "Search your library" in t and "Sacrifice" in t:
            continue
        if any(re.search(p, t) for p in PAD):
            achados.append((n, src.count(n) if sims else None, t.replace("\n", " / ")[:95]))
    if achados:
        linhas.append((deck, bool(sims), achados))
print("| deck | simulador | terreno com mana restrita/condicional | aparece no simulador (n) | oraculo (trecho) |\n|---|---|---|---|---|")
tot = 0
for deck, tem, ach in linhas:
    for n, k, t in ach:
        tot += 1
        print(f"| {deck} | {'sim' if tem else 'NAO'} | {n} | {k if k is not None else '-'} | {t} |")
print(f"\n{tot} terrenos em {len(linhas)} decks; {sum(1 for d, tem, a in linhas if tem)} decks com simulador. Zero ocorrencias no simulador = terreno nao modelado pelo nome (pode estar modelado por tag ou como basico).")

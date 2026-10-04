"""Enumeracao POR SCRIPT (Regra #4, adendo 2026-09-28, item 4: nunca listar de memoria) das condicoes que decidem o valor de cada wipe de sacrificio no Vihaan, lendo `type_line`, `colors`,
`produced_mana` e `oracle_text` das 94 cartas distintas da lista (../dados/oraculo_lista_ao_vivo.json.xz, Scryfall ao vivo): (1) quem REAGE a sacrificio x a morte x a destruicao
(sacrificar dispara tudo isso; destruir nao dispara os de sacrificio); (2) grupos de tipo de criatura (Winnowing); (3) permanentes incolores (All Is Dust); (4) artefatos e encantamentos
nomeados (Scrap Mastery / Mythos / Tragic Arrogance); (5) fontes de W, B e R nos terrenos (castabilidade por cor); (6) cartas que protegem de wipe (Teferi's Protection, Boros Charm);
(7) quem entra em 'Dictate of Erebos' como mortes. Uso: python3 enumeracao_sac.py"""
import collections, json, lzma, os, re
AQUI = os.path.dirname(os.path.abspath(__file__))
C = json.load(lzma.open(os.path.join(AQUI, "..", "dados", "oraculo_lista_ao_vivo.json.xz"), "rt"))
LISTA = os.path.join(AQUI, "..", "..", "..", "resultados-ab", "_lista_legada", "lista.md")   # 12a rodada: a lista de a17049f (com Blood Money); a viva tem a Mythos
lista = []
sec = None
for l in open(LISTA):
    l = l.rstrip("\n")
    if l.startswith("#"):
        sec = l.lstrip("# ").strip().lower(); continue
    m = re.match(r"^(\d+)\s+(.+)$", l)
    if m and sec and not sec.startswith("comandante"):
        lista += [m.group(2).strip()] * int(m.group(1))
nomes = sorted(set(lista) | {"Vihaan, Goldwaker"})


def txt(n):
    c = C[n]
    t = c.get("oracle_text") or "\n".join(f.get("oracle_text", "") for f in c.get("card_faces", []))
    return t


def tl(n):
    return C[n]["type_line"]


def cores(n):
    c = C[n].get("colors")
    if not c and C[n].get("card_faces"):
        c = C[n]["card_faces"][0].get("colors")
    return c or []


terrenos = [n for n in nomes if "Land" in tl(n).split(" // ")[0]]
naoterr = [n for n in nomes if n not in terrenos]
print(f"Cartas distintas na lista (com o comandante): {len(nomes)} | terrenos: {len(terrenos)} | nao-terrenos: {len(naoterr)}")

print("\n=== (1) Quem reage a SACRIFICIO, a MORTE e a DESTRUICAO (oraculo ao vivo)")
def ctx(n, pad):
    out = []
    for frase in re.split(r"(?<=[.])\s+|\n", txt(n)):
        if re.search(pad, frase, re.I):
            out.append(frase.strip())
    return out
grupos = {
    "reage a SACRIFICIO (gatilho 'whenever you/a player/an opponent sacrifices ...')": r"whenever (you|a player|an opponent|one or more players)[^.,]*sacrifice",
    "reage a MORTE ('dies' / 'put into a graveyard from the battlefield')": r"(whenever|when)[^.]*(dies|put into a graveyard from the battlefield)",
    "reage a SAIR DO CAMPO ('leaves the battlefield')": r"(whenever|when)[^.]*leaves the battlefield",
    "tem 'destroy' no texto": r"destroy",
}
for g, pad in grupos.items():
    achados = [(n, ctx(n, pad)) for n in naoterr if ctx(n, pad)]
    print(f"\n-- {g}: {len(achados)} cartas")
    for n, fr in achados:
        print("   *", n, "|", " / ".join(fr)[:230])

print("\n=== (2) Grupos de TIPO DE CRIATURA entre as criaturas da lista (Winnowing: quem compartilha tipo com a escolhida sobrevive)")
tipos = collections.defaultdict(list)
for n in naoterr:
    t0 = tl(n).split(" // ")[0]
    if "Creature" in t0 and "—" in t0:
        for tp in t0.split("—", 1)[1].split():
            tipos[tp].append(n)
    elif "Changeling" in txt(n):
        tipos["(Changeling: todos os tipos)"].append(n)
for tp, ns in sorted(tipos.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    print(f"   {tp:28s} {len(ns):2d}: {', '.join(ns)}")
print("   Fichas: Treasure animado pelo Vihaan = Construct Assassin (Assassin e' outlaw); Construct (Jan Jansen); Dragao (Visitor, candidata fora da lista)")

print("\n=== (3) Permanentes nao-terreno INCOLORES x COLORIDOS (All Is Dust sacrifica so' os coloridos)")
incolores = [n for n in naoterr if not cores(n) and "Instant" not in tl(n) and "Sorcery" not in tl(n)]
coloridos = [n for n in naoterr if cores(n) and "Instant" not in tl(n) and "Sorcery" not in tl(n)]
print(f"   incolores ({len(incolores)}): {', '.join(incolores)}")
print(f"   coloridos ({len(coloridos)}): {len(coloridos)} permanentes (todos os demais, inclusive o Vihaan e quase todas as criaturas)")
print("   fichas: Treasure, Clue, Food, Construct = incolores; Dragao da Visitor = vermelho")

print("\n=== (4) Artefatos, encantamentos e criaturas NOMEADOS (Scrap Mastery / Mythos of Snapdax / Tragic Arrogance contam por tipo)")
art = [n for n in naoterr if "Artifact" in tl(n).split(" // ")[0]]
enc = [n for n in naoterr if "Enchantment" in tl(n).split(" // ")[0]]
cre = [n for n in naoterr if "Creature" in tl(n).split(" // ")[0]]
inst = [n for n in naoterr if re.search(r"Instant|Sorcery", tl(n).split(" // ")[0])]
print(f"   artefatos ({len(art)}): {', '.join(art)}")
print(f"   encantamentos ({len(enc)}): {', '.join(enc)}")
print(f"   criaturas ({len(cre)}): {len(cre)} cartas | instantaneas/feiticos: {len(inst)} | planeswalkers: {len([n for n in naoterr if 'Planeswalker' in tl(n)])}")
fontes_treasure = [n for n in naoterr if re.search(r"create[^.]*Treasure", txt(n), re.I)]
print(f"   cartas que CRIAM Treasure ({len(fontes_treasure)}): {', '.join(fontes_treasure)}")

print("\n=== (5) Fontes de cor nos terrenos da lista (castabilidade: {W}{W} da By Invitation Only/Mythos/Tragic/Winnowing/Slaughter; {B}{B} da Edict/Barter/Tergrid/Taste/...)")
cont = lista.count
ct = collections.Counter(lista)
for cor in "WBR":
    prod = [n for n in terrenos if cor in (C[n].get("produced_mana") or []) or any(cor in (f.get("produced_mana") or []) for f in C[n].get("card_faces", []))]
    tot = sum(ct[n] for n in prod)
    print(f"   {cor}: {tot} terrenos (copias) em {len(prod)} nomes distintos")
rocks = [n for n in naoterr if "Add" in txt(n) and "Artifact" in tl(n) and "mana" in txt(n).lower() and "Treasure" not in tl(n)]
print(f"   rocks/fontes de mana nao-terreno: {', '.join(rocks)}")
print(f"   total de terrenos na lista (copias, sem comandante): {sum(ct[n] for n in terrenos)}")

print("\n=== (6) Cartas da lista que PROTEGEM de wipe (e contra qual tipo)")
for n in ("Teferi's Protection", "Boros Charm"):
    print(f"   {n}: {txt(n).replace(chr(10), ' ')}")
print("   -> Teferi's Protection (phase out) protege contra DESTRUIR e contra SACRIFICAR (permanentes fasados nao existem); Boros Charm (indestructible) so' protege contra DESTRUIR (Blasphemous Act, Blood Money), NAO contra sacrificio.")

print("\n=== (7) Dictate of Erebos e o resto do pacote de morte")
print("   Dictate of Erebos:", txt("Dictate of Erebos").replace("\n", " "))
print("   Revel in Riches:", txt("Revel in Riches").replace("\n", " "))

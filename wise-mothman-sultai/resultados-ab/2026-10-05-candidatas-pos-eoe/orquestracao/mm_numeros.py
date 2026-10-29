"""Numeros do deck Mothman calculados por script: enumeracao de tipos/condicoes, fontes de entrada de terreno, hipergeometrica dos combos.
Uso: python3 mm_numeros.py <lista.md> <saida.txt>"""
import json, re, sys, collections
from math import comb
lista, saida = sys.argv[1], sys.argv[2]
cache = json.load(open("/home/user/MTG-Code/scryfall-cache/oracle-cache.json"))
deck = []
for l in open(lista):
    m = re.match(r"^(\d+)\s+(.+)$", l.rstrip("\n"))
    if m: deck += [m.group(2).strip()] * int(m.group(1))
deck = ["The Wise Mothman"] + [d for d in deck if d != "The Wise Mothman"]
out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s)
def tl(n): return cache[n]["type_line"] or ""
def tx(n): return cache[n]["oracle_text"] or ""
nb = [d for d in dict.fromkeys(deck) if d not in ("Forest", "Island", "Swamp")]
def with_type(rx): return [n for n in nb if re.search(rx, tl(n).split("//")[0])]
P("## Tipos de criatura/permanente (enumerado por type_line; sem changeling na lista)")
for t in ["Creature", "Insect", "Mutant", "Zombie", "Advisor", "Elf", "Horror", "Frog", "Wizard", "Elemental", "Construct", "Artifact", "Legendary", "Enchantment", "Planeswalker", "Vehicle", "Equipment"]:
    L = with_type(t if t != "Legendary" else "Legendary")
    P(f"- {t} ({len(L)}): {', '.join(L)}")
cre = [n for n in nb if "Creature" in tl(n).split("//")[0]]
P(f"\ncriaturas (face da frente): {len(cre)}; + Hedge Shredder (Veiculo, vira criatura com Crew 1)")
P("MDFC/adventure com face criatura:", [n for n in nb if "//" in n and "Creature" in tl(n).split("//")[0]])
P("\n## Fontes de 'terreno entra no campo' alem da jogada normal de terreno (suporta Evolution Sage / Ruin Crab / landfall)")
RX = r"Search your library for a (basic land|Forest|Island or Swamp|Swamp or Forest|Forest or Island)|put (it|that card|a land card from among them|any number of land cards from among them|up to two land cards) onto the battlefield|put (a|one) land card|put them onto the battlefield tapped|onto the battlefield tapped|additional land|play lands from your graveyard|put .* land card .* onto the battlefield|Search your library for a basic land card, put it onto the battlefield"
src = []
for n in nb:
    t = tx(n)
    if re.search(r"Search your library for an? (basic land|Forest|Island or Swamp|Swamp or Forest|Forest or Island|Island or Swamp) card|Search your library for a Forest card|put a creature, enchantment, or land card from among the milled cards onto the battlefield|During each of your turns, you may play a land|put any number of land cards from among them onto the battlefield|put (a|any number of|up to two) land cards? .* onto the battlefield|put it onto the battlefield tapped|You may play an additional land|play lands from your graveyard|Hedge|land cards are put into your graveyard from your library, put them onto the battlefield", t) or n in ("Kodama of the West Tree",):
        src.append(n)
P(f"({len(src)}) {', '.join(src)}")
P("\n## Hipergeometrica (Regra 7 de user-standing-rules): P(ter TODAS as pecas na mao ate o turno T), biblioteca de 99 cartas (comandante fora), 7 cartas na mao inicial + 1 compra por turno (no jogo de 4 jogadores todos compram no T1)")
N = 99
def hyp(k_needed, n_draws, K=None, pieces=None):
    pieces = pieces or k_needed
    # P(todas as `pieces` cartas distintas entre as n_draws cartas) = C(N-pieces, n-pieces)/C(N,n)
    return comb(N - pieces, n_draws - pieces) / comb(N, n_draws)
for nome, pieces in [("Bloodchief Ascension + Mindcrank (2 pecas)", 2), ("Altar of Dementia + The Great Henge + Glen Elendra Archmage (3 pecas)", 3)]:
    row = []
    for T in (6, 8, 10, 12):
        row.append(f"T{T}: {100 * hyp(pieces, 7 + T, pieces=pieces):.1f}%")
    P(f"- {nome}: " + " | ".join(row) + "  (so' compras normais; sem tutor/draw extra; Gitrog/Henge/Hollowmurk/Danny Pink etc. aumentam)")
P("(Antes de mana, de a Ascension juntar 3 marcadores de busca e de sobreviver a remocao.)")

# ---- adendo: com Master of Lake-town como segundo parceiro da Ascension (Spellbook: Bloodchief Ascension + The Master of Lake-town) ----
def p_todas(n, pecas):   # P(as `pecas` cartas distintas todas entre as n cartas vistas)
    return comb(N - pecas, n - pecas) / comb(N, n)
P("\n## Hipergeometrica com a candidata Master of Lake-town (segundo parceiro da Ascension)")
row = []
for T in (6, 8, 10, 12):
    n = 7 + T
    # P(Ascension E (Mindcrank OU Master)) = P(A,M1) + P(A,M2) - P(A,M1,M2)
    pa = 2 * p_todas(n, 2) - p_todas(n, 3)
    row.append(f"T{T}: {100 * pa:.1f}% (so' Mindcrank: {100 * p_todas(n, 2):.1f}%)")
P("- Bloodchief Ascension + (Mindcrank OU The Master of Lake-town): " + " | ".join(row))
P("\n## Risco do Kozilek num deck de auto-mill: P(Kozilek ser milado) = cartas milladas / 99 (ordem aleatoria)")
P("- " + " | ".join(f"{k} cartas milladas: {100 * k / 99:.0f}%" for k in (15, 30, 45, 60)) + "  (quando Kozilek vai pro cemiterio de qualquer lugar, ele embaralha o cemiterio inteiro na biblioteca: zera Six/Muldrotha/Icetill/Agatha)")

P("\n## Armadilhas de Bracket: combos de 2 cartas que UMA carta pos-EOE completaria (Spellbook 'quase'), probabilidade de ter a peca ja' na lista + k completares ate o turno T")
def p_a_e_algum(n, pecas_fixas, k):
    # P(todas as `pecas_fixas` E pelo menos 1 de k completares) = P(fixas) - P(fixas e nenhum dos k)
    # P(fixas E nenhum dos k) = C(N-pecas-k, n-pecas)/C(N,n)
    f = p_todas(n, pecas_fixas)
    sem = comb(N - pecas_fixas - k, n - pecas_fixas) / comb(N, n)
    return f - sem
for k in (1, 3, 5):
    row = [f"T{T}: {100 * p_a_e_algum(7 + T, 1, k):.1f}%" for T in (6, 8, 10)]
    P(f"- 2 pecas (1 ja' na lista, ex.: Basking Broodscale ou Walking Ballista, + 1 de {k} completares): " + " | ".join(row))
for k in (1, 3, 5):
    row = [f"T{T}: {100 * p_a_e_algum(7 + T, 2, k):.2f}%" for T in (6, 8, 10)]
    P(f"- 3 pecas (2 ja' na lista, ex.: Altar of Dementia + Glen Elendra, + 1 de {k} completares): " + " | ".join(row))

open(saida, "w").write("\n".join(out) + "\n")

"""Enumera por script, via oraculo do cache, quais cartas da lista satisfazem cada condicao dos motores do Mothman (Regra #4, item 4).
Uso: python3 mm_motores.py <lista.md> <saida.txt>"""
import json, re, sys, collections
lista, saida = sys.argv[1], sys.argv[2]
cache = json.load(open("/home/user/MTG-Code/scryfall-cache/oracle-cache.json"))
deck = []
for l in open(lista):
    m = re.match(r"^(\d+)\s+(.+)$", l.rstrip("\n"))
    if m: deck.append(m.group(2).strip())
deck = ["The Wise Mothman"] + [d for d in deck if d != "The Wise Mothman"]
BAS = {"Forest", "Island", "Swamp"}
deck = [d for d in deck if d not in BAS]
def T(n): return (cache[n]["oracle_text"] or "")
def TL(n): return cache[n]["type_line"] or ""
TAGS = collections.OrderedDict([
 ("MILL_OPONENTE", r"each opponent mills|target player mills|opponent mills|that player mills|each player mills|Mill three cards\b.*|mills? (that many|cards equal)"),
 ("MILL_PROPRIO", r"(^|\n|: |, |\. )(You may )?[Mm]ill (a|two|three|four|five|seven|X|\d+) cards?|mill a card|Mill (three|four|seven) cards|mills? a number of cards equal to the number of rad|you mill"),
 ("PAGA_CARTA_MILLED", r"nonland cards? (are|is) milled|creature cards? (are )?(put into|milled)|Whenever a player mills|put into an opponent's graveyard|put into a graveyard from anywhere|Hive Mind"),
 ("RAD", r"rad counter"),
 ("COLOCA_P1P1", r"\+1/\+1 counter"),
 ("DOBRA_CONTADOR", r"plus one|twice that many|that many plus"),
 ("PAGA_CONTADOR", r"Whenever (a|one or more) .*counters? (is|are) put|Whenever a counter is put|counters? are put on this creature|for the first time each turn|Evolve|Adapt|creatures with .*counter"),
 ("TERRENO_NO_CEMITERIO", r"land cards? (are )?put into your graveyard|play lands from your graveyard|land card from among|land cards? from among them|Landfall|retrace"),
 ("PROLIFERA", r"[Pp]roliferate"),
 ("COMPRA", r"[Dd]raw (a|two|three|four|that many) cards?|you may draw|draws? a card"),
 ("CONTRAMAGICA", r"Counter target"),
 ("PROTEGE", r"hexproof|indestructible|[Rr]egenerate|phase"),
 ("REMOVE", r"[Dd]estroy target|[Ee]xile target|-X/-X|gets -|deals 1 damage|to its owner's hand|Destroy all|Return each creature|All creatures get"),
 ("MANA", r"Add \{|Search your library for a (basic land|Forest)|Treasure|Eldrazi Spawn|additional land"),
 ("LEGENDARIA", r"^Legendary"),
])
tags = {n: [] for n in TAGS}
rows = {}
for n in deck:
    t = T(n); tl = TL(n)
    hit = []
    for k, rx in TAGS.items():
        src = tl if k == "LEGENDARIA" else t
        if re.search(rx, src, re.M): tags[k].append(n); hit.append(k)
    rows[n] = hit
out = []
for k, v in tags.items():
    out.append(f"## {k} ({len(v)}): {', '.join(v)}")
out.append("\n## cartas por numero de motores (sem LEGENDARIA/MANA/COMPRA genericos) — menos ligadas primeiro")
core = lambda hit: [h for h in hit if h not in ("LEGENDARIA", "MANA")]
for n, hit in sorted(rows.items(), key=lambda kv: (len(core(kv[1])), kv[0])):
    out.append(f"{len(core(hit))} | {n} | {','.join(hit)}")
open(saida, "w").write("\n".join(out) + "\n"); print("\n".join(out))

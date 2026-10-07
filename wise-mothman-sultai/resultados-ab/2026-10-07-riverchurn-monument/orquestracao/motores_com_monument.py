#!/usr/bin/env python3
"""Regra #4 (itens 2 e 4): enumera POR SCRIPT, lendo o oraculo do cache, (a) em quais motores do Mothman o Riverchurn Monument entra e (b) em quais motores cada finalista a corte entra, mais condicoes
especificas que decidem o corte (alvos da Urza's Saga, corpos pro 'up to X', permanentes recastaveis do cemiterio). Uso: python3 motores_com_monument.py > ../resumos/motores_por_script.txt"""
import json, os, re, sys, collections
AQUI = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
cache = json.load(open(os.path.join(ROOT, "scryfall-cache", "oracle-cache.json")))
sys.path.insert(0, AQUI)
import gera_config as G
BAS = {"Forest", "Island", "Swamp"}
deck = [n for n in dict.fromkeys(G.lista()) if n not in BAS]
deck = ["The Wise Mothman"] + deck
FINALISTAS = ["An Offer You Can't Refuse", "Negate", "Generous Patron", "Tear Asunder", "Toxic Deluge", "Wave Goodbye", "Muldrotha, the Gravetide", "Evolution Witness", "Didn't Say Please", "Zellix, Sanity Flayer",
              "Agatha's Soul Cauldron", "Arcane Denial", "Nuclear Fallout", "Cold-Eyed Selkie", "V.A.T.S.", "Soul-Guide Lantern", "Hedge Shredder", "Heroic Intervention", "Bojuka Bog", "Yavimaya Hollow"]
def T(n): return cache[n].get("oracle_text") or ""
def TL(n): return cache[n].get("type_line") or ""
TAGS = collections.OrderedDict([
 ("MILL_OPONENTE", r"each opponent mills|target player mills|opponent mills|that player mills|each player mills|Any number of target players each mill|mills? (that many|cards equal)"),
 ("MILL_PROPRIO", r"(^|\n|: |, |\. )(You may )?[Mm]ill (a|two|three|four|five|seven|X|\d+) cards?|mill a card|Mill (three|four|seven) cards|mills? a number of cards equal to the number of rad|you mill"),
 ("PAGA_CARTA_MILLED", r"nonland cards? (are|is) milled|creature cards? (are )?(put into|milled)|Whenever a player mills|put into an opponent's graveyard|put into a graveyard from anywhere|Hive Mind"),
 ("RAD", r"rad counter"),
 ("COLOCA_P1P1", r"\+1/\+1 counter"),
 ("DOBRA_CONTADOR", r"plus one|twice that many|that many plus"),
 ("PAGA_CONTADOR", r"Whenever (a|one or more) .*counters? (is|are) put|Whenever a counter is put|counters? are put on this creature|for the first time each turn|Evolve|Adapt|creatures with .*counter"),
 ("TERRENO_NO_CEMITERIO", r"land cards? (are )?put into your graveyard|play lands from your graveyard|land card from among|land cards? from among them|Landfall|retrace"),
 ("PROLIFERA", r"[Pp]roliferate"), ("COMPRA", r"[Dd]raw (a|two|three|four|that many) cards?|you may draw|draws? a card"),
 ("CONTRAMAGICA", r"Counter target"), ("PROTEGE", r"hexproof|indestructible|[Rr]egenerate|phase"),
 ("REMOVE", r"[Dd]estroy target|[Ee]xile target|-X/-X|gets -|deals 1 damage|to its owner's hand|Destroy all|Return each creature|All creatures get"),
])
def motores(n):
    t = T(n); return [k for k, rx in TAGS.items() if re.search(rx, t, re.M)]
out = []
M = "Riverchurn Monument"
out.append(f"## {M} ({cache[M]['mana_cost']}, {TL(M)}): motores = {motores(M)}  [oraculo: {T(M)!r}]")
out.append("   por clausula: {1},{T} 'any number of target players each mill two' -> MILL_OPONENTE (e MILL_PROPRIO se eu me escolho); Exhaust -> idem, com X = cemiterio; e e' ARTEFATO -> Urza's Saga (+1/+1 por artefato), Altar of the Brood (permanente entra), Mesmeric Orb (desvira me mila 1), recastavel por Muldrotha/Six")
out.append("\n## cartas da lista (por script) que satisfazem cada condicao que o Monument toca")
cond = collections.OrderedDict([
 ("artefatos que a Urza's Saga (cap. III) pode buscar: artefato com MV <= 1", lambda n: "Artifact" in TL(n) and cache[n].get("cmc", 9) <= 1),
 ("ARTEFATOS na lista (contam pro Construct da Saga; recastaveis por Muldrotha/Six)", lambda n: "Artifact" in TL(n)),
 ("lê 'Altar of the Brood': 'another permanent you control enters'", lambda n: re.search(r"another permanent you control enters", T(n)) is not None),
 ("lê 'Mesmeric Orb': 'a permanent becomes untapped'", lambda n: re.search(r"becomes untapped", T(n)) is not None),
 ("criaturas (corpos pro 'up to X target creatures' do Mothman)", lambda n: "Creature" in TL(n)),
 ("cartas de hate de cemiterio (ANTI-sinergia com o Exhaust, que le o tamanho do cemiterio dos oponentes)", lambda n: re.search(r"[Ee]xile (target player's|each opponent's) graveyard|[Ee]xile target card from a graveyard", T(n)) is not None),
 ("cartas que pagam por 'milled' ou por carta posta no cemiterio do oponente (sinergia direta com o mill do Monument)", lambda n: "PAGA_CARTA_MILLED" in motores(n)),
])
for k, f in cond.items():
    hit = [n for n in deck + [M] if f(n)]
    out.append(f"- {k} [{len(hit)}]: {', '.join(hit)}")
out.append("\n## motores de cada finalista a corte (Regra #4 item 4)")
core = lambda hit: [h for h in hit if h not in ("COMPRA",)]
for n in FINALISTAS:
    hit = motores(n)
    out.append(f"{len(core(hit))} | {n} | {TL(n)} | {','.join(hit) or '-'}")
print("\n".join(out))

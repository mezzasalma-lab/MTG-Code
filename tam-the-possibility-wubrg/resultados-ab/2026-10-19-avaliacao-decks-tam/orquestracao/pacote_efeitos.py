#!/usr/bin/env python3
"""Efeito ESTATICO do pacote de 6 trocas propostas (nada aplicado): custo medio dos planeswalkers (com a Tam; com a Tam + Oath of Ajani), contagem por tipo, por categoria de oraculo, e planeswalkers / tipos de planeswalker, antes e depois.
Le o cache de oraculos (Scryfall) e a lista do deck. Uso: python3 pacote_efeitos.py > ../resumos/pacote_efeitos.md"""
import json, os, re, collections
AQUI = os.path.dirname(os.path.abspath(__file__)); ARQ = os.path.abspath(os.path.join(AQUI, "..")); DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
cache = json.load(open(os.path.join(DECK, "..", "scryfall-cache", "oracle-cache.json"), encoding="utf-8"))
L = open(os.path.join(DECK, "lista.md"), encoding="utf-8").read(); antes = set(re.findall(r"^1 (.+)$", L.split("## Sideboard")[0], re.M)) - {"Tam, the Possibility"}
TROCAS = [("Leyline Immersion", "Swords to Plowshares"), ("Staff of Compleation", "Oath of Ajani"), ("Domri, Chaos Bringer", "Doubling Season"), ("Teferi's Talent", "Commodore Guff"), ("Baxter Building", "Karn's Bastion"), ("Liliana's Talent", "Mutational Advantage")]
depois = set(antes)
for a, b in TROCAS: assert a in depois and b not in depois; depois.remove(a); depois.add(b)
assert len(antes) == len(depois) == 99
def t(n): return cache[n]["type_line"].split("—")[0]
def eh_pw(n): return "Planeswalker" in t(n)
def gen(n):
    m = re.match(r"^(?:\{(\d+)\})?", cache[n].get("mana_cost") or ""); return int(m.group(1)) if m and m.group(1) else 0
def custos(S, ajani):
    pws = [n for n in S if eh_pw(n)]; tam = [int(cache[n]["cmc"]) - min(1, gen(n)) for n in pws]; com = [int(cache[n]["cmc"]) - min(2 if ajani else 1, gen(n)) for n in pws]
    return len(pws), sum(int(cache[n]["cmc"]) for n in pws) / len(pws), sum(tam) / len(pws), sum(com) / len(pws)
def tipos_pw(S): return sorted({s for n in S if eh_pw(n) for s in (cache[n]["type_line"].split("—")[1].split() if "—" in cache[n]["type_line"] else [])})
print("# Efeito estático do pacote de 6 trocas (proposta; NADA aplicado)\n")
print("| troca | sai | entra |\n|---|---|---|")
for a, b in TROCAS: print(f"| {a} → {b} | {cache[a]['mana_cost'] or '(terreno)'} · {t(a)} | {cache[b]['mana_cost'] or '(terreno)'} · {t(b)} |")
n0, m0, tam0, _ = custos(antes, False); n1, m1, tam1, aj1 = custos(depois, True); _, _, _, aj0 = custos(antes, "Oath of Ajani" in antes)
print(f"\n**Planeswalkers:** {n0} → {n1}. Custo médio de conjuração: sem desconto {m0:.2f} → {m1:.2f}; com a Tam em campo {tam0:.2f} → {tam1:.2f}; com a Tam **e o Oath of Ajani** (depois do pacote) **{aj1:.2f}**. (\"`{{1}}` a menos\" só reduz o genérico; Tam e Oath of Ajani são duas reduções que se somam, e o custo total soma os aumentos antes das reduções: ruling da Tam de 2026-08-21.)")
print(f"\n**Tipos de planeswalker distintos:** {len(tipos_pw(antes))} → {len(tipos_pw(depois))} (sai {', '.join(sorted(set(tipos_pw(antes)) - set(tipos_pw(depois)))) or 'nenhum'}; entra {', '.join(sorted(set(tipos_pw(depois)) - set(tipos_pw(antes)))) or 'nenhum'}).")
def tipos(S):
    c = collections.Counter()
    for n in S:
        for k in ("Land", "Creature", "Planeswalker", "Artifact", "Enchantment", "Instant", "Sorcery"):
            if k in t(n): c[k] += 1
    return c
a, d = tipos(antes), tipos(depois)
print("\n| tipo | antes | depois |\n|---|---|---|")
for k in ("Planeswalker", "Creature", "Instant", "Sorcery", "Artifact", "Enchantment", "Land"): print(f"| {k} | {a[k]} | {d[k]} |")
print("\nGame Changers no pacote (campo `game_changer` do Scryfall): " + (", ".join(sorted(b for _, b in TROCAS if cache[b].get("game_changer") or False)) or "nenhum") + " (verificado ao vivo em `dados/rulings_candidatas.json`, que guarda o campo).")

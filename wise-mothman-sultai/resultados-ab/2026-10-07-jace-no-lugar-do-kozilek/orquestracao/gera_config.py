#!/usr/bin/env python3
"""Gera os configs do A/B do Riverchurn Monument no Mothman (2026-10-07). Triagem: `Monument <- X` para TODA carta distinta da lista (basicos inclusos), exceto o comandante e as 6 pecas
protegidas (5 pecas dos 2 combos do Spellbook da propria lista + Kozilek, o seguro anti-decking que o usuario ja' mandou manter). Lotes de 14 variantes (+ base) por arquivo bruto.
Uso: python3 gera_config.py [--ip]   (escreve config_triagem[_ip]_K.json ao lado)"""
import json, os, re, sys, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROTEGIDAS = ["Altar of Dementia", "Bloodchief Ascension", "Glen Elendra Archmage", "Mindcrank", "The Great Henge", "Kozilek, Butcher of Truth"]
MON = "Riverchurn Monument"
DESTAQUE = ["riverchurn_tap_activations", "riverchurn_exhaust_activations", "riverchurn_exhaust_cards_opp", "riverchurn_exhaust_lethal", "cards_milled_opp_total", "nonland_milled_opp_total",
            "mothman_counters_placed_total", "opps_eliminated_total", "cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "cards_milled_self_total", "interaction_plays",
            "lands_entered_total", "library_min", "life_min"]
COMPACTO = ["riverchurn_tap_activations", "riverchurn_exhaust_activations", "cards_milled_opp_total", "nonland_milled_opp_total", "mothman_counters_placed_total", "opps_eliminated_total",
            "cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "cards_milled_self_total", "interaction_plays"]
def lista():
    nomes, sec = [], None
    for l in open(os.path.join(DECK, "lista.md"), encoding="utf-8"):
        l = l.rstrip("\n")
        if l.startswith("## "): sec = l[3:].strip(); continue
        m = re.match(r"^(\d+) (.+)$", l.strip())
        if m and sec == "Deck": nomes.append(m.group(2).strip())
    return nomes
def candidatas():
    return [n for n in dict.fromkeys(lista()) if n not in PROTEGIDAS]
def base_cfg(variantes):
    return {"sim": "mothman_goldfish_v1.py", "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": variantes, "variantes_10000": list(variantes), "regressao": []}
IN_PLACE = "--ip" in sys.argv                 # variante `no lugar`: SWAP_IN_PLACE=True (pareamento forte); sem a opcao: remove+append (triagem 1, superada em precisao)
def cut(x, **flags):
    d = {"SWAPS": [[x, MON]]}
    if IN_PLACE: d["SWAP_IN_PLACE"] = True
    d.update(flags); return d
if __name__ == "__main__":
    cs = candidatas()
    # a lista tem de bater com a biblioteca do simulador (cada corte tem de existir)
    spec = importlib.util.spec_from_file_location("mm_cfg", os.path.join(DECK, "mothman_goldfish_v1.py")); m = importlib.util.module_from_spec(spec); os.chdir(DECK); spec.loader.exec_module(m)
    for x in cs:
        m.SWAPS = ((x, MON),); lib = m.current_library(); assert lib.count(MON) == 1 and len(lib) == 99, x
    m.SWAPS = ()
    print("candidatas a corte:", len(cs), "| protegidas:", PROTEGIDAS)
    K = 6; por = -(-len(cs) // K)
    for k in range(K):
        lote = cs[k * por:(k + 1) * por]
        v = {"base": {}}
        for x in lote: v["cut_" + x] = cut(x)
        json.dump(base_cfg(v), open(os.path.join(AQUI, f"config_triagem{'_ip' if IN_PLACE else ''}_{k + 1}.json"), "w"), indent=1, ensure_ascii=False)
        print(f"lote {k + 1}: {len(lote)} variantes:", lote)
    json.dump(cs, open(os.path.join(AQUI, "candidatas.json"), "w"), indent=1, ensure_ascii=False)

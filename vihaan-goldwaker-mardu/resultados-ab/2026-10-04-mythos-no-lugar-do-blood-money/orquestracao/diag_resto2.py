"""Diagnostico (12a rodada), 2a passada: os 8 casos restantes eram todos Academy Manufactor (artefato-criatura) como o artefato escolhido ao lado do Vihaan como a criatura. Uso: python3 diag_resto2.py"""
import sys, collections
sys.path.insert(0, ".")
import fx_common as F
V = F.flags(F.carrega(F.DEPOIS, "diag2"), mythos=True, hold=False)
orig_ms = V._mass_sacrifice
casos = []
def nomeadas(s): return [n for n in s.battlefield if n not in V.LAND_NAMES and V.CARD_DB[n].ctype not in ("instant", "sorcery")]
def ms(state, sel):
    pre_nom = nomeadas(state)
    pre_tok = {"con": state.constructs, "oth": state.other_tokens, "dra": state.dragons, "anim": min(state.treasures_animated_alive, state.treasures),
               "inan": state.treasures - min(state.treasures_animated_alive, state.treasures), "clues": state.clues, "foods": state.foods}
    r = orig_ms(state, sel)
    sac = collections.Counter(sel["cre"] + sel["outros"])
    vivos = list((collections.Counter(pre_nom) - sac).elements())
    tok = {k: pre_tok[k] - sel[k] for k in pre_tok}
    cre = [n for n in vivos if V.is_creature_card(n)]
    art = [n for n in vivos if V.is_artifact_card(n)]
    enc = [n for n in vivos if V.is_enchantment_card(n)]
    ncre = len(cre) + tok["con"] + tok["oth"] + tok["dra"] + tok["anim"]
    nart = len(art) + tok["inan"] + tok["anim"] + tok["clues"] + tok["foods"] + tok["con"]
    resto = len(vivos) + sum(tok.values())
    if ncre > 1 or nart > 1 or len(enc) > 1 or resto > 3 or min(tok.values()) < 0:
        casos.append({"pre_nom": sorted(pre_nom), "pre_tok": pre_tok, "vivos": sorted(vivos), "tok": tok, "ncre": ncre, "nart": nart, "nenc": len(enc), "resto": resto})
    return r
V._mass_sacrifice = ms
for i in range(1500):
    V.simulate_one(5_000_000 + i)
print(len(casos), "violacoes")
for c in casos[:8]: print(c)

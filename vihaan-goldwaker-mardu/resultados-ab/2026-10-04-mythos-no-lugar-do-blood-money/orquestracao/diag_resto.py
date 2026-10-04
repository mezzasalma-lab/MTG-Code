"""Diagnostico (12a rodada) dos falsos positivos do invariante de sobreviventes da Mythos: ver o cabecalho de fx_regressao.py (historico). Uso: python3 diag_resto.py"""
import sys, collections
sys.path.insert(0, ".")
import fx_common as F
V = F.flags(F.carrega(F.DEPOIS, "diag"), mythos=True, hold=False)
orig_res = V.resolve_instant_sorcery
casos = []
def snap(s):
    nom = [n for n in s.battlefield if n not in V.LAND_NAMES and V.CARD_DB[n].ctype not in ("instant", "sorcery")]
    return {"nom": sorted(nom), "con": s.constructs, "oth": s.other_tokens, "dra": s.dragons, "tre": s.treasures, "ani": s.treasures_animated_alive, "clu": s.clues, "foo": s.foods}
def res(state, name):
    if name == V.MYTHOS:
        a = snap(state)
        pl0 = state.mythos_perm_lost_total
        orig_res(state, name)
        b = snap(state)
        if len(casos) < 400:
            casos.append((a, b, state.mythos_perm_lost_total - pl0))
        return
    return orig_res(state, name)
V.resolve_instant_sorcery = res
for i in range(6000):
    V.simulate_one(5_000_000 + i)
def distintas(x): return len(x["nom"]) + x["con"] + x["oth"] + x["dra"] + x["tre"] + x["clu"] + x["foo"]
ruins = []
c = collections.Counter()
for a, b, perdidas in casos:
    resto = distintas(b)
    esperado_resto = distintas(a) - perdidas
    cre = sum(1 for n in b["nom"] if V.is_creature_card(n)) + b["con"] + b["oth"] + b["dra"] + b["ani"]
    art = sum(1 for n in b["nom"] if V.is_artifact_card(n)) + b["tre"] + b["clu"] + b["foo"] + b["con"]
    enc = sum(1 for n in b["nom"] if V.is_enchantment_card(n))
    if resto != esperado_resto:
        c["contador != estado"] += 1
        c["delta_resto=%d" % (resto - esperado_resto)] += 1
        c["novos clu/foo/tre: %d/%d/%d" % (b["clu"] - 0, b["foo"], b["tre"])] += 0
        if len(ruins) < 6: ruins.append(("conta", a, b, perdidas))
    if cre > 1 or art > 1 or enc > 1:
        c["tipos>1 (c%d a%d e%d)" % (cre, art, enc)] += 1
        if len(ruins) < 12: ruins.append(("tipos", a, b, perdidas))
print(len(casos), "Mythos resolvidas;", dict(c))
for r in ruins: print(r)

"""Confere, em estados naturais com 3+ criaturas minhas, que criatura-escolhida o `r_winnowing` (politica 'Vihaan primeiro') escolhe e que fracao das minhas criaturas sobrevive. Uso: python3 winnowing_escolha.py"""
import os, sys, copy, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F, sac_harness as H
V = F.flags(F.carrega(F.DEPOIS, "vih_winn")); H.instala(V)
V.OWN_WIPE_HOLD_ALWAYS_ENABLED = False; V.OWN_WIPE_HOLD_ENGINE_ENABLED = False
ch = collections.Counter(); n = 0; sobre = []
orig = V.main_phase
def esp(s):
    global n
    if s.turn >= 3 and H.total_criaturas(H.inventario(V, s)) >= 3:
        H.FASE = "1a main"
        c = copy.deepcopy(s); c._info = {}
        H.r_winnowing(V, c)
        ch[str(c._info.get("escolhida"))] += 1; n += 1
        sobre.append(H.total_criaturas(H.inventario(V, c)) / max(1, H.total_criaturas(H.inventario(V, s))))
    return orig(s)
V.main_phase = esp
for i in range(400): V.simulate_one(3_000_000 + i)
print("estados com 3+ criaturas:", n, "| fracao media que sobrevive (meu lado):", round(sum(sobre) / len(sobre), 3))
for k, v in ch.most_common(12): print("  escolhida", k, v)

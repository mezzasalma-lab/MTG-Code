"""Condicional: só as sementes em que o Kingpin foi conjurado (8 turnos). Como a Blank Card entra NA MESMA POSIÇÃO do Kingpin (mesmo embaralhamento),
`Kingpin<-X` e `Blank<-X` são o contrafactual exato um do outro nessas sementes: a diferença mede o efeito do Kingpin contra uma carta morta, sem o viés de
'não gastar mana'. Também mostra a diferença contra a base (a carta X de volta). Uso: python3 kp_cond.py   (lê os brutos arquivados)"""
import math, statistics as st, sys
sys.path.insert(0, '.')
import kp_harness as H
from raw_io import carregar_raw
SLOTS = ["Academy Manufactor", "Monologue Tax", "Back in Town"]
def ci(a, b):
    d = [y - x for x, y in zip(a, b)]; return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d))
def col(rs, f): return [f(r) for r in rs]
M = {"win<=8 (pp)": (lambda r: 1.0 if (r["win_turn"] and r["win_turn"] <= 8) else 0.0, 100), "revel<=8 (pp)": (lambda r: 1.0 if (r["revel_turn"] and r["revel_turn"] <= 8) else 0.0, 100),
     "Treasures criados": (lambda r: float(r["treasures"]), 1), "Treasures no fim": (lambda r: float(r["treasures_end"]), 1), "dano mesa": (lambda r: float(r["table_dmg"]), 1),
     "combate": (lambda r: float(r["combat"]), 1), "dragões Magda": (lambda r: float(r["magda_dragons"]), 1)}
for pol in ("sim", "anim", "delib"):
    bruto = carregar_raw(H.DADOS + "/raw_ab_kingpin_6000_%s" % pol)
    print("\n== política %s (N=6000, 8 turnos) ==" % pol)
    print("%-20s %5s %-6s | " % ("slot", "n", "cast T") + " | ".join("%-17s" % k for k in M))
    for slot in SLOTS:
        kp = bruto["kp|%s" % slot]; bl = bruto["blank|%s" % slot]; base = bruto["base|None"]
        idx = [i for i, r in enumerate(kp) if r["kp_cast_turn"]]
        k = [kp[i] for i in idx]; b = [bl[i] for i in idx]; o = [base[i] for i in idx]
        cells = []
        for nome, (f, mult) in M.items():
            d = ci(col(b, f), col(k, f))
            cells.append("%+7.2f±%-7.2f  " % (mult * d[0], mult * d[1]))
        print("%-20s %5d %5.2f | " % (slot, len(idx), st.mean(r["kp_cast_turn"] for r in k)) + " | ".join(cells) + "   (Kingpin − Blank)")

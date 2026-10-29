"""Condicional: só as sementes em que a Pride foi conjurada (10 turnos). Diferença pareada variante - base."""
import json, math, statistics as st, sys
from raw_io import carregar_raw
d = carregar_raw("../dados/raw_ab_10t"); base = d["None|off"]
def ci(a, b):
    x = [v - u for u, v in zip(a, b)]; return st.mean(x), 1.96 * st.pstdev(x) / math.sqrt(len(x))
fin = lambda r, t: 1.0 if (r["finisher_turn"] and r["finisher_turn"] <= t) else 0.0
print("N sementes com Pride conjurada, por candidata/modo; diferença pareada na MESMA semente (variante - base), 10 turnos")
print("%-22s %-13s %5s | %-14s %-14s %-13s %-13s %-9s %-9s" % ("sai", "modo", "n", "fin<=8 (pp)", "fin<=10 (pp)", "xdraws", "spells", "ativ.", "compras Pride"))
for cut in ["Oversold Cemetery", "Deathbloom Ritualist", "Underrealm Lich", "Trystan's Command"]:
    for mode in ["off", "trample_line", "ceiling"]:
        v = d[f"{cut}|{mode}"]
        idx = [i for i, r in enumerate(v) if r["pride_cast_turn"]]
        b = [base[i] for i in idx]; x = [v[i] for i in idx]
        a8 = ci([fin(r, 8) for r in b], [fin(r, 8) for r in x]); a10 = ci([fin(r, 10) for r in b], [fin(r, 10) for r in x])
        xd = ci([r["extra_draws"] for r in b], [r["extra_draws"] for r in x]); sp = ci([r["spells_cast"] for r in b], [r["spells_cast"] for r in x])
        print("%-22s %-13s %5d | %+6.1f±%-5.1f %+6.1f±%-5.1f %+6.2f±%-5.2f %+5.2f±%-5.2f %-9.2f %-9.2f" % (
            cut[:22], mode, len(idx), 100*a8[0], 100*a8[1], 100*a10[0], 100*a10[1], xd[0], xd[1], sp[0], sp[1],
            st.mean(r["pride_activations"] for r in x), st.mean(r["pride_draws"] for r in x)))

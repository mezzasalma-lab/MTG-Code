"""Kingpin − Blank NA MESMA POSIÇÃO e nas MESMAS sementes (contrafactual exato), todas as partidas, 8 e 12 turnos: mede o efeito do Kingpin contra uma carta
morta, sem o viés de 'não gastar mana' do simulador. Uso: python3 kp_vs_blank.py (lê os brutos arquivados). A Blank não depende da política."""
import math, statistics as st, sys
sys.path.insert(0, '.')
import kp_harness as H
from raw_io import carregar_raw
SLOTS = ["Academy Manufactor", "Monologue Tax", "Back in Town"]
def ci(a, b):
    d = [y - x for x, y in zip(a, b)]; return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d))
for T in (8, 12):
    win = lambda r, T=T: 1.0 if (r["win_turn"] and r["win_turn"] <= T) else 0.0
    rev = lambda r, T=T: 1.0 if (r["revel_turn"] and r["revel_turn"] <= T) else 0.0
    blk = carregar_raw(H.DADOS + ("/raw_ab_kingpin_6000_sim" if T == 8 else "/raw_ab_kingpin_6000_delib_t12_slots_blk"))
    print("\nKingpin − Blank, mesmas sementes, N=6000, %d turnos (pp)" % T)
    print("%-20s %-9s %-16s %-16s" % ("slot", "política", "win<=%d (pp)" % T, "revel<=%d (pp)" % T))
    for pol in ("sim", "anim", "delib"):
        kp = carregar_raw(H.DADOS + ("/raw_ab_kingpin_6000_%s" % pol if T == 8 else "/raw_ab_kingpin_6000_%s_t12_slots" % pol))
        for slot in SLOTS:
            k = kp["kp|%s" % slot]; b = blk["blank|%s" % slot]
            w = ci([win(r) for r in b], [win(r) for r in k]); v = ci([rev(r) for r in b], [rev(r) for r in k])
            print("%-20s %-9s %+6.2f±%-8.2f %+6.2f±%-8.2f" % (slot, pol, 100*w[0], 100*w[1], 100*v[0], 100*v[1]))

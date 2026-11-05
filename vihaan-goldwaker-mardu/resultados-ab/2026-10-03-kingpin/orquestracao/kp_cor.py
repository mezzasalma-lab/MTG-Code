"""O {B} do Kingpin: o simulador do Vihaan não modela cor; instrumentação só-leitura nas partidas-base (`b4_turn` = 1º turno com ≥4 de mana e uma fonte de B:
terreno com B, Arcane Signet ou Treasure). Contexto: o comandante ({R}{W}{B}) foi conjurado até T3 em 85% (sem cor); a leitura de R+W+B está no lote da Inevitable Defeat.
Uso: python3 kp_cor.py (lê o bruto arquivado)"""
import statistics as st, sys
sys.path.insert(0, '.')
import kp_harness as H
from raw_io import carregar_raw
rs = carregar_raw(H.DADOS + "/raw_ab_kingpin_6000_sim")["base|None"]
print("Vihaan base N=%d: P(>=4 de mana e fonte de B) até o turno T (B_LANDS do harness + Arcane Signet + Treasure)" % len(rs))
for T in (3, 4, 5, 6, 8):
    print("<=T%d  %5.1f%%" % (T, 100 * sum(1 for r in rs if r["b4_turn"] is not None and r["b4_turn"] <= T) / len(rs)))
v = [r["b4_turn"] for r in rs if r["b4_turn"] is not None]
print("nunca até T8: %.1f%% | turno médio quando acontece: %.2f" % (100 * (1 - len(v) / len(rs)), st.mean(v)))

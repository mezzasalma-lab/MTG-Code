"""Castabilidade de cor da Inevitable Defeat no Vihaan (leitura do estado; o simulador só conta mana total):
1º turno em que R+W+B existem (leitura PESSIMISTA 'sim' = só terrenos já jogados pelo simulador; OTIMISTA 'best' = melhor subconjunto campo+mão)
e há >=4 de mana. Vihaan ({R}{W}{B}) comparado ao turno em que o comandante foi conjurado. Uso: python3 vih_cor.py [--sum]"""
import statistics as st, sys
sys.path.insert(0, '.')
import vih_harness as H
from raw_io import salvar_raw, carregar_raw
N = 10000; SEEDS = list(range(3_000_000, 3_000_000 + N))
RAW = H.DADOS + "/raw_castabilidade_cor_vihaan"
if "--sum" in sys.argv:
    rs = carregar_raw(RAW)["base"]
else:
    rs = H.run_variant(([], SEEDS, 8)); salvar_raw(RAW, {"base": rs})
def by(key, T): return sum(1 for r in rs if r[key] is not None and r[key] <= T) / len(rs)
print("Vihaan base N=%d (sem Defeat na lista; o jogo para no turno em que a condição de Revel in Riches é cumprida)" % N)
print("turno  P(R+W+B, pessimista)  P(R+W+B, otimista)  P(Vihaan conjurado)")
for T in (3, 4, 5, 6, 8):
    print("<=T%d   %5.1f%%                %5.1f%%              %5.1f%%" % (T, 100*by("rwb_turn_sim", T), 100*by("rwb_turn_best", T), 100*by("cmd_turn", T)))
for k in ("rwb_turn_sim", "rwb_turn_best"):
    v = [r[k] for r in rs if r[k] is not None]
    print("%s: nunca até T8 %.1f%% | turno médio quando acontece %.2f" % (k, 100 * (1 - len(v) / len(rs)), st.mean(v)))

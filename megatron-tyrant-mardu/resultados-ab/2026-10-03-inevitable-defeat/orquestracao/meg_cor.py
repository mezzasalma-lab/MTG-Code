"""Castabilidade de cor da Inevitable Defeat no Megatron (leitura do estado, sem alterar o jogo):
turno mínimo em que R+W+B existem em campo e há >=4 de mana (rwb_turn), vs. o turno em que o próprio Megatron ({R}{W}{B}) foi conjurado.
Uso: python3 meg_cor.py [--sum]"""
import json, statistics as st, sys
sys.path.insert(0, '.')
import meg_harness as H
from raw_io import salvar_raw, carregar_raw
N = 10000; SEEDS = range(3_000_000, 3_000_000 + N)
RAW = H.DADOS + "/raw_castabilidade_cor_megatron"
if "--sum" in sys.argv:
    rs = carregar_raw(RAW)["base"]
else:
    rs = H.run_variant(([], list(SEEDS), 8)); salvar_raw(RAW, {"base": rs})
def frac_by(key, T): return sum(1 for r in rs if r[key] is not None and r[key] <= T) / len(rs)
out = {"N": N}
for T in (3, 4, 5, 6, 8):
    out["rwb<=%d" % T] = frac_by("rwb_turn", T); out["cmd<=%d" % T] = frac_by("cmd_turn", T)
v = [r["rwb_turn"] for r in rs if r["rwb_turn"] is not None]
out["rwb_nunca_ate_T8"] = 1 - len(v) / len(rs); out["rwb_turno_medio"] = st.mean(v)
print("Megatron base N=%d (sem Defeat na lista)" % N)
print("turno  P(R+W+B em campo e >=4 mana)  P(Megatron conjurado)")
for T in (3, 4, 5, 6, 8):
    print("<=T%d   %5.1f%%                        %5.1f%%" % (T, 100*out["rwb<=%d" % T], 100*out["cmd<=%d" % T]))
print("nunca até T8: %.1f%% | turno médio quando acontece: %.2f" % (100*out["rwb_nunca_ate_T8"], out["rwb_turno_medio"]))

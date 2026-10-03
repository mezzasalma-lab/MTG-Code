"""Quanto da Inevitable Defeat chega ao Megatron: em quantas partidas ela é conjurada, em quantas o gatilho de postcombat converteu
NO MESMO TURNO (os 3 de vida viram 3 {C}), e o turno em que isso acontece. Leitura do estado, sem alterar o jogo.
Uso: python3 meg_fed.py [--sum]"""
import json, statistics as st, sys
sys.path.insert(0, '.')
import meg_harness as H
from raw_io import salvar_raw, carregar_raw
N = 20000; SEEDS = list(range(3_000_000, 3_000_000 + N))
RAW = H.DADOS + "/raw_defeat_alimenta_megatron"
if "--sum" in sys.argv:
    bruto = carregar_raw(RAW)
else:
    bruto = {sai: H.run_variant(([(sai, H.DEFEAT)], SEEDS, 8)) for sai in ("Chaos Warp", "Generous Gift")}
    salvar_raw(RAW, bruto)
out = {"N": N}
for sai, rs in bruto.items():
    cast = [r for r in rs if r["defeat_turn"]]
    fed = [r for r in rs if r["defeat_fed"] > 0]
    o = {"cast_pct": 100 * len(cast) / N, "fed_pct_jogos": 100 * len(fed) / N, "fed_pct_das_conjuradas": 100 * len(fed) / max(1, len(cast)),
         "mana_alimentada_media_por_jogo": st.mean(r["defeat_fed_mana"] for r in rs), "mana_convertida_media_por_jogo": st.mean(r["mana_convert"] for r in rs),
         "turno_medio_cast": st.mean(r["defeat_turn"] for r in cast), "cast_com_megatron_em_campo_pct": 100 * sum(r["defeat_with_megatron"] for r in rs) / N}
    dist = {}
    for r in cast: dist[r["defeat_turn"]] = dist.get(r["defeat_turn"], 0) + 1
    o["cast_por_turno"] = dict(sorted(dist.items()))
    out[sai] = o
    print("Defeat no lugar de %s (N=%d)" % (sai, N))
    for k, v in o.items(): print("   %-34s %s" % (k, ("%.2f" % v) if isinstance(v, float) else v))

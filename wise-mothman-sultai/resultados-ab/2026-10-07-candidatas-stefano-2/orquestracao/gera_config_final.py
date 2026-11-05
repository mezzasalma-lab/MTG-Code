"""Config do A/B FINAL (N=10.000, no lugar) das 6 candidatas do Stefano: cada carta <- Negate (corte comum, comparavel), as 4 com melhor segundo corte <- Didn't Say Please, as seis juntas no lugar das seis
(nao-aditividade), sensibilidades do Scorchbeast (SCORCH_MIN_X 1 e 6) e a base com o persist ANTIGO (PERSIST_ZERO_TOUGHNESS_DIES = False, mede o achado do baseline). Uso: python3 gera_config_final.py"""
import json, os
from gera_config import *
v = {"base": {}}
for k, n in CARTAS.items(): v[f"{k}__negate"] = swap(("Negate", n))
for k in ("fractured", "scorch", "tide", "branching"): v[f"{k}__didnt_say_please"] = swap(("Didn't Say Please", CARTAS[k]))
OUT6 = ["An Offer You Can't Refuse", "Negate", "Arcane Denial", "Toxic Deluge", "Cold-Eyed Selkie", "Didn't Say Please"]
v["seis_juntas_no_lugar_das_seis"] = swap(*zip(OUT6, CARTAS.values()))
v["sens_scorch_min1__negate"] = swap(("Negate", CARTAS["scorch"]), SCORCH_MIN_X=1)
v["sens_scorch_min6__negate"] = swap(("Negate", CARTAS["scorch"]), SCORCH_MIN_X=6)
v["sens_base_persist_antigo"] = {"PERSIST_ZERO_TOUGHNESS_DIES": False}
json.dump(cfg(v, v10000=list(v)), open(os.path.join(AQUI, "config_final.json"), "w"), indent=1)
print(len(v), "variantes no final")

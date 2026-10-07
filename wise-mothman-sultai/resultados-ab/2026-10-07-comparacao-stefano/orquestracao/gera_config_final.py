"""Config do A/B FINAL (N=10.000, no lugar) de Horrigan e Master: cortes escolhidos pela triagem (rank_triagem.txt) + os 5 cortes que o Monument/Jace ja' disputam + sensibilidades. Uso: python3 gera_config_final.py"""
import json, os
from gera_config import *
CORTES_F = ["An Offer You Can't Refuse", "Negate", "Arcane Denial", "Toxic Deluge", "Cold-Eyed Selkie", "Didn't Say Please", "Wave Goodbye", "Tear Asunder", "Kozilek, Butcher of Truth"]
CORTES_M = ["Tear Asunder", "An Offer You Can't Refuse", "Negate", "Wave Goodbye"]
v = {"base": {}}
for x in CORTES_F: v["frank__" + slug(x)] = swap((x, F))
for x in CORTES_M: v["master__" + slug(x)] = swap((x, M))
v["ambos__offer_frank__negate_master"] = swap(("An Offer You Can't Refuse", F), ("Negate", M))
v["ambos__offer_frank__tear_master"] = swap(("An Offer You Can't Refuse", F), ("Tear Asunder", M))
v["sens_frank_sem_proliferate__negate"] = swap(("Negate", F), HORRIGAN_PROLIF_TIMES=0)
v["sens_master_sem_criatura_de_oponente__negate"] = swap(("Negate", M), MASTER_TAKE_OPP=False)
v["sens_master_so_no_meu_turno__negate"] = swap(("Negate", M), MASTER_OPP_TURN=False)
c = cfg(v, v10000=list(v))
json.dump(c, open(os.path.join(AQUI, "config_final.json"), "w"), indent=1)
print(len(v), "variantes no final")

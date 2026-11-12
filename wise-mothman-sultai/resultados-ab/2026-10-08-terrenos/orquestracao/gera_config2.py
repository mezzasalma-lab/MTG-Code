"""2o lote do A/B da base de mana: QUANTOS terrenos. A lista atual tem 36 terrenos (35 + o MDFC Agadeem) + Sol Ring. Cada variante poe 1 (ou 2) basico(s) no lugar de uma magia de baixo custo/papel de apoio, para medir o valor de
um 37o/38o terreno E o que cada magia custa. NAO e' recomendacao de corte: o corte e' do usuario. Mesmo simulador congelado, N=10.000, `no lugar`, dois modos. Uso: python3 gera_config2.py"""
import json, os
from gera_config import SIM, DESTAQUE, COMPACTO, swap
AQUI = os.path.dirname(os.path.abspath(__file__))
LAN, BOO, HER, SEL = "Soul-Guide Lantern", "Swiftfoot Boots", "Heroic Intervention", "Cold-Eyed Selkie"
V = {"base": {},
     "l1_lantern_swamp": swap((LAN, "Swamp")),
     "l2_boots_swamp": swap((BOO, "Swamp")),
     "l3_heroic_swamp": swap((HER, "Swamp")),
     "l4_selkie_swamp": swap((SEL, "Swamp")),
     "l5_lantern_swamp_boots_forest": swap((LAN, "Swamp"), (BOO, "Forest"))}
cfg = {"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": V, "variantes_10000": list(V), "regressao": ["l5_lantern_swamp_boots_forest"]}
json.dump(cfg, open(os.path.join(AQUI, "config_terrenos2.json"), "w"), indent=1)
print(len(V), "variantes")

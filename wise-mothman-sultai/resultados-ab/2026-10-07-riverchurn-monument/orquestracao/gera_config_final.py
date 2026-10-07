#!/usr/bin/env python3
"""Config do lote FINAL do Monument (N=10.000 pareado, `no lugar`, 2 modos): os 20 finalistas da triagem 2 (ranking + papel real no deck) e as sensibilidades do PROPRIO Monument
(plataforma: corte da Negate). Uso: python3 gera_config_final.py  -> config_final.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gera_config as G
FINALISTAS = ["An Offer You Can't Refuse", "Negate", "Generous Patron", "Tear Asunder", "Toxic Deluge", "Wave Goodbye", "Muldrotha, the Gravetide", "Evolution Witness", "Didn't Say Please",
              "Zellix, Sanity Flayer", "Agatha's Soul Cauldron", "Arcane Denial", "Nuclear Fallout", "Cold-Eyed Selkie", "V.A.T.S.", "Soul-Guide Lantern", "Hedge Shredder", "Heroic Intervention",
              "Bojuka Bog", "Yavimaya Hollow"]
PLAT = "Negate"
SENS = {
    "sens_sem_ativar": {"RIVERCHURN_ACTIVATE": False},                                   # Monument so' como corpo (artefato, Altar of the Brood, Orb, Saga): isola o efeito das ativadas
    "sens_exhaust_so_letal": {"RIVERCHURN_EXHAUST_MIN": 10 ** 9},                        # Exhaust so' quando algum oponente morre
    "sens_exhaust_12": {"RIVERCHURN_EXHAUST_MIN": 12},
    "sens_exhaust_48": {"RIVERCHURN_EXHAUST_MIN": 48},
    "sens_eu_tambem": {"RIVERCHURN_SELF": True},                                         # 'any number of target players' inclui o controlador (so' com biblioteca segura)
    "sens_tap_primeiro": {"RIVERCHURN_TAP_FIRST": True},                                 # limite superior: o {1} sai antes das conjuracoes (com o comandante em campo)
    "sens_fim_do_oponente": {"RIVERCHURN_OPP_END_STEP": True},                           # linha real: mana que sobrou/segurada paga o Monument no fim do turno do oponente
    "sens_otimista": {"RIVERCHURN_TAP_FIRST": True, "RIVERCHURN_OPP_END_STEP": True, "RIVERCHURN_EXHAUST_MIN": 12},
}
if __name__ == "__main__":
    G.IN_PLACE = True
    cands = set(G.candidatas())
    assert all(x in cands for x in FINALISTAS + [PLAT]), [x for x in FINALISTAS + [PLAT] if x not in cands]
    v = {"base": {}}
    for x in FINALISTAS:
        v["cut_" + x] = G.cut(x)
    for nome, fl in SENS.items():
        v[nome + "__" + PLAT] = G.cut(PLAT, **fl)
    cfg = G.base_cfg(v)
    cfg["variantes_10000"] = list(v)
    cfg["destaque"] = G.DESTAQUE + ["riverchurn_tap_cards_opp", "riverchurn_exhaust_ascension", "riverchurn_enter_turn__ate_T4", "riverchurn_enter_turn__ate_T6"]
    json.dump(cfg, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_final.json"), "w"), indent=1, ensure_ascii=False)
    print(len(v) - 1, "variantes alem da base:", len(FINALISTAS), "cortes +", len(SENS), "sensibilidades (plataforma:", PLAT + ")")

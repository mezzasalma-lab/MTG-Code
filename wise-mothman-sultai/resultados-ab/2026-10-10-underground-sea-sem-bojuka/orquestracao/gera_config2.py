"""Lote U2 (2026-10-10): so' o candidato que faltou no lote U, Urza's Saga -> Underground Sea (u11), com a base de novo (bit-identica a do lote U: mesmas sementes). Uso: python3 gera_config2.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
c = json.load(open(os.path.join(AQUI, "config_u.json")))
V = {"base": {}, "u11_urzas_saga": {"SWAPS": [["Urza's Saga", "Underground Sea"]], "SWAP_IN_PLACE": True}}
c["variantes"] = V; c["variantes_10000"] = list(V)
json.dump(c, open(os.path.join(AQUI, "config_u2.json"), "w"), indent=1); print("ok")

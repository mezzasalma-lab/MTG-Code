#!/usr/bin/env python3
"""Ruling 2025-02-07 do Monument: 'If an ability triggers whenever you activate an exhaust ability, that ability resolves before the exhaust ability resolves.' Algum card da lista tem
gatilho de ativar habilidade/exhaust? (varredura do oraculo no cache). Resultado esperado: vazio (ruling N/A). Uso: python3 confere_gatilho_de_ativar.py > ../resumos/confere_gatilho_de_ativar.txt"""
import json, os, re, sys
A = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(A, "..", "..", "..", ".."))
sys.path.insert(0, A); import gera_config as G
c = json.load(open(os.path.join(ROOT, "scryfall-cache", "oracle-cache.json")))
nomes = list(dict.fromkeys(G.lista())) + ["The Wise Mothman"]
print(f"cartas lidas: {len(nomes)} (distintas, comandante incluido); todas com oraculo no cache: {all(n in c for n in nomes)}")
for rx in [r"exhaust", r"activate(s)? an? (exhaust|ability)", r"whenever you activate", r"whenever .* abilit(y|ies) (is|are) activated"]:
    print(f"{rx!r}: {[n for n in nomes if re.search(rx, c[n].get('oracle_text') or '', re.I)]}")

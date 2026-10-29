#!/usr/bin/env python3
"""Replicacao cruzada desta pasta (bruto de cada lote, simulador DEPOIS com os 3 duais originais + Prismatic Vista + COMMANDER_REMOVAL_SHARE):
 (1) `base` do lote terrenos3 (X) == `s4_vats_wave_dsp` de `../2026-10-08-cinco-entradas-remocao` (a MESMA lista de 2026-10-08, pelas 5 trocas no lugar, simulador SEM os terrenos novos): todos os campos numericos do antigo iguais, campos
     novos = 0.0, 10.000 partidas x 2 modos;
 (2) `base` de terrenos3 == `base` de terrenos4 (mesmas sementes, mesmo codigo, lotes rodados em momentos diferentes), 10.000 x 2 modos;
 (3) `base` de cmd50 (Y) == `base` de z50, resiliencia, 10.000 (COMMANDER_REMOVAL_SHARE=0.5 nos dois).
Uso: python3 confere_replicacao.py > ../resumos/replicacao.txt"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
ANT = os.path.join(ARQ, "..", "2026-10-08-cinco-entradas-remocao", "dados")
tot = ok = 0
def comp(novo, velho, rot, so_antigos):
    global tot, ok
    assert len(novo) == len(velho) == 10000, (rot, len(novo), len(velho))
    iguais = 0; campos_novos = set()
    for x, y in zip(novo, velho):
        extra = [c for c in x[1] if c not in y[1]]; campos_novos.update(extra)
        if all(x[1].get(c, 0.0) == v for c, v in y[1].items()) and (not so_antigos or all(x[1][c] == 0.0 for c in extra)):
            iguais += 1
    tot += 1; ok += iguais == 10000
    print(f"{rot}: {iguais}/10000 partidas identicas" + (f" (campos so' no novo: {sorted(campos_novos)}; todos 0.0)" if campos_novos else ""))
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    x3 = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_terrenos3_10000{suf}")); x4 = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_terrenos4_10000{suf}"))
    ant = A.carregar_raw(os.path.join(ANT, f"raw_cinco_10000{suf}"))
    comp(x3["base"], ant["s4_vats_wave_dsp"], f"(1) {modo:12s} base[terrenos3] == s4_vats_wave_dsp[cinco-entradas]", True)
    comp(x3["base"], x4["base"], f"(2) {modo:12s} base[terrenos3] == base[terrenos4]            ", False)
    if modo == "resiliencia":
        y = A.carregar_raw(os.path.join(ARQ, "dados", "raw_cmd50_10000_resiliencia")); z = A.carregar_raw(os.path.join(ARQ, "dados", "raw_z50_10000_resiliencia"))
        comp(y["base"], z["base"], f"(3) {modo:12s} base[cmd50] == base[z50] (comandante-alvo 0.5)  ", False)
print(f"{ok}/{tot} series bit-identicas")

#!/usr/bin/env python3
"""Replicacao cruzada: a `base` deste lote (simulador da lista atual) tem de ser IDENTICA, campo a campo, ao `s4_vats_wave_dsp` de ../2026-10-08-cinco-entradas-remocao (lista antiga + SWAPS s4 no lugar == lista atual), 10.000 x 2 modos.
Compara todos os campos numericos do bruto antigo (o fingerprint do estado inteiro e' ignorado). Uso: python3 confere_replicacao.py > ../resumos/replicacao.txt"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
OUT = os.path.join(ARQ, "..", "2026-10-08-cinco-entradas-remocao", "dados")
tot = ok = 0
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    novo = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_terrenos_10000{suf}"))["base"]; velho = A.carregar_raw(os.path.join(OUT, f"raw_cinco_10000{suf}"))["s4_vats_wave_dsp"]
    assert len(novo) == len(velho) == 10000
    iguais = sum(1 for x, y in zip(novo, velho) if all(x[1].get(c, 0.0) == v for c, v in y[1].items()) and all(x[1][c] == 0.0 or c in y[1] for c in x[1]))
    tot += 1; ok += iguais == 10000
    print(f"{modo:12s} base (aqui, lista atual) == s4 (cinco-entradas-remocao, lista antiga + s4): {iguais}/10000 partidas identicas (todos os campos numericos)")
print(f"{ok}/{tot} series bit-identicas")

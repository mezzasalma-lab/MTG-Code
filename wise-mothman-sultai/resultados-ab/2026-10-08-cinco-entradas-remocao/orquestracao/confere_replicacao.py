#!/usr/bin/env python3
"""Replicacao cruzada: a `base` e o `p1_so_o_par` (Frank + Branching <- Offer + Negate) desta pasta (simulador DEPOIS, com Atomize / Casualties / Trophy no CARD_DB) tem de ser BIT-IDENTICA a `base` e `p1_offer_negate`
de `../2026-10-08-pacote-e-interacao` (simulador de 2026-10-07, sem as tres), partida a partida (todos os campos numericos presentes no antigo; o fingerprint do estado inteiro NAO entra: ele inclui os campos novos e por isso muda em toda partida), 10.000 x 2 modos. Os campos NOVOS
(atomize_/casualties_/trophy_) so' existem aqui e valem 0 nesses dois cenarios. Uso: python3 confere_replicacao.py > ../resumos/replicacao.txt"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
OUT = os.path.join(ARQ, "..", "2026-10-08-pacote-e-interacao", "dados")
tot = ok = 0
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    novo = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_cinco_10000{suf}")); velho = A.carregar_raw(os.path.join(OUT, f"raw_pacote_10000{suf}"))
    for a, b in (("base", "base"), ("p1_so_o_par", "p1_offer_negate")):
        n, v = novo[a], velho[b]; assert len(n) == len(v) == 10000
        iguais = 0
        for x, y in zip(n, v):
            novos_campos = [c for c in x[1] if c not in y[1]]
            if all(x[1].get(c, 0.0) == val for c, val in y[1].items()) and all(x[1][c] == 0.0 for c in novos_campos):
                iguais += 1
        tot += 1; ok += iguais == 10000
        print(f"{modo:12s} {a:12s} (aqui) == {b:16s} (pacote-e-interacao): {iguais}/10000 partidas identicas (todos os campos numericos do antigo; campos novos = 0)")
print(f"{ok}/{tot} series bit-identicas")

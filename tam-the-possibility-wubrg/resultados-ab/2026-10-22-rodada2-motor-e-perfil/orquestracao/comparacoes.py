"""Comparacoes pareadas ENTRE variantes do A/B da rodada 2 (o driver so' compara cada variante com `antes`), SO' dos brutos arquivados: `tetos_altos` x `depois` (os tetos de 80 ativacoes / 60 magias por turno
mudam o resultado?) e `perfil_playtester` x `depois` (o perfil do oponente do playtester). Uso: python3 comparacoes.py"""
import os, sys, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
DEST = json.load(open(os.path.join(AQUI, "config.json")))["destaque"]
for N in (10000,):
    for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
        res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_ab_{N}{suf}"))
        for nome in ("tetos_altos", "perfil_playtester"):
            print(f"LOTE N={N}, modo {modo}")
            print(A.tabela_pareada(res["depois"], res[nome], DEST, rotulo=f"[{nome} - depois]"))
            print()

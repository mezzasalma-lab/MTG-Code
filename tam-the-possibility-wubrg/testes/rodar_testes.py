"""Roda TODOS os testes dirigidos do simulador do Tam. Uso: python3 testes/rodar_testes.py   (saida: contagem + falhas; codigo de saida != 0 se algum falhar)"""
import os, sys, importlib
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import harness
for m in ("t_terrenos_mana", "t_planeswalkers_a", "t_planeswalkers_b", "t_cartas_c", "t_motor", "t_rulings", "t_manual1", "t_manual2"):
    importlib.import_module(m)
ok, bad, fails = harness.run_all()
sys.exit(1 if bad else 0)

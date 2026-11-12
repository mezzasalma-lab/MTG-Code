"""Prova que o teste ghost do Fell Mire NAO e' vacuo: conta quantas vezes o ensaio a seco (`_fm_dry_run_mv`) executa de verdade em 3.000 partidas, na configuracao ghost
(piso 10, GHOST=True: roda e ignora) e na referencia (piso 99: nunca roda). Uso: python3 -I ghost_vacuidade.py config.json"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
cfg = json.load(open(sys.argv[1])); DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
for rot, fl in (("referencia (piso 99)", cfg["ghost_base"]), ("ghost (piso 10, GHOST=True)", dict(cfg["ghost_base"], **cfg["ghost"]))):
    M = A.carrega(os.path.join(DECK, cfg["sim"]), "gv_" + rot[:3], DECK)
    for k, v in fl.items(): setattr(M, k, v)
    n = [0]; orig = M._fm_dry_run_mv
    def spy(state, pay, _o=orig, _n=n):
        _n[0] += 1; return _o(state, pay)
    M._fm_dry_run_mv = spy
    pagou = terreno = 0
    for sd in range(5_000_000, 5_003_000):
        r = M.simulate_one(sd, turns=8); pagou += r.fell_mire_paid_total; terreno += r.fell_mire_land_plays_total
    print(f"{rot:30s} ensaios a seco executados={n[0]:5d} | Fell Mire jogado como terreno={terreno} | pagou 3 de vida={pagou}")

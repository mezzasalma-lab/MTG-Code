"""Roda os testes dirigidos do goldfish manual #6 (`testes/t_manual6.py`) e imprime UMA linha por teste (OK ou FALHOU + nome), mais a contagem.
Existe porque `verificar_reproducao.sh` comparava so' a ULTIMA linha de `rodar_testes.py` ("239 passaram..."): trocar um teste que falha por um que passa mantinha a contagem
(achado da revisao de 2026-10-29). Esta saida (`resumos/testes_manual6_lista.txt`) muda se um teste for trocado, renomeado ou passar a falhar.
Uso (a partir desta pasta): PYTHONHASHSEED=0 python3 -I lista_testes_manual6.py"""
import os, sys, importlib
AQUI = os.path.dirname(os.path.abspath(__file__))
TESTES = os.path.abspath(os.path.join(AQUI, "..", "..", "..", "testes"))
sys.path.insert(0, TESTES)
import harness
for m in ("t_terrenos_mana", "t_planeswalkers_a", "t_planeswalkers_b", "t_cartas_c", "t_motor", "t_rulings", "t_manual1", "t_manual2", "t_manual3", "t_manual4", "t_politicas", "t_manual5", "t_manual6"):
    importlib.import_module(m)

ok = bad = 0
for nome, fn in harness.TESTS:
    if not nome.startswith("Manual #6"):
        continue
    try:
        fn()
        ok += 1
        print("OK     " + nome)
    except Exception as e:                                   # Fail ou qualquer excecao
        bad += 1
        print("FALHOU " + nome + " -> " + str(e)[:200])
print(f"{ok} passaram, {bad} falharam, {ok + bad} testes 'Manual #6'")
sys.exit(1 if bad or ok == 0 else 0)                          # ok == 0 seria vacuo

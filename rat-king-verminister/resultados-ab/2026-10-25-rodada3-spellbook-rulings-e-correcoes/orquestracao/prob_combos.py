"""Regra 7 de user-standing-rules.md: antes de tratar combo do Commander Spellbook como achado de Bracket, calcular QUANDO e COM QUE PROBABILIDADE ele sai.
(1) Forma fechada: P(duas cartas especificas entre as k primeiras de um baralho de 99) = k(k-1)/(99*98); k = 7 + N na compra do T1 (sem mulligan, sem tutor).
(2) No simulador (arquivo vivo, modo padrao, N partidas, 12 turnos): P(as duas pecas ja' estiveram juntas ao alcance, em mao/campo ao fim de algum turno, ate T; ou o combo ja' foi executado) -- inclui os tutores da lista (Emeritus // Demonic Tutor, Ratcatcher,
    Karumonix, Ashcoat, Secret Salvage...) -- e P(o combo ja' foi EXECUTADO ate o turno T) (combo_*_turn do estado). Sementes 5_000_000+i.
Uso: python3 -I prob_combos.py <deck_dir> [N]"""
import os, random, sys, importlib.util
deck = os.path.abspath(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
os.chdir(deck)
spec = importlib.util.spec_from_file_location("sim", os.path.join(deck, "ratking_goldfish_v1.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
PARES = {"Marrow-Gnawer + Thornbite Staff (2178-3126)": ("Marrow-Gnawer", "Thornbite Staff", "combo_marrow_staff_turn"),
         "Ayara + Plague of Vermin (884-5035)": ("Ayara, First of Locthwain", "Plague of Vermin", "combo_ayara_plague_turn")}
TURNOS = (4, 5, 6, 7, 8, 10, 12)
print("== (1) forma fechada: P(as duas cartas entre as primeiras 7+N, deck de 99, na compra, sem tutor)")
print("   " + "  ".join(f"T{t}:{(7+t)*(6+t)/(99*98)*100:5.2f}%" for t in TURNOS))
vistas = {p: {t: 0 for t in range(1, 13)} for p in PARES}; exec_ate = {p: {t: 0 for t in range(1, 13)} for p in PARES}; qq = {t: 0 for t in range(1, 13)}
for i in range(N):
    sd = 5_000_000 + i
    rng = random.Random(sd); hand, lib, mulls = m.mulligan(rng); st = m.GameState(hand=hand, library=lib, mulligans=mulls)
    acesso = {p: False for p in PARES}                # "acumulado": uma vez com as duas pecas ao alcance, fica (a magia usada vai pro cemiterio e sumiria da conta)
    for t in range(12):
        m.play_turn(st, is_first_turn=(t == 0), on_play=True)
        zonas = set(st.hand) | set(st.battlefield)      # so' mao/campo: carta milada ou no cemiterio nao e' peca em mao (artefato no cemiterio nem volta)
        for p, (a, b, campo) in PARES.items():
            v = getattr(st, campo)
            if (a in zonas and b in zonas) or (v is not None and v <= t + 1): acesso[p] = True
            if acesso[p]: vistas[p][t + 1] += 1
            if v is not None and v <= t + 1: exec_ate[p][t + 1] += 1
        if st.combo_any_turn is not None and st.combo_any_turn <= t + 1: qq[t + 1] += 1
print(f"== (2) simulador (arquivo vivo, padrao), N={N}, 12 turnos, sementes 5_000_000+i")
for p in PARES:
    print(f"   {p}")
    print("      pecas ja' ao alcance (mao/campo, acumulado) ate T:" + "  ".join(f"T{t}:{vistas[p][t]/N*100:5.2f}%" for t in TURNOS))
    print("      combo EXECUTADO ate T:                       " + "  ".join(f"T{t}:{exec_ate[p][t]/N*100:5.2f}%" for t in TURNOS))
print("   qualquer um dos dois executado ate T:            " + "  ".join(f"T{t}:{qq[t]/N*100:5.2f}%" for t in TURNOS))

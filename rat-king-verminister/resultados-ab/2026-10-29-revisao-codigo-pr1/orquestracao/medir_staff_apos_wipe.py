"""Mede se, em partidas inteiras, o Thornbite Staff chega a estar com o holder VIRADO quando um wipe MEU resolve (apontamento 1 da revisao de codigo do PR #1, 2026-10-29).
Politica `WIPE_CAST_MAX_OWN_LOSS=None` (conjura sempre) para ter o maximo de wipes. Mede o simulador da rodada 5 (codigo/ratking_goldfish_v1_ANTES_a052820.py; SIM_ALVO=<caminho absoluto> para outro). Nao altera o simulador. Uso: PYTHONHASHSEED=0 python3 -I medir_staff_apos_wipe.py [N]"""
import os, sys, collections
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
ALVO = os.environ.get("SIM_ALVO") or os.path.abspath(os.path.join(AQUI, "..", "codigo", "ratking_goldfish_v1_ANTES_a052820.py"))   # por padrao o simulador da rodada 5 (o codigo REVISADO), nao o vivo
m = A.carrega(ALVO, "inst", DECK)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
m.WIPE_CAST_MAX_OWN_LOSS = None
c = collections.Counter()
orig = m.apply_own_wipe


def espia(state, name):
    c["wipes_meus_resolvidos"] += 1
    if "Thornbite Staff" in state.battlefield:
        c["com_Staff_em_campo"] += 1
        if state.staff_holder is not None:
            c["com_holder_equipado"] += 1
            h = state.staff_holder
            if (state.staff_tapped if h == "__mercenary__" else h in state.tapped_creatures_this_turn):
                c["holder_VIRADO_no_wipe"] += 1
                if m.wipe_plan(state, name)["loss"] > 0:
                    c["holder_virado_e_algo_morre"] += 1
    return orig(state, name)


m.apply_own_wipe = espia
for sd in range(5_000_000, 5_000_000 + N):
    m.simulate_one(sd, turns=8)
print(f"{N} partidas, politica 'conjura sempre' (limite None), 8 turnos, sementes 5_000_000+i:")
for k in ("wipes_meus_resolvidos", "com_Staff_em_campo", "com_holder_equipado", "holder_VIRADO_no_wipe", "holder_virado_e_algo_morre"):
    print(f"  {k}: {c.get(k, 0)}")

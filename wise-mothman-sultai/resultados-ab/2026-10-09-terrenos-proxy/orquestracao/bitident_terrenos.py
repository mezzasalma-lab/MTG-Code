"""Bit-identidade do patch de 2026-10-09 (Underground Sea / Bayou / Tropical Island / Prismatic Vista / COMMANDER_REMOVAL_SHARE): o simulador VIVO com `SWAPS=()` e `COMMANDER_REMOVAL_SHARE = 0.0` tem de ser identico, campo a campo,
ao snapshot `codigo/mothman_goldfish_v1_ANTES.py`, N sementes x 2 modos. Confere que ha > 0 partidas (verificacao vazia e' bug). Uso: python3 bitident_terrenos.py N [semente0]"""
import importlib.util, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(aqui, "..", "..", ".."))
def load(path, tag):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(tag, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ANTES = load(os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_ANTES.py"), "antes")
VIVO = load(os.path.join(DECK, "mothman_goldfish_v1.py"), "vivo")
VIVO.SWAPS = (); VIVO.SWAP_IN_PLACE = False; VIVO.COMMANDER_REMOVAL_SHARE = 0.0
assert list(VIVO.current_library()) == list(ANTES.current_library())
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 9_200_000
def snap(st):
    d = {k: v for k, v in vars(st).items() if isinstance(v, (int, float, bool, str, type(None)))}
    d["_bf"] = sorted(p.card.name + ":" + str(p.counters) + ":" + str(p.tapped) + ":" + str(sorted(p.ctr.items())) for p in st.battlefield)
    d["_gy"] = sorted(st.graveyard); d["_hand"] = sorted(st.hand); d["_ex"] = sorted(st.exile); d["_lib"] = list(st.library)
    d["_opp"] = [(o.life, list(o.library), list(o.graveyard), o.rad, o.eliminated, o.lands) for o in st.opps]
    d["_mill_src"] = sorted(st.opp_mill_by_source.items())
    return d
ok = bad = 0
for resil in (False, True):
    for i in range(N):
        sd = S0 + i
        a = snap((ANTES.simulate_one_with_interaction if resil else ANTES.simulate_one)(sd, 12))
        b = snap((VIVO.simulate_one_with_interaction if resil else VIVO.simulate_one)(sd, 12))
        if a != b: bad += 1; print("DIVERGE", sd, resil, [k for k in a if a[k] != b.get(k)][:5])
        else: ok += 1
print(f"vivo (SWAPS=(), COMMANDER_REMOVAL_SHARE=0) == ANTES: {ok} identicas, {bad} divergencias")
assert ok > 0
sys.exit(1 if bad else 0)

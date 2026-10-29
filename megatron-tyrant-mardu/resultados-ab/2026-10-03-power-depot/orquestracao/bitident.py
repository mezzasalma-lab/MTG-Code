"""Bit-identidade: a base do harness (sem o Power Depot na lista) tem de ser IGUAL, campo a campo do GameState, ao simulador ORIGINAL sem patch
(carregado como módulo separado). Uso: python3 bitident.py [N] [turnos]"""
import dataclasses, importlib.util, os, sys
sys.path.insert(0, '.')
import pd_harness as H
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
TURNS = int(sys.argv[2]) if len(sys.argv) > 2 else 8
spec = importlib.util.spec_from_file_location("megatron_pristine", os.path.join(H.REPO, "megatron-tyrant-mardu", "megatron_goldfish_v1.py"))
P = importlib.util.module_from_spec(spec); sys.modules["megatron_pristine"] = P; spec.loader.exec_module(P)
H.apply_swap([])
assert list(H.M.BASE_LIBRARY) == list(P.BASE_LIBRARY), "BASE_LIBRARY difere"
campos = [f.name for f in dataclasses.fields(P.GameState)]
for modo in ("core", "early", "fodder7"):
    H.POLICY["mode"] = modo
    dif = 0; det = {}
    for i in range(N):
        sd = 3_000_000 + i
        a = P.simulate_one(sd, TURNS); b = H.M.simulate_one(sd, TURNS)
        for c in campos:
            va, vb = getattr(a, c), getattr(b, c)
            if c == "rng": va, vb = va.getstate(), vb.getstate()
            if va != vb:
                dif += 1; det[c] = det.get(c, 0) + 1; break
    print(f"Megatron (PD_POLICY={modo}): {N - dif}/{N} partidas idênticas em {len(campos)} campos do GameState (original sem patch x base do harness); divergências por campo: {det or 'nenhuma'}")

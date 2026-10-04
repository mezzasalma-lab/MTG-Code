"""Bit-identidade: a base do harness (sem a Defeat na lista), nos 3 modos de cor, tem de ser IGUAL campo a campo ao simulador ORIGINAL sem patch
(módulo separado). Uso: VIH_COLOR=off|sim|best python3 bitident.py [N] [turnos]"""
import dataclasses, importlib.util, os, sys
sys.path.insert(0, '.')
import vih_harness as H
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
TURNS = int(sys.argv[2]) if len(sys.argv) > 2 else 8
spec = importlib.util.spec_from_file_location("vihaan_pristine", os.path.join(H.REPO, "vihaan-goldwaker-mardu", "vihaan_goldfish_v1.py"))
P = importlib.util.module_from_spec(spec); sys.modules["vihaan_pristine"] = P; spec.loader.exec_module(P)

# 12a rodada (Mythos no lugar do Blood Money): o arquivo vivo agora tem a Mythos na lista; aqui as chaves novas ficam desligadas, a lista volta a ter o Blood Money (bit-identico a a17049f)
# e esta pasta continua reproduzindo o simulador COMO ERA no commit dela.
if hasattr(P, "MYTHOS_REPLACES_BLOOD_MONEY_ENABLED"):
    P.MYTHOS_REPLACES_BLOOD_MONEY_ENABLED = False
    P.CASCADE_DECLINE_HELD_WIPES_ENABLED = False
    P.BASE_LIBRARY = P.build_library()
assert list(H.ORIG_LIBRARY) == list(P.BASE_LIBRARY), "BASE_LIBRARY difere"
campos = [f.name for f in dataclasses.fields(P.GameState)]
dif = 0; detalhes = {}
for i in range(N):
    sd = 3_000_000 + i
    a = P.simulate_one(sd, TURNS); b = H.V.simulate_one(sd, TURNS)
    for c in campos:
        if getattr(a, c) != getattr(b, c):
            dif += 1; detalhes[c] = detalhes.get(c, 0) + 1
            break
print(f"Vihaan (VIH_COLOR={H.COLOR_MODE}): {N - dif}/{N} partidas idênticas em {len(campos)} campos do GameState (original sem patch x base do harness); divergências por campo: {detalhes or 'nenhuma'}")

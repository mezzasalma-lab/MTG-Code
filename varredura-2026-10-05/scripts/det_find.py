import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
caminho, deck, modo, seed, turns = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
m = A.carrega(caminho, "detf", deck)
out = {}
for k in range(1, turns + 1):
    r = A.chama(m, modo, seed, k, None)
    if isinstance(r, tuple): r = r[0]
    campos = vars(r) if hasattr(r, "__dict__") else r
    out[k] = {f: hashlib.sha1(repr(A._norm(v)).encode()).hexdigest()[:8] for f, v in campos.items() if f not in A.IGNORA}
print(json.dumps(out))

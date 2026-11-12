import sys, os, json, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
caminho, deck, modo, n, turns = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
extra = tuple(json.loads(sys.argv[6])) if len(sys.argv) > 6 else None
m = A.carrega(caminho, "detg", deck)
for _k, _v in json.loads(os.environ.get("FLAGS", "{}")).items():
    setattr(m, _k, _v)
out = []
for sd in range(1_000_000, 1_000_000 + n):
    r = A.chama(m, modo, sd, turns, extra)
    if isinstance(r, tuple): r = r[0]
    campos = vars(r) if hasattr(r, "__dict__") else r
    out.append({f: hashlib.sha1(repr(A._norm(v)).encode()).hexdigest()[:8] for f, v in campos.items() if f not in A.IGNORA})
print(json.dumps(out))

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
caminho, deck, modo, seed, turns = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
m = A.carrega(caminho, "detb", deck)
out = {}
for k in range(1, turns + 1):
    r = A.chama(m, modo, seed, k, None)
    out[k] = list(r.battlefield)
print(json.dumps(out))

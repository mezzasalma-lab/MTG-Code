import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
caminho, deck, modo, n, turns = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
extra = tuple(json.loads(sys.argv[6])) if len(sys.argv) > 6 else None
m = A.carrega(caminho, "det", deck)
out = []
for sd in range(1_000_000, 1_000_000 + n):
    r = A.chama(m, modo, sd, turns, extra)
    out.append(A.impressao(r, ("commander_cast_count","tapped_land_first_plays_total","tapped_land_skipped_for_play_total")))
print(json.dumps(out))

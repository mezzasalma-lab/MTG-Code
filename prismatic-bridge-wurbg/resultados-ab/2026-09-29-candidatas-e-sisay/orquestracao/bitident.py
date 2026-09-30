import sys, importlib.util, dataclasses
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
SC = "/tmp/claude-0/-home-user-MTG-Code/6f4db589-169e-5ac7-b0c5-42b29015f83f/scratchpad/pb/"
old = load(SC + "pb_before.py", "pb_old")
new = load("/home/user/MTG-Code/prismatic-bridge-wurbg/prismatic_bridge_goldfish_v1.py", "pb_new")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
bad = 0
for i in range(N):
    a = old.simulate_one(3_000_000 + i, 10, False); b = new.simulate_one(3_000_000 + i, 10, False)
    b = {k: v for k, v in b.items() if k != "cand_stats"}
    if a != b:
        bad += 1; print("STD diff seed", 3_000_000 + i, {k: (a[k], b.get(k)) for k in a if a[k] != b.get(k)})
        if bad > 3: break
FIELDS = [f.name for f in dataclasses.fields(old.GameState) if f.name not in ("rng", "interaction_rng")]
for prof in ("mixed", "go_wide", "voltron", "low"):
    for i in range(N // 3):
        a = old.simulate_one_with_interaction(6_000_000 + i, turns=10, attack_profile=prof)
        b = new.simulate_one_with_interaction(6_000_000 + i, turns=10, attack_profile=prof)
        for f in FIELDS:
            va, vb = getattr(a, f), getattr(b, f)
            if va != vb:
                bad += 1; print("RES diff", prof, 6_000_000 + i, f, str(va)[:80], str(vb)[:80]); break
        if bad > 3: break
print("N std =", N, "| res =", 4 * (N // 3), "| divergencias:", bad)

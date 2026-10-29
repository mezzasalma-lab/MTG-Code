import json, glob, sys, math
prefix = sys.argv[1]
data = {}
for f in sorted(glob.glob(f"{prefix}_*.json")):
    data.update(json.load(open(f)))
base_file = sys.argv[2] if len(sys.argv) > 2 else None
if "base" not in data and base_file:
    for f in glob.glob(f"{base_file}_*.json"):
        d = json.load(open(f))
        if "base" in d:
            data["base"] = d["base"]
base = data["base"]
N = len(base["std"])

def paired(v, mode, key, fn=lambda x: x):
    a = [fn(g[key]) for g in base[mode]]
    b = [fn(g[key]) for g in data[v][mode]]
    d = [y - x for x, y in zip(a, b)]
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1)) if len(d) > 1 else 0
    return m, 1.96 * sd / math.sqrt(len(d))

def fmt(m, ci, pct=False, better="low"):
    sig = abs(m) > ci
    good = (m < 0) if better == "low" else (m > 0)
    mark = ("+" if good else "-") if sig else " "
    if pct:
        return f"{100*m:+6.2f}pp±{100*ci:4.2f}{mark}"
    return f"{m:+6.3f}±{ci:5.3f}{mark}"

def usage(v, mode, key):
    return sum(g.get(key, 0) for g in data[v][mode]) / N

b_fu = sum(g["first_ult"] for g in base["std"]) / N
print(f"BASE (n={N}) std: 1o ult medio {b_fu:.3f} | P(ult<=8) {100*sum(1 for g in base['std'] if g['first_ult']<=8)/N:.1f}% | "
      f"turnos c/ ult {sum(g['turns_ult'] for g in base['std'])/N:.3f}")
print(f"           res: morreu {100*sum(g['died'] for g in base['res'])/N:.1f}% | 1o ult {sum(g['first_ult'] for g in base['res'])/N:.3f} | "
      f"PW-turnos {sum(g['pw_turns_alive'] for g in base['res'])/N:.2f} | P(ult<=8) {100*sum(1 for g in base['res'] if g['first_ult']<=8)/N:.1f}%")
print()
hdr = f"{'variante':46s} | {'std 1o ult':16s} | {'std P(ult<=8)':16s} | {'std turnos c/ult':16s} | {'res morreu':16s} | {'res 1o ult':16s} | {'res PW-turnos':16s} | uso"
print(hdr)
for v in data:
    if v == "base":
        continue
    cols = [fmt(*paired(v, "std", "first_ult"), better="low"),
            fmt(*paired(v, "std", "first_ult", lambda x: 1 if x <= 8 else 0), pct=True, better="high"),
            fmt(*paired(v, "std", "turns_ult"), better="high"),
            fmt(*paired(v, "res", "died"), pct=True, better="low"),
            fmt(*paired(v, "res", "first_ult"), better="low"),
            fmt(*paired(v, "res", "pw_turns_alive"), better="high")]
    use = f"tam {usage(v,'std','tam_acts'):.2f}/{usage(v,'std','tam_saved'):.2f}mana lt {usage(v,'std','lt_bridge'):.2f}+{usage(v,'std','lt_draw'):.2f} ent {usage(v,'std','entrust'):.2f}"
    print(f"{v[:46]:46s} | " + " | ".join(cols) + " | " + use)

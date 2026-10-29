"""Sensibilidade a perfil de mesa (so' resiliencia): candidata - controle e candidata - base, pareado, por perfil.
Uso: python3 ab_perfis_sum.py "<candidata|SAI>" "<controle|SAI>" perfil=prefixo[,prefixo...] [perfil=...]
Ex.:  python3 ab_perfis_sum.py "Sisay, Weatherlight Captain|Arena Rector" "Control Body (2/2 lendaria sem texto)|Arena Rector" \
        mista=ab/main,ab/sis2 go_wide=ab/sprof2_go_wide voltron=ab/sprof2_voltron low=ab/sprof2_low
`base` vem do proprio prefixo do perfil (em `mista` vem de ab/main). Negrito = IC95% nao cruza 0."""
import glob
import json
import math
import sys

cand, ctrl = sys.argv[1], sys.argv[2]
perfis = [a.split("=") for a in sys.argv[3:]]
METRICAS = [("vida ≤ 0", "died", lambda x: x, True), ("1º ult", "first_ult", lambda x: x, False),
            ("PW-turnos vivos", "pw_turns_alive", lambda x: x, False),
            ("PWs mortos em combate", "pw_combat_deaths", lambda x: x, False),
            ("P(dano ≥ 40)", "our_dmg", lambda x: 1 if x >= 40 else 0, True)]


def carrega(prefixos):
    data = {}
    for prefix in prefixos.split(","):
        for f in sorted(glob.glob(f"{prefix}_*.json")):
            for k, v in json.load(open(f)).items():
                if k == "base" and "base" in data:
                    continue
                data[k] = v
    return data


def diff(data, v, w, key, fn):
    a = [fn(g[key]) for g in data[w]["res"]]
    b = [fn(g[key]) for g in data[v]["res"]]
    d = [y - x for x, y in zip(a, b)]
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1))
    return m, 1.96 * sd / math.sqrt(len(d))


def fmt(t, pct):
    m, ci = t
    s = f"{100 * m:+.2f} pp ±{100 * ci:.2f}" if pct else f"{m:+.3f} ±{ci:.3f}"
    return f"**{s}**" if abs(m) > ci else s


datas = [(nome, carrega(p)) for nome, p in perfis]
for titulo, ref in (("candidata − controle (o que o TEXTO faz)", ctrl), ("candidata − base (o que o SLOT faz)", "base")):
    print(f"| {titulo} | " + " | ".join(n for n, _ in datas) + " |")
    print("|---|" + "---|" * len(datas))
    for nome, key, fn, pct in METRICAS:
        cels = []
        for _, d in datas:
            cels.append(fmt(diff(d, cand, ref, key, fn), pct) if cand in d and ref in d else "—")
        print(f"| {nome} | " + " | ".join(cels) + " |")
    print()

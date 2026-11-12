"""Re-simula, com o simulador CONGELADO `codigo/mothman_goldfish_v1_ANTES.py`, as 1.000 primeiras sementes (3.000.000+i) de `base`, `u1_watery_grave`, `u3_swamp` e `u8_strip_mine` nos dois modos (config_u) e compara com o bruto
arquivado (campos numericos; o bruto guarda so' 12 chars do fingerprint e preenche com 0,0 os campos ausentes numa partida)."""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, "..")); DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
cfg = json.load(open(os.path.join(AQUI, "config_u.json"))); SIM = os.path.join(DECK, cfg["sim"])
bad = 0; n_series = 0
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    raw = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_under_10000{suf}"))
    for nome in ("base", "u1_watery_grave", "u3_swamp", "u8_strip_mine"):
        rs = A.serie_paralela(SIM, f"rs_{nome[:6]}_{modo}", DECK, cfg["variantes"][nome], modo, range(3_000_000, 3_001_000), cfg["turns"])
        iguais = sum(1 for x, y in zip(rs, raw[nome][:1000]) if x[0][:12] == y[0][:12] and set(x[1]) <= set(y[1]) and all(x[1].get(c, 0.0) == v for c, v in y[1].items()))
        print(f"{modo:12s} {nome:18s}: {iguais}/1000 identicas", flush=True); bad += iguais != 1000; n_series += 1
print(f"{n_series - bad}/{n_series} series identicas ao bruto")
sys.exit(1 if bad else 0)

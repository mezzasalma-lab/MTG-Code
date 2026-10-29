"""Re-simula base e p1_offer_negate nas 1.000 primeiras sementes (3.000.000+i) dos dois modos com o simulador congelado e compara com o bruto arquivado: fingerprint + todos os campos."""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, "..")); DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
cfg = json.load(open(os.path.join(AQUI, "config_pacote.json"))); SIM = os.path.join(DECK, cfg["sim"])
bad = 0
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    raw = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_pacote_10000{suf}"))
    for nome in ("base", "p1_offer_negate"):
        rs = A.serie_paralela(SIM, f"rs_{nome[:8]}_{modo}", DECK, cfg["variantes"][nome], modo, range(3_000_000, 3_001_000), cfg["turns"])
        iguais = sum(1 for x, y in zip(rs, raw[nome][:1000]) if x[0][:12] == y[0][:12] and set(x[1]) <= set(y[1]) and all(x[1].get(c, 0.0) == v for c, v in y[1].items()))      # o bruto guarda so' os 12 primeiros chars do fingerprint e preenche com 0.0 os campos ausentes numa partida
        print(f"{modo:12s} {nome:16s}: {iguais}/1000 identicas", flush=True); bad += iguais != 1000
sys.exit(1 if bad else 0)

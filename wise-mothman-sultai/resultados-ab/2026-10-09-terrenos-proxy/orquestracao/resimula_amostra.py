"""Re-simula, com o simulador CONGELADO `codigo/mothman_goldfish_v1_DEPOIS.py`, as 1.000 primeiras sementes (3.000.000+i) de `base` e `d1_hollow_bayou_passage_vista` nos dois modos (config_z) e, em resiliencia, as mesmas duas variantes com
COMMANDER_REMOVAL_SHARE=0.5 (config_z50), e compara com o bruto arquivado (campos numericos; o bruto guarda so' 12 chars do fingerprint e preenche com 0,0 os campos ausentes numa partida)."""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, "..")); DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
bad = 0; n_series = 0
CASOS = (("config_z.json", "raw_terrenos4_10000", "padrao", ""), ("config_z.json", "raw_terrenos4_10000", "resiliencia", "_resiliencia"), ("config_z50.json", "raw_z50_10000", "resiliencia", "_resiliencia"))
for cfgnome, rawbase, modo, suf in CASOS:
    cfg = json.load(open(os.path.join(AQUI, cfgnome))); SIM = os.path.join(DECK, cfg["sim"])
    raw = A.carregar_raw(os.path.join(ARQ, "dados", f"{rawbase}{suf}"))
    for nome in ("base", "d1_hollow_bayou_passage_vista"):
        rs = A.serie_paralela(SIM, f"rs_{cfgnome[7:-5]}_{nome[:4]}_{modo}", DECK, cfg["variantes"][nome], modo, range(3_000_000, 3_001_000), cfg["turns"])
        iguais = sum(1 for x, y in zip(rs, raw[nome][:1000]) if x[0][:12] == y[0][:12] and set(x[1]) <= set(y[1]) and all(x[1].get(c, 0.0) == v for c, v in y[1].items()))
        print(f"{cfgnome:16s} {modo:12s} {nome:30s}: {iguais}/1000 identicas", flush=True); bad += iguais != 1000; n_series += 1
print(f"{n_series - bad}/{n_series} series identicas ao bruto")
sys.exit(1 if bad else 0)

"""Bit-identidade da correcao EXOTIC_ORCHARD_PROXY (CLAUDE.md Regras #1 e #10), no desenho do Mothman/Tam/Prismatic Bridge/Bumbleflower/Ulalek:
(1) com a chave DESLIGADA o simulador vivo == o snapshot (`../codigo/`), impressao digital do resultado INTEIRO, N sementes x 2 modos;
(2) com a chave LIGADA, toda partida em que a Exotic Orchard NUNCA esteve em campo durante um calculo de cor (`color_sources`) e' IDENTICA a do snapshot; so' as que a tiveram em campo podem diferir.
Uso: PYTHONHASHSEED=0 python3 bitident_orchard.py N [semente0] [config.json]   (codigo de saida != 0 se algo diverge; confere que ha > 0 partidas em cada grupo)"""
import json, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, aqui)
import abgen as A
ARQ = os.path.abspath(os.path.join(aqui, ".."))
DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
cfg = json.load(open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(aqui, "config.json")))
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 5_000_000
IGN = tuple(cfg["ignora_campos"]); TURNS = cfg["turns"]; EXTRA = tuple(cfg["extra"]) if cfg.get("extra") is not None else None
ANTES = A.carrega(os.path.join(ARQ, cfg["snapshot"]), "orc_antes", DECK)
NOVO = A.carrega(os.path.join(DECK, cfg["sim"]), "orc_novo", DECK)
visto = {"orq": False}
_orig = NOVO.color_sources
def _vigia(state, *a, **k):
    for x in state.battlefield:
        if x == "Exotic Orchard" or getattr(x, "card", None) == "Exotic Orchard":
            visto["orq"] = True
            break
    return _orig(state, *a, **k)
NOVO.color_sources = _vigia
bad = off_ok = com_orq = igual_sem_orq = 0
for modo in ("padrao", "resiliencia"):
    for i in range(N):
        sd = S0 + i
        a = A.impressao(A.chama(ANTES, modo, sd, TURNS, EXTRA), IGN)
        for k in cfg["flags_off"]:
            setattr(NOVO, k, False)
        b = A.impressao(A.chama(NOVO, modo, sd, TURNS, EXTRA), IGN)
        if a != b:
            bad += 1; print("DIVERGE (chave desligada)", sd, modo); continue
        off_ok += 1
        for k in cfg["flags_off"]:
            setattr(NOVO, k, True)
        visto["orq"] = False
        c = A.impressao(A.chama(NOVO, modo, sd, TURNS, EXTRA), IGN)
        if visto["orq"]:
            com_orq += 1
        elif a != c:
            bad += 1; print("DIVERGE (chave ligada, sem Exotic Orchard em campo)", sd, modo)
        else:
            igual_sem_orq += 1
print(f"N = {N} x 2 modos (sementes {S0}..{S0 + N - 1}): chave DESLIGADA identica ao snapshot em {off_ok} partidas; chave LIGADA: {igual_sem_orq} sem Exotic Orchard em campo e identicas, {com_orq} com ela (podem diferir); divergencias: {bad}")
assert off_ok > 0 and igual_sem_orq > 0 and com_orq > 0, "grupo vazio: verificacao vacua"
sys.exit(1 if bad else 0)

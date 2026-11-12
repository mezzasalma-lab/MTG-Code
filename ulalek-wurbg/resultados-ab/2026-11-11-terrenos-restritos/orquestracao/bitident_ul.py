"""Bit-identidade da correcao RESTRICTED_LAND_BONUS do Ulalek (Eldrazi Temple / Shrine of the Forsaken Gods) (CLAUDE.md Regras #1 e #10), no desenho do Mothman/Tam/Prismatic Bridge:
(1) com a chave DESLIGADA o simulador vivo == o snapshot f9b8905 (`../codigo/`), impressao digital do resultado INTEIRO, N sementes x 2 modos;
(2) com a chave LIGADA, toda partida em que `restricted_land_discount` NUNCA devolveu desconto > 0 e' IDENTICA a do f9b8905; so' as que o tiveram podem diferir.
Uso: PYTHONHASHSEED=0 python3 bitident_ul.py N [semente0] [config.json]   (codigo de saida != 0 se algo diverge; confere que ha > 0 partidas em cada grupo)"""
import json, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, aqui)
import abgen as A
ARQ = os.path.abspath(os.path.join(aqui, ".."))
DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
cfg = json.load(open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(aqui, "config.json")))
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 5_000_000
IGN = tuple(cfg["ignora_campos"]); TURNS = cfg["turns"]; EXTRA = tuple(cfg["extra"]) if cfg.get("extra") is not None else None
ANTES = A.carrega(os.path.join(ARQ, cfg["snapshot"]), "ul_antes", DECK)
NOVO = A.carrega(os.path.join(DECK, cfg["sim"]), "ul_novo", DECK)
visto = {"oak": False}
_orig = NOVO.restricted_land_discount
def _vigia(state, name, cost, commit=False):
    r = _orig(state, name, cost, commit)
    if r > 0:
        visto["oak"] = True
    return r
NOVO.restricted_land_discount = _vigia
bad = off_ok = com_oak = igual_sem_oak = 0
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
        visto["oak"] = False
        c = A.impressao(A.chama(NOVO, modo, sd, TURNS, EXTRA), IGN)
        if visto["oak"]:
            com_oak += 1
        elif a != c:
            bad += 1; print("DIVERGE (chave ligada, sem desconto)", sd, modo)
        else:
            igual_sem_oak += 1
print(f"N = {N} x 2 modos (sementes {S0}..{S0 + N - 1}): chave DESLIGADA identica ao f9b8905 em {off_ok} partidas; chave LIGADA: {igual_sem_oak} sem desconto e identicas, {com_oak} com desconto (podem diferir); divergencias: {bad}")
assert off_ok > 0 and igual_sem_oak > 0 and com_oak > 0, "grupo vazio: verificacao vacua"
sys.exit(1 if bad else 0)

"""Bit-identidade das correcoes do Oakhollow Village do Bumbleflower (CLAUDE.md Regras #1 e #10), no desenho do Mothman/Tam/Prismatic Bridge:
(1) com as 2 chaves DESLIGADAS o simulador vivo == o snapshot 99fde54 (`../codigo/`), impressao digital do resultado INTEIRO, N sementes x 2 modos;
(2) com as 2 chaves LIGADAS, toda partida em que o Oakhollow Village NUNCA esteve em campo durante um calculo de mana (envolve `total_mana`) e' IDENTICA a do 99fde54; so' as que o tiveram podem diferir.
Uso: PYTHONHASHSEED=0 python3 bitident_bf.py N [semente0] [config.json]   (codigo de saida != 0 se algo diverge; confere que ha > 0 partidas em cada grupo)"""
import json, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, aqui)
import abgen as A
ARQ = os.path.abspath(os.path.join(aqui, ".."))
DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
cfg = json.load(open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(aqui, "config.json")))
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 5_000_000
IGN = tuple(cfg["ignora_campos"]); TURNS = cfg["turns"]; EXTRA = tuple(cfg["extra"]) if cfg.get("extra") is not None else None
ANTES = A.carrega(os.path.join(ARQ, cfg["snapshot"]), "bf_antes", DECK)
NOVO = A.carrega(os.path.join(DECK, cfg["sim"]), "bf_novo", DECK)
visto = {"oak": False}
_orig = NOVO.total_mana
def _vigia(state):
    if any(p.card == "Oakhollow Village" for p in state.battlefield):
        visto["oak"] = True
    return _orig(state)
NOVO.total_mana = _vigia
bad = off_ok = com_oak = igual_sem_oak = 0
for modo in ("padrao", "resiliencia"):
    for i in range(N):
        sd = S0 + i
        a = A.impressao(A.chama(ANTES, modo, sd, TURNS, EXTRA), IGN)
        for k in cfg["flags_off"]:
            setattr(NOVO, k, False)
        b = A.impressao(A.chama(NOVO, modo, sd, TURNS, EXTRA), IGN)
        if a != b:
            bad += 1; print("DIVERGE (chaves desligadas)", sd, modo); continue
        off_ok += 1
        for k in cfg["flags_off"]:
            setattr(NOVO, k, True)
        visto["oak"] = False
        c = A.impressao(A.chama(NOVO, modo, sd, TURNS, EXTRA), IGN)
        if visto["oak"]:
            com_oak += 1
        elif a != c:
            bad += 1; print("DIVERGE (chaves ligadas, sem Oakhollow em campo)", sd, modo)
        else:
            igual_sem_oak += 1
print(f"N = {N} x 2 modos (sementes {S0}..{S0 + N - 1}): chaves DESLIGADAS identicas ao 99fde54 em {off_ok} partidas; chaves LIGADAS: {igual_sem_oak} sem Oakhollow em campo e identicas, {com_oak} com Oakhollow (podem diferir); divergencias: {bad}")
assert off_ok > 0 and igual_sem_oak > 0 and com_oak > 0, "grupo vazio: verificacao vacua"
sys.exit(1 if bad else 0)

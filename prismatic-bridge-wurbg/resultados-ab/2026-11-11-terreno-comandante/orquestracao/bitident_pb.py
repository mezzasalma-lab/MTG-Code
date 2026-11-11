"""Bit-identidade da correcao COMMANDER_ENABLING_LAND do Prismatic Bridge (CLAUDE.md Regras #1 e #10), no mesmo desenho do Mothman e do Tam:
(1) com a chave DESLIGADA o simulador vivo == o snapshot 1b7dd73 (`../codigo/`), impressao digital do resultado INTEIRO (so' o campo novo `m_commander_land_overrides` ignorado), N sementes x 2 modos;
(2) com a chave LIGADA, toda partida em que o terreno NUNCA foi trocado em estado nenhum (`COMMANDER_LAND_OVERRIDES_ANYWHERE == 0`: inclui copias de ensaio a seco que rodem `play_land_phase`) e' IDENTICA a do 1b7dd73; so' as que disparam podem diferir.
Uso: PYTHONHASHSEED=0 python3 bitident_pb.py N [semente0] [config.json]   (codigo de saida != 0 se algo diverge; confere que ha > 0 partidas em cada grupo)"""
import json, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, aqui)
import abgen as A
ARQ = os.path.abspath(os.path.join(aqui, ".."))
DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
cfg = json.load(open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(aqui, "config.json")))
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 5_000_000
IGN = tuple(cfg["ignora_campos"]); TURNS = cfg["turns"]; EXTRA = tuple(cfg["extra"]) if cfg.get("extra") is not None else None
ANTES = A.carrega(os.path.join(ARQ, cfg["snapshot"]), "pb_antes", DECK)
NOVO = A.carrega(os.path.join(DECK, cfg["sim"]), "pb_novo", DECK)
bad = off_ok = disparou = igual_sem_disparo = 0
for modo in ("padrao", "resiliencia"):
    for i in range(N):
        sd = S0 + i
        a = A.impressao(A.chama(ANTES, modo, sd, TURNS, EXTRA), IGN)
        NOVO.COMMANDER_ENABLING_LAND = False
        b = A.impressao(A.chama(NOVO, modo, sd, TURNS, EXTRA), IGN)
        if a != b:
            bad += 1; print("DIVERGE (chave desligada)", sd, modo); continue
        off_ok += 1
        NOVO.COMMANDER_ENABLING_LAND = True
        NOVO.COMMANDER_LAND_OVERRIDES_ANYWHERE = 0
        c = A.impressao(A.chama(NOVO, modo, sd, TURNS, EXTRA), IGN)
        if NOVO.COMMANDER_LAND_OVERRIDES_ANYWHERE > 0:
            disparou += 1
        elif a != c:
            bad += 1; print("DIVERGE (chave ligada, sem troca)", sd, modo)
        else:
            igual_sem_disparo += 1
print(f"N = {N} x 2 modos (sementes {S0}..{S0 + N - 1}): chave DESLIGADA identica ao 1b7dd73 em {off_ok} partidas; chave LIGADA: {igual_sem_disparo} sem troca e identicas, {disparou} com troca (podem diferir); divergencias: {bad}")
assert off_ok > 0 and igual_sem_disparo > 0 and disparou > 0, "grupo vazio: verificacao vacua"
sys.exit(1 if bad else 0)

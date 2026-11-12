"""Bit-identidade da correcao PLAZA_ENABLES_COMMANDER (CLAUDE.md Regra #1 e #10):
(1) com a chave DESLIGADA o simulador vivo == o snapshot c59226f (`../codigo/`), campo a campo, N sementes x 2 modos;
(2) com a chave LIGADA, toda partida em que o terreno NUNCA foi trocado em estado nenhum (`COMMANDER_LAND_OVERRIDES_ANYWHERE == 0`: inclui as copias do ensaio a seco da guarda do landfall, que rodam `play_land_phase` com a politica nova) e' IDENTICA a do c59226f; so' as que disparam podem diferir;
(3) modo GHOST: com `state.ghost` o ensaio roda mas o resultado e' ignorado: nao ha como ligar o ghost pela API publica, entao a prova de 'ensaio sem efeito colateral' e' o item (2) (partida sem troca == identica, inclusive `next_uid` e contadores).
Uso: python3 bitident.py N [semente0]   (sai com codigo != 0 se algo diverge; confere que ha > 0 partidas em cada grupo)"""
import importlib.util, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(aqui, "..", "..", ".."))
os.chdir(DECK)
def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ANTES = load(os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_ANTES_c59226f.py"), "antes")
NOVO = load(os.path.join(DECK, "mothman_goldfish_v1.py"), "novo")
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 5_000_000
CAMPO_NOVO = {"commander_land_overrides_total"}
def snap(st):
    d = {k: v for k, v in vars(st).items() if isinstance(v, (int, float, bool, str, type(None))) and k not in CAMPO_NOVO}
    d["_bf"] = sorted(p.card.name + ":" + str(p.counters) + ":" + str(p.tapped) for p in st.battlefield)
    d["_gy"] = sorted(st.graveyard); d["_hand"] = sorted(st.hand); d["_lib"] = len(st.library)
    d["_opp"] = [(o.life, len(o.library), o.rad, o.eliminated) for o in st.opps]
    return d
def run(m, sd, resil):
    return (m.simulate_one_with_interaction if resil else m.simulate_one)(sd, 12)
bad = 0; disparou = 0; igual_sem_disparo = 0; off_ok = 0
for resil in (False, True):
    for i in range(N):
        sd = S0 + i
        a = snap(run(ANTES, sd, resil))
        NOVO.PLAZA_ENABLES_COMMANDER = False
        b = snap(run(NOVO, sd, resil))
        if a != b:
            bad += 1; print("DIVERGE (chave desligada)", sd, resil, [k for k in a if a[k] != b.get(k)][:5]); continue
        off_ok += 1
        NOVO.PLAZA_ENABLES_COMMANDER = True
        NOVO.COMMANDER_LAND_OVERRIDES_ANYWHERE = 0          # conta as trocas em QUALQUER estado, inclusive nas copias do ensaio a seco da guarda do landfall (o `commander_land_overrides_total` do estado real nao as ve)
        st = run(NOVO, sd, resil)
        c = snap(st)
        if NOVO.COMMANDER_LAND_OVERRIDES_ANYWHERE > 0:
            disparou += 1
        else:
            if a != c:
                bad += 1; print("DIVERGE (chave ligada, sem troca)", sd, resil, [k for k in a if a[k] != c.get(k)][:5])
            else:
                igual_sem_disparo += 1
print(f"N = {N} x 2 modos (sementes {S0}..{S0 + N - 1}): chave DESLIGADA identica ao c59226f em {off_ok} partidas; chave LIGADA: {igual_sem_disparo} sem troca e identicas, {disparou} com troca (podem diferir); divergencias: {bad}")
assert off_ok > 0 and igual_sem_disparo > 0 and disparou > 0, "grupo vazio: verificacao vacua"
sys.exit(1 if bad else 0)

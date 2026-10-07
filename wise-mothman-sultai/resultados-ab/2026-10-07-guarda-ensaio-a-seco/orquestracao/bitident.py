"""[2026-10-07: versao com a guarda PADRAO (ensaio a seco); a de 2026-10-06 fixa a guarda aritmetica] Bit-identidade da correcao LANDFALL_PAYOFF_FIRST (Regra #1 de CLAUDE.md): (1) com a chave DESLIGADA o simulador novo == o commit 91b1a3d, campo a campo, N sementes x 2 modos;
(2) com a chave LIGADA, toda partida em que NENHUM payoff foi conjurado antes do terreno (`payoff_first_casts == 0`) e' IDENTICA a' do 91b1a3d; so' as que disparam podem diferir.
Uso: python3 bitident.py N [semente0]   (sai com codigo != 0 se algo diverge; confere que ha > 0 partidas em cada grupo)"""
import importlib.util, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(aqui, "..", "..", ".."))
def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ANTES = load(os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_ANTES_91b1a3d.py"), "antes")
NOVO = load(os.path.join(DECK, "mothman_goldfish_v1.py"), "novo")
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 5_000_000
def snap(st):
    d = {k: v for k, v in vars(st).items() if isinstance(v, (int, float, bool, str, type(None))) and k != "payoff_first_casts"}
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
        NOVO.LANDFALL_PAYOFF_FIRST = False
        b = snap(run(NOVO, sd, resil))
        if a != b:
            bad += 1; print("DIVERGE (chave desligada)", sd, resil, [k for k in a if a[k] != b.get(k)][:5]); continue
        off_ok += 1
        NOVO.LANDFALL_PAYOFF_FIRST = True
        st = run(NOVO, sd, resil)
        c = snap(st)
        if st.payoff_first_casts > 0:
            disparou += 1
        else:
            if a != c:
                bad += 1; print("DIVERGE (chave ligada, sem disparo)", sd, resil, [k for k in a if a[k] != c.get(k)][:5])
            else:
                igual_sem_disparo += 1
print(f"N = {N} x 2 modos (sementes {S0}..{S0 + N - 1}): chave DESLIGADA identica ao 91b1a3d em {off_ok} partidas; chave LIGADA: {igual_sem_disparo} sem disparo e identicas, {disparou} com disparo (podem diferir); divergencias: {bad}")
assert off_ok > 0 and igual_sem_disparo > 0 and disparou > 0, "grupo vazio: verificacao vacua"
sys.exit(1 if bad else 0)

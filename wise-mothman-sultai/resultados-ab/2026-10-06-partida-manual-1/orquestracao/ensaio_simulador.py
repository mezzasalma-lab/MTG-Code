"""Ensaio dirigido (evidencia de APOIO, Regra #5): reconstroi no simulador o estado do INICIO de cada turno (T6..T9) a partir do log da partida manual e roda UM turno do simulador.
Mostra o que o simulador joga (terrenos da mao/cemiterio, ordem Ruin Crab x terreno, mill de oponente, contadores) para comparar com o que o usuario jogou.
Limites: biblioteca = a da lista (embaralhada por semente) com a carta comprada no log no topo; rad = 0 (o log nao registra rad); o Mothman devolvido a mao vale como zona de comando sem imposto.
Uso: python3 ensaio_simulador.py N > resumos/ensaio_simulador.txt  (N sementes por turno)"""
import collections, importlib.util, json, lzma, os, random, sys
aqui = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(aqui, "..", "..", ".."))
SIM = os.environ.get("SIM") or os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_91b1a3d.py")   # por padrao a copia FIXADA do simulador (commit 91b1a3d); SIM=<caminho> usa outra
spec = importlib.util.spec_from_file_location("mm", SIM)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
T = json.load(lzma.open(os.path.join(aqui, "..", "dados", "partida.json.xz")))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
DRAW = {6: "Overgrown Tomb", 7: "Generous Patron", 8: "Agadeem's Awakening // Agadeem, the Undercrypt", 9: "Swiftfoot Boots"}   # compra do turno, lida do log
def estado_fim(n):
    est = {}
    for t in T[:n]:
        for e in t:
            est[e["id"]] = e
    return est
def construir(n, seed):
    est = estado_fim(n - 1)
    st = m.new_state(seed)
    st.turn = n - 1
    st.hand, st.graveyard, st.battlefield, st.exile = [], [], [], []
    st.life = st.life_min = 40
    st.rad = 0
    st.commander_in_cz = True
    st.commander_cast_count = 0
    for e in est.values():
        nm, z = e["name"], e["zone"]
        if z == "hand":
            if nm == m.COMMANDER:
                continue               # o Mothman na mao = pode ser conjurado de novo sem imposto (ver cabecalho)
            st.hand.append(nm)
        elif z == "graveyard":
            st.graveyard.append(nm)
        elif z == "battlefield":
            p = m.mk_perm(st, nm)
            p.counters = sum(v["count"] for k, v in (e.get("counters") or {}).items() if k.startswith("+1"))
            p.ctr.update({"lore": v["count"] for k, v in (e.get("counters") or {}).items() if k == "Lore"})
            p.tapped = False
            p.entered_turn = st.turn - 2
            st.battlefield.append(p)
            if nm == m.COMMANDER:
                st.commander_in_cz = False
    # biblioteca = a lista menos TODAS as cartas ja' vistas em outras zonas no log (singleton: nao pode haver copia em campo e na biblioteca); a compra do turno vai ao topo
    vistas = collections.Counter(e["name"] for e in est.values())
    lib = []
    for c in m.current_library():
        if vistas[c] > 0:
            vistas[c] -= 1
            continue
        lib.append(c)
    random.Random(seed * 1009 + n).shuffle(lib)
    assert DRAW[n] in lib, DRAW[n]
    lib.remove(DRAW[n])
    st.library = [DRAW[n]] + lib
    st.library_min = len(st.library)
    return st, est
def nomes(st): return collections.Counter(p.card.name for p in st.battlefield)
print(f"# Ensaio no simulador ({os.path.basename(SIM)}), N = {N} sementes por turno\n")
AGG = {}
for n in (6, 7, 8, 9):
    cont = collections.Counter(); jogou = collections.Counter(); ordem = collections.Counter(); exemplo = None
    for sd in range(1, N + 1):
        st, est = construir(n, sd)
        l0 = st.lands_entered_total; c0 = st.ruin_crab_mills; i0 = st.icetill_replays; b0 = nomes(st)
        # ordem: o Ruin Crab entra ANTES do 1o terreno do turno?
        reg = {"crab_antes_terreno": None}
        orig_land = m.put_land_onto_battlefield
        def wrap(state, name, *a, **k):
            if reg["crab_antes_terreno"] is None:
                reg["crab_antes_terreno"] = m.has_perm(state, "Ruin Crab")
            return orig_land(state, name, *a, **k)
        m.put_land_onto_battlefield = wrap
        m.play_turn(st)
        m.put_land_onto_battlefield = orig_land
        b1 = nomes(st)
        novos = b1 - b0
        lands_new = st.lands_entered_total - l0
        cont["terrenos que entraram"] += lands_new
        cont["entradas de terreno do cemiterio (Icetill)"] += st.icetill_replays - i0
        cont["gatilhos do Ruin Crab"] += st.ruin_crab_mills - c0
        cont["cartas milladas de oponente"] += st.cards_milled_opp_total
        cont["contadores +1/+1 postos (total no campo)"] += sum(p.counters for p in st.battlefield)
        if lands_new >= 2: jogou["2+ terrenos entraram"] += 1
        if lands_new == 0: jogou["0 terreno"] += 1
        if reg["crab_antes_terreno"] is True: ordem["Ruin Crab ja' em campo quando o 1o terreno entrou"] += 1
        elif reg["crab_antes_terreno"] is False: ordem["1o terreno entrou SEM Ruin Crab em campo"] += 1
        if sd == 1:
            exemplo = (sorted(novos.elements()), lands_new, st.ruin_crab_mills - c0)
    print(f"## T{n} (compra do log: {DRAW[n]})")
    print(f"- O usuario jogou no T{n}: " + {6: "1 terreno (Overgrown Tomb); Ruin Crab (retrace) e Memory Erosion", 7: "0 terrenos da mao/cemiterio; Patron, Wave Goodbye, Hardened Scales (retrace)", 8: "1 terreno (Urza's Saga do cemiterio) DEPOIS de Ruin Crab, Mothman e Icetill", 9: "0 terrenos ate o fim do log; Six e Kami"}[n])
    print(f"- Simulador (media por partida, N = {N}): " + "; ".join(f"{k} {v / N:.2f}" for k, v in cont.items()))
    print(f"- Simulador: " + "; ".join(f"{k} em {100 * v / N:.0f}%" for k, v in {**jogou, **ordem}.items()))
    print(f"- Exemplo (semente 1): entraram {exemplo[0]}; terrenos que entraram: {exemplo[1]}; gatilhos do Crab: {exemplo[2]}\n")

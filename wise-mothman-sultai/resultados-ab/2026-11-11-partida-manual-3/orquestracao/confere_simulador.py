"""Conferencia do simulador do Mothman com as clausulas operacionais da partida manual #3 (Regra #6: cada clausula do relato do usuario e' uma afirmacao testavel sobre o simulador).
(1) cada resolucao do Altar of the Brood (os 3 oponentes milam JUNTOS) vale UM gatilho do Mothman e +1 no Mothman (ruling 2024-03-08), nao 3;
(2) um gatilho com X = 3 poe 1 contador em CADA um de 3 alvos (nunca 3 no mesmo);
(3) Evolution Witness devolve so' carta PERMANENTE (nunca Instant);
(4) retrace da Six exige um terreno na MAO e nunca recai em terreno nem em Instant;
(5) o mill do rad (CR 728.1) no inicio da fase principal 1 tira 1 carta por contador e remove 1 rad por carta nao-terreno;
(6) a linha legal do T4 da partida: com Tropical Island, Breeding Pool e Forest em campo e Plaza of Heroes (+ Springs, Forest, Saga) na mao, o simulador deve jogar a Plaza e conjurar o Mothman ({B} so' sai da Plaza, que da' qualquer cor para magia lendaria).
Uso: python3 -I confere_simulador.py [caminho do simulador]   (padrao: a copia ARQUIVADA ANTES da correcao da Plaza, em ../codigo/). Sai com 1 se algum teste falhar."""
import glob, importlib.util, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
SIM = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_ANTES_plaza_*.py")))[0]
spec = importlib.util.spec_from_file_location("mm", SIM); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def fresh(bf=(), hand=(), turn=4, cz=False):
    st = m.new_state(1); st.turn = turn; st.hand = list(hand); st.graveyard = []; st.battlefield = []; st.exile = []; st.rad = 0
    st.library = ["Sol Ring"] * 40; st.library_min = 40; st.commander_in_cz = cz
    for o in st.opps:
        o.library = ["N", "C", "L"] * 30
    def add(n, c=0, tapped=False):
        p = m.mk_perm(st, n); p.counters = c; p.tapped = tapped; p.entered_turn = st.turn - 2; st.battlefield.append(p); return p
    for n in bf:
        add(n)
    st.add = add
    return st
res = []
def teste(rot, ok, detalhe):
    res.append(bool(ok)); print(f"{'PASSA' if ok else 'FALHA'} | {rot} | {detalhe}")
print("simulador:", os.path.basename(SIM))
# (1) Altar: 1 gatilho por resolucao
st = fresh(bf=["Altar of the Brood"]); mo = st.add(m.COMMANDER, 0)
t0, c0 = st.mothman_triggers_total, mo.counters
m.put_land_onto_battlefield(st, "Forest", source="play")
teste("(1) Altar: um terreno entra com 3 oponentes", (st.mothman_triggers_total - t0, mo.counters - c0) == (1, 1), f"gatilhos do Mothman +{st.mothman_triggers_total - t0}, contadores no Mothman +{mo.counters - c0} (regra: 1 e 1)")
# (2) X = 3, tres alvos
st = fresh(); mo = st.add(m.COMMANDER, 0); six = st.add("Six", 0); wit = st.add("Evolution Witness", 0)
m.mothman_trigger(st, 3)
teste("(2) gatilho X=3 com Mothman, Six e Witness", (mo.counters, six.counters, wit.counters) == (1, 1, 1), f"contadores {(mo.counters, six.counters, wit.counters)} (regra: 1 em cada alvo)")
# (3) Witness so' devolve permanente
st = fresh(); st.graveyard = ["Didn't Say Please", "An Offer You Can't Refuse", "Gyre Sage"]
m.evolution_witness_return(st); m.evolution_witness_return(st)
teste("(3) Witness com 2 Instants e 1 criatura no cemiterio, 2 gatilhos", st.hand == ["Gyre Sage"] and sorted(st.graveyard) == ["An Offer You Can't Refuse", "Didn't Say Please"], f"mao {st.hand}, cemiterio {st.graveyard}")
# (4) retrace
st = fresh(bf=["Six"], hand=["Memory Erosion"]); st.graveyard = ["Gyre Sage", "Rejuvenating Springs", "Didn't Say Please"]
sem = m.graveyard_cast_options(st)
st.hand = ["Forest"]
com = m.graveyard_cast_options(st)
teste("(4) retrace da Six", sem == [] and [x[0] for x in com] == ["Gyre Sage"], f"sem terreno na mao {sem}; com Forest na mao {com}")
# (5) rad
st = fresh(); st.rad = 1; st.library = ["Sol Ring"] * 10
m.rad_trigger_self(st)
teste("(5) rad 1 no inicio da fase principal 1", len(st.library) == 9 and st.rad == 0, f"biblioteca {len(st.library)}, rad {st.rad} (1 carta nao-terreno milada remove 1 rad)")
# (6) linha legal do T4
st = fresh(bf=["Tropical Island", "Breeding Pool", "Forest", "Altar of the Brood"], hand=["Plaza of Heroes", "Forest", "Urza's Saga", "Didn't Say Please", "An Offer You Can't Refuse", "Rejuvenating Springs"], cz=True)
st.lands_played_this_turn = 0
m.play_land_phase(st)
plaza = any(p.card.name == "Plaza of Heroes" for p in st.battlefield)
cast = m.cast_commander(st)
campo = [p.card.name for p in st.battlefield if p.card.name == m.COMMANDER]
teste("(6) T4 do log: Plaza + Springs + Forest na mao, Mothman no comando", plaza and cast and campo == [m.COMMANDER], f"Plaza em campo: {plaza}; cast_commander: {cast}; Mothman em campo: {bool(campo)}; terreno jogado: {[p.card.name for p in st.battlefield if 'land' in p.card.types][-1]}")
print(f"\n{sum(res)}/{len(res)} conferencias passam")
sys.exit(0 if all(res) else 1)

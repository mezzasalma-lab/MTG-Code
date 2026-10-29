"""Teste dirigido (Regra #6: cada clausula operacional da partida e' uma afirmacao testavel sobre o simulador): o simulador acerta o que o log da partida #2 errou?
(1) Gyre Sage da' 1 G por CONTADOR (0 contadores = 0 mana); (2) The Great Henge custa {7}{G}{G} menos o maior poder (Mothman 3 + 1 contador = 4 -> 5); (3) com Kami e Constrictor em campo uma
colocacao de 1 contador vira 3; (4) o Constrictor soma 1 aos rad counters que EU recebo (ETB/ataque do Mothman dao 2); (5) o gatilho de combate do Ouroboroid poe X = poder dele em CADA criatura,
ficha inclusive, com as duas substituicoes (X = 5 -> +7 por criatura, como no T6 com o estado que o log mostrava). Uso: python3 confere_simulador.py [caminho do simulador]"""
import importlib.util, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
SIM = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, "..", "..", "..", "mothman_goldfish_v1.py")
spec = importlib.util.spec_from_file_location("mm", SIM); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def fresh(bf=(), hand=(), turn=5):
    st = m.new_state(1); st.turn = turn; st.hand = list(hand); st.graveyard = []; st.battlefield = []; st.exile = []; st.rad = 0
    st.library = ["Forest"] * 40; st.library_min = 40; st.commander_in_cz = False
    for o in st.opps:
        o.library = ["N", "C", "L"] * 30
    def add(n, c=0, tapped=False):
        p = m.mk_perm(st, n); p.counters = c; p.tapped = tapped; p.entered_turn = st.turn - 2; st.battlefield.append(p); return p
    for n in bf:
        add(n)
    st.add = add
    return st
ok = 0
# (1) Gyre Sage
st = fresh(); g = st.add("Gyre Sage"); st.add("Island")
base = m.available_mana(st)
g.counters = 1
um = m.available_mana(st)
print(f"(1) mana disponivel: Island + Gyre Sage sem contador = {base}; com 1 contador = {um}"); assert (base, um) == (1, 2); ok += 1
# (2) Henge
st = fresh(); mo = st.add(m.COMMANDER, 1); st.hand = ["The Great Henge"]
g_, pips = m.effective_cost(st, "The Great Henge")
print(f"(2) Henge com o Mothman 3/3 + 1 contador (poder {m.power(st, mo)}): generico {g_} + {len(pips)} coloridos = {g_ + len(pips)}"); assert g_ + len(pips) == 5; ok += 1
# (3) Kami + Constrictor
st = fresh(bf=["Kami of Whispered Hopes", "Winding Constrictor", "Basking Broodscale"]); b = [p for p in st.battlefield if p.card.name == "Basking Broodscale"][0]
tot = m.place_counters(st, b, 1)
print(f"(3) 1 contador em criatura com Kami + Constrictor em campo -> {tot}"); assert tot == 3; ok += 1
# (4) rad com Constrictor
st = fresh(bf=["Winding Constrictor"]); st.rad = 0
m.give_rad(st, 0, 1)
print(f"(4) rad recebido com o Constrictor em campo (ETB/ataque do Mothman = 1) -> {st.rad}"); assert st.rad == 2; ok += 1
# (5) Ouroboroid no estado do T6 do log: Ouroboroid 4, Mothman 4, Gyre 3, Broodscale 1, Constrictor 1, Kami 2, 1 ficha Spawn
st = fresh(bf=[]); 
est = {}
for n, c in (("Ouroboroid", 4), (m.COMMANDER, 4), ("Gyre Sage", 3), ("Basking Broodscale", 1), ("Winding Constrictor", 1), ("Kami of Whispered Hopes", 2)):
    est[n] = st.add(n, c)
spawn = m.mk_perm(st, "Eldrazi Spawn Token", is_token=True); spawn.entered_turn = st.turn - 2; st.battlefield.append(spawn)
before = {n: p.counters for n, p in est.items()}; sb = spawn.counters
m.beginning_of_combat(st)
dif = {n: est[n].counters - before[n] for n in est}
print(f"(5) gatilho de combate do Ouroboroid (poder {1 + 4}): contadores por criatura {dif}; ficha Spawn +{spawn.counters - sb}")
assert all(v == 7 for v in dif.values()) and spawn.counters - sb == 7; ok += 1
print(f"\n{ok}/5 conferencias do simulador batem com as regras (o log da partida #2 errou o que o simulador acerta).")

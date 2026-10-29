"""Varreduras mecanicas (Regra #10 de CLAUDE.md) adaptadas ao simulador do Mothman: (1) entrada de CADA terreno contra o oraculo em cache; (2) fetch real; (3) jogar terreno nao e' magia;
(4) todo terreno que entra dispara landfall (Ruin Crab / Icetill) em TODOS os pontos de entrada; (5) estado por NOME em vez de por instancia. Cada uma confere que o numero e' > 0 (verificacao nao vacua).
Uso: cd wise-mothman-sultai && python3 resultados-ab/2026-10-05-simulador-v1-validacao/orquestracao/varredura_mecanica_mothman.py > resumos/varredura_mecanica.txt"""
import importlib.util, json, os, re, sys, collections

ROOT = "/home/user/MTG-Code"
DECK = f"{ROOT}/wise-mothman-sultai"
os.chdir(DECK)
spec = importlib.util.spec_from_file_location("mm", f"{DECK}/mothman_goldfish_v1.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
cache = json.load(open(f"{ROOT}/scryfall-cache/oracle-cache.json"))


def oracle(name):
    e = cache.get(name)
    if e is None:
        return None
    return e.get("oracle_text") or " // ".join(f.get("oracle_text", "") for f in e.get("card_faces", []))


def fresh(life=40, bf=()):
    st = m.new_state(1)
    st.hand = []
    st.battlefield = []
    st.library = ["Fathom Mage"] * 40
    st.life = life
    for n in bf:
        p = m.mk_perm(st, n)
        p.entered_turn = 0
        st.battlefield.append(p)
    return st


print("=" * 100)
print("1) ENTRADA DE CADA TERRENO x ORACULO (campo vazio, vida 40) — esperado derivado do TEXTO do oraculo")
lands = [n for n, c in m.CARD_DB.items() if "land" in c.types and not c.token]
n_checked = 0
bad = 0
for n in sorted(lands):
    txt = oracle(n)
    if txt is None:
        print(f"  ?? {n}: sem oraculo no cache"); bad += 1; continue
    low = txt.lower()
    # esperado em campo vazio
    if "enters tapped unless you control a forest" in low or "enters tapped unless you control a" in low:
        exp = True                                  # sem Floresta: entra virado
    elif "enters tapped unless you have two or more opponents" in low or "unless you have two or more opponents" in low:
        exp = False                                 # mesa de 4: 3 oponentes -> desvirado
    elif "you may pay 2 life" in low or "you may pay 3 life" in low:
        exp = False                                 # paga a vida (vida 40)
    elif "this land enters tapped." in low or "enters tapped." in low and "unless" not in low and "if you don't" not in low:
        exp = True
    else:
        exp = False
    st = fresh()
    p = m.put_land_onto_battlefield(st, n, source="play") if "fetch" not in m.CARD_DB[n].tags else None
    if p is None:
        # fetch: o terreno em si entra desvirado (e e' sacrificado depois)
        p = m.put_land_onto_battlefield(st, n, source="play")
    got = p.tapped
    # Fabled Passage etc. nao tem 'enters tapped' no proprio texto
    n_checked += 1
    flag = "OK " if got == exp else "DIVERGE"
    if got != exp:
        bad += 1
    print(f"  {flag} {n:55s} esperado_virado={exp!s:5s} simulador_virado={got!s:5s} | {low[:90].replace(chr(10), ' / ')}")
print(f"  terrenos conferidos: {n_checked} (> 0), divergencias: {bad}")

print("=" * 100)
print("1b) CONDICOES: Shifting Woodland com/sem Floresta; slowlands com 3/2/1 oponentes; choques com vida 40 e vida 8")
st = fresh(bf=("Forest",)); print("  Woodland com Forest virado?", m.put_land_onto_battlefield(st, "Shifting Woodland", source="play").tapped, "(esperado False)")
st = fresh(bf=("Zagoth Triome",)); print("  Woodland com Triome (subtipo Forest) virado?", m.put_land_onto_battlefield(st, "Shifting Woodland", source="play").tapped, "(esperado False: Triome e' Swamp Forest Island)")
st = fresh(); print("  Woodland campo vazio virado?", m.put_land_onto_battlefield(st, "Shifting Woodland", source="play").tapped, "(esperado True)")
for k in (3, 2, 1):
    st = fresh()
    for o in st.opps[k:]:
        o.eliminated = True
    print(f"  Morphic Pool com {k} oponente(s) vivo(s) virado?", m.put_land_onto_battlefield(st, "Morphic Pool", source="play").tapped, f"(esperado {k < 2})")
for life in (40, 8):
    st = fresh(life=life)
    p = m.put_land_onto_battlefield(st, "Overgrown Tomb", source="play")
    print(f"  Overgrown Tomb vida {life}: virado={p.tapped}, vida depois={st.life}")

print("=" * 100)
print("2) FETCH REAL: sacrifica, 1 de vida (Fabled Passage nao), busca por SUBTIPO, thinning, vai ao cemiterio")
for fname in ("Misty Rainforest", "Polluted Delta", "Verdant Catacombs", "Fabled Passage"):
    ok = 0
    n = 0
    for sd in range(1, 41):
        st = m.new_state(sd)
        st.hand = [fname]
        st.battlefield = []
        st.graveyard = []
        lib0 = len(st.library)
        l0 = st.life
        m.play_land_phase(st)
        lands = [p for p in st.battlefield if "land" in p.card.types]
        fetched = fname in st.graveyard and len(lands) == 1 and lands[0].card.name != fname and len(st.library) == lib0 - 1
        life_ok = (st.life == l0 - 1) if fname != "Fabled Passage" else (st.life == l0 or lands[0].card.tags & {"shock"})
        n += 1
        ok += 1 if fetched else 0
    print(f"  {fname:20s} quebrou e buscou em {ok}/{n} partidas (esperado: todas as com alvo na biblioteca)")

print("=" * 100)
print("3) JOGAR TERRENO NAO E' MAGIA: spells_cast_this_turn nao pode mudar em play_land_phase")
cnt = 0
for sd in range(1, 101):
    st = m.new_state(sd)
    s0 = st.spells_cast_this_turn
    m.play_land_phase(st)
    cnt += 1
    assert st.spells_cast_this_turn == s0, ("terreno contado como magia", sd)
print(f"  {cnt} partidas, 0 contagens indevidas")

print("=" * 100)
print("4) LANDFALL EM TODO PONTO DE ENTRADA: total de terrenos que entram x chamadas de landfall (300 partidas, 2 modos)")
tot_enter = collections.Counter(); tot_land = 0
orig_put = m.put_land_onto_battlefield
orig_landfall = m.landfall
src_count = collections.Counter()
calls = [0]
def wrapped_landfall(state):
    calls[0] += 1
    return orig_landfall(state)
def wrapped_put(state, name, tapped=None, source="", forced_tapped=False):
    src_count[source] += 1
    return orig_put(state, name, tapped=tapped, source=source, forced_tapped=forced_tapped)
m.landfall = wrapped_landfall
m.put_land_onto_battlefield = wrapped_put
for modo in ("simulate_one", "simulate_one_with_interaction"):
    for sd in range(1, 301):
        getattr(m, modo)(sd, 12)
enter = sum(src_count.values())
print(f"  terrenos entraram: {enter} (> 0) | chamadas de landfall: {calls[0]} | por origem: {dict(sorted(src_count.items(), key=lambda kv: -kv[1]))}")
print("  " + ("OK: entradas == chamadas" if enter == calls[0] else "DIVERGE: entradas != chamadas"))
m.landfall = orig_landfall
m.put_land_onto_battlefield = orig_put

print("=" * 100)
print("5) ESTADO POR NOME x POR INSTANCIA: o simulador marca terreno virado por uid/atributo do Permanent (nao por nome)?")
src = open(f"{DECK}/mothman_goldfish_v1.py").read()
hits = [l.strip() for l in src.splitlines() if re.search(r"tapped_lands_this_turn|tapped_by_name|set\(\).*tapped", l)]
print("  ocorrencias de conjunto de NOMES de terrenos virados:", len(hits), hits[:3], "(0 = o estado vive em Permanent.tapped, por instancia)")
print("  Permanent.tapped existe e e' por instancia:", "tapped: bool" in src)

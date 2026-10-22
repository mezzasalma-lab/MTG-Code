"""audit_tam_terrenos.py (2026-10-22) — as varreduras de terreno da Regra #10 PARA O SIMULADOR DO TAM (os scripts audit_entrada/audit_fetch/audit_terreno_nao_e_magia/audit_landfall tem a lista de decks fixa e
usam `total_mana`/`play_land`, que o Tam nao tem: aqui o ponto de entrada e' `play_land_phase`/`put_land_onto_battlefield`). Quatro varreduras, todas EM RUNTIME contra o oraculo em cache:
 (1) ENTRADA: cada um dos terrenos da lista, T1, 40 de vida, 3 oponentes vivos: entra virado/desvirado como o oraculo manda? (o oraculo de cada terreno que cita 'tapped' e' impresso ao lado do resultado; a conclusao e' lida a mao)
 (2) FETCH: cada fetch e' sacrificada, paga 1 de vida, busca de verdade e o CONJUNTO de alvos do simulador == o conjunto de terrenos da lista cujo `type_line` tem o subtipo (calculado do oraculo, nao de memoria)
 (3) TERRENO NAO E' MAGIA: jogar um terreno comum nao muda nenhum contador de magia conjurada
 (4) LANDFALL: nenhuma carta da lista tem gatilho de 'land enters'/'play a land'/landfall (varredura por regex no oraculo; o simulador declara N/A em `land_enters`)
Uso: python3 audit_tam_terrenos.py [ROOT]"""
import sys, os, re, json, random
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(os.path.join(AQUI, "..", ".."))
DECK = os.path.join(ROOT, "tam-the-possibility-wubrg")
M = A.carrega(os.path.join(DECK, "tam_goldfish_v1.py"), "tamaudit", DECK)
OC = json.load(open(os.path.join(ROOT, "scryfall-cache", "oracle-cache.json")))
FALHAS = []


def estado(hand=(), turn=1, life=40):
    st = M.GameState(rng=random.Random(3))
    st.proxy_rng = random.Random(4); st.interaction_rng = random.Random(5)
    st.opps = [M.make_opp(3, i) for i in range(1, 4)]
    st.opp_rngs = [None] + [random.Random(100 + i) for i in range(1, 4)]
    st.turn = turn; st.turn_id = turn * 4; st.life = life; st.phase = "main1"
    st.hand = list(hand)
    st.library = [c for c in M.current_library() if c not in hand]
    st.commander_in_cz = True
    return st


def oraculo(n):
    return (OC.get(n) or OC.get(n.split(" // ")[0]) or {}).get("oracle_text") or ""


print("== (1) ENTRADA: terreno x oraculo (T1, 40 de vida, 3 oponentes, campo vazio)")
lands = sorted(M.LANDS)
for n in lands:
    st = estado([n])
    M.TAPPED_LAND_FIRST_ENABLED = False
    M.play_land_phase(st)
    p = next((q for q in st.battlefield if q.card.name == n), None)
    orc = oraculo(n)
    tap_lines = [l.strip() for l in orc.split("\n") if "tapped" in l.lower()]
    k = M.LANDS[n]["kind"]
    estado_sim = "NAO ENTROU (fetch sacrificada)" if p is None else ("virado" if p.tapped else "desvirado") + (f", vida {st.life}" if st.life != 40 else "")
    print(f"  {n:28s} [{k:9s}] sim: {estado_sim:34s} oraculo: {' | '.join(tap_lines) or '(nada sobre entrar virado)'}")
print("   (lido a mao: triomes virados; choques 'pay 2 life' -> desvirado com 38; lentos 'two or more opponents' -> desvirado com 3 oponentes; Starting Town 'first, second or third turn' -> desvirado no T1; os demais desvirados)")

print("\n== (2) FETCH: sacrificada + 1 de vida + busca real + conjunto de alvos == subtipos do oraculo")
deck_lands = [n for n in lands]
for n in lands:
    if M.LANDS[n]["kind"] != "fetch":
        continue
    orc = oraculo(n)
    m = re.search(r"Search your library for an? (.+?) card", orc)
    tipos = [t for t in re.findall(r"\b(Plains|Island|Swamp|Mountain|Forest)\b", m.group(1))] if m else []
    esperado = sorted(c for c in deck_lands if c != n and any(t in (OC.get(c, {}).get("type_line", "")) for t in tipos) and c in M.CARD_DB)
    st = estado([n])
    life0 = st.life; lib0 = len(st.library)
    M.TAPPED_LAND_FIRST_ENABLED = False
    M.play_land_phase(st)
    bf = [q.card.name for q in st.battlefield]
    alvo = [c for c in bf if c != n]
    st2 = estado([n]); p2 = M.mk_perm(st2, n); st2.battlefield.append(p2)
    sim_alvos = sorted(M.fetch_targets(st2, p2))
    ok = (n not in bf and n in st.graveyard and st.life == life0 - 1 and len(st.library) == lib0 - 1 and len(alvo) == 1 and sim_alvos == esperado)
    if not ok:
        FALHAS.append(("fetch", n))
    print(f"  {n:20s} tipos {tipos}: em campo={n in bf} cemiterio={n in st.graveyard} vida {life0}->{st.life} biblioteca {lib0}->{len(st.library)} buscou={alvo}\n      alvos do simulador == subtipos do oraculo? {sim_alvos == esperado} ({len(esperado)} terrenos){'' if sim_alvos == esperado else ' DIFERENCA: so sim ' + str(sorted(set(sim_alvos) - set(esperado))) + ' so oraculo ' + str(sorted(set(esperado) - set(sim_alvos)))}  -> {'OK' if ok else 'DIVERGE'}")

print("\n== (3) TERRENO NAO E' MAGIA: contadores de magia antes/depois de jogar um terreno comum")
for n in ("Command Tower", "City of Brass", "Plaza of Heroes"):
    st = estado([n])
    antes = {k: getattr(st, k) for k in ("spells_cast_this_turn", "noncreature_spells_this_turn")}
    antes_m = (st.m["spells_cast_total"], st.m["noncreature_spells_total"], dict(st.spells_this_turn_by_player), dict(st.casts_by_card))
    M.play_land_phase(st)
    depois = {k: getattr(st, k) for k in antes}
    depois_m = (st.m["spells_cast_total"], st.m["noncreature_spells_total"], dict(st.spells_this_turn_by_player), dict(st.casts_by_card))
    ok = antes == depois and antes_m == depois_m
    if not ok:
        FALHAS.append(("magia", n))
    print(f"  {n:20s} contadores iguais: {ok}  ({antes} -> {depois})")

print("\n== (4) LANDFALL: cartas da lista com gatilho de entrada/jogada de terreno (oraculo)")
rx = re.compile(r"(?<!this )(?<!that )land enters|landfall|whenever you play a land|whenever a land|whenever one or more lands|play a land from", re.I)   # 'this land enters tapped' e' o PROPRIO terreno (secao 1), nao gatilho
achou = []
for n in sorted(M.CARD_DB):
    if n.endswith("Token") or n in ("Jace Token",):
        continue
    orc = oraculo(n)
    if rx.search(orc):
        achou.append(n)
        print(f"  {n}: {orc[:140]!r}")
print(f"  total de cartas com gatilho de terreno: {len(achou)} (o simulador declara N/A em `land_enters`; `audit_landfall_ordem.py` fica sem candidato)" if not achou else f"  total: {len(achou)} -> CONFERIR se o simulador trata (land_enters)")
extra = [n for n in sorted(M.CARD_DB) if re.search(r"additional land", oraculo(n), re.I)]
print(f"  cartas que mudam as jogadas de terreno por turno ('additional land'): {extra} -> tratadas por `extra_land_drops` -> `land_drops_available` (teste dirigido: tam-the-possibility-wubrg/testes/t_manual1.py, "Manual #1 T7")")
print("\nFALHAS:", FALHAS or "nenhuma")

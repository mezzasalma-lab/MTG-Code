"""Mede o apontamento 2 da revisao de codigo do PR #1 (2026-10-29): "TAPPED_FIRST_COUNTS_MANA decide por `mana_spent_this_turn`, que conta mana gasto em QUALQUER habilidade
(extort, ativacoes), nao so' em desenvolvimento". Em cada decisao do ensaio a seco do terreno virado (terreno virado E desvirado na mao, turno <= TAPPED_LAND_FIRST_MAX_TURN),
calcula para os dois terrenos: (a) mana gasto, (b) MV que sai da mao, (c) o comandante foi conjurado no ensaio. Compara a decisao pela metrica ATUAL (mana) com a decisao por
"desenvolvimento" (MV que sai da mao + custo do comandante, sem sorvedouros de mana) e conta quantas partidas e quantas decisoes divergem. Mede o simulador da rodada 5 (codigo/ratking_goldfish_v1_ANTES_a052820.py; SIM_ALVO=<caminho absoluto> para outro). Nao altera o simulador.
Uso: python3 medir_vies_ensaio.py N [semente_base]   (padrao: N=3000, semente 1_000_000; PYTHONHASHSEED=0)"""
import os, sys, copy, random, collections, json
os.environ.setdefault("PYTHONHASHSEED", "0")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
ALVO = os.environ.get("SIM_ALVO") or os.path.abspath(os.path.join(AQUI, "..", "codigo", "ratking_goldfish_v1_ANTES_a052820.py"))   # por padrao o simulador da rodada 5 (o codigo REVISADO), nao o vivo
m = A.carrega(ALVO, "vies", DECK)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
BASE = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
orig = m.tapped_first_pick
dec = []          # (semente, turno, mana_t, mana_u, dev_t, dev_u, escolha_mana, escolha_dev)


def ensaio(state, land):
    memo = {id(c): c for c in m.CARD_DB.values()}
    saved = random.getstate()
    sim = copy.deepcopy(state, memo)
    ficam = collections.Counter(sim.hand); ficam[land] -= 1
    cast0 = sim.commander_cast_count
    m._TL_FORCED, m._TL_BUSY = land, True
    try:
        m.play_land(sim); m._tl_develop(sim, None)
    finally:
        m._TL_FORCED, m._TL_BUSY = None, False
        random.setstate(saved)
    saiu = ficam - collections.Counter(sim.hand)
    mv_mao = sum(m.CARD_DB[c].mv for c in saiu.elements() if c in m.CARD_DB)
    cmd = m.CARD_DB[m.COMMANDER].mv if sim.commander_cast_count > cast0 else 0
    return sim.mana_spent_this_turn, mv_mao + cmd


SEED = [None]


def espia(state, lands_in_hand):
    if (m._TL_FORCED is None and m.TAPPED_LAND_FIRST_ENABLED and not m._TL_BUSY and state.turn <= m.TAPPED_LAND_FIRST_MAX_TURN):
        tapped = [n for n in lands_in_hand if m._tl_is_tapped(state, n)]
        untapped = [n for n in lands_in_hand if not m._tl_is_tapped(state, n)]
        if tapped and untapped:
            mt, dt = ensaio(state, tapped[0]); mu, du = ensaio(state, untapped[0])
            dec.append((SEED[0], state.turn, mt, mu, dt, du, "virado" if mt >= mu else "desvirado", "virado" if dt >= du else "desvirado"))
    return orig(state, lands_in_hand)


m.tapped_first_pick = espia
for i in range(N):
    SEED[0] = BASE + i
    m.simulate_one(BASE + i, turns=3)
jogos = {d[0] for d in dec}
div = [d for d in dec if d[6] != d[7]]
print(f"partidas={N} | decisoes com virado E desvirado na mao (T<={m.TAPPED_LAND_FIRST_MAX_TURN})={len(dec)} em {len(jogos)} partidas")
print(f"decisoes em que 'mana gasto' e 'desenvolvimento (MV da mao + comandante)' escolhem DIFERENTE: {len(div)} ({100*len(div)/max(1,len(dec)):.1f}% das decisoes) em {len({d[0] for d in div})} partidas ({100*len({d[0] for d in div})/N:.2f}% das partidas)")
for t in sorted({d[1] for d in dec}):
    dt = [d for d in dec if d[1] == t]; dv = [d for d in div if d[1] == t]
    print(f"  T{t}: {len(dt)} decisoes, {len(dv)} divergentes")
print("divergentes: (semente, turno, mana_virado, mana_desvirado, dev_virado, dev_desvirado, escolha_mana, escolha_dev)")
for d in div[:12]:
    print("  ", d)
import lzma
saida = os.environ.get("VIES_JSON") or os.path.join(AQUI, "..", "dados", "vies_ensaio_decisoes.json.xz")
with lzma.open(saida, "wt") as f:
    json.dump(dec, f)

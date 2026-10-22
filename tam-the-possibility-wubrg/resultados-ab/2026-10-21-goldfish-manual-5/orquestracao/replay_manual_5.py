"""Replay do goldfish manual #5 do usuario (2026-10-21) no simulador: a MESMA ordem de cartas, a IA do simulador joga.
Mao inicial: o bloco 1 do log tem 7 compras da abertura, 2 devolvidas ao fundo da biblioteca (The Chain Veil e Narset Transcendent: mulligan; quantos mulligans foi, o log nao diz) e a compra do T1 (Way of the Paradox).
Mao de 5 cartas: Way of the Pyromancer, Bloom Tender, Fire-Lit Thicket, Ripples of Potential, Bountiful Promenade. Compras seguintes: TODA carta `library -> hand` do log depois da compra do T1, na ordem do log
(inclui as de habilidade: Jace -3, Garruk, Teferi +1...). As 2 cartas do mulligan ficam no fundo. Nenhuma busca (library -> battlefield).
Uso: python3 replay_manual_5.py [semente]  (saida: linha por turno)."""
import os, sys, json, random
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, DECK)
import tam_goldfish_v1 as T

_LOG = json.load(open(os.path.join(AQUI, "..", "dados", "goldfish_manual_5_bruto.json")))
_B1 = _LOG[0]
_ini = [e["name"] for e in _B1[:7]]                                     # 7 library->hand da abertura
_fundo = [e["name"] for e in _B1[7:9] if e["fromZone"] == "hand" and e["toZone"] == "library"]   # mulligan: vao pro fundo
FUNDO = _fundo
MAO = [c for c in _ini if c not in _fundo]                               # 5 cartas
COMPRAS = [e["name"] for b in _LOG for e in b[(9 if b is _B1 else 0):] if e["fromZone"] == "library" and e["toZone"] == "hand"]
assert MAO == ["Way of the Pyromancer", "Bloom Tender", "Fire-Lit Thicket", "Ripples of Potential", "Bountiful Promenade"], MAO
assert FUNDO == ["The Chain Veil", "Narset Transcendent"], FUNDO


class SemEmbaralhar(random.Random):
    """O log do usuario e' a ordem JA' REALIZADA das compras: o embaralhar do simulador (fetch/tutor) nao pode reordenar a biblioteca."""
    def shuffle(self, x, *a, **k):
        return None


def estado(seed: int, resiliencia: bool = False):
    st = T.GameState(rng=random.Random(seed))
    st.proxy_rng = random.Random(seed * 1_000_033 + 17)
    st.opps = [T.make_opp(seed, i) for i in range(1, T.NUM_OPPONENTS + 1)]
    st.opp_rngs = [None] + [random.Random(seed * 1_000_037 + i * 104729 + 7) for i in range(1, T.NUM_OPPONENTS + 1)]
    resto = [c for c in T.current_library() if c not in MAO and c not in COMPRAS and c not in FUNDO]
    st.rng.shuffle(resto)
    st.rng = SemEmbaralhar(seed)
    st.hand = list(MAO)
    st.library = list(COMPRAS) + resto + list(FUNDO)
    assert len(st.hand) + len(st.library) == 99, (len(st.hand), len(st.library))
    if resiliencia:
        T.setup_resilience(st, seed)
    return st


def resumo(st, t):
    pw = [(p.card.name.split(",")[0].split(" ")[0] + ("" if p.card.name != "Jace Token" else "tok"), T.loyalty(p)) for p in T.pws(st)]
    return (f"T{t:2d}: PWs {len(T.pws(st))} {pw} | terrenos {T.n_lands(st)} | mana(ini) {st.by_turn.get(t, {}).get('mana')} | Tam {'sim' if not st.commander_in_cz else 'nao'} "
            f"| mao {len(st.hand)} | outros {[p.card.name for p in T.vis(st) if 'land' not in p.card.types and 'planeswalker' not in p.card.types][:9]}")


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    st = estado(seed)
    st.verbose = True
    for t in range(1, 11):
        T.play_turn(st)
        for o in list(st.opps):
            if not o.eliminated:
                T.opponent_turn(st, o)
        print(resumo(st, t))
        if st.game_over:
            print("FIM da partida: mesa limpa no turno", st.table_cleared_turn)
            break

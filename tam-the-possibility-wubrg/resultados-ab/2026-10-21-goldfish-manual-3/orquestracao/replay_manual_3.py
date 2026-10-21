"""Replay do goldfish manual #3 do usuario (2026-10-21) no simulador: a MESMA ordem de cartas, a IA do simulador joga.
Mao inicial (8 = 7 + compra do T1; sem foto desta vez: as 8 primeiras compras do bloco 1 do log): Flux Channeler, Ajani Unrelenting, Garruk Curse Breaker, Hallowed Fountain, Faeburrow Elder, Exotic Orchard,
Chromatic Orrery, Birds of Paradise. Compras seguintes na ordem do log (library -> hand; a Chain Veil devolvida ao topo pela Aminatou conta uma vez): The Chain Veil, Aminatou, Ripples of Potential, City of Brass,
Professor Dellian Fel, Undergrowth Stadium. O usuario nao fez buscas (library -> campo) neste jogo.
Uso: python3 replay_manual_3.py [semente]  (saida: linha por turno; varias sementes = varias ordens do resto do baralho)."""
import os, sys, random
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, DECK)
import tam_goldfish_v1 as T

MAO = ["Flux Channeler", "Ajani Unrelenting", "Garruk, Curse Breaker", "Hallowed Fountain", "Faeburrow Elder", "Exotic Orchard", "Chromatic Orrery", "Birds of Paradise"]
COMPRAS = ["The Chain Veil", "Aminatou, the Fateshifter", "Ripples of Potential", "City of Brass", "Professor Dellian Fel", "Undergrowth Stadium"]


class SemEmbaralhar(random.Random):
    """O log do usuario e' a ordem JA' REALIZADA das compras (inclui o embaralhar da fetch dele): o embaralhar da fetch/tutor do simulador nao pode reordenar a biblioteca."""
    def shuffle(self, x, *a, **k):
        return None


def estado(seed: int, resiliencia: bool = False):
    st = T.GameState(rng=random.Random(seed))
    st.proxy_rng = random.Random(seed * 1_000_033 + 17)
    st.opps = [T.make_opp(seed, i) for i in range(1, T.NUM_OPPONENTS + 1)]
    st.opp_rngs = [None] + [random.Random(seed * 1_000_037 + i * 104729 + 7) for i in range(1, T.NUM_OPPONENTS + 1)]
    resto = [c for c in T.current_library() if c not in MAO and c not in COMPRAS]
    st.rng.shuffle(resto)
    st.rng = SemEmbaralhar(seed)
    st.hand = MAO[:7]
    st.library = [MAO[7]] + COMPRAS + resto          # a compra do T1 e' a 8a carta
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
    for t in range(1, 8):
        T.play_turn(st)
        for o in list(st.opps):
            if not o.eliminated:
                T.opponent_turn(st, o)
        print(resumo(st, t))
        if st.game_over:
            print("FIM da partida: mesa limpa no turno", st.table_cleared_turn)
            break

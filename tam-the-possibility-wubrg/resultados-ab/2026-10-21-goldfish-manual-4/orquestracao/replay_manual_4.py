"""Replay do goldfish manual #4 do usuario (2026-10-21) no simulador: a MESMA ordem de cartas, a IA do simulador joga.
Mao inicial (8 = 7 da foto + compra do T1): Ajani Unrelenting, Teferi Temporal Archmage, Nissa Ascended Animist, Indatha Triome, Ichormoon Gauntlet, Starting Town, Ketria Triome, Flooded Grove. Compras
seguintes que FICARAM com o usuario, na ordem do log (library -> hand; o Mossfire Valley e o Staff of Compleation do Teferi +1 mal jogado voltaram ao fundo e nao entram): Overflowing Basin, Twilight Mire,
Exotic Orchard, Yavimaya, Elspeth (anulada pela Vex), Garruk Veiled Butcher (a carta da Vex), Onakke Oathkeeper, Wooded Bastion, Garruk Curse Breaker, Bloom Tender. Nenhuma busca (library -> campo).
Uso: python3 replay_manual_4.py [semente]  (saida: linha por turno; varias sementes = varias ordens do resto do baralho)."""
import os, sys, random
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, DECK)
import tam_goldfish_v1 as T

MAO = ["Ajani Unrelenting", "Teferi, Temporal Archmage", "Nissa, Ascended Animist", "Indatha Triome", "Ichormoon Gauntlet", "Starting Town", "Ketria Triome", "Flooded Grove"]
COMPRAS = ["Overflowing Basin", "Twilight Mire", "Exotic Orchard", "Yavimaya, Cradle of Growth", "Elspeth, Sun's Champion", "Garruk, Veiled Butcher", "Onakke Oathkeeper", "Wooded Bastion", "Garruk, Curse Breaker", "Bloom Tender"]


class SemEmbaralhar(random.Random):
    """O log do usuario e' a ordem JA' REALIZADA das compras (inclui o embaralhar da fetch dele): o embaralhar da fetch/tutor do simulador nao pode reordenar a biblioteca."""
    def shuffle(self, x, *a, **k):
        return None


def liberar_cores(st):
    """Os terrenos dos 3 oponentes passam a produzir as 5 cores (como no playtester do Archidekt, onde a Exotic Orchard do usuario tocou {G} no T2). Chamado DEPOIS dos primeiros turnos de oponente: no T1 do jogador
    os oponentes ainda nao jogaram terreno, e a Orchard nao produz nada (oraculo: 'a land an opponent controls could produce')."""
    for o in st.opps:
        o.land_colors = ["W", "U", "B", "R", "G"]


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
    for t in range(1, 10):
        T.play_turn(st)
        for o in list(st.opps):
            if not o.eliminated:
                T.opponent_turn(st, o)
        print(resumo(st, t))
        if st.game_over:
            print("FIM da partida: mesa limpa no turno", st.table_cleared_turn)
            break

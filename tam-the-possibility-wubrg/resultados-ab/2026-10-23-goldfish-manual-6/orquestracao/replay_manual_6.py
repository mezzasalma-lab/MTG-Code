"""Replay do goldfish manual #6 do usuario (2026-10-23) no simulador: a MESMA mao e as MESMAS compras na MESMA ordem; a IA do simulador joga.
Mao inicial: a foto (`dados/mao_inicial.webp`, "Keep this" / "Mulligan (0)": sem mulligan) mostra Promise of Loyalty, Steam Vents, Hallowed Fountain, Way of the Paradox, Oko, Dihada, Domri = os 7 primeiros
`library -> hand` do bloco 1; o 8o (Liliana's Talent) e' a compra do T1. Compras seguintes: TODA carta `library -> hand` do log depois da abertura, na ordem do log (inclui as de habilidade: Jace -3, WotMS, Surveil...).
Nenhuma busca (`library -> battlefield`: Indatha Triome, Ichormoon Gauntlet, Jetmir's Garden, Zagoth Triome: o simulador as busca por conta propria, com as habilidades dele).
Uso: python3 replay_manual_6.py [semente]  (saida: linha por turno)."""
import os, sys, json, random
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, DECK)
import tam_goldfish_v1 as T

_LOG = json.load(open(os.path.join(AQUI, "..", "dados", "goldfish_manual_6_bruto.json")))
_B1 = _LOG[0]
MAO = [e["name"] for e in _B1[:7]]
assert MAO == ["Promise of Loyalty", "Steam Vents", "Hallowed Fountain", "Way of the Paradox", "Oko, Thief of Crowns", "Dihada, Binder of Wills", "Domri, Chaos Bringer"], MAO
COMPRAS = [e["name"] for b in _LOG for e in b[(7 if b is _B1 else 0):] if e["fromZone"] == "library" and e["toZone"] == "hand"]
assert COMPRAS[:3] == ["Liliana's Talent", "Wrenn and Realmbreaker", "Plaza of Heroes"], COMPRAS[:3]


class SemEmbaralhar(random.Random):
    """O log do usuario e' a ordem JA' REALIZADA das compras: o embaralhar do simulador (fetch/tutor) nao pode reordenar a biblioteca."""
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
    st.hand = list(MAO)
    st.library = list(COMPRAS) + resto
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
    for t in range(1, 12):
        T.play_turn(st)
        for o in list(st.opps):
            if not o.eliminated:
                T.opponent_turn(st, o)
        print(resumo(st, t))
        if st.game_over:
            print("FIM da partida: mesa limpa no turno", st.table_cleared_turn)
            break

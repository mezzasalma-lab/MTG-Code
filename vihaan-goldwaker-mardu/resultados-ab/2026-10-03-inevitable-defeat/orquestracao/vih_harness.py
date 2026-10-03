"""Harness A/B da Inevitable Defeat no simulador do Vihaan, SEM alterar vihaan_goldfish_v1.py (usa o `swap` que o simulador já tem).

Oráculo (Scryfall ao vivo, 2026-10-03): {1}{R}{W}{B}, Instant. "This spell can't be countered. Exile target nonland permanent.
Its controller loses 3 life and you gain 3 life."
Modelagem (convenção das outras remoções do arquivo): tag `removal` (conta `removal_cast_total`), o EXÍLIO é 📊 (sem permanente de
oponente modelado); alvo = permanente de oponente => `commits_crime_this_turn` (Magda: Treasure no fim do turno); perda de vida do
dono do alvo = `drain(3, each_opp=False)` (alvo único: 3 de vida de mesa) e ganho `gain_life(3)`.
ATENÇÃO: este simulador NÃO modela cor de mana (só total de mana). A restrição R+W+B do Defeat é medida à parte (vih_cor.py)."""
import os
import sys

REPO = "/home/user/MTG-Code"
DADOS = os.path.join(REPO, "vihaan-goldwaker-mardu", "resultados-ab", "2026-10-03-inevitable-defeat", "dados")
os.chdir(os.path.join(REPO, "vihaan-goldwaker-mardu"))
sys.path.insert(0, os.path.join(REPO, "vihaan-goldwaker-mardu"))
import vihaan_goldfish_v1 as V  # noqa: E402

DEFEAT = "Inevitable Defeat"
BLANK = "Blank Card"
V.add(DEFEAT, 4, "instant", {"removal", "inevitable_defeat"})
BLANK_TYPE = os.environ.get("BLANK_TYPE", "instant")   # "artifact" reproduz o lote SUPERADO
V.add(BLANK, 99, BLANK_TYPE, set())
V.LAND_NAMES = {n for n, c in V.CARD_DB.items() if c.ctype == "land"}
ORIG_LIBRARY = list(V.BASE_LIBRARY)

_orig_resolve = V.resolve_instant_sorcery


def _resolve(state, name):
    _orig_resolve(state, name)
    if name == DEFEAT:
        state.commits_crime_this_turn = True
        V.drain(state, 3, each_opp=False)
        V.gain_life(state, 3)
        state.defeat_cast_turn = state.turn
        state.defeat_magda = "Magda, the Hoardmaster" in state.battlefield
        state.defeat_witch = "Witch of the Moors" in state.battlefield


V.resolve_instant_sorcery = _resolve


# ---------------------------------------------------------------------------
# Porta de COR para a Inevitable Defeat ({1}{R}{W}{B}) — o simulador só conta mana total.
# VIH_COLOR=off  : comportamento original do harness (sem restrição de cor; resultados já arquivados)
# VIH_COLOR=sim  : PESSIMISTA — só terrenos JÁ jogados pelo simulador (que joga lands_in_hand[0], sem sequenciar por cor),
#                  Exotic Orchard sem cor (goldfish sem terrenos de oponente), filtros/Pathway como 1 fonte de 2 cores
# VIH_COLOR=best : OTIMISTA — melhor subconjunto de terrenos (campo + mão, mesmo nº de terrenos em campo), Orchard = qualquer cor
# Em ambos: Arcane Signet e cada Treasure = fonte de qualquer cor (R/W/B); Sol Ring incolor. Precisa de 3 fontes distintas p/ R, W, B.
# ---------------------------------------------------------------------------
COLOR_MODE = os.environ.get("VIH_COLOR", "off")
RWB = {"R", "W", "B"}
LAND_COLORS = {
    "Battlefield Forge": {"R", "W"}, "Blackcleave Cliffs": {"B", "R"}, "Blood Crypt": {"B", "R"}, "Bojuka Bog": {"B"},
    "Brightclimb Pathway // Grimclimb Pathway": {"W", "B"}, "Caves of Koilos": {"W", "B"}, "Clifftop Retreat": {"R", "W"},
    "Command Tower": set(RWB), "Desolate Mire": {"W", "B"}, "Dragonskull Summit": {"B", "R"}, "Fetid Heath": {"W", "B"},
    "Isolated Chapel": {"W", "B"}, "Luxury Suite": {"B", "R"}, "Mountain": {"R"}, "Path of Ancestry": set(RWB), "Plains": {"W"},
    "Rugged Prairie": {"R", "W"}, "Shadowblood Ridge": {"B", "R"}, "Spectator Seating": {"R", "W"}, "Sulfurous Springs": {"B", "R"},
    "Swamp": {"B"}, "Tainted Peak": {"B", "R"},
}
ORCHARD = "Exotic Orchard"


def _land_color_sets(state, mode):
    on_bf = [n for n in state.battlefield if n in V.LAND_NAMES]
    pool = list(on_bf)
    if mode == "best":
        pool += [n for n in state.hand if n in V.LAND_NAMES]

    def cs(n):
        if n == ORCHARD:
            return set(RWB) if mode == "best" else set()
        return LAND_COLORS.get(n, set())
    return [cs(n) for n in pool], len(on_bf)


def color_ok(state, mode):
    """Existe atribuição de 3 fontes distintas a R, W, B (terrenos <= nº em campo; Signet; Treasures curinga)?"""
    lands, cap = _land_color_sets(state, mode)
    signet = 1 if "Arcane Signet" in state.battlefield else 0
    wild = state.treasures

    def rec(i, need, used_lands, signet_left, wild_left, taken):
        if i == len(need):
            return True
        col = need[i]
        for j, cset in enumerate(lands):
            if j not in taken and col in cset and used_lands < cap:
                if rec(i + 1, need, used_lands + 1, signet_left, wild_left, taken | {j}):
                    return True
        if signet_left and rec(i + 1, need, used_lands, 0, wild_left, taken):
            return True
        if wild_left and rec(i + 1, need, used_lands, signet_left, wild_left - 1, taken):
            return True
        return False
    return rec(0, ["R", "W", "B"], 0, signet, wild, frozenset())


_orig_can_cast = V.can_cast


def _can_cast(state, name):
    ok = _orig_can_cast(state, name)
    if ok and name == DEFEAT and COLOR_MODE != "off":
        return color_ok(state, COLOR_MODE)
    return ok


V.can_cast = _can_cast

_orig_play_turn = V.play_turn


def _play_turn(state, is_first_turn, on_play):
    _orig_play_turn(state, is_first_turn, on_play)
    # instrumentação (só leitura): 1º turno em que as 3 cores existem (nas 2 leituras) e há >= 4 de mana total
    for m in ("sim", "best"):
        k = "rwb_turn_" + m
        if getattr(state, k, None) is None and V.total_mana(state) >= 4 and color_ok(state, m):
            setattr(state, k, state.turn)


V.play_turn = _play_turn


def summarize(s):
    return {
        "win_turn": s.win_turn,
        "cmd_turn": s.commander_cast_turn,
        "treasures": s.treasures_created_total,
        "drain": s.drain_damage_total,
        "table_dmg": s.table_damage_total,
        "combat": s.combat_damage_proxy_total,
        "removal": s.removal_cast_total,
        "life_gained": s.life_gained_total,
        "cards_extra": s.cards_drawn_extra,
        "revel_turn": s.revel_condition_met_turn,
        "defeat_turn": getattr(s, "defeat_cast_turn", None),
        "mulligans": s.mulligans,
        "defeat_magda": 1 if getattr(s, "defeat_magda", False) else 0,
        "defeat_witch": 1 if getattr(s, "defeat_witch", False) else 0,
        "recursion": s.recursion_events_total,
        "rwb_turn_sim": getattr(s, "rwb_turn_sim", None),
        "rwb_turn_best": getattr(s, "rwb_turn_best", None),
    }


def run_variant(args):
    pairs, seeds, turns = args
    return [summarize(V.simulate_one(sd, turns, swap=(pairs or None))) for sd in seeds]


def verifica_bit_identidade(n=300, turns=8, seed_base=3_000_000):
    """swap=None com o harness carregado tem de bater com o simulador (mesmos campos)."""
    ok = 0
    for i in range(n):
        a = V.simulate_one(seed_base + i, turns)
        b = V.simulate_one(seed_base + i, turns, swap=None)
        if all(getattr(a, k) == getattr(b, k) for k in ("win_turn", "commander_cast_turn", "treasures_created_total", "drain_damage_total", "removal_cast_total")):
            ok += 1
    return ok, n


if __name__ == "__main__":
    print("determinismo (base x base):", verifica_bit_identidade())

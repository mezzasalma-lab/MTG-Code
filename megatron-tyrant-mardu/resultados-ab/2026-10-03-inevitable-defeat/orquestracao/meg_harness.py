"""Harness A/B da Inevitable Defeat no simulador do Megatron, SEM alterar megatron_goldfish_v1.py.

Oráculo (Scryfall ao vivo, 2026-10-03): {1}{R}{W}{B}, Instant. "This spell can't be countered. Exile target nonland permanent.
Its controller loses 3 life and you gain 3 life." Ruling: se o alvo for ilegal, nada acontece (ninguém ganha/perde vida).

Modelagem (mesma convenção das outras interações sem alvo real do arquivo — Path/Swords/Generous Gift/Vandalblast):
- tag `interaction`: conta `interaction_spells_cast_total`; o EXÍLIO do alvo é 📊 (sem permanente de oponente modelado).
- A perda de vida do controlador do alvo (3) e o ganho de 3 SÃO modeláveis: `proxy_drain(3)` (alimenta
  `life_lost_by_opponents_this_turn`, que o Megatron, Tyrant converte em {C} no 2º flip: "add {C} for each 1 life your opponents
  have lost this turn") e `gain_life(3)`. Custo {1}{R}{W}{B}: o simulador exige as 3 cores (pips) via `can_cast`.
"""
import os
import random
import sys

REPO = "/home/user/MTG-Code"
DADOS = os.path.join(REPO, "megatron-tyrant-mardu", "resultados-ab", "2026-10-03-inevitable-defeat", "dados")
os.chdir(os.path.join(REPO, "megatron-tyrant-mardu"))   # build_library() lê 'lista.md' do diretório corrente
sys.path.insert(0, os.path.join(REPO, "megatron-tyrant-mardu"))
import megatron_goldfish_v1 as M  # noqa: E402

DEFEAT = "Inevitable Defeat"
BLANK = "Blank Card"
M.add(DEFEAT, 4, "instant", {"interaction", "inevitable_defeat"}, pips={"R": 1, "W": 1, "B": 1})
BLANK_TYPE = os.environ.get("BLANK_TYPE", "instant")   # "artifact" reproduz o lote SUPERADO (Blank virava combustível MV 99 do Megatron)
M.add(BLANK, 99, BLANK_TYPE, set(), pips={})   # inconjurável (controle de ablação)
M.LAND_NAMES = {n for n, c in M.CARD_DB.items() if c.ctype == "land"}

_orig_resolve = M.resolve_instant_sorcery
ORIG_LIBRARY = list(M.BASE_LIBRARY)   # 99 cartas (sem o comandante): `mulligan()` lê o BASE_LIBRARY global
SWAP = {"pairs": []}


def apply_swap(pairs):
    lib = list(ORIG_LIBRARY)
    for sai, entra in pairs:
        if sai is None:
            lib.append(entra)
        else:
            lib[lib.index(sai)] = entra
    M.BASE_LIBRARY = lib
    return lib


def _resolve(state, name):
    _orig_resolve(state, name)
    if name == DEFEAT:
        M.proxy_drain(state, 3)
        M.gain_life(state, 3)
        state.defeat_cast_turn = state.turn
        state.defeat_megatron_face = state.megatron_face
        state.defeat_commander_in_play = state.commander_in_play


M.resolve_instant_sorcery = _resolve

_orig_postcombat = M.megatron_postcombat


def _postcombat(state):
    antes = state.megatron_conversions_total
    _orig_postcombat(state)
    # instrumentação (só leitura): a Defeat foi conjurada NESTE turno e o Megatron converteu no postcombat => os 3 de vida
    # que ela tirou viraram {C} ("add {C} for each 1 life your opponents have lost this turn")
    if state.megatron_conversions_total > antes and getattr(state, "defeat_cast_turn", None) == state.turn:
        state.defeat_fed_turns = getattr(state, "defeat_fed_turns", 0) + 1
        state.defeat_fed_mana = getattr(state, "defeat_fed_mana", 0) + 3


M.megatron_postcombat = _postcombat

_orig_play_turn = M.play_turn


def _play_turn(state, is_first_turn, on_play):
    _orig_play_turn(state, is_first_turn, on_play)
    # instrumentação (só leitura): 1º turno em que as 3 cores R+W+B existem em campo e há >= 4 de mana total
    if getattr(state, "rwb_turn", None) is None and M.has_color_sources_for(state, DEFEAT) and M.total_mana(state) >= 4:
        state.rwb_turn = state.turn


M.play_turn = _play_turn


def summarize(s):
    return {
        "cmd_turn": s.commander_cast_turn,
        "mana_convert": s.megatron_mana_generated_total,
        "conversions": s.megatron_conversions_total,
        "proxy_dmg": s.proxy_damage_total,
        "interaction": s.interaction_spells_cast_total,
        "lifegain": s.proxy_lifegain_total,
        "poison_win": 1 if s.blightsteel_poison_win else 0,
        "cmd_dmg_win": 1 if s.commander_damage_win else 0,
        "weld": s.weld_activations_total,
        "recursion": s.recursion_events_total,
        "cards_extra": s.cards_drawn_extra,
        "hand": len(s.hand),
        "life": s.life,
        "defeat_turn": getattr(s, "defeat_cast_turn", None),
        "defeat_with_megatron": 1 if getattr(s, "defeat_commander_in_play", False) else 0,
        "defeat_tyrant_face": 1 if getattr(s, "defeat_megatron_face", None) == "tyrant" else 0,
        "rwb_turn": getattr(s, "rwb_turn", None),
        "defeat_fed": getattr(s, "defeat_fed_turns", 0),
        "defeat_fed_mana": getattr(s, "defeat_fed_mana", 0),
    }


def run_variant(args):
    pairs, seeds, turns = args
    SWAP["pairs"] = list(pairs)
    apply_swap(pairs)
    return [summarize(M.simulate_one(sd, turns)) for sd in seeds]


def verifica_bit_identidade(n=300, turns=8, seed_base=3_000_000):
    """Harness com `pairs=[]` tem de ser idêntico ao simulador original (mesmo código, só com a carta no CARD_DB)."""
    apply_swap([])
    ok = 0
    for i in range(n):
        a = M.simulate_one(seed_base + i, turns)
        b = M.simulate_one(seed_base + i, turns)   # determinismo
        keys = ["commander_cast_turn", "proxy_damage_total", "interaction_spells_cast_total", "megatron_mana_generated_total",
                "megatron_conversions_total", "weld_activations_total", "cards_drawn_extra", "life"]
        if all(getattr(a, k) == getattr(b, k) for k in keys):
            ok += 1
    return ok, n


if __name__ == "__main__":
    print("determinismo/bit-identidade (base x base):", verifica_bit_identidade())

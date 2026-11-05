"""Harness A/B da The Pride of Hull Clade no simulador do Thranduil, SEM alterar thranduil_goldfish_v1.py.

A carta é acrescentada em tempo de execução (monkeypatch) e o simulador original fica intocado, então a base
(sem a Pride) é bit-idêntica por construção; `verifica_bit_identidade()` confere isso contra `T.simulate_one`.

Oráculo (Scryfall ao vivo, 2026-10-03): {10}{G}, Legendary Creature — Crocodile Elk Turtle 2/15, Defender.
"This spell costs {X} less to cast, where X is the total toughness of creatures you control."
"{2}{U}{U}: Until end of turn, target creature you control gets +1/+0, gains 'Whenever this creature deals combat damage
to a player, draw cards equal to its toughness,' and can attack as though it didn't have defender."
Rulings: o custo não cai abaixo de {G}; o MV continua 11; o toughness é lido ao anunciar a magia.

Modelagem (premissas documentadas no LEIAME):
- custo = max(1, 11 - toughness total das criaturas): toughness impresso (oracle-cache) + anthem de Elfo (mesma contagem de
  `anthem` que o simulador usa para o poder) + contadores da Marwyn; fichas 'Elf Warrior Token' = 1.
- PRIDE_MODE:
    'off'          corpo 2/15 defender sem a habilidade ativada (isola custo do corpo)
    'trample_line' ativa só no turno em que a Ezuri já pagou o +3/+3 trample dos Elfos (linha deliberada): alvo = o Elfo
                   de maior toughness; compra = esse toughness + 3 (x2 com a Roaming Throne em campo: o gatilho concedido
                   é de um Elfo). Exige {2}{U}{U} sobrando e >=2 fontes de U.
    'ceiling'      teto sob a convenção do simulador (sem bloqueio): ativa no próprio Pride (15 de toughness) todo turno
                   em que ele já pode atacar e sobram {2}{U}{U}; compra 15. É TETO, não expectativa.
"""
import json
import os
import random
import sys
from collections import Counter

REPO = "/home/user/MTG-Code"
sys.path.insert(0, os.path.join(REPO, "thranduil-sultai"))
import thranduil_goldfish_v1 as T  # noqa: E402

CACHE = json.load(open(os.path.join(REPO, "scryfall-cache", "oracle-cache.json")))
PRIDE = "The Pride of Hull Clade"
BLANK = "Blank Card"
ORIG_DECKLIST = T.DECKLIST_TEXT

T.add(PRIDE, 11, {"Creature"}, tags={"pride"}, colors={"G"}, power=2)
BLANK_TYPE = os.environ.get("BLANK_TYPE", "Instant")   # "Artifact" reproduz a 1ª ablação (superada)
T.add(BLANK, 99, {BLANK_TYPE})  # inconjurável: remove a carta do jogo (controle de ablação)


def _printed_toughness(name):
    e = CACHE.get(name) or CACHE.get(name.split(" // ")[0]) or {}
    t = e.get("toughness")
    if t is None and e.get("card_faces"):
        t = e["card_faces"][0].get("toughness")
    try:
        return int(t)
    except (TypeError, ValueError):
        return None


TOUGH = {}
for _n, _c in T.CARD_DB.items():
    if "Creature" in _c.types:
        _t = _printed_toughness(_n)
        TOUGH[_n] = _t if _t is not None else 1  # CDA ('*'): base 1 (subestima Jarad)
TOUGH["Elf Warrior Token"] = 1
TOUGH[PRIDE] = 15
TOUGH["Roaming Throne"] = 4


def total_toughness(state):
    anth = sum(1 for c in state.battlefield if T.has_tag(c, "anthem"))
    tot = 0
    for c in state.battlefield:
        if not T.is_creature(c):
            continue
        t = TOUGH.get(c, 1)
        if T.is_elf(c):
            t += anth
        if c == "Marwyn, the Nurturer":
            t += state.marwyn_counters
        tot += t
    return tot


_orig_emv = T.effective_mv


def _emv(state, card):
    if card == PRIDE:
        return max(1, 11 - total_toughness(state))
    return _orig_emv(state, card)


T.effective_mv = _emv

_orig_cast = T.cast_spell


def _cast(state, card, log):
    if card == PRIDE:
        state.pride_cast_turn = state.turn
        state.pride_cost = _emv(state, PRIDE)
        state.pride_toughness_at_cast = total_toughness(state)
    return _orig_cast(state, card, log)


T.cast_spell = _cast

_orig_fin = T.activate_finishers


def _fin(state, log):
    before = len(state.finishers_activated)
    _orig_fin(state, log)
    new = state.finishers_activated[before:]
    if "Ezuri, Renegade Leader" in new:
        state.ezuri_pump_turn = state.turn
    return None


T.activate_finishers = _fin

PRIDE_MODE = {"mode": "off"}
_orig_cs = T.combat_step


def _best_elf_toughness(state):
    anth = sum(1 for c in state.battlefield if T.has_tag(c, "anthem"))
    best = 0
    for c in state.battlefield:
        if T.is_creature(c) and T.is_elf(c):
            t = TOUGH.get(c, 1) + anth + (state.marwyn_counters if c == "Marwyn, the Nurturer" else 0)
            best = max(best, t)
    return best


def _cs(state, log):
    mode = PRIDE_MODE["mode"]
    if mode != "off" and PRIDE in state.battlefield:
        can_attack = state.creature_cast_turn.get(PRIDE, state.turn) < state.turn or state.lightning_greaves_equipped_to == PRIDE
        has_uu = T.color_sources(state, "U") >= 2
        if has_uu and T.remaining_mana(state) >= 4:
            n = 0
            if mode == "ceiling" and can_attack:
                n = TOUGH[PRIDE]
            elif mode == "trample_line" and getattr(state, "ezuri_pump_turn", None) == state.turn:
                n = _best_elf_toughness(state) + 3
                if state.roaming_throne_active():
                    n *= 2          # a habilidade concedida é gatilho de um Elfo: Roaming Throne dispara 1 vez a mais
                    state.roaming_throne_doublings += 1
            if n:
                state.mana_spent_this_turn += 4
                state.draw(n, source="Pride of Hull Clade")
                state.pride_activations = getattr(state, "pride_activations", 0) + 1
                state.pride_draws = getattr(state, "pride_draws", 0) + n
                log.append({"trigger": "pride_activation", "turn": state.turn, "draw": n})
    return _orig_cs(state, log)


T.combat_step = _cs


def sim_state(seed, turns, decklist_text):
    """Cópia fiel de T.simulate_one que devolve o estado final (RNG consumido na mesma ordem)."""
    T.DECKLIST_TEXT = decklist_text
    rng = random.Random(seed)
    deck = T.parse_decklist(T.DECKLIST_TEXT)
    rng.shuffle(deck)
    state = T.GameState(rng=rng, library=deck)
    mulligans = 0
    while True:
        state.hand = []
        state.draw(7, source="normal")
        if T.should_keep(state.hand) or mulligans >= 2:
            break
        mulligans += 1
        state.library.extend(state.hand)
        state.hand = []
        rng.shuffle(state.library)
    penalty = max(0, mulligans - 1)
    if penalty:
        bottoms = T.choose_bottom(state.hand, penalty)
        for c in bottoms:
            state.hand.remove(c)
            state.library.append(c)
    game_log = [[{"seed": seed, "mulligans": mulligans, "starting_hand": list(state.hand)}]]
    for t in range(1, turns + 1):
        T.play_turn(state, t, game_log)
    state.mulligans = mulligans
    return state


def summarize(state):
    return {
        "mulligans": state.mulligans,
        "commander_cast_turn": state.commander_cast_turn,
        "finisher_turn": state.finisher_turn,
        "extra_draws": state.extra_draws,
        "spells_cast": state.spells_cast,
        "legendary_elf_triggers": state.thranduil_legendary_elf_triggers,
        "combat_damage_draws": state.combat_damage_draws,
        "creature_engine_draws": state.creature_engine_draws,
        "hand_size": len(state.hand),
        "battlefield": len(state.battlefield),
        "blue_screw_turns": state.blue_screw_turns,
        "pride_cast_turn": getattr(state, "pride_cast_turn", None),
        "pride_cost": getattr(state, "pride_cost", None),
        "pride_toughness_at_cast": getattr(state, "pride_toughness_at_cast", None),
        "pride_activations": getattr(state, "pride_activations", 0),
        "pride_draws": getattr(state, "pride_draws", 0),
        "total_toughness_end": total_toughness(state),
        "discarded_hand_size": state.cards_discarded_to_hand_size,
        "uu_sources_end": T.color_sources(state, "U"),
    }


def swap_text(sai, entra, base_text=None):
    """Troca NA MESMA POSIÇÃO (1 cópia de `sai` por `entra`); `sai`=None adiciona sem cortar."""
    base_text = base_text or ORIG_DECKLIST
    lines = base_text.splitlines()
    out, done = [], False
    for l in lines:
        s = l.strip()
        if not done and sai and s.startswith("1 ") and s[2:] == sai:
            out.append(l.replace(sai, entra))
            done = True
        elif not done and sai and s.split(" ", 1)[-1] == sai and s.split(" ", 1)[0].isdigit() and int(s.split(" ", 1)[0]) > 1:
            q = int(s.split(" ", 1)[0])
            out.append(f"{q - 1} {sai}")
            out.append(f"1 {entra}")
            done = True
        else:
            out.append(l)
    assert done or not sai, f"carta nao encontrada: {sai}"
    return "\n".join(out)


def run_variant(args):
    """args = (decklist_text, mode, seeds, turns). Retorna lista de dicts (um por semente)."""
    text, mode, seeds, turns = args
    PRIDE_MODE["mode"] = mode
    res = []
    for sd in seeds:
        res.append(summarize(sim_state(sd, turns, text)))
    return res


def verifica_bit_identidade(n=300, turns=8, seed_base=3_000_000):
    """A base do harness (sem Pride) tem de bater campo a campo com T.simulate_one."""
    T.DECKLIST_TEXT = ORIG_DECKLIST
    campos = ["commander_cast_turn", "finisher_turn", "extra_draws", "spells_cast", "thranduil_legendary_elf_triggers",
              "combat_damage_draws", "creature_engine_draws", "hand_size", "blue_screw_turns", "mulligans",
              "lands_played_total", "cards_discarded_to_hand_size"]
    PRIDE_MODE["mode"] = "off"
    ok = 0
    for i in range(n):
        a = T.simulate_one(seed_base + i, turns)
        s = sim_state(seed_base + i, turns, ORIG_DECKLIST)
        b = {"commander_cast_turn": s.commander_cast_turn, "finisher_turn": s.finisher_turn, "extra_draws": s.extra_draws,
             "spells_cast": s.spells_cast, "thranduil_legendary_elf_triggers": s.thranduil_legendary_elf_triggers,
             "combat_damage_draws": s.combat_damage_draws, "creature_engine_draws": s.creature_engine_draws,
             "hand_size": len(s.hand), "blue_screw_turns": s.blue_screw_turns, "mulligans": s.mulligans,
             "lands_played_total": s.lands_played_total, "cards_discarded_to_hand_size": s.cards_discarded_to_hand_size}
        if all(a[k] == b[k] for k in campos):
            ok += 1
    return ok, n


if __name__ == "__main__":
    ok, n = verifica_bit_identidade()
    print(f"bit-identidade base (harness x simulate_one): {ok}/{n} partidas iguais em {12} campos")

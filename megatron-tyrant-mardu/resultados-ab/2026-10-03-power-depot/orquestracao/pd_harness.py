"""Harness A/B do Power Depot no simulador do Megatron, SEM alterar megatron_goldfish_v1.py.

Oráculo (Scryfall ao vivo, 2026-10-03): Artifact Land (Modern Horizons 2). "This land enters tapped. {T}: Add {C}. {T}: Add one mana of any color.
Spend this mana only to cast artifact spells or activate abilities of artifacts. Modular 1."
Rulings (4, 2021-06-18): só pode ser jogado como terreno; entra com contador +1/+1 que não faz nada enquanto for terreno; ao ir ao cemitério
você pode pôr os contadores em UM artefato-criatura alvo (quaisquer que sejam os tipos dele naquele momento); o mana do 3º efeito não paga habilidades de
cartas-artefato em outras zonas (cycling, unearth).

Modelagem (política documentada no LEIAME):
- terreno que entra TAPPED, rende {C} (conta em `total_mana` como qualquer terreno; `produces=set()` => não entra na checagem de cor original);
- FIXAÇÃO CONDICIONAL: a checagem de cor `has_color_sources_for` do simulador conta fontes por cor, sem casar fontes. Para uma magia-ARTEFATO (o próprio
  Megatron, Tyrant é artefato, as duas faces; Gearhulks, Cursed Mirror, Junker, Moxite, Steel Seraph…), cada Power Depot untapped cobre UM pip faltante
  (não 3 de uma vez): `soma dos pips faltantes <= nº de Depots untapped`. Magia não-artefato: o Depot não fixa nada;
- Demonic Junker (Affinity for artifacts): o Depot é artefato, então reduz {1} (o simulador só conta cartas com tag artifact);
- NÃO é tratado como artefato nas demais piscinas do simulador (combustível do Megatron, Welder, Engineer, Trash for Treasure, Ultron, Pia's Revolution),
  por política: o piloto não sacrifica terreno à toa. Sensibilidade `fodder7`: com >=7 terrenos em campo, o Depot sobrando vira o combustível MAIS BARATO
  de Welder/Scrap Welder/Engineer/Trash (MV 0), sem as sinergias de "artifact put into graveyard" (Pia's Revolution, Scrap Trawler), que NÃO são modeladas;
- política de jogada `early`: com o Depot na mão, joga-o no T1/T2 (terreno tapped no turno em que não há nada pra jogar); o piloto original só ordena
  terrenos por cor faltante e, em empate, pela ordem da mão (`sim`).
NÃO modelado: Ultron copiando o Depot por {2} (o simulador só copia artefato com MV>=3 ou rock/Moxite; a cópia seria um terreno tapped que vira 2/2),
Modular (contador no Megatron artefato-criatura ao morrer o Depot), improvise/convoke.
"""
import os
import sys

REPO = "/home/user/MTG-Code"
DADOS = os.path.join(REPO, "megatron-tyrant-mardu", "resultados-ab", "2026-10-03-power-depot", "dados")
os.chdir(os.path.join(REPO, "megatron-tyrant-mardu"))   # build_library() lê 'lista.md' do diretório corrente
sys.path.insert(0, os.path.join(REPO, "megatron-tyrant-mardu"))
import megatron_goldfish_v1 as M  # noqa: E402

DEPOT = "Power Depot"
BLANK = "Blank Card"
M.add(DEPOT, 0, "land", {"power_depot"}, produces=set())
M.add(BLANK, 99, "instant", set(), pips={})
M.LAND_NAMES = {n for n, c in M.CARD_DB.items() if c.ctype == "land"}
M.ETB_TAPPED_LANDS.add(DEPOT)
ORIG_LIBRARY = list(M.BASE_LIBRARY)

# core: piloto original do simulador | early: só o Depot é jogado no T1/T2 | early_all: QUALQUER terreno que entra tapped é jogado primeiro no T1/T2
# (piloto deliberado, vale também para a BASE: compara Depot vs terrenos tapped já jogados do mesmo jeito) | fodder7: early + Depot sobrando vira combustível
# | early_all_fodder7: early_all + combustível. A BASE só é bit-idêntica ao simulador original em core/early/fodder7.
POLICY = {"mode": os.environ.get("PD_POLICY", "core")}
# PD_COLOR=strict: troca a checagem de cor do simulador (que deixa UM terreno tri-color/Command Tower pagar R, W e B ao mesmo tempo) por casamento exato
# fonte->pip. Muda também a BASE (não é bit-idêntica ao simulador original): serve de sensibilidade, com base e variantes sob a mesma regra.


def apply_swap(pairs):
    lib = list(ORIG_LIBRARY)
    for sai, entra in pairs:
        if sai is None:
            lib.append(entra)
        else:
            lib[lib.index(sai)] = entra
    M.BASE_LIBRARY = lib
    return lib


def depots_untapped(state):
    n = sum(1 for c in state.battlefield if c == DEPOT)
    if state.tapped_land_this_turn == DEPOT:
        n -= 1
    return max(0, n)


_orig_has_color = M.has_color_sources_for
COLOR = os.environ.get("PD_COLOR", "sim")   # sim: checagem de cor do simulador (conta fontes por cor, sem casar) | strict: casamento exato fonte->pip (cada fonte paga 1 pip)


def _strict_match(state, name, wild):
    need = [c for c, k in M.CARD_DB[name].pips.items() for _ in range(k)]
    if not need:
        return True
    sources = []
    for card in state.battlefield:
        if card not in M.CARD_DB or card == state.tapped_land_this_turn:
            continue
        prod = M.CARD_DB[card].produces
        if prod:
            sources.append(set(prod))

    def rec(i, used, wild_left):
        if i == len(need):
            return True
        for j, ps in enumerate(sources):
            if j not in used and need[i] in ps and rec(i + 1, used | {j}, wild_left):
                return True
        return wild_left > 0 and rec(i + 1, used, wild_left - 1)
    return rec(0, frozenset(), wild)


def _has_color(state, name):
    d = depots_untapped(state) if M.is_artifact_card(name) else 0
    if COLOR == "strict":
        ok = _strict_match(state, name, d)
        if ok and d > 0 and not _strict_match(state, name, 0) and name == M.COMMANDER and getattr(state, "depot_fixed_cmd_turn", None) is None:
            state.depot_fixed_cmd_turn = state.turn
        return ok
    base = _orig_has_color(state, name)
    if base:
        return True
    if not M.is_artifact_card(name) or d <= 0:
        return False
    deficit = 0
    for color, needed in M.CARD_DB[name].pips.items():
        deficit += max(0, needed - M.color_sources(state, color))
    ok = deficit <= d
    if ok and name == M.COMMANDER and getattr(state, "depot_fixed_cmd_turn", None) is None:
        state.depot_fixed_cmd_turn = state.turn     # 1ª vez em que o Depot é o que deixa o comandante castável
    return ok


M.has_color_sources_for = _has_color

_orig_eff_cost = M.effective_cost


def _eff_cost(state, name):
    c = _orig_eff_cost(state, name)
    if name == "Demonic Junker":
        c = max(0, c - sum(1 for n in state.battlefield if n == DEPOT))
    return c


M.effective_cost = _eff_cost

_orig_play_land = M.play_land


def _missing_score(state, card):
    score = 0
    for color in "WBR":
        if M.color_sources(state, color) == 0 and color in M.CARD_DB[card].produces:
            score += 1
    return -score


def _play_land(state):
    if POLICY["mode"] in ("early_all", "early_all_fodder7") and state.lands_played_this_turn < 1 and state.turn <= 2:
        tapped = [n for n in state.hand if n in M.ETB_TAPPED_LANDS]
        if tapped:
            tapped.sort(key=lambda n: _missing_score(state, n))
            choice = tapped[0]
            state.hand.remove(choice)
            state.lands_played_this_turn += 1
            state.battlefield.append(choice)
            if choice == "Smoldering Marsh":
                basics = sum(1 for n in state.battlefield if n in ("Mountain", "Plains", "Swamp"))
                if basics < 2:
                    state.tapped_land_this_turn = choice
            else:
                state.tapped_land_this_turn = choice
            if choice == DEPOT and getattr(state, "depot_turn", None) is None:
                state.depot_turn = state.turn
            return
    if (POLICY["mode"] in ("early", "fodder7") and DEPOT in state.hand and state.lands_played_this_turn < 1 and state.turn <= 2):
        state.hand.remove(DEPOT)
        state.lands_played_this_turn += 1
        state.battlefield.append(DEPOT)
        state.tapped_land_this_turn = DEPOT
        if getattr(state, "depot_turn", None) is None:
            state.depot_turn = state.turn
        return
    _orig_play_land(state)
    if DEPOT in state.battlefield and getattr(state, "depot_turn", None) is None:
        state.depot_turn = state.turn


M.play_land = _play_land

_orig_fodder = M.best_weld_fodder


def _fodder(state, min_mv=0):
    if POLICY["mode"] in ("fodder7", "early_all_fodder7") and DEPOT in state.battlefield and min_mv <= 0:
        lands = sum(1 for n in state.battlefield if n in M.LAND_NAMES)
        pend = [n for n in state.temp_creatures_pending_sacrifice if n in state.battlefield and M.is_artifact_card(n)]
        if lands >= 7 and not pend:
            return DEPOT
    return _orig_fodder(state, min_mv)


M.best_weld_fodder = _fodder


def summarize(s):
    return {
        "cmd_turn": s.commander_cast_turn,
        "proxy_dmg": s.proxy_damage_total,
        "mana_convert": s.megatron_mana_generated_total,
        "conversions": s.megatron_conversions_total,
        "weld": s.weld_activations_total,
        "recursion": s.recursion_events_total,
        "cards_extra": s.cards_drawn_extra,
        "poison_win": 1 if s.blightsteel_poison_win else 0,
        "cmd_dmg_win": 1 if s.commander_damage_win else 0,
        "lands_end": sum(1 for n in s.battlefield if n in M.LAND_NAMES),
        "hand": len(s.hand),
        "depot_turn": getattr(s, "depot_turn", None),
        "depot_fixed_cmd_turn": getattr(s, "depot_fixed_cmd_turn", None),
        "ramp": s.ramp_pieces_cast_total,
    }


def run_variant(args):
    pairs, seeds, turns = args
    apply_swap(pairs)
    return [summarize(M.simulate_one(sd, turns)) for sd in seeds]

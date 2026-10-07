import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)

# 1) cartas
sub('''add("Riverchurn Monument", "{1}{U}", {"artifact"}, {"riverchurn"})      # candidata de 2026-10-07 (oraculo ao vivo: resultados-ab/2026-10-07-riverchurn-monument)
''', '''add("Riverchurn Monument", "{1}{U}", {"artifact"}, {"riverchurn"})      # candidata de 2026-10-07 (oraculo ao vivo: resultados-ab/2026-10-07-riverchurn-monument)
add("Agent Frank Horrigan", "{5}{B}{G}", {"creature"}, {"horrigan", "trample"}, 8, 6, legendary=True, subtypes={"Mutant", "Warrior"})      # candidata de 2026-10-07 (resultados-ab/2026-10-07-comparacao-stefano)
add("The Master, Transcendent", "{1}{B}{G}{U}", {"artifact", "creature"}, {"master_t"}, 2, 4, legendary=True, subtypes={"Mutant"})        # candidata de 2026-10-07 (resultados-ab/2026-10-07-comparacao-stefano)
add("Opponent Creature Card", "", {"creature"}, {"opp_card"}, 3, 3, subtypes={"Mutant"})   # ficticia: a carta de criatura de oponente que a Master levou (corpo 3/3 generico; volta ao cemiterio dele)
''')
# 2) campos do Permanent
sub('''    exhausted: bool = False


@dataclass
class Opp:''', '''    exhausted: bool = False
    attacked_turn_id: int = -1         # Horrigan: "indestructible as long as it attacked this turn"
    base_pt: Optional[tuple] = None    # The Master, Transcendent: "base power and toughness 3/3" (sobrepoe CDA, ruling 2024-03-08)
    mutant: bool = False               # The Master: "It's a green Mutant ... It loses its other colors and creature types"
    owner_idx: int = 0                 # Opponent Creature Card: de qual oponente veio (volta ao cemiterio dele)


@dataclass
class Opp:''')
# 3) power/toughness
sub('''def power(state: GameState, p: Permanent) -> int:
    c = eff_card(p)
    m1 = p.ctr.get("minus1", 0)
''', '''def perm_subtypes(p: Permanent):
    """Subtipos de criatura do permanente: a Master, Transcendent troca todos por Mutant."""
    return {"Mutant"} if p.mutant else eff_card(p).subtypes


def power(state: GameState, p: Permanent) -> int:
    c = eff_card(p)
    m1 = p.ctr.get("minus1", 0)
    if p.base_pt is not None:
        return max(0, p.base_pt[0] + p.counters + p.temp_power - m1)
''')
sub('''def toughness(state: GameState, p: Permanent) -> int:
    c = eff_card(p)
    m1 = p.ctr.get("minus1", 0)
''', '''def toughness(state: GameState, p: Permanent) -> int:
    c = eff_card(p)
    m1 = p.ctr.get("minus1", 0)
    if p.base_pt is not None:
        return max(0, p.base_pt[1] + p.counters - m1)
''')
sub('if zomb and "Zombie" in eff_card(p).subtypes and ml is not None:', 'if zomb and "Zombie" in perm_subtypes(p) and ml is not None:')
sub('if has_perm(state, "Undead Alchemist") and "Zombie" in eff_card(p).subtypes:', 'if has_perm(state, "Undead Alchemist") and "Zombie" in perm_subtypes(p):')
sub('cands = [p for p in victims if "Insect" in eff_card(p).subtypes and p.uid not in saved and is_creature(p)]', 'cands = [p for p in victims if "Insect" in perm_subtypes(p) and p.uid not in saved and is_creature(p)]')
# 4) prioridades
sub('''    "Riverchurn Monument": 57, "Jace, Wielder of Mysteries": 66,
''', '''    "Riverchurn Monument": 57, "Jace, Wielder of Mysteries": 66, "Agent Frank Horrigan": 71, "The Master, Transcendent": 67,
''')
# 5) campos de estado
sub('''    riverchurn_enter_turn: Optional[int] = None''', '''    horrigan_enter_turn: Optional[int] = None     # turno em que o Horrigan entrou pela 1a vez (indicadores ate' T6..T8)
    horrigan_etb_prolifs: int = 0
    horrigan_attack_prolifs: int = 0
    horrigan_attacks: int = 0
    horrigan_attack_damage: int = 0
    master_enter_turn: Optional[int] = None
    master_activations: int = 0
    master_act_mine: int = 0                      # alvo: criatura MINHA milada neste turno
    master_act_opp: int = 0                       # alvo: criatura de OPONENTE milada neste turno (corpo generico 3/3)
    master_act_on_opp_turn: int = 0
    master_etb_rad: int = 0
    master_no_target_checks: int = 0              # varreduras da habilidade sem alvo (Master pronta, nada milado)
    master_names: dict = field(default_factory=dict)
    milled_mine: list = field(default_factory=list)            # [(nome, turn_id)]: criaturas MINHAS milladas (alvo legal da Master no mesmo turno)
    milled_opp_creatures: dict = field(default_factory=dict)   # {idx: (turn_id, n)}: criaturas milladas do oponente neste turn_id
    prolif_by_source: dict = field(default_factory=dict)
    prolif_counters_by_source: dict = field(default_factory=dict)
    prolif_rad_by_source: dict = field(default_factory=dict)
    riverchurn_enter_turn: Optional[int] = None''')
# 6) proliferate x N
sub('''def proliferate(state: GameState, source: str = ""):''', '''def proliferate(state: GameState, source: str = "", times: int = 1):''')
sub('''    state.proliferates_total += 1
    times = 1 + count_named(state, "Tekuthal, Inquiry Dominus")      # candidata: "proliferate twice"
    for _ in range(times):
        for p in list(state.battlefield):
            if p not in state.battlefield:
                continue
            if p.counters > 0 and is_creature(p):
                place_counters(state, p, 1, source="proliferate")
            for kind in ("quest", "influence", "loyalty", "charge"):
                if p.ctr.get(kind, 0) > 0:
                    if kind == "loyalty" and "planeswalker" in p.card.types:
                        place_counters(state, p, 1, kind=kind, source="proliferate")
                    elif kind != "loyalty":
                        place_counters(state, p, 1, kind=kind, source="proliferate")
        for o in alive_opps(state):
            if o.rad > 0:
                o.rad += 1
                state.rad_counters_given_opp_total += 1
''', '''    state.proliferates_total += 1
    state.prolif_by_source[source] = state.prolif_by_source.get(source, 0) + 1
    times = times * (1 + count_named(state, "Tekuthal, Inquiry Dominus"))      # Tekuthal (candidata): "proliferate twice instead"; Horrigan: "proliferate twice" (2 escolhas independentes, ruling 2024-03-08)
    for _ in range(times):
        for p in list(state.battlefield):
            if p not in state.battlefield:
                continue
            if p.counters > 0 and is_creature(p):
                k = place_counters(state, p, 1, source="proliferate")
                state.prolif_counters_by_source[source] = state.prolif_counters_by_source.get(source, 0) + k
            for kind in ("quest", "influence", "loyalty", "charge"):
                if p.ctr.get(kind, 0) > 0:
                    if kind == "loyalty" and "planeswalker" in p.card.types:
                        place_counters(state, p, 1, kind=kind, source="proliferate")
                    elif kind != "loyalty":
                        place_counters(state, p, 1, kind=kind, source="proliferate")
        for o in alive_opps(state):
            if o.rad > 0:
                o.rad += 1
                state.rad_counters_given_opp_total += 1
                state.prolif_rad_by_source[source] = state.prolif_rad_by_source.get(source, 0) + 1
''')
# 7) ETB
sub('''    if "jace_wom" in t:
        p.ctr["loyalty"] = 4
''', '''    if "jace_wom" in t:
        p.ctr["loyalty"] = 4
    if "horrigan" in t:
        # "Whenever Agent Frank Horrigan enters or attacks, proliferate twice."
        if state.horrigan_enter_turn is None:
            state.horrigan_enter_turn = state.turn
        state.horrigan_etb_prolifs += 1
        proliferate(state, "horrigan_etb", times=2)
    if "master_t" in t:
        # "When The Master enters, target player gets two rad counters."
        if state.master_enter_turn is None:
            state.master_enter_turn = state.turn
        o = pick_rad_target(state)
        if o is not None:
            commit_crime(state, "master_t_etb")
            give_rad(state, o.idx, 2)
            state.master_etb_rad += 1
''')
# 8) ataque
sub('''    for p in attackers:
        if p not in state.battlefield:
            continue
        t = eff_card(p).tags
        if "mentor" in t:''', '''    for p in attackers:
        if p not in state.battlefield:
            continue
        t = eff_card(p).tags
        if "horrigan" in t:
            # "Whenever Agent Frank Horrigan enters or attacks, proliferate twice." + "has indestructible as long as it attacked this turn" (vale desde que e' declarado atacante, ruling)
            p.attacked_turn_id = state.turn_id
            state.horrigan_attacks += 1
            state.horrigan_attack_prolifs += 1
            proliferate(state, "horrigan_attack", times=2)
            if state.game_over or p not in state.battlefield:
                continue
            state.horrigan_attack_damage += power(state, p)
        if "mentor" in t:''')
# 9) indestrutivel
sub('''def try_protect_from_destroy(state: GameState, victims: list, spell_mv: int, noncreature: bool = True) -> set:''', '''def is_indestructible(state: GameState, p: Permanent) -> bool:
    """Horrigan: indestrutivel enquanto atacou NESTE turno (turn_id); nos turnos dos oponentes nao vale (ele atacou no meu)."""
    return "horrigan" in eff_card(p).tags and p.attacked_turn_id == state.turn_id


def try_protect_from_destroy(state: GameState, victims: list, spell_mv: int, noncreature: bool = True) -> set:
    indestr = {p.uid for p in victims if is_indestructible(state, p)}
    if not indestr:
        return _try_protect_from_destroy(state, victims, spell_mv, noncreature)
    rest = [p for p in victims if p.uid not in indestr]
    if not rest:
        return indestr
    return _try_protect_from_destroy(state, rest, spell_mv, noncreature) | indestr


def _try_protect_from_destroy(state: GameState, victims: list, spell_mv: int, noncreature: bool = True) -> set:''')
# 10) remove_permanent: criatura de oponente volta ao cemiterio dele
sub('''    had_minus = perm.ctr.get("minus1", 0) > 0
    put_card_into_graveyard(state, name, "battlefield", sacrificed=sacrificed)''', '''    if "opp_card" in perm.card.tags:
        state.opps[max(0, perm.owner_idx - 1)].graveyard.append("C")        # a carta e' DO OPONENTE: vai ao cemiterio dele, nao ao meu
        return
    had_minus = perm.ctr.get("minus1", 0) > 0
    put_card_into_graveyard(state, name, "battlefield", sacrificed=sacrificed)''')
# 11) rastreio de "milada neste turno"
sub('''            creature_cards += sum(1 for c in cards if "creature" in CARD_DB[c].types)
            state.library_min = min(state.library_min, len(state.library))''', '''            creature_cards += sum(1 for c in cards if "creature" in CARD_DB[c].types)
            for c in cards:
                if "creature" in CARD_DB[c].types and not CARD_DB[c].token:
                    state.milled_mine.append((c, state.turn_id))
            state.library_min = min(state.library_min, len(state.library))''')
sub('''            cc = sum(1 for c in cards if c == "C")
            creature_cards += cc
            opp_creature_cards += cc''', '''            cc = sum(1 for c in cards if c == "C")
            creature_cards += cc
            opp_creature_cards += cc
            if cc:
                tid, n0 = state.milled_opp_creatures.get(pl, (-1, 0))
                state.milled_opp_creatures[pl] = (state.turn_id, (n0 if tid == state.turn_id else 0) + cc)''')
# 12) habilidade da Master
sub('''def jace_removal_roll(state: GameState):''', '''MASTER_OPP_TURN = True       # usa a habilidade tambem no turno dos oponentes (instante; a Master so' desvira no meu untap)
MASTER_TAKE_OPP = True       # pode levar criatura milada do cemiterio de OPONENTE (corpo generico 3/3 sem habilidades: piso)


def master_ready(state: GameState, p: Permanent) -> bool:
    if p.tapped or p not in state.battlefield or not is_creature(p):
        return False
    return p.entered_turn < state.turn or has_haste(state, p)       # criatura com {T}: doenca de invocacao (Swiftfoot Boots da' haste)


def master_candidates(state: GameState) -> list:
    out = []
    for name, tid in state.milled_mine:
        if tid == state.turn_id and name in state.graveyard:
            out.append(("mine", name, graveyard_value(state, name)))
    if MASTER_TAKE_OPP:
        for pl, (tid, n) in sorted(state.milled_opp_creatures.items()):
            if tid == state.turn_id and state.opps[pl - 1].graveyard.count("C") > 0 and n > 0 and not state.opps[pl - 1].eliminated:
                out.append(("opp", pl, 50.0))
    return out


def act_master(state: GameState) -> bool:
    """The Master, Transcendent: "{T}: Put target creature card in a graveyard that was milled this turn onto the battlefield under your control. It's a green Mutant with base
    power and toughness 3/3. (It loses its other colors and creature types.)" Alvo em QUALQUER cemiterio; so' 'mill' (ruling 2024-03-08)."""
    ms = [p for p in perms_named(state, "The Master, Transcendent") if master_ready(state, p)]
    if not ms or state.game_over:
        return False
    cands = master_candidates(state)
    if not cands:
        state.master_no_target_checks += 1
        return False
    kind, who, _ = max(cands, key=lambda c: (c[2], str(c[1])))
    m_perm = ms[0]
    m_perm.tapped = True
    state.master_activations += 1
    if state.turn_id != getattr(state, "_my_turn_id", state.turn_id):
        pass
    if kind == "mine":
        state.graveyard.remove(who)
        graveyard_leave(state, [who])
        q = mk_perm(state, who)
        state.master_act_mine += 1
        state.master_names[who] = state.master_names.get(who, 0) + 1
    else:
        o = state.opps[who - 1]
        o.graveyard.remove("C")
        tid, n = state.milled_opp_creatures[who]
        state.milled_opp_creatures[who] = (tid, n - 1)
        q = mk_perm(state, "Opponent Creature Card")
        q.owner_idx = who
        state.master_act_opp += 1
        state.master_names["(oponente)"] = state.master_names.get("(oponente)", 0) + 1
    q.base_pt = (3, 3)
    q.mutant = True
    state.battlefield.append(q)
    enter_permanent_triggers(state, q, from_cast=False)
    return True


def jace_removal_roll(state: GameState):''')
sub('''ACTIONS = (act_saga_construct, act_ashiok, act_jace, act_cauldron,''', '''ACTIONS = (act_saga_construct, act_ashiok, act_jace, act_master, act_cauldron,''')
# 13) no turno do oponente, depois do rad dele
sub('''    # rad no inicio da fase principal 1
    rad_trigger_opp(state, o)
    if o.eliminated or state.game_over:
        return
''', '''    # rad no inicio da fase principal 1
    rad_trigger_opp(state, o)
    if o.eliminated or state.game_over:
        return
    if MASTER_OPP_TURN and has_perm(state, "The Master, Transcendent") and act_master(state):
        state.master_act_on_opp_turn += 1
''')
open(p, "w", encoding="utf-8").write(s)
print("ok", len(s))

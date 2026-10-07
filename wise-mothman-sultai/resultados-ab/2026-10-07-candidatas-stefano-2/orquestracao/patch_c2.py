"""Patch das 6 candidatas (Fractured Sanity, Screeching Scorchbeast, Inexorable Tide, Branching Evolution, Loading Zone, The Earth Crystal) sobre o simulador do Mothman com Horrigan/Master (HM).
Uso: python3 patch_c2.py <arquivo.py> (edita no lugar). Cada `sub` confere que a ancora existe UMA vez."""
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:100])
    s = s.replace(old, new)

# 1) cartas e ficha
sub('add("Opponent Creature Card", ""', '''add("Fractured Sanity", "{U}{U}{U}", {"sorcery"}, {"fractured_sanity"})        # candidatas de 2026-10-07 (lista do Stefano): resultados-ab/2026-10-07-candidatas-stefano-2
add("Screeching Scorchbeast", "{4}{B}{B}", {"creature"}, {"scorchbeast", "flying", "menace"}, 5, 5, subtypes={"Bat", "Mutant"})
add("Inexorable Tide", "{3}{U}{U}", {"enchantment"}, {"inex_tide"})
add("Branching Evolution", "{2}{G}", {"enchantment"}, {"branching_evo"})
add("Loading Zone", "{3}{G}", {"enchantment"}, {"loading_zone"})
add("The Earth Crystal", "{2}{G}{G}", {"artifact"}, {"earth_crystal"}, legendary=True)
add("Opponent Creature Card", ""''')
sub('add("Zombie Token", "", {"creature"}, {"token"}, 2, 2, token=True, subtypes={"Zombie"})', '''add("Zombie Token", "", {"creature"}, {"token"}, 2, 2, token=True, subtypes={"Zombie"})
add("Zombie Mutant Token", "", {"creature"}, {"token"}, 2, 2, token=True, subtypes={"Zombie", "Mutant"})''')
# 2) prioridades de conjuracao (convencao, sem sensibilidade)
sub('"Agent Frank Horrigan": 71, "The Master, Transcendent": 67,', '"Agent Frank Horrigan": 71, "The Master, Transcendent": 67,\n    "Fractured Sanity": 64, "Screeching Scorchbeast": 70, "Inexorable Tide": 60, "Branching Evolution": 70, "Loading Zone": 58, "The Earth Crystal": 61,')
# 3) campos
sub('    owner_idx: int = 0                 # Opponent Creature Card: de qual oponente veio (volta ao cemiterio dele)\n', '    owner_idx: int = 0                 # Opponent Creature Card: de qual oponente veio (volta ao cemiterio dele)\n    warped: bool = False               # Loading Zone conjurada com Warp {G}: exila no proximo end step\n')
sub('    prolif_by_source: dict = field(default_factory=dict)\n', '''    prolif_by_source: dict = field(default_factory=dict)
    fractured_casts: int = 0
    fractured_cycles: int = 0
    scorch_enter_turn: Optional[int] = None
    scorch_attacks: int = 0
    scorch_rad_self: int = 0
    scorch_token_events: int = 0
    scorch_tokens: int = 0
    scorch_skipped: int = 0
    scorch_used: dict = field(default_factory=dict)            # uid -> turn_id em que criou os Zumbis ("only once each turn")
    tide_enter_turn: Optional[int] = None
    tide_triggers: int = 0
    branching_enter_turn: Optional[int] = None
    loading_enter_turn: Optional[int] = None
    crystal_enter_turn: Optional[int] = None
    crystal_activations: int = 0
    crystal_counters: int = 0
    crystal_discount_total: int = 0
    warp_casts: int = 0
    warp_exiled: int = 0
    warp_recasts: int = 0
    warp_exile: list = field(default_factory=list)             # [(nome, turno em que foi exilada)]: pode ser conjurada do exilio em turno posterior
''')
# 4) ETB: turno de entrada de cada carta
sub('''    if "master_t" in t:
        # "When The Master enters, target player gets two rad counters."''', '''    for _tag, _campo in (("scorchbeast", "scorch_enter_turn"), ("inex_tide", "tide_enter_turn"), ("branching_evo", "branching_enter_turn"), ("loading_zone", "loading_enter_turn"), ("earth_crystal", "crystal_enter_turn")):
        if _tag in t and getattr(state, _campo) is None:
            setattr(state, _campo, state.turn)
    if "master_t" in t:
        # "When The Master enters, target player gets two rad counters."''')
# 5) dobradores: Branching Evolution e The Earth Crystal ("twice that many +1/+1 counters"); Loading Zone ja' estava (todos os tipos, so' criatura)
sub('count_named(state, "Primal Vigor") + count_named(state, "Shang-Chi, Martial Mentor"))', 'count_named(state, "Primal Vigor") + count_named(state, "Shang-Chi, Martial Mentor")\n                           + count_named(state, "Branching Evolution") + count_named(state, "The Earth Crystal"))')
# 6) persist (Glen Elendra): o -1/-1 que ela poe em si passa pelos substituidores (Constrictor +1; Loading Zone x2: "twice that many of each of those kinds") e, se a tenacidade chegar a 0,
#    ela MORRE antes de qualquer gatilho de entrada (CR 704.5f; tem -1/-1: sem persist). Chave PERSIST_ZERO_TOUGHNESS_DIES (False = comportamento anterior, bit a bit).
sub('''        q.ctr["minus1"] = 1 + count_named(state, "Winding Constrictor")      # Constrictor: +1 de cada tipo de contador
        state.battlefield.append(q)
        state.persist_returns += 1
        on_counters_placed(state, q, q.ctr["minus1"], "-1/-1", "persist")     # Hollowmurk Sultai / Danny: 'a counter is put on a creature you control' (de qualquer tipo)
''', '''        _pl, _mu = counter_modifiers(state, q, "-1/-1")
        q.ctr["minus1"] = (1 + _pl) * _mu      # Constrictor: +1 de cada tipo de contador; Loading Zone: dobra (igual a 1 + Constrictor sem esse dobrador)
        state.battlefield.append(q)
        state.persist_returns += 1
        on_counters_placed(state, q, q.ctr["minus1"], "-1/-1", "persist")     # Hollowmurk Sultai / Danny: 'a counter is put on a creature you control' (de qualquer tipo)
        if PERSIST_ZERO_TOUGHNESS_DIES and toughness(state, q) <= 0:
            state.persist_zero_deaths += 1
            remove_permanent(state, q, "dies")                                 # 0/0: morre como ESB, antes dos gatilhos de entrada (Henge ainda compra; o contador +1/+1 se perde)
''')
sub('    persist_returns: int = 0', '    persist_returns: int = 0\n    persist_zero_deaths: int = 0')
# 7) custo: Warp {G} e The Earth Crystal (verdes custam {1} a menos: so' o generico)
sub('''    if face == "adventure":                                  # Fetch Quest {5}{G}{G}
        g, pips = 5, (frozenset("G"), frozenset("G"))''', '''    if face == "adventure":                                  # Fetch Quest {5}{G}{G}
        g, pips = 5, (frozenset("G"), frozenset("G"))
    elif face == "warp":                                     # Loading Zone: Warp {G}
        g, pips = 0, (frozenset("G"),)''')
sub('''        g = max(0, g - red)
    return g, pips''', '''        g = max(0, g - red)
    n_ec = count_named(state, "The Earth Crystal")
    if n_ec and g > 0 and any("G" in pp for pp in pips):
        # "Green spells you cast cost {1} less to cast." (ruling 2025-06-06: so' o generico do custo total; uma carta com pip hibrido {G/U} e' verde)
        g = max(0, g - n_ec)
    return g, pips''')
# 8) conjuracao: gatilho "whenever you cast" (Inexorable Tide) em TODOS os 4 pontos; label do Warp; face warp
sub('''    key = name if face == "front" else name + " [aventura]"''', '''    key = name if face == "front" else name + (" [warp]" if face == "warp" else " [aventura]")''')
assert s.count("state.spells_cast_this_turn += 1\n") == 4, s.count("state.spells_cast_this_turn += 1\n")
s = re.sub(r"^(\s*)state\.spells_cast_this_turn \+= 1\n", lambda m: f"{m.group(1)}state.spells_cast_this_turn += 1\n{m.group(1)}on_my_spell_cast(state, name)\n", s, flags=re.M)
sub('''    p = mk_perm(state, name)
    if "ballista" in tags:
        plus, mult = counter_modifiers(state, p, "+1/+1")''', '''    p = mk_perm(state, name)
    if face == "warp":
        p.warped = True
        state.warp_casts += 1
    if "ballista" in tags:
        plus, mult = counter_modifiers(state, p, "+1/+1")''')
sub('''    tags = CARD_DB[name].tags
    if "natures_lore" in tags or "three_visits" in tags:''', '''    tags = CARD_DB[name].tags
    if "fractured_sanity" in tags:
        # "Each opponent mills fourteen cards." (nao mira: nao e' crime) - UM evento de mill simultaneo (um gatilho do Mothman, uma do Scorchbeast...)
        state.fractured_casts += 1
        parts = [(o.idx, 14) for o in alive_opps(state)]
        if parts:
            mill_event(state, parts, source="fractured_sanity")
        return
    if "natures_lore" in tags or "three_visits" in tags:''')
sub('''    for name in state.adventure_exile:
        if can_cast_name(state, name):
            cands.append((name, "exile", "front"))''', '''    for name in state.adventure_exile:
        if can_cast_name(state, name):
            cands.append((name, "exile", "front"))
    for name, t_exiled in state.warp_exile:
        if t_exiled < state.turn and can_cast_name(state, name):
            cands.append((name, "warpexile", "front"))             # Warp: "you may cast it from exile on a later turn" (custo cheio)''')
sub('''        if can_cast_name(state, name):
            cands.append((name, "hand", "front"))
        if "bramble" in tags and safe_self_mill(state, 7):''', '''        if can_cast_name(state, name):
            cands.append((name, "hand", "front"))
        elif "loading_zone" in tags and creatures(state) and can_pay(state, 0, (frozenset("G"),), c):
            cands.append((name, "hand", "warp"))                  # Warp {G} (politica: so' quando o custo cheio nao cabe e ha criatura para receber contador)
        if "bramble" in tags and safe_self_mill(state, 7):''')
sub('''        ok = cast_card(state, name, x=choose_x(state, name) if CARD_DB[name].is_x else 0, zone="hand", face=face if face == "adventure" else "front")''', '''        ok = cast_card(state, name, x=choose_x(state, name) if CARD_DB[name].is_x else 0, zone="hand", face=face if face in ("adventure", "warp") else "front")''')
sub('''    elif zone == "exile":
        state.adventure_exile.remove(name)''', '''    elif zone == "warpexile":
        item = next(i for i in state.warp_exile if i[0] == name)
        state.warp_exile.remove(item)
        ok = cast_card(state, name, zone="exile")
        if ok:
            state.warp_recasts += 1
        else:
            state.warp_exile.append(item)
    elif zone == "exile":
        state.adventure_exile.remove(name)''')
sub('''"adventure" if face == "adventure" else "front")
            if res and sc < 60''', '''face if face in ("adventure", "warp") else "front")
            if res and sc < 60''')
sub('''    if face == "adventure":
        return 58.0''', '''    if face == "adventure":
        return 58.0
    if face == "warp":
        return 44.0''')
# 9) end step: Warp exila no PROXIMO end step
sub('''def end_step(state: GameState):
    palantir_end_step(state)''', '''def end_step(state: GameState):
    for _w in [q for q in state.battlefield if q.warped]:
        state.battlefield.remove(_w)                                      # "Exile this permanent at the beginning of the next end step"
        state.warp_exile.append((_w.card.name, state.turn))
        state.warp_exiled += 1
    palantir_end_step(state)''')
# 10) Scorchbeast: gatilho de "milled" (depois da Mirelurk Queen, antes do Zellix) e de ataque
sub('''    # --- Zellix: "Whenever a player mills one or more creature cards, you create a 1/1 black Horror creature token."''', '''    # --- Screeching Scorchbeast: "Whenever one or more nonland cards are milled, you may create that many 2/2 black Zombie Mutant creature tokens. Do this only once each turn." (qualquer jogador;
    #     ruling: "you may" na resolucao: se nao criar, o gatilho volta a disparar; politica: crio quando o evento tem >= SCORCH_MIN_X cartas)
    if nonland_total > 0:
        for sb in perms_named(state, "Screeching Scorchbeast"):
            if state.scorch_used.get(sb.uid) == state.turn_id:
                continue
            if nonland_total >= SCORCH_MIN_X:
                state.scorch_used[sb.uid] = state.turn_id
                state.scorch_token_events += 1
                for _ in range(nonland_total):
                    if state.game_over:
                        break
                    create_token(state, "Zombie Mutant Token")
                    state.scorch_tokens += 1
            else:
                state.scorch_skipped += 1
    # --- Zellix: "Whenever a player mills one or more creature cards, you create a 1/1 black Horror creature token."''')
sub('''        if "horrigan" in t:
            # "Whenever Agent Frank Horrigan enters or attacks, proliferate twice."''', '''        if "scorchbeast" in t:
            # "Whenever this creature attacks, each player gets two rad counters." (eu tambem: Constrictor soma +1 nos MEUS)
            state.scorch_attacks += 1
            give_rad(state, 0, 2)
            state.scorch_rad_self += 2
            for o in alive_opps(state):
                give_rad(state, o.idx, 2)
        if "horrigan" in t:
            # "Whenever Agent Frank Horrigan enters or attacks, proliferate twice."''')
# 11) resiliencia: as novas pecas entram na lista de alvos da remocao de oponente (depois da Muldrotha, junto de Master/Horrigan)
sub('"The Master, Transcendent", "Agent Frank Horrigan",\n', '"The Master, Transcendent", "Agent Frank Horrigan", "Screeching Scorchbeast", "Branching Evolution", "The Earth Crystal", "Loading Zone", "Inexorable Tide",\n')
# 12) acoes: ciclar a Fractured Sanity, ativar a The Earth Crystal
sub('ACTIONS = (act_saga_construct, act_ashiok, act_jace, act_master, act_cauldron,', 'ACTIONS = (act_saga_construct, act_ashiok, act_jace, act_master, act_fractured_cycle, act_earth_crystal, act_cauldron,')
sub('''def jace_removal_roll(state: GameState):''', '''PERSIST_ZERO_TOUGHNESS_DIES = True   # Glen Elendra volta do persist com tenacidade 0 (Constrictor: 2 contadores; Loading Zone: 2): morre (CR 704.5f). False = o 0/0 ficava em campo (antigo)
SCORCH_MIN_X = 3             # Scorchbeast: cria os Zumbis no 1o evento de mill do turno com >= X cartas nao-terreno (senao espera: o gatilho volta)


def on_my_spell_cast(state: GameState, name: str):
    """"Whenever you cast a spell": Inexorable Tide ("proliferate"); o gatilho resolve ANTES da magia (ruling 2011-01-01). Chamada nos 4 pontos de conjuracao."""
    for _ in range(count_named(state, "Inexorable Tide")):
        state.tide_triggers += 1
        proliferate(state, "inexorable_tide")


def act_fractured_cycle(state: GameState) -> bool:
    """Fractured Sanity: Cycling {1}{U}; "When you cycle this card, each opponent mills four cards." (resolve ANTES da compra, ruling 2021-06-18). Politica: cicla quando o UUU nao fecha
    (menos de 3 fontes de {U} em campo) e ha mana de sobra; senao a conjuro (sorcery) no loop de conjuracao."""
    if "Fractured Sanity" not in state.hand or not alive_opps(state) or state.game_over:
        return False
    if can_cast_name(state, "Fractured Sanity"):
        return False
    n_u = sum(1 for q in lands_in_play(state) if "U" in eff_card(q).produces)
    if n_u >= 3 and state.turn < 9:
        return False
    if SELF_MILL_GUARD_ENABLED and library_budget(state) < 1:
        return False
    U = frozenset("U")
    if not afford(state, 1, (U,)):
        return False
    spend(state, 1, (U,))
    state.hand.remove("Fractured Sanity")
    state.fractured_cycles += 1
    put_card_into_graveyard(state, "Fractured Sanity", "hand")
    mill_event(state, [(o.idx, 4) for o in alive_opps(state)], source="fractured_cycle")
    if not state.game_over:
        draw_cards(state, 1, source="cycling")
    return True


def act_earth_crystal(state: GameState) -> bool:
    """The Earth Crystal: "{4}{G}{G}, {T}: Distribute two +1/+1 counters among one or two target creatures you control." (cada alvo recebe pelo menos 1; ruling 2025-06-06).
    Dois alvos quando ha (cada um passa pelos amplificadores/dobradores), um so' se so' ha uma criatura."""
    for c in perms_named(state, "The Earth Crystal"):
        if c.tapped or not creatures(state):
            continue
        G = frozenset("G")
        c.tapped = True
        if not afford(state, 4, (G, G)):
            c.tapped = False
            continue
        spend(state, 4, (G, G))
        alvos = sorted(creatures(state), key=lambda q: (-counter_target_value(state, q), q.uid))[:2]
        state.crystal_activations += 1
        if len(alvos) == 1:
            state.crystal_counters += place_counters(state, alvos[0], 2, source="earth_crystal")
        else:
            for q in alvos:
                state.crystal_counters += place_counters(state, q, 1, source="earth_crystal")
        return True
    return False


def jace_removal_roll(state: GameState):''')
open(p, "w", encoding="utf-8").write(s)
print("ok c2", len(s))

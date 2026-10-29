"""Harness dos wipes/efeitos de SACRIFICIO em massa no simulador do Vihaan, SEM alterar vihaan_goldfish_v1.py (nenhuma dessas cartas esta na lista: avaliacao pedida pelo usuario em 2026-10-04,
"algum wipe de sacrificio valido no deck muda esses numeros e avaliacao?"). Oraculos e rulings lidos ao vivo em ../dados/oraculo_candidatas_rulings.json (resumos/oraculo_candidatas.txt).
Generaliza o `edict_harness.py` da rodada da Blasphemous Edict: UM executor de sacrificio simultaneo (`sacrificar`) e um resolvedor por carta.
So' o MEU lado e' modelado; o lado do oponente (quantas criaturas/permanentes ELE sacrifica e tudo que isso dispara: Mayhem Devil por permanente dele, Revel in Riches, Dictate) e' 📊.
Convencoes (as mesmas da rodada da Edict): o jogador escolhe sacrificar primeiro os Treasures animados, depois Constructs, fichas genericas, Dragoes e so' entao criaturas nomeadas de menor MV,
guardando por ultimo Vihaan, Mahadi e Mayhem Devil; Mayhem Devil dispara por CADA permanente sacrificado (de qualquer jogador; o proprio Mayhem Devil tambem, mortes simultaneas);
Mirkwood Bats so' em sacrificio de ficha; o custo e' pago primeiro com Treasures animados (OWN_WIPE_PAY_WITH_ANIMATED), exceto Winnowing (convoke: as criaturas pagam, nao morrem).
Uso: import sac_harness as H; H.instala(V) com V = modulo do simulador ja' carregado (e H.FASE = '1a main' | '2a main' antes de cada ensaio)."""
import json, lzma, os

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = json.load(lzma.open(os.path.join(AQUI, "..", "dados", "oraculo_lista_ao_vivo.json.xz"), "rt"))
ENGINES = ("Vihaan, Goldwaker", "Mahadi, Emporium Master", "Mayhem Devil")
FASE = "1a main"          # definido pelo ensaio: convoke so' conta criaturas desviradas (na 2a main so' as com vigilance do Vihaan)

# nome-da-variante: (MV impresso, {pips de cor}, tipo-de-fila)
ACT, EDICT = "Blasphemous Act", "Blasphemous Edict"
BIO13, BIOMOT, BIOFOD = "By Invitation Only [N=13]", "By Invitation Only [N=motores]", "By Invitation Only [N=fodder]"
BARTER, TERGRID, PRANK = "Barter in Blood", "Tergrid's Shadow", "Rankle's Prank [2 criaturas + 4 de vida]"
TASTE, HEX, LILIANA = "Taste of Death", "Necrotic Hex", "Liliana, Dreadhorde General [-4]"
ZODIARK, MEATHOOK = "Zodiark, Umbral God", "Meathook Massacre II [X max]"
MYTHOS, TRAGIC = "Mythos of Snapdax [B+R pagos]", "Tragic Arrogance"
WINNOW, SLAUGHTER = "Winnowing [convoke]", "Slaughter the Strong"
WINNOW2 = "Winnowing [convoke, guarda os animados]"
BM = "Blood Money"   # so' REFERENCIA (ja' existe no simulador): destroi todas as criaturas, Treasure virado por nao-ficha destruida
LIVING, SCRAP, DUST = "Living Death", "Scrap Mastery", "All Is Dust"
VARIANTES = [EDICT, BIO13, BIOMOT, BIOFOD, BARTER, TERGRID, PRANK, TASTE, HEX, LILIANA, ZODIARK, MEATHOOK, MYTHOS, TRAGIC, WINNOW, WINNOW2, SLAUGHTER, LIVING, SCRAP, DUST]
REFERENCIAS = [ACT, BM]   # cartas JA' na lista (o que sai numa troca): medidas com o simulador, nao pelo harness
MV = {EDICT: 5, BIO13: 5, BIOMOT: 5, BIOFOD: 5, BARTER: 4, TERGRID: 5, PRANK: 4, TASTE: 6, HEX: 7, LILIANA: 6, ZODIARK: 5, MEATHOOK: 4, MYTHOS: 4, TRAGIC: 5, WINNOW: 6, WINNOW2: 6,
      SLAUGHTER: 3, LIVING: 5, SCRAP: 5, DUST: 7}
PIPS = {ACT: ["R"], EDICT: ["B", "B"], BIO13: ["W", "W"], BIOMOT: ["W", "W"], BIOFOD: ["W", "W"], BARTER: ["B", "B"], TERGRID: ["B", "B"], PRANK: ["B", "B"], TASTE: ["B", "B"],
        HEX: ["B"], LILIANA: ["B", "B"], ZODIARK: ["B"] * 5, MEATHOOK: ["B"] * 4, MYTHOS: ["W", "W", "B", "R"], TRAGIC: ["W", "W"], WINNOW: ["W", "W"], WINNOW2: ["W", "W"], SLAUGHTER: ["W", "W"], BM: ["B", "B"],
        LIVING: ["B", "B"], SCRAP: ["R", "R"], DUST: []}


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- cache/tipos
def _face0(nome):
    return CACHE[nome]["type_line"].split(" // ")[0]


def tipos_criatura(nome):
    tl = _face0(nome)
    return set(tl.split("—", 1)[1].split()) if "—" in tl else set()


def poder(nome):
    p = CACHE[nome].get("power")
    if p is None and CACHE[nome].get("card_faces"):
        p = CACHE[nome]["card_faces"][0].get("power")
    return int(p) if p is not None and str(p).lstrip("-").isdigit() else 0


def cores(nome):
    c = CACHE[nome].get("colors")
    if not c and CACHE[nome].get("card_faces"):
        c = CACHE[nome]["card_faces"][0].get("colors")
    return list(c or [])


def produz(nome):
    c = CACHE[nome]
    p = set(c.get("produced_mana") or [])
    for f in c.get("card_faces") or []:
        p |= set(f.get("produced_mana") or [])
    return p & {"W", "B", "R"}


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- cores (castabilidade)
def fontes(V, state):
    """Uma entrada por fonte de mana que pode pagar W/B/R agora: terrenos em campo (menos os que entraram virados), Arcane Signet e Treasures desvirados (qualquer cor). Otimista: ignora
    o mana ja' gasto no turno e trata filter lands/Pathway pela uniao das cores."""
    f = []
    virados = set(state.tapped_lands_this_turn)
    for n in state.battlefield:
        if n in V.LAND_NAMES:
            if n in virados:
                continue
            cs = produz(n)
            if cs:
                f.append(frozenset(cs))
        elif n == "Arcane Signet":
            f.append(frozenset("WBR"))
    f += [frozenset("WBR")] * max(0, state.treasures - state.treasures_tapped)
    return f


def pips_ok(fonte, pips):
    pips = sorted(pips, key=lambda p: sum(1 for s in fonte if p in s))

    def rec(i, usadas):
        if i == len(pips):
            return True
        for j, s in enumerate(fonte):
            if j not in usadas and pips[i] in s:
                if rec(i + 1, usadas | {j}):
                    return True
        return False
    return rec(0, frozenset())


def cor_ok(V, state, nome):
    pips = PIPS.get(nome)
    if pips is None:
        return True
    if nome == EDICT and V.creatures_on_battlefield(state) >= 13:
        pips = ["B"]
    return pips_ok(fontes(V, state), pips)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- inventario / escolha
def inventario(V, state):
    nome = [n for n in state.battlefield if n not in V.LAND_NAMES]
    anim = min(state.treasures_animated_alive, state.treasures)
    return {"cre": [n for n in nome if V.is_creature_card(n)], "outros": [n for n in nome if not V.is_creature_card(n)], "con": state.constructs, "oth": state.other_tokens,
            "dra": state.dragons, "anim": anim, "inan": state.treasures - anim, "clues": state.clues, "foods": state.foods}


def total_criaturas(inv):
    return len(inv["cre"]) + inv["con"] + inv["oth"] + inv["dra"] + inv["anim"]


def escolhe_n(V, state, n):
    """Sacrifica `n` criaturas minhas: animados, Constructs, fichas, Dragoes, depois nomeadas de menor MV (motores por ultimo)."""
    inv = inventario(V, state)
    resto = max(0, n)
    sel = {"cre": [], "outros": [], "con": 0, "oth": 0, "dra": 0, "anim": 0, "inan": 0, "clues": 0, "foods": 0}
    for k in ("anim", "con", "oth", "dra"):
        t = min(inv[k], resto)
        sel[k] = t
        resto -= t
    nomeadas = sorted(inv["cre"], key=lambda x: (x in ENGINES, V.CARD_DB[x].mv))   # ordem estavel: empates de MV seguem a ordem do campo (igual ao edict_harness)
    sel["cre"] = nomeadas[:resto]
    return sel


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- executor de sacrificio simultaneo
def sacrificar(V, state, sel):
    """Sacrificio SIMULTANEO de `sel` (todas as pecas saem juntas; gatilhos olham pra tras). Devolve quantas permanentes foram sacrificadas."""
    cre, outros = list(sel.get("cre", [])), list(sel.get("outros", []))
    con, oth, dra, anim, inan = (sel.get(k, 0) for k in ("con", "oth", "dra", "anim", "inan"))
    clues, foods = sel.get("clues", 0), sel.get("foods", 0)
    total = len(cre) + len(outros) + con + oth + dra + anim + inan + clues + foods
    if total == 0:
        return 0
    V.begin_mass_death(state, cre)
    if "Mayhem Devil" in state.battlefield:
        V.drain(state, total)  # 1 de dano por permanente sacrificada (todas simultaneas: o Mayhem Devil ve todas, inclusive a propria)
    for c in cre:
        V.on_creature_dies(state, 1, is_token=False, dying=c)
        if V.is_artifact_card(c):
            V.on_artifact_dies(state, 1)
    for c in outros:
        if V.is_artifact_card(c):
            V.on_artifact_dies(state, 1)
    if con:
        V.on_creature_dies(state, con, is_token=True); V.on_artifact_dies(state, con); V.on_token_leaves(state, con, sacrificed=True)
    if oth:
        V.on_creature_dies(state, oth, is_token=True); V.on_token_leaves(state, oth, sacrificed=True)
    if dra:
        V.on_creature_dies(state, dra, is_token=True); V.on_token_leaves(state, dra, sacrificed=True)
    if anim:
        V.on_creature_dies(state, anim, is_token=True); V.on_artifact_dies(state, anim); V.on_token_leaves(state, anim, sacrificed=True)
    if inan:
        V.on_artifact_dies(state, inan); V.on_token_leaves(state, inan, sacrificed=True)
    for k in (clues, foods):
        if k:
            V.on_artifact_dies(state, k); V.on_token_leaves(state, k, sacrificed=True)
    V.end_mass_death(state)
    for c in cre + outros:
        state.battlefield.remove(c)
        state.creature_cast_turn.pop(c, None)
        if c == V.COMMANDER:
            state.commander_in_play = False
            state.own_wipe_commander_destroyed_total += 1
        else:
            state.graveyard.append(c)
        if c == "The Reaver Cleaver" or c == getattr(state, "reaver_cleaver_host", None):
            state.reaver_cleaver_equipped = False
            state.reaver_cleaver_host = None
    state.constructs -= con; state.constructs_sick = min(state.constructs_sick, state.constructs)
    state.other_tokens -= oth; state.other_tokens_sick = min(state.other_tokens_sick, state.other_tokens)
    state.dragons -= dra; state.dragons_sick = min(state.dragons_sick, state.dragons)
    state.clues -= clues
    state.foods -= foods
    if anim + inan:
        state.treasures -= anim + inan
        state.treasures_animated_alive = max(0, state.treasures_animated_alive - anim)
        state.treasures_tapped = min(state.treasures_tapped, state.treasures)
        state.treasures_sacrificed_total += anim + inan  # Captain Lannery Storm: "whenever you sacrifice a Treasure"
        state.treasures_sacrificed_this_turn += anim + inan
    return total


def n_minhas(sel):
    return len(sel["cre"]) + sel["con"] + sel["oth"] + sel["dra"] + sel["anim"]


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- resolvedores
def r_n(V, state, n):
    sel = escolhe_n(V, state, n)
    state._info = {"n_opp": n, "n_minhas": n_minhas(sel)}
    return sacrificar(V, state, sel)


def r_bio(V, state, pol):
    inv = inventario(V, state)
    if pol == "13":
        n = 13
    elif pol == "motores":
        n = max(0, total_criaturas(inv) - sum(1 for e in ENGINES if e in inv["cre"]))
    else:
        n = inv["con"] + inv["oth"] + inv["dra"] + inv["anim"]
    return r_n(V, state, n)


def r_prank(V, state):
    V.drain(state, 4, each_opp=True)  # modo "each player loses 4 life": cada oponente perde 4 (proxy)
    state.life -= 4
    return r_n(V, state, 2)


def r_taste(V, state):
    t = r_n(V, state, 3)
    total = 3 * (2 if "Anointed Procession" in state.battlefield else 1)
    if "Academy Manufactor" in state.battlefield:   # cada Food vira Treasure + Clue + Food
        V.create_treasures(state, 3, source="Taste of Death (Academy Manufactor)")
    else:
        state.foods += total; state.foods_created_total += total
        V.on_tokens_created(state, total, kind="food")
    return t


def r_hex(V, state):
    t = r_n(V, state, 6)
    V.create_other_tokens(state, 6, source="Necrotic Hex")  # seis Zumbis 2/2 (entram virados)
    return t


def r_liliana(V, state):
    t = r_n(V, state, 2)
    V.draw_cards(state, state._info["n_minhas"])  # "Whenever a creature you control dies, draw a card" (Liliana ja' esta em campo quando a habilidade resolve)
    return t


def r_zodiark(V, state):
    inv = inventario(V, state)
    return r_n(V, state, total_criaturas(inv) // 2)  # metade das criaturas nao-Deus, arredondada pra baixo (o Zodiark nao conta: e' Deus)


def x_meathook(V, state):
    """X maximo: custo {X}{X}{B}{B}{B}{B} = 4 + 2X, com X <= fodder que sobra depois de pagar com Treasures animados."""
    inv = inventario(V, state)
    tv = V.treasure_value(state)
    mana = V.remaining_mana(state)
    for x in range(min(inv["con"] + inv["oth"] + inv["dra"] + inv["anim"], (mana - 4) // 2), 0, -1):
        custo = 4 + 2 * x
        pagos = min(inv["anim"], (custo + tv - 1) // tv)
        if x <= inv["con"] + inv["oth"] + inv["dra"] + inv["anim"] - pagos:
            return x
    return 0


def r_meathook(V, state):
    inv = inventario(V, state)
    x = min(state._x_meathook, total_criaturas(inv))  # X escolhido no cast (`custo`); o que sobrou de criaturas depois de pagar com animados limita o que de fato e' sacrificado
    return r_n(V, state, x)


def r_manter_um(V, state):
    """Mythos of Snapdax (com {B}{R} gastos eu escolho por cada jogador) / Tragic Arrogance: guardo 1 artefato, 1 criatura, 1 encantamento (e 1 planeswalker: nenhum na lista); o resto
    dos permanentes nao-terreno e' sacrificado. Criatura guardada: Vihaan > Mahadi > Mayhem Devil > nomeada de maior MV > Treasure animado > outras fichas. Artefato (de preferencia um
    objeto DIFERENTE da criatura): Sol Ring > Ashnod's Altar > Krark-Clan Ironworks > Arcane Signet > Reaver Cleaver > outro nomeado > Treasure > Construct/Clue/Food; se so' sobra a propria
    criatura-artefato, ela serve de artefato E de criatura (ruling 2020-04-17 / 2015-06-22). Encantamento: Dictate of Erebos > Anointed Procession > Revel in Riches > outro."""
    inv = inventario(V, state)
    cre = inv["cre"]
    sel = {"cre": list(cre), "outros": list(inv["outros"]), "con": inv["con"], "oth": inv["oth"], "dra": inv["dra"], "anim": inv["anim"], "inan": inv["inan"], "clues": inv["clues"], "foods": inv["foods"]}

    def tira(g):
        if g[0] == "nome":
            (sel["cre"] if g[1] in sel["cre"] else sel["outros"]).remove(g[1])
        else:
            sel[g[1]] -= 1

    def eh_artefato(g):
        return V.is_artifact_card(g[1]) if g[0] == "nome" else g[1] in ("anim", "con", "inan", "clues", "foods")
    c_keep = next((("nome", e) for e in ENGINES if e in cre), None)
    if c_keep is None and cre:
        c_keep = ("nome", max(cre, key=lambda n: (V.CARD_DB[n].mv, n)))
    if c_keep is None:
        c_keep = next((("ficha", k) for k in ("anim", "con", "dra", "oth") if sel[k] > 0), None)
    if c_keep:
        tira(c_keep)
    nomeados_art = [n for n in sel["cre"] + sel["outros"] if V.is_artifact_card(n)]
    a_keep = next((("nome", p) for p in ("Sol Ring", "Ashnod's Altar", "Krark-Clan Ironworks", "Arcane Signet", "The Reaver Cleaver") if p in nomeados_art), None)
    if a_keep is None and nomeados_art:
        a_keep = ("nome", sorted(nomeados_art)[0])
    if a_keep is None:
        a_keep = next((("ficha", k) for k in ("inan", "anim", "con", "clues", "foods") if sel[k] > 0), None)
    if a_keep:
        tira(a_keep)
    enc = next((p for p in ("Dictate of Erebos", "Anointed Procession", "Revel in Riches") if p in sel["outros"]), None)
    if enc is None:
        encs = sorted(n for n in sel["outros"] if V.is_enchantment_card(n))
        enc = encs[0] if encs else None
    if enc:
        sel["outros"].remove(enc)
    state._info = {"n_opp": None, "n_minhas": n_minhas(sel), "guarda_cre": c_keep, "guarda_art": a_keep if a_keep else (c_keep if c_keep and eh_artefato(c_keep) else None), "guarda_enc": enc}
    return sacrificar(V, state, sel)


TIPOS_FICHA = {"anim": {"Construct", "Assassin"}, "con": {"Construct"}, "dra": {"Dragon"}, "oth": set()}


def r_winnowing(V, state, pol="vihaan"):
    """"For each player, you choose a creature that player controls. Each player sacrifices all other creatures they control that don't share a creature type with the chosen creature."
    Eu escolho a MINHA criatura-escolhida que maximiza (Vihaan sobrevive, Mahadi/Mayhem sobreviventes, total de sobreviventes). Tipos: nomeadas pelo type_line do Scryfall; Treasure animado = {Construct, Assassin}
    (oraculo do Vihaan); Construct = {Construct}; Dragao = {Dragon}; ficha generica = {} (conservador: so' a escolhida sobrevive)."""
    inv = inventario(V, state)
    cre = inv["cre"]
    escolhas = [("nome", n) for n in cre] + [("ficha", k) for k in ("anim", "con", "dra", "oth") if inv[k]]
    melhor = None
    for g in escolhas:
        t_esc = tipos_criatura(g[1]) if g[0] == "nome" else TIPOS_FICHA[g[1]]
        vn = [n for n in cre if (g[0] == "nome" and n == g[1]) or (tipos_criatura(n) & t_esc)]
        vt = {k: (inv[k] if (TIPOS_FICHA[k] & t_esc) else 0) for k in TIPOS_FICHA}
        if g[0] == "ficha":
            vt[g[1]] = max(vt[g[1]], 1)  # a propria escolhida sobrevive
        if pol == "vihaan":   # Vihaan primeiro (anima os Treasures), depois Mahadi/Mayhem, depois o total
            pont = (1 if V.COMMANDER in vn else 0, sum(1 for e in ENGINES[1:] if e in vn), len(vn) + sum(vt.values()), g[1])
        else:                 # "fichas": guardo o maior numero de fichas/animados (os Treasures animados valem mana), depois o Vihaan
            pont = (sum(vt.values()), 1 if V.COMMANDER in vn else 0, len(vn), g[1])
        if melhor is None or pont > melhor[0]:
            melhor = (pont, g, vn, vt)
    if melhor is None:
        state._info = {"n_opp": None, "n_minhas": 0}
        return 0
    _, g, vn, vt = melhor
    sel = {"cre": [n for n in cre if n not in vn], "outros": [], "con": inv["con"] - vt["con"], "oth": inv["oth"] - vt["oth"], "dra": inv["dra"] - vt["dra"], "anim": inv["anim"] - vt["anim"],
           "inan": 0, "clues": 0, "foods": 0}
    state._info = {"n_opp": None, "n_minhas": n_minhas(sel), "escolhida": g[1]}
    return sacrificar(V, state, sel)


def r_slaughter(V, state):
    """Cada jogador escolhe criaturas com poder total <= 4 e sacrifica o resto. Eu guardo, na ordem Vihaan > Mahadi > Mayhem Devil > nomeadas por poder > Treasure animado (3/3) > Dragao (5/5, nunca cabe)
    > Construct (1/1) > ficha generica (poder 1, suposicao), ate' somar 4. Poder das nomeadas: Scryfall."""
    inv = inventario(V, state)
    cap = 4
    sel = {"cre": list(inv["cre"]), "outros": [], "con": inv["con"], "oth": inv["oth"], "dra": inv["dra"], "anim": inv["anim"], "inan": 0, "clues": 0, "foods": 0}
    ordem = [n for n in ENGINES if n in inv["cre"]] + sorted((n for n in inv["cre"] if n not in ENGINES), key=lambda n: (-poder(n), n))
    for n in ordem:
        if poder(n) <= cap:
            cap -= poder(n)
            sel["cre"].remove(n)
    for k, p in (("anim", 3), ("con", 1), ("oth", 1)):
        while inv[k] and sel[k] > 0 and p <= cap:
            cap -= p
            sel[k] -= 1
    state._info = {"n_opp": None, "n_minhas": n_minhas(sel)}
    return sacrificar(V, state, sel)


def r_living(V, state):
    """Living Death: cada jogador exila as cartas de criatura do proprio cemiterio, sacrifica todas as criaturas e poe as exiladas em campo (so' as exiladas no 1o passo; as que acabaram de ser sacrificadas
    ficam no cemiterio)."""
    exiladas = [n for n in state.graveyard if V.is_creature_card(n)]
    for n in exiladas:
        state.graveyard.remove(n)
    inv = inventario(V, state)
    sel = {"cre": list(inv["cre"]), "outros": [], "con": inv["con"], "oth": inv["oth"], "dra": inv["dra"], "anim": inv["anim"], "inan": 0, "clues": 0, "foods": 0}
    state._info = {"n_opp": None, "n_minhas": n_minhas(sel), "reviveram": len(exiladas)}
    t = sacrificar(V, state, sel)
    for n in exiladas:
        V.enter_battlefield(state, n, from_hand=False)
        state.recursion_events_total += 1
    return t


def r_scrap(V, state):
    """Scrap Mastery: cada jogador exila as cartas de artefato do cemiterio, sacrifica TODOS os artefatos (inclusive Treasures, Constructs, Clues, Foods) e poe as exiladas em campo."""
    exiladas = [n for n in state.graveyard if V.is_artifact_card(n)]
    for n in exiladas:
        state.graveyard.remove(n)
    inv = inventario(V, state)
    arts = [n for n in inv["cre"] + inv["outros"] if V.is_artifact_card(n)]
    sel = {"cre": [n for n in arts if V.is_creature_card(n)], "outros": [n for n in arts if not V.is_creature_card(n)], "con": inv["con"], "oth": 0, "dra": 0, "anim": inv["anim"],
           "inan": inv["inan"], "clues": inv["clues"], "foods": inv["foods"]}
    state._info = {"n_opp": None, "n_minhas": n_minhas(sel), "reviveram": len(exiladas)}
    t = sacrificar(V, state, sel)
    for n in exiladas:
        V.enter_battlefield(state, n, from_hand=False)
        state.recursion_events_total += 1
    return t


def r_dust(V, state):
    """All Is Dust: sacrifica todos os permanentes COLORIDOS (nomeados com cor no Scryfall; Dragoes da Visitor sao vermelhos; ficha generica suposta colorida). Treasures, Constructs, Clues, Foods,
    terrenos e artefatos incolores ficam."""
    inv = inventario(V, state)
    cre = [n for n in inv["cre"] if cores(n)]
    outros = [n for n in inv["outros"] if cores(n)]
    sel = {"cre": cre, "outros": outros, "con": 0, "oth": inv["oth"], "dra": inv["dra"], "anim": 0, "inan": 0, "clues": 0, "foods": 0}
    state._info = {"n_opp": None, "n_minhas": n_minhas(sel)}
    return sacrificar(V, state, sel)


RESOLVEDORES = {
    EDICT: lambda V, s: r_n(V, s, 13), BIO13: lambda V, s: r_bio(V, s, "13"), BIOMOT: lambda V, s: r_bio(V, s, "motores"), BIOFOD: lambda V, s: r_bio(V, s, "fodder"),
    BARTER: lambda V, s: r_n(V, s, 2), TERGRID: lambda V, s: r_n(V, s, 2), PRANK: r_prank, TASTE: r_taste, HEX: r_hex, LILIANA: r_liliana, ZODIARK: r_zodiark,
    MEATHOOK: r_meathook, MYTHOS: r_manter_um, TRAGIC: r_manter_um, WINNOW: r_winnowing, WINNOW2: lambda V, s: r_winnowing(V, s, "fichas"), SLAUGHTER: r_slaughter, LIVING: r_living, SCRAP: r_scrap, DUST: r_dust,
}
SEM_PAGAR_COM_ANIMADOS = {WINNOW, WINNOW2}   # convoke: as criaturas pagam sem morrer


def custo(V, state, nome):
    if nome == EDICT:
        return 1 if V.creatures_on_battlefield(state) >= 13 else 5   # {B} no lugar de {3}{B}{B} se ha' 13 ou mais criaturas no campo (so' as minhas: piso)
    if nome == MEATHOOK:
        x = x_meathook(V, state)
        state._x_meathook = x
        return 4 + 2 * x if x >= 1 else 999
    if nome in (WINNOW, WINNOW2):
        inv = inventario(V, state)
        if FASE == "1a main":
            conv = total_criaturas(inv)
        else:
            conv = (inv["anim"] + sum(1 for n in inv["cre"] if V.is_outlaw(n))) if state.commander_in_play else 0   # vigilance do Vihaan: desviradas na 2a main
        return max(2, 6 - conv)
    return MV[nome]


def instala(V):
    for nome in VARIANTES:
        V.add(nome, MV[nome], "sorcery", {"wipe"})
        if nome not in SEM_PAGAR_COM_ANIMADOS and nome not in V.OWN_WIPES:
            V.OWN_WIPES = tuple(V.OWN_WIPES) + (nome,)
    orig_cost, orig_res = V.spell_cost, V.resolve_instant_sorcery

    def spell_cost(state, name):
        if name in RESOLVEDORES:
            return custo(V, state, name)
        return orig_cost(state, name)

    def resolve(state, name):
        if name in RESOLVEDORES:
            state.own_wipes_cast_total += 1
            state._info = {}
            RESOLVEDORES[name](V, state)
            return
        return orig_res(state, name)
    V.spell_cost, V.resolve_instant_sorcery = spell_cost, resolve
    return V


def invariantes(V, state):
    """Violacoes de consistencia do estado (contadores negativos, animados acima do estoque, fichas virando negativas, carta nomeada duplicada, comandante inconsistente...).
    NAO inclui 'doentes > total': `sacrifice_constructs`/`sacrifice_other_tokens` do simulador nunca decrementam os contadores de fichas "com doenca de invocacao" (so' o total), entao esse
    estado aparece em jogo normal (ex.: ETB do Sephiroth devolvido pelo Living Death sacrificando Constructs recem-criados); e' inofensivo porque os prontos sao `max(0, total - doentes)` e os
    doentes zeram no fim do turno. Medido (3.000 partidas): so' 12 (padrao) / 9 (resiliencia) jogos sacrificam fichas doentes ANTES do combate (0,3-0,4%), com 1 atacante a menos por evento."""
    import collections
    v = []
    if state.treasures < 0:
        v.append("treasures<0")
    if state.treasures_animated_alive > state.treasures:
        v.append("animados>estoque")
    if not 0 <= state.treasures_tapped <= state.treasures:
        v.append("virados fora de [0,estoque]")
    for k in ("constructs", "other_tokens", "dragons", "clues", "foods", "constructs_sick", "other_tokens_sick", "dragons_sick"):
        if getattr(state, k) < 0:
            v.append(k + "<0")
    cnt = collections.Counter(state.battlefield)
    if any(k > 1 and n not in ("Mountain", "Plains", "Swamp") for n, k in cnt.items()):
        v.append("carta duplicada no campo")
    if any(n in state.graveyard for n in cnt if n not in ("Mountain", "Plains", "Swamp")):
        v.append("carta no campo e no cemiterio")
    if (V.COMMANDER in state.battlefield) != state.commander_in_play:
        v.append("comandante inconsistente")
    return v

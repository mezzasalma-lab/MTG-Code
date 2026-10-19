"""
Goldfish simulator — Tam, the Possibility (WUBRG): superfriends (planeswalkers + proliferate + empower Jace)

Construido do zero em 2026-10-19, a pedido direto do usuario ("crie o simulador do deck e primeiro rode as simulacoes para ver como o deck assim roda!").
Passo 0 (CLAUDE.md, Regras #1/#3): oraculo e rulings de TODAS as 100 cartas (comandante + 99) lidos de `scryfall-cache/oracle-cache.json` (recorte em `tam_cartas.json`, gerado por
`resultados-ab/2026-10-19-simulador-baseline/orquestracao/gera_tam_cartas.py`) e de `resultados-ab/2026-10-19-simulador-baseline/dados/rulings_deck.json` (JSON do Scryfall + `rulings_uri`), nao de memoria.
Clausula-a-clausula: `checklist-oraculo.md`. Custo de mana, tipo, P/T e lealdade vem SO' do recorte do cache (nada digitado de memoria).

======================================================================
O QUE ESTE DECK FAZ — e como o motor reflete isso
======================================================================
Tam, the Possibility ({1}{G}{U}, 2/4): "Planeswalker spells you cast cost {1} less" (so' o generico) e "{W}{U}{B}{R}{G}, {T}: proliferate X times, X = tipos de planeswalker entre os planeswalkers que voce controla".
O deck e' um superfriends: 25 planeswalkers (21 tipos) + 8 "Way of the ..." (empower Jace N: cria/reforca a ficha de Jace e da' habilidades a TODOS os planeswalkers) + proliferate (Tam, Flux Channeler,
Ichormoon Gauntlet, Staff of Compleation, Vraska, Peacemaker, Dreamtide Whale, Ripples, Teferi's Talent) + dano por contador (All Will Be One) e por contagem de planeswalkers (Chandra, Legacy of Fire).
Por isso:
- TODA mudanca de lealdade passa por `put_counters`/`remove_loyalty` (um ponto so'), que dispara All Will Be One, e a lealdade e' rastreada de verdade (`perm.ctr["loyalty"]`), com UMA
  ativacao por planeswalker por turno (CR 606.3; duas com Oath of Teferi; mais uma por The Chain Veil; uma por turno de oponente com o emblema do Teferi, Temporal Archmage).
- As habilidades de lealdade sao DADOS (`PW_ABILITIES`) + efeito + pontuacao; as CONCEDIDAS (Ways, Ichormoon Gauntlet, Kiora, Sanctum Lurker, Kasmina, auras) entram no mesmo conjunto de candidatas
  de cada planeswalker (inclusive a ficha de Jace) e competem por UMA ativacao.
- Mana: pip a pip (correspondencia exata de cores) com fontes simples, multimana, filtros ({R/G},{T}: dois mana), conversores ({1},{T}: RG; {4},{T}: 4 de qualquer cor), mana restrito
  (so' magia lendaria / so' magia / so' planeswalker) e Orrery ("spend mana as though any color").

======================================================================
CONVENCOES DECLARADAS (premissas explicitas, nao ausencia de checagem)
======================================================================
- Mesa de 4 (NUM_OPPONENTS = 3), 40 de vida cada. Vitoria = todos os oponentes eliminados (vida <= 0 ou 10 contadores de veneno) = "mesa limpa". Oponentes PASSIVOS no modo padrao: compram,
  jogam terreno (cores dos terrenos deles: Exotic Orchard/Fellwar Stone) e magias de forma estatistica (so' quantas e MV: Dreamtide Whale conta a 2a magia de QUALQUER jogador). SEM tabuleiro de
  oponente no modo padrao (todo atacante conecta: convencao de todos os simuladores do repositorio).
- Habilidade que precisa de ALVO no tabuleiro do oponente (remocao, tap, bounce, roubar artefato) so' vale como metrica proxy `interaction_plays` quando `OPP_TARGET_PROB` diz que existe alvo
  (estrutural, citado no checklist); no modo de resiliencia ha tabuleiro de oponente (criaturas) e o efeito e' REAL.
- Regras de motor ja' validadas em outras rodadas (CLAUDE.md Regra #10): mulligan ESCOLHE o fundo (CR 103.5), imposto do comandante conta no cast (CR 903.8), upkeep antes do draw, terreno que entra
  virado jogado primeiro em T1/T2 quando nao custa desenvolvimento (ensaio a seco com copia profunda), fetch real (busca por SUBTIPO: a Yavimaya NAO faz carta de terreno na biblioteca virar Forest,
  ruling 2021-06-18), todo ponto de entrada de terreno por `put_land_onto_battlefield`.
- Determinismo: nenhuma iteracao de set/dict de str com ordem importando (usar listas/sorted); `PYTHONHASHSEED` nao pode mudar o resultado.
"""

import collections
import copy
import json
import math
import os
import random
import re
import statistics
from dataclasses import dataclass, field
from typing import Optional

AQUI = os.path.dirname(os.path.abspath(__file__))

# =========================================================
# CHAVES DE VARIANTE / PARAMETROS (A/B e sensibilidade)
# =========================================================
FETCH_LANDS_ENABLED = True
TAPPED_LAND_FIRST_ENABLED = True
TAPPED_LAND_FIRST_MAX_TURN = 2
TAPPED_LAND_FIRST_GHOST = False          # so' validacao: roda o ensaio mas joga o padrao (a chave ligada + GHOST == chave desligada prova que o ensaio nao tem efeito colateral)
NUM_OPPONENTS = 3
OPP_START_LIFE = 40
OPP_HAND_START = 7
OPP_SPELLS_PROB = {0: 0.10, 1: 0.55, 2: 0.35}    # a partir do 2o turno do oponente: P(0, 1, 2 magias por turno)
OPP_CREATURE_SPELL_FRACTION = 0.45
OPP_SPELL_MV = [1, 2, 3, 4, 5, 6]
OPP_SPELL_MV_W = [0.15, 0.25, 0.25, 0.17, 0.12, 0.06]
OPP_TARGET_PROB = 0.7                    # a partir do T3: P(o oponente tem alvo legal pra efeito que mira o tabuleiro dele) — premissa
OPP_TARGET_FROM_TURN = 3
OPP_CRIME_PROB_PER_NONCREATURE_SPELL = 0.25      # premissa (Patrolling Peacemaker): fracao das magias nao-criatura de oponente que mira outro jogador/permanente (crime) no modo padrao
OPP_NONPERMANENT_FRACTION = 0.6
ALL_ATTACKERS_COMBAT = True              # convencao do repositorio: ataca com toda criatura pronta, sempre (sem bloqueio no modo padrao)
SELF_LIFE_FLOOR = 10                     # nao pago vida opcional (choque, Staff, fetch) abaixo disto
TAM_ACTIVATE = True                      # chave: False = a Tam nunca usa a habilidade de proliferate (sensibilidade)
COMBO_EXECUTE = True                     # executa Orrery + Tezzeret + Chain Veil (loop infinito) quando ha' um pagamento de dano em campo (All Will Be One / Sanctum Lurker)
BASE_TURNS = 12

# =========================================================
# CARD DATABASE (do recorte do cache; tags e comportamento por NOME)
# =========================================================
_DATA = json.load(open(os.path.join(AQUI, "tam_cartas.json"), encoding="utf-8"))


@dataclass
class Card:
    name: str
    mv: int
    types: frozenset                       # {"creature","land","planeswalker","artifact","enchantment","instant","sorcery"}
    subtypes: frozenset = field(default_factory=frozenset)
    legendary: bool = False
    power: int = 0
    toughness: int = 0
    loyalty: int = 0
    generic: int = 0
    pips: tuple = ()                       # tuple de frozensets de cores aceitas por pip (hibrido = 2 cores)
    phy: int = 0                           # quantos pips sao phyrexianos ({G/P}, {B/P}): 2 de vida no lugar do mana
    colors: frozenset = field(default_factory=frozenset)
    tags: frozenset = field(default_factory=frozenset)
    token: bool = False
    text: str = ""
    land_types: frozenset = field(default_factory=frozenset)


CARD_DB: dict = {}
COLORS5 = ("W", "U", "B", "R", "G")


def parse_cost(cost: str):
    """({generic}, pips, n_phyrexian). Phyrexiano `{G/P}`: pip G + 2 de vida alternativo. Hibrido `{U/R}`: aceita as duas cores."""
    generic, pips, phy = 0, [], 0
    for sym in re.findall(r"\{([^}]+)\}", cost or ""):
        if sym.isdigit():
            generic += int(sym)
        elif sym.endswith("/P"):
            pips.append(frozenset(sym[0]))
            phy += 1
        elif "/" in sym:
            pips.append(frozenset(sym.split("/")))
        else:
            pips.append(frozenset(sym))
    return generic, tuple(pips), phy


def _types_of(type_line: str):
    head = type_line.split(" — ")[0]
    sub = type_line.split(" — ")[1].split() if " — " in type_line else []
    types = {t.lower() for t in head.split() if t not in ("Legendary", "Basic", "Snow")}
    return frozenset(types), frozenset(sub), "Legendary" in head.split()


# tags por carta (comportamento); o resto vem do oraculo
TAGS = {
    "Tam, the Possibility": {"commander", "tam"},
    "Birds of Paradise": {"dork", "flying"}, "Bloom Tender": {"dork"}, "Faeburrow Elder": {"dork", "vigilance"}, "Ignoble Hierarch": {"dork", "exalted"}, "Noble Hierarch": {"dork", "exalted"},
    "Sol Ring": {"rock"}, "Arcane Signet": {"rock"}, "Fellwar Stone": {"rock"},
    "Chromatic Orrery": {"orrery"}, "The Chain Veil": {"veil"}, "Ichormoon Gauntlet": {"gauntlet"}, "Staff of Compleation": {"staff"},
    "Leyline Immersion": {"aura", "immersion"}, "Teferi's Talent": {"aura", "talent"}, "Liliana's Talent": {"aura", "talent"},
    "Sanctum Lurker": {"lurker"}, "Kiora of Salt and Sand": {"kiora"}, "Displacer Kitten": {"kitten"}, "Flux Channeler": {"channeler"}, "Dreamtide Whale": {"whale", "vanishing"},
    "Patrolling Peacemaker": {"peacemaker"}, "Onakke Oathkeeper": {"oathkeeper"},
    "All Will Be One": {"awbo"}, "Oath of Teferi": {"oath_teferi"}, "Oath of Nissa": {"oath_nissa"},
    "Blasphemous Act": {"wipe", "blasphemous"}, "Overwrite the Multiverse": {"wipe", "overwrite"}, "Promise of Loyalty": {"promise"},
    "Entrust the Spark": {"entrust"}, "Ripples of Potential": {"ripples"},
    "Way of the Paradox": {"way"}, "Way of the Pyromancer": {"way"}, "Way of the Mind Sculptor": {"way"}, "Way of the Warlord": {"way"}, "Way of the Necromancer": {"way"},
    "Way of the Deathbringer": {"way"}, "Way of the Healer": {"way"}, "Way of the Wildspeaker": {"way"},
}
for _n, _d in _DATA.items():
    _g, _pips, _phy = parse_cost(_d["mana_cost"] or "")
    _types, _sub, _leg = _types_of(_d["type_line"])
    _lt = frozenset(t for t in _sub if t in ("Forest", "Island", "Swamp", "Mountain", "Plains")) if "land" in _types else frozenset()
    _t = set(TAGS.get(_n, set()))
    if "Planeswalker" in _d["type_line"]:
        _t.add("pw")
    CARD_DB[_n] = Card(name=_n, mv=int(_d["cmc"]), types=_types, subtypes=_sub, legendary=_leg,
                       power=int(_d["power"]) if (_d.get("power") or "").lstrip("-").isdigit() else 0,
                       toughness=int(_d["toughness"]) if (_d.get("toughness") or "").lstrip("-").isdigit() else 0,
                       loyalty=int(_d["loyalty"]) if (_d.get("loyalty") or "").isdigit() else 0,
                       generic=_g, pips=_pips, phy=_phy, colors=frozenset(_d.get("colors") or []), tags=frozenset(_t), text=_d["oracle_text"] or "", land_types=_lt)

# --- fichas (nao estao no cache: sao criadas por habilidades; tipos/cores do TEXTO das cartas que as criam) ---
def _tok(name, types, power=0, toughness=0, colors=(), subtypes=(), legendary=False, tags=()):
    CARD_DB[name] = Card(name=name, mv=0, types=frozenset(types), subtypes=frozenset(subtypes), legendary=legendary, power=power, toughness=toughness, colors=frozenset(colors),
                         tags=frozenset(tags) | {"token"}, token=True)


_tok("Food Token", {"artifact"}, subtypes={"Food"})
_tok("Treasure Token", {"artifact"}, subtypes={"Treasure"})
_tok("Servo Token", {"artifact", "creature"}, 1, 1, subtypes={"Servo"})                                          # Saheeli: 1/1 colorless Servo artifact creature
_tok("Soldier Token", {"creature"}, 1, 1, {"W"}, {"Soldier"})                                                      # Elspeth, Sun's Champion
_tok("Cadet Token", {"creature"}, 2, 2, (), {"Wizard", "Soldier"})                                                 # Ajani Unrelenting / Way of the Healer: 2/2 colorless Wizard Soldier named Cadet
_tok("Beast Token", {"creature"}, 4, 4, {"G"}, {"Beast"}, tags={"trample"})                                        # 4/4 verde com trample (Ways, Garruk, Domri)
_tok("Beast3 Token", {"creature"}, 3, 3, {"G"}, {"Beast"})                                                         # Garruk Wildspeaker -1: 3/3 verde
_tok("Horror Token", {"creature"}, 0, 0, {"G"}, {"Phyrexian", "Horror"})                                           # Nissa: X/X (X fixado ao resolver; guardado como contadores base)
_tok("Fractal Token", {"creature"}, 0, 0, {"G", "U"}, {"Fractal"})                                                 # Kasmina: 0/0 verde e azul com X contadores
_tok("Elk Token", {"creature"}, 3, 3, {"G"}, {"Elk"})                                                              # Oko: o Food/artefato vira Elk 3/3 (vira esta ficha em campo)
_tok("Samurai Token", {"creature"}, 2, 2, {"W"}, {"Samurai"}, tags={"double_strike"})                              # Eternal Wanderer 0
_tok("Boo Token", {"creature"}, 1, 1, {"R"}, {"Hamster"}, legendary=True, tags={"trample", "haste"})              # Minsc & Boo: Boo legendario 1/1 vermelho Hamster com trample e haste
_tok("Leviathan Token", {"creature"}, 8, 8, {"U"}, {"Leviathan"}, tags={"hexproof"})                              # Kiora: 8/8 azul com hexproof
_tok("Jace Token", {"planeswalker"}, 0, 0, {"U"}, {"Jace"}, tags={"pw", "jace"})                                  # empower Jace: ficha de planeswalker azul Jace; [-1]: Surveil 1; [-3]: Draw a card

# --- terrenos: arquetipo de entrada/mana de CADA um (Regra 12), conferido no oraculo ---
LANDS = {
    "Baxter Building": dict(kind="baxter", prod="C"),
    "Boseiju, Who Endures": dict(kind="boseiju", prod="G"),
    "Bountiful Promenade": dict(kind="slow", prod="GW"),
    "Breeding Pool": dict(kind="shock", prod="GU"),
    "City of Brass": dict(kind="city", prod="WUBRG"),
    "Command Tower": dict(kind="tower", prod="WUBRG"),
    "Exotic Orchard": dict(kind="orchard", prod=""),
    "Fire-Lit Thicket": dict(kind="filter", prod="C", filt="RG"),
    "Flooded Grove": dict(kind="filter", prod="C", filt="GU"),
    "Great Hall of the Citadel": dict(kind="greathall", prod="C"),
    "Hallowed Fountain": dict(kind="shock", prod="WU"),
    "Indatha Triome": dict(kind="triome", prod="WBG"),
    "Jetmir's Garden": dict(kind="triome", prod="RGW"),
    "Ketria Triome": dict(kind="triome", prod="GUR"),
    "Misty Rainforest": dict(kind="fetch", prod="", ftypes=("Forest", "Island")),
    "Mossfire Valley": dict(kind="pay1", prod="", out="RG"),
    "Overflowing Basin": dict(kind="pay1", prod="", out="GU"),
    "Overgrown Tomb": dict(kind="shock", prod="BG"),
    "Plaza of Heroes": dict(kind="plaza", prod="C"),
    "Rejuvenating Springs": dict(kind="slow", prod="GU"),
    "Spara's Headquarters": dict(kind="triome", prod="GWU"),
    "Spire Garden": dict(kind="slow", prod="RG"),
    "Starting Town": dict(kind="town", prod="C"),
    "Steam Vents": dict(kind="shock", prod="UR"),
    "Stomping Ground": dict(kind="shock", prod="RG"),
    "Temple Garden": dict(kind="shock", prod="GW"),
    "The World Tree": dict(kind="worldtree", prod="G"),
    "Twilight Mire": dict(kind="filter", prod="C", filt="BG"),
    "Undergrowth Stadium": dict(kind="slow", prod="BG"),
    "Verdant Catacombs": dict(kind="fetch", prod="", ftypes=("Swamp", "Forest")),
    "Watery Grave": dict(kind="shock", prod="UB"),
    "Windswept Heath": dict(kind="fetch", prod="", ftypes=("Forest", "Plains")),
    "Wooded Bastion": dict(kind="filter", prod="C", filt="GW"),
    "Wooded Foothills": dict(kind="fetch", prod="", ftypes=("Mountain", "Forest")),
    "Yavimaya, Cradle of Growth": dict(kind="yavimaya", prod="G"),
    "Zagoth Triome": dict(kind="triome", prod="BGU"),
}


# =========================================================
# ESTADO
# =========================================================

@dataclass
class Permanent:
    card: Card
    uid: int = 0
    tapped: bool = False
    ctr: dict = field(default_factory=dict)        # loyalty, p1p1 (+1/+1), time, vow
    entered_turn: int = 0                          # meu turno em que entrou (doenca de invocacao: entered_turn == state.turn; o turno de oponente conta como "ontem")
    is_token: bool = False
    phased: bool = False                           # fase fora (Vronos, Ripples): nao existe pra nada
    acts: int = 0                                  # ativacoes de lealdade neste turno (turn_id em acts_turn_id)
    acts_turn_id: int = -1
    attached_to: Optional[int] = None              # uid do permanente encantado (Leyline Immersion, Teferi's/Liliana's Talent)
    anim: Optional[str] = None                     # "eot" | "next_turn": virou criatura por efeito (Wrenn, Tezzeret, Vronos)
    base_pt: Optional[tuple] = None                # P/T base fixado (Oko Elk 3/3, Tezzeret 5/5, Vronos 9/9)
    lost_abilities: bool = False                   # Oko: Elk perde todas as habilidades
    temp_p: int = 0                                # bonus ate o fim do turno
    temp_t: int = 0
    haste_until_eot: bool = False
    tapped_for_mana_turn: int = -1
    owner_idx: int = 0
    exalted_pending: int = 0
    unblockable: bool = False
    first_ult_done: bool = False


@dataclass
class Opp:
    idx: int
    life: int = OPP_START_LIFE
    poison: int = 0
    eliminated: bool = False
    elim_turn: Optional[int] = None
    elim_reason: str = ""
    lands: int = 0
    land_colors: list = field(default_factory=list)   # cores que os terrenos dele PRODUZEM (Exotic Orchard / Fellwar Stone)
    identity: list = field(default_factory=list)      # 2 cores
    hand_size: int = OPP_HAND_START
    spells_total: int = 0
    turns_taken: int = 0
    spells_this_turn: int = 0
    board: list = field(default_factory=list)         # modo de resiliencia: criaturas {"p","t","flying","trample","token","sick","frozen","frozen_now","cmc"}
    archetype: str = "low"
    lost_life_this_turn: int = 0
    cmd_cooldown: int = 0
    cmd_bonus: int = 0
    artifacts: int = 0
    cgy: int = 0                                      # cartas de criatura no cemiterio dele (Liliana's Talent)


@dataclass
class GameState:
    turn: int = 0
    turn_id: int = 0                  # +1 a cada turno de QUALQUER jogador: "uma vez a cada turno" conta por aqui
    rng: Optional[random.Random] = None
    proxy_rng: Optional[random.Random] = None
    interaction_rng: Optional[random.Random] = None
    on_play: bool = True
    library: list = field(default_factory=list)
    hand: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    exile: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    opps: list = field(default_factory=list)
    opp_rngs: list = field(default_factory=list)
    next_uid: int = 1
    mulligans: int = 0
    life: int = 40
    life_min: int = 40
    commander_in_cz: bool = True
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    commander_uid: Optional[int] = None
    # turno corrente
    lands_played_this_turn: int = 0
    extra_land_drops: int = 0
    pool: dict = field(default_factory=dict)               # mana flutuante da fase corrente {cor: n}
    spells_cast_this_turn: int = 0
    noncreature_spells_this_turn: int = 0
    activated_loyalty_this_turn: bool = False
    loyalty_acts_this_turn: int = 0
    attackers_this_turn: list = field(default_factory=list)
    end_step_untap: int = 0                                # Teferi, Hero of Dominaria +1: desvira N terrenos no proximo end step
    phase_out_at_end: list = field(default_factory=list)   # uids (Vronos +1): saem de fase no inicio do proximo end step
    delayed_return: list = field(default_factory=list)     # (nome, token?) devolvidos no inicio do proximo end step (Oath of Teferi / Eternal Wanderer)
    rebound_pending: list = field(default_factory=list)    # Narset -2: nomes de magia a conjurar de graca no proximo upkeep
    rebound_armed: bool = False
    impulse: list = field(default_factory=list)            # Chandra 0: cartas exiladas jogaveis neste turno
    riot_pool: int = 0
    mana_from_domri: dict = field(default_factory=dict)
    spells_this_turn_by_player: dict = field(default_factory=dict)   # Dreamtide Whale: segunda magia de CADA jogador no turno
    # emblemas
    emblems: list = field(default_factory=list)
    # modos
    resilience: bool = False
    ghost: bool = False
    verbose: bool = False
    log: list = field(default_factory=list)
    # fim de jogo
    decked: bool = False
    died_life: bool = False
    died_turn: Optional[int] = None
    game_over: bool = False
    table_cleared_turn: Optional[int] = None
    first_opp_elim_turn: Optional[int] = None
    combo_win: Optional[str] = None
    combo_assembled_turn: Optional[int] = None
    # metricas
    m: collections.Counter = field(default_factory=collections.Counter)      # contadores diversos
    by_turn: dict = field(default_factory=dict)                               # {turno: {campo: valor}}
    casts_by_card: dict = field(default_factory=dict)
    draws_by_source: dict = field(default_factory=dict)
    dmg_by_source: dict = field(default_factory=dict)
    activations: dict = field(default_factory=dict)                           # {(fonte, chave): n}
    first_turn: dict = field(default_factory=dict)                            # {marco: turno}
    color_screw_turns: list = field(default_factory=list)
    opp_removed_log: list = field(default_factory=list)
    attack_profile: Optional[str] = None
    attention: bool = True
    wiped_this_round: bool = False
    removed_this_turn: bool = False
    phase: str = "untap"
    target_ok: bool = False                                # ha' alvo no tabuleiro do oponente neste turno (proxy, modo padrao)
    dihada_shield: Optional[int] = None
    cb_buff: bool = False                                  # Garruk, Curse Breaker -4: atacantes ganham +2/+2 e trample ate' meu proximo turno
    tamiyo_marked: list = field(default_factory=list)      # uids marcados pela Tamiyo +1: compra ao causar dano de combate
    extra_turn_pending: bool = False
    delayed_return_wanderer: bool = False
    riot_flag: bool = False                                # a criatura em resolucao foi paga com mana da Domri: ganha riot
    cast_zone: str = "hand"                                # zona de onde a magia em resolucao foi conjurada (rebound so' vale da mao)
    _pool_used: int = 0


def mark(state: GameState, key: str):
    if key not in state.first_turn:
        state.first_turn[key] = state.turn


def new_uid(state: GameState) -> int:
    u = state.next_uid
    state.next_uid += 1
    return u


def mk_perm(state: GameState, name: str, token: bool = False) -> Permanent:
    c = CARD_DB[name]
    return Permanent(card=c, uid=new_uid(state), entered_turn=state.turn, is_token=token or c.token)


def vis(state: GameState) -> list:
    """Permanentes que existem (os fora de fase nao existem pra nada)."""
    return [p for p in state.battlefield if not p.phased]


def perms_named(state: GameState, name: str) -> list:
    return [p for p in state.battlefield if not p.phased and p.card.name == name]


def has_perm(state: GameState, name: str) -> bool:
    return any(p.card.name == name and not p.phased for p in state.battlefield)


def count_named(state: GameState, name: str) -> int:
    return sum(1 for p in state.battlefield if p.card.name == name and not p.phased)


def has_tag(state: GameState, tag: str) -> bool:
    return any(tag in p.card.tags and not p.phased for p in state.battlefield)


def perms_tag(state: GameState, tag: str) -> list:
    return [p for p in state.battlefield if tag in p.card.tags and not p.phased]


def find_perm(state: GameState, uid) -> Optional[Permanent]:
    return next((p for p in state.battlefield if p.uid == uid), None)


def lands_of(state: GameState) -> list:
    return [p for p in state.battlefield if "land" in p.card.types and not p.phased]


def n_lands(state: GameState) -> int:
    return len(lands_of(state))


def is_pw(p: Permanent) -> bool:
    return "planeswalker" in p.card.types and not p.phased


def pws(state: GameState) -> list:
    return [p for p in state.battlefield if "planeswalker" in p.card.types and not p.phased]


def is_creature(p: Permanent) -> bool:
    if p.phased:
        return False
    if p.anim is not None or p.base_pt is not None:
        return True
    return "creature" in p.card.types


def creatures(state: GameState) -> list:
    return [p for p in state.battlefield if is_creature(p)]


def is_artifact(p: Permanent) -> bool:
    return "artifact" in p.card.types and not p.phased


def artifacts(state: GameState) -> list:
    return [p for p in state.battlefield if is_artifact(p)]


def is_legendary(p: Permanent) -> bool:
    return p.card.legendary and not p.is_token or ("Boo" in p.card.name)


def card_colors(p: Permanent) -> frozenset:
    return p.card.colors


def colors_among(state: GameState) -> list:
    """Cores entre os permanentes que eu controlo (Bloom Tender / Faeburrow Elder / Orrery): so' W U B R G contam (incolor nao e' cor). Ordem fixa."""
    have = set()
    for p in state.battlefield:
        if p.phased:
            continue
        have |= set(p.card.colors)
    return [c for c in COLORS5 if c in have]


def pw_types(state: GameState) -> int:
    """X da Tam: numero de TIPOS de planeswalker entre os planeswalkers que eu controlo (CR 205.3j; The Eternal Wanderer nao tem tipo; a ficha de Jace e' do tipo Jace)."""
    s = set()
    for p in pws(state):
        s |= {t for t in p.card.subtypes if t not in ("Legendary",)}
    return len(s)


def loyalty(p: Permanent) -> int:
    return p.ctr.get("loyalty", 0)


def power(state: GameState, p: Permanent) -> int:
    if p.card.name == "Faeburrow Elder":
        base = len(colors_among(state))
    elif p.base_pt is not None:
        base = p.base_pt[0]
    else:
        base = p.card.power
    bonus = p.ctr.get("p1p1", 0) + p.temp_p
    if is_creature(p) and any(e == "elspeth" for e in state.emblems):
        bonus += 2
    return max(0, base + bonus)


def toughness(state: GameState, p: Permanent) -> int:
    if p.card.name == "Faeburrow Elder":
        base = len(colors_among(state))
    elif p.base_pt is not None:
        base = p.base_pt[1]
    else:
        base = p.card.toughness
    bonus = p.ctr.get("p1p1", 0) + p.temp_t
    if is_creature(p) and any(e == "elspeth" for e in state.emblems):
        bonus += 2
    return max(0, base + bonus)


def has_flying(state: GameState, p: Permanent) -> bool:
    return "flying" in p.card.tags or "elspeth" in state.emblems


def has_haste(state: GameState, p: Permanent) -> bool:
    return "haste" in p.card.tags or p.haste_until_eot


def sick(state: GameState, p: Permanent) -> bool:
    """Doenca de invocacao: nao controlo desde o INICIO do meu turno (entrou neste turno meu)."""
    return p.entered_turn >= state.turn and not has_haste(state, p)


def can_attack(state: GameState, p: Permanent) -> bool:
    if not is_creature(p) or p.tapped or p.phased:
        return False
    if sick(state, p):
        return False
    if p.card.name in NON_ATTACKERS:
        return False
    return True


def alive_opps(state: GameState) -> list:
    return [o for o in state.opps if not o.eliminated]


def log(state: GameState, msg: str):
    if state.verbose:
        state.log.append(f"T{state.turn}: {msg}")


def cnt(state: GameState, key: str, n: int = 1):
    state.m[key] += n


NON_ATTACKERS = frozenset({"Tam, the Possibility", "Birds of Paradise", "Bloom Tender", "Ignoble Hierarch", "Noble Hierarch", "Kiora of Salt and Sand"})   # {T} de mana/proliferate vale mais que o ataque (Faeburrow Elder tem vigilancia: ataca e ainda toca)


# =========================================================
# MODELO DE MANA (pip a pip; correspondencia exata das cores; filtros e conversores)
# =========================================================
ALL5 = frozenset(COLORS5)
ANYC = frozenset(COLORS5 + ("C",))      # "as though it were mana of any color" (Orrery): ate' o incolor paga pip colorido


@dataclass
class Ctx:
    """O que esta sendo pago: define as restricoes do mana (so' magia lendaria / so' magia / so' planeswalker) e o Oath of Nissa."""
    spell: bool = True
    legendary: bool = False
    pw: bool = False
    creature: bool = False


CTX_SPELL = Ctx()
CTX_ABILITY = Ctx(spell=False)


def ctx_for(name: str) -> Ctx:
    c = CARD_DB[name]
    return Ctx(spell=True, legendary=c.legendary, pw="planeswalker" in c.types, creature="creature" in c.types)


@dataclass
class Src:
    perm: Optional[Permanent]
    units: list                      # [(colors, restr)]: um mana cada, todos saem quando ela toca
    life: int = 0                    # vida paga ao tocar (Staff of Compleation)
    ping: int = 0                    # dano a mim ao ficar virado (City of Brass)
    life_colored: int = 0            # Starting Town: 1 de vida se o mana pago for colorido
    sac: bool = False
    conv: Optional[dict] = None      # conversor: {"kind", "in": frozenset|None, "n": int, "out": [(colors, restr)]} (precisa de n unidades de ENTRADA de outras fontes)
    name: str = ""


def opp_land_colors(state: GameState) -> frozenset:
    cols = set()
    for o in state.opps:
        cols |= set(o.land_colors)
    return frozenset(cols) & ALL5


def lands_any_color(state: GameState) -> bool:
    """Wrenn and Realmbreaker ("Lands you control have '{T}: Add one mana of any color'") e The World Tree (6+ terrenos controlados)."""
    if has_perm(state, "Wrenn and Realmbreaker"):
        return True
    return has_perm(state, "The World Tree") and n_lands(state) >= 6


def yavimaya_forest(state: GameState) -> bool:
    return has_perm(state, "Yavimaya, Cradle of Growth")


def legendary_colors(state: GameState) -> frozenset:
    """Plaza of Heroes: 'one mana of any color among legendary permanents you control' (cor = cores do permanente lendario; terreno lendario e' incolor; fichas nao-lendarias nao contam)."""
    cols = set()
    for p in state.battlefield:
        if p.phased or not is_legendary(p):
            continue
        cols |= set(p.card.colors)
    return frozenset(cols) & ALL5


def land_src(state: GameState, p: Permanent, ctx: Ctx, forest: bool, anyl: bool, ocols: frozenset, life_ok: bool) -> Optional[Src]:
    nm = p.card.name
    L = LANDS[nm]
    kind = L["kind"]
    if kind == "fetch":
        return None
    base = set(L["prod"])
    if kind == "tower":
        base = set(COLORS5)                       # identidade de cor do comandante = WUBRG
    elif kind == "orchard":
        base = set(ocols)                          # so' cores que um terreno de OPONENTE produz (nunca incolor)
    if forest and kind != "orchard":
        base.add("G")
    elif forest:
        base.add("G")
    if anyl:
        base = set(COLORS5) | (base & {"C"})
    src = Src(p, [], name=nm)
    if kind == "plaza":
        cols = set(base) | {"C"} | set(legendary_colors(state))
        if ctx.legendary:
            cols |= set(COLORS5)
        src.units = [(frozenset(cols), None)]
    elif kind == "town":
        cols = set(base) | ({"C"})
        if life_ok:
            cols |= set(COLORS5)
            src.life_colored = 1
        src.units = [(frozenset(cols), None)]
    elif kind == "city":
        src.units = [(frozenset(set(COLORS5) | (set() if not forest else {"G"})), None)]
        src.ping = 1
    elif kind == "filter":
        f = frozenset(L["filt"])
        src.units = [(frozenset({"C"} | (set(COLORS5) if anyl else set()) | ({"G"} if forest else set())), None)]
        src.conv = {"kind": "filter", "in": f, "n": 1, "out": [(f, None), (f, None)]}
    elif kind == "pay1":
        o = L["out"]
        src.units = [(frozenset(set(COLORS5) if anyl else ({"G"} if forest else set())), None)] if (anyl or forest) else []
        src.conv = {"kind": "pay1", "in": None, "n": 1, "out": [(frozenset({o[0]}), None), (frozenset({o[1]}), None)]}
    elif kind == "greathall":
        src.units = [(frozenset({"C"} | (set(COLORS5) if anyl else set()) | ({"G"} if forest else set())), None)]
        if ctx.legendary:
            src.conv = {"kind": "hall", "in": None, "n": 1, "out": [(ALL5, None), (ALL5, None)]}      # "Spend this mana only to cast legendary spells": so' vale pra magia lendaria
    elif kind == "baxter":
        src.units = [(frozenset({"C"} | (set(COLORS5) if anyl else set()) | ({"G"} if forest else set())), None)]
        src.conv = {"kind": "baxter", "in": None, "n": 4, "out": [(ALL5, None)] * 4}
    else:
        src.units = [(frozenset(base), None)] if base else []
    if not src.units and not src.conv:
        return None
    return src


def mana_sources(state: GameState, ctx: Ctx = CTX_SPELL) -> list:
    """Fontes de mana disponiveis AGORA (permanentes desvirados). Cada uma: lista de unidades (um mana cada) que saem quando ela toca; conversores a parte."""
    out = []
    forest = yavimaya_forest(state)
    anyl = lands_any_color(state)
    ocols = opp_land_colors(state)
    life_ok = state.life > 5
    for p in state.battlefield:
        if p.phased or p.tapped:
            continue
        c = p.card
        nm = c.name
        if "land" in c.types:
            s = land_src(state, p, ctx, forest, anyl, ocols, life_ok)
            if s is not None:
                out.append(s)
            continue
        if is_creature(p) and sick(state, p) and not p.lost_abilities:
            pass     # criatura com doenca de invocacao: nenhuma habilidade de {T} (CR 302.6), nem a concedida pela Leyline
        elif p.lost_abilities:
            pass
        elif nm == "Sol Ring":
            out.append(Src(p, [(frozenset({"C"}), None)] * 2, name=nm))
        elif nm == "Arcane Signet":
            out.append(Src(p, [(ALL5, None)], name=nm))
        elif nm == "Fellwar Stone":
            if ocols:
                out.append(Src(p, [(ocols, None)], name=nm))
        elif nm == "Birds of Paradise":
            out.append(Src(p, [(ALL5, None)], name=nm))
        elif nm == "Noble Hierarch":
            out.append(Src(p, [(frozenset("GWU"), None)], name=nm))
        elif nm == "Ignoble Hierarch":
            out.append(Src(p, [(frozenset("BRG"), None)], name=nm))
        elif nm in ("Bloom Tender", "Faeburrow Elder"):
            cs = colors_among(state)
            if cs:
                out.append(Src(p, [(frozenset({k}), None) for k in cs], name=nm))
        elif nm == "Chromatic Orrery":
            out.append(Src(p, [(frozenset({"C"}), None)] * 5, name=nm))
        elif nm == "Staff of Compleation" and state.life > 6:
            out.append(Src(p, [(ALL5, None)], life=2, name=nm))
        elif nm == "Treasure Token":
            out.append(Src(p, [(ALL5, None)], sac=True, name=nm))
        if is_creature(p) and not sick(state, p) and not p.lost_abilities and ctx.spell:
            for q in state.battlefield:
                if q.card.name == "Leyline Immersion" and q.attached_to == p.uid and not q.phased:
                    out.append(Src(p, [(ALL5, None)] * 5, name="Leyline Immersion"))      # so' pra conjurar magias (ctx.spell); {T} da propria criatura
    out.sort(key=_src_sort)
    return out


def _src_sort(s: Src):
    cols = set()
    for c, r in s.units:
        cols |= set(c)
    n = len(cols - {"C"})
    cost = (4 if (s.life or s.ping or s.life_colored) else 0) + (60 if s.sac else 0) + (30 if s.name == "Leyline Immersion" else 0)
    return (n * 10 - (5 if s.perm is not None and is_creature(s.perm) else 0) - (3 if len(s.units) > 1 else 0) + cost, s.name, s.perm.uid if s.perm else 0)


def pool_units(state: GameState) -> list:
    """Mana flutuante da fase (src None). 'A' = qualquer cor, so' pra magia (sobra da Leyline Immersion)."""
    out = []
    for col in ("C", "W", "U", "B", "R", "G", "A"):
        for _ in range(state.pool.get(col, 0)):
            out.append((None, ALL5 if col == "A" else frozenset({col}), "spell" if col == "A" else None))
    return out


def _any_color_pay(state: GameState, ctx: Ctx) -> bool:
    """Chromatic Orrery: 'You may spend mana as though it were mana of any color.' Oath of Nissa: o mesmo, so' pra conjurar planeswalker."""
    if has_perm(state, "Chromatic Orrery"):
        return True
    return ctx.spell and ctx.pw and has_perm(state, "Oath of Nissa")


def _ok_restr(restr, ctx: Ctx) -> bool:
    return not ((restr == "spell" and not ctx.spell) or (restr == "legend" and not ctx.legendary))


def _units_of(src: Src, any_pay: bool, ctx: Ctx) -> list:
    return [(src, ANYC if any_pay else colors, restr) for colors, restr in src.units if _ok_restr(restr, ctx)]


def _match(units: list, generic: int, pips: tuple):
    """Kuhn: cada pip -> uma unidade que produz alguma das cores aceitas; o generico sai das unidades que sobram (as MENOS flexiveis primeiro).
    Devolve (indices usados, indices casados com pip) ou None."""
    n = len(units)
    order = sorted(range(n), key=lambda i: (0 if units[i][0] is None else 1, len(units[i][1] - {"C"}), i))
    su = [units[i] for i in order]
    adj = [[j for j, (_, cols, _) in enumerate(su) if cols & pip] for pip in pips]
    match_u = [-1] * n

    def try_pip(i, seen):
        for j in adj[i]:
            if j in seen:
                continue
            seen.add(j)
            if match_u[j] == -1 or try_pip(match_u[j], seen):
                match_u[j] = i
                return True
        return False
    for i in range(len(pips)):
        if not try_pip(i, set()):
            return None
    free = [j for j in range(n) if match_u[j] == -1]
    if len(free) < generic:
        return None
    matched = [order[j] for j in range(n) if match_u[j] != -1]
    return matched + [order[j] for j in free[:generic]], matched


def _plan(state: GameState, generic: int, pips: tuple, ctx: Ctx = CTX_SPELL, srcs: Optional[list] = None):
    """Procura uma atribuicao de unidades que paga `generic` + `pips`. Devolve {"units","used","matched","feeds"} ou None.
    Conversores (filtro {R/G},{T}: dois mana; {1},{T}: RG; Great Hall; Baxter {4},{T}: 4 de qualquer cor) so' entram se o pagamento simples nao fecha: o conversor toca,
    consome N unidades de entrada de OUTRAS fontes e entrega as unidades de saida (ate' 3 conversores por plano)."""
    if srcs is None:
        srcs = mana_sources(state, ctx)
    any_pay = _any_color_pay(state, ctx)
    base = [(None, ANYC if any_pay else u[1], u[2]) for u in pool_units(state) if _ok_restr(u[2], ctx)]
    for s in srcs:
        base.extend(_units_of(s, any_pay, ctx))
    r = _match(base, generic, pips)
    if r is not None:
        return {"units": base, "used": r[0], "matched": r[1], "feeds": []}
    convs = [s for s in srcs if s.conv is not None]
    if not convs:
        return None
    from itertools import combinations
    for k in range(1, min(3, len(convs)) + 1):
        for sub in combinations(convs, k):
            ids = {id(c) for c in sub}
            units = [u for u in base if u[0] is None or id(u[0]) not in ids]       # o toque do conversor e' a conversao: as unidades simples dele nao existem
            feeds, ok = [], True
            for cs in sub:
                cv = cs.conv
                fed = []
                for _ in range(cv["n"]):
                    cand = [u for u in units if (cv["in"] is None or (u[1] & cv["in"])) and (u[0] is None or id(u[0]) not in ids)]
                    if not cand:
                        ok = False
                        break
                    u = min(cand, key=lambda x: (0 if x[0] is None else 1, len(x[1] - {"C"}), x[0].name if x[0] else "", x[0].perm.uid if (x[0] and x[0].perm) else 0))
                    units.remove(u)
                    fed.append(u)
                if not ok:
                    break
                feeds.append((cs, fed))
                for colors, restr in cv["out"]:
                    if _ok_restr(restr, ctx):
                        units.append((cs, ANYC if any_pay else colors, restr))
            if not ok:
                continue
            r = _match(units, generic, pips)
            if r is not None:
                return {"units": units, "used": r[0], "matched": r[1], "feeds": feeds}
    return None


def can_pay(state: GameState, generic: int, pips: tuple, ctx: Ctx = CTX_SPELL) -> bool:
    return _plan(state, generic, pips, ctx) is not None


def _pool_key(colors: frozenset) -> str:
    return "A" if len(colors) >= 5 else ("C" if "C" in colors and len(colors) == 1 else sorted(colors - {"C"})[0] if colors - {"C"} else "C")


def pay_mana(state: GameState, generic: int, pips: tuple, ctx: Ctx = CTX_SPELL) -> bool:
    """Paga: toca as fontes escolhidas; o que sobra de fonte multimana (Sol Ring, Orrery, Bloom Tender, Leyline) vai pro `state.pool` (vale ate' o fim da fase).
    Custos de vida/dano das fontes (City of Brass, Staff, Starting Town colorido) sao pagos aqui."""
    plan = _plan(state, generic, pips, ctx)
    if plan is None:
        return False
    units, used, matched, feeds = plan["units"], plan["used"], set(plan["matched"]), plan["feeds"]
    cnt_used = collections.defaultdict(int)
    town_colored = set()
    pool_used = collections.Counter()
    for i in used:
        src, cols, restr = units[i]
        if src is None:
            pool_used[_pool_key(cols)] += 1
        else:
            cnt_used[id(src)] += 1
            if src.life_colored and i in matched:
                town_colored.add(id(src))
    srcs_tapped = collections.OrderedDict()
    fed_pool = collections.Counter()
    for cs, fed in feeds:
        srcs_tapped[id(cs)] = (cs, cnt_used.get(id(cs), 0), True)
        for u in fed:
            if u[0] is None:
                fed_pool[_pool_key(u[1])] += 1
            else:
                cnt_used[id(u[0])] += 1
                srcs_tapped.setdefault(id(u[0]), (u[0], 0, False))
    for i in used:
        src = units[i][0]
        if src is not None:
            srcs_tapped.setdefault(id(src), (src, 0, False))
    state._pool_used = sum(pool_used.values())
    for col, n in list(pool_used.items()) + list(fed_pool.items()):
        state.pool[col] = state.pool.get(col, 0) - n
    for sid, (src, _n, is_conv) in srcs_tapped.items():
        total_taken = cnt_used.get(sid, 0)
        if src.perm is not None and not src.sac:
            src.perm.tapped = True
        if src.perm is not None and src.sac and src.perm in state.battlefield:
            state.battlefield.remove(src.perm)
        n_units = len(src.units) if not is_conv else (len(src.conv["out"]) if src.conv else 0)
        if not is_conv and len(src.units) > 1 and total_taken < len(src.units):
            # unidades que sairam e nao foram usadas: flutuam
            for colors, restr in src.units[total_taken:]:
                key = "A" if (restr == "spell" and len(colors) >= 5) else _pool_key(colors)
                state.pool[key] = state.pool.get(key, 0) + 1
        elif is_conv:
            out_total = len(src.conv["out"])
            if total_taken < out_total:
                for colors, restr in src.conv["out"][total_taken:]:
                    if _ok_restr(restr, ctx):
                        key = _pool_key(colors)
                        state.pool[key] = state.pool.get(key, 0) + 1
        if src.perm is not None and src.perm.card.name == "City of Brass":
            state_hit_city(state)
        if src.life and not is_conv:
            lose_life(state, src.life, "staff_mana")
        if sid in town_colored:
            lose_life(state, 1, "starting_town")
    state.m["mana_spent_total"] += generic + len(pips)
    return True


def state_hit_city(state: GameState):
    lose_life(state, 1, "city_of_brass")


def available_mana(state: GameState, ctx: Ctx = CTX_SPELL) -> int:
    """Total de mana disponivel agora (pool + unidades das fontes; cada conversor "pay1"/filtro soma +1 se ha' de onde puxar; Baxter nao soma)."""
    n = sum(state.pool.values())
    srcs = mana_sources(state, ctx)
    n += sum(len(s.units) for s in srcs)
    for s in srcs:
        if s.conv is not None and s.conv["kind"] in ("filter", "pay1", "hall") and (n - len(s.units)) >= 1:
            n += 1
    return n


# =========================================================
# VIDA, DANO, OPONENTES, COMPRA
# =========================================================

def lose_life(state: GameState, n: int, reason: str = ""):
    if n <= 0:
        return
    state.life -= n
    state.life_min = min(state.life_min, state.life)
    state.m["life_lost_" + reason] += n
    if state.life <= 0 and not state.died_life:
        # convencao do repositorio (Prismatic/Mothman): o motor NAO encerra a partida com vida <= 0; a metrica marca o turno
        state.died_life = True
        state.died_turn = state.turn


def gain_life(state: GameState, n: int, reason: str = ""):
    """Ganho de vida. Emblema da Professor Dellian Fel: 'Whenever you gain life, target opponent loses that much life.'"""
    if n <= 0:
        return
    state.life += n
    state.m["life_gained_" + reason] += n
    if "dellian" in state.emblems and alive_opps(state):
        o = lowest_opp(state)
        if o is not None:
            damage_opp(state, n, "dellian_emblem", o.idx, drain=True)


def lowest_opp(state: GameState) -> Optional[Opp]:
    al = alive_opps(state)
    if not al:
        return None
    return min(al, key=lambda o: (o.life - 3 * o.poison, o.idx))


def damage_opp(state: GameState, n: int, src: str, idx: Optional[int] = None, combat: bool = False, drain: bool = False):
    """Dano / perda de vida de UM oponente (default: o de menor vida). Contabiliza por fonte."""
    if n <= 0 or state.game_over:
        return
    o = state.opps[idx - 1] if idx is not None else lowest_opp(state)
    if o is None or o.eliminated:
        o = lowest_opp(state)
        if o is None:
            return
    o.life -= n
    o.lost_life_this_turn += n
    state.dmg_by_source[src] = state.dmg_by_source.get(src, 0) + n
    state.m["opp_damage_total"] += n
    if combat:
        state.m["combat_damage_total"] += n
    if o.life <= 0:
        eliminate_opp(state, o, "life")


def damage_each_opp(state: GameState, n: int, src: str):
    for o in list(alive_opps(state)):
        if state.game_over:
            return
        damage_opp(state, n, src, o.idx)


def give_poison(state: GameState, idx: int, n: int, src: str = ""):
    o = state.opps[idx - 1]
    if o.eliminated or n <= 0:
        return
    o.poison += n
    state.m["poison_counters_given"] += n
    state.m["counters_placed_on_players"] += 1
    on_counters_put(state, n, None, "poison", src)
    if o.poison >= 10:
        eliminate_opp(state, o, "poison")


def eliminate_opp(state: GameState, o: Opp, reason: str):
    if o.eliminated:
        return
    o.eliminated = True
    o.elim_turn = state.turn
    o.elim_reason = reason
    state.m["opps_eliminated_total"] += 1
    state.m["opps_elim_" + reason] += 1
    if state.first_opp_elim_turn is None:
        state.first_opp_elim_turn = state.turn
    if all(x.eliminated for x in state.opps):
        state.table_cleared_turn = state.turn
        state.game_over = True


def draw_cards(state: GameState, n: int, source: str = "normal", optional: bool = False):
    if optional:
        n = max(0, min(n, library_budget(state)))
    for _ in range(n):
        if state.game_over:
            return
        if not state.library:
            state.decked = True
            state.game_over = True
            state.m["decked_turn"] = state.turn
            return
        c = state.library.pop(0)
        state.hand.append(c)
        state.m["draws_total"] += 1
        state.draws_by_source[source] = state.draws_by_source.get(source, 0) + 1
        if source != "normal":
            state.m["cards_drawn_extra"] += 1
        # Teferi's Talent: "Whenever you draw a card, put a loyalty counter on enchanted planeswalker."
        for a in [x for x in state.battlefield if x.card.name == "Teferi's Talent" and not x.phased]:
            tgt = find_perm(state, a.attached_to) if a.attached_to is not None else None
            if tgt is not None and not tgt.phased:
                put_counters(state, tgt, "loyalty", 1, "teferis_talent")
        if "teferi_hero" in state.emblems:
            teferi_emblem_exile(state)


def library_budget(state: GameState) -> int:
    return len(state.library) - 8


def scry(state: GameState, n: int):
    """Scry N: o que nao presta vai pro fundo (terreno quando ja' tenho de sobra; carta de custo maior que o mana alcancavel em 3 turnos nao)."""
    n = min(n, len(state.library))
    if n <= 0:
        return
    top = state.library[:n]
    del state.library[:n]
    keep = [c for c in top if scry_keep(state, c)]
    bottom = [c for c in top if not scry_keep(state, c)]
    state.library = keep + state.library + bottom
    state.m["scry_events"] += 1


def scry_keep(state: GameState, c: str) -> bool:
    cc = CARD_DB[c]
    held_lands = sum(1 for h in state.hand if "land" in CARD_DB[h].types)
    if "land" in cc.types:
        return n_lands(state) + held_lands < 7
    return True


def surveil(state: GameState, n: int):
    """Surveil N: cada carta do topo vai pro cemiterio ou fica; cemiterio = recursao futura (Wrenn emblem, Onakke). Politica: terreno sobrando ou carta inutil vai pro cemiterio."""
    n = min(n, len(state.library))
    if n <= 0:
        return
    top = state.library[:n]
    del state.library[:n]
    keep = []
    for c in top:
        if scry_keep(state, c):
            keep.append(c)
        else:
            state.graveyard.append(c)
    state.library = keep + state.library
    state.m["surveil_events"] += 1


def opp_target_proxy(state: GameState, kind: str) -> bool:
    """Alvo no tabuleiro do oponente: no modo padrao e' ESTRUTURAL (tabuleiro de oponente nao e' simulado): conta como metrica proxy quando OPP_TARGET_PROB diz que existe alvo."""
    if state.turn < OPP_TARGET_FROM_TURN or not alive_opps(state):
        return False
    if state.proxy_rng.random() < OPP_TARGET_PROB:
        state.m["proxy_" + kind] += 1
        state.m["interaction_plays"] += 1
        return True
    return False


# =========================================================
# CONTADORES, LEALDADE, PROLIFERATE
# =========================================================

def counter_mult(state: GameState, perm: Optional[Permanent], kind: str) -> int:
    """Substituicao de contadores postos por EFEITO (nao por custo): Doubling Season dobra (candidata; nao esta na lista base) e Vorinclex (sideboard)."""
    m = 1
    m *= 2 ** count_named(state, "Doubling Season")
    m *= 2 ** count_named(state, "Vorinclex, Monstrous Raider")
    return m


def put_counters(state: GameState, perm: Optional[Permanent], kind: str, n: int, src: str = "", cost: bool = False) -> int:
    """TODO contador posto num permanente MEU passa por aqui (lealdade de entrada, +1/+1, tempo, proliferate, Gauntlet, Talent...). `cost=True`: [+N] pago como CUSTO (nao e' substituido por
    Doubling Season, ruling 2024-11-08), mas continua sendo 'contador posto' pra All Will Be One."""
    if perm is None or n <= 0 or perm not in state.battlefield:
        return 0
    k = n if cost else n * counter_mult(state, perm, kind)
    perm.ctr[kind] = perm.ctr.get(kind, 0) + k
    state.m["counters_" + kind] += k
    state.m["counter_events"] += 1
    if kind == "loyalty":
        state.m["loyalty_counters_by_" + src] += k
    on_counters_put(state, k, perm, kind, src)
    return k


def on_counters_put(state: GameState, total: int, perm: Optional[Permanent], kind: str, src: str):
    """All Will Be One: 'Whenever you put one or more counters on a permanent or player, this enchantment deals that much damage to target opponent, creature an opponent controls,
    or planeswalker an opponent controls.' (um gatilho por EVENTO: por permanente ou jogador que recebe). Mais Peacemaker/Flux nao dependem disto."""
    if total <= 0 or state.game_over:
        return
    for _ in range(count_named(state, "All Will Be One")):
        if state.game_over:
            return
        state.m["awbo_triggers"] += 1
        awbo_hit(state, total)


def awbo_hit(state: GameState, dmg: int):
    if state.resilience:
        c = best_killable_threat(state, dmg)
        if c is not None:
            opp_remove_creature(state, c[0], c[1], "damage")
            state.m["awbo_kills"] += 1
            return
    damage_opp(state, dmg, "all_will_be_one")


def remove_loyalty(state: GameState, perm: Permanent, n: int):
    perm.ctr["loyalty"] = perm.ctr.get("loyalty", 0) - n


def proliferate(state: GameState, src: str = "", times: int = 1):
    """CR 701.34a: escolho qualquer numero de permanentes e jogadores com contador e dou +1 de cada tipo. Politica: tudo que me ajuda — lealdade (planeswalkers e a ficha de Jace),
    +1/+1, contador de tempo (Dreamtide Whale vive mais), veneno nos oponentes; NUNCA 'vow' (Promise of Loyalty). Cada permanente/jogador e' um EVENTO de contador (All Will Be One)."""
    log(state, f"  proliferate x{times} ({src})")
    for _ in range(times):
        if state.game_over:
            return
        state.m["proliferates_total"] += 1
        state.m["prolif_by_" + src] += 1
        gained = 0
        for p in list(state.battlefield):
            if p.phased or p not in state.battlefield:
                continue
            if "planeswalker" in p.card.types and p.ctr.get("loyalty", 0) >= 1:
                gained += put_counters(state, p, "loyalty", 1, "proliferate")
            if p.ctr.get("p1p1", 0) > 0:
                put_counters(state, p, "p1p1", 1, "proliferate")
            if p.ctr.get("time", 0) > 0:
                put_counters(state, p, "time", 1, "proliferate")
            if state.game_over:
                return
        for o in alive_opps(state):
            if o.poison > 0:
                give_poison(state, o.idx, 1, "proliferate")
        state.m["prolif_loyalty_" + src] += gained


# =========================================================
# PERMANENTES: entrar, sair, fichas, fase, piscar
# =========================================================

def create_token(state: GameState, name: str, n: int = 1, counters: int = 0, tapped: bool = False, haste: bool = False, src: str = "") -> list:
    """Fichas (Doubling Season, candidata, dobra a quantidade: `token_mult`)."""
    n = n * (2 ** count_named(state, "Doubling Season"))
    out = []
    for _ in range(n):
        if state.game_over:
            break
        p = mk_perm(state, name, token=True)
        p.tapped = tapped
        p.haste_until_eot = haste
        state.battlefield.append(p)
        if counters:
            k = counters * counter_mult(state, p, "p1p1")
            p.ctr["p1p1"] = p.ctr.get("p1p1", 0) + k
            on_counters_put(state, k, p, "p1p1", src)
        state.m["tokens_created"] += 1
        state.m["tokens_" + name] += 1
        enter_triggers(state, p, from_cast=False)
        out.append(p)
    return out


def enter_triggers(state: GameState, p: Permanent, from_cast: bool = True):
    """Gatilhos de 'um permanente entra' (nao-terreno; terrenos usam land_enters) + ETB proprio."""
    c = p.card
    if is_creature(p):
        # Garruk, Curse Breaker: "Whenever a creature you control with power 4 or greater enters, draw a card."
        if power(state, p) >= 4:
            for _ in range(count_named(state, "Garruk, Curse Breaker")):
                state.m["garruk_cb_draws"] += 1
                draw_cards(state, 1, "garruk_curse_breaker")
    apply_etb(state, p, from_cast)


def land_enters(state: GameState, p: Permanent, source: str = ""):
    state.m["lands_entered_total"] += 1
    # (nenhuma carta da lista tem landfall / "land enters": categoria N/A; Yavimaya/Wrenn/World Tree sao estaticos)


def die_trigger_creature(state: GameState, p: Permanent):
    """Way of the Necromancer: 'Whenever a creature you control dies, put a loyalty counter on each planeswalker you control.'"""
    for _ in range(count_named(state, "Way of the Necromancer")):
        for q in list(pws(state)):
            put_counters(state, q, "loyalty", 1, "necromancer")
            if state.game_over:
                return
    state.m["creatures_died"] += 1


def remove_permanent(state: GameState, perm: Permanent, reason: str = "dies"):
    """Permanente MEU sai do campo. reason: dies | sacrificed | exile | bounce | opp_removal | wipe. So' dies/sacrificed disparam 'dies'. Fichas deixam de existir; o comandante volta pra zona de comando
    (CR 903.9a: acao baseada em estado, escolha minha: sempre volto — o imposto e' so' 2 por conjuracao)."""
    if perm not in state.battlefield:
        return
    log(state, f"  sai: {perm.card.name} ({reason})")
    was_creature = is_creature(perm)
    state.battlefield.remove(perm)
    for a in [q for q in state.battlefield if q.attached_to == perm.uid]:
        state.battlefield.remove(a)                      # aura sem hospedeiro vai ao cemiterio
        if not a.is_token:
            state.graveyard.append(a.card.name)
    nm = perm.card.name
    if perm.is_token:
        if was_creature and reason in ("dies", "sacrificed", "opp_removal", "wipe"):
            die_trigger_creature(state, perm)
        return
    if "commander" in perm.card.tags:
        state.commander_in_cz = True
        state.commander_uid = None
        if was_creature and reason in ("dies", "sacrificed", "opp_removal", "wipe"):
            die_trigger_creature(state, perm)
        return
    if reason == "exile":
        state.exile.append(nm)
    elif reason == "bounce":
        state.hand.append(nm)
    else:
        state.graveyard.append(nm)
        state.m["permanents_to_graveyard"] += 1
        if "planeswalker" in perm.card.types:
            state.m["pw_died"] += 1
    if was_creature and reason in ("dies", "sacrificed", "opp_removal", "wipe"):
        die_trigger_creature(state, perm)


def sba(state: GameState):
    """Acoes baseadas em estado: planeswalker com 0 de lealdade morre (Sanctum Lurker impede: 'aren't put into graveyards for having 0 loyalty'); criatura com resistencia 0 morre."""
    changed = True
    guard = 0
    while changed and guard < 20 and not state.game_over:
        changed = False
        guard += 1
        lurker = has_perm(state, "Sanctum Lurker")
        for p in list(state.battlefield):
            if p.phased or p not in state.battlefield:
                continue
            if "planeswalker" in p.card.types and p.ctr.get("loyalty", 0) <= 0 and not lurker:
                remove_permanent(state, p, "dies")
                changed = True
            elif is_creature(p) and toughness(state, p) <= 0:
                remove_permanent(state, p, "dies")
                changed = True


def phase_out(state: GameState, perm: Permanent):
    perm.phased = True
    state.m["phase_outs"] += 1
    for a in state.battlefield:
        if a.attached_to == perm.uid:
            a.phased = True


def phase_in_all(state: GameState):
    for p in state.battlefield:
        if p.phased:
            p.phased = False
            state.m["phase_ins"] += 1


def blink(state: GameState, perm: Permanent, src: str = "") -> Optional[Permanent]:
    """Exila e devolve: OBJETO NOVO (contadores somem, aura cai, lealdade volta ao valor de entrada, pode ativar de novo, ETB dispara; ficha deixa de existir)."""
    if perm not in state.battlefield or perm.is_token:
        return None
    nm = perm.card.name
    cmd = "commander" in perm.card.tags
    state.battlefield.remove(perm)
    for a in [q for q in state.battlefield if q.attached_to == perm.uid]:
        state.battlefield.remove(a)
        state.graveyard.append(a.card.name)
        state.m["auras_lost_to_blink"] += 1
    state.m["blinks_total"] += 1
    state.m["blink_by_" + src] += 1
    q = mk_perm(state, nm)
    state.battlefield.append(q)
    if cmd:
        state.commander_uid = q.uid
    enter_permanent(state, q, from_cast=False)
    return q


def enter_permanent(state: GameState, p: Permanent, from_cast: bool = True):
    """Entrada de um permanente que NAO e' terreno: lealdade/contadores de entrada, Whale, Peacemaker, ETB."""
    c = p.card
    if "planeswalker" in c.types:
        p.entered_turn = state.turn
        base = c.loyalty
        put_counters(state, p, "loyalty", base - p.ctr.get("compleated_less", 0), "enters")
        mark(state, "first_pw")
        state.m["pw_entered"] += 1
    if "whale" in c.tags:
        put_counters(state, p, "time", 2, "enters")
    if "peacemaker" in c.tags:
        put_counters(state, p, "p1p1", 2, "enters")
    enter_triggers(state, p, from_cast)
    if "creature" in c.types and is_creature(p):
        pass


def best_blink_target(state: GameState, exclude=None) -> Optional[Permanent]:
    """Alvo de um piscar (Displacer Kitten / Oath of Teferi / Aminatou -1): o que mais ganha — Way (empower Jace de novo), Sanctum Lurker, Peacemaker, Whale; planeswalker que ja' gastou a ativacao
    (novo objeto: ativa DE NOVO neste turno) ou com lealdade abaixo da inicial. Nunca piscar quem carrega uma aura nossa sem motivo, nem a Tam (perde a Leyline e ainda gasta o {T})."""
    best, best_v = None, 0.0
    for p in state.battlefield:
        if p.phased or p is exclude or p.is_token or p not in state.battlefield:
            continue
        v = blink_value(state, p)
        if v > best_v:
            best, best_v = p, v
    return best


def blink_value(state: GameState, p: Permanent) -> float:
    c = p.card
    nm = c.name
    if "land" in c.types:
        return 0.0
    aura_penalty = 0.0
    for a in state.battlefield:
        if a.attached_to == p.uid:
            aura_penalty += 40.0
    v = 0.0
    if "way" in c.tags:
        v = {"Way of the Wildspeaker": 70, "Way of the Paradox": 55, "Way of the Mind Sculptor": 55, "Way of the Warlord": 50, "Way of the Deathbringer": 50, "Way of the Healer": 50,
             "Way of the Necromancer": 25, "Way of the Pyromancer": 25}.get(nm, 40) * (0.5 if empower_jace_is_capped(state) else 1.0)
    elif nm == "Sanctum Lurker":
        v = 20
    elif nm == "Patrolling Peacemaker":
        v = 12 if p.ctr.get("p1p1", 0) < 3 else 0
    elif nm == "Dreamtide Whale":
        v = 25 if p.ctr.get("time", 0) <= 1 else 0
    elif "planeswalker" in c.types and nm != "Jace Token":
        start = c.loyalty
        if p.acts_turn_id == state.turn_id and p.acts > 0:
            v = 45 + 2 * start                              # novo objeto: ativa de novo
        elif loyalty(p) < start - 1:
            v = 8 + (start - loyalty(p)) * 3
        else:
            v = 0
    elif nm == "Oath of Teferi":
        v = 14
    return max(0.0, v - aura_penalty)


def empower_jace_is_capped(state: GameState) -> bool:
    return False


def jace_token(state: GameState) -> Optional[Permanent]:
    js = [p for p in state.battlefield if p.card.name == "Jace Token" and not p.phased]
    return js[0] if js else None


def empower_jace(state: GameState, n: int, src: str = ""):
    """CR 701.71a: se nao controlo uma ficha de Jace, crio uma (azul, 0 de lealdade, [-1]: Surveil 1, [-3]: Draw a card); ponho N contadores de lealdade numa ficha de Jace que controlo.
    Se ja' controlo uma, NAO posso criar outra (ruling 2026-08-21). Os contadores vao pelas substituicoes e disparam All Will Be One."""
    if n <= 0 or state.game_over:
        return
    j = jace_token(state)
    if j is None:
        j = mk_perm(state, "Jace Token", token=True)
        state.battlefield.append(j)
        enter_permanent_token_jace(state, j)
    got = put_counters(state, j, "loyalty", n, "empower_" + src)
    state.m["empower_events"] += 1
    state.m["empower_loyalty"] += got
    mark(state, "first_empower")


def enter_permanent_token_jace(state: GameState, j: Permanent):
    state.m["jace_tokens_created"] += 1
    j.entered_turn = state.turn


# =========================================================
# TERRENOS: entrada, fetch, jogar terreno (Regra 12: arquetipo real de CADA terreno)
# =========================================================
COLOR_WEIGHT = {"W": 1.0, "U": 1.3, "B": 1.0, "R": 0.9, "G": 1.2}


def land_enters_tapped(state: GameState, name: str, forced_tapped: bool = False) -> bool:
    """Arquetipo de entrada de CADA terreno (oraculo): triomes e The World Tree sempre virados; choques: pago 2 de vida se a vida permitir (vida e' rastreada; abaixo de 10 entra virado);
    slowlands (Promenade, Springs, Spire Garden, Stadium): desvirados com 2+ OPONENTES vivos (conta os de agora, ruling 2018/2020); Starting Town: desvirado so' no meu 1o, 2o ou 3o turno;
    fetch, filtros, Command Tower, City of Brass etc.: desvirados."""
    if forced_tapped:
        return True
    k = LANDS[name]["kind"]
    if k in ("triome", "worldtree"):
        return True
    if k == "shock":
        return state.life < 10
    if k == "slow":
        return len(alive_opps(state)) < 2
    if k == "town":
        return state.turn > 3
    return False


def land_cost_life(state: GameState, name: str, tapped: bool) -> int:
    return 2 if (LANDS[name]["kind"] == "shock" and not tapped) else 0


def put_land_onto_battlefield(state: GameState, name: str, tapped: Optional[bool] = None, source: str = "") -> Permanent:
    """TODO ponto de entrada de terreno passa por aqui (jogar, fetch). `tapped=True`: o efeito poe o terreno virado (choque ainda pode pagar 2, mas continua virado: nao paga)."""
    t = True if tapped is True else land_enters_tapped(state, name)
    cost = land_cost_life(state, name, t)
    if cost:
        lose_life(state, cost, "shock")
    p = mk_perm(state, name)
    p.tapped = bool(t)
    state.battlefield.append(p)
    log(state, f"  terreno: {name}{' (virado)' if t else ''} [{source}]")
    land_enters(state, p, source)
    return p


def colors_have(state: GameState) -> collections.Counter:
    """Fontes (permanentes, nao a mao) por cor: terrenos em campo (fetch conta pelas cores dos alvos possiveis), rocks e dorks."""
    have = collections.Counter()
    forest = yavimaya_forest(state)
    anyl = lands_any_color(state)
    for p in state.battlefield:
        if p.phased:
            continue
        nm = p.card.name
        if "land" in p.card.types:
            k = LANDS[nm]["kind"]
            cols = set(LANDS[nm]["prod"]) - {"C"}
            if k in ("tower", "city", "town"):
                cols = set(COLORS5)
            elif k == "orchard":
                cols = set(opp_land_colors(state))
            elif k == "filter":
                cols = set(LANDS[nm]["filt"])
            elif k == "pay1":
                cols = set(LANDS[nm]["out"])
            if anyl:
                cols = set(COLORS5)
            if forest:
                cols.add("G")
            for c in cols:
                have[c] += 1
        elif nm in ("Arcane Signet", "Birds of Paradise"):
            for c in COLORS5:
                have[c] += 1
        elif nm == "Noble Hierarch":
            for c in "GWU":
                have[c] += 1
        elif nm == "Ignoble Hierarch":
            for c in "BRG":
                have[c] += 1
        elif nm == "Fellwar Stone":
            for c in opp_land_colors(state):
                have[c] += 1
    return have


def land_play_score(state: GameState, name: str, hand_after: Optional[list] = None) -> float:
    L = LANDS[name]
    k = L["kind"]
    have = colors_have(state)
    held = [h for h in state.hand if h != name]
    # cores que as cartas da mao pedem (pips) e as que ja' tenho
    need = collections.Counter()
    for h in held:
        for pip in CARD_DB[h].pips:
            for c in pip:
                if c in COLOR_WEIGHT:
                    need[c] += 1.0 / len(pip)
    cols = set(L["prod"]) - {"C"}
    if k in ("tower", "city", "town"):
        cols = set(COLORS5)
    elif k == "orchard":
        cols = set(opp_land_colors(state))
    elif k == "filter":
        cols = set(L["filt"])
    elif k == "pay1":
        cols = set(L["out"])
    elif k == "fetch":
        cols = set()
        for t in L["ftypes"]:
            cols |= {"Forest": {"G"}, "Island": {"U"}, "Swamp": {"B"}, "Mountain": {"R"}, "Plains": {"W"}}[t]
    sc = 0.0
    for c in sorted(cols):
        w = COLOR_WEIGHT[c]
        sc += w * (10.0 / (1 + have[c])) + 3.0 * need[c] / (1 + have[c])
        if have[c] == 0:
            sc += 8.0
    if len(cols) >= 2:
        sc += 2.0
    tapped = land_enters_tapped(state, name)
    if tapped and name != "Starting Town":
        sc -= 3.0 if state.turn <= 5 else 0.5
    if k == "fetch":
        sc += 1.0 if state.turn >= 3 else 0.0
    if k in ("baxter", "greathall", "plaza", "boseiju", "yavimaya"):
        sc -= 2.0 if n_lands(state) < 6 else -0.5
    if k == "worldtree":
        sc += 2.0 if n_lands(state) >= 3 else 0.0
    if k == "orchard" and not opp_land_colors(state):
        sc -= 5.0
    if k == "filter" and n_lands(state) < 2:
        sc -= 4.0
    if k == "pay1" and n_lands(state) < 2:
        sc -= 4.0
    if k == "triome":
        sc -= 0.3
    return sc


def fetch_targets(state: GameState, perm: Permanent) -> list:
    """Cartas de terreno da BIBLIOTECA com um dos subtipos pedidos (busca por SUBTIPO: choques, triomes). A Yavimaya NAO transforma carta na biblioteca em Forest (ruling 2021-06-18)."""
    types = set(LANDS[perm.card.name]["ftypes"])
    seen, out = set(), []
    for c in state.library:
        if c in seen:
            continue
        seen.add(c)
        cc = CARD_DB[c]
        if "land" in cc.types and (cc.land_types & types):
            out.append(c)
    return out


def best_fetch_pick(state: GameState, cands: list) -> Optional[str]:
    if not cands:
        return None
    return max(cands, key=lambda c: (land_play_score(state, c), c))


def crack_fetch(state: GameState, perm: Permanent) -> bool:
    """Fetch real: paga 1 de vida (CUSTO) e sacrifica (a fetch vai ao cemiterio), a habilidade RESOLVE: busca por SUBTIPO, o terreno entra DESVIRADO (sujeito ao proprio arquetipo: choque paga 2 se puder),
    embaralha. So' quebro se existe alvo agora."""
    cands = fetch_targets(state, perm)
    if not cands:
        state.m["fetch_no_target"] += 1
        return False
    state.battlefield.remove(perm)
    lose_life(state, 1, "fetch")
    state.graveyard.append(perm.card.name)
    target = best_fetch_pick(state, fetch_targets(state, perm))
    state.library.remove(target)
    state.rng.shuffle(state.library)
    state.m["fetches_cracked"] += 1
    put_land_onto_battlefield(state, target, source="fetch")
    return True


def land_drops_available(state: GameState) -> int:
    return 1 + state.extra_land_drops


def count_castable(state: GameState) -> int:
    n = 0
    seen = []
    for name in state.hand:
        if name in seen:
            continue
        seen.append(name)
        c = CARD_DB[name]
        if "land" in c.types:
            continue
        if can_cast_name(state, name):
            n += 1
    return n


def tapped_first_pick(state: GameState, cands: list) -> Optional[str]:
    """T1/T2: se existe terreno que entra virado, so' o jogo ele primeiro quando o ensaio a seco mostra que isso NAO custa nenhuma conjuracao (CLAUDE.md Regra #10)."""
    tapped = [c for c in cands if land_enters_tapped(state, c)]
    if not tapped:
        return None
    untapped = [c for c in cands if c not in tapped]
    if not untapped:
        return None
    base = count_castable(state)
    best_un = max(untapped, key=lambda c: (land_play_score(state, c), c))
    uid0 = state.next_uid
    tmp = mk_perm(state, best_un)
    state.battlefield.append(tmp)
    with_un = count_castable(state)
    state.battlefield.remove(tmp)
    state.next_uid = uid0                    # ensaio a seco sem efeito colateral
    if with_un > base:
        state.m["tapped_land_skipped_for_play"] += 1
        return None
    pick = max(tapped, key=lambda c: (land_play_score(state, c), c))
    state.m["tapped_land_first_plays"] += 1
    return pick


def play_land_phase(state: GameState):
    while state.lands_played_this_turn < land_drops_available(state) and not state.game_over:
        cands = []
        for c in state.hand:
            if "land" in CARD_DB[c].types and c not in cands:
                cands.append(c)
        if state.impulse:
            for c in state.impulse:
                if "land" in CARD_DB[c].types and c not in cands:
                    cands.append(c)
        if "wrenn" in state.emblems:
            for c in state.graveyard:
                if "land" in CARD_DB[c].types and c not in cands:
                    cands.append(c)
        if not cands:
            break
        pick = None
        if TAPPED_LAND_FIRST_ENABLED and state.turn <= TAPPED_LAND_FIRST_MAX_TURN:
            pick = tapped_first_pick(state, cands)
            if state.ghost:
                pick = None
        if pick is None:
            pick = max(cands, key=lambda c: (land_play_score(state, c), c))
        if pick in state.hand:
            state.hand.remove(pick)
        elif pick in state.impulse:
            state.impulse.remove(pick)
        else:
            state.graveyard.remove(pick)
            state.m["recursion_events"] += 1
        state.lands_played_this_turn += 1
        p = put_land_onto_battlefield(state, pick, source="play")
        if LANDS[pick]["kind"] == "fetch" and FETCH_LANDS_ENABLED and state.life > 3:
            crack_fetch(state, p)


# =========================================================
# CUSTO E CONJURACAO
# =========================================================

def commander_tax(state: GameState) -> int:
    return 2 * state.commander_cast_count


def creatures_on_battlefield_all(state: GameState) -> int:
    """Blasphemous Act: 'costs {1} less for each creature on the battlefield' (de QUALQUER jogador): as minhas + as dos oponentes (so' no modo de resiliencia ha' tabuleiro de oponente)."""
    return len(creatures(state)) + sum(len(o.board) for o in state.opps)


def effective_cost(state: GameState, name: str, life_pips: int = 0):
    """(generico, pips) da conjuracao: custo impresso, + imposto do comandante (CR 903.8: conta conjuracoes, inclusive contra-atacadas), depois reducoes (so' abatem GENERICO, CR 601.2f):
    Tam e Oath of Ajani abatem {1} de magia de planeswalker; Blasphemous Act abate {1} por criatura em campo. `life_pips`: quantos pips phyrexianos pago com 2 de vida cada (Nissa, Vraska)."""
    c = CARD_DB[name]
    g = c.generic
    pips = list(c.pips)
    if life_pips:
        pips = pips[:len(pips) - life_pips]
    if "commander" in c.tags:
        g += commander_tax(state)
    if "planeswalker" in c.types:
        g = max(0, g - count_named(state, "Tam, the Possibility") - count_named(state, "Oath of Ajani"))
    if "blasphemous" in c.tags:
        g = max(0, g - creatures_on_battlefield_all(state))
    return g, tuple(pips)


def cast_cost_option(state: GameState, name: str, zone: str = "hand"):
    """Primeira forma viavel de pagar: tudo em mana; senao pago os pips phyrexianos com vida (so' se a vida >= 2k + 12). Emblema da Tamiyo (-7): 'You may cast spells from your hand without paying
    their mana costs' (so' da MAO: a Tam na zona de comando, a Wrenn do cemiterio e a Chandra do exilio pagam o custo normal)."""
    c = CARD_DB[name]
    if "tamiyo" in state.emblems and zone == "hand" and "land" not in c.types:
        return (0, (), 0)
    ctx = ctx_for(name)
    for k in range(0, c.phy + 1):
        if k and state.life < 2 * k + 12:
            break
        g, pips = effective_cost(state, name, k)
        if can_pay(state, g, pips, ctx):
            return (g, pips, k)
    return None


def aura_host(state: GameState, name: str) -> Optional[Permanent]:
    """Alvo da aura: Leyline Immersion -> criatura lendaria (a Tam; senao a Kiora); Teferi's/Liliana's Talent -> planeswalker."""
    if name == "Leyline Immersion":
        for nm in ("Tam, the Possibility", "Kiora of Salt and Sand", "Boo Token"):
            for p in perms_named(state, nm):
                if not any(a.attached_to == p.uid and a.card.name == name for a in state.battlefield):
                    return p
        return None
    cands = [p for p in pws(state) if not any(a.attached_to == p.uid and a.card.name == name for a in state.battlefield)]
    if not cands:
        return None
    if name == "Teferi's Talent":
        return max(cands, key=lambda p: (CARD_ULT.get(p.card.name, 0) > 0, loyalty(p), -p.uid))
    return max(cands, key=lambda p: (loyalty(p), -p.uid))


CARD_ULT = {}


def can_cast_name(state: GameState, name: str, zone: str = "hand") -> bool:
    c = CARD_DB[name]
    if "land" in c.types:
        return False
    if "commander" in c.tags and not state.commander_in_cz and zone == "cz":
        return False
    if "aura" in c.tags and aura_host(state, name) is None:
        return False
    return cast_cost_option(state, name, zone) is not None


def counterspell_check(state: GameState, name: str) -> bool:
    """Modo de resiliencia: um oponente pode anular a magia (MV >= 3). Devolve True se foi anulada."""
    if not state.resilience or state.turn <= INTERACTION_SETUP_TURNS or CARD_DB[name].mv < COUNTER_MIN_MV:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * COUNTERSPELL_CHANCE_FACTOR * (0.0 if "narset" in state.emblems else 1.0):
        return False
    state.m["smart_counters"] += 1
    return True


def on_cast(state: GameState, name: str, source_zone: str = "hand"):
    """Gatilhos de 'quando voce conjura' (resolvem ANTES da magia): contagem de magias, Dreamtide Whale (a 2a magia de QUALQUER jogador no turno), e os de magia nao-criatura: Flux Channeler (proliferate),
    Ichormoon Gauntlet (contador a mais), Saheeli (ficha Servo), Displacer Kitten (piscar)."""
    c = CARD_DB[name]
    state.spells_cast_this_turn += 1
    state.m["spells_cast_total"] += 1
    state.casts_by_card[name] = state.casts_by_card.get(name, 0) + 1
    nc = "creature" not in c.types
    if nc:
        state.noncreature_spells_this_turn += 1
        state.m["noncreature_spells_total"] += 1
    state.spells_this_turn_by_player[0] = state.spells_this_turn_by_player.get(0, 0) + 1
    if state.spells_this_turn_by_player[0] == 2:
        whale_trigger(state)
    if nc:
        for _ in range(count_named(state, "Flux Channeler")):
            proliferate(state, "flux_channeler")
        for g in perms_named(state, "Ichormoon Gauntlet"):
            gauntlet_cast_trigger(state)
        for _ in range(count_named(state, "Saheeli, Sublime Artificer")):
            create_token(state, "Servo Token", 1, src="saheeli")
        for k in perms_named(state, "Displacer Kitten"):
            kitten_trigger(state, name)
    if "pw" in c.tags:
        state.m["pw_spells_cast"] += 1


def whale_trigger(state: GameState):
    for _ in range(count_named(state, "Dreamtide Whale")):
        proliferate(state, "dreamtide_whale")


def gauntlet_cast_trigger(state: GameState):
    """'Whenever you cast a noncreature spell, choose a counter on target permanent. Put an additional counter of that kind on that permanent.' Alvo: o planeswalker com mais valor em +1 (o que mais perto esta de um ultimate)."""
    cands = [p for p in pws(state) if loyalty(p) >= 1]
    if not cands:
        cands = [p for p in vis(state) if p.ctr.get("p1p1", 0) > 0 or p.ctr.get("time", 0) > 0]
        if not cands:
            return
        t = max(cands, key=lambda p: (p.ctr.get("p1p1", 0), -p.uid))
        put_counters(state, t, "p1p1" if t.ctr.get("p1p1", 0) else "time", 1, "gauntlet")
        state.m["gauntlet_counters"] += 1
        return
    t = best_pw_for_counter(state, cands)
    put_counters(state, t, "loyalty", 1, "gauntlet")
    state.m["gauntlet_counters"] += 1


def kitten_trigger(state: GameState, cast_name: str):
    """Displacer Kitten (Avoidance): 'Whenever you cast a noncreature spell, exile up to one target nonland permanent you control, then return that card to the battlefield under its owner's control.'"""
    t = best_blink_target(state)
    if t is None or blink_value(state, t) < 14:
        return
    state.m["kitten_blinks"] += 1
    blink(state, t, "kitten")


def best_pw_for_counter(state: GameState, cands: list) -> Permanent:
    """O planeswalker que mais ganha +1: o mais perto do ultimate (sem passar), depois o de menor lealdade."""
    def key(p):
        u = ult_cost(p.card.name)
        gap = (u - loyalty(p)) if u else 99
        reach = 0 if (u and 0 < gap <= 3) else 1
        return (reach, gap if u else 99, loyalty(p), p.uid)
    return min(cands, key=key)


def ult_cost(name: str) -> int:
    return PW_ULT.get(name, 0)


PW_ULT = {"Chandra, Legacy of Fire": 0, "Domri, Chaos Bringer": 8, "Garruk Wildspeaker": 4, "Wrenn and Realmbreaker": 7, "Dack Fayden": 6, "Dihada, Binder of Wills": 11, "Garruk, Curse Breaker": 4,
          "Minsc & Boo, Timeless Heroes": 0, "Narset Transcendent": 9, "Professor Dellian Fel": 6, "Tamiyo, Field Researcher": 7, "Teferi, Hero of Dominaria": 8, "Teferi, Temporal Archmage": 10,
          "Garruk, Veiled Butcher": 0, "Nissa, Ascended Animist": 7, "Oko, Thief of Crowns": 5, "The Eternal Wanderer": 4, "Vraska, Betrayal's Sting": 9, "Ajani Unrelenting": 0,
          "Elspeth, Sun's Champion": 7, "Kasmina, Enigma Sage": 8, "Saheeli, Sublime Artificer": 0, "Vronos, Masked Inquisitor": 7, "Aminatou, the Fateshifter": 0, "Tezzeret the Seeker": 5, "Jace Token": 3}


def cast_card(state: GameState, name: str, zone: str = "hand", free: bool = False) -> bool:
    """Conjura `name` (mao, zona de comando, cemiterio via emblema da Wrenn, exilio da Chandra). Paga custo, dispara gatilhos de conjuracao, resolve."""
    c = CARD_DB[name]
    life_pips = 0
    if not free:
        opt = cast_cost_option(state, name, zone)
        if opt is None:
            return False
        g, pips, life_pips = opt
        state._pool_used = 0
        if not pay_mana(state, g, pips, ctx_for(name)):
            return False
        if "tamiyo" in state.emblems and zone == "hand":
            state.m["tamiyo_free_casts"] += 1
        # Domri +1: 'If that mana is spent on a creature spell, it gains riot.' O mana da Domri e' rastreado como contagem (`riot_pool`) dentro do mana flutuante
        if state._pool_used > 0 and state.riot_pool > 0:
            if "creature" in c.types:
                state.riot_flag = True
                state.m["riot_creatures"] += 1
            state.riot_pool = max(0, state.riot_pool - state._pool_used)
        if life_pips:
            lose_life(state, 2 * life_pips, "phyrexian")
            state.m["compleated_casts"] += 1
    if zone == "hand" and name in state.hand:
        state.hand.remove(name)
    elif zone == "graveyard" and name in state.graveyard:
        state.graveyard.remove(name)
        state.m["recursion_events"] += 1
    elif zone == "impulse" and name in state.impulse:
        state.impulse.remove(name)
    if "commander" in c.tags:
        state.commander_cast_count += 1
        state.commander_in_cz = False
        if state.commander_cast_turn is None:
            state.commander_cast_turn = state.turn
    log(state, f"  conjura: {name} ({zone}{', gratis' if free else ''})")
    state.cast_zone = zone
    on_cast(state, name, zone)
    if state.game_over:
        return True
    if counterspell_check(state, name):
        if "commander" in c.tags:
            state.commander_in_cz = True
        else:
            state.graveyard.append(name)
        state.m["our_spells_countered"] += 1
        return True
    resolve_spell(state, name, life_pips)
    return True


def resolve_spell(state: GameState, name: str, life_pips: int = 0):
    c = CARD_DB[name]
    if "instant" in c.types or "sorcery" in c.types:
        resolve_instant_sorcery(state, name)
        return
    p = mk_perm(state, name)
    if life_pips:
        p.ctr["compleated_less"] = 2 * life_pips
    if "aura" in c.tags:
        host = aura_host(state, name)
        if host is None:
            state.graveyard.append(name)
            return
        p.attached_to = host.uid
    state.battlefield.append(p)
    if "commander" in c.tags:
        state.commander_uid = p.uid
    if state.riot_flag:
        state.riot_flag = False
        if "creature" in c.types:
            # riot: 'enters with your choice of a +1/+1 counter or haste': haste pro mana-dork e pra criatura grande (ataca ja'); contador nos demais (e dispara All Will Be One)
            if "dork" in c.tags or c.power >= 5:
                p.haste_until_eot = True
                state.m["riot_haste"] += 1
            else:
                put_counters(state, p, "p1p1", 1, "riot")
                state.m["riot_counters"] += 1
    if name in ("Sol Ring", "Arcane Signet", "Fellwar Stone", "Birds of Paradise", "Bloom Tender", "Faeburrow Elder", "Noble Hierarch", "Ignoble Hierarch", "Chromatic Orrery", "Leyline Immersion"):
        state.m["ramp_pieces"] += 1
    enter_permanent(state, p, from_cast=True)
    sba(state)


def apply_etb(state: GameState, p: Permanent, from_cast: bool):
    nm = p.card.name
    if "way" in p.card.tags:
        m = re.search(r"empower Jace (\d+)", p.card.text)
        empower_jace(state, int(m.group(1)), "way")
    elif nm == "Sanctum Lurker":
        empower_jace(state, 1, "lurker")
    elif nm == "Oath of Nissa":
        oath_of_nissa_etb(state)
    elif nm == "Oath of Teferi":
        t = best_blink_target(state, exclude=p)
        if t is not None and blink_value(state, t) >= 10:
            state.delayed_return.append(t.uid)
            state.m["oath_blink_marked"] += 1
            exile_for_delayed_return(state, t)
    elif nm == "Minsc & Boo, Timeless Heroes":
        make_boo(state, "etb")


def exile_for_delayed_return(state: GameState, t: Permanent):
    """Oath of Teferi / Eternal Wanderer: exila agora, devolve no inicio do proximo end step (objeto novo). Ficha nao volta."""
    if t not in state.battlefield:
        return
    nm = t.card.name
    token = t.is_token
    state.battlefield.remove(t)
    for a in [q for q in state.battlefield if q.attached_to == t.uid]:
        state.battlefield.remove(a)
        state.graveyard.append(a.card.name)
    state.delayed_return = [x for x in state.delayed_return if x != t.uid]
    if not token:
        state.delayed_return.append(nm)


def oath_of_nissa_etb(state: GameState):
    """'Look at the top three cards of your library. You may reveal a creature, land, or planeswalker card from among them and put it into your hand. Put the rest on the bottom in any order.'"""
    top = state.library[:3]
    del state.library[:3]
    held_lands = sum(1 for h in state.hand if "land" in CARD_DB[h].types)
    pick = None
    pwc = [c for c in top if "planeswalker" in CARD_DB[c].types]
    if pwc:
        pick = max(pwc, key=lambda c: (CARD_PRIORITY.get(c, 20), c))
    else:
        lands = [c for c in top if "land" in CARD_DB[c].types]
        cr = [c for c in top if "creature" in CARD_DB[c].types]
        if lands and n_lands(state) + held_lands < 5:
            pick = max(lands, key=lambda c: (land_play_score(state, c), c))
        elif cr:
            pick = max(cr, key=lambda c: (CARD_PRIORITY.get(c, 20), c))
        elif lands:
            pick = max(lands, key=lambda c: (land_play_score(state, c), c))
    if pick:
        top.remove(pick)
        state.hand.append(pick)
        state.m["oath_of_nissa_hits"] += 1
    state.library.extend(top)


def make_boo(state: GameState, why: str):
    """Minsc & Boo: 'When Minsc & Boo enters and at the beginning of your upkeep, you may create Boo, a legendary 1/1 red Hamster creature token with trample and haste.' Regra da lenda: so' um Boo."""
    if any(q.card.name == "Boo Token" for q in state.battlefield):
        return
    create_token(state, "Boo Token", 1, haste=True, src="boo")
    state.m["boo_created"] += 1


# =========================================================
# HABILIDADES DE LEALDADE: dados + efeito + pontuacao (proprias e CONCEDIDAS no mesmo conjunto de candidatas)
# =========================================================
# ABILITIES[fonte] = [(chave, custo)]  custo int (+N poe, -N tira, 0) ou "X" (-X variavel)
ABILITIES = {
    "Chandra, Legacy of Fire": [("+1", 1), ("0", 0)],
    "Domri, Chaos Bringer": [("+1", 1), ("-3", -3), ("-8", -8)],
    "Garruk Wildspeaker": [("+1", 1), ("-1", -1), ("-4", -4)],
    "Wrenn and Realmbreaker": [("+1", 1), ("-2", -2), ("-7", -7)],
    "Dack Fayden": [("+1", 1), ("-2", -2), ("-6", -6)],
    "Dihada, Binder of Wills": [("+2", 2), ("-3", -3), ("-11", -11)],
    "Garruk, Curse Breaker": [("+2", 2), ("-3", -3), ("-4", -4)],
    "Minsc & Boo, Timeless Heroes": [("+1", 1), ("-2", -2)],
    "Narset Transcendent": [("+1", 1), ("-2", -2), ("-9", -9)],
    "Professor Dellian Fel": [("+2", 2), ("0", 0), ("-3", -3), ("-6", -6)],
    "Tamiyo, Field Researcher": [("+1", 1), ("-2", -2), ("-7", -7)],
    "Teferi, Hero of Dominaria": [("+1", 1), ("-3", -3), ("-8", -8)],
    "Teferi, Temporal Archmage": [("+1", 1), ("-1", -1), ("-10", -10)],
    "Garruk, Veiled Butcher": [("+2", 2), ("-2", -2), ("-3", -3)],
    "Nissa, Ascended Animist": [("+1", 1), ("-1", -1), ("-7", -7)],
    "Oko, Thief of Crowns": [("+2", 2), ("+1", 1), ("-5", -5)],
    "The Eternal Wanderer": [("+1", 1), ("0", 0), ("-4", -4)],
    "Vraska, Betrayal's Sting": [("0", 0), ("-2", -2), ("-9", -9)],
    "Ajani Unrelenting": [("+1", 1), ("-2", -2), ("-3", -3)],
    "Elspeth, Sun's Champion": [("+1", 1), ("-3", -3), ("-7", -7)],
    "Kasmina, Enigma Sage": [("+2", 2), ("-X", "X"), ("-8", -8)],
    "Saheeli, Sublime Artificer": [("-2", -2)],
    "Vronos, Masked Inquisitor": [("+1", 1), ("-2", -2), ("-7", -7)],
    "Aminatou, the Fateshifter": [("+1", 1), ("-1", -1), ("-6", -6)],
    "Tezzeret the Seeker": [("+1", 1), ("-X", "X"), ("-5", -5)],
    "Jace Token": [("-1", -1), ("-3", -3)],
}
# habilidades concedidas
GRANTED = {
    "Way of the Pyromancer": [("+1", 1)],
    "Way of the Warlord": [("-4", -4)],
    "Way of the Deathbringer": [("-2", -2)],
    "Way of the Healer": [("-2", -2)],
    "Way of the Wildspeaker": [("-4", -4)],
    "Ichormoon Gauntlet": [("0", 0), ("-12", -12)],
    "Kiora of Salt and Sand": [("-8", -8)],
    "Sanctum Lurker": [("+2", 2)],
}
KASMINA = "Kasmina, Enigma Sage"
EFFECT = {}          # (fonte, chave) -> fn(state, host, x)
SCORE = {}           # (fonte, chave) -> fn(state, host) -> float | None  (None = nao vale / nao pode)


def eff(src, key):
    def deco(fn):
        EFFECT[(src, key)] = fn
        return fn
    return deco


def sc(src, key):
    def deco(fn):
        SCORE[(src, key)] = fn
        return fn
    return deco


def acts_allowed(state: GameState) -> int:
    """Oath of Teferi: duas ativacoes por planeswalker por turno; The Chain Veil soma mais uma (por uso)."""
    return (2 if has_perm(state, "Oath of Teferi") else 1) + state.m.get("_veil_extra", 0)


def pw_acts_used(state: GameState, p: Permanent) -> int:
    return p.acts if p.acts_turn_id == state.turn_id else 0


def pw_can_activate(state: GameState, p: Permanent, window: str = "main") -> bool:
    if not is_pw(p):
        return False
    if window == "opp":
        return "teferi_ta" in state.emblems and pw_acts_used(state, p) < 1
    return pw_acts_used(state, p) < acts_allowed(state)


def own_abilities(state: GameState, host: Permanent) -> list:
    nm = host.card.name
    out = [(nm, k, c) for k, c in ABILITIES.get(nm, [])]
    for g, lst in GRANTED.items():
        if has_perm(state, g):
            out += [(g, k, c) for k, c in lst]
    kas = [q for q in perms_named(state, KASMINA) if q is not host]
    if kas:
        out += [(KASMINA, k, c) for k, c in ABILITIES[KASMINA]]
    for a in state.battlefield:
        if a.attached_to == host.uid and a.card.name in ("Teferi's Talent", "Liliana's Talent") and not a.phased:
            out.append((a.card.name, "-12" if a.card.name == "Teferi's Talent" else "-8", -12 if a.card.name == "Teferi's Talent" else -8))
    return out


def ability_options(state: GameState, host: Permanent) -> list:
    """[(score, fonte, chave, x)] das habilidades possiveis agora, melhor primeiro."""
    L = loyalty(host)
    lurker = has_perm(state, "Sanctum Lurker")
    out = []
    for src, key, cost in own_abilities(state, host):
        fn = SCORE.get((src, key))
        if fn is None:
            continue
        if cost == "X":
            xs = range(1, L + 1)
        else:
            xs = [0]
            if cost < 0 and L < -cost:
                continue
        for x in xs:
            s = fn(state, host) if cost != "X" else fn(state, host, x)
            if s is None:
                continue
            out.append((s, src, key, x))
    out.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    return out


def activate_ability(state: GameState, host: Permanent, src: str, key: str, x: int, window: str = "main") -> bool:
    """Ativa UMA habilidade de lealdade: paga o custo (contadores de custo NAO sao substituidos, mas disparam All Will Be One), dispara os gatilhos de 'whenever you activate a loyalty ability'
    (Ajani Unrelenting: a ficha Cadet entra ANTES da habilidade resolver; Way of the Paradox: 1 de vida e 2o terreno; Way of the Mind Sculptor: compra se tirou 2+; Kiora), resolve, SBA."""
    cost = next((c for s, k, c in own_abilities(state, host) if s == src and k == key), None)
    if cost is None or host not in state.battlefield:
        return False
    log(state, f"  habilidade: {host.card.name} [{src}:{key}] custo {cost} x={x} (lealdade {loyalty(host)})")
    L = loyalty(host)
    removed = 0
    if cost == "X":
        removed = x
    elif cost < 0:
        removed = -cost
    if removed > L:
        return False
    if cost == "X" or cost < 0:
        remove_loyalty(state, host, removed)
    elif cost > 0:
        put_counters(state, host, "loyalty", cost, "cost_" + key, cost=True)
    if host.acts_turn_id != state.turn_id:
        host.acts_turn_id = state.turn_id
        host.acts = 0
    host.acts += 1
    state.activated_loyalty_this_turn = True
    state.loyalty_acts_this_turn += 1
    state.m["pw_activations"] += 1
    state.activations[(src, key)] = state.activations.get((src, key), 0) + 1
    state.m["pw_act_by_" + host.card.name] += 1
    if window == "opp":
        state.m["pw_activations_opp_turn"] += 1
    # gatilhos
    for _ in range(count_named(state, "Ajani Unrelenting")):
        create_token(state, "Cadet Token", 1, src="ajani")           # entra ANTES da habilidade resolver: a +1 (que atinge 'creatures you control' na resolucao) ja' o inclui, uma vez so'
        state.m["ajani_cadets"] += 1
    for _ in range(count_named(state, "Way of the Paradox")):
        gain_life(state, 1, "way_paradox")
        state.extra_land_drops += 1
        state.m["paradox_triggers"] += 1
    if removed >= 2:
        for _ in range(count_named(state, "Way of the Mind Sculptor")):
            draw_cards(state, 1, "way_mind_sculptor")
    if cost == "X":
        EFFECT[(src, key)](state, host, x)
    else:
        EFFECT[(src, key)](state, host, 0)
    if remove_ult(src, key, cost):
        state.m["ultimates_used"] += 1
        host.first_ult_done = True
        mark(state, "first_ultimate")
    sba(state)
    return True


def remove_ult(src: str, key: str, cost) -> bool:
    ult = {("Domri, Chaos Bringer", "-8"), ("Wrenn and Realmbreaker", "-7"), ("Dack Fayden", "-6"), ("Dihada, Binder of Wills", "-11"), ("Narset Transcendent", "-9"),
           ("Professor Dellian Fel", "-6"), ("Tamiyo, Field Researcher", "-7"), ("Teferi, Hero of Dominaria", "-8"), ("Teferi, Temporal Archmage", "-10"), ("Nissa, Ascended Animist", "-7"),
           ("Oko, Thief of Crowns", "-5"), ("The Eternal Wanderer", "-4"), ("Vraska, Betrayal's Sting", "-9"), ("Elspeth, Sun's Champion", "-7"), ("Kasmina, Enigma Sage", "-8"),
           ("Vronos, Masked Inquisitor", "-7"), ("Aminatou, the Fateshifter", "-6"), ("Tezzeret the Seeker", "-5"), ("Garruk Wildspeaker", "-4"), ("Garruk, Curse Breaker", "-4"),
           ("Ichormoon Gauntlet", "-12"), ("Kiora of Salt and Sand", "-8"), ("Teferi's Talent", "-12"), ("Liliana's Talent", "-8")}
    return (src, key) in ult


# ---------- helpers de politica ----------

def mana_shortage(state: GameState) -> bool:
    """Ha carta na mao que eu conjuraria com ate' 3 de mana a mais?"""
    for h in sorted(set(state.hand)):
        c = CARD_DB[h]
        if "land" in c.types or can_cast_name(state, h):
            continue
        g, pips = effective_cost(state, h)
        if g + len(pips) <= available_mana(state) + 3 and CARD_PRIORITY.get(h, 20) >= 40:
            return True
    return False


def untapped_attackers(state: GameState) -> list:
    return [p for p in creatures(state) if can_attack(state, p)]


def tapped_lands(state: GameState) -> list:
    return [p for p in lands_of(state) if p.tapped]


def total_pw_count(state: GameState) -> int:
    return len(pws(state))


def opp_threat_power(state: GameState) -> int:
    return sum(c["p"] for o in alive_opps(state) for c in o.board)


# ---------- Chandra, Legacy of Fire ----------
@eff("Chandra, Legacy of Fire", "+1")
def _chandra_plus1(state, host, x):
    n = len(pws(state))
    state.pool["R"] = state.pool.get("R", 0) + n
    state.m["chandra_mana"] += n


@sc("Chandra, Legacy of Fire", "+1")
def _chandra_plus1_s(state, host):
    return 62 if mana_shortage(state) else 32


@eff("Chandra, Legacy of Fire", "0")
def _chandra_zero(state, host, x):
    """'Remove a loyalty counter from each of any number of permanents you control. Exile that many cards from the top of your library. You may play them this turn.'"""
    S = chandra_zero_set(state)
    for p in S:
        remove_loyalty(state, p, 1)
    k = len(S)
    cards = state.library[:k]
    del state.library[:k]
    state.impulse.extend(cards)
    state.m["chandra_exiled"] += k
    state.m["impulse_cards"] += k


def chandra_zero_set(state: GameState) -> list:
    out = []
    for p in pws(state):
        L = loyalty(p)
        u = ult_cost(p.card.name)
        if L >= 3 and (p.first_ult_done or (u == 0) or L >= max(6, u + 2)):
            out.append(p)
    return out


@sc("Chandra, Legacy of Fire", "0")
def _chandra_zero_s(state, host):
    S = chandra_zero_set(state)
    if len(S) >= 2 and len(state.library) > 18 and len(state.hand) <= 3:
        return 36 + 4 * len(S)
    return None


# ---------- Domri, Chaos Bringer ----------
@eff("Domri, Chaos Bringer", "+1")
def _domri_plus1(state, host, x):
    need = collections.Counter()
    for h in state.hand:
        for pip in CARD_DB[h].pips:
            for c in pip & {"R", "G"}:
                need[c] += 1
    col = "R" if need["R"] > need["G"] and not colors_have(state)["R"] > 2 else "G"
    state.pool[col] = state.pool.get(col, 0) + 1
    state.riot_pool += 1


@sc("Domri, Chaos Bringer", "+1")
def _domri_plus1_s(state, host):
    return 56 if mana_shortage(state) else 30


@eff("Domri, Chaos Bringer", "-3")
def _domri_minus3(state, host, x):
    top = state.library[:4]
    del state.library[:4]
    cr = sorted([c for c in top if "creature" in CARD_DB[c].types], key=lambda c: (-CARD_PRIORITY.get(c, 20), c))[:2]
    for c in cr:
        top.remove(c)
        state.hand.append(c)
    state.rng.shuffle(top)
    state.library.extend(top)
    state.m["domri_dig_hits"] += len(cr)


@sc("Domri, Chaos Bringer", "-3")
def _domri_minus3_s(state, host):
    return 40 if loyalty(host) >= 4 and len(state.library) > 12 else None


@eff("Domri, Chaos Bringer", "-8")
def _domri_ult(state, host, x):
    state.emblems.append("domri")


@sc("Domri, Chaos Bringer", "-8")
def _domri_ult_s(state, host):
    return 92


# ---------- Garruk Wildspeaker ----------
def untap_best_lands(state: GameState, n: int) -> int:
    """Desvira ate' N terrenos virados (os que mais ajudam: cor que falta, depois os de mais mana/flexiveis)."""
    cands = [p for p in lands_of(state) if p.tapped]
    cands.sort(key=lambda p: (-len(set(LANDS[p.card.name]["prod"]) - {"C"}) - (3 if LANDS[p.card.name]["kind"] in ("tower", "city") else 0), p.uid))
    k = 0
    for p in cands[:n]:
        p.tapped = False
        k += 1
    state.m["lands_untapped_by_effect"] += k
    return k


@eff("Garruk Wildspeaker", "+1")
def _garruk_w_plus1(state, host, x):
    untap_best_lands(state, 2)


@sc("Garruk Wildspeaker", "+1")
def _garruk_w_plus1_s(state, host):
    t = len(tapped_lands(state))
    return 64 if (t >= 1 and mana_shortage(state)) else (40 if t >= 2 else 26)


@eff("Garruk Wildspeaker", "-1")
def _garruk_w_minus1(state, host, x):
    create_token(state, "Beast3 Token", 1, src="garruk_w")


@sc("Garruk Wildspeaker", "-1")
def _garruk_w_minus1_s(state, host):
    return 52 if loyalty(host) >= 2 else None


@eff("Garruk Wildspeaker", "-4")
def _garruk_w_overrun(state, host, x):
    for p in creatures(state):
        p.temp_p += 3
        p.temp_t += 3
        p.ctr["trample_eot"] = 1
    state.m["overrun_uses"] += 1


@sc("Garruk Wildspeaker", "-4")
def _garruk_w_overrun_s(state, host):
    return 84 if len(untapped_attackers(state)) >= 3 and loyalty(host) >= 4 and state.phase == "main1" else None


# ---------- Wrenn and Realmbreaker ----------
@eff("Wrenn and Realmbreaker", "+1")
def _wrenn_plus1(state, host, x):
    cands = [p for p in lands_of(state) if not p.tapped and p.anim is None and LANDS[p.card.name]["kind"] not in ("fetch",)]
    if not cands:
        return
    cands.sort(key=lambda p: (land_play_score_perm(state, p), p.uid))
    p = cands[0]
    p.anim = "next_turn"
    p.base_pt = (3, 3)
    p.haste_until_eot = True
    p.ctr["vigilance"] = 1
    state.m["wrenn_land_animated"] += 1


def land_play_score_perm(state: GameState, p: Permanent) -> float:
    k = LANDS[p.card.name]["kind"]
    cols = set(LANDS[p.card.name]["prod"]) - {"C"}
    return len(cols) * 3 + (6 if k in ("tower", "city", "town") else 0) + (4 if k in ("shock", "triome") else 0) - (3 if k in ("baxter", "greathall", "plaza", "boseiju", "yavimaya") else 0)


@sc("Wrenn and Realmbreaker", "+1")
def _wrenn_plus1_s(state, host):
    return 46 if state.phase == "main1" else 40


@eff("Wrenn and Realmbreaker", "-2")
def _wrenn_minus2(state, host, x):
    top = state.library[:3]
    del state.library[:3]
    state.graveyard.extend(top)
    perm = [c for c in top if any(t in CARD_DB[c].types for t in ("creature", "artifact", "enchantment", "planeswalker", "land"))]
    if perm:
        held_lands = sum(1 for h in state.hand if "land" in CARD_DB[h].types)
        def val(c):
            cc = CARD_DB[c]
            if "land" in cc.types:
                return 60 if n_lands(state) + held_lands < 5 else 8
            return CARD_PRIORITY.get(c, 20)
        pick = max(perm, key=lambda c: (val(c), c))
        state.graveyard.remove(pick)
        state.hand.append(pick)
        state.m["wrenn_minus2_hits"] += 1
    state.m["self_mill_cards"] += 3


@sc("Wrenn and Realmbreaker", "-2")
def _wrenn_minus2_s(state, host):
    return 50 if loyalty(host) >= 3 and len(state.hand) <= 3 and len(state.library) > 14 else None


@eff("Wrenn and Realmbreaker", "-7")
def _wrenn_ult(state, host, x):
    state.emblems.append("wrenn")


@sc("Wrenn and Realmbreaker", "-7")
def _wrenn_ult_s(state, host):
    return 80


# ---------- Dack Fayden ----------
def discard_value(state: GameState, c: str) -> float:
    cc = CARD_DB[c]
    if "land" in cc.types:
        return 6.0 if n_lands(state) >= 6 else 55.0
    return float(CARD_PRIORITY.get(c, 25)) + 0.1 * cc.mv


def discard_cards(state: GameState, n: int):
    for _ in range(n):
        if not state.hand:
            return
        c = min(state.hand, key=lambda x: (discard_value(state, x), x))
        state.hand.remove(c)
        state.graveyard.append(c)
        state.m["cards_discarded"] += 1


@eff("Dack Fayden", "+1")
def _dack_plus1(state, host, x):
    draw_cards(state, 2, "dack")
    discard_cards(state, 2)


@sc("Dack Fayden", "+1")
def _dack_plus1_s(state, host):
    junk = sum(1 for h in state.hand if discard_value(state, h) < 20)
    return 54 if junk >= 2 else 44


@eff("Dack Fayden", "-2")
def _dack_minus2(state, host, x):
    state.m["proxy_steal_artifact"] += 1
    state.m["interaction_plays"] += 1


@sc("Dack Fayden", "-2")
def _dack_minus2_s(state, host):
    return 28 if loyalty(host) >= 3 and state.target_ok else None


@eff("Dack Fayden", "-6")
def _dack_ult(state, host, x):
    state.emblems.append("dack")          # 'Whenever you cast a spell that targets one or more permanents, gain control of those permanents': nenhuma magia da lista mira permanente (emblema sem uso)


@sc("Dack Fayden", "-6")
def _dack_ult_s(state, host):
    return None                           # emblema sem alvo na lista (checklist): nao vale gastar 6


# ---------- Dihada, Binder of Wills ----------
def legendary_card(c: str) -> bool:
    return CARD_DB[c].legendary


def dihada_target(state: GameState) -> Optional[Permanent]:
    """+2: 'Up to one target legendary creature gains vigilance, lifelink, and indestructible until your next turn.' Alvo: no modo de resiliencia a Tam (protege o motor da remocao); senao o legendario que ataca
    (Boo com contadores: o lifelink vira vida, que alimenta o emblema da Dellian)."""
    leg = [p for p in creatures(state) if is_legendary(p)]
    if not leg:
        return None
    def v(p):
        return (50 if (p.card.name == "Tam, the Possibility" and state.resilience) else 0) + (power(state, p) if can_attack(state, p) or p.card.name == "Boo Token" else 0)
    return max(leg, key=lambda p: (v(p), -p.uid))


@eff("Dihada, Binder of Wills", "+2")
def _dihada_plus2(state, host, x):
    t = dihada_target(state)
    if t is not None:
        state.dihada_shield = t.uid
        state.m["dihada_shields"] += 1


@sc("Dihada, Binder of Wills", "+2")
def _dihada_plus2_s(state, host):
    return 36 if loyalty(host) < 6 else 24


@eff("Dihada, Binder of Wills", "-3")
def _dihada_minus3(state, host, x):
    top = state.library[:4]
    del state.library[:4]
    leg = [c for c in top if legendary_card(c)]
    rest = [c for c in top if not legendary_card(c)]
    state.hand.extend(leg)
    state.graveyard.extend(rest)
    state.m["dihada_legend_cards"] += len(leg)
    state.m["self_mill_cards"] += len(rest)
    if rest:
        create_token(state, "Treasure Token", len(rest), src="dihada")
        state.m["dihada_treasures"] += len(rest)


@sc("Dihada, Binder of Wills", "-3")
def _dihada_minus3_s(state, host):
    return 74 if loyalty(host) >= 3 and len(state.library) > 12 else None


@eff("Dihada, Binder of Wills", "-11")
def _dihada_ult(state, host, x):
    """'Gain control of all nonland permanents until end of turn. Untap them. They gain haste': o poder dos permanentes de oponente que atacam e' dano no oponente mais fraco (modo de resiliencia);
    no modo padrao nao ha' tabuleiro de oponente (estrutural, proxy de interacao)."""
    if state.resilience:
        dmg = sum(c["p"] for o in alive_opps(state) for c in o.board)
        damage_opp(state, dmg, "dihada_ult", combat=True)
    else:
        state.m["proxy_dihada_ult"] += 1
        state.m["interaction_plays"] += 1


@sc("Dihada, Binder of Wills", "-11")
def _dihada_ult_s(state, host):
    return 90


# ---------- Garruk, Curse Breaker ----------
@eff("Garruk, Curse Breaker", "+2")
def _garruk_cb_plus2(state, host, x):
    untap_best_lands(state, 2)


@sc("Garruk, Curse Breaker", "+2")
def _garruk_cb_plus2_s(state, host):
    return 55 if (tapped_lands(state) and mana_shortage(state)) else 34


@eff("Garruk, Curse Breaker", "-3")
def _garruk_cb_minus3(state, host, x):
    create_token(state, "Beast Token", 1, src="garruk_cb")


@sc("Garruk, Curse Breaker", "-3")
def _garruk_cb_minus3_s(state, host):
    return 66 if loyalty(host) >= 4 else None


@eff("Garruk, Curse Breaker", "-4")
def _garruk_cb_minus4(state, host, x):
    state.m["garruk_cb_buff_armed"] += 1
    state.cb_buff = True


@sc("Garruk, Curse Breaker", "-4")
def _garruk_cb_minus4_s(state, host):
    return 66 if loyalty(host) >= 5 and len(untapped_attackers(state)) >= 2 and state.phase == "main1" else None


# ---------- Minsc & Boo ----------
def trample_or_haste(state: GameState, p: Permanent) -> bool:
    return is_creature(p) and ("trample" in p.card.tags or "haste" in p.card.tags or p.ctr.get("trample_eot") or p.haste_until_eot)


def boo_perm(state: GameState) -> Optional[Permanent]:
    b = [p for p in state.battlefield if p.card.name == "Boo Token" and not p.phased]
    return b[0] if b else None


@eff("Minsc & Boo, Timeless Heroes", "+1")
def _minsc_plus1(state, host, x):
    b = boo_perm(state)
    cands = [b] if b else sorted([p for p in creatures(state) if trample_or_haste(state, p)], key=lambda p: (-power(state, p), p.uid))
    if cands:
        put_counters(state, cands[0], "p1p1", 3, "minsc")


@sc("Minsc & Boo, Timeless Heroes", "+1")
def _minsc_plus1_s(state, host):
    b = boo_perm(state)
    if b is not None and power(state, b) < 7:
        return 60
    if any(trample_or_haste(state, p) for p in creatures(state)):
        return 52
    return 20


def minsc_sac_choice(state: GameState) -> Optional[Permanent]:
    b = boo_perm(state)
    cands = [p for p in creatures(state) if p.card.name not in ("Tam, the Possibility", "Kiora of Salt and Sand", "Dreamtide Whale")]
    if not cands:
        return None
    best = max(cands, key=lambda p: (power(state, p), 1 if p is b else 0, -p.uid))
    return best


@eff("Minsc & Boo, Timeless Heroes", "-2")
def _minsc_minus2(state, host, x):
    p = minsc_sac_choice(state)
    if p is None:
        return
    X = power(state, p)
    hamster = "Hamster" in p.card.subtypes
    remove_permanent(state, p, "sacrificed")
    state.m["minsc_sacs"] += 1
    state.m["minsc_damage"] += X
    if state.resilience and best_killable_threat(state, X) is not None and opp_threat_power(state) >= 8:
        c = best_killable_threat(state, X)
        opp_remove_creature(state, c[0], c[1], "damage")
    else:
        damage_opp(state, X, "minsc_boo")
    if hamster and X > 0:
        draw_cards(state, X, "minsc_boo", optional=True)
        state.m["minsc_draws"] += X


@sc("Minsc & Boo, Timeless Heroes", "-2")
def _minsc_minus2_s(state, host):
    p = minsc_sac_choice(state)
    if p is None:
        return None
    X = power(state, p)
    if "Hamster" in p.card.subtypes and X >= 5:
        return 80
    if X >= 6:
        return 66
    return None


# ---------- Narset Transcendent ----------
@eff("Narset Transcendent", "+1")
def _narset_plus1(state, host, x):
    if not state.library:
        return
    c = state.library[0]
    t = CARD_DB[c].types
    if "creature" not in t and "land" not in t:
        state.library.pop(0)
        state.hand.append(c)
        state.m["narset_hits"] += 1


@sc("Narset Transcendent", "+1")
def _narset_plus1_s(state, host):
    return 46


@eff("Narset Transcendent", "-2")
def _narset_minus2(state, host, x):
    state.rebound_armed = True


@sc("Narset Transcendent", "-2")
def _narset_minus2_s(state, host):
    if loyalty(host) < 4:
        return None
    for h in ("Entrust the Spark", "Ripples of Potential"):
        if h in state.hand and can_cast_name(state, h) and cast_gate(state, h):
            return 50
    return None


@eff("Narset Transcendent", "-9")
def _narset_ult(state, host, x):
    state.emblems.append("narset")


@sc("Narset Transcendent", "-9")
def _narset_ult_s(state, host):
    return 88


# ---------- Professor Dellian Fel ----------
@eff("Professor Dellian Fel", "+2")
def _dellian_plus2(state, host, x):
    gain_life(state, 3, "dellian")


@sc("Professor Dellian Fel", "+2")
def _dellian_plus2_s(state, host):
    return 62 if "dellian" in state.emblems else (46 if loyalty(host) < 6 else 34)


@eff("Professor Dellian Fel", "0")
def _dellian_zero(state, host, x):
    draw_cards(state, 1, "dellian")
    lose_life(state, 1, "dellian_draw")


@sc("Professor Dellian Fel", "0")
def _dellian_zero_s(state, host):
    return 52 if state.life >= 12 and len(state.library) > 20 else None


@eff("Professor Dellian Fel", "-3")
def _dellian_minus3(state, host, x):
    kill_threat(state, "dellian_destroy")


@sc("Professor Dellian Fel", "-3")
def _dellian_minus3_s(state, host):
    if loyalty(host) < 4:
        return None
    if state.resilience:
        return 58 if biggest_threat(state)[1] is not None and biggest_threat(state)[1]["p"] >= THREAT_POWER else None
    return 28 if state.target_ok else None


@eff("Professor Dellian Fel", "-6")
def _dellian_ult(state, host, x):
    state.emblems.append("dellian")


@sc("Professor Dellian Fel", "-6")
def _dellian_ult_s(state, host):
    return 86


# ---------- Tamiyo, Field Researcher ----------
@eff("Tamiyo, Field Researcher", "+1")
def _tamiyo_plus1(state, host, x):
    ours = sorted(untapped_attackers(state) or creatures(state), key=lambda p: (-power(state, p), p.uid))[:2]
    state.tamiyo_marked = [p.uid for p in ours]
    state.m["tamiyo_marks"] += len(ours)


@sc("Tamiyo, Field Researcher", "+1")
def _tamiyo_plus1_s(state, host):
    return 52 if len(untapped_attackers(state)) >= 1 and alive_opps(state) else 30


@eff("Tamiyo, Field Researcher", "-2")
def _tamiyo_minus2(state, host, x):
    freeze_threats(state, 2, "tamiyo")


@sc("Tamiyo, Field Researcher", "-2")
def _tamiyo_minus2_s(state, host):
    if loyalty(host) < 3:
        return None
    if state.resilience:
        return 44 if opp_threat_power(state) >= 5 else None
    return 24 if state.target_ok else None


@eff("Tamiyo, Field Researcher", "-7")
def _tamiyo_ult(state, host, x):
    draw_cards(state, 3, "tamiyo_ult")
    state.emblems.append("tamiyo")


@sc("Tamiyo, Field Researcher", "-7")
def _tamiyo_ult_s(state, host):
    return 95


# ---------- Teferi, Hero of Dominaria ----------
@eff("Teferi, Hero of Dominaria", "+1")
def _teferi_h_plus1(state, host, x):
    draw_cards(state, 1, "teferi_hero")
    state.end_step_untap += 2          # 'At the beginning of the next end step, untap up to two lands.'


@sc("Teferi, Hero of Dominaria", "+1")
def _teferi_h_plus1_s(state, host):
    return 72


@eff("Teferi, Hero of Dominaria", "-3")
def _teferi_h_minus3(state, host, x):
    kill_threat(state, "teferi_hero_tuck", how="tuck")


@sc("Teferi, Hero of Dominaria", "-3")
def _teferi_h_minus3_s(state, host):
    if loyalty(host) < 5:
        return None
    if state.resilience:
        return 46 if opp_threat_power(state) >= 5 else None
    return 24 if state.target_ok else None


@eff("Teferi, Hero of Dominaria", "-8")
def _teferi_h_ult(state, host, x):
    state.emblems.append("teferi_hero")


@sc("Teferi, Hero of Dominaria", "-8")
def _teferi_h_ult_s(state, host):
    return 92


def teferi_emblem_exile(state: GameState):
    """Emblema do Teferi, Hero: 'Whenever you draw a card, exile target permanent an opponent controls.' (alvo de oponente: real no modo de resiliencia, proxy no padrao)"""
    kill_threat(state, "teferi_hero_emblem", how="exile")


# ---------- Teferi, Temporal Archmage ----------
@eff("Teferi, Temporal Archmage", "+1")
def _teferi_ta_plus1(state, host, x):
    top = state.library[:2]
    if not top:
        return
    del state.library[:len(top)]
    pick = max(top, key=lambda c: (CARD_PRIORITY.get(c, 20) if "land" not in CARD_DB[c].types else (60 if n_lands(state) < 5 else 8), c))
    top.remove(pick)
    state.hand.append(pick)
    state.library.extend(top)
    state.m["teferi_ta_looks"] += 1


@sc("Teferi, Temporal Archmage", "+1")
def _teferi_ta_plus1_s(state, host):
    return 58


def untap_best_permanents(state: GameState, n: int) -> int:
    """Teferi TA -1 / Tezzeret +1: desvira permanentes que dao mana (Orrery > Sol Ring > resto) ou o The Chain Veil se vale reativar."""
    def val(p):
        nm = p.card.name
        if nm == "Chromatic Orrery":
            return 50
        if nm == "The Chain Veil":
            return 45 if veil_worth_it(state) else 1
        if nm == "Sol Ring":
            return 30
        if "land" in p.card.types:
            return 10 + len(set(LANDS[nm]["prod"]) - {"C"})
        if nm in ("Arcane Signet", "Fellwar Stone", "Birds of Paradise", "Noble Hierarch", "Ignoble Hierarch", "Bloom Tender", "Faeburrow Elder"):
            return 12
        if nm == "Staff of Compleation":
            return 5
        return 0
    cands = [p for p in vis(state) if p.tapped and val(p) > 0]
    cands.sort(key=lambda p: (-val(p), p.uid))
    k = 0
    for p in cands[:n]:
        p.tapped = False
        k += 1
    return k


@eff("Teferi, Temporal Archmage", "-1")
def _teferi_ta_minus1(state, host, x):
    untap_best_permanents(state, 4)
    state.m["teferi_ta_untaps"] += 1


@sc("Teferi, Temporal Archmage", "-1")
def _teferi_ta_minus1_s(state, host):
    if loyalty(host) < 2:
        return None
    gain = sum(1 for p in vis(state) if p.tapped and p.card.name in ("Chromatic Orrery", "Sol Ring", "The Chain Veil")) + (len(tapped_lands(state)) >= 2)
    if gain >= 1 and (mana_shortage(state) or (state.phase == "main1" and any(p.tapped and p.card.name == "Chromatic Orrery" for p in vis(state)))):
        return 66
    return None


@eff("Teferi, Temporal Archmage", "-10")
def _teferi_ta_ult(state, host, x):
    state.emblems.append("teferi_ta")


@sc("Teferi, Temporal Archmage", "-10")
def _teferi_ta_ult_s(state, host):
    return 96


# ---------- Garruk, Veiled Butcher ----------
@eff("Garruk, Veiled Butcher", "+2")
def _garruk_vb_plus2(state, host, x):
    """'Up to one target creature gets -4/-1 until your next turn.' No modo de resiliencia: a maior ameaca perde 4 de poder e 1 de resistencia ate' o meu proximo upkeep (restaurado la'); com resistencia 1
    ela morre (exilada: estatico da propria Garruk). No padrao: proxy (alvo no tabuleiro do oponente)."""
    if state.resilience:
        o, c = biggest_threat(state)
        if c is None:
            return
        dp = min(4, c["p"])
        c["p"] -= dp
        c["t"] -= 1
        c["dp_applied"] = c.get("dp_applied", 0) + dp
        c["dt_applied"] = c.get("dt_applied", 0) + 1
        state.m["garruk_vb_debuffs"] += 1
        state.m["interaction_plays"] += 1
        if c["t"] <= 0:
            c["t"] += c.pop("dt_applied", 0)
            c["p"] += c.pop("dp_applied", 0)
            opp_remove_creature(state, o, c, "damage")
            state.m["garruk_vb_kills"] += 1
    elif state.target_ok:
        state.m["proxy_garruk_vb"] += 1
        state.m["interaction_plays"] += 1


@sc("Garruk, Veiled Butcher", "+2")
def _garruk_vb_plus2_s(state, host):
    return 40


def sacrifice_fodder(state: GameState) -> Optional[Permanent]:
    """Criatura que posso sacrificar sem dor: ficha de menor valor (nunca o Boo com contadores, a Tam, o Kiora, a Whale)."""
    cands = [p for p in creatures(state) if p.is_token and p.card.name not in ("Boo Token", "Leviathan Token") and power(state, p) < 4 and not p.anim]
    if not cands:
        return None
    return min(cands, key=lambda p: (power(state, p) + p.ctr.get("p1p1", 0), p.uid))


@eff("Garruk, Veiled Butcher", "-2")
def _garruk_vb_minus2(state, host, x):
    """'Each player sacrifices a creature of their choice. If you sacrificed a creature this way, create a 4/4 green Beast creature token with trample.' EU tambem sacrifico (a de menor valor: ficha primeiro)."""
    mine = creatures(state)
    ours = False
    if mine:
        f = sacrifice_fodder(state) or min(mine, key=lambda p: (0 if p.is_token else 1, power(state, p) + toughness(state, p), p.uid))
        remove_permanent(state, f, "sacrificed")
        ours = True
    if state.resilience:
        for o in alive_opps(state):
            if o.board:
                weakest = min(o.board, key=lambda c: (c["p"], c["t"]))
                opp_remove_creature(state, o, weakest, "exile")      # 'If a creature an opponent controls would die, exile it instead'
        state.m["garruk_edicts"] += 1
    elif state.target_ok:
        state.m["proxy_edict"] += 1
        state.m["interaction_plays"] += 1
    if ours:
        create_token(state, "Beast Token", 1, src="garruk_vb")


@sc("Garruk, Veiled Butcher", "-2")
def _garruk_vb_minus2_s(state, host):
    if loyalty(host) < 3:
        return None
    if sacrifice_fodder(state) is not None:
        return 58
    if state.resilience and any(o.board for o in alive_opps(state)) and not creatures(state):
        return 52                                 # eu nao controlo criatura: so' eles sacrificam
    return None


@eff("Garruk, Veiled Butcher", "-3")
def _garruk_vb_minus3(state, host, x):
    n = 0
    for o in alive_opps(state):
        if o.hand_size > 0:
            o.hand_size = max(0, o.hand_size - 2)
            n += 1
            if state.proxy_rng.random() < 0.7:
                draw_cards(state, 1, "garruk_vb_discard")
                state.m["garruk_vb_draws"] += 1
    state.m["opp_discards"] += n
    state.m["interaction_plays"] += 1


@sc("Garruk, Veiled Butcher", "-3")
def _garruk_vb_minus3_s(state, host):
    return 42 if loyalty(host) >= 4 and any(o.hand_size >= 2 for o in alive_opps(state)) else None


# ---------- Nissa, Ascended Animist ----------
@eff("Nissa, Ascended Animist", "+1")
def _nissa_plus1(state, host, x):
    X = loyalty(host)
    toks = create_token(state, "Horror Token", 1, src="nissa")
    for t in toks:
        t.base_pt = (X, X)
        if X >= 4 and False:
            pass
    # o token entrou com 0/0: o poder so' passa a valer agora (garruk, curse breaker: poder >= 4 compra) -> reavalia
    for t in toks:
        if X >= 4:
            for _ in range(count_named(state, "Garruk, Curse Breaker")):
                draw_cards(state, 1, "garruk_curse_breaker")
                state.m["garruk_cb_draws"] += 1
    sba(state)


@sc("Nissa, Ascended Animist", "+1")
def _nissa_plus1_s(state, host):
    return 84


@eff("Nissa, Ascended Animist", "-1")
def _nissa_minus1(state, host, x):
    state.m["proxy_artifact_enchantment_destroy"] += 1
    state.m["interaction_plays"] += 1


@sc("Nissa, Ascended Animist", "-1")
def _nissa_minus1_s(state, host):
    return 18 if loyalty(host) >= 3 and state.target_ok else None


def forest_count(state: GameState) -> int:
    if yavimaya_forest(state):
        return n_lands(state)
    return sum(1 for p in lands_of(state) if "Forest" in p.card.land_types)


@eff("Nissa, Ascended Animist", "-7")
def _nissa_ult(state, host, x):
    n = forest_count(state)
    for p in creatures(state):
        p.temp_p += n
        p.temp_t += n
        p.ctr["trample_eot"] = 1
    state.m["nissa_overrun"] += 1


@sc("Nissa, Ascended Animist", "-7")
def _nissa_ult_s(state, host):
    return 82 if len(untapped_attackers(state)) >= 2 and state.phase == "main1" else None


# ---------- Oko, Thief of Crowns ----------
@eff("Oko, Thief of Crowns", "+2")
def _oko_plus2(state, host, x):
    create_token(state, "Food Token", 1, src="oko")


@sc("Oko, Thief of Crowns", "+2")
def _oko_plus2_s(state, host):
    return 54 if not oko_target(state) else 40


def oko_target(state: GameState) -> Optional[Permanent]:
    """+1: 'Target artifact or creature loses all abilities and becomes a green Elk creature with base power and toughness 3/3.' Alvo: Food/Treasure (vira 3/3 do nada), senao ficha criatura com poder < 3."""
    for nm in ("Food Token", "Treasure Token"):
        c = [p for p in state.battlefield if p.card.name == nm and not p.phased and p.base_pt is None]
        if c:
            return min(c, key=lambda p: p.uid)
    c = [p for p in creatures(state) if p.is_token and p.base_pt is None and power(state, p) < 3 and p.card.name not in ("Boo Token",)]
    if c:
        return min(c, key=lambda p: (power(state, p), p.uid))
    return None


@eff("Oko, Thief of Crowns", "+1")
def _oko_plus1(state, host, x):
    t = oko_target(state)
    if t is None:
        return
    t.lost_abilities = True
    t.base_pt = (3, 3)
    t.anim = None
    t.ctr["elk"] = 1
    state.m["oko_elks"] += 1


@sc("Oko, Thief of Crowns", "+1")
def _oko_plus1_s(state, host):
    return 76 if oko_target(state) is not None else None


@eff("Oko, Thief of Crowns", "-5")
def _oko_minus5(state, host, x):
    if state.resilience:
        cands = [(o, c) for o in alive_opps(state) for c in o.board if c["p"] <= 3]
        if cands:
            o, c = max(cands, key=lambda oc: (oc[1]["p"], oc[1]["t"]))
            f = sacrifice_fodder(state) or min(creatures(state), key=lambda p: (power(state, p), p.uid), default=None)
            if f is not None:
                remove_permanent(state, f, "exile")
            opp_remove_creature(state, o, c, "exchange")
            create_token(state, "Elk Token", 1, src="oko_exchange")
    else:
        state.m["proxy_exchange"] += 1
        state.m["interaction_plays"] += 1


@sc("Oko, Thief of Crowns", "-5")
def _oko_minus5_s(state, host):
    if loyalty(host) < 5:
        return None
    if state.resilience:
        return 50 if any(c["p"] <= 3 for o in alive_opps(state) for c in o.board) else None
    return None


# ---------- The Eternal Wanderer ----------
@eff("The Eternal Wanderer", "+1")
def _wanderer_plus1(state, host, x):
    cands = [p for p in vis(state) if (is_creature(p) or is_artifact(p)) and not p.is_token and p.card.name not in ("Tam, the Possibility",)]
    best = None
    bv = 0.0
    for p in cands:
        v = blink_value(state, p)
        if v > bv:
            best, bv = p, v
    if best is not None and bv >= 15:
        state.m["wanderer_blinks"] += 1
        state.delayed_return_wanderer = True
        exile_for_delayed_return(state, best)
    elif state.resilience:
        c = biggest_threat(state)
        if c[1] is not None:
            opp_remove_creature(state, c[0], c[1], "exile_temp")
            state.m["wanderer_exiles_opp"] += 1


@sc("The Eternal Wanderer", "+1")
def _wanderer_plus1_s(state, host):
    cands = [p for p in vis(state) if (is_creature(p) or is_artifact(p)) and not p.is_token and p.card.name not in ("Tam, the Possibility",)]
    if any(blink_value(state, p) >= 15 for p in cands):
        return 55
    return 32


@eff("The Eternal Wanderer", "0")
def _wanderer_zero(state, host, x):
    create_token(state, "Samurai Token", 1, src="wanderer")


@sc("The Eternal Wanderer", "0")
def _wanderer_zero_s(state, host):
    return 60


@eff("The Eternal Wanderer", "-4")
def _wanderer_minus4(state, host, x):
    ours = sorted(creatures(state), key=lambda p: (-(power(state, p) + toughness(state, p)), p.uid))
    keep = ours[0] if ours else None
    for p in list(creatures(state)):
        if p is not keep:
            remove_permanent(state, p, "sacrificed")
    if state.resilience:
        for o in alive_opps(state):
            if o.board:
                keepc = min(o.board, key=lambda c: (c["p"], c["t"]))      # 'For each player, choose a creature that player controls': EU escolho, a mais fraca fica
                for c in o.board:
                    if c is not keepc:
                        state.m["opp_creatures_removed"] += 1
                        state.m["opp_creatures_removed_sacrifice"] += 1
                o.board = [keepc]
    state.m["wanderer_wipes"] += 1


@sc("The Eternal Wanderer", "-4")
def _wanderer_minus4_s(state, host):
    if state.resilience and sum(len(o.board) for o in alive_opps(state)) >= 5 and opp_threat_power(state) >= 12 and loyalty(host) >= 5:
        return 48
    return None


# ---------- Vraska, Betrayal's Sting ----------
@eff("Vraska, Betrayal's Sting", "0")
def _vraska_zero(state, host, x):
    draw_cards(state, 1, "vraska")
    lose_life(state, 1, "vraska")
    proliferate(state, "vraska")


@sc("Vraska, Betrayal's Sting", "0")
def _vraska_zero_s(state, host):
    return 86 if state.life >= 6 else None


@eff("Vraska, Betrayal's Sting", "-2")
def _vraska_minus2(state, host, x):
    kill_threat(state, "vraska_treasure", how="treasure")


@sc("Vraska, Betrayal's Sting", "-2")
def _vraska_minus2_s(state, host):
    if loyalty(host) < 3:
        return None
    if state.resilience:
        return 40 if opp_threat_power(state) >= 6 else None
    return 26 if state.target_ok else None


@eff("Vraska, Betrayal's Sting", "-9")
def _vraska_ult(state, host, x):
    """'If target player has fewer than nine poison counters, they get a number of poison counters equal to the difference.' (9 total; 10 e' a derrota: o proliferate seguinte fecha)."""
    o = lowest_opp(state)
    if o is None:
        return
    diff = max(0, 9 - o.poison)
    give_poison(state, o.idx, diff, "vraska_ult")
    state.m["vraska_ult_poison"] += diff


@sc("Vraska, Betrayal's Sting", "-9")
def _vraska_ult_s(state, host):
    return 92


# ---------- Ajani Unrelenting ----------
@eff("Ajani Unrelenting", "+1")
def _ajani_plus1(state, host, x):
    for p in creatures(state):
        p.temp_p += 1
        p.haste_until_eot = True


@sc("Ajani Unrelenting", "+1")
def _ajani_plus1_s(state, host):
    return 62 if len(creatures(state)) >= 2 else 36


@eff("Ajani Unrelenting", "-2")
def _ajani_minus2(state, host, x):
    n = len(creatures(state))
    discard_all = list(state.hand)
    state.hand.clear()
    state.graveyard.extend(discard_all)
    state.m["cards_discarded"] += len(discard_all)
    draw_cards(state, n, "ajani_minus2", optional=True)


@sc("Ajani Unrelenting", "-2")
def _ajani_minus2_s(state, host):
    n = len(creatures(state))
    return 48 if n >= 5 and len(state.hand) <= 2 and loyalty(host) >= 3 else None


@eff("Ajani Unrelenting", "-3")
def _ajani_minus3(state, host, x):
    for p in list(creatures(state)):
        if not p.is_token and toughness(state, p) <= 4:
            remove_permanent(state, p, "dies")
    if state.resilience:
        for o in alive_opps(state):
            for c in list(o.board):
                if c["t"] <= 4:
                    opp_remove_creature(state, o, c, "damage")
    state.m["ajani_wipes"] += 1


@sc("Ajani Unrelenting", "-3")
def _ajani_minus3_s(state, host):
    if not state.resilience or loyalty(host) < 4:
        return None
    lost = sum(1 for p in creatures(state) if not p.is_token and toughness(state, p) <= 4)      # inclui a Tam (2/4: morre, volta pra zona de comando e o proximo cast paga +2)
    gain = sum(c["p"] for o in alive_opps(state) for c in o.board if c["t"] <= 4)
    if lost == 0 and gain >= 8:
        return 50
    return 44 if (lost <= 1 and gain >= 14) else None


# ---------- Elspeth, Sun's Champion ----------
@eff("Elspeth, Sun's Champion", "+1")
def _elspeth_plus1(state, host, x):
    create_token(state, "Soldier Token", 3, src="elspeth")


@sc("Elspeth, Sun's Champion", "+1")
def _elspeth_plus1_s(state, host):
    return 82


@eff("Elspeth, Sun's Champion", "-3")
def _elspeth_minus3(state, host, x):
    for p in list(creatures(state)):
        if power(state, p) >= 4:
            remove_permanent(state, p, "dies")
    if state.resilience:
        for o in alive_opps(state):
            for c in list(o.board):
                if c["p"] >= 4:
                    opp_remove_creature(state, o, c, "destroy")
    state.m["elspeth_wipes"] += 1


@sc("Elspeth, Sun's Champion", "-3")
def _elspeth_minus3_s(state, host):
    if not state.resilience:
        return None
    mine = sum(1 for p in creatures(state) if power(state, p) >= 4 and p.card.name != "Tam, the Possibility")
    theirs = sum(c["p"] for o in alive_opps(state) for c in o.board if c["p"] >= 4)
    return 60 if theirs >= 8 and mine <= 1 else None


@eff("Elspeth, Sun's Champion", "-7")
def _elspeth_ult(state, host, x):
    state.emblems.append("elspeth")


@sc("Elspeth, Sun's Champion", "-7")
def _elspeth_ult_s(state, host):
    return 92


# ---------- Kasmina, Enigma Sage (e as habilidades dela concedidas aos outros planeswalkers) ----------
@eff(KASMINA, "+2")
def _kasmina_plus2(state, host, x):
    scry(state, 1)


@sc(KASMINA, "+2")
def _kasmina_plus2_s(state, host):
    return 48 if host.card.name == KASMINA else 44


@eff(KASMINA, "-X")
def _kasmina_minusx(state, host, x):
    """'-X: Create a 0/0 green and blue Fractal creature token. Put X +1/+1 counters on it.' (os contadores entram pela substituicao e disparam All Will Be One)"""
    toks = create_token(state, "Fractal Token", 1, src="kasmina")
    for t in toks:
        put_counters(state, t, "p1p1", x, "kasmina")
    sba(state)


@sc(KASMINA, "-X")
def _kasmina_minusx_s(state, host, x):
    L = loyalty(host)
    start = host.card.loyalty if host.card.loyalty else 5
    ult = ult_cost(host.card.name)
    if host.card.name == KASMINA:
        return None                                       # a Kasmina precisa da lealdade pra viver; so' o excesso dos outros vira Fractal
    excess = L - max(start, (ult if ult else start))
    if excess >= 2 and x == excess:
        return 38 + min(x, 6)
    return None


@eff(KASMINA, "-8")
def _kasmina_ult(state, host, x):
    """'Search your library for an instant or sorcery card that shares a color with this planeswalker, exile that card, then shuffle. You may cast that card without paying its mana cost.'
    ('this planeswalker' = o que ativou: ruling 2021-04-16; incolor nao busca.)"""
    cols = set(host.card.colors)
    cands = [c for c in sorted(set(state.library)) if ("instant" in CARD_DB[c].types or "sorcery" in CARD_DB[c].types) and (CARD_DB[c].colors & cols)]
    state.rng.shuffle(state.library)
    if not cands:
        return
    pick = max(cands, key=lambda c: (CARD_PRIORITY.get(c, 20), c))
    state.library.remove(pick)
    state.m["kasmina_tutor"] += 1
    state.exile.append(pick)
    state.cast_zone = "exile"
    on_cast(state, pick)
    resolve_spell(state, pick)


@sc(KASMINA, "-8")
def _kasmina_ult_s(state, host):
    cols = set(host.card.colors)
    ok = any(("instant" in CARD_DB[c].types or "sorcery" in CARD_DB[c].types) and (CARD_DB[c].colors & cols) for c in set(state.library))
    return 78 if ok else None


# ---------- Saheeli, Sublime Artificer ----------
@eff("Saheeli, Sublime Artificer", "-2")
def _saheeli_minus2(state, host, x):
    arts = [p for p in artifacts(state) if p.card.name in ("Servo Token", "Food Token", "Treasure Token") and not sick(state, p) and not p.tapped and p.base_pt is None]
    big = sorted([p for p in creatures(state) if p.card.name not in ("Tam, the Possibility",)], key=lambda p: (-power(state, p), p.uid))
    if not arts or not big:
        return
    t = arts[0]
    src = big[0]
    t.base_pt = (power(state, src), toughness(state, src))
    t.anim = "eot"
    state.m["saheeli_copies"] += 1


@sc("Saheeli, Sublime Artificer", "-2")
def _saheeli_minus2_s(state, host):
    arts = [p for p in artifacts(state) if p.card.name in ("Servo Token", "Food Token", "Treasure Token") and not sick(state, p) and not p.tapped and p.base_pt is None]
    big = [p for p in creatures(state) if power(state, p) >= 5 and p.card.name != "Tam, the Possibility"]
    if arts and big and loyalty(host) >= 4 and state.phase == "main1":
        return 30
    return None


# ---------- Vronos, Masked Inquisitor ----------
@eff("Vronos, Masked Inquisitor", "+1")
def _vronos_plus1(state, host, x):
    if state.resilience:
        threatened = sorted([p for p in pws(state) if p is not host], key=lambda p: (-loyalty(p), p.uid))[:2]
        state.phase_out_at_end.extend(p.uid for p in threatened)
        state.m["vronos_phase_marks"] += len(threatened)


@sc("Vronos, Masked Inquisitor", "+1")
def _vronos_plus1_s(state, host):
    return 48 if state.resilience else 36


@eff("Vronos, Masked Inquisitor", "-2")
def _vronos_minus2(state, host, x):
    if state.resilience:
        for o in alive_opps(state):
            if o.board:
                c = max(o.board, key=lambda c: (c["p"], c["t"]))
                opp_remove_creature(state, o, c, "bounce")
        state.m["vronos_bounces"] += 1
    elif state.target_ok:
        state.m["proxy_bounce"] += 1
        state.m["interaction_plays"] += 1


@sc("Vronos, Masked Inquisitor", "-2")
def _vronos_minus2_s(state, host):
    if loyalty(host) < 3:
        return None
    if state.resilience:
        return 44 if opp_threat_power(state) >= 6 else None
    return 24 if state.target_ok else None


VRONOS_ARTIFACT_PREF = ("Arcane Signet", "Fellwar Stone", "Sol Ring", "Food Token", "Treasure Token", "Staff of Compleation", "Ichormoon Gauntlet", "The Chain Veil", "Chromatic Orrery")


def vronos_artifact(state: GameState) -> Optional[Permanent]:
    cands = [p for p in artifacts(state) if not p.anim and p.base_pt is None and not is_creature(p)]
    if not cands:
        return None
    def key(p):
        return (VRONOS_ARTIFACT_PREF.index(p.card.name) if p.card.name in VRONOS_ARTIFACT_PREF else 99, p.uid)
    # prefere um artefato que esta em campo desde o inicio do turno (pode atacar) e nao e' motor
    ready = [p for p in cands if not sick(state, p)]
    pool = ready or cands
    return min(pool, key=key)


@eff("Vronos, Masked Inquisitor", "-7")
def _vronos_ult(state, host, x):
    a = vronos_artifact(state)
    if a is not None:
        a.base_pt = (9, 9)
        a.anim = "forever"
        a.ctr["indestructible"] = 1
        a.ctr["vigilance"] = 1
        a.unblockable = True
        state.m["vronos_constructs"] += 1


@sc("Vronos, Masked Inquisitor", "-7")
def _vronos_ult_s(state, host):
    return 84 if vronos_artifact(state) is not None else None


# ---------- Aminatou, the Fateshifter ----------
@eff("Aminatou, the Fateshifter", "+1")
def _aminatou_plus1(state, host, x):
    draw_cards(state, 1, "aminatou")
    if state.hand and not state.game_over:
        worst = min(state.hand, key=lambda c: (discard_value(state, c), c))
        state.hand.remove(worst)
        state.library.insert(0, worst)


@sc("Aminatou, the Fateshifter", "+1")
def _aminatou_plus1_s(state, host):
    return 56


@eff("Aminatou, the Fateshifter", "-1")
def _aminatou_minus1(state, host, x):
    t = best_blink_target(state, exclude=host)
    if t is not None:
        blink(state, t, "aminatou")


@sc("Aminatou, the Fateshifter", "-1")
def _aminatou_minus1_s(state, host):
    if loyalty(host) < 2:
        return None
    t = best_blink_target(state, exclude=host)
    if t is None:
        return None
    v = blink_value(state, t)
    return 40 + v / 3 if v >= 25 else None


@eff("Aminatou, the Fateshifter", "-6")
def _aminatou_ult(state, host, x):
    state.m["aminatou_ult_swaps"] += 1


@sc("Aminatou, the Fateshifter", "-6")
def _aminatou_ult_s(state, host):
    return None            # troca TODOS os meus permanentes nao-terreno pelos do vizinho: sem tabuleiro de oponente a troca so' me custa o campo (checklist)


# ---------- Tezzeret the Seeker ----------
@eff("Tezzeret the Seeker", "+1")
def _tezzeret_plus1(state, host, x):
    n = 0
    cands = [p for p in artifacts(state) if p.tapped]
    cands.sort(key=lambda p: ({"Chromatic Orrery": 0, "The Chain Veil": 1 if veil_worth_it(state) else 9, "Sol Ring": 2}.get(p.card.name, 5), p.uid))
    for p in cands[:2]:
        p.tapped = False
        n += 1
    state.m["tezzeret_untaps"] += n


@sc("Tezzeret the Seeker", "+1")
def _tezzeret_plus1_s(state, host):
    tapped = [p for p in artifacts(state) if p.tapped and p.card.name in ("Chromatic Orrery", "Sol Ring", "Arcane Signet", "The Chain Veil")]
    return 60 if (tapped and mana_shortage(state)) else (40 if tapped else 32)


def tezzeret_pick(state: GameState, x: int) -> Optional[str]:
    cands = [c for c in sorted(set(state.library)) if "artifact" in CARD_DB[c].types and CARD_DB[c].mv <= x]
    if not cands:
        return None
    return max(cands, key=lambda c: (TEZZ_PRIORITY.get(c, 0), CARD_DB[c].mv, c))


TEZZ_PRIORITY = {"The Chain Veil": 60, "Chromatic Orrery": 70, "Sol Ring": 55, "Ichormoon Gauntlet": 50, "Arcane Signet": 40, "Staff of Compleation": 30, "Fellwar Stone": 20, "Patrolling Peacemaker": 25}


@eff("Tezzeret the Seeker", "-X")
def _tezzeret_minusx(state, host, x):
    pick = tezzeret_pick(state, x)
    if pick is None:
        state.rng.shuffle(state.library)
        return
    state.library.remove(pick)
    state.rng.shuffle(state.library)
    p = mk_perm(state, pick)
    state.battlefield.append(p)
    state.m["tezzeret_tutors"] += 1
    enter_permanent(state, p, from_cast=False)


@sc("Tezzeret the Seeker", "-X")
def _tezzeret_minusx_s(state, host, x):
    L = loyalty(host)
    if L < 2:
        return None
    pick = tezzeret_pick(state, x)
    if pick is None or x != min(L - 1, CARD_DB[pick].mv):
        return None
    if x < CARD_DB[pick].mv:
        return None
    return 62 + TEZZ_PRIORITY.get(pick, 0) / 10


@eff("Tezzeret the Seeker", "-5")
def _tezzeret_ult(state, host, x):
    for p in artifacts(state):
        if not is_creature(p):
            p.base_pt = (5, 5)
            p.anim = "eot"
    state.m["tezzeret_ults_artifacts"] += len(artifacts(state))


def tezzeret_attackers(state: GameState) -> int:
    return sum(1 for p in artifacts(state) if not sick(state, p) and not p.tapped and not is_creature(p) and p.card.name != "Chromatic Orrery")


@sc("Tezzeret the Seeker", "-5")
def _tezzeret_ult_s(state, host):
    n = tezzeret_attackers(state)
    return 90 if n >= 3 and state.phase == "main1" else None


# ---------- Jace token ----------
@eff("Jace Token", "-1")
def _jace_minus1(state, host, x):
    surveil(state, 1)


@sc("Jace Token", "-1")
def _jace_minus1_s(state, host):
    L = loyalty(host)
    return 22 if (L >= 2 or has_perm(state, "Sanctum Lurker")) else None


@eff("Jace Token", "-3")
def _jace_minus3(state, host, x):
    draw_cards(state, 1, "jace_token")


@sc("Jace Token", "-3")
def _jace_minus3_s(state, host):
    return 54 if loyalty(host) >= 3 else None


# ---------- habilidades CONCEDIDAS ----------
@eff("Way of the Pyromancer", "+1")
def _pyro_plus1(state, host, x):
    state.pool["R"] = state.pool.get("R", 0) + 1


@sc("Way of the Pyromancer", "+1")
def _pyro_plus1_s(state, host):
    return 58 if mana_shortage(state) else 31


@eff("Way of the Warlord", "-4")
def _warlord_minus4(state, host, x):
    damage_opp(state, 2, "way_warlord")
    if state.resilience:
        c = best_killable_threat(state, 2)
        if c is not None:
            opp_remove_creature(state, c[0], c[1], "damage")
    state.m["warlord_pings"] += 1


@sc("Way of the Warlord", "-4")
def _warlord_minus4_s(state, host):
    L = loyalty(host)
    if L >= max(8, ult_cost(host.card.name) + 2 if ult_cost(host.card.name) else 8):
        return 16
    return None


@eff("Way of the Deathbringer", "-2")
def _deathbringer_minus2(state, host, x):
    f = sacrifice_fodder(state)
    if f is None:
        return
    remove_permanent(state, f, "sacrificed")
    create_token(state, "Beast Token", 1, src="way_deathbringer")
    state.m["deathbringer_beasts"] += 1


@sc("Way of the Deathbringer", "-2")
def _deathbringer_minus2_s(state, host):
    if loyalty(host) < 3 or sacrifice_fodder(state) is None:
        return None
    return 44


@eff("Way of the Healer", "-2")
def _healer_minus2(state, host, x):
    create_token(state, "Cadet Token", 1, src="way_healer")
    surveil(state, 1)


@sc("Way of the Healer", "-2")
def _healer_minus2_s(state, host):
    return 38 if loyalty(host) >= 4 else None


@eff("Way of the Wildspeaker", "-4")
def _wildspeaker_minus4(state, host, x):
    create_token(state, "Beast Token", 1, src="way_wildspeaker")


@sc("Way of the Wildspeaker", "-4")
def _wildspeaker_minus4_s(state, host):
    return 58 if loyalty(host) >= 6 else None


@eff("Ichormoon Gauntlet", "0")
def _gauntlet_zero(state, host, x):
    proliferate(state, "gauntlet_zero")


@sc("Ichormoon Gauntlet", "0")
def _gauntlet_zero_s(state, host):
    n = sum(1 for p in vis(state) if (is_pw(p) and loyalty(p) >= 1) or p.ctr.get("p1p1", 0) > 0)
    return 40 + 7 * n if n >= 2 else None


@eff("Ichormoon Gauntlet", "-12")
def _gauntlet_extra_turn(state, host, x):
    state.m["extra_turns_taken"] += 1
    state.extra_turn_pending = True


@sc("Ichormoon Gauntlet", "-12")
def _gauntlet_extra_turn_s(state, host):
    return 94


@eff("Kiora of Salt and Sand", "-8")
def _kiora_leviathan(state, host, x):
    create_token(state, "Leviathan Token", 1, src="kiora")


@sc("Kiora of Salt and Sand", "-8")
def _kiora_leviathan_s(state, host):
    return 72


@eff("Sanctum Lurker", "+2")
def _lurker_plus2(state, host, x):
    damage_each_opp(state, 1, "sanctum_lurker")
    gain_life(state, 1, "sanctum_lurker")


@sc("Sanctum Lurker", "+2")
def _lurker_plus2_s(state, host):
    return 46


@eff("Teferi's Talent", "-12")
def _teferis_talent_ult(state, host, x):
    if "teferi_ta" not in state.emblems:
        state.emblems.append("teferi_ta")


@sc("Teferi's Talent", "-12")
def _teferis_talent_ult_s(state, host):
    return 60 if "teferi_ta" not in state.emblems else None


@eff("Liliana's Talent", "-8")
def _lilianas_talent_ult(state, host, x):
    """'Put all creature cards from all graveyards onto the battlefield under your control.'"""
    mine = [c for c in list(state.graveyard) if "creature" in CARD_DB[c].types]
    for c in mine:
        state.graveyard.remove(c)
        p = mk_perm(state, c)
        state.battlefield.append(p)
        enter_permanent(state, p, from_cast=False)
        state.m["recursion_events"] += 1
    if state.resilience:
        for o in alive_opps(state):
            n = o.cgy
            o.cgy = 0
            for _ in range(n):
                create_token(state, "Cadet Token", 1, src="lilianas_talent_opp")      # carta de criatura de oponente: corpo generico (a Master do Mothman usou a mesma convencao)


@sc("Liliana's Talent", "-8")
def _lilianas_talent_ult_s(state, host):
    n = sum(1 for c in state.graveyard if "creature" in CARD_DB[c].types) + (sum(o.cgy for o in alive_opps(state)) if state.resilience else 0)
    return 55 if n >= 2 else None


# =========================================================
# MAGIAS (instantaneas / feiticos): efeitos
# =========================================================
CARD_PRIORITY = {
    "Tam, the Possibility": 200, "Sol Ring": 100, "Arcane Signet": 90, "Birds of Paradise": 88, "Noble Hierarch": 88, "Ignoble Hierarch": 86, "Bloom Tender": 84, "Faeburrow Elder": 80,
    "Fellwar Stone": 70, "Oath of Nissa": 82, "Leyline Immersion": 56,
    "Oko, Thief of Crowns": 78, "Garruk, Curse Breaker": 66, "Garruk Wildspeaker": 70, "Wrenn and Realmbreaker": 74, "Dack Fayden": 52, "Dihada, Binder of Wills": 60, "Domri, Chaos Bringer": 62,
    "Minsc & Boo, Timeless Heroes": 76, "Narset Transcendent": 54, "Professor Dellian Fel": 64, "Tamiyo, Field Researcher": 61, "Teferi, Hero of Dominaria": 72, "Teferi, Temporal Archmage": 66,
    "Garruk, Veiled Butcher": 62, "Nissa, Ascended Animist": 68, "The Eternal Wanderer": 64, "Vraska, Betrayal's Sting": 70, "Ajani Unrelenting": 66, "Elspeth, Sun's Champion": 74,
    "Kasmina, Enigma Sage": 72, "Saheeli, Sublime Artificer": 50, "Vronos, Masked Inquisitor": 58, "Aminatou, the Fateshifter": 60, "Tezzeret the Seeker": 56, "Chandra, Legacy of Fire": 66,
    "All Will Be One": 60, "Ichormoon Gauntlet": 68, "Flux Channeler": 64, "Displacer Kitten": 58, "Kiora of Salt and Sand": 52, "Dreamtide Whale": 46, "Patrolling Peacemaker": 50,
    "Onakke Oathkeeper": 48, "Sanctum Lurker": 66, "Oath of Teferi": 60, "The Chain Veil": 55, "Chromatic Orrery": 62, "Staff of Compleation": 40, "Entrust the Spark": 45,
    "Ripples of Potential": 30, "Teferi's Talent": 36, "Liliana's Talent": 35, "Blasphemous Act": 20, "Overwrite the Multiverse": 20, "Promise of Loyalty": 20,
    "Way of the Wildspeaker": 70, "Way of the Mind Sculptor": 66, "Way of the Paradox": 72, "Way of the Necromancer": 55, "Way of the Deathbringer": 62, "Way of the Healer": 60,
    "Way of the Pyromancer": 50, "Way of the Warlord": 52,
}
THREAT_POWER = 3
WIPE_MIN_OPP_POWER = 8


def veil_worth_it(state: GameState) -> bool:
    n = 0
    for p in pws(state):
        if pw_acts_used(state, p) >= acts_allowed(state):
            continue
    used = [p for p in pws(state) if pw_acts_used(state, p) >= 1]
    return len(used) >= 2


def cast_gate(state: GameState, name: str) -> bool:
    """Politica de situacao: magias que so' valem com alvo/ameaca (nao conjuro 'por conjurar')."""
    c = CARD_DB[name]
    t = c.tags
    nopp = alive_opps(state)
    if not nopp and "commander" not in t:
        pass
    if "blasphemous" in t:
        mine = [p for p in creatures(state) if not p.is_token and p.card.name != "Tam, the Possibility"]
        if state.resilience:
            return opp_threat_power(state) >= WIPE_MIN_OPP_POWER and len(mine) <= 1
        return state.target_ok and len(mine) == 0 and len(creatures(state)) <= 2
    if "overwrite" in t:
        mine = [p for p in creatures(state) if p.card.name != "Tam, the Possibility"]
        if state.resilience:
            return opp_threat_power(state) >= WIPE_MIN_OPP_POWER + 2 and len(mine) <= 2
        return state.target_ok and len(mine) == 0
    if "promise" in t:
        return state.resilience and sum(len(o.board) for o in nopp) >= 4 and opp_threat_power(state) >= 8
    if "entrust" in t:
        return entrust_plan(state) is not None
    if "ripples" in t:
        return False                            # tratada em ACTIONS (proliferate no fim do turno / protecao no turno dele)
    if "aura" in t:
        host = aura_host(state, name)
        if host is None:
            return False
        if name == "Leyline Immersion":
            return mana_shortage(state) or available_mana(state) <= 8
        if name == "Teferi's Talent":
            return loyalty(host) >= 3
        return True
    if "veil" in t:
        return len(pws(state)) >= 2 or any("planeswalker" in CARD_DB[h].types for h in state.hand)
    if "awbo" in t:
        return True
    return True


def entrust_plan(state: GameState):
    """Entrust the Spark: sacrifico o planeswalker de MENOR valor (Jace token / lealdade baixa / ultimate ja' usado) e busco o de maior valor na biblioteca. Devolve (sacrificado, buscado) ou None."""
    pwl = [c for c in sorted(set(state.library)) if "planeswalker" in CARD_DB[c].types]
    if not pwl:
        return None
    cands = []
    for p in pws(state):
        v = pw_keep_value(state, p)
        cands.append((v, p))
    best_lib = max(pwl, key=lambda c: (CARD_PRIORITY.get(c, 20), c))
    if not cands:
        return None
    v, p = min(cands, key=lambda vp: (vp[0], vp[1].uid))
    if v + 12 < CARD_PRIORITY.get(best_lib, 20) and (loyalty(p) <= 3 or p.first_ult_done or p.card.name == "Jace Token"):
        return p, best_lib
    return None


def pw_keep_value(state: GameState, p: Permanent) -> float:
    nm = p.card.name
    if nm == "Jace Token":
        return 5.0 + loyalty(p)
    v = float(CARD_PRIORITY.get(nm, 30)) + loyalty(p) * 1.5
    if p.first_ult_done:
        v -= 12
    return v


def resolve_instant_sorcery(state: GameState, name: str):
    t = CARD_DB[name].tags
    dest = "graveyard"
    if "blasphemous" in t:
        n_opp_c = sum(len(o.board) for o in state.opps)
        for p in list(creatures(state)):
            if toughness(state, p) <= 13:
                remove_permanent(state, p, "dies")
        for o in alive_opps(state):
            for c in list(o.board):
                opp_remove_creature(state, o, c, "damage")
        if not state.resilience and state.target_ok:
            state.m["proxy_wipe"] += 1
        state.m["interaction_plays"] += 1
        state.m["wipes_cast"] += 1
    elif "overwrite" in t:
        n = len(creatures(state))
        for p in list(creatures(state)):
            remove_permanent(state, p, "exile")
        for o in alive_opps(state):
            n += len(o.board)
            for c in list(o.board):
                opp_remove_creature(state, o, c, "exile")
        empower_jace(state, n, "overwrite")
        if not state.resilience and state.target_ok:
            state.m["proxy_wipe"] += 1
        state.m["interaction_plays"] += 1
        state.m["wipes_cast"] += 1
    elif "promise" in t:
        mine = sorted(creatures(state), key=lambda p: (-(power(state, p) + toughness(state, p)), p.uid))
        for p in mine[1:]:
            remove_permanent(state, p, "sacrificed")
        for o in alive_opps(state):
            o.board = []                      # cada um poe um vow numa criatura e sacrifica o resto; a que fica nao ataca voce nem seus planeswalkers (neutralizada)
        state.m["wipes_cast"] += 1
        state.m["interaction_plays"] += 1
    elif "entrust" in t:
        plan = entrust_plan(state)
        if plan is not None:
            fodder, tutor = plan
            remove_permanent(state, fodder, "sacrificed")
            if tutor in state.library:
                state.library.remove(tutor)
                state.rng.shuffle(state.library)
                p = mk_perm(state, tutor)
                state.battlefield.append(p)
                state.m["entrust_tutors"] += 1
                state.m["recursion_events"] += 0
                enter_permanent(state, p, from_cast=False)
        else:
            state.m["entrust_fizzled"] += 1
    elif "ripples" in t:
        before = {p.uid: (p.ctr.get("loyalty", 0), p.ctr.get("p1p1", 0), p.ctr.get("time", 0)) for p in vis(state)}
        proliferate(state, "ripples")
        if state.resilience:
            for p in list(vis(state)):
                b = before.get(p.uid)
                if b is not None and (p.ctr.get("loyalty", 0), p.ctr.get("p1p1", 0), p.ctr.get("time", 0)) != b and is_pw(p):
                    phase_out(state, p)
            state.m["ripples_phase_outs"] += 1
    if state.rebound_armed and state.cast_zone == "hand" and name in ("Entrust the Spark", "Ripples of Potential", "Overwrite the Multiverse", "Blasphemous Act", "Promise of Loyalty") and name not in state.rebound_pending:
        state.rebound_armed = False
        state.rebound_pending.append(name)
        state.exile.append(name)
        state.m["rebounds_set"] += 1
        return
    state.graveyard.append(name)
    sba(state)


# =========================================================
# ACOES (habilidades ativadas que nao sao de lealdade; mana ociosa)
# =========================================================

def tam_ready(state: GameState) -> Optional[Permanent]:
    for p in perms_named(state, "Tam, the Possibility"):
        if not p.tapped and not sick(state, p):
            return p
    return None


def act_tam_proliferate(state: GameState) -> bool:
    """Tam: '{W}{U}{B}{R}{G}, {T}: Proliferate X times, where X is the number of planeswalker types among planeswalkers you control.' Vale a pena com X >= 2 e lealdade pra dar."""
    if not TAM_ACTIVATE:
        return False
    tam = tam_ready(state)
    if tam is None:
        return False
    X = pw_types(state)
    targets = sum(1 for p in vis(state) if (is_pw(p) and loyalty(p) >= 1) or p.ctr.get("p1p1", 0) > 0 or p.ctr.get("time", 0) > 0) + sum(1 for o in alive_opps(state) if o.poison > 0)
    if X < 2 or targets < 2 or X * targets < 6:
        return False
    pips = tuple(frozenset({c}) for c in COLORS5)
    if not can_pay(state, 0, pips, CTX_ABILITY):
        return False
    pay_mana(state, 0, pips, CTX_ABILITY)
    tam.tapped = True
    state.m["tam_activations"] += 1
    state.m["tam_x_total"] += X
    mark(state, "first_tam_activation")
    proliferate(state, "tam", times=X)
    return True


def act_chain_veil(state: GameState) -> bool:
    """The Chain Veil: '{4}, {T}: For each planeswalker you control, you may activate one of its loyalty abilities once this turn as though none of its loyalty abilities have been activated this turn.'"""
    if state.phase not in ("main1", "main2"):
        return False
    for v in perms_named(state, "The Chain Veil"):
        if v.tapped:
            continue
        # vale se >= 2 planeswalkers ja' ativaram e tem habilidade boa pra repetir
        gain = 0.0
        for p in pws(state):
            if pw_acts_used(state, p) >= acts_allowed(state):
                tmp = ability_options_ignoring_used(state, p)
                if tmp and tmp[0][0] >= 44:
                    gain += tmp[0][0]
        if gain < 100:
            return False
        if not can_pay(state, 4, (), CTX_ABILITY):
            return False
        pay_mana(state, 4, (), CTX_ABILITY)
        v.tapped = True
        state.m["_veil_extra"] = state.m.get("_veil_extra", 0) + 1
        state.m["veil_activations"] += 1
        activate_planeswalkers(state)
        return True
    return False


def ability_options_ignoring_used(state: GameState, host: Permanent) -> list:
    return ability_options(state, host)


def staff_use_kind(state: GameState) -> Optional[str]:
    """Qual ativacao do Staff vale agora: proliferate (3 de vida: >= 4 permanentes com contador), compra (4 de vida: com folga de vida e biblioteca) ou nenhuma."""
    n = sum(1 for p in vis(state) if (is_pw(p) and loyalty(p) >= 1) or p.ctr.get("p1p1", 0) > 0)
    if n >= 4 and state.life >= 18:
        return "proliferate"
    if state.life >= 22 and len(state.library) > 20:
        return "draw"
    return None


def act_staff(state: GameState) -> bool:
    """Staff of Compleation: '{T}, Pay 3 life: Proliferate.' / '{T}, Pay 4 life: Draw a card.' e '{5}: Untap this artifact.' (o {5} liga uma ativacao na outra enquanto houver mana ociosa e vida)."""
    if state.phase != "main2":
        return False
    for s in perms_named(state, "Staff of Compleation"):
        kind = staff_use_kind(state)
        if kind is None or state.life < 16:
            continue
        if s.tapped:
            if not can_pay(state, 5, (), CTX_ABILITY):
                continue
            pay_mana(state, 5, (), CTX_ABILITY)
            s.tapped = False
            state.m["staff_untaps"] += 1
        s.tapped = True
        if kind == "proliferate":
            lose_life(state, 3, "staff")
            proliferate(state, "staff")
            state.m["staff_proliferates"] += 1
        else:
            lose_life(state, 4, "staff")
            draw_cards(state, 1, "staff")
            state.m["staff_draws"] += 1
        return True
    return False


def act_orrery_draw(state: GameState) -> bool:
    """Chromatic Orrery: '{5}, {T}: Draw a card for each color among permanents you control.' (so' com mana ociosa e o Orrery virado nao e' fonte necessaria)"""
    if state.phase != "main2":
        return False
    for o in perms_named(state, "Chromatic Orrery"):
        if o.tapped:
            continue
        k = len(colors_among(state))
        if k < 3 or len(state.library) < 20:
            continue
        # os 5 vem de outras fontes; o proprio Orrery toca pelo custo
        srcs = [s for s in mana_sources(state, CTX_ABILITY) if s.perm is not o]
        if _plan(state, 5, (), CTX_ABILITY, srcs=srcs) is None:
            continue
        # paga com as outras fontes
        o.tapped = True
        if not pay_mana(state, 5, (), CTX_ABILITY):
            o.tapped = False
            continue
        draw_cards(state, k, "orrery")
        state.m["orrery_draws"] += 1
        return True
    return False


def act_baxter_draw(state: GameState) -> bool:
    if state.phase != "main2":
        return False
    for b in perms_named(state, "Baxter Building"):
        if b.tapped or len(state.library) < 20:
            continue
        if not any(toughness(state, p) >= 4 for p in creatures(state)):
            continue
        srcs = [s for s in mana_sources(state, CTX_ABILITY) if s.perm is not b]
        if _plan(state, 4, (), CTX_ABILITY, srcs=srcs) is None:
            continue
        b.tapped = True
        if not pay_mana(state, 4, (), CTX_ABILITY):
            b.tapped = False
            continue
        draw_cards(state, 1, "baxter")
        state.m["baxter_draws"] += 1
        return True
    return False


def act_cycle_triome(state: GameState) -> bool:
    """Cycling {3} dos triomes: carta de terreno sobrando na mao com mana ociosa."""
    if state.phase != "main2" or n_lands(state) < 6 or len(state.library) < 20:
        return False
    for h in sorted(set(state.hand)):
        if LANDS.get(h, {}).get("kind") == "triome":
            others = [x for x in state.hand if "land" in CARD_DB[x].types and x != h]
            if state.lands_played_this_turn >= land_drops_available(state) or others:
                if can_pay(state, 3, (), CTX_ABILITY):
                    pay_mana(state, 3, (), CTX_ABILITY)
                    state.hand.remove(h)
                    state.graveyard.append(h)
                    draw_cards(state, 1, "triome_cycling")
                    state.m["triome_cycles"] += 1
                    return True
    return False


def act_boseiju_channel(state: GameState) -> bool:
    """Boseiju, Channel: '{1}{G}, discard: destroy target artifact, enchantment, or nonbasic land an opponent controls' (custa {1} a menos por criatura lendaria sua): alvo de oponente = proxy."""
    if "Boseiju, Who Endures" not in state.hand or n_lands(state) < 7 or not state.target_ok:
        return False
    legs = sum(1 for p in creatures(state) if is_legendary(p))
    g = max(0, 1 - legs)
    pips = (frozenset("G"),)
    if can_pay(state, g, pips, CTX_ABILITY):
        pay_mana(state, g, pips, CTX_ABILITY)
        state.hand.remove("Boseiju, Who Endures")
        state.graveyard.append("Boseiju, Who Endures")
        state.m["proxy_channel"] += 1
        state.m["interaction_plays"] += 1
        return True
    return False


def act_onakke_recursion(state: GameState) -> bool:
    """Onakke Oathkeeper (no cemiterio): '{4}{W}{W}, Exile this card: Return target planeswalker card from your graveyard to the battlefield.'"""
    if "Onakke Oathkeeper" not in state.graveyard:
        return False
    cands = [c for c in state.graveyard if "planeswalker" in CARD_DB[c].types]
    if not cands:
        return False
    pips = (frozenset("W"), frozenset("W"))
    if not can_pay(state, 4, pips, CTX_ABILITY):
        return False
    pay_mana(state, 4, pips, CTX_ABILITY)
    state.graveyard.remove("Onakke Oathkeeper")
    state.exile.append("Onakke Oathkeeper")
    pick = max(cands, key=lambda c: (CARD_PRIORITY.get(c, 20), c))
    state.graveyard.remove(pick)
    p = mk_perm(state, pick)
    state.battlefield.append(p)
    state.m["recursion_events"] += 1
    state.m["onakke_returns"] += 1
    enter_permanent(state, p, from_cast=False)
    return True


def act_ripples(state: GameState) -> bool:
    """Ripples of Potential ({1}{U}, instantanea): no fim do meu turno com mana sobrando, proliferate quando ha' lealdade pra dar (e protege no modo de resiliencia)."""
    if "Ripples of Potential" not in state.hand or state.phase != "main2":
        return False
    n = sum(1 for p in vis(state) if (is_pw(p) and loyalty(p) >= 1) or p.ctr.get("p1p1", 0) > 0)
    if n < 3 and not (state.resilience and n >= 2):
        return False
    if can_cast_name(state, "Ripples of Potential"):
        # nao gasta o mana do comandante/PW ainda na mao: so' com sobra
        if sum(1 for h in state.hand if "planeswalker" in CARD_DB[h].types and can_cast_name(state, h)) > 0:
            return False
        return cast_card(state, "Ripples of Potential")
    return False


def act_cast_impulse(state: GameState) -> bool:
    """Chandra 0: cartas exiladas jogaveis neste turno (terreno, magia)."""
    for c in list(state.impulse):
        if "land" not in CARD_DB[c].types and can_cast_name(state, c) and cast_gate(state, c):
            return cast_card(state, c, zone="impulse")
    return False


def act_staff_necromancer(state: GameState) -> bool:
    """Staff: '{T}, Pay 1 life: Destroy target permanent you own.' com Way of the Necromancer em campo e uma ficha descartavel: cada morte poe lealdade em todos os planeswalkers."""
    if not has_perm(state, "Way of the Necromancer") or state.life < 14 or state.phase != "main2":
        return False
    f = sacrifice_fodder(state)
    if f is None:
        return False
    for s in perms_named(state, "Staff of Compleation"):
        if not s.tapped and len(pws(state)) >= 2:
            s.tapped = True
            lose_life(state, 1, "staff")
            remove_permanent(state, f, "dies")
            state.m["staff_destroys"] += 1
            return True
    return False


ACTIONS = [act_cast_impulse, act_onakke_recursion, act_tam_proliferate, act_chain_veil, act_staff_necromancer, act_ripples, act_staff, act_orrery_draw, act_baxter_draw,
           act_cycle_triome, act_boseiju_channel]


def use_spare_mana(state: GameState):
    for _ in range(40):
        if state.game_over:
            return
        acted = False
        for fn in ACTIONS:
            if fn(state):
                acted = True
                break
        if not acted:
            return


# =========================================================
# ATIVACAO DOS PLANESWALKERS (uma passada ANTES de conjurar so' com as que dao mana/cartas; outra DEPOIS; e a do PW que acabou de entrar)
# =========================================================
PRE_ABILITIES = {("Chandra, Legacy of Fire", "+1"), ("Chandra, Legacy of Fire", "0"), ("Domri, Chaos Bringer", "+1"), ("Domri, Chaos Bringer", "-3"), ("Way of the Pyromancer", "+1"),
                 ("Teferi, Hero of Dominaria", "+1"), ("Aminatou, the Fateshifter", "+1"), ("Professor Dellian Fel", "0"), ("Jace Token", "-3"), ("Vraska, Betrayal's Sting", "0"),
                 ("Dack Fayden", "+1"), ("Narset Transcendent", "+1"), ("Teferi, Temporal Archmage", "+1"), ("Teferi, Temporal Archmage", "-1"), ("Dihada, Binder of Wills", "-3"),
                 ("Tezzeret the Seeker", "-X"), ("Wrenn and Realmbreaker", "-2")}
POOL_MANA_ABILITIES = {("Chandra, Legacy of Fire", "+1"), ("Domri, Chaos Bringer", "+1"), ("Way of the Pyromancer", "+1")}


def activation_pick(state: GameState, host: Permanent, pre: bool = False, window: str = "main"):
    opts = ability_options(state, host)
    if window == "opp":
        opts = [o for o in opts if (o[1], o[2]) not in POOL_MANA_ABILITIES and (o[1], o[2]) not in (("Garruk Wildspeaker", "-4"), ("Nissa, Ascended Animist", "-7"))]
    if not opts:
        return None
    best = opts[0]
    if pre and (best[1], best[2]) not in PRE_ABILITIES:
        return None
    if best[0] <= 0:
        return None
    return best


def activate_one(state: GameState, host: Permanent, pre: bool = False, window: str = "main") -> bool:
    if not pw_can_activate(state, host, window) or host not in state.battlefield:
        return False
    pick = activation_pick(state, host, pre, window)
    if pick is None:
        return False
    s, src, key, x = pick
    return activate_ability(state, host, src, key, x, window)


def pw_order(state: GameState) -> list:
    order = sorted(pws(state), key=lambda p: (-CARD_PRIORITY.get(p.card.name, 20), p.uid))
    return order


def activate_planeswalkers(state: GameState, pre: bool = False, window: str = "main"):
    """Ativa os planeswalkers que ainda podem (uma por turno; duas com Oath of Teferi; mais uma por uso da Chain Veil). Repete ate' ninguem poder (efeitos reabrem: piscar, Veil)."""
    for _ in range(12):
        if state.game_over:
            return
        did = False
        for p in pw_order(state):
            if p not in state.battlefield:
                continue
            if activate_one(state, p, pre, window):
                did = True
                if state.game_over:
                    return
        if not did or pre:
            return


# =========================================================
# CAST LOOP
# =========================================================

def cast_candidates(state: GameState) -> list:
    out = []
    seen = []
    for name in state.hand:
        if name in seen:
            continue
        seen.append(name)
        c = CARD_DB[name]
        if "land" in c.types:
            continue
        if can_cast_name(state, name) and cast_gate(state, name):
            out.append((name, "hand"))
    if state.commander_in_cz and can_cast_name(state, "Tam, the Possibility", "cz"):
        out.append(("Tam, the Possibility", "cz"))
    if "wrenn" in state.emblems:
        seen = []
        for name in state.graveyard:
            if name in seen:
                continue
            seen.append(name)
            c = CARD_DB[name]
            if ("instant" in c.types or "sorcery" in c.types) or "land" in c.types or c.token:
                continue
            if can_cast_name(state, name) and cast_gate(state, name):
                out.append((name, "graveyard"))
    for name in sorted(set(state.impulse)):
        c = CARD_DB[name]
        if "land" not in c.types and can_cast_name(state, name) and cast_gate(state, name):
            out.append((name, "impulse"))
    return out


def cast_score(state: GameState, name: str, zone: str) -> float:
    s = float(CARD_PRIORITY.get(name, 20))
    if name == "Tam, the Possibility":
        return 200.0
    c = CARD_DB[name]
    ramp = ("Sol Ring", "Arcane Signet", "Birds of Paradise", "Noble Hierarch", "Ignoble Hierarch", "Bloom Tender", "Faeburrow Elder", "Fellwar Stone")
    if name in ramp and n_lands(state) <= 6:
        s += 12
    if zone == "graveyard":
        s -= 4
    # planeswalker de custo alto so' passa na frente se nao deixa a mao sem jogada barata
    s += 0.05 * c.mv
    return s


def cast_loop(state: GameState):
    failed = set()
    for _ in range(40):
        if state.game_over:
            return
        cands = [t for t in cast_candidates(state) if t not in failed]
        if not cands:
            return
        best = max(cands, key=lambda t: (cast_score(state, t[0], t[1]), t[0]))
        name, zone = best
        before_pws = {p.uid for p in pws(state)}
        if not cast_card(state, name, zone=zone):
            failed.add(best)
            continue
        if state.game_over:
            return
        # o PW que acabou de entrar pode ativar NESTE turno (CR 606.3: nao ha' doenca de invocacao pra lealdade)
        for p in pws(state):
            if p.uid not in before_pws and p in state.battlefield:
                activate_one(state, p)
                activate_planeswalkers(state)
                break


# =========================================================
# OPONENTES (passivos no modo padrao: terreno, magias; modo de resiliencia: tabuleiro, ataque, remocao)
# =========================================================
INTERACTION_SETUP_TURNS = 2
COUNTER_MIN_MV = 3
COUNTERSPELL_CHANCE_FACTOR = 0.5
OPPONENT_ATTENTION_CHANCE = 1.0 / 3
BOARD_WIPE_CHANCE_FACTOR = 0.4


def make_opp(seed: int, idx: int) -> Opp:
    rng = random.Random(seed * 1_000_003 + idx * 7919 + 13)
    o = Opp(idx=idx)
    o.identity = rng.sample(list(COLORS5), 2)
    o.hand_size = OPP_HAND_START
    return o


def opp_rng(state: GameState, o: Opp) -> random.Random:
    return state.opp_rngs[o.idx]


def begin_any_turn(state: GameState):
    state.turn_id += 1
    state.spells_this_turn_by_player = {}


def opp_spell_cast(state: GameState, o: Opp, noncreature: bool, mv: int):
    """Gatilhos de 'quando um jogador conjura a sua 2a magia no turno' (Dreamtide Whale: qualquer jogador) e crime de oponente (Patrolling Peacemaker)."""
    o.spells_this_turn += 1
    state.spells_this_turn_by_player[o.idx] = state.spells_this_turn_by_player.get(o.idx, 0) + 1
    if state.spells_this_turn_by_player[o.idx] == 2:
        whale_trigger(state)
    if noncreature and state.proxy_rng.random() < OPP_CRIME_PROB_PER_NONCREATURE_SPELL:
        for _ in range(count_named(state, "Patrolling Peacemaker")):
            state.m["opp_crimes_total"] += 1
            proliferate(state, "peacemaker")


def opponent_turn(state: GameState, o: Opp):
    if o.eliminated or state.game_over:
        return
    o.turns_taken += 1
    o.spells_this_turn = 0
    begin_any_turn(state)
    rng = opp_rng(state, o)
    o.lost_life_this_turn = 0
    if o.hand_size < 12:
        o.hand_size += 1
    # terreno: cada terreno produz uma cor da identidade dele
    if o.hand_size > 0 and rng.random() < (0.8 if o.turns_taken <= 8 else 0.35):
        o.lands += 1
        o.hand_size -= 1
        o.land_colors.append(rng.choice(o.identity))
    if state.resilience:
        opp_turn_start(state, o)
    if "teferi_ta" in state.emblems:
        activate_planeswalkers(state, window="opp")      # emblema do Teferi, Temporal Archmage: ativacao de lealdade a qualquer hora (1 por planeswalker por turno de oponente)
    if o.turns_taken == 1:
        nspells = 1 if rng.random() < 0.15 else 0
    else:
        r = rng.random()
        nspells = 0 if r < OPP_SPELLS_PROB[0] else (1 if r < OPP_SPELLS_PROB[0] + OPP_SPELLS_PROB[1] else 2)
    mana = o.lands
    spent = 0
    for _ in range(nspells):
        if o.hand_size <= 0 or o.eliminated or state.game_over:
            break
        mv = rng.choices(OPP_SPELL_MV, weights=OPP_SPELL_MV_W)[0]
        creature = rng.random() < OPP_CREATURE_SPELL_FRACTION
        if mv > mana - spent:
            mv = max(0, mana - spent)
            if mv == 0:
                break
        spent += mv
        o.hand_size -= 1
        o.spells_total += 1
        state.m["opp_spells_total"] += 1
        if "narset" in state.emblems and not creature:
            state.m["opp_spells_blocked_narset"] += 1
            continue
        opp_spell_cast(state, o, noncreature=not creature, mv=mv)
        if state.game_over:
            return
    if state.resilience:
        opponent_combat(state, o)
    end_step_any(state, mine=False)


def end_step_any(state: GameState, mine: bool):
    """Domri, Chaos Bringer (emblema): 'At the beginning of each end step, create a 4/4 red and green Beast creature token with trample.' (cada end step: o meu e o de cada oponente)."""
    if "domri" in state.emblems:
        create_token(state, "Beast Token", 1, src="domri_emblem")
        state.m["domri_emblem_beasts"] += 1


# ---- alvos de oponente: real no modo de resiliencia, proxy no modo padrao ----
def opp_threats(state: GameState) -> list:
    return [(o, c) for o in alive_opps(state) for c in o.board if not c.get("frozen")]


def biggest_threat(state: GameState, max_toughness: Optional[int] = None):
    cands = [(o, c) for o, c in opp_threats(state) if max_toughness is None or c["t"] <= max_toughness]
    if not cands:
        return (None, None)
    return max(cands, key=lambda oc: (oc[1]["p"], oc[1]["trample"], oc[1]["flying"], -oc[0].idx))


def opp_threat_power(state: GameState) -> int:
    return sum(c["p"] for o in alive_opps(state) for c in o.board)


def best_killable_threat(state: GameState, dmg: int):
    cands = [(o, c) for o in alive_opps(state) for c in o.board if c["t"] <= dmg]
    if not cands:
        return None
    return max(cands, key=lambda oc: (oc[1]["p"], oc[1]["t"], -oc[0].idx))


def opp_remove_creature(state: GameState, o: Opp, c: dict, how: str = "destroy"):
    for i, x in enumerate(o.board):
        if x is c:
            del o.board[i]
            break
    else:
        return
    state.m["opp_creatures_removed"] += 1
    state.m["opp_creatures_removed_" + how] += 1
    if how in ("destroy", "damage", "combat") and not has_perm(state, "Garruk, Veiled Butcher"):
        o.cgy += 1                                       # Garruk, Veiled Butcher: 'If a creature an opponent controls would die, exile it instead' (nao vai pro cemiterio dele)
    elif how in ("destroy", "damage", "combat"):
        state.m["opp_creatures_exiled_by_garruk_vb"] += 1
    if c.get("cmd"):
        o.cmd_cooldown = 1
        o.cmd_bonus = max(0, (c["p"] - 3) // 2)


def kill_threat(state: GameState, src: str, how: str = "destroy") -> bool:
    """Remocao/bounce/exilio mirando criatura de oponente: no modo de resiliencia remove a maior ameaca de verdade; no padrao conta como proxy quando ha' alvo (OPP_TARGET_PROB)."""
    if state.resilience:
        o, c = biggest_threat(state)
        if c is None:
            return False
        state.m["interaction_plays"] += 1
        opp_remove_creature(state, o, c, "exile" if how in ("exile", "tuck", "bounce", "treasure") else "destroy")
        state.m["kills_by_" + src] += 1
        return True
    if state.target_ok:
        state.m["proxy_" + src] += 1
        state.m["interaction_plays"] += 1
        return True
    return False


def freeze_threats(state: GameState, n: int, src: str):
    """'Tap ... It doesn't untap during its controller's next untap step' / -4/-1 (Garruk VB): neutraliza ate' N ameacas no proximo turno do dono."""
    if state.resilience:
        for _ in range(n):
            o, c = biggest_threat(state)
            if c is None:
                return
            c["frozen"] = 1
            state.m["opp_creatures_frozen"] += 1
        state.m["interaction_plays"] += 1
    elif state.target_ok:
        state.m["proxy_" + src] += 1
        state.m["interaction_plays"] += 1


# =========================================================
# FLUXO DO TURNO
# =========================================================

def untap_my_permanents(state: GameState):
    phase_in_all(state)
    for p in state.battlefield:
        p.tapped = False
        p.haste_until_eot = False


def expire_effects_upkeep(state: GameState):
    """'Ate' o seu proximo turno' acaba agora (Wrenn: terreno deixa de ser criatura)."""
    for p in state.battlefield:
        if p.anim == "next_turn":
            p.anim = None
            p.base_pt = None
            p.ctr.pop("vigilance", None)
    state.cb_buff = False
    state.tamiyo_marked = []
    state.dihada_shield = None


def upkeep_step(state: GameState):
    state.lands_played_this_turn = 0
    state.extra_land_drops = 0
    state.spells_cast_this_turn = 0
    state.noncreature_spells_this_turn = 0
    state.activated_loyalty_this_turn = False
    state.loyalty_acts_this_turn = 0
    state.attackers_this_turn = []
    state.pool = {}
    state.riot_pool = 0
    state.impulse = []
    state.m["_veil_extra"] = 0
    for p in state.battlefield:
        p.temp_p = 0
        p.temp_t = 0
        p.ctr.pop("trample_eot", None)
    for o in state.opps:
        for c in o.board:                                  # fim do -4/-1 da Garruk, Veiled Butcher ('until your next turn')
            c["p"] += c.pop("dp_applied", 0)
            c["t"] += c.pop("dt_applied", 0)
    expire_effects_upkeep(state)
    # Minsc & Boo: 'at the beginning of your upkeep, you may create Boo'
    for _ in range(count_named(state, "Minsc & Boo, Timeless Heroes")):
        make_boo(state, "upkeep")
    # Dreamtide Whale: vanishing 2 (remove um contador de tempo; ao tirar o ultimo, sacrifica)
    for w in perms_named(state, "Dreamtide Whale"):
        if w.ctr.get("time", 0) > 0:
            w.ctr["time"] -= 1
            if w.ctr["time"] == 0:
                remove_permanent(state, w, "sacrificed")
                state.m["whale_vanished"] += 1
    # rebound (Narset -2): conjura de graca a magia exilada
    for name in list(state.rebound_pending):
        state.rebound_pending.remove(name)
        if name in state.exile:
            state.exile.remove(name)
        state.cast_zone = "exile"
        on_cast(state, name)
        resolve_spell(state, name)
        state.m["rebounds_cast"] += 1
    state.target_ok = (state.turn >= OPP_TARGET_FROM_TURN) and (state.proxy_rng.random() < OPP_TARGET_PROB)


def draw_step(state: GameState):
    if state.turn == 1 and state.on_play:
        return
    draw_cards(state, 1, "normal")


def end_step(state: GameState):
    """Fim do MEU turno: Chandra (X de dano a CADA oponente, X = planeswalkers), Teferi Hero (desvira 2 terrenos), Vronos (planeswalkers saem de fase), devolucoes atrasadas (Oath of Teferi /
    Eternal Wanderer), emblema do Domri, The Chain Veil (perde 2 de vida se nao ativei lealdade), limite de mao."""
    state.phase = "end"
    for _ in range(count_named(state, "Chandra, Legacy of Fire")):
        x = len(pws(state))
        damage_each_opp(state, x, "chandra_end_step")
        state.m["chandra_triggers"] += 1
        if state.game_over:
            return
    if state.end_step_untap:
        untap_best_lands(state, state.end_step_untap)
        state.end_step_untap = 0
    for uid in state.phase_out_at_end:
        p = find_perm(state, uid)
        if p is not None and not p.phased:
            phase_out(state, p)
    state.phase_out_at_end = []
    for item in list(state.delayed_return):
        state.delayed_return.remove(item)
        if isinstance(item, str) and True:
            q = mk_perm(state, item)
            state.battlefield.append(q)
            if "commander" in q.card.tags:
                state.commander_uid = q.uid
            state.m["delayed_returns"] += 1
            enter_permanent(state, q, from_cast=False)
    end_step_any(state, mine=True)
    for _ in range(count_named(state, "The Chain Veil")):
        if not state.activated_loyalty_this_turn:
            lose_life(state, 2, "chain_veil")
    if state.game_over:
        return
    use_spare_mana(state)
    while len(state.hand) > 7:
        c = min(state.hand, key=lambda x: (discard_value(state, x), x))
        state.hand.remove(c)
        state.graveyard.append(c)
    for p in state.battlefield:
        if p.anim == "eot":
            p.anim = None
            p.base_pt = None
        p.temp_p = 0
        p.temp_t = 0
        p.haste_until_eot = False if not p.ctr.get("elk") else p.haste_until_eot


def main_phase(state: GameState, phase: str):
    if state.game_over:
        return
    state.phase = phase
    play_land_phase(state)
    activate_planeswalkers(state, pre=True)
    if COMBO_EXECUTE:
        try_infinite_combo(state)
        if state.game_over:
            return
    for _ in range(12):
        if state.game_over:
            return
        fp = fingerprint(state)
        cast_loop(state)
        play_land_phase(state)
        activate_planeswalkers(state)
        use_spare_mana(state)
        if COMBO_EXECUTE:
            try_infinite_combo(state)
        if fingerprint(state) == fp:
            break


def fingerprint(state: GameState):
    return (len(state.hand), len(state.battlefield), len(state.graveyard), len(state.library), state.spells_cast_this_turn, state.lands_played_this_turn, state.loyalty_acts_this_turn,
            sum(p.ctr.get("loyalty", 0) for p in state.battlefield), sum(1 for p in state.battlefield if p.tapped), state.m["mana_spent_total"])


def try_infinite_combo(state: GameState):
    """Chromatic Orrery + Tezzeret the Seeker + The Chain Veil: Orrery {C}x5, Veil {4},{T}: cada planeswalker ativa de novo; Tezzeret +1 desvira Orrery e Veil: +1 de mana e +1 de lealdade por volta,
    ativacoes infinitas. So' fecha a partida se ha' PAGAMENTO em campo (All Will Be One: dano por contador; Sanctum Lurker: +2 da 1 de dano a cada oponente por ativacao). Sem pagamento: registra montagem."""
    need = ("Chromatic Orrery", "Tezzeret the Seeker", "The Chain Veil")
    if not all(has_perm(state, n) for n in need):
        return
    tez = perms_named(state, "Tezzeret the Seeker")[0]
    orr = perms_named(state, "Chromatic Orrery")[0]
    veil = perms_named(state, "The Chain Veil")[0]
    if loyalty(tez) < 1:
        return
    ready = (not orr.tapped and not veil.tapped) or (pw_acts_used(state, tez) < acts_allowed(state))
    if not ready:
        return
    if state.combo_assembled_turn is None:
        state.combo_assembled_turn = state.turn
        state.m["combo_assembled"] += 1
    payoff = has_perm(state, "All Will Be One") or has_perm(state, "Sanctum Lurker")
    if payoff and not state.game_over:
        state.combo_win = "orrery_tezzeret_veil"
        for o in list(alive_opps(state)):
            eliminate_opp(state, o, "combo")
        state.m["combo_wins"] += 1


def play_turn(state: GameState):
    state.turn += 1
    begin_any_turn(state)
    state.phase = "untap"
    if state.turn > 1:
        untap_my_permanents(state)
    expire_effects_upkeep(state)
    upkeep_step(state)
    if state.game_over:
        return
    draw_step(state)
    if state.game_over:
        return
    state.by_turn.setdefault(state.turn, {})["mana"] = available_mana(state)
    log(state, f"=== turno {state.turn}: vida {state.life}, mao {sorted(state.hand)}, mana {available_mana(state)}, campo "
               f"{[p.card.name + ('*' if p.tapped else '') + (':' + str(loyalty(p)) if 'planeswalker' in p.card.types else '') for p in vis(state)]}, oponentes {[(o.life, o.poison) for o in alive_opps(state)]}")
    main_phase(state, "main1")
    if state.game_over:
        return
    combat_step(state)
    if state.game_over:
        return
    main_phase(state, "main2")
    if state.game_over:
        return
    end_step(state)
    record_turn_metrics(state)


def record_turn_metrics(state: GameState):
    t = state.turn
    bt = state.by_turn.setdefault(t, {})
    bt["pws"] = len(pws(state))
    bt["pw_types"] = pw_types(state)
    bt["loyalty"] = sum(loyalty(p) for p in pws(state))
    bt["lands"] = n_lands(state)
    bt["hand"] = len(state.hand)
    bt["creatures"] = len(creatures(state))
    bt["power"] = sum(power(state, p) for p in creatures(state))
    bt["opp_life"] = sum(max(0, o.life) for o in alive_opps(state))
    bt["opps_alive"] = len(alive_opps(state))
    bt["dmg"] = state.m["opp_damage_total"]
    bt["tam"] = 0 if state.commander_in_cz else 1
    bt["library"] = len(state.library)


# =========================================================
# COMBATE
# =========================================================

def pick_attackers(state: GameState) -> list:
    out = [p for p in creatures(state) if can_attack(state, p) and power(state, p) > 0]
    if state.resilience:
        keep = max([len(o.board) for o in alive_opps(state)] + [0])
        if keep:
            blockers = sorted(out, key=lambda p: (-(toughness(state, p)), p.uid))
            # fica em casa os de maior resistencia (bloqueiam); os sem doenca de invocacao mais fortes atacam
            stay = set(p.uid for p in blockers[:keep]) if len(out) > keep else set()
            out = [p for p in out if p.uid not in stay]
    return out


def assign_targets(state: GameState, attackers: list) -> dict:
    al = alive_opps(state)
    if not al:
        return {}
    rem = {o.idx: o.life for o in al}
    out = {}
    for p in sorted(attackers, key=lambda q: (-power(state, q), q.uid)):
        alive_rem = [o for o in al if rem[o.idx] > 0]
        tgt = min(alive_rem, key=lambda o: (rem[o.idx], o.idx)) if alive_rem else max(al, key=lambda o: (o.life, -o.idx))
        out[p.uid] = tgt.idx
        rem[tgt.idx] -= power(state, p)
    return out


def combat_step(state: GameState):
    if state.game_over:
        return
    state.phase = "combat"
    # Kiora of Salt and Sand: 'Whenever you attack, if you've activated a loyalty ability this turn, untap target attacking creature. It can't be blocked this turn.'
    attackers = pick_attackers(state)
    if not attackers or not alive_opps(state):
        return
    # exalted: so' se UM atacante
    if len(attackers) == 1:
        n_ex = sum(1 for p in vis(state) if "exalted" in p.card.tags)
        if n_ex:
            attackers[0].temp_p += n_ex
            attackers[0].temp_t += n_ex
            state.m["exalted_triggers"] += n_ex
    state.attackers_this_turn = list(attackers)
    for p in attackers:
        if "vigilance" not in p.card.tags and not p.ctr.get("vigilance") and p.uid != state.dihada_shield:
            p.tapped = True
    if state.activated_loyalty_this_turn:
        for k in perms_named(state, "Kiora of Salt and Sand"):
            tgt = max(attackers, key=lambda p: (power(state, p), p.uid))
            tgt.tapped = False
            tgt.unblockable = True
            state.m["kiora_triggers"] += 1
    # Garruk, Curse Breaker -4: +2/+2 e trample pros que atacam
    if state.cb_buff:
        for p in attackers:
            p.temp_p += 2
            p.temp_t += 2
        state.m["cb_buff_applied"] += len(attackers)
    targets = assign_targets(state, attackers)
    dmg = collections.defaultdict(int)
    for p in attackers:
        pw = power(state, p)
        if "double_strike" in p.card.tags:
            pw *= 2
        if pw <= 0:
            continue
        dmg[targets.get(p.uid)] += pw
        if p.uid == state.dihada_shield:
            gain_life(state, pw, "dihada_lifelink")                # lifelink concedido pela Dihada +2
            state.m["dihada_lifelink_total"] += pw
        if p.uid in state.tamiyo_marked:
            draw_cards(state, 2 if "double_strike" in p.card.tags else 1, "tamiyo_marked")
            state.m["tamiyo_combat_draws"] += 1
    for idx, n in sorted(dmg.items(), key=lambda kv: (kv[0] is None, kv[0] or 0)):
        if state.game_over or idx is None:
            continue
        damage_opp(state, n, "combat", idx, combat=True)
    state.m["attacks_total"] += len(attackers)
    state.m["attack_turns"] += 1
    for p in state.battlefield:
        if p.anim == "forever" and p.card.name in ("Food Token", "Treasure Token", "Servo Token") :
            pass


# =========================================================
# MULLIGAN (London; 1o gratis — mesma convencao dos outros simuladores; o jogador ESCOLHE o fundo, CR 103.5)
# =========================================================

def should_keep(hand: list, mulls: int) -> bool:
    L = sum(1 for c in hand if "land" in CARD_DB[c].types)
    cheap = sum(1 for c in hand if "land" not in CARD_DB[c].types and CARD_DB[c].mv <= 3)
    ramp = sum(1 for c in hand if c in ("Sol Ring", "Arcane Signet", "Birds of Paradise", "Noble Hierarch", "Ignoble Hierarch", "Bloom Tender", "Faeburrow Elder", "Fellwar Stone"))
    if mulls >= 3:
        return L >= 1
    if mulls == 2:
        return 2 <= L <= 5
    if L < 2 or L > 5:
        return False
    if L == 2 and (cheap < 2 and ramp < 1):
        return False
    if L == 5 and cheap < 2:
        return False
    return True


def bottom_priority(c: str, hand: list) -> float:
    """Maior = vai pro fundo primeiro."""
    cc = CARD_DB[c]
    lands = sum(1 for h in hand if "land" in CARD_DB[h].types)
    if "land" in cc.types:
        return 80.0 if lands >= 5 else (30.0 if lands == 4 else -5.0)
    if cc.mv >= 7:
        return 70.0
    return 50.0 - float(CARD_PRIORITY.get(c, 25)) * 0.4 + 0.5 * cc.mv


def mulligan(state: GameState):
    mulls = 0
    while True:
        hand = state.library[:7]
        rest = state.library[7:]
        if should_keep(hand, mulls) or mulls >= 4:
            penalty = max(0, mulls - 1)
            keep = list(hand)
            bottom = []
            for _ in range(penalty):
                worst = max(keep, key=lambda c: (bottom_priority(c, keep), c))
                keep.remove(worst)
                bottom.append(worst)
            state.hand = keep
            state.library = rest + bottom
            state.mulligans = mulls
            return
        mulls += 1
        state.rng.shuffle(state.library)


# =========================================================
# LISTA DO DECK (fonte: lista.md, na ordem do arquivo; nomes REAIS do Scryfall, Regra #2) E BIBLIOTECA
# =========================================================
# A ordem das linhas e' a ordem da biblioteca ANTES do embaralhar: a troca de A/B e' feita NO LUGAR (SWAP_IN_PLACE) pra preservar o pareamento por semente.
DECKLIST_TEXT = """
1 Baxter Building
1 Boseiju, Who Endures
1 Bountiful Promenade
1 Breeding Pool
1 City of Brass
1 Command Tower
1 Exotic Orchard
1 Fire-Lit Thicket
1 Flooded Grove
1 Great Hall of the Citadel
1 Hallowed Fountain
1 Indatha Triome
1 Jetmir's Garden
1 Ketria Triome
1 Misty Rainforest
1 Mossfire Valley
1 Overflowing Basin
1 Overgrown Tomb
1 Plaza of Heroes
1 Rejuvenating Springs
1 Spara's Headquarters
1 Spire Garden
1 Starting Town
1 Steam Vents
1 Stomping Ground
1 Temple Garden
1 The World Tree
1 Twilight Mire
1 Undergrowth Stadium
1 Verdant Catacombs
1 Watery Grave
1 Windswept Heath
1 Wooded Bastion
1 Wooded Foothills
1 Yavimaya, Cradle of Growth
1 Zagoth Triome
1 Arcane Signet
1 Birds of Paradise
1 Bloom Tender
1 Chandra, Legacy of Fire
1 Chromatic Orrery
1 Domri, Chaos Bringer
1 Faeburrow Elder
1 Fellwar Stone
1 Garruk Wildspeaker
1 Ignoble Hierarch
1 Leyline Immersion
1 Noble Hierarch
1 Sol Ring
1 Way of the Paradox
1 Way of the Pyromancer
1 Wrenn and Realmbreaker
1 Dack Fayden
1 Dihada, Binder of Wills
1 Garruk, Curse Breaker
1 Minsc & Boo, Timeless Heroes
1 Narset Transcendent
1 Oath of Nissa
1 Professor Dellian Fel
1 Tamiyo, Field Researcher
1 Teferi, Hero of Dominaria
1 Teferi, Temporal Archmage
1 Way of the Mind Sculptor
1 All Will Be One
1 Blasphemous Act
1 Garruk, Veiled Butcher
1 Nissa, Ascended Animist
1 Oko, Thief of Crowns
1 Overwrite the Multiverse
1 Promise of Loyalty
1 The Eternal Wanderer
1 Way of the Warlord
1 Dreamtide Whale
1 Flux Channeler
1 Ichormoon Gauntlet
1 Patrolling Peacemaker
1 Staff of Compleation
1 Teferi's Talent
1 The Chain Veil
1 Vraska, Betrayal's Sting
1 Way of the Necromancer
1 Ajani Unrelenting
1 Elspeth, Sun's Champion
1 Kasmina, Enigma Sage
1 Kiora of Salt and Sand
1 Saheeli, Sublime Artificer
1 Way of the Deathbringer
1 Way of the Healer
1 Way of the Wildspeaker
1 Liliana's Talent
1 Onakke Oathkeeper
1 Ripples of Potential
1 Sanctum Lurker
1 Vronos, Masked Inquisitor
1 Aminatou, the Fateshifter
1 Displacer Kitten
1 Oath of Teferi
1 Entrust the Spark
1 Tezzeret the Seeker
"""


def parse_decklist(text: str) -> list:
    out = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue
        n, name = line.split(" ", 1)
        out.extend([name.strip()] * int(n))
    return out


BASE_LIBRARY = parse_decklist(DECKLIST_TEXT)       # 99 cartas (a comandante fica na zona de comando)
SWAPS = ()                                          # variante de A/B: tupla de (carta_que_sai, carta_que_entra)
SWAP_IN_PLACE = True                                # a carta que entra ocupa o LUGAR da que sai (mesma permutacao da semente => pareamento forte)


def current_library() -> list:
    lib = list(BASE_LIBRARY)
    for out_c, in_c in SWAPS:
        if SWAP_IN_PLACE:
            lib[lib.index(out_c)] = in_c
        else:
            lib.remove(out_c)
            lib.append(in_c)
    return lib


# =========================================================
# MODO DE RESILIENCIA (interacao de oponente): tabuleiro de oponente (criaturas), ataque aos planeswalkers, remocao, wipe, descarte, anular magia, cemiterio
# Mesmo design dos outros decks: gate de atencao por oponente (1/3 dos turnos dele), 2 turnos de preparacao; criaturas dos oponentes por arquetipo (go_wide / voltron / low).
# =========================================================
OPP_ARCHETYPES = ("go_wide", "voltron", "low")
GO_WIDE_CAP = 15
LOW_CAP = 3
VOLTRON_BASE = 3
VOLTRON_CAP = 20
TAX_BUDGET_FRACTION = 0.5
COMMANDER_REMOVAL_SHARE = 0.15              # fracao das remocoes pontuais do oponente que mira a TAM quando ela esta em campo (e' a peca de motor: desconto e proliferate)
WARD_MIN_LANDS = 4                          # premissa: a remocao tem custo ~2 e o ward {2} da Leyline Immersion exige mais 2: o oponente precisa de >= 4 terrenos (rastreados em `Opp.lands`)
PW_REMOVAL_SHARE = 0.6                      # fracao que mira o planeswalker de maior valor
WIPE_TYPE_WEIGHTS = {"creature": 0.4, "artifact": 0.2, "enchantment": 0.15}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())
GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
ENGINE_PRIORITY = ["Ichormoon Gauntlet", "All Will Be One", "Oath of Teferi", "The Chain Veil", "Chromatic Orrery", "Flux Channeler", "Displacer Kitten", "Sanctum Lurker", "Kiora of Salt and Sand",
                   "Way of the Paradox", "Way of the Mind Sculptor", "Way of the Wildspeaker", "Oath of Nissa", "Onakke Oathkeeper"]


def interaction_chance(state: GameState) -> float:
    board_impact = sum(1 for p in vis(state) if "land" not in p.card.types)
    return min(0.10 + 0.03 * board_impact, 0.75)


def new_opp_creature(p: int, t: int, flying: bool = False, haste: bool = False, trample: bool = False, cmd: bool = False, token: bool = False, cmc: int = 0) -> dict:
    return {"p": p, "t": t, "flying": flying, "trample": trample, "cmd": cmd, "token": token, "sick": not haste, "frozen": 0, "frozen_now": False, "cmc": 0 if token else cmc}


def develop_opponent_board(state: GameState, o: Opp):
    rng = state.interaction_rng
    t = o.turns_taken
    b = o.board
    if o.archetype == "go_wide":
        if t >= 2:
            for _ in range(rng.randint(1, 3)):
                if len(b) >= GO_WIDE_CAP:
                    break
                size = 1 if rng.random() < 0.6 else 2
                b.append(new_opp_creature(size, size, flying=rng.random() < 0.15, haste=rng.random() < 0.10, token=True))
    elif o.archetype == "voltron":
        cmd = next((c for c in b if c["cmd"]), None)
        if cmd is not None:
            grow = rng.randint(1, 3)
            cmd["p"] = min(VOLTRON_CAP, cmd["p"] + grow)
            cmd["t"] = min(VOLTRON_CAP, cmd["t"] + grow)
        elif o.cmd_cooldown > 0:
            o.cmd_cooldown -= 1
        elif t >= 3:
            base = VOLTRON_BASE + o.cmd_bonus
            b.append(new_opp_creature(base, base, flying=rng.random() < 0.35, haste=rng.random() < 0.15, trample=True, cmd=True, cmc=3))
        if t >= 2 and sum(1 for c in b if not c["cmd"]) < 2 and rng.random() < 0.25:
            b.append(new_opp_creature(2, 2, cmc=2))
    else:
        if t >= 3 and len(b) < LOW_CAP and rng.random() < 0.30:
            size = rng.choice((3, 4))
            b.append(new_opp_creature(size, size, flying=rng.random() < 0.25, haste=rng.random() < 0.05, cmc=size))


def opp_turn_start(state: GameState, o: Opp):
    for c in o.board:
        c["sick"] = False
        c["frozen_now"] = c["frozen"] > 0
        if c["frozen"] > 0:
            c["frozen"] -= 1
    develop_opponent_board(state, o)


def can_block(state: GameState, p: Permanent) -> bool:
    return is_creature(p) and not p.tapped and not p.phased


def choose_blocker(state: GameState, c: dict, target_pw: Optional[Permanent], avail: list) -> Optional[Permanent]:
    cands = [b for b in avail if not c["flying"] or has_flying(state, b)]
    if not cands:
        return None

    def outcome(b):
        p, t = power(state, b), toughness(state, b)
        dt = "deathtouch" in b.card.tags
        ds = "double_strike" in b.card.tags
        kills = dt or p * (2 if ds else 1) >= c["t"]
        survives = c["p"] < t or b.ctr.get("indestructible")
        return kills, survives

    def worth(b):
        return (0 if b.is_token else CARD_PRIORITY.get(b.card.name, 30), power(state, b) + toughness(state, b))
    good = [b for b in cands if all(outcome(b))]
    if good:
        return min(good, key=worth)
    if target_pw is None:
        return None
    walls = [b for b in cands if outcome(b)[1]]
    if walls:
        return min(walls, key=worth)
    lethal = c["p"] >= loyalty(target_pw)
    chumps = [b for b in cands if b.is_token or b.card.name in ("Birds of Paradise", "Bloom Tender")]
    if chumps and (lethal or c["p"] >= 2):
        return min(chumps, key=worth)
    trades = [b for b in cands if outcome(b)[0]]
    if trades and lethal:
        return min(trades, key=worth)
    return None


def opponent_combat(state: GameState, o: Opp):
    """Combate do oponente `o` contra mim e meus planeswalkers (so' depois do gate de atencao). Alvo: o planeswalker de maior lealdade ainda nao coberto; senao eu. The Eternal Wanderer: no maximo uma
    criatura a ataca por combate. Onakke Oathkeeper: atacar planeswalker custa {1} por criatura (orcamento = metade dos terrenos dele). Liliana's Talent: criatura que da' dano ao planeswalker encantado morre."""
    if state.turn <= INTERACTION_SETUP_TURNS or not state.attention:
        return
    attackers = [c for c in o.board if not c["sick"] and not c["frozen_now"]]
    if not attackers:
        return
    pw_list = sorted([p for p in pws(state)], key=lambda p: (-loyalty(p), p.uid))
    need = {p.uid: loyalty(p) for p in pw_list}
    wander_taken = [False]

    def pick_pw():
        for p in pw_list:
            if p.card.name == "The Eternal Wanderer" and wander_taken[0]:
                continue
            if need[p.uid] <= 0 and not has_perm(state, "Sanctum Lurker"):
                continue
            if need[p.uid] <= 0:
                continue
            return p
        return None
    assign = []
    for c in sorted(attackers, key=lambda c: -c["p"]):
        tgt = pick_pw()
        if tgt is not None:
            need[tgt.uid] -= c["p"]
            if tgt.card.name == "The Eternal Wanderer":
                wander_taken[0] = True
            assign.append([c, tgt])
        else:
            assign.append([c, None])
    oath = count_named(state, "Onakke Oathkeeper")
    if oath:
        budget = int(TAX_BUDGET_FRACTION * o.lands)
        paid = []
        for c, tgt in sorted(assign, key=lambda a: -a[0]["p"]):
            if tgt is None:
                paid.append([c, None])
            elif oath <= budget:
                budget -= oath
                paid.append([c, tgt])
            else:
                paid.append([c, None])           # nao pagou: nao pode atacar o planeswalker; ataca a mim
                state.m["attackers_stopped_by_tax"] += 1
        assign = paid
    if not assign:
        return
    state.m["opp_attackers_total"] += len(assign)
    state.m["opp_attacks_on_pw"] += sum(1 for _, t in assign if t is not None)
    # bloqueio: criaturas minhas desviradas
    avail = [b for b in creatures(state) if can_block(state, b)]
    max_blocks = 1 if (has_perm(state, "The Eternal Wanderer") and False) else len(avail)
    blocks = {}
    for c, tgt in sorted(assign, key=lambda a: (a[1] is None, -a[0]["p"])):
        if len(blocks) >= max_blocks:
            break
        b = choose_blocker(state, c, tgt, avail)
        if b is not None:
            blocks[id(c)] = b
            avail.remove(b)
    pw_damage = collections.defaultdict(int)
    face = 0
    dead_attackers, dead_blockers = [], []
    for c, tgt in assign:
        b = blocks.get(id(c))
        if b is None:
            if tgt is None:
                face += c["p"]
            else:
                pw_damage[tgt.uid] += c["p"]
            continue
        state.m["blocks_total"] += 1
        bp, bt = power(state, b), toughness(state, b)
        ds = "double_strike" in b.card.tags
        dt = "deathtouch" in b.card.tags
        attacker_dead = ds and (bp >= c["t"] or dt)
        if b.uid in state.tamiyo_marked and bp > 0:
            n_steps = 2 if ds and not attacker_dead else 1          # Tamiyo +1: 'whenever either of those creatures deals combat damage, you draw a card' (duplo se da' dano nos 2 passos)
            draw_cards(state, n_steps, "tamiyo_marked_block")
            state.m["tamiyo_block_draws"] += n_steps
        if not attacker_dead:
            if c["p"] >= bt and not b.ctr.get("indestructible"):
                dead_blockers.append(b)
            if c["trample"]:
                excess = max(0, c["p"] - bt)
                if excess:
                    if tgt is None:
                        face += excess
                    else:
                        pw_damage[tgt.uid] += excess
            if dt or bp * (2 if ds else 1) >= c["t"]:
                attacker_dead = True
        if attacker_dead:
            dead_attackers.append(c)
    # resposta: um planeswalker ia morrer em combate -> Ripples of Potential (proliferate + fase fora)
    if any(d >= loyalty(find_perm(state, uid)) for uid, d in pw_damage.items() if find_perm(state, uid) is not None):
        try_protective_ripples(state)
        pw_damage = {uid: d for uid, d in pw_damage.items() if (find_perm(state, uid) is not None and not find_perm(state, uid).phased)}
    lose_life(state, face, "opponent_attack")
    state.m["face_combat_damage_total"] += face
    for uid, d in pw_damage.items():
        p = find_perm(state, uid)
        if p is None:
            continue
        state.m["pw_combat_damage_total"] += min(d, loyalty(p))
        remove_loyalty(state, p, d)
        for a in state.battlefield:
            if a.card.name == "Liliana's Talent" and a.attached_to == p.uid and not a.phased:
                state.m["lilianas_talent_kills"] += sum(1 for c, t in assign if t is p)
                for c, t in assign:
                    if t is p and c not in dead_attackers:
                        dead_attackers.append(c)
    for c in dead_attackers:
        opp_remove_creature(state, o, c, "combat")
    for b in dead_blockers:
        if b in state.battlefield:
            remove_permanent(state, b, "dies")
            state.m["our_blockers_lost"] += 1
    n_before = len(pws(state))
    sba(state)
    state.m["pw_combat_deaths"] += max(0, n_before - len(pws(state)))


def try_protective_ripples(state: GameState) -> bool:
    """Ripples of Potential em resposta (instantanea): proliferate e os planeswalkers que ganharam contador saem de fase (nao recebem o dano)."""
    if "Ripples of Potential" not in state.hand or not can_cast_name(state, "Ripples of Potential"):
        return False
    cast_card(state, "Ripples of Potential")
    state.m["ripples_protections"] += 1
    return True


def try_smart_opponent_removal(state: GameState, o: Optional[Opp] = None) -> Optional[str]:
    if state.turn <= INTERACTION_SETUP_TURNS:
        return None
    pw_cands = [p for p in pws(state) if p.card.name != "Jace Token"] or [p for p in pws(state)]
    tam = perms_named(state, "Tam, the Possibility")
    engines = [p for n in ENGINE_PRIORITY for p in perms_named(state, n)]
    if not pw_cands and not tam and not engines:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    r = state.interaction_rng.random()
    if tam and r < COMMANDER_REMOVAL_SHARE:
        target = tam[0]
    elif pw_cands and r < COMMANDER_REMOVAL_SHARE + PW_REMOVAL_SHARE:
        target = max(pw_cands, key=lambda p: (CARD_PRIORITY.get(p.card.name, 20) + loyalty(p) * 1.5, -p.uid))
    elif engines:
        target = engines[0]
    elif pw_cands:
        target = max(pw_cands, key=lambda p: (CARD_PRIORITY.get(p.card.name, 20) + loyalty(p) * 1.5, -p.uid))
    else:
        target = tam[0]
    # ward {2} (Leyline Immersion): o oponente que mira o criatura encantada tem que pagar {2} a mais
    if o is not None and any(a.card.name == "Leyline Immersion" and a.attached_to == target.uid and not a.phased for a in state.battlefield):
        if o.lands < WARD_MIN_LANDS:
            state.m["ward_blocked_removals"] += 1
            return None
        state.m["ward_paid_removals"] += 1
    # protecao
    if is_legendary(target) and is_creature(target):
        for pz in perms_named(state, "Plaza of Heroes"):
            if not pz.tapped and can_pay(state, 3, (), CTX_ABILITY):
                # {3},{T}, exile: hexproof e indestrutivel
                pay_mana(state, 3, (), CTX_ABILITY)
                state.battlefield.remove(pz)
                state.exile.append("Plaza of Heroes")
                state.m["plaza_protections"] += 1
                return None
    if state.dihada_shield == target.uid:
        state.m["dihada_protections"] += 1
        return None
    if "Ripples of Potential" in state.hand and is_pw(target) and can_cast_name(state, "Ripples of Potential"):
        cast_card(state, "Ripples of Potential")
        if target.phased:
            state.m["ripples_protections"] += 1
            return None
    remove_permanent(state, target, "opp_removal")
    state.m["smart_removals"] += 1
    state.m["opp_crimes_total"] += 1
    for _ in range(count_named(state, "Patrolling Peacemaker")):
        proliferate(state, "peacemaker")
    return target.card.name


def try_smart_opponent_discard(state: GameState) -> Optional[str]:
    if state.turn <= INTERACTION_SETUP_TURNS or not state.hand:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    c = state.interaction_rng.choice(state.hand)
    state.hand.remove(c)
    state.graveyard.append(c)
    state.m["smart_discards"] += 1
    return c


def try_smart_opponent_wipe(state: GameState) -> Optional[list]:
    if state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    cands = {"creature": [p for p in vis(state) if is_creature(p)],
             "artifact": [p for p in vis(state) if is_artifact(p) and not is_creature(p)],
             "enchantment": [p for p in vis(state) if "enchantment" in p.card.types]}
    avail = [t for t in ("creature", "artifact", "enchantment") if cands[t]]
    if not avail:
        return None
    wt = state.interaction_rng.choices(avail, weights=[WIPE_TYPE_WEIGHTS[t] for t in avail])[0]
    victims = list(cands[wt])
    # Ripples de resposta: protege so' o que ganha contador (criaturas com +1/+1, tempo)
    if "Ripples of Potential" in state.hand and can_cast_name(state, "Ripples of Potential") and wt == "creature":
        cast_card(state, "Ripples of Potential")
        for p in list(vis(state)):
            if p.ctr.get("p1p1", 0) > 0 and is_creature(p):
                phase_out(state, p)
        state.m["ripples_protections"] += 1
        victims = [p for p in victims if not p.phased]
    names = [p.card.name for p in victims]
    for p in victims:
        if p in state.battlefield and not p.ctr.get("indestructible"):
            remove_permanent(state, p, "wipe")
    key = {"creature": "smart_wipes", "artifact": "smart_artifact_wipes", "enchantment": "smart_enchantment_wipes"}[wt]
    state.m[key] += 1
    if wt == "creature":
        state.wiped_this_round = True
    sba(state)
    return names


def try_smart_opponent_graveyard_wipe(state: GameState) -> Optional[list]:
    if state.turn <= INTERACTION_SETUP_TURNS or state.m["graveyard_wipe_used"] or not state.graveyard:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_WIPE_CHANCE_FACTOR:
        return None
    ex = list(state.graveyard)
    state.graveyard.clear()
    state.exile.extend(ex)
    state.m["graveyard_wipe_used"] = 1
    state.m["smart_graveyard_hate"] += 1
    return ex


def try_smart_opponent_turn(state: GameState, o: Opp):
    state.attention = state.turn <= INTERACTION_SETUP_TURNS or state.interaction_rng.random() < OPPONENT_ATTENTION_CHANCE
    if not state.attention:
        return
    try_smart_opponent_wipe(state)
    try_smart_opponent_graveyard_wipe(state)
    try_smart_opponent_removal(state, o)
    try_smart_opponent_discard(state)


# =========================================================
# PARTIDA
# =========================================================

def new_state(seed: int) -> GameState:
    rnd = random.Random(seed)
    st = GameState(rng=rnd)
    st.proxy_rng = random.Random(seed * 1_000_033 + 17)
    st.library = current_library()
    rnd.shuffle(st.library)
    st.opps = [make_opp(seed, i) for i in range(1, NUM_OPPONENTS + 1)]
    st.opp_rngs = [None] + [random.Random(seed * 1_000_037 + i * 104729 + 7) for i in range(1, NUM_OPPONENTS + 1)]
    st.life = 40
    st.life_min = 40
    mulligan(st)
    return st


def setup_resilience(state: GameState, seed: int):
    state.resilience = True
    state.interaction_rng = random.Random(seed + 999_999)
    for o in state.opps:
        o.archetype = OPP_ARCHETYPES[(seed + o.idx) % 3] if False else state.interaction_rng.choice(OPP_ARCHETYPES)


def finalize(state: GameState):
    """Achata as metricas em campos numericos de topo (o harness de A/B le TODOS os campos numericos)."""
    t = state.table_cleared_turn
    for n in (6, 7, 8, 9, 10, 12):
        setattr(state, f"cleared_T{n}", 1 if (t is not None and t <= n) else 0)
    f = state.first_opp_elim_turn
    state.first_elim_T6 = 1 if (f is not None and f <= 6) else 0
    state.first_elim_T8 = 1 if (f is not None and f <= 8) else 0
    state.self_lost = 1 if state.decked else 0
    d = state.died_turn
    for n in (6, 8, 10, 12):
        setattr(state, f"died_T{n}", 1 if (d is not None and d <= n) else 0)
    state.died_any = 1 if state.died_life else 0
    state.commander_cast_turn_v = state.commander_cast_turn
    for T in (3, 4, 5, 6, 8, 10):
        bt = state.by_turn.get(T) or state.by_turn.get(max(state.by_turn)) if state.by_turn else {}
        setattr(state, f"pws_T{T}", (state.by_turn.get(T, {}) or {}).get("pws", 0))
        setattr(state, f"loyalty_T{T}", (state.by_turn.get(T, {}) or {}).get("loyalty", 0))
        setattr(state, f"mana_T{T}", (state.by_turn.get(T, {}) or {}).get("mana", 0))
        setattr(state, f"lands_T{T}", (state.by_turn.get(T, {}) or {}).get("lands", 0))
        setattr(state, f"pw_types_T{T}", (state.by_turn.get(T, {}) or {}).get("pw_types", 0))
        setattr(state, f"creatures_T{T}", (state.by_turn.get(T, {}) or {}).get("creatures", 0))
        setattr(state, f"hand_T{T}", (state.by_turn.get(T, {}) or {}).get("hand", 0))
    for k, v in list(state.m.items()):
        if isinstance(k, str) and not k.startswith("_"):
            setattr(state, "m_" + k, v)
    for k, v in state.first_turn.items():
        setattr(state, k + "_turn", v)
    state.mulligans_v = state.mulligans
    state.life_final = state.life
    state.game_turns = state.turn


def play_rounds(state: GameState, turns: int):
    for _ in range(turns):
        play_turn(state)
        while state.extra_turn_pending and not state.game_over:
            state.extra_turn_pending = False
            state.m["extra_turns_played"] += 1
            play_turn(state)
        if state.game_over:
            break
        state.wiped_this_round = False
        for o in list(state.opps):
            if o.eliminated:
                continue
            opponent_turn(state, o)
            if state.game_over:
                break
            if state.resilience:
                try_smart_opponent_turn(state, o)
                if state.game_over:
                    break
        if state.game_over:
            break


def simulate_one(seed: int, turns: int = BASE_TURNS) -> GameState:
    state = new_state(seed)
    play_rounds(state, turns)
    finalize(state)
    return state


def simulate_one_with_interaction(seed: int, turns: int = BASE_TURNS) -> GameState:
    state = new_state(seed)
    setup_resilience(state, seed)
    play_rounds(state, turns)
    finalize(state)
    return state

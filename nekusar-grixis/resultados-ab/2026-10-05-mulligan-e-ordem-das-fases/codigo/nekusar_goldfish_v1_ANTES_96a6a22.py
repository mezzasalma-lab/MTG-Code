"""
Goldfish simulator — Nekusar, the Mindrazer, "V9 Wheel Breach Storm" (Grixis, U/B/R)

Construido do zero em 2026-08-23. Passo 0 (regra de
`references/goldfish-sim-card-rules.md`): a auditoria (`auditoria.md`,
secoes 5 e 6) ja fez a varredura mecanica completa no oraculo real de
todas as 99 cartas — reaproveitada aqui integralmente, nao refeita do
zero. 9 payoffs de dano/perda-de-vida-por-compra e 15 fontes de
wheel/draw-em-massa catalogados.

Achado real 2026-08-28 (auditoria de checklist obrigatoria de mecanica,
`references/goldfish-sim-card-rules.md`): a frase acima ("todos com
efeito real implementado abaixo") estava ERRADA — 11 das ~15 fontes de
wheel/draw catalogadas tinham só a tag, sem nenhum gatilho real
(Waste Not, Liliana's Caress, Jace's Archivist, Magus of the Wheel,
Faerie Mastermind, Resonating Lute, Sensei's Divining Top, Teferi's
Puzzle Box, Mikokoro, Geier Reach Sanitarium, Cephalid Coliseum).
Corrigido nesta rodada - ver `goldfish-log.md`.

Auditoria oraculo-por-oraculo completa 2026-09-13 (releitura linha-a-
linha contra o oraculo real via Scryfall de todas as 92 cartas +
comandante - ver `checklist-oraculo.md`): 11 gaps reais adicionais, a
maioria de propagacao (um efeito correto numa funcao, nunca propagado
pras outras funcoes que geram o MESMO evento real) - Sheoldred
("whenever you draw, gain 2 life") so contava em draw_step(), nao em
draw_cards() (o VERDADEIRO ponto central de toda compra); Mindcrank/
Bloodchief Ascension so contavam dentro de wheel_event(), nao em
proxy_drain() (o VERDADEIRO ponto central de "oponente perde vida").
Tambem: The One Ring 100% inerte (a habilidade principal, {T}: burden+
draw, nunca implementada); Underworld Breach restrito a instant/sorcery
quando o oraculo real cobre qualquer nao-terreno; Orcish Bowmasters ETB
overcounted 3x; 4 gatilhos de discard falso-positivos (Winds of Change/
Echo of Eons sao shuffle, nao discard); 3 terrenos-choque e 2 terrenos
tapped nunca modelados; Imperial Seal/Vampiric Tutor sem a perda de 2
vida; Lightning Greaves 100% inerte. Ambos corrigidos - ver
`goldfish-log.md` pra tabela antes/depois.

Mecanica central: o comandante ("Whenever an opponent draws a card,
Nekusar deals 1 damage to that player" + "At the beginning of each
player's draw step, that player draws an additional card") empilha com
8 outros payoffs reais (Orcish Bowmasters, Sheoldred, Underworld
Dreams, Spiteful Visions, Phyrexian Tyranny, Razorkin Needlehead,
Scrawling Crawler, Liliana's Caress-p/descarte) — cada evento de wheel
(Wheel of Fortune, Windfall, etc.) multiplica o dano por quantos desses
estao em campo.

Sem oponente real num goldfish solo: os "3 oponentes" e suas compras
sao um PROXY agregado, documentado explicitamente — nunca finjo vida
real de oponente nem "matei a mesa". `NUM_OPPONENTS = 3` e uma premissa
declarada (mesa de 4), nao um dado real. `drain_damage_total` e
`proxy_kill_damage_total` sao contadores agregados de dano teorico
gerado pelos payoffs, nunca subtraidos de uma vida real de ninguem.

Combo real de storm/recursao (auditoria secao 6, nao um combo de 2
pecas isolado — cadeia que pode explodir quando as pecas se alinham):
**Underworld Breach** da escape (custo = mana cost + exilar 3 outras
cartas do cemiterio) a toda carta nao-terreno no cemiterio, sacrificada
no fim do turno. Combinado com rituais baratos (Dark Ritual, Cabal
Ritual) e o proprio cemiterio cheio de wheels descartados, isso pode
recastar varios wheels/rituais no mesmo turno antes do cemiterio
esgotar (a exigencia de exilar 3 cartas a cada recast e AUTO-LIMITANTE
— nao e um loop infinito, e um loop real mas finito que termina quando
o cemiterio fica pequeno demais). Implementado como um loop real que
respeita esse custo, nao decorativo.

Simplificacoes documentadas (nao inventadas — omissoes explicitas):
- Sem oponente real: todo dano/perda-de-vida de oponente e PROXY
  agregado (`NUM_OPPONENTS=3`), nunca vida real rastreada de ninguem.
  Contramagicas/protecao (Force of Will, Mana Drain, Counterspell,
  Arcane Denial, Swan Song, Flusterstorm, Pact of Negation, Mindbreak
  Trap, An Offer You Can't Refuse, Deflecting Swat) sao conjuradas
  quando ha mana sobrando (mesma convencao dos outros simuladores
  desta biblioteca), sem efeito de combate real modelado.
- Fetchlands (Arid Mesa, Bloodstained Mire, Flooded Strand, Marsh
  Flats, Misty Rainforest, Polluted Delta, Scalding Tarn, Verdant
  Catacombs, Wooded Foothills): tratadas como terreno generico normal
  no modelo de mana total (nao pip a pip); custo de 1 vida aplicado
  real, thinning de biblioteca NAO modelado (simplificacao disclosed).
- Brain Freeze: `storm_count` real rastreado (spells conjuradas no
  turno), mas o efeito (mill 3 x copias) e só registrado como
  `mill_proxy_total` — nao existe biblioteca de oponente real pra
  milhar de verdade.
- Mindcrank: mila voce mesmo (nao ha oponente real) proporcional ao
  `proxy` de dano gerado — registrado como metrica separada, nao
  aplicado a biblioteca real de ninguem.
- Wheel of Misfortune: modelado como um wheel "cheio" padrao (assume
  premissa de nao ser quem escolheu o menor numero, cenario mais
  comum); a metade de dano por numero escolhido nao e modelada
  numericamente (depende de escolha simultanea de oponente real).
- Combate: nenhum dano de combate real modelado (deck nao e de
  criaturas de ataque, e um deck de dano por gatilho de compra).
"""

import json
import random
import re
import signal
import statistics
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Card database
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Card:
    name: str
    mv: int
    ctype: str
    tags: frozenset = field(default_factory=frozenset)


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=()):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags))


COMMANDER = "Nekusar, the Mindrazer"
add(COMMANDER, 5, "creature", {"commander", "payoff"})

NUM_OPPONENTS = 3  # premissa declarada (mesa de 4), nunca vida real rastreada

# --- Terrenos (36) ------------------------------------------------------------
FETCH_NAMES = {"Arid Mesa", "Bloodstained Mire", "Flooded Strand", "Marsh Flats",
                "Misty Rainforest", "Polluted Delta", "Scalding Tarn", "Verdant Catacombs",
                "Wooded Foothills"}
for n in FETCH_NAMES:
    add(n, 0, "land", {"fetch"})
# Blood Crypt/Steam Vents/Watery Grave (achado real 2026-09-13): oraculo
# real *"As this land enters, you may pay 2 life. If you don't, it enters
# tapped."* - nunca modelado, tratadas como terreno generico gratis e
# sempre destapado. Premissa documentada (consistente com a mesma decisao
# ja tomada pras fetches, que tambem pagam vida por eficiencia): sempre
# pagar os 2 de vida, ja que este e' um deck de storm/combo que quer mana
# disponivel no MESMO turno - tag "shock".
add("Blood Crypt", 0, "land", {"shock"})
add("Badlands", 0, "land", set())
# Cascade Bluffs: real oraculo NAO entra tapped ("{T}: Add {C}. {1},{T}: Add
# {U/R}{U/R}.") - achado real 2026-08-28 (auditoria de checklist): tag
# "etb_tapped_filter" era um mislabel (nunca lida em lugar nenhum de
# qualquer forma, mas o nome sugeria um efeito que a carta real nao tem).
add("Cascade Bluffs", 0, "land", set())
add("Cephalid Coliseum", 0, "land", {"threshold_wheel"})
add("City of Brass", 0, "land", set())
add("Command Tower", 0, "land", set())
add("Emergence Zone", 0, "land", {"flash_enabler"})
add("Exotic Orchard", 0, "land", set())
add("Geier Reach Sanitarium", 0, "land", {"wheel_source_small"})
add("Gemstone Caverns", 0, "land", set())
add("Mikokoro, Center of the Sea", 0, "land", {"wheel_source_small"})
# Mistrise Village (achado real 2026-09-13): oraculo real *"This land
# enters tapped unless you control a Mountain or a Forest."* Sem Forest
# nesta lista (Grixis), so a metade "Mountain" importa - checado
# dinamicamente contra MOUNTAIN_TYPE_LANDS no momento do land drop
# (`cast_card`), nao um tag estatico (unico caso condicional do arquivo).
add("Mistrise Village", 0, "land", {"etb_tapped_conditional"})
add("Otawara, Soaring City", 0, "land", set())
# Steam Vents: mesmo "pay 2 life or enters tapped" do Blood Crypt/Watery Grave.
add("Steam Vents", 0, "land", {"shock"})
add("Underground Sea", 0, "land", set())
# Undercity Sewers: real oraculo *"This land enters tapped. When this land
# enters, surveil 1."* - achado real 2026-08-28 (auditoria de checklist):
# tinha uma tag ("etb_tapped_filter") mal-rotulada e nunca lida - nem o
# "enters tapped" nem o surveil eram modelados.
add("Undercity Sewers", 0, "land", {"etb_tapped", "surveil_on_etb"})
add("Volcanic Island", 0, "land", set())
# Watery Grave: mesmo "pay 2 life or enters tapped" do Blood Crypt/Steam Vents.
add("Watery Grave", 0, "land", {"shock"})
# Xander's Lounge (achado real 2026-09-13): oraculo real *"This land
# enters tapped."* (incondicional, diferente de Undercity Sewers que TAMBEM
# faz surveil 1 - Xander's Lounge nao) + Cycling {3} (modo alternativo
# descartavel, nao modelado - mesma classe de simplificacao ja aplicada a
# outros modos discricionarios do arquivo, ex: Wheel of Misfortune).
# Sem tag nenhuma antes = tratada como terreno instantaneo destapado, o
# que superestimava mana disponivel no turno em que entra.
add("Xander's Lounge", 0, "land", {"etb_tapped"})
add("Island", 0, "land", set())
add("Mountain", 0, "land", set())
add("Swamp", 0, "land", set())

# --- Comandante-adjacente / criaturas payoff (9) ------------------------------
add("Dauthi Voidwalker", 2, "creature", set())
add("Faerie Mastermind", 2, "creature", {"opponent_dependent"})
add("Jace's Archivist", 3, "creature", {"wheel_repeatable"})
add("Magus of the Wheel", 3, "creature", {"wheel_sac"})
add("Orcish Bowmasters", 2, "creature", {"payoff"})
add("Razorkin Needlehead", 2, "creature", {"payoff"})
add("Scrawling Crawler", 3, "artifact_creature", {"payoff", "wheel_upkeep"})
add("Sheoldred, the Apocalypse", 4, "creature", {"payoff", "lifegain_on_draw"})
add("Spark Double", 4, "creature", {"copy"})

# --- Wheels (7) ----------------------------------------------------------------
add("Echo of Eons", 6, "sorcery", {"wheel_full"})
add("Teferi's Puzzle Box", 4, "artifact", {"wheel_passive"})
add("Wheel and Deal", 4, "instant", {"wheel_full"})
add("Wheel of Fortune", 3, "sorcery", {"wheel_full"})
add("Wheel of Misfortune", 3, "sorcery", {"wheel_full"})
add("Windfall", 3, "sorcery", {"wheel_full"})
add("Winds of Change", 1, "sorcery", {"wheel_full"})

# --- Payoffs (6) ----------------------------------------------------------------
add("Bloodchief Ascension", 1, "enchantment", {"quest_drain"})
add("Liliana's Caress", 2, "enchantment", {"discard_payoff"})
add("Phyrexian Tyranny", 3, "enchantment", {"payoff"})
add("Spiteful Visions", 4, "enchantment", {"payoff", "wheel_passive"})
add("Underworld Dreams", 3, "enchantment", {"payoff"})
add("Waste Not", 2, "enchantment", {"discard_payoff"})

# --- Combo e recursao (7) -------------------------------------------------------
add("Animate Dead", 2, "enchantment", {"reanimate"})
add("Brain Freeze", 2, "instant", {"storm_mill"})
add("Cabal Ritual", 2, "instant", {"ritual"})
add("Dark Ritual", 1, "instant", {"ritual"})  # tambem listado em Artefatos e Outros, mesma carta
add("Flashback", 1, "instant", {"interaction"})
add("Past in Flames", 4, "sorcery", {"breach_engine"})
add("Reanimate", 1, "sorcery", {"reanimate"})
add("Underworld Breach", 2, "enchantment", {"breach_engine"})

# --- Tutores (5) -----------------------------------------------------------------
add("Beseech the Mirror", 4, "sorcery", {"tutor"})
add("Demonic Tutor", 2, "sorcery", {"tutor"})
add("Imperial Seal", 2, "sorcery", {"tutor_top"})
add("Solve the Equation", 3, "sorcery", {"tutor_instant_sorcery"})
add("Vampiric Tutor", 1, "instant", {"tutor_top"})

# --- Protecao e remocao (14) -------------------------------------------------------
add("An Offer You Can't Refuse", 2, "instant", {"interaction"})
add("Arcane Denial", 2, "instant", {"interaction"})
add("Counterspell", 2, "instant", {"interaction"})
add("Cyclonic Rift", 2, "instant", {"interaction"})
add("Deadly Rollick", 2, "instant", {"interaction"})
add("Deflecting Swat", 3, "instant", {"interaction", "free_with_commander"})
add("Feed the Swarm", 2, "instant", {"interaction"})
add("Flusterstorm", 1, "instant", {"interaction"})
add("Force of Will", 5, "instant", {"interaction"})
add("Mana Drain", 2, "instant", {"interaction"})
add("Mindbreak Trap", 3, "instant", {"interaction"})
add("Pact of Negation", 3, "instant", {"interaction"})
add("Return the Favor", 3, "instant", {"interaction"})
add("Swan Song", 1, "instant", {"interaction"})

# --- Artefatos e outros (15) -------------------------------------------------------
add("Arcane Signet", 2, "artifact", {"rock1"})
add("Cursed Totem", 2, "artifact", set())
add("Defense Grid", 2, "artifact", set())
add("Hexing Squelcher", 2, "creature", set())
add("Lightning Greaves", 2, "artifact", set())
add("Mindcrank", 2, "artifact", {"mill_engine"})
add("Mox Opal", 0, "artifact", {"rock_conditional"})
add("Propaganda", 3, "enchantment", set())
add("Resonating Lute", 4, "artifact", {"draw_conditional"})
add("Sensei's Divining Top", 1, "artifact", {"card_selection"})
add("Sol Ring", 1, "artifact", {"rock2"})
add("Talisman of Creativity", 2, "artifact", {"rock1"})
add("Talisman of Dominance", 2, "artifact", {"rock1"})
add("The One Ring", 4, "artifact", {"the_one_ring"})

ARTIFACT_ISH = {"artifact", "artifact_creature"}
CREATURE_ISH = {"creature", "artifact_creature"}
LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}

# Mistrise Village ("...unless you control a Mountain or a Forest" - sem
# Forest nesta decklist Grixis): terrenos reais com o tipo Mountain na
# type line (checado no Scryfall, nao inventado).
MOUNTAIN_TYPE_LANDS = {"Badlands", "Blood Crypt", "Steam Vents", "Volcanic Island",
                        "Xander's Lounge", "Mountain"}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype in ARTIFACT_ISH


def is_enchantment_card(name: str) -> bool:
    return CARD_DB[name].ctype == "enchantment"


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------

@dataclass
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    library: list = field(default_factory=list)
    mulligans: int = 0

    lands_played_this_turn: int = 0
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0
    spells_cast_this_turn: int = 0
    underworld_breach_active: bool = False
    the_one_ring_burden: int = 0
    life: int = 40
    tapped_lands_this_turn: set = field(default_factory=set)
    spark_double_copy_target: Optional[str] = None

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    creature_cast_turn: dict = field(default_factory=dict)

    # metrics -------------------------------------------------------------
    wheel_events_total: int = 0
    full_wheels_total: int = 0
    proxy_damage_total: int = 0
    proxy_lifegain_total: int = 0
    cards_drawn_extra: int = 0
    tutors_used_total: int = 0
    storm_count_max: int = 0
    breach_recasts_total: int = 0
    breach_loops_total: int = 0
    mill_proxy_total: int = 0
    reanimator_targets_total: int = 0
    library_emptied: bool = False
    faerie_mastermind_draws_total: int = 0
    sensei_top_draws_total: int = 0
    small_wheel_lands_used_total: int = 0
    discard_payoff_life_loss_total: int = 0
    waste_not_draws_total: int = 0
    puzzle_box_events_total: int = 0
    cephalid_coliseum_used: bool = False
    zombie_tokens_total: int = 0
    self_damage_total: int = 0
    flashback_card_recasts_total: int = 0
    surveil_mills_total: int = 0
    rituals_cast_total: int = 0
    interaction_spells_cast_total: int = 0

    # Modo de resiliencia (interacao de oponente) — 2026-09-21, porte do
    # Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/Toph/Prismatic
    # Bridge/Maralen/Rat King Verminister/Vihaan. `interaction_rng`
    # None = modo padrao, totalmente inerte (bit-identico ao motor sem
    # estas categorias).
    interaction_rng: Optional[random.Random] = None
    wiped_this_round: bool = False
    graveyard_wipe_used: bool = False

    smart_removals_total: int = 0
    smart_removal_log: list = field(default_factory=list)
    smart_attacks_taken_total: int = 0
    smart_attack_log: list = field(default_factory=list)
    smart_discards_total: int = 0
    smart_discard_log: list = field(default_factory=list)
    smart_wipes_total: int = 0
    smart_wipe_log: list = field(default_factory=list)
    smart_artifact_wipes_total: int = 0
    smart_artifact_wipe_log: list = field(default_factory=list)
    smart_enchantment_wipes_total: int = 0
    smart_enchantment_wipe_log: list = field(default_factory=list)
    smart_counters_total: int = 0
    smart_counter_log: list = field(default_factory=list)
    smart_graveyard_wipes_total: int = 0
    smart_graveyard_wipe_log: list = field(default_factory=list)
    smart_graveyard_snipes_total: int = 0
    smart_graveyard_snipe_log: list = field(default_factory=list)


def _copies_of(state: GameState, name: str) -> int:
    """Conta quantas 'copias' de uma criatura-payoff estao valendo em campo
    - normalmente 0 ou 1 (decklist singleton de Commander), mas pode virar
    2 se Spark Double copiou essa criatura (achado real 2026-08-28: Spark
    Double estava 100% inerte, tag "copy" nunca despachada - copiar um dos
    proprios payoffs de dano-por-compra e' o efeito de maior valor
    esperado do deck pra essa carta, ja que empilha o motor central)."""
    base = 1 if name in state.battlefield else 0
    copy = 1 if state.spark_double_copy_target == name else 0
    return base + copy


def _commander_copies(state: GameState) -> int:
    n = 1 if state.commander_in_play else 0
    if state.spark_double_copy_target == COMMANDER:
        n += 1
    return n


def remove_permanent(state: GameState, name: str, source: str = "opponent"):
    """Ponto central de remocao de permanente NOMEADO do campo por acao de
    OPONENTE (wipe/remocao do modo de resiliencia, 2026-09-21 -- porte do
    Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/Toph/Prismatic
    Bridge/Maralen/Rat King Verminister/Vihaan, ja' incorporando desde o
    inicio a correcao de CR 903.9a validada nesta sessao).

    Comandante: CR 903.9a (cemiterio/exilio, o caso de MORTE) e' ACAO
    BASEADA EM ESTADO (CR 704), NAO substituicao -- ver
    `rules-cache/comprehensive-rules.txt` linhas 6888-6896, Regra 18 de
    `references/user-standing-rules.md`. Nekusar vai pro cemiterio DE
    VERDADE primeiro (CR 700.4, 'dies'), so' DEPOIS e' removido de la'
    pra representar a escolha do dono de move-lo pra zona de comando.
    Sem efeito NUMERICO aqui -- **0 cartas 'creature dies' neste deck**
    (grep confirmado: e' um deck de dano-por-compra/wheel/storm, sem
    NENHUM motor de aristocrata/sacrificio) -- mas corrigido por
    consistencia estrutural desde a 1a linha, nao como retrofit.

    Spark Double: se ELA MESMA for removida, `state.spark_double_copy_
    target` e' limpo -- a copia deixa de existir com ela (CR 706.2,
    'copiar' e' um efeito de caracteristica aplicado 1x na entrada, nao
    um link continuo com o original). Remover a criatura ORIGINAL que
    ela copiou nao afeta a copia -- ela continua sendo uma copia
    daquela criatura pro resto do jogo, mesmo que o original ja' tenha
    saido de campo antes."""
    if name not in state.battlefield:
        return
    state.battlefield.remove(name)
    state.creature_cast_turn.pop(name, None)
    state.graveyard.append(name)
    if name == "Spark Double":
        state.spark_double_copy_target = None
    if name == COMMANDER:
        if name in state.graveyard:
            state.graveyard.remove(name)
        state.commander_in_play = False


def draw_cards(state: GameState, n: int):
    actually_drawn = 0
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
            actually_drawn += 1
        else:
            state.library_emptied = True
    # achado real 2026-09-13: usava `n` (pedido) em vez de `actually_drawn`
    # (efetivo) pro dano/vida proprios - so importa se a biblioteca esgota
    # no meio de uma compra (raro com 99 cartas/8 turnos, mas real).
    dmg = self_damage_per_draw(state) * actually_drawn
    if dmg:
        state.life -= dmg
        state.self_damage_total += dmg
    # Sheoldred, the Apocalypse: "Whenever YOU draw a card, you gain 2
    # life." Achado real 2026-09-13: so' estava cravada dentro de
    # `draw_step()` (a compra normal do meu turno) - toda compra vinda de
    # QUALQUER outro motor (wheels, Sensei's Top, Waste Not, Resonating
    # Lute, Cephalid Coliseum, tutores nao) NUNCA disparava o ganho de
    # vida, apesar de `draw_cards()` ja ser o unico ponto de entrada real
    # de toda compra do arquivo (mesmo padrao usado pro autodano acima).
    # Centralizado aqui, removido o calculo duplicado de draw_step().
    sheoldred_copies = _copies_of(state, "Sheoldred, the Apocalypse")
    if sheoldred_copies and actually_drawn:
        gain = 2 * actually_drawn * sheoldred_copies
        state.life += gain
        state.proxy_lifegain_total += gain


def self_damage_per_draw(state: GameState) -> int:
    """Achado real 2026-08-28 (auditoria de checklist categoria 9): Spiteful
    Visions ("Whenever A PLAYER draws a card...") e Phyrexian Tyranny
    ("Whenever A PLAYER draws a card, that player loses 2 life unless they
    pay {2}") dizem "a player", NAO "an opponent" como Nekusar/Underworld
    Dreams/Razorkin Needlehead/Scrawling Crawler - entao tambem me acertam
    quando EU compro. Nunca era rastreado, apesar do deck comprar em volume
    extremo (ate 7+ cartas por wheel). Premissa documentada pro Phyrexian
    Tyranny: nao pago o {2} pra evitar (mesma decisao ja assumida pro lado
    do oponente - pagar {2} POR CARTA durante um wheel de 7 compras seria
    14 mana, inviavel na pratica)."""
    total = 0
    if "Spiteful Visions" in state.battlefield:
        total += 1
    if "Phyrexian Tyranny" in state.battlefield:
        total += 2
    return total


def proxy_drain(state: GameState, n: int):
    """Dano/perda-de-vida agregada dos PROXY opponents — nunca vida real de
    ninguem, so um contador de output teorico dos payoffs.

    Achado real 2026-09-13: Mindcrank ("Whenever an opponent LOSES LIFE,
    mill that many") e Bloodchief Ascension (aproximacao ja documentada:
    todo evento de dano real conta como "oponente perdeu 2+" o suficiente
    vezes) so estavam checados dentro de `wheel_event()`, usando o
    `total_dmg` local em vez de passar por esta funcao - que e' o
    VERDADEIRO ponto central de "oponente perde vida" no arquivo inteiro
    (chamado tambem por draw_step, upkeep_step/Scrawling Crawler,
    try_teferis_puzzle_box e o ETB do Orcish Bowmasters). Esses 4 outros
    pontos reais nunca disparavam Mindcrank nem Bloodchief Ascension -
    mesma classe de bug de "gatilho cravado num so' dos varios pontos
    reais" ja vista no Edgar Markov (cascata de sacrificio). Centralizado
    aqui; a checagem duplicada dentro de wheel_event foi removida."""
    state.proxy_damage_total += n
    if n <= 0:
        return
    if "Mindcrank" in state.battlefield:
        state.mill_proxy_total += n
    if "Bloodchief Ascension" in state.battlefield:
        state.proxy_lifegain_total += min(NUM_OPPONENTS, n // 2) * 2


# ---------------------------------------------------------------------------
# Motor central — payoffs de dano por compra + wheels
# ---------------------------------------------------------------------------

def damage_per_opponent_draw(state: GameState, count_bowmasters: bool = True) -> int:
    """Soma quanto dano/perda-de-vida CADA compra de UM oponente causa,
    somando todos os payoffs ativos (auditoria secao 5.1). `count_bowmasters`
    existe porque o oraculo real de Orcish Bowmasters e' "...whenever an
    opponent draws a card EXCEPT THE FIRST ONE they draw in each of their
    draw steps..." (achado real 2026-08-28 - a versao anterior contava
    TODA compra, inclusive a normal do draw step, superestimando; so'
    `draw_step()` precisa excluir a compra base - wheels/ativadas fora do
    draw step disparam Bowmasters normalmente, contam com o default True)."""
    total = 0
    total += _commander_copies(state)
    if count_bowmasters:
        total += _copies_of(state, "Orcish Bowmasters")
    total += 2 * _copies_of(state, "Sheoldred, the Apocalypse")
    if "Underworld Dreams" in state.battlefield:
        total += 1
    if "Spiteful Visions" in state.battlefield:
        total += 1
    if "Phyrexian Tyranny" in state.battlefield:
        total += 2  # premissa: oponente nao paga o {2}, documentado
    total += _copies_of(state, "Razorkin Needlehead")
    total += _copies_of(state, "Scrawling Crawler")
    return total


def symmetric_extra_draws_per_player(state: GameState) -> int:
    """Efeitos 'at the beginning of each player's draw step, draws +1'."""
    n = _commander_copies(state)
    if "Spiteful Visions" in state.battlefield:
        n += 1
    return n


def discard_payoff_total(state: GameState, discards_per_opp: int):
    """Waste Not/Liliana's Caress: gatilhos por CADA carta que um oponente
    descarta (evento distinto de "compra", que wheel_event ja cobria).
    Achado real 2026-08-28 (auditoria de checklist de mecanica): as duas
    cartas tinham tag "discard_payoff" mas nenhum gatilho real disparava.

    Premissa documentada (sem oponente real, sem tipo de carta descartada
    rastreado): a composicao da mao descartada e aproximada pela
    composicao REAL desta decklist (22 terrenos, 10 criaturas, ~67
    outras, de 99 cartas) - usado so pro Waste Not (as 3 clausulas dele
    dependem do TIPO da carta descartada). Liliana's Caress nao depende
    de tipo, aplicada a todo descarte."""
    if discards_per_opp <= 0:
        return
    total_discards = discards_per_opp * NUM_OPPONENTS
    if "Liliana's Caress" in state.battlefield:
        state.discard_payoff_life_loss_total += 2 * total_discards
        proxy_drain(state, 2 * total_discards)
    if "Waste Not" in state.battlefield:
        land_frac, creature_frac = 22 / 99, 10 / 99
        other_frac = 1 - land_frac - creature_frac
        lands_discarded = total_discards * land_frac
        creatures_discarded = total_discards * creature_frac
        other_discarded = total_discards * other_frac
        state.bonus_mana_pool += int(lands_discarded) * 2  # "add {B}{B}" por land descartada
        state.zombie_tokens_total += int(creatures_discarded)
        drawn = int(other_discarded)
        state.waste_not_draws_total += drawn
        draw_cards(state, drawn)


def wheel_event(state: GameState, my_draws: int, opp_draws_each: int, source: str, full_wheel: bool = True,
                 discards_per_opp: int = None):
    """Um evento de wheel: EU compro `my_draws` cartas de verdade (vantagem
    real de mao); cada um dos NUM_OPPONENTS oponentes-proxy compra
    `opp_draws_each`, cada compra alheia gerando dano real via
    `damage_per_opponent_draw()`. `discards_per_opp` (default =
    opp_draws_each, premissa documentada: na maioria dos wheels simetricos
    "discard hand, draw N" o descarte e da mesma ordem de grandeza do
    redraw) alimenta Waste Not/Liliana's Caress via discard_payoff_total."""
    state.wheel_events_total += 1
    if full_wheel:
        state.full_wheels_total += 1
    draw_cards(state, my_draws)
    if state.commander_in_play or "Spiteful Visions" in state.battlefield:
        pass  # meu proprio draw ja processado acima; dano por MINHA compra tratado a parte no draw_step
    dpd = damage_per_opponent_draw(state)
    total_dmg = dpd * opp_draws_each * NUM_OPPONENTS
    proxy_drain(state, total_dmg)  # Mindcrank/Bloodchief Ascension ja aplicados dentro (centralizado, achado real 2026-09-13)
    discard_payoff_total(state, opp_draws_each if discards_per_opp is None else discards_per_opp)


def draw_step(state: GameState):
    extra = symmetric_extra_draws_per_player(state)
    my_draws = 1 + extra
    # self_damage_per_draw E o ganho de vida da Sheoldred ("whenever you
    # draw a card, gain 2 life") ja aplicados dentro de draw_cards()
    # (centralizado - achado real 2026-09-13, ver comentario na funcao).
    draw_cards(state, my_draws)
    # Dano proxy pelas compras simetricas dos OPONENTES nesse mesmo draw step.
    # A compra "base" (a 1a de cada draw step) NAO conta pro Bowmasters
    # (exclusao real do oraculo dele); as extras (Nekusar/Spiteful Visions)
    # nao sao "a primeira", entao contam normalmente.
    dpd_baseline = damage_per_opponent_draw(state, count_bowmasters=False)
    dpd_extra = damage_per_opponent_draw(state, count_bowmasters=True)
    proxy_drain(state, dpd_baseline * 1 * NUM_OPPONENTS)
    if extra:
        proxy_drain(state, dpd_extra * extra * NUM_OPPONENTS)

    # Faerie Mastermind (metade passiva): "Whenever an opponent draws
    # their second card each turn, you draw a card." Achado real
    # 2026-08-28: nunca implementada. So' dispara se cada oponente
    # realmente compra uma 2a carta no proprio turno - isso so' acontece
    # com o estatico da propria Nekusar ativo (my_draws >= 2, ja que o
    # mesmo efeito simetrico vale pra todo mundo). Uma vez por MEU turno,
    # representando os 3 turnos-proxy dos oponentes desde o meu ultimo.
    if "Faerie Mastermind" in state.battlefield and my_draws >= 2:
        draw_cards(state, NUM_OPPONENTS)
        state.faerie_mastermind_draws_total += NUM_OPPONENTS

    try_teferis_puzzle_box(state)


def upkeep_step(state: GameState):
    if "Scrawling Crawler" in state.battlefield:
        draw_cards(state, 1)
        dpd = damage_per_opponent_draw(state)
        proxy_drain(state, dpd * NUM_OPPONENTS)
    if "The One Ring" in state.battlefield and state.the_one_ring_burden > 0:
        state.life -= state.the_one_ring_burden


# ---------------------------------------------------------------------------
# Mana
# ---------------------------------------------------------------------------

def ready_creatures(state: GameState):
    # Lightning Greaves (achado real 2026-09-13): "Equipped creature has
    # haste" + "Equip {0}" - a carta inteira estava 100% inerte (nem
    # tagueada, nunca referenciada fora do add()). Equipar custa 0 mana e
    # nao usa {T}, entao e' efetivamente gratis mover pra qualquer criatura
    # que precise de haste no turno em que entra - simplificado como "toda
    # criatura esta pronta" enquanto Greaves esta em campo (so' 2 criaturas
    # da lista tem habilidade ativada com {T} que se importam: Jace's
    # Archivist, Magus of the Wheel - dificilmente as duas entram no mesmo
    # turno, entao a simplificacao de "cobre qualquer uma" e' segura).
    if "Lightning Greaves" in state.battlefield:
        return [n for n in state.battlefield if is_creature_card(n)]
    return [n for n in state.battlefield if is_creature_card(n)
            and (state.creature_cast_turn.get(n, -1) < state.turn)]


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    for n in ("Arcane Signet", "Talisman of Creativity", "Talisman of Dominance"):
        if n in state.battlefield:
            total += 1
    if "Mox Opal" in state.battlefield and sum(1 for n in state.battlefield if is_artifact_card(n)) >= 3:
        total += 1
    return total


def total_mana(state: GameState) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES) - len(state.tapped_lands_this_turn)
    return lands + rocks_mana(state) + state.bonus_mana_pool


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def can_cast(state: GameState, name: str) -> bool:
    # Deflecting Swat: "If you control a commander, you may cast this spell
    # without paying its mana cost." Achado real 2026-08-28 (auditoria de
    # checklist): tagueada "free_with_commander", nunca despachada - pagava
    # o custo cheio ({3}) igual a qualquer outra "interaction" generica.
    if "free_with_commander" in CARD_DB[name].tags and state.commander_in_play:
        return True
    return remaining_mana(state) >= CARD_DB[name].mv


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


def do_surveil_1(state: GameState):
    """Undercity Sewers: "When this land enters, surveil 1." Heuristica
    documentada (nao ha decisao "certa" universal sem saber o resto da
    mao): se o topo e' um terreno E ja ha mana suficiente em campo (4+),
    manda pro cemiterio (alimenta o motor central de Underworld Breach/
    Past in Flames, que reciclam instant/sorcery do cemiterio); senao
    mantem no topo (guarda pra compra normal)."""
    if not state.library:
        return
    top = state.library[0]
    if top in LAND_NAMES and total_mana(state) >= 4:
        state.library.pop(0)
        state.graveyard.append(top)
        state.surveil_mills_total += 1


# ---------------------------------------------------------------------------
# Resolucao de gatilhos ETB / cast
# ---------------------------------------------------------------------------

def resolve_spark_double_target(state: GameState) -> Optional[str]:
    """Spark Double: "You may have this creature enter as a copy of a
    creature or planeswalker you control, except it isn't legendary" (evita
    a legend rule ao copiar o proprio Nekusar). Sem planeswalkers na lista
    (categoria 12 - N/A, confirmado). Prioriza a criatura em campo que mais
    empilha o motor central de dano-por-compra: Nekusar (dano + MAIS UMA
    compra extra simetrica por turno pra todo mundo, efeito composto) >
    Sheoldred (dano dobrado + ganho de vida dobrado) > Bowmasters/Razorkin/
    Scrawling Crawler (todos +1 flat)."""
    priority = [COMMANDER, "Sheoldred, the Apocalypse", "Orcish Bowmasters",
                "Razorkin Needlehead", "Scrawling Crawler"]
    for p in priority:
        if p == COMMANDER:
            if state.commander_in_play:
                return p
        elif p in state.battlefield:
            return p
    # fallback: copia qualquer criatura em campo (sem valor numerico extra
    # modelado - so' um corpo, documentado, nao inventado).
    creatures = [n for n in state.battlefield if is_creature_card(n) and n != "Spark Double"]
    return creatures[0] if creatures else None


def resolve_etb(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if name == "Orcish Bowmasters":
        # Achado real 2026-09-13: oraculo real e' "...deals 1 damage to ANY
        # TARGET" (um alvo so', 1 dano total) - nao "each opponent". O
        # codigo original multiplicava por NUM_OPPONENTS (3x overcounting).
        # Corrigido pra 1 dano so' (premissa: sempre mira um oponente-proxy,
        # a jogada obviamente correta).
        proxy_drain(state, 1)  # gatilho de ETB dela propria (independente de compra), amass Orcs 1 fora de escopo (sem combate modelado)
    if name == "The One Ring":
        state.life += 0  # protecao total (ETB), sem efeito numerico modelado (sem oponente real atacando/removendo)
    if name == "Spark Double":
        target = resolve_spark_double_target(state)
        state.spark_double_copy_target = target
        if target == "Orcish Bowmasters":
            # a copia TAMBEM dispara o "when this creature enters" de
            # Bowmasters - 1 dano so' (mesma correcao acima, achado real 2026-09-13).
            proxy_drain(state, 1)
    if "ritual" in tags:
        pass  # tratado em resolve_instant


def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if "ritual" in tags:
        state.rituals_cast_total += 1
        if name == "Dark Ritual":
            state.bonus_mana_pool += 3
        elif name == "Cabal Ritual":
            state.bonus_mana_pool += 5 if len(state.graveyard) >= 7 else 3
    elif "wheel_full" in tags:
        if name == "Wheel of Fortune":
            wheel_event(state, my_draws=7, opp_draws_each=7, source=name)
        elif name == "Windfall":
            discard_n = len(state.hand)
            wheel_event(state, my_draws=max(discard_n, 1), opp_draws_each=max(discard_n, 1), source=name)
        elif name == "Winds of Change":
            # Achado real 2026-09-13: oraculo real "shuffles the cards from
            # their hand into their library" - NAO e' um discard (Waste
            # Not/Liliana's Caress exigem "discards" especificamente).
            # discards_per_opp=0 corrige o default (que herdava opp_draws_each).
            n = len(state.hand)
            wheel_event(state, my_draws=n, opp_draws_each=n, source=name, discards_per_opp=0)
        elif name == "Echo of Eons":
            # Mesmo achado: "shuffles their hand AND graveyard into their
            # library" - tambem nao e' discard.
            wheel_event(state, my_draws=7, opp_draws_each=7, source=name, discards_per_opp=0)
        elif name == "Wheel and Deal":
            wheel_event(state, my_draws=1, opp_draws_each=7, source=name)
        elif name == "Wheel of Misfortune":
            wheel_event(state, my_draws=7, opp_draws_each=7, source=name)
    elif "tutor" in tags or "tutor_top" in tags or "tutor_instant_sorcery" in tags:
        do_tutor(state, name)
    elif name == "Brain Freeze":
        copies = state.spells_cast_this_turn  # storm: copiada 1x por spell ja conjurada antes
        state.mill_proxy_total += 3 * (1 + copies) * NUM_OPPONENTS
    elif name == "Reanimate" or name == "Animate Dead":
        targets = [c for c in state.graveyard if is_creature_card(c)]
        if targets:
            best = max(targets, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            enter_battlefield(state, best, from_hand=False)
            state.reanimator_targets_total += 1
            if name == "Reanimate":
                state.life -= CARD_DB[best].mv
    elif name == "Past in Flames":
        work_breach_or_flames_recast(state, mode="flashback")
    elif name == "Flashback":
        # Oraculo real: "Target instant or sorcery card in your graveyard
        # gains flashback until end of turn. The flashback cost is equal to
        # its mana cost." Achado real 2026-08-28: tagueada generica
        # "interaction", so' conjurada e descartada sem efeito (o card
        # NAMED "Flashback" e' distinto da palavra-chave que Past in
        # Flames concede - os dois existem nesta mesma decklist).
        before = state.breach_recasts_total
        work_breach_or_flames_recast(state, mode="flashback", max_iterations=1)
        state.flashback_card_recasts_total += state.breach_recasts_total - before
    elif "interaction" in tags:
        # Contramagicas/remocao/protecao: conjuradas quando ha mana sobrando
        # (documentado no docstring), sem efeito de combate real modelado
        # por ser goldfish solo sem oponente real pra mirar - so contadas
        # aqui pra metrica INTERACTION do checklist (categoria 10).
        state.interaction_spells_cast_total += 1


def do_tutor(state: GameState, name: str):
    """Busca a peca mais necessaria: prioriza Underworld Breach (motor de
    storm) se ainda nao tiver, senao o proximo wheel/payoff que faltar."""
    priority = ["Underworld Breach", "Past in Flames", "Wheel of Fortune", "Sheoldred, the Apocalypse",
                "Underworld Dreams", "Sol Ring", "Dark Ritual"]
    pool = [n for n in priority if n in state.library]
    if not pool:
        # fallback: qualquer wheel ou payoff que ainda esteja na biblioteca
        pool = [n for n in state.library if CARD_DB[n].tags & {"wheel_full", "payoff", "breach_engine"}]
    if not pool:
        return
    choice = pool[0]
    state.library.remove(choice)
    if "tutor_top" in CARD_DB[name].tags:
        state.library.insert(0, choice)
        # Achado real 2026-09-13: Imperial Seal e Vampiric Tutor (as 2
        # cartas com a tag "tutor_top") dizem os dois, no oraculo real,
        # "...put that card on top. YOU LOSE 2 LIFE." - clausula nunca
        # modelada (Demonic Tutor/Solve the Equation/Beseech the Mirror nao
        # tem esse custo, corretamente sem essa linha).
        state.life -= 2
    else:
        state.hand.append(choice)
    state.tutors_used_total += 1


def work_breach_or_flames_recast(state: GameState, mode: str, max_iterations: int = 40):
    """Underworld Breach: escape = mana cost + exilar 3 outras do GY.
    Past in Flames (via flashback / resolve_instant_sorcery chamando isso):
    flashback = mana cost, sem exilar. Past in Flames diz explicitamente
    "Each INSTANT and SORCERY card in your graveyard gains flashback" -
    restrito a esses 2 tipos, mantido assim pro modo "flashback".

    Underworld Breach, porem, diz *"Each NONLAND card in your graveyard
    has escape"* - achado real 2026-09-13: o codigo original restringia o
    modo "escape" tambem so a instant/sorcery, mas o oraculo real cobre
    QUALQUER carta nao-terreno, inclusive criaturas/artefatos/encantamentos
    (varios dos proprios payoffs de dano-por-compra desta lista podem
    parar no cemiterio via wheels que descartam a mao, ou via
    `cleanup_discard`, e ficavam presos la sem poder voltar). Corrigido:
    permanentes escapados VAO PRO CAMPO (`enter_battlefield`), nao voltam
    pro cemiterio (diferente de instant/sorcery, que resolvem e voltam pro
    GY normalmente sob escape - escape em si nao exila a carta).

    O loop termina sozinho quando faltar mana ou cartas suficientes no GY.
    `max_iterations=1` reaproveitado pro card "Flashback" (achado real
    2026-08-28: enabler de UM tiro so, "target instant/sorcery in your
    graveyard gains flashback... cost = mana cost" - nao e' um motor
    repetivel como Breach/Past in Flames, mesma mecanica de resolucao
    (recasta do cemiterio, exila ao resolver - CR 702.32a), so' que
    limitado a 1 carta)."""
    escape_types = ("instant", "sorcery", "creature", "artifact", "artifact_creature", "enchantment")
    allowed_types = ("instant", "sorcery") if mode == "flashback" else escape_types
    loop_iterations = 0
    while loop_iterations < max_iterations:  # teto defensivo (nunca deveria ser atingido de verdade)
        loop_iterations += 1
        castable_gy = [c for c in state.graveyard
                       if CARD_DB[c].ctype in allowed_types
                       and CARD_DB[c].mv <= remaining_mana(state)]
        if mode == "escape":
            castable_gy = [c for c in castable_gy if len(state.graveyard) - 1 >= 3]
        if not castable_gy:
            break
        castable_gy.sort(key=lambda n: CARD_DB[n].mv)
        choice = castable_gy[0]
        is_permanent = CARD_DB[choice].ctype not in ("instant", "sorcery")
        spend_mana(state, CARD_DB[choice].mv)
        state.graveyard.remove(choice)
        if mode == "escape":
            exile_pool = [c for c in state.graveyard][:3]
            for c in exile_pool:
                state.graveyard.remove(c)
        state.spells_cast_this_turn += 1
        state.breach_recasts_total += 1
        if is_permanent:
            # criatura/artefato/encantamento escapado: resolve como permanente
            # normal, vai pro campo (nao volta pro cemiterio).
            enter_battlefield(state, choice, from_hand=False)
        else:
            resolve_instant_sorcery(state, choice)
            if mode == "escape":
                state.graveyard.append(choice)  # escape nao exila a propria carta (so o custo de 3 outras)
            # mode == "flashback": a carta e EXILADA ao resolver (regra real de flashback,
            # CR 702.32a) -- nao volta pro cemiterio. Sem isso o loop nunca convergia
            # (bug real encontrado no smoke-test: storm ficava preso no teto de 40).
    if loop_iterations > 1:
        state.breach_loops_total += 1
    state.storm_count_max = max(state.storm_count_max, state.spells_cast_this_turn)


def create_permanent(state: GameState, name: str):
    state.battlefield.append(name)


def enter_battlefield(state: GameState, name: str, from_hand: bool = True):
    if from_hand and name in state.hand:
        state.hand.remove(name)
    state.battlefield.append(name)
    if name == COMMANDER:
        state.commander_in_play = True
        state.commander_cast_count += 1
        if state.commander_cast_turn is None:
            state.commander_cast_turn = state.turn
    if is_creature_card(name):
        state.creature_cast_turn[name] = state.turn
    resolve_etb(state, name)


def cast_card(state: GameState, name: str, from_hand: bool = True):
    card = CARD_DB[name]
    if name == COMMANDER:
        spend_mana(state, card.mv + 2 * state.commander_cast_count)
    elif "free_with_commander" in card.tags and state.commander_in_play:
        pass  # Deflecting Swat gratis com comandante em campo (achado real 2026-08-28)
    else:
        spend_mana(state, card.mv)
    if from_hand and name != COMMANDER:
        state.hand.remove(name)
    state.spells_cast_this_turn += 1
    state.storm_count_max = max(state.storm_count_max, state.spells_cast_this_turn)

    if name in LAND_NAMES:
        state.battlefield.append(name)
        if "fetch" in card.tags:
            state.life -= 1
        if "etb_tapped" in card.tags:
            state.tapped_lands_this_turn.add(name)
        if "shock" in card.tags:
            # Blood Crypt/Steam Vents/Watery Grave (achado real 2026-09-13):
            # "you may pay 2 life. If you don't, it enters tapped." Sempre
            # paga (premissa documentada: deck de storm/combo quer mana no
            # mesmo turno, mesma logica ja usada pras fetches).
            state.life -= 2
        if "etb_tapped_conditional" in card.tags:
            # Mistrise Village (achado real 2026-09-13): "enters tapped
            # unless you control a Mountain or a Forest" - checado contra o
            # board real no momento do land drop.
            if not any(n in MOUNTAIN_TYPE_LANDS for n in state.battlefield):
                state.tapped_lands_this_turn.add(name)
        if "surveil_on_etb" in card.tags:
            do_surveil_1(state)
        return

    if card.ctype in ("instant", "sorcery"):
        resolve_instant_sorcery(state, name)
        if name == "Underworld Breach":
            state.underworld_breach_active = True
            state.battlefield.append(name)
            return
        state.graveyard.append(name)
        return

    # Contra-ataque (`try_smart_opponent_counter`, 7a categoria do modo de
    # resiliencia -- so' faz sentido no exato momento do cast, mesma
    # logica do Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Vihaan): mana e
    # taxa ja' foram gastos ACIMA (CR 903.10a/608.2b contam "cast", nao
    # "resolved") -- so' mira o comandante, e' o motor de dano-por-compra
    # inteiro do deck. `interaction_rng is None` (modo padrao) faz isso
    # ser sempre False, sem custo nenhum de bit-identidade. Comandante
    # contra-atacada nunca chega a `enter_battlefield` -- ela nunca
    # esteve fisicamente em `state.hand` (command zone), entao nao ha'
    # zona nenhuma pra mover (nem cemiterio: CR 903.9a so' se aplica a
    # permanente que JA' foi a campo, "dies" exige "from the
    # battlefield" -- um cast contra-atacado nunca resolveu).
    if name == COMMANDER and try_smart_opponent_counter(state):
        return

    enter_battlefield(state, name, from_hand=False)
    if name == "Underworld Breach":
        state.underworld_breach_active = True


def play_land(state: GameState):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    if not lands_in_hand:
        return
    choice = lands_in_hand[0]
    cast_card(state, choice)
    state.lands_played_this_turn += 1


def main_phase(state: GameState):
    if not state.commander_in_play and can_cast(state, COMMANDER):
        cast_card(state, COMMANDER)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)]
        if not castables:
            break
        # prioriza: rituais/rocks primeiro (geram mais mana pro resto do turno),
        # depois wheels/payoffs/tutores, cartas mais baratas primeiro dentro de cada grupo
        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"ritual", "rock1", "rock2"}) else (1 if (tags & {"payoff", "wheel_full", "wheel_passive", "breach_engine"}) else 2)
            return (group, CARD_DB[n].mv)
        castables.sort(key=prio)
        cast_card(state, castables[0])

    if state.underworld_breach_active and remaining_mana(state) > 0:
        work_breach_or_flames_recast(state, mode="escape")

    try_sensei_divining_top(state)
    try_jaces_archivist(state)
    try_magus_of_the_wheel(state)
    try_faerie_mastermind_activated(state)
    try_resonating_lute_draw(state)
    try_small_wheel_lands(state)
    try_the_one_ring(state)


def try_sensei_divining_top(state: GameState):
    """Achado real 2026-08-28: o codigo checava "Sensei's Divining Top" em
    ready_creatures() - lista SO de criaturas (is_creature_card()), e o Top
    e' um Artifact, nunca uma criatura. Condicao morta por construcao,
    nunca disparava. Artefato nao tem doenca de invocacao (CR 302.6).
    Oraculo real: "{T}: Draw a card, then put this artifact on top of its
    owner's library." Premissa documentada: simplificado como +1 carta
    liquida por turno (assume que o motor de wheels/manipulacao de topo ja
    presente no deck evita so' redesencavar o proprio Top no draw seguinte)."""
    if "Sensei's Divining Top" not in state.battlefield:
        return
    draw_cards(state, 1)
    state.sensei_top_draws_total += 1


def try_jaces_archivist(state: GameState):
    """"{U}, {T}: Each player discards their hand, then draws cards equal
    to the greatest number of cards a player discarded this way." Achado
    real 2026-08-28: tagueada "wheel_repeatable", nunca despachada. {T} =
    1 ativacao por turno. Premissa: greatest discard = maior mao entre eu
    e os oponentes-proxy - usa a MINHA mao (unica rastreada de verdade)
    como piso conservador."""
    if "Jace's Archivist" not in state.battlefield or "Jace's Archivist" not in ready_creatures(state):
        return
    if remaining_mana(state) < 1:
        return
    spend_mana(state, 1)
    n = max(len(state.hand), 1)
    wheel_event(state, my_draws=n, opp_draws_each=n, source="Jace's Archivist", full_wheel=False)


def try_magus_of_the_wheel(state: GameState):
    """"{1}{R}, {T}, Sacrifice this creature: Each player discards their
    hand, then draws seven cards." Achado real 2026-08-28: tagueada
    "wheel_sac", nunca despachada. Um tiro so' (se sacrifica)."""
    if "Magus of the Wheel" not in state.battlefield or "Magus of the Wheel" not in ready_creatures(state):
        return
    if remaining_mana(state) < 2:
        return
    spend_mana(state, 2)
    state.battlefield.remove("Magus of the Wheel")
    wheel_event(state, my_draws=7, opp_draws_each=7, source="Magus of the Wheel")


def try_faerie_mastermind_activated(state: GameState):
    """"{3}{U}: Each player draws a card." Sem {T} - repetivel enquanto
    sobrar mana. Achado real 2026-08-28: tagueada "opponent_dependent",
    metade ativada nunca despachada. Teto duro de 10 ativacoes/turno
    (mesma cautela de outros decks desta sessao contra loops sem teto)."""
    if "Faerie Mastermind" not in state.battlefield:
        return
    for _ in range(10):
        if remaining_mana(state) < 4:
            break
        spend_mana(state, 4)
        # Achado real 2026-09-13: "Each player draws a card" - sem NENHUMA
        # clausula de discard. discards_per_opp=0 corrige o default (que
        # herdava opp_draws_each=1 e disparava Waste Not/Liliana's Caress
        # indevidamente).
        wheel_event(state, my_draws=1, opp_draws_each=1, source="Faerie Mastermind (ativada)", full_wheel=False, discards_per_opp=0)


def try_resonating_lute_draw(state: GameState):
    """"{T}: Draw a card. Activate only if you have seven or more cards in
    your hand." Achado real 2026-08-28: tagueada "draw_conditional", nunca
    despachada. A estatica de campo (lands ganham mana extra restrita a
    instant/sorcery) NAO foi modelada (esse motor nao restringe mana por
    tipo de spell - baixo valor pro escopo, documentado)."""
    if "Resonating Lute" not in state.battlefield:
        return
    if len(state.hand) >= 7:
        draw_cards(state, 1)


def try_the_one_ring(state: GameState):
    """The One Ring: "{T}: Put a burden counter on The One Ring, then draw
    a card for each burden counter on The One Ring." Achado real
    2026-09-13: essa era a habilidade PRINCIPAL da carta (motor de compra
    escalonado, uma das mais fortes do formato) e estava 100% ausente - so
    o gatilho de upkeep ("lose 1 life per burden counter") existia no
    codigo, mas `the_one_ring_burden` nunca era incrementado em lugar
    nenhum, entao aquele gatilho tambem nunca disparava de verdade (efeito
    morto por construcao). {T} = 1 ativacao por turno; artefato, sem
    doenca de invocacao (CR 302.6), pode ativar no turno em que entra."""
    if "The One Ring" not in state.battlefield:
        return
    state.the_one_ring_burden += 1
    draw_cards(state, state.the_one_ring_burden)


def try_small_wheel_lands(state: GameState):
    """Mikokoro/Geier Reach Sanitarium ("{2},{T}: each player draws a
    card[, then discards a card]") e Cephalid Coliseum ("{U},{T},
    Sacrifice: target player draws three, discards three. Threshold: 7+
    no cemiterio"). Achado real 2026-08-28: todas as 3 tageadas
    "wheel_source_small"/"threshold_wheel", nenhuma despachada. Todas tem
    {T} - 1 ativacao cada por turno (Cephalid tambem se sacrifica, uma vez
    na vida)."""
    if "Mikokoro, Center of the Sea" in state.battlefield and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        wheel_event(state, my_draws=1, opp_draws_each=1, source="Mikokoro", full_wheel=False, discards_per_opp=0)
        state.small_wheel_lands_used_total += 1
    if "Geier Reach Sanitarium" in state.battlefield and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        wheel_event(state, my_draws=1, opp_draws_each=1, source="Geier Reach Sanitarium", full_wheel=False, discards_per_opp=1)
        state.small_wheel_lands_used_total += 1
    if ("Cephalid Coliseum" in state.battlefield and not state.cephalid_coliseum_used
            and len(state.graveyard) >= 7 and remaining_mana(state) >= 1):
        spend_mana(state, 1)
        state.battlefield.remove("Cephalid Coliseum")
        state.cephalid_coliseum_used = True
        # Achado real 2026-09-13: "target player draws three, discards
        # three" - modelado como alvo EU MESMO (premissa ja estabelecida:
        # my_draws=3/opp_draws_each=0), mas o discards_per_opp=3 anterior
        # creditava Waste Not/Liliana's Caress (que exigem "an OPPONENT
        # discards") pro MEU proprio descarte, multiplicado por
        # NUM_OPPONENTS dentro de discard_payoff_total - nunca deveria
        # disparar aqui de jeito nenhum. Corrigido pra 0.
        wheel_event(state, my_draws=3, opp_draws_each=0, source="Cephalid Coliseum", full_wheel=False, discards_per_opp=0)


def try_teferis_puzzle_box(state: GameState):
    """"At the beginning of each player's draw step, that player puts the
    cards in their hand on the bottom of their library in any order, then
    draws that many cards." Achado real 2026-08-28: tagueada
    "wheel_passive", so' era lida pra ordenar prioridade de cast, nunca
    disparava o efeito. Dispara no MEU draw step (hand shuffle, sem ganho
    liquido de cartas) e nos dos 3 oponentes-proxy (premissa documentada:
    tamanho medio de mao 5, contribuindo dano via damage_per_opponent_draw
    pelas ~5 compras extra de cada oponente, uma vez por MEU turno,
    representando o ciclo completo dos turnos deles ate o meu proximo)."""
    if "Teferi's Puzzle Box" not in state.battlefield:
        return
    state.puzzle_box_events_total += 1
    AVG_OPP_HAND_SIZE = 5  # premissa documentada, nao dado real
    dpd = damage_per_opponent_draw(state)
    proxy_drain(state, dpd * AVG_OPP_HAND_SIZE * NUM_OPPONENTS)


def combat_step(state: GameState):
    pass  # deck de dano por gatilho de compra, sem combate real modelado


def cleanup_discard(state: GameState):
    """CR 514.3: descarta ate a mao ter 7 cartas no cleanup step. Sem isso a
    mao cresce sem limite (achado real testando: mao de 74 cartas apos 8
    turnos, com o volume de compra deste deck) — bug real corrigido.
    Mantem as cartas mais caras/valiosas (mv maior primeiro), descarta as
    baratas/substituiveis, ja que o deck tem Underworld Breach/wheels que
    se beneficiam de cemiterio cheio de qualquer forma."""
    while len(state.hand) > 7:
        worst = min(state.hand, key=lambda n: CARD_DB[n].mv)
        state.hand.remove(worst)
        state.graveyard.append(worst)


def end_step(state: GameState):
    if state.underworld_breach_active:
        if "Underworld Breach" in state.battlefield:
            state.battlefield.remove("Underworld Breach")
        state.graveyard.append("Underworld Breach")
        state.underworld_breach_active = False
    cleanup_discard(state)


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    good_early = {"Sol Ring", "Arcane Signet", "Dark Ritual", COMMANDER}
    if lands >= 3:
        return True
    if lands == 2 and any(n in good_early for n in hand):
        return True
    return False


def build_library():
    lib = []
    text = open("lista.md").read()
    for l in text.splitlines():
        l = l.strip()
        if not l or l.startswith("#") or l.startswith(">") or "Bracket" in l or "Game Changers" in l or "V9 vs" in l:
            continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if not m:
            continue
        qty, name = int(m.group(1)), m.group(2).strip()
        if name == COMMANDER:
            continue
        assert name in CARD_DB, f"faltando no CARD_DB: {name}"
        for _ in range(qty):
            lib.append(name)
    assert len(lib) == 99, len(lib)
    return lib


BASE_LIBRARY = build_library()


def mulligan(rng: random.Random, max_mulls: int = 3):
    mulls = 0
    hand, lib = [], []
    while mulls < max_mulls:
        lib = BASE_LIBRARY[:]
        rng.shuffle(lib)
        hand = lib[:7]
        lib = lib[7:]
        if should_keep(hand) or mulls == max_mulls - 1:
            # Achado real 2026-09-18 (mesma convencao dos goldfishes
            # manuais do usuario no Archidekt): 1o mulligan e' GRATIS.
            penalty = max(0, mulls - 1)
            if penalty > 0:
                rng.shuffle(hand)
                bottom = hand[:penalty]
                hand = hand[penalty:]
                lib = lib + bottom
            return hand, lib, mulls
        mulls += 1
    return hand, lib, mulls


def play_turn(state: GameState, is_first_turn: bool, on_play: bool):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.spells_cast_this_turn = 0
    state.tapped_lands_this_turn = set()

    upkeep_step(state)
    # Achado real 2026-09-18: "skip the draw step" no 1o turno de quem
    # comeca so' existe na regra 1x1 (CR 103.8a). Commander e' sempre
    # multiplayer -- sempre roda o draw_step, mesmo no T1.
    draw_step(state)

    play_land(state)
    main_phase(state)
    combat_step(state)
    main_phase(state)
    end_step(state)


# ---------------------------------------------------------------------------
# Modo de resiliencia (interacao de oponente) — 2026-09-21
# ---------------------------------------------------------------------------
# Porte completo do design FINAL ja' validado nos outros 10 decks desta
# sessao (Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/Toph/Prismatic
# Bridge/Maralen/Rat King Verminister/Vihaan). 7 categorias
# padronizadas (removal/attack/discard/wipe/graveyard-wipe/
# graveyard-snipe/counterspell), 1 rolagem "algum wipe acontece" +
# escolha ponderada de 1 TIPO so' (nao 3 rolagens independentes), gate
# de atencao por oponente (`OPPONENT_ATTENTION_CHANCE`), supressao de
# ataque pos-wipe simetrico (`state.wiped_this_round`).
#
# Igual ao Vihaan (o outro deck desta sessao a nascer sem retrofit):
# ja' nasce com a correcao de CR 903.9a aplicada desde a 1a linha
# (`remove_permanent`, ver docstring) -- mas aqui SEM nenhum efeito
# numerico, ja' que este e' um deck de dano-por-compra/wheel/storm, com
# ZERO cartas "creature dies" (grep confirmado antes de escrever
# `remove_permanent`) e ZERO motor de aristocrata/sacrificio -- mais
# proximo do Ur-Dragon/Hei Bai/Ulalek (correcao estrutural) do que do
# Edgar Markov/Rat King/Vihaan (correcao com impacto numerico real).
# Tambem ZERO token agregado (Treasure/Construct/etc) -- Zombie tokens
# do Waste Not sao proxy de metrica pura (`zombie_tokens_total`), nunca
# entram em `state.battlefield` de verdade, entao o wipe nao precisa de
# nenhuma logica de bucket de token.

NUM_OPPONENTS = 3  # premissa declarada (mesa de 4), mesma convencao dos outros 10 decks

INTERACTION_SETUP_TURNS = 2
# Turnos 1-2 sao sempre setup, sem chance de reacao nenhuma -- o
# oponente ainda nao tem motivo/mana pra reagir.


def interaction_chance(state: GameState) -> float:
    """Formula compartilhada de 'chance do oponente reagir esse turno' --
    identica aos outros 10 decks: escala com o impacto do meu proprio
    board (permanentes nao-terreno em campo)."""
    board_impact = sum(1 for n in state.battlefield if n not in LAND_NAMES)
    return min(0.10 + 0.03 * board_impact, 0.75)


OPPONENT_ATTENTION_CHANCE = 1.0 / NUM_OPPONENTS
# Gate de "esse oponente esta' de olho em mim esse turno" -- chance
# BASE de que um turno de oponente qualquer seja sobre MIM, antes de
# qualquer ajuste por ameaca de board (que ja' fica dentro de
# `interaction_chance()`). Rolado 1x no INICIO de `try_smart_opponent_
# turn`, antes de qualquer categoria.

POST_WIPE_ATTACK_HASTE_FACTOR = 0.15
# Board wipe e' SIMETRICO -- acerta TODA criatura da mesa, nao so' as
# minhas. Se um wipe ja' aconteceu NESTA RODADA (`state.wiped_this_
# round`), TODOS os turnos de oponente restantes na mesma rodada tambem
# ficam sem criaturas de verdade pra atacar -- exceto por haste.

BOARD_WIPE_CHANCE_FACTOR = 0.4
ARTIFACT_WIPE_CHANCE_FACTOR = 0.2
ENCHANTMENT_WIPE_CHANCE_FACTOR = 0.15
GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_SNIPE_CHANCE_FACTOR = 0.5
COUNTERSPELL_CHANCE_FACTOR = 0.5
# Pesos relativos de cada TIPO de sweeper (criatura/artefato/
# encantamento) -- design final ja' validado nos outros 10 decks: 1
# rolagem "algum wipe acontece" (soma dos 3 pesos) + SO' DEPOIS escolha
# ponderada de qual TIPO, restrita aos tipos com pelo menos 1 alvo legal
# em campo. Wipe de criatura muito mais comum numa lista real que
# artefato/encantamento.
WIPE_TYPE_WEIGHTS = {
    "creature": BOARD_WIPE_CHANCE_FACTOR,
    "artifact": ARTIFACT_WIPE_CHANCE_FACTOR,
    "enchantment": ENCHANTMENT_WIPE_CHANCE_FACTOR,
}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())

INTERACTION_ENGINE_PRIORITY = [
    "Underworld Dreams",
    "Phyrexian Tyranny",
    "Spiteful Visions",
    "Liliana's Caress",
    "Waste Not",
    "Bloodchief Ascension",
    "Teferi's Puzzle Box",
    "The One Ring",
    "Sensei's Divining Top",
    "Mindcrank",
]
# Lista curada por prioridade (a mais critica primeiro) -- so' cartas
# que sao motor RECORRENTE de valor (dano/vida por compra ou descarte
# do oponente, wheel forcado, draw/protecao/mill repetivel), nao corpos
# grandes isolados. O proprio Nekusar fica DE FORA de proposito -- ja'
# tem categoria dedicada (`try_smart_opponent_counter`, mira o CAST
# dele especificamente) e remocao pontual nao o mata de verdade mesmo
# (vai pra zona de comando via `remove_permanent`, recastavel depois
# pagando a taxa de novo), entao um oponente esperto prefere gastar a
# remocao pontual numa peca irrecuperavel.

OPPONENT_ATTACKER_PROFILES = [
    ("Knight Token", 2), ("Saproling Token", 1), ("Vampire Token", 1),
    ("Zombie Token", 2), ("Soldier Token", 1), ("Goblin Token", 1),
    ("Elemental Token", 3),
]
# Mesmos perfis genericos ja' validados nos outros 10 decks -- sem
# toughness, este arquivo nao modela combate/bloqueio de um oponente de
# verdade (o proprio `combat_step` do meu lado tambem e' no-op, ver
# docstring la). Todo ataque conecta.


def try_smart_opponent_removal(state: GameState) -> Optional[str]:
    """Remocao 'inteligente' -- mira sempre a peca-motor de maior
    prioridade presente em campo (`INTERACTION_ENGINE_PRIORITY`), nunca
    aleatorio."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    present = [n for n in INTERACTION_ENGINE_PRIORITY if n in state.battlefield]
    if not present:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    target = present[0]
    remove_permanent(state, target, source="opponent_removal")
    state.smart_removals_total += 1
    state.smart_removal_log.append((state.turn, target))
    return target


def try_smart_opponent_attack(state: GameState) -> Optional[str]:
    """Ataque de oponente -- SEM bloqueio (limitacao estrutural: este
    arquivo nao modela combate/bloqueio de nenhum tipo, nem o meu
    proprio). Sempre conecta em `state.life`.

    Se `state.wiped_this_round` (algum wipe ja' disparou nesta rodada,
    de qualquer oponente, incluindo este mesmo turno) a chance cai pra
    `POST_WIPE_ATTACK_HASTE_FACTOR` -- representa so' um atacante com
    haste conjurado DEPOIS do wipe."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    chance = interaction_chance(state) * (POST_WIPE_ATTACK_HASTE_FACTOR if state.wiped_this_round else 1.0)
    if state.interaction_rng.random() >= chance:
        return None
    name, power = state.interaction_rng.choice(OPPONENT_ATTACKER_PROFILES)
    state.life -= power
    state.smart_attacks_taken_total += 1
    state.smart_attack_log.append((state.turn, name))
    return name


def try_smart_opponent_discard(state: GameState) -> Optional[str]:
    """Discard aleatorio -- mesma logica dos outros 10 decks (alvo
    puramente ao acaso na mao, sem filtro nenhum)."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if not state.hand:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    target = state.interaction_rng.choice(state.hand)
    state.hand.remove(target)
    state.graveyard.append(target)
    state.smart_discards_total += 1
    state.smart_discard_log.append((state.turn, target))
    return target


def try_smart_opponent_wipe(state: GameState) -> Optional[list]:
    """Board wipe ('destroy all creatures'/'destroy all artifacts'/
    'destroy all enchantments') -- destroi TODOS os meus permanentes do
    tipo escolhido de uma vez via `remove_permanent` (que ja' trata
    comandante->zona de comando). Nekusar nunca e' artefato/encantamento
    (Legendary Creature, tags {"commander", "payoff"}, confirmado no
    CARD_DB), entao so' e' alvo do wipe de criatura -- exatamente como
    deveria (CR 903.9a: ele genuinamente morre nesse caso, so' depois
    volta pra zona de comando).

    Design de 2 passos (nao 3 rolagens independentes): 1) rola 1x se
    ALGUM wipe acontece esse turno de oponente, chance =
    `interaction_chance() * TOTAL_WIPE_CHANCE_FACTOR`; 2) SO' se isso
    disparar, escolhe qual TIPO de sweeper via escolha ponderada
    (`state.interaction_rng.choices`) restrita aos tipos que tem pelo
    menos 1 alvo legal em campo. Sem tokens agregados neste deck (ver
    nota estrutural no topo da secao) -- diferente dos outros decks,
    nenhum bucket extra pra zerar."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    candidates = {
        "creature": [n for n in state.battlefield if is_creature_card(n)],
        "artifact": [n for n in state.battlefield if is_artifact_card(n)],
        "enchantment": [n for n in state.battlefield if is_enchantment_card(n)],
    }
    available = [t for t in candidates if candidates[t]]
    if not available:
        return None
    wipe_type = state.interaction_rng.choices(available, weights=[WIPE_TYPE_WEIGHTS[t] for t in available])[0]
    targets = candidates[wipe_type]
    hit_creature = any(is_creature_card(n) for n in targets)
    for n in targets:
        remove_permanent(state, n, source=f"opponent_{wipe_type}_wipe")
    if wipe_type == "creature":
        state.smart_wipes_total += 1
        state.smart_wipe_log.append((state.turn, targets))
    elif wipe_type == "artifact":
        state.smart_artifact_wipes_total += 1
        state.smart_artifact_wipe_log.append((state.turn, targets))
    else:
        state.smart_enchantment_wipes_total += 1
        state.smart_enchantment_wipe_log.append((state.turn, targets))
    if hit_creature:
        state.wiped_this_round = True
    return targets


def try_smart_opponent_graveyard_wipe(state: GameState) -> Optional[list]:
    """Graveyard hate, modelo MASS EXILE (Bojuka Bog/Soul-Guide
    Lantern-style) -- dispara NO MAXIMO 1x por partida inteira
    (`state.graveyard_wipe_used`). Relevante de verdade neste deck --
    Animate Dead/Reanimate/Underworld Breach dependem do cemiterio."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.graveyard_wipe_used or not state.graveyard:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_WIPE_CHANCE_FACTOR:
        return None
    exiled = state.graveyard[:]
    state.graveyard.clear()
    state.graveyard_wipe_used = True
    state.smart_graveyard_wipes_total += 1
    state.smart_graveyard_wipe_log.append((state.turn, exiled))
    return exiled


def try_smart_opponent_graveyard_snipe(state: GameState) -> Optional[str]:
    """Graveyard hate, modelo EXILIO DE CARTA UNICA (Scavenging
    Ooze/Cease-style) -- repetivel todo turno. Alvo SMART: maior MV
    entre criatura no cemiterio -- mesmo criterio que Animate
    Dead/Reanimate ja' usam pra escolher alvo real de reanimacao."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    candidates = [c for c in state.graveyard if is_creature_card(c)]
    if not candidates:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_SNIPE_CHANCE_FACTOR:
        return None
    target = max(candidates, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(target)
    state.smart_graveyard_snipes_total += 1
    state.smart_graveyard_snipe_log.append((state.turn, target))
    return target


def try_smart_opponent_counter(state: GameState) -> bool:
    """Counterspell -- so' mira a conjuracao do proprio Nekusar (mesma
    logica dos outros 10 decks: o motor inteiro do deck depende do
    comandante resolver -- dano-por-compra E MAIS UMA compra extra
    simetrica por turno pra todo mundo). Chamada de dentro de
    `cast_card()`, nao do loop de `simulate_one_with_interaction` -- so'
    faz sentido no exato momento do cast, dentro do MEU turno."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * COUNTERSPELL_CHANCE_FACTOR:
        return False
    state.smart_counters_total += 1
    state.smart_counter_log.append(state.turn)
    return True


def try_smart_opponent_turn(state: GameState):
    """Simula O TURNO DE UM oponente dentro da rodada entre os meus
    turnos (Regra #6 do CLAUDE.md: bug de orquestracao de turno que
    auditoria carta-a-carta nao pega). Chamada `NUM_OPPONENTS` vezes por
    rodada -- um wipe de um oponente ANTERIOR na rodada continua
    afetando corretamente o ataque de um oponente POSTERIOR na MESMA
    rodada (chamadas em sequencia, mesmo `state`).

    Gate de atencao: antes de rolar QUALQUER categoria, este turno de
    oponente precisa passar em `OPPONENT_ATTENTION_CHANCE`. Wipe e
    ataque nao precisam de exclusao mutua manual aqui: `try_smart_
    opponent_attack` ja' se auto-regula via `state.wiped_this_round`
    (setado por `try_smart_opponent_wipe`, que roda antes, dentro desta
    mesma chamada)."""
    if state.turn > INTERACTION_SETUP_TURNS and state.interaction_rng.random() >= OPPONENT_ATTENTION_CHANCE:
        return
    try_smart_opponent_wipe(state)
    try_smart_opponent_attack(state)
    try_smart_opponent_graveyard_wipe(state)
    try_smart_opponent_graveyard_snipe(state)
    try_smart_opponent_removal(state)
    try_smart_opponent_discard(state)


def simulate_one_with_interaction(seed: int, turns: int = 8) -> GameState:
    """Mesmo goldfish de `simulate_one`, mas com `NUM_OPPONENTS` turnos
    de oponente de verdade simulados (`try_smart_opponent_turn`) a cada
    rodada entre os meus turnos. Counterspell (7a categoria) NAO mora
    neste loop -- ver `try_smart_opponent_counter`, chamada de dentro de
    `cast_card()` no exato momento do cast do comandante.

    NUNCA chamado por `run_batch`/`simulate_one` padrao (nem o loop
    aqui, nem o counter dentro de `cast_card` -- ambos ficam inertes sem
    `interaction_rng`). Retorna o `GameState` bruto (nao um resumo),
    mesma convencao dos outros 10 decks, pra inspecao detalhada das
    metricas de resiliencia."""
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls,
                       interaction_rng=random.Random(seed + 999_999))
    for t in range(turns):
        play_turn(state, is_first_turn=(t == 0), on_play=True)
        state.wiped_this_round = False
        for _ in range(NUM_OPPONENTS):
            try_smart_opponent_turn(state)
    return state


def run_batch_with_interaction(n=2000, turns=8, seed_base=6000000):
    """Batch do modo de resiliencia -- reporta so' as metricas
    relevantes pra 'o motor aguenta perder a peca central?', nao
    duplica o relatorio inteiro do `run_batch` padrao."""
    states = [simulate_one_with_interaction(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns} (MODO RESILIENCIA -- wipe + graveyard hate + "
          f"remocao + ataque + discard aleatorio + counterspell de oponente)")
    print(f"Avg counterspells sofridos (so' mira a conjuracao do Nekusar): "
          f"{avg([s.smart_counters_total for s in states]):.2f}")
    cmd_cast = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"  -- Turno medio de conjuracao QUE RESOLVEU: {avg(cmd_cast):.2f} | "
          f"nunca resolveu em {turns} turnos: {100*(n-len(cmd_cast))/n:.1f}%")
    print(f"Avg board wipes sofridos: {avg([s.smart_wipes_total for s in states]):.2f}")
    print(f"Avg artifact wipes sofridos: {avg([s.smart_artifact_wipes_total for s in states]):.2f}")
    print(f"Avg enchantment wipes sofridos: {avg([s.smart_enchantment_wipes_total for s in states]):.2f}")
    gy_wiped = sum(1 for s in states if s.smart_graveyard_wipes_total > 0)
    print(f"Partidas com graveyard wipe sofrido (no maximo 1x/partida): {100*gy_wiped/n:.1f}%")
    print(f"Avg graveyard snipes sofridos (sempre a maior MV criatura): "
          f"{avg([s.smart_graveyard_snipes_total for s in states]):.2f}")
    print(f"Avg remocoes inteligentes sofridas: {avg([s.smart_removals_total for s in states]):.2f}")
    print(f"Avg ataques sofridos: {avg([s.smart_attacks_taken_total for s in states]):.2f}")
    print(f"Avg descartes sofridos: {avg([s.smart_discards_total for s in states]):.2f}")
    return states


def simulate_one(seed: int, turns: int = 8):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls)
    for t in range(turns):
        play_turn(state, is_first_turn=(t == 0), on_play=True)
    return state


def run_batch(n: int, seed_base: int, turns: int = 8):
    states = [simulate_one(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns}")
    print(f"Avg mulligans: {avg([s.mulligans for s in states]):.2f}")
    cmd_turn = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"Turno medio de conjuracao do Nekusar: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurado em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    print(f"Avg eventos de wheel (full+parcial): {avg([s.wheel_events_total for s in states]):.2f}")
    print(f"Avg wheels completos (descarta mao, compra 7): {avg([s.full_wheels_total for s in states]):.2f}")
    print(f"Avg dano/perda-de-vida proxy total (3 oponentes hipoteticos, NUNCA vida real): {avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"Avg vida ganha (Sheoldred, proxy Bloodchief): {avg([s.proxy_lifegain_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg tutores usados: {avg([s.tutors_used_total for s in states]):.2f}")
    print(f"Avg recasts via Underworld Breach/Past in Flames: {avg([s.breach_recasts_total for s in states]):.2f}")
    breach_hits = sum(1 for s in states if s.breach_loops_total > 0)
    print(f"Partidas com pelo menos 1 loop de Breach/Flames (2+ recasts no mesmo evento): {100*breach_hits/n:.1f}%")
    print(f"Avg storm count maximo no turno: {avg([s.storm_count_max for s in states]):.2f}")
    print(f"Avg mill proxy total (Mindcrank + Brain Freeze): {avg([s.mill_proxy_total for s in states]):.2f}")
    print(f"Avg reanimados (Animate Dead/Reanimate): {avg([s.reanimator_targets_total for s in states]):.2f}")
    print(f"Avg compras via Faerie Mastermind (passiva+ativada, agora despachadas): {avg([s.faerie_mastermind_draws_total for s in states]):.2f}")
    print(f"Avg compras via Sensei's Divining Top (agora despachado): {avg([s.sensei_top_draws_total for s in states]):.2f}")
    print(f"Avg perda de vida proxy via discard payoffs (Waste Not/Liliana's Caress, agora despachados): {avg([s.discard_payoff_life_loss_total for s in states]):.2f}")
    print(f"Avg eventos de Teferi's Puzzle Box (agora despachado): {avg([s.puzzle_box_events_total for s in states]):.2f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")

    spark_hits = sum(1 for s in states if s.spark_double_copy_target is not None)
    print(f"Spark Double copiou algo (agora despachado): {100*spark_hits/n:.1f}% dos jogos"
          + (f" | alvos: {statistics.mode([s.spark_double_copy_target for s in states if s.spark_double_copy_target])}" if spark_hits else ""))
    print(f"Avg recasts via Flashback (o card, agora despachado): {avg([s.flashback_card_recasts_total for s in states]):.2f}")
    print(f"Avg mills via surveil (Undercity Sewers, agora despachado): {avg([s.surveil_mills_total for s in states]):.2f}")
    print(f"Avg autodano (Spiteful Visions + Phyrexian Tyranny nas MINHAS proprias compras, agora rastreado): {avg([s.self_damage_total for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life for s in states]):.2f}")
    own_payoffs_ko = sum(1 for s in states if s.life <= 0)
    print(f"Partidas em que os PROPRIOS payoffs simetricos derrubam minha vida a 0 ou menos: {100*own_payoffs_ko/n:.1f}% "
          f"(risco real de Spiteful Visions/Phyrexian Tyranny simetricos num deck que compra em volume extremo)")

    # --- Metricas basicas (checklist obrigatorio, categoria 10) --------------
    print("--- Metricas basicas (checklist obrigatorio) ---")
    rocks_in_play = [sum(1 for c in s.battlefield if CARD_DB[c].tags & {"rock1", "rock2"}) for s in states]
    print(f"RAMP: avg mana rocks em campo ao fim da partida (Sol Ring/Arcane Signet/Talismas/Mox Opal): "
          f"{avg(rocks_in_play):.2f} | avg rituais conjurados (Dark Ritual/Cabal Ritual): "
          f"{avg([s.rituals_cast_total for s in states]):.2f}")
    print(f"DRAW: avg cartas compradas extras totais (todos os motores - wheels, Sensei's Top, Faerie "
          f"Mastermind, Resonating Lute, terrenos de wheel, Waste Not): {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"INTERACTION: avg spells de interacao/contramagica conjurados quando ha mana sobrando (Counterspell, "
          f"Mana Drain, Force of Will, Swan Song, Deflecting Swat -agora gratis com comandante, achado real "
          f"2026-08-28-, etc.) - sem efeito de combate real por ser goldfish solo sem oponente real pra mirar: "
          f"{avg([s.interaction_spells_cast_total for s in states]):.2f}")
    print(f"RECURSION: avg criaturas reanimadas do cemiterio pro campo (Animate Dead/Reanimate): "
          f"{avg([s.reanimator_targets_total for s in states]):.2f}. Recasts de instant/sorcery via Underworld "
          f"Breach/Past in Flames/Flashback NAO contam aqui - reciclam do cemiterio pra STACK, nao pro campo, "
          f"categoria diferente (contados em 'Avg recasts' acima). Tutores (Demonic Tutor etc.) buscam da "
          f"biblioteca, tambem categoria diferente.")
    print(f"FINISHER/LETHALITY: sem dano de combate real medido (deck nao ataca) - o 'finisher' real e' o dano "
          f"proxy agregado por gatilho-de-compra ({avg([s.proxy_damage_total for s in states]):.2f} medio) mais "
          f"o risco simetrico de autodano ({avg([s.self_damage_total for s in states]):.2f} medio, "
          f"{100*own_payoffs_ko/n:.1f}% das partidas com risco de vida propria a 0 ou menos)")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=7300000, turns=8)

    with open("nekusar_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "wheel_events_total": s.wheel_events_total,
                "full_wheels_total": s.full_wheels_total,
                "proxy_damage_total": s.proxy_damage_total,
                "cards_drawn_extra": s.cards_drawn_extra,
                "tutors_used_total": s.tutors_used_total,
                "breach_recasts_total": s.breach_recasts_total,
                "storm_count_max": s.storm_count_max,
            }) + "\n")

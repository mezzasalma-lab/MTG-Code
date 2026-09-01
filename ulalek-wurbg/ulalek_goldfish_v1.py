"""
Goldfish simulator — Ulalek, Fused Atrocity (5 cores, WUBRG, Eldrazi/Devoid)

Construido do zero em 2026-08-23. Passo 0 (regra de
`references/goldfish-sim-card-rules.md`): a `auditoria.md` deste deck e uma
categorizacao funcional (ramp/draw/removal/protecao/flash/multiplicadores),
nao um catalogo carta-a-carta de gatilhos como o do Nekusar — entao a
varredura mecanica completa no oraculo real das 100 cartas (regex
"Whenever"/"At the beginning of"/"When ... enters"/"When you cast this
spell") foi feita aqui pela primeira vez (ver /tmp/ulalek_full.txt).

IMPORTANTE — numeros do Colab do usuario (auditoria.md secao 8) NAO foram
usados como alvo. Aquela secao e explicita: sao numeros de um simulador
externo que a propria auditoria diz nao poder verificar. Este script foi
construido de forma independente a partir do oraculo real; qualquer
divergencia com os numeros do Colab e reportada com honestidade, nao
forcada a bater.

======================================================================
MECANICA CENTRAL — o motor de copia da propria comandante
======================================================================
Ulalek: "Whenever you cast an Eldrazi spell, you may pay {C}{C}. If you do,
copy all spells you control, then copy all other activated and triggered
abilities you control. You may choose new targets for the copies."

Duas cópias distintas por Eldrazi-cast pago (CC):
1. Copia do PROPRIO SPELL (o que acabou de ser conjurado) — se for
   permanente, gera um TOKEN copia extra entrando em campo; se for
   instant/sorcery, so resolve o efeito de novo (a copia nao vira carta
   fisica, nao vai pro cemiterio).
2. Copia da(s) habilidade(s) ativada(s)/disparada(s) que voce controla —
   na pratica, o gatilho "When you cast this spell" da PROPRIA carta que
   acabou de ser conjurada (Kozilek Butcher, Nulldrifter, etc), que ainda
   esta na pilha (nao resolveu) no momento em que o gatilho da Ulalek
   resolve. Isso e SEPARADO da copia do spell em si — copiar Kozilek
   Butcher da 2 corpos 10/10 E dobra o "compre 4" pra "compre 8" (2
   disparos de 4), nao e a mesma coisa.

Simplificacao documentada (arquitetura sem pilha real): este simulador
resolve um spell por vez, greedy, sem manter multiplos spells
simultaneos na pilha — "copiar todos os spells que voce controla" na
pratica sempre significa "o spell que acabou de ser conjurado" (unico
spell "na pilha" neste modelo), consistente com a convencao ja usada nos
outros 8 simuladores desta biblioteca.

======================================================================
Echoes of Eternity — o segundo motor de copia/dobra
======================================================================
"If a triggered ability of a colorless spell you control or another
colorless permanent you control triggers, that ability triggers an
additional time. Whenever you cast a colorless spell, copy it."

Duas habilidades DISTINTAS, implementadas separadamente:
- 1a habilidade: DOBRA gatilhos cuja fonte e (a) um spell colorless
  (inclui gatilhos "when you cast this spell" — quase todo cast-trigger
  deste deck e de uma carta colorless via Devoid, mesmo com pips
  coloridos no custo) OU (b) OUTRO permanente colorless (Glaring
  Fleshraker, Forsaken Monument, Kozilek's Unsealing, Chittering
  Dispatcher etc). Isso e ortogonal a Roaming Throne (que so dobra
  gatilhos de CRIATURA em campo, nunca gatilho de spell na pilha).
- 2a habilidade: copia o SPELL colorless em si ao ser conjurado
  (incondicional, sem pagar nada) — empilha com a copia paga da Ulalek
  se as duas estiverem em campo (2 gatilhos de copia independentes = ate
  3 corpos totais de um permanente colorless caro, alem da copia
  original).

======================================================================
Roaming Throne — tipo escolhido: Eldrazi
======================================================================
Obvio e central pro tema — MAS, ao contrario do Ur-Dragon (onde o
gatilho de ataque da propria comandante era Dragao e levava a maior
parte do valor), aqui a comandante e a maioria dos motores de valor
disparam no CAST (nao em permanente-em-campo), e Roaming Throne SO dobra
gatilhos de criatura EM CAMPO — nunca gatilho de conjuracao. Achado real
documentado no goldfish-log: Roaming Throne e uma peca bem mais fraca
neste deck do que no Ur-Dragon, porque a maior parte do valor de Ulalek
e cast-trigger, nao permanente-trigger. Na pratica dobra: Glaring
Fleshraker (as DUAS habilidades reais — "voce conjura colorless: cria
spawn" E "outra criatura colorless entra: 1 dano proxy" — fonte e o
proprio Fleshraker EM CAMPO em ambas, entao as duas contam), Chittering
Dispatcher (leaves-trigger), Spawnbed Protector (end step). NAO dobra
Liberator, Urza's Battlethopter (tipo Thopter, nao Eldrazi) nem nenhum
"when you cast this spell" (fonte e spell, nao criatura em campo).

======================================================================
Zhulodok, Void Gorger — cascade cascade
======================================================================
"Colorless spells you cast from your hand with mana value 7 or greater
have Cascade, cascade." Implementado como busca real na biblioteca
(exila ate achar nao-terreno de MV menor, poe embaixo o resto — ordem
simplificada, nao randomizada, documentado) — carta achada e conjurada
de graca via o MESMO pipeline de `resolve_cast`, entao pode re-disparar
Ulalek/Echoes recursivamente (comportamento real das cartas, nao um
teto artificial; ha um cap de seguranca de profundidade 8 só como
salvaguarda contra bug, nunca esperado ser atingido em jogo real).

======================================================================
Warp — Anticausal Vestige
======================================================================
"Warp {4}": pode ser conjurada da mao pelo custo de warp; e exilada no
proximo end step, podendo ser conjurada da exilada depois. Implementado
de verdade (nao decorativo): sempre usa o modo warp quando conjurada da
mao (estritamente mais barato, escolha greedy correta pra um goldfish),
e o end step exila e dispara o leaves-trigger real (compra 1 carta, pode
colocar um permanente MV <= terrenos da mao em campo tapped) — depois
disponivel pra reconjurar da zona de exilio (custo cheio, sem novo warp,
evita loop).

======================================================================
All Is Dust — wipe assimetrico real
======================================================================
"Each player sacrifices all permanents they control that are one or
mais colors." So sacrifica NOSSOS permanentes coloridos. Checagem real
contra `colors` do Scryfall (nao contra pips do custo — Devoid muda a
cor real da carta pra incolor mesmo com pips coloridos no custo,
diferenca que importa aqui). Neste deck, checado carta a carta: SO
Defense of the Heart (G) e Rhystic Study (U) sao permanentes coloridos
em toda a lista de 100 cartas — o resto (mesmo com pips coloridos tipo
Sowing Mycospawn {3}{G} ou World Breaker {6}{G}) e Devoid = incolor de
verdade. Entao o pior caso realista pra nos mesmos e sacrificar 0-2
permanentes, validando a tese da auditoria de "wipe assimetrico" com
numero real, nao estimado.

======================================================================
Rodada ampliada — categorias 10-13 (achado real 2026-08-31)
======================================================================
Pedido explicito do usuario: aplicar a checklist ampliada (categorias
10-13 de `references/goldfish-sim-card-rules.md`) a este deck pela
primeira vez — as categorias 1-9 ja tinham sido auditadas em 2026-08-28.

- **Categoria 11 (multi-face) e categoria 13 (Classe/Saga): N/A
  confirmado.** Varredura programatica das 100 cartas de `lista.md`
  contra `scryfall-cache/oracle-cache.json` (nome exato + campos
  `mana_cost`/`oracle_text`/`type_line`) nao achou nenhuma carta com "//"
  no nome, nenhum `card_faces`, e nenhum `type_line` contendo "Class" ou
  "Saga". Nenhuma implementacao necessaria, so' documentacao.
- **Categoria 12 (planeswalker): Ugin, the Ineffable.** ZERO
  `state.loyalty` existia no arquivo antes desta correcao. Implementado
  de verdade — ver `do_ugin_loyalty()` mais abaixo pra oraculo real,
  heuristica documentada (sempre +1; -3 disponivel mas sem alvo colorido
  de oponente real neste goldfish solo) e efeitos (token Spirit 2/2,
  carta exilada presa em exilio).
- **Categoria 10 (metricas basicas): RECURSION, RAMP e
  FINISHER/LETHALITY nunca tinham linha propria no relatorio.**
  RECURSION existia de fato desde 2026-08-28 (Spawnbed Protector
  retornando carta do cemiterio pra mao), mas nunca virava metrica
  reportada — corrigido, e um 2o gap real foi achado durante essa
  varredura: **World Breaker** ("{2}{C}, Sacrifice a land: Return this
  card from your graveyard to your hand.") tinha SO' o cast-trigger
  implementado, a habilidade de recursao 100% ausente — implementada via
  `do_world_breaker_recursion()`. FINISHER/LETHALITY implementada via
  tag "finisher" nas 8 criaturas MV>=9 (mesmo conjunto ja citado em
  `auditoria.md` secao 2). RAMP ganhou uma linha agregada
  (`ramp_pieces_resolved_total`) e as amostras de mana por turno
  (`true_c_capacity_samples`/`total_mana_samples`, coletadas desde
  2026-08-30 mas NUNCA impressas no relatorio) finalmente aparecem no
  `run_batch()`.
- **Limitacao conhecida, fora de escopo desta rodada:** o motor de copia
  (Ulalek/Echoes) nao aplica a "legend rule" a copias-token de
  permanentes lendarios (Kozilek x3, Ulamog x2, Emrakul, Zhulodok,
  Morophon, e agora potencialmente Ugin via Echoes) — uma copia de um
  permanente lendario deveria forcar o sacrificio de um dos dois pela
  regra real (CR 704.5j). Isso ja era assim antes desta rodada (mesmo
  comportamento documentado e aceito em multiplas sessoes anteriores,
  ex: "Kozilek Butcher... 2 corpos 10/10 EM CAMPO" no goldfish-log) —
  corrigir agora mudaria numeros do motor central ja validados em varias
  rodadas sem pedido explicito do usuario pra essa mudanca especifica.
  Documentado aqui como achado real desta auditoria, nao corrigido.

======================================================================
Simplificacoes documentadas (nao inventadas — omissoes explicitas)
======================================================================
- Modelo de mana GENERICO/TOTAL (mesma convencao de Nekusar/Ur-
  Dragon/Maralen) — nao rastreia pip a pip. Dano de vida de manabase
  (painlands, City of Brass, Mana Confluence, Ancient Tomb, Talismans)
  NAO e rastreado — o modelo generico nao atribui mana a uma fonte
  especifica, entao nao ha como contar isso com fidelidade sem
  reconstruir o modelo inteiro. Custo real conhecido do deck, nao
  quantificado aqui.
- Eldrazi Temple / Cascading Cataracts / Shrine of the Forsaken Gods:
  suas habilidades de mana RESTRITA (so pra Eldrazi/spells colorless, ou
  condicional a 7+ terrenos) sao tratadas como terreno generico de 1 mana
  — mesma convencao de fetchland-como-generico usada nos outros
  simuladores.
- Ancient Tomb: SEM excecao, modelado como 2 mana generica (unico bonus
  de terreno explicitamente modelado, pela magnitude e por nao depender
  de condicao).
- Defense of the Heart: condicao "oponente controla 3+ criaturas" nunca
  e assumida verdadeira (Regra 1 — sem oponente real modelado, nao
  inventar comportamento alheio). Nunca dispara neste simulador.
- Sire of Stagnation: gatilho depende de terreno de OPONENTE entrando —
  nunca dispara (mesmo motivo).
- Void Grafter (ETB hexproof): sem oponente/remocao real modelada pra
  proteger contra — 📊 estrutural, nao um julgamento de valor.
- Liberator, Urza's Battlethopter ("+1/+1 counter sempre que voce
  conjura magia com custo pago > power do Liberator"): exigiria rastrear
  o power dele contador-a-contador pra comparar contra cada gasto de mana
  futuro — mesma classe de limite ja documentada (sem P/T por criatura
  individual neste modelo). NAO implementado por essa razao estrutural,
  nao por baixo valor esperado.
- Ruins of Oran-Rief: 2a habilidade (contador +1/+1 em colorless que
  entrou no turno) implementada em 2026-09-01, ver `try_ruins_oran_rief()`
  abaixo — contador agregado, nao aplicado a P/T real de nenhuma criatura
  especifica (mesmo limite estrutural do resto do arquivo).
- Achado real 2026-08-28 (auditoria de checklist de mecanica): a linha
  anterior desta lista tratava Urza's Cave/Sanctum of Ugin/Eye of Ugin
  como "ativacoes pagas (exilar topo)" — isso e' o texto real de OUTRA
  carta (Mystic Forge), nao dessas 3. Corrigido: Sanctum of Ugin
  implementado de verdade (gatilho gratis, tutor pra mao ao conjurar
  spell colorless MV7+ — ver `on_any_spell_cast_hooks`). Urza's Cave
  ({3},{T},sac: busca land pro campo) e Eye of Ugin ({7},{T}: busca
  criatura colorless pra mao, alem do desconto de custo pra Eldrazi
  colorless) implementados de verdade em 2026-09-01
  (`try_urzas_cave()`/`try_eye_of_ugin()`, achado na leitura linha-a-linha
  completa) — o desconto estatico da Eye of Ugin ja era coberto por nome
  em `eldrazi_cost_discount()` desde antes, so a ativada faltava.
- Ruins of Oran-Rief tambem tinha uma 2a habilidade real ("{T}: +1/+1 em
  colorless que entrou este turno", mutuamente exclusiva com a mana {C}
  basica) nunca implementada — corrigido em `try_ruins_oran_rief()`
  (2026-09-01), contador agregado, sem P/T por criatura (mesma convencao
  ja documentada nesta lista). Simplificacao: so conta criaturas
  conjuradas via `resolve_cast`/`creature_etb_hooks`, nao cobre
  Spawn/Scion/Manifest tokens criados fora desse fluxo.
- Mystic Forge: implementado o essencial (pode conjurar do topo da
  biblioteca se for artifact ou colorless) — a habilidade de tap-exilar
  topo por 1 de vida NAO e modelada.
- The One Ring: burden counters + draw real implementados; perda de
  vida por upkeep tambem. Protecao "from everything" no ETB nao tem
  efeito modelavel (sem oponente/combate real).
- Removal/contramagica (Abstruse Appropriation, Beast Within, Swan Song,
  Swords to Plowshares, Toxic Deluge, Null Elemental Blast, Not of This
  World, An Offer You Can't Refuse, Warping Wail, Eldritch Immunity,
  Ugin's Binding, Eldrazi Confluence, Ulamog exile/destroy, World
  Breaker exile, Flayer of Loyalties, Emrakul) — sem alvo real (nenhum
  oponente modelado), tratadas como PROXY: conjuradas quando ha mana
  sobrando (contribuem pra metricas de interacao/remocao), sem efeito
  colateral em nosso proprio campo.
- Leaves-the-battlefield triggers (Anticausal Vestige fora do warp,
  Chittering Dispatcher) so disparam nos casos onde este simulador
  efetivamente causa a saida (o proprio warp da Vestige) — sem remocao
  real de oponente, nao ha outro jeito de examinar isso.
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


COMMANDER = "Ulalek, Fused Atrocity"
add(COMMANDER, 5, "creature", {"commander", "eldrazi", "colorless"})

ROAMING_THRONE_TYPE = "eldrazi"
UGIN_NAME = "Ugin, the Ineffable"

# --- Terrenos (37) ---------------------------------------------------------
for n in ["Adarkar Wastes", "Badlands", "Bayou", "Brushland", "Cascading Cataracts",
          "Cavern of Souls", "Caves of Koilos", "City of Brass", "Command Tower",
          "Corrupted Crossroads", "Eldrazi Temple", "Emergence Zone", "Exotic Orchard",
          "Eye of Ugin", "Karplusan Forest", "Llanowar Wastes", "Mana Confluence",
          "Plateau", "Reflecting Pool", "Ruins of Oran-Rief", "Sanctum of Ugin",
          "Savannah", "Scrubland", "Shivan Reef", "Shrine of the Forsaken Gods",
          "Sulfurous Springs", "Taiga", "Tropical Island", "Tundra", "Underground Sea",
          "Urza's Cave", "Volcanic Island", "Wastes", "Yavimaya Coast",
          "Ugin's Labyrinth", "Spawning Bed"]:
    add(n, 0, "land", {"colorless"})
add("Ancient Tomb", 0, "land", {"colorless", "tomb2"})

# --- Rampa / rocks -----------------------------------------------------------
add("Arcane Signet", 2, "artifact", {"colorless", "rock1"})
add("Sol Ring", 1, "artifact", {"colorless", "rock2"})
add("Thran Dynamo", 4, "artifact", {"colorless", "rock3"})
add("Talisman of Dominance", 2, "artifact", {"colorless", "rock1"})
add("Talisman of Impulse", 2, "artifact", {"colorless", "rock1"})
add("Talisman of Resilience", 2, "artifact", {"colorless", "rock1"})
add("Farseek", 2, "sorcery", {"land_tutor1"})
add("Nature's Lore", 2, "sorcery", {"land_tutor1"})
add("Three Visits", 2, "sorcery", {"land_tutor1"})
add("Expedition Map", 1, "artifact", {"colorless", "land_tutor_hand_paid"})

# --- Eldrazi com cast-trigger real ------------------------------------------
add("Anticausal Vestige", 6, "creature", {"eldrazi", "colorless", "warp"})
add("Conduit of Ruin", 6, "creature", {"eldrazi", "colorless", "ct_conduit"})
# Radagast of Rhosgobel: NAO esta na lista.md (nao faz parte do deck oficial
# hoje) — cadastrado aqui so pra permitir o teste comparativo com/sem via
# `ulalek_radagast_test.py`. {2}{G}{G}, verde real (colors=['G'], NAO
# colorless — importa pra All Is Dust/Echoes/Roaming Throne) e NAO e
# Eldrazi (Avatar Wizard — nao dispara o gatilho de copia da Ulalek).
# Oraculo real: "The first creature spell you cast each turn costs {2}
# less to cast and can be cast as though it had flash."
add("Radagast of Rhosgobel", 4, "creature", set())
# Tag "finisher": criaturas MV>=9 desta lista, mesmo conjunto de 8 ja
# citado em auditoria.md secao 2 ("multiplos Eldrazi de CMC 9-13: Kozilek
# x3, Ulamog x2, Emrakul, Void Winnower, Flayer of Loyalties") — usado pela
# nova metrica basica obrigatoria FINISHER/LETHALITY (regra 9, categoria
# 10), achado real 2026-08-31 (rodada ampliada): nenhuma linha de
# finisher/lethality existia no relatorio antes desta correcao.
add("Emrakul, the Promised End", 13, "creature", {"eldrazi", "colorless", "ct_emrakul", "finisher"})
add("Flayer of Loyalties", 10, "creature", {"eldrazi", "colorless", "ct_flayer", "finisher"})
add("Kozilek, Butcher of Truth", 10, "creature", {"eldrazi", "colorless", "ct_draw4", "finisher"})
add("Kozilek, the Broken Reality", 9, "creature", {"eldrazi", "colorless", "ct_manifest2", "finisher"})
add("Kozilek, the Great Distortion", 10, "creature", {"eldrazi", "colorless", "ct_draw_to7", "finisher"})
add("Nulldrifter", 7, "creature", {"eldrazi", "colorless", "ct_draw2"})
add("Sowing Mycospawn", 4, "creature", {"eldrazi", "colorless", "ct_land_tutor"})
add("Ulamog, the Ceaseless Hunger", 10, "creature", {"eldrazi", "colorless", "ct_removal2", "finisher"})
add("Ulamog, the Infinite Gyre", 11, "creature", {"eldrazi", "colorless", "ct_removal1", "finisher"})
# World Breaker: achado real 2026-08-31 (rodada ampliada, categoria 10 —
# varredura de recursao). Oraculo real (Scryfall, confirmado via cache):
# "{2}{C}, Sacrifice a land: Return this card from your graveyard to your
# hand." — habilidade ativada de recursao 100% ausente ate agora (so' o
# cast-trigger ct_removal1 estava implementado). Tag "gy_recursion" nova,
# ver do_world_breaker_recursion() abaixo.
add("World Breaker", 7, "creature", {"eldrazi", "colorless", "ct_removal1", "gy_recursion"})
add("Writhing Chrysalis", 4, "creature", {"eldrazi", "colorless", "ct_spawn2"})

# --- Eldrazi sem cast-trigger (corpo / estatico) ----------------------------
add("Sire of Seven Deaths", 7, "creature", {"eldrazi", "colorless"})
add("Sire of Stagnation", 6, "creature", {"eldrazi", "colorless"})
add("Void Winnower", 9, "creature", {"eldrazi", "colorless", "finisher"})

# --- Eldrazi Drones com gatilho de permanente em campo ----------------------
add("Chittering Dispatcher", 3, "creature", {"eldrazi", "colorless", "leaves_spawn"})
add("Glaring Fleshraker", 3, "creature", {"eldrazi", "colorless", "on_colorless_cast_spawn"})
add("It That Heralds the End", 2, "creature", {"eldrazi", "colorless"})
add("Void Grafter", 3, "creature", {"eldrazi", "colorless"})
add("Spawnbed Protector", 7, "creature", {"eldrazi", "colorless", "endstep_recursion"})

# --- Kindred nao-criatura tipo Eldrazi (tambem disparam Ulalek) -------------
add("All Is Dust", 7, "sorcery", {"eldrazi", "colorless"})
add("Echoes of Eternity", 6, "enchantment", {"eldrazi", "colorless"})
add("Eldritch Immunity", 1, "instant", {"eldrazi", "colorless", "interaction"})
add("Not of This World", 7, "instant", {"eldrazi", "colorless", "interaction"})

# --- Motores de valor / consistencia -----------------------------------------
add("Echoes of Eternity", 6, "enchantment", {"eldrazi", "colorless"})  # (redeclarado c/ tag eldrazi acima; mantido por clareza)
add("Forsaken Monument", 5, "artifact", {"colorless", "on_colorless_cast_life"})
add("Kozilek's Unsealing", 3, "enchantment", {"colorless", "on_creature_cast_unsealing"})
add("Morophon, the Boundless", 7, "creature", {"colorless"})
add("Mystic Forge", 4, "artifact", {"colorless", "cast_from_top"})
add("Roaming Throne", 4, "artifact_creature", {ROAMING_THRONE_TYPE, "colorless", "roaming_throne"})
add("The One Ring", 4, "artifact", {"colorless", "one_ring"})
add("Ugin, the Ineffable", 6, "planeswalker", {"colorless", "planeswalker_ugin"})
add("Urza's Incubator", 3, "artifact", {"colorless"})
add("Vedalken Orrery", 4, "artifact", {"colorless", "flash_source"})
add("Liberator, Urza's Battlethopter", 3, "artifact_creature", {"colorless", "flash_source"})
add("Skittering Cicada", 3, "creature", {"colorless", "flash_source"})
add("Zhulodok, Void Gorger", 6, "creature", {"eldrazi", "colorless", "cascade_cascade"})

# --- Removal / interacao / protecao (proxy, sem alvo real) -------------------
add("Abstruse Appropriation", 4, "instant", {"colorless", "interaction"})
add("An Offer You Can't Refuse", 1, "instant", {"interaction"})
add("Beast Within", 3, "instant", {"interaction"})
add("Eladamri's Call", 2, "instant", {"tutor_creature_hand"})
add("Eldrazi Confluence", 4, "instant", {"colorless", "interaction"})
add("Heroic Intervention", 2, "instant", {"interaction"})
add("Null Elemental Blast", 1, "instant", {"colorless", "interaction"})
add("Swan Song", 1, "instant", {"interaction"})
add("Swords to Plowshares", 1, "instant", {"interaction"})
add("Toxic Deluge", 3, "sorcery", {"interaction"})
add("Ugin's Binding", 3, "instant", {"colorless", "interaction"})
add("Warping Wail", 2, "instant", {"colorless", "interaction"})
add("Lightning Greaves", 2, "artifact", {"colorless", "interaction"})

# --- Draw / valor sem cast-trigger especifico ---------------------------------
add("Defense of the Heart", 4, "enchantment", set())  # nunca dispara (Regra 1, ver docstring)
add("Rhystic Study", 3, "enchantment", {"opponent_dependent"})

# --- Tokens sinteticos (nao existem em lista.md, criados em jogo) ------------
add("Eldrazi Spawn Token", 0, "creature", {"colorless", "token"})
add("Manifest Token", 0, "creature", {"colorless", "token"})


CREATURE_ISH = {"creature", "artifact_creature"}
LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}
WARP_COST = {"Anticausal Vestige": 4}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_eldrazi(name: str) -> bool:
    return "eldrazi" in CARD_DB[name].tags


def is_colorless(name: str) -> bool:
    return "colorless" in CARD_DB[name].tags


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
    conduit_used_this_turn: bool = False

    commander_in_play: bool = False
    commander_cast_turn: Optional[int] = None

    warp_pending: list = field(default_factory=list)   # em campo, sera exilado no proximo end step
    warp_exile_zone: list = field(default_factory=list)  # exilado, pode ser reconjurado

    one_ring_burden: int = 0
    spawn_tokens_available: int = 0

    # metrics -------------------------------------------------------------
    ulalek_copies_total: int = 0
    echoes_spell_copies_total: int = 0
    spell_token_copies_total: int = 0
    cast_trigger_extra_resolutions_total: int = 0
    roaming_throne_doubles_total: int = 0
    cards_drawn_extra: int = 0
    tutors_used_total: int = 0
    spawn_tokens_created_total: int = 0
    manifest_tokens_created_total: int = 0
    proxy_removal_total: int = 0
    proxy_life_gained_total: int = 0
    proxy_life_lost_total: int = 0
    interaction_spells_cast_total: int = 0
    cascades_total: int = 0
    cascade_hits_total: int = 0
    all_is_dust_cast: bool = False
    all_is_dust_self_sacrificed: int = 0
    one_ring_cards_drawn_total: int = 0
    library_emptied: bool = False
    flash_online_turns: int = 0
    first_creature_discount_events_total: int = 0
    radagast_flash_grants_total: int = 0
    glaring_fleshraker_damage_total: int = 0
    ulalek_cc_payments_safe: int = 0
    ulalek_cc_payments_risky: int = 0
    ulalek_cc_declined_but_had_true_c: int = 0
    true_c_capacity_samples: list = field(default_factory=list)
    total_mana_samples: list = field(default_factory=list)
    leftover_mana_samples: list = field(default_factory=list)

    # --- Achado real 2026-08-31 (rodada ampliada, categoria 12 da
    # checklist) — lealdade de planeswalker rastreada de verdade. Antes
    # desta correcao, "loyalty" tinha ZERO ocorrencias no arquivo inteiro. ---
    loyalty: dict = field(default_factory=dict)
    ugin_activations_total: int = 0
    ugin_plus1_total: int = 0
    ugin_minus3_skipped_no_target_total: int = 0
    ugin_spirit_tokens_created_total: int = 0
    ugin_cards_exiled_stuck_total: int = 0

    # --- Achado real 2026-08-31 (categoria 10 — metrica basica RECURSION
    # ausente do relatorio, apesar de Spawnbed Protector ja retornar carta
    # do cemiterio pra mao desde a correcao de 2026-08-28). ---
    recursion_events_total: int = 0
    spawnbed_protector_recursion_total: int = 0
    world_breaker_recursion_total: int = 0

    # --- Achado real 2026-08-31 (categoria 10 — metrica basica RAMP nunca
    # tinha uma linha propria/agregada no relatorio). ---
    ramp_pieces_resolved_total: int = 0

    # --- Achado real 2026-08-31 (categoria 10 — metrica basica
    # FINISHER/LETHALITY 100% ausente do relatorio). ---
    finisher_resolved_total: int = 0
    first_finisher_turn: Optional[int] = None

    # --- Achado real 2026-09-01 (leitura linha-a-linha, "compile TUDO"):
    # Eye of Ugin ({7},{T} tutor), Urza's Cave ({3},{T},sac: busca land) e
    # Ruins of Oran-Rief (2a habilidade, +1/+1 em colorless que entrou no
    # turno) estavam entre os 34 terrenos registrados so como
    # add(n, 0, "land", {"colorless"}) generico -- so a mana {C} basica e a
    # reducao estatica de custo da Eye of Ugin (ja tratada por nome em
    # eldrazi_cost_discount) eram cobertas. O proprio docstring do
    # cabecalho ja documentava isso como "decisao de escopo... fica pra
    # uma rodada dedicada" pra Urza's Cave/Eye of Ugin. ---
    eye_of_ugin_used_this_turn: bool = False
    eye_of_ugin_tutors_total: int = 0
    urzas_cave_used: bool = False
    colorless_creature_entered_this_turn: bool = False
    ruins_oran_rief_counters_total: int = 0


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


def create_spawn_tokens(state: GameState, n: int):
    state.spawn_tokens_created_total += n
    # convertidos em mana disponivel no mesmo turno quando uteis (mesma
    # convencao "cria e usa" ja empregada pro Treasure no Ur-Dragon) —
    # tambem existem como corpos 0/1 em campo pra fins de contagem.
    for _ in range(n):
        state.battlefield.append("Eldrazi Spawn Token")
        on_colorless_creature_etb(state, "Eldrazi Spawn Token")
    state.spawn_tokens_available += n


def sac_spawns_for_mana(state: GameState, n: int) -> int:
    use = min(n, state.spawn_tokens_available)
    for _ in range(use):
        if "Eldrazi Spawn Token" in state.battlefield:
            state.battlefield.remove("Eldrazi Spawn Token")
    state.spawn_tokens_available -= use
    state.bonus_mana_pool += use
    return use


# ---------------------------------------------------------------------------
# Trigger multiplier — Echoes of Eternity + Roaming Throne
# ---------------------------------------------------------------------------

def trigger_times(state: GameState, source_name: str, is_permanent_source: bool) -> int:
    """Quantas vezes um gatilho de `source_name` deve resolver.
    `is_permanent_source=False` = gatilho de conjuracao (cast trigger),
    fonte e o spell na pilha -> so Echoes pode dobrar, Roaming Throne NUNCA
    (exige criatura EM CAMPO, nao spell). `is_permanent_source=True` =
    gatilho de um permanente ja em campo -> ambos podem se aplicar."""
    times = 1
    if ("Echoes of Eternity" in state.battlefield and is_colorless(source_name)
            and source_name != "Echoes of Eternity"):
        times += 1
    if (is_permanent_source and "Roaming Throne" in state.battlefield
            and source_name != "Roaming Throne"
            and is_creature_card(source_name) and is_eldrazi(source_name)):
        times += 1
        state.roaming_throne_doubles_total += 1
    return times


def on_colorless_creature_etb(state: GameState, name: str):
    """Glaring Fleshraker, 2a habilidade (real, achada na reconfirmacao de
    oraculo 2026-08-30): "Whenever another colorless creature you control
    enters, this creature deals 1 damage to each opponent." So' a 1a
    habilidade (spawn token ao CONJURAR spell colorless) estava
    implementada antes - esta e' uma criatura ENTRANDO (qualquer criatura
    colorless, incluindo Eldrazi Spawn/Scion e Manifest tokens, nao so'
    spells conjurados), e nunca tinha sido despachada nem documentada como
    omissao. Sem oponente real (Regra 1), tratada como proxy de dano —
    mesma convencao de proxy_removal_total."""
    if ("Glaring Fleshraker" in state.battlefield and name != "Glaring Fleshraker"
            and name in CARD_DB and is_colorless(name)):
        times = trigger_times(state, "Glaring Fleshraker", is_permanent_source=True)
        state.glaring_fleshraker_damage_total += 1 * times
    if name in CARD_DB and is_colorless(name):
        # Ruins of Oran-Rief: "{T}: Put a +1/+1 counter on target colorless
        # creature that entered this turn." Ver try_ruins_oran_rief().
        state.colorless_creature_entered_this_turn = True


# ---------------------------------------------------------------------------
# Cast-trigger effects ("When you cast this spell")
# ---------------------------------------------------------------------------

def ct_conduit(state: GameState):
    pool = [n for n in state.library if is_creature_card(n) and is_colorless(n) and CARD_DB[n].mv >= 7]
    if pool:
        best = max(pool, key=lambda n: CARD_DB[n].mv)
        state.library.remove(best)
        state.library.insert(0, best)
        state.tutors_used_total += 1


def ct_emrakul(state: GameState):
    state.proxy_removal_total += 0  # mind-control + extra turn: sem oponente real, so nota o evento
    state.tutors_used_total += 0


def ct_flayer(state: GameState):
    state.proxy_removal_total += 0  # rouba criatura ate o final do turno: proxy, sem alvo real


def ct_draw4(state: GameState):
    draw_cards(state, 4)


def ct_manifest2(state: GameState):
    n = min(2, len(state.hand))
    for _ in range(n):
        c = state.hand.pop(0)
        state.battlefield.append("Manifest Token")
        on_colorless_creature_etb(state, "Manifest Token")
        state.manifest_tokens_created_total += 1
        state.graveyard.append(c) if False else None  # a carta manifestada NAO vai pro cemiterio, fica face-down em campo (Manifest Token representa isso; a carta original "desaparece" do modelo, simplificacao documentada)
    draw_cards(state, n)


def ct_draw_to7(state: GameState):
    if len(state.hand) < 7:
        draw_cards(state, 7 - len(state.hand))


def ct_draw2(state: GameState):
    draw_cards(state, 2)


def ct_land_tutor(state: GameState):
    candidates = [n for n in state.library if n in LAND_NAMES]
    if candidates:
        pick = candidates[0]
        state.library.remove(pick)
        state.battlefield.append(pick)
        state.ramp_pieces_resolved_total += 1  # RAMP (categoria 10): Sowing Mycospawn


def ct_removal2(state: GameState):
    state.proxy_removal_total += 2


def ct_removal1(state: GameState):
    state.proxy_removal_total += 1


def ct_spawn2(state: GameState):
    create_spawn_tokens(state, 2)


CAST_TRIGGER_FNS = {
    "ct_conduit": ct_conduit,
    "ct_emrakul": ct_emrakul,
    "ct_flayer": ct_flayer,
    "ct_draw4": ct_draw4,
    "ct_manifest2": ct_manifest2,
    "ct_draw_to7": ct_draw_to7,
    "ct_draw2": ct_draw2,
    "ct_land_tutor": ct_land_tutor,
    "ct_removal2": ct_removal2,
    "ct_removal1": ct_removal1,
    "ct_spawn2": ct_spawn2,
}


def cast_trigger_fn_for(name: str):
    for tag in CARD_DB[name].tags:
        if tag in CAST_TRIGGER_FNS:
            return CAST_TRIGGER_FNS[tag]
    return None


# ---------------------------------------------------------------------------
# Gatilhos de permanente-em-campo reagindo a QUALQUER carta conjurada
# ---------------------------------------------------------------------------

def on_any_spell_cast_hooks(state: GameState, name: str, colorless: bool, mv: int, ctype: str):
    if colorless and "Forsaken Monument" in state.battlefield:
        # Forsaken Monument e artifact, nao criatura -> Roaming Throne nunca
        # dobra este gatilho (trigger_times so aplicaria se fosse criatura
        # Eldrazi); so Echoes pode dobrar aqui.
        times = trigger_times(state, "Forsaken Monument", is_permanent_source=True)
        state.proxy_life_gained_total += 2 * times

    if colorless and "Glaring Fleshraker" in state.battlefield and name != "Glaring Fleshraker":
        times = trigger_times(state, "Glaring Fleshraker", is_permanent_source=True)
        create_spawn_tokens(state, 1 * times)

    if "Kozilek's Unsealing" in state.battlefield and ctype == "creature":
        times = trigger_times(state, "Kozilek's Unsealing", is_permanent_source=True)
        if mv in (4, 5, 6):
            create_spawn_tokens(state, 2 * times)
        elif mv >= 7:
            for _ in range(times):
                draw_cards(state, 3)

    # Sanctum of Ugin: "Whenever you cast a colorless spell with mana
    # value 7 or greater, you may sacrifice this land. If you do, search
    # your library for a colorless creature card, reveal it, put it into
    # your hand." Achado real 2026-08-28 (auditoria de checklist de
    # mecanica): o docstring do arquivo mischaracterizava isso como
    # "ativacao paga (exilar topo)" - texto real de OUTRA carta (Mystic
    # Forge). Sanctum e' um gatilho GRATIS, e esse deck e' centrado em
    # conjurar spells colorless MV7+ - implementado de verdade (tutor pra
    # mao). Sempre sacrifica quando disponivel (valor imediato > land drop
    # perdido, mesma filosofia agressiva ja usada no resto do motor).
    if "Sanctum of Ugin" in state.battlefield and colorless and mv >= 7:
        state.battlefield.remove("Sanctum of Ugin")
        pool = [n for n in state.library if is_creature_card(n) and is_colorless(n)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.library.remove(best)
            state.hand.append(best)
            state.tutors_used_total += 1


# ---------------------------------------------------------------------------
# Mana
# ---------------------------------------------------------------------------

def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    if "Arcane Signet" in state.battlefield:
        total += 1
    if "Thran Dynamo" in state.battlefield:
        total += 3
    total += sum(1 for n in state.battlefield if n in
                 ("Talisman of Dominance", "Talisman of Impulse", "Talisman of Resilience"))
    return total


def land_mana(state: GameState) -> int:
    total = sum(1 for n in state.battlefield if n in LAND_NAMES)
    total += sum(1 for n in state.battlefield if n == "Ancient Tomb")  # +1 extra (total 2)
    return total


# Fontes que realmente tapam por {C} de verdade no oraculo (conferido carta a
# carta, Scryfall) - a tag "colorless" nos 37 terrenos deste arquivo so
# significa "contado genericamente neste modelo", nao "produz {C} de
# verdade". Usado so por forsaken_monument_bonus() abaixo, que precisa saber
# exatamente quais fontes tapam por {C} pra dobrar direito.
#
# Correcao 2026-08-30 (reconfirmacao de oraculo pedida pelo usuario): os 10
# duais ABUR (Badlands, Bayou, Plateau, Savannah, Scrubland, Taiga, Tropical
# Island, Tundra, Underground Sea, Volcanic Island) de fato NAO tem modo
# {C} - so produzem as 2 cores nomeadas. MAS os 8 painlands da lista
# (Adarkar Wastes, Brushland, Caves of Koilos, Karplusan Forest, Llanowar
# Wastes, Shivan Reef, Sulfurous Springs, Yavimaya Coast) SIM tem um modo
# "{T}: Add {C}." incondicional e sem custo de vida, alem do modo colorido
# com dano - confirmado carta a carta via Scryfall fresco, nao por
# semelhanca com os duais ABUR. Faltavam todos os 8 aqui, subestimando o
# bonus de Forsaken Monument sempre que algum estava em campo.
TRUE_C_LANDS = {"Eldrazi Temple", "Cascading Cataracts", "Wastes", "Shrine of the Forsaken Gods",
                 "Ugin's Labyrinth", "Spawning Bed", "Urza's Cave", "Cavern of Souls",
                 "Corrupted Crossroads", "Sanctum of Ugin", "Emergence Zone",
                 "Adarkar Wastes", "Brushland", "Caves of Koilos", "Karplusan Forest",
                 "Llanowar Wastes", "Shivan Reef", "Sulfurous Springs", "Yavimaya Coast"}


def forsaken_monument_bonus(state: GameState) -> int:
    """Forsaken Monument: "Whenever you tap a permanent for {C}, add an
    additional {C}." Achado real 2026-08-28 (auditoria de checklist de
    mecanica): so' a metade "gain 2 life ao conjurar spell colorless" era
    modelada - essa dobra de mana (a habilidade mais impactante das 3
    reais da carta) nunca existia. So' aplica a fontes que REALMENTE
    tapam por {C} (ver TRUE_C_LANDS acima) - a maioria dos terrenos deste
    deck produz cor real, nao {C}, e nao e' afetada."""
    if "Forsaken Monument" not in state.battlefield:
        return 0
    bonus = sum(1 for n in state.battlefield if n in TRUE_C_LANDS)  # cada uma tapa por 1 {C} -> +1
    if "Ancient Tomb" in state.battlefield:
        bonus += 2  # tapa por {C}{C} -> +2
    if "Sol Ring" in state.battlefield:
        bonus += 2  # tapa por {C}{C} -> +2
    if "Thran Dynamo" in state.battlefield:
        bonus += 3  # tapa por {C}{C}{C} -> +3
    bonus += sum(1 for n in state.battlefield if n in
                 ("Talisman of Dominance", "Talisman of Impulse", "Talisman of Resilience"))  # {C} cada -> +1
    return bonus


def true_colorless_capacity(state: GameState) -> int:
    """Quanto mana {C} de VERDADE (nao generico) esta disponivel neste
    momento, somando so as fontes que realmente tapam por {C} (TRUE_C_LANDS
    + Ancient Tomb {C}{C} + Sol Ring {C}{C} + Thran Dynamo {C}{C}{C} +
    Talismans {C} cada + Eldrazi Spawn/Scion tokens disponiveis pra
    sacrificar por {C}) - NAO inclui Forsaken Monument (esse e' um bonus
    condicional, ja contado por forsaken_monument_bonus() separadamente).
    Adicionado 2026-08-30 a pedido do usuario, pra medir se o aperto de
    mana incolor sentido em jogo real (pra pagar o {C}{C} da Ulalek, ou
    ativar algo tipo Strionic Resonator/Peter Parker's Camera) e' um
    problema sistematico do deck ou so' de maos especificas. O modelo
    principal usa mana generica/fungivel (convencao do repositorio inteiro
    - nao rastreia pip a pip) - esta funcao e' uma medida PARALELA e
    aproximada: conta a CAPACIDADE de {C} real que existe em campo,
    independente de quanto dela ja foi "gasta" genericamente nesse turno
    (o modelo nao sabe DE QUAL fonte especifica cada gasto saiu). Trate
    como um teto otimista de {C} disponivel, nao um numero garantido."""
    total = sum(1 for n in state.battlefield if n in TRUE_C_LANDS)
    if "Ancient Tomb" in state.battlefield:
        total += 2
    if "Sol Ring" in state.battlefield:
        total += 2
    if "Thran Dynamo" in state.battlefield:
        total += 3
    total += sum(1 for n in state.battlefield if n in
                 ("Talisman of Dominance", "Talisman of Impulse", "Talisman of Resilience"))
    total += state.spawn_tokens_available
    return total


def total_mana(state: GameState) -> int:
    return land_mana(state) + rocks_mana(state) + state.bonus_mana_pool + forsaken_monument_bonus(state)


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


# Fontes de "o primeiro creature spell que voce conjura no turno custa {2}
# a menos" — Conduit of Ruin (na lista) e, opcionalmente pro teste
# comparativo, Radagast of Rhosgobel (mesmo texto, so muda "and can be cast
# as though it had flash" no final). Empilham no MESMO gatilho (a mesma
# criatura, se for a primeira do turno, recebe -2 de cada fonte presente),
# nao dobram quantas criaturas por turno sao descontadas.
FIRST_CREATURE_DISCOUNT_SOURCES = ["Conduit of Ruin", "Radagast of Rhosgobel"]


def graveyard_card_types(state: GameState) -> set:
    """Tipos de carta distintos no cemiterio (regra real de Emrakul, the
    Promised End abaixo) - artifact_creature conta como Artifact E
    Creature ao mesmo tempo (tipo real da carta, nao categoria unica do
    modelo)."""
    types = set()
    for n in state.graveyard:
        ctype = CARD_DB[n].ctype
        if ctype == "artifact_creature":
            types.add("artifact")
            types.add("creature")
        else:
            types.add(ctype)
    return types


def eldrazi_cost_discount(state: GameState, name: str) -> int:
    d = 0
    tags = CARD_DB[name].tags
    if "eldrazi" in tags:
        if "Eye of Ugin" in state.battlefield:
            d += 2
        if "Urza's Incubator" in state.battlefield and CARD_DB[name].ctype == "creature":
            d += 2
    if "colorless" in tags:
        if "Ugin, the Ineffable" in state.battlefield:
            d += 2
        if "It That Heralds the End" in state.battlefield and CARD_DB[name].mv >= 7:
            d += 1
    if name == "Emrakul, the Promised End":
        # Achado real 2026-08-30 (reconfirmacao de oraculo pedida pelo
        # usuario): "This spell costs {1} less to cast for each card type
        # among cards in your graveyard." Nunca era aplicado - Emrakul
        # ficava sempre travada no custo cheio de 13, quando na pratica
        # (ate 7 tipos: creature/artifact/enchantment/instant/sorcery/
        # planeswalker/land) pode custar bem menos num jogo real com
        # cemiterio desenvolvido. Empilha com os descontos acima (regras
        # reais permitem multiplas reducoes de custo simultaneas).
        d += len(graveyard_card_types(state))
    if CARD_DB[name].ctype == "creature" and not state.conduit_used_this_turn:
        d += 2 * sum(1 for s in FIRST_CREATURE_DISCOUNT_SOURCES if s in state.battlefield)
    return d


def effective_cost(state: GameState, name: str) -> int:
    d = eldrazi_cost_discount(state, name)
    if name in WARP_COST:
        return max(0, WARP_COST[name] - d)
    return max(0, CARD_DB[name].mv - d)


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name)


# ---------------------------------------------------------------------------
# Resolucao de spell (permanente entra / instant-sorcery resolve)
# ---------------------------------------------------------------------------

def resolve_instant_sorcery_effect(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if "land_tutor1" in tags:
        candidates = [n for n in state.library if n in LAND_NAMES]
        if candidates:
            pick = candidates[0]
            state.library.remove(pick)
            state.battlefield.append(pick)
            state.ramp_pieces_resolved_total += 1  # RAMP (categoria 10): Farseek/Nature's Lore/Three Visits
    elif "tutor_creature_hand" in tags:
        pool = [n for n in state.library if is_creature_card(n)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.library.remove(best)
            state.hand.append(best)
            state.tutors_used_total += 1
    elif name == "All Is Dust":
        colored = [n for n in state.battlefield if n not in LAND_NAMES and not is_colorless(n)]
        for n in colored:
            state.battlefield.remove(n)
            state.graveyard.append(n)
        state.all_is_dust_cast = True
        state.all_is_dust_self_sacrificed += len(colored)
    elif "interaction" in tags:
        state.interaction_spells_cast_total += 1


def enter_battlefield(state: GameState, name: str, is_token: bool = False):
    state.battlefield.append(name)
    if name == COMMANDER:
        state.commander_in_play = True
        if state.commander_cast_turn is None:
            state.commander_cast_turn = state.turn
    if is_creature_card(name) and "leaves_spawn" in CARD_DB[name].tags:
        pass  # tratado quando sair de campo — nunca modelado sem remocao real (ver docstring)
    if name == "The One Ring" and not is_token:
        pass  # protecao ETB sem efeito modelavel

    tags = CARD_DB[name].tags
    # Ugin, the Ineffable: lealdade inicial real (Scryfall: "loyalty": "4").
    # Se uma copia (token, via Echoes de Eternity — Ugin e' colorless de
    # verdade) entrar depois, o dict e' por NOME e simplesmente reseta pra
    # 4 de novo — mesma convencao ja aceita no resto do arquivo pra copias
    # de permanentes lendarios (Kozilek/Ulamog/Zhulodok ja documentados nas
    # rodadas anteriores como "2 corpos em campo", sem enforcement de legend
    # rule neste modelo — fora de escopo mudar isso agora, mudaria numeros
    # ja validados em multiplas rodadas anteriores do motor de copia).
    if "planeswalker_ugin" in tags:
        state.loyalty[UGIN_NAME] = 4

    # RAMP (categoria 10): mana rocks resolvendo como permanente contam
    # como peca de ramp real (Sol Ring/Arcane Signet/Talismans/Thran
    # Dynamo).
    if tags & {"rock1", "rock2", "rock3"}:
        state.ramp_pieces_resolved_total += 1

    # FINISHER/LETHALITY (categoria 10): tag "finisher" = 8 criaturas
    # MV>=9 (Emrakul, Flayer of Loyalties, Kozilek x3, Ulamog x2, Void
    # Winnower — mesmo conjunto ja citado em auditoria.md secao 2).
    # Conta reais + copias (spell_token_copies via Echoes/Ulalek) +
    # cascade hits, ja que todos passam por aqui.
    if "finisher" in tags:
        state.finisher_resolved_total += 1
        if state.first_finisher_turn is None:
            state.first_finisher_turn = state.turn


def do_cascade(state: GameState, x: int, depth: int = 0):
    if depth > 8 or not state.library:
        return
    state.cascades_total += 1
    exiled = []
    found = None
    while state.library:
        c = state.library.pop(0)
        if c not in LAND_NAMES and CARD_DB[c].mv < x:
            found = c
            break
        exiled.append(c)
    state.library.extend(exiled)  # simplificado: ordem preservada, nao randomizada
    if found:
        state.cascade_hits_total += 1
        resolve_cast(state, found, free=True, from_hand=False)


def resolve_cast(state: GameState, name: str, free: bool = False, from_hand: bool = True, warp_mode: bool = False):
    """Resolve conjurar `name`: paga mana (a menos que `free`), remove da
    mao/exilio se aplicavel, dispara cast-trigger + copias de Echoes/Ulalek,
    entao resolve o spell em si (com sua propria contagem de copias)."""
    card = CARD_DB[name]
    colorless = is_colorless(name)
    eldrazi = is_eldrazi(name)
    mv = card.mv

    if not free:
        cost = WARP_COST[name] if warp_mode else effective_cost(state, name)
        cost = max(0, cost - (eldrazi_cost_discount(state, name) if warp_mode else 0)) if warp_mode else cost
        spend_mana(state, cost)
    if from_hand and name in state.hand:
        state.hand.remove(name)
    elif not from_hand and name in state.warp_exile_zone:
        state.warp_exile_zone.remove(name)

    if card.ctype == "creature" and not state.conduit_used_this_turn:
        sources_in_play = [s for s in FIRST_CREATURE_DISCOUNT_SOURCES if s in state.battlefield]
        if sources_in_play:
            state.first_creature_discount_events_total += 1
        if "Radagast of Rhosgobel" in sources_in_play:
            # Radagast tambem da flash pra essa conjuracao especifica ("and
            # can be cast as though it had flash") — metrica direta e causal,
            # separada de flash_online_turns (que so cobre Vedalken
            # Orrery/Liberator/Skittering Cicada, cujo flash e incondicional
            # pra qualquer spell, ao contrario do flash condicional/estreito
            # do Radagast, restrito a essa unica criatura por turno).
            state.radagast_flash_grants_total += 1
        state.conduit_used_this_turn = True

    # --- Ulalek: pode pagar CC se for Eldrazi ---
    ulalek_paid = False
    if eldrazi and COMMANDER in state.battlefield:
        true_c = true_colorless_capacity(state)
        if remaining_mana(state) >= 2:
            spend_mana(state, 2)
            ulalek_paid = True
            state.ulalek_copies_total += 1
            # Medida paralela (2026-08-30, a pedido do usuario): o modelo
            # principal usa mana generica/fungivel, entao "pagou CC" aqui
            # so' checa TOTAL >= 2, nao se a mana e' realmente {C}. Marca
            # como "risky" quando a capacidade REAL de {C} em campo (fontes
            # que tapam por {C} de verdade + Spawn/Scion disponiveis) e'
            # menor que 2 no momento do pagamento - sinal de que, numa mesa
            # real com pips de verdade, esse pagamento pode nao ser legal
            # dependendo de quais fontes ja foram gastas em outras coisas.
            if true_c >= 2:
                state.ulalek_cc_payments_safe += 1
            else:
                state.ulalek_cc_payments_risky += 1
        elif true_c >= 2:
            # Modelo NAO pagou (mana generica total insuficiente), mas a
            # capacidade real de {C} ainda estava disponivel - sinal do
            # sentido oposto: um jogador real, guardando as fontes de {C}
            # de proposito, poderia ter pago mesmo aqui.
            state.ulalek_cc_declined_but_had_true_c += 1

    # --- Echoes of Eternity: copia incondicional de spell colorless ---
    echoes_spell_copy = ("Echoes of Eternity" in state.battlefield and colorless
                          and name != "Echoes of Eternity")
    if echoes_spell_copy:
        state.echoes_spell_copies_total += 1

    spell_resolutions = 1 + (1 if echoes_spell_copy else 0) + (1 if ulalek_paid else 0)

    # --- cast-trigger (se houver), dobrado por Echoes (1a habilidade) + Ulalek ---
    ct_fn = cast_trigger_fn_for(name)
    if ct_fn:
        base_times = trigger_times(state, name, is_permanent_source=False)
        total_ct_times = base_times + (1 if ulalek_paid else 0)
        if total_ct_times > 1:
            state.cast_trigger_extra_resolutions_total += (total_ct_times - 1)
        for _ in range(total_ct_times):
            ct_fn(state)

    # gatilhos de OUTROS permanentes reagindo a esta carta sendo conjurada
    on_any_spell_cast_hooks(state, name, colorless, mv, card.ctype)

    # --- resolucao do spell em si (permanente entra / instant-sorcery) ---
    for i in range(spell_resolutions):
        is_copy = i > 0
        if is_copy:
            state.spell_token_copies_total += 1
        if card.ctype in ("instant", "sorcery"):
            resolve_instant_sorcery_effect(state, name)
            if not is_copy and not free:
                state.graveyard.append(name)
            elif not is_copy and free:
                state.graveyard.append(name)  # cascade: carta gratis tambem vai pro cemiterio se nao permanente
        else:
            enter_battlefield(state, name, is_token=is_copy)
            if is_creature_card(name):
                creature_etb_hooks(state, name, is_copy)

    if name == "Zhulodok, Void Gorger":
        pass
    if "cascade_cascade" in card.tags:
        pass  # Zhulodok em campo checado em cascade_check() abaixo, nao aqui

    # Zhulodok: colorless MV>=7 conjurado DA MAO -> cascade, cascade
    if (from_hand and not free and colorless and mv >= 7
            and "Zhulodok, Void Gorger" in state.battlefield):
        do_cascade(state, mv)
        do_cascade(state, mv)

    if warp_mode:
        state.warp_pending.append(name)


def creature_etb_hooks(state: GameState, name: str, is_copy: bool):
    if name == "The One Ring" and not is_copy:
        pass
    on_colorless_creature_etb(state, name)


def cast_card(state: GameState, name: str):
    if name in WARP_COST and name in state.hand:
        resolve_cast(state, name, warp_mode=True)
    elif name in state.warp_exile_zone:
        resolve_cast(state, name, from_hand=False)
    else:
        resolve_cast(state, name, from_hand=True)


def play_land(state: GameState):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    if not lands_in_hand:
        return
    choice = lands_in_hand[0]
    state.hand.remove(choice)
    state.battlefield.append(choice)
    state.lands_played_this_turn += 1


def do_expedition_map(state: GameState):
    if "Expedition Map" not in state.battlefield or remaining_mana(state) < 2:
        return
    candidates = [n for n in state.library if n in LAND_NAMES]
    if not candidates:
        return
    spend_mana(state, 2)
    pick = candidates[0]
    state.library.remove(pick)
    state.hand.append(pick)
    state.battlefield.remove("Expedition Map")
    state.ramp_pieces_resolved_total += 1  # RAMP (categoria 10): Expedition Map


def try_eye_of_ugin(state: GameState):
    """Achado real 2026-09-01 (leitura linha-a-linha, "compile TUDO"): Eye
    of Ugin estava registrada so como terreno {C} generico (loop de 34
    terrenos) -- a reducao estatica de custo ("Colorless Eldrazi spells
    you cast cost {2} less") ja era tratada por nome em
    eldrazi_cost_discount(), mas a 2a habilidade real, "{7}, {T}: Search
    your library for a colorless creature card, reveal it, put it into
    your hand, then shuffle", nunca foi implementada -- o proprio
    docstring do cabecalho ja documentava isso como "decisao de escopo...
    fica pra uma rodada dedicada"."""
    if "Eye of Ugin" not in state.battlefield or state.eye_of_ugin_used_this_turn:
        return
    if remaining_mana(state) < 7:
        return
    pool = [n for n in state.library if is_creature_card(n) and is_colorless(n)]
    if not pool:
        return
    spend_mana(state, 7)
    state.eye_of_ugin_used_this_turn = True
    best = max(pool, key=lambda n: CARD_DB[n].mv)
    state.library.remove(best)
    state.hand.append(best)
    state.eye_of_ugin_tutors_total += 1
    state.tutors_used_total += 1


def try_urzas_cave(state: GameState):
    """Achado real 2026-09-01 (mesma auditoria acima): Urza's Cave
    ("{3}, {T}, Sacrifice this land: Search your library for a land card,
    put it onto the battlefield tapped, then shuffle") nunca foi
    implementada -- mesmo tratamento do Eye of Ugin acima. Uso unico por
    partida (a propria habilidade sacrifica o terreno)."""
    if state.urzas_cave_used or "Urza's Cave" not in state.battlefield:
        return
    if remaining_mana(state) < 3:
        return
    if "Ancient Tomb" in state.library:
        fetched = "Ancient Tomb"
    else:
        candidates = [n for n in state.library if n in LAND_NAMES]
        fetched = candidates[0] if candidates else None
    if fetched is None:
        return
    spend_mana(state, 3)
    state.battlefield.remove("Urza's Cave")
    state.urzas_cave_used = True
    state.library.remove(fetched)
    state.battlefield.append(fetched)  # entra tapped -- ja nao produz mana neste turno (nao somado a total_mana ja calculado)
    state.ramp_pieces_resolved_total += 1  # RAMP (categoria 10): Urza's Cave


def try_ruins_oran_rief(state: GameState):
    """Achado real 2026-09-01 (mesma auditoria): Ruins of Oran-Rief tem
    uma 2a habilidade real ("{T}: Put a +1/+1 counter on target colorless
    creature that entered this turn"), mutuamente exclusiva com a mana
    {C} basica no mesmo turno (mesmo {T}) -- nunca implementada, so o
    modo de mana generica era coberto. Simplificacao documentada: so
    dispara pra criaturas coloridas conjuradas via resolve_cast/
    creature_etb_hooks nesse turno (nao cobre tokens Spawn/Scion/Manifest
    criados fora desse fluxo -- este arquivo nao centraliza toda criacao
    de token num unico ponto de entrada). Contador agregado (este
    simulador nao rastreia P/T por criatura individual, mesma convencao
    ja documentada alhures)."""
    if "Ruins of Oran-Rief" not in state.battlefield:
        return
    if not state.colorless_creature_entered_this_turn:
        return
    state.ruins_oran_rief_counters_total += 1


def do_one_ring(state: GameState):
    if "The One Ring" not in state.battlefield:
        return
    state.one_ring_burden += 1
    n = state.one_ring_burden
    draw_cards(state, n)
    state.one_ring_cards_drawn_total += n


def do_world_breaker_recursion(state: GameState):
    """World Breaker: "{2}{C}, Sacrifice a land: Return this card from your
    graveyard to your hand." Achado real 2026-08-31 (rodada ampliada,
    categoria 10 — varredura de RECURSAO): habilidade ativada 100% ausente
    ate agora, so' o cast-trigger (ct_removal1) estava implementado.

    Heuristica documentada: so' ativa quando (a) World Breaker esta no
    cemiterio e NAO ja na mao/campo, (b) ha mana sobrando >= 3 (custo real
    {2}{C}, modelo generico), e (c) ha mais de 5 terrenos em campo — piso
    de seguranca pra nunca sacrificar land que reduza a manabase abaixo de
    5, mesmo greedy. No maximo 1 ativacao por turno neste modelo (nao ha
    ganho em ativar 2x sem recastar entre elas, e recastar tira a carta do
    cemiterio de novo)."""
    if "World Breaker" not in state.graveyard:
        return
    if "World Breaker" in state.hand or "World Breaker" in state.battlefield:
        return
    lands_in_play = [n for n in state.battlefield if n in LAND_NAMES]
    if len(lands_in_play) <= 5:
        return
    if remaining_mana(state) < 3:
        return
    spend_mana(state, 3)
    state.battlefield.remove(lands_in_play[0])
    state.graveyard.remove("World Breaker")
    state.hand.append("World Breaker")
    state.recursion_events_total += 1
    state.world_breaker_recursion_total += 1


def do_ugin_loyalty(state: GameState):
    """Ugin, the Ineffable — CR 606.3 (uma ativacao de lealdade por turno,
    velocidade de feitiço). Achado real 2026-08-31 (rodada ampliada,
    categoria 12): nenhum `state.loyalty` existia no arquivo inteiro (0
    ocorrencias de "loyalty" antes desta correcao), apesar da parte
    estatica do Ugin (desconto de {2} em spells colorless, ver
    `eldrazi_cost_discount`) ja estar correta ha varias rodadas.

    Oraculo real (Scryfall, loyalty inicial 4):
    "Colorless spells you cast cost {2} less to cast.
    +1: Exile the top card of your library face down and look at it.
    Create a 2/2 colorless Spirit creature token. When that token leaves
    the battlefield, put the exiled card into your hand.
    −3: Destroy target permanent that's one or more colors."

    Heuristica documentada (uma decisao real por turno, nao decorativa):
    SEMPRE +1. -3 e' reativa e so' vale a pena com um alvo colorido de
    verdade — mas este simulador nao modela oponente real (Regra 1), e as
    UNICAS 2 cartas coloridas de verdade em toda a lista de 100 sao NOSSAS
    (Defense of the Heart, Rhystic Study — ver docstring do topo do
    arquivo e a checagem carta-a-carta ja feita pro All Is Dust): destruir
    permanente PROPRIO seria uma piora, nunca escolhido por uma heuristica
    greedy. -3 fica "disponivel mas sem efeito numerico proveitoso" nesta
    convencao — mesmo tratamento ja usado pra Defense of the Heart/Sire of
    Stagnation (condicao de oponente nunca presumida verdadeira) — contada
    em `ugin_minus3_skipped_no_target_total` pra deixar a decisao auditavel,
    nao so' omitida.

    Token 2/2 Spirit criado por +1: colorless, sem sac outlet proprio (so'
    Eldrazi Spawn/Scion tem "sacrifice: add {C}"), sem combate ou remocao
    de oponente reais neste goldfish solo -> nunca sai de campo neste
    simulador. "When that token leaves the battlefield, put the exiled
    card into your hand" portanto NUNCA dispara aqui — documentado como
    omissao explicita, mesma convencao ja usada pros outros leaves-the-
    battlefield triggers do arquivo (so' disparam quando o proprio
    simulador causa a saida, ex: warp da Anticausal Vestige). A carta
    exilada por +1 fica presa em exilio (nunca volta a mao) — modelado
    explicitamente via `ugin_cards_exiled_stuck_total` pra tornar essa
    perda visivel na metrica, em vez de silenciada."""
    if UGIN_NAME not in state.battlefield:
        return
    if state.loyalty.get(UGIN_NAME, 0) <= 0:
        return
    state.loyalty[UGIN_NAME] = state.loyalty.get(UGIN_NAME, 4) + 1
    state.ugin_activations_total += 1
    state.ugin_plus1_total += 1
    state.ugin_spirit_tokens_created_total += 1
    state.ugin_minus3_skipped_no_target_total += 1  # -3 estava disponivel, heuristica sempre prefere +1 (ver docstring)
    if state.library:
        state.library.pop(0)  # exilado face down; nunca volta (token nunca sai de campo, ver docstring)
        state.ugin_cards_exiled_stuck_total += 1


def mystic_forge_top_castable(state: GameState) -> Optional[str]:
    if "Mystic Forge" not in state.battlefield or not state.library:
        return None
    top = state.library[0]
    if top in LAND_NAMES:
        return None
    card = CARD_DB[top]
    if card.ctype in ("artifact", "artifact_creature") or is_colorless(top):
        if remaining_mana(state) >= effective_cost(state, top):
            return top
    return None


def main_phase(state: GameState):
    if not state.commander_in_play and can_cast(state, COMMANDER):
        resolve_cast(state, COMMANDER, from_hand=False)
        if COMMANDER in state.hand:
            state.hand.remove(COMMANDER)

    do_world_breaker_recursion(state)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)]
        castables += [n for n in state.warp_exile_zone if can_cast(state, n)]
        top = mystic_forge_top_castable(state)
        use_top = top is not None and top not in castables

        if not castables and not use_top:
            break

        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"rock1", "rock2", "rock3", "land_tutor1", "land_tutor_hand_paid"}) else 1
            return (group, effective_cost(state, n))

        best_hand = min(castables, key=prio) if castables else None
        if use_top and (best_hand is None or effective_cost(state, top) <= effective_cost(state, best_hand)):
            state.library.pop(0)
            resolve_cast(state, top, from_hand=False)
        else:
            cast_card(state, best_hand)
        sac_spawns_for_mana(state, state.spawn_tokens_available)

    do_expedition_map(state)
    do_one_ring(state)
    do_ugin_loyalty(state)
    try_eye_of_ugin(state)
    try_urzas_cave(state)
    try_ruins_oran_rief(state)


def end_step(state: GameState):
    for name in state.warp_pending:
        if name in state.battlefield:
            state.battlefield.remove(name)
        draw_cards(state, 1)
        # "pode colocar permanente MV <= terrenos da mao em campo tapped" —
        # simplificado: nao modelado (raro ter algo util MV<=terrenos parado
        # na mao no exato momento; a compra de carta e o efeito principal)
        state.warp_exile_zone.append(name)
    state.warp_pending = []

    # Spawnbed Protector: "At the beginning of your end step, return up to
    # one target Eldrazi creature card from your graveyard to your hand.
    # Create two 1/1 colorless Eldrazi Scion creature tokens..." Achado
    # real 2026-08-28 (auditoria de checklist de mecanica): tagueada
    # "endstep_recursion", nunca despachada - dead code. Scion tokens
    # reaproveitam create_spawn_tokens() (mesma habilidade real, "sac:
    # add {C}", so' nome de token diferente - simplificacao documentada).
    if "Spawnbed Protector" in state.battlefield:
        eligible = [n for n in state.graveyard if is_creature_card(n) and is_eldrazi(n)]
        if eligible:
            best = max(eligible, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            state.hand.append(best)
            # Achado real 2026-08-31 (rodada ampliada, categoria 10): o
            # retorno de carta ja era implementado (correcao 2026-08-28),
            # mas nunca virava uma metrica de RECURSAO agregada e
            # reportavel — ficava "invisivel" no relatorio final.
            state.recursion_events_total += 1
            state.spawnbed_protector_recursion_total += 1
        create_spawn_tokens(state, 2)

    while len(state.hand) > 7:
        worst = min(state.hand, key=lambda n: effective_cost(state, n) if n not in LAND_NAMES else 0)
        state.hand.remove(worst)
        state.graveyard.append(worst)


def upkeep_step(state: GameState):
    pass


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    good_early = {"Sol Ring", "Arcane Signet", "Talisman of Dominance", "Talisman of Impulse",
                  "Talisman of Resilience", "Thran Dynamo", "Ancient Tomb", "Command Tower"}
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
        if not l or l.startswith("#"):
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
            if mulls > 0:
                rng.shuffle(hand)
                bottom = hand[:mulls]
                hand = hand[mulls:]
                lib = lib + bottom
            return hand, lib, mulls
        mulls += 1
    return hand, lib, mulls


def play_turn(state: GameState, is_first_turn: bool, on_play: bool):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.conduit_used_this_turn = False
    state.eye_of_ugin_used_this_turn = False
    state.colorless_creature_entered_this_turn = False

    upkeep_step(state)
    if not (is_first_turn and on_play):
        if state.library:
            state.hand.append(state.library.pop(0))
        else:
            state.library_emptied = True

    play_land(state)
    sac_spawns_for_mana(state, state.spawn_tokens_available)
    # Amostra de mana incolor de verdade vs. mana total, no inicio da fase
    # principal (antes de gastar) - 1 amostra por turno (2026-08-30, a
    # pedido do usuario).
    state.true_c_capacity_samples.append(true_colorless_capacity(state))
    state.total_mana_samples.append(total_mana(state))
    main_phase(state)
    # Mana generica (qualquer cor) que sobrou depois do loop guloso de
    # conjuracao - relevante pra ativacoes de custo generico tipo Strionic
    # Resonator/Peter Parker's Camera ({2},{T}), diferente da pergunta de
    # {C} especifico da Ulalek acima (2026-08-30, a pedido do usuario).
    state.leftover_mana_samples.append(remaining_mana(state))
    end_step(state)

    if any("flash_source" in CARD_DB[n].tags for n in state.battlefield):
        state.flash_online_turns += 1


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
    print(f"Turno medio de conjuracao da Ulalek: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    print(f"Avg copias pagas da Ulalek (CC): {avg([s.ulalek_copies_total for s in states]):.2f}")
    print(f"Avg copias incondicionais de Echoes of Eternity: {avg([s.echoes_spell_copies_total for s in states]):.2f}")
    print(f"Avg tokens-copia de permanentes (spell copies): {avg([s.spell_token_copies_total for s in states]):.2f}")
    print(f"Avg resolucoes extras de cast-trigger (Echoes+Ulalek): {avg([s.cast_trigger_extra_resolutions_total for s in states]):.2f}")
    print(f"Avg cascade cascade disparadas (Zhulodok): {avg([s.cascades_total for s in states]):.2f} | acertos: {avg([s.cascade_hits_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra (motores de draw): {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg cartas via The One Ring: {avg([s.one_ring_cards_drawn_total for s in states]):.2f}")
    print(f"Avg tutores usados: {avg([s.tutors_used_total for s in states]):.2f}")
    print(f"Avg Eldrazi Spawn tokens criados: {avg([s.spawn_tokens_created_total for s in states]):.2f}")
    print(f"Avg Manifest tokens criados (Kozilek Broken Reality): {avg([s.manifest_tokens_created_total for s in states]):.2f}")
    print(f"Avg remocao/exilio proxy total: {avg([s.proxy_removal_total for s in states]):.2f}")
    print(f"Avg vida ganha proxy (Forsaken Monument): {avg([s.proxy_life_gained_total for s in states]):.2f}")
    print(f"Avg spells de interacao conjurados (proxy): {avg([s.interaction_spells_cast_total for s in states]):.2f}")
    print(f"% de jogos que conjuraram All Is Dust: {100*sum(1 for s in states if s.all_is_dust_cast)/n:.1f}%")
    ad_games = [s for s in states if s.all_is_dust_cast]
    if ad_games:
        print(f"  Avg permanentes proprios sacrificados por All Is Dust nesses jogos: {avg([s.all_is_dust_self_sacrificed for s in ad_games]):.2f}")
    print(f"Avg dobras via Roaming Throne (contador direto): {avg([s.roaming_throne_doubles_total for s in states]):.2f}")
    print(f"Avg dano proxy via Glaring Fleshraker (2a habilidade, criatura colorless entra): {avg([s.glaring_fleshraker_damage_total for s in states]):.2f}")
    print(f"Avg turnos com flash online (Vedalken Orrery/Liberator/Skittering Cicada): {avg([s.flash_online_turns for s in states]):.2f}")
    print(f"Avg descontos de 'primeira criatura do turno' aplicados (Conduit/Radagast): {avg([s.first_creature_discount_events_total for s in states]):.2f}")
    print(f"Avg flash concedido pelo Radagast (se presente): {avg([s.radagast_flash_grants_total for s in states]):.2f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")
    print(f"Avg tutores via Eye of Ugin ({{7}},{{T}}: busca criatura colorless): {avg([s.eye_of_ugin_tutors_total for s in states]):.2f}")
    print(f"Urza's Cave sacrificado por terreno ({{3}},{{T}},sac): {100*sum(1 for s in states if s.urzas_cave_used)/n:.1f}% dos jogos")
    print(f"Avg contadores +1/+1 via Ruins of Oran-Rief (agregado, sem P/T por criatura): {avg([s.ruins_oran_rief_counters_total for s in states]):.2f}")

    # -----------------------------------------------------------------
    # Achado real 2026-08-31 (rodada ampliada, categoria 12): lealdade e
    # ativacoes de Ugin, the Ineffable, agora rastreadas de verdade.
    # -----------------------------------------------------------------
    print("--- Ugin, the Ineffable (planeswalker, categoria 12) ---")
    print(f"Avg ativacoes de lealdade (CR 606.3, 1/turno): {avg([s.ugin_activations_total for s in states]):.2f}")
    print(f"Avg '+1' escolhido (heuristica: sempre): {avg([s.ugin_plus1_total for s in states]):.2f}")
    print(f"Avg '-3' disponivel mas sem alvo colorido de oponente (nao escolhido): {avg([s.ugin_minus3_skipped_no_target_total for s in states]):.2f}")
    print(f"Avg Spirit tokens 2/2 criados via +1: {avg([s.ugin_spirit_tokens_created_total for s in states]):.2f}")
    print(f"Avg cartas exiladas presas via +1 (token nunca sai de campo neste modelo): {avg([s.ugin_cards_exiled_stuck_total for s in states]):.2f}")
    ugin_games = [s for s in states if UGIN_NAME in s.loyalty]
    if ugin_games:
        print(f"Avg lealdade final do Ugin (jogos em que resolveu, n={len(ugin_games)}): {avg([s.loyalty[UGIN_NAME] for s in ugin_games]):.2f}")

    # -----------------------------------------------------------------
    # Achado real 2026-08-31 (rodada ampliada, categoria 10): as 5
    # metricas basicas obrigatorias (Regra 9 do user-standing-rules.md),
    # reportadas aqui como linhas proprias, auditaveis e separadas —
    # RECURSION e FINISHER/LETHALITY nao existiam nenhuma antes desta
    # correcao; RAMP nunca tinha uma linha agregada propria (so os
    # componentes espalhados acima); DRAW e INTERACTION ja existiam
    # (linhas "cartas compradas extra"/"spells de interacao"), repetidas
    # aqui com rotulo explicito pra ficarem juntas e auditaveis.
    # -----------------------------------------------------------------
    print("--- 5 metricas basicas obrigatorias (Regra 9, categoria 10) ---")
    print(f"RAMP — Avg pecas de ramp resolvidas (rocks + land tutors, Sol Ring/Signet/Talismans/Dynamo/Farseek/Nature's Lore/Three Visits/Sowing Mycospawn/Expedition Map/Urza's Cave): {avg([s.ramp_pieces_resolved_total for s in states]):.2f}")
    print(f"RAMP — Avg mana TOTAL disponivel por turno (amostrado no inicio da main phase): {avg([m for s in states for m in s.total_mana_samples]):.2f}")
    print(f"RAMP — Avg capacidade de {{C}} real disponivel por turno (fontes que tapam por {{C}} de verdade, ver true_colorless_capacity): {avg([m for s in states for m in s.true_c_capacity_samples]):.2f}")
    print(f"DRAW — Avg cartas compradas extra (motores de draw, ja reportado acima): {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"INTERACTION — Avg spells de interacao conjurados (proxy, ja reportado acima): {avg([s.interaction_spells_cast_total for s in states]):.2f}")
    print(f"RECURSION — Avg eventos de recursao total (Spawnbed Protector + World Breaker): {avg([s.recursion_events_total for s in states]):.4f}")
    print(f"RECURSION — Avg retornos via Spawnbed Protector (cemiterio->mao, end step): {avg([s.spawnbed_protector_recursion_total for s in states]):.4f}")
    print(f"RECURSION — Avg retornos via World Breaker (ativada {{2}}{{C}}, sac land): {avg([s.world_breaker_recursion_total for s in states]):.4f}")
    recursion_games = sum(1 for s in states if s.recursion_events_total > 0)
    print(f"RECURSION — % de jogos com pelo menos 1 evento de recursao: {100*recursion_games/n:.2f}%")
    print(f"FINISHER/LETHALITY — Avg finishers resolvidos (MV>=9: Emrakul/Flayer/Kozilek x3/Ulamog x2/Void Winnower): {avg([s.finisher_resolved_total for s in states]):.2f}")
    finisher_games = [s for s in states if s.finisher_resolved_total > 0]
    print(f"FINISHER/LETHALITY — % de jogos com pelo menos 1 finisher resolvido: {100*len(finisher_games)/n:.1f}%")
    first_finisher_turns = [s.first_finisher_turn for s in states if s.first_finisher_turn is not None]
    if first_finisher_turns:
        print(f"FINISHER/LETHALITY — Avg turno do 1o finisher (entre os jogos que resolveram): {avg(first_finisher_turns):.2f} | mediana: {statistics.median(first_finisher_turns):.1f}")

    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=8600000, turns=8)

    with open("ulalek_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "ulalek_copies_total": s.ulalek_copies_total,
                "echoes_spell_copies_total": s.echoes_spell_copies_total,
                "spell_token_copies_total": s.spell_token_copies_total,
                "cast_trigger_extra_resolutions_total": s.cast_trigger_extra_resolutions_total,
                "cascades_total": s.cascades_total,
                "cascade_hits_total": s.cascade_hits_total,
                "cards_drawn_extra": s.cards_drawn_extra,
                "one_ring_cards_drawn_total": s.one_ring_cards_drawn_total,
                "tutors_used_total": s.tutors_used_total,
                "spawn_tokens_created_total": s.spawn_tokens_created_total,
                "manifest_tokens_created_total": s.manifest_tokens_created_total,
                "proxy_removal_total": s.proxy_removal_total,
                "all_is_dust_cast": s.all_is_dust_cast,
                "all_is_dust_self_sacrificed": s.all_is_dust_self_sacrificed,
                "glaring_fleshraker_damage_total": s.glaring_fleshraker_damage_total,
                # Achado real 2026-08-31 (rodada ampliada categorias 10-13):
                "ugin_loyalty_final": s.loyalty.get(UGIN_NAME),
                "ugin_activations_total": s.ugin_activations_total,
                "ugin_spirit_tokens_created_total": s.ugin_spirit_tokens_created_total,
                "recursion_events_total": s.recursion_events_total,
                "spawnbed_protector_recursion_total": s.spawnbed_protector_recursion_total,
                "world_breaker_recursion_total": s.world_breaker_recursion_total,
                "ramp_pieces_resolved_total": s.ramp_pieces_resolved_total,
                "finisher_resolved_total": s.finisher_resolved_total,
                "first_finisher_turn": s.first_finisher_turn,
                "eye_of_ugin_tutors_total": s.eye_of_ugin_tutors_total,
                "urzas_cave_used": s.urzas_cave_used,
                "ruins_oran_rief_counters_total": s.ruins_oran_rief_counters_total,
            }) + "\n")

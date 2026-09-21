"""
Goldfish simulator - Esika, God of the Tree // The Prismatic Bridge (5 cores - WUBRG)
Escrito e executado por Claude.

Metodologia:
- Tags de cada carta derivadas de oracle_text real (Scryfall,
  /tmp/scryfall_cache/prismatic_bridge_full.json), nao inventadas.
- Este e um simulador FOCADO, nao um goldfish completo de curva geral como
  o do Thranduil/Beorn. Escopo deliberadamente restrito ao que a pergunta
  do usuario pede: turno em que a Bridge resolve, taxa de acerto da Bridge
  em criatura/planeswalker, e sobrevivencia da Bridge/protetores sob
  remocao do oponente - especificamente pra decidir se vale incluir
  Greater Auramancy.
- NAO modelado (limitacao documentada, nao e um bug): a frente do
  comandante (Esika, God of the Tree) e sua habilidade de conceder mana de
  qualquer cor a outras lendarias; efeitos dos 11 criaturas que nao sejam
  ramp/draw/removal/counter-doubler ja tageados. O simulador so joga a
  carta "The Prismatic Bridge" (verso do MDFC) como comandante, direto do
  zone de comando.
- Correcao GRANDE 2026-08-28 (usuario: "Preciso que os counters de
  lealdade e ativacoes de planeswalker sejam sempre contabilizados, a base
  do Prismatic Bridge e essa!" - ver regra permanente categoria 12 em
  references/goldfish-sim-card-rules.md): os 17 planeswalkers da lista
  AGORA tem lealdade real rastreada (state.loyalty) e ativam uma
  habilidade real por turno (CR 606.3) - antes eram so um nome parado em
  campo depois da Bridge acertar, sem nenhum efeito. Doubling
  Season/Vorinclex (dobradores de counter) e Evolution Sage/Deepglow
  Skate/Vraska (proliferate) agora tem efeito real sobre a lealdade
  tambem. Correcao 2026-08-28 (2a rodada, regra nova de Classes/Sagas -
  "níveis"): Innkeeper's Talent agora sobe de nivel de verdade
  (try_level_up_innkeepers_talent, custo real {G}/{3}{G}) - nivel 3 dobra
  TODOS os counters (empilha com Doubling Season/Vorinclex em
  counter_doubler_multiplier), incluindo lealdade de planeswalker ao
  entrar. Ver goldfish-log.md pra detalhe completo e o que ficou
  deliberadamente deferido (estatico da Nicol Bolas, proliferate de outras
  6 fontes que precisam de hooks de cast/end-step que este arquivo ainda
  nao tem).
- NAO modelado (achado 2026-08-28, auditoria de checklist de mecanica -
  decisao consciente de escopo, nao esquecimento silencioso): as 14
  cartas tageadas "draw" que NAO sao planeswalker (Rhystic Study, etc.)
  tem a tag mas nenhum gatilho real disparado. Ficou de fora desta rodada
  por volume (14 motores, escopo comparavel a montar um goldfish completo)
  - fica pra uma rodada dedicada se o usuario quiser.
- PREMISSA NAO VALIDADA (usuario nao tem dado real, deck nunca jogado):
  taxa de tentativa de remocao por oponente por turno mirando a Bridge ou
  seus protetores. Default usado: 12% por oponente por turno, 3 oponentes
  (confirmado pelo usuario). Isso e um CHUTE razoavel pra Bracket 3
  upgraded, NAO um dado real - o resultado do teste Greater Auramancy deve
  ser lido como "dado esse chute, o efeito e X", nao como "X e a resposta
  definitiva". Ajustar REMOVAL_CHANCE_PER_OPPONENT se o usuario validar um
  numero diferente depois de jogar partidas reais.
"""

import random
from dataclasses import dataclass, field
from typing import Set, List, Dict, Optional

COMMANDER = "The Prismatic Bridge"
N_OPPONENTS = 3
REMOVAL_CHANCE_PER_OPPONENT = 0.12  # premissa assumida, ver docstring

# Politica de conjuracao da Bridge:
# False (default) = "cast ASAP" - conjura normal na main phase assim que
#   fica pagavel, nunca espera pra flashar (comportamento historico).
# True = "hold for flash" - se um habilitador de flash JA esta em campo,
#   segura a Bridge de proposito (nao conjura normal, mesmo pagavel) e
#   espera a janela de flash no end step alheio, especificamente pra
#   pular a rodada de remocao antes do 1o gatilho de upkeep (o plano de
#   jogo real do usuario). So muda comportamento nos jogos em que um
#   habilitador chega a estar em campo (~17% das partidas, ver auditoria).
HOLD_FOR_FLASH_POLICY = False

DECKLIST_TEXT = """
1 Alchemist's Refuge
1 All Will Be One
1 Aminatou, the Fateshifter
1 Anguished Unmaking
1 Arcane Signet
1 Arena Rector
1 Ashiok, Dream Render
1 Atraxa, Praetors' Voice
1 Blasphemous Act
1 Bloom Tender
1 Carth the Lion
1 Chromatic Lantern
1 Counterspell
1 Damn
1 Deepglow Skate
1 Delighted Halfling
1 Doubling Season
1 Dovin's Veto
1 Elspeth, Sun's Champion
1 Evolution Sage
1 Farseek
1 Farewell
1 Flux Channeler
1 Ichormoon Gauntlet
1 Inexorable Tide
1 Innkeeper's Talent
1 Kaya, Intangible Slayer
1 Liliana, Dreadhorde General
1 Mana Drain
1 Mutational Advantage
1 Narset, Parter of Veils
1 Nature's Lore
1 Nesting Grounds
1 Nicol Bolas, Dragon-God
1 Oath of Nissa
1 Oath of Teferi
1 Oko, the Ringleader
1 Paradox Haze
1 Path to Exile
1 Rhystic Study
1 Ripples of Potential
1 Sol Ring
1 Sphinx of the Second Sun
1 Sterling Grove
1 Supreme Verdict
1 Swan Song
1 Swords to Plowshares
1 Tamiyo, Compleated Sage
1 Tamiyo, Field Researcher
1 Teferi, Hero of Dominaria
1 Teferi, Temporal Archmage
1 Teferi, Time Raveler
1 Teferi, Who Slows the Sunset
1 The Chain Veil
1 The Eternal Wanderer
1 The Peregrine Dynamo
1 The World Tree
1 Three Visits
1 Toxic Deluge
1 Ugin, the Spirit Dragon
1 Urza Assembles the Titans
1 Veil of Summer
1 Void Rend
1 Vorinclex, Monstrous Raider
1 Vraska, Betrayal's Sting
1 Badlands
1 Bayou
1 Blood Crypt
1 Breeding Pool
1 Brushland
1 City of Brass
1 Command Tower
1 Emergence Zone
1 Exotic Orchard
1 Fabled Passage
1 Godless Shrine
1 Hallowed Fountain
1 Interplanar Beacon
1 Mana Confluence
1 Overgrown Tomb
1 Plateau
1 Plaza of Heroes
1 Sacred Foundry
1 Savannah
1 Scrubland
1 Snow-Covered Forest
1 Snow-Covered Island
1 Snow-Covered Mountain
1 Snow-Covered Plains
1 Snow-Covered Swamp
1 Steam Vents
1 Stomping Ground
1 Taiga
1 Temple Garden
1 Tropical Island
1 Tundra
1 Underground Sea
1 Volcanic Island
1 Watery Grave
"""

@dataclass
class Card:
    name: str
    mv: int
    type: str
    colors: Set[str] = field(default_factory=set)
    produces: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)

CARD_DB: Dict[str, Card] = {}

def add(name, mv, type_, colors=None, produces=None, tags=None):
    CARD_DB[name] = Card(name=name, mv=mv, type=type_,
                          colors=set(colors or []), produces=set(produces or []),
                          tags=set(tags or []))

# -------- Comandante (so o verso - ver limitacao no docstring) --------
add("The Prismatic Bridge", 5, "Enchantment", colors={"B", "G", "R", "U", "W"}, tags={"bridge_engine"})
add("Greater Auramancy", 2, "Enchantment", colors={"W"}, tags={"protection_shroud"})

# -------- Deck (99 cartas, geradas via Scryfall cards/collection) --------
add("Alchemist's Refuge", 0, "Land", colors={"G", "U"}, produces={"C"}, tags={"flash_enabler"})
add("All Will Be One", 5, "Enchantment", colors={"R"}, produces=set(), tags=set())
add("Aminatou, the Fateshifter", 3, "Planeswalker", colors={"B", "U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("Anguished Unmaking", 3, "Instant", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Arcane Signet", 2, "Artifact", colors=set(), produces={"B", "G", "R", "U", "W"}, tags={"ramp"})
add("Arena Rector", 4, "Creature", colors={"W"}, produces=set(), tags={"creature"})
add("Ashiok, Dream Render", 3, "Planeswalker", colors={"B", "U"}, produces=set(), tags={"planeswalker"})
add("Atraxa, Praetors' Voice", 4, "Creature", colors={"B", "G", "U", "W"}, produces=set(), tags={"creature", "proliferate"})
add("Blasphemous Act", 9, "Sorcery", colors={"R"}, produces=set(), tags={"wipe"})
add("Bloom Tender", 2, "Creature", colors={"G"}, produces=set(), tags={"creature", "ramp", "bloom_tender"})
# Achado real 2026-08-28 (auditoria de checklist): oraculo real e' "Vivid -
# {T}: For each color among permanents you control, add one mana of that
# color" - escala com cores REAIS em campo, nao 5c fixo. produces=set(),
# tratada com logica propria em color_sources()/total_mana() via tag
# "bloom_tender".
add("Carth the Lion", 4, "Creature", colors={"B", "G"}, produces=set(), tags={"creature"})
add("Chromatic Lantern", 3, "Artifact", colors=set(), produces={"B", "G", "R", "U", "W"}, tags={"ramp", "lands_any_color"})
# Achado real 2026-08-28: alem do proprio {T}: Add any color (produces
# acima, correto), tem uma estatica de campo inteiro nunca implementada:
# "Lands you control have '{T}: Add one mana of any color.'" - afeta TODO
# terreno em campo, nao so ela mesma. Tag "lands_any_color" checada em
# color_sources().
add("Counterspell", 2, "Instant", colors={"U"}, produces=set(), tags={"counterspell"})
add("Damn", 2, "Sorcery", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Deepglow Skate", 5, "Creature", colors={"U"}, produces=set(), tags={"counter_doubler", "creature"})
add("Delighted Halfling", 1, "Creature", colors={"G"}, produces={"C"}, tags={"creature", "ramp", "legendary_only_color"})
# Achado real 2026-08-28: "{T}: Add {C}." incondicional (produces acima),
# mas a mana colorida real e' "{T}: Add one mana of any color. Spend this
# mana only to cast a legendary spell, and that spell can't be countered" -
# so' incolor era incondicional. Tag "legendary_only_color" checada em
# color_sources() (so conta pra spells lendarios de verdade).
add("Doubling Season", 5, "Enchantment", colors={"G"}, produces=set(), tags={"counter_doubler"})
add("Dovin's Veto", 2, "Instant", colors={"U", "W"}, produces=set(), tags=set())
add("Elspeth, Sun's Champion", 6, "Planeswalker", colors={"W"}, produces=set(), tags={"planeswalker", "wipe"})
add("Evolution Sage", 3, "Creature", colors={"G"}, produces=set(), tags={"creature", "proliferate"})
add("Farseek", 2, "Sorcery", colors={"G"}, produces=set(), tags={"ramp"})
add("Farewell", 6, "Sorcery", colors={"W"}, produces=set(), tags={"wipe"})
add("Flux Channeler", 3, "Creature", colors={"U"}, produces=set(), tags={"creature", "proliferate"})
add("Ichormoon Gauntlet", 3, "Artifact", colors={"U"}, produces=set(), tags={"proliferate"})
add("Inexorable Tide", 5, "Enchantment", colors={"U"}, produces=set(), tags={"proliferate"})
add("Innkeeper's Talent", 2, "Enchantment", colors={"G"}, produces=set(), tags={"counter_doubler"})
add("Kaya, Intangible Slayer", 7, "Planeswalker", colors={"B", "W"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Liliana, Dreadhorde General", 6, "Planeswalker", colors={"B"}, produces=set(), tags={"draw", "planeswalker", "wipe"})
add("Mana Drain", 2, "Instant", colors={"U"}, produces=set(), tags={"counterspell"})
add("Mutational Advantage", 3, "Instant", colors={"G", "U"}, produces=set(), tags={"proliferate"})
add("Narset, Parter of Veils", 3, "Planeswalker", colors={"U"}, produces=set(), tags={"planeswalker"})
add("Nature's Lore", 2, "Sorcery", colors={"G"}, produces=set(), tags={"ramp"})
add("Nesting Grounds", 0, "Land", colors=set(), produces={"C"}, tags=set())
add("Nicol Bolas, Dragon-God", 5, "Planeswalker", colors={"B", "R", "U"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Oath of Nissa", 1, "Enchantment", colors={"G"}, produces=set(), tags=set())
# Achado real (auditoria oraculo-por-oraculo): "You may activate the
# loyalty abilities of planeswalkers you control TWICE each turn rather
# than only once" -- estatico, sempre ligado enquanto em campo, nunca
# implementado (so a metade de ETB-flicker, de baixo valor, ficaria de
# fora mesmo). Com 17 planeswalkers na lista, e' um dos maiores
# multiplicadores de valor do deck. Ver extra_pw_activation_sources().
add("Oath of Teferi", 5, "Enchantment", colors={"U", "W"}, produces=set(), tags={"double_pw_activation"})
add("Oko, the Ringleader", 4, "Planeswalker", colors={"G", "U"}, produces=set(), tags={"draw", "planeswalker"})
add("Paradox Haze", 3, "Enchantment", colors={"U"}, produces=set(), tags={"extra_upkeep"})
add("Path to Exile", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Rhystic Study", 3, "Enchantment", colors={"U"}, produces=set(), tags={"draw"})
add("Ripples of Potential", 2, "Instant", colors={"U"}, produces=set(), tags={"proliferate"})
add("Sol Ring", 1, "Artifact", colors=set(), produces={"C"}, tags={"ramp"})
add("Sphinx of the Second Sun", 8, "Creature", colors={"U"}, produces=set(), tags={"creature"})
add("Sterling Grove", 2, "Enchantment", colors={"G", "W"}, produces=set(), tags={"protection_shroud"})
add("Supreme Verdict", 4, "Sorcery", colors={"U", "W"}, produces=set(), tags={"wipe"})
add("Swan Song", 1, "Instant", colors={"U"}, produces=set(), tags=set())
add("Swords to Plowshares", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Tamiyo, Compleated Sage", 5, "Planeswalker", colors={"G", "U"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Tamiyo, Field Researcher", 4, "Planeswalker", colors={"G", "U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("Teferi, Hero of Dominaria", 5, "Planeswalker", colors={"U", "W"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Teferi, Temporal Archmage", 6, "Planeswalker", colors={"U"}, produces=set(), tags={"planeswalker"})
add("Teferi, Time Raveler", 3, "Planeswalker", colors={"U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("Teferi, Who Slows the Sunset", 4, "Planeswalker", colors={"U", "W"}, produces=set(), tags={"draw", "planeswalker"})
# Achado real (auditoria oraculo-por-oraculo): "{4},{T}: For each
# planeswalker you control, you may activate one of its loyalty
# abilities once this turn as though none of its loyalty abilities have
# been activated this turn" -- habilidade ativada real, paga, nunca
# implementada (so' o downside de vida, sem rastreio de vida neste
# arquivo, ficaria de fora mesmo). Ver try_chain_veil_activation().
add("The Chain Veil", 4, "Artifact", colors=set(), produces=set(), tags={"chain_veil"})
add("The Eternal Wanderer", 6, "Planeswalker", colors={"W"}, produces=set(), tags={"planeswalker", "wipe"})
add("The Peregrine Dynamo", 3, "Creature", colors=set(), produces=set(), tags={"creature"})
add("The World Tree", 0, "Land", colors={"G"}, produces={"G"}, tags={"world_tree_6lands"})
# Achado real 2026-08-28: "{T}: Add {G}" incondicional (produces acima),
# mas o resto do oraculo real e' "This land enters tapped." + "As long as
# you control six or more lands, lands you control have '{T}: Add one
# mana of any color.'" (afeta TODO terreno em campo, condicionado a 6+
# terrenos - nao 5c incondicional desde o turno 1). Tag "world_tree_6lands"
# checada em color_sources(). NAO modelado (esse arquivo nao rastreia
# terreno tapped-on-ETB pra nenhuma carta - mesma simplificacao geral ja
# em uso aqui): o "enters tapped" proprio dela, atraso de 1 turno.
add("Three Visits", 2, "Sorcery", colors={"G"}, produces=set(), tags={"ramp"})
add("Toxic Deluge", 3, "Sorcery", colors={"B"}, produces=set(), tags={"wipe"})
add("Ugin, the Spirit Dragon", 8, "Planeswalker", colors=set(), produces=set(), tags={"draw", "planeswalker", "removal"})
# Achado real (auditoria oraculo-por-oraculo): Saga real (Read ahead) 100%
# ausente -- I: scry 4 (nao modelado, sem infra de scry neste arquivo,
# mesma convencao de omissao ja usada noutros decks) + revela o topo, se
# for planeswalker vai pra mao; II: pode botar um planeswalker MV<=6 da
# mao em campo de graca; III: ativa lealdade 2x so' neste turno. Ver
# try_urza_saga_tick().
add("Urza Assembles the Titans", 5, "Enchantment", colors={"W"}, produces=set(), tags={"urza_saga"})
add("Veil of Summer", 1, "Instant", colors={"G"}, produces=set(), tags={"draw"})
add("Void Rend", 3, "Instant", colors={"B", "U", "W"}, produces=set(), tags={"removal"})
add("Vorinclex, Monstrous Raider", 6, "Creature", colors={"G"}, produces=set(), tags={"counter_doubler", "creature"})
add("Vraska, Betrayal's Sting", 6, "Planeswalker", colors={"B"}, produces={"B", "G", "R", "U", "W"}, tags={"draw", "planeswalker", "proliferate", "ramp"})
add("Badlands", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Bayou", 0, "Land", colors={"B", "G"}, produces={"B", "G"}, tags=set())
add("Blood Crypt", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Breeding Pool", 0, "Land", colors={"G", "U"}, produces={"G", "U"}, tags=set())
add("Brushland", 0, "Land", colors={"G", "W"}, produces={"C", "G", "W"}, tags=set())
add("City of Brass", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Command Tower", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Emergence Zone", 0, "Land", colors=set(), produces={"C"}, tags={"flash_enabler"})
add("Exotic Orchard", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
# Achado real 2026-08-28 (auditoria de checklist): Fabled Passage NAO TEM
# nenhuma habilidade de mana no oraculo real - so' "{T}, Sacrifice this
# land: Search your library for a basic land card, put it onto the
# battlefield tapped, then shuffle. Then if you control four or more
# lands, untap that land." Estava modelada como fonte incondicional de
# qualquer cor (nem sequer excluida do +1 generico de is_land()). Corrigido:
# produces=set() + tag "fabled_passage" (excluida do +1 generico em
# total_mana(), tem busca real implementada em try_fabled_passage()).
add("Fabled Passage", 0, "Land", colors=set(), produces=set(), tags={"fabled_passage"})
add("Godless Shrine", 0, "Land", colors={"B", "W"}, produces={"B", "W"}, tags=set())
add("Hallowed Fountain", 0, "Land", colors={"U", "W"}, produces={"U", "W"}, tags=set())
add("Interplanar Beacon", 0, "Land", colors=set(), produces={"C"}, tags=set())
# Achado real 2026-08-28: "{T}: Add {C}" incondicional (produces acima) e'
# a UNICA parte generica real - a mana colorida real ("{1},{T}: Add two
# mana of different colors") custa mana adicional e so' vale pra conjurar
# planeswalkers. Modelada como 5c incondicional antes - corrigido pra so'
# incolor. A metade restrita a planeswalkers nao foi modelada (custo extra
# de mana + restricao de tipo, baixo valor pro escopo desse sim).
add("Mana Confluence", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Overgrown Tomb", 0, "Land", colors={"B", "G"}, produces={"B", "G"}, tags=set())
add("Plateau", 0, "Land", colors={"R", "W"}, produces={"R", "W"}, tags=set())
add("Plaza of Heroes", 0, "Land", colors=set(), produces={"C"}, tags=set())
# Achado real 2026-08-28: "{T}: Add {C}" incondicional (produces acima) e'
# a UNICA parte generica real - as outras 2 habilidades de mana colorida
# ("Spend only to cast a legendary spell" / "any color among legendary
# permanents you control") sao restritas, nao modeladas (baixo valor pro
# escopo desse sim, deck ja tem Delighted Halfling pro caso legendary).
add("Sacred Foundry", 0, "Land", colors={"R", "W"}, produces={"R", "W"}, tags=set())
add("Savannah", 0, "Land", colors={"G", "W"}, produces={"G", "W"}, tags=set())
add("Scrubland", 0, "Land", colors={"B", "W"}, produces={"B", "W"}, tags=set())
add("Snow-Covered Forest", 0, "Land", colors={"G"}, produces={"G"}, tags=set())
add("Snow-Covered Island", 0, "Land", colors={"U"}, produces={"U"}, tags=set())
add("Snow-Covered Mountain", 0, "Land", colors={"R"}, produces={"R"}, tags=set())
add("Snow-Covered Plains", 0, "Land", colors={"W"}, produces={"W"}, tags=set())
add("Snow-Covered Swamp", 0, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Steam Vents", 0, "Land", colors={"R", "U"}, produces={"R", "U"}, tags=set())
add("Stomping Ground", 0, "Land", colors={"G", "R"}, produces={"G", "R"}, tags=set())
add("Taiga", 0, "Land", colors={"G", "R"}, produces={"G", "R"}, tags=set())
add("Temple Garden", 0, "Land", colors={"G", "W"}, produces={"G", "W"}, tags=set())
add("Tropical Island", 0, "Land", colors={"G", "U"}, produces={"G", "U"}, tags=set())
add("Tundra", 0, "Land", colors={"U", "W"}, produces={"U", "W"}, tags=set())
add("Underground Sea", 0, "Land", colors={"B", "U"}, produces={"B", "U"}, tags=set())
add("Volcanic Island", 0, "Land", colors={"R", "U"}, produces={"R", "U"}, tags=set())
add("Watery Grave", 0, "Land", colors={"B", "U"}, produces={"B", "U"}, tags=set())

# -------- Tokens gerados por habilidades de planeswalker --------
add("Soldier Token", 0, "Creature", colors={"W"}, produces=set(), tags=set())
add("Zombie Token", 0, "Creature", colors={"B"}, produces=set(), tags=set())
add("Elk Token", 0, "Creature", colors={"G"}, produces=set(), tags=set())
add("Samurai Token", 0, "Creature", colors={"W"}, produces=set(), tags=set())

def C(name: str) -> Card:
    return CARD_DB[name]

def parse_decklist(text: str) -> List[str]:
    deck = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue
        parts = line.split(" ", 1)
        qty = int(parts[0])
        name = parts[1].strip()
        deck.extend([name] * qty)
    return deck

def is_land(card: str) -> bool:
    return C(card).type == "Land"

def has_tag(card: str, tag: str) -> bool:
    return tag in C(card).tags

# Permanentes lendarios de verdade na decklist (type_line real, Scryfall) -
# usado por Delighted Halfling/Plaza of Heroes ("cast a legendary spell").
LEGENDARY_CARD_NAMES = {
    "Aminatou, the Fateshifter", "Ashiok, Dream Render", "Atraxa, Praetors' Voice",
    "Carth the Lion", "Elspeth, Sun's Champion", "Kaya, Intangible Slayer",
    "Liliana, Dreadhorde General", "Narset, Parter of Veils", "Nicol Bolas, Dragon-God",
    "Oath of Nissa", "Oath of Teferi", "Oko, the Ringleader", "Tamiyo, Compleated Sage",
    "Tamiyo, Field Researcher", "Teferi, Hero of Dominaria", "Teferi, Temporal Archmage",
    "Teferi, Time Raveler", "Teferi, Who Slows the Sunset", "The Chain Veil",
    "The Eternal Wanderer", "The Peregrine Dynamo", "Ugin, the Spirit Dragon",
    "Vorinclex, Monstrous Raider", "Vraska, Betrayal's Sting",
}

# Achado real 2026-08-28 (auditoria de checklist): Farseek/Nature's
# Lore/Three Visits eram conjurados como Sorcery generica e iam direto pro
# cemiterio, sem NENHUMA busca real - puro sink de mana. Pools reais
# (type_line, Scryfall) de terrenos desta decklist que se qualificam:
BASIC_LAND_NAMES = {"Snow-Covered Forest", "Snow-Covered Island", "Snow-Covered Mountain",
                     "Snow-Covered Plains", "Snow-Covered Swamp"}
FARSEEK_POOL = {"Badlands", "Bayou", "Blood Crypt", "Breeding Pool", "Godless Shrine",
                 "Hallowed Fountain", "Overgrown Tomb", "Plateau", "Sacred Foundry", "Savannah",
                 "Scrubland", "Snow-Covered Island", "Snow-Covered Mountain", "Snow-Covered Plains",
                 "Snow-Covered Swamp", "Steam Vents", "Stomping Ground", "Taiga", "Temple Garden",
                 "Tropical Island", "Tundra", "Underground Sea", "Volcanic Island", "Watery Grave"}
FOREST_FETCH_POOL = {"Bayou", "Breeding Pool", "Overgrown Tomb", "Savannah", "Snow-Covered Forest",
                      "Stomping Ground", "Taiga", "Temple Garden", "Tropical Island"}
LAND_FETCH_SPELLS = {"Farseek", "Nature's Lore", "Three Visits"}

# Achado real 2026-08-28 (usuario: "Preciso que os counters de lealdade e
# ativacoes de planeswalker sejam sempre contabilizados, a base do
# Prismatic Bridge e essa!"): lealdade inicial real (Scryfall) dos 17
# planeswalkers da lista - nenhum tinha lealdade rastreada antes, so a tag
# decorativa "planeswalker". Ver regra permanente nova em
# references/goldfish-sim-card-rules.md, categoria 12.
PLANESWALKER_STARTING_LOYALTY = {
    "Aminatou, the Fateshifter": 3, "Ashiok, Dream Render": 5,
    "Elspeth, Sun's Champion": 4, "Kaya, Intangible Slayer": 6,
    "Liliana, Dreadhorde General": 6, "Narset, Parter of Veils": 5,
    "Nicol Bolas, Dragon-God": 4, "Oko, the Ringleader": 3,
    "Tamiyo, Compleated Sage": 5, "Tamiyo, Field Researcher": 4,
    "Teferi, Hero of Dominaria": 4, "Teferi, Temporal Archmage": 5,
    "Teferi, Time Raveler": 4, "Teferi, Who Slows the Sunset": 4,
    "The Eternal Wanderer": 5, "Ugin, the Spirit Dragon": 7,
    "Vraska, Betrayal's Sting": 6,
}
# Tamiyo, Compleated Sage / Vraska, Betrayal's Sting tem custo "Compleated"
# (paga 2 vida em vez de mana colorida, entra com 2 lealdade a menos) - so
# se aplica quando a carta e' CONJURADA pagando o custo. A Bridge poe a
# carta direto em campo (nao e' um cast), entao a lealdade inicial e'
# sempre a cheia - nao ha custo alternativo a pagar aqui.

# =========================================================
# GAME STATE
# =========================================================

@dataclass
class GameState:
    rng: random.Random
    library: List[str]
    hand: List[str] = field(default_factory=list)
    battlefield: List[str] = field(default_factory=list)
    graveyard: List[str] = field(default_factory=list)
    turn: int = 0
    land_played: bool = False
    mana_spent_this_turn: int = 0
    tapped_lands_this_turn: Set[str] = field(default_factory=set)  # Farseek/Fabled Passage - terreno entra tapped esse turno, resetado em play_turn()
    evolution_sage_proliferates: int = 0
    mana_held_back: int = 0  # mana nao gasta no ultimo turno, disponivel pra flash no end step alheio (untap so acontece no MEU untap step - CR 500.1 - entao isso NAO reseta pra total_mana entre meus turnos)
    lands_played_total: int = 0

    bridge_in_play: bool = False
    bridge_cast_turn: Optional[int] = None
    bridge_first_cast_turn: Optional[int] = None
    bridge_cast_count: int = 0
    bridge_removed_count: int = 0
    bridge_flash_cast: bool = False
    bridge_triggers: int = 0
    bridge_hits_creature: int = 0
    bridge_hits_planeswalker: int = 0
    bridge_no_hit_empty_library: int = 0
    first_pw_hit_turn: Optional[int] = None

    protectors_removed_count: int = 0
    removal_attempts_total: int = 0
    removal_attempts_wasted: int = 0

    with_greater_auramancy: bool = False

    # Doenca de invocacao pra mana dorks criatura (Bloom Tender, Delighted
    # Halfling) - achado real 2026-08-28 (auditoria de checklist de
    # mecanica): nao existia NENHUM rastreio de turno de entrada, entao
    # ambas produziam mana no proprio turno em que eram conjuradas.
    creature_cast_turn: Dict[str, int] = field(default_factory=dict)

    # Lealdade real dos planeswalkers em campo (nome -> lealdade atual).
    loyalty: Dict[str, int] = field(default_factory=dict)
    pw_draws_total: int = 0
    pw_tokens_created_total: int = 0
    pw_life_gained_total: int = 0
    pw_life_lost_opponent_total: int = 0
    pw_removal_proxy_total: int = 0
    pw_wipe_proxy_total: int = 0
    pw_recursion_total: int = 0
    pw_ultimates_used_total: int = 0
    pw_deaths_total: int = 0
    pw_activations_total: int = 0
    teferi_sunset_emblem: bool = False  # ultimate: draw extra durante upkeep de cada oponente (ver do_upkeep)

    # Achado real 2026-08-28 (usuario: "verifique as cartas com niveis,
    # como classes e sagas... o innkeeper's no Prismatic no nivel 3 DOBRA
    # TODOS OS COUNTERS, inclusive os de lealdade de PWs ao entrarem no
    # jogo!"): nivel comeca em 1 (habilidade base) ao ser conjurada, sobe
    # "as a sorcery" pagando o custo real de cada nivel.
    innkeepers_talent_level: int = 1

    # Achados reais 2026-09-01 (leitura linha-a-linha completa do
    # oraculo, "compile TUDO" - a nota antiga do docstring sobre "11
    # criaturas nao-ramp/draw/removal/counter-doubler" ficou desatualizada;
    # verificado carta a carta contra o oraculo real via Scryfall):
    # Sphinx of the Second Sun ("if you cast it, take an extra turn") e
    # Carth the Lion (ETB: tutor de planeswalker + taxa de {1} extra em
    # TODA ativacao de lealdade, inclusive a nossa) sao reais e
    # implementaveis neste motor - Arena Rector (gatilho de MORTE, nao
    # ETB) e The Peregrine Dynamo (copiar gatilho entre N fontes
    # legendarias, mesma excecao arquitetural do Strionic Resonator)
    # permanecem estruturalmente fora de escopo, ver docstring.
    extra_turns_pending: int = 0
    sphinx_extra_turns_total: int = 0
    sphinx_sacrifice_pending: bool = False
    carth_tutors_total: int = 0

    # Achado real (auditoria oraculo-por-oraculo): "removal"/"counterspell"/
    # "wipe" nas 11 cartas nao-planeswalker (Anguished Unmaking, Blasphemous
    # Act, Counterspell, Damn, Farewell, Mana Drain, Path to Exile, Supreme
    # Verdict, Swords to Plowshares, Toxic Deluge, Void Rend) nunca eram
    # lidas em lugar nenhum -- as cartas eram conjuradas pelo loop generico
    # (corretamente sem efeito de bordo real, Regra 1: sem oponente real, um
    # wipe/remocao sem alvo nao faz nada), mas nem sequer contavam pra
    # metrica de interacao, ao contrario de TODOS os outros decks desta
    # sessao (que tem esse contador pras 5 metricas basicas).
    interaction_spells_cast_total: int = 0

    # Achado real: 3 fontes reais de "ative habilidades de lealdade mais de
    # 1x por turno" nunca implementadas -- Oath of Teferi (estatico,
    # "twice each turn rather than only once"), The Chain Veil ({4},{T}:
    # mais 1x pra CADA planeswalker) e Urza Assembles the Titans capitulo
    # III (2x so' no turno em que resolve). Com 17 planeswalkers na lista,
    # sao os maiores multiplicadores de valor do deck inteiro fora da
    # propria Bridge -- nenhum estava implementado.
    chain_veil_activated_this_turn: bool = False
    urza_chapter: int = 0
    urza_last_ticked_turn: int = -1
    urza_chapter_iii_this_turn: bool = False
    chain_veil_activations_total: int = 0
    urza_pw_cheated_total: int = 0
    urza_pw_tutored_total: int = 0

    # ---- Modo opcional de resiliencia (interacao de oponente), 2026-09-20 ----
    # Porte do mesmo modo ja implementado e validado no Megatron/Ur-Dragon/
    # Hei Bai/Markov/Ulalek/Toph. Todos os campos abaixo ficam INERTES em
    # modo padrao (`simulate_one`/`run_batch`) -- so' tem efeito quando
    # `interaction_rng` e' setado por `simulate_one_with_interaction`, que
    # tambem passa `skip_legacy_removal=True` pra `play_turn` (desliga o
    # sistema antigo `resolve_removal_round`, ver decisao do usuario no
    # checklist-oraculo.md -- os 2 sistemas nao se empilham). `life` e'
    # NOVO neste arquivo (nunca rastreou vida propria) -- serve so' de
    # alvo pro ataque de oponente do modo de resiliencia, comeca em 40.
    interaction_rng: Optional[random.Random] = None
    life: int = 40
    wiped_this_round: bool = False
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
    graveyard_wipe_used: bool = False
    smart_graveyard_snipes_total: int = 0
    smart_graveyard_snipe_log: list = field(default_factory=list)

    def draw(self, n: int = 1):
        for _ in range(n):
            if self.library:
                self.hand.append(self.library.pop(0))

    def has(self, name: str) -> bool:
        return name in self.battlefield

# =========================================================
# MANA MODEL
# =========================================================

def _dork_ready(state: GameState, card: str) -> bool:
    return state.creature_cast_turn.get(card, -1) < state.turn

def total_mana(state: GameState) -> int:
    total = 0
    for card in state.battlefield:
        if has_tag(card, "fabled_passage"):
            continue  # sem habilidade de mana propria - so' fetch (try_fabled_passage)
        if is_land(card):
            if card in state.tapped_lands_this_turn:
                continue  # entrou tapped esse turno (Farseek/Fabled Passage), ainda nao produz
            total += 1
        elif card == "Sol Ring":
            total += 2
        elif has_tag(card, "bloom_tender"):
            if _dork_ready(state, card):
                colors_in_play = set()
                for c in state.battlefield:
                    colors_in_play |= C(c).colors
                total += max(0, len(colors_in_play))
        elif has_tag(card, "ramp") and card != "Delighted Halfling":
            if C(card).type == "Creature" and not _dork_ready(state, card):
                continue  # doenca de invocacao (CR 302.6) - so' pra criatura
            total += 1
        elif card == "Delighted Halfling":
            if _dork_ready(state, card):
                total += 1  # so' o {T}: Add {C} incondicional
    return total

def color_sources(state: GameState, color: str, legendary_spell: bool = False) -> int:
    n = 0
    world_tree_active = "The World Tree" in state.battlefield and sum(1 for c in state.battlefield if is_land(c)) >= 6
    lantern_active = "Chromatic Lantern" in state.battlefield
    for card in state.battlefield:
        base_produces = C(card).produces
        # Chromatic Lantern / The World Tree (6+ terrenos): TODO terreno em
        # campo ganha "{T}: Add one mana of any color" via efeito estatico.
        if is_land(card) and (lantern_active or world_tree_active) and card != "Chromatic Lantern":
            n += 1
            continue
        if has_tag(card, "bloom_tender"):
            colors_in_play = {cc for c in state.battlefield for cc in C(c).colors}
            if _dork_ready(state, card) and color in colors_in_play:
                n += 1
            continue
        if color not in base_produces:
            continue
        if has_tag(card, "legendary_only_color") and not legendary_spell:
            continue
        if C(card).type == "Creature" and not _dork_ready(state, card):
            continue
        n += 1
    return n

def remaining_mana(state: GameState) -> int:
    return total_mana(state) - state.mana_spent_this_turn

def bridge_effective_mv(state: GameState) -> int:
    return C(COMMANDER).mv + 2 * state.bridge_cast_count

def can_cast(state: GameState, card: str) -> bool:
    mv = bridge_effective_mv(state) if card == COMMANDER else C(card).mv
    if remaining_mana(state) < mv:
        return False
    legendary = card == COMMANDER or card in LEGENDARY_CARD_NAMES
    for color in C(card).colors:
        if color_sources(state, color, legendary_spell=legendary) < 1:
            return False
    return True

# =========================================================
# MULLIGAN (simplificado - so garante mao jogavel de terrenos)
# =========================================================

# Rocks/dorks reais que aceleram de verdade (validado por analise de
# correlacao, n=8000 maos, 2026-08-21): Sol Ring/Arcane Signet/Bloom
# Tender/Delighted Halfling/Chromatic Lantern reduzem o turno medio da
# 1a conjuracao da Bridge de ~4,1-4,2 pra ~3,2-3,8 quando estao na mao
# inicial. Farseek/Nature's Lore/Three Visits (tutores de terreno) NAO
# entram aqui de proposito - a mesma analise mostrou que eles pioram a
# velocidade (custam carta+2 mana pra fazer o que 1 land drop ja faz de
# graca), entao nao contam como equivalente a um rock pra decisao de
# mulligan.
FAST_RAMP_ROCKS_DORKS = {"Sol Ring", "Arcane Signet", "Chromatic Lantern", "Bloom Tender", "Delighted Halfling"}

def should_keep(hand: List[str]) -> bool:
    # Heuristico validado por dados (n=8000, 2026-08-21): 2 terrenos sem
    # rock e uma mao ruim de verdade (turno medio 5,72, 31,8% nunca
    # conjura a Bridge) - pior que 3 terrenos sozinhos (4,50/14,0%), que
    # por sua vez e pior que 2 terrenos + 1 rock (4,32/12,2%). Exige 3+
    # terrenos OU 2 terrenos + pelo menos 1 rock/dork real.
    lands = sum(1 for c in hand if is_land(c))
    if lands > 5:
        return False
    if lands >= 3:
        return True
    if lands == 2:
        return any(c in FAST_RAMP_ROCKS_DORKS for c in hand)
    return False

def choose_bottom(hand: List[str], n: int) -> List[str]:
    nonlands = [c for c in hand if not is_land(c)]
    nonlands.sort(key=lambda c: -C(c).mv)
    return nonlands[:n] if len(nonlands) >= n else (nonlands + [c for c in hand if is_land(c)])[:n]

# =========================================================
# LAND DROP
# =========================================================

def play_land(state: GameState, log: List[Dict]):
    if state.land_played:
        return
    lands_in_hand = [c for c in state.hand if is_land(c)]
    if not lands_in_hand:
        return
    # prioriza terreno que cobre cor que falta
    have_colors = set()
    for c in state.battlefield:
        have_colors |= C(c).produces
    missing = {"W", "U", "B", "R", "G"} - have_colors
    best = None
    for c in lands_in_hand:
        if C(c).produces & missing:
            best = c
            break
    choice = best or lands_in_hand[0]
    state.hand.remove(choice)
    state.battlefield.append(choice)
    state.land_played = True
    state.lands_played_total += 1
    on_land_enters(state, log)

def on_land_enters(state: GameState, log: List[Dict]):
    # Evolution Sage: "Landfall - Whenever a land you control enters,
    # proliferate." Achado real 2026-08-28: sem NENHUM despacho de landfall
    # nesse arquivo, mesma classe do bug do Beorn. Achado real 2026-08-28
    # (2a rodada, regra nova de lealdade): agora que a lealdade de
    # planeswalker E' rastreada de verdade, proliferate tem um alvo real -
    # aplicado via proliferate_loyalty() (+1 lealdade em cada planeswalker
    # que controla, dobrado se Doubling Season/Vorinclex em campo).
    if "Evolution Sage" in state.battlefield:
        state.evolution_sage_proliferates += 1
        proliferate_loyalty(state, log, source="evolution_sage")

def do_land_fetch_spell(state: GameState, card: str, log: List[Dict]):
    """Farseek/Nature's Lore/Three Visits - busca real de terreno, corrigindo
    o achado 2026-08-28: eram Sorcery generica sem NENHUM efeito de board,
    puro sink de mana."""
    pool = FARSEEK_POOL if card == "Farseek" else FOREST_FETCH_POOL
    available = [c for c in state.library if c in pool]
    if not available:
        return
    have_colors = set()
    for c in state.battlefield:
        have_colors |= C(c).produces
    missing = {"W", "U", "B", "R", "G"} - have_colors
    best = next((c for c in available if C(c).produces & missing), available[0])
    state.library.remove(best)
    state.battlefield.append(best)
    if card == "Farseek":
        state.tapped_lands_this_turn.add(best)  # "put onto the battlefield tapped"
    log.append({"action": "land_fetch", "card": card, "target": best, "turn": state.turn})
    on_land_enters(state, log)


def _carth_lion_look_at_top7(state: GameState, log: List[Dict], source: str):
    """Carth the Lion (Scryfall, oraculo real): 'Whenever Carth enters
    or a planeswalker you control dies, look at the top seven cards of
    your library. You may reveal a planeswalker card from among them
    and put it into your hand. Put the rest on the bottom of your
    library in a random order.'

    Extraido de `do_carth_etb` (achado real 2026-09-20, ao auditar como
    `remove_permanent` do modo de resiliencia deveria interagir com
    `state.loyalty`): 2 bugs reais encontrados na mesma funcao, os 2
    JA' alcancaveis em modo padrao, sem relacao nenhuma com o modo de
    resiliencia -- so' achados por estar auditando esta area por outro
    motivo.

    1. **"Put the rest on the bottom" estava colocando no TOPO**
       (`state.library = top7 + rest`) -- inverteu duas vezes o
       posicionamento real (nem "topo" nem realmente "random" no
       sentido correto de fundo). Corrigido: `rest + shuffled_top7`.
    2. **A metade "morte de planeswalker" nunca disparava** -- o
       comentario original (2026-09-01) dizia que "nada remove nossos
       planeswalkers uma vez em campo", mas isso ja' era falso mesmo em
       modo padrao: `add_loyalty()` mata um planeswalker de verdade
       quando a lealdade cai a 0 ou menos (ex.: ultimate que zera a
       propria lealdade) -- medido: 1.861 mortes de planeswalker em
       3.000 partidas de modo padrao, nao um evento raro. Ver hook
       adicionado em `add_loyalty()`."""
    top7 = state.library[:7]
    rest = state.library[7:]
    pw_in_top7 = [c for c in top7 if C(c).type == "Planeswalker"]
    if pw_in_top7:
        found = pw_in_top7[0]
        top7.remove(found)
        state.hand.append(found)
        state.carth_tutors_total += 1
        log.append({"trigger": "carth_tutor", "found": found, "source": source, "turn": state.turn})
    state.rng.shuffle(top7)
    state.library = rest + top7


def do_carth_etb(state: GameState, log: List[Dict]):
    _carth_lion_look_at_top7(state, log, source="etb")

def try_fabled_passage(state: GameState, log: List[Dict]):
    """Fabled Passage: '{T}, Sacrifice this land: Search your library for a
    basic land card, put it onto the battlefield tapped, then shuffle. Then
    if you control four or more lands, untap that land.' Ativa assim que
    entra (nenhum motivo real pra segurar - vira um basico de verdade, que
    o resto do motor ja sabe usar pra mana)."""
    if "Fabled Passage" not in state.battlefield:
        return
    available = [c for c in state.library if c in BASIC_LAND_NAMES]
    if not available:
        return
    have_colors = set()
    for c in state.battlefield:
        have_colors |= C(c).produces
    missing = {"W", "U", "B", "R", "G"} - have_colors
    best = next((c for c in available if C(c).produces & missing), available[0])
    state.library.remove(best)
    state.battlefield.remove("Fabled Passage")
    state.battlefield.append(best)
    lands_now = sum(1 for c in state.battlefield if is_land(c))
    if lands_now < 4:
        state.tapped_lands_this_turn.add(best)  # so' fica tapped se < 4 terrenos
    log.append({"action": "fabled_passage_crack", "target": best, "turn": state.turn})
    on_land_enters(state, log)

# =========================================================
# BRIDGE ENGINE
# =========================================================
# LEALDADE DE PLANESWALKER (regra nova - ver goldfish-sim-card-rules.md #12)
# =========================================================

def counter_doubler_multiplier(state: GameState) -> int:
    # Doubling Season ("counters... twice that many") e Vorinclex, Monstrous
    # Raider (mesmo efeito pros NOSSOS counters) sao replacement effects
    # reais que dobram lealdade - empilham multiplicativamente (regra real,
    # mesmo padrao ja usado pros dobradores de token no Edgar Markov).
    # Achado real 2026-08-28 (usuario: "verifique as cartas com niveis...
    # o innkeeper's no Prismatic no nivel 3 DOBRA TODOS OS COUNTERS"):
    # Innkeeper's Talent nivel 3 ("If you would put one or more counters on
    # a permanent or player, put twice that many...") e' o MESMO efeito -
    # engine de leveling implementada (ver try_level_up_innkeepers_talent),
    # empilha com os outros 2 igual.
    n = sum(1 for c in ("Doubling Season", "Vorinclex, Monstrous Raider") if state.has(c))
    if "Innkeeper's Talent" in state.battlefield and state.innkeepers_talent_level >= 3:
        n += 1
    return 2 ** n

INNKEEPERS_TALENT_LEVEL_COST = {2: 1, 3: 4}  # {G}=1 pro nivel 2, {3}{G}=4 pro nivel 3

def try_level_up_innkeepers_talent(state: GameState, log: List[Dict]):
    if "Innkeeper's Talent" not in state.battlefield or state.innkeepers_talent_level >= 3:
        return
    next_level = state.innkeepers_talent_level + 1
    cost = INNKEEPERS_TALENT_LEVEL_COST[next_level]
    if remaining_mana(state) < cost or color_sources(state, "G") < 1:
        return
    state.mana_spent_this_turn += cost
    state.innkeepers_talent_level = next_level
    log.append({"trigger": "innkeepers_talent_level_up", "level": next_level, "turn": state.turn})

def _planeswalker_dies(state: GameState, pw: str, log: List[Dict]):
    """Cascata de 'um planeswalker seu morre' -- extraida de `add_loyalty()`
    (achado real 2026-09-20, ao portar `remove_permanent` do modo de
    resiliencia) pra ser reusada tanto por lealdade chegando a 0 (causa
    original, self-inflicted via ultimate/custo) quanto por remocao/wipe de
    OPONENTE (`remove_permanent`) -- a regra real ("whenever a planeswalker
    you control dies") nao distingue a CAUSA da morte, so' que ela
    aconteceu. Mesmo comportamento de antes pro call site original
    (confirmado por regressao bit-a-bit do modo padrao)."""
    if pw in state.battlefield:
        state.battlefield.remove(pw)
    state.graveyard.append(pw)
    if pw in state.loyalty:
        del state.loyalty[pw]
    state.pw_deaths_total += 1
    log.append({"trigger": "planeswalker_death", "pw": pw, "turn": state.turn})
    # Carth the Lion, "...or a planeswalker you control dies" -- achado real
    # 2026-09-20, ver `_carth_lion_look_at_top7`.
    if "Carth the Lion" in state.battlefield:
        _carth_lion_look_at_top7(state, log, source="pw_death")


def add_loyalty(state: GameState, pw: str, amount: int, log: List[Dict], reason: str = ""):
    """Aplica uma mudanca de lealdade (positiva = ganha counters, negativa =
    remove) - so a parte POSITIVA e' dobrada por Doubling Season/Vorinclex
    (sao "puts counters", nao afetam remocao de lealdade pra pagar uma
    habilidade). Mata o planeswalker (remove de campo) se a lealdade
    chegar a 0 ou menos."""
    if pw not in state.loyalty:
        return
    if amount > 0:
        amount *= counter_doubler_multiplier(state)
    state.loyalty[pw] += amount
    log.append({"trigger": "loyalty_change", "pw": pw, "amount": amount,
                "new_loyalty": state.loyalty[pw], "reason": reason, "turn": state.turn})
    if state.loyalty[pw] <= 0:
        _planeswalker_dies(state, pw, log)

def proliferate_loyalty(state: GameState, log: List[Dict], source: str = ""):
    # "Choose any number of permanents/players... give each another counter
    # of each kind already there." Modelado so pra lealdade de planeswalker
    # (unico sistema de counters rastreado por este simulador) - sempre
    # escolhe proliferar TODOS os planeswalkers que controla (nunca ha
    # razao real pra nao escolher os proprios).
    for pw in list(state.loyalty.keys()):
        add_loyalty(state, pw, 1, log, reason=f"proliferate_{source}")

def planeswalker_enters(state: GameState, name: str, log: List[Dict]):
    base = PLANESWALKER_STARTING_LOYALTY[name]
    mult = counter_doubler_multiplier(state)
    state.loyalty[name] = base * mult
    log.append({"trigger": "planeswalker_enters", "pw": name, "loyalty": state.loyalty[name], "turn": state.turn})
    # Deepglow Skate: "When this creature enters, double the number of each
    # kind of counter on any number of target permanents" - ETB de UMA VEZ
    # SO (nao e' estatico), so' relevante se ela mesma entrar DEPOIS de um
    # planeswalker ja estar em campo (ver dispatch no cast normal dela).

def bridge_upkeep_trigger(state: GameState, log: List[Dict]):
    state.bridge_triggers += 1
    revealed_nonhit = []
    hit = None
    while state.library:
        card = state.library.pop(0)
        if C(card).type in ("Creature", "Planeswalker"):
            hit = card
            break
        revealed_nonhit.append(card)
    state.rng.shuffle(revealed_nonhit)
    state.library.extend(revealed_nonhit)
    if hit:
        state.battlefield.append(hit)
        if C(hit).type == "Creature":
            state.bridge_hits_creature += 1
            if hit == "Evolution Sage":
                pass  # landfall dela ja e' tratada em on_land_enters, nao precisa nada aqui
        else:
            state.bridge_hits_planeswalker += 1
            if state.first_pw_hit_turn is None:
                state.first_pw_hit_turn = state.turn
            planeswalker_enters(state, hit, log)
        log.append({"trigger": "bridge_hit", "card": hit, "type": C(hit).type, "turn": state.turn})
    else:
        state.bridge_no_hit_empty_library += 1
        log.append({"trigger": "bridge_no_hit", "reason": "biblioteca vazia", "turn": state.turn})

# Custo pra ativar cada habilitador de flash (generico, simplificacao - o
# Alchemist's Refuge exige G+U especificamente, tratado aqui so como 2
# generico ja que color_sources ja garante que essas cores existem no
# manabase). Emergence Zone se sacrifica ao ser usado (perde a fonte de
# mana permanentemente, nao so tapa).
FLASH_ENABLER_COST = {"Alchemist's Refuge": 2, "Emergence Zone": 1}

def choose_flash_enabler(state: GameState) -> Optional[str]:
    candidates = [c for c in state.battlefield if has_tag(c, "flash_enabler")]
    if not candidates:
        return None
    # prioriza o mais barato
    candidates.sort(key=lambda c: FLASH_ENABLER_COST.get(c, 0))
    return candidates[0]

def can_flash_bridge(state: GameState) -> bool:
    # A Bridge vem da zona de comando, nao precisa estar na mao (mesma
    # convencao do simulador do Thranduil: comandante sempre "disponivel").
    # IMPORTANTE: untap so acontece no MEU untap step (CR 500.1 - untap,
    # upkeep, draw). Terrenos ficam tapados do jeito que ficaram no meu
    # ultimo turno durante os turnos dos oponentes - entao a mana
    # disponivel pra flashar no end step alheio e o que sobrou NAO GASTO
    # do meu ultimo turno (state.mana_held_back), nao o total_mana atual.
    if state.bridge_in_play:
        return False
    enabler = choose_flash_enabler(state)
    if enabler is None:
        return False
    needed = FLASH_ENABLER_COST[enabler] + bridge_effective_mv(state)
    if state.mana_held_back < needed:
        return False
    for color in C(COMMANDER).colors:
        if color_sources(state, color) < 1:
            return False
    return True

def cast_bridge(state: GameState, log: List[Dict], via_flash: bool):
    # Contraataque (`try_smart_opponent_counter`, 7a categoria do modo de
    # resiliencia -- so' faz sentido no exato momento do cast, mesmo
    # padrao dos outros 6 decks): mana/enabler e taxa contam ANTES do
    # counter (CR 903.10a conta "cast", nao "resolved"), entrada em
    # campo so' DEPOIS de passar.
    if COMMANDER in state.hand:
        state.hand.remove(COMMANDER)
    mv = bridge_effective_mv(state)
    if via_flash:
        enabler = choose_flash_enabler(state)
        cost = FLASH_ENABLER_COST[enabler] + mv
        state.mana_held_back -= cost
        if enabler == "Emergence Zone":
            state.battlefield.remove(enabler)  # se sacrifica ao ativar
        log.append({"action": "flash_enabler_used", "card": enabler, "turn": state.turn})
    else:
        state.mana_spent_this_turn += mv
    state.bridge_cast_count += 1
    if try_smart_opponent_counter(state):
        log.append({"action": "cast_bridge_countered", "via_flash": via_flash, "turn": state.turn})
        return
    state.battlefield.append(COMMANDER)
    state.bridge_in_play = True
    state.bridge_cast_turn = state.turn
    if state.bridge_first_cast_turn is None:
        state.bridge_first_cast_turn = state.turn
    state.bridge_flash_cast = via_flash
    log.append({"action": "cast_bridge", "via_flash": via_flash, "turn": state.turn, "effective_mv": mv})

# =========================================================
# REMOCAO DO OPONENTE (premissa assumida - ver docstring)
# =========================================================

def protectors_in_play(state: GameState) -> List[str]:
    prot = ["Sterling Grove"]
    if state.with_greater_auramancy:
        prot.append("Greater Auramancy")
    return [p for p in prot if state.has(p)]

def resolve_removal_round(state: GameState, log: List[Dict]):
    if not state.bridge_in_play and not protectors_in_play(state):
        return
    for _ in range(N_OPPONENTS):
        if state.rng.random() >= REMOVAL_CHANCE_PER_OPPONENT:
            continue
        state.removal_attempts_total += 1
        prot = protectors_in_play(state)
        if prot:
            target = state.rng.choice(prot)
            state.battlefield.remove(target)
            state.graveyard.append(target)  # simplificacao: remocao = destroy (maioria dos casos reais)
            state.protectors_removed_count += 1
            log.append({"trigger": "removal", "target": target, "turn": state.turn})
        elif state.bridge_in_play:
            state.battlefield.remove(COMMANDER)
            state.bridge_in_play = False
            state.bridge_removed_count += 1
            log.append({"trigger": "removal", "target": COMMANDER, "turn": state.turn})
        else:
            state.removal_attempts_wasted += 1

def remove_permanent(state: GameState, name: str, log: List[Dict], source: str = "opponent"):
    """Ponto central de remocao de permanente do CAMPO pelo modo de
    resiliencia (7 categorias padronizadas, 2026-09-20 -- porte do
    Megatron/Ur-Dragon/Hei Bai/Markov/Ulalek/Toph). Diferente de
    `resolve_removal_round` (sistema ANTIGO, especifico deste deck, so'
    mira Bridge/protetores, sempre ativo desde o turno 1) -- por decisao
    do usuario, o modo de resiliencia NAO empilha os 2 sistemas: dentro
    dele, `resolve_removal_round` fica desligado (ver `play_turn(...,
    skip_legacy_removal=True)`) e SO' este chokepoint novo, com os
    mesmos gates/calibracao ja validados nos outros 6 decks, roda.

    Comandante: mesma convencao ja' usada em `resolve_removal_round`
    (vai pra zona de comando via CR 903.9 -- `bridge_in_play=False`,
    nunca cemiterio).

    Planeswalker: delega pra `_planeswalker_dies` (mesma cascata real de
    "um planeswalker seu morre" que a lealdade chegando a 0 usa --
    remove de `state.battlefield` E `state.loyalty`, dispara Carth the
    Lion se em campo).

    Token: deixa de existir sem ir pro cemiterio (mesma convencao dos
    outros decks -- nomes com "Token" no final, ver `make_pw_token`).
    Carta nomeada: vai pro cemiterio de verdade."""
    if name not in state.battlefield:
        return
    if name == COMMANDER:
        state.battlefield.remove(name)
        state.bridge_in_play = False
        return
    if name in state.loyalty:
        _planeswalker_dies(state, name, log)
        return
    state.battlefield.remove(name)
    if "Token" not in name:
        state.graveyard.append(name)

# =========================================================
# ATIVACAO DE PLANESWALKER (regra nova - ver goldfish-sim-card-rules.md #12)
# =========================================================
# Cada planeswalker so ativa UMA habilidade por turno (velocidade de
# feitico, CR 606.3) - garantido aqui por so' chamar o resolver 1x por PW
# por turno (activate_planeswalkers, chamada 1x no main_phase). Heuristica
# geral: prioriza a habilidade de maior valor real e sem downside
# simetrico (nunca usa uma habilidade que prejudica nosso proprio board
# sem necessidade); usa o ultimate assim que alcancavel se ele for
# claramente bom (nao simetrico); helper make_pw_token() reusa o padrao
# de criacao de token ja usado no resto do arquivo.

def make_pw_token(state: GameState, token_name: str, n: int, log: List[Dict]):
    for _ in range(n):
        state.battlefield.append(token_name)
    state.pw_tokens_created_total += n
    log.append({"trigger": "pw_token", "token": token_name, "count": n, "turn": state.turn})

def resolve_planeswalker(state: GameState, pw: str, log: List[Dict]):
    loy = state.loyalty[pw]
    state.pw_activations_total += 1

    if pw == "Aminatou, the Fateshifter":
        # +1: draw then put back (filtragem, sem vantagem liquida de cartas
        # - so registra a ativacao). -1 (blink proprio) e -6 (simetrico,
        # ajuda oponentes) ficam de fora - sem alvo/valor claro nesse motor.
        add_loyalty(state, pw, 1, log, reason="aminatou_plus1")

    elif pw == "Ashiok, Dream Render":
        # -1 e' a UNICA habilidade real - mill 4 + exila cemiterio de um
        # oponente. Sem efeito numerico no nosso lado (nao ha cemiterio de
        # oponente rastreado), mas e' denial real - conta como interacao.
        if loy >= 1:
            add_loyalty(state, pw, -1, log, reason="ashiok_minus1")
            state.pw_removal_proxy_total += 1

    elif pw == "Elspeth, Sun's Champion":
        if loy >= 7:
            add_loyalty(state, pw, -7, log, reason="elspeth_ultimate")
            state.pw_ultimates_used_total += 1  # emblem: +2/+2 e voar pras criaturas, estatico
        else:
            add_loyalty(state, pw, 1, log, reason="elspeth_plus1")
            make_pw_token(state, "Soldier Token", 3, log)

    elif pw == "Kaya, Intangible Slayer":
        # +2 sempre (drenagem real + cresce lealdade, sem downside - nao ha
        # razao pra preferir o modo "0" de compra, que nao drena).
        add_loyalty(state, pw, 2, log, reason="kaya_plus2")
        state.pw_life_lost_opponent_total += 3
        state.pw_life_gained_total += 3

    elif pw == "Liliana, Dreadhorde General":
        if loy >= 9:
            add_loyalty(state, pw, -9, log, reason="liliana_ultimate")
            state.pw_ultimates_used_total += 1
            state.pw_wipe_proxy_total += 1  # oponente sacrifica quase tudo
        else:
            add_loyalty(state, pw, 1, log, reason="liliana_plus1")
            make_pw_token(state, "Zombie Token", 1, log)

    elif pw == "Narset, Parter of Veils":
        # -2: olha 4, pega 1 nao-criatura-nao-terreno - carta real na mao.
        if loy >= 2:
            add_loyalty(state, pw, -2, log, reason="narset_minus2")
            state.draw(1)
            state.pw_draws_total += 1

    elif pw == "Nicol Bolas, Dragon-God":
        # Estatico real "has all loyalty abilities of all other
        # planeswalkers on the battlefield" NAO modelado - exigiria um
        # dispatch combinatorio (Bolas ganhando as habilidades de QUALQUER
        # outro PW simultaneamente em campo) desproporcional ao valor real:
        # a Bridge so acerta 1 permanente por gatilho, entao ter 2+
        # planeswalkers vivos ao mesmo tempo (nenhum morreu ainda) e' raro
        # por padrao. Documentado, nao omitido silenciosamente.
        if loy >= 8:
            add_loyalty(state, pw, -8, log, reason="bolas_ultimate")
            state.pw_ultimates_used_total += 1  # oponente sem lendaria perde o jogo - sinal de finisher
        else:
            add_loyalty(state, pw, 1, log, reason="bolas_plus1")
            state.draw(1)
            state.pw_draws_total += 1

    elif pw == "Oko, the Ringleader":
        # -1: cria Elk 3/3 real. +1: compra 2 descarta 2 (sem "crime"
        # rastreado, assume o pior caso - liquido 0 cartas, sem valor
        # numerico, so mantem a lealdade se -1 nao for pagavel).
        if loy >= 2:
            add_loyalty(state, pw, -1, log, reason="oko_minus1")
            make_pw_token(state, "Elk Token", 1, log)
        else:
            add_loyalty(state, pw, 1, log, reason="oko_plus1")

    elif pw == "Tamiyo, Compleated Sage":
        # -X: exila carta do CEMITERIO com MV=X, cria token copia dela -
        # recursao real (mesma categoria da regra de RECURSION). Escolhe o
        # maior X pagavel que tenha alvo real no cemiterio.
        gy_creatures = [c for c in state.graveyard if C(c).type in ("Creature", "Artifact", "Enchantment", "Planeswalker")]
        by_mv = {}
        for c in gy_creatures:
            if C(c).mv not in by_mv:
                by_mv[C(c).mv] = c
        affordable = sorted((mv, c) for mv, c in by_mv.items() if mv <= loy)
        if affordable:
            mv, target = affordable[-1]
            add_loyalty(state, pw, -mv, log, reason="tamiyo_sage_minusX")
            state.graveyard.remove(target)
            state.battlefield.append(target)  # token copia - simplificado como o mesmo nome em campo
            if C(target).type == "Planeswalker":
                planeswalker_enters(state, target, log)
            elif C(target).type == "Creature":
                state.creature_cast_turn[target] = state.turn
            state.pw_recursion_total += 1
            log.append({"trigger": "tamiyo_sage_token_copy", "of": target, "turn": state.turn})
        elif loy >= 7:
            add_loyalty(state, pw, -7, log, reason="tamiyo_sage_ultimate")
            state.pw_ultimates_used_total += 1  # Tamiyo's Notebook - sem efeito numerico modelado
        else:
            add_loyalty(state, pw, 1, log, reason="tamiyo_sage_plus1")  # sem alvo pro tap, so cresce

    elif pw == "Tamiyo, Field Researcher":
        if loy >= 7:
            add_loyalty(state, pw, -7, log, reason="tamiyo_researcher_ultimate")
            state.pw_ultimates_used_total += 1
            state.draw(3)
            state.pw_draws_total += 3  # emblem de cast gratis nao modelado (sem alvo/limite claro)
        else:
            add_loyalty(state, pw, 1, log, reason="tamiyo_researcher_plus1")  # gatilho de dano de combate, sem combate modelado

    elif pw == "Teferi, Hero of Dominaria":
        if loy >= 8:
            add_loyalty(state, pw, -8, log, reason="teferi_hero_ultimate")
            state.pw_ultimates_used_total += 1  # emblem exila permanente de oponente ao comprar - sem oponente real
        else:
            add_loyalty(state, pw, 1, log, reason="teferi_hero_plus1")
            state.draw(1)
            state.pw_draws_total += 1  # untap de 2 lands no proximo end step - sem valor de instant-speed modelado

    elif pw == "Teferi, Temporal Archmage":
        if loy >= 10:
            add_loyalty(state, pw, -10, log, reason="teferi_archmage_ultimate")
            state.pw_ultimates_used_total += 1  # emblem de ativar loyalty a qualquer momento - sem instant-speed modelado
        else:
            add_loyalty(state, pw, 1, log, reason="teferi_archmage_plus1")
            state.draw(1)
            state.pw_draws_total += 1  # olha 2, fica com 1 - carta real selecionada

    elif pw == "Teferi, Time Raveler":
        # -3: "up to one target" bounce (opcional) + compra 1 - sempre pode
        # escolher ZERO alvos e so comprar, sem downside.
        if loy >= 3:
            add_loyalty(state, pw, -3, log, reason="teferi_raveler_minus3")
            state.draw(1)
            state.pw_draws_total += 1
        else:
            add_loyalty(state, pw, 1, log, reason="teferi_raveler_plus1")  # flash pra sorceries - sem valor de instant-speed modelado

    elif pw == "Teferi, Who Slows the Sunset":
        if loy >= 7:
            add_loyalty(state, pw, -7, log, reason="teferi_sunset_ultimate")
            state.pw_ultimates_used_total += 1
            state.teferi_sunset_emblem = True
        elif loy >= 2:
            add_loyalty(state, pw, -2, log, reason="teferi_sunset_minus2")
            state.draw(1)
            state.pw_draws_total += 1
        else:
            add_loyalty(state, pw, 1, log, reason="teferi_sunset_plus1")
            state.pw_life_gained_total += 2

    elif pw == "The Eternal Wanderer":
        # "0" custa 0 lealdade, cria Samurai 2/2 double strike de graca -
        # sempre a melhor escolha (sem custo, sem risco).
        add_loyalty(state, pw, 0, log, reason="eternal_wanderer_zero")
        make_pw_token(state, "Samurai Token", 1, log)

    elif pw == "Ugin, the Spirit Dragon":
        if loy >= 10:
            add_loyalty(state, pw, -10, log, reason="ugin_ultimate")
            state.pw_ultimates_used_total += 1
            state.pw_life_gained_total += 7
            state.draw(7)
            state.pw_draws_total += 7
            # "put up to seven permanent cards from your hand onto the
            # battlefield" - mesmo padrao do Last March of the Ents no
            # Beorn (coloca em campo de graca, sem pagar custo).
            free_permanents = [c for c in state.hand if C(c).type != "Instant" and C(c).type != "Sorcery"][:7]
            for c in free_permanents:
                state.hand.remove(c)
                state.battlefield.append(c)
                if C(c).type == "Creature":
                    state.creature_cast_turn[c] = state.turn
                elif C(c).type == "Planeswalker":
                    planeswalker_enters(state, c, log)
                log.append({"trigger": "ugin_ultimate_free_permanent", "card": c, "turn": state.turn})
        else:
            add_loyalty(state, pw, 2, log, reason="ugin_plus2")
            state.pw_removal_proxy_total += 1  # "3 dano a qualquer alvo" - sem alvo de oponente real

    elif pw == "Vraska, Betrayal's Sting":
        # "0": compra 1 + proliferate - sempre a melhor escolha (sem custo
        # de lealdade, e agora proliferate tem alvo real - lealdade dos
        # OUTROS planeswalkers que controla).
        add_loyalty(state, pw, 0, log, reason="vraska_zero")
        state.draw(1)
        state.pw_draws_total += 1
        proliferate_loyalty(state, log, source="vraska")

def try_chain_veil_activation(state: GameState, log: List[Dict]):
    """Achado real: '{4}, {T}: For each planeswalker you control, you
    may activate one of its loyalty abilities once this turn as though
    none of its loyalty abilities have been activated this turn.'
    Habilidade ativada real, paga -- nunca era conjurada com efeito
    algum (so' entrava em campo). So' vale pagar se ha' planeswalker
    real em campo pra se beneficiar."""
    if "The Chain Veil" not in state.battlefield or state.chain_veil_activated_this_turn:
        return
    if not state.loyalty:
        return
    if remaining_mana(state) < 4:
        return
    state.mana_spent_this_turn += 4
    state.chain_veil_activated_this_turn = True
    state.chain_veil_activations_total += 1
    log.append({"trigger": "chain_veil_activation", "turn": state.turn})

def try_urza_saga_tick(state: GameState, log: List[Dict]):
    """Achado real: Saga real (Read ahead) 100% ausente. Capitulo I:
    scry 4 (nao modelado, sem infra de scry neste arquivo) + revela o
    topo, planeswalker vai pra mao. Capitulo II: planeswalker MV<=6 da
    mao pra campo de graca. Capitulo III: libera ativacao dupla de
    lealdade so' neste turno (via extra_pw_activation_sources()), depois
    sacrifica (regra real de Saga: 'Sacrifice after III')."""
    if "Urza Assembles the Titans" not in state.battlefield:
        return
    if state.urza_last_ticked_turn == state.turn:
        return
    state.urza_last_ticked_turn = state.turn
    state.urza_chapter += 1
    ch = state.urza_chapter
    if ch == 1:
        if state.library and C(state.library[0]).type == "Planeswalker":
            state.hand.append(state.library.pop(0))
            state.urza_pw_tutored_total += 1
    elif ch == 2:
        pw_in_hand = [c for c in state.hand if C(c).type == "Planeswalker" and C(c).mv <= 6]
        if pw_in_hand:
            best = max(pw_in_hand, key=lambda c: C(c).mv)
            state.hand.remove(best)
            state.battlefield.append(best)
            planeswalker_enters(state, best, log)
            state.urza_pw_cheated_total += 1
    elif ch == 3:
        state.urza_chapter_iii_this_turn = True
    if ch >= 3 and "Urza Assembles the Titans" in state.battlefield:
        state.battlefield.remove("Urza Assembles the Titans")
        state.graveyard.append("Urza Assembles the Titans")
    log.append({"trigger": "urza_saga_chapter", "chapter": ch, "turn": state.turn})

def extra_pw_activation_sources(state: GameState) -> int:
    """Achado real: 3 fontes reais e distintas de ativar lealdade mais de
    1x por turno, todas aditivas (cada uma concede 'mais uma' ativacao,
    nao se sobrepoe): Oath of Teferi (estatico, sempre liga enquanto em
    campo), The Chain Veil (pago neste turno, {4},{T}) e Urza Assembles
    the Titans capitulo III (so' no turno em que resolve)."""
    extra = 0
    if state.has("Oath of Teferi"):
        extra += 1
    if state.chain_veil_activated_this_turn:
        extra += 1
    if state.urza_chapter_iii_this_turn:
        extra += 1
    return extra

def activate_planeswalkers(state: GameState, log: List[Dict]):
    # Carth the Lion: "Planeswalkers' loyalty abilities you activate cost
    # an additional {1} to activate." Achado real 2026-09-01 (leitura
    # linha-a-linha, "compile TUDO"): estatico real, sem excecao pros
    # NOSSOS proprios planeswalkers - aplicado como custo de mana real
    # antes de CADA ativacao (inclusive as extras, se sobrar mana), se
    # nao sobrar mana, essa ativacao especifica e' pulada nesse turno,
    # sem gastar loyalty de graca.
    carth_tax = 1 if state.has("Carth the Lion") else 0
    extra = extra_pw_activation_sources(state)
    for pw in list(state.loyalty.keys()):
        for _ in range(1 + extra):
            if pw not in state.battlefield:
                break  # morreu por outro efeito nesse meio tempo (Deepglow Skate etc. nao removem, so seguranca)
            if carth_tax and remaining_mana(state) < carth_tax:
                break
            if carth_tax:
                state.mana_spent_this_turn += carth_tax
            resolve_planeswalker(state, pw, log)

# =========================================================
# TURNO
# =========================================================

def main_phase(state: GameState, log: List[Dict]):
    # Subir de nivel a Innkeeper's Talent primeiro (sorcery speed, pilha
    # vazia) - se alcancar nivel 3 neste turno, o dobro de counter so vale
    # pra gatilhos QUE AINDA VAO ACONTECER neste turno em diante (nao
    # retroage sobre o upkeep da Bridge, que ja resolveu antes do main
    # phase, mesma ordem real do jogo).
    try_level_up_innkeepers_talent(state, log)

    # Urza (se ja estava em campo de um turno anterior) e Chain Veil (pago)
    # precisam resolver ANTES da ativacao de lealdade, pra que a 2a/3a
    # ativacao por planeswalker (extra_pw_activation_sources) ja valha
    # neste mesmo turno.
    try_urza_saga_tick(state, log)
    try_chain_veil_activation(state, log)

    # Ativa a habilidade de lealdade de cada planeswalker em campo primeiro
    # (velocidade de feitico, pilha vazia, mesmo momento real que um
    # jogador faria isso) - qualquer compra/mana disso alimenta o resto do
    # turno.
    activate_planeswalkers(state, log)

    # protetores primeiro (sao baratos e habilitam a Bridge)
    protection_cards = [c for c in state.hand if has_tag(c, "protection_shroud") and can_cast(state, c)]
    for c in sorted(protection_cards, key=lambda c: C(c).mv):
        state.hand.remove(c)
        state.mana_spent_this_turn += C(c).mv
        state.battlefield.append(c)
        log.append({"action": "cast", "card": c, "turn": state.turn})

    try_fabled_passage(state, log)

    # Bridge via main phase normal, se nao foi flashada nesse ciclo.
    # Sob HOLD_FOR_FLASH_POLICY, se um habilitador de flash ja esta em
    # campo, o jogador segura a Bridge de proposito (nao conjura normal
    # mesmo pagavel) e espera a janela de flash no end step alheio.
    skip_normal_cast = HOLD_FOR_FLASH_POLICY and choose_flash_enabler(state) is not None
    if not state.bridge_in_play and not skip_normal_cast and can_cast(state, COMMANDER):
        cast_bridge(state, log, via_flash=False)

    # Se ja tem habilitador de flash em campo e a Bridge ainda nao saiu,
    # o jogador segura mana de proposito pra linha de flash no end step
    # alheio (plano de jogo explicito do usuario) - nao gasta tudo no
    # resto da mao.
    reserved = 0
    if not state.bridge_in_play:
        enabler = choose_flash_enabler(state)
        if enabler is not None:
            reserved = FLASH_ENABLER_COST[enabler] + bridge_effective_mv(state)

    # resto da mao, ordem generica por CMC crescente, respeitando a reserva
    for _ in range(8):
        budget = remaining_mana(state) - reserved
        castables = [c for c in state.hand if c != COMMANDER and can_cast(state, c) and C(c).mv <= budget]
        if not castables:
            break
        castables.sort(key=lambda c: C(c).mv)
        choice = castables[0]
        state.hand.remove(choice)
        state.mana_spent_this_turn += C(choice).mv

        # Achados reais 2026-09-01 (leitura linha-a-linha, "compile TUDO" -
        # a nota antiga do docstring listava estas 5 fontes de proliferate
        # como deferidas por volume; implementadas aqui reusando
        # `proliferate_loyalty()`, ja testada pro Evolution Sage/Vraska):
        # Flux Channeler/Inexorable Tide ("whenever you cast a
        # noncreature/any spell, proliferate") + Mutational
        # Advantage/Ripples of Potential (proliferate no proprio efeito ao
        # serem conjuradas). Ichormoon Gauntlet permanece fora de escopo -
        # concede uma habilidade de lealdade NOVA a cada um dos 17
        # planeswalkers (exigiria reestruturar a logica hardcoded por-PW
        # de `resolve_planeswalker()`, escopo desproporcional ao resto
        # desta rodada), ver docstring.
        # Fontes independentes (permanentes DIFERENTES) - proliferam
        # separadamente se ambas estiverem em campo, nao mutuamente exclusivas.
        if state.has("Inexorable Tide"):
            proliferate_loyalty(state, log, source="inexorable_tide")
        if state.has("Flux Channeler") and C(choice).type != "Creature":
            proliferate_loyalty(state, log, source="flux_channeler")
        if choice in ("Mutational Advantage", "Ripples of Potential"):
            proliferate_loyalty(state, log, source=choice.lower().replace(" ", "_").replace(",", ""))

        if has_tag(choice, "removal") or has_tag(choice, "counterspell") or has_tag(choice, "wipe"):
            # Achado real: essas 11 cartas nunca contavam pra metrica de
            # interacao (Regra 1 ja corretamente nao aplica o efeito
            # destrutivo/de contramagia sem alvo/spell de oponente real,
            # mas nem o "foi conjurada" era contado, ao contrario de todos
            # os outros decks desta sessao).
            state.interaction_spells_cast_total += 1

        if C(choice).type in ("Instant", "Sorcery"):
            state.graveyard.append(choice)
        else:
            state.battlefield.append(choice)
            if choice == "Urza Assembles the Titans":
                try_urza_saga_tick(state, log)  # capitulo I dispara no proprio turno do cast
            if C(choice).type == "Creature":
                state.creature_cast_turn[choice] = state.turn
                if choice == "Deepglow Skate" and state.loyalty:
                    # "When this creature enters, double the number of each
                    # kind of counter on any number of target permanents."
                    # ETB de UMA VEZ SO (nao e' estatico) - achado real
                    # 2026-08-28 (regra nova de lealdade): sempre escolhe
                    # dobrar TODOS os planeswalkers que ja estao em campo
                    # (nunca ha razao real pra nao escolher).
                    for pw in list(state.loyalty.keys()):
                        add_loyalty(state, pw, state.loyalty[pw], log, reason="deepglow_skate_etb")
                if choice == "Sphinx of the Second Sun":
                    # "When this creature enters, IF YOU CAST IT, take an
                    # extra turn after this one." Achado real 2026-09-01
                    # (leitura linha-a-linha, "compile TUDO"): "if you cast
                    # it" so' e' satisfeito neste caminho (conjurada de
                    # verdade da mao) - quando a Bridge POE a carta em campo
                    # (nao conjura), essa condicao nao e' satisfeita (regra
                    # real, nao omissao), ver `bridge_upkeep_trigger()`.
                    state.extra_turns_pending += 1
                    state.sphinx_extra_turns_total += 1
                    state.sphinx_sacrifice_pending = True
                    log.append({"trigger": "sphinx_second_sun_extra_turn", "turn": state.turn})
                if choice == "Carth the Lion":
                    do_carth_etb(state, log)
        if choice in LAND_FETCH_SPELLS:
            do_land_fetch_spell(state, choice, log)
        log.append({"action": "cast", "card": choice, "turn": state.turn})

def play_turn(state: GameState, turn: int, game_log: List[List[Dict]], skip_legacy_removal: bool = False):
    """`skip_legacy_removal`: usado SO' pelo modo de resiliencia
    (`simulate_one_with_interaction`) -- desliga `resolve_removal_round`
    (sistema ANTIGO, especifico deste deck) pra evitar empilhar com o
    novo sistema padronizado de 7 categorias (decisao do usuario,
    2026-09-20: modo de resiliencia SUBSTITUI o antigo, nao soma).
    Default `False` preserva 100% o comportamento de todo call site
    existente (`simulate_one` nunca passa este argumento)."""
    state.turn = turn
    state.land_played = False
    state.mana_spent_this_turn = 0
    state.tapped_lands_this_turn = set()
    state.chain_veil_activated_this_turn = False
    state.urza_chapter_iii_this_turn = False
    log = []

    if state.sphinx_sacrifice_pending:
        # "At the beginning of that turn's upkeep, sacrifice Sphinx of
        # the Second Sun." Achado real 2026-09-01. Este e' exatamente o
        # inicio da propria turma extra concedida (flag setada no cast,
        # consumida aqui no proximo play_turn() - que so' pode ser a
        # extra, ja que o upkeep do turno QUE disparou ja passou antes
        # do main_phase setar a flag).
        if "Sphinx of the Second Sun" in state.battlefield:
            state.battlefield.remove("Sphinx of the Second Sun")
            state.graveyard.append("Sphinx of the Second Sun")
        state.sphinx_sacrifice_pending = False

    # Linha de flash no end step do oponente anterior (ver docstring: modelado
    # como acontecendo ANTES da rodada de remocao deste turno, entao a Bridge
    # flashada escapa da rodada de remocao que precede seu primeiro gatilho)
    if can_flash_bridge(state):
        cast_bridge(state, log, via_flash=True)

    if not skip_legacy_removal:
        resolve_removal_round(state, log)

    if state.bridge_in_play:
        n_triggers = 2 if state.has("Paradox Haze") else 1
        for _ in range(n_triggers):
            bridge_upkeep_trigger(state, log)

    state.draw(1)
    if state.teferi_sunset_emblem:
        # Ultimate de Teferi, Who Slows the Sunset: "You draw a card during
        # each opponent's draw step." Este motor so avanca os PROPRIOS
        # turnos - modelado como N_OPPONENTS compras extras por ciclo do
        # nosso turno, mesma premissa/convencao ja usada em
        # REMOVAL_CHANCE_PER_OPPONENT (ver docstring do arquivo).
        state.draw(N_OPPONENTS)
        state.pw_draws_total += N_OPPONENTS
    play_land(state, log)
    main_phase(state, log)

    # Mana nao gasta neste turno fica destapada ate o MEU proximo untap
    # step (CR 500.1) - e a mana real disponivel pra flashar algo no end
    # step de um oponente antes do meu proximo turno.
    state.mana_held_back = max(0, total_mana(state) - state.mana_spent_this_turn)

    game_log.append(log)

# =========================================================
# SIMULACAO
# =========================================================

def build_decklist(with_greater_auramancy: bool) -> str:
    if not with_greater_auramancy:
        return DECKLIST_TEXT
    # troca 1 carta de baixo synergy score/pouco impacto pela Greater Auramancy
    # (The Peregrine Dynamo - unica criatura sem nenhuma tag de sinergia)
    return DECKLIST_TEXT.replace("1 The Peregrine Dynamo\n", "1 Greater Auramancy\n")

def simulate_one(seed: int, turns: int, with_greater_auramancy: bool) -> Dict:
    rng = random.Random(seed)
    decklist = build_decklist(with_greater_auramancy)
    deck = parse_decklist(decklist)
    assert len(deck) == 99, f"Mainboard deveria ser 99, deu {len(deck)}"
    rng.shuffle(deck)
    state = GameState(rng=rng, library=deck, with_greater_auramancy=with_greater_auramancy)

    mulligans = 0
    while True:
        state.hand = []
        state.draw(7)
        if should_keep(state.hand) or mulligans >= 2:
            break
        mulligans += 1
        state.library.extend(state.hand)
        state.hand = []
        rng.shuffle(state.library)
    # Achado real 2026-09-18 (mesma convencao dos goldfishes manuais do
    # usuario no Archidekt): 1o mulligan e' GRATIS, so' o 2o+ bota cartas.
    penalty = max(0, mulligans - 1)
    if penalty:
        bottoms = choose_bottom(state.hand, penalty)
        for c in bottoms:
            state.hand.remove(c)
            state.library.append(c)
        rng.shuffle(state.library)

    game_log = []
    t = 0
    turns_played = 0
    while turns_played < turns:
        t += 1
        play_turn(state, t, game_log)
        turns_played += 1
        while state.extra_turns_pending > 0 and turns_played < turns:
            # Sphinx of the Second Sun: "take an extra turn after this
            # one" - achado real 2026-09-01. Inserida imediatamente
            # apos o turno que a disparou (mesma convencao ja usada nos
            # simuladores do Maralen/Megatron desta sessao).
            state.extra_turns_pending -= 1
            t += 1
            play_turn(state, t, game_log)
            turns_played += 1

    return {
        "seed": seed,
        "mulligans": mulligans,
        "bridge_cast_turn": state.bridge_cast_turn,
        "bridge_first_cast_turn": state.bridge_first_cast_turn,
        "bridge_flash_cast": state.bridge_flash_cast,
        "bridge_cast_count": state.bridge_cast_count,
        "bridge_in_play_end": state.bridge_in_play,
        "bridge_removed_count": state.bridge_removed_count,
        "bridge_triggers": state.bridge_triggers,
        "bridge_hits_creature": state.bridge_hits_creature,
        "bridge_hits_planeswalker": state.bridge_hits_planeswalker,
        "first_pw_hit_turn": state.first_pw_hit_turn,
        "bridge_no_hit": state.bridge_no_hit_empty_library,
        "protectors_removed_count": state.protectors_removed_count,
        "removal_attempts_total": state.removal_attempts_total,
        "lands_played_total": state.lands_played_total,
        "pw_activations_total": state.pw_activations_total,
        "pw_draws_total": state.pw_draws_total,
        "pw_tokens_created_total": state.pw_tokens_created_total,
        "pw_life_gained_total": state.pw_life_gained_total,
        "pw_life_lost_opponent_total": state.pw_life_lost_opponent_total,
        "pw_removal_proxy_total": state.pw_removal_proxy_total,
        "pw_wipe_proxy_total": state.pw_wipe_proxy_total,
        "pw_recursion_total": state.pw_recursion_total,
        "pw_ultimates_used_total": state.pw_ultimates_used_total,
        "pw_deaths_total": state.pw_deaths_total,
        "planeswalkers_in_play_end": len(state.loyalty),
        "innkeepers_talent_in_play": "Innkeeper's Talent" in state.battlefield,
        "innkeepers_talent_level_end": state.innkeepers_talent_level,
        # Achados reais 2026-09-01 (leitura linha-a-linha completa do oraculo):
        "sphinx_extra_turns_total": state.sphinx_extra_turns_total,
        "carth_tutors_total": state.carth_tutors_total,
        # Achados reais da auditoria oraculo-por-oraculo 2026-09-13/14:
        "interaction_spells_cast_total": state.interaction_spells_cast_total,
        "chain_veil_activations_total": state.chain_veil_activations_total,
        "urza_pw_tutored_total": state.urza_pw_tutored_total,
        "urza_pw_cheated_total": state.urza_pw_cheated_total,
        "urza_chapter_end": state.urza_chapter,
    }

def run_batch(n=2000, turns=10, with_greater_auramancy=False, seed_base=3000000, label=""):
    import statistics
    results = [simulate_one(seed_base + i, turns, with_greater_auramancy) for i in range(n)]

    bridge_turns = [r["bridge_cast_turn"] for r in results if r["bridge_cast_turn"] is not None]
    first_cast_turns = [r["bridge_first_cast_turn"] for r in results if r["bridge_first_cast_turn"] is not None]
    never = n - len(bridge_turns)
    flash_casts = sum(1 for r in results if r["bridge_flash_cast"])
    total_triggers = sum(r["bridge_triggers"] for r in results)
    total_hits_creature = sum(r["bridge_hits_creature"] for r in results)
    total_hits_pw = sum(r["bridge_hits_planeswalker"] for r in results)
    end_in_play = sum(1 for r in results if r["bridge_in_play_end"])
    avg_removed = sum(r["bridge_removed_count"] for r in results) / n
    avg_protectors_removed = sum(r["protectors_removed_count"] for r in results) / n
    avg_attempts = sum(r["removal_attempts_total"] for r in results) / n

    print(f"=== Prismatic Bridge Goldfish v1 ({label}) — n={n}, turns={turns} ===")
    print(f"Greater Auramancy no deck: {with_greater_auramancy}")
    print(f"Avg mulligans: {sum(r['mulligans'] for r in results)/n:.2f}")
    print(f"Bridge nunca conjurada em {turns} turnos: {100*never/n:.1f}%")
    if first_cast_turns:
        print(f"Turno medio da PRIMEIRA conjuracao da Bridge: {statistics.mean(first_cast_turns):.2f} | mediana: {statistics.median(first_cast_turns)}")
    if bridge_turns:
        print(f"Turno medio da ULTIMA conjuracao (inclui recasts pos-remocao, taxa de comandante +2 cada vez): {statistics.mean(bridge_turns):.2f} | mediana: {statistics.median(bridge_turns)}")
    print(f"Conjurada via flash (end step anterior): {100*flash_casts/n:.1f}% das partidas")
    print(f"Avg gatilhos de upkeep da Bridge por partida: {total_triggers/n:.2f}")
    print(f"  Acertos em criatura: {total_hits_creature} | em planeswalker: {total_hits_pw} | total: {total_hits_creature+total_hits_pw}")
    print(f"% da Bridge ainda em campo no fim da simulacao: {100*end_in_play/n:.1f}%")
    print(f"Avg vezes que a Bridge foi removida por partida: {avg_removed:.2f}")
    print(f"Avg vezes que um protetor (Sterling Grove/Greater Auramancy) foi removido: {avg_protectors_removed:.2f}")
    print(f"Avg tentativas de remocao do oponente por partida (premissa: {REMOVAL_CHANCE_PER_OPPONENT*100:.0f}%/oponente/turno, {N_OPPONENTS} oponentes): {avg_attempts:.2f}")

    pw_hit_turns = [r["first_pw_hit_turn"] for r in results if r["first_pw_hit_turn"] is not None]
    from collections import Counter
    c = Counter(pw_hit_turns)
    print(f"\n--- Bridge colocou planeswalker em jogo (1o acerto de PW via gatilho de upkeep) ---")
    for t in [6, 7, 8]:
        cum = sum(v for k, v in c.items() if k <= t)
        print(f"  Chance acumulada ate o turno {t}: {100*cum/n:.1f}%")
    never_pw = n - len(pw_hit_turns)
    print(f"  Nunca acertou planeswalker em {turns} turnos: {100*never_pw/n:.1f}%")

    # Achado real 2026-08-28 (usuario: "Preciso que os counters de lealdade
    # e ativacoes de planeswalker sejam sempre contabilizados") - antes
    # NENHUMA habilidade de planeswalker era simulada, so se a Bridge
    # acertava um. Agora os 17 planeswalkers tem lealdade real e ativam
    # uma habilidade real por turno em campo.
    print(f"\n--- Planeswalkers (lealdade + ativacoes reais, regra nova) ---")
    print(f"Avg ativacoes de habilidade de planeswalker por partida: {sum(r['pw_activations_total'] for r in results)/n:.2f}")
    print(f"Avg planeswalkers vivos no fim da simulacao: {sum(r['planeswalkers_in_play_end'] for r in results)/n:.2f}")
    print(f"Avg mortes de planeswalker (lealdade a 0) por partida: {sum(r['pw_deaths_total'] for r in results)/n:.2f}")
    print(f"Avg ultimates usados por partida: {sum(r['pw_ultimates_used_total'] for r in results)/n:.2f}")
    print(f"RECURSION (via Tamiyo, Compleated Sage -X): {sum(r['pw_recursion_total'] for r in results)/n:.2f}")
    print(f"DRAW: avg compras via planeswalker: {sum(r['pw_draws_total'] for r in results)/n:.2f}")
    print(f"Avg tokens criados via planeswalker: {sum(r['pw_tokens_created_total'] for r in results)/n:.2f}")
    print(f"Avg vida ganha via planeswalker: {sum(r['pw_life_gained_total'] for r in results)/n:.2f} | "
          f"vida perdida do oponente (proxy): {sum(r['pw_life_lost_opponent_total'] for r in results)/n:.2f}")
    print(f"INTERACTION: avg remocao proxy (Ashiok/Ugin, sem alvo real de oponente): "
          f"{sum(r['pw_removal_proxy_total'] for r in results)/n:.2f} | wipe proxy (Elspeth/Liliana ultimate): "
          f"{sum(r['pw_wipe_proxy_total'] for r in results)/n:.2f}")
    it_in_play = sum(1 for r in results if r["innkeepers_talent_in_play"])
    if it_in_play:
        it_lvl3 = sum(1 for r in results if r["innkeepers_talent_level_end"] >= 3)
        print(f"Innkeeper's Talent em campo em {100*it_in_play/n:.1f}% dos jogos, alcancou nivel 3 "
              f"(dobra TODOS os counters, inclusive lealdade de planeswalker ao entrar) em "
              f"{100*it_lvl3/n:.1f}%")
    print(f"Avg proliferates via Flux Channeler/Inexorable Tide/Mutational Advantage/Ripples of Potential "
          f"(achado 2026-09-01, implementado nesta rodada): "
          f"{sum(r['pw_activations_total'] for r in results)/n:.2f} ativacoes de PW no total (inclui esses proliferates)")
    print(f"Sphinx of the Second Sun (turno extra real, so' quando conjurada de verdade - nao via Bridge): "
          f"{sum(r['sphinx_extra_turns_total'] for r in results)/n:.3f} avg | "
          f"{100*sum(1 for r in results if r['sphinx_extra_turns_total']>0)/n:.1f}% dos jogos")
    print(f"Carth the Lion (tutor de planeswalker no ETB): {sum(r['carth_tutors_total'] for r in results)/n:.2f} avg | "
          f"{100*sum(1 for r in results if r['carth_tutors_total']>0)/n:.1f}% dos jogos")
    print(f"\n--- Auditoria oraculo-por-oraculo 2026-09-13/14 (achados novos) ---")
    print(f"INTERACTION (Counterspell/Mana Drain/Path/Swords/Anguished Unmaking/Damn/Void Rend/Toxic Deluge/"
          f"Blasphemous Act/Supreme Verdict/Farewell, so' contadas - Regra 1, sem efeito de bordo real): "
          f"{sum(r['interaction_spells_cast_total'] for r in results)/n:.2f} avg")
    print(f"Chain Veil ativado (dobra lealdade de TODOS os planeswalkers naquele turno): "
          f"{sum(r['chain_veil_activations_total'] for r in results)/n:.2f} avg | "
          f"{100*sum(1 for r in results if r['chain_veil_activations_total']>0)/n:.1f}% dos jogos")
    urza_cast_games = [r for r in results if r["urza_chapter_end"] >= 1]
    print(f"Urza Assembles the Titans: planeswalker tutorado (cap. I) {sum(r['urza_pw_tutored_total'] for r in results)/n:.2f} avg | "
          f"planeswalker colocado de graca (cap. II) {sum(r['urza_pw_cheated_total'] for r in results)/n:.2f} avg | "
          f"conjurada em {100*len(urza_cast_games)/n:.1f}% dos jogos, alcancou cap. III (dobra lealdade naquele "
          f"turno) em {100*sum(1 for r in urza_cast_games if r['urza_chapter_end']>=3)/len(urza_cast_games):.1f}% "
          f"desses" if urza_cast_games else "Urza Assembles the Titans: nunca conjurada nesta amostra")
    print(f"Deferido nesta rodada (nao implementado, documentado - genuinamente estrutural ou desproporcional): "
          f"estatico da Nicol Bolas ('has all loyalty abilities of all other planeswalkers' - exigiria uma "
          f"segunda camada de escolha por PW); Ichormoon Gauntlet (concede uma habilidade de lealdade NOVA a "
          f"cada um dos 17 planeswalkers - exigiria reestruturar a logica hardcoded por-PW de "
          f"resolve_planeswalker()); Arena Rector (gatilho de MORTE, nada remove nossas criaturas neste sim); "
          f"The Peregrine Dynamo (copiar gatilho entre N fontes legendarias, mesma excecao do Strionic Resonator).")
    print()
    return results

# =========================================================
# MODO OPCIONAL DE RESILIENCIA (interacao de oponente)
# =========================================================
# Porte do modo de resiliencia ja' implementado e validado no Megatron/
# Ur-Dragon/Hei Bai/Markov/Ulalek/Toph (usuario, 2026-09-20: "Repita o
# processo todo com o deck da Prismatic Bridge"). Aditivo e OPCIONAL --
# nunca chamado por `simulate_one`/`run_batch` (modo padrao), gated
# inteiramente por `state.interaction_rng`. Design final direto (mesmas 7
# categorias + as 3 rodadas de correcao de orquestracao de turno ja'
# validadas nos outros 6 decks), sem precisar reproduzir o historico.
#
# DIFERENCA REAL vs. os outros 6 decks: este arquivo JA TINHA um sistema
# de remocao de oponente proprio (`resolve_removal_round`, especifico
# pra decidir se vale Greater Auramancy -- 12%/oponente/turno, sempre
# ativo desde o turno 1, sem gates, mira so' Bridge/protetores). Por
# decisao EXPLICITA do usuario (perguntado antes de implementar, ver
# checklist-oraculo.md): o modo de resiliencia NAO empilha os 2 sistemas.
# `simulate_one_with_interaction` chama `play_turn(..., skip_legacy_
# removal=True)`, desligando o sistema antigo DENTRO do modo de
# resiliencia -- o modo PADRAO continua 100% intocado, `resolve_removal_
# round` roda exatamente como sempre rodou, respondendo a pergunta
# original do Greater Auramancy sem nenhuma mudanca.
#
# Outras diferencas estruturais reais (levadas em conta no design):
# - Planeswalkers sao rastreados em `state.loyalty` (nome -> lealdade),
#   ALEM de `state.battlefield` -- remocao/wipe precisa manter os 2
#   sincronizados. `remove_permanent` delega pra `_planeswalker_dies`
#   (mesma cascata que a lealdade chegando a 0 ja usa -- Carth the Lion
#   dispara igual, nao importa a causa da morte).
# - O comandante (The Prismatic Bridge) e' um ENCHANTMENT, nao criatura
#   -- board wipe ("destroy all creatures") nunca a alcanca por
#   definicao de tipo, so' remocao/counterspell dedicados.
# - Nenhum combate real e' modelado (sem funcao de ataque neste arquivo)
#   -- ataque de oponente aqui tambem conecta sem bloqueio, mesmo padrao
#   dos outros 6 decks.
# - `INTERACTION_ENGINE_PRIORITY` prioriza o planeswalker de MAIOR
#   lealdade em campo (motor dinamico real deste deck -- qualquer um
#   dos 17 pode estar em campo a qualquer momento, entao uma lista fixa
#   de nomes nao capturaria a ameaca real), com fallback pra uma lista
#   fixa curada de nao-planeswalkers recorrentes.
# - 📊 Nao corrigido nesta rodada (decisao documentada, nao esquecimento
#   -- mesma classe do token do Ugin no Ulalek): Arena Rector ("When
#   this creature dies, you may exile it... search for a planeswalker
#   card, put it onto the battlefield") so' importa se ELA especificamente
#   morrer -- ao contrario do bug real do Carth (ja' corrigido acima,
#   JA' alcancavel em modo padrao via lealdade chegando a 0, 1.861/3.000
#   jogos), morte de CRIATURA nomeada nunca foi possivel neste arquivo
#   antes desta rodada -- so' fica relevante especificamente quando MEU
#   novo wipe/remocao alcanca a propria Arena Rector, nao um
#   pre-requisito estrutural do port (diferente dos 2 fixes do Carth).

NUM_OPPONENTS = N_OPPONENTS  # reusa a mesma constante ja' declarada no topo do arquivo (mesa de 4, ja documentada)

INTERACTION_SETUP_TURNS = 2
# Turnos 1-2 sao sempre setup, sem chance de reacao nenhuma -- o
# oponente ainda nao tem motivo/mana pra reagir.

def interaction_chance(state: GameState) -> float:
    """Formula compartilhada de 'chance do oponente reagir esse turno' --
    identica aos outros 6 decks: escala com o impacto do meu proprio
    board (permanentes nao-terreno em campo)."""
    board_impact = sum(1 for n in state.battlefield if not is_land(n))
    return min(0.10 + 0.03 * board_impact, 0.75)

OPPONENT_ATTENTION_CHANCE = 1.0 / NUM_OPPONENTS
# Gate de "esse oponente esta' de olho em mim esse turno" (achado real
# do usuario nos outros decks, 2026-09-20: "se sempre for 3 contra 1,
# ai' nao consigo fazer nada, nunca!") -- por simetria, ha' 3 alvos
# possiveis pra atencao de qualquer oponente (eu e os outros 2 que este
# simulador nao modela), entao a chance BASE de que um turno de
# oponente qualquer seja sobre MIM e' 1/NUM_OPPONENTS, antes de
# qualquer ajuste por ameaca de board (que ja' fica dentro de
# `interaction_chance()`). Rolado 1x no INICIO de `try_smart_opponent_
# turn`, antes de qualquer categoria.

POST_WIPE_ATTACK_HASTE_FACTOR = 0.15
# Board wipe e' SIMETRICO -- acerta TODA criatura da mesa, nao so' as
# minhas. Se um wipe ja' aconteceu NESTA RODADA (`state.wiped_this_
# round`), TODOS os turnos de oponente restantes na mesma rodada
# tambem ficam sem criaturas de verdade pra atacar -- exceto por haste
# (fisicamente possivel, Regra #1 do CLAUDE.md: so' impossibilidade
# estrutural justifica nao modelar, nunca zerar por completo).

BOARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_SNIPE_CHANCE_FACTOR = 0.5
COUNTERSPELL_CHANCE_FACTOR = 0.5
# Mesmos fatores redutores dos outros 6 decks sobre a MESMA
# `interaction_chance()` compartilhada.

NONPLANESWALKER_ENGINE_PRIORITY = [
    "Doubling Season",
    "The Chain Veil",
    "Vorinclex, Monstrous Raider",
    "Innkeeper's Talent",
    "Deepglow Skate",
    "Carth the Lion",
    "Evolution Sage",
    "Flux Channeler",
]
# Fallback de `try_smart_opponent_removal` quando NENHUM planeswalker
# esta' em campo -- lista curada por prioridade (dobradores de
# contador/lealdade primeiro, maior multiplicador de valor do deck;
# depois ativacao extra, tutor de carta, proliferate). A propria Bridge
# fica de fora de proposito -- ja' tem categoria dedicada
# (`try_smart_opponent_counter`) e remocao nao a mata de verdade mesmo.

OPPONENT_ATTACKER_PROFILES = [
    ("Knight Token", 2), ("Saproling Token", 1), ("Vampire Token", 1),
    ("Zombie Token", 2), ("Soldier Token", 1), ("Goblin Token", 1),
    ("Elemental Token", 3),
]
# Mesmos perfis genericos ja' validados nos outros 6 decks -- sem
# toughness, este arquivo nao modela combate/bloqueio de um oponente de
# verdade. Todo ataque conecta.

def try_smart_opponent_removal(state: GameState, log: List[Dict]) -> Optional[str]:
    """Remocao 'inteligente' -- mira o planeswalker de MAIOR lealdade em
    campo (motor dinamico real deste deck), com fallback pra
    `NONPLANESWALKER_ENGINE_PRIORITY` se nenhum planeswalker estiver em
    campo. Nunca aleatorio.

    Achado real do usuario 2026-09-21: Sterling Grove/Greater Auramancy
    ('Other enchantments you control have shroud' -- confirmado via
    Scryfall, shroud de verdade, nao hexproof) blindam qualquer OUTRO
    encantamento contra remocao ALVO (nao contra wipe -- 'destroy
    all'/'exile all' nunca usa 'target', shroud nao se aplica la', ver
    `try_smart_opponent_wipe`). 2 dos 8 itens de `NONPLANESWALKER_
    ENGINE_PRIORITY` sao encantamentos de verdade (Doubling Season,
    Innkeeper's Talent) -- o sistema LEGADO (`resolve_removal_round`,
    ja' desligado no modo resiliencia) ja' respeitava isso via
    `protectors_in_play()`, redirecionando remocao pro PROTETOR primeiro
    (unico jeito de destravar o alvo real depois). Essa checagem nunca
    foi portada pra esta categoria nova -- corrigido aqui, reaproveitando
    a mesma `protectors_in_play()` de sempre. Planeswalkers nunca sao
    encantamento nesta lista (confirmado, sem hibrido), entao o ramo de
    lealdade nunca precisa de redirecionamento."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.loyalty:
        target = max(state.loyalty, key=lambda pw: state.loyalty[pw])
    else:
        target = next((n for n in NONPLANESWALKER_ENGINE_PRIORITY if n in state.battlefield), None)
    if target is None:
        return None
    if C(target).type == "Enchantment":
        prot = protectors_in_play(state)
        if prot:
            target = state.interaction_rng.choice(prot)
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    remove_permanent(state, target, log, source="opponent_removal")
    state.smart_removals_total += 1
    state.smart_removal_log.append((state.turn, target))
    return target

def try_smart_opponent_attack(state: GameState, log: List[Dict]) -> Optional[str]:
    """Ataque de oponente -- SEM bloqueio (limitacao estrutural: este
    arquivo nao modela combate/bloqueio de um oponente de verdade, nao
    tem nenhuma funcao de combate). Sempre conecta em `state.life`.

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

def try_smart_opponent_discard(state: GameState, log: List[Dict]) -> Optional[str]:
    """Discard aleatorio -- mesma logica dos outros 6 decks (alvo
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

ARTIFACT_WIPE_CHANCE_FACTOR = 0.2
ENCHANTMENT_WIPE_CHANCE_FACTOR = 0.15
# Pesos relativos de cada TIPO de sweeper (criatura/artefato/
# encantamento) -- nao sao 3 chances INDEPENDENTES (achado real do
# usuario 2026-09-20, mesma correcao feita primeiro no Megatron: "Vandalblast,
# Farewell, Austere Command, etc" tem que existir, MAS "Obviamente tem
# que ter uma alternancia de remocoes, aleatoria, ate pq wipes de
# criaturas sao muito mais comuns que remocao de artefatos e
# encantamentos"). Um oponente real, num turno so', conjura NO MAXIMO 1
# sweeper -- nunca "destroy all creatures" E "destroy all artifacts" no
# mesmo turno. `try_smart_opponent_wipe` rola 1x se ALGUM wipe acontece
# (chance = soma dos 3 pesos) e SO' DEPOIS escolhe qual tipo, com
# escolha ponderada pelos mesmos 3 fatores. The Chain Veil (ja' na
# `NONPLANESWALKER_ENGINE_PRIORITY`) e' um artefato real -- um wipe de
# artefato pode alcancar o maior multiplicador de ativacao do deck de
# uma vez. IMPORTANTE: a propria The Prismatic Bridge E' Enchantment
# (confirmado via Scryfall) -- este e' o UNICO dos 3 tipos de wipe
# (criatura/artefato/encantamento) que alcanca o comandante de verdade
# neste deck. `remove_permanent` ja' trata isso corretamente (CR 903.9,
# zona de comando em vez de cemiterio) sem precisar de excecao extra
# aqui.
WIPE_TYPE_WEIGHTS = {
    "creature": BOARD_WIPE_CHANCE_FACTOR,
    "artifact": ARTIFACT_WIPE_CHANCE_FACTOR,
    "enchantment": ENCHANTMENT_WIPE_CHANCE_FACTOR,
}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())


def try_smart_opponent_wipe(state: GameState, log: List[Dict]) -> Optional[list]:
    """Board wipe ('destroy all creatures'/'destroy all artifacts'/
    'destroy all enchantments') -- destroi TODOS os meus permanentes do
    tipo escolhido de uma vez via `remove_permanent`. Um wipe de
    CRIATURA nunca alcanca o comandante (Enchantment) nem planeswalkers
    -- so' `C(n).type == "Creature"` de verdade. Um wipe de ARTEFATO
    tambem nunca alcanca a Bridge (ela nunca e' artefato de verdade). Um
    wipe de ENCANTAMENTO E' O UNICO dos 3 tipos que alcanca o comandante
    de verdade neste deck (CR 903.9, `remove_permanent` ja' trata isso
    corretamente -- zona de comando em vez de cemiterio, sem precisar
    de excecao extra aqui).

    Design de 2 passos (nao 3 rolagens independentes -- ver comentario
    de `WIPE_TYPE_WEIGHTS` acima): 1) rola 1x se ALGUM wipe acontece
    esse turno de oponente, chance = `interaction_chance() *
    TOTAL_WIPE_CHANCE_FACTOR`; 2) SO' se isso disparar, escolhe qual
    TIPO de sweeper via escolha ponderada (`state.interaction_rng.
    choices`) restrita aos tipos que tem pelo menos 1 alvo legal em
    campo. Se o tipo escolhido nao for 'creature' mas algum alvo
    destruido TAMBEM for uma criatura de verdade, `state.wiped_this_
    round` e' setado igual -- nenhuma carta desta lista e' hibrida hoje,
    mas a checagem fica por robustez (uma troca futura pode adicionar
    um artifact/enchantment creature). Sem nenhum alvo legal de tipo
    nenhum, retorna None sem fazer nada."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    candidates = {
        "creature": [n for n in state.battlefield if C(n).type == "Creature"],
        "artifact": [n for n in state.battlefield if C(n).type == "Artifact"],
        "enchantment": [n for n in state.battlefield if C(n).type == "Enchantment"],
    }
    available = [t for t in candidates if candidates[t]]
    if not available:
        return None
    wipe_type = state.interaction_rng.choices(available, weights=[WIPE_TYPE_WEIGHTS[t] for t in available])[0]
    targets = candidates[wipe_type]
    hit_creature = any(C(n).type == "Creature" for n in targets)
    for n in targets:
        remove_permanent(state, n, log, source=f"opponent_{wipe_type}_wipe")
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

def try_smart_opponent_graveyard_wipe(state: GameState, log: List[Dict]) -> Optional[list]:
    """Graveyard hate, modelo MASS EXILE (Bojuka Bog/Soul-Guide
    Lantern-style) -- dispara NO MAXIMO 1x por partida inteira
    (`state.graveyard_wipe_used`)."""
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

def try_smart_opponent_graveyard_snipe(state: GameState, log: List[Dict]) -> Optional[str]:
    """Graveyard hate, modelo EXILIO DE CARTA UNICA (Scavenging
    Ooze/Cease-style) -- repetivel todo turno. Alvo SMART: maior MV
    entre criatura OU planeswalker no cemiterio -- mesmo criterio real
    que `Tamiyo, Compleated Sage -X` ja' usa pra escolher alvo de
    recursao (`by_mv`/`affordable`, qualquer permanente card, nao so'
    criatura)."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    candidates = [c for c in state.graveyard if C(c).type in ("Creature", "Planeswalker")]
    if not candidates:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_SNIPE_CHANCE_FACTOR:
        return None
    target = max(candidates, key=lambda n: C(n).mv)
    state.graveyard.remove(target)
    state.smart_graveyard_snipes_total += 1
    state.smart_graveyard_snipe_log.append((state.turn, target))
    return target

def try_smart_opponent_counter(state: GameState) -> bool:
    """Counterspell -- so' mira a conjuracao da propria Bridge (mesma
    logica dos outros 6 decks: o motor inteiro do deck depende do
    comandante resolver). Chamada de dentro de `cast_bridge()`, nao do
    loop de `simulate_one_with_interaction` -- so' faz sentido no exato
    momento do cast, dentro do MEU turno (cobre tanto cast normal
    quanto flash)."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * COUNTERSPELL_CHANCE_FACTOR:
        return False
    state.smart_counters_total += 1
    state.smart_counter_log.append(state.turn)
    return True

def try_smart_opponent_turn(state: GameState, log: List[Dict]):
    """Simula O TURNO DE UM oponente dentro da rodada entre os meus
    turnos (mesmo design final ja' validado nos outros 6 decks, Regra
    #6 do CLAUDE.md: bug de orquestracao de turno que auditoria
    carta-a-carta nao pega). Chamada `NUM_OPPONENTS` vezes por rodada --
    um wipe de um oponente ANTERIOR na rodada continua afetando
    corretamente o ataque de um oponente POSTERIOR na MESMA rodada
    (chamadas em sequencia, mesmo `state`).

    Gate de atencao: antes de rolar QUALQUER categoria, este turno de
    oponente precisa passar em `OPPONENT_ATTENTION_CHANCE`. Wipe e
    ataque nao precisam de exclusao mutua manual aqui: `try_smart_
    opponent_attack` ja' se auto-regula via `state.wiped_this_round`
    (setado por `try_smart_opponent_wipe`, que roda antes, dentro desta
    mesma chamada)."""
    if state.turn > INTERACTION_SETUP_TURNS and state.interaction_rng.random() >= OPPONENT_ATTENTION_CHANCE:
        return
    try_smart_opponent_wipe(state, log)
    try_smart_opponent_attack(state, log)
    try_smart_opponent_graveyard_wipe(state, log)
    try_smart_opponent_graveyard_snipe(state, log)
    try_smart_opponent_removal(state, log)
    try_smart_opponent_discard(state, log)

def simulate_one_with_interaction(seed: int, turns: int, with_greater_auramancy: bool = False) -> GameState:
    """Mesmo goldfish de `simulate_one`, mas com `NUM_OPPONENTS` turnos
    de oponente de verdade simulados (`try_smart_opponent_turn`) a cada
    rodada entre os meus turnos, e `resolve_removal_round` (sistema
    ANTIGO) desligado via `skip_legacy_removal=True` (ver decisao do
    usuario no topo da secao). Counterspell (7a categoria) NAO mora
    neste loop -- ver `try_smart_opponent_counter`, chamada de dentro de
    `cast_bridge` no exato momento do cast (normal ou flash).

    Mulligan duplicado (nao extraido pra helper compartilhado) de
    proposito -- este arquivo nunca teve uma funcao `mulligan()`
    separada, e extrair uma agora tocaria `simulate_one` (modo padrao)
    sem necessidade real -- mais seguro duplicar aqui.

    NUNCA chamado por `run_batch`/`simulate_one` padrao. Retorna o
    `GameState` bruto (nao um dict resumido como `simulate_one`), mesma
    convencao dos outros 6 decks."""
    rng = random.Random(seed)
    decklist = build_decklist(with_greater_auramancy)
    deck = parse_decklist(decklist)
    assert len(deck) == 99, f"Mainboard deveria ser 99, deu {len(deck)}"
    rng.shuffle(deck)
    state = GameState(rng=rng, library=deck, with_greater_auramancy=with_greater_auramancy,
                       interaction_rng=random.Random(seed + 999_999))

    mulligans = 0
    while True:
        state.hand = []
        state.draw(7)
        if should_keep(state.hand) or mulligans >= 2:
            break
        mulligans += 1
        state.library.extend(state.hand)
        state.hand = []
        rng.shuffle(state.library)
    penalty = max(0, mulligans - 1)
    if penalty:
        bottoms = choose_bottom(state.hand, penalty)
        for c in bottoms:
            state.hand.remove(c)
            state.library.append(c)
        rng.shuffle(state.library)

    game_log = []
    interaction_log: List[Dict] = []
    t = 0
    turns_played = 0
    while turns_played < turns:
        t += 1
        play_turn(state, t, game_log, skip_legacy_removal=True)
        turns_played += 1
        state.wiped_this_round = False
        for _ in range(NUM_OPPONENTS):
            try_smart_opponent_turn(state, interaction_log)
        while state.extra_turns_pending > 0 and turns_played < turns:
            state.extra_turns_pending -= 1
            t += 1
            play_turn(state, t, game_log, skip_legacy_removal=True)
            turns_played += 1
            state.wiped_this_round = False
            for _ in range(NUM_OPPONENTS):
                try_smart_opponent_turn(state, interaction_log)
    return state

def run_batch_with_interaction(n=2000, turns=10, with_greater_auramancy=False, seed_base=6000000):
    """Batch do modo de resiliencia -- reporta so' as metricas
    relevantes pra 'o motor aguenta perder a peca central?', nao
    duplica o relatorio inteiro do `run_batch` padrao."""
    states = [simulate_one_with_interaction(seed_base + i, turns=turns,
                                             with_greater_auramancy=with_greater_auramancy) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"=== Prismatic Bridge Goldfish v1 - MODO DE RESILIENCIA - n={n}, turns={turns}, Greater Auramancy={with_greater_auramancy} ===")
    print(f"Avg remocoes inteligentes sofridas: {avg([s.smart_removals_total for s in states]):.2f}")
    print(f"Avg ataques de oponente sofridos: {avg([s.smart_attacks_taken_total for s in states]):.2f}")
    print(f"Avg descartes forcados sofridos: {avg([s.smart_discards_total for s in states]):.2f}")
    print(f"Avg board wipes sofridos: {avg([s.smart_wipes_total for s in states]):.2f}")
    print(f"Avg artifact wipes sofridos: {avg([s.smart_artifact_wipes_total for s in states]):.2f}")
    print(f"Avg enchantment wipes sofridos: {avg([s.smart_enchantment_wipes_total for s in states]):.2f}")
    print(f"Board wipe sofrido em {100*sum(1 for s in states if s.smart_wipes_total > 0)/n:.1f}% das partidas")
    print(f"Avg graveyard wipes (mass exile) sofridos: {avg([s.smart_graveyard_wipes_total for s in states]):.2f}")
    print(f"Avg graveyard snipes (exilio unico) sofridos: {avg([s.smart_graveyard_snipes_total for s in states]):.2f}")
    print(f"Avg counterspells sofridos (cast da Bridge): {avg([s.smart_counters_total for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life for s in states]):.2f}")
    never_cast = sum(1 for s in states if s.bridge_cast_count == 0)
    print(f"Bridge nunca conjurada em {turns} turnos: {100*never_cast/n:.1f}%")
    recast = sum(1 for s in states if s.bridge_cast_count >= 2)
    print(f"Bridge recastada ao menos 1x (removida e voltou): {100*recast/n:.1f}%")
    return states


if __name__ == "__main__":
    run_batch(n=2000, turns=10, with_greater_auramancy=False, label="SEM Greater Auramancy (lista atual)")
    run_batch(n=2000, turns=10, with_greater_auramancy=True, label="COM Greater Auramancy (troca The Peregrine Dynamo)")

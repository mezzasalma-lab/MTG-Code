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
  tambem. Ver goldfish-log.md pra detalhe completo e o que ficou
  deliberadamente deferido (estatico da Nicol Bolas, nivel 3 do
  Innkeeper's Talent, proliferate de outras 6 fontes que precisam de hooks
  de cast/end-step que este arquivo ainda nao tem).
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
add("Oath of Teferi", 5, "Enchantment", colors={"U", "W"}, produces=set(), tags=set())
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
add("The Chain Veil", 4, "Artifact", colors=set(), produces=set(), tags=set())
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
add("Urza Assembles the Titans", 5, "Enchantment", colors={"W"}, produces=set(), tags=set())
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
    # Innkeeper's Talent so' dobra a partir do nivel 3 ({3}{G} pra subir) -
    # esse simulador nao tem engine de leveling pra Class (mesma
    # simplificacao ja usada no Caretaker's Talent do Hei Bai, so' a
    # habilidade base), entao o dobro dela fica de fora aqui, documentado.
    n = sum(1 for c in ("Doubling Season", "Vorinclex, Monstrous Raider") if state.has(c))
    return 2 ** n

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
        if pw in state.battlefield:
            state.battlefield.remove(pw)
        state.graveyard.append(pw)
        del state.loyalty[pw]
        state.pw_deaths_total += 1
        log.append({"trigger": "planeswalker_death", "pw": pw, "turn": state.turn})

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
    state.battlefield.append(COMMANDER)
    state.bridge_in_play = True
    state.bridge_cast_turn = state.turn
    if state.bridge_first_cast_turn is None:
        state.bridge_first_cast_turn = state.turn
    state.bridge_cast_count += 1
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

def activate_planeswalkers(state: GameState, log: List[Dict]):
    for pw in list(state.loyalty.keys()):
        if pw not in state.battlefield:
            continue  # morreu por outro efeito nesse meio tempo (Deepglow Skate etc. nao removem, so seguranca)
        resolve_planeswalker(state, pw, log)

# =========================================================
# TURNO
# =========================================================

def main_phase(state: GameState, log: List[Dict]):
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
        if C(choice).type in ("Instant", "Sorcery"):
            state.graveyard.append(choice)
        else:
            state.battlefield.append(choice)
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
        if choice in LAND_FETCH_SPELLS:
            do_land_fetch_spell(state, choice, log)
        log.append({"action": "cast", "card": choice, "turn": state.turn})

def play_turn(state: GameState, turn: int, game_log: List[List[Dict]]):
    state.turn = turn
    state.land_played = False
    state.mana_spent_this_turn = 0
    state.tapped_lands_this_turn = set()
    log = []

    # Linha de flash no end step do oponente anterior (ver docstring: modelado
    # como acontecendo ANTES da rodada de remocao deste turno, entao a Bridge
    # flashada escapa da rodada de remocao que precede seu primeiro gatilho)
    if can_flash_bridge(state):
        cast_bridge(state, log, via_flash=True)

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
    if mulligans:
        bottoms = choose_bottom(state.hand, mulligans)
        for c in bottoms:
            state.hand.remove(c)
            state.library.append(c)
        rng.shuffle(state.library)

    game_log = []
    for t in range(1, turns + 1):
        play_turn(state, t, game_log)

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
    print(f"Deferido nesta rodada (nao implementado, documentado): estatico da Nicol Bolas ('has all loyalty "
          f"abilities of all other planeswalkers'); Innkeeper's Talent nivel 3 (dobro de counters, precisa de "
          f"engine de leveling); Flux Channeler/Ichormoon Gauntlet/Inexorable Tide/Mutational "
          f"Advantage/Ripples of Potential/Atraxa (proliferate de outras fontes alem do Evolution Sage/Vraska - "
          f"precisam de hooks de cast-trigger/end-step que este arquivo ainda nao tem).")
    print()
    return results

if __name__ == "__main__":
    run_batch(n=2000, turns=10, with_greater_auramancy=False, label="SEM Greater Auramancy (lista atual)")
    run_batch(n=2000, turns=10, with_greater_auramancy=True, label="COM Greater Auramancy (troca The Peregrine Dynamo)")

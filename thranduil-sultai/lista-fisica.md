# Thranduil, the Elvenking — lista FÍSICA (o que está de verdade na coleção)

## Atualização 2026-10-23: faltam 6 cartas (94/100 em mãos)

O usuário informou (2026-10-23): *"O deck do Thranduil faltam as seguintes cartas:"* e, uma por linha, **Beast Whisperer; Devoted Druid; Maralen, Fae Ascendant; Buried Alive; Deadly Rollick; Awaken the Honored Dead**
(são **6 cartas**: "Maralen, Fae Ascendant" é um nome só, com vírgula). Os 6 nomes estão em `lista.md` e foram conferidos ao vivo no Scryfall (nomes exatos, sem `flavor_name`, Regra #2; legais em Commander).
**Tudo o mais de `lista.md` está em mãos, segundo o usuário:** 94 das 100 cartas (comandante incluso). Nenhuma carta foi cortada ou trocada da lista; só mudou o que é físico.
Os 6 nomes aparecem no `thranduil_goldfish_v1.py` (3 a 10 vezes cada, conferido por `grep`); **não reauditei as cláusulas deles contra o oráculo nesta atualização** (só registrei o que é físico), e ela não mexe no simulador.

### O que falta (proxar ou comprar)
| carta | custo | tipo | USD (Scryfall, 2026-10-23) | EUR | o que faz (oráculo) |
|---|---|---|---|---|---|
| **Beast Whisperer** | {2}{G}{G} | Creature — Elf Druid | 9.41 | 6.90 | Whenever you cast a creature spell, draw a card. |
| **Devoted Druid** | {1}{G} | Creature — Elf Druid | 1.47 | 1.07 | {T}: Add {G}. / Put a -1/-1 counter on this creature: Untap this creature. |
| **Maralen, Fae Ascendant** | {2}{B}{G}{U} | Legendary Creature — Elf Faerie Noble | 0.30 | 0.34 | Flying / Whenever Maralen or another Elf or Faerie you control enters, exile the top two cards of target opponent's library. / Once each turn, you may cast a spell with mana value less than or equal to the number of Elves and Faer |
| **Buried Alive** | {2}{B} | Sorcery | 2.69 | 1.35 | Search your library for up to three creature cards, put them into your graveyard, then shuffle. |
| **Deadly Rollick** | {3}{B} | Instant | 27.91 | 24.38 | If you control a commander, you may cast this spell without paying its mana cost. / Exile target creature. |
| **Awaken the Honored Dead** | {B}{G}{U} | Enchantment — Saga | 0.44 | 0.38 | (As this Saga enters and after your draw step, add a lore counter. Sacrifice after III.) / I — Destroy target nonland permanent. / II — Mill three cards. / III — You may discard a card. When you do, return target creature or land  |

Soma dos 6 em USD: **42.22** (preços `usd` do Scryfall em 2026-10-23, que são uma referência e não uma cotação de loja; o Deadly Rollick sozinho é 66% do total).
Respostas cruas do Scryfall: `resultados-ab/2026-10-23-lista-fisica/scryfall_faltantes.json`.

### Lista física atual (94 cartas = `lista.md` sem os 6 acima)
```
1 Thranduil, the Elvenking
1 Agatha's Soul Cauldron
1 Allosaurus Shepherd
1 Arbor Elf
1 Arcane Signet
1 Arwen, Weaver of Hope
1 Assassin's Trophy
1 Bloodline Bidding
1 Bloom Tender
1 Breeding Pool
1 Cavern of Souls
1 Champions of the Perfect
1 Command Tower
1 Deathbloom Ritualist
1 Botanical Sanctum
1 Dionus, Elvish Archdruid
1 Eclipsed Realms
1 Edric, Spymaster of Trest
1 Eladamri, Korvecdal
1 Elrond, Moon-Reader
1 Elvenking's Halls
1 Elves of Deep Shadow
1 Elvish Archdruid
1 Elvish Mystic
1 Elvish Warmaster
1 Ezuri, Renegade Leader
1 Fauna Shaman
1 Finale of Devastation
7 Forest
1 Gilt-Leaf Palace
1 Glissa Sunslayer
1 Gwenna, Eyes of Gaea
1 Heroic Intervention
1 High Perfect Morcant
1 Immaculate Magistrate
1 Imperious Perfect
1 Incubation Druid
1 Iron-Shield Elf
1 Island
1 Jarad, Golgari Lich Lord
1 Kindred Dominance
1 Kindred Summons
1 Lathril, Blade of the Elves
1 Lightning Greaves
1 Llanowar Elves
1 Lluwen, Imperfect Naturalist
1 Malakir Rebirth // Malakir Mire
1 Marwyn, the Nurturer
1 Nurturing Peatland
1 Overgrown Tomb
1 Oversold Cemetery
1 Priest of Titania
1 Prime Speaker Vannifar
1 Raise the Palisade
1 Reflecting Pool
1 Rejuvenating Springs
1 Revitalizing Repast // Old-Growth Grove
1 Rhystic Study
1 Roaming Throne
1 Ruthless Winnower
1 Selfless Safewright
1 Selvala, Heart of the Wilds
1 Sol Ring
4 Swamp
1 Takenuma, Abandoned Mire
1 Thranduil's Company
1 Thranduil, Sindarin Liege // Silvan Rally
1 Three Tree City
1 Trystan's Command
1 Trystan, Callous Cultivator // Trystan, Penitent Culler
1 Tyvar the Bellicose
1 Tyvar, Jubilant Brawler
1 Tyvar, the Pummeler
1 Underground River
1 Hinterland Harbor
1 Underrealm Lich
1 Wastewood Verge
1 Waterlogged Grove
1 Watery Grave
1 Willowrush Verge
1 Wirewood Channeler
1 Wirewood Lodge
1 Yavimaya Coast
1 Yavimaya, Cradle of Growth
1 Zagoth Triome
```

---

## Registro anterior (2026-09-22): 42 de 100 cartas confirmadas

Mantido como histórico (não apagado). O texto abaixo é o de 2026-09-22; a seção "Deck" dele é a lista que estava em mãos naquela data.

Lista digitada de cabeça pelo usuário (nomes em português e alguns nomes
alternativos resolvidos ao vivo no Scryfall — Regra #2: nenhum foi marcado
como "fora do deck" sem checar tradução/impressão real primeiro). Do total
de 100 cartas do `lista.md`, 42 estão confirmadas como posse física; as
outras 58 ainda precisam ser proxadas/compradas.

**Nomes traduzidos/alternativos resolvidos:**
- "Charco da Procriação" → **Breeding Pool**
- "Druida do Círculo dos sonhos" → **Circle of Dreams Druid**
- "Mestre de Guerra elfo" → **Elvish Warmaster**
- "Marwyn, a Nutriz" → **Marwyn, the Nurturer**
- "Peneirador impiedoso" → **Ruthless Winnower**

**5 cartas reais que o usuário tem mas que NÃO estão no decklist discutido**
(nenhuma foi cortada — nunca estiveram na lista; todas são sinergia real de
Elfo, então ficam registradas aqui para referência futura, não descartadas):
- Circle of Dreams Druid — `{1}{G}`, "{T}: Add one mana of any color. If
  you control eight or more lands, add two mana of any one color instead."
- Eclipsed Elf — `{B/G}{B/G}{B/G}`, ETB olha as 4 do topo, pega Elfo/Swamp/
  Forest pra mão.
- Harmonized Crescendo — `{4}{U}{U}` instant, Convoke, "Choose a creature
  type. Draw a card for each permanent you control of that type."
- Lys Alana Huntmaster — `{2}{G}{G}`, "Whenever you cast an Elf spell, you
  may create a 1/1 green Elf Warrior."
- Urza's Incubator — `{3}` artifact, criaturas do tipo escolhido custam
  {2} a menos.

## Comandante

1 Thranduil, the Elvenking

## Deck

1 Arbor Elf
1 Assassin's Trophy
1 Breeding Pool
1 Cavern of Souls
1 Champions of the Perfect
1 Command Tower
1 Dionus, Elvish Archdruid
1 Eladamri, Korvecdal
1 Elrond, Moon-Reader
1 Elvenking's Halls
1 Elvish Archdruid
1 Elvish Mystic
1 Elvish Warmaster
1 Glissa Sunslayer
1 Gwenna, Eyes of Gaea
1 High Perfect Morcant
1 Immaculate Magistrate
1 Incubation Druid
1 Jarad, Golgari Lich Lord
1 Iron-Shield Elf
1 Lathril, Blade of the Elves
1 Lightning Greaves
1 Llanowar Elves
1 Lluwen, Imperfect Naturalist
1 Marwyn, the Nurturer
1 Reflecting Pool
1 Rhystic Study
1 Ruthless Winnower
1 Selfless Safewright
1 Sol Ring
4 Swamp
1 Thranduil's Company
1 Thranduil, Sindarin Liege // Silvan Rally
1 Trystan's Command
1 Trystan, Callous Cultivator // Trystan, Penitent Culler
1 Tyvar, the Pummeler
1 Watery Grave
1 Wirewood Channeler

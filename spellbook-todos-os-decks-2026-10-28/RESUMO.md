# Commander Spellbook em TODOS os decks do repositório — 2026-10-28

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Esta pasta guarda o resumo; os dados de cada deck ficam em `<deck>/resultados-ab/2026-10-28-spellbook/` (resposta CRUA da API em `.json.xz`, JSON derivado, `LEIAME.md`, `SHA256SUMS`).

## O que foi feito (e com que método)

- **46 decks** (todo `<deck>/lista.md` do repositório, exceto o `rat-king-verminister`, que tem a rodada própria de 2026-10-25 em `rat-king-verminister/resultados-ab/2026-10-25-rodada3-spellbook-rulings-e-correcoes/`).
- **Nomes resolvidos ANTES** (a API ignora, sem erro, nome que não reconhece; achado de 2026-10-05): 2510 nomes únicos, via `GET /cards/?q=<nome>` (face da frente conta para cartas de 2 faces); **0 não reconhecidos**.
- Para cada deck: `POST /find-my-combos` (comandante + lista) e `POST /estimate-bracket`. **Precons de 2 ou mais comandantes** rodam uma opção por comandante, com os outros comandantes entrando na lista.
- **Controle positivo** (lista + Basalt Monolith + Rings of Brighthearth: o combo dos dois TEM de aparecer) e **controle de corte** (lista + Basalt Monolith + Mind Stone: o combo NÃO pode aparecer): passaram em **46 de 46** decks.
- Seções ignoradas na leitura da lista: as de notas, mudanças, sugestões, trocas, sideboard, fora do deck, cortadas/removidas e links; só se lê depois do primeiro `## Comandante`. Total de cartas lidas por deck na tabela (100, ou 99 no Captain Storm, cuja lista tem 99).

**Legenda da coluna "tag"** (`bracketTag` da API, rótulos do Spellbook): `R` Ruthless, `S` Spicy, `P` Powerful, `O` Oddball, `C` Core, `E` Exhibition, `B` Banned. **Não são os Brackets oficiais 1–4**: não verifiquei a correspondência com o texto oficial.

## Tabela por deck

| deck | comandante(s) | cartas | combos | de 2 cartas | "quase" | tag Spellbook | Game Changers | "Bracket N" citado em `lista.md`/`auditoria.md` (grep) |
|---|---|---|---|---|---|---|---|---|
| `azula-grixis` | Fire Lord Azula | 100 | 4 | 1 | 73 | R | 0 | 2, 3 |
| `beorn-fierce` | Beorn the Fierce | 100 | 0 | 0 | 21 | P | 1 | 3, 4 |
| `captain-storm-izzet` | Captain Storm, Cosmium Raider | 99 | 0 | 0 | 44 | E | 0 | 2 |
| `edgar-markov-mardu` | Edgar Markov | 100 | 4 | 4 | 183 | S | 3 | 1, 3, 4 |
| `edge-of-eternities-counter-intelligence` | Inspirit, Flagship Vessel | 100 | 0 | 0 | 43 | E | 0 | — |
| `edge-of-eternities-world-shaper` | Hearthhull, the Worldseed | 100 | 1 | 1 | 33 | S | 0 | — |
| `enduring-enchantments-abzan` | Anikthea, Hand of Erebos / Narci, Fable Singer | 100 | 0/0 | 0 | 20/20 | E/E | 0 | — |
| `final-fantasy-counter-blitz` | Tidus, Yuna's Guardian / Yuna, Grand Summoner | 100 | 1/1 | 0 | 65/65 | P/P | 1 | — |
| `final-fantasy-limit-break` | Cloud, Ex-SOLDIER / Tifa, Martial Artist | 100 | 0/0 | 0 | 6/6 | E/E | 0 | — |
| `final-fantasy-revival-trance` | Terra, Herald of Hope / Celes, Rune Knight | 100 | 0/0 | 0 | 3/3 | E/E | 0 | — |
| `final-fantasy-scions-spellcraft` | Y'shtola, Night's Blessed / G'raha Tia, Scion Reborn | 100 | 0/0 | 0 | 8/8 | E/E | 0 | — |
| `hei-bai-wurbg` | Hei Bai, Forest Guardian | 100 | 0 | 0 | 94 | P | 3 | 3, 4 |
| `kutzil-selesnya` | Kutzil, Malamet Exemplar | 100 | 0 | 0 | 45 | P | 2 | 3 |
| `lorwyn-eclipsed-blight-curse` | Auntie Ool, Cursewretch | 100 | 2 | 2 | 40 | E | 0 | — |
| `lorwyn-eclipsed-dance-of-elements` | Ashling, the Limitless | 100 | 0 | 0 | 87 | E | 0 | — |
| `lotr-elven-council` | Galadriel, Elven-Queen / Gandalf, Westward Voyager | 100 | 0/0 | 0 | 11/11 | C/C | 0 | — |
| `lotr-food-and-fellowship` | Frodo, Adventurous Hobbit / Sam, Loyal Attendant | 100 | 0/0 | 0 | 16/16 | E/E | 0 | — |
| `lotr-hosts-of-mordor` | Sauron, Lord of the Rings / Saruman, the White Hand | 100 | 0/0 | 0 | 19/19 | P/P | 1 | — |
| `lotr-riders-of-rohan` | Éowyn, Shieldmaiden / Aragorn, King of Gondor | 100 | 1/1 | 1 | 24/24 | S/S | 0 | — |
| `maralen-sultai` | Maralen, Fae Ascendant | 100 | 9 | 9 | 95 | S | 3 | 3, 4 |
| `marvel-avengers-assemble` | Captain America, Team Leader / Director Nick Fury | 100 | 0/0 | 0 | 7/7 | E/E | 0 | — |
| `marvel-doom-prevails` | Doctor Doom, King of Latveria / Loki, the Deceiver | 100 | 0/0 | 0 | 17/17 | E/E | 0 | — |
| `marvel-fantastic-four` | Invisible Woman / Mister Fantastic / Human Torch / The Thing | 100 | 0/0/0/0 | 0 | 16/16/16/16 | E/E/E/E | 0 | — |
| `marvel-wakanda-forever` | T'Challa, the Black Panther / Shuri, the Black Panther | 100 | 0/0 | 0 | 3/3 | E/E | 0 | — |
| `megatron-tyrant-mardu` | Megatron, Tyrant | 100 | 2 | 1 | 27 | R | 0 | — |
| `ms-bumbleflower-bant` | Ms. Bumbleflower | 100 | 2 | 2 | 67 | S | 3 | — |
| `nekusar-grixis` | Nekusar, the Mindrazer | 100 | 1 | 1 | 96 | R | 8 | 1, 2, 3, 4 |
| `prismatic-bridge-wurbg` | Esika, God of the Tree // The Prismatic Bridge | 100 | 12 | 5 | 92 | R | 3 | 3 |
| `secrets-strixhaven-lorehold` | Quintorius, History Chaser / Excava, the Risen Past | 100 | 0/0 | 0 | 0/0 | E/E | 0 | — |
| `secrets-strixhaven-prismari` | Rootha, Mastering the Moment / Muddle, the Ever-Changing | 100 | 0/0 | 0 | 75/75 | E/E | 0 | — |
| `secrets-strixhaven-quandrix` | Zimone, Infinite Analyst / Primo, the Unbounded | 100 | 0/0 | 0 | 16/16 | E/E | 0 | — |
| `secrets-strixhaven-silverquill` | Killian, Decisive Mentor / Scriv, the Obligator | 100 | 0/0 | 0 | 9/9 | E/E | 0 | — |
| `secrets-strixhaven-witherbloom` | Dina, Essence Brewer / Gorma, the Gullet | 100 | 0/0 | 0 | 33/33 | E/E | 0 | — |
| `tam-the-possibility-wubrg` | Tam, the Possibility | 100 | 2 | 1 | 92 | S | 0 | 3 |
| `tarkir-dragonstorm-sultai-arisen` | Teval, the Balanced Scale / Kotis, Sibsig Champion | 100 | 0/0 | 0 | 49/49 | E/E | 0 | — |
| `thranduil-sultai` | Thranduil, the Elvenking | 100 | 4 | 1 | 98 | R | 1 | 3, 4 |
| `tom-bombadil-wubrg` | Tom Bombadil | 100 | 1 | 1 | 83 | P | 3 | 3 |
| `toph-naya` | Toph, the First Metalbender | 100 | 29 | 4 | 377 | R | 3 | 3 |
| `ulalek-wurbg` | Ulalek, Fused Atrocity | 100 | 5 | 0 | 58 | R | 3 | 3 |
| `ur-dragon-wurbg` | The Ur-Dragon | 100 | 3 | 2 | 148 | S | 3 | 2, 3, 4 |
| `vihaan-goldwaker-mardu` | Vihaan, Goldwaker | 100 | 4 | 0 | 98 | P | 2 | 3, 4 |
| `wh40k-forces-of-imperium` | Inquisitor Greyfax / Marneus Calgar | 100 | 0/0 | 0 | 6/6 | E/E | 0 | — |
| `wh40k-necron-dynasties` | Szarekh, the Silent King / Imotekh the Stormlord | 100 | 0/0 | 0 | 26/26 | E/E | 0 | — |
| `wh40k-ruinous-powers` | Abaddon the Despoiler / Be'lakor, the Dark Master | 100 | 0/0 | 0 | 47/47 | E/E | 0 | — |
| `wh40k-tyranid-swarm` | The Swarmlord / Magus Lucea Kane | 100 | 0/0 | 0 | 5/5 | E/E | 0 | — |
| `wise-mothman-sultai` | The Wise Mothman | 100 | 2 | 2 | 138 | S | 1 | 3 |

A coluna "Bracket N citado" é um `grep` cru de "Bracket <dígito>" nos dois arquivos: pode listar vários números (o deck discute 3 e 4, por exemplo) e **não é uma decisão registrada**. "Quase" = combos a uma carta de distância (informativo; não são sugestões de troca).

## Combos achados, por deck (só decks com pelo menos um)

### `azula-grixis` — 4 combo(s), tag R
  - `11-3368` (2 cartas, tag E Exhibition): Narset's Reversal + Reiterate → Infinite magecraft triggers
  - `11-2196-7089` (3 cartas, tag S Spicy): Fire Lord Azula + Frantic Search + Narset's Reversal → Infinite self-discard triggers; Infinite draw triggers; Infinite looting; Near-infinite storm count
  - `11-5195-7089` (3 cartas, tag S Spicy): Fire Lord Azula + Narset's Reversal + Storm-Kiln Artist → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite artifact tokens
  - `3368-4036-5195` (3 cartas, tag E Exhibition): Reiterate + Seething Song + Storm-Kiln Artist → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite artifact tokens

### `edgar-markov-mardu` — 4 combo(s), tag S; Game Changers: Smothering Tithe, Teferi's Protection, Vampiric Tutor
  - `5755-6191` (2 cartas, tag S Spicy): Bloodthirsty Conqueror + Enduring Tenacity → Infinite lifegain triggers; Infinite lifeloss; Infinite lifegain
  - `314-6191` (2 cartas, tag S Spicy): Bloodthirsty Conqueror + Vito, Thorn of the Dusk Rose → Infinite lifegain triggers; Infinite lifeloss; Infinite lifegain
  - `3966-5755` (2 cartas, tag S Spicy): Enduring Tenacity + Exquisite Blood → Infinite lifegain triggers; Infinite lifeloss; Infinite lifegain
  - `314-3966` (2 cartas, tag S Spicy): Exquisite Blood + Vito, Thorn of the Dusk Rose → Infinite lifegain triggers; Infinite lifeloss; Infinite lifegain

### `edge-of-eternities-world-shaper` — 1 combo(s), tag S
  - `250-779` (2 cartas, tag S Spicy): Dakmor Salvage + The Gitrog Monster → Infinite self-mill; Near-infinite self-discard triggers

### `final-fantasy-counter-blitz` — 1 combo(s), tag P/P; Game Changers: Farewell
- opção Tidus, Yuna's Guardian:
  - `2265-3693-6593` (3 cartas, tag S Spicy): Gatta and Luzzu + Hardened Scales + Walking Ballista → Infinite damage; Infinite +1/+1 counters on a creature
- opção Yuna, Grand Summoner:
  - `2265-3693-6593` (3 cartas, tag S Spicy): Gatta and Luzzu + Hardened Scales + Walking Ballista → Infinite damage; Infinite +1/+1 counters on a creature

### `lorwyn-eclipsed-blight-curse` — 2 combo(s), tag E
  - `1084-4994` (2 cartas, tag E Exhibition): Blowfly Infestation + Flourishing Defenses → Infinite creature ETB; Infinite creature LTB; Infinite death triggers
  - `2228-4994` (2 cartas, tag E Exhibition): Blowfly Infestation + Hapatra, Vizier of Poisons → Infinite death triggers; Infinite creature ETB; Infinite creature LTB

### `lotr-riders-of-rohan` — 1 combo(s), tag S/S
- opção Éowyn, Shieldmaiden:
  - `847-2059` (2 cartas, tag S Spicy): Gilraen, Dúnedain Protector + Village Bell-Ringer → Infinite creature ETB; Infinite creature LTB; Infinite mana creatures you control can produce; Infinite untap of creatures you control
- opção Aragorn, King of Gondor:
  - `847-2059` (2 cartas, tag S Spicy): Gilraen, Dúnedain Protector + Village Bell-Ringer → Infinite creature ETB; Infinite creature LTB; Infinite mana creatures you control can produce; Infinite untap of creatures you control

### `maralen-sultai` — 9 combo(s), tag S; Game Changers: Cyclonic Rift, Rhystic Study, Seedborn Muse
  - `2645-5168` (2 cartas, tag S Spicy): Bloom Tender + Staff of Domination → Infinite lifegain triggers; Infinite lifegain; Infinite card draw; Infinite untap of creatures you control
  - `1526-2645` (2 cartas, tag S Spicy): Circle of Dreams Druid + Staff of Domination → Infinite card draw; Infinite draw triggers; Infinite lifegain; Infinite lifegain triggers
  - `1526-2816` (2 cartas, tag S Spicy): Circle of Dreams Druid + Umbral Mantle → Infinite green mana; Infinitely large creature until end of turn; Infinite untap of creatures you control; Infinite mana creatures you control can produce
  - `2645-3151` (2 cartas, tag S Spicy): Elvish Archdruid + Staff of Domination → Infinite card draw; Infinite draw triggers; Infinite lifegain; Infinite lifegain triggers
  - `2816-3151` (2 cartas, tag S Spicy): Elvish Archdruid + Umbral Mantle → Infinite green mana; Infinitely large creature until end of turn; Infinite untap of creatures you control; Infinite mana creatures you control can produce
  - `2436-2645` (2 cartas, tag S Spicy): Marwyn, the Nurturer + Staff of Domination → Infinite card draw; Infinite draw triggers; Infinite lifegain; Infinite lifegain triggers
  - `2436-2816` (2 cartas, tag S Spicy): Marwyn, the Nurturer + Umbral Mantle → Infinite green mana; Infinitely large creature until end of turn; Infinite untap of creatures you control; Infinite mana creatures you control can produce
  - `1376-2645` (2 cartas, tag S Spicy): Priest of Titania + Staff of Domination → Infinite card draw; Infinite draw triggers; Infinite lifegain; Infinite lifegain triggers
  - `1376-2816` (2 cartas, tag S Spicy): Priest of Titania + Umbral Mantle → Infinite green mana; Infinitely large creature until end of turn; Infinite untap of creatures you control; Infinite mana creatures you control can produce

### `megatron-tyrant-mardu` — 2 combo(s), tag R
  - `1571-2560` (2 cartas, tag R Ruthless): Blightsteel Colossus + Chandra's Ignition → Each opponent loses the game
  - `3169-5291-6250` (3 cartas, tag E Exhibition): Cursed Mirror + Daretti, Rocketeer Engineer + Genesis Chamber → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite creature LTB

### `ms-bumbleflower-bant` — 2 combo(s), tag S; Game Changers: Cyclonic Rift, Rhystic Study, Smothering Tithe
  - `3807-4762` (2 cartas, tag S Spicy): Devoted Druid + Swift Reconfiguration → Infinite green mana
  - `1274-3693` (2 cartas, tag S Spicy): Heliod, Sun-Crowned + Walking Ballista → Infinite damage; Infinite lifegain; Infinite lifegain triggers

### `nekusar-grixis` — 1 combo(s), tag R; Game Changers: Cyclonic Rift, Demonic Tutor, Force of Will, Imperial Seal, Orcish Bowmasters, The One Ring, Underworld Breach, Vampiric Tutor
  - `936-1290` (2 cartas, tag S Spicy): Bloodchief Ascension + Mindcrank → Infinite mill; Near-infinite lifegain; Near-infinite lifegain triggers; Near-infinite lifeloss

### `prismatic-bridge-wurbg` — 12 combo(s), tag R; Game Changers: Farewell, Narset, Parter of Veils, Rhystic Study
  - `1529-5902` (2 cartas, tag S Spicy): Innkeeper's Talent + Vraska, Betrayal's Sting → Target opponent loses the game
  - `787-1124` (2 cartas, tag S Spicy): Teferi, Temporal Archmage + The Chain Veil → Infinite card draw; Infinite colored mana; Infinite colorless mana; Infinite planeswalker activations
  - `1124-2696` (2 cartas, tag S Spicy): Teferi, Who Slows the Sunset + The Chain Veil → Infinite activations of most planeswalkers; Infinite lifegain; Infinite lifegain triggers; Infinite mana permanents you control can produce
  - `2341-2696` (2 cartas, tag S Spicy): Teferi, Who Slows the Sunset + The Peregrine Dynamo → Infinite untap of permanents you control; Infinite lifegain; Infinite lifegain triggers; Infinite mana permanents you control can produce
  - `1529-1887` (2 cartas, tag S Spicy): Vorinclex, Monstrous Raider + Vraska, Betrayal's Sting → Target opponent loses the game
  - `193-1180-2369` (3 cartas, tag R Ruthless): Aminatou, the Fateshifter + Nicol Bolas, Dragon-God + Oath of Teferi → Exile all of your opponents' permanents and hands; Infinite card draw; Infinite creature ETB; Infinite creature LTB
  - `193-1124-1180` (3 cartas, tag R Ruthless): Aminatou, the Fateshifter + Nicol Bolas, Dragon-God + The Chain Veil → Exile all permanents opponents control; Infinite planeswalker activations; Infinite card draw; Infinite draw triggers
  - `787-1124-4450` (3 cartas, tag E Exhibition): Carth the Lion + Teferi, Temporal Archmage + The Chain Veil → Infinite card draw; Infinite colored mana; Infinite colorless mana; Infinite mana permanents you control can produce
  - `193-1543-1940-4772` (4 cartas, tag R Ruthless): Aminatou, the Fateshifter + Doubling Season + Ichormoon Gauntlet + Liliana, Dreadhorde General → Infinite turns; Lock
  - `193-1543-2984-4772` (4 cartas, tag R Ruthless): Aminatou, the Fateshifter + Doubling Season + Ichormoon Gauntlet + Ugin, the Spirit Dragon → Infinite turns; Lock
  - `193-1543-1887-1940` (4 cartas, tag R Ruthless): Aminatou, the Fateshifter + Ichormoon Gauntlet + Liliana, Dreadhorde General + Vorinclex, Monstrous Raider → Infinite turns; Lock
  - `193-1543-1887-2984` (4 cartas, tag R Ruthless): Aminatou, the Fateshifter + Ichormoon Gauntlet + Ugin, the Spirit Dragon + Vorinclex, Monstrous Raider → Infinite turns; Lock

### `tam-the-possibility-wubrg` — 2 combo(s), tag S
  - `787-1124` (2 cartas, tag S Spicy): Teferi, Temporal Archmage + The Chain Veil → Infinite card draw; Infinite colored mana; Infinite colorless mana; Infinite planeswalker activations
  - `1124-1283-2495` (3 cartas, tag E Exhibition): Chromatic Orrery + Tezzeret the Seeker + The Chain Veil → Infinite card draw; Infinite colored mana; Infinite colorless mana; Infinite planeswalker activations

### `thranduil-sultai` — 4 combo(s), tag R; Game Changers: Rhystic Study
  - `4762-6189` (2 cartas, tag P Powerful): Devoted Druid + Tyvar, the Pummeler → Infinite green mana; Infinitely large creatures you control until end of turn
  - `2207-4613-4762` (3 cartas, tag E Exhibition): Agatha's Soul Cauldron + Devoted Druid + Immaculate Magistrate → Infinite green mana; Infinite mana creatures you control can produce; Infinite untap of creatures you control; Infinite +1/+1 counters on creatures you control
  - `3990-4613-4762` (3 cartas, tag E Exhibition): Agatha's Soul Cauldron + Devoted Druid + Incubation Druid → Infinite colored mana
  - `2207-4762-7821` (3 cartas, tag S Spicy): Devoted Druid + Immaculate Magistrate + Thranduil, the Elvenking → Infinite +1/+1 counters on creatures you control; Infinite green mana

### `tom-bombadil-wubrg` — 1 combo(s), tag P; Game Changers: Enlightened Tutor, Serra's Sanctum, Teferi's Protection
  - `112-974` (2 cartas, tag C Core): Clockspinning + There and Back Again → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite artifact tokens

### `toph-naya` — 29 combo(s), tag R; Game Changers: Enlightened Tutor, Field of the Dead, Teferi's Protection
  - `3470-5702--143` (2 cartas, tag E Exhibition): Lotus Cobra + Springheart Nantuko → Infinite landfall triggers; Infinite tapped land tokens
  - `2653-5702--143` (2 cartas, tag S Spicy): Nissa, Resurgent Animist + Springheart Nantuko → Infinite landfall triggers; Infinite tapped land tokens
  - `3875-5702--143` (2 cartas, tag E Exhibition): Springheart Nantuko + Tireless Provisioner → Infinite landfall triggers; Infinite tapped land tokens
  - `4155-6871` (2 cartas, tag S Spicy): The Stasis Coffin + Toph, the First Metalbender → Prevent all damage that would be dealt to you; You have protection from everything during your opponents' turns; Lock
  - `539-1315-7008` (3 cartas, tag S Spicy): Ashaya, Soul of the Wild + Badgermole Cub + Zuran Orb → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers
  - `539-1315-7034` (3 cartas, tag S Spicy): Ashaya, Soul of the Wild + Bumi, Eclectic Earthbender + Zuran Orb → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers
  - `539-1315-7085` (3 cartas, tag S Spicy): Ashaya, Soul of the Wild + Earth Kingdom General + Zuran Orb → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers
  - `539-1315-7035` (3 cartas, tag S Spicy): Ashaya, Soul of the Wild + Earthbending Student + Zuran Orb → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers
  - `573-1479-2692` (3 cartas, tag E Exhibition): Felidar Retreat + Gruul Turf + Kodama of the East Tree → Infinite creature tokens; Infinite creature ETB; Infinite landfall triggers
  - `907-1479-2692` (3 cartas, tag E Exhibition): Felidar Retreat + Kodama of the East Tree + Selesnya Sanctuary → Infinite creature tokens; Infinite creature ETB; Infinite landfall triggers
  - `573-1479-3534` (3 cartas, tag P Powerful): Field of the Dead + Gruul Turf + Kodama of the East Tree → Infinite creature ETB; Infinite creature tokens; Infinite landfall triggers
  - `907-1479-3534` (3 cartas, tag P Powerful): Field of the Dead + Kodama of the East Tree + Selesnya Sanctuary → Infinite creature ETB; Infinite creature tokens; Infinite landfall triggers
  - `573-1479-7201` (3 cartas, tag E Exhibition): Gruul Turf + Kodama of the East Tree + Sapling Nursery → Infinite creature ETB; Infinite creature tokens; Infinite landfall triggers
  - `573-1479-2907` (3 cartas, tag E Exhibition): Gruul Turf + Kodama of the East Tree + Scute Swarm → Infinite creature tokens; Infinite landfall triggers; Infinite creature ETB
  - `573-1479-5702` (3 cartas, tag E Exhibition): Gruul Turf + Kodama of the East Tree + Springheart Nantuko → Infinite creature ETB; Infinite creature tokens; Infinite landfall triggers
  - `573-1479-3875` (3 cartas, tag E Exhibition): Gruul Turf + Kodama of the East Tree + Tireless Provisioner → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite artifact tokens
  - `907-1479-7201` (3 cartas, tag E Exhibition): Kodama of the East Tree + Sapling Nursery + Selesnya Sanctuary → Infinite creature ETB; Infinite creature tokens; Infinite landfall triggers
  - `907-1479-2907` (3 cartas, tag E Exhibition): Kodama of the East Tree + Scute Swarm + Selesnya Sanctuary → Infinite creature tokens; Infinite landfall triggers; Infinite creature ETB
  - `907-1479-5702` (3 cartas, tag E Exhibition): Kodama of the East Tree + Selesnya Sanctuary + Springheart Nantuko → Infinite creature ETB; Infinite creature tokens; Infinite landfall triggers
  - `907-1479-3875` (3 cartas, tag E Exhibition): Kodama of the East Tree + Selesnya Sanctuary + Tireless Provisioner → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite artifact tokens
  - `3263-4659-6871--211` (3 cartas, tag E Exhibition): Krark-Clan Ironworks + Mycosynth Lattice + Toph, the First Metalbender → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite colored mana
  - `3470-5702-6871` (3 cartas, tag S Spicy): Lotus Cobra + Springheart Nantuko + Toph, the First Metalbender → Infinite landfall triggers; Infinite tapped land tokens
  - `1315-3263-6871--183` (3 cartas, tag E Exhibition): Mycosynth Lattice + Toph, the First Metalbender + Zuran Orb → Infinite creature ETB; Infinite creature LTB; Infinite death triggers; Infinite landfall triggers
  - `2653-5702-6871` (3 cartas, tag S Spicy): Nissa, Resurgent Animist + Springheart Nantuko + Toph, the First Metalbender → Infinite landfall triggers; Infinite tapped land tokens
  - `3875-5702-6871` (3 cartas, tag S Spicy): Springheart Nantuko + Tireless Provisioner + Toph, the First Metalbender → Infinite landfall triggers; Infinite tapped land tokens
  - `573-4572-5702-6763` (4 cartas, tag E Exhibition): Dryad of the Ilysian Grove + Gruul Turf + Horizon Explorer + Springheart Nantuko → Infinite creature tokens; Infinite landfall triggers; Infinite creature ETB
  - `573-4572-5478-5702` (4 cartas, tag E Exhibition): Dryad of the Ilysian Grove + Gruul Turf + Spelunking + Springheart Nantuko → Infinite creature tokens; Infinite landfall triggers; Infinite creature ETB; Infinite green mana
  - `907-4572-5702-6763` (4 cartas, tag E Exhibition): Dryad of the Ilysian Grove + Horizon Explorer + Selesnya Sanctuary + Springheart Nantuko → Infinite creature tokens; Infinite landfall triggers; Infinite creature ETB
  - `907-4572-5478-5702` (4 cartas, tag E Exhibition): Dryad of the Ilysian Grove + Selesnya Sanctuary + Spelunking + Springheart Nantuko → Infinite creature tokens; Infinite landfall triggers; Infinite creature ETB; Infinite green mana

### `ulalek-wurbg` — 5 combo(s), tag R; Game Changers: Ancient Tomb, Rhystic Study, The One Ring
  - `5642-5657-5705` (3 cartas, tag E Exhibition): Echoes of Eternity + Glaring Fleshraker + Ulalek, Fused Atrocity → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers
  - `5637-5642-5657--34` (3 cartas, tag E Exhibition): Echoes of Eternity + Kozilek's Unsealing + Ulalek, Fused Atrocity → Infinite colorless mana; Infinite copies of abilities you control on the stack; Infinite copies of a specific creature; Infinite creature tokens
  - `5642-5657-5664` (3 cartas, tag S Spicy): Echoes of Eternity + Ulalek, Fused Atrocity + Writhing Chrysalis → Infinite copies of abilities you control on the stack; Infinite creature tokens; Infinite death triggers; Infinite creature ETB
  - `5657-5664-7116` (3 cartas, tag O Oddball): Eldritch Immunity + Ulalek, Fused Atrocity + Writhing Chrysalis → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers
  - `5334-5657-5705` (3 cartas, tag E Exhibition): Glaring Fleshraker + Roaming Throne + Ulalek, Fused Atrocity → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers

### `ur-dragon-wurbg` — 3 combo(s), tag S; Game Changers: Ancient Tomb, Smothering Tithe, Teferi's Protection
  - `2855-5982` (2 cartas, tag S Spicy): Ancient Gold Dragon + Dragon Tempest → Near-infinite damage
  - `1800-3398` (2 cartas, tag O Oddball): Hellkite Charger + Old Gnawbone → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite artifact tokens
  - `380-1110-3362` (3 cartas, tag O Oddball): Bladewing the Risen + Miirym, Sentinel Wyrm + Terror of the Peaks → Infinite creature LTB; Infinite creature ETB; Infinite death triggers; Infinite damage

### `vihaan-goldwaker-mardu` — 4 combo(s), tag P; Game Changers: Smothering Tithe, Teferi's Protection
  - `1308-4682-7890` (3 cartas, tag P Powerful): Anointed Procession + Gleaming Splendor + Smothering Tithe → Infinite card draw for any number of players; Infinite draw triggers for any number of players; Near-infinite Treasure tokens; Near-infinite colored mana
  - `865-2034-2429` (3 cartas, tag E Exhibition): Ashnod's Altar + Mahadi, Emporium Master + Revel in Riches → Win the game at the beginning of your next upkeep
  - `3809-4682-7890` (3 cartas, tag P Powerful): Gleaming Splendor + Goldspan Dragon + Smothering Tithe → Infinite card draw for any number of players; Infinite draw triggers for any number of players; Near-infinite Treasure tokens; Near-infinite colored mana
  - `4682-5184-7890` (3 cartas, tag P Powerful): Gleaming Splendor + Smothering Tithe + Xorn → Infinite card draw for any number of players; Infinite draw triggers for any number of players; Near-infinite Treasure tokens; Near-infinite colored mana

### `wise-mothman-sultai` — 2 combo(s), tag S; Game Changers: Fierce Guardianship
  - `3139-5256--5` (2 cartas, tag E Exhibition): Altar of Dementia + The Great Henge → Infinite self-mill; Infinite creature ETB; Infinite creature LTB; Infinite death triggers
  - `936-1290` (2 cartas, tag S Spicy): Bloodchief Ascension + Mindcrank → Infinite mill; Near-infinite lifegain; Near-infinite lifegain triggers; Near-infinite lifeloss

Decks com **0 combos** achados (27): `beorn-fierce`, `captain-storm-izzet`, `edge-of-eternities-counter-intelligence`, `enduring-enchantments-abzan`, `final-fantasy-limit-break`, `final-fantasy-revival-trance`, `final-fantasy-scions-spellcraft`, `hei-bai-wurbg`, `kutzil-selesnya`, `lorwyn-eclipsed-dance-of-elements`, `lotr-elven-council`, `lotr-food-and-fellowship`, `lotr-hosts-of-mordor`, `marvel-avengers-assemble`, `marvel-doom-prevails`, `marvel-fantastic-four`, `marvel-wakanda-forever`, `secrets-strixhaven-lorehold`, `secrets-strixhaven-prismari`, `secrets-strixhaven-quandrix`, `secrets-strixhaven-silverquill`, `secrets-strixhaven-witherbloom`, `tarkir-dragonstorm-sultai-arisen`, `wh40k-forces-of-imperium`, `wh40k-necron-dynasties`, `wh40k-ruinous-powers`, `wh40k-tyranid-swarm`.

## O que NÃO foi feito (Regra #7)

- **Não conferi se o simulador de cada deck EXECUTA os combos achados** (Regra #4, adendo, item 3). O Rat King tinha 2 combos e um simulador que não executava nenhum (rodada de 2026-10-25); a mesma classe de erro pode estar nos decks com simulador e combos (Toph, Prismatic Bridge, Maralen, Ulalek, Thranduil, Azula, Edgar, Vihaan, Mothman, Tam, Ur-Dragon, Megatron, Bumbleflower, Nekusar, Tom). **Não varrido.**
- **Não calculei a probabilidade por turno** de cada combo (regra 7 de `references/user-standing-rules.md`).
- **Não comparei** com os registros antigos de Spellbook dos 8 decks que já tinham (Beorn, Megatron, Prismatic Bridge, Tam, Thranduil, Ur-Dragon, Vihaan, Mothman): esta rodada é independente, com a lista de hoje; as rodadas antigas não foram reauditadas e algumas passaram nomes sem a checagem de resolução.
- **Não verifiquei o texto oficial atual do critério de Brackets**; as tags acima são do Spellbook.
- Decks sem `goldfish-log.md` (27) não ganharam o link no topo do log; o link está só neste arquivo e no `LEIAME.md` da pasta de cada deck. `lista.md` não foi tocado.
- **Duas execuções da etapa por deck** (a 1ª sem gravar o bruto: `resumos/log_csb_todos_execucao1_sem_bruto.txt`; a 2ª, que grava o bruto e é a que vale: `resumos/log_csb_todos.txt`), minutos de diferença: 46 decks nas duas, **0 com linha diferente** (combos, tag, controles). A resolução de nomes teve uma tentativa anterior que caiu por erro de rede (o log dessa tentativa não foi guardado); as duas execuções por deck usaram o mesmo cache de nomes resolvidos (`dados/nomes_resolvidos_parcial.json`).

## Como refazer

```
python3 -I spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py <raiz do repositório> [deck ...]   # consulta a API (rede); REFAZER=1 refaz decks já gravados
python3 -I spellbook-todos-os-decks-2026-10-28/orquestracao/gera_resumo.py <raiz do repositório>                  # só dos arquivos salvos (sem rede): este RESUMO.md, os LEIAME e os SHA256SUMS
```

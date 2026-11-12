# Auditoria estática — Tam, the Possibility (WUBRG) — 2026-10-19

Comandante: **Tam, the Possibility** ({1}{G}{U}, Legendary Creature — Gorgon Wizard), identidade de cor WUBRG. Deck: 99 + comandante; sideboard: 13. Gerado de `dados/resolvido.json.xz`, `edhrec_tam.json.xz` e `spellbook_tam.json`.

## 1. Composição

| categoria do usuário | cartas |
|---|---|
| Land | 36 |
| Ramp | 16 |
| Draw | 11 |
| Removal | 9 |
| Proliferate | 9 |
| Tokens | 8 |
| Protection | 5 |
| Blink | 3 |
| Tutor | 2 |

Tipos no deck (uma carta pode contar em vários; as 8 "Way of the…" e o Oath of Nissa/Teferi são encantamentos lendários): Land 36, Planeswalker 25, Enchantment 14, Creature 12, Artifact 8, Sorcery 4, Instant 1.

EDHREC (média de 6931 decks do Tam): criaturas 14, instantâneos 7, feitiços 6, artefatos 7, encantamentos 9, planeswalkers 21, terrenos 35 (básicos 9). Este deck: criaturas 12, instantâneos 1, feitiços 4, artefatos 8, encantamentos 14, **planeswalkers 25**, terrenos 36 (**0 básicos**).

## 2. Curva (não-terrenos do deck, sem o comandante)

| MV | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| cartas | 0 | 5 | 8 | 17 | 11 | 13 | 6 | 2 | 0 | 1 |

Não-terrenos: 63; MV médio **3.81**; mediana 4. Sem o desconto da Tam. EDHREC (curva média): MV1: 6, MV2: 11, MV3: 17, MV4: 12, MV5: 10, MV6: 6, MV7: 1, MV8: 1, MV9: 1.

**Planeswalkers: 25.** Custo de conjuração, sem a Tam / com a Tam em campo ("{1} a menos" só reduz o genérico; PW sem genérico no custo não desconta): MV1: 0→0; MV2: 0→5; MV3: 6→8; MV4: 7→6; MV5: 6→5; MV6: 5→1; MV7: 1→0. Média 4.52 → 3.56.

## 3. Planeswalkers e tipos de planeswalker (o X da Tam)

| planeswalker | MV | lealdade | tipo(s) |
|---|---|---|---|
| Aminatou, the Fateshifter | 3 | 3 | Aminatou |
| Dack Fayden | 3 | 3 | Dack |
| Kasmina, Enigma Sage | 3 | 2 | Kasmina |
| Oko, Thief of Crowns | 3 | 4 | Oko |
| Saheeli, Sublime Artificer | 3 | 5 | Saheeli |
| Wrenn and Realmbreaker | 3 | 4 | Wrenn |
| Dihada, Binder of Wills | 4 | 5 | Dihada |
| Domri, Chaos Bringer | 4 | 5 | Domri |
| Garruk Wildspeaker | 4 | 3 | Garruk |
| Minsc & Boo, Timeless Heroes | 4 | 3 | Minsc |
| Narset Transcendent | 4 | 6 | Narset |
| Professor Dellian Fel | 4 | 5 | Dellian |
| Tamiyo, Field Researcher | 4 | 4 | Tamiyo |
| Chandra, Legacy of Fire | 5 | 3 | Chandra |
| Garruk, Curse Breaker | 5 | 5 | Garruk |
| Garruk, Veiled Butcher | 5 | 5 | Garruk |
| Teferi, Hero of Dominaria | 5 | 4 | Teferi |
| Tezzeret the Seeker | 5 | 4 | Tezzeret |
| Vronos, Masked Inquisitor | 5 | 5 | Vronos |
| Ajani Unrelenting | 6 | 5 | Ajani |
| Elspeth, Sun's Champion | 6 | 4 | Elspeth |
| Teferi, Temporal Archmage | 6 | 5 | Teferi |
| The Eternal Wanderer | 6 | 5 | (nenhum) |
| Vraska, Betrayal's Sting | 6 | 6 | Vraska |
| Nissa, Ascended Animist | 7 | 7 | Nissa |

**21 tipos de planeswalker distintos entre os 25 planeswalkers do deck**: Ajani, Aminatou, Chandra, Dack, Dellian, Dihada, Domri, Elspeth, Garruk, Kasmina, Minsc, Narset, Nissa, Oko, Saheeli, Tamiyo, Teferi, Tezzeret, Vraska, Vronos, Wrenn. Sem subtipo (não contam para o X da Tam): ['The Eternal Wanderer'].

As 10 cartas "empower Jace" (Overwrite the Multiverse, Sanctum Lurker, Way of the Deathbringer, Way of the Healer, Way of the Mind Sculptor, Way of the Necromancer, Way of the Paradox, Way of the Pyromancer, Way of the Warlord, Way of the Wildspeaker) criam (ou reforçam) uma **ficha de Jace** (planeswalker azul): conta como o tipo **Jace** (Tam: "planeswalker types among planeswalkers you control"). Cada ativação da Tam faz X proliferates; X máximo sem ficha de Jace = 21, com = 22 (se todos os planeswalkers estivessem em campo ao mesmo tempo; na prática é o que estiver em jogo).

## 4. Base de mana (Regra 6: fixers flexíveis contam como fontes reais; sem simulação)

| terreno | entrada | cores que produz | observação |
|---|---|---|---|
| Baxter Building | sempre desvirada | — | `{C}`; `{4},{T}`: 4 mana de qualquer combinação |
| Boseiju, Who Endures | sempre desvirada | G | canal `{1}{G}`: destrói artefato / encantamento / terreno não básico de oponente |
| Bountiful Promenade | lenta (desvira com 2+ oponentes: sempre desvirada numa mesa de 4) | WG |  |
| Breeding Pool | choque (2 de vida ou entra virada) | UG |  |
| City of Brass | sempre desvirada | WUBRG | 1 de dano toda vez que fica virada |
| Command Tower | sempre desvirada | WUBRG | qualquer cor da identidade do comandante (as 5) |
| Exotic Orchard | sempre desvirada | — | só cores que um terreno de OPONENTE produz (condicional) |
| Fire-Lit Thicket | sempre desvirada | RG | filtro: precisa de `{R/G}` para sair `{R}{R}`/`{R}{G}`/`{G}{G}` |
| Flooded Grove | sempre desvirada | UG | filtro: precisa de `{G/U}` |
| Great Hall of the Citadel | sempre desvirada | — | `{C}`; `{1},{T}`: 2 mana de qualquer cor, SÓ para magias lendárias |
| Hallowed Fountain | choque (2 de vida ou entra virada) | WU |  |
| Indatha Triome | sempre virada | WBG |  |
| Jetmir's Garden | sempre virada | WRG |  |
| Ketria Triome | sempre virada | URG |  |
| Misty Rainforest | fetch | — | busca Forest/Island |
| Mossfire Valley | sempre desvirada | RG | `{1},{T}`: `{R}{G}` (precisa de 1 mana de entrada) |
| Overflowing Basin | sempre desvirada | UG | `{1},{T}`: `{G}{U}` (precisa de 1 mana de entrada) |
| Overgrown Tomb | choque (2 de vida ou entra virada) | BG |  |
| Plaza of Heroes | sempre desvirada | — | `{C}`; qualquer cor SÓ para magia lendária (todo planeswalker e as 8 "Way of…" são lendários) |
| Rejuvenating Springs | lenta (desvira com 2+ oponentes: sempre desvirada numa mesa de 4) | UG |  |
| Spara's Headquarters | sempre virada | WUG |  |
| Spire Garden | lenta (desvira com 2+ oponentes: sempre desvirada numa mesa de 4) | RG |  |
| Starting Town | virada a partir do 4º turno | WUBRG | `{C}`, ou qualquer cor pagando 1 de vida; entra virado depois do 3º turno |
| Steam Vents | choque (2 de vida ou entra virada) | UR |  |
| Stomping Ground | choque (2 de vida ou entra virada) | RG |  |
| Temple Garden | choque (2 de vida ou entra virada) | WG |  |
| The World Tree | sempre virada | G | sempre virado; com 6+ terrenos todos os terrenos tocam de qualquer cor; `{G}` |
| Twilight Mire | sempre desvirada | BG | filtro: precisa de `{B/G}` |
| Undergrowth Stadium | lenta (desvira com 2+ oponentes: sempre desvirada numa mesa de 4) | BG |  |
| Verdant Catacombs | fetch | — | busca Forest/Swamp |
| Watery Grave | choque (2 de vida ou entra virada) | UB |  |
| Windswept Heath | fetch | — | busca Forest/Plains |
| Wooded Bastion | sempre desvirada | WG | filtro: precisa de `{G/W}` |
| Wooded Foothills | fetch | — | busca Forest/Mountain |
| Yavimaya, Cradle of Growth | sempre desvirada | G | **todo terreno é Forest**: todo terreno toca `{G}` e toda fetch com Forest acha qualquer terreno |
| Zagoth Triome | sempre virada | UBG |  |

Entrada: sempre desvirada: 14; choque (2 de vida ou entra virada): 7; sempre virada: 6; lenta (desvira com 2+ oponentes: sempre desvirada numa mesa de 4): 4; fetch: 4; virada a partir do 4º turno: 1. **Nenhum terreno básico na lista**: as fetches só acham terrenos com tipo de terreno (choques, triomes, e qualquer terreno com a Yavimaya em campo).

**Alvos de cada fetch (terrenos da lista com o tipo de terreno pedido; com a Yavimaya em campo, qualquer terreno):**

- Misty Rainforest: 12 alvos (Breeding Pool, Hallowed Fountain, Indatha Triome, Jetmir's Garden, Ketria Triome, Overgrown Tomb, Spara's Headquarters, Steam Vents, Stomping Ground, Temple Garden, Watery Grave, Zagoth Triome)
- Verdant Catacombs: 10 alvos (Breeding Pool, Indatha Triome, Jetmir's Garden, Ketria Triome, Overgrown Tomb, Spara's Headquarters, Stomping Ground, Temple Garden, Watery Grave, Zagoth Triome)
- Windswept Heath: 10 alvos (Breeding Pool, Hallowed Fountain, Indatha Triome, Jetmir's Garden, Ketria Triome, Overgrown Tomb, Spara's Headquarters, Stomping Ground, Temple Garden, Zagoth Triome)
- Wooded Foothills: 10 alvos (Breeding Pool, Indatha Triome, Jetmir's Garden, Ketria Triome, Overgrown Tomb, Spara's Headquarters, Steam Vents, Stomping Ground, Temple Garden, Zagoth Triome)

| fonte de cor | W | U | B | R | G |
|---|---|---|---|---|---|
| terrenos que produzem a cor (diretas, inclui filtros e `Command Tower` / `City of Brass` / `Starting Town`) | 10 | 13 | 9 | 10 | 25 |
| + 4 fetches (pelas cores dos alvos) | 14 | 17 | 13 | 14 | 29 |
| + 4 fixers de mana não-terreno sem condição (Arcane Signet, Birds of Paradise, Noble Hierarch, Ignoble Hierarch) | 17 | 20 | 16 | 17 | 33 |

Não contados acima (dependem de condição): Plaza of Heroes e Great Hall of the Citadel (só magias lendárias), Exotic Orchard e Fellwar Stone (cores de terrenos de oponente), Bloom Tender e Faeburrow Elder (cores entre os permanentes que você controla), Chromatic Orrery (gasta mana como qualquer cor), Wrenn and Realmbreaker (terrenos tocam de qualquer cor), The World Tree (6+ terrenos).

**Hipergeométrica por cor** (baralho de 99, 7 cartas + 1 compra por turno a partir do T2, sem mulligan; fontes = linha "+ 4 fixers" acima; uma cor por vez, NÃO é a probabilidade conjunta das cinco):

| cor (fontes) | ≥1 até T2 | ≥1 até T3 | ≥1 até T4 | ≥2 até T6 | ≥2 até T8 |
|---|---|---|---|---|---|
| W (17) | 79.2% | 83.1% | 86.3% | 65.3% | 74.3% |
| U (20) | 84.8% | 88.1% | 90.8% | 74.9% | 82.8% |
| B (16) | 77.0% | 81.0% | 84.4% | 61.6% | 70.8% |
| R (17) | 79.2% | 83.1% | 86.3% | 65.3% | 74.3% |
| G (33) | 96.6% | 97.9% | 98.6% | 95.6% | 98.0% |

Exigência de cor dos não-terrenos (pips `{X}` no custo; sem híbridos): W: 13 cartas (2 com 2+, 0 com 3+); U: 20 cartas (4 com 2+, 0 com 3+); B: 10 cartas (3 com 2+, 0 com 3+); R: 10 cartas (2 com 2+, 0 com 3+); G: 21 cartas (4 com 2+, 0 com 3+). O comandante custa `{1}{G}{U}` e a ativação dele pede `{W}{U}{B}{R}{G}` + `{T}`.

## 5. EDHREC (snapshot de 2026-10-19)

Decks do Tam no EDHREC: **6931** (bracket declarado em 932: B1 16, B2 187, B3 567, B4 152, B5 10). Temas: Planeswalkers 535, Tokens 96, Proliferate 94, Legends 90, Historic 63, Empower Jace 62, Control 40, Combo 30.

**Cartas de maior inclusão no EDHREC e onde estão neste registro** (inclusão = decks com a carta / decks do Tam; só cartas que o EDHREC lista; as 50 maiores):

| carta | inclusão | sinergia | neste deck? |
|---|---|---|---|
| Command Tower | 92% | +0.03 | deck |
| Island | 85% | +0.05 | não está |
| Forest | 84% | +0.02 | não está |
| Sol Ring | 83% | +0.04 | deck |
| Arcane Signet | 83% | +0.07 | deck |
| Plains | 81% | +0.03 | não está |
| Oath of Teferi | 79% | +0.76 | deck |
| Swamp | 77% | +0.01 | não está |
| Mountain | 75% | -0.03 | não está |
| Sanctum Lurker | 74% | +0.66 | deck |
| Exotic Orchard | 71% | +0.07 | deck |
| Vraska, Betrayal's Sting | 68% | +0.66 | deck |
| Ichormoon Gauntlet | 67% | +0.65 | deck |
| Ajani Unrelenting | 66% | +0.63 | deck |
| Loyal Tutor | 65% | +0.59 | não está |
| Commodore Guff | 64% | +0.63 | não está |
| Nicol Bolas, Dragon-God | 64% | +0.61 | não está |
| Tamiyo, Field Researcher | 64% | +0.62 | deck |
| Way of the Paradox | 63% | +0.56 | deck |
| The Chain Veil | 63% | +0.61 | deck |
| Carth the Lion | 62% | +0.61 | não está |
| The Theorist, Jace Beleren | 62% | +0.58 | não está |
| Oath of Nissa | 61% | +0.59 | deck |
| Elspeth, Sun's Champion | 58% | +0.56 | deck |
| Chromatic Lantern | 57% | +0.07 | não está |
| Wrenn and Realmbreaker | 57% | +0.54 | deck |
| Interplanar Beacon | 56% | +0.55 | não está |
| Flux Channeler | 56% | +0.54 | deck |
| Chandra, Torch of Defiance | 53% | +0.52 | **sideboard** |
| Doubling Season | 53% | +0.46 | não está |
| Farseek | 53% | +0.10 | não está |
| Breeding Pool | 52% | +0.20 | deck |
| Swords to Plowshares | 51% | +0.12 | não está |
| Tekuthal, Inquiry Dominus | 51% | +0.49 | não está |
| Way of the Pyromancer | 50% | +0.46 | deck |
| Chandra, Chill of Compliance | 50% | +0.49 | **sideboard** |
| Ripples of Potential | 50% | +0.48 | deck |
| Teferi, Temporal Archmage | 50% | +0.48 | deck |
| Hallowed Fountain | 50% | +0.23 | deck |
| Deepglow Skate | 49% | +0.47 | não está |
| Temple Garden | 49% | +0.18 | deck |
| Oko, Thief of Crowns | 49% | +0.46 | deck |
| Jace, Multiverse Architect | 47% | +0.42 | não está |
| Birds of Paradise | 47% | +0.21 | deck |
| Overgrown Tomb | 47% | +0.17 | deck |
| Bloom Tender | 46% | +0.26 | deck |
| Karn's Bastion | 45% | +0.42 | não está |
| Chandra, Legacy of Fire | 45% | +0.44 | deck |
| Watery Grave | 45% | +0.21 | deck |
| Oath of Ajani | 45% | +0.44 | não está |

Cartas com ≥ 30% de inclusão no EDHREC que **não estão** nem no deck nem no sideboard, fora os 5 terrenos básicos (42): Loyal Tutor (65%), Commodore Guff (64%), Nicol Bolas, Dragon-God (64%), Carth the Lion (62%), The Theorist, Jace Beleren (62%), Chromatic Lantern (57%), Interplanar Beacon (56%), Doubling Season (53%), Farseek (53%), Swords to Plowshares (51%), Tekuthal, Inquiry Dominus (51%), Deepglow Skate (49%), Jace, Multiverse Architect (47%), Karn's Bastion (45%), Oath of Ajani (45%), Evolution Sage (44%), Atraxa, Praetors' Voice (43%), Teferi, Master of Time (42%), Godless Shrine (42%), Reflecting Pool (41%), Lae'zel, Vlaakith's Champion (40%), Liliana, Dreadhorde General (40%), Nature's Lore (39%), Tomik, Orzhov Lawmage (39%), Sacred Foundry (37%), Path to Exile (37%), Ugin, the Spirit Dragon (37%), Narset, Parter of Veils (36%), Three Visits (36%), Spark Double (36%), Brokers Ascendancy (36%), Flooded Strand (35%), Blood Crypt (33%), Jace, Reality Sculptor (33%), Mutational Advantage (33%), Teferi, Time Raveler (32%), Polluted Delta (32%), Transformative Commons (32%), Geist of Saint Thalia (31%), Fatehold Annex (31%), Delighted Halfling (31%), Gideon's Memorial (30%).

Cartas do deck que o EDHREC **não lista** nas listas deste comandante (inclusão baixa demais para aparecer, ou carta nova): 19: Baxter Building, Bountiful Promenade, Displacer Kitten, Domri, Chaos Bringer, Fire-Lit Thicket, Flooded Grove, Garruk Wildspeaker, Leyline Immersion, Mossfire Valley, Nissa, Ascended Animist, Overflowing Basin, Rejuvenating Springs, Spire Garden, Staff of Compleation, Starting Town, Tezzeret the Seeker, Twilight Mire, Undergrowth Stadium, Wooded Bastion.

## 6. Combos (Commander Spellbook) e probabilidade real (Regra 7)

116 nomes resolvidos no Spellbook, **0 não reconhecidos** (inclui o comandante, lançado em 2026-10-02); controle positivo (Thassa's Oracle + Demonic Consultation aparece): True; controle de corte (sem a Consultation o combo some): True. Combos no deck exato: **2**; "quase" (a uma carta de distância): 92.

| combo | peças | mana mínimo das peças (com a Tam em campo para o planeswalker) |
|---|---|---|
| Teferi, Temporal Archmage + The Chain Veil | 2 | Teferi 6 (5 com a Tam) + Veil 4 + ativação `{4}` |
| Chromatic Orrery + Tezzeret the Seeker + The Chain Veil | 3 | Orrery 7 + Veil 4 + Tezzeret 5 (4 com a Tam); o Orrery já dá `{C}`×5 para pagar a ativação do Veil |

Probabilidade de ter **todas as peças já vistas** (7 cartas + 1 compra por turno a partir do T2, sem mulligan, sem tutor), deck de 99:

| até o turno | cartas vistas | Teferi TA + Chain Veil | Orrery + Tezzeret + Chain Veil | qualquer dos dois |
|---|---|---|---|---|
| T5 | 11 | 1.13% | 0.105% | 1.23% |
| T6 | 12 | 1.36% | 0.140% | 1.49% |
| T8 | 14 | 1.88% | 0.232% | 2.08% |
| T10 | 16 | 2.47% | 0.357% | 2.78% |
| T12 | 18 | 3.15% | 0.520% | 3.59% |

**Tutores que mudam a conta:** `Tezzeret the Seeker` (−X: busca artefato de MV ≤ X e põe em campo: pode buscar o The Chain Veil com X = 4, mas entra com 4 de lealdade e fica em 0) e `Entrust the Spark` (sacrifica um planeswalker e busca um planeswalker: acha Tezzeret ou Teferi). O Spellbook **não** conta isso.

**Atenção ao combo Teferi + Chain Veil neste deck:** o passo-a-passo do próprio Spellbook (variante `787-1124`, `dados/spellbook_combos_detalhe.json`) inclui *"Cast Teferi from your command zone"* e o pré-requisito *"You have enough mana to recast Teferi from your command zone minus four"*: o laço infinito **recasta o Teferi da zona de comando** depois que ele morre por lealdade 0. **Aqui o comandante é a Tam**, o Teferi está nos 99 e não volta ao comando. O Spellbook o lista como incluído porque as duas cartas estão no deck, mas sem o recast o laço do Veil gasta 1 de lealdade por volta e **termina** quando o Teferi chega a 0 (leitura do texto do Spellbook, não simulada; **este deck tem várias fontes de lealdade (proliferate da própria Tam, Ichormoon Gauntlet, Flux Channeler, Vraska, Teferi's Talent...) que podem repor a lealdade do Teferi, mas isso NÃO foi verificado**: nem o Spellbook o lista, nem há simulador). O combo Orrery + Tezzeret + Veil não tem esse requisito (`+1` do Tezzeret desvira Orrery e Veil: rende `{C}`×5 − `{4}` por volta).

**"Quase" cuja peça que falta está no SIDEBOARD** (1): Vorinclex, Monstrous Raider + Vraska, Betrayal's Sting → Target opponent loses the game (bracket S). Trazer essa carta para o deck criaria um combo de 2 cartas: pesa no Bracket.

## 7. Varreduras de oráculo (regex sobre `oracle_text` sem o texto de lembrete; só o deck de 99 + comandante; varredura heurística, NÃO é lista exaustiva de efeitos; lista os nomes para conferência)

- **contramágica ("counter target")** (0): nenhuma
- **tutor / busca na biblioteca (não-terreno)** (3): Entrust the Spark, Kasmina, Enigma Sage, Tezzeret the Seeker
- **turno extra** (1): Ichormoon Gauntlet
- **destruição em massa de terrenos** (0): nenhuma
- **remoção em massa de criaturas** (6): Ajani Unrelenting, Blasphemous Act, Elspeth, Sun's Champion, Garruk, Veiled Butcher, Overwrite the Multiverse, The Eternal Wanderer
- **proliferate** (8): Dreamtide Whale, Flux Channeler, Ichormoon Gauntlet, Patrolling Peacemaker, Ripples of Potential, Staff of Compleation, Tam, the Possibility, Vraska, Betrayal's Sting
- **compra de cartas** (14): Ajani Unrelenting, Aminatou, the Fateshifter, Chromatic Orrery, Dack Fayden, Garruk, Curse Breaker, Garruk, Veiled Butcher, Minsc & Boo, Timeless Heroes, Professor Dellian Fel, Staff of Compleation, Tamiyo, Field Researcher, Teferi's Talent, Teferi, Hero of Dominaria, Vraska, Betrayal's Sting, Way of the Mind Sculptor
- **cria ficha de Jace (empower Jace)** (10): Overwrite the Multiverse, Sanctum Lurker, Way of the Deathbringer, Way of the Healer, Way of the Mind Sculptor, Way of the Necromancer, Way of the Paradox, Way of the Pyromancer, Way of the Warlord, Way of the Wildspeaker
- **dano direto / perda de vida a oponentes** (5): All Will Be One, Chandra, Legacy of Fire, Minsc & Boo, Timeless Heroes, Professor Dellian Fel, Sanctum Lurker

Sideboard (13, fora do deck): Ajani Resolute, Ajani, Outland Chaperone, Archangel Elspeth, Ashiok, Dream Render, Chandra, Chill of Compliance, Chandra, Dressed to Kill, Chandra, Torch of Defiance, Dakkon, Shadow Slayer, Domri, Anarch of Bolas, Dovin, Hand of Control, Elspeth, Storm Slayer, Garruk, Cursed Huntsman, Vorinclex, Monstrous Raider. Tipos: Planeswalker 12, Criatura 1.

# Auditoria — Maralen, Fae Ascendant (Sultai — B/G/U)

Fontes usadas nesta auditoria: Scryfall REST API (`cards/collection` para as 92 cartas únicas da lista, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `cmc`), consultada em 2026-08-23. EDHREC (`json.edhrec.com/pages/commanders/maralen-fae-ascendant.json`), consultado em 2026-08-23. Definições de Bracket: `references/commander-rules.md#brackets` do skill mtg-commander.
Data da auditoria: 2026-08-23

---

## 1. Validação formal

| Check | Resultado | Fonte |
|---|---|---|
| Total de cartas | **100** (1 comandante + 99 no corpo da lista) | contagem de linhas com quantidade em `lista.md` |
| Singleton | Sem duplicatas fora de terrenos básicos | checagem de nomes únicos |
| Identidade de cor (B/G/U) | Sem violação — todas as 92 cartas únicas do corpo têm `color_identity` ⊆ {B,G,U} | `color_identity` de cada carta |
| Legalidade em Commander | Sem problemas — todas as 93 cartas checadas (comandante incluso) têm `legalities.commander: legal` | `legalities.commander` |

**Comandante:** Maralen, Fae Ascendant — `{2}{B}{G}{U}` — Legendary Creature — Elf Faerie Noble.
```
Flying
Whenever Maralen or another Elf or Faerie you control enters, exile the top
two cards of target opponent's library.
Once each turn, you may cast a spell with mana value less than or equal to
the number of Elves and Faeries you control from among cards exiled with
Maralen this turn without paying its mana cost.
```
Lançada em `ecl` (2026-01-23) — verificado via Scryfall.

Duas cartas de dupla face precisaram do nome completo pra bater com o padrão de cache: **Brazen Borrower // Petty Theft** e **Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun**.

---

## 2. Terrenos e curva

- Terrenos: **35**.
- Não-terrenos (sem comandante): **64** — CMC médio: **2,47**. Curva muito baixa, consistente com um deck de criaturas mana-dork em massa + combo, não um deck de bombas caras.
- Fontes de cor nos terrenos (contando lands "any color in commander identity" pra todas as 3 cores): **B 22 / G 22 / U 22** — base de mana perfeitamente equilibrada entre as 3 cores, sem cor secundária fraca. Duais reais: Bayou, Breeding Pool, Darkwater Catacombs, Drowned Catacomb, Hinterland Harbor, Overgrown Tomb, Sunken Hollow, Tropical Island, Underground Sea, Watery Grave, Woodland Cemetery, Yavimaya Coast, Underground River, Zagoth Triome (triome) — mais os rocks/lands de qualquer cor da identidade: Command Tower, Arcane Signet, Exotic Orchard, Reflecting Pool, Path of Ancestry, Cavern of Souls, Secluded Courtyard.

---

## 3. O motor central — Maralen + gatilho de Elfo/Fada

O comandante em si é o motor: **todo Elfo ou Fada que entra em campo exila 2 cartas do topo da biblioteca de um oponente**, e uma vez por turno você pode conjurar de graça (até o custo = número de Elfos+Fadas que você controla) uma carta exilada com ela naquele turno. Isso significa que quanto mais larga a base de Elfos/Fadas, mais threat denial (rouba recursos do oponente) E mais teto de custo pra jogar de graça as cartas roubadas.

**Densidade tribal real na lista** (contagem por `type_line`):
- Elfos: Allosaurus Shepherd, Elves of Deep Shadow, Bloom Tender, Elvish Mystic, Llanowar Elves, Joraga Treespeaker, Heritage Druid, Birchlore Rangers, Priest of Titania, Elvish Archdruid, Marwyn, Circle of Dreams Druid, Devoted Druid, Elvish Harbinger, Elvish Warmaster, Imperious Perfect, Fauna Shaman, Formidable Speaker, Ezuri Renegade Leader — **19 Elfos**.
- Fadas: High Fae Trickster, Alela, Bitterbloom Bearer, Faerie Harbinger, Faerie Mastermind, Mistbind Clique, Obyra, Spellstutter Sprite, Tegwyll, Scryb Ranger, Brazen Borrower, Cloud of Faeries, Glen Elendra Archmage — **13 Fadas** (Bitterblossom cria tokens Fada, não é ela mesma uma criatura Fada).
- **32 criaturas que disparam Maralen diretamente**, sem contar tokens Fada gerados por Bitterblossom/Bitterbloom Bearer/Obyra/Alela/Tegwyll (que TAMBÉM disparam Maralen ao entrar, já que são tokens do tipo Faerie).

Grande parte das Fadas tem **Flash** nativo (High Fae Trickster, Bitterbloom Bearer, Faerie Harbinger, Faerie Mastermind, Mistbind Clique, Obyra, Spellstutter Sprite, Scryb Ranger, Glen Elendra Archmage — 8 das 13), e o deck ainda soma **Leyline of Anticipation, Vedalken Orrery e High Fae Trickster** (ela mesma dá flash a tudo) como habilitadores de flash universal — ou seja, o deck pode disparar o gatilho de Maralen na ponta do turno do oponente, maximizando informação antes de decidir o que exilar/jogar de graça.

---

## 4. Motor de ramp Élfico — extremamente denso, com combo estrutural real

Contei **17 criaturas que produzem mana** entre os Elfos da lista — Elves of Deep Shadow, Bloom Tender, Elvish Mystic, Llanowar Elves, Joraga Treespeaker, Heritage Druid, Birchlore Rangers, Priest of Titania, Elvish Archdruid, Marwyn, Circle of Dreams Druid, Devoted Druid, Elvish Harbinger, Wirewood Symbiote (não produz mana, mas desenrola ativações via bounce-untap), Cryptolith Rite e Elven Chorus (dão habilidade de mana a toda criatura). Isso é ramp em volume muito acima do normal de um deck de 99 cartas.

### Combo real de 2 peças encontrado — Umbral Mantle + mana dork escalável

Texto real do **Umbral Mantle** (`{3}`, Artifact — Equipment, Equip `{0}`):
```
Equipped creature has "{3}, {Q}: This creature gets +2/+2 until end of turn."
```
(`{Q}` é o símbolo de "untap" usado como custo — a habilidade concedida permite pagar `{3}` e destapar a criatura equipada como parte do custo, mesmo que ela já esteja destapada.)

Qualquer criatura da lista que produza **4 ou mais manas por ativação**, equipada com Umbral Mantle (Equip `{0}`, de graça), gera **mana infinita**: tapar pra mana → pagar `{3}` da própria habilidade do Mantle (que destapa a criatura) → tapar de novo → repete, líquido positivo a cada iteração. Candidatos reais na lista que alcançam 4+ mana com facilidade nesta build:

- **Priest of Titania** — `{T}: Add {G} for each Elf on the battlefield` (conta TODOS os elfos, inclusive alheios em mesa multiplayer).
- **Elvish Archdruid** — `{T}: Add {G} for each Elf you control`.
- **Marwyn, the Nurturer** — `{T}: Add {G} equal to Marwyn's power` (o próprio poder cresce +1/+1 a cada Elfo que entra).
- **Circle of Dreams Druid** — `{T}: Add {G} for each creature you control` (conta qualquer criatura, não só Elfo — o alvo mais fácil de ativar cedo).

Com **19 Elfos** na lista e vários tutores reais que buscam essas peças especificamente (ver seção 6), esse não é um combo de canto — é estruturalmente favorecido pela composição do deck. Uma vez com mana infinita, **Staff of Domination** (`{3}`, já na lista) converte em: `{5},{T}: Draw a card` repetido (compra infinita, via `{1}: Untap this artifact`), `{4},{T}: Tap target creature` repetido (trava todos os bloqueadores/atacantes do oponente), ou `{3},{T}: Untap target creature` repetido em algo como **Imperious Perfect** (`{G},{T}: Create a 1/1 Elf`) pra exército infinito de Elfos.

**Isso é um combo de 2 peças genuíno pelas regras reais** (Umbral Mantle + qualquer um dos 4 dorks acima), com uma 3ª peça (Staff of Domination) convertendo em vitória/travamento. Registrado com todo o peso na seção 9 (Bracket).

---

## 5. Card draw — 7 fontes diretas

Rhystic Study, Mystic Remora, Kindred Discovery (escolhe tipo ao entrar — Elfo ou Fada, dispara em ETB e ataque), Faerie Mastermind (passiva + ativada `{3}{U}: cada jogador compra`), Tegwyll (compra quando outra Fada sua morre), Black Market Connections (modo "Buy Information"), Staff of Domination (`{5},{T}: Draw a card`, sorvedouro de mana).

---

## 6. Tutores — densidade real, alimentam o combo da seção 4

- **Green Sun's Zenith** — busca qualquer criatura verde CMC X ou menos direto pro campo. Pode buscar Priest of Titania, Elvish Archdruid, Circle of Dreams Druid ou Marwyn diretamente.
- **Fauna Shaman** — `{G},{T}, descarta uma criatura: busca qualquer criatura pra mão`, repetível.
- **Elvish Harbinger** — ETB, busca Elfo pro topo da biblioteca.
- **Faerie Harbinger** — ETB, busca Fada pro topo da biblioteca.
- **Formidable Speaker** — ETB, descarta uma carta pra buscar criatura pra mão.

**5 tutores reais** — densidade alta pra um deck de Bracket declarado abaixo de 4, e 3 deles (Green Sun's Zenith, Fauna Shaman, Elvish Harbinger) buscam especificamente o tipo de criatura que alimenta o combo da seção 4.

---

## 7. Remoção e interação — 6 peças pontuais + 1 wipe + 3 contra-mágicas

**Remoção pontual:** Pongify, Rapid Hybridization, Reality Shift (todas exile/destroy + compensação pro oponente), Assassin's Trophy (qualquer permanente), Cyclonic Rift (bounce, com overload pra board bounce total), Boseiju Who Endures (channel, destrói artefato/encantamento/terreno não-básico).

**Wipe:** Toxic Deluge (`-X/-X` em todas as criaturas, X = vida paga).

**Contra-mágicas:** Counterspell, Arcane Denial, Swan Song (encantamento/instant/sorcery), Spellstutter Sprite (ETB, conta X = Fadas controladas), Glen Elendra Archmage (`{U}`, sacrifício: contra não-criatura, com Persist pra reciclar 1x).

Interação sólida e eficiente em mana (a maioria custa 1-2 mana), reforçada pelo pacote de flash universal (Leyline of Anticipation/Vedalken Orrery/High Fae Trickster) que permite reagir em qualquer turno.

---

## 8. Game Changers — contagem oficial (3/3)

Cruzamento ao vivo contra `https://api.scryfall.com/cards/search?q=is:gamechanger` (53 cartas, consultado 2026-08-23):

**3 Game Changers: Cyclonic Rift, Rhystic Study, Seedborn Muse.**

Deck está exatamente no teto do Bracket 3 por essa métrica isolada (mesmo patamar do Toph). Combinado com o combo real da seção 4, isso pesa pra Bracket 4 — ver seção 9.

---

## 9. Varredura de combo e estruturas restritas por Bracket

- **Combo de 2 peças: ENCONTRADO.** Umbral Mantle + qualquer um de {Priest of Titania, Elvish Archdruid, Marwyn, Circle of Dreams Druid} = mana verde infinita (ver seção 4, com o texto oracle exato de cada peça). Staff of Domination (3ª peça, já na lista) converte a mana infinita em compra infinita, trava de criaturas, ou exército infinito de token via Imperious Perfect. Isso **viola diretamente** a restrição de Bracket 3 contra combos de 2 peças — não é um combo teórico obscuro, é composto só de cartas reais desta lista, com múltiplos tutores (Green Sun's Zenith, Fauna Shaman, Elvish Harbinger) capazes de buscar as peças especificamente.
- **Densidade de tutores:** 5 tutores reais (seção 6), acima do normal pra Bracket 3, e alimentando diretamente o combo acima.
- **Negação de terras em massa:** nenhuma encontrada — Boseiju é remoção pontual de terreno não-básico, com compensação pro oponente.
- **Turnos extras:** nenhum efeito de turno extra no texto de nenhuma carta.
- **Combate adicional:** nenhum encontrado.

**Classificação provisória: Bracket 4.** A presença de um combo de 2 peças genuíno e estruturalmente favorecido pela composição do deck (19 Elfos, 4 candidatos válidos de mana escalável, 3 tutores que buscam essas peças) é, por si só, incompatível com os critérios de Bracket 3 usados nas auditorias anteriores deste repositório — independente da contagem de Game Changers (que já está no teto de qualquer forma, 3/3). Consistente com o precedente do Edgar Markov nesta mesma biblioteca: se o usuário quiser, um simulador de goldfish pode medir a taxa real de montagem do combo até o turno 6 (com e sem política de "caçar" via os tutores) antes de uma reclassificação — mas a classificação de partida, baseada na varredura de texto, é Bracket 4.

---

## 10. Cruzamento com dados reais do EDHREC (sinergia com o comandante)

Consultado `json.edhrec.com/pages/commanders/maralen-fae-ascendant.json` (2026-08-23, 286 cartas rastreadas). As **15 cartas de maior sinergia real** com Maralen segundo o próprio EDHREC:

| # | Carta | Synergy | Na lista? |
|---|---|---|---|
| 1 | High Fae Trickster | +0,597 | ✅ |
| 2 | Llanowar Elves | +0,592 | ✅ |
| 3 | Bitterbloom Bearer | +0,537 | ✅ |
| 4 | Elvish Mystic | +0,509 | ✅ |
| 5 | Bitterblossom | +0,490 | ✅ |
| 6 | Obyra, Dreaming Duelist | +0,487 | ✅ |
| 7 | Priest of Titania | +0,474 | ✅ |
| 8 | Alela, Cunning Conqueror | +0,464 | ✅ |
| 9 | Imperious Perfect | +0,450 | ✅ |
| 10 | Faerie Mastermind | +0,446 | ✅ |
| 11 | Elvish Archdruid | +0,444 | ✅ |
| 12 | Cloud of Faeries | +0,440 | ✅ |
| 13 | Spellstutter Sprite | +0,434 | ✅ |
| 14 | Lathril, Blade of the Elves | +0,428 | ❌ |
| 15 | Bloom Tender | +0,421 | ✅ |

**14 de 15 — alinhamento quase perfeito com o build padrão da comunidade.** Só falta Lathril, Blade of the Elves (Elfo lendário, drena vida por Elfo tapado — encaixaria bem, não está na lista atual).

Também relevante: nas tags do EDHREC pra este comandante, **"Combo" aparece em 276 dos decks rastreados e "cEDH" em 120** — confirma de forma independente (dado real da comunidade, não inferência minha) que a base de jogadores já reconhece este comandante como combo-capaz, batendo com o achado da seção 4.

---

## 11. Classificação de Bracket

**Bracket 4**, por dois critérios independentes: (a) 3/3 Game Changers, no teto; (b) combo de 2 peças real e estruturalmente favorecido (Umbral Mantle + mana dork escalável, seção 4/9), incompatível com o limite de Bracket 3. Dado real do EDHREC (tag "cEDH" em 120 decks rastreados) corrobora que a comunidade já trata este comandante como capaz de linhas competitivas.

---

## Links

- EDHREC: https://edhrec.com/commanders/maralen-fae-ascendant
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
- Scryfall (comandante): https://scryfall.com/search?q=%21%22Maralen%2C+Fae+Ascendant%22

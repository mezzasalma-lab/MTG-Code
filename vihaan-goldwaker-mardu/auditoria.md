# Auditoria — Vihaan, Goldwaker (Mardu — R/W/B)

Fontes usadas nesta auditoria: Scryfall REST API (`cards/collection` para as 94 cartas únicas da lista, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `produced_mana`, `cmc`), consultada em 2026-08-22. EDHREC (`json.edhrec.com/pages/commanders/vihaan-goldwaker.json`), consultado em 2026-08-22. Definições de Bracket: `references/commander-rules.md#brackets` do skill mtg-commander (fonte primária: anúncios oficiais da Wizards).
Data da auditoria: 2026-08-22

---

## 1. Validação formal

| Check | Resultado | Fonte |
|---|---|---|
| Total de cartas | **100** (1 comandante + 99 no corpo da lista) | contagem de linhas com quantidade em `lista.md` |
| Singleton | Sem duplicatas fora de terrenos básicos | checagem de nomes únicos |
| Identidade de cor (R/W/B) | Sem violação — todas as 93 cartas únicas do corpo têm `color_identity` ⊆ {R,W,B} | `color_identity` de cada carta |
| Legalidade em Commander | Sem problemas — todas as 94 cartas checadas (comandante incluso) têm `legalities.commander: legal` | `legalities.commander` |

**Comandante:** Vihaan, Goldwaker — `{R}{W}{B}` — Legendary Creature — Dwarf Warlock.
```
Other outlaws you control have vigilance and haste. (Assassins, Mercenaries,
Pirates, Rogues, and Warlocks are outlaws.)
At the beginning of combat on your turn, you may have Treasures you control
become 3/3 Construct Assassin artifact creatures in addition to their other
types until end of turn.
```
Nota mecânica: um Treasure virado 3/3 Construct **Assassin** é, ele mesmo, um outlaw — então ganha vigilance/haste da própria habilidade estática do Vihaan. É um wincon de verdadeiro exército de tesouros, não só uma curiosidade de texto.

---

## 2. Terrenos e curva

- Terrenos: **35** (varredura de `type_line` em qualquer face, incluindo o MDFC Brightclimb Pathway // Grimclimb Pathway).
- Não-terrenos (sem comandante): **64** — CMC médio: **3,42** (puxado pra cima por bombas de custo alto: Marionette Master, Blood Money, Goldspan Dragon, Witch of the Moors).

**Contagem de fontes de cor nos terrenos, direto do `produced_mana` da Scryfall:**

| Cor | Fontes (terrenos) |
|---|---|
| B | **21** |
| R | **17** |
| W | **14** |

Preto é a cor primária (bate com o volume de remoção/aristocratas em preto), vermelho secundário (motor de Treasures), branco é o mais raro em fontes dedicadas — mas o deck tem uma base de mana real de duais/checklands/painlands: Blood Crypt, Blackcleave Cliffs, Isolated Chapel, Clifftop Retreat, Dragonskull Summit, Sulfurous Springs, Caves of Koilos, Battlefield Forge, Rugged Prairie, Fetid Heath, Luxury Suite, Spectator Seating, Tainted Peak, Shadowblood Ridge, Desolate Mire — mais os 3 rocks de qualquer cor da identidade (Command Tower, Exotic Orchard, Path of Ancestry). Base de mana sólida pra 3 cores.

---

## 3. O motor central — Treasures em escala industrial

Esse é, de longe, o tema mais denso do deck: **contei 23 fontes reais de criação de Treasure** na lista (sem contar os 3 multiplicadores abaixo):

Captain Lannery Storm, Deadly Derision, Deadly Dispute, Goldspan Dragon, Grim Hireling, Inspired Tinkering, Kellogg Dangerous Mind, Lotho Corrupt Shirriff, Magda the Hoardmaster, Mahadi Emporium Master, Mari the Killing Quill (via drain), Monologue Tax, Olivia Opulent Outlaw, Orochi Soul-Reaver, Pitiless Plunderer, Professional Face-Breaker, Prosper Tome-Bound, Rain of Riches, Revel in Riches, Smothering Tithe, The Reaver Cleaver, Treasure Vault, Unexpected Windfall, Big Score, Black Market Connections, Jan Jansen (via sac de artefato).

**3 multiplicadores reais, empilháveis entre si:**
- **Xorn** — `If you would create one or more Treasure tokens, instead create those tokens plus an additional Treasure token.` +1 fixo por evento de criação.
- **Academy Manufactor** — `If you would create a Clue, Food, or Treasure token, instead create one of each.` Transforma qualquer criação de Treasure numa criação de Clue+Food+Treasure junto.
- **Anointed Procession** — `If an effect would create one or more tokens under your control, it creates twice that many of those tokens instead.` Dobra qualquer token, Treasure incluso.

Com os 3 em campo simultaneamente, um único evento de "crie 1 Treasure" pode virar bem mais que 1 token — não testei a matemática exata aqui (isso é trabalho pro goldfish simulator), mas a estrutura está clara.

**Sacrifício de Treasure com payoff, não só mana:**
- Grim Hireling — `{B}, Sacrifice X Treasures: Target creature gets -X/-X` (removal escalável)
- Kellogg — `Sacrifice five Treasures: Gain control of target creature`
- Magda — `Sacrifice three Treasures: Create a 4/4 red Scorpion Dragon`
- Olivia — `{3}, Sacrifice two Treasures: Put two +1/+1 counters on each creature you control`
- Captain Lannery Storm — `+1/+0 until end of turn` sempre que você sacrifica um Treasure
- Vihaan (comandante) — vira os Treasures em criaturas 3/3 pra atacar

**Wincon alternativo real:** Revel in Riches — `At the beginning of your upkeep, if you control ten or more Treasures, you win the game.` Não é um combo de 2 peças (não liga sozinho, precisa de volume real de board state acumulado), mas é uma condição de vitória alternativa genuína que a auditoria de Bracket precisa registrar — ver seção 8.

---

## 4. Motores identificados — sinergia Outlaw + aristocratas

**Outlaws (Assassin/Mercenary/Pirate/Rogue/Warlock) com sinergia direta ao tipo:**
- Vihaan (comandante): vigilance+haste a outlaws.
- Olivia, Opulent Outlaw: Treasure quando outlaw causa dano de combate.
- Laughing Jasper Flint: torna toda criatura que você não é dona (roubada, etc.) num Mercenary — sinergiza com a contagem "X = outlaws você controla" da própria habilidade dele.
- Mari, the Killing Quill: dá deathtouch + drain-on-combat-damage a Assassins/Mercenaries/Rogues.
- Shoot the Sheriff: remoção condicional — só mata **não-outlaw**, ou seja, o próprio time do deck é imune a ela (relevante se houver troca de controle de criatura, ex: via Kellogg).

**Pacote de drena/aristocratas (paga por criatura/token morrendo ou saindo):**
Zulaport Cutthroat, Nadier's Nightblade, Mirkwood Bats, Kambal Profiteering Mayor (dois gatilhos: token de oponente entra E token seu entra), Agent of the Iron Throne (drain quando artefato/criatura sua morre), Dictate of Erebos (edict simétrico quando sua criatura morre), Sephiroth (as duas faces drenam e transformam a própria carta após 4 mortes), Witch of the Moors, Marionette Master (drain igual ao próprio poder quando um artefato seu morre — sinergiza direto com o volume de Treasures que nascem e são sacrificados).

**Sac outlets reais (não só Treasure):** Ashnod's Altar, Krark-Clan Ironworks, Phyrexian Tower, High Market, Jan Jansen (dois modos).

**Recursão de graveyard:** Sevinne's Reclamation (permanente CMV≤3, com flashback e auto-cópia se lançada do cemitério), Phyrexian Reclamation (criatura, repetível), Back in Town (X criaturas outlaw), Lich-Knights' Conquest (sacrifica artefatos/encantamentos/tokens — tem MUITO Treasure pra alimentar isso — por N criaturas do cemitério).

**Card advantage por exílio ("play from exile"):** Grenzo Havoc Raiser, Laughing Jasper Flint (do oponente!), Prosper Tome-Bound, Professional Face-Breaker, Inspired Tinkering — todos exilam carta(s) do topo e permitem jogar depois, geralmente financiados pela abundância de mana dos próprios Treasures.

---

## 5. Ramp — 3 rocks dedicados + a economia de Treasure

Arcane Signet, Sol Ring, Rakdos Signet — ramp "tradicional" é enxuto (3 peças), porque **o motor de Treasure faz esse papel em volume muito maior** (23 fontes reais, seção 3). Isso é uma escolha de design coerente, não uma lacuna — não conto Treasures como "ramp" separado pra não duplicar a contagem da seção 3.

---

## 6. Card draw — 8 fontes diretas

Caretaker's Talent, Big Score, Unexpected Windfall, Insatiable Avarice (modo Spree `{B}{B}`), Deadly Dispute, Black Market Connections (modo "Buy Information"), Mari the Killing Quill (condicional, via combate), e a linha de "jogar do exílio" da seção 4 funciona como pseudo-draw (Grenzo, Prosper, Professional Face-Breaker, Inspired Tinkering, Laughing Jasper Flint).

---

## 7. Remoção e interação — 5 peças pontuais + 2 wipes

**Remoção pontual:**
- Path to Exile — exile em criatura, `{W}`.
- Shoot the Sheriff — destroy, mas só criaturas **não-outlaw** (seu próprio time passa ileso).
- Council's Judgment — exile via voto, sem precisar de alvo, pega qualquer permanente não-terreno.
- Deadly Derision — destroy criatura/planeswalker + cria Treasure (remoção que também alimenta o motor).
- Requisition Raid — Spree: destrói artefato e/ou encantamento, modos combináveis.

**Wipes:**
- Blasphemous Act — `{8}{R}` reduzido por criatura em campo, 13 de dano em todas — geralmente muito barato de conjurar tarde no jogo.
- Blood Money — destroy all creatures, e cada criatura não-token destruída vira um Treasure tapped pra você — outro wipe que alimenta o próprio motor.

7 peças de interação real (5+2) é uma contagem razoável pro Bracket 3-4, com o detalhe de que **duas delas (Deadly Derision, Blood Money) geram valor positivo pro próprio jogador ao mesmo tempo que interagem** — não é "remoção pura", é remoção com upside.

---

## 8. Game Changers — contagem oficial (2/2)

Cruzamento ao vivo contra `https://api.scryfall.com/cards/search?q=is:gamechanger` (53 cartas, consultado 2026-08-22):

**2 Game Changers: Smothering Tithe, Teferi's Protection.**

---

## 9. Varredura de combo e estruturas restritas por Bracket

- **Combo de 2 peças:** varredura manual do texto oracle completo das 94 cartas, com atenção redobrada nos sac outlets (Ashnod's Altar, Krark-Clan Ironworks, Phyrexian Tower, High Market, Jan Jansen) cruzados com os geradores de Treasure/token. **Não encontrei um loop fechado e gratuito de 2 peças.** Todo sac outlet consome um recurso finito (criatura real ou artefato real) — não há um gerador de token "grátis e repetível dentro do mesmo turno" o suficiente para alimentar um sac outlet infinitamente sem gastar mana adicional a cada iteração. Jan Jansen chega mais perto (sacrifica artefato não-criatura → 2 Constructs; sacrifica artefato-criatura → 2 Treasures) mas cada modo só ativa 1x por turno (`{T}`), não é repetível no mesmo turno.
- **Wincon alternativo (Revel in Riches, 10+ Treasures):** não é um combo de 2 peças pelo critério oficial — não liga sozinho, exige acúmulo real de recurso ao longo de várias partidas de turno. Registrado como wincon real (seção 3), não como violação estrutural.
- **Negação de terras em massa:** nenhuma encontrada — Demolition Field é destruição de terreno único do oponente (com compensação pra ambos os lados, inclusive).
- **Turnos extras:** nenhum efeito de turno extra no texto de nenhuma carta.
- **Combate adicional/turnos extras encadeados:** nenhum encontrado.
- **Densidade de tutores:** **Insatiable Avarice** é o único tutor de carta real da lista (`Spree +{2}: Search your library for a card, put on top`) — 1 tutor em 99 cartas é baixo, dentro do esperado pra Bracket 3.

**Nenhuma das quatro restrições estruturais de Bracket 3 é violada.**

---

## 10. Cruzamento com dados reais do EDHREC (sinergia com o comandante)

Consultado `json.edhrec.com/pages/commanders/vihaan-goldwaker.json` (2026-08-22). As **15 cartas de maior sinergia real** com Vihaan segundo o próprio EDHREC:

| # | Carta | Synergy | Na lista? |
|---|---|---|---|
| 1 | Mahadi, Emporium Master | +0,718 | ✅ |
| 2 | Olivia, Opulent Outlaw | +0,714 | ✅ |
| 3 | Xorn | +0,710 | ✅ |
| 4 | Mari, the Killing Quill | +0,669 | ✅ |
| 5 | Pitiless Plunderer | +0,668 | ✅ |
| 6 | Blood Money | +0,661 | ✅ |
| 7 | Jan Jansen, Chaos Crafter | +0,631 | ✅ |
| 8 | Grim Hireling | +0,621 | ✅ |
| 9 | Big Score | +0,606 | ✅ |
| 10 | Professional Face-Breaker | +0,597 | ✅ |
| 11 | Monologue Tax | +0,577 | ✅ |
| 12 | Goldspan Dragon | +0,577 | ✅ |
| 13 | Lotho, Corrupt Shirriff | +0,575 | ✅ |
| 14 | Deadly Dispute | +0,559 | ✅ |
| 15 | Rain of Riches | +0,553 | ✅ |

**15 de 15 — alinhamento perfeito com o build padrão da comunidade** pra esse comandante. Essa é a lista mais alinhada ao EDHREC das já auditadas neste repositório (Toph teve 11/16, Edgar Markov teve forte alinhamento parcial).

---

## 11. Classificação de Bracket

**Bracket 3 (Upgraded), no teto de Game Changers folgado (2 de 3 — 1 abaixo do teto).**

Base: 2 Game Changers (abaixo do teto de 3), sem negação de terras em massa, sem turnos extras, sem combo de 2 peças identificado na varredura de texto, densidade de tutores baixa (1 carta). O wincon alternativo do Revel in Riches não muda a classificação — não é um combo, é um objetivo de longo prazo condicionado a acumular recurso real. Como o deck está 1 Game Changer abaixo do teto do Bracket 3, há espaço real (não usado) pra subir a densidade de poder dentro do próprio Bracket 3 sem estourar pra Bracket 4, se o usuário quiser.

---

## Links

- EDHREC: https://edhrec.com/commanders/vihaan-goldwaker
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
- Scryfall (comandante): https://scryfall.com/search?q=%21%22Vihaan%2C+Goldwaker%22

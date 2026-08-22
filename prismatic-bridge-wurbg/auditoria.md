# Auditoria — Esika, God of the Tree // The Prismatic Bridge (5 cores — WUBRG)

Fontes usadas nesta auditoria: Scryfall REST API (`cards/collection`, `cards/named`, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `cmc`, `produced_mana`), consultada em 2026-08-20/21. EDHREC (`json.edhrec.com/pages/commanders/esika-god-of-the-tree.json`, campos `synergy`/`num_decks`/`potential_decks`). Definições de Bracket: anúncios oficiais da Wizards ("Introducing Commander Brackets Beta", atualização de outubro/2025) já registrados em `references/commander-rules.md` do skill mtg-commander.
Data da auditoria: 2026-08-20. Ramp/draw/remoção/sinergia/bracket (seções 2-8, 10-11) completados em 2026-08-21 — a versão original não tinha dado de EDHREC nem varredura mecânica de `oracle_text`.

---

## 1. Validação formal

| Check | Resultado | Fonte |
|---|---|---|
| Total de cartas | 100 (99 + comandante) | contagem das linhas coladas pelo usuário |
| Singleton | Sem duplicatas | `uniq -d` sobre os nomes |
| Identidade de cor (5 cores) | Sem violação | `color_identity` de cada carta vs. do comandante |
| Cartas banidas em Commander | Nenhuma | `legalities.commander` |

**Comandante:** Esika, God of the Tree // The Prismatic Bridge — MDFC. Frente: Legendary Creature — God (custo não informado no Scryfall pro lado frente desse card, comum em cards de dupla face com custo só na segunda face). Verso: Legendary Enchantment.

---

## 2. Terrenos e curva

- Terrenos: **37** (contagem por `type_line` contendo "Land" e não contendo "Creature").
- CMC médio, não-terrenos, sem comandante: **3.66** (campo `cmc` do Scryfall).

**Fontes de mana por cor (campo `produced_mana` do Scryfall, todos os 37 terrenos):**

| Cor | Fontes |
|---|---|
| W | 17 |
| U | 16 |
| B | 16 |
| R | 16 |
| G | 17 |

Base de mana muito bem distribuída pras 5 cores — nenhuma cor abaixo de 16 fontes. Isso é esperado nesse arquétipo: o deck roda vários fixadores "qualquer cor" de verdade (Command Tower, Mana Confluence, City of Brass, Exotic Orchard, Arcane Signet, Chromatic Lantern), os 10 dual lands originais (ABUR: Bayou, Badlands, Plateau, Savannah, Scrubland, Taiga, Tropical Island, Tundra, Underground Sea, Volcanic Island — cada um cobre 2 das 5 cores) e os 5 shocklands restantes (Breeding Pool, Blood Crypt, Godless Shrine, Hallowed Fountain, Overgrown Tomb, Sacred Foundry, Steam Vents, Stomping Ground, Temple Garden, Watery Grave — conferir contagem exata). Diferente do Thranduil (3 cores, 1 cor sistematicamente mais fraca), aqui não há gargalo de cor evidente pelos números brutos.

Ainda não tenho dado de goldfish rodado (script Python) pra esse deck — a única simulação registrada é 1 partida manual em `goldfish-log.md`. Não vou estimar taxa de "color screw" real sem isso.

---

## 3. Ramp — 9 peças

Cruzamento mecânico de `oracle_text` (regex por `{T}: Add`/"search your library for a [tipo básico] card", não de memória) contra as 99 cartas do mainboard:

Arcane Signet, Bloom Tender, Chromatic Lantern, Delighted Halfling, Farseek, Nature's Lore, Sol Ring, Three Visits, Vraska, Betrayal's Sting (ultimate de mana, ver seção 7).

**9 peças de ramp num deck de 5 cores com CMC médio 3.66** é uma contagem baixa pro que a curva pede — a recomendação padrão de 10-12 (`SKILL.md`) já é pra decks de 2-3 cores; num 5-color com fixação exigente, o normal é rodar mais rocks/dorks, não menos. Ponto de atenção real, mas o comandante em si (Esika, God of the Tree: `{T}: Add one mana of any color` + concede a mesma habilidade a outras criaturas lendárias) funciona como ramp/fixação adicional sempre que estiver em campo — o que atenua bastante o problema, já que o deck tem alta densidade de lendárias (ver seção 8).

---

## 4. Card draw — 14 fontes

Aminatou the Fateshifter, Kaya Intangible Slayer, Liliana Dreadhorde General, Nicol Bolas Dragon-God, Oko the Ringleader, Rhystic Study, Tamiyo Compleated Sage, Tamiyo Field Researcher, Teferi Hero of Dominaria, Teferi Time Raveler, Teferi Who Slows the Sunset, Ugin the Spirit Dragon, Veil of Summer, Vraska Betrayal's Sting.

Boa contagem, mas quase toda concentrada em planeswalkers (a maioria via +1 "olhe as 2 de cima, uma pra mão"), não em draw incondicional de criatura/enchantment — se os planeswalkers forem removidos rápido, o motor de draw esvazia junto. Rhystic Study é a única fonte de draw realmente incondicional e recorrente da lista.

---

## 5. Remoção e interação

| Tipo | Cartas | Qtde |
|---|---|---|
| Remoção pontual | Anguished Unmaking, Damn, Kaya Intangible Slayer, Nicol Bolas Dragon-God, Path to Exile, Swords to Plowshares, Tamiyo Compleated Sage, Teferi Hero of Dominaria, Ugin the Spirit Dragon, Void Rend | 10 |
| Wipe | Blasphemous Act, Elspeth Sun's Champion, Farewell, Liliana Dreadhorde General, Supreme Verdict, The Eternal Wanderer, Toxic Deluge | 7 |
| Counterspell | Counterspell, Dovin's Veto, Mana Drain, Swan Song | 4 |

**Total: 21 efeitos de interação** — bem acima da faixa recomendada de 8-10 remoção pontual + 3-5 wipes (`SKILL.md`), mesmo considerando que várias dessas cartas são multifuncionais (Nicol Bolas Dragon-God, Ugin, Tamiyo Compleated Sage também geram vantagem de carta, não são "só" remoção). Deck de perfil claramente controlador — controle 5 cores com muito mais interação que o Thranduil (que tinha só 8-10 depois da rebalanceada).

---

## 6. Sinergia de contadores/proliferate — pacote real, confirmado no EDHREC

Varredura de `oracle_text` (termo "proliferate" + termos de "dobrar contador") encontra **12 cartas** de um pacote de contadores coeso, não é um punhado de goodstuff solto:

**Motores de proliferate:** Evolution Sage, Flux Channeler, Ichormoon Gauntlet, Inexorable Tide, Mutational Advantage, Ripples of Potential, Vraska Betrayal's Sting, Atraxa Praetors' Voice.
**Dobradores de contador:** Doubling Season, Vorinclex Monstrous Raider, Deepglow Skate, All Will Be One.

Confirmado com dado real do EDHREC (`json.edhrec.com/pages/commanders/esika-god-of-the-tree.json`, campo `synergy` de cada carta — positivo = joga mais nesse comandante especificamente do que em média geral, não é só popularidade):

| Carta | Inclusão em decks de Esika | Synergy score |
|---|---|---|
| Nicol Bolas, Dragon-God | 27,3% | **+0,241** |
| Vorinclex, Monstrous Raider | 19,1% | **+0,172** |
| Ichormoon Gauntlet | 17,7% | **+0,164** |
| Atraxa, Praetors' Voice | 18,0% | **+0,153** |
| Deepglow Skate | 15,0% | **+0,137** |
| Doubling Season | 19,1% | **+0,131** |

Todos com synergy score positivo e significativo — não é sinergia inventada, é o padrão real de decks desse comandante no EDHREC. A ligação mecânica faz sentido: The Prismatic Bridge (verso do comandante) põe permanentes direto do topo da biblioteca a cada upkeep sem pagar custo, então quanto mais rápido as peças de counters/proliferate entrarem em jogo (por essa via gratuita ou por conjuração normal), mais rápido o pacote de contadores (incluindo os +1/+1 dos próprios planeswalkers via lealdade, e o Ichormoon Gauntlet puxando pro extra-turn ultimate) fica online.

---

## 7. Win conditions

Não tem 1 finisher único claro — o plano de vitória é atrito de vantagem de carta (planeswalkers) + o pacote de contadores fechando com Ichormoon Gauntlet (ver seção 10, extra turn via ultimate `[-12]` de planeswalker equipado, acelerado pelo pacote de proliferate) ou dano incremental via Nicol Bolas Dragon-God/Ugin. Elspeth Sun's Champion e Liliana Dreadhorde General geram board wide (tokens/exército) que também fecham jogo por combate depois de estabilizar via wipes.

Vraska, Betrayal's Sting merece nota: ultimate `-9` transforma um permanente em terreno que produz mana de qualquer cor igual ao seu poder — ramp/fixação de fechamento, não dano direto.

---

## 8. Sinergia com o comandante (Esika / Prismatic Bridge)

- **Esika, God of the Tree** (frente, `{1}{G}{G}`): dá vigilance + `{T}: Add one mana of any color` a TODAS as lendárias que você controla. O deck tem uma densidade alta de lendárias (praticamente todos os planeswalkers contam, mais Aminatou, Arena Rector, Carth the Lion, Tamiyo x2, Vorinclex, Atraxa, Nicol Bolas, Vraska x1) — cada uma vira uma fonte extra de fixação de mana quando Esika está em campo, o que ajuda a compensar a contagem baixa de ramp dedicado (seção 3).
- **The Prismatic Bridge** (verso, `{W}{U}{B}{R}{G}`): a cada upkeep, revela do topo até achar criatura ou planeswalker, põe em campo de graça. Motor de vantagem de material puro, sem seletividade — favorece mainboard com densidade alta de criaturas/planeswalkers.

**Achado real (contagem exata via `type_line` das 99 cartas, não a média do EDHREC):** este deck tem **11 criaturas e 17 planeswalkers** — o INVERSO da distribuição média de decks de Esika no EDHREC (24 criaturas / 6 planeswalkers, seção "Average Type Distribution" do `container.json_dict`). **Confirmado pelo usuário como intencional (2026-08-21):** o plano do deck é jogar planeswalkers de graça pela Bridge, proteger a Bridge, e tentar conjurá-la no end step do oponente logo antes do próprio turno pra já garantir 1 gatilho de upkeep. A proporção alta de planeswalkers não é um desvio a corrigir — é o motor central do deck.
- Interação com o pacote de contadores (seção 6): qualquer planeswalker que a Bridge coloque em jogo de graça já entra "pronto" pra crescer de lealdade mais rápido com o pacote de proliferate — reforça o plano principal em vez de ser um tema paralelo.

### Plano de jogo confirmado: flashar a Bridge no end step do oponente

**Viável com as peças reais do deck** — verificado via `oracle_text`, não é premissa:

- **Alchemist's Refuge** (`{G}{U}, {T}: You may cast spells this turn as though they had flash`) e **Emergence Zone** (`{1}, {T}, Sacrifice this land: You may cast spells this turn as though they had flash`) — os 2 habilitadores de flash do deck. Sem eles, The Prismatic Bridge (Legendary Enchantment, sem flash própria) só pode ser conjurada em velocidade sorcery na sua própria main phase — a linha "end step do oponente" depende de ter 1 desses 2 em campo.
- Isso é uma janela estreita: só 2 cartas em 99 habilitam a linha. Vale considerar se mais fontes de flash (ex: Vedalken Orrery, outro efeito genérico de "spells as though flash") melhorariam a consistência do plano principal do deck — ainda não testei isso num goldfish.

**Correção de mana (2026-08-21, apontada pelo usuário):** meu goldfish inicial modelava a linha de flash com mana sempre disponível, ignorando que o untap step só destapa os permanentes do jogador ativo (CR 500.1) — meus terrenos ficam tapados do jeito que ficaram no MEU último turno durante os turnos alheios. Corrigido (`prismatic_bridge_goldfish_v1.py`, campo `mana_held_back`). Resultado: a taxa de flash-cast caiu de 3,7% pra **0,0%** em n=5000 — não é só um ajuste, é estrutural: como a Bridge está sempre "disponível" no modelo (vem da zona de comando), a IA gananciosa sempre a conjura normal assim que fica pagável, e isso sempre acontece ANTES de acumular mana suficiente pra flashar (que custa mais).

**Política "hold-for-flash" implementada e testada (2026-08-21):** modelei o jogador segurando a Bridge de propósito quando um habilitador já está em campo, mesmo já podendo conjurar normal, especificamente pra tentar flashar depois. **Resultado: essa política piora o desempenho geral, não melhora.** n=5000: a linha de flash passa a ativar em 9,4% das partidas e a remoção média cai (0,78→0,69 — a proteção funciona), mas o custo é maior que o ganho — Bridge nunca conjurada em 8 turnos sobe de 14,1% pra 21,5%, gatilhos totais caem de 1,96 pra 1,73, e a taxa de acerto de planeswalker cai uns 4-5 pontos em T6/T7/T8. Motivo: o limiar de mana pra flashar é sempre maior que pra conjurar normal, então esperar por essa condição atrasa (ou às vezes impede) a entrada da Bridge em campo mais do que compensa a segurança ganha. **Conclusão prática: não vale segurar a Bridge de propósito pra tentar flashar — o certo é conjurar assim que fica pagável (comportamento padrão do simulador) e só aproveitar a linha de flash nos casos em que ela coincide naturalmente.** Ver `goldfish-log.md` pra a tabela completa.

### Proteção da Bridge — o que já existe

- **Sterling Grove** (`Other enchantments you control have shroud`) — proteção direta e incondicional, a Bridge fica intargetável assim que Sterling Grove está em campo.
- **Counterspell, Dovin's Veto, Mana Drain, Swan Song** (seção 5) — proteção reativa: contra-atacam remoção/exile mirada na Bridge antes de resolver.
- **Não encontrei** proteção dedicada adicional pra permanentes não-criatura além dessas (ex: nenhum "hexproof genérico pra encantamentos" fora do Sterling Grove). Se Sterling Grove for removido/nunca chegar, a Bridge fica exposta só à proteção reativa dos counterspells.

**Testado com goldfish dedicado (`prismatic_bridge_goldfish_v1.py`, n=2000, 3 taxas de remoção assumidas — ver `goldfish-log.md`): incluir Greater Auramancy (2º shroud-granter) melhora a sobrevivência da Bridge em menos de 1,5 ponto percentual, em qualquer cenário testado.** Não é porque shroud não empilha (isso já era esperado) — é porque **só 14,7% das partidas chegam a ter Sterling Grove em campo em 10 turnos, e só 2,4% chegam a ter os dois protetores em campo** (mesmo com Greater Auramancy no deck). A redundância só importa nesses 2,4% dos jogos. O gargalo real é a baixa taxa de conseguir sequer 1 protetor em campo, não a falta de um segundo. **Não recomendo Greater Auramancy pra esse objetivo específico.**

**Testado também: Enlightened Tutor** (`{W}`, `Search your library for an artifact or enchantment card... put that card on top`) no lugar de Greater Auramancy. Resultado misto:
- **Melhora bem a taxa de conseguir Sterling Grove em campo: 14,7% → 24,3%** (+9,6pp, ~65% de aumento relativo) — ataca o problema real de acesso, diferente do Greater Auramancy.
- **Mas isso não vira sobrevivência maior da Bridge no fim da partida** (63,3% → 63,2%, Bridge removida 1,18 → 1,14 — mesma ordem de grandeza do Greater Auramancy). Motivo: Sterling Grove continua sendo 1 único ponto de falha (não se protege a si mesmo) e Enlightened Tutor é singleton — depois que o Sterling Grove morre, não tem como buscar de novo. O tutor resolve "conseguir a proteção mais cedo/mais vezes", não "a proteção persistir depois que cai".

**Testado também: Hall of Heliod's Generosity** (Legendary Land, `{1}{W}, {T}: Put target enchantment card from your graveyard on top of your library`) — recursão repetível, diferente do Enlightened Tutor (spell singleton, uso único). Testado em 10 E 16 turnos (pra dar tempo da cadeia completa: Sterling Grove morrer → Hall em campo → mana disponível → recursão → compra → recast). **Efeito também praticamente zero, em qualquer horizonte:**

| Métrica | Baseline 10t | + Hall 10t | Baseline 16t | + Hall 16t |
|---|---|---|---|---|
| Sterling Grove em campo | 15,1% | 15,1% | 21,1% | 21,1% (idêntico) |
| Bridge em campo no fim | 63,3% | 63,1% | 69,8% | 70,0% |
| Bridge removida (média) | 1,18 | 1,17 | 2,44 | 2,42 |

Instrumentado: só 48 eventos de recursão em 2000 partidas (2,4%) em 10 turnos — Hall of Heliod's Generosity é 1 carta em 37 terrenos (~2,7% de densidade), só ativa se Sterling Grove já morreu E ela já está em campo E sobra mana. Cadeia de baixa probabilidade que raramente se completa mesmo com mais turnos.

**(Nota técnica: essa iteração corrigiu um bug real no simulador — a rodada de remoção fazia a carta "sumir" do jogo sem passar pelo cemitério, o que teria feito a recursão nunca encontrar o alvo. Corrigido em `resolve_removal_round`.)**

**Conclusão consolidada das 3 opções testadas (Greater Auramancy, Enlightened Tutor, Hall of Heliod's Generosity): nenhuma resolve o problema de forma perceptível.** O motivo é o mesmo nas três — é um deck de 99 cartas singleton com **1 única** peça de proteção dedicada (Sterling Grove) competindo por espaço de compra com as outras 96 cartas; qualquer solução de 1 carta adicional ainda precisa primeiro ser puxada, o que já é raro em 10-16 turnos. Não há uma troca de carta única que resolva isso de forma decisiva — a alternativa realista é aceitar que proteção robusta contra remoção pontual não é o forte desse build (os counterspells da seção 5 seguem sendo a defesa mais confiável), ou investir em várias peças simultaneamente em vez de uma só.

### Achado adicional: Paradox Haze pode dobrar o gatilho de upkeep da Bridge

`Paradox Haze` (Aura, `Enchant player` — `At the beginning of enchanted player's first upkeep each turn, that player gets an additional upkeep step after this step`): se encantar o PRÓPRIO jogador, gera um segundo upkeep todo turno — e a Bridge (`At the beginning of your upkeep...`) dispararia **duas vezes por turno**, não uma. Isso não estava registrado na varredura anterior porque a regex de sinergia procurava por "proliferate"/"+1/+1 counter", não por "additional upkeep" — é uma peça de sinergia direta com o motor central do comandante que passou batido na primeira varredura. Vale considerar isso um achado de alta prioridade pra reavaliação de prioridade de cast em jogo.

---

## 9. Game Changers — contagem oficial

Cruzamento carta a carta contra a lista de 53 Game Changers obtida via `https://api.scryfall.com/cards/search?q=is:gamechanger` em 2026-08-20:

**3 Game Changers: Farewell, Narset Parter of Veils, Rhystic Study.**

Isso é exatamente o teto do Bracket 3 (até 3 Game Changers, por `references/commander-rules.md#brackets`).

---

## 10. Estruturas restritas pelo sistema de Brackets

Varredura de `oracle_text` de todas as 100 cartas procurando por combo de 2 peças, negação de terras em massa, e turnos extras.

- **Negação de terras em massa:** não encontrado nenhum efeito do tipo "destroy all lands"/"sacrifice all lands" no texto de nenhuma carta.
- **Turnos extras:** encontrado em **Ichormoon Gauntlet** — texto (Scryfall): *"Planeswalkers you control have '[0]: Proliferate' and '[−12]: Take an extra turn after this one.'"* — habilidade de turno extra condicionada a um planeswalker equipado chegar a -12 de lealdade. Não é um efeito "livre"/repetível de turno extra por si só, mas é uma fonte real de turno extra presente na lista. Com o pacote de proliferate do deck (Inexorable Tide, Deepglow Skate, Evolution Sage — todos conferidos por `oracle_text`), a lealdade pode subir mais rápido que o normal.
- **Combo de 2 peças:** não identifiquei nenhum via varredura de texto (procurei por padrões de untap/copy livre e "infinite"-adjacentes nas 100 cartas). Isso não é uma prova formal de ausência de combo — só que não achei um usando os padrões de busca que apliquei.

---

## 11. Classificação de Bracket

**Bracket 3 (Upgraded), no teto de Game Changers (3 de 3), com ressalva.**

Base formal: 3 Game Changers (seção 9), sem negação de terras em massa, sem combo de 2 peças identificado. O Ichormoon Gauntlet dá acesso a turno extra, mas não da forma "encadiada" que o texto oficial da Wizards usa como critério de exclusão de Bracket 3 (fonte: `references/commander-rules.md#brackets`, que reproduz o texto oficial "turnos extras... não encadeado" pra Bracket 3) — é uma ultimate de planeswalker específico, não um motor repetível independente.

**Ressalva pós-varredura completa (seções 3-8):** 21 efeitos de interação (seção 5) e um pacote de contadores/proliferate com synergy score real confirmado no EDHREC (seção 6, até +0,241) empurram o deck bem além do "goodstuff Upgraded" comum de Bracket 3 em termos de qualidade de carta individual — mesmo sem violar nenhum critério estrutural formal dos Brackets. O teto de 3 Game Changers é o critério oficial decisivo, então a classificação formal continua Bracket 3, mas é um Bracket 3 forte, próximo do 4 em qualidade de peça (mesma leitura já registrada informalmente pra outros decks desse usuário — ver `references/user-standing-rules.md`).

---

## Links

- EDHREC: https://edhrec.com/commanders/esika-god-of-the-tree
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger

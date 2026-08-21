# Auditoria — Kutzil, Malamet Exemplar (Selesnya — G/W)

Auditoria feita via skill `mtg-commander`, dados em tempo real do Scryfall (inclusive as cartas de crossover/Universes Beyond, todas conferidas uma a uma).
Data: 2026-08-20

---

## 1. Validação formal

| Check | Resultado |
|---|---|
| Total de cartas | **100** (99 + comandante) ✅ |
| Singleton | ✅ nenhuma duplicata |
| Identidade de cor (G/W) | ✅ nenhuma violação — inclusive as cartas de Avatar, TMNT, Sonic, FF, GoT, LOTR, 40k etc. estão todas dentro da identidade |
| Cartas banidas em Commander | ✅ nenhuma |
| Erros de grafia/cartas não encontradas | ✅ nenhuma (MDFCs como Branchloft Pathway, Kabira Takedown, Witch Enchanter todas resolvidas corretamente) |

**Comandante:** Kutzil, Malamet Exemplar — `{1}{G}{W}` — Legendary Creature Cat Warrior.
Seus oponentes não podem conjurar mágicas no seu turno; sempre que uma ou mais criaturas com poder maior que o base causam dano de combate a um jogador, você compra uma carta.

---

## 2. Base de mana

- **Terrenos: 32** — abaixo do ideal (36-38). **Porém**, isso é compensado por dois fatores fortes:
  1. **7 mana dorks/rocks de 1-2 mana** (Avacyn's Pilgrim, Birds of Paradise, Fyndhorn Elves, Llanowar Elves, Delighted Halfling, Biophagus, Sol Ring) — funcionam como "terrenos extras" na prática.
  2. **Qualidade de fixação excepcional**: 8 duais verdadeiros G/W (Bountiful Promenade, Brushland, Canopy Vista, Fortified Village, Horizon Canopy, Overgrown Farmland, Sunpetal Grove, Temple Garden) + Branchloft Pathway + Command Tower + Exotic Orchard + Windswept Heath (busca Forest ou Plains). Quase todo terreno não-básico produz as duas cores.
- Mesmo assim, **32 é genuinamente baixo** para Bracket 3 — a curva do deck é excepcionalmente baixa (CMC médio 2.54, ver abaixo), o que ajuda, mas ainda recomendo **34-35 terrenos** como alvo mais seguro contra mãos sem dork verde na abertura.
- Pips: G=54, W=31 — verde é claramente a cor primária (a maioria dos enablers de contador é verde), branco entra como o pacote de remoção/proteção/draw. A base de mana reflete bem essa proporção.

---

## 3. Curva de mana

CMC médio (sem terrenos, sem comandante): **2.54** — excepcionalmente baixo, bem abaixo do "ideal" genérico de 2.5-3.5, mas isso é uma escolha de design correta pra esse arquétipo (contadores agressivo).

| CMC | Qtde |
|---|---|
| 0 | 2 |
| 1 | 18 |
| 2 | 17 |
| 3 | 16 |
| 4 | 9 |
| 5 | 2 |
| 7 | 1 |
| 8 | 1 (Craterhoof Behemoth) |
| 9 | 1 (The Great Henge — custo nominal, reduz pelo maior poder em campo) |

Curva agressiva e consistente — 37 das 67 cartas não-terreno custam 1-2 mana. Isso justifica plenamente rodar menos terrenos que o padrão.

---

## 4. Ramp — ~13 peças, mais que suficiente

Mana direto: Avacyn's Pilgrim, Birds of Paradise, Fyndhorn Elves, Llanowar Elves, Delighted Halfling, Biophagus, Sol Ring (7)
Ramp de terreno: Summon: Fenrir (capítulo I), Kodama of the West Tree (busca por dano de combate de criatura modificada), The Earth King (busca ao atacar com poder 4+) (3)
Ramp/redução indireta: Selvala Heart of the Wilds, Rishkar Peema Renegade (dá mana a criaturas com contador), The Earth Crystal (reduz custo verde) (3)

Volume adequado — não excessivo como no Beorn, bem calibrado pro que o deck precisa.

---

## 5. Card draw — ~9 fontes, muito bem conectadas ao tema

- **Mikey & Leo, Chaos & Order** — compra ao colocar QUALQUER contador (1x por turno) — com a quantidade de contadores que esse deck distribui, é praticamente draw todo turno.
- **Terrasymbiosis** — compra uma carta POR contador colocado (1x por turno) — combinado com Ouroboroid/Ornery Tumblewagg/Rishkar, pode ser burst de várias cartas de uma vez.
- **Esper Sentinel** — taxa/compra contra spells não-criatura do oponente, um dos melhores 1-drops de valor do formato.
- **Beast Whisperer**, **The Great Henge**, **Selvala** (condicional), **Kutzil** (o próprio comandante, via dano de combate de criaturas buffadas).

Esse é o ponto mais forte do deck: o draw não é "genérico", ele está costurado diretamente no mecanismo central (colocar contadores), então mais sinergia = mais cartas, criando um loop de valor autossustentável.

---

## 6. Remoção — 🟢 o melhor dos 3 decks auditados até agora

| Carta | Função |
|---|---|
| Path to Exile | Exílio de criatura, instantâneo |
| Swords to Plowshares | Exílio de criatura, instantâneo |
| Damning Verdict | **Destrói todas as criaturas SEM contador** — como o board deste deck vive coberto de contadores, isso tende a ser um wrath quase uma via só contra o oponente |
| Knight of Autumn | Modal — destrói artefato/encantamento, ou +2 contadores, ou vida |
| Hopeful Initiate | Remove 2 contadores: destrói artefato/encantamento |
| Requisition Raid | Modal (Spree) — destrói artefato E/OU encantamento |
| Witch Enchanter // Witch-Blessed Meadow | ETB destrói artefato/encantamento (E ainda pode ser jogada como terreno) |
| Wakka, Devoted Guardian | Destrói artefato ao causar dano de combate |
| District Mascot | Remove contadores: destrói artefato |
| Galadriel's Dismissal / Clever Concealment | Phase out (pseudo-remoção/proteção temporal) |

**Total: 11 efeitos de remoção/interação**, incluindo 2 exilos premium, um wrath assimétrico muito forte pro seu próprio plano de jogo, e SEIS respostas diferentes pra artefato/encantamento (isso é redundante — dá pra cortar 1-2 sem perder cobertura). Não há remoção dedicada de planeswalker, mas é um gap menor dado o volume geral.

---

## 7. Proteção — excelente, com uma inclusão de elite

- **Teferi's Protection** — uma das melhores cartas de proteção/reset do formato inteiro.
- **Mother of Runes**, **Swiftfoot Boots**, **Dauntless Escort**, **Akroma's Will** (modo indestructible+proteção), **Delighted Halfling** (protege spells lendários de contramágica).

---

## 8. Win conditions

- **Craterhoof Behemoth** — finalizador clássico.
- **Akroma's Will** — modo de voo+vigilância+double strike pra alpha strike com o board cheio de criaturas grandes.
- **Ouroboroid** e **Ornery Tumblewagg** — explodem contadores pelo board (o segundo literalmente dobra os contadores de uma criatura via saddle).
- **Kutzil** (o comandante) — não é um wincon per se, mas transforma toda vitória em combate em compra de carta, criando pressão de recursos junto com dano.

O plano de vitória é claro: empilhar contadores com os multiplicadores (ver seção 9), dar trample (Duskshell Crawler, Sphere Grid, Kodama, Rancor), e vencer por combate — não depende de um combo de 2 peças, mas escala de forma muito consistente turno a turno.

---

## 9. Sinergia com o tema de +1/+1 counters — 🟢 construção de altíssima qualidade

Esse é o deck mais coeso dos três que já auditamos. A cadeia é clara:

**Multiplicadores de contador (empilham entre si):**
- Hardened Scales (+1)
- Michelangelo, Weirdness to 11 (+1)
- Branching Evolution (dobra)
- The Earth Crystal (dobra)
- Innkeeper's Talent nível 3 (dobra)
- Ozolith, the Shattered Spire (+1, e também guarda contadores de criaturas que morrem)

Com 2-3 desses simultâneos em campo, um único gatilho de "coloque um contador" (Luminarch Aspirant, Urdnan, Rishkar, etc.) pode virar 4-6 contadores de uma vez.

**Geradores de contador em massa:**
- Ouroboroid, Railway Brawler, Ornery Tumblewagg, Maester Seymour — todos colocam contadores em MÚLTIPLAS criaturas ou em quantidade escalável.

**Payoffs que convertem contador em recurso:**
- Mikey & Leo / Terrasymbiosis → compra
- Kutzil → compra por combate
- Sphere Grid / Duskshell Crawler / Kodama / Training Regimen → trample (garantindo que o dano conecte)
- Urdnan → first strike/double strike condicional a ter contadores
- The Ozolith → preserva o investimento mesmo se a criatura morrer

Não é apenas "tribal de contador" — é um motor fechado onde cada peça reforça as outras. Isso também explica por que a remoção é tão boa aqui: Damning Verdict é literalmente desenhada para esse deck específico.

---

## 10. Cruzamento com os goldfishes (10 testes registrados em `goldfish-log.md`)

Reauditoria feita depois do compilado de goldfishes que você trouxe. Nem todo teste tem dado recuperável (#1-4 são `DADOS_INCOMPLETOS`, #5 e #9 são `DADOS_PARCIAIS`), mas os 6 testes completos (#6, #7, #8, o teste v8, #10, e as observações de #5/#9) dão sinal real sobre como as previsões da auditoria se comportam na mesa.

| Achado da auditoria (teórico) | O que os goldfishes confirmaram |
|---|---|
| Curva baixíssima (CMC médio 2.54) deveria compensar os 32 terrenos | ✅ Confirmado na prática: Kutzil resolveu no T2 em 2 dos 5 testes completos (#7, teste v8) e no T3 nos outros 3 (#6, #8, #10) — consistente com dork T1 → Kutzil T2/T3, exatamente o padrão que a auditoria previu |
| Motor de contadores multiplicativo é "genuinamente explosivo" | ✅✅ Confirmado com folga: no teste v8, **Ornery Tumblewagg terminou com 22 counters +1/+1** numa única sequência. No #8, o próprio piloto identificou a entrada do **The Earth Crystal** como o pico de explosividade mais alto observado até então — bate exatamente com o que a auditoria apontou como a peça-chave de multiplicação (seção 9) |
| Teferi's Protection como proteção de elite | ✅ Confirmado: no #7 ela ficou disponível na mão e só foi usada no momento certo (T6), validando que o deck consegue *segurar* a resposta em vez de precisar gastá-la cedo |
| Damning Verdict / Clever Concealment como respostas disponíveis | ⚠️ Parcial: apareceram na mão do teste v8 como opção disponível, mas — como em qualquer goldfish — **nunca foram testadas contra uma ameaça real**, porque não há oponente simulando board. Mesma limitação que já tínhamos apontado nos decks do Beorn e do Thranduil: a auditoria de remoção continua sendo teórica até rodar numa mesa de verdade |
| 32 terrenos é "genuinamente baixo" | ⚠️ Parcialmente estressado: o **Goldfish #10** foi um teste proposital de mão com 0 fontes verdes — e **todos os 6 mana dorks do deck custam `{G}`** (Avacyn's Pilgrim, Birds of Paradise, Fyndhorn Elves, Llanowar Elves, Delighted Halfling, Biophagus). Ou seja, sem uma fonte verde inicial, a rampa inteira trava. O teste se recuperou (Forest no draw do T2), mas o próprio piloto documentou isso como "não deve ser interpretado como uma mão sem verde é segura" — o risco é real, só não se materializou dessa vez |

**Achado novo que a auditoria original não previu:** o **Fight Rigging**, presente nos testes pré-v8/v8 mas **cortado da lista atual**, foi responsável por duas das linhas mais explosivas registradas — soltar Esper Sentinel de graça (#6) e soltar Michelangelo de graça com Kutzil em poder 7 (teste v8). Isso significa que a versão atual do deck **perdeu uma fonte real de spells gratuitos** que os próprios goldfishes comprovaram funcionar bem. Vale reconsiderar (ver sugestão 4 abaixo).

**Achado prático, não de deck:** em pelo menos 2 testes (#6, #7) você mesmo relatou ter se confundido na contagem de counters. Isso não é falha do deck, mas reforça que esse arquétipo (múltiplos multiplicadores + múltiplos gatilhos simultâneos) exige tracking rigoroso numa mesa real — vale considerar dados/contadores físicos dedicados ou um app de life/counter tracking em vez de só decorar os números.

---

## 11. Estimativa de Bracket

**Bracket 3, com tendência a 3.5.** (mantida após cruzar com os goldfishes — se algo, os testes reforçam o "tendência a 3.5": a explosividade real observada, como os 22 counters do Ornery Tumblewagg, é mais alta do que a leitura só da lista sugeria.)

A favor: Sol Ring, Teferi's Protection, Esper Sentinel, motor de contadores multiplicativo genuinamente explosivo (agora confirmado em jogo, não só na lista), remoção de altíssima qualidade (Path/Swords/Damning Verdict).
Contra bracket 4/cEDH puro: sem fast mana além do Sol Ring, sem tutores (nenhum no deck), e sem combo de 2 peças de vitória instantânea — o plano é "montar o motor e vencer por combate", que é poderoso mas não da velocidade turno 3-4 de cEDH.

Esse é, dos três decks que auditamos, o que tem **construção mais coesa e menos buracos estruturais** — Thranduil tinha gap de remoção, Beorn tinha gap de remoção ainda maior; Kutzil já vem com remoção de sobra e um motor de sinergia muito bem fechado, e os goldfishes confirmam que esse motor liga de forma consistente (T2-T3 em 5 de 5 testes completos).

---

## 12. Sugestões de melhoria (prioridade)

1. **Considerar +2-3 terrenos** (32→34-35), **priorizando fontes verdes** — o Goldfish #10 mostrou que uma mão sem verde trava literalmente todos os 6 dorks do deck (todos custam `{G}`), então qualquer terreno adicional deveria puxar a balança de G:W (hoje ~20:18 nas fontes de terreno) ainda mais pro G, ou incluir mais um dork/rock que não dependa de G para ativar (ex: Arcane Signet).
2. **Cortar 1 das 6 respostas de artefato/encantamento** — Requisition Raid ou Witch Enchanter cobrem a categoria com mais eficiência que District Mascot.
3. Opcional: um tutor de criatura barato (**Eladamri's Call**) ajudaria a achar Craterhoof ou um multiplicador de contador no momento certo, aumentando a consistência sem mudar o plano de jogo.
4. **Novo, baseado nos goldfishes:** considerar reintroduzir **Fight Rigging** no lugar de uma das remoções redundantes de artefato/encantamento (item 2). Os próprios testes comprovaram que ele gera valor real (spells grátis via hideaway quando Kutzil está grande) — foi cortado numa versão anterior, mas os dados de goldfish sugerem que essa troca pode ter sido prematura.
5. O deck já está muito bem calibrado — não force mudanças estruturais grandes; os ajustes aqui são de polimento, não de reparo.

---

## Links

- EDHREC: https://edhrec.com/commanders/kutzil-malamet-exemplar
- Tema Counters: https://edhrec.com/themes/counters
- Moxfield (criar/comparar): https://moxfield.com/decks/new

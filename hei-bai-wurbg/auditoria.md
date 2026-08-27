# Auditoria — Hei Bai, Forest Guardian (5 cores — WUBRG)

Auditoria feita via skill `mtg-commander`, dados em tempo real do Scryfall.
Data: 2026-08-20

---

## 1. Validação formal

| Check | Resultado |
|---|---|
| Total de cartas | **100** (99 + comandante) ✅ |
| Singleton | ✅ nenhuma duplicata |
| Identidade de cor (5 cores) | ✅ nenhuma violação |
| Cartas banidas em Commander | ✅ nenhuma |
| Erros de grafia/cartas não encontradas | ✅ nenhuma |

**Comandante:** Hei Bai, Forest Guardian — `{3}{G}` — Legendary Creature Bear Spirit.
Ao entrar, revela até achar uma **Shrine** e pode colocá-la em jogo direto. Habilidade ativada de 5 cores cria Spirits para cada encantamento lendário que você controla.

Esse comandante deixa claro o plano do deck antes mesmo de olhar o resto da lista: **Shrine tribal** (o subtipo de encantamento "Shrine", introduzido em Kamigawa e expandido em sets crossover) com um pacote de Enchantress por cima.

---

## 2. Um deck genuinamente Shrine tribal — 17 Shrines na lista

Confirmado carta a carta no Scryfall: todos os 12 "Sanctum/Honden/Temple/Plaza/Oasis" **e** os 5 "Go-Shintai" são `Legendary Enchantment — Shrine` (ou `Legendary Enchantment Creature — Shrine`). Ou seja, o deck roda **17 Shrines**, cada uma escalando com "quantas Shrines você controla":

- **Drain:** Northern Air Temple, Sanctum of Stone Fangs
- **Draw:** Honden of Seeing Winds, Sanctum of Calm Waters, The Spirit Oasis
- **Tokens:** Honden of Life's Web, Southern Air Temple (+1/+1 counters), Crescent Island Temple, Go-Shintai of Shared Purpose
- **Ramp:** Sanctum of Fruitful Harvest, Kyoshi Island Plaza
- **Remoção/dano:** Sanctum of Shattered Heights, Go-Shintai of Hidden Cruelty, Go-Shintai of Ancient Wars
- **Recursão/utilidade:** Sanctum of All (busca outra Shrine todo turno — motor puxando motor), Go-Shintai of Life's Origin (recorre encantamento + cria token Shrine)

> **Correção (2026-08-24, conferida ao vivo no Scryfall):** Sanctum of All tem uma SEGUNDA habilidade que faltava aqui — oráculo real: *"If a triggered ability of another Shrine you control triggers **while you control six or more Shrines**, that ability triggers an additional time."* É um dobrador de gatilho de Shrine condicional (6+ Shrines em campo), não só o tutor. Empilha com a Elesh Norn (dobra incondicional de qualquer ETB): com as duas em campo e 6+ Shrines, um gatilho de ETB de Shrine (ex: o "compre 1" do Spirit Oasis, o dreno da Northern Air Temple) dispara **3 vezes** — 1 original + Elesh Norn + Sanctum of All. Reforça a leitura de "motor que se realimenta" da seção 6/9, com um multiplicador concreto que faltava. Nota lateral: a dobra da Annie Joins Up ("legendary creature you control") só vale pros 5 Go-Shintai (`Enchantment Creature`), não pelas outras 12 Shrines (só `Enchantment`).

Isso não é um monte de encantamentos aleatórios — é um tribal de verdade em torno de um subtipo raro, com o comandante desenhado especificamente pra buscar a primeira peça (ETB) e depois amplificar todas elas (habilidade ativada conta encantamentos lendários, e virtualmente toda Shrine aqui é lendária).

---

## 3. Base de mana — a melhor das 4 que já auditamos

- **Terrenos: 35** (dentro do ideal 36-38, levemente abaixo mas com fixação impecável).
- **9 dos 10 duais originais (ABUR)**: Badlands, Bayou, Plateau, Savannah, Scrubland, Taiga, Tropical Island, Tundra, Underground Sea — falta só Volcanic Island. Mana base premium, sem dano nem condição pra entrar destravada.
- **7 fetchlands**: Arid Mesa, Bloodstained Mire, Flooded Strand, Marsh Flats, Misty Rainforest, Scalding Tarn, Verdant Catacombs, Windswept Heath — buscam os duais acima sem tapped.
- **2 Triomes** (Indatha, Ketria) cobrindo 3 cores cada, Command Tower, City of Brass, Abandoned Air Temple, Yavimaya Cradle of Growth (torna todo terreno também Forest).
- Curva bem distribuída (CMC médio 2.94) e o deck praticamente não tem tapland problemático fora dos Triomes.

Nada a corrigir aqui — é uma das bases de mana mais bem construídas que já vi em auditoria, condizente com o investimento (esses duais + fetches são as cartas mais caras do deck de longe).

---

## 4. Curva de mana

CMC médio (sem terrenos, sem Shrines, sem comandante): **2.94** — dentro do ideal.

| CMC | Qtde |
|---|---|
| 1 | 8 |
| 2 | 22 |
| 3 | 11 |
| 4 | 14 |
| 5 | 7 |
| 6 | 2 |

Pico saudável em CMC 2, sem topo pesado — a maior parte do "custo alto" do deck vem das próprias Shrines (que ficam mais baratas em valor conforme entram outras), não de bombas isoladas de 7+.

---

## 5. Ramp — ~14 peças, muito acima do mínimo

Birds of Paradise, Bloom Tender, Sol Ring, Arcane Signet, The Mind Stone, Cultivate, Farseek, Nature's Lore, Three Visits, Sanctum of Fruitful Harvest, Kyoshi Island Plaza, Sanctum Weaver, Herald of the Pantheon (redução de custo), Enduring Vitality (dá "T: add any color" pra todas as suas criaturas).

Volume alto, mas justificado: um deck de 5 cores com curva de encantamentos precisa de mana abundante e fixação redundante.

---

## 6. Card draw — 🟢 provavelmente o motor mais forte que já auditamos

- **Argothian Enchantress**, **Enchantress's Presence**, **Sythis, Harvest's Hand** — as três compram ao conjurar QUALQUER encantamento. Como o deck tem 17 Shrines + mais ~15 outros encantamentos, **cada uma dessas três pode disparar dezenas de vezes por partida**, e as três empilham simultaneamente na mesma mágica.
- **Honden of Seeing Winds** e **Sanctum of Calm Waters** compram uma quantidade igual ao número de Shrines, TODO turno (upkeep/main phase) — com o board desenvolvido, isso é comprar 5-10+ cartas por turno sozinho.
- **The Spirit Oasis** compra ao entrar E a cada nova Shrine que entra depois.

Isso é um motor de vantagem de cartas que se realimenta: mais Shrines → mais draw por Shrine → mais Shrines na mão pra jogar. Genuinamente do nível de poder mais alto que vimos nos 4 decks.

---

## 7. Remoção/Interação — 🟢 também o melhor conjunto que já auditamos

| Carta | Função |
|---|---|
| Path to Exile, Swords to Plowshares | Exílio de criatura premium |
| An Offer You Can't Refuse | Contramágica não-criatura (paga vida = CMC do oponente) |
| Arcane Denial, Dovin's Veto | Contramágica dura (Dovin's Veto não pode ser contra-contrado) |
| Swan Song | Contramágica de encantamento/instantâneo/sorcery — ótima contra outra remoção ou outro deck de encantamento |
| Aura Shards | Remoção repetível grátis: "whenever a creature you control enters, you may destroy target artifact or enchantment" — com o volume de token deste deck (Honden of Life's Web, Go-Shintai of Shared Purpose, Crescent Island Temple, o ativado da própria Hei Bai, Hallowed Haunting a cada encantamento), dispara ~3,8x/partida em goldfish (ver `goldfish-log.md`, Teste #1) |
| Touch the Spirit Realm | O-Ring + modo channel instantâneo |
| Sanctum of Shattered Heights, Go-Shintai of Hidden Cruelty, Go-Shintai of Ancient Wars | Remoção/dano escalando com número de Shrines |
| Annie Joins Up | 5 de dano a criatura/planeswalker ao entrar, e dobra gatilhos de criaturas lendárias (muitas Shrines são criaturas lendárias) |

**11 efeitos de remoção/contramágica**, cobrindo exile, remoção repetível e 3 contramágicas diferentes — é o único dos 4 decks que roda counterspells de verdade, o que sozinho já empurra o nível de interação pra cima dos outros três.

> **Atualização (2026-08-24):** Farewell foi trocada por Aura Shards (pedido
> do usuário, testado em `goldfish-log.md` Teste #1 antes da troca real —
> deltas em turno de comandante/Shrines/draw/tokens todos dentro do ruído,
> a troca é isolada do motor central). Farewell era um wipe modal de 1 uso;
> Aura Shards é repetível e escala com a alta densidade de token do deck.
> Ambas são Game Changers reais — a troca 1-por-1 mantém o deck em 3/3,
> não muda o Bracket.

---

## 8. Proteção

Heroic Intervention, Teferi's Protection, Ephemerate (com rebound = 2 usos), e principalmente:

- **Greater Auramancy** e **Sterling Grove** — dão **shroud pra todos os outros encantamentos que você controla**. Isso torna as 17 Shrines essencialmente imunes a remoção direcionada assim que uma dessas duas resolve — fecha a maior vulnerabilidade natural de um deck de encantamentos.
- Pacote de blink (Displacer Kitten, Deadeye Navigator, Thassa Deep-Dwelling, Teleportation Circle, The Mind Stone) reseta ETBs e também funciona como pseudo-proteção contra remoção pontual.

---

## 9. Win conditions

Esse deck não vence por combate/voltron como os outros três — vence por **inevitabilidade**:

- **Drain escalando com Shrines** (Northern Air Temple, Sanctum of Stone Fangs) — dreno recorrente que cresce conforme o board se desenvolve.
- **Purphoros, God of the Forge** — com os vários geradores de token do próprio ciclo de Shrines (Honden of Life's Web, Southern Air Temple, Crescent Island Temple, Go-Shintai of Shared Purpose), cada token causa 2 de dano a cada oponente.
- **Elesh Norn, Mother of Machines** — dobra TODOS os seus próprios gatilhos de entrada (inclusive das Shrines) e desliga os gatilhos de entrada dos oponentes. É uma carta de altíssimo poder que também funciona como stax leve.
- **Hallowed Haunting** e **Sphere of Safety** — com 7+ encantamentos (fácil de bater com 17 Shrines só), seu time todo voa/tem vigilância, e atacar você fica proibitivamente caro pros oponentes.
- **Card draw absurdo** eventualmente esgota os recursos da mesa por si só.

Não é um deck "combo mata no turno X" — é controle/valor que, se não for pressionado rápido, simplesmente acumula vantagem até ser impossível de alcançar.

---

## 10. Tutores

**Idyllic Tutor** (busca qualquer encantamento) e **Sterling Grove** (sacrifica pra buscar encantamento) — 2 tutores, ambos indo direto no plano principal (achar a Shrine que falta ou a peça de proteção certa).

---

## 11. Estimativa de Bracket — CORRIGIDA (ver nota abaixo)

**Bracket 3 (Upgraded), no teto exato do que o bracket permite.**

> **Nota de correção:** a versão anterior desta auditoria classificou o deck como Bracket 4 usando uma leitura informal ("tem contramágica, tem Elesh Norn, deve ser mais forte"). Isso estava errado. O sistema oficial da Wizards (5 brackets, beta) não classifica por "sensação de poder" — classifica por **contagem de Game Changers** (lista oficial de 53 cartas) mais a presença ou não de combo de 2 peças cedo, negação de terras em massa, e turnos extras encadeados. Reclassificação feita conferindo a lista real contra o Scryfall (`is:gamechanger`).

**Contagem real de Game Changers no deck: 3**
- Seedborn Muse
- Teferi's Protection
- Aura Shards *(trocada por Farewell em 2026-08-24 — ambas Game Changers, troca 1-por-1 mantém o teto de 3)*

Isso é **exatamente o teto do Bracket 3** (até 3 Game Changers permitidas). Confirmando os outros critérios:
- Sem combo de 2 peças que vença cedo no jogo (Deadeye Navigator/Thassa/blink não geram loop infinito sozinhos, todos custam mana por ativação).
- Sem mass land denial.
- Sem turnos extras encadeados (nenhuma carta de turno extra na lista).
- Tutores raros (só Idyllic Tutor e Sterling Grove — 2 no total).

Portanto: **Bracket 3**, no limite superior — é um deck "Upgraded" muito bem otimizado dentro do teto que o bracket permite, não um deck de Bracket 4. Ele é mais forte que Beorn/Thranduil (1 Game Changer cada) e Kutzil (2 Game Changers), mas os quatro decks continuam tecnicamente no mesmo bracket oficial. A diferença de "sensação de poder" que eu descrevi antes é real (motor de draw mais denso, mana base mais cara) — só não é o suficiente pra mudar a classificação oficial, porque o teto de Game Changers é o que decide, e ele está exatamente em cima da linha, não acima dela.

**Ficar de olho:** com 3/3 Game Changers já usadas, qualquer troca futura que adicione uma quarta (ex: trocar algo por Rhystic Study, Smothering Tithe, Cyclonic Rift etc.) empurraria o deck pra Bracket 4 automaticamente — vale avisar seu grupo se isso mudar.

---

## 11.5 Revisão completa do simulador (2026-08-27)

Usuário pediu a mesma revisão rigorosa aplicada ao Ur-Dragon nessa
sessão ("deve ter muitos erros semelhantes") — confirmado: sim. 13
achados reais corrigidos, incluindo 3 mecânicas 100% ausentes
(Displacer Kitten, Enduring Vitality, a segunda habilidade ativada da
própria Hei Bai) e um bug sistêmico no motor de blink inteiro (alvo
ilegal — Shrines puramente encantamento sendo repiscadas por efeitos
restritos a "target creature"). Impacto real (mesma seed): dano proxy
total 10,82→**195,95**, tokens criados 7,51→**59,10**, dobras via Elesh
Norn 2,87→**89,87**. Ver `goldfish-log.md` Correção #1 (segunda rodada)
pra lista completa. Não muda a contagem de Game Changers nem a
classificação de Bracket (correção de simulador, não de decklist) —
mas confirma que o motor de valor real do deck é significativamente
mais forte do que qualquer número reportado antes desta revisão.

---

## 12. Sugestões de melhoria (prioridade)

1. O deck está extremamente bem construído — não há gap estrutural óbvio como nos outros três (nem remoção fraca, nem land count baixo, nem falta de draw).
2. Se quiser mais consistência ainda, considerar **Volcanic Island** (o único dual ABUR que falta) para fechar o ciclo, embora não seja estritamente necessário dado o resto da fixação.
3. O deck é Bracket 3 como os outros três, mas está no teto exato (3/3 Game Changers) e com uma mana base muito mais cara/consistente — na prática ele deve jogar "no topo" do bracket. Vale mencionar isso ao grupo mesmo estando tecnicamente no mesmo bracket. E lembrar: qualquer adição de uma 4ª Game Changer o empurra pra Bracket 4 de verdade.
4. Se quiser, um wincon mais definitivo de "fechar agora" (algo como **Approach of the Second Sun** ou um X grande de dano escalando com Shrines) daria uma saída mais rápida pros jogos que se arrastam — hoje o deck vence por atrito, o que é ótimo em mesas lentas mas pode ser lento demais contra decks combo/aggro rápidos.

---

## Links

- EDHREC: https://edhrec.com/commanders/hei-bai-forest-guardian
- Tema Shrines: https://edhrec.com/themes/shrines
- Moxfield (criar/comparar): https://moxfield.com/decks/new

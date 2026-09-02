# Checklist cláusula-a-cláusula — Ms. Bumbleflower (Bant, G/W/U)

Pedido direto do usuário (2026-09-02): lista completa colada ao vivo
nesta conversa, em resposta a "Preciso que você mande a lista de cartas
dele" (o `lista.md` estava vazio, sem decklist alguma). Último dos 4
decks sem simulador desta sessão a ser fechado (depois de Kutzil, Azula
e Captain Storm). Mesma disciplina de "compile TUDO".

**Fonte de dados:** oráculo real das 94 cartas não-básicas + comandante,
buscado ao vivo via Scryfall (`POST /cards/collection` em 2 lotes +
`/cards/named` pros 3 MDFCs — Barkchannel Pathway // Tidechannel
Pathway, Brazen Borrower // Petty Theft, Tamiyo Inquisitive Student //
Seasoned Scholar). Lista fornecida pelo usuário: 99 cartas de biblioteca
+ comandante, **completa** (sem buraco, ao contrário do Captain Storm).

**Arquitetura:** objetos `Permanent` (mesmo padrão do Kutzil/Toph/Captain
Storm) — este é o deck de contadores mais denso da sessão inteira:
+1/+1 counters persistentes disparando efeitos em cascata (Danny Pink,
Simic Ascendancy) são o coração do plano de jogo.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real modelado, mesma convenção de
  toda a sessão.
- 🐛 **Achado e corrigido durante a própria construção** — gap que passou
  no primeiro rascunho e foi achado numa varredura automatizada, aplicada
  ANTES de considerar o deck pronto.

## 🐛 Gaps reais achados

### O comandante nunca entrava em campo (achado ANTES da varredura, no primeiro smoke test)

Mesmo bug já corrigido no Azula nesta sessão: `try_cast_commander()`
inicialmente chamava `cast_permanent()`, que faz `state.hand.remove(name)`
— mas Ms. Bumbleflower vem da zona de comando (`BASE_LIBRARY` correto,
sem o comandante nela), nunca esteve em `state.hand`. Corrigido com um
caminho de conjuração dedicado que não depende da mão. Confirmado:
488/500 partidas com o comandante em campo até o turno 10 depois do fix
(0/500 antes).

### 8 gaps reais achados na varredura de tags órfãs

1. **Chasm Skulker** — *"Whenever you draw a card, put a +1/+1 counter on
   this creature."* Só a morte (X Squid tokens) estava implementada; o
   próprio motor de crescer nunca disparava. Corrigido em `on_draw_card()`.
2. **Communal Brewing** — a ETB (*"put AN ingredient counter on this
   enchantment"*, incondicional, antes da parte opcional por oponente)
   nunca setava `communal_brewing_ingredient_counters` — o bônus real em
   criaturas conjuradas depois sempre referenciava um valor preso em 0.
   Corrigido.
3. **Jolrael, Mwonvuli Recluse** — *"Whenever you draw your SECOND card
   each turn, create a 2/2 green Cat."* Carta inteira sem dispatch nenhum.
   Corrigido em `on_draw_card()` via `state.cards_drawn_this_turn`.
4. **Forgotten Ancient** — só a metade de CAST (*"whenever a player casts
   a spell, +1/+1 counter on this"*) estava implementada; a metade de
   UPKEEP (*"you may move any number of counters from this creature onto
   OTHER creatures"*) nunca disparava. Corrigido em `try_upkeep()` —
   move tudo pro melhor alvo (concentra valor), e o destino passa por
   `put_counters()` (mover conta como "por" pra fins de Danny
   Pink/Simic Ascendancy, ruling oficial confirmado).
5. **Noble Heritage** — inicialmente classificado como 100% 📊
   ("precisa de oponente reagindo"), mas a leitura completa mostra que
   *"each player may put two +1/+1 counters on a creature they control"*
   inclui **nós mesmos** — só a cláusula de proteção ("for each opponent
   who does, you gain protection") é opponent-dependent. A colocação de
   2 contadores em nossa própria criatura (na ETB do comandante E em
   cada upkeep) é real e não precisa de oponente nenhum. Corrigido.
6. **Struggle for Project Purity** (modo Brotherhood, escolhido por
   padrão — Enclave é 100% 📊) — *"each opponent draws a card. You draw
   a card for each card drawn this way."* Carta inteira sem dispatch.
   Corrigido em `try_upkeep()`.
7. **Vigilance** — criaturas com vigilance (a própria Ms. Bumbleflower,
   Faeburrow Elder, Loran of the Third Path) tapavam ao atacar igual a
   qualquer outra — quebrava sinergias reais same-turn (Faeburrow Elder
   atacar E ainda tapar por mana no mesmo turno, Rishkar precisar de
   criaturas destapadas pra sua mana-de-contador, Loran atacar e ainda
   usar a habilidade ativada). Corrigido em `combat_step()`.
8. **Swift Reconfiguration** — *"enchant creature or Vehicle... vira um
   Vehicle crew 5, perde os outros tipos"* só tem uso real contra um
   alvo de OPONENTE (neutraliza a criatura) — em nós mesmos só prejudica
   (transforma nosso próprio corpo, removendo-o de atacar sem crew).
   Sem essa exclusão explícita, o loop guloso de conjuração acabaria
   conjurando nela mesma assim que tivesse mana — corrigido excluindo
   do `try_cast_loop()`, mesma lógica de "sem alvo bom sem oponente"
   já usada pro Encore do Captain Storm.

Validado com 2 baterias de testes unitários (5 + 7 = 12 testes isolados,
todos passando) + regressão de 20.000 partidas (seed 5.000.000+,
turns=10, 0 exceções, ~62s).

## Motor central verificado

- **`put_counters()`** — função central por onde passa TODA colocação de
  contador do deck (Bumbleflower, Rishkar, Forgotten Ancient,
  Managorger/Kalonian Hydra, Deepglow Skate, Simic Ascendancy, Noble
  Heritage, Wizard Class nível 3, Oakhollow Village, Slip Out the Back,
  Walking Ballista, The Ozolith) — dispara os 2 gatilhos reais que
  reagem a QUALQUER fonte: Danny Pink (1º contador de cada criatura por
  turno = compra) e Simic Ascendancy (growth counters, 20+ = vitória).
  Testado isoladamente.
- **Ms. Bumbleflower (comandante)** — dispara em TODA magia conjurada
  (não só instant/sorcery), força o oponente a comprar (retrigger real
  de Smothering Tithe, testado), põe contador, e no 2º gatilho do turno
  compra 2 — testado.
- **Kalonian Hydra** — dobra os contadores de TODAS as criaturas ao
  atacar (inclusive ela mesma), via `put_counters(perm, perm.counters)`
  — testado.
- **Simic Ascendancy** — vitória alternativa real com 20+ growth
  counters — testado, e confirmado em batalha real: **4.093/20.000
  partidas (~20.5%)** venceram assim na regressão de 10 turnos.
- **Twenty-Toed Toad** — segunda vitória alternativa real (20+ contadores
  nele OU 20+ cartas na mão ao atacar) — **505/20.000 (~2.5%)**.

## Estrutural (📊, sem oponente real — não julgamento de valor)

- **Beza, the Bounding Spring** — as 4 cláusulas da ETB comparam contra
  "an opponent" (mais terrenos/vida/criaturas/cartas na mão que nós) —
  sem dados de oponente rastreados, nenhuma condição pode ser avaliada
  como verdadeira de forma não-inventada. O corpo 4/5 ainda soma poder
  de ataque normalmente.
- **Path to Exile / Swords to Plowshares / Generous Gift / Pongify /
  Cyclonic Rift / Fractured Identity / Illusionist's Gambit / Loran's
  destroy** — 📊 `interaction_plays`, precisam de alvo de oponente real.
- **Contramagias** (Swan Song, Long River's Pull, An Offer You Can't
  Refuse) — 📊, precisam de spell de oponente.
- **Esper Sentinel / Rhystic Study / Mangara (2º spell do oponente) /
  Faerie Mastermind (2ª compra do oponente)** — precisam de ação de
  oponente real.
- **Struggle for Project Purity, modo Enclave** — 📊, precisa de ataque
  de oponente (Brotherhood, escolhido por padrão, é real — ver acima).
- **Kwain / Loran / Faerie Mastermind (ativada)** — a parte "you draw" é
  real (implementada), a parte "opponent draws"/"each player" retrigger
  Smothering Tithe de verdade (real, implementado via
  `force_opponent_draw()`).
- **Drumbellower / Wilderness Reclamation** — efeitos que só têm valor
  durante o turno DO OPONENTE (untap em resposta, mana pra instant
  speed) — sem turno de oponente simulado, nenhum valor numérico real
  pra capturar.

## Aproximações documentadas (reais, não inventadas)

- **Devoted Druid** — mana engine real (T: G, remove -1/-1 counter:
  untap), aproximado como +2 mana fixo por turno em vez de rastrear o
  -1/-1 counter como estado persistente (exigiria um 2º campo de
  contador só pra esta carta, já que o resto do motor usa `counters`
  como +1/+1 universalmente).
- **Tamiyo, Field Researcher** — +1 aproximado como "compra 1 se
  causamos dano de combate este turno" (captura o valor real sem
  rastrear quais 2 criaturas específicas foram escolhidas, irrelevante
  num goldfish sem bloqueio); -7 real (emblema de conjurar de graça,
  cuidadosamente limitado pelo tamanho finito da mão/biblioteca, sem
  risco de loop infinito).
- **Tamiyo, Inquisitive Student // Seasoned Scholar** — Clue real no
  ataque, transformação real (3ª carta comprada no turno), Seasoned
  Scholar usa -3 (recursão real de instant/sorcery do cemitério) quando
  possível, senão +2 (sem valor ofensivo, documentado).
- **Barkchannel Pathway // Tidechannel Pathway** — sempre registrada
  como o lado Barkchannel (G) — a escolha real seria flexível
  (G ou U conforme necessidade no momento), mas com 1 única cópia numa
  lista de 99 isso é um ajuste de baixíssimo impacto, não implementado
  dinamicamente.

---

## Resumo numérico

- **94 cartas não-básicas + comandante**, 99 cartas de biblioteca real
  (lista completa, sem buracos).
- **🐛 8 gaps reais achados e corrigidos na varredura de tags órfãs** +
  **1 bug crítico** (comandante nunca em campo, achado antes da
  varredura).
- **✅ ~70 cartas/cláusulas com efeito real implementado e testado.**
- **📊 ~10 cartas/cláusulas estruturais confirmadas** (opponent-dependent
  genuíno, mesma convenção de toda a sessão).
- **2 condições de vitória alternativa reais implementadas** (Simic
  Ascendancy, Twenty-Toed Toad), ambas disparando de verdade na
  regressão longa.

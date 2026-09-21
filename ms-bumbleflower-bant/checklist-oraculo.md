# Checklist cláusula-a-cláusula — Ms. Bumbleflower (Bant, G/W/U)

## Porte completo do modo de resiliência (interação de oponente) + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** *"Faça agora a Ms. Bumbleflower"* — seguindo diretamente o
porte concluído no Nekusar, Azula, Beorn e Thranduil (mesma sessão,
mesmo protocolo). Este deck nunca tinha o modo de resiliência atual —
porte completo do zero, nascendo já com a correção de CR 903.9a nativa
desde a 1ª linha.

**Diferença de arquitetura vs os outros 4 decks já portados:**
`state.battlefield` aqui é uma lista de objetos `Permanent` (`uid`,
`card`, `counters`, `tapped`...), não de strings — `remove_permanent`
precisou ser adaptado pra trabalhar com o objeto `Permanent` direto
(identificação por `uid`, nunca só nome, mesmo padrão já usado por
`commander_damage_dealt`/CR 903.10a neste arquivo). `remove_permanent`
**envolve** a função `leave_battlefield` já existente (que já tratava
corretamente transferência de contadores pro Ozolith e geração de
tokens Squid do Chasm Skulker) e adiciona por cima só o que faltava: o
tratamento do comandante (CR 903.9a — cemitério de verdade primeiro,
CR 700.4/704, só depois removida de lá pra representar a zona de
comando).

**Auditoria de pontos de sacrifício pré-existentes (disciplina
obrigatória antes de construir o modo de resiliência, Regra #6 do
CLAUDE.md):** grep confirmado — **0 cartas desta lista sacrificam
permanente nenhum** como custo/efeito real (nenhuma ocorrência de
"sacrifice"/"destroy" no dispatch do arquivo). Diferente do Beorn/
Thranduil (que tinham Natural Order/Prime Speaker Vannifar com bug de
deprioritização do comandante), este deck não tinha NENHUM sacrifice
outlet pra auditar — mais parecido estruturalmuente com o porte do
Nekusar (limpo, sem bugs de sacrifício pré-existentes).

## Achado real ADICIONAL: taxa de comandante (CR 903.8) tinha o contador certo mas o efeito de taxação nunca era lido — 2026-09-21

**Gatilho:** ao inserir o contra-ataque em `try_cast_commander`, notei
que `GameState.commander_cast_count` **já existia** (campo declarado,
incrementado corretamente a cada cast) — mas `effective_cost()` **nunca
lia esse campo em lugar nenhum** (grep confirmado: só 1 ocorrência de
`commander_cast_count` no arquivo inteiro antes desta rodada, o próprio
incremento). Categoria de bug ligeiramente diferente da já vista no
Beorn/Thranduil (ausência total) — aqui havia uma ilusão de
implementação completa (o campo existe, incrementa, parece certo numa
auditoria superficial), mas o efeito real de taxação (+{2} por cast
anterior) nunca acontecia. Só passou a importar de verdade agora que o
modo de resiliência pode genuinamente remover o comandante e forçar um
recast.

**Corrigido:** `effective_cost()` agora soma `2 *
state.commander_cast_count` ao MV base quando `name == COMMANDER`,
antes do `return`.

**Validação:** 3 testes dirigidos confirmando `effective_cost(COMMANDER)`
sobe exatamente +2 por `commander_cast_count` (0→4, 1→6, 3→10).

## Achado real ADICIONAL, não relacionado a CR 903.9a: `mulligan()` reembaralhava via RNG global, não seedado (mesma classe de bug do Azula) — 2026-09-21

**Gatilho:** antes de construir `simulate_one_with_interaction`,
auditei `simulate_one`/`mulligan()` pra confirmar threading correto do
RNG (mesma disciplina já aplicada nos outros decks desta sessão, depois
do bug real achado no Azula). `simulate_one` usa `rnd = random.Random
(seed)` só pro shuffle INICIAL da library — mas `mulligan()`
reembaralhava via `random.shuffle(state.library)` (módulo GLOBAL, não
seedado) a cada mulligan além do 1º. Confirmado empiricamente: **685
de 3.000 partidas (22,8%) davam resultado diferente rodando a MESMA
seed duas vezes**, toda vez que havia pelo menos 1 mulligan.

**Corrigido:** adicionado `rng: Optional[random.Random] = None` ao
`GameState`; `simulate_one`/`simulate_one_with_interaction` agora
passam `GameState(rng=rnd)` (o mesmo RNG seedado já usado pro shuffle
inicial); `mulligan()` trocado pra `state.rng.shuffle(state.library)`.

**Validação:** 0/3.000 partidas não-determinísticas após o fix (vs
685/3.000 antes). Bit-identidade em modo padrão (20.000 seeds,
seed_base 1000000) contra uma versão do commit anterior **patcheada
com APENAS o fix de determinismo** (isolando o efeito puro do porte do
modo de resiliência + fix de CR 903.8): **0/20000 mismatches** — porte
100% estrutural em modo padrão, como esperado (0 sacrifícios
voluntários pré-existentes = comandante nunca sai de campo em modo
padrão = taxa nunca é diferente de 0 = nenhuma das duas correções tem
efeito observável fora do modo de resiliência). Regressão de 20.000
partidas em modo de resiliência: 0 exceções, 0 comandantes presos no
cemitério, 33,48% das partidas com `commander_cast_count >= 2` (recast
pagando a taxa CR 903.8 depois de removida). 22 testes dirigidos:
`remove_permanent` no comandante (não presa no cemitério,
`commander_in_play`/`commander_uid` resetados), `remove_permanent` em
criatura comum (vai pro cemitério normalmente), `remove_permanent`
preserva a transferência de contadores pro Ozolith (via
`leave_battlefield`), taxa de comandante em `effective_cost` (3 casos),
`try_cast_commander` debita taxa e incrementa contador, contra-ataque
intercepta o cast (mana/taxa já gastos, comandante nunca entra em
campo, log correto), `try_smart_opponent_wipe` inclui o comandante nos
alvos de criatura e roteia corretamente pra zona de comando, mulligan
determinístico (300 amostras).

**Resultado:** porte de CR 903.9a sem impacto numérico direto
estrutural em si (0 sacrifícios voluntários pré-existentes), mas achou
2 bugs REAIS não relacionados entre si — taxa de comandante com
contador fantasma (declarado, incrementado, nunca lido) e mulligan
não-determinístico (mesma classe do Azula) — nenhum dos dois visível
numa auditoria carta-a-carta isolada da comandante em si.

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai/Maralen/Kutzil (detalhes de cada
um no topo dos respectivos `checklist-oraculo.md`). Este deck já tinha
passado por 1 rodada de auditoria na própria construção (8 gaps achados
por varredura de tags órfãs + 1 bug crítico do comandante, ver seções
abaixo) — mesmo assim esta 2ª rodada, linha-a-linha contra o oráculo real
via Scryfall (94 cartas não-básicas + comandante, 2 lotes de
`/cards/collection` + 3 `/cards/named?fuzzy=` pros MDFCs), achou **12
gaps reais novos**.

**Achado principal — Heliod, Sun-Crowned tratado como criatura o tempo
todo, incondicionalmente:** o oráculo real diz "As long as your devotion
to white is less than five, Heliod isn't a creature" — mas a carta era
adicionada com `ctype="creature"` fixo (nunca condicionado a nada), então
sempre contava poder de ataque, sempre era um alvo válido de
contador/mana do Rishkar, e suas próprias +1/+1 counters sempre iam pro
Ozolith ao sair de campo, mesmo com devoção baixa (early game). Mesma
classe de bug do "gate faltando na função central" já visto no Kutzil
(lá era `place_counters()`; aqui é `creatures_in_play()`). Corrigido com
`devotion_to_white()` (soma de pips `{W}` de todo permanente controlado)
+ `is_creature_now(state, perm)` (só Heliod é condicional; todo resto
continua usando `is_creature_card`, baseado no type line que nunca muda)
— threaded por `creatures_in_play()`, `put_counters()`, `rocks_mana()`,
`color_sources()` e o check do Ozolith em `leave_battlefield()` (este
último lido ANTES de remover o permanente, já que a devoção de Heliod no
instante de sair ainda inclui ele mesmo).

**12 gaps reais encontrados e corrigidos:**

1. **Heliod, Sun-Crowned — gate de devoção ausente** (ver acima), afetando
   5 pontos reais do motor.
2. **Heliod — "Whenever you gain life, put a +1/+1 counter..." só estava
   ligado ao lifelink de combate.** Kwain, Itinerant Meddler também
   ganha 1 de vida real ("...each player who drew a card this way gains 1
   life") e nunca disparava o Heliod. Centralizado dentro do próprio
   `gain_life()` (único ponto real de "você ganha vida" do arquivo, mesmo
   padrão do `put_counters()`), cobrindo QUALQUER fonte.
3. **Heliod — "{1}{W}: Another target creature gains lifelink until end
   of turn." 100% ausente** (só o gatilho de ganho de vida existia, nunca
   a fonte que o alimenta além do combate normal). Implementado como
   sink de mana em `try_activated_abilities()`, alvo = melhor atacante
   real sem lifelink ainda — converte o próprio dano de combate dele em
   vida ganha, retriggerando o próprio Heliod.
4. **Deepglow Skate — ETB só dobrava contadores do MELHOR alvo, não de
   "any number of target permanents" (plural, oráculo real).** Sem
   nenhuma desvantagem em escolher todos os elegíveis, corrigido pra
   dobrar TODO permanente com contadores >0 — inclusive os growth
   counters do próprio Simic Ascendancy (rastreados à parte por não
   serem +1/+1 counters), que também dobram corretamente agora.
5. **Jolrael, Mwonvuli Recluse — "{4}{G}{G}: creatures you control have
   base power and toughness X/X" 100% ausente** (só o gatilho de compra
   da 2ª carta estava implementado, tag `jolrael` órfã pro resto). Único
   modo real da carta inteiramente sem dispatch. Implementado com um
   flag `jolrael_overdrive_active` lido em `creature_power()` (layer 7b,
   sobrescreve o base ANTES dos +1/+1 counters somarem por cima, como
   nas regras reais) — só ativa quando X (cartas na mão) é maior que o
   melhor poder atual do time, senão seria um downgrade.
6. **Swiftfoot Boots — Equip {1} nunca cobrado.** Mesma classe de bug já
   vista no Captain Storm (lá, 11 peças de Equipment; aqui, só 1 — Lightning
   Greaves é Equip {0} de verdade, então não tinha impacto nela).
   `try_equip()` não gastava mana nenhuma em lugar algum. Corrigido com
   `EQUIP_COST` real por carta, checando `remaining_mana()` antes de
   anexar (se não sobrar mana, fica desanexada até um turno futuro).
7. **Slip Out the Back — "It phases out" completamente ignorado.** O alvo
   continuava atacando normalmente no mesmo turno, quando na verdade
   fasear = "tratado como se não existisse" (CR 702.26e) até o próximo
   turno do controlador. Corrigido com `phased_out_until` checado dentro
   de `creatures_in_play()` (ponto central, cascade automático pro
   combate/mana/alvos) — e o heurístico de alvo agora prefere uma
   criatura com doença de invocação (fasear ela não custa NENHUM dano de
   combate real), só caindo pro melhor alvo geral quando todas já podem
   atacar.
8. **Tamiyo, Seasoned Scholar — ultimate (−7, "draw cards equal to half
   your library, emblem no max hand size") 100% ausente**, só +2/−3
   estavam implementados. Mesmo padrão do −7 da Tamiyo Field Researcher
   (já implementado antes), só faltava o da Scholar. Corrigido com
   prioridade sobre o −3 quando disponível.
9. **Walking Ballista — "Remove a +1/+1 counter: deals 1 damage to any
   target" 100% ausente** (só a entrada com X counters e o `{4}:` de
   crescer estavam implementados). Como o alvo pode ser o oponente
   diretamente, e a simulação roda um número fixo de turnos, implementado
   como conversão no ÚLTIMO turno simulado (`is_last_turn`, threaded por
   `run_turn`/`simulate_one`): sem mais turnos pra atacar de novo,
   contadores parados não geram mais dano nenhum — convertê-los em dano
   direto no fim maximiza o dano real medido (nos turnos anteriores,
   manter os contadores pra atacar repetidamente continua sendo
   estritamente melhor, por isso só converte no último turno).
10. **Twenty-Toed Toad — "your maximum hand size is TWENTY" (número fixo)
    jogado no mesmo balde `no_max_hand` de Reliquary Tower/Thought
    Vessel/Wizard Class (esses sim, sem limite nenhum).** Sem nenhuma
    dessas 3 fontes verdadeiras em campo, o Toad sozinho deveria limitar
    a mão em 20, não em 99. Nunca prejudicou nenhuma métrica pra baixo
    (99>20 só significa reter cartas A MAIS), mas não batia com o
    oráculo real. Corrigido com `max_hand_size()` separando as 2
    categorias; `hand_size_no_max` agora reservado só pras fontes
    verdadeiramente ilimitadas + o emblema da Seasoned Scholar (achado
    #8).
11. **Flooded Grove contava como mana ZERO, junto com Overflowing
    Basin/Skycloud Expanse/Sungrass Prairie.** Esses 3 últimos são
    corretos (só têm o modo filtro "{1},{T}: Add 2 mana coloridas",
    líquido 0 extra) — mas Flooded Grove tem TAMBÉM um "{T}: Add {C}" de
    graça no oráculo real, que as outras 3 não têm. Agrupada no mesmo
    balde, subcontava 1 mana toda vez que estava em campo. Corrigido
    removendo-a do conjunto zerado em `lands_available()`.
12. **Oakhollow Village — "put a +1/+1 counter on each Frog, Rabbit,
    Raccoon, or Squirrel you control that entered this turn" esquecia
    Twenty-Toed Toad** (Frog Wizard, tipo de criatura real desta lista
    exata) do set `RABBIT_LIKE` — só Bumbleflower/Kwain/Rabbit Token
    estavam nele. Corrigido incluindo Twenty-Toed Toad.

**Considerado e deliberadamente NÃO implementado (decisão de design
documentada, não gap deixado pra trás):**
- **Ms. Bumbleflower — "It gains flying until end of turn"** (parte do
  próprio gatilho do comandante): sem bloqueio nenhum modelado neste
  goldfish, evasão temporária não tem nenhum valor numérico capturável —
  mesma classe de "sem janela real pra manifestar valor" do Wilderness
  Reclamation/Drumbellower já documentados.
- **Tamiyo, Field Researcher −2** ("tap up to two target nonland
  permanents") — só tem uso real contra permanentes de OPONENTE; nos
  nossos próprios, só atrapalha. O código já nunca escolhe essa linha
  (sempre +1 ou −7), mas isso não estava documentado explicitamente antes
  desta auditoria.
- **Fellwar Stone** — não tem entrada dedicada nenhuma no `rocks_mana()`
  (produz 0 mana). Confirmado que segue a MESMA convenção já usada no
  Captain Storm/Azula pra esta carta exata ("add mana of a color a land
  an OPPONENT controls could produce" — sem oponente modelado, 0 mana
  real, não um gap novo).
- **Peerless Recycling — modo "Gift"** (prometer uma carta ao oponente
  pra trocar 1 alvo por 2): precisa de um oponente real pra receber o
  presente. Sem ele, o modo base (1 alvo) é o único genuinamente
  disponível — mesma lógica já usada pra Long River's Pull/Peerless
  Recycling's Gift em outros decks da sessão.
- **Ponder** — "look at top 3, put back in any order" não afeta o valor
  numérico aqui (biblioteca já embaralhada aleatoriamente, sem heurística
  de "board need" modelada pra reordenar de propósito); só a compra base
  é capturada, consistente com o resto do arquivo.

Validado com 23 checagens dirigidas (1 arquivo, uma por gap, todas
passando) + 2.000 partidas antes/depois (mesma seed, ver `goldfish-log.md`
pra tabela) + regressão de 20.000 partidas (seed 9.500.000+, turns=10, 0
exceções, ~40s).

---

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

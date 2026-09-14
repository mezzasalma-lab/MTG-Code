# Checklist cláusula-a-cláusula — Thranduil, the Elvenking

## Achado real 2026-09-14 (usuário perguntou se Roaming Throne está certa em todos os decks onde aparece)

Mesma varredura pedida depois dos fixes no Beorn/Edgar Markov/Ur-Dragon/
Ulalek. Este deck (tribal Elfo) tagueia Roaming Throne direto como
`"elf"` no `CARD_DB`. Achados **2 pontos reais** onde isso deixava
Roaming Throne contar como "an Elf card" fora do campo de batalha, o que
o oráculo não permite (o tipo é ganho só ao entrar, não persiste em
mão/cemitério):

1. **Champions of the Perfect** — custo adicional real *"exile an Elf
   you control or an Elf card from your hand"*. Se Roaming Throne fosse
   a única "Elfo" na mão, `_champions_of_the_perfect_exile_candidate()`
   a devolvia como alvo válido — o jogo pagaria o custo exilando a
   Roaming Throne direto da mão, sem ela nunca ter chegado a resolver.
2. **Gilt-Leaf Palace** — *"As this land enters, you may reveal an Elf
   card from your hand. If you don't, this land enters tapped."*
   Roaming Throne na mão contava como esse "Elf card", destravando o
   terreno (mana no mesmo turno) sem ter revelado um Elfo de verdade.

Confirmado como já correto (não precisou de fix): a 3ª ocorrência de
`is_elf()` fora de battlefield (`gy_borrow_sources`, habilidade
emprestada do cemitério via Thranduil) já exige `activation_cost > 0` —
Roaming Throne não tem habilidade ativada nenhuma (`activation_cost ==
0`), então já era excluída corretamente por acidente arquitetural, sem
precisar do fix.

**Corrigido:** novo helper `is_elf_card(name)` (= `is_elf(name) and name
!= "Roaming Throne"`), usado nos 2 pontos reais acima. `is_elf()` puro
continua correto pras checagens de battlefield (candidato de exílio EM
CAMPO do Champions of the Perfect, contagem de Elfos, etc. — inalterado).

**Validação:** 3 testes unitários dirigidos (Gilt-Leaf Palace entra
tapped com só Roaming Throne na mão; entra destapada com um Elfo real
na mão; Champions of the Perfect não acha candidato de exílio com só
Roaming Throne na mão e nenhum Elfo em campo) — todos passando. Batch
de 2.000 partidas: `champions_of_the_perfect_costs_paid` 0,1405→0,1405
(sem movimento na seed testada — cenário raro; a correção real é
comprovada pelos testes unitários). 20.000 partidas de regressão (seed
8400000+), **0 exceções**.

---

## Auditoria oráculo-por-oráculo completa — 2026-09-14

Extensão pra este deck da mesma auditoria já feita em Beorn/Captain
Storm/Rat King/Prismatic Bridge/Toph/Edgar Markov/Hei Bai/Maralen/
Megatron/Nekusar nesta sessão. Este era **o simulador mais extensamente
auditado da sessão antes desta rodada** — já tinha passado por 3 rodadas
completas (2026-08-28, 2026-08-30, 2026-09-01, ver seção abaixo com os 6
gaps daquela última rodada). Mesmo assim, a releitura linha-a-linha do
oráculo real (Scryfall, `/cards/collection` + `/cards/named?fuzzy=` pros
4 MDFC/transform) contra as 91 cartas atuais achou **9 gaps reais
adicionais**, provando de novo que "já foi auditado 3x" não é garantia
de completude.

**Método:** (a) detecção automatizada de tags órfãs (definidas em `add()`,
nunca lidas fora dele) — achou 4 candidatos reais (protection: Heroic
Intervention/Lightning Greaves/Iron-Shield Elf/Selfless Safewright, ver
triagem abaixo); (b) releitura clause-by-clause do oráculo completo
contra cada `add()`/dispatcher, indo atrás do padrão "só 1 das 2+
habilidades reais da carta está implementada" (o mais comum nas rodadas
anteriores desta sessão) e do padrão "uma tag de mana genérica aproxima
uma fórmula real já calculável no arquivo".

### 🐛 Os 9 gaps reais corrigidos nesta rodada

1. **Jarad, Golgari Lich Lord — mana fantasma, mesma classe de bug já
   corrigida pra Immaculate Magistrate em 2026-08-30.** `CARD_DB` tinha a
   tag `gy_scaling` nele (a mesma tag usada por Deathbloom Ritualist pra
   dar mana = cartas de criatura no cemitério) — mas o oráculo real de
   Jarad (*"Jarad gets +1/+1 for each creature card in your graveyard.
   {1}{B}{G}, Sacrifice another creature: ... . Sacrifice a Swamp and a
   Forest: Return this card from your graveyard to your hand."*) **não
   tem nenhuma habilidade de mana**. `total_mana()` tratava qualquer
   carta com essa tag como dork — Jarad gerava mana de graça (até
   `len(graveyard)//3`) todo turno em que ficava em campo, sem nunca ter
   tido essa habilidade de verdade. Tag removida de `add()`.
2. **Selvala, Heart of the Wilds — mesma fórmula real já identificada e
   corrigida no arquivo irmão `beorn_goldfish_v1.py`, mas nunca replicada
   aqui.** Oráculo real: `{G},{T}: Add X mana in any combination of
   colors, where X is the greatest power among creatures you control` —
   estava caindo na mesma aproximação genérica "power_scaling" (+2 fixo)
   usada pra Marwyn, subestimando MUITO o valor real num deck com
   finishers de poder alto (Champions of the Perfect 6/6, overruns
   temporários, etc). Corrigido com `greatest_power_in_play()` (nova
   função): `max(0, greatest_power_in_play(state) - 1)` (o -1 é o próprio
   {G} da ativação).
3. **Marwyn, the Nurturer — mesmo bug de "CDA/contador real hardcoded",
   classe já documentada no Beorn pra Lumra.** Oráculo real: `{T}: Add an
   amount of {G} equal to Marwyn's power` — também caía no "power_scaling"
   +2 fixo, ignorando os contadores reais que o PRÓPRIO arquivo já
   rastreia em `state.marwyn_counters` ("whenever another Elf enters,
   +1/+1 on Marwyn"). Corrigido com `effective_power()` (nova função):
   poder impresso (1) + `marwyn_counters` acumulados.
4. **Deathbloom Ritualist — fórmula errada na tag `gy_scaling`.** Oráculo
   real: `{T}: Add X mana of any one color, where X is the number of
   CREATURE CARDS in your graveyard` — o código usava
   `len(state.graveyard) // 3` (proxy de cartas TOTAIS no cemitério,
   incluindo terrenos/feitiços minados, dividido por 3), não a contagem
   real de cartas de criatura. Corrigido: `sum(1 for c in state.graveyard
   if is_creature(c))`.
5. **Bloom Tender — mana ability real "Vivid" tratada como dork genérico
   de 1 mana fixo.** Oráculo real: `Vivid — {T}: For each color among
   permanents you control, add one mana of that color` — num deck
   tricolor que quase sempre tem 2-3 cores entre os permanentes por T3+,
   isso é um dork de 2-3 mana, não 1. Corrigido com nova função
   `distinct_permanent_colors()` (cores distintas entre permanentes
   NÃO-terreno controlados — terrenos são incolores, não contam).
6. **Lightning Greaves — 100% ausente, mesmo bug documentado no arquivo
   irmão `beorn_goldfish_v1.py` pra essa MESMA carta** ("o haste que ela
   concede de graça nunca beneficiava nenhuma criatura"). Oráculo real:
   `Equipped creature has haste and shroud. Equip {0}` — tag `protection`
   nunca lida em lugar nenhum. Corrigido com `try_lightning_greaves_equip()`
   (Equip {0} de graça, sem limite de vezes/turno, pro melhor alvo com
   doença de invocação e uma habilidade de {T} real modelada) +
   `_dork_ready()` atualizado pra bypassar a doença de invocação do alvo
   equipado. Shroud fica 📊 (proteção pura, sem remoção de oponente
   modelada, mesma classe de Heroic Intervention/Iron-Shield Elf).
7. **Champions of the Perfect — custo adicional real nunca pago.** Oráculo
   real: `As an additional cost to cast this spell, behold an Elf and
   exile it (exile an Elf you control or an Elf card from your hand)` — a
   magia era conjurada de graça sem nunca exigir/pagar o Elfo. Corrigido:
   `can_cast()` agora exige um Elfo disponível pra exilar (mão, preferido,
   senão o Elfo mais barato/não-lendário em campo); `cast_spell()` exila
   de verdade. *"When this creature leaves the battlefield, return the
   exiled card..."* fica deliberadamente fora de escopo (exigiria um hook
   de "leaves battlefield" universal que este arquivo não tem — mesmo
   nível de simplificação temporal já aceito noutros efeitos "delayed"
   deste arquivo).
8. **Tyvar the Bellicose — 2ª habilidade real 100% ausente.** Só a
   1ª habilidade (deathtouch em ataque, sem efeito numérico modelado, já
   documentada) estava coberta. Oráculo real da 2ª: *"Each creature you
   control has 'Whenever a mana ability of this creature resolves, put a
   number of +1/+1 counters on it equal to the amount of mana this
   creature produced. This ability triggers only once each turn.'"* — um
   motor de contadores real disparando toda vez que um dork ativa, nunca
   implementado. Corrigido com `try_tyvar_bellicose_counters()` (soma
   agregada da mana produzida por criaturas no turno, via nova
   `creature_mana_produced()` — mesmo padrão de agregação já usado pra
   Marwyn/Immaculate Magistrate neste arquivo).
9. **Wirewood Lodge / Nurturing Peatland / Waterlogged Grove — 2ªs
   habilidades reais nunca lidas** (só o `{T}: Add` genérico de cada terreno
   estava coberto via `produces`). Wirewood Lodge: `{G}, {T}: Untap target
   Elf` — permite reativar uma habilidade de {T} de Elfo (Fauna
   Shaman/Immaculate Magistrate/Prime Speaker Vannifar/Eladamri/Imperious
   Perfect) uma 2ª vez no mesmo turno; corrigido com
   `try_wirewood_lodge_untap()`. Nurturing Peatland/Waterlogged Grove:
   `{1}, {T}, Sacrifice this land: Draw a card` (canopy lands) — corrigido
   com `try_horizon_land_sac()`, só ativa com 7+ terrenos em campo (land
   flood real, nunca corta a própria base de mana enquanto ela importa).

### Triagem das 4 tags órfãs de "protection" (achado automatizado)

Das 4 cartas com tag `protection` nunca lida fora do `add()` (Heroic
Intervention, Lightning Greaves, Iron-Shield Elf, Selfless Safewright),
só **Lightning Greaves** era um gap real (item 6 acima) — as outras 3 são
**confirmadas 📊 N/A estrutural**, oráculo lido linha a linha:

- **Heroic Intervention** (`Permanents you control gain hexproof and
  indestructible until end of turn`) e **Selfless Safewright** (`When
  this creature enters, choose a creature type. Other permanents you
  control of that type gain hexproof and indestructible until end of
  turn`) — proteção reativa pura contra remoção/wipe de oponente, que
  este simulador não modela (Regra 1). Correto ficar sem efeito numérico
  (mesma classe já documentada pro modo "destroy enchantment"/"remove
  counters" da Glissa Sunslayer).
- **Iron-Shield Elf** (`Discard a card: This creature gains indestructible
  until end of turn. Tap it`) — custo REAL (descartar uma carta) por um
  benefício sem contraparte modelada (proteção contra remoção
  inexistente) seria estritamente ruim de ativar neste motor. Correto
  nunca ativar.
- **Underrealm Lich** (`Pay 4 life: ... gains indestructible ... Tap it`)
  — mesma classe acima; vida não é um total rastreado neste arquivo.

**Também confirmado (não corrigido, documentado como N/A/baixa
prioridade):**
- **High Perfect Morcant** — 2ª habilidade real (`Tap three untapped Elves
  you control: Proliferate`) nunca antes mencionada no checklist. Fica
  📊: proliferate exige estado real de "quais permanentes têm quais
  contadores" que este motor não rastreia (só agrega totais por fonte,
  nunca por permanente individual) — mesma limitação estrutural já
  documentada pros contadores do Immaculate Magistrate/Agatha's Cauldron.
- **Elvenking's Halls** (`{2}{G}{U}, {T}, Sacrifice this land: Put two
  +1/+1 counters on target Elf`) e **Jarad** (`Sacrifice a Swamp and a
  Forest: Return this card from your graveyard to your hand`) — ambas
  reais, mas sacrificar um recurso permanente (terreno) por um retorno
  pequeno/situacional é negativo em valor esperado neste motor guloso;
  documentado como corretamente nunca ativado, mesmo padrão já aceito
  noutros "sac a permanent for marginal value" espalhados pela sessão.
- **Zagoth Triome** (Cycling {3}) — não modelado (este arquivo não tem
  conceito de "converter terreno da mão em carta" fora dos casos já
  cobertos); baixa prioridade, fora de escopo desta rodada.

**Validação:** smoke test (102 nomes no `CARD_DB` — incluindo os órfãos de
lista já documentados —, 99 cartas na `BASE_LIBRARY`, 0 desconhecidas,
commander presente) + `run_batch` antes/depois via `git stash` (2.000
jogos, mesma seed 5000000): Avg finishers ativados 1.50→1.79 (mais mana
real disponível pros overruns), % com finisher até T8 55.4%→59.6%, Avg
spells cast 11.20→11.42, Avg ramp em campo 3.57→3.60, Immaculate
Magistrate contadores/partida 2.94→3.82 (Wirewood Lodge reativando),
Thranduil ativou habilidade emprestada da GY 0.51→0.63/partida — todas as
métricas se moveram na direção esperada (mais mana real, mais value),
nenhuma explodiu. Regressão de 20.000 partidas (seed 9000000+, turns=10),
**0 exceções**. 11 testes unitários dirigidos (script isolado) confirmando
cada uma das 9 correções individualmente, todos passando.

---

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge e Rat King.

**Contexto importante:** este é o simulador mais extensamente auditado da
sessão antes desta rodada — já tinha passado por auditorias completas em
2026-08-28 e 2026-08-30 (documentadas no próprio código com comentários
"Achado real 2026-08-28/30" espalhados pelo arquivo, corrigindo dezenas
de gaps: Cavern of Souls/Eclipsed Realms tratadas como incolor, Thranduil's
Company land drop bloqueado, landfall triggers só logando sem efeito,
Oversold Cemetery só tutorando sem devolver, etc). Mesmo assim, a
releitura desta rodada achou **6 gaps reais adicionais**.

**Método diferente do Rat King:** este arquivo despacha majoritariamente
por **nome de carta** (não por tag) — a detecção automatizada aqui
cruzou 2 sinais: (a) tags órfãs (definidas em `add()`, nunca lidas) e (b)
nomes de carta que só aparecem na própria linha `add()` + no
`DECKLIST_TEXT`, nunca em nenhuma lógica de resolução. 8 candidatos
apareceram; 2 eram falsos positivos (cobertos pelo dispatcher genérico de
`finisher_repeatable`), 6 eram gaps reais.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — não produz número neste modelo por decisão de
  arquitetura documentada (sem oponente real, sem combate/P-T por
  criatura individual, sem tap-de-criatura-por-mana) — limite conhecido,
  não julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.
- ⚠️ **Órfão de lista** — carta definida em `CARD_DB` mas fora da lista
  atual de 91 cartas (`lista.md`); implementação correta, mas inerte hoje.

## 🐛 Os 6 gaps corrigidos nesta rodada

1. **Deadly Rollick** — não era uma tag órfã, era um **julgamento de
   valor disfarçado de custo estático**: `CARD_DB` tinha `mv=2` como
   aproximação ("quase sempre paga {1}{B}, controla comandante") em vez
   de checar a condição real. Oráculo real (Scryfall): *"If you control a
   commander, you may cast this spell without paying its mana cost.
   Exile target creature."* Custo real impresso {3}{B}=MV4. Corrigido com
   `effective_mv()`: retorna 0 quando `state.commander_in_play`, senão o
   custo real (4). Usado em `can_cast()`, `cast_spell()` e na ordenação de
   `try_use_own_interaction()`.
2. **Urza's Incubator** ⚠️ órfão de lista (tag `cost_reducer`) — *"As this
   artifact enters, choose a creature type. Creature spells of the chosen
   type cost {2} less to cast."* Tipo = Elfo. Corrigido em
   `effective_mv()`. Correto, mas fora da lista atual de 91 cartas.
3. **Eclipsed Elf** ⚠️ órfão de lista (tag `card_selection`) — *"When this
   creature enters, look at the top four cards of your library. You may
   reveal an Elf, Swamp, or Forest card from among them and put it into
   your hand."* Corrigido em `_apply_etb()`, usando `LAND_SUBTYPES` (já
   existente pro check-land Hinterland Harbor) pra checar Swamp/Forest de
   verdade, não só nome literal. Correto, mas fora da lista atual.
4. **Harmonized Crescendo** ⚠️ órfão de lista (tag `draw_burst`) — *"Choose
   a creature type. Draw a card for each permanent you control of that
   type."* Tipo = Elfo. Corrigido em `_apply_etb()` — compra 1 por
   permanente Elfo controlado. Convoke não modelado (limitação
   estrutural do motor de mana inteiro, não recorte desta carta). Correto,
   mas fora da lista atual.
5. **Kindred Dominance** (tag `wipe_asymmetric`) — *"Choose a creature
   type. Destroy all creatures that aren't of the chosen type."* Mesma
   convenção já aplicada nesta sessão pros wipes assimétricos do Rat King:
   destruiria as PRÓPRIAS criaturas não-Elfo sem oponente real — conta
   como conjurável (mana gasta via `cast_spell`, já incrementa
   `removal_cast`), sem destruir o próprio board (Regra 1).
6. **Raise the Palisade** (tag `bounce_asymmetric`) — *"Choose a creature
   type. Return all creatures that aren't of the chosen type to their
   owners' hands."* Mesma lógica do item 5 (bounce assimétrico do próprio
   board sem oponente real) — conjurável, sem efeito no próprio board.
7. **Takenuma, Abandoned Mire** (tag `gy_engine`) — Channel já documentado
   como deferido desde 2026-08-30. Oráculo real: *"Channel — {3}{B},
   Discard this card: Mill three cards, then return a creature or
   planeswalker card from your graveyard to your hand. This ability costs
   {1} less to activate for each legendary creature you control."*
   Corrigido com `try_takenuma_channel()` (chamada antes de
   `play_land()`) — só descarta quando sobra outro terreno na mão nesse
   turno. `is_legendary_elf` cobre "legendary creature" com exatidão
   nesta lista: as 21 criaturas lendárias do deck são todas Elfos
   (verificado via Scryfall/`thranduil_full.json`, sem exceção).

**Falsos positivos descartados** (nomes que apareciam só em `add()`+
decklist, mas na verdade já cobertos): **Allosaurus Shepherd** e
**Tyvar, the Pummeler** — suas ativadas de finisher (`{4}{G}{G}`/
`{3}{G}{G}`) já eram despachadas genericamente via
`has_tag(card, "finisher_repeatable")` em `activate_finishers()`; só as
estáticas "can't be countered"/"tap outra criatura pra indestructible"
ficam 📊 (sem contraparte de oponente/remoção modelada).

Validado com 8 testes unitários isolados + regressão de 20.000 partidas
(seed 2000000+, turns=10, 0 exceções) + `run_batch` antes/depois via
`importlib` (3000 jogos, seed 5000000, turns=10): RECURSION 0.68→0.92,
Kindred Dominance 4.9%, Raise the Palisade 9.0%, Takenuma Channel 20.8%
dos jogos.

## Demais cartas — confirmadas ✅ implementadas ou 📊 estruturais

Nenhum outro nome ou tag ficou órfão na varredura automatizada. As
categorias 📊 já documentadas em rodadas anteriores (2026-08-28/30)
seguem válidas: efeitos opponent-dependent (Rhystic Study, High Perfect
Morcant, Maralen, Ruthless Winnower symmetric part), combat-dependent sem
P/T por criatura (Tyvar the Bellicose deathtouch), e simplificações de
escopo já documentadas no próprio código (Three Tree City 2ª habilidade,
Cavern/Eclipsed Realms só pro modo criatura).

---

## Resumo numérico

- **91 cartas na lista atual** (comandante + 90 de biblioteca,
  `lista.md`) — confirmado por comparação direta `CARD_DB` vs `lista.md`.
- **🐛 Corrigido nesta rodada, ativo na lista atual:** 4 cartas (Deadly
  Rollick, Kindred Dominance, Raise the Palisade, Takenuma, Abandoned
  Mire).
- **🐛 Corrigido nesta rodada, mas ⚠️ órfão de lista (inerte hoje):** 3
  cartas (Eclipsed Elf, Harmonized Crescendo, Urza's Incubator).
- **⚠️ Outras 8 entradas órfãs de lista já existentes** (não corrigidas
  nem quebradas nesta rodada, apenas confirmadas fora da lista atual):
  Deathcap Glade, Elf Warrior Token (token, não é carta real da lista),
  Feed the Swarm, Formidable Speaker, Llanowar Wastes, Lys Alana
  Huntmaster, Putrefy, Undergrowth Stadium.
- **✅ Falsos positivos descartados (já cobertos por dispatcher
  genérico):** Allosaurus Shepherd, Tyvar, the Pummeler.

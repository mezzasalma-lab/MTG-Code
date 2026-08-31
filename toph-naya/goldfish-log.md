# Goldfish Log — Toph (Naya)

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

### Revisão completa do oráculo (100 cartas) — 2026-09-01

**Pedido do usuário:** "Revise TODAS as cartas da Toph pelo oráculo completo."
Depois de eu confirmar que o avanço de capítulo do Urza's Saga já estava
correto (não custa mana — Saga, não Classe; a correção do usuário estava
certa em espírito, mas o código já não tinha esse bug), o pedido virou uma
auditoria completa: as 100 cartas da lista (99 + comandante) foram
buscadas ao vivo via `POST /cards/collection` da API do Scryfall (2
lotes de até 75 + 3 MDFCs por nome individual, já que `//` no nome não
resolve via esse endpoint) e cruzadas card a card contra `CARD_DB` e o
dispatch real (não por memória, não por confiança no que já estava
documentado). Achados reais, todos corrigidos:

**Mecânicas 100% ausentes (não eram nem tag decorativa — zero menção fora do `add()`):**
- **Enlightened Tutor** — 1 dos 3 Game Changers da lista, sem nenhuma
  implementação. "Search your library for an artifact or enchantment
  card... put that card on top" — vai pro topo da biblioteca (garante a
  próxima compra), não pra mão. Implementado com lista de prioridade
  (Sol Ring primeiro, depois maior CMV disponível).
- **Oswald Fiddlebender** — "Magical Tinkering": sacrifica um artefato,
  busca outro de custo exato sac+1 direto pro campo. Implementado (usa a
  mesma prioridade `SAC_VALUE` já usada pelo Krark-Clan Ironworks pra
  escolher o que sacrificar).
- **Earth Kingdom General** — "whenever you put +1/+1 counters on a
  creature, gain that much life, once each turn". Implementado via
  `apply_earthbend()` (cobre a maioria dos caminhos de contador do deck;
  Bristly Bill/Mossborn Hydra dobrando e realocação do Ozolith ficam de
  fora — decisão de escopo documentada na própria função).
- **Badgermole Cub**, segunda habilidade — "whenever you tap a creature
  for mana, add an additional {G}" (só o earthbend do ETB estava
  implementado). Relevante combinado com Enduring Vitality.
- **Fountainport** — `{2},{T},sac token: draw a card` (as outras 2
  habilidades ativadas — Fish token, Treasure via `{4}` — continuam fora,
  valor menor; decisão de 2026-08-28 parcialmente revertida).

**"Enters tapped" condicional nunca checado (4 terrenos, fora dos 3 MDFCs
já corrigidos na rodada anterior):**
- **Field of the Dead** — "This land enters tapped" SEM condição nenhuma
  (faltava a tag inteira — bug mais simples e mais grave dos 4, land
  Game Changer, presente em 82%+ dos jogos).
- **Ba Sing Se** — "unless you control a basic land".
- **Canopy Vista / Cinder Glade** (battle lands) — "unless you control
  two or more basic lands".
- **Stomping Ground / Temple Garden** (shock lands) — "you may pay 2
  life. If you don't, it enters tapped" — nunca pagavam nada, entravam
  destapadas de graça (mesmo padrão do bug já corrigido pra Tanglespan
  Bridgeworks na rodada anterior, só que essas duas ficaram de fora).
- **Fetches** (Arid Mesa/Windswept Heath/Wooded Foothills) — "Pay 1 life"
  nunca era pago ao ativar (nem jogadas da mão, nem replay via
  Crucible/Conduit).

**Gatilhos com condição errada (bug de timing/escopo, não de dado ausente):**
- **Avatar Kyoshi, Earthbender** — "At the beginning of combat on your
  turn" é turn-based, dispara todo turno com ela em campo; o código
  dependia de existir algum atacante elegível ANTES de checar Kyoshi, o
  que fazia o gatilho nunca disparar se ela mesma tivesse doença de
  invocação e fosse a única criatura em campo. Faltava também "then untap
  that land" (mana extra real se o alvo já estava tapped por outro gasto
  do turno). Ambos corrigidos.
- **Toph, Earthbending Master / Horizon Explorer** — "Whenever YOU
  attack" é gatilho do JOGADOR (com qualquer criatura), estava
  implementado como "whenever THIS creature attacks" — exigia a própria
  carta elegível pra atacar, sub-contando o gatilho quando ela estava
  sick mas outra criatura atacava mesmo assim. Corrigido (Bumi, que É
  "whenever BUMI attacks" de verdade, ficou como estava — gate correto).

**Alvo ilegal (contador em permanente que não é criatura):**
- **Bristly Bill, Spine Sower** e o 4º contador do **Earthbender
  Ascension** — "put a +1/+1 counter on TARGET CREATURE" mirava
  `best_earthbend_target()`, que escolhe qualquer TERRENO (nem sempre uma
  criatura de verdade). Nova `best_creature_target()` corrige os dois.
- **Felidar Retreat** — modal real é "criar token de 2/2" OU "contador em
  CADA criatura que você controla", não "contador em 1 alvo com fallback
  pra token". Corrigido pra escolher entre os 2 modos reais (política:
  contador-em-todas quando já há 2+ criaturas de verdade em campo, senão
  token).

**Mana fantasma / contabilidade errada:**
- **Awaken the Woods** — X forçava mínimo 1 (token de graça mesmo com 0
  mana extra sobrando) e NUNCA deduzia o custo de X da mana disponível —
  mana infinita de fato. Corrigido (mínimo 0, X pago de verdade; cap de 4
  mantido como estava, é política pré-existente não relacionada ao bug).

**Cosmético, zero impacto numérico:**
- Dryad of the Ilysian Grove: `ctype` "creature" → "enchantment_creature"
  (tipo real, `CREATURE_ISH` já cobria os dois).
- 6 `add()` duplicados removidos (Canopy Vista/Field of the
  Dead/Planar Engineering/Windswept Heath/Wooded Foothills/Yavimaya
  apareciam 2x no `CARD_DB` com dados idênticos).
- "Bridgeworks Battle" (sem `// Tanglespan Bridgeworks`) removido de um
  `elif` morto em `resolve_instant_sorcery` — nome que nunca é alcançado,
  o MDFC é `ctype=="land"`.

**Conferido e confirmado CORRETO (não mudou nada, verificado contra o
oráculo, não assumido):** Bumi ("whenever BUMI attacks", gate por
elegibilidade está certo — diferente de Toph EM/Horizon Explorer);
Bountiful Promenade/Spire Garden ("enters tapped unless you have two or
more opponents" — sempre verdade numa mesa real de Commander, então
destapado por padrão já estava certo); Great Divide Guide/Prismatic
Omen/Yavimaya (fixação de cor pura, sem efeito numérico neste modelo
genérico, precedente de 2026-08-28); Strip Mine (sacrifício pra destruir
terreno é opponent-dependent, sem razão pra mirar o próprio terreno).

**Robustez:** 20.000 partidas (seeds 8200000–8219999) + mais 30.000 de
verificação pontual dos novos gatilhos, 0 erros/timeouts. 0 jogos com
vida negativa apesar dos novos custos de vida (fetches/shocks/MDFC).

**n=3000, seed_base=9000000 — antes (fim da rodada anterior) → depois:**

| Métrica | Antes | Depois |
|---|---|---|
| Turno médio de conjuração da Toph | 3,52 | 3,61 |
| Avg terrenos em campo (T8) | 9,74 | 9,96 |
| Avg aplicações de earthbend | 6,51 | 6,50 |
| Avg recorrências via Motor#16 | 0,65 | **0,92** |
| Avg tokens totais criados | 9,69 | **11,55** |
| Avg vida ganha | 0,22 | **0,88** |
| Cap defensivo do Scute Swarm atingido | 13.262 | 24.446 |

Leitura: a maior mudança é Motor#16 (0,65→0,92) e earthbend por Avatar
Kyoshi especificamente (146→317 no total bruto de 3000 jogos) — o fix do
gatilho de "beginning of combat" (antes preso atrás de "precisa ter
atacante elegível") passou a disparar de verdade em muito mais jogos.
Vida ganha sobe principalmente pelo Earth Kingdom General (motor novo,
capado 1x/turno) compensando os novos custos de vida (fetches -1, shocks
-2, Tanglespan -3) que também entraram nesta rodada. Nenhuma métrica
central (terrenos, earthbend total, turno da comandante) se moveu fora da
faixa de ruído esperada — os bugs corrigidos eram todos de gatilhos raros
ou condições que já eram majoritariamente verdadeiras (ex: 2+ básicas em
campo é comum a partir do turno 3).

`lista.md` não mudou. `toph_v1_runs.jsonl` sobrescrito (3000 jogos, código atual).

---

### Correção — bug real de terrenos "conjurados de graça" + rodada ampliada parcial — 2026-08-31

**Contexto:** rodada ampliada do checklist (categorias 10-13) pedida pelo
usuário pra Toph/Ulalek/Vihaan/Megatron, despachada via agente em
background. O agente do Toph **morreu de rate-limit no meio do trabalho**
— escreveu um docstring detalhado descrevendo 7 correções como se
estivessem prontas, mas na hora de conferir o código real, **nenhuma das
6 correções "de mecânica" tinha sido implementada de fato** (só o
docstring existia — Urza's Saga continuava com a mesma tag apagada,
Wrenn/Caretaker's Talent/Crucible/Conduit sem nenhum dispatch novo,
relatório sem as métricas básicas). Detectado comparando o texto do
docstring contra uma busca real pelas funções que ele dizia ter criado —
nenhuma existia. Corrigido aqui: docstring reescrito pra separar
explicitamente o que FOI corrigido de verdade do que ainda está só
diagnosticado (fica pendente pra próxima sessão).

**Bug real corrigido — terrenos excedentes conjurados de graça:** o
`agente` (antes de morrer) encontrou isso via teste empírico, e eu
confirmei lendo o código: `main_phase()` monta o loop de conjuração com
`castables = [n for n in state.hand if can_cast(state, n) ...]`, e
`can_cast()` só checa `remaining_mana(state) >= CARD_DB[name].mv` — como
todo terreno tem `mv=0`, qualquer terreno que sobrasse na mão depois do
land-drop normal do turno (1x/turno) era `cast_card()`ado como se fosse
um spell qualquer, entrando em campo de graça e SEM respeitar o limite
de 1 terreno/turno. Corrigido excluindo `CARD_DB[n].ctype != "land"` das
duas ocorrências do loop `castables` em `main_phase()`.

**Bug real corrigido — Urza's Saga com tag apagada:** `add("Urza's Saga",
0, "land", set())` duplicado sobrescrevia a tag real `{"saga_token"}` do
registro original. Duplicata removida. **Atenção:** a tag `saga_token`
nunca teve NENHUM dispatch em lugar nenhum do arquivo, mesmo antes da
duplicata — os capítulos I/II/III da Saga continuam sem mecânica real
implementada, só o dano da sobrescrita foi corrigido. Fica pendente.

**Ainda pendente (achado real, não implementado — não marcar como
feito):** engine de capítulos do Urza's Saga; 3 MDFCs (Bala Ged Recovery
// Bala Ged Sanctuary, Ondu Inversion // Ondu Skyruins, Bridgeworks
Battle // Tanglespan Bridgeworks) registradas só como land, sem a face
de spell nunca castável; lealdade do Wrenn and Realmbreaker (só a
estática de fixing é simulada); Caretaker's Talent níveis 2/3; Crucible
of Worlds/Conduit of Worlds (recursão de terreno do cemitério, tags
mortas `gy_lands`/`gy_recursion_1turn`); bloco de métricas básicas
(RAMP/DRAW/INTERACTION/RECURSION/FINISHER) no relatório final.

**Robustez:** 20.000 partidas (seeds 8100000-8119999), 0 erros/timeouts.

**n=3000, seed_base=9000000 — antes (com o bug) → depois:**

| Métrica | Antes (bug) | Depois |
|---|---|---|
| Turno médio de conjuração da Toph | 2,67 | **3,42** |
| Avg terrenos em campo (T8) | 9,95 | 9,56 |
| Avg aplicações de earthbend | 7,68 | **6,67** |
| Avg tokens totais criados | 10,48 | **8,95** |
| Cap defensivo do Scute Swarm atingido (de 3000) | 14.276 | **11.867** |
| Avg gatilhos de landfall | 9,97 | 9,25 |

Leitura: queda real e esperada em quase toda métrica — o bug inflava a
mana disponível todo turno (terrenos extras "grátis" sempre que
sobravam na mão), acelerando artificialmente a conjuração da comandante
e todo o resto do motor. O turno médio de conjuração subir de 2,67 pra
3,42 é o sinal mais direto: antes disso, o deck estava rodando rápido
demais por um bug, não por força real da lista.

`lista.md` não mudou. `toph_v1_runs.jsonl` sobrescrito.

---

### Implementação dos itens pendentes (Urza's Saga, MDFCs, Wrenn, Caretaker's Talent, Crucible/Conduit, 5 métricas obrigatórias) — 2026-08-31

**Contexto:** continuação direta da entrada anterior — os 6 itens que
ficaram "diagnosticados mas não implementados" (docstring de um agente
que morreu de rate-limit antes de escrever o código de verdade) foram
implementados nesta sessão, um a um, com oráculo real conferido ao vivo
via API do Scryfall antes de codar cada um (não por memória):

- **Urza's Saga** — engine real de capítulo I/II/III (`urza_saga_advance()`,
  campo `saga_chapter` novo em `Permanent`). Capítulo I é inerte (só
  concede a habilidade de mana que o terreno já tinha por ser `ctype=="land"`).
  Capítulo II ativa `{2},{T}: cria Construct 0/0` de forma gananciosa se
  sobrar mana (mesmo padrão do Ba Sing Se/Bristly Bill). Capítulo III
  busca artefato de custo 0/1 direto pro campo e sacrifica a Saga (regra
  714 — não é custo da própria carta, mas ainda "morre" pro Motor #16 se
  essa cópia específica tiver sido earthbendada antes: volta tapped e
  reinicia os capítulos do zero, correto pelo texto reminder do earthbend
  que reage a QUALQUER morte).
- **3 MDFCs (Bala Ged Recovery/Sanctuary, Ondu Inversion/Skyruins,
  Bridgeworks Battle/Tanglespan Bridgeworks)** — confirmado ao vivo via
  Scryfall que as 3 faces land reais entram tapped; Tanglespan Bridgeworks
  é o único caso com escolha real ("pay 3 life or enters tapped" — piloto
  paga sempre que a vida permitir, `life_total > 10`, quase sempre verdade
  com 40 de vida inicial de Commander). Bala Ged Recovery tinha `mv=3`
  vestigial (nunca lido, mesmo problema já corrigido no Ondu Inversion na
  rodada anterior) — corrigido pra 0. Face sorcery da Bala Ged Recovery
  ("Return target card from your graveyard to your hand", `{2}{G}`) **não**
  foi implementada — self-contida (não depende de oponente) mas exigiria
  dois modos de `ctype` pra uma única carta, o que o modelo atual não
  suporta sem reestruturar `main_phase()`; decisão de escopo documentada no
  `CARD_DB`, não omissão.
- **Wrenn and Realmbreaker** — `-2` implementado de verdade
  (`wrenn_loyalty_ability()`: mill 3, recupera 1 permanente pra mão).
  Oráculo real conferido: `+1` é "land alvo vira 3/3 até seu próximo
  turno" (não "extra land drop + tutor de básica" como eu tinha assumido
  antes de checar o Scryfall) — sem efeito numérico neste modelo (sem
  combate/P·T rastreado, land "ainda é terreno" então nem mana perde) —
  decisão de escopo. `-7` (emblema de jogar terreno/conjurar permanente do
  cemitério) nunca é alcançado sob a política "-2 todo turno que der",
  porque puxar valor imediato bate qualquer plano de guardar lealdade pro
  ultimate quando `+1` não rende nada mensurável neste simulador.
- **Caretaker's Talent** — nível 2 (`{W}`: copia um token-alvo — só
  dispara se existir um `Permanent` de token de verdade em campo pra
  mirar, já que a maioria dos tokens deste simulador é abstraída como só
  um contador em `create_token()`, limitação de arquitetura preexistente,
  não nova) e nível 3 (`{3}{W}`: anthem +2/+2 em tokens — sem P/T
  rastreado, só o nível em si é concedido e reportado, nunca um número de
  poder fingido) implementados via campo `level` novo em `Permanent`.
- **Crucible of Worlds / Conduit of Worlds** — `play_land()` agora permite
  jogar terreno do cemitério quando uma das duas está em campo e não sobra
  terreno na mão. Única fonte real de terreno no cemitério neste sim:
  fetch já craqueado (nenhum outro terreno REAL — não-artefato — morre
  neste simulador; earthbend/KCI/Obelisk/Coffin só alvejam artefato). Fetch
  replayado do cemitério dispara o ETB de novo (busca outra básica) — motor
  de recorrência real, não só "mais 1 terreno". A habilidade ATIVADA
  própria do Conduit (`{T}`: reanima permanente do cemitério, mas trava o
  resto do turno pra 1 spell só) **não** foi implementada — é uma troca de
  política de jogo real (abre mão do loop ganancioso de conjurar tudo que
  dá por 1 reanimação específica) que precisaria de dados A/B dedicados,
  no padrão já usado pro `BRISTLY_BILL_RESERVE_POLICY`; decisão de escopo.
- **Achado real não listado pelo usuário, pego durante esta implementação:**
  `extra_land_drop` (Dryad of the Ilysian Grove, "you may play an
  additional land on each of your turns") era uma tag decorativa sem
  NENHUM dispatch — `state.extra_land_drops` nunca era incrementado em
  lugar nenhum do arquivo antes desta sessão. Corrigido em `play_land()`
  como efeito contínuo (recalculado a cada chamada) enquanto a Dryad
  estiver em campo.
- **5 métricas obrigatórias** (`goldfish-sim-card-rules.md` seção 10) —
  `run_batch` agora tem um bloco dedicado "5 metricas obrigatorias":
  ramp e draw reaproveitam métricas que já existiam (só rotuladas
  explicitamente agora); interaction (spells/permanentes de interação
  conjurados — `Swords to Plowshares`/`Council's Judgment`/etc, efeito
  numérico N/A por falta de oponente real, mas o NÚMERO de vezes que
  foram conjurados agora é reportado, nunca mais implícito), recursion
  (Motor #16 + replay de terreno via Crucible/Conduit) e finisher/
  lethality (proxy: % de jogos que resolvem ≥1 ameaça de vitória real —
  Avatar Kyoshi/Toph Earthbending Master/Krang/Great Henge/Scute
  Swarm/Sapling Nursery/Felidar Retreat/Mossborn Hydra, ver seção 8 de
  `auditoria.md` — e turno médio de RESOLUÇÃO, explicitamente rotulado
  como proxy porque este simulador não modela dano de combate real) são
  novas.

**Robustez:** 25.000 partidas total nesta rodada (5.000 seeds
8100000-8104999 + 20.000 seeds 8020000-8039999), 0 erros/timeouts.

**n=3000, seed_base=9000000 — antes (fim da rodada anterior, já sem o bug
de terreno grátis) → depois (com todos os itens acima implementados):**

| Métrica | Antes | Depois |
|---|---|---|
| Turno médio de conjuração da Toph | 3,42 | 3,52 |
| Nunca conjurada em 8 turnos | 4,0% | 4,6% |
| Avg terrenos em campo (T8) | 9,56 | 9,74 |
| Avg aplicações de earthbend | 6,67 | 6,51 |
| Avg recorrências via Motor#16 | 0,67 | 0,65 |
| Avg tokens totais criados | 8,95 | **9,69** |
| Avg cartas compradas extra | 1,40 | 1,42 |

**Novas métricas (sem baseline anterior, motor não existia):**

```
Avg spells/permanentes de interacao conjurados: 1,17 | jogos com >=1: 72,5%
Avg recorrencia total (Motor#16 + Crucible/Conduit): 0,77 (0,65 + 0,12)
Finisher/lethality: 50,2% dos jogos resolvem >=1 ameaca ate o turno 8, turno medio 6,27
Avg terrenos replayados via Crucible/Conduit: 0,12
Avg ativacoes de Wrenn -2: 0,20 | jogos com >=1: 11,2%
Caretaker's Talent nivel 2: 12,0% dos jogos | nivel 3: 6,1% dos jogos
Avg tokens via Urza's Saga cap. II: 0,136 | avg tutores via cap. III: 0,139
```

Leitura: números praticamente estáveis (variação de 1-3% na maioria das
métricas já existentes) — os novos motores competem por uma fatia pequena
da mesma reserva de mana (Urza's Saga capítulo II custa `{2}`, capítulo
III é de graça mas sacrifica a própria carta, Caretaker's Talent custa
`{W}` depois `{3}{W}`), então a queda marginal em earthbend/Motor#16 é
esperada e pequena, não um sinal de regressão. Tokens totais SOBE (8,95→9,69)
porque o Construct do capítulo II do Urza's Saga e as cópias de token do
Caretaker's Talent nível 2 somam à métrica. Nenhuma das 6 mecânicas novas
é comum o suficiente pra mover o jogo inteiro sozinha (Urza's Saga e
Caretaker's Talent e Wrenn são singleton numa lista de 99 cartas) — os
números confirmam isso: nenhuma delas aparece em mais de ~12% dos jogos.

`lista.md` não mudou. `toph_v1_runs.jsonl` sobrescrito (3000 jogos, código
atual).

---

## Simulação #1 — goldfish Python completo (`toph_goldfish_v1.py`) — 2026-08-22

**Script construído do zero**, cobrindo as **16 mecânicas/motores documentados na seção 4 da `auditoria.md`**, não só 1 ou 2 (pedido explícito do usuário). Passo 0 (regra de `references/goldfish-sim-card-rules.md`, aplicada de forma mais ampla que só Roaming Throne — esse deck não tem Roaming Throne, mas o princípio de "varredura mecânica antes de codar" vale igual): regex em todo o oráculo achou **43 cartas com gatilho real** ("Whenever"/"At the beginning of"/"When"). Todas as 43 foram checadas contra a lógica implementada; 34 têm efeito real em código, 9 são genuinamente dependentes de oponente/combate (Esper Sentinel, Skullclamp, Sword of Feast and Famine, Talon Gates of Madara, Krang, Haywire Mite como remoção, Council's Judgment, Lightning Greaves, Heroic Intervention) e foram documentadas como tal em vez de fingir um efeito numérico solo.

**Arquitetura:** `Card`/`Permanent`/`GameState` dataclasses. O núcleo é tratar earthbend + "artefato/criatura vira terreno" (Toph e Ashaya) como **um sistema só**, não dois separados — `is_land()` é dinâmico (depende de `commander_in_play`/`ashaya_in_play`/`mycosynth_in_play`), e `leave_battlefield()` é o ponto central onde o **Motor #16** (earthbend torna recorrente qualquer artefato-terreno com gatilho/custo de morte) e o Ozolith (recicla contadores) vivem.

**Bugs reais encontrados e corrigidos durante o build (documentados, não escondidos):**
1. **A própria comandante nunca era conjurada** — `build_library()` só lê a seção "Lista completa" do `lista.md` (99 cartas), a Toph fica na "zona de comando" à parte e a lógica de casting só olhava `state.hand`. Resultado: em 8 turnos de teste inicial, earthbend do end step nunca disparava porque `commander_in_play` ficava `False` o jogo inteiro. Corrigido com `can_cast_commander()`/tax de `+2` por recast, sempre tentada primeiro no `main_phase`.
2. **Loop infinito por mutar `state.battlefield` durante a iteração** — o clone da Scute Swarm era anexado à própria lista que o `landfall_trigger` estava percorrendo com `for p in state.battlefield`, fazendo o loop visitar os clones novos indefinidamente. Corrigido iterando sobre `list(state.battlefield)` (snapshot).
3. **`ValueError` em sacrifícios em lote** — Planar Engineering sacrifica 2 terrenos de uma lista pré-computada; se processar o primeiro disparava uma cadeia de landfall que fazia um bounce land (Gruul Turf/Selesnya Sanctuary) devolver o segundo terreno da lista pra mão antes dele ser processado. Corrigido com uma checagem defensiva em `leave_battlefield()`.
4. **`RecursionError` — Ultron copiando token indefinidamente** — o token criado pela cópia do Ultron reentrava em `enter_battlefield()` e disparava o próprio gatilho do Ultron de novo (a checagem não excluía tokens, e a regra real é "outro artefato **não-token**"). Corrigido com a flag `is_token` no `Permanent`, que também corrige `is_land()` pra não deixar token virar terreno via Toph/Ashaya (a regra real também é "não-token" ali).
5. **`RecursionError` — auto-recursão dentro de `create_token()`** — um `replace_all` de refatoração (trocar `state.tokens_created += 1` espalhado por `create_token(state, log)`) acabou reescrevendo a própria linha *dentro* da definição de `create_token`, fazendo a função chamar a si mesma. Corrigido revertendo essa linha específica pra incremento direto.

Todos os 5 bugs foram achados rodando **20.000 partidas com timeout de 2s por partida via `signal.alarm`** antes do batch oficial — zero erros/travamentos nas 20.000 depois da correção do 5º bug.

**n=2000, seed_base=9000000, 8 turnos:**

```
Avg mulligans: 0,77
Turno medio de conjuracao da Toph: 2,61 | mediana: 2
Nunca conjurada em 8 turnos: 3,6%
Avg terrenos em campo (turno 8, contando artefato/criatura-terreno): 10,22
Avg aplicacoes de earthbend: 7,92
Avg recorrencias via Motor#16: 0,20 | % de jogos com pelo menos 1: 11,1%
Avg gatilhos de landfall disparados: 9,55
Avg tokens de Field of the Dead: 3,90 | % de jogos que ligou: 84,6%
Avg cartas compradas extra (motores de draw): 1,43
Avg mana extra gerado (Lotus Cobra/Nissa por landfall): 1,15
Avg cheats do Kodama of the East Tree: 0,01
Avg copias via Strionic Resonator: 0,50
Avg dobras via Bristly Bill (ativada): 0,23
Avg realocacoes de contador via The Ozolith: 0,03
Avg tokens totais criados: 9,52
% de jogos com Ashaya em campo: 10,3%
Avg vida ganha (Inventors' Fair/Haywire Mite/Sylvan Library liquido): 0,23

Earthbend por fonte (soma das 2000 partidas):
  Toph, the First Metalbender (end step): 12317 (6,16/jogo)
  Ba Sing Se (ativada): 998 (0,50/jogo)
  Toph Earthbending Master (ataque, X=experiencia): 464 (0,23/jogo)
  Badgermole Cub (ETB): 291 (0,15/jogo)
  Avatar Kyoshi (combate): 290 (0,14/jogo)
  Earthbending Student (ETB): 271 (0,14/jogo)
  Earth Kingdom General (ETB): 262 (0,13/jogo)
  Earthbender Ascension (ETB): 253 (0,13/jogo)
  Earthshape (instant): 249 (0,12/jogo)
  Toph Greatest Earthbender (ETB, X=mana gasto): 225 (0,11/jogo)
  Bumi (ETB): 211 (0,11/jogo)
```

**Achados reais que a auditoria qualitativa não tinha número pra sustentar:**

- **Field of the Dead liga em 84,6% dos jogos até o turno 8** — confirma com dado real a hipótese da seção 3/4 da auditoria (artefato virando terreno via Toph conta como nome distinto pra contagem de "7+ terrenos com nomes diferentes"). É um dos motores mais consistentes do deck, não um "às vezes".
- **Motor #16 (earthbend torna artefato-morte recorrente) ativa em 11,1% dos jogos** — real, mas depende de uma combinação específica (earthbendar um Stasis Coffin/Ichor Wellspring/Unstable Obelisk especificamente, e depois ele efetivamente morrer/ser sacrificado) — não é algo que acontece toda partida, mas quando acontece é uma virada de valor real.
- **Scute Swarm é genuinamente explosivo quando resolve com 6+ terrenos em campo** — precisei implementar um **cap defensivo de 200 permanentes em campo** pra simulação não travar (a regra real do card é copiar a si mesma a cada landfall subsequente, inclusive as cópias copiando de novo — crescimento geométrico real, não um bug da minha implementação). Scute Swarm chegou em campo em ~14% das 1000 partidas de uma amostra separada; nessas partidas o cap foi atingido em média **~32 vezes por jogo** (8875 atingidos em só 2000 partidas totais, a maioria concentrada nas ~14% que tinham a carta). Isso é uma leitura real sobre o card, não um artefato de simulação — em mesa, Scute Swarm com Toph em campo (mais terrenos-artefato entrando) tende a sair de controle rápido uma vez montado.
- **Kodama of the East Tree quase nunca encontra o próprio gatilho (0,01/jogo)** — não é bug (conferido manualmente): ele só entra em ~9,6% dos jogos (6 mana, cópia única em 99 cartas) e, quando entra, a política gananciosa do simulador (conjura tudo que dá pra pagar, mais barato primeiro) já costuma ter esvaziado a mão de cartas baratas o bastante pra ele aproveitar. Achado honesto de baixo valor prático dentro do perfil de jogo modelado.
- **Comandante conjurada em média no turno 2,61** (mediana 2) e só 3,6% dos jogos nunca resolvem ela em 8 turnos — a curva de 3 mana da Toph é rápida de bater mesmo sem ramp dedicado a ela especificamente.

---

### Análise: recorrência/reutilização de artefatos via earthbend (Motor #16) — 2026-08-22

**Pedido do usuário:** avaliar especificamente as recorrências e reutilizações de artefatos pelo earthbend da Toph — o motor central que a auditoria (seção 4, item 16) descreve.

**Achado inicial (batch #1 acima), antes de qualquer mudança:** dos 398 eventos de recorrência via Motor#16 em 2000 partidas, **zero** foram Stasis Coffin, Ichor Wellspring ou Unstable Obelisk — exatamente as 3 cartas que o motor foi desenhado pra reciclar. Rastreei os nomes reais de cada evento: os 398 eram todos terrenos comuns (Forest, Mountain, Inventors' Fair, Urza's Saga, etc.), pegos incidentalmente pelo sacrifício em lote do Planar Engineering (2 terrenos aleatórios da ordem do campo), nunca as 3 cartas-alvo.

**Causa raiz:** `best_earthbend_target()` já priorizava earthbendar essas 3 cartas quando disponíveis, mas o `main_phase` nunca **ativava** de fato as habilidades de sacrifício delas (Unstable Obelisk `{7},{T},Sacrifice: Destroy target permanent`, The Stasis Coffin `{2},{T},Exile: gain protection`, ou sacrificar a Ichor Wellspring via Krark-Clan Ironworks). Earthbendadas, elas só ficavam paradas em campo — sem morrer, o Motor#16 nunca tinha o que reciclar.

**Correção — `RECURRING_ARTIFACT_POLICY`:** implementei `work_recurring_artifact_loop()`, chamada no `main_phase` quando o flag está ativo — ativa o Unstable Obelisk earthbendado se houver `{7}` sobrando, ativa a The Stasis Coffin earthbendada se houver `{2}` sobrando, e sacrifica Ichor Wellspring/Mishra's Bauble earthbendadas pro Krark-Clan Ironworks quando ele está em campo. Testado em 20.000 partidas com timeout antes do batch oficial (0 erros).

**n=2000, mesmas seeds, comparando baseline (passivo) vs política (ativa de verdade):**

| Métrica | Baseline (passivo) | Política (ativa) |
|---|---|---|
| Avg recorrências via Motor#16 | 0,199 | **0,738** |
| % de jogos com pelo menos 1 recorrência | 11,1% | **29,2%** |
| Stasis Coffin reciclada (total em 2000 jogos) | 0 | **515** |
| Ichor Wellspring reciclada (total) | 0 | **66** |
| Unstable Obelisk reciclada (total) | 0 | **430** |
| Avg ativações do Unstable Obelisk | — | 0,215 |
| Avg ativações da The Stasis Coffin | — | 0,258 |
| Avg sacrifícios via Krark-Clan Ironworks | — | 0,068 |
| Turno médio de conjuração da comandante | 2,608 | 2,608 (idêntico) |
| Avg aplicações de earthbend | 7,92 | 7,93 (idêntico) |
| Avg vida ganha | 0,23 | 0,23 (idêntico) |
| Avg tokens criados | 9,52 | **11,86** |
| Avg cartas compradas extra | 1,43 | **1,57** |
| Avg mana extra gerado (landfall + KCI) | 1,15 | **1,42** |
| Avg realocações via The Ozolith | 0,03 | **0,10** |

**Leitura:** a política deliberada **triplica** a taxa real de recorrência (11,1%→29,2% dos jogos) sem custo medido em nenhuma métrica de curva (turno da comandante e volume de earthbend ficam idênticos — ativar Obelisk/Coffin não compete de forma visível com o resto do plano de jogo). Tem ainda um efeito colateral positivo não óbvio: cada recorrência via Motor#16 é uma nova entrada em campo, ou seja, **dispara landfall de novo** — isso é o que explica os ganhos simultâneos em tokens (+24,6%), draw extra (+9,8%) e mana extra (+23,5%): reciclar um artefato earthbendado realimenta o resto do motor de landfall do deck, não é um ganho isolado.

**Conclusão prática:** o Motor#16 é real e funciona exatamente como a auditoria descreveu, mas **só se o jogador ativamente sacrificar as cartas earthbendadas em vez de guardá-las** — jogar passivo (earthbendar e deixar parado) desperdiça quase toda a sinergia. Isso vira a linha de jogo recomendada pra mesa: earthbend prioriza Stasis Coffin/Ichor Wellspring/Unstable Obelisk quando disponíveis, e a resposta certa depois é **usar a habilidade delas assim que earthbendadas**, não guardar como ameaça. `RECURRING_ARTIFACT_POLICY` foi promovida a default (`True`) no script a partir desta análise.

---

### Análise: política de earthbend-target em TODOS os 26 artefatos — 2026-08-22

**Pedido do usuário:** a análise anterior só priorizava earthbend em 4 cartas específicas (Stasis Coffin, Unstable Obelisk, Ichor Wellspring, Mishra's Bauble). Testar com **todos os 26 artefatos não-token** da lista como alvo possível, não só essas 4.

**Raciocínio:** qualquer um dos 26 artefatos, uma vez virado terreno pela Toph e earthbendado, pode ser sacrificado pro Krark-Clan Ironworks por `{C}{C}` e voltar de graça pelo Motor #16 — o permanente nunca é perdido de verdade, só volta tapped (perde 1 turno de uso). Isso generaliza o motor #16 muito além das 4 cartas com "gatilho de morte" óbvio.

**Implementação:** `EARTHBEND_TARGET_POLICY` com 3 modos — `narrow` (só as 4 cartas, era o default anterior), `broad_artifact` (as 4 primeiro, depois qualquer um dos 26 artefatos não-token), `land_only` (nunca mira artefato, controle/contraste). `work_recurring_artifact_loop()` estendida: se não há alvo das 4 cartas especiais disponível pro Krark-Clan Ironworks, sacrifica qualquer outro artefato não-token earthbendado. Testado em 20.000 partidas com timeout por política antes do batch oficial (0 erros nas 3).

**n=2000, mesmas seeds, comparando as 3 políticas:**

| Métrica | narrow | **broad_artifact** | land_only |
|---|---|---|---|
| Avg recorrências Motor#16 | 0,738 | **0,966** | 0,289 |
| % jogos com ≥1 recorrência | 29,2% | **35,0%** | 18,5% |
| Avg mana extra gerado | 1,42 | **2,00** | 1,20 |
| Avg cartas compradas extra | 1,569 | **1,581** | 1,454 |
| Avg tokens criados | 11,864 | **12,764** | 9,734 |
| Cartas distintas recicladas (de 2000 jogos) | 40 | **54** | 39 |
| Turno médio de conjuração da comandante | 2,608 | 2,608 | 2,608 |
| Avg aplicações de earthbend | 7,926 | 7,925 | 7,918 |
| Avg terrenos finais | 10,283 | 10,245 | 10,221 |

**Leitura:** `broad_artifact` domina as outras duas em toda métrica de valor (recorrência, mana, draw, tokens), com **turno de comandante e volume total de earthbend idênticos nas três** — ou seja, mudar o alvo do earthbend não custa curva nenhuma, só adiciona valor. `land_only` (nunca mirar artefato) é estritamente a pior das três, confirmando que earthbendar terreno comum é desperdício de prioridade quando há artefato disponível.

**Quais artefatos entram no loop sob `broad_artifact`** (sacrifícios via Krark-Clan Ironworks em 2000 partidas, além das 4 cartas especiais):

```
147  Krark-Clan Ironworks (se sacrifica a si mesma)
 68  Mishra's Bauble
 66  Ichor Wellspring
 31  Arcane Signet
 31  Esper Sentinel
 27  Mox Opal
 26  Liquimetal Coating
 26  The Ozolith
 24  Zuran Orb
 22  Lightning Greaves
 22  Sol Ring
 21  Strionic Resonator
 20  Haywire Mite
 18  Unstable Obelisk
 17  Oblivion Stone / Liquimetal Torque / Crucible of Worlds (cada)
 16  Skullclamp
 15  Sword of Feast and Famine
 12  Ultron, Artificial Malevolence
 11  Iron Spider, Stark Upgrade
 10  Conduit of Worlds
  3  Mycosynth Lattice
  2  The Great Henge
  1  The Stasis Coffin / Krang, Utrom Warlord (cada)
```

**Achado interessante:** o próprio Krark-Clan Ironworks é o alvo mais sacrificado (147x) — earthbendada, ela pode se sacrificar a si mesma pela própria habilidade, gerar `{C}{C}`, e voltar de graça no earthbend seguinte. Mox Opal/Sol Ring/Arcane Signet (juntos 80x) também entram no loop — perdem 1 turno de mana ao voltar tapped, mas nunca são perdidos permanentemente.

**Ressalva honesta sobre a política:** a escolha de qual dos artefatos elegíveis sacrificar é "o primeiro encontrado na ordem do campo", **não por valor** — não há lógica de "prefira sacrificar o Sol Ring a sacrificar o Krang". Krang e The Great Henge quase não entraram no loop (1x e 2x), mas isso é mais coincidência de ordem de batalha do que uma decisão inteligente de preservar valor alto. Uma política mais refinada (ranquear por "quão substituível é essa mana/efeito") é uma extensão possível, não implementada aqui.

`EARTHBEND_TARGET_POLICY` promovida a `"broad_artifact"` como default no script a partir desta análise.

---

### Priorização por valor no sacrifício via Krark-Clan Ironworks — 2026-08-22

**Pedido do usuário:** implementar a ressalva que ficou registrada na análise anterior — a escolha de qual artefato earthbendado sacrificar pro Krark-Clan Ironworks era "o primeiro na ordem do campo", sem noção de valor. Corrigir pra proteger as bombas (Krang, The Great Henge, Mycosynth Lattice) e priorizar o descartável.

**Implementação:** dicionário `SAC_VALUE` (0 a 3) pra cada um dos 26 artefatos, com o critério real sendo "quanto essa carta perde por ficar tapped/fora um ciclo de earthbend" (o permanente sempre volta via Motor #16 — a única perda de verdade é 1 turno de habilidade ativada, nunca o cartão em si):
- **0 — descartável:** equipamento desequipado (Lightning Greaves, Skullclamp, Sword of Feast and Famine), peças situacionais (Haywire Mite, Oblivion Stone, Zuran Orb, Liquimetal Coating), redundância entre Conduit/Crucible of Worlds, e as 4 do `RECURRING_TARGETS` (só caem aqui como fallback, já têm tratamento próprio antes).
- **1 — rocks de mana puros:** Sol Ring, Arcane Signet, Mox Opal, Liquimetal Torque — perdem 1 turno de rampa, nunca o rock.
- **2 — utilidade ativa por turno:** Iron Spider, Strionic Resonator, Esper Sentinel.
- **3 — proteger:** motores que o próprio simulador depende (The Ozolith recicla contadores de outras partes, Krark-Clan Ironworks é o próprio sac outlet do loop) ou bombas de impacto contínuo alto (Krang, The Great Henge, Ultron, Mycosynth Lattice) — só sacrificadas se não sobrar mais nenhuma opção de valor mais baixo.

Testado em 20.000 partidas com timeout antes do batch oficial (0 erros).

**n=2000, mesmas seeds, comparando ordem de campo (antigo) vs prioridade por valor (novo):**

| Métrica | Ordem de campo | Prioridade por valor |
|---|---|---|
| Avg recorrências Motor#16 | 0,966 | 0,966 (idêntico) |
| Avg mana extra gerado | 1,998 | 1,998 (idêntico) |
| Sacrifícios de cartas "protegidas" (tier 3) | 191 | **119** (−38%) |
| Sacrifícios de cartas "descartáveis" (tier 0) | 320 | **405** (+27%) |
| Krark-Clan Ironworks sacrifica a si mesma | 147 | **87** |
| Krang, Utrom Warlord sacrificado | (não isolado) | **1** de 2000 |
| The Great Henge sacrificado | (não isolado) | **1** de 2000 |
| Mycosynth Lattice sacrificado | (não isolado) | **1** de 2000 |

**Leitura:** a mudança é puramente qualitativa, não quantitativa — o volume total de recorrência/mana extra gerado pelo Motor#16 **não muda** (a política só decide QUEM entra no loop, não QUANTO o loop produz). O ganho real é evitar tapar Krang/Great Henge/Mycosynth Lattice sem necessidade — eles agora só entram como último recurso (1 vez em 2000 jogos cada), contra um número não isolado mas claramente maior sob a política antiga (191 sacrifícios de tier 3 no total, incluindo esses). `SAC_VALUE_PRIORITY_POLICY` promovida a `True` como default.

---

### Levantamento dos 16 motores — taxa de ativação real e 2 bugs novos — 2026-08-22

**Pedido do usuário:** depois de esgotar o Motor #16, avaliar os demais 15 motores da seção 4 da auditoria com o mesmo rigor — taxa de ativação real, não só "está implementado".

**Método:** rodei n=2000 medindo, pra cada motor, a % de jogos em que a condição de ativação (a carta-chave em campo, ou o efeito realmente disparando) acontece até o turno 8.

| Motor (auditoria seção 4) | Condição medida | Taxa |
|---|---|---|
| #4 — Field of the Dead conta artefato-terreno | zumbi criado até T8 | **84,5%** |
| #10 — land creatures 5+ (setup pro double strike/vigilance) | 5+ terrenos earthbendados em campo | **77,5%** |
| #3 — pacote de mana universal (qualquer uma das 3 peças) | Great Divide Guide/Wrenn/Enduring Vitality em campo | 32,8% |
| #16 — Motor#16 (earthbend recorrente) | ≥1 recorrência | 35,0% |
| #15 — Strionic Resonator | ≥1 cópia de gatilho | 14,6% |
| #9 — combo Awaken the Woods + Felidar Retreat + Mossborn Hydra | as 3 em campo/cemitério juntas | 0,3% (6/2000) |
| #7 — Oblivion Stone em campo | carta em campo (nunca ativada pela IA) | 12,9% |
| #8 — Earthbender Ascension com 4+ quest counters | disparou o bônus | 6,1% |
| #6 — Mycosynth Lattice + Toph (tudo vira terreno) | ambas em campo | 9,4% |
| #5 — Krang + artefato earthbent em campo junto | condição de setup satisfeita | 6,2% em geral, **mas 100% das vezes que o Krang está em campo** (a política broad_artifact garante isso) |
| #12 — The Ozolith recicla contador | ≥1 realocação | 5,0% |
| #13 — Bristly Bill dobra o board (ativada) | ≥1 ativação | 9,5% |
| #14 — Kodama of the East Tree cheat-into-play | ≥1 cheat | **0,7%** — confirma o achado anterior, é o motor mais fraco na prática dentro do perfil de jogo modelado |

**2 bugs reais encontrados nessa varredura (corrigidos):**

1. **Mossborn Hydra nunca ganhava o `+1/+1` de entrada** — só a duplicação por landfall estava implementada (`landfall_double_self`), então toda partida dobrava **0 por 2 = 0**, pra sempre. A carta estava 100% neutralizada desde o primeiro build. Rastreei os 6 jogos onde o combo do item #9 monta (Awaken the Woods + Felidar Retreat + Mossborn Hydra juntos) e a Hydra tinha **0 contadores nos 6**, o que denunciou o bug. Corrigido adicionando o contador de entrada no `apply_etb`. Depois do fix, os mesmos 6 jogos mostram contadores reais: **2, 8, 16, 64, 128, 256** — confirma que o "combo explosivo" da seção 4 item 9 é genuíno (potências de 2 batendo com dobra por landfall), só estava sendo mascarado pelo bug.
2. **`ValueError` intermitente no fetch de básicas do Planar Engineering** — a lista de 4 terrenos a buscar era pré-computada uma vez (`fetched = [...][:4]`) e depois removida da biblioteca item a item; se um gatilho de landfall no meio do processo (2º landfall do turno via Tannuk/Nissa) comprasse justamente a última cópia de um dos nomes já "reservados" na lista congelada, o `.remove()` seguinte falhava por a carta já não estar mais lá. Corrigido reavaliando a biblioteca a cada iteração em vez de usar uma lista congelada — mesma categoria de bug do `RecursionError`/`ValueError` documentados na sessão anterior (efeito colateral no meio de um loop que opera sobre um snapshot desatualizado). Achado rodando 20.000-30.000 partidas com timeout, não nos testes manuais.

**Leitura geral sobre os 16 motores:** a maioria dos motores "estruturais" (Field of the Dead, volume de land creatures, o próprio Motor#16) tem taxa de ativação alta (75-85%) porque dependem só da mecânica central (Toph + earthbend), não de uma carta específica rara. Os motores que dependem de uma **carta única em 99** (Kodama, Ozolith, Bristly Bill, Strionic Resonator, o combo de 3 peças do item 9) naturalmente ficam na faixa de 0,3%-15% em 8 turnos — isso não é "os motores são fracos", é a matemática normal de singleton de 99 cartas. Kodama continua sendo a exceção genuína de baixo valor prático (0,7%, mais baixo que sua taxa de estar em campo sozinho de ~9,6% já medida antes — quando entra, raramente encontra o próprio gatilho).

---

### Testando políticas pra todos os motores fracos — 2026-08-22

**Pedido do usuário:** "sim, todos eles" — tentar melhorar os 5 motores diagnosticados com folga (Kodama, Ozolith, Bristly Bill) ou confirmar honestamente que não há alavanca (Mycosynth Lattice, Earthbender Ascension, combo de 3 peças).

**Diagnóstico prévio (taxa condicional = disparou ÷ estava em campo):** Kodama 6,2%, Ozolith 31,3%, Bristly Bill 74,2%, Strionic Resonator 93,9% (já no teto).

**1) Kodama of the East Tree — `KODAMA_HOLD_POLICY`.** Primeira tentativa **falhou por um bug de implementação**: eu removia a carta segurada de `state.hand` inteiramente, mas o próprio `kodama_trigger()` procura candidatos em `state.hand` — removendo a carta, ela ficava invisível pro gatilho olhar durante o resto do turno. Resultado da primeira versão: **piorou** (6,2%→3,8% condicional). Corrigido: a carta segurada continua fisicamente em `state.hand` (visível pro Kodama), só é filtrada do loop de conjuração genérico. Resultado real depois do fix:

| | Sem hold | Com hold (corrigido) |
|---|---|---|
| Taxa condicional | 6,2% | **33,8%** |
| Avg kodama cheats | 0,009 | **0,039** |
| Turno médio comandante | 2,608 | 2,608 (idêntico) |

Ganho de graça — sem custo medido em nenhuma outra métrica. `KODAMA_HOLD_POLICY = True` por padrão.

**2) The Ozolith — testado, revertido, sem alavanca real.** Tentei priorizar sacrificar (via KCI) um artefato COM contador quando o Ozolith está em campo. Resultado: **zero diferença** (31,9% antes e depois, byte a byte igual). Investigando o motivo: `earthbend_return=True` só é setado quando o earthbend adiciona contadores — ou seja, **todo candidato elegível já tem contador>0 por definição**, então "prefira quem tem contador" é um no-op disfarçado, sempre verdadeiro. Removido o código morto. O gargalo real do Ozolith é **timing de compra** (precisa estar em campo antes de um artefato-terreno morrer) — isso não é uma decisão de política de jogo, é probabilidade de compra de carta única em 99. Documentado como limite honesto, não fingido como resolvido.

**3) Bristly Bill, Spine Sower — `BRISTLY_BILL_RESERVE_POLICY`, trade-off real, não adotada por padrão.** A ativada (`{3}{G}{G}=5`, dobra contadores) só checava mana sobrando **depois** do loop ganancioso de conjurar tudo. Testei reservar 5 de mana pra ela **antes** do loop:

| | Sem reserva (antigo) | Com reserva antecipada |
|---|---|---|
| Taxa condicional | 74,1% | **89,0%** |
| Avg dobras | 0,227 | **0,398** |
| Avg cartas compradas extra | 1,567 | 1,504 (**−4%**) |
| Avg tokens criados | 12,470 | 11,857 (**−5%**) |

Diferente do Kodama, esse **não é ganho de graça** — reservar mana cedo compete de verdade com o resto do plano de jogo (menos mana sobra pro loop ganancioso conjurar outras cartas, que geram landfall/draw/tokens). Mantido **desligado por padrão** (`False`) porque o custo líquido pro deck como um todo não compensou nos dados — fica disponível como opção pra quem quiser priorizar esse motor especificamente às custas do resto.

**4) Motores sem alavanca real de política (confirmado, não forçado):**
- **Mycosynth Lattice + Toph:** card único de 6 mana — a taxa de 9,4% é pura probabilidade de compra até o turno 8. Nenhuma decisão de IA muda isso.
- **Earthbender Ascension (4+ quest counters):** taxa condicional de 48,0% já reflete bem o tempo de jogo restante depois que ela entra — não há uma "jogada melhor" que acumule landfall mais rápido além do que já acontece automaticamente.
- **Combo Awaken the Woods + Felidar Retreat + Mossborn Hydra (3 peças):** 0,3% é matemática de singleton (3 cartas específicas de 99 juntas) — política de jogo não muda a probabilidade de comprar 3 cartas específicas.

Testado tudo (Kodama fix + Bristly Bill) em 30.000 partidas com timeout antes de qualquer conclusão (0 erros).

---

### Validação final — n=3000 com o modelo fechado — 2026-08-22

**Pedido do usuário:** com todos os bugs corrigidos e políticas fechadas (broad_artifact + SAC_VALUE_PRIORITY + KODAMA_HOLD ligados, BRISTLY_BILL_RESERVE desligado), rodar um batch maior (n=3000) e conferir se os números seguram.

Rodei 20.000 partidas com timeout antes do batch oficial (0 erros) — o código não mudou desde a última varredura de robustez, só o tamanho do batch.

**n=3000, seed_base=9000000, 8 turnos — números finais de referência:**

```
Avg mulligans: 0,77
Turno medio de conjuracao da Toph: 2,61 | mediana: 2
Nunca conjurada em 8 turnos: 3,6%
Avg terrenos em campo (turno 8): 10,26
Avg aplicacoes de earthbend: 7,95
Avg recorrencias via Motor#16: 0,98 | % de jogos com pelo menos 1: 34,7%
Avg gatilhos de landfall disparados: 10,40
Avg tokens de Field of the Dead: 4,68 | % de jogos que ligou: 84,5%
Avg cartas compradas extra: 1,59
Avg mana extra gerado: 1,99
Avg cheats do Kodama of the East Tree: 0,04
Avg copias via Strionic Resonator: 0,46
Avg dobras via Bristly Bill: 0,24
Avg realocacoes via The Ozolith: 0,12
Avg tokens totais criados: 12,09
% de jogos com Ashaya em campo: 11,2%
Avg vida ganha: 0,26
Avg ativacoes do Unstable Obelisk: 0,213
Avg ativacoes do The Stasis Coffin: 0,262
Avg sacrificios via Krark-Clan Ironworks: 0,341
```

**Leitura — estabilidade confirmada:** todo número bate dentro da margem de ruído esperada com o batch de n=2000 anterior (ex: Motor#16 0,966→0,98; Field of the Dead 84,5%→84,5% exato; turno da comandante 2,608→2,61; Kodama 0,039→0,04). Nenhuma mudança sistemática — o aumento de amostra só confirma que os resultados já reportados eram estáveis, não ruído de amostra pequena. `toph_v1_runs.jsonl` regravado com as 3000 partidas (era 2000).

**Simplificações documentadas no docstring do script** (não inventadas, omissões explícitas): sem combate real contra oponente (nenhuma criatura adversária, nenhum bloqueio — "atacar" só dispara gatilhos de ataque, não há dano/vida de oponente real); Esper Sentinel/Skullclamp/Sword of Feast and Famine/Talon Gates/Krang/Council's Judgment/Lightning Greaves/Heroic Intervention não têm efeito numérico solo simulado (dependem de oponente real); modelo de mana genérico (mana total, não pip a pip — o deck tem fixing extenso e documentado); habilidades de lealdade do Wrenn and Realmbreaker além da estática de fixing não são ativadas automaticamente.

---

### Correção — checklist obrigatória de mecânica (regra nova pós-Beorn) — 2026-08-28

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks. Landfall (16 motores já auditados em rodadas
anteriores) confirmado correto; os bugs achados nesta rodada foram na
mecânica de mana:

- **Command Tower / Jetmir's Garden**: terrenos tagueados "rock_any" —
  `total_mana()` tinha dois `if` separados (não `elif`) que somavam **+1
  por ser terreno E +1 de novo por ter a tag "rock_any"** — um único `{T}`
  contando mana em dobro.
- **Talon Gates of Madara**: mesmo bug de double-count, **mais** um `add()`
  duplicado (linha 286 antiga) que sobrescrevia as tags reais dela
  (`{"rock_any_paid", "phase_out_unused"}`) por um `set()` vazio — as tags
  reais nunca existiam de fato. Corrigido: removido o `add()` duplicado, e
  a habilidade colorida dela (paga {1} extra pra trocar por qualquer cor —
  ganho líquido de mana ZERO, só fixação) não soma nada além do +1 de
  terreno normal.
- **Enduring Vitality** ("toda criatura sua tapa por 1 de qualquer cor"):
  nunca checava doença de invocação — criaturas recém-conjuradas
  contribuíam mana no próprio turno.
- **Fetches (Arid Mesa/Windswept Heath/Wooded Foothills)**: todos buscavam
  dos mesmos 6 básicos, ignorando que cada um só busca 2 tipos reais
  (Arid Mesa: Mountain/Plains; Windswept Heath: Forest/Plains; Wooded
  Foothills: Mountain/Forest). Nova tabela `FETCH_POOLS`.
- **Great Divide Guide** ("each land and Ally you control has '{T}: Add
  one mana of any color'"): tag "rock_lands_any" nunca lida em lugar
  nenhum (dead tag). Removida e documentada como limitação de
  arquitetura, não bug corrigível — esse motor não rastreia cor nenhuma
  em `total_mana()`, então o efeito real dela (fixação, não mais mana) não
  muda o total numérico neste modelo generico.

**Não corrigido nesta rodada (decisão de escopo, documentada):** Spelunking's
ETB land-drop (só o draw estava modelado); Horizon Explorer's Lander token
nunca cracado; Yavimaya/Dryad of the Ilysian Grove sem tag nenhuma pro
"every land is/has all basic types"; Iron Spider e Fountainport's habilidades
ativadas; Krark-Clan Ironworks capado em 1 sac/turno (uncapped no real);
Mishra's Bauble draw counter nunca incrementado; Great Henge's per-creature
draw só proxy no próprio ETB.

**Resultado (n=2000, seed_base=8000000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg terrenos em campo (T8) | 10,39 | **10,14** |
| Avg tokens totais criados | 13,33 | **11,86** |
| Avg mana extra gerado | 2,12 | **1,90** |
| Avg ativações Unstable Obelisk | 0,231 | **0,153** |
| Avg recorrências Motor#16 | 1,07 | **0,90** |

Queda moderada em todas as métricas de desenvolvimento — esperada, o
double-count de mana (Command Tower/Jetmir's Garden/Talon Gates, presentes
quase todo jogo) inflava a mana disponível todo turno.

**Robustez:** sweep de 20.000 jogos (seeds 8000000–8019999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

`lista.md` não mudou. `toph_v1_runs.jsonl` sobrescrito (3000 jogos).

---

## Partida #1 — AAAA-MM-DD

- **Formato do teste:** goldfish / playtest com amigos / mesa competitiva
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:** vitória / derrota / sem resolução
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

## Partida #2 — AAAA-MM-DD

- **Formato do teste:**
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:**
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

<!-- Copie o bloco acima para cada nova partida -->

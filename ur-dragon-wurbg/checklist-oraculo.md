# Checklist cláusula-a-cláusula — The Ur-Dragon (`urdragon_goldfish_v1.py`)

## Bug real de orquestração de turno: wipe e ataque no mesmo turno de oponente — 2026-09-20

**Gatilho:** mesmo achado do usuário aplicado ao Megatron primeiro —
board wipe é sorcery (main phase de UM oponente), ataque vem de
criatura em campo DAQUELE MESMO oponente. Se o wipe for simétrico, ele
não ataca no mesmo turno. Regra #6 do CLAUDE.md (bug de orquestração,
não pego em auditoria carta-a-carta). Raciocínio e validação completos
em `megatron-tyrant-mardu/checklist-oraculo.md` — aqui só o resultado
específico deste deck.

**Corrigido:** `try_smart_opponent_turn()` simula o turno de 1 oponente
por vez (`NUM_OPPONENTS = 3` por rodada, nova constante — este deck
não tinha essa convenção antes, adotada agora igual ao Megatron), wipe
e ataque mutuamente exclusivos dentro do MESMO turno de oponente.

**Validação:** teste dirigido (2000 seeds, exclusão mútua 100%) +
regressão de 20.000 partidas, 0 exceções + modo padrão confirmado
intocado (nenhuma função compartilhada tocada).

**Resultado (batch 2000 jogos mesma seed):**

| Métrica | Modelo antigo (1 rolagem/rodada) | Modelo novo (3 turnos/rodada) |
|---|---|---|
| Avg board wipes sofridos | 0,43 | 0,87 |
| Graveyard wipe sofrido (partidas) | 41,3% | 72,2% |
| Avg remoções inteligentes sofridas | 0,83 | 1,26 |
| Nunca resolveu em 8 turnos | 31,6% | 45,0% |
| Avg dano proxy total | 310,33 | 43,29 |

Queda MUITO mais acentuada que a do Megatron (310→43, ~14% do valor
anterior) — este deck depende inteiramente da comandante resolver E
atacar pra qualquer dano real, e com 3 turnos de oponente reais por
rodada em vez de 1 rolagem agregada, a chance dela nunca resolver
subiu de 31,6% pra 45,0%.

## Modo de resiliência portado do Megatron (6 categorias de interação de oponente) — 2026-09-20

**Gatilho:** usuário pediu pra avaliar o esforço de portar o modo de
resiliência (implementado no Megatron, várias rodadas 2026-09-19/20)
pro resto dos decks. Avaliação usando o Hei Bai como piloto mostrou 2
lacunas estruturais sérias lá (sem `sacrifice()` central, sem combate
modelado nenhum). Usuário então pediu pra implementar de verdade no
Ur-Dragon, com resultado **separado do goldfish atual, preservando o
original**.

**Arquitetura preservada:** `simulate_one`/`run_batch` continuam
exatamente como sempre foram — confirmado com **5.000 seeds de
equivalência bit-a-bit** (`commander_cast_turn`,
`commander_cast_count`, `proxy_damage_total`, `commander_damage_dealt`,
`cards_drawn_extra`, `dragon_tokens`), 0 diferenças, mesmo mexendo em
`cast_card`/`enter_battlefield` (funções compartilhadas pelos 2 modos).
Todo o modo novo mora em `simulate_one_with_interaction`/
`run_batch_with_interaction`, funções NOVAS, nunca chamadas pelo
goldfish padrão.

**Diferenças reais do port vs. o Megatron original (não foi
copy-paste):**

1. **Sem `sacrifice()` preexistente** — o motor do Ur-Dragon é ETB/
   ataque, não sacrifício. `remove_permanent()` é uma versão nova e
   mais simples: grep confirmou **0 cartas "whenever ~ dies"** neste
   deck, então não existe web de gatilhos de morte pra replicar (era o
   grosso da complexidade do `sacrifice()` do Megatron). Só precisa
   saber mandar o comandante pra zona de comando (mesmo padrão já
   usado no retorno do Hellkite Courser em `end_step`) em vez do
   cemitério.
2. **Sem `toughness` rastreado por criatura** — o `Card` deste arquivo
   só tem `power` (motor só precisa de poder de saída, nunca modelou
   bloqueio pro lado do jogador). Isso torna **bloqueio impossível de
   implementar sem inventar dado que não existe** — `try_smart_
   opponent_attack` aqui nunca é bloqueado, todo ataque conecta direto
   em `state.life` (novo, só existe pro modo de resiliência — o
   goldfish padrão documenta explicitamente "Vida não é rastreada no
   simulador", convenção preservada 100%).
3. **Sem `state.rng` guardado no state** — nenhuma carta tipo
   Blightsteel Colossus (Megatron) achada nesta rodada. `put_into_
   graveyard()` existe como rede de segurança central, mas **isso NÃO
   é uma auditoria completa das 99 cartas** procurando "would be put
   into a graveyard from anywhere" — só o Megatron recebeu essa
   auditoria até agora.
4. **Alvo do graveyard snipe é Dragão-específico**: usa o MESMO
   critério que `reanimate_dragons_from_graveyard()` (Haunting Voyage)
   já usa — maior MV entre Dragão-criatura no cemitério — em vez do
   critério criatura/artefato genérico do Megatron, porque a recursão
   real deste deck é de Dragão, não de artefato.
5. **`INTERACTION_ENGINE_PRIORITY` curada do zero** pros motores reais
   do Ur-Dragon: Roaming Throne (dobra tudo, prioridade 1), Dragon
   Tempest, Scourge of Valkas, Herald's Horn, Smothering Tithe,
   Dragon's Hoard, Up the Beanstalk, Elemental Bond, Garruk's Uprising,
   Sylvan Library.
6. **Counterspell** — mesmo padrão do Megatron: taxa de comandante
   (CR 903.10a, já existia neste arquivo como `commander_cast_count`)
   incrementada ANTES do check de counter (conta "vezes conjurado",
   não "vezes resolvido"); movido de `enter_battlefield` pra
   `cast_card` pra evitar incremento duplicado. Hookado direto no
   branch `if name == COMMANDER` de `cast_card()`.

**Validação:** 8 testes unitários dirigidos (gating; board wipe destrói
tudo e manda comandante pra zona de comando; removal mira a peça de
maior prioridade presente; ataque sempre conecta — sem bloqueio; discard
aleatório; graveyard wipe dispara 1x só; graveyard snipe mira Dragão de
maior MV; counterspell gasta mana+taxa mas não resolve, e recast no
turno seguinte paga taxa mais alta) + 5.000 seeds de equivalência
bit-a-bit do modo padrão (0 diferenças) + smoke test (batch 2000) +
**regressão de 20.000 partidas em CADA modo, 0 exceções nos dois**.

**Resultado real (batch 2000 jogos mesma seed, padrão vs. resiliência):**

| Métrica | Padrão | Resiliência |
|---|---|---|
| Turno médio de conjuração (que resolveu) | 6,66 | — |
| Nunca resolveu em 8 turnos | 21,3% | 31,6% |
| Avg dano/perda-de-vida proxy total | 990,50 | 310,33 |
| Avg counterspells sofridos | — | 0,10 |
| Avg board wipes sofridos | — | 0,43 (5,25 criaturas perdidas quando dispara) |
| Partidas com graveyard wipe sofrido | — | 41,3% (máx. 1x/partida) |
| Avg graveyard snipes sofridos | — | 0,15 |
| Avg remoções inteligentes sofridas | — | 0,83 (Roaming Throne 16,1%, Dragon Tempest 14,4%) |
| Avg ataques de oponente sofridos | — | 1,26 |
| Avg descartes forçados sofridos | — | 1,21 |

Direção esperada em tudo: a comandante resolve 10,3pp menos vezes em 8
turnos e o dano proxy cai pra menos de 1/3 (990,50→310,33) — bate com o
quanto o motor inteiro deste deck depende da Ur-Dragon resolver E
atacar (Roaming Throne/Dragon Tempest/Scourge of Valkas, os alvos mais
removidos, são multiplicadores centrais — perde-los corta o motor de
dano escalável pela raiz).

## Achado real 2026-09-14 (usuário perguntou se Roaming Throne está certa em todos os decks onde aparece)

Mesma varredura pedida depois do fix do Beorn. Este deck já tinha uma
arquitetura mais madura pra Roaming Throne (`ROAMING_THRONE_TYPE =
"dragon"`, tag cravada diretamente no `CARD_DB` da própria carta — bem
melhor que o Beorn original), mas isso trouxe um problema DIFERENTE: como
`is_dragon(name)` só olha a tag estática, ela reconhece Roaming Throne
como Dragão mesmo enquanto ela está só na **biblioteca ou na mão** — onde
o oráculo real não concede tipo nenhum ainda ("as this creature enters,
choose a creature type" só se aplica depois de resolver). Achei **5
pontos reais** de busca/tutor de Dragão fora do campo de batalha que
incorretamente aceitavam Roaming Throne como se fosse "a Dragon creature
card":

1. **Sarkhan's Triumph** ("search your library for a Dragon creature
   card, put it into your hand") — podia tutorar a própria Roaming
   Throne.
2. Métrica auxiliar do mesmo Sarkhan's Triumph (`sarkhan_triumph_hand_had_no_dragon`)
   — checava a mão por um "Dragão" incluindo Roaming Throne.
3. **Orb of Dragonkind** (checagem "tem Dragão na mão?") — mesma coisa.
4. **Orb of Dragonkind** (tutor pela ativação de sacrifício) — mesma coisa.
5. **Sarkhan Unbroken**, ultimate (−8: "put all Dragon creature cards
   from your library onto the battlefield") — o mais grave dos 5, porque
   não é um tutor de 1 carta, é um mass-cheat: colocaria a Roaming Throne
   em campo de graça igual a qualquer Dragão de verdade.

**Não é bug** (verificado e mantido): o tutor da **Magda** (sacrificar 5
Treasures → "search for an artifact or Dragon creature card") continua
encontrando Roaming Throne normalmente — mas isso está CORRETO, porque
Roaming Throne também é um artefato de verdade (`is_artifact_card`),
então o modo "artifact card" da busca genuinamente a alcança, independente
de ser Dragão ou não.

**Corrigido:** novo helper `is_dragon_card(name)` (= `is_dragon(name) and
name != "Roaming Throne"`), usado nos 5 pontos acima que buscam fora do
campo de batalha. `is_dragon()` puro continua reconhecendo Roaming Throne
normalmente pras checagens de BATALHA (contagem de Dragões em campo, a
própria dobra do gatilho dela via Roaming Throne — que já estava correta
antes, essa parte não mudou).

**Validação:** 2 testes unitários dirigidos (Sarkhan's Triumph tutora um
Dragão real quando disponível, ignorando Roaming Throne; sem Dragão real
na biblioteca, não tutora nada — não usa Roaming Throne como substituto)
— passando. Batch de 2.000 partidas antes/depois (mesma seed 7500000):
`tutors_used_total` 0,3935→0,398; `orb_mana_activations_total`
0,4675→0,4585; `dragons_free_entry_total` 1,1575→1,1495 — movimento
pequeno (cenário raro: só importa quando Roaming Throne seria o único ou
o de maior MV entre os "Dragões" candidatos). 20.000 partidas de
regressão (seed 7600000+), **0 exceções**.

---

## Auditoria oráculo-por-oráculo completa — 2026-09-14

Extensão pra este deck da mesma auditoria já feita em Beorn/Captain
Storm/Rat King/Prismatic Bridge/Toph/Edgar Markov/Hei Bai/Maralen/
Megatron/Nekusar/Thranduil nesta sessão. Este já era um dos simuladores
mais auditados da sessão (rodadas em 2026-08-27, 2026-08-29, 2026-08-30 e
2026-09-01, ver seção abaixo com o gap daquela última rodada — Lightning
Greaves). Mesmo assim, a releitura clause-by-clause do oráculo real
(Scryfall `/cards/collection`, 100 nomes — comandante + 71 cartas de
deck + 36 terrenos incluindo as 8 registradas só pra teste comparativo,
0 `not_found`) contra o `CARD_DB`/dispatch real achou **2 gaps reais
adicionais**, ambos em mecânicas centrais do tema tribal (escala por
contagem de Dragão / dobra de Roaming Throne), a mesma classe de bug já
achada em Beorn (anthem estático não propagado) e Rat King (contagem de
tribo mal disparada).

**Método:** (a) detecção automatizada de tags órfãs (definidas em `add()`,
nunca lidas fora dele) — achou 20 candidatos, **todos falsos positivos**
confirmados lendo o dispatch real (por nome, dentro de funções
compartilhadas como `dragon_enters()`/`creature_etb_hooks()`/
`try_dragon_pumps()` — este arquivo já é maduro o bastante pra ter várias
dessas, mesmo padrão já documentado na rodada de 2026-09-01); (b)
releitura completa do oráculo de cada carta com gatilho "whenever a
Dragon enters/attacks" ou anthem/contador estático, comparando contra
TODAS as funções que leem `power`/dano/contagem de Dragão (não só a
primeira que aparece), atrás do padrão "efeito estático aplicado em UMA
função mas não propagado pras outras que leem o mesmo dado" (mesma classe
do Beorn) e "cascata de gatilho compartilhada só parcialmente
correta" (mesma classe do Rat King/Prismatic Bridge).

### 🐛 Os 2 gaps reais corrigidos nesta rodada

1. **Roaming Throne dobrava a fonte ERRADA de dano em `dragon_enters()`
   — Dragon Tempest sendo dobrado quando NUNCA deveria, Scourge of Valkas
   deixando de dobrar exatamente quando deveria.** Oráculo real da
   Roaming Throne: *"If a triggered ability of ANOTHER CREATURE you
   control of the chosen type triggers, it triggers an additional
   time."* A restrição é sobre a FONTE da habilidade ser uma criatura
   (diferente da própria Roaming Throne) — não tem nada a ver com QUAL
   Dragão causou o gatilho disparar. O código anterior tratava Scourge of
   Valkas (`"Whenever this creature or another Dragon you control
   enters... X damage"`, criatura Dragão) e Dragon Tempest (`"Whenever a
   Dragon you control enters... X damage"`, **encantamento**, não
   criatura) como UMA única fonte combinada (`dmg_sources`), com o mesmo
   multiplicador `total_times = times_scourge if (name !=
   "Scourge of Valkas") else 1` — comparando contra o NOME DO DRAGÃO QUE
   ENTROU, não contra a fonte da habilidade. Isso já contradizia o padrão
   correto usado no próprio arquivo em `combat_step()` pros gatilhos de
   ataque (`times = 2 if (Roaming Throne in battlefield and n !=
   Roaming Throne) else 1`, que compara a FONTE). Dois erros reais na
   direção oposta:
   - **Dragon Tempest era dobrado sempre que Roaming Throne estava em
     campo** (superestimando dano em TODO evento de Dragão entrando, não
     um caso raro — o efeito mais impactante dos dois), quando o texto
     real da Roaming Throne nunca alcança um encantamento.
   - **Scourge of Valkas deixava de dobrar exatamente quando ELA MESMA
     era o Dragão entrando** (subestimando dano nesse caso específico —
     o "another" da Roaming Throne se refere a Scourge não ser a própria
     Roaming Throne, não ao Dragão que disparou o gatilho).
   Corrigido separando as duas fontes: Scourge dobra com Roaming Throne
   em campo (independente de qual Dragão entrou); Dragon Tempest nunca
   dobra (independente de Roaming Throne). Validado isoladamente (ver
   `goldfish-log.md`) — cenário só-Dragon-Tempest+Roaming-Throne não
   dobra mais; cenário só-Scourge+Roaming-Throne, com a própria Scourge
   entrando, agora dobra.

2. **The Great Henge — só metade do gatilho recorrente estava
   implementada (o draw, nunca o contador).** Oráculo real: *"Whenever a
   nontoken creature you control enters, put a +1/+1 counter on it AND
   draw a card."* `creature_etb_hooks()` já tinha o draw desde a rodada
   de 2026-08-27 (registrado no `goldfish-log.md` como correção da carta
   inteira), mas o `+1/+1 counter` real — que aumenta o PODER daquela
   criatura pelo resto do jogo — nunca tinha sido rastreado em lugar
   nenhum. Isso subestimava poder em TODO gatilho power-dependente do
   arquivo que usa `effective_power()`: Elemental Bond/Garruk's
   Uprising/Temur Ascendancy (thresholds de poder pra compra), Terror of
   the Peaks (dano = poder da criatura que entrou), Klauth (soma do poder
   de todos os Dragões atacantes), Return of the Wildspeaker (maior poder
   entre não-Humanos), e o próprio custo dinâmico da Great Henge pra
   qualquer avaliação futura de "maior poder em campo". Corrigido com
   `state.great_henge_counters` (dict por nome, mesmo padrão de
   contadores agregados já usado pra Marwyn/Immaculate Magistrate no
   arquivo irmão `thranduil_goldfish_v1.py`) — incrementado em
   `creature_etb_hooks()` junto do draw já existente, lido em
   `effective_power()` (que já centralizava o anthem estático da
   Morophon, agora soma os dois). ~2.19 contadores/partida em média — não
   é um efeito marginal.

### Falsos positivos descartados (tags órfãs, 20 candidatos, 0 gaps reais)

Todas as 20 tags reportadas pela detecção automatizada (`tribal_impulse`,
`dragon_hoard`, `dragon_tutor_sac`, `kindred_discovery`,
`sarkhan_unbroken`, `reanimate_dragon_etb`, `upkeep_dragon_token`,
`goldspan`, `extra_combat_paid`, `dragon_etb_token`, `dragon_etb_copy`,
`ramos_counters`, `creature_etb_damage_power`, `treasure_tutor_dragon`,
`first_creature_discount`, `power4_draw_optional`, `cost_reduce_power`,
`opponent_dependent`, `treasure_tax`, `roaming_throne`) são rótulos
descritivos — a carta correspondente é despachada de verdade por
checagem de NOME dentro de uma função compartilhada (`dragon_enters()`,
`creature_etb_hooks()`, `resolve_etb()`, `combat_step()`,
`try_dragon_pumps()`, `try_dragon_hoard_draw()`, `try_haven_recursion()`,
`do_magda_treasures()`, `do_orb_dragonkind()`, `main_phase()`,
`upkeep_step()`, `effective_cost()`/`rocks_mana()`), não pela tag em si —
confirmado lendo cada dispatcher, não só contando ocorrências de string
(mesmo cuidado documentado na rodada de 2026-09-01).

### Dragonlord Dromoka — clásula confirmada 📊 (não é gap novo)

*"Your opponents can't cast spells during your turn"* — puramente
dependente de oponente real (sem contramagia/timing de oponente
modelado neste goldfish solo), mesma classe já documentada pra Cavern of
Souls ("can't be countered")/Balefire Dragon (limpeza de board de
oponente)/Rhythm of the Wild (creature spells can't be countered).
Flying/lifelink já cobertos pela abstração de combate existente (lifelink
não numérico — vida não é rastreada no simulador, mesma premissa de
sempre).

---

## Resumo numérico (rodada 2026-09-14)

- **99 cartas na lista afinada** (`lista.md`) + comandante, mais 8
  cartas registradas só pra testes comparativos fora da lista atual.
- **🐛 Corrigido nesta rodada:** 2 gaps (Roaming Throne dobrando fonte
  errada em `dragon_enters()`; The Great Henge sem o `+1/+1` contador
  real).
- **✅ Falsos positivos descartados:** 20 tags órfãs, todas já
  corretamente dispatchadas por nome.
- **📊 Estrutural confirmado (sem mudança de código):** Dragonlord
  Dromoka ("opponents can't cast spells during your turn").

---

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge, Rat King, Thranduil e Ulalek.

**Contexto importante:** este simulador já tinha passado por múltiplas
rodadas de auditoria completa antes desta (2026-08-27, 2026-08-29,
2026-08-30 — documentadas extensivamente em `goldfish-log.md`), incluindo
correções reais de haste/summoning sickness, lealdade de Sarkhan Unbroken,
Haunting Voyage foretell, etc. **Este deck tem 2 simuladores** —
`urdragon_goldfish_v1.py` (lista "afinada", `lista.md`) e
`urdragon_goldfish_physical_v1.py` (deck físico real, `lista-fisica.md`,
com 3 cartas extras registradas só nesse arquivo). Esta auditoria cobriu o
arquivo principal (`urdragon_goldfish_v1.py`); o físico herda a mesma
base de código e as mesmas correções onde as cartas coincidem.

**Método:** detecção automatizada de (a) tags órfãs e (b) nomes de carta
com poucas ocorrências. ~26 candidatos apareceram; a esmagadora maioria
eram falsos positivos (dispatch por nome dentro de funções compartilhadas
como `dragon_enters()`, `try_dragon_pumps()`, `ready_creatures()` — este
arquivo já é maduro o bastante pra ter várias dessas). **1 gap real
confirmado.**

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real, sem combate/P-T por criatura
  individual — limite conhecido, não julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 O gap corrigido nesta rodada

**Lightning Greaves** — tinha só a tag genérica `"interaction"` (bucket
de proteção do próprio board), **sem nenhum efeito real implementado**
— nem sequer o haste, que é o ganho mais relevante possível pra este
deck especificamente: a Ur-Dragon não tem haste nativo, e o motor
inteiro de compra de cartas do deck (*"Whenever one or more Dragons you
control attack, draw that many cards..."*) depende dela atacar. Oráculo
real: *"Equipped creature has haste and shroud. Equip {0}."* Corrigido
com `try_lightning_greaves_equip()` — equipa automaticamente na
comandante assim que ambas estão em campo (Equip {0}, sem custo real),
reequipa em outra criatura se a comandante ainda não resolveu, e
re-equipa automaticamente se o alvo anterior saiu de campo. `shroud` não
tem efeito modelável (sem oponente/remoção alheia neste goldfish solo)
— 📊, documentado.

Este arquivo já modela haste/summoning-sickness de forma sofisticada
(`ready_creatures()`, tags `haste`/`haste_all`/`haste_flying`/`riot`)
desde a rodada de 2026-08-27 — o gap era especificamente a ausência total
de qualquer lógica de equipamento pra essa carta, não um limite do
motor de haste em si.

Validado com 4 testes unitários isolados + regressão de 20.000 partidas
(seed 4000000+, turns=10, 0 exceções) + `run_batch` antes/depois via
`importlib` (3000 jogos, seed 7000000, turns=10) — ver `goldfish-log.md`
pra métricas específicas.

## Falsos positivos descartados (já corretamente implementados)

- **Ancient Copper Dragon / Ancient Gold Dragon** — habilidades de d20
  (`combat_treasure_d20`/`combat_token_d20`) dispatchadas por tag numa
  função central de combate, não por nome — confirmado lendo o dispatch
  real, não só contando ocorrências do nome.
- **The Great Henge, Terror of the Peaks, Miirym, Lathliss, Dragon's
  Hoard, Orb of Dragonkind, Hellkite Charger, Radagast of Rhosgobel,
  Goldspan Dragon, Kindred Discovery, Temur Ascendancy, Ramos Dragon
  Engine, Bladewing the Risen, Sarkhan Unbroken, Smothering Tithe,
  Magda Brazen Outlaw, Herald's Horn, Dragon Broodmother** — todas
  dispatchadas por checagem de nome direta dentro de funções
  compartilhadas (`dragon_enters()`, `try_dragon_pumps()`,
  `resolve_etb()`, etc), confirmadas lendo o código, não a contagem
  ingênua de string.
- **Rhythm of the Wild** (tag `opponent_dependent`) — dispatchada de
  verdade (riot→haste, ver `ready_creatures()`); a tag em si é só um
  rótulo descritivo órfão, não indica ausência de efeito.
- **Mana Confluence** — terreno de mana genérica pura (produz qualquer
  cor, sem habilidade condicional adicional), corretamente sem tag
  extra.
- **An Offer You Can't Refuse, Heroic Intervention** — pacote
  "interaction", proxy consistente com o resto da sessão (conjuráveis,
  sem alvo de oponente real, `try_use_own_interaction()`).

## Sarkhan Unbroken — heurística de pilotagem (não um gap)

As 3 habilidades de lealdade estão todas implementadas (+1 draw+mana, -2
token de Dragão, -8 ultimate búsca todos os Dragões). A escolha de
"nunca usar o -2, sempre +1 até poder usar o -8" é uma heurística de
pilotagem racional documentada (token único não compensa desviar do
caminho pro ultimate) — não uma lacuna de implementação.

---

## Resumo numérico

- **99 cartas na lista afinada** (`lista.md`).
- **🐛 Corrigido nesta rodada:** 1 carta (Lightning Greaves).
- **✅ Falsos positivos descartados:** ~20 cartas/grupos, já corretamente
  implementadas via dispatch por nome ou por tag central.
- **📊 Estrutural confirmado:** shroud do próprio Lightning Greaves (sem
  oponente/remoção alheia modelada).

---

# Achado adicional — `urdragon_goldfish_physical_v1.py` estava QUEBRADO

Ao verificar se o mesmo gap do Lightning Greaves existia na variante
física (já que o docstring dela cita a carta explicitamente como
presente na caixa), a simples tentativa de `import` do arquivo **crashava
imediatamente** com `AssertionError: faltando no CARD_DB: Sarkhan
Unbroken` — ou seja, este segundo simulador não rodava UMA ÚNICA partida
desde que a variante física existe (`lista-fisica.md` data de
2026-08-29). Investigando mais a fundo (comparação sistemática de todo
nome em `lista-fisica.md` contra as chaves reais do `CARD_DB`, não só o
primeiro erro que aparecia), achei **3 cartas genuinamente ausentes do
CARD_DB apesar de estarem na lista física real**:

1. **Sarkhan Unbroken** — planeswalker inteiro faltando (nem `add()`, nem
   nenhuma lógica de lealdade). Corrigido registrando a carta e portando
   a mesma implementação real de lealdade (+1 draw+mana / -2 token / -8
   ultimate, heurística de pilotagem já validada) do
   `urdragon_goldfish_v1.py`.
2. **Mana Confluence** — terreno de mana genérica de qualquer cor,
   faltando por completo.
3. **Sundown Pass** — slow land real ("enters tapped unless you control
   two or more other lands"). Corrigido registrando a carta + portando a
   lógica `SLOW_LANDS` do arquivo principal pro `play_land()` local.

Além disso, apliquei o **mesmo fix do Lightning Greaves** (equipa na
comandante, concede haste real) nesta variante — a carta está
confirmada na caixa física pelo próprio docstring do cabeçalho.

**Bug adicional encontrado e corrigido, não relacionado ao crash:** os
dois arquivos escreviam no MESMO nome de arquivo de saída
(`urdragon_v1_runs.jsonl`) — rodar um dos dois simuladores por último
sobrescrevia silenciosamente o output do outro sem aviso nenhum.
Corrigido: a variante física agora escreve em
`urdragon_physical_v1_runs.jsonl` (arquivo novo, não sobrescreve nada).

**Validação:** 5 testes unitários isolados (import sem crash + Lightning
Greaves + Sarkhan Unbroken +1 uma vez por turno + Sundown Pass tapped/
destravado) + regressão de 200 partidas de sanidade + regressão completa
de 20.000 partidas (seed 5000000+, turns=10, 0 exceções). Como o arquivo
nunca tinha rodado uma partida sequer antes, não há uma comparação
antes/depois de métricas no sentido usual — a validação real É o arquivo
passar a rodar de ponta a ponta com números plausíveis (Dragon tokens
médios ~12.0, color screw em ~31% dos jogos — mesma ordem de grandeza do
arquivo principal, nenhum outlier suspeito).

**Escopo não coberto nesta rodada:** esta correção resolveu o crash e
portou os 2 gaps já identificados no arquivo principal (Lightning
Greaves, e agora Sarkhan Unbroken/Mana Confluence/Sundown Pass como
efeito colateral de destravar o import). Uma auditoria linha-a-linha
COMPLETA da variante física — cobrindo as cartas que só existem nela
(Scalelord Reckoner, Dragon's Hoard, Smuggler's Surprise, Magda Brazen
Outlaw, Firdoch Core) contra o oráculo real — **não foi feita nesta
rodada** e fica como trabalho futuro dedicado, na mesma categoria dos 4
decks sem simulador algum (não é uma decisão de valor, é reconhecer que
essa é uma tarefa de escopo comparável a auditar um deck inteiro à parte,
não um recorte que cabe dentro desta passada).

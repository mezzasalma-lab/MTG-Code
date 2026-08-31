# Goldfish Log — Vihaan, Goldwaker

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Simulação #1 — goldfish Python completo (`vihaan_goldfish_v1.py`) — 2026-08-22

**Contexto:** o usuário trouxe um script pronto gerado por ChatGPT pra essa mesma decklist, com resultado de n=500 já rodado. Antes de reaproveitar, revisei o código inteiro e encontrei **5 problemas reais que invalidavam a maior parte dos números reportados**:

1. **Mana nunca era gasta de verdade.** `pay_mana()` só descontava Treasure (via sacrifício); terreno e rock eram recalculados do zero a cada carta conjurada, sem nunca subtrair o que já tinha sido gasto naquele turno. Com 5 terrenos, o script conseguia conjurar cinco mágicas de 5 manas diferentes no mesmo turno — mana efetivamente infinita disfarçada. Isso explica os números inflados do relatório original (battlefield médio 14,34, dano de combate médio 79,23 por turno).
2. **Um "combo" que não existe** — `combo_check()` tratava Jan Jansen + Ashnod's Altar + Pitiless Plunderer como um loop infinito e, quando "montava" (0,4% dos jogos), zerava a vida dos 3 oponentes fictícios na hora. Conferi o oráculo real: as duas habilidades da Jan Jansen custam `{T}` sem nenhuma forma de destapar — no máximo 1 ativação de cada por turno, sem loop possível. Isso já tinha sido conferido (e não encontrado) na varredura de combo da auditoria (seção 9).
3. **Combate contra 3 oponentes fictícios de 40 de vida que nunca bloqueiam nem interagem** — o script reportava "39,6% mata pelo menos 1 oponente, 33,6% mata os 3" até o turno 8, simulando dano sempre desbloqueado contra alvos indefesos. Nenhum outro simulador desta biblioteca faz isso — combate real de oponente nunca é modelado, só os gatilhos de ataque/dano que geram recurso pro próprio jogador.
4. **Gatilhos reais e rastreáveis viraram sorteio de moeda** — Lotho (real: "quando um jogador conjura a 2ª mágica do turno", condição rastreável) usava `random() < 0.45`; mesmo problema no Orochi Soul-Reaver.
5. **Mahadi com timing errado** — o gatilho real é em lote no final do turno ("para cada criatura que morreu ESTE turno"), o script disparava por morte individual, na hora.

Dado isso, reconstruí a lógica de jogo do zero (mantendo só a decklist, que já batia com a auditoria), seguindo a arquitetura já estabelecida nos outros 4 simuladores deste repositório: mana rastreada de verdade turno a turno, sem vida de oponente fictícia, gatilhos implementados a partir do oráculo real.

**Passo 0** (varredura mecânica no oráculo completo): 40 cartas com gatilho real. Todas conferidas contra a lógica implementada; as opponent-dependentes (Smothering Tithe, Monologue Tax, Mari, Revel in Riches morte-de-criatura-do-oponente, Grenzo goad) documentadas como tal, não fingidas.

**3 bugs reais encontrados e corrigidos durante o build** (achados rodando 20-30 mil partidas com timeout antes do batch oficial, não em teste manual):

1. **Treasure Vault (terreno) sendo conjurado como se fosse mágica** — mesmo bug clássico já visto no Toph e no Edgar Markov: o loop genérico de conjuração não excluía terrenos (mv=0, sempre "pagável"). Corrigido filtrando `n not in LAND_NAMES` no loop de castables.
2. **Cascade descartando a própria carta que estava sendo conjurada** — quando o Rain of Riches dá cascade num spell com custo adicional de descarte (Big Score/Unexpected Windfall), o cascade acontecia ANTES da carta original sair da mão, então o "descarte uma carta" do spell cascadeado podia acabar descartando a própria carta original (ainda presa na mão), causando `ValueError` no `.remove()` seguinte. Corrigido reordenando `cast_card()`: a carta sai da mão (ou vai a campo) antes de qualquer efeito colateral (cascade, Lotho) rodar.
3. **Métrica "cartas compradas extra" inflada pela compra normal do turno** — a compra obrigatória de cada turno usava a mesma função `draw_cards()` das compras-bônus dos motores, contando as duas juntas (média reportada de 8,17). Corrigido usando compra direta (`state.hand.append(...)`) pra compra normal, reservando `draw_cards()`/o contador pra compras de motor de verdade — a média real caiu pra 1,17.

**n=2000, seed_base=5000000, 8 turnos — resultado final:**

```
Avg mulligans: 0,59
Turno medio de conjuracao do Vihaan: 3,17 | mediana: 3
Nunca conjurado em 8 turnos: 1,8%
Avg Treasures criados (total no jogo): 4,01
Avg Treasures em campo no fim: 2,51
Avg Treasures sacrificados (total): 1,49
Avg Constructs criados: 0,37
Avg outros tokens criados: 0,73
Avg mortes de criatura: 0,58
Avg mortes de artefato: 1,55
Avg drain/dano agregado (proxy, NAO vida real de oponente): 1,10
Avg vida ganha: 0,47
Avg cartas compradas extra: 1,17
Avg cascades via Rain of Riches: 0,04
Avg combates com pelo menos 1 atacante: 3,89
Revel in Riches (10+ Treasures) — condicao satisfeita: 0,1% dos jogos | turno medio: 7,67
```

**Comparação com o relatório original (n=500) — pra deixar claro o tamanho da distorção:**

| Métrica | Script original (com os bugs) | Este script (corrigido) |
|---|---|---|
| Treasures em campo no fim | 6,49 | 2,51 |
| Battlefield count médio | 14,34 | não comparável diretamente (contagem diferente) |
| Revel in Riches condição batida | 4,8% | **0,1%** |
| "Combo" ligado | 0,4% (inexistente) | 0% (não existe, confirmado) |
| Mata pelo menos 1 oponente | 39,6% | não medido (sem oponente fictício) |

O motor de Treasure é real e funciona, mas em volume bem mais modesto do que o relatório original sugeria — 23 fontes em 99 cartas não significa "todas ativam toda partida"; a maioria das fontes é uma criatura/spell específica que precisa ser comprada E resolvida E (nos casos de combate) sobreviver até atacar. **0,1% de Revel in Riches é o número honesto** — é um wincon real mas de baixíssima frequência num jogo de 8 turnos, não os 4,8% fictícios do script original.

**Simplificações documentadas no docstring do script:** sem oponente real (nenhum permanente/spell/vida adversária de verdade — Smothering Tithe, Monologue Tax, Mari, Revel in Riches contra criatura do oponente, e o modo "goad" do Grenzo ficam sem efeito numérico solo); drain/dano são contadores agregados, nunca vida real de oponente; combate sem bloqueio (mesma convenção de todos os outros simuladores desta biblioteca); Grenzo e Laughing Jasper Flint (que exilariam da biblioteca do oponente) aproximados puxando da própria biblioteca, documentado no código.

---

---

### Política "maximizar criação e destruição de Treasure" — 2026-08-22

**Pedido do usuário:** priorizar a criação E destruição de Treasures como mecânica principal do goldfish (confirmando antes que Mirkwood Bats está no deck — está — e que "Marionette Apprentice" **não** está — a carta real na lista é **Marionette Master**, diferente: Fabricate 3 em vez de Fabricate 1, drain = poder da criatura em vez de fixo 1).

**Implementação — `TREASURE_MAXIMIZE_POLICY`, duas partes:**
1. **Criação:** cartas com tag de geração de Treasure ganham prioridade de conjuração sobre outras de mesmo custo (`is_treasure_source()`).
2. **Destruição — o achado central desta sessão:** se o Vihaan animou os Treasures em criaturas 3/3 outlaw no combate (`At the beginning of combat... Treasures you control become 3/3 Construct Assassin`), sacrificá-los pro **Ashnod's Altar** enquanto ainda são criaturas dispara **três categorias de gatilho ao mesmo tempo** — morte de criatura (Zulaport, Sephiroth, Pitiless Plunderer), morte de artefato (Marionette Master, Agent of the Iron Throne) e token saindo (Nadier's Nightblade, Mirkwood Bats) — porque um Treasure animado É simultaneamente artefato, criatura e token. Sacrificar direto pro Krark-Clan Ironworks (sem animar) só pega artefato+token, perde a categoria de morte de criatura inteira. Implementado em `aggressive_treasure_destruction()`, chamada no fim do `combat_step`; a mana gerada (`{C}{C}` por Treasure, sempre — não só quando o Goldspan Dragon está fora) entra num `bonus_mana_pool` disponível numa segunda passada de main phase pós-combate (adicionada pra aproveitar essa mana ainda no mesmo turno).

**Bug real encontrado e corrigido no processo:** o cálculo de drain da Marionette Master usava um poder chutado de "4" sem checar a carta real — o poder base real dela (Scryfall) é **1/3**, e como a implementação sempre escolhe o modo "3 Servos" do Fabricate 3 (não contadores), o poder nunca sai de 1. Corrigido pra usar o valor real.

Testado em 30.000 partidas com timeout antes do batch oficial (0 erros).

**n=2000, mesmas seeds, baseline (só sacrifica Treasure pra pagar mana) vs política nova:**

| Métrica | Baseline | Maximize | Δ |
|---|---|---|---|
| Avg Treasures criados (total) | 4,245 | 6,432 | +51,5% |
| Avg Treasures sacrificados (total) | 2,179 | 4,123 | +89,3% |
| Avg mortes de criatura | 0,667 | 1,264 | +89,5% |
| Avg mortes de artefato | 2,268 | 4,268 | +88,2% |
| Avg drain/dano agregado (proxy) | 1,327 | 1,764 | +32,9% |
| Avg vida ganha | 0,558 | 0,718 | +28,7% |
| Avg cartas compradas extra | 1,198 | 1,371 | +14,4% |
| Avg mana bonus gerada pós-combate | 0 | 1,323 | (mecânica nova) |
| Turno médio de conjuração do Vihaan | 3,171 | 3,17 | ~igual |
| Revel in Riches (10+ Treasures) | 0,25% | 0,25%¹ | ~igual |

¹ No batch de reporte final (seed diferente) saiu 0,2%/0,25% — dentro do ruído normal de amostra, não uma mudança real.

**Leitura:** a política quase **dobra** os gatilhos de aristocratas (mortes de criatura e de artefato) e aumenta drain em quase um terço, **sem custo medido na curva da comandante** — a mana gerada pelos sac outlets no combate compensa a mana que teria vindo dos Treasures se eles tivessem sido só guardados. É um ganho real de valor incremental por turno.

**Ressalva honesta — tensão real com o Revel in Riches:** essa política **compete diretamente** com o wincon alternativo de acumular 10+ Treasures simultâneos (Revel in Riches), porque ela ativamente esvazia o estoque de Treasure toda vez que anima e sacrifica. Nos dados, a taxa de Revel in Riches ficou estatisticamente igual nas duas políticas (a carta já é rara o suficiente — 1 cópia em 99 — que o efeito não apareceu de forma clara na amostra), mas conceitualmente são dois planos de jogo em tensão: se o objetivo prioritário for fechar o jogo via Revel in Riches, "maximizar destruição" não é a política certa — seria o oposto (acumular sem sacrificar). Como o usuário pediu explicitamente "criação e destruição como mecânica principal" (não o wincon do Revel in Riches), mantive `TREASURE_MAXIMIZE_POLICY = True` como default.

---

## Simulação #2 — re-run pós-troca de cartas (Rakdos Signet → Gleaming Splendor, Insatiable Avarice → Smaug the Magnificent) — 2026-08-22

**Mudanças no `CARD_DB` e no motor:**
- Removido `add("Rakdos Signet", ...)` e sua entrada em `GOOD_KEEP` (não contava mana em `rocks_mana()` de qualquer forma — era filtro, mana líquida 0 — então a remoção não altera a matemática de mana, só a fixação de cor real que a carta dava no jogo físico, registrado na auditoria).
- Removido `add("Insatiable Avarice", ...)` e seu bloco em `resolve_instant_sorcery`.
- Adicionado `Gleaming Splendor` com tag `opponent_dependent` — mesma convenção já usada pra Smothering Tithe/Monologue Tax/Mari (gatilho depende de ação real do oponente, não modelado numericamente aqui; carta fica "disponível" mas sem efeito solo na simulação, documentado desde o topo do arquivo).
- Adicionado `Smaug the Magnificent` com dois gatilhos reais implementados:
  - Upkeep — `create_treasures(state, 1, ...)` logo no início de `play_turn`, condicionado a já estar em campo (não dispara no turno em que é conjurado, igual à regra real).
  - Ataque — `drain(state, state.treasures)` no bloco de gatilhos de "ataca" do `combat_step` (mesmo padrão do Captain Lannery Storm/Goldspan Dragon/Kellogg), usando o contador agregado `drain_damage_total` como proxy de "dano igual ao número de Treasures", nunca vida real de oponente.
  - Tag `upkeep_treasure` adicionada a `TREASURE_SOURCE_TAGS` pra a política de priorização de conjuração (`TREASURE_MAXIMIZE_POLICY`) reconhecer a carta como fonte de Treasure.

**Bug real encontrado e corrigido nesta passada (não relacionado à troca de cartas, achado ao revisar `play_turn` pra decidir onde encaixar o upkeep do Smaug):** o gatilho da Magda (`Whenever you commit a crime, create a tapped Treasure token`) estava sendo checado **logo depois do reset de `commits_crime_this_turn = False`**, ou seja, sempre lia `False` — nenhuma magia do turno atual tinha sido conjurada ainda naquele ponto do código. Resultado: **o gatilho da Magda nunca disparava em nenhuma partida simulada**, apesar da carta estar corretamente implementada em todo o resto (tag `crime_treasure`, contada como fonte na seção 3 da auditoria). Corrigido movendo a checagem pra depois das duas chamadas de `main_phase()` (onde as magias que cometem crime — Path to Exile, Council's Judgment, Deadly Derision, Requisition Raid, Boros Charm, Teferi's Protection — são de fato conjuradas), antes do `end_step()`.

**Teste de robustez** (prática obrigatória documentada em `references/goldfish-sim-card-rules.md`): 15.000 partidas com timeout de 2s/partida via `signal.alarm`, **0 erros, 0 timeouts**.

**Batch oficial: n=3000, seed_base=6000000, turns=8** (substitui o batch anterior de n=2000/seed=5000000):

| Métrica | v1 (n=2000, lista antiga) | v2 (n=3000, lista nova + fix Magda) | Δ |
|---|---|---|---|
| Avg Treasures criados (total no jogo) | 6,43 | 6,62 | +3,0% |
| Avg Treasures em campo no fim | 2,31 | 2,39 | +3,5% |
| Avg mortes de criatura | 1,26 | 1,13 | −10,3% |
| Avg drain/dano agregado (proxy) | 1,76 | 2,27 | +28,7% |
| Avg cartas compradas extra | 1,37 | 0,99 | −27,7% |
| Revel in Riches (10+ Treasures) | 0,25% | 0,4% | +0,15pp |

**Leitura honesta, sem inventar causa única — a troca mistura vários efeitos ao mesmo tempo, então a leitura é qualitativa:**
- **Drain/dano subiu bastante (+28,7%)** — soma de dois efeitos reais: o novo gatilho de ataque do Smaug (`dano = Treasures controlados`) e, principalmente, o fix do bug da Magda (mais Treasures reais criados por crime → mais material pro resto da cadeia de aristocratas/drain).
- **Cartas compradas extra caiu (−27,7%)** — efeito direto e esperado da perda do Insatiable Avarice, que era uma fonte de draw puro (draw 3) e não foi substituída por nada equivalente. Bate com o que já estava registrado na auditoria (seção 6: 8→7 fontes de draw).
- **Treasures criados subiu só um pouco (+3,0%)**, apesar de ter ganho uma fonte nova (Smaug upkeep) e corrigido o bug da Magda — porque perdeu a fixação de mana do Rakdos Signet (efeito indireto: menos consistência de curva pode atrasar levemente o motor), e porque Gleaming Splendor não contribui numericamente na simulação (opponent-dependent, sem oponente real modelado — na mesa física ela deve contribuir mais do que aparece aqui).
- **Mortes de criatura caíram (−10,3%)** — dentro do ruído esperado de amostra a amostra (dois seeds diferentes, n diferentes), não atribuo isso a nenhuma das trocas especificamente.

Resultados salvos em `vihaan_v1_runs.jsonl` (sobrescrito com os 3000 jogos novos — o nome do arquivo ficou "v1" porque é a mesma versão do simulador, só re-rodado com a lista atualizada).

---

## Correção — checklist obrigatória de mecânica (regra nova pós-Beorn) — 2026-08-28

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks — última rodada da varredura completa dos 10
decks com simulador Python. Landfall N/A (0 cartas), dorks N/A (0 mana
dorks criatura na lista).

**Bugs reais achados (fixing lands + 3 cartas com tag e nenhum gatilho):**

- **Desolate Mire / Shadowblood Ridge**: são *filter lands* — real:
  `{1},{T}: Add {W}{B}` / `{1},{T}: Add {B}{R}`, **sem NENHUMA habilidade de
  mana grátis**. `lands_in_play()` contava as duas como +1 incondicional,
  igual qualquer terreno normal, mesmo sem nenhuma outra fonte de mana em
  campo pra "semear" o filtro. Corrigido: só contribuem se houver pelo
  menos 1 outra fonte de mana real presente (mesmo padrão do Fetid
  Heath/Rugged Prairie corrigido no Edgar Markov nesta sessão).
- **Bojuka Bog / Path of Ancestry / Clifftop Retreat / Dragonskull Summit /
  Isolated Chapel / Blackcleave Cliffs**: tags `etb_tapped`/`checkland_*`/
  `fastland` existiam no `CARD_DB`, nunca lidas em lugar nenhum — todo
  terreno produzia mana no próprio turno em que era jogado, mesmo os que
  entram tapped de verdade (incondicional, ou condicionado a controlar um
  básico do tipo certo, ou condicionado a ter 2 ou menos outros terrenos).
  Nova infraestrutura `tapped_lands_this_turn` (mesmo padrão de outros
  decks desta sessão). Blood Crypt (shockland) segue sempre entrando
  destapada — este arquivo rastreia vida de verdade, mas a convenção já
  estabelecida é assumir que o custo de vida sempre é pago.
- **Black Market Connections**: só existia a entrada no `CARD_DB` — **zero
  gatilho em lugar nenhum**. "At the beginning of your first main phase,
  choose one or more" (Treasure -1 vida / compra -2 vida / token 3/2 -3
  vida) — implementado escolhendo os 3 modos todo turno (IA agressiva,
  vida própria só perdida por fontes auto-infligidas neste sim solo).
- **Mirkwood Bats**: "Whenever you create **or sacrifice** a token" — só a
  metade "create" disparava (via `on_tokens_created`); a metade "sacrifice"
  nunca era checada em `on_token_leaves()`, apesar de ser o motor central
  de sacrifício do deck (`aggressive_treasure_destruction` dispara isso o
  jogo inteiro).
- **Sephiroth, Fabled SOLDIER**: só a metade passiva ("whenever another
  creature dies, opponent loses 1/you gain 1") estava modelada — a metade
  ETB/ataque ("you may sacrifice another creature. If you do, draw a
  card") 100% ausente. Implementada nos dois gatilhos reais (ETB via
  `resolve_permanent_etb`, ataque via `combat_step`), sacrificando só
  fodder barato (token genérico ou Construct), nunca uma criatura nomeada.

**Não corrigido (decisão de escopo, não bug):** Demolition Field's
habilidade paga exige "target nonbasic land an opponent controls" — sem
alvo legal possível num goldfish solo sem oponente real, a ativação não
pode acontecer de verdade (Regra 1 — não inventar estado alheio). Diferente
de Sephiroth/Black Market Connections, que não dependem de alvo do
oponente.

**Resultado (n=2000, seed_base=5500000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg Treasures criados (total) | 6,57 | **7,89** |
| Avg drain/dano agregado (proxy) | 2,54 | **3,63** |
| Avg vida ganha | 0,73 | **1,00** |
| Avg cartas compradas extra | 1,03 | **2,00** |
| Avg mortes de criatura | 1,16 | **1,43** |

Salto grande em quase toda métrica — Black Market Connections e Mirkwood
Bats eram motores centrais 100%/50% ausentes, então a correção teve
impacto real e substancial, não marginal.

**Robustez:** sweep de 20.000 jogos (seeds 5500000–5519999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

`lista.md` não mudou. `vihaan_v1_runs.jsonl` sobrescrito (3000 jogos).

---

## Correção — rodada ampliada da checklist obrigatória (categorias 10-13) — 2026-08-31

**Contexto:** pedido explícito do usuário pra completar a rodada ampliada do
`references/goldfish-sim-card-rules.md#checklist-obrigatória-de-categorias-de-mecânica`
(categorias 10 a 13 — métricas básicas, multi-face, planeswalker, Classes/Sagas)
neste deck, que só tinha recebido a checklist original (1-9) em 2026-08-28.

**Categoria 12 (planeswalker) — N/A confirmado independentemente:** varredura
programática de `type_line` no cache pra todas as 94 cartas únicas da lista
(comandante incluso). Zero cartas com `Planeswalker` no `type_line`. 0
planeswalkers na lista, categoria N/A.

**Categoria 13 (Classes/Sagas) — 1 carta na lista:** mesma varredura achou
só `Caretaker's Talent` (`Enchantment — Class`). 0 Sagas.

**Categoria 11 (multi-face) — 2 cartas na lista** (varredura de "//" em
`lista.md`, confirmado via API real que nenhuma outra carta tem layout
multi-face): `Brightclimb Pathway // Grimclimb Pathway` e `Sephiroth, Fabled
SOLDIER // Sephiroth, One-Winged Angel`.

### Bugs reais corrigidos

1. **Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel — o achado
   central desta rodada.** `layout` real (API Scryfall) = `transform`.
   `state.sephiroth_transformed` já existia e era SETADO na 4ª morte do
   turno (linha ~508 antiga), mas **nunca era LIDO em lugar nenhum** — uma
   tag de estado morta. Oráculo real completo:
   ```
   Frente ({2}{B}): Whenever Sephiroth enters or attacks, you may sacrifice
   another creature. If you do, draw a card.
   Whenever another creature dies, target opponent loses 1 life and you
   gain 1 life. If this is the fourth time this ability has resolved this
   turn, transform Sephiroth.
   Verso: Flying
   Super Nova — As this creature transforms into Sephiroth, One-Winged
   Angel, you get an emblem with "Whenever a creature dies, target
   opponent loses 1 life and you gain 1 life."
   Whenever Sephiroth attacks, you may sacrifice any number of other
   creatures. If you do, draw that many cards.
   ```
   3 correções reais:
   - **Emblem Super Nova** (`state.has_super_nova_emblem`, novo campo) é uma
     2ª fonte INDEPENDENTE de drain 1/vida 1 por morte — não substitui a
     habilidade da frente, ela deixa de existir junto com a transformação (o
     verso não tem mais "whenever another creature dies", só o emblem tem).
     O emblem drena em QUALQUER morte de criatura (texto "a creature", sem
     "another" — inclui a morte do próprio Sephiroth) e SEM limite de 4x por
     turno, permanente pro resto da partida mesmo se Sephiroth sair de campo
     depois. `on_creature_dies()` reescrita pra checar o emblem primeiro,
     caindo pra habilidade da frente só antes da transformação.
   - **Ataque muda de escala:** `try_sephiroth_sac_draw()` sempre usava
     "sacrifica 1, compra 1" (correto pra frente). Depois de transformado, o
     verso sacrifica QUALQUER NÚMERO de outras criaturas e compra essa
     quantidade — corrigido pra sacrificar TODO o fodder disponível
     (tokens + constructs) de uma vez quando `sephiroth_transformed`.
   - **Edge case adicional encontrado:** se Sephiroth já transformado morre
     e é recuperado via Sevinne's Reclamation (mv≤3, alcança ele), a nova
     cópia física reentra pela FRENTE (transform é do objeto físico, não do
     jogador) — `enter_battlefield()` agora reseta `sephiroth_transformed`
     nesse caso (o emblem, sendo independente, NÃO reseta).

2. **Caretaker's Talent — nível 1 só (nível 2/3 ausentes).** Oráculo real:
   ```
   Nivel 1: Whenever one or more tokens you control enter, draw a card.
   This ability triggers only once each turn.
   {W}: Level 2 — When this Class becomes level 2, create a token that's a
   copy of target token you control.
   {3}{W}: Level 3 — Creature tokens you control get +2/+2.
   ```
   Implementada `try_level_caretakers_talent()`: sobe de nível pagando como
   sorcery (mana sobrando depois de conjurar tudo da mão + Phyrexian
   Reclamation, heurística documentada no código — prioridade baixa em
   relação a desenvolver board novo, alta em relação a deixar mana parada),
   nível 2 cria cópia do token de maior valor controlado (Treasure >
   Construct > outro), nível 3 é cumulativo com 1/2. **O anthem do nível 3
   não tem onde se aplicar numericamente neste simulador** — nenhum efeito
   do deck (nem antes, nem depois desta correção) depende de poder de
   criatura-token; Marionette Master usa o próprio poder DELA, não de
   token. Decisão de arquitetura honesta (documentada no código, não
   inventado): reportado como métrica PROXY (tokens em campo × anthem
   implicado), nunca dano real calculado — mesma convenção já usada pra
   drain/vida no resto do arquivo.

3. **Brightclimb Pathway // Grimclimb Pathway — sem bug, decisão de
   arquitetura documentada.** `layout` real = `modal_dfc`. Confirmado: o
   motor de mana inteiro deste simulador (`lands_in_play`/`rocks_mana`/
   `total_mana`) nunca rastreou cor por fonte individual em NENHUM dos 35
   terrenos, antes ou depois desta rodada — só soma mana total agregada.
   Tratar a Pathway como land genérico de 1 mana é consistente com o resto
   do arquivo, não uma simplificação nova só pra esta carta. Comentário
   adicionado no `CARD_DB` explicando a decisão, sem inventar rastreamento
   de cor pra 1 carta só (nenhuma métrica reportada depende de cor).

4. **Achado extra (fora da lista original do pedido) — Phyrexian
   Reclamation sem NENHUMA lógica de ativação.** Categoria 7 (ativadas
   repetíveis) + categoria 10 (métrica RECURSION): só existia a entrada no
   `CARD_DB` (tag `recursion_repeat`), zero código em qualquer lugar.
   Oráculo real: `{1}{B}, Pay 2 life: Return target creature card from your
   graveyard to your hand.` Sem "activate only as sorcery" — repetível
   livremente. Implementada `try_phyrexian_reclamation()`, ativa quantas
   vezes mana+cemitério permitirem no main phase, priorizando devolver a
   criatura de maior mv (heurística documentada).

5. **Achado extra — Witch of the Moors com condição errada.** Oráculo real:
   "if you gained life THIS TURN" — o código checava
   `state.life_gained_total` (acumulado do JOGO INTEIRO), então depois de
   qualquer 1 ponto de vida ganho em qualquer turno anterior, a condição
   ficava permanentemente satisfeita pro resto da partida (recursão de
   graça todo turno sem depender de ganhar vida de novo). Corrigido com
   contador per-turno novo (`life_gained_this_turn`, resetado em
   `play_turn()`), mesmo padrão já usado noutros flags per-turno do
   arquivo.

6. **Achado extra — Black Market Connections disparando 2x por turno.**
   Oráculo real: "At the beginning of your **first** main phase" — só 1x
   por turno. `main_phase()` é chamada 2x por turno (pré e pós-combate,
   pra usar a mana bonus dos sac outlets — mecânica adicionada em
   2026-08-22) e `try_black_market_connections()` não tinha guarda contra a
   2ª chamada desde a correção de 2026-08-28 que implementou essa carta —
   dobrando Treasure/draw/token/perda de vida todo turno. Corrigido com
   flag per-turno (`black_market_connections_triggered_this_turn`), mesmo
   padrão de `caretaker_drawn_this_turn`/`kambal_drawn_this_turn`.

### Categoria 10 — métricas básicas obrigatórias, agora com linha formal

Antes desta rodada não havia linha "RECURSION"/"INTERACTION" formal no
relatório (`run_batch`), apesar do deck ter cartas reais de cada categoria.
Adicionadas 5 linhas explícitas no relatório: `RAMP`, `DRAW`, `INTERACTION`,
`RECURSION`, `FINISHER/LETHALITY` — cada uma citando as cartas que a
compõem, não só um número solto.

### Robustez

20.000 partidas (seeds 7000000–7019999, timeout 2s/partida via
`signal.alarm`) — **0 erros, 0 timeouts**.

### Resultado — batch oficial (n=3000, seed_base=6000000, turns=8), antes vs. depois

**Nota honesta:** a maioria das métricas CAIU, não subiu — o achado extra
#6 (Black Market Connections disparando 2x/turno desde 2026-08-28) estava
inflando quase toda métrica de Treasure/draw/drain por um fator real, e sua
correção domina o delta total mais do que os efeitos NOVOS (Sephiroth
transform, Caretaker nível 2/3, Phyrexian Reclamation), que são raros o
suficiente (peças únicas, condições específicas) pra não compensar a queda.

| Métrica | Antes (com bug do BMC 2x) | Depois (corrigido) | Δ |
|---|---|---|---|
| Avg Treasures criados (total) | 8,33 | 7,63 | −8,4% |
| Avg Treasures sacrificados (total) | 5,61 | 5,11 | −8,9% |
| Avg mortes de criatura | 1,52 | 1,36 | −10,5% |
| Avg mortes de artefato | 5,76 | 5,26 | −8,7% |
| Avg drain/dano agregado (proxy) | 3,54 | 3,09 | −12,7% |
| Avg vida ganha | 1,04 | 0,94 | −9,6% |
| Avg cartas compradas extra | 2,02 | 1,63 | −19,3% |
| Revel in Riches (10+ Treasures) | 0,5% | 0,4% | −0,1pp |

**Métricas novas (sem baseline "antes", efeitos recém-implementados):**

| Métrica nova | Valor |
|---|---|
| Sephiroth transformado (emblem Super Nova ativo) — % de jogos | 0,5% |
| Avg cartas compradas via sac do Sephiroth (as 2 faces) | 0,09 |
| Caretaker's Talent nível 2 alcançado — % de jogos | 10,0% |
| Caretaker's Talent nível 3 alcançado — % de jogos | 5,4% |
| RECURSION — avg cartas recuperadas do cemitério/jogo | 0,14 |
| ...das quais via Phyrexian Reclamation (repetível) | 0,03 |
| INTERACTION — avg remoção/wipe conjurados/jogo | 0,71 |

**Leitura:** o efeito líquido desta rodada é uma correção pra BAIXO nas
métricas centrais (o bug do BMC 2x era o maior distorcedor não descoberto
até agora), compensada só parcialmente pelos efeitos novos genuínos — mas
raros o suficiente numa lista de 99 cartas singleton (Sephiroth transforma
em 0,5% dos jogos porque exigir 4 mortes de criatura NO MESMO turno é um
board state avançado; Caretaker nível 3 exige {2}+{W}+{3}{W}=6 mana extra
sobrando além de tudo mais que o turno já gastou). Os números "depois" são
os honestos — nenhuma métrica estava inflada por efeito novo desta rodada,
só corrigida de uma distorção antiga (dobra do BMC).

`lista.md` não mudou. `vihaan_v1_runs.jsonl` sobrescrito (3000 jogos, mesma
seed_base=6000000 — script principal não mudou de seed).

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

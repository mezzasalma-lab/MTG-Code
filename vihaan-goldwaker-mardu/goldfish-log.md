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

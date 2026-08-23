# Goldfish Log — Maralen, Fae Ascendant

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Simulação #1 — goldfish Python completo (`maralen_goldfish_v1.py`) — 2026-08-23

**Script construído do zero**, seguindo a arquitetura já estabelecida nos outros 6 simuladores desta biblioteca (`Card`/`GameState` dataclasses, `total_mana()`/`remaining_mana()`/`spend_mana()` com gasto real rastreado por turno). Passo 0 (regra de `references/goldfish-sim-card-rules.md`): varredura mecânica no oráculo completo das 99 cartas achou os gatilhos reais listados no docstring do script. Todos com efeito real implementado, exceto os explicitamente dependentes de oponente real (Rhystic Study, Mystic Remora, Faerie Mastermind passivo, Alela, Bojuka Bog) — documentados como "disponíveis mas sem efeito numérico solo", nunca fingidos.

**Roaming Throne — tipo escolhido: Faerie.** Maralen é ela mesma `Elf Faerie Noble`, então o próprio gatilho dela dobra com QUALQUER um dos dois tipos escolhidos (ela conta como "outra criatura do tipo escolhido" pra si mesma). Faerie foi escolhido porque tem mais criaturas com gatilho relevante além da comandante (Bitterbloom Bearer, Obyra, Tegwyll, Faerie Harbinger, Spellstutter Sprite, Mistbind Clique) do que Elfo (só Marwyn e Elvish Warmaster têm ETB relevante).

**Motor central implementado com fidelidade real:** o gatilho da própria Maralen (`Whenever Maralen or another Elf or Faerie you control enters, exile the top two cards of target opponent's library. Once each turn, you may cast a spell with mana value <= Elves+Faeries you control from among cards exiled with Maralen this turn without paying its mana cost`). Sem biblioteca de oponente real num goldfish solo, a exilada vem da PRÓPRIA biblioteca — mesma aproximação já usada pro Grenzo/Laughing Jasper Flint no simulador do Vihaan, documentada no código, nunca fingida como "roubo real".

**Combo de 2 peças (Umbral Mantle + mana dork escalável) implementado como detecção real, não decorativa:** a cada turno, `dork_mana()` calcula a saída de cada dork; se Umbral Mantle está equipada num dork cuja saída (Priest of Titania/Elvish Archdruid = nº de Elfos; Marwyn = seu poder; Circle of Dreams Druid = nº de criaturas) atinge 4+, a flag `infinite_mana_this_turn` liga de verdade (não é um número arbitrário — é a mesma lógica de "mana líquida positiva" descrita na auditoria). Staff of Domination, quando em campo junto com mana infinita, resolve puxando a biblioteca inteira pra mão (limite defensivo real: **nunca finge vencer por deck-out**, só registra `staff_infinite_draws` e marca `library_emptied`).

**Simplificações documentadas** (não inventadas — omissões explícitas, ver docstring completo do script):
- Bloom Tender: aproximado como 2 mana fixo (cores em jogo tipicamente 2-3, não rastreio cor exata de cada permanente).
- Joraga Treespeaker: nivelado só até nível 1 (2 mana investidos), nível 5 quase nunca compensa em 8 turnos.
- Heritage Druid / Birchlore Rangers: aproximação documentada — convertem Elfos "sick" (recém-conjurados, que ainda não produziriam mana) em mana extra, já que tapar OUTROS Elfos como custo ignora summoning sickness (CR 302.6) — sem duplicar a contagem desses Elfos caso eles não estivessem sick.
- Devoted Druid: self-untap via -1/-1 counter com teto defensivo de 3 ativações extras/turno.
- Mistbind Clique (Champion a Faerie): sacrificada no ETB se não há outra Fada em campo pra exilar.

**Teste de robustez** (prática obrigatória): 15.000 partidas com timeout de 2s/partida via `signal.alarm`, **0 erros, 0 timeouts** — o único bug real encontrado (comandante nunca saía da mão porque ela nunca ESTAVA na mão — vem direto da zona de comando, mesmo bug documentado nos outros 5 simuladores desta biblioteca) foi corrigido antes mesmo dessa varredura, durante o smoke-test manual de 20 partidas.

**Bug real encontrado e corrigido (achado no smoke-test manual, antes da varredura de robustez):** `resolve_cast()` tentava `state.hand.remove(COMMANDER)` incondicionalmente ao conjurá-la, mas a comandante nunca entra na mão (vem da zona de comando) — `ValueError` imediato na primeira partida testada. Corrigido excluindo a comandante dessa remoção.

**n=3000, seed_base=8000000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0,55
Turno medio de conjuracao da Maralen: 4,60 | mediana: 4,0
Nunca conjurada em 8 turnos: 4,5%
Avg gatilhos de Maralen (exila 2): 5,11
Avg cartas exiladas total: 9,36
Avg casts gratis via Maralen: 2,24
Avg tutores usados: 0,65
Avg tokens criados (exclui explosao infinita): 3,35
Avg dobras via Roaming Throne: 0,21
Combo Umbral Mantle (mana infinita) montado: 7,8% dos jogos | turno medio: 6,65
Staff of Domination converteu em compra infinita: 1,5% dos jogos
Avg cartas compradas extra (motores de draw, exclui staff infinito): 0,39
Avg mao final: 0,87
```

**Leituras principais:**

- **O motor central funciona desde cedo**: comandante em campo no turno 4,6 em média, com ~5,1 gatilhos de exílio por partida (9,4 cartas exiladas) e **2,24 casts grátis** via a habilidade dela — o plano de "roubar e jogar de graça" está ativo na maioria das partidas, não é situacional.
- **O combo do Umbral Mantle é real, mas não trivial de montar**: 7,8% das partidas em 8 turnos, turno médio 6,65 quando acontece. Isso confirma numericamente o que a auditoria já tinha identificado por leitura de texto — não é um combo de canto teórico, mas também não é algo que "sempre liga cedo". Consistente com o padrão já visto no Edgar Markov desta mesma biblioteca (combo real ≠ combo garantido).
- **Staff of Domination como fechador é ainda mais raro (1,5%)** — precisa da junção de DUAS condições independentes (mana infinita montada + Staff já em campo), o que reduz a taxa efetiva pela metade.
- **Densidade de tutores baixa em jogo (0,65 usados/partida)** apesar de 5 tutores reais na lista — é matemática normal de deck singleton de 99 cartas (cada tutor é ~1% de densidade), não um problema de implementação.
- **Roaming Throne dobrou gatilhos em 0,21/partida** — como o tipo escolhido (Faerie) também cobre a própria Maralen, isso inclui dobras do gatilho central dela quando a Roaming Throne está em campo, não só das Fadas menores.

Resultados salvos em `maralen_v1_runs.jsonl` (3000 jogos).

**Simplificações documentadas no docstring do script** (não inventadas — omissões explícitas): sem combate real contra oponente; drain/vida de oponente nunca reais; Rhystic Study/Mystic Remora/Faerie Mastermind passivo/Alela/Bojuka Bog opponent-dependent, sem efeito numérico solo; removal/contra-mágica conjuradas quando há mana sobrando, sem efeito de combate real (mesma convenção dos outros 6 simuladores desta biblioteca).

---

### Teste pontual — motor de flash em criaturas, T4-T8, COM vs SEM Radagast of Rhosgobel — 2026-08-23

**Pedido do usuário:** medir a probabilidade real de ter o "motor de flash" online nos turnos 4, 5, 6, 7 e 8, comparando a lista atual (com Radagast) contra a versão anterior (sem Radagast, com Elves of Deep Shadow no lugar), pra decidir se a troca vale a pena.

**Script:** `maralen_flash_radagast_test.py`. Duas métricas rastreadas por turno em `maralen_goldfish_v1.py` (`flash_universal_by_turn`, `flash_with_radagast_by_turn`, populadas no fim de cada `play_turn`):
- **Motor universal puro**: pelo menos 1 de Leyline of Anticipation / Vedalken Orrery / High Fae Trickster / Alchemist's Refuge em campo.
- **Motor combinado**: o universal OU Radagast of Rhosgobel em campo (Radagast não dá flash universal — só a 1ª criatura do turno, com desconto de {2} — mas conta como fonte parcial pra essa métrica).

Duas variantes de biblioteca, mesmas 3000 seeds pareadas (comparação direta, não amostras independentes): lista atual (com Radagast) vs. lista revertida (Radagast → Elves of Deep Shadow). Teste de robustez prévio na variante nova (sem Radagast, nunca simulada antes): 5.000 jogos com timeout de 2s, 0 erros.

**Checagem de sanidade — motor universal puro (deveria ser ~igual nas duas listas, já que nenhuma das duas cartas trocadas é fonte de flash universal):**

| Turno | Com Radagast na lista | Sem Radagast na lista |
|---|---|---|
| T4 | 14,2% | 14,7% |
| T5 | 23,0% | 23,6% |
| T6 | 33,8% | 34,6% |
| T7 | 42,2% | 43,2% |
| T8 | 48,4% | 49,3% |

Diferença de ~0,5-1pp entre as duas — dentro do ruído esperado de amostra (mesmas seeds, então nem deveria zerar por completo: a ordem de embaralhamento muda porque a biblioteca tem cartas diferentes num slot). Confirma que a troca não afetou acidentalmente o pacote universal — bom sinal de que a implementação está correta.

**Resultado principal — motor de flash em criaturas disponível (universal + Radagast quando presente):**

| Turno | Com Radagast | Sem Radagast | Δ |
|---|---|---|---|
| T4 | 15,3% | 14,7% | +0,7pp |
| T5 | 26,4% | 23,6% | +2,8pp |
| T6 | 39,3% | 34,6% | +4,6pp |
| T7 | 49,6% | 43,2% | +6,4pp |
| T8 | 56,5% | 49,3% | +7,2pp |

**Leitura:** Radagast adiciona uma cobertura real e crescente ao motor de flash — de +0,7pp no turno 4 (ele mesmo ainda raramente resolvido tão cedo, CMC 4) até +7,2pp no turno 8 (quase 1 em cada 14 partidas a mais tem alguma forma de flash em criaturas só por causa dele). Dito isso, o teto absoluto do motor combinado ainda fica abaixo de 60% mesmo no turno 8 — em mais de 4 de cada 10 partidas, NENHUMA das 5 peças (4 universais + Radagast) está em campo até o fim do jogo, porque cada uma é 1 carta em 99. A contribuição do Radagast é real mas incremental sobre uma base já limitada por densidade de singleton, não uma mudança estrutural na confiabilidade do motor.

---

## Simulação #2 — implementação do landfall (Thranduil, Sindarin Liege + Thranduil's Company) — 2026-08-23

**Contexto:** a lista trocou Devoted Druid e Cloud of Faeries por Thranduil, Sindarin Liege // Silvan Rally e Thranduil's Company — um subtema de landfall que o script ainda não tinha nenhum gancho pra modelar (nenhum `landfall_trigger()` existia até agora).

**Implementação real (não decorativa):**
- `play_land()` reescrita: agora suporta até **2 lands por turno** quando Thranduil's Company está em campo E há outro Elfo controlado (`As long as you control another Elf, you may play an additional land on each of your turns` — checado de verdade contra Elfos nomeados + tokens de Elfo, não assumido).
- Nova função `landfall_trigger(state)`, chamada a cada terreno que entra (land normal ou o extra do Company): se Thranduil, Sindarin Liege está em campo, cria um token de Elfo 1/1 real (`Landfall — ... create a 1/1 green Elf creature token`); se Thranduil's Company está em campo, registra o gatilho de "2 contadores +1/+1 num alvo" — modelado com efeito numérico real quando o alvo de maior valor (Marwyn, the Nurturer) está em campo (a mana dela escala com o próprio poder, então +2 de poder é +2 de mana real), documentado como não-modelado pra outros alvos sem relevância numérica no sim.

**Bug real encontrado e corrigido nesse processo (não é sobre as cartas novas — achado ao mexer em `create_token()` pra ela aceitar o tipo do token):** `create_token()` **nunca disparava o gatilho da Maralen** pra nenhum token — nem os de Elfo Guerreiro do Elvish Warmaster/Imperious Perfect, nem os de Fada do Bitterblossom/Bitterbloom Bearer, que já estavam na lista desde o início. Pelas regras reais, um token Elfo ou Fada entrando em campo DEVE disparar "Whenever Maralen or another Elf or Faerie you control enters" — isso nunca tinha sido implementado, mesmo antes desta atualização. Corrigido: `create_token(state, kind, source)` agora recebe o tipo do token e dispara `maralen_trigger_token()` (mesma lógica de exílio/dobra por Roaming Throne da carta nomeada) pra todo token Elfo ou Fada, além de contar corretamente pra `elf_faerie_count()` (teto de custo do cast grátis), pra a contagem de Elfos que os dorks escaláveis (Priest of Titania/Elvish Archdruid/Circle of Dreams Druid) usam, e pro contador de poder da Marwyn.

**Também separei o contador genérico `other_tokens` em `elf_tokens`/`faerie_tokens`** — necessário pra tokens de Elfo contarem certo nos cálculos de mana escalável (antes, tokens nunca contribuíam pra `elves_in_play`/`creatures_in_play`, subestimando a saída real do Priest of Titania, Elvish Archdruid, Marwyn e Circle of Dreams Druid sempre que havia token de Elfo em campo).

Teste de robustez: 15.000 partidas com timeout de 2s, **0 erros, 0 timeouts**.

**n=3000, seed_base=8000000, 8 turnos — comparação com o batch anterior (antes do landfall + antes do fix de token):**

| Métrica | v1 (sem landfall, bug do token) | v2 (com landfall, token fixo) | Δ |
|---|---|---|---|
| Turno médio de conjuração da Maralen | 4,60 | 4,67 | ~igual |
| Avg gatilhos de Maralen (exila 2) | 5,11 | 7,28 | **+42,5%** |
| Avg cartas exiladas total | 9,36 | 13,58 | +45,1% |
| Avg casts grátis via Maralen | 2,24 | 2,40 | +7,1% |
| Avg dobras via Roaming Throne | 0,21 | 0,35 | +66,7% |
| Combo Umbral Mantle montado | 7,8% | 7,7% | ~igual |
| Avg terrenos jogados (total) | (não rastreado) | 5,37 | — |
| Avg tokens de Elfo via landfall (Sindarin Liege) | — | 0,15 | (mecânica nova) |
| Avg contadores via landfall (Company) | — | 0,14 | (mecânica nova) |

**Leitura honesta — o salto grande (+42,5% nos gatilhos da Maralen) é majoritariamente o bug corrigido, não as cartas novas.** Os tokens de landfall do Sindarin Liege contribuem pouco em volume absoluto (0,15/partida — CMC 4, 1 cópia em 99, raramente resolve e ainda mais raramente com terreno sobrando na mão pra aproveitar). O grosso do aumento vem de Elvish Warmaster e Imperious Perfect (que já estavam na lista desde o início) finalmente disparando a Maralen quando criam token — um efeito que deveria ter existido desde a Simulação #1 e não existia. Registrado aqui com transparência total, não escondido como se fosse "ganho" das cartas novas. O combo do Umbral Mantle ficou estatisticamente idêntico (7,8% → 7,7%), como esperado — nenhuma das mudanças desta rodada afeta a montagem dele.

Resultados salvos em `maralen_v1_runs.jsonl` (sobrescrito com os 3000 jogos novos).

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

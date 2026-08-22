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

# Goldfish Log — Thranduil (Sultai)

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Simulação estatística v1 — escrita e rodada por Claude (não é dado seu)

**Atribuição:** assim como o simulador do Beorn, este script foi **escrito e executado por mim**, a seu pedido, nos mesmos moldes do `beorn_goldfish_v1.py`. Script completo salvo em `thranduil_goldfish_v1.py` nesta pasta — reproduzível, não é caixa-preta. Metodologia completa (modelo de mana tricolor, proxy estatístico pra "Elfos no cemitério", limitações conhecidas) documentada no docstring do próprio script.

**Resultado (n=2000, 8 turnos, multiplayer — compra sempre no T1 por CR 103.8a):**

```
Avg commander cast turn: 4.00 | por T5: 82,3% | por T6: 86,5%
Avg spells cast: 9.83 | Avg extra draws (gatilhos): 2.86
Avg ramp em campo: 2.31 | Avg remoção conjurada: 0.54
Avg gatilhos "elfo lendário entrou" (Thranduil draw2/discard1): 1.43
Avg cartas milhadas: 2.93 | Avg Elfos milhados pro cemitério (proxy): 0.49
Avg finishers ativados: 2.37 | turno médio do 1º: 4.83 | 53,4% dos jogos até T8
Avg cartas descartadas por limite de mão: 0.08
Avg battlefield final: 14.90 | Avg mão final: 0.68 | Avg terrenos jogados: 6.25
```

Consistente com o teste anterior de n=500 (turno do comandante 4,05→4,00; finisher até T8 55,0%→53,4%; mão final 0,72→0,68) — números estáveis, não é ruído de amostra pequena.

**Duas limitações conhecidas, ainda não corrigidas (mesma transparência que apliquei no Beorn):**
1. **"Elfos no cemitério" é um proxy estatístico**, não contagem real carta-por-carta — assume ~16,5% de chance de qualquer carta milhada ser Elfo, com base na densidade real do deck. Não rastreia identidade individual.
2. **Avg mão final ficou muito baixo (0,68)** — sinal de que o motor de conjuração está esvaziando a mão demais por turno, porque o script (como o do Beorn antes das correções) não rastreia mana já gasta dentro do turno, só um teto por carta individual. Isso provavelmente infla `spells_cast` e `finishers_ativados` de forma otimista. Ainda não corrigi isso — fica pra quando você validar os números, do jeito que fizemos com o Beorn.

---

### Correção — as 4 engines de draw não tinham lógica nenhuma implementada

Você perguntou se o Rhystic Study e as outras engines de draw estavam gerando compra de verdade na simulação. Não estavam — mesmo padrão de bug do Managorger Hydra no Beorn: só tinham a tag `draw_engine`/`draw_filter`, sem código conectado. Implementei as 4 de uma vez:

1. **Beast Whisperer / Champions of the Perfect** (`"whenever you cast a creature spell, draw a card"`) — implementado de forma **rigorosa, sem premissa**: toda vez que uma criatura é conjurada, cada engine já em campo compra 1.
2. **Edric, Spymaster of Trest** (`"whenever a creature deals combat damage to a player, its controller may draw"`) — precisou de uma **fase de combate nova** (`combat_step()`), que não existia nesse script. Simplificação: sem doença de invocação nem bloqueadores modelados (mesmo nível do combat_step do Beorn) — toda criatura em campo é tratada como atacando e conectando.
3. **Rhystic Study** (`"whenever an opponent casts a spell, you may draw unless that player pays {1}"`) — depende de spells de **oponentes**, mesma limitação estrutural do Managorger. Usei **duas premissas explícitas**:
   - `ASSUMED_OPPONENT_SPELLS_PER_TURN = 2` — reaproveitei a mesma premissa que você já validou pro Managorger Hydra, por consistência.
   - `ASSUMED_RHYSTIC_STUDY_PAY_RATE = 0.5` — **essa é minha, não validada por você**: assumi que o oponente paga o {1} pra evitar a compra 50% das vezes. Se achar que isso não reflete sua mesa, me diga o número certo.
4. **Underrealm Lich** (`"If you would draw a card, instead look at top 3, put 1 into hand, rest into graveyard"`) — reescrevi `GameState.draw()` pra redirecionar TODAS as compras (inclusive as das outras 3 engines) por esse filtro quando ele está em campo. Isso também alimenta o proxy de "Elfos no cemitério", já que as 2 cartas descartadas contam como mill.

**Bônus:** ao implementar Edric, também modelei os tokens do Lathril via dano de combate (`"whenever Lathril deals combat damage to a player, create that many 1/1 Elf Warrior tokens"`), que dependia da mesma fase de combate nova.

**Resultado (n=2000, mesmos parâmetros, seed diferente pra ser amostra independente):**

| Métrica | Antes (bug) | Depois |
|---|---|---|
| Avg extra draws (gatilhos) | 2,86 | **14,12** |
| Avg spells cast | 9,83 | 11,87 |
| Avg mão final | 0,68 | 2,49 |
| Avg cartas descartadas por limite de mão | 0,08 | **6,38** |
| Avg compras via Beast Whisperer/Champions | 0 (bug) | 2,22 |
| Avg compras via Edric (combate) | 0 (bug) | **8,36** |
| Avg tokens de Elfo via Lathril (combate) | 0 (bug) | 1,61 |
| Rhystic Study — avg compras / vezes que pagaram | 0 (bug) | 4,74 / 4,55 |
| % finisher ativado até T8 | 53,4% | 59,2% |

**Leitura, com ressalva:** o número do Edric (8,36 compras médias por partida) chama atenção — é alto até pros padrões reais desse card, que já é notoriamente forte em mesas largas. Isso provavelmente está inflado pela falta de bloqueadores/doença de invocação: na simulação, toda criatura conecta todo turno, o que não reflete uma mesa real onde oponentes bloqueiam ou removem o Edric assim que percebem o motor (é um alvo clássico de remoção prioritária). Trato esse número como teto otimista, não estimativa realista — mesma ressalva que já vale pro resto do motor de combate simplificado.

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

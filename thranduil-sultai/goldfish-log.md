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

### Correção — premissas validadas por você (Rhystic Study 50%, Edric ~2 turnos de vida)

Você confirmou a taxa de 50% de pagamento do Rhystic Study (`ASSUMED_RHYSTIC_STUDY_PAY_RATE`, sem mudança de código, só deixou de ser "não validada" no comentário) e pediu pra assumir que o **Edric sobrevive em média 2 dos seus turnos** antes de ser removido — mesmo padrão de correção que já tínhamos aplicado no Managorger Hydra do Beorn.

Implementado: quando Edric entra, sorteia um tempo de vida (`randint(1,3)`, média 2) via `ASSUMED_EDRIC_LIFESPAN_TURNS_MEAN = 2`; ao fim do combate do turno em que esse prazo estoura, ele sai do campo e para de gerar compra.

**Re-execução com n=2000, seed independente:**

| Métrica | Sem limite de vida do Edric | Com Edric removido (~2 turnos) |
|---|---|---|
| Avg compras via Edric (combate) | 8,36 | **2,30** |
| Edric conjurada em X% dos jogos | (não rastreado) | 14,9% |
| Edric removida antes do T8 | — | 88,6% dos jogos em que foi conjurada, turno médio de morte: 4,95 |
| Avg extra draws (gatilhos, todas as engines somadas) | 14,12 | 9,11 |
| Avg cartas descartadas por limite de mão | 6,38 | 1,89 |
| % finisher ativado até T8 | 59,2% | 58,1% |

O número do Edric caiu de 8,36 pra 2,30 — muito mais compatível com o padrão real do card numa mesa que remove agressivamente motores óbvios. A queda também arrastou pra baixo o total de "extra draws" (14,12→9,11) e o descarte por limite de mão (6,38→1,89), já que menos compra sobrando significa menos cartas excedentes.

---

### Correção maior — teto real de mana por turno + rastreio de "color screw" de azul

Duas coisas pedidas: (1) parar de checar cada carta contra `total_mana()` de forma independente (o que permitia, na prática, gastar mais mana do que existia no turno — mesmo bug que corrigi no Beorn antes) e (2) medir de verdade quantas vezes a base de mana fraca em azul (~9 fontes hard, sinalizada na auditoria estática) trava o comandante mesmo com mana total sobrando.

**Implementado:**
- `remaining_mana(state) = total_mana(state) - mana_spent_this_turn`, resetado no início de cada turno. `can_cast()`, o loop de conjuração e `activate_finishers()` agora descontam do total real conforme gastam — antes, cada checagem era independente e podia gastar mais mana do que existia.
- `blue_screw_turns`: conta turnos em que a mana total já daria pros 5 do comandante, mas não havia nenhuma fonte de `U` em campo.

**Re-execução com n=2000, seed independente:**

| Métrica | Sem teto de mana | Com teto de mana |
|---|---|---|
| Avg commander cast turn | 3,96 | **4,46** |
| Commander cast by T5 | 82,0% | 77,6% |
| Avg finishers ativados | 2,70 | **1,06** |
| % finisher ativado até T8 | 58,1% | **42,5%** |
| Avg turno do 1º finisher | 4,84 | 6,61 |
| Avg extra draws | 9,11 | 8,58 |
| Avg cartas descartadas por limite de mão | 1,89 | 1,62 |

**Leitura:** a diferença é grande — sem o teto de mana, o motor estava efetivamente "trapaceando" gastando mais mana do que tinha disponível em boa parte dos turnos, o que inflava tanto a velocidade do comandante quanto a taxa de finisher. Com o teto real, **42,5%** (não mais 58,1%) é o número que confia mais — os 3 overruns repetíveis (Tyvar the Pummeler, Ezuri, Elvish Warmaster) custam 4-7 mana de ativação, e competem por mana no mesmo turno com desenvolver o board, então essa queda faz sentido mecanicamente.

**Color screw de azul (novo, nunca medido antes):**

```
Avg turnos com blue screw por partida: 0,34
% de partidas com pelo menos 1 turno de blue screw: 12,3%
Turno médio do 1º blue screw: 4,30
```

Confirma quantitativamente a preocupação qualitativa da auditoria: em **~12% das partidas**, há pelo menos um turno em que a mana total já dava pro comandante, mas faltou uma fonte de azul especificamente — e isso costuma acontecer bem cedo (turno ~4,3 em média), atrasando exatamente o motor "elfo lendário entra → compra 2" que depende do Thranduil estar em campo.

### Mudança de deck — mais remoção, cortes de peças de baixo impacto (ver `auditoria.md` seção 6)

Aplicada a troca real de remoção (ver auditoria — Chaos Warp/Vindicate da sugestão original nem eram Sultai, corrigido): cortadas Agatha's Soul Cauldron, Oversold Cemetery e Harmonized Crescendo; adicionadas Deadly Rollick, Putrefy e Feed the Swarm. `lista.md` e o `DECKLIST_TEXT`/`CARD_DB` do simulador atualizados juntos.

**Re-execução com n=2000, seed independente, lista corrigida:**

| Métrica | Antes da troca | Depois da troca |
|---|---|---|
| Avg remoção conjurada | 0,52 | **1,11** |
| % finisher ativado até T8 | 42,5% | 38,4% |
| Avg battlefield final | 17,14 | 16,71 |
| Avg turnos com blue screw | 0,34 | 0,31 |

A remoção mais que dobrou (0,52→1,11), como esperado — as 3 cartas cortadas não competiam por essa função. A taxa de finisher caiu um pouco (42,5%→38,4%) porque as peças cortadas tinham algum valor de desenvolvimento/draw que ajudava indiretamente a montar o board mais rápido; é uma troca real (mais interação, um pouco menos de velocidade pra fechar), não um erro de modelagem.

### Correção — Agatha's Soul Cauldron e Oversold Cemetery voltaram (leitura errada sobre GY revertida)

O corte dos dois acima usou uma leitura errada: "dependem do volume de Elfos na GY, que é baixo". Falso nos dois casos — Agatha's Soul Cauldron exila carta de **qualquer** cemitério (hate real, não GY-payoff próprio), e Oversold Cemetery só pede 4+ **criaturas** na GY, não Elfos especificamente (Buried Alive sozinho já bate isso). Detalhe completo em `auditoria.md` seção 6.

Voltaram pro deck no lugar de **Eclipsed Elf** e **Lys Alana Huntmaster** (cortes que sobreviveram a toda a matriz de sinergia mecânica — `thranduil_synergy_matrix.py` — sem nenhuma função protegida, sem habilidade herdável pela Thranduil, sem presença no EDHREC).

**Re-execução com n=2000, lista corrigida (Agatha's Soul Cauldron + Oversold Cemetery de volta, Eclipsed Elf + Lys Alana Huntmaster fora):**

```
Avg commander cast turn: 4,42 | por T5: 79,1% | por T6: 85,2%
Avg remoção conjurada: 1,12 | Avg ramp em campo: 2,91
Avg finishers ativados: 0,98 | 41,9% dos jogos até T8
Avg turnos com blue screw: 0,29 | 10,6% das partidas com pelo menos 1
```

Números estáveis em relação à rodada anterior — a troca dessas 2 cartas específicas não muda o quadro geral, é o ajuste correto de uma leitura equivocada, não uma mudança estrutural.

### Implementado — duplicação de gatilhos do Roaming Throne

Você pediu pra implementar o efeito real do Roaming Throne (`"If a triggered ability of another creature you control of the chosen type triggers, it triggers an additional time"`) em vez de só ter ele como tag decorativa — e pediu que isso vire regra permanente pra qualquer deck futuro com essa carta (documentado em `references/goldfish-sim-card-rules.md` do skill mtg-commander).

**Premissa:** tipo escolhido sempre "Elf" (única escolha sensata nesse deck — todo gatilho de criatura que já modelei tem fonte Elfo).

**Implementado nos 4 gatilhos de criatura já existentes no simulador:**
- Gatilho da própria Thranduil (elfo lendário entra → compra 2, descarta 1) — dispara uma **segunda vez completa** (compra 2 + descarta 1 de novo), não só dobra os números de um disparo.
- Beast Whisperer / Champions of the Perfect (draw ao conjurar criatura) — compra dobrada por engine em campo.
- Edric (draw por dano de combate) — cada instância do gatilho (uma por criatura que conecta) dispara de novo.
- Lathril (tokens por dano de combate) — cria os tokens uma segunda vez.

**Não dobra Rhystic Study** — não é criatura, então a cláusula do Roaming Throne não se aplica a ela.

**Resultado (n=2000):**

```
Roaming Throne em campo em 11,2% dos jogos (tipo escolhido: Elf)
Avg gatilhos de criatura Elfo dobrados por partida: 2,06
```

Só 11,2% dos jogos (1 carta em 99, compra é aleatória), mas quando ela resolve, dobra em média ~2 gatilhos de criatura por partida — consistente com o que já tinha argumentado sobre ela na discussão de corte (o interação com o próprio gatilho da Thranduil é real, não hipotética).

### Implementados os 11 Elfos restantes com gatilho próprio (exceto Selfless Safewright)

Varredura mecânica em `oracle_text` (não de memória) achou **16 Elfos com gatilho próprio** no deck, incluindo a própria Thranduil. Só 4 estavam implementados (Thranduil, Beast Whisperer/Champions, Edric, Lathril). Implementei os outros 11 a pedido do usuário — todos exceto **Selfless Safewright** (dobrar hexproof/indestructible não muda nada).

**Regra confirmada com o usuário antes de implementar:** Roaming Throne só dobra a parte GATILHADA de cada carta ("Whenever"/"At the beginning of"/"When ... enters"). Nunca dobra habilidade ATIVADA (`{custo}: efeito`), mesmo quando a mesma carta tem as duas (Selvala e Marwyn são exemplos — só o gatilho de contador/compra dobra, a habilidade de mana delas nunca).

**Adicionado:** campo `power` no `Card` dataclass, populado automaticamente do cache do Scryfall pra todas as criaturas (necessário pra Selvala — "maior poder entre as criaturas" — e Gwenna — "criatura poder ≥5").

| Carta | Gatilho implementado | Efeito numérico real no modelo? |
|---|---|---|
| Marwyn, the Nurturer | Outro Elfo entra → +1/+1 nela | Sim — contador rastreado |
| Selvala, Heart of the Wilds | Criatura entra com maior poder que todas as outras → compra | Sim |
| Elrond, Moon-Reader | Ativa habilidade de criatura (1x/turno) → compra | Sim |
| Elvish Warmaster | 1+ Elfo entra (1x/turno) → token | Sim |
| Glissa Sunslayer | Dano de combate → modo "compre 1, perca 1 vida" | Só a compra (vida não é rastreada no state) |
| Gwenna, Eyes of Gaea | Conjura criatura poder≥5 → contador+destapa | Só o contador |
| High Perfect Morcant | Ela/outro Elfo entra → blight no oponente | **Não** — sem oponente real, só contador de "disparou" |
| Maralen, Fae Ascendant | Ela/Elfo/Faerie entra → exila biblioteca do oponente | **Não** — mesma razão, só contador |
| Ruthless Winnower | Upkeep → sacrifica seu próprio não-Elfo | Sim, mas **achado real:** o deck não tem NENHUMA criatura não-Elfo (Roaming Throne também vira Elfo pela premissa de tipo escolhido) — a auto-punição da carta nunca acontece nesse build |
| Tyvar the Bellicose | Elfo(s) atacam → deathtouch | **Não** — sem bloqueadores modelados no motor de combate |

**Resultado (n=2000):**

```
Avg contadores em Marwyn: 1,04
Avg compras via Selvala: 0,12
Avg compras via Elrond: 0,12
Avg tokens via Elvish Warmaster: 0,41
Avg compras via Glissa Sunslayer: 0,57
Avg contadores em Gwenna: 0,13
Avg gatilhos de High Perfect Morcant (sem efeito numérico): 0,32
Avg gatilhos de Maralen (sem efeito numérico): 0,18
Avg auto-sacrifícios via Ruthless Winnower: 0,00
Avg gatilhos de Tyvar the Bellicose (sem efeito numérico): 0,49

Roaming Throne dobra em média 4,61 gatilhos de criatura por partida (subiu de ~2 pra ~4,6 com os 11 novos gatilhos elegíveis pra dobrar)
```

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

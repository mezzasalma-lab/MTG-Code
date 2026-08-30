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

### Rebalanceada da lista — 3 cortes / 3 adições (2026-08-21)

**Cortes:** Feed the Swarm, Putrefy, Urza's Incubator.
**Adições:** Devoted Druid, Imperious Perfect, Formidable Speaker.

Antes de rodar, `DECKLIST_TEXT` do script foi atualizado pra bater com `lista.md` (as três cartas cortadas ainda estavam no texto embutido; as três novas já existiam no `CARD_DB` de sessões anteriores, só faltava incluir na decklist). Deck volta a bater 99 mainboard + comandante.

**Awaken the Honored Dead ({B}{G}{U}) mantida** — avaliação separada mostrou que, apesar de ser a única peça de remoção do deck que pede as 3 cores simultâneas (nenhuma outra remoção passa de 2), é Saga de conjuração única (atraso não desperdiça valor) e a simulação de disponibilidade de mana (n=3000, ver conversa) mostrou B+G+U simultâneos disponíveis em 75,2% dos jogos até o turno 3 e 85,1% até o turno 5 — modelo otimista (ignora terreno-entra-tapado), mas não a ponto de justificar corte agora.

**n=2000 (`thranduil_v1_runs_rebalanced_2000.jsonl`, seed_base=1400000), lista pós-rebalanceada:**

```
Avg commander cast turn: 4,42 | por T5: 79,9% | por T6: 86,0%
Avg spells cast: 11,23 | Avg extra draws: 10,24
Avg ramp em campo: 3,19 | Avg remoção conjurada: 0,78
Avg finishers ativados: 1,10 | 42,8% dos jogos até T8
Avg turnos com blue screw: 0,32 | 11,9% das partidas com pelo menos 1 | turno médio do 1º: 4,19
Roaming Throne em campo: 11,2% | Avg gatilhos dobrados: 4,91
```

**Comparação com o baseline anterior (11-elfos, antes do corte de Feed the Swarm/Putrefy):**

| Métrica | Antes (1,12 remoção) | Depois (rebalanceada) |
|---|---|---|
| Avg remoção conjurada | 1,12 | **0,78** |
| Avg commander cast turn | 4,42 | 4,42 |
| Commander cast by T5 | 79,1% | 79,9% |
| Avg finishers ativados | 0,98 | 1,10 |
| % finisher até T8 | 41,9% | 42,8% |
| Avg turnos com blue screw | 0,29 | 0,32 |

**Leitura:** a remoção conjurada caiu de verdade (1,12→0,78) porque Feed the Swarm e Putrefy eram remoção real e nenhuma das 3 adições é. Isso é esperado e é a troca deliberada — trocou-se 2 remoções por 2 peças de desenvolvimento de board (Imperious Perfect = anthem + token, Formidable Speaker = seleção de carta que alimenta o GY) e 1 mana dork extra (Devoted Druid). O resto do perfil do deck (velocidade do comandante, taxa de finisher, blue screw) ficou estatisticamente estável — a troca não introduziu nenhum efeito colateral estrutural, só reduziu a densidade de remoção pontual (contagem estática cai de 10 pra 8 efeitos confirmados por oracle_text (Assassin's Trophy, Deadly Rollick, Trystan's Command, Awaken the Honored Dead, Ruthless Winnower, Kindred Dominance, Raise the Palisade, Agatha's Soul Cauldron) — ainda dentro da faixa 8-10 recomendada, mas agora no piso, não mais no meio dela).

---

### Fonte de U — Underground River no lugar de Llanowar Wastes (2026-08-21)

Pedido do usuário: fonte de U **destapada** (não tapada) pra engordar azul sem ceder velocidade de mana. Llanowar Wastes (`{T}: Add {C}` / `{T}: Add {B} or {G}. Causa 1 dano a você`) era 1 dos 7 terrenos do deck que só tocam B/G — cor já bem suprida (15 fontes de G, 12 de B contra só 10 de U antes desta troca). Trocado por **Underground River**, a mesma painland exata (sempre destapada, sem condição de ETB), só que B/U (`{T}: Add {U} or {B}. Causa 1 dano a você` — Scryfall, `color_identity: [B, U]`, legal em Commander, `$2,43`).

`DECKLIST_TEXT` e `CARD_DB` do script atualizados (`add("Underground River", 0, {"Land"}, produces={"B", "U"})`), deck volta a bater 99 mainboard + comandante.

**n=2000 (`thranduil_v1_runs_underground_river_2000.jsonl`, seed_base=1500000):**

```
Avg commander cast turn: 4,44 | por T5: 80,4% | por T6: 86,5%
Avg remoção conjurada: 0,77 | Avg ramp em campo: 3,22
Avg finishers ativados: 1,11 | 43,9% dos jogos até T8
Avg turnos com blue screw: 0,23 | 8,4% das partidas com pelo menos 1 | turno médio do 1º: 4,22
Roaming Throne em campo: 11,7% | Avg gatilhos dobrados: 4,36
```

| Métrica | Antes (10 fontes de U) | Depois (11 fontes de U) |
|---|---|---|
| Avg turnos com blue screw | 0,32 | **0,23** |
| % partidas com blue screw | 11,9% | **8,4%** |
| Turno médio do 1º blue screw | 4,19 | 4,22 |
| Avg commander cast turn | 4,42 | 4,44 |
| Avg remoção conjurada | 0,78 | 0,77 |

**Leitura:** melhora real e mensurável no problema de azul — blue screw caiu quase 30% relativo (11,9%→8,4%) com uma única troca 1:1, sem custo de velocidade de mana (painland pra painland, ambas sempre destapadas) nem redução de terrenos totais (37 mantido). O resto do perfil ficou estável, como esperado — a troca não mexeu em nenhuma outra carta. Ainda restam 6 terrenos B/G-only no deck (Gilt-Leaf Palace, Nurturing Peatland, Undergrowth Stadium, Wastewood Verge, Deathcap Glade, Overgrown Tomb) como candidatos a trocas futuras se quiser reduzir o screw ainda mais.

---

### Formidable Speaker → Arcane Signet (2026-08-21)

Pedido do usuário: melhorar a chance de ter mana pro comandante em T4/T5/T6 e reduzir mulligans problemáticos. Testados 4 candidatos no lugar do Formidable Speaker (Thranduil's Company nunca foi considerado — vetado permanentemente pelo usuário, `references/user-standing-rules.md` regra 5):

| Candidato | Resultado do teste | Decisão |
|---|---|---|
| **Arcane Signet** (`{2}`, any color na identidade, sempre destapado) | T4 +3,7pp, T5 +1,5pp, blue screw -0,8pp | **Escolhido** |
| Chromatic Lantern (`{3}`, fixa TODOS os terrenos — mecânica real implementada em `color_sources()` pro teste) | Mesmo efeito prático do Arcane Signet, só que 1 mana mais caro e 1 turno mais lento | Descartado |
| Urza's Incubator (`{3}`, custo -2 pra Elfos — mecânica real implementada em `can_cast`/`cast_spell`) | T4 +0,3pp, blue screw 0pp — não ataca o gargalo de cor | Descartado |
| The World Tree | `color_identity` inclui R/W (custo de sacrifício) — **ilegal** em B/G/U | Descartado, nem testado em goldfish |

`lista.md`, `CARD_DB` e `DECKLIST_TEXT` atualizados (`add("Arcane Signet", 2, {"Artifact"}, tags={"ramp"}, produces={"B", "G", "U"})`, adicionado também a `KEEPERS` pra pesar na decisão de mulligan). Deck volta a bater 99 mainboard + comandante.

**n=2000 (`thranduil_v1_runs_arcane_signet_2000.jsonl`, seed_base=2000000):**

```
Avg commander cast turn: 4,31 | por T4: 62,1% | por T5: 82,8% | por T6: 88,8%
Avg mulligans: 0,47 | Avg remoção conjurada: 0,76 | Avg ramp em campo: 3,50
Avg turnos com blue screw: 0,26 | 9,3% das partidas com pelo menos 1
```

| Métrica | Antes (Formidable Speaker) | Depois (Arcane Signet) |
|---|---|---|
| Avg commander cast turn | 4,44 | **4,31** |
| Por T4 | 58,5% | **62,1%** |
| Por T5 | 80,4% | **82,8%** |
| Por T6 | 86,5% | **88,8%** |
| % partidas com blue screw | 8,4% | **9,3%*** |

*\*O % de blue screw oscilou pra cima nessa rodada específica (ruído de seed — a mesma troca testada isoladamente antes deu 9,2%, dentro da mesma faixa). O ganho real e consistente está nos números de turno do comandante, que são os que mais importam pro plano do deck.*

**Leitura:** ganho real e mensurável em cima da base já melhorada pelo Underground River — turno médio do comandante caiu de 4,44 pra 4,31, chance por T4 subiu quase 4 pontos. Combinado com a troca do Underground River (sessão anterior), o deck saiu de ~58,9%/80,7%/86,5% (T4/T5/T6, antes de qualquer correção de mana) pra 62,1%/82,8%/88,8% hoje.

---

### Deathcap Glade/Undergrowth Stadium → Botanical Sanctum/Hinterland Harbor (2026-08-23)

Terceira rodada de correção de U (depois de Underground River e Arcane Signet), pedida pelo usuário depois da auditoria com a Maralen ter reaproveitado a metodologia de recontagem de fontes de cor e achado a base de mana do Thranduil um pouco desbalanceada ainda: G 22 / B 16 / U 12. Trocados os 2 terrenos B/G puros sem utilidade extra (Deathcap Glade, Undergrowth Stadium — este último ainda com a desvantagem de só destapar com 2+ oponentes) por Botanical Sanctum e Hinterland Harbor, ambos G/U reais e acessíveis (sem precisar de dual original — o usuário não tinha ABUR sobrando).

`DECKLIST_TEXT` e `CARD_DB` atualizados (`add("Botanical Sanctum", 0, {"Land"}, produces={"G", "U"})`, `add("Hinterland Harbor", 0, {"Land"}, produces={"G", "U"})`), deck volta a bater 99 mainboard + comandante. Teste de robustez: 15.000 partidas com timeout de 2s, 0 erros/timeouts.

**Comparação pareada (mesmas 3000 seeds, seed_base=6500000) — antes (revertido via monkeypatch pro `DECKLIST_TEXT` antigo) vs depois:**

| Métrica | Antes (Deathcap Glade + Undergrowth Stadium) | Depois (Botanical Sanctum + Hinterland Harbor) |
|---|---|---|
| Avg turnos com blue screw | 0,214 | **0,141** |
| % partidas com blue screw | 8,1% | **5,6%** |
| Turno médio do 1º blue screw | 4,23 | 4,29 |

**n=3000 oficial (`thranduil_v1_runs_manafix2.jsonl`, seed_base=6500000) — números completos pós-troca:**

```
Avg commander cast turn: 4,30 | por T5: 83,9% | por T6: 89,4%
Avg remoção conjurada: 0,77 | Avg ramp em campo: 3,45
Avg finishers ativados: 1,13 | 43,5% dos jogos até T8
Avg turnos com blue screw: 0,14 | 5,6% das partidas com pelo menos 1 | turno médio do 1º: 4,29
Roaming Throne em campo: 11,5% | Avg gatilhos dobrados: 4,75
```

**Leitura:** terceira melhora consecutiva e mensurável na mesma métrica — blue screw caiu de 11,9% (base original) → 8,4% (Underground River) → 9,3%/~9,2% (ruído após Arcane Signet, sem regressão real) → **5,6%** agora. Redução relativa de mais de **50%** desde o primeiro fix. Turno médio do comandante ficou estável (4,31→4,30, dentro do ruído), confirmando que a troca não custou velocidade — só resolveu o gargalo de cor. Restam agora só 4 terrenos B/G-only no deck com utilidade própria além da fixação (Gilt-Leaf Palace, Nurturing Peatland, Wastewood Verge, Overgrown Tomb) — não recomendados pra troca a menos que o objetivo mude pra maximizar U além do necessário.

---

### Correção — checklist obrigatória de mecânica (regra nova pós-Beorn) — 2026-08-28

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks.

**Achado mais grave — landfall só logava, nunca criava efeito real:**
`play_land()` tinha `log.append({"trigger": "landfall_elf_token", ...})`
pra Thranduil, Sindarin Liege, mas **nenhum token era criado de verdade** —
o log existia, o efeito não. Thranduil's Company (2 contadores +1/+1 no
landfall) nem tinha esse log — 100% ausente. E o próprio segundo land drop
do Company (`As long as you control another Elf, you may play an
additional land`) estava **hard-bloqueado**: `if state.land_played: return`
no topo da função impedia qualquer segunda jogada de terreno,
independente do Company estar em campo.

**Outros bugs reais achados (todos de mana):**

- **13 mana dorks criatura sem doença de invocação nenhuma** — produziam
  mana no próprio turno em que eram conjurados. Novo
  `creature_cast_turn`/`_dork_ready()` (mesmo padrão de outros decks desta
  sessão).
- **Gwenna, Eyes of Gaea**: "{T}: Add TWO mana" tratada como ramp genérico
  (+1) — corrigido pra +2 (a restrição "só pra spells/habilidades de
  criatura" não foi modelada, deck é quase todo criatura).
- **Cavern of Souls**: o docstring do script já documentava isso como
  "condicional demais pra modelar" e tratava como incolor — mas a mesma
  situação no Ur-Dragon (regra #6 adendo, `user-standing-rules.md`) já
  tinha estabelecido que, num deck tribal com tipo óbvio (aqui: Elfo),
  vira fixação REAL pro subconjunto de spells daquele tipo. Corrigido com
  a mesma lógica (tag `elf_only_color`).
- **Yavimaya, Cradle of Growth**: "Each land is a Forest" nunca
  implementada — nenhum terreno ganhava G extra por ela.
- **Reflecting Pool**: fixa em {B,G,U} quando o texto real é "any type
  that a land you control could produce" (dinâmico, deveria refletir os
  OUTROS terrenos em campo).
- **Revitalizing Repast // Old-Growth Grove**: faltava o modo B
  ("{T}: Add {B} or {G}"), só G estava modelado.
- **Imperious Perfect**: "{G},{T}: Create a 1/1 Elf Warrior token" —
  `activation_cost` nunca setado (default 0), e `activate_finishers()`
  pula qualquer carta com custo ≤0 — nunca disparava.

**Não corrigido nesta rodada (decisão de escopo, documentada):** Three
Tree City's habilidade de mana colorida escalável (exigiria uma pool de
mana com cor que este arquivo não tem); Fauna Shaman, Eladamri's dig,
Prime Speaker Vannifar, Agatha's Soul Cauldron, Jarad's sac-drain — 5
habilidades ativadas ainda não implementadas de verdade, ficam pra uma
rodada dedicada; Elrond continua só disparando via ativação de finisher,
não do gatilho real (qualquer tap de mana dork).

**Resultado (n=2000, seed_base=71000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg spells cast | 11,62 | **11,20** |
| Avg finishers ativados | 1,15 | **0,87** |
| % jogos com finisher até T8 | 46,0% | **40,0%** |
| Avg tokens via landfall (Sindarin Liege, novo) | — | **0,28** |
| Avg contadores via landfall (Company, novo) | — | **0,70** |
| Avg tokens via Imperious Perfect (novo) | — | **0,37** |

Queda moderada nas métricas de desenvolvimento — esperada, já que a
correção de doença de invocação (13 dorks) desacelera o ramp real mais do
que os novos motores (landfall/Imperious Perfect) compensam. Direção
correta: o deck estava sendo simulado com mana rápida demais.

**Robustez:** sweep de 20.000 jogos (seeds 71000–91000, timeout 2s/jogo) —
0 erros, 0 timeouts.

`lista.md` não mudou.

---

### Correção — Oversold Cemetery sem efeito real + bloco de métricas básicas ausente (regra das 5 categorias) — 2026-08-29

**Gatilho:** fechamento da análise comparativa com Ur-Dragon e Beorn — o
Thranduil nunca tinha recebido o bloco `--- Métricas básicas (checklist
obrigatória) ---` (RAMP/DRAW/INTERACTION/RECURSION/FINISHER-LETHALITY) que
a regra permanente da Correção #6 do Beorn exige "para tudo, sempre
também". Ao montar esse bloco, RECURSION não tinha nenhuma fonte de dado
real — `Oversold Cemetery` estava cadastrada com `tags={"recursion"}` desde
a correção pós-Beorn (802258d) mas **nunca teve efeito de jogo implementado
de verdade**, mesma classe de bug do landfall que só logava sem criar
efeito (Correção pós-Beorn original).

**Corrigido:** `Oversold Cemetery` — *"At the beginning of your upkeep, if
there are four or more creature cards in your graveyard, you may return a
creature card from your graveyard to your hand."* Implementado no início
do upkeep (`play_turn`, mesma posição do gatilho de Ruthless Winnower):
conta criaturas no cemitério, se ≥4 devolve a de maior custo de mana pra
mão (`oversold_cemetery_returns`). Bloco de métricas básicas adicionado ao
`run_batch()`, RECURSION alimentado por essa nova métrica.

**Robustez:** 20.000 seeds (71000–91000), timeout padrão — 0 erros.

**Batch oficial, n=5000, seed_base=71000 (antes → depois, mesma seed):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg spells cast | 11,16 | 11,25 |
| Avg extra draws | 10,12 | 10,26 |
| Oversold Cemetery ativou | — | 5,4% dos jogos, avg 0,08/partida |

**Leitura:** impacto real mas pequeno — Oversold Cemetery raramente acumula
4+ criaturas no cemitério neste deck (mill é baixo, ~4,5 cartas/partida
totais, não todas criaturas), então o motor de recursão fica majoritariamente
dormente. Ainda assim, é um efeito real que antes simplesmente não existia
— igual à lição do landfall antes desta correção: melhor um gatilho raro
mas real do que uma tag morta. `lista.md` não muda.

---

### Rodada oficial final pós-checklist de mecânica — 2026-08-29

**n=5000, seed_base=71000 (padrão do script), com todas as correções desta
sessão aplicadas (landfall, doença de invocação, Oversold Cemetery):**

```
Avg mulligans: 0,48
Avg commander cast turn: 4,35 | por T5: 83,7% | por T6: 89,2%
Avg spells cast: 11,25 | Avg extra draws: 10,26
Avg finishers ativados: 0,85 | 38,9% dos jogos com finisher até T8
Avg turnos com blue screw: 0,15 | 6,2% das partidas com pelo menos 1

--- Métricas básicas (checklist obrigatória) ---
RAMP: 3,45 | DRAW: 10,26 | INTERACTION: 0,73 | RECURSION: 0,08
FINISHER/LETHALITY: 0,85 ativados, 38,9% até T8, turno médio 6,89
```

**Leitura:** número de referência oficial atual do deck, com as 5 métricas
básicas obrigatórias registradas pela primeira vez juntas num único batch
(paridade com Ur-Dragon e Beorn). RECURSION (0,08) é visivelmente a
categoria mais fraca do deck — não por bug, mas porque só uma carta
(`Oversold Cemetery`) provê recursão real e ela raramente encontra a
condição. Vale nota pra uma futura sessão de deckbuilding (fora do escopo
desta auditoria de mecânica), não uma mudança de lista agora.

---

### Leva de 200 jogos — análise de melhoria (goldfish instrumentado, n=200, seed_base=8900000) — 2026-08-29

**Contexto:** mesmo pedido do Beorn — leva de 200 jogos pra minerar dados
reais de melhoria, não só confirmar médias.

**Números (dentro do ruído esperado frente ao batch oficial de 5000):**

```
Avg commander cast turn: 4,25 | por T5/T6: 88,0%/94,5%
Avg finishers ativados: 0,96 | 42,0% dos jogos com finisher até T8
Avg turnos com blue screw: 0,10 | 5,0% das partidas afetadas
RAMP 3,54 | DRAW 10,67 | INTERACTION 0,65 | RECURSION 0,06
```

**Diagnóstico (minerado direto do `.jsonl`):**

- **Comandante e mana não são o gargalo:** só 1,0% dos jogos nunca conjuram
  Thranduil, e só 5,0% têm algum turno de blue screw — a manabase de 3
  cores segue sólida, confirmando as correções anteriores desta sessão.
- **RECURSION está estruturalmente morta:** **95,5% dos jogos terminam sem
  nenhuma ativação de Oversold Cemetery.** Não é mais um bug de
  implementação (corrigido nesta sessão) — é que o deck não milha o
  suficiente pra acumular as 4 criaturas na GY que a carta exige: avg de
  mill total é só 4,5 cartas por partida inteira (nem todas criaturas). A
  única fonte de recursão real da lista está numa condição que o resto do
  deck não ajuda a cumprir.
- **Fechar o jogo também é o gargalo aqui, como no Beorn:** **58,0% dos
  jogos terminam SEM nenhum finisher ativado** até o turno 8, apesar da
  lista ter 8 cartas com tag de finisher (Finale of Devastation, Elvish
  Warmaster, Ezuri, Tyvar the Pummeler, Jarad, Lathril, Kindred Summons,
  Bloodline Bidding) — mais opções nominais que o Beorn (que tem ~5-6), mas
  taxa de sucesso parecida. Motivo provável: a maioria dessas é uma
  habilidade ATIVADA cara (custo 5-7 de mana) que compete por mana no MESMO
  turno em que já se gastou pra desenvolver o board, em vez de um efeito
  instantâneo de "ataque agora" — diferente do Craterhoof do Beorn, que
  resolve e já fecha o combate no mesmo turno sem custo adicional.

**O que podemos melhorar (recomendação, não aplicada — decisão do
usuário):**

1. **Recursão:** trocar `Oversold Cemetery` (95,5% inativa) por uma peça de
   recursão que não dependa de um gatilho de 4+ criaturas na GY — ex.
   `Eternal Witness` (devolve QUALQUER carta do cemitério pra mão, sem
   pré-requisito, e já está validada e funcionando bem no Beorn nesta
   mesma sessão) ou `Regrowth`. Ataca a métrica mais fraca (0,06) na raiz.
2. **Finisher/lethality:** a lista não tem nenhum efeito de "overrun"
   incondicional (all creatures +X/+X, resolve e ataca no mesmo turno) —
   só habilidades ativadas caras. Como o deck já vai largo com tokens de
   Elfo (Imperious Perfect, Elvish Warmaster, Lathril), um efeito desse
   tipo converteria board width em dano de forma muito mais confiável que
   as ativações de 5-7 mana atuais. `Craterhoof Behemoth` é verde, já
   validado como o melhor finisher do Beorn nesta mesma sessão, e encaixa
   na identidade de cor (Sultai inclui verde) — candidato natural de
   inclusão se o usuário quiser fechar esse gargalo.

**Robustez:** herdada dos sweeps já rodados nesta sessão — nenhum código
mudou nesta rodada, só mineração de dados de uma amostra nova.

---

### Correção — Tyvar, Jubilant Brawler nunca auditado (categoria 12) + Agatha's Soul Cauldron sem efeito real — 2026-08-29

**Gatilho (usuário):** apontou que os finishers/peças de valor do Thranduil
incluem "Tyvar the Pummeler e outros elfos como Jarad, que ele pode copiar
as atividades do cemitério" — questionando o diagnóstico anterior de que
RECURSION é fraca "porque só o Oversold Cemetery existe".

**Verificação contra o oráculo real (Scryfall), carta por carta:**

- **Tyvar, the Pummeler** ({1}{G}{G}): confirmado — `{3}{G}{G}: Creatures
  you control get +X/+X until end of turn, where X is the greatest power
  among creatures you control.` É um overrun repetível, **sem nenhuma
  interação com cemitério**. Já estava corretamente modelada como
  `finisher_repeatable`, custo 5 — nenhuma mudança necessária aqui.
- **Jarad, Golgari Lich Lord**: tem `Sacrifice a Swamp and a Forest: Return
  this card from your graveyard to your hand` — recursão real, mas
  **auditada e confirmada estruturalmente inatingível neste simulador**:
  Jarad só entra no cemitério se for sacrificado ou morto, e nenhuma fonte
  do deck sacrifica/mata o próprio Jarad (seu próprio sac-outlet exige
  "outra" criatura; sem oponente real, nada mais remove criaturas). Fica
  documentado como N/A por construção do goldfish solo, não implementado
  (mesma classe de limitação já registrada pra habilidades
  `opponent_dependent`).
- **Agatha's Soul Cauldron** ({2}, artefato): **era exatamente o achado
  real** — `{T}: Exile target card from a graveyard. When a creature card
  is exiled this way, put a +1/+1 counter on target creature you control.
  Creatures you control with +1/+1 counters on them have all activated
  abilities of all creature cards exiled with this.` Cadastrada desde a
  Correção pós-Beorn só com tag `gy_hate`, **zero efeito implementado**.
  É literalmente a carta que "copia as atividades do cemitério" que o
  usuário descreveu.
- **Tyvar, Jubilant Brawler** (planeswalker, {1}{B}{G}, lealdade 3):
  achado à parte, mas do mesmo carão — **nunca passou pela auditoria de
  categoria 12 (regra permanente pós-Prismatic Bridge)** que o Beorn já
  tinha recebido. Pior: o `mill=3` cadastrado nele estava sendo disparado
  como se fosse ETB automático (mesmo pipeline genérico de Awaken the
  Honored Dead/Buried Alive), quando na real é o custo da habilidade **-2**
  (`Mill three cards, then you may return a creature card with mana value
  2 or less from your graveyard to the battlefield`) — a metade boa
  (reanimar) nunca existia.

**Corrigido (3 mudanças):**

1. `Agatha's Soul Cauldron` — nova função `try_agathas_soul_cauldron()`,
   chamada toda main phase: se houver criatura no seu cemitério, exila a
   de maior custo e põe +1/+1 num alvo (`agathas_cauldron_counters`). O
   static de "criaturas com contador ganham as habilidades ativadas das
   criaturas exiladas" fica documentado como não modelado numericamente
   (efeito qualitativo demais pro simulador — mesma classe de
   simplificação já usada em Smuggler's Surprise/Scalelord Reckoner no
   Beorn).
2. `Tyvar, Jubilant Brawler` — `mill=3` genérico removido; nova lógica
   dedicada em `_apply_etb`: sempre ativa o -2 no turno em que resolve
   (premissa: reanimar um corpo vale mais que guardar lealdade num
   goldfish solo sem ataques de oponente no PW), mila 3 e devolve a melhor
   criatura mv≤2 do cemitério pro campo (`tyvar_jubilant_reanimations`). O
   +1 (untap) fica documentado como não modelado (linha de menor valor,
   descartada pela mesma premissa greedy já usada em outros
   planeswalkers/ativadas do repositório).
3. `_dork_ready()` — estática do Tyvar Jubilant Brawler ("you may activate
   abilities of creatures you control as though they had haste") agora
   bypassa a doença de invocação pra mana dorks enquanto ele estiver em
   campo — achado novo, nunca modelado antes.

**Interação real entre as 3 peças:** Agatha's Soul Cauldron e Tyvar
Jubilant Brawler competem pelo MESMO recurso (criaturas no cemitério) —
Agatha exila permanentemente o que o Tyvar poderia reanimar. Isso é
tensão real do oráculo, não bug — ambas implementadas fielmente ao texto,
a IA gulosa deste simulador só não arbitra qual delas "vale mais" entre
turnos (prioriza o que aparece primeiro na ordem do `battlefield`).

**Robustez:** 20.000 seeds (71000-91000), timeout padrão — 0 erros.

**Batch oficial, n=5000, seed_base=71000 (antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| RECURSION | 0,08 | **0,15** (quase dobrou) |
| Avg finishers ativados | 0,85 | 0,89 |
| % finisher até T8 | 38,9% | 40,4% |
| Avg battlefield final | 18,92 | 19,12 |
| Tyvar Jubilant reanimou | — | 8,6% dos jogos, avg 0,09 |
| Agatha's Cauldron exilou | — | 18,4% dos jogos, avg 0,40 exílios |

**Leitura:** o usuário tinha razão em questionar o diagnóstico anterior —
RECURSION não era fraca só porque a lista carecia de recursão real, era
fraca porque **2 peças de recursão/valor real da própria lista nunca
tinham sido implementadas** (Agatha's Soul Cauldron 100% ausente, Tyvar
Jubilant Brawler só com a metade errada modelada). Corrigido, RECURSION
quase dobra (0,08→0,15) e Agatha's Soul Cauldron vira um engine ativo em
quase 1 a cada 5 jogos — ainda modesto frente ao Beorn (que tem Eternal
Witness sem pré-requisito), mas real agora, não mais uma tag morta. A
recomendação anterior de "trocar Oversold Cemetery por Eternal Witness"
seguia válida por si (Oversold ainda é a mais fraca das 3 fontes), mas a
lista já tinha mais recursão latente do que o relatório anterior mostrou —
o problema era mecânica não implementada, não ausência de cartas.
`lista.md` não muda.

---

### Correção grave — a habilidade estática do PRÓPRIO Thranduil nunca foi implementada — 2026-08-30

**Gatilho (usuário):** *"Vc sabe que o Thranduil copia habilidades de
elfos do cemitério, né? Preciso te lembrar do básico? Tem outro elfo que
ativa com mana para dar boost em todos os elfos…"* — correção direta
depois que a rodada anterior implementou Agatha's Soul Cauldron como se
fosse "a carta que copia atividades do cemitério", sem checar o oráculo do
próprio comandante primeiro.

**Verificado contra o oráculo real (Scryfall):**

```
Thranduil, the Elvenking {2}{B}{G}{U}
Legendary Creature — Elf Noble
Thranduil has all activated abilities of all Elf cards in your graveyard.
Whenever another legendary Elf you control enters, draw two cards, then discard a card.
```

**Erro grave confirmado:** `grep` por "all activated abilities" no
simulador só batia no texto da Agatha's Soul Cauldron — a linha 1 do
próprio oráculo do comandante, a metade que dá NOME ao arquétipo do deck,
**nunca tinha sido implementada**. Só a 2ª linha (gatilho "elfo lendario
entra -> compra 2, descarta 1") estava modelada. Isso não é uma carta
qualquer esquecida — é a habilidade estática definidora da própria
comandante, maior gap desta sessão inteira nos 3 decks.

**O "outro elfo que ativa com mana pra dar boost em todos os elfos"
apontado pelo usuário:** conferido — `Elvish Warmaster`: `{5}{G}{G}: Elves
you control get +2/+2 and gain deathtouch until end of turn.` Já estava
corretamente cadastrada como `finisher_repeatable`, custo 7 — mas só
disparava enquanto o próprio Elvish Warmaster estivesse VIVO em campo. Com
a estática do Thranduil implementada, essa mesma habilidade passa a ser
utilizável mesmo com o Elvish Warmaster morto/descartado no cemitério —
exatamente a conexão que o usuário estava apontando.

**Corrigido:** `activate_finishers()` agora considera duas fontes de
ativação, não só o battlefield: quando o comandante está em campo, Elfos
no cemitério com `activation_cost > 0` entram na mesma lista de
candidatos (`gy_borrow_sources`), usando a MESMA lógica de custo/tag já
existente (`finisher_repeatable`, `finisher_drain` do Jarad) — cobre
Elvish Warmaster, Ezuri Renegade Leader, Tyvar the Pummeler e Jarad, Golgari
Lich Lord como fontes de cemitério. O gatilho de Elrond ("whenever you
activate an ability of a creature, draw a card") continua disparando
mesmo nesses casos — regra real (CR 602.5b): a habilidade emprestada
pertence a quem a ganhou (Thranduil, uma criatura em campo), não ao cartão
original no cemitério.

**Escopo desta correção (decisão explícita):** só as habilidades já
tagueadas `finisher_repeatable`/`finisher_drain` foram estendidas pro
cemitério — Imperious Perfect (token maker), Selvala/Elrond (suas próprias
ativadas de mana/flicker) e Immaculate Magistrate (contador) continuam
modeladas só via battlefield, cada uma com sua própria função dedicada;
estendê-las também é trabalho real mas separado, não incluído agora.
Lathril (gatilho de dano de combate, não ativada — `activation_cost=0`)
corretamente nunca entra em `gy_borrow_sources`.

**Robustez:** 20.000 seeds (71000–91000), timeout padrão — 0 erros.

**Batch oficial, n=5000, seed_base=71000 (antes → depois desta correção):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg finishers ativados | 0,89 | **1,41** (+58%) |
| % de jogos com finisher até T8 | 40,4% | **54,3%** (+13,9pp) |
| Thranduil ativou hab. emprestada do cemitério | — | 24,3% dos jogos, avg 0,52/partida |
| Avg compras via Elrond | 0,11 | 0,18 |
| Avg battlefield final | 19,12 | 19,13 (~igual) |

**Leitura:** o usuário estava certo e o gap era sério — o relatório da
rodada anterior ("58% dos jogos sem finisher, recomendo Craterhoof-style
overrun") estava medindo um Thranduil incompleto, sem a própria habilidade
que dá nome ao deck. Com ela implementada, FINISHER/LETHALITY sobe de
40,4% pra **54,3%** — mudança muito maior que qualquer coisa que uma troca
de carta isolada renderia. A recomendação anterior de "adicionar um
overrun tipo Craterhoof" fica bem menos urgente: o deck já fecha o jogo
consideravelmente mais que o medido antes. `lista.md` não muda — isso foi
100% correção de simulador, nenhuma carta trocada.

---

### Auditoria completa de oráculo — TODAS as 91 cartas (comandante + 90), Scryfall em lote — 2026-08-30

**Gatilho (usuário):** *"Eu já cansei de pedir para vc compilar TODAS as
habilidades de TODAS as cartas, qual a dificuldade?"* — depois de 3
rodadas seguidas de achados pontuais (Agatha's Soul Cauldron, depois a
estática do próprio Thranduil), ficou claro que correção reativa
carta-a-carta não bastava. Auditoria sistemática de verdade: `POST
https://api.scryfall.com/cards/collection` em 2 lotes (75+16 cartas),
oráculo completo de cada uma das 91 cartas da lista salvo e comparado
linha a linha contra `CARD_DB` e a lógica do simulador (Regra 13).

**11 achados reais, todos corrigidos:**

1. **Terrenos nunca tinham mecanismo de "enters tapped" modelado (violação
   direta da Regra 12)** — o próprio cabeçalho do arquivo documentava isso
   como "simplificação deliberada, igual ao Beorn", mas o Beorn é
   mono-verde sem terrenos condicionais reais; o Ur-Dragon já tinha esse
   mecanismo. Implementado do zero: `tapped_lands_this_turn` (novo campo),
   `_land_enters_tapped()`, `has_land_subtype()`/`LAND_SUBTYPES`. Cobertura
   real por arquétipo: sempre-tapped incondicional (Elvenking's Halls,
   Zagoth Triome, face-terreno de Malakir Rebirth e Revitalizing Repast),
   fast land (Botanical Sanctum — tapped a partir do 4º terreno), check
   land (Hinterland Harbor — precisa Forest ou Island em campo), reveal
   land (Gilt-Leaf Palace — precisa Elfo na mão). Shocks e Rejuvenating
   Springs ficam sempre destravados por premissa já estabelecida
   (vida/multiplayer não rastreados) — documentado explicitamente, não
   mais silencioso.
2. **BUG GRAVE — Immaculate Magistrate inflava mana disponível todo
   turno.** Estava marcada com a tag `elf_scaling`, a MESMA usada por
   Priest of Titania/Elvish Archdruid/Wirewood Channeler pra escalar mana
   de dork real — mas o oráculo dela ("{T}: Put a +1/+1 counter on target
   creature for each Elf you control") não produz mana nenhuma.
   `total_mana()` tratava qualquer carta com essa tag como fonte de mana.
   Tag removida; habilidade real implementada em `try_immaculate_magistrate()`.
3. **BUG — Roaming Throne dobrando habilidade ATIVADA por engano.**
   `try_imperious_perfect()` aplicava a dobra de Roaming Throne na criação
   de token — mas RT só dobra habilidade **triggered** ("if a triggered
   ability... triggers, it triggers an additional time"), nunca ativada
   ({custo}: efeito). Corrigido (removida a dobra indevida).
4. **Eclipsed Realms tratada como puramente incolor** — mesma classe de
   erro já corrigida na Cavern of Souls (Regra 6 adendo): "Spend this mana
   only to cast a spell of the chosen type" (Elfo, escolha óbvia) vira
   fixação real pro subconjunto de spells de criatura Elfo. Tag
   `elf_only_color` aplicada.
5. **Wastewood Verge/Willowrush Verge tratadas como sempre destravadas nas
   2 cores** — a 2ª cor de cada uma é condicional ("Activate only if you
   control a Swamp or a Forest" / "...Forest or an Island"), nunca
   checada. Implementado via `has_land_subtype()`.
6. **Allosaurus Shepherd — finisher inteiro faltando.** Só a proteção
   contra counterspell estava modelada; "{4}{G}{G}: Until end of turn,
   each Elf creature you control has base power and toughness 5/5..." é um
   overrun real (mesma família de Tyvar the Pummeler/Ezuri/Elvish
   Warmaster), nunca cadastrado como finisher. Corrigido (`activation_cost=6`,
   tag `finisher_repeatable`).
7. **Trystan's Command — modal sem nenhum modo real implementado.** Só a
   tag genérica `removal` (1 dos 4 modos, sem alvo real em goldfish solo).
   Implementados os 2 modos com valor quantificável sem oponente: copiar
   Elfo não-lendário + devolver até 2 permanentes da GY pra mão (recursão
   real, nunca contada).
8. **Awaken the Honored Dead, capítulo III — recursão real ausente.** Só o
   mill do capítulo II estava capturado (via `mill=3` genérico); "You may
   discard a card. When you do, return target creature or land card from
   your graveyard to your hand" nunca foi implementado. Corrigido
   (simplificação documentada: os 3 capítulos da Saga, que resolvem em 3
   upkeeps separados, são comprimidos pro momento do cast).
9. **Fauna Shaman, Prime Speaker Vannifar, Eladamri — 3 tutores/motores
   com tag mas ZERO efeito implementado**, achados já citados como
   "deferidos" numa correção anterior (pós-Beorn) mas nunca revisitados
   pro Thranduil especificamente. Implementados: Fauna Shaman (descarta
   criatura, tutora criatura da biblioteca pra mão), Prime Speaker
   Vannifar (sacrifica criatura, busca outra de mv+1 direto pro campo),
   Eladamri (aproximação documentada do custo "tap 2 criaturas" via
   contagem — este simulador não rastreia tapped/untapped por criatura —
   revela criatura da mão e põe em campo de graça).
10. **Devoted Druid, Elrond (flicker), Takenuma (Channel)** — auditados e
    **deliberadamente deixados de fora**, cada um com nota explícita no
    `add()`/comentário do porquê (combo de auto-sacrifício de 1 uso só,
    flicker exigiria re-disparar ETBs, Channel compete com o land drop da
    própria carta) — decisão de escopo documentada, não esquecimento
    silencioso (Regra 13).
11. **Docstring do cabeçalho mentia sobre Takenuma channel** — citava a
    habilidade como já contabilizada no proxy de mill de Elfos no
    cemitério; nunca tinha sido implementada. Corrigida a citação.

**Robustez:** 20.000 seeds (71000–91000) rodadas 3 vezes ao longo da
correção (após o pacote de bugs de mana, depois após os 3 tutores) — 0
erros em todas as passadas.

**Batch oficial, n=5000, seed_base=71000 (antes de TODA esta auditoria →
depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg commander cast turn | 4,35 | 4,43 (mais lento, correto — a inflação de mana da Immaculate Magistrate desapareceu) |
| Commander cast por T5 | 83,9% | 83,4% |
| Avg finishers ativados | 0,89 | **1,49** |
| % jogos com finisher até T8 | 40,4% | **55,4%** |
| RECURSION | 0,08 | **0,40** (5x) |
| % jogos com blue screw | 6,2% | 5,1% |
| Avg battlefield final | 19,12 | 18,94 |

**Leitura:** a soma de todos os achados desta rodada (já em cima da
correção anterior da estática do próprio Thranduil) deixa RECURSION 5x
maior que o número reportado originalmente nesta sessão e confirma, de
novo, que os buracos reais do deck eram simulador incompleto, não falta
de cartas na lista. O turno médio da comandante ficou levemente mais
lento (4,35→4,43) — isso é uma CORREÇÃO pra baixo, não uma regressão: a
Immaculate Magistrate estava inflando mana disponível artificialmente
antes. `lista.md` não muda — 100% correção de simulador.

**Pendência explícita pro usuário:** esta auditoria completa foi feita só
pro Thranduil até agora. Beorn e Ur-Dragon ainda precisam da mesma
varredura completa (Scryfall em lote, carta por carta) — vou continuar
nos dois a seguir.

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

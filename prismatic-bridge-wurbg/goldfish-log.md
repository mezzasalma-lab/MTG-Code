# Goldfish Log — Esika, God of the Tree // The Prismatic Bridge

## Simulação #1 — gerada por Claude (RNG real, não é partida sua)

**Método:** embaralhei a lista de 100 cartas de `lista.md` com `random.shuffle` do Python (sem seed fixa, usa entropia do sistema operacional) em 2026-08-20. Mão inicial = 7 cartas do topo pós-embaralhamento. Convenção: jogador na ponta ("on the play"), sem compra no turno 1, compra 1 carta a partir do turno 2. Efeitos de "olhe o topo N" (ex: Oath of Nissa) foram resolvidos consultando a ordem real da biblioteca simulada, não escolhidos livremente. Este é um teste solo sem oponente — anotei explicitamente onde isso limita alguma carta (ex: Exotic Orchard).

**Mão inicial:** Oath of Nissa, Plateau, Command Tower, Sphinx of the Second Sun, Exotic Orchard, Bayou, Tamiyo, Field Researcher

**T1:** Joga Command Tower. Conjura Oath of Nissa (`{G}`). Resolve olhando o topo 3 da biblioteca simulada: Arena Rector, City of Brass, Savannah. Escolha: Arena Rector (criatura — já tinha 3 terrenos na mão, land não era prioridade). City of Brass e Savannah vão pro fundo.
Mão pós-T1: Plateau, Sphinx of the Second Sun, Exotic Orchard, Bayou, Tamiyo Field Researcher, Arena Rector.

**T2:** Compra: Badlands. Joga Bayou. Nenhum spell de 2 custa esse valor na mão — passa.

**T3:** Compra: Swords to Plowshares. Joga Plateau. 3 fontes de mana (Command Tower/Bayou/Plateau). Tamiyo, Field Researcher custa `{1}{G}{W}{U}` = 4 total, falta 1 — não castável ainda. Passa.

**T4:** Compra: The Peregrine Dynamo. Joga Exotic Orchard — **nota:** em goldfish solo sem oponente, Exotic Orchard não tem fonte confiável (não há terreno alheio pra copiar), tratado como mana morto neste teste. Com Command Tower + Bayou + Plateau (3 mana úteis), conjura The Peregrine Dynamo (`{3}`).

**T5:** Compra: Sol Ring. Conjura Sol Ring. Com Sol Ring + os 3 lands úteis, monta `{1}{G}{W}{U}` e conjura Tamiyo, Field Researcher.

**T6:** Compra: Teferi, Time Raveler. Conjura Teferi, Time Raveler (`{1}{W}{U}`).

**Board final (fim do T6):** Command Tower, Bayou, Plateau, Exotic Orchard (morto), Sol Ring | Oath of Nissa, The Peregrine Dynamo, Tamiyo Field Researcher, Teferi Time Raveler.
**Mão remanescente:** Sphinx of the Second Sun, Arena Rector, Badlands, Swords to Plowshares.
**Sem compra ainda:** nenhuma das Game Changers da lista (Farewell, Narset Parter of Veils, Rhystic Study) apareceu nesses 6 turnos — dado real dessa simulação, não uma afirmação sobre a lista em geral.

---

## Simulação #2 — goldfish Python focado (Greater Auramancy?) — 2026-08-21

**Script:** `prismatic_bridge_goldfish_v1.py` — construído do zero pra essa pergunta específica (não é o goldfish completo de curva geral, escopo documentado no docstring do arquivo). CARD_DB gerado via Scryfall `cards/collection` (99 cartas) com tags derivadas de `oracle_text` real. Simula só a face "The Prismatic Bridge" do comandante (a frente Esika não foi modelada — limitação documentada).

**Objetivo:** decidir se vale incluir Greater Auramancy, testando o deck atual vs. uma versão com Greater Auramancy no lugar de The Peregrine Dynamo (única criatura sem nenhuma tag de sinergia).

**Premissa não validada** (usuário não tem dado real, deck nunca jogado — citação: *"3 oponentes, não joguei com o deck ainda"*): taxa de tentativa de remoção por oponente por turno mirando a Bridge/protetores. Testado em 3 cenários (12%, 25%, 40% por oponente por turno) pra checar se a conclusão muda com a taxa.

**n=2000 por cenário, 10 turnos:**

| Taxa de remoção assumida | Bridge removida (méd/partida) sem GA | com GA | % Bridge em campo no fim, sem GA | com GA |
|---|---|---|---|---|
| 12%/oponente/turno | 1,18 | 1,14 | 63,3% | 64,5% |
| 25%/oponente/turno | 1,59 | 1,58 | 39,4% | 40,0% |
| 40%/oponente/turno | 1,72 | 1,73 | 28,4% | 28,4% |

**Achado principal — por que o efeito é tão pequeno em qualquer cenário:** instrumentei quantas partidas (de 2000, mesma seed base, deck com Greater Auramancy) chegam a ter cada protetor em campo em algum momento dos 10 turnos:

```
Sterling Grove chegou a estar em campo: 14,7%
Greater Auramancy chegou a estar em campo: 16,4%
Os 2 chegaram a estar em campo (mesmo que não simultâneo): 2,4%
```

**A redundância de shroud só importa nos jogos em que os DOIS protetores entram em campo — e isso acontece em só 2,4% das partidas.** O gargalo real não é "1 protetor não é redundante o suficiente", é "a chance de sequer conjurar 1 protetor de 2 mana num deck de 99 cartas em 10 turnos já é baixa (~15%)". Greater Auramancy não ataca esse problema — ela é mais uma carta de baixa densidade competindo pelo mesmo espaço, não uma solução pra reliability.

**Outros números de referência (taxa 12%, sem Greater Auramancy):**
```
Turno médio da 1ª conjuração da Bridge: 4,50 | mediana: 4,0
Bridge nunca conjurada em 10 turnos: 5,9%
Conjurada via flash (end step do turno anterior): 3,5% das partidas
Avg gatilhos de upkeep: 2,94 | acertos: 2305 criatura / 3581 planeswalker
```

**Conclusão:** sob qualquer uma das 3 premissas de remoção testadas, Greater Auramancy melhora a sobrevivência da Bridge em menos de 1,5 ponto percentual — efeito real mas pequeno, e consistente (não muda de ordem de grandeza mesmo triplicando a taxa de remoção assumida). Não é uma troca de alto impacto pra esse objetivo específico. Se a prioridade é proteção da Bridge, o gargalo real (~15% de chance de ter QUALQUER protetor em campo) provavelmente pede outra solução (ex: um tutor de encantamento, ou simplesmente aceitar que a proteção robusta contra remoção pontual não é o forte desse build — os counterspells da seção 5 da auditoria seguem sendo a defesa mais confiável).

---

### Simulação #3 — Enlightened Tutor no lugar do Greater Auramancy — 2026-08-21

**Teste de acompanhamento**, pedido do usuário depois do resultado do Greater Auramancy. Enlightened Tutor (`{W}`, Instant, `Search your library for an artifact or enchantment card... put that card on top`) no lugar de The Peregrine Dynamo, buscando Sterling Grove especificamente (lógica adicionada: busca só se Sterling Grove ainda não está em campo e ainda está na biblioteca).

**n=2000, taxa de remoção 12%/oponente/turno:**

```
Sterling Grove chegou a estar em campo:
  sem tutor:            14,7%
  com Enlightened Tutor: 24,3%   (+9,6pp, ~65% de aumento relativo)

% Bridge ainda em campo no fim da simulação:
  sem tutor:             63,3%
  com Enlightened Tutor: 63,2%   (~igual)

Avg vezes que a Bridge foi removida por partida:
  sem tutor:             1,18
  com Enlightened Tutor: 1,14   (mesma ordem de grandeza do Greater Auramancy)
```

**Leitura:** o tutor melhora bastante a taxa de ACESSO ao Sterling Grove (quase 2/3 de aumento relativo), mas isso não vira sobrevivência maior da Bridge no fim da partida. Motivo: Sterling Grove não se protege a si mesmo, e Enlightened Tutor é singleton — depois que o Sterling Grove morre (o que ainda acontece com frequência normal), não tem como buscar de novo. O tutor ataca "conseguir a proteção mais cedo", não "a proteção persistir depois que cai" — que é o mesmo problema estrutural de antes, só adiado.

**Nenhuma das duas opções testadas (Greater Auramancy, Enlightened Tutor) resolve o problema de forma decisiva sozinha.**

---

### Simulação #4 — Hall of Heliod's Generosity (recursão repetível) — 2026-08-21

**Diferença do Enlightened Tutor:** Hall of Heliod's Generosity (`{1}{W}, {T}: Put target enchantment card from your graveyard on top of your library`) é um TERRENO — permanente, repetível, não singleton. Testado no lugar de Nesting Grounds, em 10 E 16 turnos (pra dar tempo da cadeia completa: Sterling Grove morrer → Hall em campo → mana disponível → recursão → compra → recast).

**Bug encontrado e corrigido nesse teste:** `resolve_removal_round` fazia a carta removida sumir do jogo em vez de ir pro cemitério — teria feito a recursão nunca achar o alvo. Corrigido em `prismatic_bridge_goldfish_v1.py` (agora `state.graveyard.append(target)` na remoção de protetores).

**n=2000, taxa de remoção 12%/oponente/turno, comparando 10 vs 16 turnos:**

```
                          Baseline 10t   +Hall 10t   Baseline 16t   +Hall 16t
Sterling Grove em campo   15,1%          15,1%       21,1%          21,1%
Bridge em campo no fim    63,3%          63,1%       69,8%          70,0%
Bridge removida (média)   1,18           1,17        2,44           2,42
```

**Efeito praticamente zero em qualquer horizonte de turnos.** Instrumentado: só 48 eventos de recursão em 2000 partidas (2,4%) em 10 turnos. Hall of Heliod's Generosity é 1 carta em 37 terrenos (~2,7% de densidade) — só ativa se Sterling Grove já morreu E ela já está em campo E sobra mana, uma cadeia de baixa probabilidade que raramente se completa mesmo dando mais tempo de jogo (16 turnos não muda o resultado vs. o baseline no mesmo horizonte).

**Conclusão consolidada das 3 opções testadas (Greater Auramancy, Enlightened Tutor, Hall of Heliod's Generosity): nenhuma resolve o problema de forma perceptível.** Mesmo motivo nas três — deck de 99 cartas singleton com 1 única peça de proteção dedicada (Sterling Grove), competindo por espaço de compra com as outras 96. Qualquer solução de 1 carta ainda precisa ser puxada primeiro, o que já é raro em 10-16 turnos. Ver `auditoria.md` seção de proteção pra recomendação final.

---

### Simulação #5 — avaliação principal, n=5000: Bridge cast + acerto de planeswalker até T6/T7/T8 — 2026-08-21

**Objetivo pedido pelo usuário:** avaliar o deck pela capacidade real de (a) conjurar a Bridge e (b) ela acertar um planeswalker (não criatura) via gatilho de upkeep, até os turnos 6, 7 e 8. Métrica nova adicionada ao simulador: `first_pw_hit_turn` (turno do primeiro acerto de planeswalker, rastreado em `bridge_upkeep_trigger`).

**Lista atual, sem nenhuma das trocas testadas nas sessões anteriores** (Greater Auramancy/Enlightened Tutor/Hall of Heliod's Generosity não estão na lista real — só foram experimentos). n=5000, 8 turnos, seed_base=4000000.

```
Avg mulligans: 0,23
Bridge nunca conjurada em 8 turnos: 12,5%
Turno médio da 1ª conjuração da Bridge: 4,07 | mediana: 4
Conjurada via flash (end step anterior): 3,7% das partidas
Avg gatilhos de upkeep por partida: 2,04
  Acertos em criatura: 3985 | em planeswalker: 6230 | total: 10215
% da Bridge ainda em campo no fim (T8): 59,0%
Avg vezes que a Bridge foi removida: 0,82
```

**Bridge colocou planeswalker em jogo (1º acerto de PW via gatilho de upkeep):**

| Turno | Chance acumulada |
|---|---|
| **T6** | **42,4%** |
| **T7** | **50,2%** |
| **T8** | **57,7%** |
| Nunca em 8 turnos | 42,3% |

**Leitura:** menos da metade das partidas (42,4%) já teve um planeswalker colocado de graça pela Bridge até o turno 6 — o motor central do deck ainda não "ligou" na maioria dos jogos nesse ponto. Só passa de 50% no turno 7. No turno 8, ainda quase 1 em cada 4 partidas (42,3% projetado ao fim de 8 turnos) nunca viu isso acontecer. Isso é consistente com os dados já registrados: turno médio de 1ª conjuração da Bridge é 4,07, e ela só acerta planeswalker em 6230 de 10215 gatilhos totais (61%, já que o deck tem mais planeswalker que criatura — seção 8 da auditoria), então mesmo quando a Bridge está em campo cedo, ainda precisa de outro gatilho de upkeep pra realmente acertar. A tese do deck (jogar PW de graça pela Bridge) é real, mas não é rápida nem garantida — é um plano de médio prazo (turno 7-8 em diante), não um plano de turno 4-5.

---

### Correção — mana disponível pra flashar a Bridge (CR 500.1: untap, upkeep, draw) — 2026-08-21

**Bug real identificado pelo usuário:** meu `can_flash_bridge` usava `total_mana`/`remaining_mana` (mana atual do jogador), como se tudo estivesse sempre destapado no momento de flashar a Bridge no end step de um oponente. Isso está errado — o untap step só destapa os permanentes do jogador ativo (CR 500.1). Meus terrenos ficam tapados do jeito que ficaram no MEU último turno durante os turnos dos oponentes; só destapam de novo no MEU próximo untap step. A mana real disponível pra flashar algo no end step alheio é o que sobrou NÃO GASTO do meu último turno, não o total atual.

**Correção aplicada:**
- Novo campo `state.mana_held_back` — calculado no fim de cada turno (`total_mana - mana_spent_this_turn`), representa o que ficou destapado e disponível até meu próximo untap.
- `can_flash_bridge` agora checa `mana_held_back` contra o custo do habilitador de flash (`Alchemist's Refuge` = 2, `Emergence Zone` = 1, `Emergence Zone` se sacrifica ao usar) + custo efetivo da Bridge (com taxa de comandante).
- `main_phase` agora reserva mana de propósito quando um habilitador de flash já está em campo e a Bridge ainda não saiu — não gasta tudo no resto da mão, seguindo mana pra viabilizar a linha de flash no futuro.

**Resultado, n=5000, 8 turnos:**

| Métrica | Antes (bug) | Depois (corrigido) |
|---|---|---|
| Conjurada via flash | 3,7% | **0,0%** |
| 1º acerto de PW até T6 | 42,4% | 40,9% |
| 1º acerto de PW até T7 | 50,2% | 48,6% |
| 1º acerto de PW até T8 | 57,7% | 55,9% |

**Achado estrutural, não só um ajuste numérico:** a linha de flash caiu pra ZERO, não só diminuiu. Motivo: no modelo, a Bridge está sempre "disponível" (vem da zona de comando, não depende de estar na mão) — assim que fica pagável, a IA gananciosa conjura ela imediatamente na main phase. O custo de flashar (habilitador + Bridge) é sempre maior que o custo de conjurar normal (só a Bridge). Como o mana total só cresce turno a turno, no momento em que teria mana suficiente pra flashar, já teria tido mana suficiente pra conjurar normal num turno anterior — e a IA já teria feito isso antes de chegar lá. **O modelo atual nunca escolhe segurar a Bridge de propósito só pra flashar**, porque não pesa o benefício real da linha (pular a janela de remoção antes do 1º gatilho) contra abrir mão de 1 turno com a Bridge já em campo. Pra medir esse benefício de verdade, seria preciso modelar uma política diferente (segurar a Bridge deliberadamente quando o habilitador já está em campo, mesmo podendo conjurar normal) — ainda não implementado.

---

<!-- Para novas partidas (reais ou novas simulações), use o formato abaixo -->

## Partida #N — AAAA-MM-DD

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

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
